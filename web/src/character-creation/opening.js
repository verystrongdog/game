/**
 * 开局经历：词表读取 / 查询 / 选择合法性 / 属性结算 / 契约校验。
 *
 * 边界（AGENTS.md §二 拦截规则）：
 *   本模块只服务开局与 Web 演示。不得引入 C# 引擎或神经模拟系统的任何概念。
 *
 * 设计属性：
 *   - 全部是无状态纯函数（db + 已答的八问 + selectedIds 进，值出）。无单例、无缓存、
 *     无隐藏状态，所以病历单上可以任意回退、重答，一个 id 数组就能分享同一个开局。
 *   - 本模块不自己载入数据：调用方把 `data/opening.json` 传进来（Vite 下 `import db from ...json`）。
 *     这样它同时能在浏览器与 node 里跑，不绑定任何载入方式。
 *
 * 数据权威：data/opening.json 是唯一来源。本文件不含任何数据字面量。
 */

// ── 记录上允许出现的非 facet 字段 ────────────────────────────────────────
const META_KEYS = ['id', 'title', 'summary', 'effects', 'diseases'];
const ID_PATTERN = /^exp_\d{4}$/;

/**
 * 玩家可见文案里**不许出现的内部实现词**。
 * 「锚点」就是这样一个词：契约里到处是它，但玩家一个都不该看见——他在纸上看得到的
 * 只有医生的七句问话与纸上的栏目。校验器据此扫 `interview.screen` 与 `record_shell`。
 * ⚠️ 它**留在词表里**（而不是跟着旧口径一起删掉）：阶段 3 把「锚点」这一整套口径退役了，
 * 词表正是拦住它重新漏回屏上的那道门。
 */
const INTERNAL_COPY_WORDS = ['锚点', '输出槽', '后果出口', '维度', '字段', '槽位', '元数据', 'facet', 'selector'];

/**
 * 递归收集一块数据里**所有字符串**（含嵌套对象与数组，也含键名）。
 *
 * 为什么要递归：病历外壳从 2026-09-27 起有了嵌套（`paper.columns[].writes[].label`、
 * `general[].blank`、`character.fields[]`）。只扫顶层的校验会让嵌进去的一句内部黑话漏网
 * ——那正是 `record_shell_copy_leaks_internal` 要防的事。键名一并扫，是因为键名也可能
 * 被渲染（如 `general[].value_to` 这种自己会成为标签的键）。
 *
 * 返回 `[{path, text}]`，`path` 形如 `general[0].blank`，报错时能指到具体那一句。
 */
export function collectStrings(node, path = '', { keys = true } = {}) {
  if (typeof node === 'string') return [{ path, text: node }];
  if (Array.isArray(node)) return node.flatMap((v, i) => collectStrings(v, `${path}[${i}]`, { keys }));
  if (node && typeof node === 'object') {
    return Object.entries(node).flatMap(([k, v]) => {
      const at = path ? `${path}.${k}` : k;
      const inner = collectStrings(v, at, { keys });
      return keys ? inner.concat([{ path: at, text: k }]) : inner;
    });
  }
  return [];
}

/**
 * 递归扫描时要放行的「元数据键」：这些路径下的字符串是依据表，不是屏上文案。
 * 放行是有代价的（内部词可以藏在依据里），所以这张表必须短而且要写死——
 * 加一条就要问一次「这句话真的不上屏吗」。
 */
export const META_COPY_PATHS = [
  /(^|\.)source$/,
  /(^|\.)ask$/,
  /(^|\.)column_sources(\[|$)/,
  /(^|\.)character_vocab_gaps(\[|$)/,
  /_source$/,
  // 依据表：问诊每一问的法定依据、每一条分类与每一级放宽口径的理由。这些字是给 owner
  // 与校验器读的，要能自由使用「取值」「记录」这类词来描述契约本身；它们不上屏。
  /(^|\.)basis(\[|\.|$)/,
];

/** `blank_from` 指到的空白态（如 `complaint.empty`）——纸上的空栏只有一份副本。 */
export function blankFromResolves(db, path) {
  const [block, key] = String(path).split('.');
  const value = db?.[block]?.[key];
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * 自建人物的某一笔落在页眉哪一行上（`character.fields[].row` → `general[].label`）。
 * 返回那条行；没登记就返回 null——校验器据此报 `character_field_without_row`。
 * 它同时是「玩家可填的笔数」的算术来源：见 `character-source.js` 的 `writableRows`。
 */
export function rowOfCharacterField(shell, field) {
  return (shell.general ?? []).find((r) => r.label === field.row) ?? null;
}

// ── 基础读取 ─────────────────────────────────────────────────────────────
export function byId(db, id) {
  const r = db.experiences.find((x) => x.id === id);
  if (!r) throw new Error(`未知经历 id: ${id}`);
  return r;
}

export function facetSpec(db, facet) {
  const s = db.vocab[facet];
  if (!s) throw new Error(`未知 facet: ${facet}`);
  return s;
}

export function labelOf(db, facet, valueId) {
  const v = facetSpec(db, facet).values.find((x) => x.id === valueId);
  if (!v) throw new Error(`未登记取值: ${facet}=${valueId}`);
  return v.label;
}

export const facetIds = (db) => Object.keys(db.vocab);
export const valuesOf = (db, facet) => facetSpec(db, facet).values.map((v) => v.id);

/**
 * 输出槽 facet（`vocab[id].output === true`）。
 * 它是**结果**不是身份，所以渲染时不当分组行，只当"留下了什么"一节。
 * 标在数据里而不是写死在这里——校验器要求全表恰好一个。
 */
export const outputFacetId = (db) => facetIds(db).find((f) => db.vocab[f].output === true) ?? null;

/** 会出现在卡面分组行里的 facet（= 全部 facet 减去输出槽）。 */
export const groupingFacetIds = (db) => facetIds(db).filter((f) => db.vocab[f].output !== true);

/** facet 的取值数组（单值 facet 也归一成数组）。 */
const asArray = (raw) => (Array.isArray(raw) ? raw : [raw]);

// ── 查询：按 facet，不按路径 ─────────────────────────────────────────────
/** 子句形态：{facet, in?} | {facet, not_in?} | {facet, empty:true}。视图与非法组合共用。 */
export function clauseHits(rec, c) {
  const raw = rec[c.facet];
  if (raw === undefined) throw new Error(`子句指向不存在的 facet: ${c.facet}`);
  const arr = asArray(raw);
  if (c.empty === true) return arr.length === 0;
  if (Array.isArray(c.in)) return arr.some((x) => c.in.includes(x));
  if (Array.isArray(c.not_in)) return !arr.some((x) => c.not_in.includes(x));
  throw new Error(`子句形状非法: ${JSON.stringify(c)}`);
}

/** selector = {all:[], any:[], none:[]}，三段都可省略。 */
export function evalSelector(db, selector) {
  const { all = [], any = [], none = [] } = selector || {};
  return db.experiences.filter(
    (r) =>
      all.every((c) => clauseHits(r, c)) &&
      (any.length === 0 || any.some((c) => clauseHits(r, c))) &&
      none.every((c) => !clauseHits(r, c)),
  );
}

export const queryByFacets = (db, clauses) => evalSelector(db, { all: clauses });

export function evalView(db, viewId) {
  const v = db.views.find((x) => x.id === viewId);
  if (!v) throw new Error(`未知视图: ${viewId}`);
  return evalSelector(db, v.selector);
}

export const viewIndex = (db) =>
  db.views.map((v) => ({ id: v.id, label: v.label, count: evalView(db, v.id).length }));

/** 卡片渲染所需的一切：叙事文本 + 每个 facet 的玩家可读标签 + 留下的东西。 */
export function describe(db, id) {
  const r = byId(db, id);
  const facets = groupingFacetIds(db).map((facet) => {
    const spec = db.vocab[facet];
    const arr = asArray(r[facet]);
    return {
      facet,
      name: spec.name,
      // 空的「和谁」读作「一个人」——空值怎么念由词表的 empty_label 决定，不在这里写死。
      values: arr.length ? arr.map((v) => labelOf(db, facet, v)) : spec.empty_label ? [spec.empty_label] : [],
    };
  });
  const out = outputFacetId(db);
  return {
    id: r.id,
    title: r.title,
    summary: r.summary,
    facets,
    channels: out ? asArray(r[out]).map((v) => labelOf(db, out, v)) : [],
  };
}

// ── 问诊（一屏一张纸上的八问：自述 → 诱因经历 → 时间三问） ─────────────
/**
 * 玩家不再在 facet 上「落锚」：患者先自述疾病（第 1 问），病历撰写人再按七问逐句追问，患者在**闭集**里答一句，
 * 答案当场写进病历（写入哪一栏写在 `record_shell.paper.columns[].writes[].from` 上）。
 *
 * 三条口径，全部由数据决定，代码里不写死：
 *   ① 问什么、答什么：`interview.questions`，答案闭集一律来自 `vocab[facet]`；
 *   ② 哪一问参与池子：`questions[].matches`（自述与时间三问只写病历）；
 *   ③ 谁答哪一面：`interview.who_answers`（patient / hospital）——它是全部 11 个
 *      facet 的**完全划分**，所以「没得选的那部分」不许只活在散文里。
 */
export const interviewRule = (db) => db.interview;
export const interviewQuestions = (db) => db.interview.questions;
export const questionById = (db, id) => interviewQuestions(db).find((q) => q.id === id) ?? null;
export const questionOfFacet = (db, facet) => interviewQuestions(db).find((q) => q.facet === facet) ?? null;

/** 参与池子相符判断的那几问（其余只写病历）。 */
export const matchQuestions = (db) => interviewQuestions(db).filter((q) => q.matches === true);
export const matchFacets = (db) => matchQuestions(db).map((q) => q.facet);

/** 谁答哪一面：两份名单合起来必须恰好覆盖 11 个 facet。 */
export const facetsAnsweredBy = (db, who) => (db.interview.who_answers[who] ?? []).map((x) => x.facet);

/**
 * 一问的答案闭集从哪来 —— `answer_from` 只有两种取值，两种都写在数据里：
 *
 *   `vocab`      答案 = 某个记录 facet 的一个取值（`vocab[facet].values`）。经历四问与
 *                时间三问都是这一种；答案只决定**已经写好**的条目怎么排（§十.3）。
 *   `complaint`  答案 = 主诉块里的**自述症状表**（`complaint.self_report.values`）。
 *                它**不是记录 facet**：患者自述的那个病只写进主诉栏，既不参与池子的相符
 *                判断，也拿不到任何一条记录的取值——所以它必须 `matches: false`
 *                （`interview_nonfacet_question_matches`）。这是红线在数据上的形式。
 *
 * 找不到来源时返回 `null`，由 `validateInterview` 报出来；这里不抛错，
 * 因为数据坏掉时界面仍要能渲染出「这一问没有可选项」，而不是整屏崩掉。
 */
export function answerSpec(db, question) {
  // 故意不走 `facetSpec`（那个会在未登记 facet 上抛错）：数据坏掉时界面要能把这一问
  // 渲染成「没有可选项」，而不是整屏崩掉——报错是 `validateInterview` 的活。
  if (question?.answer_from === 'vocab') return db.vocab?.[question.facet] ?? null;
  if (question?.answer_from === 'complaint') return db.complaint?.self_report ?? null;
  return null;
}

/**
 * 一问的答案闭集（规范化后的形状）。**两个来源在这里合流**，所以下游
 * （`answerChoices` / `answerText` / `poolCensus` / `answerCardinality`）都不必知道
 * 答案是来自记录词表还是主诉的自述表。
 */
export function answerOptions(db, question) {
  const spec = answerSpec(db, question) ?? {};
  const multi = spec.multi === true;
  const values = (spec.values ?? []).map((v) => ({ id: v.id, label: v.label }));
  return {
    facet: question.facet,
    multi,
    minItems: multi ? (spec.min_items ?? 0) : 1,
    maxItems: multi ? (spec.max_items ?? values.length) : 1,
    emptyLabel: multi && spec.min_items === 0 ? (spec.empty_label ?? null) : null,
    values,
  };
}

export const isAnswered = (answers, facet) => answers?.[facet] !== undefined && answers[facet] !== null;

/** 八问都答完了吗（纸上的现病史与主诉才写得成）。 */
export const answersComplete = (db, answers = {}) =>
  interviewQuestions(db).every((q) => isAnswered(answers, q.facet));

/** 一条答案上屏怎么念（多值按词表顺序连起来，空值念 empty_label）。 */
export function answerText(db, question, value) {
  const spec = answerOptions(db, question);
  if (spec.multi) {
    const arr = asArray(value);
    if (arr.length === 0) return spec.emptyLabel ?? '';
    return spec.values.filter((v) => arr.includes(v.id)).map((v) => v.label).join(' · ');
  }
  if (value === undefined || value === null) return '';
  return spec.values.find((v) => v.id === value)?.label ?? '';
}

/**
 * 答案是否踩到一条非法组合（`forbidden_combos`）。
 *
 * 这是**答案侧**的合法性，与记录的筛选无关：时间三问不参与池子，但它们照样
 * 会写进现病史——「瞬时 × 持续不断」写在纸上自相矛盾，所以那一档在按钮上就灰掉。
 * 判据与记录侧共用同一份 `forbidden_combos`，不存在第二套匹配语义。
 */
export function answerHitsClause(clause, answers = {}) {
  const raw = answers[clause.facet];
  if (raw === undefined || raw === null) return false;
  const arr = asArray(raw);
  if (clause.empty === true) return arr.length === 0;
  if (Array.isArray(clause.in)) return arr.some((x) => clause.in.includes(x));
  if (Array.isArray(clause.not_in)) return !arr.some((x) => clause.not_in.includes(x));
  return false;
}

export const answersForceCombos = (db, answers = {}) =>
  db.forbidden_combos.filter((fc) => fc.when.length > 0 && fc.when.every((c) => answerHitsClause(c, answers)));

/** 把某个取值选上 / 取消（多值问用；单值问直接替换）。 */
export function toggleAnswer(db, answers, question, value) {
  const spec = answerOptions(db, question);
  if (!spec.multi) return { ...answers, [question.facet]: value };
  const arr = asArray(answers[question.facet]).slice();
  const at = arr.indexOf(value);
  if (at >= 0) arr.splice(at, 1);
  else if (arr.length < spec.maxItems) arr.push(value);
  const next = { ...answers };
  if (arr.length === 0) next[question.facet] = [];  // 「一个人」= 空数组，仍是答过了
  else next[question.facet] = arr;
  return next;
}

/** 八问当前的可点性：每个取值点下去会不会踩非法组合 / 超过多选上限。 */
export function answerChoices(db, answers = {}) {
  return interviewQuestions(db).map((question) => {
    const spec = answerOptions(db, question);
    const chosen = answers[question.facet];
    const chosenArr = asArray(chosen);
    return {
      id: question.id,
      facet: question.facet,
      ask: question.ask,
      matches: question.matches === true,
      multi: spec.multi,
      maxItems: spec.maxItems,
      answered: isAnswered(answers, question.facet),
      chosen,
      emptyOption: spec.emptyLabel === null ? null : {
        label: spec.emptyLabel,
        chosen: isAnswered(answers, question.facet) && chosenArr.length === 0,
      },
      values: spec.values.map((v) => {
        const picked = spec.multi ? chosenArr.includes(v.id) : chosen === v.id;
        const next = spec.multi && !picked && chosenArr.length >= spec.maxItems
          ? null
          : toggleAnswer(db, answers, question, v.id);
        const reasons = next === null
          ? [{ code: 'answer_items_full', max: spec.maxItems }]
          : answersForceCombos(db, next).map((fc) => ({ code: 'answer_combo_forbidden', combo: fc.id, label: fc.label }));
        return { id: v.id, label: v.label, chosen: picked, ok: reasons.length === 0, reasons };
      }),
    };
  });
}

// ── 池子（问诊第 2–5 问筛出、玩家逐条核对的那一池） ──────────────────────
/**
 * 一条记录与一条答案对不对得上：
 *   单值问 —— 取值相同；
 *   多值问 —— 至少有一个相同；
 *   答「一个人」（空数组）—— 只与那一条多值 facet 为空的记录相符。
 */
export function answersMatchRecord(db, rec, facet, value) {
  const spec = facetSpec(db, facet);
  const recValues = asArray(rec[facet]);
  const ans = asArray(value);
  if (spec.multi) {
    if (ans.length === 0) return recValues.length === 0;
    return recValues.some((x) => ans.includes(x));
  }
  return recValues[0] === ans[0];
}

/**
 * 某一问的一个答案在**整库**上的相符掩码（1 = 相符）。
 *
 * 全部打分都走这一处：`scoreAnswers` 把若干个掩码加起来就是相符问数。写成掩码是为了
 * **全部已答前缀**跑得动（十八万个状态 × 288 段），不是为了省几行——语义一字未变。
 */
export function answerMask(db, question, value, records = db.experiences) {
  const spec = facetSpec(db, question.facet);
  const facet = question.facet;
  const ans = asArray(value);
  const out = new Uint8Array(records.length);
  if (spec.multi) {
    const empty = ans.length === 0;
    for (let i = 0; i < records.length; i += 1) {
      const rv = records[i][facet];
      if (empty) out[i] = rv.length === 0 ? 1 : 0;
      else out[i] = rv.some((x) => ans.includes(x)) ? 1 : 0;
    }
  } else {
    const only = ans[0];
    for (let i = 0; i < records.length; i += 1) out[i] = records[i][facet] === only ? 1 : 0;
  }
  return out;
}

/** 已答的那几问（按问序）。 */
export const answeredMatchQuestions = (db, answers = {}) =>
  matchQuestions(db).filter((q) => isAnswered(answers, q.facet));

/**
 * 给整库打分：每条记录对上几问，外加每一问的掩码（放宽与「去掉最难相符的一问」都要用）。
 * 返回 `{records, hits, dims, answered}`——`answered` 是已答的问数，也就是满分。
 */
export function scoreAnswers(db, answers = {}, records = db.experiences) {
  const qs = answeredMatchQuestions(db, answers);
  const hits = new Uint8Array(records.length);
  const dims = qs.map((q) => ({ facet: q.facet, mask: answerMask(db, q, answers[q.facet], records) }));
  for (const d of dims) {
    for (let i = 0; i < hits.length; i += 1) hits[i] += d.mask[i];
  }
  return { records, hits, dims, answered: qs.length };
}

/** 相符问数：这条记录对上了几问（0–4）。越多排得越前。 */
export function matchedCount(db, rec, answers = {}) {
  return scoreAnswers(db, answers, [rec]).hits[0];
}

/**
 * 按相符问数从多到少排序的库内下标；同分按库内原顺序（稳定、可复现）。
 * 用计数排序写进定长数组：这一步在每个已答前缀上都要跑一遍，不能靠 sort 的分配。
 */
export function orderByHits(hits, max) {
  const counts = new Int32Array(max + 1);
  for (let i = 0; i < hits.length; i += 1) counts[hits[i]] += 1;
  const at = new Int32Array(max + 1);
  let acc = 0;
  for (let s = max; s >= 0; s -= 1) { at[s] = acc; acc += counts[s]; }
  const order = new Int32Array(hits.length);
  for (let i = 0; i < hits.length; i += 1) order[at[hits[i]]++] = i;
  return order;
}

/** `scored` 上挂一份排好的下标表：同一个前缀要试好几级放宽，排序只做一次。 */
function scoredOrder(scored) {
  if (!scored.order) scored.order = orderByHits(scored.hits, scored.answered);
  return scored.order;
}

/**
 * 某一级放宽收哪些记录 —— 返回按下标判定的谓词，所以候选不必先落成一份数组。
 *
 *   matched_all       相符问数 = 已答问数
 *   matched_drop_one  去掉「去掉它之后候选最多」的那一问（平手取靠后那一问），其余照旧
 *   matched_any       相符问数 ≥ 1
 *   library           全收（仍按相符问数排序）
 */
export function levelPredicate(level, scored) {
  const { hits, dims, answered } = scored;
  if (level === 'library') return () => true;
  if (level === 'matched_any') return (i) => answered === 0 || hits[i] >= 1;
  if (level === 'matched_all') return (i) => hits[i] === answered;
  if (answered <= 1) return () => true;
  let drop = dims.length - 1;
  let best = -1;
  for (let d = 0; d < dims.length; d += 1) {
    let count = 0;
    for (let i = 0; i < hits.length; i += 1) {
      if (hits[i] - dims[d].mask[i] === answered - 1) count += 1;
    }
    if (count >= best) { best = count; drop = d; }
  }
  const dm = dims[drop].mask;
  return (i) => hits[i] - dm[i] === answered - 1;
}

/** 某一级放宽下的候选（按相符问数排序的整条记录）。界面与测试用它，不做池子的收口。 */
export function poolCandidates(db, answers = {}, level = 'matched_all') {
  const scored = scoreAnswers(db, answers);
  const keep = levelPredicate(level, scored);
  // ⚠️ `orderByHits` 返回的是定长整数数组，`.filter().map()` 在它上面会退化成整数数组，
  // 所以这里手动收集（曾经踩过：候选变成了 NaN 的数组）。
  const out = [];
  for (const i of scoredOrder(scored)) if (keep(i)) out.push(scored.records[i]);
  return out;
}

/** 池子的下限：两个数都是**推出来的**，不是新参数。 */
export function poolFloors(db, ddb = null) {
  const minSize = db.quota.total;
  const perContext = db.quota.per_value_max;
  return {
    minSize,
    perContext,
    minContexts: Math.ceil(minSize / perContext),
    minDiseases: ddb?.pool_rule?.diseases_min ?? null,
    maxDiseases: ddb?.pool_rule?.diseases_max ?? null,
  };
}

export function poolStats(db, ddb, records) {
  const facet = db.quota.per_facet;
  return {
    size: records.length,
    contexts: new Set(records.map((r) => r[facet])).size,
    diseaseUnion: ddb ? new Set(records.flatMap((r) => r.diseases)).size : null,
  };
}

export function poolMeetsFloors(db, ddb, records) {
  const f = poolFloors(db, ddb);
  const s = poolStats(db, ddb, records);
  if (s.size < f.minSize) return false;
  if (s.contexts < f.minContexts) return false;
  if (ddb && s.diseaseUnion !== null) {
    if (f.minDiseases !== null && s.diseaseUnion < f.minDiseases) return false;
    if (f.maxDiseases !== null && s.diseaseUnion > f.maxDiseases) return false;
  }
  return true;
}

/**
 * 从「已排好序的候选」里放满一池：
 *   - 按相符问数逐条放，**每个地方最多 `quota.per_value_max` 条**；
 *   - **病并集不得超过 `ddb.pool_rule` 的上下界**；
 *   - 还没够下界时只收能添上新病的条目（否则一池可能只有一张病）。
 * 起手那一条若把某个界顶破，就换下一条重来（`pool.seed_tries`）——池子宁可换种子，
 * 也不肯为了凑数破掉契约。
 *
 * `scored` 是 `scoreAnswers` 的结果，`keep` 是这一级放宽的谓词；候选不落成数组，
 * 直接按有序下标放——池子因此只有一处实现。
 */
export function fillPool(db, ddb, scored, keep, size = null) {
  const cfg = db.interview.pool;
  const limit = size ?? cfg.display_size;
  const floors = poolFloors(db, ddb);
  const facet = db.quota.per_facet;
  const contextKeys = valuesOf(db, facet);
  const diseaseKeys = ddb ? ddb.items.map((d) => d.id) : [];
  // 取值 → 下标：字符串比较只在建表时做一次。放池子的热路径上全是整数，
  // 这是「全部已答前缀」跑得动的关键（不然每看一条记录都要在 27 个病名里搜一遍）。
  const ctxIndex = new Map(contextKeys.map((k, i) => [k, i]));
  const diseaseIndex = new Map(diseaseKeys.map((k, i) => [k, i]));
  const order = scoredOrder(scored);
  // 这一级放宽收哪些记录：先挑一遍，后面的每次起手重试只在这张表上走。
  const kept = [];
  for (const i of order) if (keep(i)) kept.push(i);
  // 凑不出十段就别开火：候选本身不够，换哪个起手都一样（这一条把绝大多数失败的
  // 那一级挡在门外，是枚举十八万个前缀跑得动的主要原因，判据本身没变）。
  if (kept.length < floors.minSize) {
    return {
      picked: [],
      attempts: 0,
      size: 0,
      contexts: 0,
      diseaseUnion: ddb ? 0 : null,
      meets: false,
      candidates: kept.length,
    };
  }
  const perContext = new Int8Array(contextKeys.length);
  const perDisease = new Int16Array(diseaseKeys.length);
  const maxSeeds = Math.max(1, cfg.seed_tries ?? 1);
  const seeds = Math.min(maxSeeds, kept.length);
  let last = null;
  for (let t = 0; t < seeds; t += 1) {
    const seed = kept[t];
    const picked = [seed];
    perContext.fill(0);
    perDisease.fill(0);
    perContext[ctxIndex.get(scored.records[seed][facet])] = 1;
    let unionSize = 0;
    for (const d of scored.records[seed].diseases) {
      const at = diseaseIndex.get(d);
      if (at !== undefined && perDisease[at] === 0) { perDisease[at] = 1; unionSize += 1; }
    }
    for (const i of kept) {
      if (picked.length >= limit) break;
      if (i === seed) continue;
      const rec = scored.records[i];
      const ci = ctxIndex.get(rec[facet]);
      if (perContext[ci] >= floors.perContext) continue;
      let fresh = 0;
      for (const d of rec.diseases) {
        const at = diseaseIndex.get(d);
        if (at !== undefined && perDisease[at] === 0) fresh += 1;
      }
      if (floors.maxDiseases !== null && unionSize + fresh > floors.maxDiseases) continue;
      // 病并集的下界也要顾到：还没够病时，先只收能添上新病的条目。
      if (floors.minDiseases !== null && unionSize < floors.minDiseases && fresh === 0) continue;
      picked.push(i);
      perContext[ci] += 1;
      for (const d of rec.diseases) {
        const at = diseaseIndex.get(d);
        if (at !== undefined && perDisease[at] === 0) { perDisease[at] = 1; unionSize += 1; }
      }
    }
    let contexts = 0;
    for (let k = 0; k < perContext.length; k += 1) if (perContext[k] > 0) contexts += 1;
    // 池子的四条下限就地判掉：热路径上不另外摊一份 Set。
    const meets = picked.length >= floors.minSize
      && contexts >= floors.minContexts
      && (ddb === null || ((floors.minDiseases === null || unionSize >= floors.minDiseases)
        && (floors.maxDiseases === null || unionSize <= floors.maxDiseases)));
    last = { picked, attempts: t + 1, size: picked.length, contexts, diseaseUnion: ddb ? unionSize : null, meets };
    if (meets) return last;
    // 候选比十段还少而这一手也没凑够：再换起手也不会更多。
    if (kept.length < floors.minSize) break;
  }
  return last;
}

/** 这一级放宽收了多少条候选（只有报数时才数一遍，不进放池子的热路径）。 */
export function countCandidates(scored, keep) {
  const order = scoredOrder(scored);
  let n = 0;
  for (const i of order) if (keep(i)) n += 1;
  return n;
}

/**
 * **本局的池子**：从放宽阶梯的第一级往下走，取第一个同时满足三条下限的级别。
 *
 * 三条下限：池子 ≥ `quota.total` 段 · 跨 ≥ `ceil(quota.total / per_value_max)` 个地方 ·
 * 病并集在 `ddb.pool_rule` 的 2–4 之间。所以**任何已答前缀下都选得到十段**——
 * 玩家答什么都不会把路走死（owner 2026-09-27 第 5 条）。
 */
export function interviewPool(db, ddb, answers = {}) {
  const ladder = db.interview.pool.ladder;
  const scored = scoreAnswers(db, answers);
  const trail = [];
  for (const step of ladder) {
    const keep = levelPredicate(step.level, scored);
    const filled = fillPool(db, ddb, scored, keep);
    const row = {
      level: step.level,
      name: step.name,
      candidates: countCandidates(scored, keep),
      attempts: filled.attempts,
      size: filled.size,
      contexts: filled.contexts,
      diseaseUnion: filled.diseaseUnion,
      meets: filled.meets,
    };
    trail.push(row);
    if (row.meets) {
      const records = filled.picked.map((i) => scored.records[i]);
      return {
        ...row,
        records,
        ids: records.map((r) => r.id),
        ladder: trail,
        relaxed: step.level !== ladder[0].level,
      };
    }
  }
  const last = trail[trail.length - 1];
  const records = fillPool(db, ddb, scored, levelPredicate(last.level, scored))
    .picked.map((i) => scored.records[i]);
  return {
    ...last,
    records,
    ids: records.map((r) => r.id),
    ladder: trail,
    relaxed: false,
    meets: false,
  };
}

export const poolIdsFor = (db, ddb, answers = {}) => interviewPool(db, ddb, answers).ids;

/** 八问的答案闭集：每问几个取值（自检与文档用，跑一遍就能报数）。 */
export function answerCardinality(db) {
  return interviewQuestions(db).map((q) => {
    const spec = answerOptions(db, q);
    const subsets = spec.multi
      ? countSubsets(spec.values.length, spec.minItems, spec.maxItems)
      : spec.values.length;
    return { id: q.id, facet: q.facet, multi: spec.multi, values: spec.values.length, answers: subsets, matches: q.matches === true };
  });
}

function countSubsets(n, lo, hi) {
  let total = 0;
  for (let k = Math.max(0, lo); k <= Math.min(n, hi); k += 1) total += choose(n, k);
  return total;
}

function choose(n, k) {
  let out = 1;
  for (let i = 1; i <= k; i += 1) out = (out * (n - k + i)) / i;
  return Math.round(out);
}

/**
 * 一对互斥能不能出现在**同一个池子**里。
 *
 * 格退役之后，「跨格互斥是死条款」这句判据不再成立（池子不再是一个格，全库都可能进池），
 * 所以死条款的判据换成可算的那一条：**两条的病并集超过池子的病并集上界时，它们永远进不了
 * 同一个池子**（池子的病并集被 `ddb.pool_rule.diseases_max` 封顶）。这是格退役后唯一还
 * 成立的那种死条款，也是 `validate()` 报 `mutex_never_cooccurs` 的判据。
 */
export function mutexCanCoexist(db, ddb, idA, idB) {
  const max = ddb?.pool_rule?.diseases_max
  if (max === undefined || max === null) return true;
  const union = new Set([...byId(db, idA).diseases, ...byId(db, idB).diseases]);
  return union.size <= max;
}

/** 一个答案状态的稳定短哈希（抽样用，不参与任何机制）。 */
function stateHash(snapshot) {
  const text = JSON.stringify(Object.entries(snapshot).sort());
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

/**
 * **全部已答前缀**的实测（脚本与校验器共用这一处）。
 *
 * 每个状态跑一遍池子的放宽阶梯，报四件事：
 *   ① 分支总数 ② 需要放宽的分支数 ③ 最坏池子规模 ④ 最坏地方跨度。
 * 另外报池病并集的上下界与逐级的分布——「答什么都不锁死」这句话因此是可算的。
 *
 * 速度来自两点（语义一点没变）：一、相符掩码按「问 + 答案」缓存，所以每个状态只做
 * 若干次 288 长的整数加法；二、候选不落成数组，直接按有序下标放池子。
 */
export function poolCensus(db, ddb = null, { sample = 0 } = {}) {
  const qs = matchQuestions(db);
  const maskCache = new Map();
  const cachedMask = (q, value) => {
    const key = `${q.id}\u0000${JSON.stringify(value)}`;
    if (!maskCache.has(key)) maskCache.set(key, answerMask(db, q, value));
    return maskCache.get(key);
  };
  const records = db.experiences;

  let branches = 0;
  let relaxed = 0;
  let illegal = 0;
  let minSize = Infinity;
  let minContexts = Infinity;
  let maxUnion = 0;
  let minUnion = Infinity;
  let floorBreaks = 0;
  let seedRetries = 0;
  let sampledOut = 0;
  let tested = 0;
  let worstSize = null;
  let worstContexts = null;
  const levelCounts = {};
  const answers = {};

  const walk = (i) => {
    if (i === qs.length) {
      const snapshot = { ...answers };
      if (answersForceCombos(db, snapshot).length > 0) { illegal += 1; return; }
      branches += 1;
      // 抽样模式：已答 ≤ 2 问的**全部**状态照跑（它们覆盖每一个取值与每一对问），
      // 其余按稳定哈希抽 1/sample。默认全枚举（sample 0），抽样只给校验器的默认档用。
      if (sample > 0 && qs.filter((q) => isAnswered(snapshot, q.facet)).length > 2
        && stateHash(snapshot) % sample !== 0) {
        sampledOut += 1;
        return;
      }
      tested += 1;
      const dims = qs.filter((q) => isAnswered(snapshot, q.facet))
        .map((q) => ({ facet: q.facet, mask: cachedMask(q, snapshot[q.facet]) }));
      const hits = new Uint8Array(records.length);
      for (const d of dims) {
        for (let k = 0; k < hits.length; k += 1) hits[k] += d.mask[k];
      }
      const scored = { records, hits, dims, answered: dims.length };
      let pool = null;
      for (const step of db.interview.pool.ladder) {
        const filled = fillPool(db, ddb, scored, levelPredicate(step.level, scored));
        pool = {
          size: filled.size,
          contexts: filled.contexts,
          diseaseUnion: filled.diseaseUnion,
          level: step.level,
          name: step.name,
          attempts: filled.attempts,
          meets: filled.meets,
          relaxed: step.level !== db.interview.pool.ladder[0].level,
        };
        if (filled.meets) break;
      }
      if (pool.relaxed) relaxed += 1;
      if (pool.attempts > 1) seedRetries += 1;
      if (!pool.meets) floorBreaks += 1;
      levelCounts[pool.level] = (levelCounts[pool.level] ?? 0) + 1;
      if (pool.size < minSize) { minSize = pool.size; worstSize = { answers: snapshot, pool }; }
      if (pool.contexts < minContexts) { minContexts = pool.contexts; worstContexts = { answers: snapshot, pool }; }
      if (pool.diseaseUnion !== null) {
        maxUnion = Math.max(maxUnion, pool.diseaseUnion);
        minUnion = Math.min(minUnion, pool.diseaseUnion);
      }
      return;
    }
    const q = qs[i];
    const spec = answerOptions(db, q);
    const domain = [null];
    if (!spec.multi) {
      for (const v of spec.values) domain.push(v.id);
    } else {
      const ids = spec.values.map((v) => v.id);
      for (let mask = 0; mask < (1 << ids.length); mask += 1) {
        const pick = ids.filter((_, k) => (mask >> k) & 1);
        if (pick.length < spec.minItems || pick.length > spec.maxItems) continue;
        domain.push(pick);
      }
    }
    for (const value of domain) {
      if (value === null) delete answers[q.facet];
      else answers[q.facet] = value;
      walk(i + 1);
    }
    delete answers[q.facet];
  };
  walk(0);

  return {
    questions: qs.map((q) => q.facet),
    /** ① 分支总数（合法答案状态；「还没答」也算一种前缀） */
    branches,
    /** 被非法组合判掉的状态（不在按钮上出现，所以不算分支） */
    illegalStates: illegal,
    /** 抽样模式：真正跑过池子的分支数（全枚举模式下 = branches） */
    testedBranches: tested,
    /** 抽样模式：被抽样漏掉的分支数 */
    sampledOut,
    /** ② 需要放宽的分支数（跳过了「每一问都相符」那一级） */
    relaxedBranches: relaxed,
    levelCounts,
    /** 起手种子换过的分支数 */
    seedRetries,
    /** ③ 最坏池子规模 */
    minSize: minSize === Infinity ? 0 : minSize,
    /** ④ 最坏地方跨度 */
    minContexts: minContexts === Infinity ? 0 : minContexts,
    minDiseaseUnion: minUnion === Infinity ? 0 : minUnion,
    maxDiseaseUnion: maxUnion,
    /** 池子撑不起一局的分支数（应为 0） */
    floorBreaks,
    worstSize,
    worstContexts,
  };
}

/**
 * 池子里的取舍力：一池最多能认下几段。
 *
 * 只有配额约束（`mutex` 已退役为空）时这是**精确值**：
 * `Σ_v min(上限, 池内该取值条数)`，再被总额封顶。它与"已经选了什么"无关——
 * `Σ_v min(cap_v − used_v, n_v − used_v) = Σ_v min(cap_v, n_v) − |S|`（|S| ≤ cap_v 时），
 * 右边与 S 无关，所以"还能不能补满"是个**静态量**。运行期仍保留 `would_deadlock`
 * 作兜底：数据结构一旦变化，它立刻会响。
 * ⚠️ 若将来重新引入互斥，本函数退化为**上界**（互斥只会让真实值更小），
 * 此时可完成性由 `canStillComplete` 的贪心兜底负责。
 */
export function maxSelectable(db, poolIds) {
  const facet = db.quota.per_facet;
  const count = {};
  for (const id of poolIds) {
    const v = byId(db, id)[facet];
    count[v] = (count[v] || 0) + 1;
  }
  const sum = valuesOf(db, facet).reduce((s, v) => s + Math.min(db.quota.per_value_max, count[v] || 0), 0);
  return Math.min(db.quota.total, sum);
}

// ── 配额与选择合法性 ─────────────────────────────────────────────────────
export function quotaState(db, selectedIds) {
  const facet = db.quota.per_facet;
  const byValue = {};
  for (const id of selectedIds) {
    const v = byId(db, id)[facet];
    byValue[v] = (byValue[v] || 0) + 1;
  }
  return {
    facet,
    used: selectedIds.length,
    total: db.quota.total,
    remaining: db.quota.total - selectedIds.length,
    byValue,
    perValueMax: db.quota.per_value_max,
  };
}

/** 互斥是无向 pair，对称性由数据结构保证，不需要两处维护。 */
export const mutexNeighbors = (db, id) =>
  db.mutex.filter((p) => p.includes(id)).map((p) => (p[0] === id ? p[1] : p[0]));

/**
 * 从当前选择出发，是否还能补满配额。`poolIds` 给出**本局的池子**（问诊筛出来的那一池）；
 * 省略表示整个库都可选（旧口径，仍被属性结算与校验器使用）。
 *
 * 注意：本作**不要求**每个取值都选满（没有下限），所以可行性判据是
 *   Σ_v min(该取值剩余容量, 该取值在池子里还没选的条数) ≥ 还需要的段数
 * 而不是"每一档都必须够"。`mutex` 退役为空时上式是**精确判据**（静态量，见
 * `maxSelectable` 的推导）；一旦有人重新引入互斥，就退回贪心模拟：按"稀缺取值优先"
 * 推进，并把逐次选择的互斥封锁一起算进去——它可能比真实可行域更保守，但绝不会
 * 放行不可行的选择。每次点击另有 `canSelect` 复核，所以不会把玩家卡死。
 */
export function canStillComplete(db, selectedIds, poolIds = null) {
  const remaining = db.quota.total - selectedIds.length;
  if (remaining <= 0) return true;

  const sel = new Set(selectedIds);
  const pool = poolIds === null ? db.experiences.map((r) => r.id) : poolIds;
  const facet = db.quota.per_facet;
  const cap = db.quota.per_value_max;

  if (db.mutex.length === 0) {
    const used = {};
    for (const id of selectedIds) used[byId(db, id)[facet]] = (used[byId(db, id)[facet]] || 0) + 1;
    const left = {};
    for (const id of pool) {
      if (sel.has(id)) continue;
      const v = byId(db, id)[facet];
      left[v] = (left[v] || 0) + 1;
    }
    const room = valuesOf(db, facet).reduce(
      (s, v) => s + Math.min(Math.max(0, cap - (used[v] || 0)), left[v] || 0),
      0,
    );
    return room >= remaining;
  }

  const capacity = {};
  for (const v of valuesOf(db, facet)) capacity[v] = cap;
  for (const id of selectedIds) capacity[byId(db, id)[facet]] -= 1;

  const blocked = new Set();
  for (const id of selectedIds) for (const nb of mutexNeighbors(db, id)) blocked.add(nb);

  const avail = pool.filter((id) => !sel.has(id) && !blocked.has(id)).map((id) => byId(db, id));
  let taken = 0;

  while (taken < remaining) {
    const counts = {};
    for (const r of avail) counts[r[facet]] = (counts[r[facet]] || 0) + 1;
    let best = null;
    let bestCount = Infinity;
    for (const [v, n] of Object.entries(counts)) {
      if (capacity[v] > 0 && n < bestCount) {
        bestCount = n;
        best = v;
      }
    }
    if (best === null) return false;

    const idx = avail.findIndex((r) => r[facet] === best);
    const pick = avail.splice(idx, 1)[0];
    capacity[best] -= 1;
    taken += 1;

    for (const nb of mutexNeighbors(db, pick.id)) blocked.add(nb);
    for (let i = avail.length - 1; i >= 0; i -= 1) {
      if (blocked.has(avail[i].id)) avail.splice(i, 1);
    }
  }
  return true;
}

/**
 * 界面拿这个决定卡片是否灰掉，以及灰掉的理由文案。
 * 传了 `poolIds` 时，池子外的记录不是"灰掉"，而是**根本不出现在屏幕上**——
 * 这个理由码是给"改了答案以后旧选择失效"这类情况兜底用的。
 */
export function canSelect(db, selectedIds, candidateId, poolIds = null) {
  const reasons = [];
  const r = byId(db, candidateId);
  const q = quotaState(db, selectedIds);
  const facet = db.quota.per_facet;
  const v = r[facet];

  if (poolIds !== null && !poolIds.includes(candidateId)) reasons.push({ code: 'not_in_pool' });
  if (selectedIds.includes(candidateId)) reasons.push({ code: 'already_selected' });
  if (q.remaining <= 0) reasons.push({ code: 'quota_total_full' });
  if ((q.byValue[v] || 0) >= db.quota.per_value_max) {
    reasons.push({
      code: 'quota_value_full',
      facet,
      value: v,
      label: labelOf(db, facet, v),
      max: db.quota.per_value_max,
    });
  }
  const hits = mutexNeighbors(db, candidateId).filter((x) => selectedIds.includes(x));
  if (hits.length) reasons.push({ code: 'mutex', with: hits });

  if (reasons.length === 0 && !canStillComplete(db, [...selectedIds, candidateId], poolIds)) {
    reasons.push({ code: 'would_deadlock' });
  }
  return { ok: reasons.length === 0, reasons };
}

// ── 结算 ─────────────────────────────────────────────────────────────────
export function bandOf(db, score) {
  const t = db.bands.tiers.find((b) => score >= b.min && score <= b.max);
  if (!t) {
    throw new Error(
      `分数 ${score} 无对应档位（档位表未覆盖 ${db.attribute_bounds.min}–${db.attribute_bounds.max}）`,
    );
  }
  return { id: t.id, ordinal: t.ordinal, label: t.label };
}

/** 所有数值只来自 records 的 effects 与配置块；本函数里没有任何增量字面量。 */
export function settleAttributes(db, selectedIds, base = db.base_attributes) {
  const raw = {};
  for (const k of db.attributes.ids) raw[k] = base[k];
  for (const id of selectedIds) {
    for (const [k, d] of Object.entries(byId(db, id).effects.attributes)) raw[k] += d;
  }
  const { min, max } = db.attribute_bounds;
  const clamped = {};
  const band = {};
  const overflow = {};
  for (const k of db.attributes.ids) {
    clamped[k] = Math.min(max, Math.max(min, raw[k]));
    overflow[k] = raw[k] - clamped[k];
    band[k] = bandOf(db, clamped[k]);
  }
  const totalRaw = db.attributes.ids.reduce((s, k) => s + raw[k], 0);
  return { raw, clamped, band, overflow, totalRaw };
}

/** 镜子屏的人生线：先按「从什么时候开始」，再按「多久」，最后按 id 稳定排序。 */
export function timeline(db, selectedIds) {
  const onset = valuesOf(db, 'onset');
  const span = valuesOf(db, 'duration_span');
  return selectedIds
    .map((id) => byId(db, id))
    .sort(
      (a, b) =>
        onset.indexOf(a.onset) - onset.indexOf(b.onset) ||
        span.indexOf(a.duration_span) - span.indexOf(b.duration_span) ||
        a.id.localeCompare(b.id),
    );
}

// ── 疾病 ─────────────────────────────────────────────────────────────────
/**
 * 候选 = 已选经历指向的病 id 的并集。
 * 名册在 data/diseases.json（邻居契约），所以 ddb 由调用方传入；
 * 固有项（always_on）不是候选，不进并集。
 */
export function diseaseCandidates(db, ddb, selectedIds) {
  const hit = new Set();
  for (const id of selectedIds) for (const d of byId(db, id).diseases) hit.add(d);
  return ddb.items
    .filter((d) => d.always_on !== true && hit.has(d.id))
    .map((d) => ({ ...d, from: selectedIds.filter((id) => byId(db, id).diseases.includes(d.id)) }));
}

/**
 * 调参用：候选并集有多大。
 * 若 sampleUnion 接近名册规模，「只能在候选里选」就几乎没有约束力——需要扩容名册
 * 或让每条记录只指向更少的疾病。
 */
export function diseaseCoverage(db, ddb) {
  const perDisease = {};
  const roster = ddb.items.filter((r) => r.always_on !== true);
  for (const d of roster) perDisease[d.id] = 0;
  for (const r of db.experiences) {
    for (const d of r.diseases) perDisease[d] = (perDisease[d] || 0) + 1;
  }
  const unionOf = (ids) => new Set(ids.flatMap((id) => byId(db, id).diseases)).size;
  const sample = db.experiences.slice(0, db.quota.total).map((r) => r.id);
  return {
    perDisease,
    roster: roster.length,
    sampleUnion: unionOf(sample),
  };
}

// ── 契约校验（开发期用；不是门禁，没有任何 CI 在跑它） ────────────────────
export function validate(db, ddb = null) {
  const errors = [];
  const warnings = [];
  const E = (code, detail) => errors.push({ code, detail });
  const W = (code, detail) => warnings.push({ code, detail });

  const V = db.vocab;
  const facets = Object.keys(V);
  const attrIds = db.attributes.ids;
  const used = Object.fromEntries(facets.map((f) => [f, new Set()]));
  const ids = new Set();
  const tomb = new Set(db.tombstones || []);

  const banned = [...(db.text_lint.extra_banned || [])];
  for (const f of db.text_lint.from_label_facets) {
    for (const v of V[f].values) banned.push(v.label, v.id);
  }

  // 词表自身
  for (const f of facets) {
    const s = V[f];
    if (!s.ask || !String(s.ask).trim()) E('facet_without_ask', f);
    if (!s.values || !s.values.length) E('facet_without_values', f);
    const seen = new Set();
    for (const v of s.values || []) {
      if (seen.has(v.id)) E('vocab_value_duplicate', `${f}=${v.id}`);
      seen.add(v.id);
      if (!v.label) E('vocab_value_without_label', `${f}=${v.id}`);
      if (/unknown|unspecified|tbd|todo|待定/i.test(v.id)) E('vocab_wildcard_forbidden', `${f}=${v.id}`);
      if (v.id === 'none' && v.label !== '不适用') E('none_label_inconsistent', `${f}=${v.label}`);
    }
    if (s.multi) {
      if (!(s.min_items >= 0) || !(s.max_items >= s.min_items)) E('facet_items_range', f);
      if ((s.values || []).some((v) => v.id === 'none')) E('multi_facet_has_none_value', f);
      // 允许空数组的多值 facet（如「和谁」= 一个人）必须给出空值怎么念，
      // 否则卡面上会出现一个没有内容的行。
      if (s.min_items === 0 && !s.empty_label) E('multi_facet_without_empty_label', f);
    }
  }

  // 配置块：每个含数值的块必须能追溯来源
  for (const p of ['effects_rule', 'attribute_bounds', 'base_attributes', 'quota', 'bands', 'interview']) {
    if (!db[p] || !db[p].source || !String(db[p].source).trim()) E('config_without_source', p);
  }

  // 病历外壳：这一张病例单的文书栏（页眉一般情况 / 栏目与每一笔 / 落款）。
  // 栏目名与笔迹写法是玩家看得见的文案，所以和 interview.screen 同一套纪律：
  // 缺一条就报错，内部实现词一个都不许出现。
  const shell = db.record_shell;
  if (!shell) E('record_shell_missing', 'record_shell');
  else {
    for (const p of ['ask', 'source']) {
      if (!shell[p] || !String(shell[p]).trim()) E('record_shell_without_source', p);
    }
    for (const p of ['ink', 'fill', 'general', 'paper', 'sign']) {
      if (!shell[p]) E('record_shell_block_missing', p);
    }
    // 「谁落笔」与「谁可改」都是闭集，值必须登记在 `fill` 词表里——
    // 「这一栏玩家能不能填」不许只活在散文或界面代码的判断里。
    const fills = Object.keys(shell.fill ?? {});
    if (!fills.includes('system') || !fills.includes('patient_input')) {
      E('record_shell_fill_axis_missing', fills.join(',') || '(空)');
    }
    const charVocab = db.character_vocab ?? {};
    const namePool = db.character_source?.name_pool;
    const charFields = shell.character?.fields;
    const inks = Object.keys(shell.ink ?? {});
    for (const [i, row] of (shell.general ?? []).entries()) {
      const at = `general[${i}]`;
      if (!row.label || (row.value === undefined && row.value_from_source === undefined)) {
        E('record_shell_row_incomplete', at);
      }
      // 笔迹标注不许出现未登记的值。阶段 1 报 `record_shell_ink_unknown`，阶段 2 把
      // 「谁的笔迹」=`who` 明确成落笔表的一根轴；两个码同时报，免得既有消费方踩空。
      if (!inks.includes(row.who)) {
        E('record_shell_ink_unknown', `${at}.who=${row.who}`);
        E('record_shell_row_by_unknown', `${at}=${row.who}`);
      }
      if (!fills.includes(row.fill)) E('record_shell_row_fill_unknown', `${at}=${row.fill}`);
      if (row.fill === 'patient_input' && row.who !== 'patient') {
        E('record_shell_row_source_not_patient', `${at}.fill=patient_input who=${row.who}`);
      }
      if (!row.blank) E('record_shell_row_without_blank', at);
      // 笔迹与落笔必须同在患者侧：`who` = 谁的笔迹，`fill` = 这支笔现在能不能落。
      // 患者侧那一半的值可以现算（字面值只是没落笔时显示的那个）。来源必须登记过，
      // 否则界面会从空气里取值。
      if (row.value_from_source) {
        const known = row.value_from_source === 'name'
          ? Boolean(namePool)
          : Object.keys(charVocab).includes(row.value_from_source);
        if (!known) E('record_shell_row_source_unknown', `${at}.value_from_source=${row.value_from_source}`);
      }
      // 院方那一半是**永不由玩家书写**的：它只能写成字面值，不许有来源，也不许
      // 记在一个玩家能改的落笔上。这条是自建人物不打穿《无法离开医院》②
      // 「身份黏着」的机械判据——玩家能写的那一半与院方写的那一半在数据上分开。
      const hospitalSide = row.value_to !== undefined || row.value_to_source !== undefined;
      if (!hospitalSide) continue;
      if (row.who !== 'hospital') E('record_shell_hospital_side_not_hospital', `${at} who=${row.who}`);
      if (row.fill !== 'system') E('record_shell_hospital_side_writable', `${at} fill=${row.fill}`);
      if (row.value_to_source !== undefined) E('record_shell_hospital_side_from_source', `${at}.value_to_source`);
      if (!row.value_to) E('record_shell_hospital_side_missing', at);
    }

    // 页眉上必须**存在**院方写的那一半。只核"有院方侧的行对不对"是不够的：
    // 把 `value_to` 整笔删掉，那一笔就退化成普通患者行，上面四条一条都不会响，
    // 而《无法离开医院》② 身份黏着的物证（自述 ≠ 院方记录）已经从病历上消失。
    // 🔧 2026-09-27 补：反例实测漏网，见 design/presentation/开局病历填报.md §十二.3。
    const hospitalHalf = (shell.general ?? []).filter(
      (r) => r.value_to !== undefined || r.value_to_source !== undefined,
    );
    if (!hospitalHalf.length) E('record_shell_hospital_side_absent', '页眉没有任何一笔写院方记录');

    // 自述可达的名字集**不许**与院方记录的名字相交。相交 = 玩家能把自己报成院方那个人，
    // 身份黏着在结构上就没了（owner 2026-09-27：院方那一半永不由玩家写）。
    // 判据是可算的：姓名池的笛卡尔积 ∩ { 院方名字 } = ∅。
    const identity = db.character_source?.identity;
    if (identity?.hospital_name && namePool?.surname?.values?.length && namePool?.given?.values?.length) {
      const reachable = new Set();
      for (const s of namePool.surname.values) {
        for (const g of namePool.given.values) reachable.add(`${s}${g}`);
      }
      if (reachable.has(identity.hospital_name)) {
        E('character_name_hits_hospital_identity', `${identity.hospital_name} 可由姓名池拼出`);
      }
    }

    // 「可填」的前提是**有闭集可填**：一笔标成 `patient_input`，就必须绑到一条
    // 有枚举取值的轴上（姓名走 name_pool，其余走 character_vocab）。没绑上的那笔
    // 只可能由界面自己想办法凑值——那就是自由书写的入口，正是红线要拦的东西。
    for (const [i, row] of (shell.general ?? []).entries()) {
      if (row.fill !== 'patient_input') continue;
      const bound = (charFields ?? []).find((f) => rowOfCharacterField(shell, f) === row);
      const enumerable = bound
        ? (bound.value_source === 'name'
          ? Boolean(namePool?.surname?.values?.length && namePool?.given?.values?.length)
          : Boolean(charVocab[bound.vocab ?? bound.key]?.values?.length))
        : false;
      if (!enumerable) E('record_shell_row_without_closed_set', `general[${i}]=${row.label}`);
    }
    const seenCharKeys = new Set();
    for (const [i, f] of (charFields ?? []).entries()) {
      const at = `character.fields[${i}]`;
      if (!f.key || !f.label) E('character_field_incomplete', at);
      if (seenCharKeys.has(f.key)) E('character_field_duplicate', f.key);
      seenCharKeys.add(f.key);
      if (!fills.includes(f.fill)) E('record_shell_row_fill_unknown', `${at}=${f.fill}`);
      // 一笔的取值闭集登记在 character_vocab 的哪一项上：默认同名，姓名那笔
      // 另有 name_pool 兜底，所以显式记在 `vocab` 键上（closes the gap 三个栏目例外）。
      const axisKey = f.vocab ?? f.key;
      const axis = charVocab[axisKey];
      // 自建人物可落笔的每一笔，取值必须来自一个可枚举的闭集；给不出闭集的
      // （职业 / 婚姻 : 一手来源没给取值枚举）就只能留在 `system`，显示为未填。
      // 这样「没有自由文本输入」不是靠界面自觉，而是数据上就填不出来。
      if (f.fill !== 'patient_input') continue;
      const enumerable = f.value_source === 'name'
        ? Boolean(namePool?.surname?.values?.length && namePool?.given?.values?.length)
        : Boolean(axis?.values?.length);
      if (!enumerable) E('character_field_without_closed_set', `${at} key=${f.key}`);
      if (f.value_source !== 'name' && axis === undefined) E('character_field_without_vocab', f.key);
      if (axis && axis.open_to_player === false) E('character_field_axis_closed', f.key);
      const bound = rowOfCharacterField(shell, f);
      if (bound === null) E('character_field_without_row', f.key);
      // 可落的笔必须在页眉上有一条能显示它的行：没行 = 玩家选了也看不见，
      // 或者报了名字而病历上不写——两种都是形态坏掉。
      if (bound !== null && f.fill === 'patient_input' && bound.value_from_source !== f.value_source) {
        E('character_field_row_mismatch', `${f.key} → ${bound.label}`);
      }
      // 页眉那一笔自己必须有一个回落值（正典字面值），否则自建 / 正典两条路都会空着。
      if (bound !== null && bound.value === undefined && bound.value_from_source !== f.value_source) {
        E('record_shell_row_incomplete', `${f.key} → ${bound.label}`);
      }
    }
    // 闭集反向核：character_vocab 里每一条都要有引用方，否则就是自造的死词表。
    // 'name_choice' 由姓名选择控件（name_pool）承担，'onset' / 'duration_pattern'
    // 由主诉的拼句承担——三者在下方一并核。
    const referenced = new Set((charFields ?? []).map((f) => f.vocab ?? f.key).filter(Boolean));
    referenced.add('name_choice');
    if (db.complaint?.duration_pattern) referenced.add('duration_pattern');
    if ((shell.general ?? []).some((r) => r.value_from_source === 'onset')) referenced.add('onset');
    for (const key of Object.keys(charVocab)) {
      if (key === 'ask') continue;
      if (!referenced.has(key)) E('character_vocab_unreferenced', key);
    }

    // ── 病历单（paper）：栏目顺序 · 每一笔的落笔方 · 空白态 ──────────────
    // 五屏与步条已退役（owner 2026-09-27 第 3 条：不要照搬旧页面格式），
    // 结构与纪律一并搬到这张纸上：栏名、栏目数、每笔谁落笔、可填的笔必有闭集。
    const paperCols = shell.paper?.columns ?? [];
    if (!shell.paper) E('record_shell_block_missing', 'paper');
    else {
      if (!shell.paper.title) E('record_shell_paper_title_missing', 'paper.title');
      const writeSources = Object.keys(shell.paper.write_sources ?? {});
      const colIds = paperCols.map((c) => c.id);
      for (const id of shell.paper.required ?? []) {
        if (!colIds.includes(id)) E('paper_column_missing', id);
      }
      if (new Set(colIds).size !== colIds.length) E('paper_column_duplicate', colIds.join(','));
      for (const [i, col] of paperCols.entries()) {
        const at = `paper.columns[${i}]`;
        if (!col.id || !col.label || !col.basis) E('paper_column_incomplete', at);
        if (!col.writes_ref && !(col.writes ?? []).length) E('paper_column_without_writes', at);
        if (col.writes_ref && !shell[col.writes_ref]) E('paper_column_writes_ref_unknown', `${at}=${col.writes_ref}`);
        for (const [j, w] of (col.writes ?? []).entries()) {
          const wat = `${at}.writes[${j}]`;
          if (!w.label || !w.who || !w.fill || !w.from) E('paper_write_incomplete', wat);
          if (!inks.includes(w.who)) E('record_shell_ink_unknown', `${wat}.who=${w.who}`);
          if (!fills.includes(w.fill)) E('record_shell_row_fill_unknown', `${wat}=${w.fill}`);
          if (w.blank === undefined && w.blank_from === undefined) E('paper_write_without_blank', wat);
          if (w.blank !== undefined && w.blank_from !== undefined) E('paper_write_two_blanks', wat);
          if (w.blank_from && !blankFromResolves(db, w.blank_from)) {
            E('paper_blank_source_unknown', `${wat}=${w.blank_from}`);
          }
          // 院方那一笔永不由玩家落笔：落笔方与笔迹必须同在院方侧（与页眉同一条判据）。
          if (w.who === 'hospital' && w.fill !== 'system') E('record_shell_hospital_side_writable', wat);
          // 可填的笔必须指到一个**闭集**：要么是问诊的一问（答案来自 vocab），要么是
          // write_sources 里登记过、且写明闭集的那一个。给不出闭集的笔不许标成可填。
          if (w.fill === 'patient_input') {
            const isQuestion = questionById(db, w.from) !== null;
            const src = shell.paper.write_sources?.[w.from];
            if (!isQuestion && !src) E('paper_write_unknown_source', `${wat}=${w.from}`);
            // 「可填」的前提是**有闭集可填**：来源表上 `closed: false` 的那一个（未写）
            // 没有闭集，所以它那一笔永远不许标成可填。
            else if (!isQuestion && src.closed !== true) E('paper_write_without_closed_set', `${wat}=${w.from}`);
          } else if (!writeSources.includes(w.from) && questionById(db, w.from) === null) {
            E('paper_write_unknown_source', `${wat}=${w.from}`);
          }
        }
      }
    }

    for (const { path, text } of collectStrings(shell)) {
      // 依据表（source / ask / column_sources / character_vocab_gaps）是给 owner 与校验器
      // 看的元数据，不上屏；它们要能自由使用「字段」「维度」这类词来描述契约本身。
      if (META_COPY_PATHS.some((re) => re.test(path))) continue;
      for (const w of INTERNAL_COPY_WORDS) {
        if (text.includes(w)) E('record_shell_copy_leaks_internal', `${path} 含「${w}」`);
      }
    }
    // 同一套纪律也得管阶段 2 新加的两块上屏文案：人物来源的界面文案与自建人物的
    // 闭集标签（性别 / 姓 / 名），以及问诊块（每一问的问法与屏文案）。它们不在
    // record_shell 里，上面那次扫描扫不到——**新增一块上屏数据就同步挂进扫描**。
    for (const [block, code, keys] of [
      [db.character_source, 'character_copy_leaks_internal', true],
      [db.character_vocab, 'character_copy_leaks_internal', true],
      [db.complaint, 'complaint_copy_leaks_internal', true],
      // 问诊块的**键名**是契约名（questions / matches / ladder / facet…），一个都不上屏；
      // 要干净的是它的字符串**取值**（医生的问法、按钮文案、放宽级别的名字）。
      // 病历外壳那边仍然连键名一起扫——那里的键（`value_to`）自己会变成标签。
      [db.interview, 'interview_copy_leaks_internal', false],
    ]) {
      if (!block) continue;
      for (const { path, text } of collectStrings(block, '', { keys })) {
        if (META_COPY_PATHS.some((re) => re.test(path))) continue;
        for (const w of INTERNAL_COPY_WORDS) {
          if (text.includes(w)) E(code, `${path} 含「${w}」`);
        }
      }
    }
    for (const p of ['consent', 'historian', 'clinician', 'pending']) {
      if (!shell.sign?.[p]) E('record_shell_sign_missing', p);
    }
  }

  // 人物来源：默认来源必须真的登记在册，且登记表上只有一个键能当 source 之外的用途。
  const src = db.character_source;
  if (src) {
    if (!src.characters?.[src.default]) E('character_source_unknown', String(src.default));
    if (!src.characters?.custom) E('character_source_missing', 'custom');
    if (!src.identity?.hospital_name || !src.identity?.hospital_number) {
      E('character_identity_missing', 'identity');
    }
    if (!src.name_pool?.surname?.values?.length || !src.name_pool?.given?.values?.length) {
      E('character_name_pool_empty', 'name_pool');
    }
  }

  // 主诉的拼句表必须与词表**一一对应**：少一档就拼不出那一路的主诉，
  // 多一档就是自造的取值（两条都在 complaint_validator 里报）。
  const cmp = db.complaint;
  if (cmp) {
    for (const [facet, key] of [['onset', 'onset'], ['duration_pattern', 'duration_pattern']]) {
      const want = valuesOf(db, facet).slice().sort().join(',');
      const got = Object.keys(cmp[key] ?? {}).sort().join(',');
      if (want !== got) E('complaint_values_mismatch', `${key}: ${got} ≠ ${want}`);
    }
  }

  // 输出槽：恰好一个。多于一个会让「留下了什么」一节不知道该取哪个；
  // 零个会让它空着。标在 vocab 的 output 字段上，不写死在代码里。
  const outputs = facets.filter((f) => V[f].output === true);
  if (outputs.length !== 1) E('output_facet_count', `output=true 的 facet 有 ${outputs.length} 个（应为 1）`);

  // 配额轴
  const qf = db.quota.per_facet;
  if (!V[qf]) E('quota_facet_unknown', qf);
  else if (V[qf].multi) E('quota_facet_multi', qf);
  else {
    const valueCount = V[qf].values.length;
    const cap = db.quota.per_value_max * valueCount;
    if (cap < db.quota.total) {
      E('quota_infeasible', `${db.quota.per_value_max}×${valueCount}=${cap} < total ${db.quota.total}`);
    }
    if (cap === db.quota.total) {
      W(
        'quota_forces_full_domains',
        `上限×取值数恰等于总额（${cap}=${db.quota.total}）——玩家必须把每个取值都选满，没有偏科自由`,
      );
    }
  }

  // 记录
  for (const r of db.experiences) {
    const w = r.id || '(缺 id)';
    if (!ID_PATTERN.test(r.id || '')) E('id_format', w);
    if (ids.has(r.id)) E('id_duplicate', w);
    ids.add(r.id);
    if (tomb.has(r.id)) E('id_reused', w);

    for (const k of META_KEYS) if (!(k in r)) E('record_missing_field', `${w}.${k}`);
    for (const k of Object.keys(r)) {
      if (!facets.includes(k) && !META_KEYS.includes(k)) E('record_unknown_field', `${w}.${k}`);
    }

    for (const f of facets) {
      const s = V[f];
      const v = r[f];
      if (v === undefined) {
        E('record_missing_facet', `${w}.${f}`);
        continue;
      }
      const mark = (x) => {
        if (s.values.some((y) => y.id === x)) used[f].add(x);
        else E('value_not_in_vocab', `${w}.${f}=${x}`);
      };
      if (s.multi) {
        if (!Array.isArray(v)) {
          E('facet_type', `${w}.${f} 应为数组`);
          continue;
        }
        if (v.length < s.min_items || v.length > s.max_items) E('facet_item_count', `${w}.${f} n=${v.length}`);
        if (new Set(v).size !== v.length) E('facet_duplicate_value', `${w}.${f}`);
        v.forEach(mark);
      } else {
        if (Array.isArray(v)) {
          E('facet_type', `${w}.${f} 应为单值`);
          continue;
        }
        mark(v);
      }
    }

    // 属性负载
    const eff = r.effects && r.effects.attributes;
    if (!eff || typeof eff !== 'object' || Array.isArray(eff)) {
      E('effects_shape', w);
    } else {
      const terms = Object.entries(eff);
      if (terms.length < 1 || terms.length > db.effects_rule.max_terms) {
        E('effects_term_count', `${w} n=${terms.length}`);
      }
      let sum = 0;
      for (const [k, d] of terms) {
        if (!attrIds.includes(k)) E('effects_unknown_attribute', `${w}.${k}`);
        if (!Number.isInteger(d) || d === 0 || Math.abs(d) > db.effects_rule.max_abs_term) {
          E('effects_term_range', `${w}.${k}=${d}`);
        }
        sum += d;
      }
      if (sum !== db.effects_rule.net) E('effects_net', `${w} sum=${sum}`);
      // 「留下了什么」里有「能力」⟺ 这条记录真的动了属性。两边必须同进同出。
      const outId = outputs[0];
      const hasAbility = outId !== undefined && Array.isArray(r[outId]) && r[outId].includes('ability');
      if (hasAbility !== terms.length > 0) E('ability_channel_mismatch', w);
    }

    // 疾病引用
    if (!Array.isArray(r.diseases) || !r.diseases.length) E('record_without_disease', w);
    else {
      for (const d of r.diseases) {
        if (ddb && !ddb.items.some((x) => x.id === d)) E('disease_unknown', `${w}->${d}`);
      }
    }

    // 文本 lint：语义不许藏在人类可读文本里
    for (const k of ['title', 'summary']) {
      const t = r[k];
      if (typeof t !== 'string' || !t.trim()) {
        E('text_missing', `${w}.${k}`);
        continue;
      }
      if (db.text_lint.forbid_digits && /[0-9０-９]/.test(t)) E('text_has_digit', `${w}.${k}`);
      const max = db.text_lint[k === 'title' ? 'title_max' : 'summary_max'];
      if (typeof max === 'number' && [...t].length > max) E('text_too_long', `${w}.${k} ${[...t].length} > ${max}`);
      for (const b of banned) if (t.includes(b)) E('text_has_facet_word', `${w}.${k} 含「${b}」`);
    }
  }

  // 死值：词表里没有任何记录用到的取值
  for (const f of facets) {
    for (const v of V[f].values) if (!used[f].has(v.id)) E('dead_value', `${f}=${v.id}`);
  }

  // 非法组合
  for (const fc of db.forbidden_combos) {
    for (const r of db.experiences) {
      if (fc.when.every((c) => clauseHits(r, c))) E('forbidden_combo', `${fc.id} 命中 ${r.id}`);
    }
  }

  // 互斥
  const pair = new Set();
  for (const p of db.mutex) {
    if (!Array.isArray(p) || p.length !== 2 || p[0] === p[1]) {
      E('mutex_shape', JSON.stringify(p));
      continue;
    }
    const key = [...p].sort().join('|');
    if (pair.has(key)) E('mutex_duplicate', key);
    pair.add(key);
    for (const x of p) if (!ids.has(x)) E('mutex_unknown_id', x);
    // 池子不再是「一个格」：全库都可能进池，所以死条款的判据换成可算的那一条——
    // **两条的病并集超过池子的病并集上界时，它们永远进不了同一个池子**（见 mutexCanCoexist）。
    // `mutex` 现为空，所以这条判据平时不花任何代价。
    if (ids.has(p[0]) && ids.has(p[1]) && db.interview && !mutexCanCoexist(db, ddb, p[0], p[1])) {
      E('mutex_never_cooccurs', `${key}：两条的病并集超过池子的病并集上界，永远进不了同一个池子`);
    }
  }

  // 配额可填性 + 存在一个合法的满额选择
  if (V[qf] && !V[qf].multi) {
    const values = valuesOf(db, qf);
    const count = {};
    for (const r of db.experiences) count[r[qf]] = (count[r[qf]] || 0) + 1;
    for (const v of values) {
      const n = count[v] || 0;
      if (n === 0) E('quota_value_unfillable', v);
      else if (n < db.quota.per_value_max) {
        W('quota_value_below_cap', `${v} n=${n} < 上限 ${db.quota.per_value_max}（该取值选不满上限）`);
      }
    }
    if (!canStillComplete(db, [])) {
      E('quota_no_feasible_selection', `从空选择出发存在不了满额 ${db.quota.total} 段的合法选择`);
    }
  }

  // 名册与视图
  // 死病与「每条病被几条经历指向」由 diseases.js 的 validateDiseases(db, ddb) 负责——
  // 名册在那边，这里不再持有一份。

  for (const v of db.views) {
    const n = evalSelector(db, v.selector).length;
    if (n === 0) E('empty_view', v.id);
    else if (n < 3) W('thin_view', `${v.id} n=${n}`);
  }

  // 档位表覆盖 0–10 无重叠无空隙；起始值在界内
  const covered = [];
  for (const b of db.bands.tiers) {
    for (let s = b.min; s <= b.max; s += 1) {
      if (covered.includes(s)) E('band_overlap', `${b.id}@${s}`);
      covered.push(s);
    }
  }
  for (let s = db.attribute_bounds.min; s <= db.attribute_bounds.max; s += 1) {
    if (!covered.includes(s)) E('band_gap', String(s));
  }
  for (const k of attrIds) {
    const b = db.base_attributes[k];
    if (!Number.isInteger(b) || b < db.attribute_bounds.min || b > db.attribute_bounds.max) {
      E('base_attribute_range', `${k}=${b}`);
    }
  }

  return { errors, warnings };
}

/**
 * 问诊与池子的契约校验（开发期用；不是门禁，没有任何 CI 在跑它）。
 *
 * 🔧 2026-09-27 阶段 3：由 `validateAnchors` 的**格级判据平移**而来。格（锚点组合）
 * 已经退役，判据一条也没丢，换成池子口径：
 *   ① 谁答哪一面必须是 11 个 facet 的完全划分（可锚 / 禁锚 / 系统定 → patient / hospital）
 *   ② 输出槽一个都不许落在患者侧
 *   ③ 每一问都必须有一个栏目接着（纸上有地方写）
 *   ④ 屏文案不漏内部实现词
 *   ⑤ **每一个已答前缀**的池子都 ≥ quota.total 段 · 跨 ≥ ceil(total/per_value_max) 个地方 ·
 *      病并集在 `ddb.pool_rule` 的上下界内 ——「答什么都不锁死」的可算形式
 *   ⑥ 不是记录 facet 的答案轴（患者自述的那个病，`answer_from: complaint`）：
 *      不许与 facet 重名、不许参与相符判断、必须标 `who: patient`
 *
 * ⑤ 要枚举全部 3 万个已答前缀（约 1 秒），所以它有三档：
 *   `{ census: 'full' }` 全枚举 · `{ census: 'sample' }`（默认）已答 ≤2 问的全跑 + 其余抽 1/40 ·
 *   `{ census: 'off' }` 只核形状。
 * 交付里报的四个数一律来自全枚举（`web/scripts/pool-census.mjs` 与 interview.test.js 那一条），
 * 抽样只是让校验器能随时跑而不必等一整秒。
 */
export function validateInterview(db, ddb = null, { census: censusMode = 'sample', sample = 40 } = {}) {
  const errors = [];
  const warnings = [];
  const E = (code, detail) => errors.push({ code, detail });
  const W = (code, detail) => warnings.push({ code, detail });

  const rule = db.interview;
  if (!rule) {
    E('interview_missing', 'data 里没有 interview 块');
    return { errors, warnings, census: null };
  }
  if (!rule.source || !String(rule.source).trim()) E('config_without_source', 'interview');

  const facets = facetIds(db);
  const questions = rule.questions ?? [];

  // 1. 八问自身的形状：id / 答案轴 / 问法 / 答案来源 / 依据
  for (const [i, q] of questions.entries()) {
    const at = `questions[${i}]`;
    if (!q.id || !q.facet || !q.ask || !String(q.ask).trim()) E('interview_question_incomplete', at);
    const isFacet = facets.includes(q.facet);
    // 答案来自记录词表时，问的必须是一个真的 facet——**先拦这一条**，
    // 否则下面的闭集检查会拿着一个不存在的 facet 去取值。
    if (q.answer_from === 'vocab' && !isFacet) { E('interview_facet_unknown', String(q.facet)); continue; }
    if (!['vocab', 'complaint'].includes(q.answer_from)) {
      E('interview_answer_source_unsupported', `${at}=${q.answer_from}`);
    } else if (!(answerSpec(db, q)?.values ?? []).length) {
      // 两种来源都要求「有闭集可答」：问诊里不存在没有选项的问。
      E('interview_question_without_closed_set', `${at}=${q.answer_from}.${q.facet}`);
    }
    // 不是记录 facet 的答案轴（患者自述的那个病）：它没有记录的取值可比，所以
    // 既不能当筛子，也不许跟记录 facet 重名——那是「悄悄多出一个 facet」的入口。
    if (q.answer_from !== 'vocab') {
      if (isFacet) E('interview_facet_source_conflict', `${at}.facet=${q.facet} 已是记录 facet`);
      if (q.matches === true) E('interview_nonfacet_question_matches', `${at}=${q.facet}`);
      if (q.who !== 'patient') E('interview_question_not_patient', `${at}=${q.facet} 未标 who=patient`);
    }
    if (!q.basis?.clinical || !String(q.basis.clinical).trim()) E('interview_reason_missing', `${at}.clinical`);
  }
  const qids = questions.map((q) => q.id);
  if (new Set(qids).size !== qids.length) E('interview_question_duplicate', qids.join(','));
  const qFacets = questions.map((q) => q.facet);
  if (new Set(qFacets).size !== qFacets.length) E('interview_facet_asked_twice', qFacets.join(','));

  // 2. 谁答哪一面：**完全划分**，不重不漏
  const patient = facetsAnsweredBy(db, 'patient');
  const hospital = facetsAnsweredBy(db, 'hospital');
  for (const f of [...patient, ...hospital]) {
    if (!facets.includes(f)) E('interview_facet_unknown', f);
  }
  for (const f of facets) {
    // 数的是**条目数**，不是「在哪一份名单里」：同一份名单里写两遍也是重复分类。
    const n = patient.filter((x) => x === f).length + hospital.filter((x) => x === f).length;
    if (n === 0) E('interview_facet_unclassified', `${f}：既没由患者答，也没写"为什么不由他答"`);
    if (n > 1) E('interview_facet_multiply_classified', f);
  }
  for (const [list, name] of [[rule.who_answers?.patient ?? [], 'patient'], [rule.who_answers?.hospital ?? [], 'hospital']]) {
    for (const x of list) if (!x.basis || !String(x.basis).trim()) E('interview_reason_missing', `${name}.${x.facet}`);
  }
  for (const x of rule.who_answers?.patient ?? []) {
    const q = qids.includes(x.by) ? questionById(db, x.by) : null;
    if (!q) E('interview_patient_answer_without_question', `${x.facet} → ${x.by}`);
    else if (q.facet !== x.facet) E('interview_question_mismatch', `${x.by} 问的是 ${q.facet}，登记成 ${x.facet}`);
  }
  // 红线：输出槽永不由患者答（它是结果不是处境）
  for (const f of facets) {
    if (db.vocab[f].output === true && patient.includes(f)) E('interview_output_facet_answered_by_patient', f);
  }

  // 2b. 只有患者侧那几个 facet 可以被问：医生不会拿着「留下什么」去问患者。
  for (const [i, q] of questions.entries()) {
    if (facets.includes(q.facet) && !patient.includes(q.facet)) {
      E('interview_question_not_patient', `questions[${i}]=${q.facet} 不由患者答`);
    }
  }

  // 3. 池子口径的形状
  const cfg = rule.pool ?? {};
  const floors = poolFloors(db, ddb);
  if (!(cfg.display_size >= floors.minSize)) {
    E('interview_pool_display_too_small', `display_size ${cfg.display_size} < ${floors.minSize}`);
  }
  if (!(cfg.seed_tries >= 1)) E('interview_pool_seed_tries', String(cfg.seed_tries));
  if (!matchQuestions(db).length) E('interview_no_matching_question', '没有一问参与池子的相符判断');
  const wantLevels = ['matched_all', 'matched_drop_one', 'matched_any', 'library'];
  const gotLevels = (cfg.ladder ?? []).map((s) => s.level);
  if (wantLevels.join(',') !== gotLevels.join(',')) {
    E('interview_ladder_incomplete', `${gotLevels.join(',') || '(空)'} ≠ ${wantLevels.join(',')}`);
  }
  for (const [i, s] of (cfg.ladder ?? []).entries()) {
    if (!s.name || !s.basis) E('interview_ladder_step_incomplete', `ladder[${i}]`);
  }
  if (!cfg.match_basis || !cfg.fill_basis || !cfg.ladder_note) E('interview_pool_rule_missing', 'pool');

  // 4. 每一问都要有栏目接着：纸上写在哪里，不许只活在散文里
  const paperWrites = (db.record_shell?.paper?.columns ?? [])
    .flatMap((c) => (c.writes ?? []).map((w) => ({ column: c.id, ...w })))
    .concat((db.record_shell?.paper?.columns ?? [])
      .filter((c) => c.writes_ref === 'general')
      .flatMap((c) => (db.record_shell.general ?? []).map((r) => ({ column: c.id, from: 'character', label: r.label }))));
  for (const q of questions) {
    if (!paperWrites.some((w) => w.from === q.id)) E('interview_question_without_column', `${q.id} 没有落在任何一栏上`);
  }
  for (const w of paperWrites) {
    if (String(w.from).startsWith('q_') && !qids.includes(w.from)) {
      E('paper_write_unknown_source', `${w.column}.${w.label}=${w.from}`);
    }
  }

  // 5. 玩家看得见的文案：内部实现词一个都不许出现
  const copy = [
    ...Object.entries(rule.screen ?? {}).map(([k, v]) => [`screen.${k}`, v]),
    ...questions.map((q, i) => [`questions[${i}].ask`, q.ask]),
    ...(rule.pool?.ladder ?? []).map((s, i) => [`pool.ladder[${i}].name`, s.name]),
    ['doctor', rule.doctor], ['reanswer', rule.reanswer],
    ['answer_note', rule.answer_note], ['reanswer_note', rule.reanswer_note],
  ];
  for (const [k, v] of copy) {
    if (typeof v !== 'string' || !v.trim()) { E('interview_copy_missing', k); continue; }
    for (const w of INTERNAL_COPY_WORDS) if (v.includes(w)) E('interview_copy_leaks_internal', `${k} 含「${w}」`);
  }

  // 6. 池子级判据：跑一遍**全部已答前缀**。
  //    形状先坏掉时不再往下跑：那时 interviewPool 拿不到可信的答案域，
  //    报不出「哪个前缀的池子不够」这种有用的话——形状错误本身已经在上面了。
  const census = errors.length === 0 && censusMode !== 'off'
    ? poolCensus(db, ddb, censusMode === 'full' ? {} : { sample })
    : null;
  if (census) {
    if (census.floorBreaks > 0) {
      E('interview_pool_never_locks', `跑过的 ${census.testedBranches} 个已答前缀里有 ${census.floorBreaks} 个凑不出合格的池子`);
    }
    if (census.minSize < floors.minSize) {
      E('interview_pool_too_thin', `最坏池子 ${census.minSize} < ${floors.minSize}`);
    }
    if (census.minContexts < floors.minContexts) {
      E('interview_pool_contexts_too_few', `最坏只跨 ${census.minContexts} 个地方，需 ≥${floors.minContexts}`);
    }
    if (ddb && census.maxDiseaseUnion !== null) {
      if (floors.minDiseases !== null && census.minDiseaseUnion < floors.minDiseases) {
        E('interview_pool_diseases_too_few', `池病并集最小 ${census.minDiseaseUnion} < ${floors.minDiseases}`);
      }
      if (floors.maxDiseases !== null && census.maxDiseaseUnion > floors.maxDiseases) {
        E('interview_pool_diseases_too_many', `池病并集最大 ${census.maxDiseaseUnion} > ${floors.maxDiseases}`);
      }
    }
    // 放宽不是错误，但必须**有数**：多少前缀需要往下走一级，走的是哪几级。
    if (census.relaxedBranches > 0) {
      W('interview_pool_relaxed', `跑过的 ${census.testedBranches} 个已答前缀里 ${census.relaxedBranches} 个需要放宽：`
        + Object.entries(census.levelCounts).map(([k, v]) => `${k} ${v}`).join(' · '));
    }
  }

  return { errors, warnings, census };
}

/**
 * 文档用派生表。输出的表是**生成物**——设计文档里不许手写记录清单，
 * 需要表就地跑这个函数，避免同一批数据出现第二份副本。
 */
export function renderTable(db) {
  const facets = facetIds(db);
  const head = ['id', 'title', ...facets, 'Δ属性', 'diseases'];
  const rows = db.experiences.map((r) => [
    r.id,
    r.title,
    ...facets.map((f) => (Array.isArray(r[f]) ? r[f].join('+') : r[f])),
    Object.entries(r.effects.attributes)
      .map(([k, d]) => `${k}${d > 0 ? '+' : ''}${d}`)
      .join(' '),
    r.diseases.join('+'),
  ]);
  return [head, ...rows].map((row) => `| ${row.join(' | ')} |`).join('\n');
}
