import { afterEach, describe, expect, test } from 'bun:test'
import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import { interviewPool, interviewQuestions, validate } from './opening.js'
import {
  allComplaints,
  characterFieldOf,
  characterFor,
  characterOptions,
  characterSources,
  characterUi,
  complaintText,
  isKnownSource,
  composeName,
  defaultSourceId,
  fillOf,
  hospitalIdentity,
  lockedRows,
  namePool,
  recordRows,
  validateComplaint,
  writableFields,
  writableRows,
} from './character-source.js'

/**
 * 开局病历：**栏位落笔表 · 人物来源 · 主诉** 的契约。
 *
 * 这里守的是三件不许被"看起来没问题"蒙过去的事：
 *   ① 玩家能落哪几笔是**数据算出来的**，不是界面自觉（没有自由文本输入）；
 *   ② 院方记录栏**永不由玩家写** —— 自建人物也会拿到一个与自述不同的院方记录，
 *      《无法离开医院》②「身份黏着」的四个症状因此对两条入口都成立；
 *   ③ 主诉是从词表拼出来的，字数 / 禁数字 / 禁内部词都可算。
 *
 * 依据：design/presentation/开局病历填报.md §十一 · §十二；
 *      design/entities/疾病特长.md §4.6.2 / §4.6.4。
 * 文案断言一律对着 `data/` 比，不在测试里手抄第二份。
 */

const CANONICAL = { source: defaultSourceId(db) }
const CUSTOM = { source: 'custom', name: '陈宁', gender: 'male' }

describe('栏位落笔表：谁落笔、谁可改、空白时显示什么', () => {
  test('页眉 9 笔，其中玩家可落的恰好 2 笔（姓名 · 性别）', () => {
    expect(db.record_shell.general).toHaveLength(9)
    expect(writableRows(db).map((r) => r.label)).toEqual(['姓名', '性别'])
    expect(lockedRows(db)).toHaveLength(7)
    // 两半分开写的行只有姓名一行（患者自述 vs 院方记录）。
    expect(recordRows(db, CANONICAL).filter((r) => r.composite).map((r) => r.label)).toEqual(['姓名'])
  })

  test('每一笔都读得出 who / fill / blank，且 fill 只在登记的两个值里', () => {
    const fills = Object.keys(db.record_shell.fill)
    expect(fills.sort()).toEqual(['patient_input', 'system'])
    for (const row of db.record_shell.general) {
      expect(row.who, row.label).toBeTruthy()
      expect(fills, row.label).toContain(fillOf(db, row))
      expect(row.blank, row.label).toBeTruthy()
    }
  })

  test('「玩家可填几笔」是算出来的：character.fields 的 patient_input 与页眉一一对上', () => {
    expect(writableFields(db).map((f) => f.key)).toEqual(['name', 'gender'])
    const rowOf = (label) => db.record_shell.general.find((r) => r.label === label)
    for (const f of writableFields(db)) {
      // 每一笔可落笔都指向页眉上的一行，且两侧说的来源是同一个。
      expect(rowOf(f.row), f.key).toBeTruthy()
      expect(rowOf(f.row).value_from_source, f.key).toBe(f.value_source)
      expect(characterFieldOf(db, rowOf(f.row)), f.key).toBe(f)
    }
    // 反向：页眉上能落的每一笔都有一张 fields 登记（否则界面会不知道自己能落什么）。
    for (const row of writableRows(db)) expect(characterFieldOf(db, row), row.label).toBeTruthy()
  })

  test('院方那一半永远是字面值：玩家改不了它', () => {
    const name = db.record_shell.general.find((r) => r.label === '姓名')
    expect(name.who).toBe('hospital')
    expect(name.fill).toBe('system')          // 这一行整体不是玩家可改的
    expect(name.value_to).toBe(hospitalIdentity(db).hospital_name)
    expect(name.value_to_source).toBeUndefined()
    // 正典与自建两条入口下，院方那一半都是同一个值——这就是身份黏着的那一半。
    for (const who of [CANONICAL, CUSTOM]) {
      const row = recordRows(db, characterFor(db, who))[0]
      expect(row.lockedTo.text).toBe(hospitalIdentity(db).hospital_name)
      expect(row.who).toBe('hospital')
    }
  })

  test('自建人物拿到的是「自己报的姓名」+「院方写的另一个名字」', () => {
    const rows = recordRows(db, characterFor(db, CUSTOM))
    expect(rows[0].from.text).toBe('陈宁')
    expect(rows[0].lockedTo.text).toBe('苟笙')
    expect(rows[0].from.text).not.toBe(rows[0].lockedTo.text)
    // 性别也落在页眉上，且它读的是数据里的标签而不是 id。
    expect(rows.find((r) => r.label === '性别').text).toBe('男')
  })

  test('姓名两段都选完才算报上；只选一半回落到正典字面值 / 空白态', () => {
    expect(composeName(db, { surname: '陈', given: '宁' })).toBe('陈宁')
    expect(composeName(db, { surname: '陈', given: '不存在' })).toBeNull()
    expect(composeName(db, { surname: '不存在', given: '宁' })).toBeNull()

    const half = recordRows(db, characterFor(db, { source: 'custom', name: '陈' }))
    expect(half[0].from.text).toBe(db.record_shell.general[0].blank)
    expect(half[0].lockedTo.text).toBe('苟笙')
  })

  test('自建人物的闭集：姓 × 名可拼出的姓名数，且没有重复', () => {
    const pool = namePool(db)
    const pairs = pool.surname.values.length * pool.given.values.length
    expect(pairs).toBeGreaterThanOrEqual(100)
    for (const part of [pool.surname, pool.given]) {
      expect(part.values.length).toBeGreaterThan(5)
      expect(new Set(part.values).size).toBe(part.values.length)
    }
    // 界面照 characterOptions 渲染，不自己写取值。
    const opts = characterOptions(db)
    expect(opts.name.surname.values).toEqual(pool.surname.values)
    expect(opts.gender.values.map((v) => v.label)).toEqual(['男', '女'])
  })

  test('院方书写栏在实现上也拿不到写入口：唯一能写的入口只认患者侧那两笔', () => {
    // 界面把玩家选择喂回 `characterFor` 的就只有 source / name / gender 三个键，
    // 它们分别落在院方侧之外：姓名只覆盖「自述」那一半，性别只覆盖性别那一笔。
    const hostile = characterFor(db, {
      source: 'custom',
      name: '陈宁',
      gender: 'male',
      姓名: '苟笙', hospital: '苟笙', number: '9999', bed: '任意床位',
    })
    expect(Object.keys(hostile).sort()).toEqual(['gender', 'name', 'source'])
    // 就算硬塞字段名一样的键，院方那一半也不动。
    const rows = recordRows(db, hostile)
    for (const label of ['住院号', '床位', '科别']) {
      const row = rows.find((r) => r.label === label)
      expect(row.text).toBe(db.record_shell.general.find((r) => r.label === label).value)
      expect(row.writable, label).toBe(false)
    }
    expect(rows[0].lockedTo.text).toBe(db.character_source.identity.hospital_name)
  })

  test('病史陈述者这一笔是患者侧，但它不是玩家可改的（他说的是别人记下的话）', () => {
    const row = db.record_shell.general.find((r) => r.label === '病史陈述者')
    expect(row.who).toBe('patient')
    expect(fillOf(db, row)).toBe('system')
  })

  test('年龄不引入玩家自填件：它读的是已认下的起病时间，不是数字', () => {
    const row = db.record_shell.general.find((r) => r.label === '年龄')
    expect(fillOf(db, row)).toBe('system')
    expect(row.value_from_source).toBe('onset')
    // 没答题时空着，答题后只写词表里那个粗档的标签。
    expect(recordRows(db, characterFor(db, CANONICAL), {})[4].resolved).toBe(false)
    expect(recordRows(db, characterFor(db, CANONICAL), { onset: 'childhood' })[4].text).toBe('童年')
    for (const band of db.vocab.onset.values) {
      expect(recordRows(db, characterFor(db, CANONICAL), { onset: band.id })[4].text).toBe(band.label)
    }
  })
})

describe('人物来源：两条入口共用同一套流程', () => {
  test('登记表里有正典与自建两条，默认是正典', () => {
    // 可当 source 用的键只有 `characters` 里那两个；界面文案在 `ui` 里，
    // 与来源键分表存放——这样「这个字符串是不是一条人物来源」不需要靠名单判断。
    expect(Object.keys(characterSources(db)).sort()).toEqual(['canonical', 'custom'])
    expect(defaultSourceId(db)).toBe('canonical')
    expect(isKnownSource(db, 'canonical')).toBe(true)
    expect(isKnownSource(db, 'custom')).toBe(true)
    expect(isKnownSource(db, 'label')).toBe(false)
    expect(isKnownSource(db, '不存在的来源')).toBe(false)
    expect(characterFor(db, CANONICAL).source).toBe('canonical')
    expect(characterFor(db, CUSTOM).source).toBe('custom')
    // 界面文案各有其位。
    const ui = characterUi(db)
    for (const k of ['label', 'note', 'custom_name', 'gender', 'name', 'unfilled']) {
      expect(ui[k], k).toBeTruthy()
    }
  })

  test('换人物不改任何一笔「谁的笔迹」：页眉的 who/fill 与人物来源无关', () => {
    const a = recordRows(db, characterFor(db, CANONICAL))
    const b = recordRows(db, characterFor(db, CUSTOM))
    expect(a.map((r) => [r.label, r.who, r.fill])).toEqual(b.map((r) => [r.label, r.who, r.fill]))
  })

  test('人物来源不参与锚点 / 配额 / 疾病候选：三样东西都不认识它', () => {
    // 问诊问的七个记录 facet + 患者自述的那一个答案轴里，没有一个是人物来源的字段；
    // 配额轴仍是 context。
    expect(interviewQuestions(db).map((q) => q.facet))
      .toEqual(['self_report', 'event', 'context', 'relation', 'agency',
        'onset', 'duration_pattern', 'duration_span'])
    expect(db.quota.per_facet).toBe('context')
    // character_vocab 与 vocab 的边界：除了三处**只读引用**（起病时间 / 病程形式 /
    // 姓名：它们只是指向词表已有取值，不引入新取值），key 一个都不许与 facet 同名。
    const derived = ['onset', 'duration_pattern', 'name_field']
    for (const key of Object.keys(db.character_vocab)) {
      if (key === 'ask') continue
      if (derived.includes(key)) {
        expect(db.character_vocab[key].values, key).toEqual([])
        continue
      }
      // 自建人物专有的那一条（没有任何理由说它不该对玩家开放，除非取值闭集不存在）。
      if (key === 'gender') continue
      expect(db.character_vocab[key].open_to_player, key).not.toBe(true)
      expect(Object.keys(db.vocab), key).not.toContain(key)
    }
    // 反向：vocab 的每个 facet 都不许被 character_vocab 声明成自己的取值来源——
    // 除了那三处「只读引用」（它们要求被引用的一方自己持有取值，不允许在这里新建）。
    const refs = ['onset', 'duration_pattern', 'name_field']
    for (const facet of Object.keys(db.vocab)) {
      if (refs.includes(facet)) continue
      expect(Object.keys(db.character_vocab), facet).not.toContain(facet)
    }
    // 只读引用的三条必须写明「取值仍归 vocab 管」。
    for (const key of refs) {
      expect(db.character_vocab[key].values, key).toEqual([])
      const src = db.character_vocab[key].source
      expect(src.includes('vocab.') || src.includes('name_pool'), key).toBe(true)
    }
    // 经历记录里一个字符也不该提到人物来源。
    for (const r of db.experiences.slice(0, 20)) {
      expect(Object.keys(r)).not.toContain('source')
      expect(Object.keys(r)).not.toContain('character')
    }
  })

  test('自建人物不打穿身份黏着：两半仍然不同，四个症状的物证还在', () => {
    const id = hospitalIdentity(db)
    expect(id.hospital_name).toBe('苟笙')
    expect(id.hospital_number).toBe('0527')
    const rows = recordRows(db, characterFor(db, CUSTOM))
    const number = rows.find((r) => r.label === '住院号')
    // 编号是院方的另一笔，玩家没有对应的可落行。
    expect(number.fill).toBe('system')
    expect(characterFieldOf(db, number)).toBeNull()
  })
})

describe('主诉：三个答案落成一行字', () => {
  test('每一条可能的主诉（自述 × 起病时间 × 病程形式）都拼得出来', () => {
    const n = db.complaint.self_report.values.length
    expect(allComplaints(db)).toHaveLength(n * 9)
    for (const c of allComplaints(db)) expect(c.text).toBeTruthy()
    // 拼句只借数据里的标签：改词表，主诉跟着改，不存在第二份文案。
    const [symptom] = db.complaint.self_report.values
    expect(complaintText(db, { self_report: symptom.id, onset: 'childhood', duration_pattern: 'continuous' }))
      .toBe(`${symptom.label}${db.complaint.self_report.join}`
        + `${db.complaint.onset.childhood}${db.complaint.duration_pattern.continuous}`)
  })

  test('主诉的字数 / 禁数字 / 禁内部词可算，且零错误', () => {
    const { errors } = validateComplaint(db)
    expect(errors).toEqual([])
    for (const { text } of allComplaints(db)) {
      expect([...text].length).toBeLessThanOrEqual(db.complaint.max_chars)
      expect(text).not.toMatch(/[0-9０-９]/)
    }
  })

  test('三个答案没答完时主诉栏是空的，不拼半句', () => {
    // 患者先自述，院方再补起病时间与病程形式——三样缺一，主诉那一行就写不出来。
    expect(complaintText(db, {})).toBeNull()
    expect(complaintText(db, { self_report: 'cannot_sleep' })).toBeNull()
    expect(complaintText(db, { onset: 'childhood', duration_pattern: 'single' })).toBeNull()
    expect(complaintText(db, { self_report: 'cannot_sleep', onset: 'childhood' })).toBeNull()
    expect(complaintText(db, { self_report: 'cannot_sleep', duration_pattern: 'single' })).toBeNull()
    expect(complaintText(db, { self_report: 'cannot_sleep', onset: 'childhood', duration_pattern: 'single' }))
      .toBeTruthy()
  })

  test('反例：自述表被抽空 / 自述那一问没指到它 → 主诉契约报错', () => {
    const empty = JSON.parse(JSON.stringify(db))
    empty.complaint.self_report.values = []
    const codes = validateComplaint(empty).errors.map((e) => e.code)
    expect(codes).toContain('complaint_self_report_empty')
    // 反例：自述表在，但没有任何一问指到它——那是没有出口的第二份词表。
    const unasked = JSON.parse(JSON.stringify(db))
    unasked.interview.questions[0].answer_from = 'vocab'
    unasked.interview.questions[0].facet = 'onset'
    expect(validateComplaint(unasked).errors.map((e) => e.code))
      .toContain('complaint_self_report_unasked')
  })

  test('反例：主诉的起病缓急少一档 → complaint_values_mismatch', () => {
    const clone = JSON.parse(JSON.stringify(db))
    delete clone.complaint.onset.adulthood
    expect(validateComplaint(clone).errors.map((e) => e.code)).toContain('complaint_values_mismatch')
  })

  test('反例：拼句表与词表对不上，validate 也要报 → complaint_values_mismatch', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.complaint.duration_pattern.rare = '偶发'
    expect(validate(clone).errors.map((e) => e.code)).toContain('complaint_values_mismatch')
  })

  test('反例：词表里那一档在拼句表里没有写法 → complaint_unresolvable', () => {
    const clone = JSON.parse(JSON.stringify(db))
    // 把词表多留一档而拼句表不给它——这一路主诉会拼不出来，是内容缺口不是形状错误，
    // 所以它必须报出来。（同时也会报 values_mismatch：两件事都要说。）
    clone.vocab.onset.values.push({ id: 'infancy', label: '婴儿期' })
    const codes = validateComplaint(clone).errors.map((e) => e.code)
    expect(codes).toContain('complaint_unresolvable')
    expect(codes).toContain('complaint_values_mismatch')
  })

  test('反例：把字数上限压到 3 → complaint_too_long', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.complaint.max_chars = 3
    expect(validateComplaint(clone).errors.map((e) => e.code)).toContain('complaint_too_long')
  })

  test('反例：主诉文案里塞进数字 → complaint_has_digit', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.complaint.duration_pattern.continuous = '持续 3 个月'
    expect(validateComplaint(clone).errors.map((e) => e.code)).toContain('complaint_has_digit')
  })
})

describe('反例：栏位落笔表坏了必须报出来', () => {
  const mutate = (fn) => {
    const clone = JSON.parse(JSON.stringify(db))
    fn(clone)
    return validate(clone).errors.map((e) => e.code)
  }

  test('反例：自建人物多了一个没有闭集的栏目 → character_field_without_closed_set', () => {
    // 自由文本的入口在数据层就堵死：可落的笔必须有取值闭集，
    // 给不出闭集的栏目（职业 / 婚姻 / 出生地）只能留在 system。
    expect(mutate((d) => {
      const f = d.record_shell.character.fields.find((x) => x.key === 'occupation')
      f.fill = 'patient_input'
      f.value_source = 'occupation'
    })).toContain('character_field_without_closed_set')
  })

  test('反例：character_vocab 里挂上一条没人引用的词表 → character_vocab_unreferenced', () => {
    expect(mutate((d) => {
      d.character_vocab.zodiac = { label: '属相', values: [{ id: 'rat', label: '鼠' }] }
    })).toContain('character_vocab_unreferenced')
  })

  test('反例：可落的笔与页眉那一行的来源对不上 → character_field_row_mismatch', () => {
    expect(mutate((d) => {
      d.record_shell.general[5].value_from_source = 'onset'
    })).toContain('character_field_row_mismatch')
  })

  test('反例：可落的笔在页眉上没有对应行 → character_field_without_row', () => {
    expect(mutate((d) => {
      d.record_shell.character.fields.find((x) => x.key === 'gender').row = '不存在的行'
    })).toContain('character_field_without_row')
  })

  test('反例：把已开放给玩家的栏目在词表里关掉 → character_field_axis_closed', () => {
    expect(mutate((d) => { d.character_vocab.gender.open_to_player = false })).toContain('character_field_axis_closed')
  })

  test('反例：落款侧缺一个新栏目 → character_field_incomplete', () => {
    expect(mutate((d) => { delete d.record_shell.character.fields[1].label })).toContain('character_field_incomplete')
  })

  /**
   * 🔧 2026-09-27 补的四条：这三处是阶段 2 交付时**反例实测漏网**的地方——
   * 删掉院方那一半、把院方名字改成池内可拼的名字、给一笔 patient_input 却不给闭集，
   * 当时都不报错。身份黏着是自建人物唯一的 canon 风险点，必须有机核判据。
   */
  test('反例：把院方那一半整笔删掉 → record_shell_hospital_side_absent', () => {
    expect(mutate((d) => {
      delete d.record_shell.general.find((r) => r.label === '姓名').value_to
    })).toContain('record_shell_hospital_side_absent')
  })

  test('反例：姓名池能拼出院方记录的那个名字 → character_name_hits_hospital_identity', () => {
    expect(mutate((d) => {
      d.character_source.name_pool.surname.values.push('苟')
      d.character_source.name_pool.given.values.push('笙')
    })).toContain('character_name_hits_hospital_identity')
  })

  test('反例：院方名字被改成池子里拼得出来的名字 → character_name_hits_hospital_identity', () => {
    expect(mutate((d) => { d.character_source.identity.hospital_name = '陈宁' }))
      .toContain('character_name_hits_hospital_identity')
  })

  test('反例：一笔标成玩家可填却没有闭集 → record_shell_row_without_closed_set', () => {
    expect(mutate((d) => {
      d.record_shell.general.push({ label: '职业', who: 'patient', fill: 'patient_input', value: '', blank: '待填' })
    })).toContain('record_shell_row_without_closed_set')
  })

  test('正例：现有姓名池与院方名字不相交（身份黏着的结构保证）', () => {
    const pool = db.character_source.name_pool
    const reachable = new Set()
    for (const s of pool.surname.values) for (const g of pool.given.values) reachable.add(`${s}${g}`)
    expect(reachable.size).toBe(pool.surname.values.length * pool.given.values.length)
    // 「自述 ≠ 院方记录」不是文案承诺，是可算的结构事实：池子里没有院方那个名字。
    expect(reachable.has(db.character_source.identity.hospital_name)).toBe(false)
    expect(validate(db).errors).toEqual([])
  })

  test('反例：主诉里用诊断名代替症状 → complaint_names_diagnosis', () => {
    const cloneDdb = JSON.parse(JSON.stringify(ddb))
    const clone = JSON.parse(JSON.stringify(db))
    clone.complaint.empty = `${cloneDdb.items[0].label}？`
    expect(validateComplaint(clone, cloneDdb).errors.map((e) => e.code)).toContain('complaint_names_diagnosis')
    // 不传 ddb 时不报——这条判据依赖疾病契约，缺了它就不装作查过。
    expect(validateComplaint(clone).errors.map((e) => e.code)).not.toContain('complaint_names_diagnosis')
  })
})

/**
 * 端到端：自建人物这条入口在界面上真走得通，而且**没有输入框**。
 * DOM 桩与 `flow.test.js` 同一套写法（只实现 index.js 真正用到的那几个接口）。
 */
function makeElement() {
  const el = {
    className: '', innerHTML: '', hidden: false, children: [], listeners: {},
    append(child) { el.children.push(child) },
    addEventListener(type, fn) { (el.listeners[type] ||= []).push(fn) },
    querySelector() { return null },
    focus() {},
  }
  return el
}

function mountDocument() {
  const shell = makeElement()
  const root = makeElement()
  root.querySelector = () => shell
  globalThis.document = {
    createElement: () => root,
    body: { append() {} },
    documentElement: { classList: { add() {}, remove() {} } },
    addEventListener() {},
  }
  return { root, shell }
}

const click = (root, dataset) => {
  const attrs = Object.keys(dataset).map(
    (key) => `[data-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}]`,
  )
  const target = { closest: (selector) => (attrs.includes(selector) ? { dataset } : null) }
  for (const fn of root.listeners.click ?? []) fn({ target })
}

describe('自建人物：界面上的那条入口', () => {
  const originalDocument = globalThis.document
  afterEach(() => { globalThis.document = originalDocument })

  test('页眉上换人物、报姓名、选性别；院方那一半不动，profile 带上来源', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    // 开局默认是正典人物：页眉上并排写着自述名与院方名。
    expect(shell.innerHTML).toContain('苟智空')
    expect(shell.innerHTML).toContain(hospitalIdentity(db).hospital_name)
    expect(cc.getProfile().source).toBe('canonical')

    // 换成自建人物，两个闭集选择件出现（姓名与性别各一排候选字）。
    click(root, { characterSource: 'custom' })
    const pool = namePool(db)
    for (const s of pool.surname.values.slice(0, 3)) {
      expect(shell.innerHTML).toContain(`data-character-field="surname" data-value="${s}"`)
    }
    for (const g of pool.given.values.slice(0, 3)) {
      expect(shell.innerHTML).toContain(`data-character-field="given" data-value="${g}"`)
    }

    // 只选姓不算报上：还没有名字。
    click(root, { characterField: 'surname', value: '陈' })
    expect(shell.innerHTML).not.toContain('陈宁')
    click(root, { characterField: 'given', value: '宁' })
    click(root, { characterField: 'gender', value: 'male' })

    // 两段选完之后页眉上写着「陈宁」与院方那个「苟笙」——两半仍然不同。
    expect(shell.innerHTML).toContain('陈宁')
    expect(shell.innerHTML).toContain(hospitalIdentity(db).hospital_name)
    expect(shell.innerHTML).toContain('男')
    const profile = cc.getProfile()
    expect(profile.source).toBe('custom')
    expect(profile.name).toBe('陈宁')
    expect(profile.gender).toBe('male')

    // 界面里没有任何自由文本入口。
    expect(shell.innerHTML).not.toContain('<input')
    expect(shell.innerHTML).not.toContain('<textarea')
    expect(shell.innerHTML).not.toContain('contenteditable')
  })

  test('换人物不清空已答的八问与已核对过的十段：人物来源不是机制', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    const answers = { self_report: 'cannot_sleep',
      event: ['threat'], context: 'work', relation: ['authority'], agency: 'coerced',
      onset: 'adulthood', duration_pattern: 'continuous', duration_span: 'long' }
    for (const q of interviewQuestions(db)) {
      const value = answers[q.facet]
      for (const v of [].concat(value)) click(root, { answerFacet: q.facet, answerValue: v })
    }
    const poolIds = interviewPool(db, ddb, answers).ids
    for (const id of poolIds.slice(0, db.quota.total)) click(root, { entry: id })
    expect(cc.getProfile().experiences).toHaveLength(db.quota.total)

    // 换成自建人物：十段一条不少（人物来源不参与问诊 / 池子）。
    click(root, { characterSource: 'custom' })
    click(root, { characterField: 'surname', value: '林' })
    click(root, { characterField: 'given', value: '安' })
    expect(cc.getProfile().experiences).toEqual(poolIds.slice(0, db.quota.total))
    // 主诉也照旧：它读的是已答下的自述、起病时间与病程形式，不读姓名。
    expect(shell.innerHTML).toContain(complaintText(db, answers))
  })

  test('患者先自述，主诉栏那一行才写得出来', async () => {
    const { root, shell } = mountDocument()
    const { createCharacterCreation } = await import('./index.js')
    const cc = createCharacterCreation({ trigger: null, required: true })
    cc.open()

    // 一句都没答：主诉栏空着，但第 1 问就是自述。
    expect(shell.innerHTML).toContain(db.complaint.empty)
    expect(shell.innerHTML).toContain(interviewQuestions(db)[0].ask)
    // 自述答完，纸上先写下患者自己的那一句；主诉那一行还缺起病时间与病程形式。
    const [symptom] = db.complaint.self_report.values
    click(root, { answerFacet: 'self_report', answerValue: symptom.id })
    expect(shell.innerHTML).toContain(symptom.label)
    expect(shell.innerHTML).toContain(db.complaint.empty)
    // 院方再补时间：主诉那一行才落成一句完整的法定写法。
    click(root, { answerFacet: 'onset', answerValue: 'childhood' })
    click(root, { answerFacet: 'duration_pattern', answerValue: 'intermittent' })
    expect(shell.innerHTML)
      .toContain(complaintText(db, { self_report: symptom.id, onset: 'childhood', duration_pattern: 'intermittent' }))
  })
})
