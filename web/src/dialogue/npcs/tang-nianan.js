// 来源：design/spec/material/drafts/唐念安-叙事视图.md §七—§十。
export const tangNianan = {
  id: 'tang_nianan', name: '唐念安', role: 'B2 女区 · 探视电话旁', mark: '唐',
  description: '她害怕的不是不爱女儿，而是自己爱得还不够安全。',
  objective: '区分一个不请自来的念头与真正的意图。',
  dossier: [
    { id: 'identity', label: '身份', text: '唐念安，B2 女区患者。', source: '当面交谈', revealsIdentity: true, requires: { met: true } },
    { id: 'observed', label: '当面观察', text: '她反复确认探视电话和电话线，床头柜上放着女儿的照片。', source: '当面观察', requires: { met: true } },
    { id: 'reason', label: '她的说法', text: '她害怕不请自来的伤害念头，把它们与自己的真实意图混在一起。', source: '当面交谈', requires: { minRelation: 1, allFlags: ['talked_tang'] } },
    { id: 'mother', label: '关系进展', text: '她开始接受“不需要完美，才能继续做母亲”。', source: '深入交谈', requires: { minRelation: 2, allFlags: ['tang_not_monster'] } },
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
        { id: 'why_here', text: '“你为什么住院？”', meta: '让她自己决定说到哪里', next: 'tang_reason', effects: { flagsAdd: ['talked_tang'], relationDelta: 1 } },
        { id: 'photo', text: '“照片里是安安？”', meta: '从女儿谈起', next: 'tang_photo' },
        { id: 'ocd_answer', text: '“念头不是意图。害怕它，恰好说明你不想那样做。”', meta: '强迫症打开的说法', next: 'tang_recognized', requires: { diseasesAny: ['强迫症'] }, effects: { flagsAdd: ['talked_tang'], relationDelta: 1 } },
      ],
    },
    tang_reason: {
      id: 'tang_reason',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我老怕自己伤害女儿。不是想，是怕。拿剪刀、给她洗澡、走到窗边……越怕，念头越来。”' }],
      options: [{ id: 'leave', text: '“你可以停在这里。”', meta: '结束会话', end: true }],
    },
    tang_photo: {
      id: 'tang_photo',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“嗯。照片安全一点。”她笑得有些不好意思，“真的她在面前，我会忍不住去摸鼻息，看她还在不在呼吸。”' }],
      options: [{ id: 'leave', text: '把照片放回原处。', meta: '结束会话', end: true }],
    },
    tang_recognized: {
      id: 'tang_recognized',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '她看着你，先是警惕，然后慢慢松开手。“你也知道那种念头？”' }],
      options: [{ id: 'leave', text: '“知道它会冒充你。”', meta: '结束会话', end: true }],
    },
    tang_familiar: {
      id: 'tang_familiar',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我以前觉得，有那种念头的人就是怪物。可我一次都没有伤害过她。我只是每天都在防一个从没发生过的我。”' }],
      options: [{ id: 'not_monster', text: '“你不需要完美，才能继续做她妈妈。”', meta: '回应她真正害怕的判断', next: 'tang_answer', effects: { flagsAdd: ['tang_not_monster'], relationDelta: 1 } }],
    },
    tang_answer: {
      id: 'tang_answer',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“我丈夫也这么说。”她擦了一下眼角，“两个人都这么说，可能……值得先信一次。”' }],
      options: [{ id: 'leave', text: '让这句话停在这里。', meta: '结束会话', end: true }],
    },
    tang_core: {
      id: 'tang_core',
      blocks: [{ kind: 'npc', speaker: '唐念安', text: '“安安需要的是一直在的人，不是脑子里从来没有坏念头的人。”她把女儿的照片立正，“这句话我还得多说几遍。”' }],
      options: [{ id: 'leave', text: '“慢慢说。”', meta: '结束深入对话', end: true }],
    },
  },
}
