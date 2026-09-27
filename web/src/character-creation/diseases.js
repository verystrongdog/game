/**
 * 开局疾病：词表读取 / 按字段查询 / 门 / 形态派生 / 候选 / 校验。
 *
 * 边界（AGENTS.md §二 拦截规则）：
 *   本模块只服务开局与 Web 演示。不得引入 C# 引擎或神经模拟系统的任何概念。
 *   ⚠️ 战斗相关内容（遭遇门的撞到点、HP/SAN、明雷暗雷）**不建模**——遭遇门原样保留，
 *   标 `paused`，`where` 一律为空数组，界面不渲染。owner 2026-09-20：战斗相关内容暂时不要碰。
 *
 * 设计属性：全部无状态纯函数（ddb 由调用方传入）。无单例、无缓存、无隐藏状态。
 * 数据权威：data/diseases.json 是唯一来源。本文件不含任何数据字面量。
 * 命名：与 opening.js 同名前缀 `disease*`，避免两个模块互相遮蔽。
 */

// ── schema ───────────────────────────────────────────────────────────────
const REQUIRED_KEYS = ['id', 'label', 'plain', 'break_in', 'speaker_change', 'phase_cycle', 'doors', 'bonus', 'cost', 'source'];
const OPTIONAL_KEYS = ['always_on', 'signs'];
const ID_PATTERN = /^dis_\d{4}$/;

const asArray = (raw) => (Array.isArray(raw) ? raw : raw === undefined || raw === null ? [] : [raw]);

// ── 基础读取 ─────────────────────────────────────────────────────────────
export function diseaseById(ddb, id) {
  const r = ddb.items.find((x) => x.id === id);
  if (!r) throw new Error(`未知疾病 id: ${id}`);
  return r;
}

export const diseaseIds = (ddb) => ddb.items.map((r) => r.id);

export function diseaseSpec(ddb, facetId) {
  const s = ddb.vocab[facetId];
  if (!s) throw new Error(`未知疾病词表: ${facetId}`);
  return s;
}

export function diseaseValues(ddb, facetId) {
  return diseaseSpec(ddb, facetId).values.map((v) => v.id);
}

export function diseaseLabel(ddb, facetId, valueId) {
  const v = diseaseSpec(ddb, facetId).values.find((x) => x.id === valueId);
  if (!v) throw new Error(`未登记取值: ${facetId}=${valueId}`);
  return v.label;
}

/** 空值怎么念由词表决定，不写死在代码里。 */
export const diseaseEmptyLabel = (ddb, facetId) => diseaseSpec(ddb, facetId).empty_label ?? null;

/** 门类的启停状态（`status: 'paused'` 表示该层已暂停，界面不渲染）。 */
export function doorVisible(ddb, kindId) {
  const v = diseaseSpec(ddb, 'door_kind').values.find((x) => x.id === kindId);
  if (!v) throw new Error(`未知门类: ${kindId}`);
  return { id: v.id, label: v.label, active: v.status !== 'paused', status: v.status ?? null };
}

// ── 派生：形态（不存字段） ────────────────────────────────────────────────
/** 只用玩家看得见的三件事判定；判据表在 form_rule 里，不在代码里。 */
export function formOf(ddb, id) {
  const r = diseaseById(ddb, id);
  for (const row of ddb.form_rule.table) {
    const when = row.when || {};
    const hit = Object.entries(when).every(([k, v]) => {
      const raw = r[k];
      return Array.isArray(raw) ? raw.length > 0 : raw === v;
    });
    if (hit) return { id: row.form, label: ddb.form_rule.labels[row.form] };
  }
  throw new Error(`${id} 的形态判不出来（form_rule.table 没有兜底行？）`);
}

// ── 按字段查询（与 opening.js 同一套子句形状） ───────────────────────────
/**
 * 子句形态：`{facet, in}` · `{facet, not_in}` · `{facet, empty}` · `{facet, not_empty}`
 * 疾病侧额外支持：
 *   `{facet:'doors', open:true, kind?}` —— 有没有这样一扇门
 *   `{facet:'form', in:[…]}` —— 派生形态
 */
export function clauseHitsOnDisease(ddb, rec, c) {
  if (c.facet === 'form') {
    const f = formOf(ddb, rec.id).id;
    if (Array.isArray(c.in)) return c.in.includes(f);
    if (Array.isArray(c.not_in)) return !c.not_in.includes(f);
    throw new Error(`form 子句形状非法: ${JSON.stringify(c)}`);
  }
  if (c.facet === 'doors') {
    const doors = rec.doors || [];
    if (c.empty === true) return doors.length === 0;
    if (c.not_empty === true) return doors.length > 0;
    if (typeof c.open === 'boolean') {
      return doors.some((d) => d.open === c.open && (c.kind === undefined || d.kind === c.kind));
    }
    if (Array.isArray(c.in)) return doors.some((d) => c.in.includes(d.kind));
    throw new Error(`doors 子句形状非法: ${JSON.stringify(c)}`);
  }
  if (c.facet === 'bonus') {
    const b = rec.bonus ?? null;
    if (c.empty === true) return b === null;
    if (c.not_empty === true) return b !== null;
    if (Array.isArray(c.in)) return b !== null && c.in.includes(b.visible);
    throw new Error(`bonus 子句形状非法: ${JSON.stringify(c)}`);
  }
  // 其余按标量 / 数组。已知但可缺的字段（always_on / signs）缺 = 空。
  if (!(c.facet in rec) && !OPTIONAL_KEYS.includes(c.facet)) {
    throw new Error(`子句指向不存在的字段: ${c.facet}`);
  }
  const arr = asArray(rec[c.facet]);
  if (c.empty === true) return arr.length === 0;
  if (c.not_empty === true) return arr.length > 0;
  if (Array.isArray(c.in)) return arr.some((x) => c.in.includes(x));
  if (Array.isArray(c.not_in)) return !arr.some((x) => c.not_in.includes(x));
  throw new Error(`子句形状非法: ${JSON.stringify(c)}`);
}

export function evalDiseaseSelector(ddb, selector) {
  const { all = [], any = [], none = [] } = selector || {};
  return ddb.items.filter(
    (r) =>
      all.every((c) => clauseHitsOnDisease(ddb, r, c)) &&
      (any.length === 0 || any.some((c) => clauseHitsOnDisease(ddb, r, c))) &&
      none.every((c) => !clauseHitsOnDisease(ddb, r, c)),
  );
}

export const queryDiseases = (ddb, clauses) => evalDiseaseSelector(ddb, { all: clauses });

export function evalDiseaseView(ddb, viewId) {
  const v = ddb.views.find((x) => x.id === viewId);
  if (!v) throw new Error(`未知疾病视图: ${viewId}`);
  return evalDiseaseSelector(ddb, v.selector);
}

export const diseaseViewIndex = (ddb) =>
  ddb.views.map((v) => ({ id: v.id, label: v.label, count: evalDiseaseView(ddb, v.id).length }));

// ── 门 ───────────────────────────────────────────────────────────────────
const doorsWhere = (ddb, rec, open) =>
  (rec.doors || [])
    .filter((d) => d.open === open)
    .map((d) => ({
      kind: d.kind,
      kindLabel: diseaseLabel(ddb, 'door_kind', d.kind),
      what: d.what,
      where: d.where,
      whereLabels: d.where.map((w) => diseaseLabel(ddb, 'door_where', w)),
      paused: !doorVisible(ddb, d.kind).active,
    }));

/** 开着的门（空数组 = 这张卡没有这道门）。 */
export const openDoors = (ddb, id) => doorsWhere(ddb, diseaseById(ddb, id), true);

/** 关着的门——「玩家在哪里会撞到自己丢了什么」。 */
export const closedDoors = (ddb, id) => doorsWhere(ddb, diseaseById(ddb, id), false);

// ── 与经历契约的接缝 ─────────────────────────────────────────────────────
/** 一条经历指向哪些病（经历记录里只存 id）。 */
export const diseasesOfExperience = (db, expId) => {
  const r = db.experiences.find((x) => x.id === expId);
  if (!r) throw new Error(`未知经历 id: ${expId}`);
  return [...r.diseases];
};

/** 反查：这张病能从哪些经历来。每次现算，病记录里不存反向键。 */
export const sourcesOf = (db, ddb, diseaseId) => {
  diseaseById(ddb, diseaseId);
  return db.experiences.filter((r) => r.diseases.includes(diseaseId)).map((r) => r.id);
};

/** 名册 = 参与候选的病（固有项不是候选，不计入）。 */
export const rosterOf = (ddb) => ddb.items.filter((r) => r.always_on !== true);

export function diseaseCandidates(db, ddb, selectedIds) {
  const hit = new Set();
  for (const id of selectedIds) {
    const r = db.experiences.find((x) => x.id === id);
    if (!r) throw new Error(`未知经历 id: ${id}`);
    for (const d of r.diseases) hit.add(d);
  }
  return rosterOf(ddb)
    .filter((d) => hit.has(d.id))
    .map((d) => ({ ...d, from: sourcesOf(db, ddb, d.id).filter((e) => selectedIds.includes(e)) }));
}

/**
 * 候选筛选力的判据与实测。
 *
 * 上界是**纯组合**的，与名册内容无关：
 *   任意合法选择 S（|S| = k）下  |候选(S)| ≤ Σ_{r∈S} 每条经历指向数 ≤ c·k
 * 所以名册里至少有 roster − c·k 张病在本局**结构上不可能出现**。
 */
export function diseaseCoverage(db, ddb) {
  const { profiles_per_experience_max: c, opening_experience_total: k, roster_size } = ddb.filter_rule;
  const roster = rosterOf(ddb);
  const perDisease = {};
  for (const d of roster) perDisease[d.id] = 0;
  for (const r of db.experiences) {
    for (const d of r.diseases) if (d in perDisease) perDisease[d] += 1;
  }
  const sample = db.experiences.slice(0, k).map((r) => r.id);
  const sampleUnion = new Set(sample.flatMap((id) => db.experiences.find((r) => r.id === id).diseases)).size;
  const upperBound = c * k;
  return {
    roster: roster_size,
    rosterActual: roster.length,
    perDisease,
    sampleUnion,
    upperBound,
    ruledOutMin: Math.max(0, roster_size - upperBound),
    ratio: sampleUnion / roster_size,
  };
}

/** 屏 4 的可点性：必须在候选里，且不超过可选上限（上限为 null 表示不设限）。 */
export function diseaseCanStillPick(db, ddb, selectedIds, diseaseId) {
  const reasons = [];
  const max = ddb.presentation.selected_diseases_max;
  const cands = diseaseCandidates(db, ddb, selectedIds).map((d) => d.id);
  if (!cands.includes(diseaseId)) reasons.push({ code: 'not_in_candidates' });
  if (max !== null && max !== undefined && selectedIds.length >= max) {
    reasons.push({ code: 'selection_full', max });
  }
  return { ok: reasons.length === 0, reasons, candidates: cands };
}

// ── 渲染 ─────────────────────────────────────────────────────────────────
export function describeDisease(db, ddb, id) {
  const r = diseaseById(ddb, id);
  const b = r.bonus ?? null;
  const vis = b ? diseaseLabel(ddb, 'visible', b.visible) : diseaseEmptyLabel(ddb, 'visible');
  return {
    id: r.id,
    label: r.label,
    plain: r.plain,
    formLabel: formOf(ddb, r.id).label,
    bonus: b
      ? { attrId: b.attr, attrLabel: db.attributes.labels[b.attr], amount: ddb.tiers.base_amount, visibleLabel: vis, atLeast: b.at_least }
      : null,
    bonusEmptyLabel: vis, // bonus 为 null 时读这句
    doors: (r.doors || []).map((d) => ({
      open: d.open,
      kindLabel: diseaseLabel(ddb, 'door_kind', d.kind),
      what: d.what,
      whereLabels: d.where.map((w) => diseaseLabel(ddb, 'door_where', w)),
      paused: !doorVisible(ddb, d.kind).active,
    })),
    cost: r.cost,
    alwaysOn: r.always_on === true,
    signs: r.signs ?? [],
  };
}

// ── 校验（开发期用；不是门禁，没有任何 CI 在跑它） ───────────────────────
export function validateDiseases(db, ddb) {
  const errors = [];
  const warnings = [];
  const E = (code, detail) => errors.push({ code, detail });
  const W = (code, detail) => warnings.push({ code, detail });

  const V = ddb.vocab;
  const activeKind = (k) => {
    const v = V.door_kind.values.find((x) => x.id === k);
    return v ? v.status !== 'paused' : true;
  };
  const facets = Object.keys(V);
  const used = Object.fromEntries(facets.map((f) => [f, new Set()]));
  const seenIds = new Set();
  const tomb = new Set(ddb.tombstones || []);
  const attrIds = db?.attributes?.ids ?? [];

  // 词表自身
  for (const f of facets) {
    const s = V[f];
    if (!s.ask || !String(s.ask).trim()) E('facet_without_ask', f);
    if (!s.values?.length) E('facet_without_values', f);
    for (const v of s.values ?? []) {
      if (!v.label) E('vocab_value_without_label', `${f}=${v.id}`);
      if (/unknown|unspecified|tbd|todo|待定/i.test(v.id)) E('vocab_wildcard_forbidden', `${f}=${v.id}`);
    }
    if (s.min_items === 0 && !s.empty_label) E('multi_facet_without_empty_label', f);
  }

  // 配置块
  for (const p of ['form_rule', 'filter_rule', 'pool_rule', 'tiers', 'presentation']) {
    if (!ddb[p]?.source) E('config_without_source', p);
  }

  // 候选筛选力：纯组合判据
  const { profiles_per_experience_max: c, experiences_per_profile_min: u, opening_experience_total: k, roster_size } = ddb.filter_rule;
  const upperBound = c * k;
  if (!(upperBound < roster_size)) {
    E('candidate_filter_too_weak', `每条经历 ≤${c} × 选 ${k} 段 = 上界 ${upperBound} ≥ 名册 ${roster_size}：候选失去约束力`);
  }

  // 记录
  for (const r of ddb.items) {
    const w = r.id || '(缺 id)';
    if (!ID_PATTERN.test(r.id || '')) E('id_format', w);
    if (seenIds.has(r.id)) E('id_duplicate', w);
    seenIds.add(r.id);
    if (tomb.has(r.id)) E('id_reused', w);

    const isInherent = r.always_on === true;
    for (const key of isInherent ? ['id', 'label', 'plain', 'source'] : REQUIRED_KEYS) {
      if (!(key in r)) E('record_missing_field', `${w}.${key}`);
    }
    for (const key of Object.keys(r)) {
      if (!REQUIRED_KEYS.includes(key) && !OPTIONAL_KEYS.includes(key)) E('record_unknown_field', `${w}.${key}`);
    }

    if (typeof r.label !== 'string' || !r.label.trim()) E('label_missing', w);
    if (typeof r.plain !== 'string' || !r.plain.trim()) E('plain_missing', w);
    if (!isInherent && (typeof r.cost !== 'string' || !r.cost.trim())) E('cost_missing', w);
    if (!r.source || !String(r.source).trim()) E('record_without_source', w);

    // 文本 lint：语义不许藏在文案里
    for (const key of ['label', 'plain']) {
      const t = r[key];
      if (typeof t !== 'string') continue;
      if (/[0-9０-９]/.test(t)) E('text_has_digit', `${w}.${key}`);
      for (const f of facets) {
        for (const v of V[f].values) {
          if (t.includes(v.label)) E('text_has_facet_word', `${w}.${key} 含「${v.label}」`);
        }
      }
    }

    // 形态三属性
    if (!isInherent) {
      if (typeof r.break_in !== 'boolean') E('form_flag_not_bool', `${w}.break_in`);
      if (typeof r.phase_cycle !== 'boolean') E('form_flag_not_bool', `${w}.phase_cycle`);
      if (!Array.isArray(r.speaker_change)) E('form_flag_not_array', `${w}.speaker_change`);
      else {
        if (r.speaker_change.length > 1) E('speaker_change_too_many', w);
        for (const v of r.speaker_change) {
          if (V.speaker.values.some((x) => x.id === v)) used.speaker.add(v);
          else E('speaker_change_unknown', `${w}=${v}`);
        }
      }
      if ([r.break_in, r.phase_cycle].filter(Boolean).length + (r.speaker_change?.length ? 1 : 0) > 1) {
        E('form_flags_conflict', w);
      }
    }

    // 门
    const doors = r.doors ?? [];
    if (isInherent) {
      if (doors.length) E('inherent_has_doors', w);
    } else {
      if (doors.length !== 2) E('door_count', `${w} n=${doors.length}`);
      const opens = doors.filter((d) => d.open === true).length;
      const closes = doors.filter((d) => d.open === false).length;
      if (opens !== 1 || closes !== 1) E('door_direction', `${w} 开 ${opens} / 关 ${closes}`);
      if (new Set(doors.map((d) => d.kind)).size !== doors.length) E('door_kind_duplicate', w);
      for (const d of doors) {
        if (!V.door_kind.values.some((x) => x.id === d.kind)) E('door_kind_unknown', `${w}=${d.kind}`);
        if (!d.what || !String(d.what).trim()) E('door_without_what', `${w}.${d.kind}`);
        if (!Array.isArray(d.where)) E('door_where_not_array', `${w}.${d.kind}`);
        else {
          const active = activeKind(d.kind);
          if (active) {
            if (d.where.length < 1) E('live_door_without_where', `${w}.${d.kind}（关门必须可见）`);
            for (const x of d.where) {
              if (V.door_where.values.some((y) => y.id === x)) used.door_where.add(x);
              else E('door_where_unknown', `${w}=${x}`);
            }
          } else if (d.where.length !== 0) {
            E('paused_door_models_where', `${w}.${d.kind}：暂停的门不得建模撞到点（战斗内容暂不碰）`);
          }
          if (d.open === true) {
            if (!Array.isArray(d.used_for_group) || d.used_for_group.length !== 1
              || !V.used_for_group.values.some((x) => x.id === d.used_for_group[0])) {
              E('open_door_without_group_key', `${w}.${d.kind}`);
            } else used.used_for_group.add(d.used_for_group[0]);
          } else if ('used_for_group' in d) {
            E('closed_door_has_group_key', `${w}.${d.kind}`);
          }
        }
        if (V.door_kind.values.some((x) => x.id === d.kind)) used.door_kind.add(d.kind);
      }
    }

    // 加成
    const b = r.bonus ?? null;
    if (isInherent) {
      if (b !== null) E('inherent_has_bonus', w);
    } else if (b === null) {
      // 空值合法；无加成是设计（两张病"没有单一成立情境"）
    } else {
      if (!V.visible.values.some((x) => x.id === b.visible)) E('bonus_visible_unknown', `${w}=${b.visible}`);
      else used.visible.add(b.visible);
      if (attrIds.length && !attrIds.includes(b.attr)) E('bonus_attr_unknown', `${w}=${b.attr}`);
      if (!('at_least' in b)) E('record_missing_field', `${w}.bonus.at_least`);
      else if (b.at_least !== null && (!Number.isInteger(b.at_least) || b.at_least < 2)) {
        E('bonus_at_least_range', `${w}=${b.at_least}`);
      }
    }

    // 固有项
    if (isInherent) {
      if (!Array.isArray(r.signs) || r.signs.length === 0) E('inherent_without_signs', w);
      for (const s of r.signs ?? []) {
        if (!s.label || !s.plain) E('inherent_sign_incomplete', w);
      }
    }
  }

  // 死值
  for (const v of V.door_kind.values) if (!used.door_kind?.has(v.id)) E('dead_value', `door_kind=${v.id}`);
  for (const v of V.door_where.values) if (!used.door_where?.has(v.id)) E('dead_value', `door_where=${v.id}`);
  for (const v of V.visible.values) if (!used.visible?.has(v.id)) E('dead_value', `visible=${v.id}`);
  for (const v of V.used_for_group.values) if (!used.used_for_group?.has(v.id)) E('dead_value', `used_for_group=${v.id}`);
  for (const v of V.speaker.values) if (!used.speaker?.has(v.id)) E('dead_value', `speaker=${v.id}`);

  // 未建模的门（战斗内容暂不碰）
  const pausedUsed = new Set(
    ddb.items.flatMap((r) => (r.doors ?? []).filter((d) => !activeKind(d.kind)).map((d) => d.kind)),
  );
  if (pausedUsed.size) {
    W('paused_door_present', `已暂停的门类被 ${pausedUsed.size} 类记录引用，界面不渲染：${[...pausedUsed].join(',')}`);
  }

  // 形态派生必须复现 §4.2 的四组
  const byForm = {};
  for (const r of rosterOf(ddb)) {
    const f = formOf(ddb, r.id).id;
    byForm[f] = (byForm[f] ?? 0) + 1;
  }
  const expected = ddb.form_rule.expected_counts;
  if (expected) {
    for (const [f, n] of Object.entries(expected)) {
      if (byForm[f] !== n) E('form_count_mismatch', `${f} 派生 ${byForm[f] ?? 0} ≠ 期望 ${n}`);
    }
  }

  // 非法组合
  for (const fc of ddb.forbidden_combos ?? []) {
    for (const r of ddb.items) {
      if (fc.when.every((cl) => clauseHitsOnDisease(ddb, r, cl))) E('forbidden_combo', `${fc.id} 命中 ${r.id}`);
    }
  }

  // 视图
  for (const v of ddb.views ?? []) {
    const n = evalDiseaseSelector(ddb, v.selector).length;
    if (n === 0) E('empty_view', v.id);
    else if (n < 2) W('thin_view', `${v.id} n=${n}`);
  }

  // 与经历契约的交叉
  if (db) {
    for (const r of db.experiences) {
      const ds = r.diseases ?? [];
      if (!ds.length) E('experience_without_disease', r.id);
      if (ds.length > c) E('experience_too_many_profiles', `${r.id} n=${ds.length} > ${c}`);
      for (const d of ds) {
        if (!ddb.items.some((x) => x.id === d)) E('disease_unknown', `${r.id}->${d}`);
        else if (ddb.items.find((x) => x.id === d).always_on === true) E('inherent_not_a_candidate', `${r.id}->${d}`);
      }
    }
    for (const d of rosterOf(ddb)) {
      const n = sourcesOf(db, ddb, d.id).length;
      if (n === 0) E('dead_disease', d.id);
      else if (n < u) W('disease_below_source_min', `${d.id} 只有 ${n} 条经历指向（目标 ≥${u}）`);
    }
  }

  return { errors, warnings, byForm };
}

/** 迁移覆盖统计：26 病在新结构里落成了什么。 */
export function migrationCoverage(ddb) {
  const roster = rosterOf(ddb);
  const byForm = {};
  const byOpenKind = {};
  const byCloseKind = {};
  for (const r of roster) {
    const f = formOf(ddb, r.id).id;
    byForm[f] = (byForm[f] ?? 0) + 1;
    for (const d of r.doors) {
      const t = d.open ? byOpenKind : byCloseKind;
      t[d.kind] = (t[d.kind] ?? 0) + 1;
    }
  }
  return {
    inTable: roster.length,
    withBonus: roster.filter((r) => r.bonus !== null).length,
    withoutBonus: roster.filter((r) => r.bonus === null).map((r) => r.id),
    byForm,
    byOpenKind,
    byCloseKind,
    inherent: ddb.items.filter((r) => r.always_on === true).map((r) => r.id),
  };
}

/**
 * 文档用派生表。输出是**生成物**——设计文档里不许手写 26 行表，
 * 需要表就地跑这个函数，避免同一批数据出现第二份副本。
 */
export function renderDiseaseTable(ddb) {
  const head = ['id', '病名', '形态', '加成情境', '属性', '开门', '关门', '代价'];
  const rows = rosterOf(ddb).map((r) => [
    r.id,
    r.label,
    formOf(ddb, r.id).label,
    r.bonus ? diseaseLabel(ddb, 'visible', r.bonus.visible) : diseaseEmptyLabel(ddb, 'visible'),
    r.bonus ? r.bonus.attr : '—',
    (r.doors.find((d) => d.open) ?? {}).what ?? '—',
    (r.doors.find((d) => !d.open) ?? {}).what ?? '—',
    r.cost,
  ]);
  return [head, ...rows].map((row) => `| ${row.join(' | ')} |`).join('\n');
}
