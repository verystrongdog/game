// 来源：design/spec/material/drafts/唐念安-叙事视图.md §七—§十。
export const tangNianan = {
  id: 'tang_nianan', name: '唐念安', role: 'B2 女区 · 探视电话旁', mark: '唐',
  description: '她放下听筒后又检查了一次电话线，床头立着一张婴儿照片。',
  objective: '听完电话里那段录音，看看她接下来做什么。',
  dossier: [
    { id: 'identity', label: '身份', text: '唐念安，B2 女区患者。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '她反复确认探视电话和电话线，床头柜上放着女儿的照片。', source: '当面观察', requires: { met: true } },
    { id: 'reason', label: '她的说法', text: '她害怕不请自来的伤害念头，把它们与自己的真实意图混在一起。', source: '当面交谈', requires: { minRelation: 1, allFlags: ['talked_tang'] } },
    { id: 'mother', label: '关系进展', text: '她开始接受“不需要完美，才能继续做母亲”。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['tang_not_monster'] } },
  ],
  situations: [
    { node: 'tang_activity_room', requires: { times: ['afternoon'], locations: ['activity_room'], activities: ['织一件小毛衣'] } },
    { node: 'tang_night', requires: { times: ['night'], locations: ['south_ward'], activities: ['在床边读小说'] } },
  ],
  levels: [
    { id: 'surface', label: '初识', entry: 'tang_surface' },
    { id: 'familiar', label: '熟悉', entry: 'tang_familiar', requires: { minRelation: 1, allFlags: ['talked_tang'] } },
    { id: 'core', label: '深入', entry: 'tang_core', requires: { minRelation: 2, allFlags: ['tang_not_monster'] } },
  ],
  nodes: {
    tang_surface: {
      id: 'tang_surface',
      blocks: [
        { kind: 'description', text: '唐念安把听筒放回电话机，又确认了一次没有压到电话线。床头柜上放着女儿的照片。' },
        { kind: 'npc', speaker: '唐念安', text: '“她今天会叫妈妈了。不是对着我叫的，但我丈夫录下来了。”' },
        { kind: 'experience', source: '经历 · 家里规矩极多，错一点就罚', text: '你听见的不是“想做得好”，而是“任何差错都不被允许存在”。', requires: { experiencesAny: ['strict-home'] } },
        { kind: 'disease', form: 'belief', source: '强迫症 · 信念式', text: '再确认一次就好。你知道确认不会结束，但这一次也许会。', requires: { diseasesAny: ['强迫症'] } },
      ],
      options: [
        { id: 'photo', text: '“照片里是安安？”', meta: '从女儿谈起', next: 'tang_photo' },
        { id: 'phone', text: '“刚才电话里放的是她的声音？”', meta: '询问丈夫带来的录音', next: 'tang_phone', effects: { flagsAdd: ['talked_tang'], relationDelta: 1 } },
        { id: 'line', text: '把压在听筒下面的电话线理顺。', meta: '回应她正在反复确认的动作', end: true },
      ],
    },
    tang_reason: {
      id: 'tang_reason',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我老怕自己伤害女儿。不是想，是怕。拿剪刀、给她洗澡、走到窗边……越怕，念头越来。”' }],
      options: [
        { id: 'counting', text: '“害怕的时候，你会做什么？”', meta: '让她描述检查与数数', next: 'tang_counting' },
        { id: 'leave', text: '“你可以停在这里。”', meta: '结束会话', end: true },
      ],
    },
    tang_counting: {
      id: 'tang_counting',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“摸鼻息，查门窗，关灯数三下。洗手要数到三十。”她看着自己的手，“每做完一次，只安静一会儿。然后‘万一’又回来。”' }],
      options: [
        { id: 'back', text: '不请她再数一遍，等她自己换个话题。', meta: '继续熟悉层对话', next: 'tang_familiar' },
        { id: 'leave', text: '让这一次确认停在三十。', meta: '结束会话', end: true },
      ],
    },
    tang_photo: {
      id: 'tang_photo',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“嗯，十一个月。”她把照片扶正，又退开一点看，“照片好整理。真的她在面前，一秒钟一个样，我总怕漏掉什么。”' }],
      options: [
        { id: 'back', text: '把照片放回原处，继续坐一会儿。', meta: '继续初识层对话', next: 'tang_surface' },
        { id: 'leave', text: '让照片停在她摆正的位置。', meta: '结束会话', end: true },
      ],
    },
    tang_phone: {
      id: 'tang_phone',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“她对着奶奶叫妈妈。唐明怕我吃醋，特地录下来。”她笑了一下，“隔着电话听，反而不用确认她有没有呼吸。”' }],
      options: [
        { id: 'back', text: '让录音停下，再换一个话题。', meta: '继续初识层对话', next: 'tang_surface' },
        { id: 'leave', text: '让录音停在那一声“妈妈”。', meta: '结束会话', end: true },
      ],
    },
    tang_scissors: {
      id: 'tang_scissors',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“上午包一层，下午觉得不够，又包一层。晚上还是想爬起来看看。”她把手压在膝上，“后来护士收走了。我轻松了一会儿，又开始怕窗户。”' }],
      options: [
        { id: 'back', text: '“所以危险不会被一把锁用完。”', meta: '继续熟悉层对话', next: 'tang_familiar' },
        { id: 'leave', text: '不再列举下一件可能危险的东西。', meta: '结束会话', end: true },
      ],
    },
    tang_recognized: {
      id: 'tang_recognized',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '她看着你，先是警惕，然后慢慢松开手。“你也知道那种念头？”' }],
      options: [
        { id: 'back', text: '“知道它会冒充你。”', meta: '继续熟悉层对话', next: 'tang_familiar' },
        { id: 'leave', text: '不要求她立刻相信这句话。', meta: '结束会话', end: true },
      ],
    },
    tang_familiar: {
      id: 'tang_familiar',
      blocks: [
        { kind: 'description', text: '唐念安放下电话后又摸了一次听筒底座。她发现你看见了，手停在半空，没有立刻解释。' },
        { kind: 'npc', speaker: '唐念安', text: '“我知道刚才已经放好了。”她把手收回来，“知道，跟能不能不再确认，是两回事。”' },
        { kind: 'disease', form: 'belief', source: '强迫症 · 信念式', text: '你认得确认之后那一小段安静，也认得安静结束时，怀疑会怎样假装成新的证据。', requires: { diseasesAny: ['强迫症'] } },
      ],
      options: [
        { id: 'why_here', text: '“你每天到底在防什么？”', meta: '建立关系后才允许她选择说到哪里', next: 'tang_reason' },
        { id: 'not_monster', text: '“你不需要完美，才能继续做她妈妈。”', meta: '回应她真正害怕的判断', next: 'tang_answer', effects: { flagsAdd: ['tang_not_monster'], relationDelta: 1 } },
        { id: 'scissors', text: '“护士站登记里有一把包了两层报纸的剪刀。”', meta: '有物证后询问，不凭空逼问', next: 'tang_scissors' },
        { id: 'ocd_answer', text: '“念头不是意图。害怕它，恰好说明你不想那样做。”', meta: '强迫症打开的说法', next: 'tang_recognized', requires: { diseasesAny: ['强迫症'] }, effects: { flagsAdd: ['tang_not_monster'], relationDelta: 1 } },
        { id: 'work', text: '“你以前也要求自己什么都不能出错？”', meta: '从广告工作谈完美标准', next: 'tang_work' },
        { id: 'husband', text: '“唐明第一次听见这些时说了什么？”', meta: '询问那个没有追问的人', next: 'tang_husband' },
      ],
    },
    tang_work: {
      id: 'tang_work',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“广告稿一个图标偏半格，我能改到凌晨三点。”她摇摇头，“后来我把做妈妈也当成一份不能有错字的稿子。可孩子不是提案。”' }],
      options: [{ id: 'back', text: '“也没有甲方给母亲定稿。”', meta: '继续熟悉层对话', next: 'tang_familiar' }],
    },
    tang_husband: {
      id: 'tang_husband',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我说心里不舒服，想去医院。他只说好，请假带安安。”她摸了摸照片边缘，“后来我问他怕不怕我。他说，有病就治，我陪你。”' }],
      options: [{ id: 'back', text: '让这句普通的话多停一会儿。', meta: '继续熟悉层对话', next: 'tang_familiar' }],
    },
    tang_answer: {
      id: 'tang_answer',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我丈夫也这么说。”她擦了一下眼角，“两个人都这么说，可能……值得先信一次。”' }],
      options: [{ id: 'leave', text: '让这句话停在这里。', meta: '结束会话', end: true }],
    },
    tang_core: {
      id: 'tang_core',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“安安需要的是一直在的人，不是脑子里从来没有坏念头的人。”她把女儿的照片立正，“这句话我还得多说几遍。”' }],
      options: [
        { id: 'novel', text: '“今天不练习做妈妈的时候，你想做什么？”', meta: '问她作为母亲之外的时间', next: 'tang_novel' },
        { id: 'leave', text: '“慢慢说。”', meta: '结束深入对话', end: true },
      ],
    },
    tang_novel: {
      id: 'tang_novel',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“看小说。不是育儿书，也不是病例。”她把书签夹回去，“以前总觉得闲书浪费时间。现在我想浪费一点。”' }],
      options: [{ id: 'leave', text: '“那就先浪费这一下午。”', meta: '结束深入对话', end: true }],
    },
    tang_activity_room: {
      id: 'tang_activity_room', objective: '从一件做给女儿的小东西认识她，而不是从病历认识她。',
      blocks: [
        { kind: 'description', text: '唐念安坐在活动室窗边织一件很小的毛衣。针脚从第三排开始忽然变密，她已经拆过那一段，毛线仍留着弯曲的记忆。' },
        { kind: 'npc', speaker: '唐念安', text: '“先别夸，还没织完。”她数到针尾，又从头数了一遍，“小孩子长得快，做大一点也不算浪费。”' },
        { kind: 'experience', source: '经历 · 家里规矩极多，错一点就罚', text: '她不是在确认毛衣能不能穿，而是在确认自己有没有资格把一个小错误留下。', requires: { experiencesAny: ['strict-home'] } },
        { kind: 'experience', source: '经历 · 长期做核对类工作', text: '第三排的针数已经对了。真正让她拆掉的，是那一针看起来和旁边不完全一样。', requires: { experiencesAny: ['checking-work'] } },
      ],
      options: [
        { id: 'size', text: '“大一点，她可以多穿一个月。”', meta: '允许成品不必刚好', next: 'tang_sweater' },
        { id: 'learn', text: '“谁教你织的？”', meta: '谈病房里的日常关系', end: true, effects: { flagsAdd: ['talked_tang'], relationDelta: 1 } },
      ],
    },
    tang_sweater: {
      id: 'tang_sweater',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“杨阿姨也这么说。”她没有再拆第三排，只在袖口多留了一截毛线，“那就让它大一点。”' }],
      options: [{ id: 'leave', text: '帮她把滚到桌下的毛线团捡回来。', meta: '结束活动室交谈', end: true, effects: { flagsAdd: ['talked_tang'], relationDelta: 1 } }],
    },
    tang_night: {
      id: 'tang_night', objective: '看见她在母亲身份之外怎样度过一段时间。',
      blocks: [
        { kind: 'description', text: '南病房的灯从门下漏进来。唐念安读的是一本翻旧的小说，不是育儿书。翻到窗户被风推开的段落时，她把书合上，起身确认了一次窗扣。' },
        { kind: 'npc', speaker: '唐念安', text: '“这页明天再看。”她回到床边，却没有再走向窗户。' },
        { kind: 'experience', source: '经历 · 家里有病人，随时待命', text: '你知道照护者很难把注意力从“会不会出事”上拿开。她能重新坐下，本身就是今晚发生的一件事。', requires: { experiencesAny: ['family-patient'] } },
        { kind: 'experience', source: '经历 · 长期扮演懂事角色', text: '她把害怕处理得安静、整齐，不给同屋添麻烦。你认得这种把求助包装成“我自己来”的方式。', requires: { experiencesAny: ['good-child-role'] } },
      ],
      options: [
        { id: 'book', text: '“读到哪儿了？”', meta: '谈一本与疾病无关的书', next: 'tang_novel' },
        { id: 'window', text: '不再替她检查窗扣。', meta: '让已经完成的动作保持完成', end: true, effects: { relationDelta: 1 } },
      ],
    },
  },
}
