// 来源：design/spec/material/drafts/吴桐-叙事视图.md §八—§十一。
export const wuTong = {
  id: 'wu_tong', name: '吴桐', role: 'B2 女区 · 11 床', mark: '吴',
  description: '她能把每个数字说得很清楚，唯独不肯让数字离开自己。',
  objective: '听懂“配合”与“控制”为什么可以同时成立。',
  dossier: [
    { id: 'identity', label: '身份', text: '吴桐，B2 女区 11 床。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '她把病号服袖口折得一样宽，床边放着一张写满数字的纸。', source: '当面观察', requires: { met: true } },
    { id: 'numbers', label: '她的说法', text: '她把体重视为少数仍由自己决定的事情。', source: '当面交谈', requires: { minRelation: 1, allFlags: ['talked_wu'] } },
    { id: 'control', label: '关系进展', text: '她开始接受把问题谈成决定权，而不只是食物和数字。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['wu_control'] } },
  ],
  levels: [
    { id: 'surface', label: '初识', entry: 'wu_surface' },
    { id: 'familiar', label: '熟悉', entry: 'wu_familiar', requires: { minRelation: 1, allFlags: ['talked_wu'] } },
    { id: 'core', label: '深入', entry: 'wu_core', requires: { minRelation: 2, allFlags: ['wu_control'] } },
  ],
  nodes: {
    wu_surface: {
      id: 'wu_surface',
      blocks: [
        { kind: 'description', text: '吴桐把病号服袖口折得一样宽。床边没有零食，只有一张写满数字的纸。' },
        { kind: 'npc', speaker: '吴桐', text: '“我知道体重太低。我也知道正常范围是多少。知道和做到不是一回事。”' },
        { kind: 'experience', source: '经历 · 被家人管过身体', text: '你认得那种语法：别人说“为你好”，真正被收走的是最后一点决定权。', requires: { experiencesAny: ['body-policed'] } },
        { kind: 'disease', form: 'belief', source: '神经性厌食症 · 信念式', text: '她纸上的数字没有错。数字不会骗你。', requires: { diseasesAny: ['神经性厌食症'] } },
      ],
      options: [
        { id: 'numbers', text: '“你为什么把每次称重都记下来？”', meta: '从数字谈起', next: 'wu_numbers', effects: { flagsAdd: ['talked_wu'], relationDelta: 1 } },
        { id: 'food', text: '“今天吃过东西了吗？”', meta: '直接询问身体状况', next: 'wu_food' },
      ],
    },
    wu_numbers: {
      id: 'wu_numbers',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我妈管成绩、专业、几点睡。只有体重，是我自己的。每少一点，至少有一件事听我的。”' }],
      options: [{ id: 'leave', text: '不去碰她那张纸。', meta: '结束会话', end: true }],
    },
    wu_food: {
      id: 'wu_food',
      blocks: [
        { kind: 'npc', speaker: '吴桐', text: '“吃过。”她答得太快，然后补了一句，“我会配合治疗。”' },
        { kind: 'disease', form: 'intrusion', source: '躯体症状障碍 · 闯入式', text: '她的指甲发白。手腕的脉搏太慢。身体先把答案说了。', requires: { diseasesAny: ['躯体症状障碍'] } },
      ],
      options: [{ id: 'leave', text: '不继续逼问。', meta: '结束会话', end: true }],
    },
    wu_familiar: {
      id: 'wu_familiar',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“他们总问我为什么不吃。没人问过，如果连这个也不由我，我还剩什么。”' }],
      options: [{ id: 'control', text: '“也许要留下的不是数字，是决定权。”', meta: '谈控制而不是食物', next: 'wu_control', effects: { flagsAdd: ['wu_control'], relationDelta: 1 } }],
    },
    wu_control: {
      id: 'wu_control',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '她看了你很久。“这句话比‘你应该多吃’好一点。只好一点。”' }],
      options: [{ id: 'leave', text: '“一点就够了。”', meta: '结束会话', end: true }],
    },
    wu_core: {
      id: 'wu_core',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我爸以前只希望我别太累。我那时觉得他没出息。”她把数字纸折起来，“现在想想，那可能是家里唯一一句没要求我变好的话。”' }],
      options: [{ id: 'leave', text: '陪她坐一会儿。', meta: '结束深入对话', end: true }],
    },
  },
}
