import { describe, expect, test } from 'bun:test'
import { createOpeningState, dispatchOpening, openingActions, openingHotspots } from './opening-runtime.js'

const profile = {
  experiences: ['night-shifts', 'checking-work', 'heavy-labor', 'chronic-pain'],
  diseases: [],
}

describe('主角开场探索', () => {
  test('查看日期后进入可自由调查的医院外围', () => {
    const state = createOpeningState(profile)
    dispatchOpening(state, 'confirm_date')
    expect(state.phase).toBe('boundary')
    expect(openingHotspots(state).map(item => item.id)).toContain('walk_perimeter')
    expect(state.transcript.some(item => item.text.includes('农历月初'))).toBe(true)
  })

  test('必须完成绕行与投石才能踏上台阶', () => {
    const state = createOpeningState(profile)
    dispatchOpening(state, 'confirm_date')
    expect(openingHotspots(state).find(item => item.id === 'enter_steps').disabled).toBe(true)
    dispatchOpening(state, 'walk_perimeter')
    dispatchOpening(state, 'throw_stone')
    dispatchOpening(state, 'throw_stone')
    expect(openingHotspots(state).find(item => item.id === 'enter_steps').disabled).toBe(false)
  })

  test('检定失败也会生成内容，投石可重试', () => {
    const state = createOpeningState({ experiences: [], diseases: [] })
    dispatchOpening(state, 'confirm_date')
    dispatchOpening(state, 'throw_stone')
    expect(state.transcript.at(-1).kind).toBe('check')
    expect(state.transcript.at(-1).success).toBe(false)
    dispatchOpening(state, 'throw_stone')
    expect(state.visited.has('stone')).toBe(true)
  })

  test('台阶后的身份回应会收束为手环证据', () => {
    const state = createOpeningState(profile)
    dispatchOpening(state, 'confirm_date')
    dispatchOpening(state, 'walk_perimeter')
    dispatchOpening(state, 'throw_stone')
    dispatchOpening(state, 'throw_stone')
    dispatchOpening(state, 'enter_steps')
    expect(state.phase).toBe('daylight')
    expect(openingActions(state)).toHaveLength(4)
    dispatchOpening(state, 'answer_correct')
    expect(state.completed).toBe(true)
    expect(state.transcript.some(item => item.kind === 'evidence' && item.text.includes('苟笙'))).toBe(true)
  })
})
