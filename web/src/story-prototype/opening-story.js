// 逻辑原型，非正式剧情实现。
// 来源：design/presentation/开局剧情逻辑原型.md §三。

export const openingStoryActions = {
  talk_zheng: {
    label: '与郑晓敏交谈',
    available: state => state.phase === 'waking',
  },
  inspect_good_days: {
    label: '查看好日子本',
    available: state => state.phase === 'investigating' && !state.clues.includes('good_days'),
  },
  inspect_handover: {
    label: '查看交接本',
    available: state => state.phase === 'investigating' && !state.clues.includes('handover'),
  },
  rest_to_night: {
    label: '休息至夜晚',
    available: state => state.phase === 'investigating'
      && state.clues.includes('good_days')
      && state.clues.includes('handover'),
  },
  talk_projection: {
    label: '询问夜间护士站投影',
    available: state => state.phase === 'night_verification',
  },
  rest_to_morning: {
    label: '休息至次日上午',
    available: state => state.phase === 'night_witnessed',
  },
  talk_tan: {
    label: '把昨夜讲给谭丽娟',
    available: state => state.phase === 'return_visit',
  },
}

export function createOpeningStoryState() {
  return {
    time: '第 1 日 · 上午',
    phase: 'waking',
    promise: null,
    clues: [],
    question: null,
    completed: false,
    scene: '你在住院楼一层醒来。一个年轻护士端着治疗盘推门进来。',
    history: [],
  }
}

export function availableOpeningStoryActions(state) {
  return Object.entries(openingStoryActions)
    .filter(([, action]) => action.available(state))
    .map(([id, action]) => ({ id, label: action.label }))
}

function append(state, action, scene, changes = {}) {
  return {
    ...state,
    ...changes,
    scene,
    history: [...state.history, action],
  }
}

export function advanceOpeningStory(state, action) {
  if (!openingStoryActions[action]?.available(state)) return state

  switch (action) {
    case 'talk_zheng':
      return append(state, action,
        '郑晓敏替你量了体温。她只能确认你是夜间入院，还说自己写过一行关于你的记录，却想不起落笔时发生了什么。', {
          phase: 'investigating',
          promise: '弄清昨夜自己为何到过护士站',
        })
    case 'inspect_good_days':
      return append(state, action,
        '好日子本里写着：新入院者昨夜自行走到护士站，又自己回了病房。郑晓敏认得字，但不记得写下这行时的情形。', {
          clues: [...state.clues, 'good_days'],
        })
    case 'inspect_handover':
      return append(state, action,
        '交接本在同一时刻写着“已劝回病房”，页面末尾仍是谭丽娟工整的四个字：全部平稳。', {
          clues: [...state.clues, 'handover'],
        })
    case 'rest_to_night':
      return append(state, action,
        '你带着两份互相咬合、却无人能解释的记录进入夜晚。护士站亮着，值班护士的动作准确得没有迟疑。', {
          time: '第 1 日 · 夜晚',
          phase: 'night_verification',
          question: '记录的是谁经历过的夜晚？',
        })
    case 'talk_projection':
      return append(state, action,
        '你问昨夜发生过什么。她只回答：“现在是夜间，请回病房。”语气、停顿和交接本中的处置一模一样。', {
          phase: 'night_witnessed',
          clues: [...state.clues, 'projection_repeat'],
        })
    case 'rest_to_morning':
      return append(state, action,
        '天亮后，护士站里的人会困、会停顿，也会忘记。谭丽娟正在核对昨夜的交接本。', {
          time: '第 2 日 · 上午',
          phase: 'return_visit',
        })
    case 'talk_tan':
      return append(state, action,
        '谭丽娟听完，只问你当时是几点。你回答后，她看了看自己的笔迹：“那你比我清楚。”你第一次替另一个人记住了她的夜晚。', {
          phase: 'complete',
          promise: '✓ 弄清昨夜自己为何到过护士站',
          question: '替别人记住，算不算证据？',
          completed: true,
        })
    default:
      return state
  }
}
