import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import { developmentDefaultCharacter } from './dev-default.js'
import {
  answerCardinality,
  answerChoices,
  answerOptions,
  answersComplete,
  answersForceCombos,
  answersMatchRecord,
  byId,
  canSelect,
  facetIds,
  interviewPool,
  interviewQuestions,
  matchFacets,
  matchQuestions,
  matchedCount,
  mutexCanCoexist,
  poolCandidates,
  poolFloors,
  questionById,
  scoreAnswers,
  validate,
  validateInterview,
} from './opening.js'
import { diseaseCandidates, validateDiseases } from './diseases.js'
import { complaintText } from './character-source.js'

/**
 * 开局「一问一答 + 池子」契约。
 *
 * 玩家不再在 facet 上落锚：患者先自述疾病（第 1 问），病历撰写人再按七问追问；
 * 患者在闭集里答，答案当场写进病历；第 2–5 问（病前经历）的答案同时把**已经写好**的
 * 条目排到他面前，他逐条核对「以上属实」。
 * 主题红线：**你无法选择出现什么，只能选择怎么面对。**
 *
 * 这些断言是契约的可执行形式（全仓门禁已于 2026-09-17 撤销，测试是唯一的机械补偿）。
 * 来源：design/entities/经历结构.md §十 · design/presentation/开局病历填报.md §十三。
 *
 * 🔧 2026-09-27 阶段 3：由 anchors.test.js 平移而来。格（锚点组合）退役，判据一条没丢：
 * 「可完成性」「候选筛选力」「池子是唯一可选项」「每个取值可点」全部搬到池子口径上；
 * 断言的对象从 24 个格换成**全部已答前缀**。
 */

const QUESTIONS = interviewQuestions(db)
const PAPER = db.record_shell.paper
const ANSWER = { self_report: 'cannot_sleep',
  event: ['threat', 'loss'], context: 'school', relation: ['peers'], agency: 'coerced',
  onset: 'childhood', duration_pattern: 'intermittent', duration_span: 'short' }
const PAPER_WRITES = PAPER.columns.flatMap((c) => (c.writes ?? []).map((w) => ({ column: c.id, ...w })))

describe('八问：问法、答案闭集、写进哪一栏', () => {
  test('八问：第 1 问自述来自主诉块，其余七问一律来自 vocab', () => {
    expect(QUESTIONS).toHaveLength(8)
    // 患者先自述疾病 —— 它不是记录 facet，答案闭集在主诉块里（`answer_from: complaint`）。
    const first = QUESTIONS[0]
    expect(first.id).toBe('q_self_report')
    expect(first.facet).toBe('self_report')
    expect(first.answer_from).toBe('complaint')
    expect(first.matches).toBe(false)
    expect(first.who).toBe('patient')
    expect(answerOptions(db, first).values.map((v) => v.id))
      .toEqual(db.complaint.self_report.values.map((v) => v.id))
    // 自述那一句必须真的能拼进主诉（取值不许是没有出口的第二份词表）。
    const [firstSymptom] = db.complaint.self_report.values
    expect(complaintText(db, { self_report: firstSymptom.id, onset: 'childhood', duration_pattern: 'single' }))
      .toContain(firstSymptom.label)
    // 其余七问：答案一律来自 vocab，问诊不另立一份内容层。
    for (const q of QUESTIONS.slice(1)) {
      expect(q.answer_from).toBe('vocab')
      const opts = answerOptions(db, q)
      expect(opts.values.map((v) => v.id)).toEqual(db.vocab[q.facet].values.map((v) => v.id))
      expect(opts.values.map((v) => v.label)).toEqual(db.vocab[q.facet].values.map((v) => v.label))
      // 单值 / 多值也照词表走：问诊不另立一份形状。
      expect(opts.multi).toBe(db.vocab[q.facet].multi === true)
    }
    // 八问各问一次，不重不漏。
    expect(new Set(QUESTIONS.map((q) => q.facet)).size).toBe(8)
  })

  test('问序：患者自述 → 病历撰写人问病前经历 → 时间三问', () => {
    // owner 2026-09-27 裁定：患者应该先自述疾病，然后病历撰写人询问有哪些经历可能导致疾病。
    // 顺序写在数据里（`interview.questions` 的数组顺序），这里对着它比。
    expect(QUESTIONS.map((q) => q.id)).toEqual([
      'q_self_report', 'q_event', 'q_context', 'q_relation', 'q_agency',
      'q_onset', 'q_duration_pattern', 'q_duration_span',
    ])
    // 时间三问在经历四问之后：它们是院方为写现病史补问的，不是玩家的入口。
    expect(QUESTIONS.map((q) => q.matches === true))
      .toEqual([false, true, false, true, true, false, false, false])
    expect(QUESTIONS.slice(1, 5).map((q) => q.facet)).toEqual(['event', 'context', 'relation', 'agency'])
    expect(QUESTIONS.slice(5).map((q) => q.facet)).toEqual(['onset', 'duration_pattern', 'duration_span'])
  })

  test('答案闭集的规模（每问几个取值、多值问几种组合）', () => {
    const sizes = Object.fromEntries(answerCardinality(db).map((x) => [x.facet, x.answers]))
    expect(sizes).toEqual({
      self_report: db.complaint.self_report.values.length,
      event: 92, context: 5, relation: 64, agency: 4,
      onset: 3, duration_pattern: 3, duration_span: 3,
    })
    // 多值问的取值上都带 min/max：超出范围的组合根本按钮不起来。
    expect(answerOptions(db, questionById(db, 'q_event')).maxItems).toBe(3)
    expect(answerOptions(db, questionById(db, 'q_relation')).minItems).toBe(0)
    expect(answerOptions(db, questionById(db, 'q_relation')).emptyLabel).toBe(db.vocab.relation.empty_label)
    // 自述是单值：一行主诉只说一个症状。
    expect(answerOptions(db, questionById(db, 'q_self_report')).multi).toBe(false)
  })

  test('每一问都有一个栏目接着：纸上有地方写', () => {
    for (const q of QUESTIONS) {
      expect(PAPER_WRITES.filter((w) => w.from === q.id).length, q.id).toBeGreaterThan(0)
    }
  })

  test('只写病历、不参与筛选的问：自述 + 时间三问 + 「这些事发生在哪儿」', () => {
    // 🔧 2026-09-27 复核改：「发生在哪儿」从筛选降为排序。原因是它当筛子时，
    // 严格相符的条目必然只落在一个地方（实测严格集地方跨度恒为 1），
    // 而配额要求池子跨 ≥4 个地方 —— 两条要求互斥，96.7% 的前缀只能靠放宽兜住。
    // 理由与数字逐字写在 data/opening.json 的 q_context.basis.why_not_a_filter。
    expect(matchFacets(db)).toEqual(['event', 'relation', 'agency'])
    expect(matchQuestions(db).map((q) => q.id)).toEqual(['q_event', 'q_relation', 'q_agency'])
    expect(db.interview.questions.filter((q) => !q.matches).map((q) => q.id))
      .toEqual(['q_self_report', 'q_context', 'q_onset', 'q_duration_pattern', 'q_duration_span'])
    // 不参与筛选的那几问仍然写进病历：主诉、现病史、个人史都靠它们。
    for (const id of ['q_self_report', 'q_onset', 'q_duration_pattern', 'q_duration_span', 'q_context']) {
      expect(PAPER_WRITES.filter((w) => w.from === id).length, id).toBeGreaterThan(0)
    }
  })

  test('八问全答完才算答完（纸上的现病史与主诉才写得成）', () => {
    expect(answersComplete(db, {})).toBe(false)
    expect(answersComplete(db, { ...ANSWER, onset: undefined })).toBe(false)
    expect(answersComplete(db, { ...ANSWER, self_report: undefined })).toBe(false)
    expect(answersComplete(db, ANSWER)).toBe(true)
    // 多值问答成空数组仍是「答过了」（一个人）。
    expect(answersComplete(db, { ...ANSWER, relation: [] })).toBe(true)
  })
})

describe('谁答哪一面：完全划分，输出槽永不在患者侧', () => {
  const patient = db.interview.who_answers.patient.map((x) => x.facet)
  const hospital = db.interview.who_answers.hospital.map((x) => x.facet)

  test('11 个 facet 不重不漏地分成 patient / hospital 两份', () => {
    expect([...patient, ...hospital].sort()).toEqual([...facetIds(db)].sort())
    expect(new Set([...patient, ...hospital]).size).toBe(facetIds(db).length)
  })

  test('输出槽不由患者答（它是结果不是处境）', () => {
    expect(patient).not.toContain('consequence')
    expect(hospital).toContain('consequence')
  })

  test('患者侧的每一条都指得回一问，且 facet 对得上', () => {
    for (const x of db.interview.who_answers.patient) {
      const q = questionById(db, x.by)
      expect(q, x.facet).toBeTruthy()
      expect(q.facet).toBe(x.facet)
      expect(x.basis.trim().length).toBeGreaterThan(0)
    }
    for (const x of db.interview.who_answers.hospital) expect(x.basis.trim().length).toBeGreaterThan(0)
  })
})

describe('答案侧的非法组合：自相矛盾的答案在按钮上就灰掉', () => {
  test('「瞬时 × 持续不断」灰掉，「瞬时 × 单次」可点', () => {
    const answers = { onset: 'childhood', duration_span: 'instant' }
    const pattern = answerChoices(db, answers).find((c) => c.facet === 'duration_pattern')
    const continuous = pattern.values.find((v) => v.id === 'continuous')
    expect(continuous.ok).toBe(false)
    expect(continuous.reasons[0].code).toBe('answer_combo_forbidden')
    expect(continuous.reasons[0].combo).toBe('fc_02')
    expect(pattern.values.find((v) => v.id === 'single').ok).toBe(true)
  })

  test('非法组合用的是同一份 forbidden_combos，不存在第二套匹配语义', () => {
    expect(answersForceCombos(db, { duration_span: 'instant', duration_pattern: 'continuous' })
      .map((f) => f.id)).toEqual(['fc_02'])
    expect(answersForceCombos(db, { context: 'school', relation: ['partner'] }).map((f) => f.id)).toEqual(['fc_01'])
    expect(answersForceCombos(db, { context: 'school', relation: ['peers'] })).toEqual([])
    // 还没答的问不算命中：答一半不会误判。
    expect(answersForceCombos(db, { duration_span: 'instant' })).toEqual([])
  })

  test('多值问选满上限后其余取值不可点', () => {
    const event = answerChoices(db, { event: ['gain', 'loss', 'conflict'] }).find((c) => c.facet === 'event')
    const other = event.values.find((v) => v.id === 'threat')
    expect(other.chosen).toBe(false)
    expect(other.ok).toBe(false)
    expect(other.reasons[0].code).toBe('answer_items_full')
    expect(event.maxItems).toBe(3)
  })
})

describe('池子：匹配规则与排序', () => {
  const rec = byId(db, 'exp_0001') // context=family, relation=[parents], event=[loss]

  test('单值问要求相同；多值问要求至少有一个相同', () => {
    expect(answersMatchRecord(db, rec, 'context', 'family')).toBe(true)
    expect(answersMatchRecord(db, rec, 'context', 'work')).toBe(false)
    expect(answersMatchRecord(db, rec, 'event', ['loss', 'threat'])).toBe(true)
    expect(answersMatchRecord(db, rec, 'event', ['gain'])).toBe(false)
  })

  test('答「一个人」时只与「和谁」为空的记录相符', () => {
    const alone = byId(db, 'exp_0004') // relation: []
    expect(answersMatchRecord(db, alone, 'relation', [])).toBe(true)
    expect(answersMatchRecord(db, rec, 'relation', [])).toBe(false)
    // 未答与答「一个人」是两件事：未答的问不计入相符问数。
    expect(matchedCount(db, alone, {})).toBe(0)
    expect(matchedCount(db, alone, { relation: [] })).toBe(1)
  })

  test('相符问数：匹配的答案越多，条目排得越前', () => {
    const answers = { event: ['loss'], relation: ['parents'], agency: 'powerless' }
    const scored = scoreAnswers(db, answers)
    expect(scored.answered).toBe(3)
    const first = poolCandidates(db, answers, 'matched_any')[0]
    expect(matchedCount(db, first, answers)).toBe(3)
    const ordered = poolCandidates(db, answers, 'matched_any').map((r) => matchedCount(db, r, answers))
    expect([...ordered].sort((a, b) => b - a)).toEqual(ordered)
  })

  test('池子下限是推出来的：10 段 · 4 个地方 · 病并集 2–4', () => {
    const f = poolFloors(db, ddb)
    expect(f.minSize).toBe(db.quota.total)
    expect(f.minContexts).toBe(Math.ceil(db.quota.total / db.quota.per_value_max))
    expect(f.minContexts).toBe(4)
    expect(f.minDiseases).toBe(ddb.pool_rule.diseases_min)
    expect(f.maxDiseases).toBe(ddb.pool_rule.diseases_max)
  })

  test('池子装得下十段、跨得开、病并集在界内，且不超过展示上限', () => {
    const pool = interviewPool(db, ddb, ANSWER)
    expect(pool.size).toBeGreaterThanOrEqual(db.quota.total)
    expect(pool.size).toBeLessThanOrEqual(db.interview.pool.display_size)
    expect(pool.contexts).toBeGreaterThanOrEqual(4)
    expect(pool.diseaseUnion).toBeGreaterThanOrEqual(ddb.pool_rule.diseases_min)
    expect(pool.diseaseUnion).toBeLessThanOrEqual(ddb.pool_rule.diseases_max)
    expect(pool.meets).toBe(true)
    // 每处最多 quota.per_value_max 条：池子与配额是同一条口径。
    const byContext = {}
    for (const id of pool.ids) {
      const v = byId(db, id)[db.quota.per_facet]
      byContext[v] = (byContext[v] || 0) + 1
    }
    for (const n of Object.values(byContext)) expect(n).toBeLessThanOrEqual(db.quota.per_value_max)
  })

  test('池内认满十段是可行的：每一段都能认，且认完仍不算死局', () => {
    const pool = interviewPool(db, ddb, ANSWER)
    const sel = []
    for (const id of pool.ids) {
      if (sel.length === db.quota.total) break
      const verdict = canSelect(db, sel, id, pool.ids)
      expect(verdict.ok, `${id} ${JSON.stringify(verdict.reasons)}`).toBe(true)
      sel.push(id)
    }
    expect(sel).toHaveLength(db.quota.total)
  })
})

describe('永不锁死：任何已答前缀下都选得到十段', () => {
  test('全部已答前缀的实测（分支数 / 放宽分支 / 最坏池子 / 最坏跨度）', () => {
    const census = validateInterview(db, ddb, { census: 'full' }).census
    // ① 分支总数：参与筛选的那几问的每一种合法答案状态（含「还没答」）
    //    🔧 2026-09-27 复核改：「发生在哪儿」退出筛选后，这一层从 166470 降到 30225
    //    （筛选维从 4 个降到 3 个：event × relation × agency）。
    expect(census.branches).toBe(30225)
    // 参与筛选的问里没有会被非法组合判掉的取值对（fc_01 是 context × relation 的事，
    // 而 context 已不参与筛选，所以这一层归零）。
    expect(census.illegalStates).toBe(0)
    // ② 需要放宽的分支数（跳过了「每一问都相符」那一级）：96.7% → 81.9%
    expect(census.relaxedBranches).toBe(24741)
    expect(Object.keys(census.levelCounts).sort()).toEqual(['library', 'matched_all', 'matched_any', 'matched_drop_one'])
    // ③ 最坏池子规模 ④ 最坏地方跨度：一条也不许掉到下限之下
    expect(census.minSize).toBe(10)
    expect(census.minContexts).toBe(4)
    // 池病并集落在 pool_rule 的 2–4 里
    expect(census.minDiseaseUnion).toBeGreaterThanOrEqual(ddb.pool_rule.diseases_min)
    expect(census.maxDiseaseUnion).toBeLessThanOrEqual(ddb.pool_rule.diseases_max)
    // 没有任何一个前缀凑不出合格的池子
    expect(census.floorBreaks).toBe(0)
  }, 60000)

  test('抽样的那一档也得零错（校验器的默认档随时可跑）', () => {
    const { errors, warnings, census } = validateInterview(db, ddb)
    expect(errors).toEqual([])
    // 默认档 = 已答 ≤2 问的全跑 + 其余抽 1/40；这里只要求它仍然覆盖两成以上分支，
    // 不写死条数——筛选维一变，分支总数就会变（见上一条实测）。
    expect(census.testedBranches).toBeGreaterThan(census.branches * 0.2)
    expect(census.floorBreaks).toBe(0)
    expect([...new Set(warnings.map((w) => w.code))]).toEqual(['interview_pool_relaxed'])
  })

  test('自述与时间三问换成别的答案，池子与已核对的条目都不受影响', () => {
    const base = { event: ['loss'], context: 'family' }
    const a = interviewPool(db, ddb, {
      ...base, self_report: 'cannot_sleep', onset: 'childhood', duration_pattern: 'intermittent',
    })
    const b = interviewPool(db, ddb, {
      ...base, self_report: 'hearing', onset: 'adulthood', duration_pattern: 'single',
    })
    expect(a.ids).toEqual(b.ids)
    expect(a.level).toBe(b.level)
  })
})

describe('池子是唯一可选项：界面拿不到池外的东西', () => {
  const pool = interviewPool(db, ddb, ANSWER)
  const outsider = db.experiences.find((r) => !pool.ids.includes(r.id)).id

  test('池外的记录被理由码 not_in_pool 挡住', () => {
    const verdict = canSelect(db, [], outsider, pool.ids)
    expect(verdict.ok).toBe(false)
    expect(verdict.reasons.map((r) => r.code)).toContain('not_in_pool')
  })

  test('整库口径不受影响（属性与候选仍按库结算）', () => {
    expect(canSelect(db, [], outsider).ok).toBe(true)
  })

  test('每个已答状态下池子都非空，且每条都能被认', () => {
    for (const answers of [{}, { event: ['exposure'] }, ANSWER, { ...ANSWER, relation: [] }]) {
      const p = interviewPool(db, ddb, answers)
      expect(p.size).toBeGreaterThan(0)
      for (const id of p.ids.slice(0, db.quota.total)) {
        expect(canSelect(db, [], id, p.ids).ok).toBe(true)
      }
    }
  })
})

describe('与疾病契约的接缝', () => {
  test('池病并集 u_pool 在 pool_rule 的上下界内，候选筛选力仍成立', () => {
    const { diseases_min: lo, diseases_max: hi } = ddb.pool_rule
    const pool = interviewPool(db, ddb, ANSWER)
    expect(pool.diseaseUnion).toBeGreaterThanOrEqual(lo)
    expect(pool.diseaseUnion).toBeLessThanOrEqual(hi)
    // 候选上界 = min(c·k, u_pool)：u_pool ≤ 4 时远小于名册 26。
    const { profiles_per_experience_max: c, opening_experience_total: k, roster_size } = ddb.filter_rule
    const bound = Math.min(c * k, ddb.pool_rule.diseases_max)
    expect(bound).toBe(4)
    expect(bound).toBeLessThan(roster_size)
    expect(roster_size - bound).toBe(22)
  })

  test('任意一局的候选都装不下名册', () => {
    const pool = interviewPool(db, ddb, ANSWER)
    const cands = diseaseCandidates(db, ddb, pool.ids.slice(0, db.quota.total))
    expect(cands.length).toBeLessThan(ddb.filter_rule.roster_size)
    expect(cands.length).toBeGreaterThan(0)
  })

  test('互斥的死条款判据换成了「病并集超过池子上界」', () => {
    expect(db.mutex).toEqual([])
    for (const r of db.experiences.slice(0, 40)) {
      expect(mutexCanCoexist(db, ddb, 'exp_0001', r.id)).toBe(true)
    }
    // 反例：给两条各配 3 / 2 张病，并集 5 > 4 —— 它们永远进不了同一个池子。
    const clone = JSON.parse(JSON.stringify(db))
    clone.experiences.find((r) => r.id === 'exp_0001').diseases = ['dis_0001', 'dis_0002', 'dis_0003']
    clone.experiences.find((r) => r.id === 'exp_0002').diseases = ['dis_0010', 'dis_0011']
    clone.mutex = [['exp_0001', 'exp_0002']]
    expect(validate(clone, ddb).errors.map((e) => e.code)).toContain('mutex_never_cooccurs')
  })

  test('每张病都真的有入口', () => {
    expect(validateDiseases(db, ddb).errors).toEqual([])
  })
})

describe('契约自洽与反例（形变实测）', () => {
  const mutate = (fn) => {
    const clone = JSON.parse(JSON.stringify(db))
    fn(clone)
    return validateInterview(clone, ddb, { census: 'sample' }).errors.map((e) => e.code)
  }

  test('validateInterview 零错误，唯一的警告是「有前缀需要放宽」', () => {
    const { errors, warnings } = validateInterview(db, ddb, { census: 'full' })
    expect(errors).toEqual([])
    expect([...new Set(warnings.map((w) => w.code))]).toEqual(['interview_pool_relaxed'])
    expect(warnings).toHaveLength(1)
  }, 60000)

  test('反例：缺 source / 缺问法 / 答案来源不是 vocab', () => {
    expect(mutate((d) => { delete d.interview.source })).toContain('config_without_source')
    expect(mutate((d) => { d.interview.questions[0].ask = '' })).toContain('interview_question_incomplete')
    expect(mutate((d) => { d.interview.questions[0].answer_from = '手写' }))
      .toContain('interview_answer_source_unsupported')
    expect(mutate((d) => { delete d.interview.questions[0].basis })).toContain('interview_reason_missing')
    expect(mutate((d) => { d.interview.questions[1].id = d.interview.questions[0].id }))
      .toContain('interview_question_duplicate')
  })

  test('反例：问未登记的 facet / 问一个不由患者答的 facet', () => {
    // 第 1 问是患者自述（答案来自主诉块），所以「未登记的 facet」要拿第 2 问（vocab 那一问）来试。
    expect(mutate((d) => { d.interview.questions[1].facet = 'nope' })).toContain('interview_facet_unknown')
    // 「留下什么」是输出槽，医生不会拿它去问患者。
    expect(mutate((d) => { d.interview.questions[1].facet = 'consequence' }))
      .toContain('interview_question_not_patient')
  })

  test('反例：不是记录 facet 的答案轴不许当筛子、不许与 facet 重名、必须标患者', () => {
    // 自述的那个病拿不到任何记录的取值，所以它一旦参与相符判断，红线就破了。
    expect(mutate((d) => { d.interview.questions[0].matches = true }))
      .toContain('interview_nonfacet_question_matches')
    // 与记录 facet 重名的「自述」= 悄悄多出一个 facet 的入口。
    expect(mutate((d) => { d.interview.questions[0].facet = 'event' }))
      .toContain('interview_facet_source_conflict')
    expect(mutate((d) => { d.interview.questions[0].who = 'hospital' }))
      .toContain('interview_question_not_patient')
    // 答案闭集被抽空 = 这一问没有可答的东西。
    expect(mutate((d) => { d.complaint.self_report.values = [] }))
      .toContain('interview_question_without_closed_set')
  })

  test('反例：分类漏掉一个 facet / 重复分类 / 输出槽被患者答', () => {
    expect(mutate((d) => { d.interview.who_answers.patient = d.interview.who_answers.patient.filter((x) => x.facet !== 'agency') }))
      .toContain('interview_facet_unclassified')
    expect(mutate((d) => { d.interview.who_answers.patient.push({ facet: 'onset', by: 'q_onset', basis: 'x' }) }))
      .toContain('interview_facet_multiply_classified')
    expect(mutate((d) => {
      d.interview.who_answers.hospital = d.interview.who_answers.hospital.filter((x) => x.facet !== 'consequence')
      d.interview.who_answers.patient.push({ facet: 'consequence', by: 'q_event', basis: 'x' })
    })).toContain('interview_output_facet_answered_by_patient')
  })

  test('反例：患者侧指不回任何一问', () => {
    expect(mutate((d) => { d.interview.who_answers.patient[0].by = 'q_nope' }))
      .toContain('interview_patient_answer_without_question')
    expect(mutate((d) => { d.interview.who_answers.patient[0].by = 'q_event' }))
      .toContain('interview_question_mismatch')
  })

  test('反例：放宽阶梯缺级 / 少一条口径说明', () => {
    expect(mutate((d) => { d.interview.pool.ladder.pop() })).toContain('interview_ladder_incomplete')
    expect(mutate((d) => { d.interview.pool.ladder[1].level = 'matched_all' })).toContain('interview_ladder_incomplete')
    expect(mutate((d) => { delete d.interview.pool.ladder_note })).toContain('interview_pool_rule_missing')
  })

  test('反例：展示上限缩到十段以下 → interview_pool_display_too_small', () => {
    expect(mutate((d) => { d.interview.pool.display_size = 9 })).toContain('interview_pool_display_too_small')
  })

  test('反例：某一问没有栏目接着 → interview_question_without_column', () => {
    expect(mutate((d) => {
      d.record_shell.paper.columns.forEach((c) => {
        if (c.writes) c.writes = c.writes.filter((w) => w.from !== 'q_agency')
      })
    })).toContain('interview_question_without_column')
  })

  test('反例：把池子的选项抽稀，最坏池子掉到十段以下', () => {
    const clone = JSON.parse(JSON.stringify(db))
    // 只留 60 段：池子再也凑不出「跨 4 个地方 + 病并集 2–4 + 十段」。
    clone.experiences = clone.experiences.slice(0, 60)
    const codes = validateInterview(clone, ddb, { census: 'full' }).errors.map((e) => e.code)
    expect(codes).toContain('interview_pool_never_locks')
  }, 60000)

  test('反例：屏文案漏内部实现词', () => {
    expect(mutate((d) => { d.interview.screen.note = '医生按锚点问。' })).toContain('interview_copy_leaks_internal')
    expect(mutate((d) => { d.interview.questions[0].ask = '你的输出槽是什么' }))
      .toContain('interview_copy_leaks_internal')
    expect(mutate((d) => { d.interview.screen.pool_note = '' })).toContain('interview_copy_missing')
  })
})

describe('开发默认人物：夹具必须真的是一组合法选择', () => {
  test('八问答案 + 池子里的十段 + 一张病都落在契约内', () => {
    const { answers, experiences, diseases } = developmentDefaultCharacter
    expect(answersComplete(db, answers)).toBe(true)
    const pool = interviewPool(db, ddb, answers)
    for (const id of experiences) expect(pool.ids).toContain(id)
    const sel = []
    for (const id of experiences) {
      expect(canSelect(db, sel, id, pool.ids).ok).toBe(true)
      sel.push(id)
    }
    expect(sel).toHaveLength(db.quota.total)
    const cands = diseaseCandidates(db, ddb, sel).map((d) => d.id)
    for (const id of diseases) expect(cands).toContain(id)
  })
})
