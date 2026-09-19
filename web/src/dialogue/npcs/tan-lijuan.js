// 来源：design/spec/material/drafts/谭丽娟-叙事视图.md §四—§八、§十四。
export const tanLijuan = {
  id: 'tan_lijuan', name: '谭丽娟', role: '住院楼一层 · 夜班护士', mark: '谭',
  description: '她认得自己的笔迹，不拥有笔迹里的那段时间。',
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
        { id: 'leave', text: '先不打扰她。', meta: '结束会话', end: true },
      ],
    },
    tan_stable: {
      id: 'tan_stable',
      blocks: [
        { kind: 'npc', speaker: '谭丽娟', text: '“这是我的笔迹。我认得。”她把本子推回来，“什么意思我记不起来了。我上九年夜班，就靠一行字认识我自己。”' },
      ],
      options: [{ id: 'leave', text: '把这句话记下来。', meta: '结束会话', end: true }],
    },
    tan_projection: {
      id: 'tan_projection', objective: '验证夜间护士是否仍是白天的谭丽娟。',
      blocks: [
        { kind: 'description', text: '护士站亮着。谭丽娟的动作准确、完整，没有疲惫，也没有可以被说服的情绪。' },
        { kind: 'npc', speaker: '谭丽娟 · 投影', text: '“现在是夜间。需要休息请登记；无其他事项，请回病房。”' },
        { kind: 'disease', form: 'intrusion', source: 'PTSD · 闯入式', text: '脚步声从走廊尽头逼近。不是现在这一次。', requires: { diseasesAny: ['PTSD'] } },
        { kind: 'disease', form: 'belief', source: '广泛性焦虑障碍 · 信念式', text: '她的每个字都正确。正因为全部正确，才没有一句能证明她在这里。', requires: { diseasesAny: ['广泛性焦虑障碍'] } },
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
      options: [{ id: 'tell', text: '把昨夜的对话原样讲给她。', meta: '成为她无法拥有的记忆', next: 'tan_told', effects: { flagsAdd: ['told_tan_night'], relationDelta: 2 } }],
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
