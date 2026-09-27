import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import {
  META_COPY_PATHS,
  bandOf,
  collectStrings,
  byId,
  canSelect,
  canStillComplete,
  clauseHits,
  describe as describeRecord,
  diseaseCandidates,
  evalSelector,
  evalView,
  facetIds,
  labelOf,
  mutexCanCoexist,
  mutexNeighbors,
  quotaState,
  renderTable,
  settleAttributes,
  timeline,
  validate,
  valuesOf,
  viewIndex,
} from './opening.js'

/**
 * 开局经历契约。
 *
 * 这些断言是契约的**可执行形式**——它们是"没有门禁"这件事的唯一补偿：
 * data/opening.json 每次改动都应当能过完这一套。
 * 来源：design/entities/经历结构.md §六（不变量）与 §七（反例清单）。
 */

describe('契约自洽', () => {
  test('validate() 零错误', () => {
    const { errors } = validate(db)
    expect(errors).toEqual([])
  })

  test('仅允许已知的、被明确记录在案的警告', () => {
    const { warnings } = validate(db)
    // 内容批（288 条）落地后连 `thin_view` 也没有了：六个视图都有 ≥3 条记录。
    // 出现任何**新的**警告码都必须先补进 §八，否则这条会红。
    expect(warnings).toEqual([])
  })
})

describe('数据结构：没有归属键', () => {
  test('记录里不存在任何类别 / 主题 / 父类字段', () => {
    const forbidden = ['category', 'theme', 'parent', 'kind', 'class', 'views', 'tags', 'note', 'comment']
    for (const r of db.experiences) {
      for (const k of forbidden) expect(Object.keys(r)).not.toContain(k)
    }
  })

  test('每个 facet 都答得出「调用方拿它查什么」', () => {
    for (const f of facetIds(db)) {
      expect(typeof db.vocab[f].ask).toBe('string')
      expect(db.vocab[f].ask.trim().length).toBeGreaterThan(0)
    }
  })

  test('视图不写进记录——删掉任意视图，记录数据不受影响', () => {
    const ids = db.experiences.map((r) => r.id)
    const withoutViews = { ...db, views: [] }
    expect(withoutViews.experiences.map((r) => r.id)).toEqual(ids)
    expect(() => evalView(withoutViews, 'view_family')).toThrow()
  })
})

describe('词表是唯一的取值来源', () => {
  test('clauseHits 对未登记取值不做字符串猜测', () => {
    expect(() => labelOf(db, 'agency', '有点被动')).toThrow()
    expect(() => labelOf(db, 'nope', 'x')).toThrow()
  })

  test('单值 facet 归一化后仍可被 empty 子句命中', () => {
    const rec = byId(db, 'exp_0004') // relation: []
    expect(clauseHits(rec, { facet: 'relation', empty: true })).toBe(true)
    expect(clauseHits(rec, { facet: 'context', empty: true })).toBe(false)
  })

  test('多值 facet 按集合相交判定', () => {
    const rec = byId(db, 'exp_0003') // event: threat, loss, exposure
    expect(clauseHits(rec, { facet: 'event', in: ['threat'] })).toBe(true)
    expect(clauseHits(rec, { facet: 'event', not_in: ['threat'] })).toBe(false)
  })
})

describe('配额与选择合法性', () => {
  test('配额轴是单值 facet，且上限×取值数 ≥ 总额（不锁死玩家）', () => {
    const f = db.quota.per_facet
    expect(db.vocab[f].multi).toBe(false)
    expect(db.quota.per_value_max * valuesOf(db, f).length).toBeGreaterThan(db.quota.total)
  })

  test('空选择可以补满', () => {
    expect(canStillComplete(db, [])).toBe(true)
  })

  test('互斥已退役；死条款的判据从「跨格」换成「病并集超过池子上界」', () => {
    // 格退役之后，池子不再只装一格，所以"跨格互斥是死条款"这句判据不成立了
    // （见 design/entities/经历结构.md §十）。换上的判据是可算的那一条：两条的病并集
    // 超过池子的病并集上界时，它们永远进不了同一个池子。
    expect(db.mutex).toEqual([])
    expect(mutexNeighbors(db, 'exp_0006')).toEqual([])
    expect(mutexCanCoexist(db, ddb, 'exp_0001', 'exp_0006')).toBe(true)

    const clone = JSON.parse(JSON.stringify(db))
    clone.experiences.find((r) => r.id === 'exp_0001').diseases = ['dis_0001', 'dis_0002', 'dis_0003']
    clone.experiences.find((r) => r.id === 'exp_0006').diseases = ['dis_0010', 'dis_0011']
    clone.mutex = [['exp_0001', 'exp_0006']]
    expect(validate(clone, ddb).errors.map((e) => e.code)).toContain('mutex_never_cooccurs')
  })

  test('同一个「在哪」选满后，该类的其余记录被拦，理由是 quota_value_full', () => {
    const inFamily = db.experiences.filter((r) => r.context === 'family').map((r) => r.id)
    expect(inFamily.length).toBeGreaterThanOrEqual(db.quota.per_value_max)
    const picked = inFamily.slice(0, db.quota.per_value_max)
    const next = db.experiences.find((r) => r.context === 'family' && !picked.includes(r.id))
    const r = canSelect(db, picked, next.id)
    expect(r.reasons.map((x) => x.code)).toContain('quota_value_full')
  })

  test('只用 canSelect 就能选满，且分布不必是均分', () => {
    const sel = []
    while (sel.length < db.quota.total) {
      const pick = db.experiences.find((r) => !sel.includes(r.id) && canSelect(db, sel, r.id).ok)
      expect(pick).toBeTruthy()
      sel.push(pick.id)
    }
    const q = quotaState(db, sel)
    expect(q.used).toBe(db.quota.total)
    expect(q.remaining).toBe(0)
    // 上限为 2 时这里必然是 2/2/2/2/2；为 3 才可能出现偏科。
    expect(Object.values(q.byValue).some((n) => n < db.quota.per_value_max)).toBe(true)
  })
})

describe('结算：数值只来自数据', () => {
  test('把某一类选满上限，原始总和 = 段数 × 净值', () => {
    const sel = db.experiences.filter((r) => r.context === 'work').map((r) => r.id)
    const s = settleAttributes(db, sel)
    expect(s.totalRaw).toBe(sel.length * db.effects_rule.net)
    expect(s.totalRaw).toBe(sel.length * 2)
  })

  test('起始值为 0 时，没投过点的属性停在笨拙', () => {
    expect(db.base_attributes.finesse).toBe(0)
    expect(bandOf(db, 0).label).toBe('笨拙')
    // 挑十段**没有**碰到巧手的经历：起始 0 必须原样落在「笨拙」，且没有溢出。
    const sel = db.experiences
      .filter((r) => r.context === 'work' && !r.effects.attributes.finesse)
      .slice(0, db.quota.total)
      .map((r) => r.id)
    expect(sel).toHaveLength(db.quota.total)
    const s = settleAttributes(db, sel)
    expect(s.raw.finesse).toBe(0)
    expect(s.band.finesse.label).toBe('笨拙')
    expect(s.overflow.finesse).toBe(0)
  })

  test('档位表覆盖 0–10 且端点归属正确', () => {
    expect(bandOf(db, 2).label).toBe('笨拙')
    expect(bandOf(db, 3).label).toBe('协调')
    expect(bandOf(db, 9).label).toBe('娴熟')
    expect(bandOf(db, 10).label).toBe('本能')
    expect(() => bandOf(db, 11)).toThrow()
  })
})

describe('视图与输出', () => {
  test('视图计数与 selector 求值一致', () => {
    for (const entry of viewIndex(db)) {
      expect(evalView(db, entry.id).length).toBe(entry.count)
    }
  })

  test('「长期反复」是两 facet 合取，不是单个复合取值', () => {
    const hit = evalView(db, 'view_long_repeat')
    expect(hit.length).toBeGreaterThan(0)
    for (const r of hit) {
      expect(r.duration_span).toBe('long')
      expect(r.duration_pattern).toBe('intermittent')
    }
  })

  test('每 facet 的名字都是卡面上读得出口的话，不是设计系统黑话', () => {
    // `name` 会被 describe() 渲染到卡面，所以它是玩家可见文案。
    // 这份黑名单防的是"从系统内部视角命名"——初版把 relation 叫过「对手方」
    // （金融术语 counterparty，且中文「对手」含敌意），context 叫过「场域」。
    const jargon = ['对手方', '场域', '权位', '照护位', '归属状态', '控制权', '后果出口', '输出槽', '跨度', '维度']
    for (const f of facetIds(db)) {
      const name = db.vocab[f].name
      expect(typeof name).toBe('string')
      for (const w of jargon) expect(name).not.toContain(w)
    }
  })

  test('空的「和谁」按词表念成「一个人」，而不是空行', () => {
    expect(db.vocab.relation.empty_label).toBe('一个人')
    const row = describeRecord(db, 'exp_0004').facets.find((f) => f.facet === 'relation') // relation: []
    expect(row.name).toBe('和谁')
    expect(row.values).toEqual(['一个人'])
  })

  test('允许空数组的多值 facet 必须给出 empty_label', () => {
    const clone = JSON.parse(JSON.stringify(db))
    delete clone.vocab.relation.empty_label
    expect(validate(clone).errors.map((e) => e.code)).toContain('multi_facet_without_empty_label')
  })

  test('「留下了什么」是输出槽，不出现在卡面的分组行里', () => {
    expect(db.vocab.consequence.output).toBe(true)
    const d = describeRecord(db, 'exp_0001')
    expect(d.facets.map((f) => f.facet)).not.toContain('consequence')
    expect(d.facets).toHaveLength(10)
    expect(d.channels).toEqual(['能力', '关系', '信念', '情绪反应'])
  })

  test('输出槽必须恰好一个', () => {
    const zero = JSON.parse(JSON.stringify(db))
    delete zero.vocab.consequence.output
    expect(validate(zero).errors.map((e) => e.code)).toContain('output_facet_count')

    const two = JSON.parse(JSON.stringify(db))
    two.vocab.event.output = true
    expect(validate(two).errors.map((e) => e.code)).toContain('output_facet_count')
  })

  test('describe 给出玩家可读标签，且不猜字符串', () => {
    const d = describeRecord(db, 'exp_0001')
    expect(d.title).toBe('空着的碗筷')
    expect(d.facets.find((f) => f.facet === 'context').values).toEqual(['家庭'])
    expect(d.channels).toContain('信念')
  })

  test('时间线按「从什么时候开始」排序', () => {
    const order = valuesOf(db, 'onset')
    const line = timeline(db, ['exp_0009', 'exp_0016', 'exp_0003'])
    const idx = line.map((r) => order.indexOf(r.onset))
    expect([...idx].sort((a, b) => a - b)).toEqual(idx)
  })

  test('疾病候选带来源经历（名册在 data/diseases.json）', () => {
    const cands = diseaseCandidates(db, ddb, ['exp_0001', 'exp_0004'])
    expect(cands.map((c) => c.id).sort()).toEqual(['dis_0003', 'dis_0004', 'dis_0012'])
    expect(cands.find((c) => c.id === 'dis_0004').from).toEqual(['exp_0001'])
    // ⚠️ id 不变但语义全变了：dis_0004 从占位「躯体耗损」变成真实的躯体症状障碍。
    // 这个断言就是为了让那次静默改写显形——旧映射必须重新配（疾病结构.md §八 缺口 1）。
    expect(cands.find((c) => c.id === 'dis_0004').label).toBe('躯体症状障碍')
  })

  test('renderTable 是派生视图，不是第二份数据', () => {
    const table = renderTable(db)
    expect(table.split('\n')).toHaveLength(db.experiences.length + 1)
    expect(table).toContain('exp_0001')
  })
})

describe('反例：这些写法必须被拒绝', () => {
  const mutate = (fn) => {
    const clone = JSON.parse(JSON.stringify(db))
    fn(clone)
    return validate(clone).errors.map((e) => e.code)
  }

  test('加类别归属键 → record_unknown_field', () => {
    expect(mutate((d) => { d.experiences[0].category = '家庭创伤' })).toContain('record_unknown_field')
  })

  test('加自由文本标签 → record_unknown_field', () => {
    expect(mutate((d) => { d.experiences[0].tags = ['被忽视'] })).toContain('record_unknown_field')
  })

  test('把语义藏回文案 → text_has_facet_word', () => {
    expect(mutate((d) => { d.experiences[0].summary = '从小就是这样。' })).toContain('text_has_facet_word')
  })

  test('文案里出现数字 → text_has_digit', () => {
    expect(mutate((d) => { d.experiences[0].summary = '你数了 3 遍。' })).toContain('text_has_digit')
  })

  test('写入未登记取值 → value_not_in_vocab', () => {
    expect(mutate((d) => { d.experiences[0].agency = '有点被动' })).toContain('value_not_in_vocab')
  })

  test('净值不再是 +2 → effects_net', () => {
    expect(mutate((d) => { d.experiences[0].effects.attributes.will = 2 })).toContain('effects_net')
  })

  test('把上限调到锁死偏科（5×2=10）→ quota_forces_full_domains', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.quota.per_value_max = 2
    const { warnings } = validate(clone)
    expect(warnings.map((w) => w.code)).toContain('quota_forces_full_domains')
  })

  test('词表出现通配取值 → vocab_wildcard_forbidden', () => {
    expect(
      mutate((d) => { d.vocab.onset.values.push({ id: 'unknown', label: '未知' }) }),
    ).toContain('vocab_wildcard_forbidden')
  })

  test('facet 没有 ask → facet_without_ask', () => {
    expect(mutate((d) => { d.vocab.onset.ask = '' })).toContain('facet_without_ask')
  })

  test('配置块丢掉 source → config_without_source', () => {
    expect(mutate((d) => { delete d.quota.source })).toContain('config_without_source')
  })

  test('非法组合被命中 → forbidden_combo', () => {
    expect(
      mutate((d) => {
        d.experiences.find((r) => r.context === 'school').relation = ['partner']
      }),
    ).toContain('forbidden_combo')
  })

  test('id 复用墓碑 → id_reused', () => {
    expect(mutate((d) => { d.tombstones = ['exp_0001'] })).toContain('id_reused')
  })
})

/**
 * 病历外壳（design/presentation/开局病历填报.md §四 · §十一）。
 * 它只是开局五屏的文书栏，不改任何机制——所以要守住的是三件事：
 * ① 栏目名与笔迹写法必须写全（缺一条界面就会露出半张空表）；
 * ② **栏位落笔表**：每一笔都带 who / fill / blank，且院方那一半永远不由玩家写；
 * ③ 它和 interview.screen 同一套文案纪律：内部实现词一个都不许出现（含嵌套）。
 */
describe('病历单：栏目 · 每一笔的落笔方 · 空栏', () => {
  const mutate = (fn) => {
    const clone = JSON.parse(JSON.stringify(db))
    fn(clone)
    return validate(clone).errors.map((e) => e.code)
  }
  const PAPER = db.record_shell.paper
  const WRITES = PAPER.columns.flatMap((c) => (c.writes ?? []).map((w) => ({ column: c.id, ...w })))

  test('纸上的栏目按法定顺序排全：一栏不少，顺序不变', () => {
    expect(PAPER.columns.map((c) => c.id)).toEqual(PAPER.required)
    // 每一栏都答得出「它在入院记录里是哪一个法定项目」。
    for (const col of PAPER.columns) {
      expect(col.label, col.id).toBeTruthy()
      expect(col.basis, col.id).toBeTruthy()
    }
    // 一般情况那一栏的九笔仍写在 general 里，不在纸上另抄一份。
    expect(PAPER.columns.find((c) => c.id === 'general').writes_ref).toBe('general')
    expect(db.record_shell.general).toHaveLength(9)
  })

  test('每一笔都答得出「谁落笔 / 谁可改 / 空白时显示什么 / 取值从哪来」', () => {
    const inks = Object.keys(db.record_shell.ink)
    const fills = Object.keys(db.record_shell.fill)
    for (const w of WRITES) {
      expect(w.label, JSON.stringify(w)).toBeTruthy()
      expect(inks, w.label).toContain(w.who)
      expect(fills, w.label).toContain(w.fill)
      expect(w.blank !== undefined || w.blank_from !== undefined, w.label).toBe(true)
      // 来源要么是问诊的一问，要么是 write_sources 里登记过的那一个。
      expect(w.from.startsWith('q_') || Object.keys(PAPER.write_sources).includes(w.from), w.label).toBe(true)
    }
  })

  test('可填的笔必有闭集：要么是问诊的一问，要么是登记过闭集的来源', () => {
    const writable = WRITES.filter((w) => w.fill === 'patient_input')
    expect(writable.length).toBeGreaterThan(0)
    for (const w of writable) {
      const isQuestion = w.from.startsWith('q_')
      expect(isQuestion || PAPER.write_sources[w.from], w.label).toBeTruthy()
      if (!isQuestion) expect(PAPER.write_sources[w.from].closed, w.label).toBe(true)
    }
    // 院方那一笔永远不由玩家落笔。
    for (const w of WRITES.filter((x) => x.who === 'hospital')) expect(w.fill).toBe('system')
  })

  test('页眉每一笔都答得出「谁落笔 / 谁可改 / 空白时显示什么」', () => {
    const fills = Object.keys(db.record_shell.fill)
    for (const row of db.record_shell.general) {
      expect(row.label, JSON.stringify(row)).toBeTruthy()
      expect(fills, row.label).toContain(row.fill)
      expect(row.blank, row.label).toBeTruthy()
      expect(row.value === undefined && row.value_from_source === undefined, row.label).toBe(false)
    }
  })

  test('问诊的问法与按钮文案不在病历单里复制第二份', () => {
    // 唯一副本在 interview；纸上只有栏目名，`from` 只指向那一问的 id。
    // 只看**上屏文案**（上屏的那几个键），依据表（source / ask / basis）不算副本。
    const onScreen = collectStrings(db.record_shell.paper, '', { keys: false })
      .filter(({ path }) => !META_COPY_PATHS.some((re) => re.test(path)))
      .map(({ text }) => text)
      .join('\n')
    for (const q of db.interview.questions) expect(onScreen, q.id).not.toContain(q.ask)
    expect(onScreen).not.toContain(db.interview.screen.pool_confirm)
    expect(onScreen).not.toContain(db.interview.screen.pool_note)
    expect(onScreen).not.toContain(db.interview.answer_note)
    // 主诉的空栏文案也不在纸上抄第二份：它读 complaint.empty。
    expect(onScreen).not.toContain(db.complaint.empty)
  })

  test('反例：丢掉病历单 → record_shell_block_missing', () => {
    expect(mutate((d) => { delete d.record_shell.paper })).toContain('record_shell_block_missing')
  })

  test('反例：少一栏法定栏目 → paper_column_missing', () => {
    expect(mutate((d) => {
      d.record_shell.paper.columns = d.record_shell.paper.columns.filter((c) => c.id !== 'family')
    })).toContain('paper_column_missing')
  })

  test('反例：某一笔没写来源 / 没写空白态', () => {
    expect(mutate((d) => { delete d.record_shell.paper.columns[2].writes[0].from }))
      .toContain('paper_write_incomplete')
    expect(mutate((d) => { delete d.record_shell.paper.columns[2].writes[0].blank }))
      .toContain('paper_write_without_blank')
  })

  test('反例：把一笔标成可填、来源却没有闭集 → paper_write_without_closed_set', () => {
    expect(mutate((d) => {
      d.record_shell.paper.columns[5].writes[0].fill = 'patient_input'
    })).toContain('paper_write_without_closed_set')
  })

  test('反例：院方那一笔挂在可写的落笔上 → record_shell_hospital_side_writable', () => {
    expect(mutate((d) => {
      d.record_shell.paper.columns[2].writes[0].who = 'hospital'
      d.record_shell.paper.columns[2].writes[0].fill = 'patient_input'
    })).toContain('record_shell_hospital_side_writable')
  })

  test('反例：问诊的一问写到了一个没有栏目接着的地方 → paper_write_unknown_source', () => {
    expect(mutate((d) => { d.record_shell.paper.columns[2].writes[0].from = 'q_nope' }))
      .toContain('paper_write_unknown_source')
  })

  test('反例：一般情况少写一笔 → record_shell_row_incomplete', () => {
    expect(mutate((d) => {
      delete d.record_shell.general[0].value
      delete d.record_shell.general[0].value_from_source
    })).toContain('record_shell_row_incomplete')
  })

  test('反例：笔迹标注用了没登记的值 → record_shell_ink_unknown', () => {
    const codes = mutate((d) => { d.record_shell.general[0].who = '机器' })
    expect(codes).toContain('record_shell_ink_unknown')
    expect(codes).toContain('record_shell_row_by_unknown')
  })

  test('反例：落款栏缺一项 → record_shell_sign_missing', () => {
    expect(mutate((d) => { delete d.record_shell.sign.historian })).toContain('record_shell_sign_missing')
  })

  test('反例：把内部实现词写进病历文案 → record_shell_copy_leaks_internal', () => {
    expect(mutate((d) => { d.record_shell.paper.columns[1].label = '主诉与输出槽' }))
      .toContain('record_shell_copy_leaks_internal')
  })

  test('反例：把内部实现词藏进嵌套一层 → record_shell_copy_leaks_internal', () => {
    expect(mutate((d) => { d.record_shell.paper.columns[4].writes[2].note = '这一栏由输出槽决定' }))
      .toContain('record_shell_copy_leaks_internal')
  })

  test('反例：某一笔没写「谁能改」/ 没写空白态', () => {
    expect(mutate((d) => { delete d.record_shell.general[1].fill })).toContain('record_shell_row_fill_unknown')
    expect(mutate((d) => { delete d.record_shell.general[1].blank })).toContain('record_shell_row_without_blank')
  })

  test('反例：院方那一半被写成从某个来源现算 → record_shell_hospital_side_from_source', () => {
    // 这是自建人物不打穿《无法离开医院》②「身份黏着」的那条判据：
    // 院方的名字只能是写好的字面值，不能来自任何玩家能改的东西。
    expect(
      mutate((d) => { d.record_shell.general[0].value_to_source = 'name' }),
    ).toContain('record_shell_hospital_side_from_source')
  })

  test('反例：院方那一半挂着可写的落笔 / 患者笔迹', () => {
    expect(
      mutate((d) => { d.record_shell.general[0].fill = 'patient_input' }),
    ).toContain('record_shell_hospital_side_writable')
    expect(
      mutate((d) => { d.record_shell.general[0].who = 'patient' }),
    ).toContain('record_shell_hospital_side_not_hospital')
  })
})
