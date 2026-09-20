// 来源：design/spec/material/drafts/郑晓敏-叙事视图.md §六、§八、§十四。
export const zhengXiaomin = {
  id: 'zheng_xiaomin', name: '郑晓敏', role: '住院楼一层 · 白班护士', mark: '郑',
  description: '她先看治疗盘上的数字，再抬头看你。',
  objective: '从白班记录里确认自己昨夜做过什么。',
  dossier: [
    { id: 'identity', label: '身份', text: '郑晓敏，住院楼一层白班护士。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '她先看治疗盘上的数字，再抬头看你。', source: '当面观察', requires: { met: true } },
    { id: 'good-days', label: '非正式记录', text: '她另用一本“好日子本”记录正式病历之外的变化。', source: '当面交谈', requires: { allFlags: ['seen_good_days'] } },
    { id: 'handover', label: '交接本', text: '她让你看过夜班交接本，其中把昨夜异常写成“全部平稳”。', source: '院内记录', requires: { allFlags: ['seen_handover'] } },
  ],
  situations: [
    { node: 'zheng_rounds', requires: { times: ['afternoon'], locations: ['south_ward'], activities: ['发药并擦门把手'] } },
  ],
  levels: [
    { id: 'surface', label: '初识', entry: 'zheng_surface' },
    { id: 'familiar', label: '熟悉', entry: 'zheng_familiar', requires: { allFlags: ['seen_good_days', 'seen_handover'] } },
    { id: 'core', label: '深入', entry: 'zheng_core', requires: { minRelation: 2, anyFlags: ['talked_wu', 'talked_zhou', 'talked_tang'] } },
  ],
  nodes: {
    zheng_surface: {
      id: 'zheng_surface', objective: '认识白班护士，并找到能跨过夜晚的记录。',
      blocks: [
        { kind: 'description', text: '郑晓敏端着治疗盘走进来。她的白大褂第三颗扣子扣得很紧，内袋里露出一本塑料封皮的小本子。' },
        { kind: 'npc', speaker: '郑晓敏', text: '“醒了？我是这层的护士，郑晓敏。先量体温，手伸出来。”' },
        { kind: 'experience', source: '经历 · 长期上夜班、三班倒', text: '你认得这种交班后的停顿：她正在努力让白天接住一个已经断掉的夜晚。', requires: { experiencesAny: ['night-shifts'] } },
        { kind: 'disease', form: 'belief', source: '广泛性焦虑障碍 · 信念式', text: '等一下。她说“夜间入院”时看了一眼记录。一定有什么地方没有对上。', requires: { diseasesAny: ['广泛性焦虑障碍'] } },
      ],
      options: [
        { id: 'good_days', text: '“你内袋里的本子记了什么？”', meta: '询问非正式记录', next: 'zheng_good_days', effects: { flagsAdd: ['seen_good_days'], relationDelta: 1, notes: [{ id: 'good_days', text: '郑晓敏用好日子本记录正式病历之外的变化。', source: '郑晓敏' }] } },
        { id: 'handover', text: '“昨夜的交接本在哪里？”', meta: '核对正式夜班记录', next: 'zheng_handover', effects: { flagsAdd: ['seen_handover'], notes: [{ id: 'handover', text: '交接本把昨夜的异常归入“全部平稳”。', source: '谭丽娟' }] } },
        { id: 'admission', text: '“我怎么进来的？”', meta: '询问入院程序', next: 'zheng_admission' },
        { id: 'names', text: '“你为什么不叫他们床号？”', meta: '留意她对患者的称呼', next: 'zheng_names' },
        { id: 'shoes', text: '“你走路怎么一点声音都没有？”', meta: '询问她的软底布鞋', next: 'zheng_shoes' },
        { id: 'handles', text: '“门把手每天都要擦吗？”', meta: '询问一件规程之外的小事', next: 'zheng_handles' },
      ],
    },
    zheng_good_days: {
      id: 'zheng_good_days',
      blocks: [
        { kind: 'player', text: '“你内袋里的本子记了什么？”' },
        { kind: 'npc', speaker: '郑晓敏', text: '“……记谁好了一点。”她把本子翻到昨夜那页，“这行是我的字。你自己走到护士站，又自己回了病房。可我想不起写的时候发生过什么。”' },
        { kind: 'disease', form: 'belief', source: '强迫症 · 信念式', text: '再确认一次。字迹、页码、时间、前后两行。只要全部对上，记忆缺失就不能把它变成没发生。', requires: { diseasesAny: ['强迫症'] } },
      ],
      options: [
        { id: 'back', text: '继续问她。', meta: '返回当前对话层', next: 'zheng_surface' },
        { id: 'leave', text: '先去看看别处。', meta: '结束会话', end: true },
      ],
    },
    zheng_handover: {
      id: 'zheng_handover',
      blocks: [
        { kind: 'player', text: '“昨夜的交接本在哪里？”' },
        { kind: 'npc', speaker: '郑晓敏', text: '她把台面上的大本子推过来。“夜班是谭丽娟。两点十七分：已劝回病房。最后还是她那四个字——全部平稳。”' },
        { kind: 'experience', source: '经历 · 长期做核对类工作', text: '日期、床号、时间、签名都对。真正刺眼的是：如此完整的记录，没有一个人能复述它。', requires: { experiencesAny: ['checking-work'] } },
      ],
      options: [
        { id: 'back', text: '继续问她。', meta: '返回当前对话层', next: 'zheng_surface' },
        { id: 'leave', text: '合上交接本。', meta: '结束会话', end: true },
      ],
    },
    zheng_admission: {
      id: 'zheng_admission',
      blocks: [
        { kind: 'player', text: '“我怎么进来的？”' },
        { kind: 'npc', speaker: '郑晓敏', text: '“病历写的是夜间入院。送你来的人签了字。我不能念给你听；想知道得去病案室。”她停了一下，“不过有些入院记录，不该空的地方是空的。”' },
      ],
      options: [{ id: 'back', text: '问别的问题。', meta: '返回当前对话层', next: 'zheng_surface' }],
    },
    zheng_names: {
      id: 'zheng_names',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '“记录里才写床号。”她朝活动室看了一眼，“周师傅会修东西，小姑娘怕冷，春兰姐吃饭慢。他们又不叫七、十一、九。”' }],
      options: [{ id: 'back', text: '“那你叫我什么？”', meta: '她先记住人，再填写表格', next: 'zheng_surface' }],
    },
    zheng_shoes: {
      id: 'zheng_shoes',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '她低头看了看软底布鞋。“有人半夜听见脚步会醒。换双鞋的事，不用等护士长开会。”' }],
      options: [{ id: 'back', text: '把声音放轻一点。', meta: '继续当前会话', next: 'zheng_surface' }],
    },
    zheng_handles: {
      id: 'zheng_handles',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '“没人要求。”她把抹布折成四方，“有人握住干净的门把手，手会松一点。我看见了，就顺手擦。”' }],
      options: [{ id: 'back', text: '“这种事也会写进好日子本吗？”', meta: '继续当前会话', next: 'zheng_surface' }],
    },
    zheng_familiar: {
      id: 'zheng_familiar', objective: '决定是否把两份互相咬合的记录带进夜晚核对。',
      blocks: [
        { kind: 'description', text: '你已经看过两本记录。郑晓敏不再把小本子往内袋里藏。' },
        { kind: 'npc', speaker: '郑晓敏', text: '“正式记录写病情，我那个记日子。现在两本都说你去过护士站——只有我们谁都想不起来。”' },
      ],
      options: [
        { id: 'why_work', text: '“你为什么还记那本没有人要求的本子？”', meta: '进入她自己的问题', next: 'zheng_why_work', effects: { relationDelta: 1 } },
        { id: 'missing_tool', text: '“护士站是不是少过一把改锥？”', meta: '核对周卫国手里的工具', next: 'zheng_missing_tool', requires: { allFlags: ['zhou_tool'] } },
        { id: 'scissors', text: '“唐念安那把剪刀，是你收走的吗？”', meta: '询问危险物品登记', next: 'zheng_scissors', requires: { allFlags: ['talked_tang'] } },
        { id: 'night', text: '休息到夜晚，亲自核对。', meta: '推进到夜晚', end: true, effects: { time: 'night', flagsAdd: ['entered_night'] } },
      ],
    },
    zheng_why_work: {
      id: 'zheng_why_work',
      blocks: [
        { kind: 'npc', speaker: '郑晓敏', text: '“我不是来救谁的。我就是来上班的。”她扣好第三颗扣子，“可这地方不让人只是来上班。”' },
      ],
      options: [{ id: 'leave', text: '让她继续交班。', meta: '关系已经改变', end: true }],
    },
    zheng_missing_tool: {
      id: 'zheng_missing_tool',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '她清点治疗车时少停了半秒。“工具一件待核。我后来补上了。”你问是谁拿的，她把笔帽扣好：“本子里没写，就是不打算补名字。”' }],
      options: [{ id: 'leave', text: '不逼她把人写回记录。', meta: '结束会话', end: true }],
    },
    zheng_scissors: {
      id: 'zheng_scissors',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '“报纸包了两层，拿在手里却很轻。”她摸出钥匙，“登记、上锁、用完收回。规矩能锁住剪刀，锁不住她怕自己这件事。”' }],
      options: [{ id: 'leave', text: '听见钥匙在她掌心碰了一下。', meta: '结束会话', end: true }],
    },
    zheng_rounds: {
      id: 'zheng_rounds', objective: '跟着她的下午工作观察病房，而不是要求她解释每个人。',
      blocks: [
        { kind: 'description', text: '郑晓敏推着发药车停在半开的门外。她先把门把手擦干净，才用指节轻轻敲门。药片的苦味从纸杯里浮起来。' },
        { kind: 'npc', speaker: '郑晓敏', text: '“先别进去。她刚睡着。药晚五分钟没事，门一响又得重来。”' },
        { kind: 'experience', source: '经历 · 长期照护卧床的人', text: '你认得这种停顿：照护不是把流程做完，是知道什么时候不该把人叫醒。', requires: { experiencesAny: ['long-care'] } },
        { kind: 'experience', source: '经历 · 长期做核对类工作', text: '发药车每个抽屉都朝同一方向合上，唯独她手里的名单折了一个角——那一床被她暂时跳过。', requires: { experiencesAny: ['checking-work'] } },
      ],
      options: [
        { id: 'door', text: '“你每扇门都先擦一下？”', meta: '从她正在做的动作问起', next: 'zheng_rounds_handles' },
        { id: 'wait', text: '和她一起在门外等五分钟。', meta: '不把照护变成盘问', end: true, effects: { relationDelta: 1 } },
      ],
    },
    zheng_rounds_handles: {
      id: 'zheng_rounds_handles',
      blocks: [{ kind: 'npc', speaker: '郑晓敏', text: '“有人抓住干净的门把手，手会松一点。”她把抹布折到没用过的一面，“不是规定。我看见了，就做。”' }],
      options: [{ id: 'leave', text: '替她扶住发药车。', meta: '结束这段走廊交谈', end: true, effects: { relationDelta: 1 } }],
    },
    zheng_core: {
      id: 'zheng_core', objective: '理解记录如何把一个人压缩成病情。',
      blocks: [
        { kind: 'npc', speaker: '郑晓敏', text: '“正式记录上只有病情，没有人。”她看了眼你从病房带回来的线索，“所以我才记谁好了一点。有人总得记点别的。”' },
      ],
      options: [{ id: 'leave', text: '“我会继续看。”', meta: '结束深入对话', end: true }],
    },
  },
}
