import { calculateAttributes } from '../character-creation/character-model.js'

// 来源：design/presentation/主角开场场景示范.md §2.1。
// 原型只使用已有属性档位边界：3=协调，5=精通，7=娴熟；不新建掷骰规则。
const thresholds = Object.freeze({ coordinated: 3, proficient: 5, practiced: 7 })

const openingParagraphs = Object.freeze([
  '苟智空下了夜班离开公司准备回家。',
  '因为差不多一整天都蜷缩在工位上，等车的间隙他没有再刷手机，而是仰起脖子，看向被城市喧嚣夺去宁静的夜空。',
  '不像那些被灯光遮掩的星星，一轮圆月仍然突兀地挂在天边，就像过去几十亿年那样，仿佛在庄严地宣告着自己才是夜晚真正的主人。',
])

const boundaryParagraphs = Object.freeze([
  '好像有什么地方不对。',
  '苟智空掏出手机确认了一下，今天是农历月初，怎么会有这么大的月亮？',
  '当苟智空重新抬起头时，身边的景色已经截然不同。身后的办公楼不见了，取而代之的是一栋医院的门诊楼，不过里面没有亮灯，那楼的楼顶竖着几个红色大字——“　　精神卫生中心”。',
  '自己正站在这栋建筑的大门前，大门的对面是一条柏油马路。马路两边的路灯都正常亮着，他却看不见任何马路对面的街景。',
])

const daylightParagraphs = Object.freeze([
  '在苟智空走上门诊前台阶的瞬间，他的周遭忽然亮了起来。',
  '夜晚的寂静被打破，喧闹的声音纷至沓来。轮子压过地砖，远处有人交班，消毒水的味道从自动门里冲出来。',
  '苟智空木木地看向周围。他摘下眼镜用衣角擦了擦，又重新戴上。',
  '如果他没认错的话，现在挂在天上的——是他妈的狗日的太阳。',
  '远处有两个人影急匆匆地赶向这里。其中一个人朝手中对讲机式的东西喊着：“找到了，找到了。”',
  '一名护士，一名保安。',
  '“0527！你为什么会在这里？你是怎么从病房里跑出来的？”',
])

function block(kind, label, text, extra = {}) {
  return { kind, label, text, ...extra }
}

function checkBlock(attribute, mode, score, threshold, success, successText, failureText) {
  return block('check', `${attribute}·${mode}检定`, success ? '成功' : '失败', {
    attribute,
    mode,
    score,
    threshold,
    success,
    detail: success ? successText : failureText,
  })
}

function experienceBlocks(profile, idsToCopy) {
  return idsToCopy
    .filter(([id]) => profile.experiences.has(id))
    .map(([, label, text]) => block('experience', `经历·${label}`, text))
}

function scoreOf(state, attribute) {
  return state.attributes[attribute]?.points ?? 0
}

function pass(state, attribute, threshold) {
  return scoreOf(state, attribute) >= threshold
}

function append(state, ...blocks) {
  state.transcript.push(...blocks.flat())
}

export function createOpeningState(rawProfile = {}) {
  const profile = {
    experiences: new Set(rawProfile.experiences || []),
    diseases: new Set(rawProfile.diseases || []),
  }
  const attributes = calculateAttributes(profile.experiences)
  return {
    phase: 'moon',
    profile,
    attributes,
    visited: new Set(),
    attempts: {},
    transcript: openingParagraphs.map(text => block('description', '夜班之后', text)),
    completed: false,
  }
}

function visitOnce(state, id, blocks) {
  if (state.visited.has(id)) return false
  state.visited.add(id)
  append(state, blocks)
  return true
}

function inspectMoon(state) {
  const success = pass(state, '观察', thresholds.coordinated)
  visitOnce(state, 'moon', [
    checkBlock('观察', '被动', scoreOf(state, '观察'), thresholds.coordinated, success,
      '今晚的月亮不只是大。它太完整了，完整得与你记得的日期互相抵触。',
      '你看得出月亮很大。疲惫暂时不允许你说出更多。'),
    ...experienceBlocks(state.profile, [
      ['night-shifts', '长期上夜班、三班倒', '你会弄错星期，不会弄错下班时的天。'],
      ['checking-work', '长期做核对类工作', '日期、月相。两个字段对不上。先别给它找解释。'],
    ]),
  ])
}

function confirmDate(state) {
  if (state.phase !== 'moon') return
  inspectMoon(state)
  state.phase = 'boundary'
  append(state, boundaryParagraphs.map(text => block('description', '再抬头', text)))
}

function inspectSign(state) {
  const success = pass(state, '观察', thresholds.coordinated)
  visitOnce(state, 'sign', [checkBlock('观察', '被动', scoreOf(state, '观察'), thresholds.coordinated, success,
    '红字前面有拆卸后的孔位和色差。那里本来确实有一个地名，不是留白。',
    '你能读出“精神卫生中心”。前面空着，夜色不肯给你更多。')])
}

function inspectPhone(state) {
  const success = pass(state, '巧手', thresholds.proficient)
  visitOnce(state, 'phone', [
    block('description', '手机', '苟智空打开导航，想看看自己现在到底在哪里。手机接收不到一丁点信号。'),
    checkBlock('巧手', '主动', scoreOf(state, '巧手'), thresholds.proficient, success,
      '飞行模式关着，卡槽没有松，导航程序也在工作。手机没坏；它只是没有任何东西可以连接。',
      '你在几个菜单之间来回切换。每一页都用不同的图标告诉你同一件事：没有信号。'),
    ...experienceBlocks(state.profile, [
      ['alone-city', '一个人在陌生城市', '导航曾经是你在陌生地方最便宜的担保人。现在它也不知道你在哪里。'],
      ['checking-work', '长期做核对类工作', '你已经排除了能排除的用户错误。'],
    ]),
  ])
}

function inspectDarkness(state) {
  const success = pass(state, '观察', thresholds.proficient)
  visitOnce(state, 'darkness', [
    block('description', '马路对面', '不，用“看不见”来描述并不准确。更确切地说，好像有一张无边无际的嘴沿着马路边缘将另一侧的一切尽数吞没一般。'),
    checkBlock('观察', '主动', scoreOf(state, '观察'), thresholds.proficient, success,
      '路灯的光并没有逐渐变暗。它在道路边缘结束得很干净，像是外面根本没有一个地方可供光线继续。',
      '你盯得太久，视野里开始出现眼球自己制造的颜色。它们不能告诉你对面有什么。'),
    ...experienceBlocks(state.profile, [
      ['guard-work', '做过保安或门卫', '边界应该把人分成里外。这道边界只留下了里面。'],
      ['stalked', '被跟踪过、被威胁过', '你的身体已经开始计算逃跑路线。它一条也没有找到。'],
    ]),
  ])
}

function walkPerimeter(state) {
  const success = pass(state, '体格', thresholds.proficient)
  state.visited.add('perimeter')
  append(state,
    block('description', '沿人行道往回走', '苟智空沿着脚下的人行道往回走，希望能找到来时的路。随着走的距离越来越远，他的心也逐渐沉到谷底。'),
    checkBlock('体格', '主动', scoreOf(state, '体格'), thresholds.proficient, success,
      '你保住了速度，也保住了对路线的记忆。歪斜的路灯、破损的围栏、大门。它们按照不可能的顺序重复了。',
      '你的腿在加班后拒绝提供精密的里程。可大门还是回来了，站在你面前，像是它从未离开。'),
    block('description', '大门', '在绕着整个建筑园区走了一圈回到大门口后，苟智空不得不绝望地承认，这里彻底被诡异的黑暗包围着。'),
    block('disease', '固有疾病·名称未显示', '你没有迷路。路把你送了回来。'))
}

function throwStone(state) {
  // 来源：同上 §2.1；失败允许重试，成功后才写入原稿确定的越界事实。
  state.attempts.stone = (state.attempts.stone || 0) + 1
  const success = pass(state, '体格', thresholds.coordinated) || state.attempts.stone >= 2
  append(state,
    block('description', '绿化带', '苟智空伸手抠起人行道边绿化带里的一块石头，猛地扔了过去。'),
    checkBlock('体格', '主动', scoreOf(state, '体格'), thresholds.coordinated, success,
      '石头越过马路，砸进了黑暗。你等着它落地。没有声音。',
      '石头撞在路沿上，弹回来。这一次你听得很清楚；外面那一次，你还没有试出来。'))
  if (success) {
    state.visited.add('stone')
    append(state,
      block('description', '黑暗', '那块石头进入黑暗后并没有传来落地的声音。'),
      block('disease', '固有疾病·名称未显示', '被吞噬的也许不是外面的世界，而是你。'))
  }
}

function enterSteps(state) {
  if (!state.visited.has('perimeter') || !state.visited.has('stone')) return
  const success = pass(state, '意志', thresholds.proficient)
  append(state,
    checkBlock('意志', '主动', scoreOf(state, '意志'), thresholds.proficient, success,
      '你没有说服自己这栋医院是安全的。你只是停止假装还有第三条路。',
      '你终究没有鼓起足够的勇气走向黑暗。逃离它的力量把你推上了台阶。'),
    ...daylightParagraphs.map(text => block('description', '台阶上', text)))
  state.phase = 'daylight'
}

function answerStaff(state, answer) {
  if (state.phase !== 'daylight') return
  const answerText = {
    correct: '“我不是 0527。我叫苟智空。”',
    help: '“先告诉我这是哪里。”',
    time: '“现在是几点？今天几号？”',
    run: '不说话。起身。跑。',
  }[answer]
  if (!answerText) return
  append(state, block('player', '你', answerText))
  if (answer !== 'run') {
    const success = pass(state, '沟通', thresholds.proficient)
    append(state, checkBlock('沟通', '主动', scoreOf(state, '沟通'), thresholds.proficient, success,
      '你把姓名、上一个地点和时间顺序说得清楚。护士也听清了。这不妨碍她把它记作“0527 否认身份”。',
      '你急着把所有事实同时挤出去。护士只抓住了其中一个词：“不是”。'))
  }
  append(state,
    block('description', '制服', '还没等苟智空站起身，保安直接用防暴叉卡住他的脖子，把他掼在了地上。'),
    block('description', '手腕', '自己衣服的袖子不知道什么时候染上了蓝白条纹。袖子下方还有一个蓝色手环。'),
    block('evidence', '蓝色手环', '姓名：苟笙\n编号：0527\n性别：男\n药物过敏史：无\n床号：B 栋 147 室 4 床'),
    block('disease', '固有疾病·名称未显示', '这不是他们现在才给你的名字。手环在他们找到你之前，就已经戴在你身上了。'),
    block('description', '苟智空', '苟智空的大脑一片空白。\n\n自己什么时候变成精神病了。'))
  state.phase = 'complete'
  state.completed = true
}

export function openingActions(state) {
  if (state.phase === 'moon') return [
    { id: 'inspect_moon', label: '仔细看那轮月亮', meta: '观察·被动检定' },
    { id: 'confirm_date', label: '掏出手机，确认日期', meta: '原稿行动·进入探索区' },
  ]
  if (state.phase === 'daylight') return [
    { id: 'answer_correct', label: '“我不是 0527。我叫苟智空。”', meta: '沟通·主动检定' },
    { id: 'answer_help', label: '“先告诉我这是哪里。”', meta: '沟通·主动检定' },
    { id: 'answer_time', label: '“现在是几点？今天几号？”', meta: '沟通·主动检定' },
    { id: 'answer_run', label: '跑！', meta: '不说话，立即行动' },
  ]
  if (state.phase === 'complete') return [{ id: 'finish', label: '醒来', meta: '进入 B 栋 147 室的第一个白天' }]
  return []
}

export function openingHotspots(state) {
  if (state.phase !== 'boundary') return []
  const exitReady = state.visited.has('perimeter') && state.visited.has('stone')
  return [
    { id: 'inspect_sign', label: '残缺招牌', visited: state.visited.has('sign'), position: 'sign' },
    { id: 'inspect_phone', label: '手机导航', visited: state.visited.has('phone'), position: 'phone' },
    { id: 'inspect_darkness', label: '马路对面', visited: state.visited.has('darkness'), position: 'darkness' },
    { id: 'walk_perimeter', label: '绕园区一周', visited: state.visited.has('perimeter'), position: 'perimeter' },
    { id: 'throw_stone', label: state.visited.has('stone') ? '石头已越过马路' : '绿化带的石头', visited: state.visited.has('stone'), position: 'stone' },
    { id: 'enter_steps', label: exitReady ? '走上门诊台阶' : '门诊台阶·还不能下决心', visited: false, disabled: !exitReady, position: 'steps' },
  ]
}

export function dispatchOpening(state, actionId) {
  const actions = {
    inspect_moon: inspectMoon,
    confirm_date: confirmDate,
    inspect_sign: inspectSign,
    inspect_phone: inspectPhone,
    inspect_darkness: inspectDarkness,
    walk_perimeter: walkPerimeter,
    throw_stone: throwStone,
    enter_steps: enterSteps,
    answer_correct: value => answerStaff(value, 'correct'),
    answer_help: value => answerStaff(value, 'help'),
    answer_time: value => answerStaff(value, 'time'),
    answer_run: value => answerStaff(value, 'run'),
  }
  actions[actionId]?.(state)
  return state
}
