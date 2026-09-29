/**
 * 对话插件 · 单步接口。
 *
 * 一次调用收六格、双方身份、一条事实，校验一场已经写好的节点包，并按选项走到下一节点。
 * 不生成句子，不串联多轮，不调用 C# 引擎。
 *
 * 来源：design/presentation/NPC对话插件.md §一、§三、§四
 * 多轮串联不在本模块：同文 §二
 */

/** 来源：场景化对话与任务写作方法 §二；插件契约 §一 */
export const CELL_KEYS = [
  '现场变化',
  '人物眼前目标',
  '摩擦',
  '隐藏欲望',
  '玩家立场',
  '离场余波',
]

/** 来源：NPC对话插件 §二 第 4 步。一致的一轮不得使用挑战叶子。 */
export const LEAVES = {
  常规: 'consistent',
  不拆穿: 'protect',
  换话题: 'protect',
  给台阶: 'protect',
  圆场: 'protect',
  追问: 'challenge',
  点破: 'challenge',
  质疑: 'challenge',
}

const DEPTHS = new Set(['surface', 'familiar', 'core'])

const fail = (errors) => ({ ok: false, errors })
const pass = () => ({ ok: true, errors: [] })

const nonempty = (value) => typeof value === 'string' && value.trim() !== ''

/**
 * 校验一次调用的输入。来源：NPC对话插件 §一
 * @param {{ cells: Record<string, string>, identities: { a: string, b: string }, fact: { id: string, text: string } }} call
 */
export function validateCall(call) {
  const errors = []
  const cells = call?.cells ?? {}
  for (const key of CELL_KEYS) {
    if (!nonempty(cells[key])) errors.push(`六格缺「${key}」`)
  }
  if (!nonempty(call?.identities?.a) || !nonempty(call?.identities?.b)) {
    errors.push('身份要写明谁在问、谁在答')
  }
  if (!nonempty(call?.fact?.id) || !nonempty(call?.fact?.text)) {
    errors.push('要有一条事实')
  }
  return errors.length ? fail(errors) : pass()
}

function factRefOk(factRef, fact) {
  return factRef === fact.id || factRef === 'identity'
}

/**
 * 校验一个节点。来源：NPC对话插件 §三、§二（一致则不写挑战）
 */
export function validateNode(call, node) {
  const errors = []
  if (!nonempty(node?.id)) errors.push('节点缺 id')
  if (node?.type !== 'npc') errors.push(`${node?.id ?? '?'} 的 type 必须是 npc`)
  if (!nonempty(node?.speaker)) errors.push(`${node?.id ?? '?'} 缺 speaker`)
  if (!DEPTHS.has(node?.depth)) errors.push(`${node?.id ?? '?'} 的 depth 必须是 surface / familiar / core`)
  if (!nonempty(node?.text)) errors.push(`${node?.id ?? '?'} 缺给予`)
  if (!factRefOk(node?.fact_ref, call.fact)) {
    errors.push(`${node?.id ?? '?'} 的 fact_ref 必须是这条事实或 identity`)
  }
  if (node?.perceptions != null && Object.keys(node.perceptions).length > 0) {
    errors.push(`${node.id} 的 perceptions 必须留空`)
  }
  if (node?.effect != null) errors.push(`${node.id} 的 effect 必须留空`)
  if (typeof node?.consistent !== 'boolean') errors.push(`${node?.id ?? '?'} 要标明 consistent`)
  const options = node?.options
  if (!Array.isArray(options)) {
    errors.push(`${node?.id ?? '?'} 缺 options`)
    return errors
  }
  if (options.length > 3) errors.push(`${node.id} 一轮最多三个选项`)
  for (const option of options) {
    if (!nonempty(option?.text)) errors.push(`${node.id} 有空选项`)
    if (!Object.hasOwn(LEAVES, option?.leaf)) errors.push(`${node.id} 的叶子「${option?.leaf}」不在第 4 步`)
    if (node.consistent && LEAVES[option?.leaf] === 'challenge') {
      errors.push(`${node.id} 一致时不能写「${option.leaf}」`)
    }
  }
  return errors
}

/**
 * 校验整包。next 必须指向包内节点，或留空表示这一支结束。
 * 来源：NPC对话插件 §三、§四
 */
export function validatePack(call, pack) {
  const callResult = validateCall(call)
  if (!callResult.ok) return callResult
  const errors = []
  const nodes = pack?.nodes
  if (!Array.isArray(nodes) || nodes.length === 0) return fail(['节点包是空的'])
  const ids = new Set()
  for (const node of nodes) {
    if (ids.has(node?.id)) errors.push(`节点 id 重复：${node.id}`)
    ids.add(node?.id)
    errors.push(...validateNode(call, node))
  }
  if (!ids.has(pack?.entry)) errors.push('entry 不在节点包里')
  for (const node of nodes) {
    for (const option of node.options ?? []) {
      if (option.next != null && option.next !== '' && !ids.has(option.next)) {
        errors.push(`${node.id} 的 next「${option.next}」不在包里`)
      }
    }
  }
  return errors.length ? fail(errors) : pass()
}

/**
 * 播出一轮。fact_ref 不上屏。来源：NPC对话插件 §四
 */
export function present(pack, nodeId) {
  const node = pack.nodes.find((item) => item.id === nodeId)
  if (!node) throw new Error(`没有节点 ${nodeId}`)
  return {
    id: node.id,
    speaker: node.speaker,
    text: node.text,
    options: node.options.map((option) => ({ text: option.text, leaf: option.leaf })),
  }
}

/**
 * 走一个选项。不决定下一轮的前提，只返回 next。
 * 来源：NPC对话插件 §四；多轮串联由调用方写，同文 §二
 */
export function choose(pack, nodeId, optionIndex) {
  const node = pack.nodes.find((item) => item.id === nodeId)
  if (!node) throw new Error(`没有节点 ${nodeId}`)
  const option = node.options[optionIndex]
  if (!option) throw new Error(`${nodeId} 没有第 ${optionIndex} 个选项`)
  if (option.next == null || option.next === '') return { done: true, nodeId: null }
  return { done: false, nodeId: option.next }
}
