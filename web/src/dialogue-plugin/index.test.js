/**
 * 对话插件单步契约。验收例不确立正式对白，也不使用现有人物稿。
 * 来源：design/presentation/NPC对话插件.md §一、§六
 */
import { describe, expect, test } from 'bun:test'
import { choose, present, validateCall, validatePack } from './index.js'

const call = {
  cells: {
    现场变化: '病历摊开，主诉栏空着，笔还没落下',
    人物眼前目标: '医师要先问清最压着的那一件',
    摩擦: '来诊的人可以只给一句，医师不能自己把格子填满',
    隐藏欲望: '把这一栏记清楚',
    玩家立场: '答这一件，或说不愿说',
    离场余波: '主诉栏写下睡眠，或仍空着',
  },
  identities: { a: '接诊医师', b: '来诊的人' },
  fact: { id: 'sleep', text: '近两周，醒了就再也睡不着' },
}

const pack = {
  entry: 'ask',
  nodes: [
    {
      id: 'ask',
      type: 'npc',
      speaker: '接诊医师',
      depth: 'surface',
      text: '今天主要是哪里不舒服？',
      fact_ref: 'identity',
      consistent: true,
      options: [
        { text: '睡不好。有两个星期了。醒了就再也睡不着。', leaf: '常规', next: 'hours' },
        { text: '不愿说。', leaf: '不拆穿', next: '' },
      ],
    },
    {
      id: 'hours',
      type: 'npc',
      speaker: '接诊医师',
      depth: 'surface',
      text: '一夜大概能睡几个小时？',
      fact_ref: 'sleep',
      consistent: true,
      options: [
        { text: '两三个小时。', leaf: '常规', next: '' },
      ],
    },
  ],
}

describe('validateCall', () => {
  test('六格、身份、一条事实齐了就通过', () => {
    expect(validateCall(call).ok).toBe(true)
  })

  test('缺事实不通过', () => {
    const broken = { ...call, fact: { id: '', text: '' } }
    expect(validateCall(broken).ok).toBe(false)
  })
})

describe('validatePack', () => {
  test('验收例这一包通过，且不确立正式对白', () => {
    expect(validatePack(call, pack).ok).toBe(true)
  })

  test('没有 fact_ref 不收', () => {
    const nodes = pack.nodes.map((node) => node.id === 'ask' ? { ...node, fact_ref: '' } : node)
    expect(validatePack(call, { ...pack, nodes }).ok).toBe(false)
  })

  test('一轮四个选项不收', () => {
    const ask = {
      ...pack.nodes[0],
      options: [
        { text: '一', leaf: '常规', next: '' },
        { text: '二', leaf: '不拆穿', next: '' },
        { text: '三', leaf: '换话题', next: '' },
        { text: '四', leaf: '给台阶', next: '' },
      ],
    }
    expect(validatePack(call, { entry: 'ask', nodes: [ask] }).ok).toBe(false)
  })

  test('一致时不能追问', () => {
    const ask = {
      ...pack.nodes[0],
      options: [{ text: '你刚才那句和事实对不上。', leaf: '追问', next: '' }],
    }
    expect(validatePack(call, { entry: 'ask', nodes: [ask] }).ok).toBe(false)
  })

  test('不一致时可以追问', () => {
    const ask = {
      ...pack.nodes[0],
      consistent: false,
      options: [{ text: '你刚才那句和事实对不上。', leaf: '追问', next: '' }],
    }
    expect(validatePack(call, { entry: 'ask', nodes: [ask] }).ok).toBe(true)
  })

  test('effect 必须留空', () => {
    const ask = { ...pack.nodes[0], effect: { san: 1 } }
    expect(validatePack(call, { entry: 'ask', nodes: [ask, pack.nodes[1]] }).ok).toBe(false)
  })
})

describe('单步播出', () => {
  test('present 不带 fact_ref', () => {
    const view = present(pack, 'ask')
    expect(view.text).toBe('今天主要是哪里不舒服？')
    expect(view.options).toHaveLength(2)
    expect(view.fact_ref).toBeUndefined()
  })

  test('choose 只走到 next，不串联整场', () => {
    expect(choose(pack, 'ask', 0)).toEqual({ done: false, nodeId: 'hours' })
    expect(choose(pack, 'ask', 1)).toEqual({ done: true, nodeId: null })
  })
})
