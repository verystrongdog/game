// 来源：design/spec/material/drafts/谭丽娟-叙事视图.md §四—§八、§十四。
export const tanLijuan = {
  id: 'tan_lijuan', name: '谭丽娟', role: '住院楼一层 · 夜班护士', mark: '谭',
  description: '她用手掌压平交接本的一角，已经核完的那页仍停在眼前。',
  objective: '核对交接本里无人能复述的夜晚。',
  lockedHint: '先从郑晓敏处读到交接本',
  dossier: [
    { id: 'identity', label: '身份', text: '谭丽娟，住院楼一层夜班护士。', source: '当面交谈或交接本', revealsIdentity: true, requires: { metOrFlags: ['seen_handover'] } },
    { id: 'observed', label: '当面观察', text: '她认得自己的笔迹，却无法复述笔迹里的那段时间。', source: '当面观察', requires: { met: true } },
    { id: 'handover', label: '交接本记录', text: '昨夜两点十七分的处置由她签名，结语是“全部平稳”。', source: '院内记录', requires: { allFlags: ['seen_handover'] } },
    { id: 'projection', label: '夜间见证', text: '夜间的她会逐字重复交接本里的规程。', source: '玩家亲历', requires: { allFlags: ['witnessed_projection'] } },
  ],
  levels: [
    { id: 'surface', label: '初识', requires: { allFlags: ['seen_handover'] }, entries: [{ node: 'tan_projection', requires: { times: ['night'] } }, { node: 'tan_surface' }] },
    { id: 'familiar', label: '熟悉', entry: 'tan_familiar', requires: { allFlags: ['witnessed_projection'], times: ['morning'] } },
    { id: 'core', label: '深入', entry: 'tan_core', requires: { minRelation: 2, allFlags: ['told_tan_night'] } },
  ],
  nodes: {
    tan_surface: {
      id: 'tan_surface',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '“换药找郑晓敏。她白班。”她低头核对医嘱单，“你要问昨晚？本子在台面上。我不记得。”' },
        { kind: 'experience', source: '经历 · 长期上夜班、三班倒', text: '她不是冷淡。她在用最少的话，保护下一次值夜前仅剩的白天。', requires: { experiencesAny: ['night-shifts'] } },
      ],
      options: [
        { id: 'ask_stable', text: '“你每天都写‘全部平稳’？”', meta: '追问她唯一拥有的夜晚', next: 'tan_stable', effects: { relationDelta: 1 } },
        { id: 'ask_night', text: '“夜里只有你一个护士？”', meta: '询问夜巡和值班配合', next: 'tan_night' },
        { id: 'ask_day', text: '“下夜班以后，你的白天怎么过？”', meta: '询问她被借走的白天', next: 'tan_day' },
        { id: 'ask_fear', text: '“你一个人在夜里不怕吗？”', meta: '问一个她无法回忆的感受', next: 'tan_fear' },
        { id: 'leave', text: '先不打扰她。', meta: '结束会话', end: true },
      ],
    },
    tan_stable: {
      id: 'tan_stable',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '“这是我的笔迹。我认得。”她把本子推回来，“什么意思我记不起来了。我上九年夜班，就靠一行字认识我自己。”' },
      ],
      options: [
        { id: 'meaning', text: '“如果那四个字写错了呢？”', meta: '追问记录与经历之间的空白', next: 'tan_margin' },
        { id: 'leave', text: '把这句话记下来。', meta: '结束会话', end: true },
      ],
    },
    tan_margin: {
      id: 'tan_margin',
      blocks: [{ kind: 'npc', speaker: '谭丽娟', text: '“那就等白班发现。”她停了一下，“发现不了的，不归交接本管。”她把那页压平，动作比回答更慢。' }],
      options: [
        { id: 'back', text: '看着那页纸重新合上，再问另一件事。', meta: '继续初识层对话', next: 'tan_surface' },
        { id: 'leave', text: '先离开护士站。', meta: '结束会话', end: true },
      ],
    },
    tan_night: {
      id: 'tan_night',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '“还有郝大力。他守门，我巡房。我叫一声，他就到。”她翻过一页，“第二天他不记得，我也不记得。两个不知道，合不到一个知道。”' },
        { kind: 'experience', source: '经历 · 做过保安或门卫', text: '“他守门，我巡房”已经是一套完整分工：谁看入口、谁处理里面、哪一声呼叫意味着必须立刻到场。', requires: { experiencesAny: ['guard-work'] } },
      ],
      options: [
        { id: 'back', text: '不把两份空白当成证词，换一个问题。', meta: '继续初识层对话', next: 'tan_surface' },
        { id: 'leave', text: '让她继续核对医嘱单。', meta: '结束会话', end: true },
      ],
    },
    tan_day: {
      id: 'tan_day',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '“回家，拉遮光布，睡到下午三点。七点做饭，九点半回来。”她拧紧保温杯，“三个闹钟，没有一个叫我晚上睡觉。”' },
        { kind: 'experience', source: '经历 · 长期上夜班、三班倒', text: '你知道她省略了什么：白天不是休息时间，只是下一班之前必须完成的睡眠。', requires: { experiencesAny: ['night-shifts'] } },
      ],
      options: [
        { id: 'back', text: '“所以白天也在等下一次夜班。”', meta: '继续初识层对话', next: 'tan_surface' },
        { id: 'leave', text: '不再占用她剩下的白天。', meta: '结束会话', end: true },
      ],
    },
    tan_fear: {
      id: 'tan_fear',
      blocks: [{ kind: 'npc', speaker: '谭丽娟', text: '她想了很久。“怕很占地方。第二天记不住，它就没地方站。”她皱了皱眉，“我也说不明白。”' }],
      options: [
        { id: 'back', text: '不要求她替遗失的感受作证，换一个问题。', meta: '继续初识层对话', next: 'tan_surface' },
        { id: 'leave', text: '让这份说不明白留在这里。', meta: '结束会话', end: true },
      ],
    },
    tan_projection: {
      id: 'tan_projection', objective: '验证夜间护士是否仍是白天的谭丽娟。',
      blocks: [
        { kind: 'description', text: '护士站亮着。谭丽娟的动作准确、完整，没有疲惫，也没有可以被说服的情绪。' },
        { kind: 'npc', speaker: '谭丽娟 · 投影', text: '“现在是夜间。需要休息请登记；无其他事项，请回病房。”' },
        { kind: 'disease', form: 'intrusion', source: 'PTSD · 闯入式', text: '脚步声从走廊尽头逼近。不是现在这一次。', requires: { diseasesAny: ['PTSD'] } },
        { kind: 'disease', form: 'belief', source: '广泛性焦虑障碍 · 信念式', text: '她的每个字都正确。正因为全部正确，才没有一句能证明她在这里。', requires: { diseasesAny: ['广泛性焦虑障碍'] } },
        { kind: 'experience', source: '经历 · 被要求把事情忘掉', text: '你听得出“没有记忆”和“有人要求你否认记忆”的差别。可眼前这个声音没有留下任何能作证的犹豫。', requires: { experiencesAny: ['forced-forgetting'] } },
      ],
      options: [
        { id: 'repeat', text: '“两点十七分，是你把我劝回去的吗？”', meta: '重复交接本中的时刻', next: 'tan_projection_repeat', effects: { flagsAdd: ['witnessed_projection'], notes: [{ id: 'projection', text: '夜间投影逐字重复交接本里的规程。', source: '玩家亲历' }] } },
      ],
    },
    tan_projection_repeat: {
      id: 'tan_projection_repeat',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟 · 投影', text: '“现在是夜间，请回病房。”' },
        { kind: 'description', text: '语气、停顿和交接本里的处置一模一样。她不是在回忆；她正在再次完成规程。' },
      ],
      options: [{ id: 'morning', text: '休息到次日上午。', meta: '把只有你记得的夜晚带回白天', end: true, effects: { time: 'morning', flagsAdd: ['returned_after_projection'] } }],
    },
    tan_familiar: {
      id: 'tan_familiar', objective: '把夜间投影说过的话交还给本人。',
      blocks: [
        { kind: 'description', text: '白天的谭丽娟会困、会停顿。她正在读昨夜留下的交接本。' },
      ],
      options: [
        { id: 'tell', text: '把昨夜的对话原样讲给她。', meta: '成为她无法拥有的记忆', next: 'tan_told', effects: { flagsAdd: ['told_tan_night'], relationDelta: 2 } },
        { id: 'clocks', text: '“你怎么确认自己真的值完了一夜？”', meta: '从三个闹钟问到交班时刻', next: 'tan_clocks' },
      ],
    },
    tan_clocks: {
      id: 'tan_clocks',
      blocks: [{ kind: 'npc', speaker: '谭丽娟', text: '“早班脚步一响，我就知道结束了。推车、说话、开柜门，一起涌进来。”她指指交接本，“夜里靠这个。天亮靠声音。”' }],
      options: [{ id: 'back', text: '回到昨夜那件事。', meta: '继续回访', next: 'tan_familiar' }],
    },
    tan_told: {
      id: 'tan_told',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '她只问：“几点？”你说两点十七分。她看了看自己的笔迹。“那你比我清楚。”' },
        { kind: 'description', text: '她没有得到记忆。她得到的是一个愿意替她记住的人。' },
      ],
      options: [{ id: 'leave', text: '合上交接本。', meta: '结束会话', end: true }],
    },
    tan_core: {
      id: 'tan_core',
      blocks: [{ kind: 'npc', speaker: '谭丽娟', text: '“怕是一种很占地方的东西。第二天记不住，它就没地方站。”她顿了一下，“昨晚如果我怕过，你替它留个地方。”' }],
      options: [{ id: 'leave', text: '“我会记着。”', meta: '结束深入对话', end: true }],
    },
  },
}
