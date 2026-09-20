// 来源：design/spec/material/drafts/吴桐-叙事视图.md §八—§十三；design/events/剧情系统设计.md §3.8.2。
export const wuTong = {
  id: 'wu_tong', name: '吴桐', role: 'B2 女区 · 11 床', mark: '吴',
  description: '她把病号服袖口折得一样宽，用手掌压着一张写满数字的纸。',
  objective: '弄清她为什么反复改写同一组数字。',
  dossier: [
    { id: 'identity', label: '身份', text: '吴桐，B2 女区 11 床。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '她把病号服袖口折得一样宽，床边放着一张写满数字的纸。', source: '当面观察', requires: { met: true } },
    { id: 'numbers', label: '她的说法', text: '她把体重视为少数仍由自己决定的事情。', source: '当面交谈', requires: { minRelation: 1, allFlags: ['talked_wu'] } },
    { id: 'control', label: '关系进展', text: '她开始接受把问题谈成决定权，而不只是食物和数字。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['wu_control'] } },
  ],
  situations: [
    { node: 'wu_court', requires: { times: ['afternoon'], locations: ['basketball_court'], activities: ['沿边线计步'] } },
    { node: 'wu_night', requires: { times: ['night'], locations: ['north_ward'], activities: ['盖着被子核对数字'] } },
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
        { kind: 'npc', speaker: '吴桐', text: '“那张纸别碰，我自己会收。”她把今天这一行重新描了一遍，日期、时间和步数之间留着同样宽的空格。' },
        { kind: 'experience', source: '经历 · 被家人管过身体', text: '你认得那种语法：别人说“为你好”，真正被收走的是最后一点决定权。', requires: { experiencesAny: ['body-policed'] } },
        { kind: 'disease', form: 'belief', source: '神经性厌食症 · 信念式', text: '她纸上的数字没有错。数字不会骗你。', requires: { diseasesAny: ['神经性厌食症'] } },
      ],
      options: [
        { id: 'numbers', text: '“你为什么把每次称重都记下来？”', meta: '从数字谈起', next: 'wu_numbers', effects: { flagsAdd: ['talked_wu'], relationDelta: 1 } },
        { id: 'food', text: '“这张表里为什么没有午饭？”', meta: '从纸面缺失而不是诊断发问', next: 'wu_food' },
        { id: 'mirror', text: '“那面镜子为什么不能收走？”', meta: '询问她每天确认的东西', next: 'wu_mirror' },
      ],
    },
    wu_numbers: {
      id: 'wu_numbers',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“称重时间不一样，数字就不能比。衣服、喝水、有没有走动，都得写。”她用指甲盖压住纸角，“不写的话，这一天像是没对齐。”' }],
      options: [
        { id: 'back', text: '不去碰她那张纸，换一个话题。', meta: '继续初识层对话', next: 'wu_surface' },
        { id: 'leave', text: '先让她把这一行写完。', meta: '结束会话', end: true },
      ],
    },
    wu_mother: {
      id: 'wu_mother',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我妈第一次说我脸圆的时候，还觉得是在提醒我。”她把纸压在膝下，“她连爱人都像在排课表。几点睡、学什么、以后做什么，一项都不能空。”' }],
      options: [
        { id: 'back', text: '“所以你给自己留了一项空白。”', meta: '继续熟悉层对话', next: 'wu_familiar' },
        { id: 'leave', text: '让她把纸重新压平。', meta: '结束会话', end: true },
      ],
    },
    wu_food: {
      id: 'wu_food',
      blocks: [
        { kind: 'npc', speaker: '吴桐', text: '“有些东西不用写。”她把纸折过去一寸，刚好遮住最下面一行，“你来找我，就是为了核账？”' },
        { kind: 'disease', form: 'intrusion', source: '躯体症状障碍 · 闯入式', text: '她的指甲发白。手腕的脉搏太慢。身体先把答案说了。', requires: { diseasesAny: ['躯体症状障碍'] } },
      ],
      options: [
        { id: 'treatment', text: '“你说的‘配合’，包括吃饭吗？”', meta: '指出她话里的边界', next: 'wu_treatment' },
        { id: 'leave', text: '不继续逼问。', meta: '结束会话', end: true },
      ],
    },
    wu_treatment: {
      id: 'wu_treatment',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我自己签字转到这里，药也按时吃。”她把袖口又折了一遍，“住院是我同意的。吃多少、称重时穿什么，是另一回事。”' }],
      options: [
        { id: 'back', text: '不把“愿意治疗”误听成“交出所有决定”。', meta: '继续初识层对话', next: 'wu_surface' },
        { id: 'leave', text: '先停在她划出的边界外。', meta: '结束会话', end: true },
      ],
    },
    wu_mirror: {
      id: 'wu_mirror',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“护士说我太瘦。我知道。”她把镜面扣向床单，“可一天不看，我就不知道自己是不是已经变回去了。”' }],
      options: [
        { id: 'back', text: '不替镜子回答，换一个话题。', meta: '继续初识层对话', next: 'wu_surface' },
        { id: 'leave', text: '让镜面继续扣在床单上。', meta: '结束会话', end: true },
      ],
    },
    wu_familiar: {
      id: 'wu_familiar',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“他们总问我为什么不吃。没人问过，如果连这个也不由我，我还剩什么。”' }],
      options: [
        { id: 'control', text: '“也许要留下的不是数字，是决定权。”', meta: '谈控制而不是食物', next: 'wu_control', effects: { flagsAdd: ['wu_control'], relationDelta: 1 } },
        { id: 'mother', text: '“这些表格最早是谁替你排好的？”', meta: '关系建立后才问控制的来路', next: 'wu_mother' },
        { id: 'father', text: '“家里有没有人问过你累不累？”', meta: '问起那个不擅长说话的人', next: 'wu_father' },
        { id: 'door', text: '“你母亲探视时为什么站在门外？”', meta: '留意她第一次没有直接推门', next: 'wu_door' },
      ],
    },
    wu_father: {
      id: 'wu_father',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我爸说过，平平安安，别太累。我当时觉得那是没出息的人才说的话。”她笑了一下，“他现在每天只回我一句：好，明天吃一碗。”' }],
      options: [{ id: 'back', text: '“至少那句话没有要求你优秀。”', meta: '继续熟悉层对话', next: 'wu_familiar' }],
    },
    wu_door: {
      id: 'wu_door',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“她以前进我房间从不敲门。”吴桐望向病区门口，“那天她站了半小时。她可能终于发现，有些地方不能替我跨进来。”' }],
      options: [{ id: 'back', text: '让那扇门先留着。', meta: '继续熟悉层对话', next: 'wu_familiar' }],
    },
    wu_control: {
      id: 'wu_control',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '她看了你很久。“这句话比‘你应该多吃’好一点。只好一点。”' }],
      options: [
        { id: 'back', text: '“一点就够了。”', meta: '继续熟悉层对话', next: 'wu_familiar' },
        { id: 'leave', text: '把剩下的话留到下次。', meta: '结束会话', end: true },
      ],
    },
    wu_core: {
      id: 'wu_core',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“我爸以前只希望我别太累。我那时觉得他没出息。”她把数字纸折起来，“现在想想，那可能是家里唯一一句没要求我变好的话。”' }],
      options: [
        { id: 'message', text: '“你今天准备怎么回他？”', meta: '问起父女每天一次的短信', next: 'wu_message' },
        { id: 'leave', text: '陪她坐一会儿。', meta: '结束深入对话', end: true },
      ],
    },
    wu_message: {
      id: 'wu_message',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '她在手机上打了很久，最后仍只有一行：“爸，今天吃了半碗饭。”发送以后，她没有立刻去改那张数字纸。' }],
      options: [{ id: 'leave', text: '等屏幕亮起父亲的回复。', meta: '结束深入对话', end: true }],
    },
    wu_court: {
      id: 'wu_court', objective: '在不接管她的计数时，弄清这条白线对她意味着什么。',
      blocks: [
        { kind: 'description', text: '下午的橡胶地面晒出一股旧轮胎味。篮网被风压在铁圈上，塑料绳一下、一下刮着漆面。吴桐沿最外侧白线走，到篮架下转身，再原路回来。' },
        { kind: 'description', text: '一只没人追的篮球从器材室门边滚出来。它还远，照这个方向，迟早会横过她的路线。' },
        { kind: 'npc', speaker: '吴桐', text: '第三次经过你时，她抬了抬下巴。“要过去就走里面。别挡线。”脚步没有停。' },
        { kind: 'experience', source: '经历 · 做过要称重的活', text: '她每次都在同一条裂缝前换脚。你见过计件的人这样保护节奏——但球场没有工头，也没有人在终点记数。', requires: { experiencesAny: ['weighed-work'] } },
        { kind: 'experience', source: '经历 · 长期挨过饿', text: '转身时，她的右脚拖了半寸。饥饿会让身体先学会节省，也可能只是鞋底开了胶。别急着让自己的胃替她作证。', requires: { experiencesAny: ['hunger'] } },
        { kind: 'disease', form: 'belief', source: '神经性厌食症 · 信念式', text: '白线不是白线，是今天还没有结清的账。替她数。至少数字不会误解好意。', requires: { diseasesAny: ['神经性厌食症'] } },
      ],
      options: [
        { id: 'count', text: '“走外圈，一圈是多少步？”', meta: '说话 · 进入她正在使用的计量方式', next: 'wu_court_count' },
        { id: 'parallel', text: '走到白线内侧，和她朝同一个方向走。', meta: '行动 · 接近她，但不占她的路线', next: 'wu_court_parallel' },
        { id: 'foot', text: '“你右脚刚才拖了一下。”', meta: '观察 · 直接指出身体泄露的细节', next: 'wu_court_foot' },
        { id: 'wait', text: '什么也不说。看那只球慢慢滚向白线。', meta: '沉默 · 让环境先打断计数', next: 'wu_court_ball' },
      ],
    },
    wu_court_count: {
      id: 'wu_court_count',
      blocks: [
        { kind: 'npc', speaker: '吴桐', text: '“外圈二百四十六。贴线二百四十二。”她回答得太快，像这句话一直含在嘴里。“下午人少，误差小。”' },
        { kind: 'npc', speaker: '吴桐', text: '她又走出三步。“别替我数。多一个人的脚步，数就不是我的了。”' },
      ],
      options: [
        { id: 'mine', text: '“我不数你的。我数我自己的。”', meta: '装作彼此可以拥有两套互不干涉的数字', next: 'wu_court_parallel' },
        { id: 'wrong', text: '“可我刚才数到的是二百四十三。”', meta: '冒犯 · 用一个数字碰她的数字', next: 'wu_court_correction' },
        { id: 'inside', text: '退到白线内侧，不再替她计算。', meta: '行动 · 接受她划出的边界', next: 'wu_court_ball' },
      ],
    },
    wu_court_parallel: {
      id: 'wu_court_parallel',
      blocks: [
        { kind: 'description', text: '你走在线内。她走在线外。最初几步互不相干，过了篮架，你们的鞋底声还是叠到了一起。' },
        { kind: 'npc', speaker: '吴桐', text: '“别跟我同速。”她慢下来半步，等你超过去。“你一快一慢，我得把你的声音从里面减掉。”' },
      ],
      options: [
        { id: 'slow', text: '再慢一点，让两组脚步彻底错开。', meta: '行动 · 不要求她解释', next: 'wu_court_ball' },
        { id: 'claim', text: '“脚步声在我这边。怎么也算进你的数里？”', meta: '追问她划定数字所有权的方式', next: 'wu_court_ownership' },
      ],
    },
    wu_court_ownership: {
      id: 'wu_court_ownership',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“因为我听见了。”她皱起眉，像你故意把一件简单的事说复杂了。“听见以后还假装没有，那才叫算错。”' }],
      options: [{ id: 'yield', text: '不争论谁拥有这阵脚步声。', meta: '沉默 · 让那只球继续靠近', next: 'wu_court_ball' }],
    },
    wu_court_correction: {
      id: 'wu_court_correction',
      blocks: [
        { kind: 'npc', speaker: '吴桐', text: '她停下。不是累，是把刚才那一圈从头到尾翻了一遍。“你在哪里开始数的？”' },
        { kind: 'description', text: '那只篮球还在滚。她没有看它。' },
      ],
      options: [
        { id: 'admit', text: '“不知道。我只是想看你会不会停。”', meta: '承认自己在试探她', next: 'wu_court_ball' },
        { id: 'retreat', text: '“那就是我数错了。”', meta: '收回没有根据的确定', next: 'wu_court_ball' },
      ],
    },
    wu_court_foot: {
      id: 'wu_court_foot',
      blocks: [
        { kind: 'npc', speaker: '吴桐', text: '“鞋底开胶了。”她仍在走，右脚落地时却更轻了。“你们是不是看见什么都要记？”' },
        { kind: 'experience', source: '经历 · 自己得过重病', text: '人会拿一个小故障替身体挡枪：鞋、床、天气、昨晚没睡。你以前也这样做过。那不等于她正在撒谎。', requires: { experiencesAny: ['major-illness'] } },
      ],
      options: [
        { id: 'shoe', text: '低头看她的鞋底，不去看她的脸。', meta: '行动 · 接受她给出的表面解释', next: 'wu_court_shoe' },
        { id: 'apologize', text: '“对不起。我不该把每一步都当成证据。”', meta: '承认观察也可能是一种侵入', next: 'wu_court_ball' },
      ],
    },
    wu_court_shoe: {
      id: 'wu_court_shoe',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '“别蹲这儿。”她终于侧身绕了你半步，“你比开胶更挡路。”' }],
      options: [{ id: 'stand', text: '站回线内。', meta: '行动 · 把路线还给她', next: 'wu_court_ball' }],
    },
    wu_court_ball: {
      id: 'wu_court_ball',
      blocks: [
        { kind: 'description', text: '篮球撞上一粒石子，偏了半掌宽，仍旧慢慢滚向白线。橡胶擦过地面的声音比脚步更粗。' },
        { kind: 'npc', speaker: '吴桐', text: '吴桐停在离球两步远的地方。“谁的球？”球场上没有人回答。' },
      ],
      options: [
        { id: 'stop', text: '用鞋底按住球，停在线外。', meta: '行动 · 替她保住这一圈', next: 'wu_court_stop' },
        { id: 'cross', text: '不碰它。让球横过白线。', meta: '沉默 · 不替她维持秩序', next: 'wu_court_cross' },
        { id: 'return', text: '把球踢回器材室门边。', meta: '行动 · 快速处理这个麻烦', next: 'wu_court_return' },
      ],
    },
    wu_court_stop: {
      id: 'wu_court_stop',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '她从球旁走过，数到下一步才说：“别一直踩着。等会儿真有人要打球。”这一次，她没有让你走开。' }],
      options: [{ id: 'finish', text: '等她越过下一条裂缝，再松开球。', meta: '完成这一小段共同处理', next: 'wu_court_finish' }],
    },
    wu_court_cross: {
      id: 'wu_court_cross',
      blocks: [{ kind: 'npc', speaker: '吴桐', text: '球从她面前滚过去。她看着它穿过白线，又滚进场内。“行了。”她转身走回篮架下，“这一圈不算。”' }],
      options: [{ id: 'finish', text: '站在线内，等她从第一步重新开始。', meta: '接受一次没有完成的计数', next: 'wu_court_finish' }],
    },
    wu_court_return: {
      id: 'wu_court_return',
      blocks: [{ kind: 'description', text: '球撞上门框，又弹回来半米。吴桐看了看球，再看你。她鼻子里短短地出了一口气；可能是笑，也可能只是嫌你脚法差。' }],
      options: [{ id: 'finish', text: '把球捡起来放好。这次不用脚。', meta: '承认刚才的处理并不高明', next: 'wu_court_finish' }],
    },
    wu_court_finish: {
      id: 'wu_court_finish',
      blocks: [
        { kind: 'description', text: '风又把篮网压回铁圈。一下、一下。吴桐重新起步，鞋底声从那个节拍旁边穿过去。' },
        { kind: 'npc', speaker: '吴桐', text: '“你要待着就待里面。”她说，“别突然跟上来。”' },
      ],
      options: [
        { id: 'bench', text: '坐到长椅上，不替她数。', meta: '结束场边交谈 · 她允许你留下', end: true, effects: { flagsAdd: ['talked_wu'], relationDelta: 1 } },
        { id: 'leave', text: '从场地内侧离开。', meta: '结束场边交谈 · 不要求一个结论', end: true, effects: { flagsAdd: ['talked_wu'] } },
      ],
    },
    wu_night: {
      id: 'wu_night', objective: '在夜间病房里辨认数字之外的身体信号。',
      blocks: [
        { kind: 'description', text: '北病房的暖气管很热。吴桐仍盖着两层被子，只把一只手伸出来，在纸上改写白天的步数。镜子被扣在床单上。' },
        { kind: 'experience', source: '经历 · 被家人或伴侣管过身体', text: '被子、镜子和数字都摆成一道边界。你知道贸然掀开任何一样，都会像替别人接管她的身体。', requires: { experiencesAny: ['body-policed'] } },
        { kind: 'experience', source: '经历 · 自己得过重病', text: '她指甲发白，写到行尾时手指轻轻发抖。身体正在说话，只是她没有给它留一栏。', requires: { experiencesAny: ['major-illness'] } },
      ],
      options: [
        { id: 'cold', text: '“要不要把窗缝挡一下？”', meta: '处理环境，不评价她的身体', end: true, effects: { relationDelta: 1 } },
        { id: 'mirror', text: '“镜子今晚为什么扣着？”', meta: '询问她主动停止的一次检查', next: 'wu_mirror' },
      ],
    },
  },
}
