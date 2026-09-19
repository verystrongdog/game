import { createInterface } from 'node:readline/promises'
import { stdin as input, stdout as output } from 'node:process'
import {
  advanceOpeningStory,
  availableOpeningStoryActions,
  createOpeningStoryState,
} from './opening-story.js'

const bold = '\x1b[1m'
const dim = '\x1b[2m'
const reset = '\x1b[0m'
const clueLabels = {
  good_days: '好日子本的夜间记录',
  handover: '交接本把异常归入“全部平稳”',
  projection_repeat: '夜间投影重复了记录中的规程',
}

function render(state, actions) {
  console.clear()
  output.write(`${bold}开局剧情逻辑原型 · 替一个人记住夜晚${reset}\n`)
  output.write(`${dim}问题：两份记录 + 一次跨夜复查，能否让玩家自行理解昼夜记忆的不对称？${reset}\n\n`)
  output.write(`${bold}时段${reset}  ${state.time}\n`)
  output.write(`${bold}阶段${reset}  ${state.phase}\n`)
  output.write(`${bold}场景${reset}  ${state.scene}\n`)
  output.write(`${bold}承诺${reset}  ${state.promise ?? '—'}\n`)
  output.write(`${bold}线索${reset}  ${state.clues.length ? state.clues.map(id => clueLabels[id]).join('；') : '—'}\n`)
  output.write(`${bold}自问${reset}  ${state.question ?? '—'}\n\n`)
  if (state.completed) {
    output.write(`${bold}原型结束。${reset} 请判断：最后得到的是“规则说明”，还是“我替她记得”的关系？\n`)
    return
  }
  actions.forEach((action, index) => output.write(`${bold}[${index + 1}]${reset} ${action.label}\n`))
  output.write(`${bold}[q]${reset} 退出\n`)
}

const terminal = createInterface({ input, output })
let state = createOpeningStoryState()

while (!state.completed) {
  const actions = availableOpeningStoryActions(state)
  render(state, actions)
  const answer = (await terminal.question('\n选择：')).trim().toLowerCase()
  if (answer === 'q') break
  const selected = actions[Number(answer) - 1]
  if (selected) state = advanceOpeningStory(state, selected.id)
}

render(state, availableOpeningStoryActions(state))
terminal.close()
