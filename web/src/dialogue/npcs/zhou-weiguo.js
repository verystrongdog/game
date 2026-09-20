// 来源：design/spec/material/drafts/周卫国-叙事视图.md §六、§八—§十。
export const zhouWeiguo = {
  id: 'zhou_weiguo', name: '周卫国', role: 'B1 男区 · 7 床', mark: '周',
  description: '他蹲在坏掉的东西旁边，先找承重点，再决定从哪里下工具。',
  objective: '看看他愿不愿意让你搭把手。',
  dossier: [
    { id: 'identity', label: '身份', text: '周卫国，B1 男区 7 床。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '他常拿着工具修理病区里的椅子和轮椅。', source: '当面观察', requires: { met: true } },
    { id: 'work', label: '过去的工作', text: '他以前在厂里干活；厂子已经没了。', source: '当面交谈', requires: { allFlags: ['talked_zhou'] } },
    { id: 'pain', label: '关系进展', text: '他愿意让你承认疼痛真实存在，而暂不争夺它的解释。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['zhou_pain_named'] } },
  ],
  situations: [
    { node: 'zhou_activity_room', requires: { times: ['afternoon'], locations: ['activity_room'], activities: ['修轮椅刹车'] } },
    { node: 'zhou_night', requires: { times: ['night'], locations: ['south_ward'], activities: ['坐着等走廊天亮'] } },
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
        { id: 'chair', text: '“这把椅子哪里坏了？”', meta: '先让他谈一件能修的东西', next: 'zhou_chair' },
      ],
    },
    zhou_tool: {
      id: 'zhou_tool',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“借的。”他没抬头，“轮椅刹车坏了，等报修得等到人摔。修完我就还。”' }],
      options: [
        { id: 'nurse', text: '“有人替你把账补上了。”', meta: '指出工具没有凭空回来', next: 'zhou_nurse' },
        { id: 'leave', text: '不追问是谁替他补上了工具。', meta: '结束会话', end: true },
      ],
    },
    zhou_nurse: {
      id: 'zhou_nurse',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '改锥在他手里停了一下。“她愿意补，是她的事。我修完会还。”他把螺丝又紧了半圈，“欠人情比欠工具麻烦。”' }],
      options: [
        { id: 'back', text: '不替郑晓敏讨这笔账，换一件能修的事。', meta: '继续初识层对话', next: 'zhou_surface' },
        { id: 'leave', text: '让他把借来的改锥用完。', meta: '结束会话', end: true },
      ],
    },
    zhou_work: {
      id: 'zhou_work',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“厂子没了。”他继续拧螺丝，“活着，就得干点啥。闲着，心里发慌。”' }],
      options: [
        { id: 'back', text: '让他继续修，换一个话题。', meta: '继续初识层对话', next: 'zhou_surface' },
        { id: 'leave', text: '让他把椅子修完。', meta: '结束会话', end: true },
      ],
    },
    zhou_factory: {
      id: 'zhou_factory',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“手上这点活儿没丢。丢的是别人还认不认。”他用拇指擦掉螺纹上的锈，“以前厂门口有我的照片。后来那面墙都拆了。”' }],
      options: [
        { id: 'back', text: '让锈留在他指腹上，等他继续说。', meta: '继续熟悉层对话', next: 'zhou_familiar' },
        { id: 'leave', text: '不再追问那面已经拆掉的墙。', meta: '结束会话', end: true },
      ],
    },
    zhou_chair: {
      id: 'zhou_chair',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“榫松了，胶没吃住。先把旧胶刮净，再压一宿。”他说得很快，“东西坏在哪儿，找着了就能修。”' }],
      options: [{ id: 'back', text: '“人也能这么找吗？”', meta: '他没有回答，但允许你继续问', next: 'zhou_surface' }],
    },
    zhou_familiar: {
      id: 'zhou_familiar',
      blocks: [
        { kind: 'description', text: '走廊尽头的金属门突然合上。周卫国肩膀一紧，改锥尖从螺帽上滑开。他低头摸了摸胸口，又立刻把手放下。' },
        { kind: 'npc', speaker: '周卫国', text: '“门轴该上油了。”他说的是门，眼睛却一直盯着自己的手。' },
      ],
      options: [
        { id: 'name_pain', text: '“我信疼是真的。原因可以以后再说。”', meta: '不争夺解释权', next: 'zhou_named', effects: { flagsAdd: ['zhou_pain_named'], relationDelta: 1 } },
        { id: 'bread', text: '“你为什么每天多拿一个馒头？”', meta: '从他的旧习惯问起', next: 'zhou_bread' },
        { id: 'noise', text: '“刚才关门声响的时候，你在看哪里？”', meta: '指出身体先于语言的反应', next: 'zhou_noise' },
        { id: 'factory', text: '“你说厂子没了。手艺也会跟着没吗？”', meta: '关系建立后再问失去的工作', next: 'zhou_factory' },
      ],
    },
    zhou_bread: {
      id: 'zhou_bread',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“半夜饿了吃。”他把馒头塞回兜里，“以前蹲劳务市场，有活儿就有下顿，没活儿就等着。手里有一个，心里不慌。”' }],
      options: [{ id: 'back', text: '不说“这里不会缺饭”。', meta: '继续熟悉层对话', next: 'zhou_familiar' }],
    },
    zhou_noise: {
      id: 'zhou_noise',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“看门轴。”他说完才发现自己攥紧了改锥，“突然响一声，谁都得看。别给我往病上套。”' }],
      options: [{ id: 'back', text: '“先不套。手松开就行。”', meta: '继续熟悉层对话', next: 'zhou_familiar' }],
    },
    zhou_named: {
      id: 'zhou_named',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '他的手停了一下。“你这话，比‘你没病’和‘你有病’都强。”' }],
      options: [{ id: 'leave', text: '把改锥递回去。', meta: '结束会话', end: true }],
    },
    zhou_core: {
      id: 'zhou_core',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“我爸那年拿刀，不是冲我。”他盯着手里的金属杆，“我知道。知道了也不代表身体肯信。”' }],
      options: [
        { id: 'dream', text: '“你希望他那天说什么？”', meta: '触碰他从未得到的回答', next: 'zhou_dream' },
        { id: 'leave', text: '不要求他继续解释。', meta: '结束深入对话', end: true },
      ],
    },
    zhou_dream: {
      id: 'zhou_dream',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“梦里他说，他害怕。厂子没了，他啥也不是了。”周卫国看着自己的手，“这话到底是他说的，还是我替他说的，我分不清。”' }],
      options: [{ id: 'leave', text: '“能说出来的那部分，先算你的。”', meta: '结束深入对话', end: true }],
    },
    zhou_activity_room: {
      id: 'zhou_activity_room', objective: '从一件正在被修好的东西认识周卫国。',
      blocks: [
        { kind: 'description', text: '活动室里有木屑和旧布味。周卫国把轮椅侧放在桌边，刹车簧、垫片和两颗螺丝按拆下来的顺序排成一线。' },
        { kind: 'npc', speaker: '周卫国', text: '“手别扶轮圈，油。”他试了两次刹车，“这东西卡住不怕，松了才摔人。”' },
        { kind: 'experience', source: '经历 · 重体力劳动', text: '他起身时没有撑膝盖，却把重心换了三次。你认得那种不肯让旁人看见旧伤的站法。', requires: { experiencesAny: ['heavy-labor'] } },
        { kind: 'experience', source: '经历 · 受过工伤', text: '他每次下工具前都先空转半圈，确认阻力。这不是炫技，是被一次失手教会的顺序。', requires: { experiencesAny: ['work-injury'] } },
      ],
      options: [
        { id: 'brake', text: '“怎么知道它是真的修好了？”', meta: '请他谈判断，不谈病历', next: 'zhou_brake' },
        { id: 'hold', text: '替他按住轮椅框架。', meta: '用动作加入，不抢过工具', end: true, effects: { flagsAdd: ['talked_zhou'], relationDelta: 1 } },
      ],
    },
    zhou_brake: {
      id: 'zhou_brake',
      blocks: [{ kind: 'npc', speaker: '周卫国', text: '“推、停、再压一次。不能光看它卡没卡住，得上重量。”他把轮椅放正，“人说没事不算，东西也一样。”' }],
      options: [{ id: 'leave', text: '推一下，再让它稳稳停住。', meta: '结束活动室交谈', end: true, effects: { flagsAdd: ['talked_zhou'] } }],
    },
    zhou_night: {
      id: 'zhou_night', objective: '陪他等一个没有突发响声的天亮。',
      blocks: [
        { kind: 'description', text: '南病房只留着门下的灯线。周卫国穿着外套坐在床边，鞋已经系好，像随时要去接一班并不存在的岗。' },
        { kind: 'npc', speaker: '周卫国', text: '“没睡不着。我以前这点儿正巡门。”走廊暖气管敲了一声，他的话断了半拍。' },
        { kind: 'experience', source: '经历 · 做过保安或门卫', text: '他坐的位置正好能看见门、窗和走廊转角。不是随便挑的床边。', requires: { experiencesAny: ['guard-work'] } },
        { kind: 'experience', source: '经历 · 长期危险与警觉', text: '声音响起前，他的脚已经踩实地面。你知道身体值班时，嘴上说“休息”没有用。', requires: { experiencesAny: ['dangerous-work', 'unsafe-place'] } },
      ],
      options: [
        { id: 'sit', text: '在他能看见门的位置坐下。', meta: '不挡出口，也不要求解释', end: true, effects: { relationDelta: 1 } },
        { id: 'sound', text: '“暖气管下一次响，大概还要多久？”', meta: '把不可控的声响变成可以一起等的事', next: 'zhou_noise' },
      ],
    },
  },
}
