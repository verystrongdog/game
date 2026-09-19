// 来源：design/spec/material/drafts/周卫国-叙事视图.md §六、§八—§十。
export const zhouWeiguo = {
  id: 'zhou_weiguo', name: '周卫国', role: 'B1 男区 · 7 床', mark: '周',
  description: '他不承认自己需要帮助，但已经修好了半层楼。',
  objective: '从一把改锥谈到他不肯命名的疼痛。',
  dossier: [
    { id: 'identity', label: '身份', text: '周卫国，B1 男区 7 床。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '他常拿着工具修理病区里的椅子和轮椅。', source: '当面观察', requires: { met: true } },
    { id: 'work', label: '过去的工作', text: '他以前在厂里干活；厂子已经没了。', source: '当面交谈', requires: { allFlags: ['talked_zhou'] } },
    { id: 'pain', label: '关系进展', text: '他愿意让你承认疼痛真实存在，而暂不争夺它的解释。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['zhou_pain_named'] } },
  ],
  levels: [
    { id: 'surface', label: '初识', entry: 'zhou_surface' },
    { id: 'familiar', label: '熟悉', entry: 'zhou_familiar', requires: { minRelation: 1, allFlags: ['talked_zhou'] } },
    { id: 'core', label: '深入', entry: 'zhou_core', requires: { minRelation: 2, allFlags: ['zhou_pain_named'] } },
  ],
  nodes: {
    zhou_surface: {
      id: 'zhou_surface',
      blocks: [
        { kind: 'description', text: '周卫国蹲在活动室门口修一把椅子。改锥在他手里转了一圈，像回到本来该在的位置。' },
        { kind: 'npc', speaker: '周卫国', text: '“别踩那条腿。刚上胶，还没吃住劲。”' },
        { kind: 'experience', source: '经历 · 长期在危险环境干活', text: '你看得出他先试了承重点，再动手。那不是谨慎，是很多年没被允许出错。', requires: { experiencesAny: ['dangerous-work'] } },
        { kind: 'disease', form: 'intrusion', source: 'PTSD · 闯入式', text: '远处金属门“当”地合上。你的肩膀先于意识绷紧。', requires: { diseasesAny: ['PTSD'] } },
      ],
      options: [
        { id: 'tool', text: '“这把改锥是护士站丢的那把？”', meta: '指出工具来路', next: 'zhou_tool', effects: { flagsAdd: ['talked_zhou', 'zhou_tool'], relationDelta: 1 } },
        { id: 'work', text: '“你以前一直干这个？”', meta: '从手艺问到厂子', next: 'zhou_work', effects: { flagsAdd: ['talked_zhou'] } },
      ],
    },
    zhou_tool: {
      id: 'zhou_tool',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“借的。”他没抬头，“轮椅刹车坏了，等报修得等到人摔。修完我就还。”' }],
      options: [{ id: 'leave', text: '不追问是谁替他补上了工具。', meta: '结束会话', end: true }],
    },
    zhou_work: {
      id: 'zhou_work',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“厂子没了。”他继续拧螺丝，“活着，就得干点啥。闲着，心里发慌。”' }],
      options: [{ id: 'leave', text: '让他把椅子修完。', meta: '结束会话', end: true }],
    },
    zhou_familiar: {
      id: 'zhou_familiar',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“他们说心电图正常。仪器正常不代表我不疼。我难受，是真的难受。”' }],
      options: [{ id: 'name_pain', text: '“我信疼是真的。原因可以以后再说。”', meta: '不争夺解释权', next: 'zhou_named', effects: { flagsAdd: ['zhou_pain_named'], relationDelta: 1 } }],
    },
    zhou_named: {
      id: 'zhou_named',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '他的手停了一下。“你这话，比‘你没病’和‘你有病’都强。”' }],
      options: [{ id: 'leave', text: '把改锥递回去。', meta: '结束会话', end: true }],
    },
    zhou_core: {
      id: 'zhou_core',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“我爸那年拿刀，不是冲我。”他盯着手里的金属杆，“我知道。知道了也不代表身体肯信。”' }],
      options: [{ id: 'leave', text: '不要求他继续解释。', meta: '结束深入对话', end: true }],
    },
  },
}
