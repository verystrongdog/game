/**
 * 开局病历：**栏位落笔表** · 人物来源 · 主诉拼句。
 *
 * 边界（AGENTS.md §二 拦截规则）：只服务开局 / Web 演示。不得引入 C# 引擎或
 * 神经模拟系统的任何概念；战斗相关内容一律不碰。
 *
 * 这个模块回答三个问题，全部可从 `data/opening.json` 算出来、不靠散文自觉：
 *
 * 1. **这一栏谁落笔？**（`rowPlan` / `writableRows`）
 *    页眉的每一笔在数据里都带 `who`（谁的笔迹）· `fill`（这支笔现在能不能落）·
 *    `blank`（没落笔时显示什么）。界面不判断"这一栏能不能填"，只读这三个键。
 *
 * 2. **玩家能落哪几种笔？**（`writableFields` / `namePool`）
 *    玩家可落的每一笔的取值必须来自一个**可枚举的闭集**：`character_vocab` 的
 *    `values`，或姓名选择控件（姓 × 名）。给不出闭集的栏目（职业 / 婚姻 / 出生地）
 *    一律留在 `fill: system` 并显示为未填——**没有自由文本输入不是靠界面自觉，
 *    是数据上就填不出来**（`character_field_without_closed_set`）。
 *
 * 3. **三个答案怎么落成一行主诉？**（`complaintText` / `allComplaints`）
 *    法定格式是「症状（或体征）+ 持续时间」。本作只把**已经答下的**三个答案搬进
 *    那一行：第 1 问的自述症状（患者自己带来的说法，来自 `complaint.self_report`）、
 *    `onset` 的标签当起病缓急、`duration_pattern` 的标签当持续时间。措辞与取值都来自
 *    `data/opening.json`，界面不拼字。
 *
 * 数据权威：`data/opening.json`。本文件不含任何数据字面量，也不含机制数值。
 */

import { labelOf } from './opening.js';

// ── 人物来源 ─────────────────────────────────────────────────────────────

/** 人物来源的登记表：`characters` 是可当来源用的键，`ui` 是给界面看的文案。 */
export const characterSources = (db) => db.character_source.characters;
export const characterUi = (db) => db.character_source.ui;

/** 页眉一般情况的落笔表：一行一笔，每笔带 `who` / `fill` / `blank`。 */
export const rowPlan = (db) => db.record_shell.general;

/** 两半分开写的那些行（患者自述 vs 院方记录）。只有「姓名」是这种行。 */
export const compositeRows = (db) => rowPlan(db).filter((r) => r.value_to !== undefined);

/** 页眉行 → 对应的 `character.fields` 登记（拿它的 `fill` 与 `value`）。 */
export const characterFieldOf = (db, row) =>
  (db.record_shell.character?.fields ?? []).find((f) => f.row === row?.label) ?? null;

/**
 * 这一笔现在能不能落。**唯一判据**：行上没有登记就让 `character.fields` 说了算。
 * 界面、校验器、测试都走这一个函数，所以「玩家可填几笔」只有一个答案。
 */
export const fillOf = (db, row) => characterFieldOf(db, row)?.fill ?? row.fill;

/** 玩家**现在能落笔**的栏目——自建人物的可填笔数就是它的长度。 */
export const writableRows = (db) => rowPlan(db).filter((r) => fillOf(db, r) === 'patient_input');

/** 院方已写、玩家改不了的栏目。 */
export const lockedRows = (db) => rowPlan(db).filter((r) => fillOf(db, r) !== 'patient_input');

/** `character.fields` 里玩家可落的那几笔（取值必须来自闭集，校验器在管）。 */
export const writableFields = (db) =>
  (db.record_shell.character?.fields ?? []).filter((f) => f.fill === 'patient_input');

/** 姓 / 名两段闭集。姓名不落进 `character_vocab` 的 `values`，因为它是拼出来的。 */
export const namePool = (db) => db.character_source?.name_pool;

/** 院方记录上那个与自述不同的名字与编号（《无法离开医院》②「身份黏着」的物证）。 */
export const hospitalIdentity = (db) => db.character_source?.identity;

/** 默认人物（正典）。 */
export const defaultSourceId = (db) => db.character_source?.default;

export const isKnownSource = (db, source) => Boolean(characterSources(db)?.[source]);

/**
 * 某一条人物来源下、供渲染用的人物对象。
 *
 * - 正典人物：不覆盖任何东西，页眉回落到数据里的字面值（`record_shell.general[].value`）。
 * - 自建人物：只覆盖**玩家能落的那几笔**（姓名 / 性别）。
 *
 * ⚠️ 姓名是**两段选**：姓与名都选完才生效。只选了一半返回的仍是默认，
 * 以免出现「自述：李」这种半截名字。
 */
export function characterFor(db, { source, name, gender } = {}) {
  if (source !== 'custom') return { source: defaultSourceId(db) };
  const pool = namePool(db);
  const parts = typeof name === 'string' ? name.split('') : [];
  const surname = pool.surname.values.find((v) => parts.includes(v));
  const given = pool.given.values.find((v) => parts.includes(v));
  const knownGender = (db.character_vocab?.gender?.values ?? []).some((v) => v.id === gender);
  return {
    source: 'custom',
    ...(surname && given ? { name } : {}),
    ...(knownGender ? { gender } : {}),
  };
}

/** 玩家在界面上选出来的那个姓名（姓 + 名）。两段都选完才算落笔。 */
export const composeName = (db, { surname, given } = {}) => {
  const pool = namePool(db);
  if (!pool?.surname.values.includes(surname) || !pool?.given.values.includes(given)) return null;
  return `${surname}${given}`;
};

/** 闭集反向核：这个取值是不是登记在 `character_vocab` 里的。 */
export function optionLabel(db, key, valueId) {
  const spec = db.character_vocab?.[key];
  if (!spec || !valueId) return null;
  return spec.values.find((v) => v.id === valueId)?.label ?? null;
}

/**
 * 某一行患者侧那半的值。三档回落，顺序写死：
 *   ① 玩家这一局报上去的（自建人物） → 标「自述」，`resolved: true`
 *   ② 数据里的字面值（正典人物）      → 不标来源，`resolved: true`
 *   ③ 字面值也标了未填 / 没锚定        → 显示 `blank`，`resolved: false`
 */
function patientSide(db, row, character, answers) {
  if (row.value_from_source === 'name') {
    if (character?.name) return { text: character.name, label: '自述', resolved: true };
    // 自建人物还没报名字：显示空白态，不显示正典人物的名字。
    const literal = character?.source === 'custom' ? null : row.value;
    return { text: literal ?? row.blank, label: literal ? '自述' : null, resolved: Boolean(literal) };
  }
  if (row.value_from_source === 'gender') {
    const label = optionLabel(db, 'gender', character?.gender);
    return { text: label ?? row.blank, label: label ? '自述' : null, resolved: Boolean(label) };
  }
  if (row.value_from_source === 'onset') {
    const label = onsetLabelOf(db, answers);
    // 三件事还没答完时这一栏空着——不拿一个猜的年龄填上去。
    return label
      ? { text: label, label: '起病时间', resolved: true }
      : { text: row.blank, label: null, resolved: false };
  }
  return { text: row.value, label: null, resolved: true };
}

/**
 * 起病时间的粗档：直接借词表里已有的 `onset` 标签，不另立年龄词表。
 * 年龄栏**没有玩家可填件**，它读的就是你在现病史里认下的那一件事——
 * 所以"自述年龄与 onset 冲突"这个状态在本作里结构上不可能出现。
 */
export function onsetLabelOf(db, answers = {}) {
  if (!answers.onset) return null;
  return labelOf(db, 'onset', answers.onset);
}

/**
 * 页眉一般情况的一行，渲染所需的一切：
 * `{label, who, fill, blank, from, to, resolved}`。
 *
 * - `who` = 这一行主要挂在谁的笔迹下（决定颜色 / 标注）；
 * - `from` = 患者侧那一半（`to` 存在时才有）；
 * - `to` = 院方侧那一半（**永不由玩家写**，只可能是字面值）。
 */
export function recordRow(db, row, character = null, answers = {}) {
  const from = patientSide(db, row, character, answers);
  // 这一笔现在能不能落，由 `character.fields` 说了算（姓名那一笔就是靠这条与
  // 院方侧分开的：自述名玩家可选，`value_to` 永远是院方写好的字面值）。
  const fill = fillOf(db, row);
  const out = {
    label: row.label,
    who: row.who,
    fill,
    blank: row.blank,
    /** 有没有院方那一侧（两半分开写的行） */
    composite: row.value_to !== undefined,
    text: from.text,
    resolved: from.resolved,
    /** 这一笔现在由玩家落吗（`patient_input` 且没有院方侧压着） */
    writable: fill === 'patient_input',
    from,
    /** 玩家改不了的部分：院方写好的那一半 */
    lockedTo: row.value_to === undefined ? null : { text: row.value_to, resolved: true },
  };
  return out;
}

/** 整张页眉。 */
export const recordRows = (db, character = null, answers = {}) =>
  rowPlan(db).map((r) => recordRow(db, r, character, answers));

/** 自建人物的可选项：界面照它渲染闭集按钮，不在代码里写任何取值。 */
export function characterOptions(db) {
  return {
    name: {
      label: characterUi(db).custom_name,
      surname: namePool(db).surname,
      given: namePool(db).given,
    },
    gender: {
      label: db.character_vocab.gender.label,
      values: db.character_vocab.gender.values.map((v) => ({ ...v })),
    },
  };
}

// ── 主诉 ─────────────────────────────────────────────────────────────────

/** 主诉那一行的拼句模板：`{onset}` 起病缓急、`{duration_pattern}` 持续时间。 */
export const complaintTemplate = (db) => db.complaint;

/**
 * 患者自述的那一句（第 1 问的答案）——主诉里的**症状**那一半。
 * 取值来自 `complaint.self_report.values`（不是 `vocab`：自述的那个病不是记录 facet），
 * 没答就是 `null`，纸上的主诉栏显示自己的空白态。
 */
export function selfReportText(db, answers = {}) {
  const spec = db.complaint?.self_report;
  const id = answers.self_report;
  if (!spec || id === undefined || id === null) return null;
  return spec.values.find((v) => v.id === id)?.label ?? null;
}

/**
 * 三个答案 → 一行主诉：**自述的症状 + 起病缓急 + 持续时间**。
 * 三个答案没答全就返回 `null`（那一栏还没写成）——患者先自述，院方再补时间。
 *
 * 取值一律走数据（自述表 / `complaint.onset` / `complaint.duration_pattern`），
 * 所以它永远与词表同源；界面不许自己拼字。
 */
export function complaintText(db, answers = {}) {
  const c = db.complaint;
  const symptom = selfReportText(db, answers);
  const onset = answers.onset ? labelOf(db, 'onset', answers.onset) : null;
  const pattern = answers.duration_pattern ? labelOf(db, 'duration_pattern', answers.duration_pattern) : null;
  if (!symptom || !onset || !pattern) return null;
  return `${symptom}${c.self_report.join}${c.onset[answers.onset]}${c.duration_pattern[answers.duration_pattern]}`;
}

/** 现病史那一栏的起病缓急写法（主诉之外单独一句）。没答就显示等待态。 */
export const complaintOnset = (db, answers = {}) =>
  answers.onset ? db.complaint.onset[answers.onset] : db.complaint.onset_fallback;

/**
 * 主诉栏底下那两行附注：起病缓急 + 供史者的写法。
 * 两条都是现病史的法定写法（第十八条（三）1 的「起病缓急」与（一）的「病史陈述者」），
 * 所以它们跟着主诉一起出现，不另占屏。
 */
export function complaintNotes(db, answers = {}) {
  const c = db.complaint;
  return [
    { label: c.onset_label, text: complaintsOnsetText(db, answers), note: c.onset_note, source: c.historian_source },
    { label: c.label, text: complaintText(db, answers), note: c.empty, source: c.max_chars_source },
  ].filter((x) => x.text !== undefined).map((x, i) => ({ ...x, index: i, facets: complaintIngredients(db) }));
}

const complaintsOnsetText = (db, answers) => db.complaint.onset[answers.onset] ?? db.complaint.onset_fallback;

/**
 * 主诉由哪几问拼成（按问序）：拼句表里有它那一档的那几问——自述症状、起病缓急、病程形式。
 * 不另立一份名单：从 `complaint` 的键现算。
 */
const complaintIngredients = (db) => (db.interview?.questions ?? [])
  .filter((q) => q.facet in (db.complaint ?? {}))
  .map((q) => q.facet);

/**
 * 全部可能的主诉（自述症状 × 起病时间 × 病程形式）。
 * 校验器拿它做**可算判据**：字数、禁数字、禁诊断名，一次把每一条都过一遍。
 */
export function allComplaints(db) {
  const out = [];
  for (const symptom of (db.complaint?.self_report?.values ?? []).map((v) => v.id)) {
    for (const onset of (db.vocab?.onset?.values ?? []).map((v) => v.id)) {
      for (const pattern of (db.vocab?.duration_pattern?.values ?? []).map((v) => v.id)) {
        out.push({ self_report: symptom, onset, duration_pattern: pattern, text: complaintText(db, { self_report: symptom, onset, duration_pattern: pattern }) });
      }
    }
  }
  return out;
}

/**
 * 主诉的契约校验（开发期函数，没有任何 CI 在跑它）。
 *
 * 判据是可算的：`自述症状 × 起病时间 × 病程形式` 的**每一条**可能的主诉都不得超字数、
 * 不得含数字；起病缓急三档必须与词表 `onset` 的取值一一对应（多一个少一个都报错）；
 * 自述那张表自己也要有收口——取值非空、id 不重复、单值、有拼接符，且**必须有一问指到它**。
 *
 * `ddb` 可选：传了它，就多核一条——主诉里（含自述取值本身）不得出现诊断名。省级细则明文
 * 「原则上不能用诊断名称代替主诉」（检索记录 §5.6），而本作的病名是现成的
 * 26 条，所以这条判据不用新造词表就能机核。
 */
export function validateComplaint(db, ddb = null) {
  const errors = [];
  const warnings = [];
  const E = (code, detail) => errors.push({ code, detail });
  const c = db.complaint;
  if (!c) {
    E('complaint_missing', 'data 里没有 complaint 块');
    return { errors, warnings };
  }
  for (const p of ['label', 'onset_label', 'onset_fallback', 'historian', 'empty', 'source']) {
    if (!c[p] || !String(c[p]).trim()) E('complaint_key_missing', p);
  }
  if (!c.max_chars_source || !String(c.max_chars_source).trim()) E('complaint_without_source', 'max_chars');
  for (const p of ['onset', 'duration_pattern']) {
    if (!c[p] || typeof c[p] !== 'object') E('complaint_key_missing', p);
  }
  // 自述那一半（第 1 问的闭集）：它必须是**患者口吻的症状说法**，而且必须真的能拼进主诉。
  // 🔧 2026-09-27 阶段 4：原先主诉的症状是写死的一句常量，现在由患者自述，所以这一块
  // 也要有与词表同级的判据——否则「自述」会变成第二个无收口的词表。
  const sr = c.self_report;
  if (!sr || typeof sr !== 'object') E('complaint_key_missing', 'self_report');
  else {
    if (!sr.name || !String(sr.name).trim()) E('complaint_key_missing', 'self_report.name');
    if (!Array.isArray(sr.values) || !sr.values.length) E('complaint_self_report_empty', 'self_report.values');
    if (sr.multi === true) E('complaint_self_report_multi', '自述是单值：一行主诉只说一个症状');
    if (typeof sr.join !== 'string' || !sr.join) E('complaint_key_missing', 'self_report.join');
    const seen = new Set();
    for (const v of sr.values ?? []) {
      if (!v.id || !v.label || !String(v.label).trim()) E('complaint_self_report_incomplete', JSON.stringify(v));
      else if (seen.has(v.id)) E('complaint_self_report_duplicate', v.id);
      seen.add(v.id);
    }
    // 自述那一问必须真的指到这张表上（问诊不许自己另立一份取值）。
    const bySelfReport = (db.interview?.questions ?? []).filter((q) => q.answer_from === 'complaint');
    if (!bySelfReport.length) E('complaint_self_report_unasked', '没有一问的 answer_from 是 complaint');
    for (const q of bySelfReport) {
      if (q.facet !== 'self_report') E('complaint_self_report_axis_mismatch', `${q.id} → ${q.facet}`);
    }
  }
  // 先报"拼不出来"：词表里有一档而拼句表没给写法，这一路主诉就是空的——那是内容缺口。
  for (const facet of ['onset', 'duration_pattern']) {
    for (const v of db.vocab?.[facet]?.values ?? []) {
      if (!c[facet]?.[v.id] || !String(c[facet][v.id]).trim()) E('complaint_unresolvable', `${facet}=${v.id}`);
    }
    // 再报"键对不上"：少一档 / 多一档都要说，后者是自造取值。
    const want = (db.vocab?.[facet]?.values ?? []).map((v) => v.id).sort().join(',');
    const got = Object.keys(c[facet] ?? {}).sort().join(',');
    if (want !== got) E('complaint_values_mismatch', `${facet}: ${got} ≠ ${want}`);
  }
  // 每一条可能的主诉都要念得通：不超字数、不出现数字。
  for (const { self_report: symptom, onset, duration_pattern: pattern, text } of allComplaints(db)) {
    const at = `${symptom}×${onset}×${pattern}`;
    if (!text) {
      E('complaint_unresolvable', at);
      continue;
    }
    if ([...text].length > c.max_chars) E('complaint_too_long', `${at} ${[...text].length} > ${c.max_chars}`);
    if (/[0-9０-９]/.test(text)) E('complaint_has_digit', at);
  }
  // 用诊断名代替主诉 = 省级细则明文禁止的写法。病名从疾病契约来，不新造词表。
  if (ddb?.items?.length) {
    const lines = [
      ...allComplaints(db).map((x) => x.text),
      ...(sr?.values ?? []).map((v) => v.label),
      ...Object.values(c.onset ?? {}),
      ...Object.values(c.duration_pattern ?? {}),
      c.empty,
      c.onset_fallback,
    ].filter((x) => typeof x === 'string');
    for (const line of lines) {
      for (const d of ddb.items) {
        if (d.label && line.includes(d.label)) E('complaint_names_diagnosis', `${line} 含「${d.label}」`);
      }
    }
  }
  return { errors, warnings };
}
