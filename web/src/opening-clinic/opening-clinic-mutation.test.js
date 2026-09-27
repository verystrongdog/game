/**
 * 开局门诊病历 · **反例形变测试**。
 *
 * 做法照搬仓库里的既有先例（`opening.test.js` 的「反例：…必须报出来」）：
 * 把一份**深拷贝**的数据故意弄坏，看校验器认不认得出、报的是不是那一条码。
 * 用意是：将来有人往 `data/opening_clinic.json` 里加东西时，这些判据还活着。
 */
import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening_clinic.json' with { type: 'json' }
import ddb from '../../../data/diseases.json' with { type: 'json' }
import { validateClinic } from './opening-clinic.js'

const clone = () => JSON.parse(JSON.stringify(db))
const codesOf = (broken) => validateClinic(broken, { diseases: ddb }).errors.map((e) => e.code)
const questionOf = (broken, id) => broken.questions.find((q) => q.id === id)

describe('反例：数据坏了必须报出来', () => {
  test('正例：未改动的那一份 0 错', () => {
    expect(codesOf(clone())).toEqual([])
  })

  test('反例：抽掉参照里的一问 → reference_question_missing', () => {
    const broken = clone()
    broken.questions = broken.questions.filter((q) => q.ref !== 41)
    expect(codesOf(broken)).toContain('reference_question_missing')
  })

  test('反例：某一问的闭集被删到只剩一档 → closed_set_too_small', () => {
    const broken = clone()
    broken.answers.duration.values = [broken.answers.duration.values[0]]
    expect(codesOf(broken)).toContain('closed_set_too_small')
  })

  test('反例：某一问的闭集被抽掉 → question_without_closed_set', () => {
    const broken = clone()
    delete broken.answers.probes
    broken.answers.probes = undefined
    broken.questions.find((q) => q.id === 'q036').answers = '不存在的闭集'
    expect(codesOf(broken)).toContain('question_without_closed_set')
  })

  test('反例：把「不愿说」整档拿掉 → refuse_missing', () => {
    const broken = clone()
    delete broken.refuse.record
    expect(codesOf(broken)).toContain('refuse_missing')
  })

  test('反例：敏感问题没有内容提示语 → sensitive_without_content_note', () => {
    const broken = clone()
    delete broken.sensitivity_levels.self_harm.content_note
    expect(codesOf(broken)).toContain('sensitive_without_content_note')
  })

  test('反例：敏感标记不在词表里 → sensitivity_unknown', () => {
    const broken = clone()
    questionOf(broken, 'q046').sensitive = '随便编的级别'
    expect(codesOf(broken)).toContain('sensitivity_unknown')
  })

  test('反例：答案里藏了一个病名 → answer_names_diagnosis', () => {
    const broken = clone()
    const name = ddb.items[0].label
    broken.answers.mood_two_weeks.values[0].label = name
    expect(codesOf(broken)).toContain('answer_names_diagnosis')
  })

  test('反例：主诉里用诊断名代替症状 → chief_complaint_names_diagnosis', () => {
    const broken = clone()
    broken.answers.chief_complaints.values[0].label = ddb.items[0].label
    broken.answers.chief_complaints.values[0].record = ddb.items[0].label
    expect(codesOf(broken)).toContain('chief_complaint_names_diagnosis')
  })

  test('反例：主诉超过 20 字 → chief_complaint_too_long', () => {
    const broken = clone()
    broken.answers.chief_complaints.values[0].label = '一段故意写得很长很长的主诉症状描述文字'
    broken.answers.chief_complaints.values[0].record = '一段故意写得很长很长的主诉症状描述文字'
    expect(codesOf(broken)).toContain('chief_complaint_too_long')
  })

  test('反例：主诉里出现阿拉伯数字 → chief_complaint_has_digits', () => {
    const broken = clone()
    broken.answers.duration.values[0].label = '2 周'
    broken.answers.duration.values[0].record = '2 周'
    expect(codesOf(broken)).toContain('chief_complaint_has_digits')
  })

  test('反例：栏目没有出处 → column_without_basis', () => {
    const broken = clone()
    delete broken.record.columns.find((c) => c.id === 'personal_history').basis
    expect(codesOf(broken)).toContain('column_without_basis')
  })

  test('反例：栏目没写「没落笔时显示什么」 → column_without_blank', () => {
    const broken = clone()
    delete broken.record.columns.find((c) => c.id === 'present_illness').blank
    expect(codesOf(broken)).toContain('column_without_blank')
  })

  test('反例：院方那一半被标成患者笔迹 → column_hospital_side_writable', () => {
    const broken = clone()
    const column = broken.record.columns.find((c) => c.id === 'signs')
    column.who = 'patient'
    column.fill = 'hospital'
    expect(codesOf(broken)).toContain('column_hospital_side_writable')
  })

  test('反例：问题指向了不存在的栏目 → question_column_unknown', () => {
    const broken = clone()
    questionOf(broken, 'q031').column = '没有这一栏'
    expect(codesOf(broken)).toContain('question_column_unknown')
  })

  test('反例：上屏文案里漏进内部词 → copy_leaks_internal', () => {
    const broken = clone()
    broken.ui.status_answering = '这一问的取值来自池子。'
    expect(codesOf(broken)).toContain('copy_leaks_internal')
  })

  test('反例：分支指向了后面的一问 → trigger_forward_reference', () => {
    const broken = clone()
    questionOf(broken, 'q008').ask_mode = 'player'
    questionOf(broken, 'q008').answers = 'duration'
    questionOf(broken, 'q008').column = 'present_illness'
    questionOf(broken, 'q008').lead = '最近一次加重：'
    questionOf(broken, 'q008').trigger = { q: 'q113', in: ['no'], label: '倒挂' }
    expect(codesOf(broken)).toContain('trigger_forward_reference')
  })

  test('反例：分支指向了不存在的一问 → trigger_unknown_question', () => {
    const broken = clone()
    questionOf(broken, 'q024b').trigger.q = 'q999'
    expect(codesOf(broken)).toContain('trigger_unknown_question')
  })

  test('反例：分支取值不在闭集里 → trigger_value_unknown', () => {
    const broken = clone()
    questionOf(broken, 'q024b').trigger.in = ['没有这一档']
    expect(codesOf(broken)).toContain('trigger_value_unknown')
  })

  test('反例：医方观察没有写观察记录 → observed_without_note', () => {
    const broken = clone()
    delete questionOf(broken, 'q097').observed_note
    expect(codesOf(broken)).toContain('observed_without_note')
  })

  test('反例：并入 / 撤回 / 保留的那几问没写理由 → question_without_note', () => {
    const broken = clone()
    delete questionOf(broken, 'q069').note
    expect(codesOf(broken)).toContain('question_without_note')
  })

  test('反例：追问层引用了不存在的提示 → probe_unknown', () => {
    const broken = clone()
    questionOf(broken, 'q038').probes = ['probe_不存在']
    expect(codesOf(broken)).toContain('probe_unknown')
  })

  test('反例：把必问的追问全部打开，一局超过 40 问 → run_too_long', () => {
    const broken = clone()
    // 把每一问都改成必问，再给每一问挂一个永远成立的追问 → 一局必然爆掉上限
    const spare = broken.questions.filter((q) => q.ask_mode === 'player').slice(0, 30)
    for (const q of spare) {
      q.required = true
      q.trigger = null
    }
    expect(codesOf(broken)).toContain('run_too_long')
  })

  test('反例：主诉拼不出来 → chief_complaint_unwritable', () => {
    const broken = clone()
    broken.refuse.record = ''
    broken.refuse.label = ''
    questionOf(broken, 'q003').ask_mode = 'player'
    // 把 q005 的闭集整档拿掉，让主诉的时间那一半永远拿不到字
    broken.questions.find((q) => q.id === 'q005').answers = '没有这个闭集'
    expect(codesOf(broken)).toContain('question_without_closed_set')
  })
})
