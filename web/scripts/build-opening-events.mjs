/**
 * 生成 `data/opening.json` 的阶段 7 `event_rule` 与 `events` 两个块（**生成物，勿手改**）。
 *
 * 用法（在仓库根目录跑）：
 *   bun web/scripts/build-opening-events.mjs --emit      # 打印将要写入的两个块的 JSON 文本
 *   bun web/scripts/build-opening-events.mjs --check     # 只核对（不写），与 data/opening.json 现状比
 *   bun web/scripts/build-opening-events.mjs --write     # 就地改写 data/opening.json 的这两个块
 *   bun web/scripts/build-opening-events.mjs --census    # 报数（事件包 / 覆盖病 / 扩展位 / 素材）
 *
 * 为什么要有这个脚本（提示词 §十二「不要手抄清单」+ §一 第 5 条「一份权威数据」）：
 *   事件的 `expansions[].label` / `clause` / `column` 是 **data/opening_clinic.json 里那一档答案的重述**。
 *   手抄必然漂移；本脚本从 clinic 数据取这三样，数据契约里的值由 `validateClinic` 的
 *   `expansion_label_mismatch` / `expansion_clause_mismatch` / `expansion_column_mismatch` 现场比对。
 *   事件的 `effects.attributes` 同理，是它扩写自的那几段素材（`source_experiences`）属性效果的**合计**；
 *   由 `validateClinic` 的 `event_effects_not_from_material` 现场比对。
 *
 * 数据来源：
 *   - data/opening.json        —— 288 段素材（experiences）· 11 facet 词表（vocab）· attributes / bands
 *   - data/opening_clinic.json —— 题库与逐档答案（label / clause / column），扩展位的文案唯一权威
 */

import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const OPENING = resolve(ROOT, 'data/opening.json')
const CLINIC = resolve(ROOT, 'data/opening_clinic.json')

// ─────────────────────────────────────────────────────────────────────────────
// 一、那件事（9 件）：阶段 7 样板批。
//     `activates` 是 owner 第 2 条裁定的落点——经历的第一职责是激活他这张病。
//     `spine` 的五轴取自提示词 §7.2；`context` / `relation` 取自提示词 §二 第 4 条的六位枚举。
//     ⚠️ onset 与 agency 两轴**没有对应的问题**（题库 114 问里一问都没有，见侦察报告），
//        所以它们只由 `spine` 承载，不进 `expansions`——这是本批的已知缺口，口径文档有 ⏳ 说明。
// ─────────────────────────────────────────────────────────────────────────────

const SPEC = [
  {
    id: 'evt_0001',
    title: '白事那几天',
    summary: '家里那个人走了以后，剩下的事都落在我身上。',
    claim: '他的人生从守灵那几天起改成了替别人过日子。',
    spine: {
      onset: 'adolescence',
      context: 'family',
      relation: ['parents'],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'coerced',
      event: ['loss', 'change'],
    },
    activates: ['dis_0009', 'dis_0017', 'dis_0007', 'dis_0012'],
    expansion_keys: ['q093:death', 'q086:loss', 'q089:widowed', 'q086:warm', 'q092:family_only', 'q007:always', 'q011:leave', 'q011:stopped'],
    basis: '教材《精神病学》第 7 版 第十二章第一节 应激源三分类（家庭因素：夫妻分居或离婚、配偶患病、配偶死亡；psy7.txt:7270-7280）；同书心境障碍章「常见负性生活事件，如丧偶、离婚……均可导致抑郁发作」（psy7.txt:5289-5290）。⚠️「这类事件激活这张具体病」是设计选择，教材不给逐病映射（见诱因事件检索记录 §七 7.1 第 1 条）。',
  },
  {
    id: 'evt_0002',
    title: '背后的那几句',
    summary: '走到哪儿都有人在背后说我，说了很久。',
    claim: '他把往后所有的不顺都归到那些话上，从此只信自己那一套。',
    spine: {
      onset: 'adolescence',
      context: 'work',
      relation: ['peers', 'group'],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'powerless',
      event: ['threat', 'conflict'],
    },
    activates: ['dis_0010', 'dis_0018', 'dis_0005', 'dis_0011'],
    expansion_keys: ['q009:relation', 'q074:threat', 'q086:often_quarrel', 'q087:change', 'q092:quiet', 'q007:always', 'q011:work_hurt', 'q011:mess'],
    basis: '教材 第十二章第一节 应激源（工作或学习因素：缺乏人际交流、缺乏被接纳和被认可感、工作伙伴之间竞争激烈；家庭因素：家庭矛盾；psy7.txt:7272-7278）；同书 7281-7284「与个体对事件的认知评价、主观体验和应对方式有关」——同一件事落在不同答案上指向不同的病，本作的候选收敛即由此而来。',
  },
  {
    id: 'evt_0003',
    title: '错了就重来',
    summary: '家里的规矩错一次都不行，我后来凡事都要重做一遍。',
    claim: '他把「不许出错」带到了往后的每一件小事上。',
    spine: {
      onset: 'childhood',
      context: 'family',
      relation: ['parents', 'authority'],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'coerced',
      event: ['threat', 'exposure'],
    },
    activates: ['dis_0015', 'dis_0020', 'dis_0006', 'dis_0025'],
    expansion_keys: ['q086:strict', 'q009:work_p', 'q092:family_only', 'q089:partner', 'q007:first', 'q007:always', 'q011:work_hurt', 'q011:some'],
    basis: '教材 第十二章第一节 应激源（家庭因素：家庭成员间……教育子女的方式或目标等方面的重大分歧；psy7.txt:7273-7274）；同书强迫障碍章「常在无明显诱因下缓慢起病」（psy7.txt:6253）——本事件是「诱因不显」的那一类，故扩展位以成长环境为主。',
  },
  {
    id: 'evt_0004',
    title: '连着几个月不睡',
    summary: '赶工那阵子几乎没合过眼，我什么都能做成。',
    claim: '他把那段没日没夜当成了自己最好的时候，之后再没能回到那儿。',
    spine: {
      onset: 'adulthood',
      context: 'work',
      relation: ['authority', 'peers'],
      duration_span: 'short',
      duration_pattern: 'single',
      agency: 'partial',
      event: ['success', 'change'],
    },
    activates: ['dis_0019', 'dis_0026', 'dis_0022', 'dis_0011'],
    expansion_keys: ['q009:work_p', 'q087:change', 'q087:now_stop', 'q089:partner_kid', 'q007:before_recent', 'q011:quit', 'q011:stopped'],
    basis: '教材 第十二章第一节 应激源（工作或学习因素：工作变换性越来越大、任务目标不确定、理想与现实的冲突、对工作（学业）不满但无法改变；psy7.txt:7275-7278）。⚠️ 教材不给「睡眠剥夺 → 躁狂发作」的因果条目（本次未检索到），「赶工那一段」作为躁狂相的诱因是设计选择，标 ⏳。',
  },
  {
    id: 'evt_0005',
    title: '那条路我不敢走',
    summary: '出过那回事以后，走到那个路口我就绕开。',
    claim: '他把一条平常的路从生活里划掉了，绕行的范围后来慢慢变大。',
    spine: {
      onset: 'adulthood',
      context: 'society',
      relation: ['strangers'],
      duration_span: 'instant',
      duration_pattern: 'single',
      agency: 'powerless',
      event: ['threat', 'loss'],
    },
    activates: ['dis_0008', 'dis_0014', 'dis_0001', 'dis_0002'],
    expansion_keys: ['q093:disaster', 'q043:now', 'q043:recent', 'q043:past', 'q009:event', 'q087:stop', 'q092:quiet', 'q007:first', 'q011:mess'],
    basis: '教材 第十二章第三节：「PTSD 是由于受到异乎寻常的威胁性、灾难性心理创伤」（psy7.txt:7408-7409）；诊断要点「遭受异乎寻常的创伤性事件或处境（如天灾人祸）」（psy7.txt:7487）；同书 7416-7419「所谓创伤性体验应该具备两个特点：第一，对未来的情绪体验具有创伤性影响」。⚠️ 按此条，指向 PTSD 的诱因**不得**是日常压力事件。',
  },
  {
    id: 'evt_0006',
    title: '名单上没有我',
    summary: '那一次留人的名单里没有我，之后我什么也没做成。',
    claim: '他从名单那天起就不再接新的活，把自己从所有事里撤了出来。',
    spine: {
      onset: 'adulthood',
      context: 'work',
      relation: ['authority'],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'powerless',
      event: ['failure', 'loss'],
    },
    activates: ['dis_0016', 'dis_0013', 'dis_0021', 'dis_0024'],
    expansion_keys: ['q093:job', 'q093:money', 'q011:stopped', 'q011:quit', 'q087:now_stop', 'q087:stop', 'q092:quiet', 'q007:before_recent'],
    basis: '教材 心境障碍章「常见负性生活事件，如丧偶、离婚、婚姻不和谐、失业、严重躯体疾病……均可导致抑郁发作。另外经济状况差、社会阶屋〔OCR:层〕低下者易患本病」（psy7.txt:5289-5291）；同书适应障碍「典型的生活事件包括居丧、离婚、失业或变换岗位……经济危机」（psy7.txt:7546-7547）。',
  },
  {
    id: 'evt_0007',
    title: '门关上以后',
    summary: '他们把我留在门外，那件事没个说法。',
    claim: '他从此不再往人群里去，也学会了先动手再说。',
    spine: {
      onset: 'adolescence',
      context: 'school',
      relation: ['peers', 'strangers'],
      duration_span: 'long',
      duration_pattern: 'intermittent',
      agency: 'powerless',
      event: ['conflict', 'exposure'],
    },
    activates: ['dis_0009', 'dis_0020', 'dis_0021', 'dis_0003'],
    expansion_keys: ['q093:legal', 'q086:cold', 'q074:past', 'q074:recent', 'q092:quiet', 'q011:mess', 'q007:always'],
    basis: '教材 第十二章第一节 应激源三分类（社会因素：社会生活中的重要事件；psy7.txt:7279-7280）；同书 7286-7291 创伤前变量「既往创伤史如童年期受歧视、受虐待、被遗弃、性创伤等」；同书 6632-6633「遭遇对个体有重大意义的生活事件」。',
  },
  {
    id: 'evt_0008',
    title: '家里躺着人',
    summary: '家里有人躺着要人管，我哪儿也去不了。',
    claim: '他把自己那份日子整个腾出来给了病人，等回头时已经没有自己的位置。',
    spine: {
      onset: 'adulthood',
      context: 'family',
      relation: ['parents', 'partner'],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'coerced',
      event: ['change', 'loss'],
    },
    activates: ['dis_0023', 'dis_0018', 'dis_0007', 'dis_0004'],
    expansion_keys: ['q093:care', 'q011:leave', 'q011:stopped', 'q087:now_stop', 'q092:family_only', 'q007:always', 'q089:partner'],
    basis: '教材 第十二章第一节 应激源（家庭因素：配偶患病、家庭矛盾……家庭成员间……教育子女的方式或目标等方面的重大分歧；psy7.txt:7272-7274）；同书 7281-7284「应激源只有其强度和主观体验超出个体的耐受能力时，才能成为应激相关障碍的致病因素」。经历侧 facet `role_care.care_giver`（谁照顾谁）与这一件事同轴。',
  },
  {
    id: 'evt_0009',
    title: '说不上哪天起',
    summary: '没有哪一件特别的事，就是一天天坏下来的。',
    claim: '他找不出那件事，可病前与病后像是两个人。',
    spine: {
      onset: 'adulthood',
      context: 'work',
      relation: [],
      duration_span: 'long',
      duration_pattern: 'continuous',
      agency: 'powerless',
      event: ['change'],
    },
    activates: ['dis_0010', 'dis_0017', 'dis_0022', 'dis_0012'],
    expansion_keys: ['q093:no', 'q093:more', 'q009:none', 'q009:unsure', 'q087:smooth', 'q092:quiet', 'q007:always', 'q007:first', 'q011:some'],
    basis: '⚠️ 本事件是**兜底**（定位规则的最后一条），用来承载「诱因不明确」这一类真实情形，依据是教材自己承认它有：强迫障碍「常在无明显诱因下缓慢起病」（psy7.txt:6253）、惊恐障碍「多数患者不能找到相关的创伤性事件」（psy7.txt:5871-5872）、心境障碍「复发之前却常常找不到这种『诱因』」（psy7.txt:5463）。它的存在保证 `one_event_per_run` 在任何答案组合下都成立。',
  },
]

// ─────────────────────────────────────────────────────────────────────────────
// 二、扩展位：哪一档答案对应 11 facet 里的哪一个坐标。
//     判据（提示词 §7.2）：取值**必须来自现有 11 facet 词表**，不许新增轴。
//     每一条都写明「为什么这一档对得上」；对不上的（两轴）在口径文档里标 ⏳。
// ─────────────────────────────────────────────────────────────────────────────

const EXPANSION_MAP = {
  'q007:first': ['duration_pattern', 'single', '无类似发作 → 这一段是单次发作（经历侧 facet「怎么发生的」的 single 端）。'],
  'q007:before': ['duration_pattern', 'intermittent', '有类似发作 → 断断续续（intermittent）。'],
  'q007:before_treated': ['duration_pattern', 'intermittent', '有类似发作、曾因此就诊 → 断断续续（intermittent）。'],
  'q007:before_recent': ['duration_pattern', 'intermittent', '有类似发作、本次为再次发作 → 断断续续（intermittent）。'],
  'q007:always': ['duration_pattern', 'continuous', '长期如此、无明显发作间歇 → 一直这样（continuous）。'],
  'q009:none': ['event', 'change', '自述没有明显的原因 → 事件本身只能记成「改变」这一类（本事件的兜底性质）。'],
  'q009:unsure': ['event', 'change', '诱因难以确定 → 同上，记成「改变」。'],
  'q009:event': ['event', 'change', '教科书级的「诱因」档：患者自己指认「某件事之后」，与《病历书写基本规范》第十八条（三）1「可能的原因或诱因」同一件事。'],
  'q009:relation': ['relation', 'group', '人际冲突是应激源的一类（psy7.txt:7272-7278：缺乏人际交流、竞争激烈）。'],
  'q009:work_p': ['context', 'work', '工作或学习压力 = 应激源第二类（psy7.txt:7275-7278）。'],
  'q009:body': ['consequence', 'ability', '躯体不适作为诱因，落进「这件事留下了什么」里的能力一项。'],
  'q043:past': ['event', 'threat', '重大创伤性经历（已过去较久）→ 威胁类事件。'],
  'q043:recent': ['event', 'threat', '重大创伤性经历（距今不久）→ 威胁类事件。'],
  'q043:now': ['event', 'threat', '重大创伤性经历（至今仍受影响）→ 威胁类事件。'],
  'q074:past': ['event', 'threat', '被人侵害（已结束）→ 威胁类事件（psy7.txt:7290-7291 创伤前变量「受虐待」）。'],
  'q074:recent': ['event', 'threat', '被人侵害（距今不久）→ 威胁类事件。'],
  'q074:threat': ['event', 'threat', '曾受到他人威胁 → 威胁类事件。'],
  'q086:warm': ['context', 'family', '幼年家庭气氛 → 「在哪」（家庭）。'],
  'q086:strict': ['context', 'family', '幼年管教方式 → 「在哪」（家庭）。'],
  'q086:cold': ['context', 'family', '幼年无人照管 → 「在哪」（家庭）。'],
  'q086:often_quarrel': ['event', 'conflict', '家中经常争吵 → 冲突类事件。'],
  'q086:loss': ['event', 'loss', '幼年有亲人去世 → 丧失类事件。'],
  'q087:smooth': ['context', 'school', '学习与工作一直较顺利 → 「在哪」（学校）。'],
  'q087:change': ['context', 'work', '多次变动 → 「在哪」（工作）。'],
  'q087:stop': ['context', 'work', '曾中断一段时间 → 「在哪」（工作）。'],
  'q087:now_stop': ['context', 'work', '目前中断 → 「在哪」（工作）。'],
  'q089:partner': ['relation', 'partner', '目前与伴侣同住 → 「身边有谁」（伴侣）。'],
  'q089:partner_kid': ['relation', 'partner', '与伴侣及子女同住 → 「身边有谁」（伴侣）。'],
  'q089:divorced': ['relation', 'partner', '已离异 → 「身边有谁」（伴侣，已成过去）。'],
  'q089:widowed': ['relation', 'partner', '伴侣已去世 → 「身边有谁」（伴侣，已成过去）。'],
  'q092:outgoing': ['relation', 'peers', '朋友较多、交往主动 → 「身边有谁」（同辈）。'],
  'q092:quiet': ['relation', 'peers', '话不多、朋友较少 → 「身边有谁」（同辈）。'],
  'q092:family_only': ['relation', 'parents', '仅与家人交谈 → 「身边有谁」（父母/家人）。'],
  'q093:no': ['event', 'change', '自述无明显重大生活事件 → 只能记成「改变」这一类（本事件的兜底性质）。'],
  'q093:death': ['event', 'loss', '有亲人去世 → 丧失类事件。'],
  'q093:split': ['event', 'loss', '有与亲近的人分开 → 丧失类事件。'],
  'q093:job': ['event', 'loss', '有失去工作 → 丧失类事件（psy7.txt:5289-5290 明列失业）。'],
  'q093:disaster': ['event', 'change', '有重大变故 → 改变类事件（灾难一级的事件另有 q043 承载）。'],
  'q093:money': ['consequence', 'resource', '在经济或住房方面有压力 → 「留下了什么」（资源）。'],
  'q093:legal': ['event', 'conflict', '与他人有纠纷 → 冲突类事件。'],
  'q093:care': ['role_care', 'care_giver', '需长期照顾他人 → 经历侧 facet「谁照顾谁」的照顾者一端。'],
  'q093:more': ['event', 'change', '有不止一件重大生活事件 → 改变类事件（兜底事件承载「多件」这一情形）。'],
  'q011:none': ['consequence', 'ability', '发病后工作与生活基本如常 → 「留下了什么」（能力）。'],
  'q011:some': ['consequence', 'ability', '发病后对工作与学习有一定影响 → 同上（能力）。'],
  'q011:work_hurt': ['consequence', 'ability', '发病后工作或学习受到明显影响 → 同上（能力）。'],
  'q011:leave': ['consequence', 'ability', '发病后曾请假或休学 → 同上（能力）。'],
  'q011:quit': ['consequence', 'ability', '发病后已辞职或退学 → 同上（能力）。'],
  'q011:stopped': ['consequence', 'ability', '发病后已不能上班上学 → 同上（能力）。'],
  'q011:mess': ['consequence', 'behavior', '发病后日常生活秩序紊乱 → 「留下了什么」（行为）。'],
}

// ⚠️ **跨文件同名 id 的逐条交代**（`value_id === value` 的那几档）。
// 两套数据（data/opening_clinic.json 与 data/opening.json）有 10 个 id 字符串撞名，其中
// `none` 在 clinic 侧被 11 个语义各不相同的闭集共用。**撞名是巧合，不是语义相等**：
// 映射表（EXPANSION_MAP）才是唯一权威，这里给同名的那几档补一句「为什么仍然这么映射」。
const SAME_ID_NOTE = {
  'q086:loss': 'clinic 的 childloss 档「小时候有过亲人去世」与 opening 的 event.loss「失去」**字符串相同、语义不同轴**：前者是**成长环境里的一件事**（个人史栏），后者是**这件事在事件轴上的坐标**。映射成立的理由是「亲人去世在事件轴上就是失去」这一句判断，不是两个 id 长得一样。⚠️ 反例口径见 event_wiring.locate.symptom_traps。',
  'q074:threat': 'clinic 的 abuse.threat「有人威胁过我」与 opening 的 event.threat「威胁」同名不同义：前者是**被侵害的一种情形**（风险栏），后者是**事件轴坐标**。',
  'q089:partner': 'clinic 的 marriage.partner「有伴，没孩子」与 opening 的 relation.partner「伴侣」同名不同义：前者是**当下的婚姻状况**（婚姻栏），后者是**那件事发生时的关系轴坐标**。',
  'q092:peers': 'clinic 的 personality_support 没有 peers 档；这条是占位，若将来出现同名档，必须在此逐条交代。',
}

// ─────────────────────────────────────────────────────────────────────────────
// 二之二、定位规则：一局恰一件那件事。
//
// ⚠️ **没有新增任何一问**（提示词 §7.3.1 的选项 ②）。理由有二，都写进了数据的 `why_these_questions`：
//   ① 侦察实测：现行 114 问里**严格同构的筛选问 = 0 个**，且 `agency`（那时你能决定多少）**一问都没有**；
//      要新增就必须给 `agency` 造一问，而门诊初诊里**没有这么问的一手出处**——`validateClinic` 的
//      `question_without_basis` 要求每一问都写出处，给一问挂 ⏳ 的出处比不新增更坏（提示词 §一 第 6 条）。
//   ② 逐病映射本来就不在教材里（见诱因事件检索记录 §七 7.1 第 1 条），所以定位靠的是
//      **教科书级的问法**（诱因 / 既往重大生活事件 / 成长环境 / 生活处境），不是症状。
//
// 规则表按顺序判，第一条 when 全部成立的胜出，都不成立取 `fallback_event`。
// **末条是无条件的兜底**，所以「任何答案组合下恰好一件」是**结构保证**，不是抽样结论。
// 用到的问：q093（必问）· q086（必问）· q009（必问）· q043（躯体型主诉分支问）· q074（想过伤人的分支问）。
// ─────────────────────────────────────────────────────────────────────────────

// 允许出现在定位规则里的问（**唯一**白名单）。每一条写明：这一问问的是「发生过什么」。
const LOCATE_EXPERIENCE_QUESTIONS = [
  { q: 'q093', asks_about: '病前有没有重大生活事件（亲人走了 / 分开 / 丢了工作 / 出过大事 / 钱或住的地方 / 与人纠纷 / 要照顾人 / 不止一件）', basis: '《病历书写基本规范》第十八条（三）1「发病情况：记录发病的时间、地点、起病缓急、前驱症状、**可能的原因或诱因**」（nhc.txt:49）；教材第十二章第一节 应激源三分类（家庭 / 工作或学习 / 社会，psy7.txt:7270-7280）。' },
  { q: 'q009', asks_about: '发病前后有没有明显的原因、什么情况下好一点 / 更差', basis: '教材第三章第三节（一）3.(1)「**发病条件及发病的相关因素**：询问患者发病的环境背景……应估计是发病原因还是诱因」（psy7.txt:2241-2243）。' },
  { q: 'q086', asks_about: '幼年家里的情况（和睦 / 管得很严 / 没人管 / 经常吵 / 小时候有亲人去世）', basis: '教材第三章第三节（一）5「**个人史**一般指从母亲妊娠到发病前的整个生活经历」（psy7.txt:2259）；第十二章第一节 易感因素之创伤前变量「既往创伤史如童年期受歧视、受虐待、被遗弃、性创伤等」（psy7.txt:7290-7291）。' },
  { q: 'q074', asks_about: '有没有被人打过 / 欺负过 / 威胁过，现在是否安全', basis: '教材 7290-7291 创伤前变量「受虐待、被遗弃」；《病历书写基本规范》现行病史采集含「可能的原因或诱因」（nhc.txt:49）。⚠️ 本问本身是**风险栏**的问，用它的 `threat` / `unsafe_now` 两档定位那件事，靠的是「被侵害是一件发生过的事」这一句判断，不是「风险 = 事件」。' },
  { q: 'q043', asks_about: '有没有经历过很难过去的事（闪回 / 噩梦 / 一直提着心）', basis: '教材第十二章第三节 PTSD「受到**异乎寻常**的威胁性、灾难性心理创伤」（psy7.txt:7408-7409）；诊断要点「遭受异乎寻常的创伤性事件或处境（如天灾人祸）」（psy7.txt:7487）。⚠️ 这一问的措辞里带症状（闪回 / 噩梦），但**它问的主干是「有没有经历过很难过去的事」**——`in` 只取 `past` / `recent` / `now` 三档（都是「有过」的时间态），不取任何症状档。' },
]

// ⚠️ **症状陷阱表**：措辞看起来像事件、其实是症状（或不是经历）的那几档。
//    判据 locate_uses_symptom_trap 会在有人把这些档写进定位规则时报错。
//    这张表逐条来自侦察报告 §12 的「语义重叠」核对——它是**反面清单**，不是可用档。
const LOCATE_SYMPTOM_TRAPS = [
  // severity: 'forbid' = 绝不许进定位规则（判据 locate_uses_symptom_trap 报错）
  //           'note'   = 本批**确实**用到它当判别档，但它偏弱/性质特殊，判据 locate_uses_weak_discriminator 只报警告，
  //                      把它摆在明面上让 owner 判断——不许偷偷用。
  { severity: 'forbid', answer_set: 'chief_complaints', value_id: 'anger', looks_like: 'event.conflict', why: '「差点跟人吵起来」是**症状**（主诉栏），`event.conflict` 是**经历**（冲突）。措辞相同、语义不同轴——全表最易误接的一处。' },
  { severity: 'forbid', answer_set: 'irritable', value_id: 'often', looks_like: 'event.conflict', why: '「经常跟人吵起来」同样是症状（易激惹），不是经历过的事。' },
  { severity: 'forbid', answer_set: 'family_history', value_id: 'suicide', looks_like: 'event.loss', why: '家族史栏的「有自杀去世的」是**家族史**，不是患者本人的经历。本批没有任何规则或扩展位引用它。' },
  { severity: 'forbid', answer_set: 'trauma', value_id: 'no', looks_like: 'event.threat', why: '「没有」不能推出「没有事件」——问事件的地方是 q009 / q093。' },
  { severity: 'forbid', answer_set: 'aggravator', value_id: 'body', looks_like: 'event.threat', why: '「有，是身体上的事」是诱因的**类别**（躯体），不是被威胁。' },
  { severity: 'forbid', answer_set: 'marriage', value_id: 'widowed', looks_like: 'event.loss', why: '「老伴走了」是**当下婚姻状况**（婚姻栏），不等于患者经历过的一次丧失事件。本批把它**显式映射**到 `relation.partner`（「曾经有伴侣」）并带 same_id_note，但**没有**拿它当定位档。' },
  { severity: 'note', answer_set: 'childhood', value_id: 'loss', looks_like: 'event.loss', why: '「小时候有过亲人去世」是**成长环境里的一件事**（个人史栏），不是「那件事」。本批用规则 loc_04 拿它定位 evt_0001——这是**弱判别档**：它说的是成长里的一次丧失，不是病前那一次。owner 若认为不合格，删 loc_04 即可（evt_0001 仍有 loc_02 兜着）。' },
  { severity: 'note', answer_set: 'childhood', value_id: 'often_quarrel', looks_like: 'event.conflict', why: '「家里经常吵」是**长期家庭气氛**，不是某一件冲突事件。本批用规则 loc_11 拿它定位 evt_0002——同样是**弱判别档**（长期处境当「那件事」）。' },
]

const LOCATE_RULES = [
  { id: 'loc_01', event: 'evt_0005', q: 'q093', in: ['disaster'], basis: '「出过大事」→ 灾难一级的事件。教材：PTSD「受到异乎寻常的威胁性、灾难性心理创伤」（psy7.txt:7408-7409）、诊断要点「遭受异乎寻常的创伤性事件或处境（如天灾人祸）」（psy7.txt:7487）。⚠️ 按此条，指向 PTSD 的诱因不得是日常压力事件，故本规则排在所有日常事件规则之前。' },
  { id: 'loc_02', event: 'evt_0001', q: 'q093', in: ['death'], basis: '「有亲人走了」→ 家庭因素的丧失。教材：应激源三分类之家庭因素「配偶患病、配偶死亡」（psy7.txt:7272-7274）；心境障碍章「常见负性生活事件，如丧偶、离婚……均可导致抑郁发作」（psy7.txt:5289-5290）。' },
  { id: 'loc_03', event: 'evt_0008', q: 'q093', in: ['care'], basis: '「要照顾人」→ 长期照护负担。教材：应激源三分类之家庭因素（家庭成员之间的矛盾与分歧）（psy7.txt:7272-7274）；同书 7283-7284「应激源只有其强度和主观体验超出个体的耐受能力时，才能成为应激相关障碍的致病因素」。经历侧 facet `role_care.care_giver` 与此同轴。' },
  { id: 'loc_04', event: 'evt_0001', q: 'q086', in: ['loss'], basis: '「小时候有过亲人去世」→ 同一类丧失，但落在**创伤前变量**上。教材：「创伤前变量……既往创伤史如童年期受歧视、受虐待、被遗弃、性创伤等」（psy7.txt:7290-7291）。' },
  { id: 'loc_05', event: 'evt_0006', q: 'q093', in: ['job'], basis: '「丢了工作」→ 工作或学习因素。教材：应激源三分类之工作或学习因素（psy7.txt:7275-7278）；心境障碍章明列「失业」（psy7.txt:5289-5290）；适应障碍「典型的生活事件包括居丧、离婚、失业或变换岗位……经济危机」（psy7.txt:7546-7547）。' },
  { id: 'loc_06', event: 'evt_0006', q: 'q093', in: ['money'], basis: '「钱或住的地方有压力」→ 经济压力。教材：心境障碍章「经济状况差、社会阶屋〔OCR:层〕低下者易患本病」（psy7.txt:5290-5291）；适应障碍「经济危机」（psy7.txt:7547）。' },
  { id: 'loc_07', event: 'evt_0007', q: 'q093', in: ['legal'], basis: '「跟人有纠纷」→ 社会因素。教材：应激源三分类之社会因素（psy7.txt:7279-7280）；同书 6632-6633「遭遇对个体有重大意义的生活事件」。' },
  { id: 'loc_08', event: 'evt_0002', q: 'q074', in: ['threat', 'unsafe_now'], basis: '「有人威胁过我」/「现在还不安全」→ 被他人侵害且**仍在持续**。教材：创伤前变量「既往创伤史如童年期受歧视、受虐待、被遗弃」（psy7.txt:7290-7291）。⚠️ q074 是分支问（q073 答了「想过伤害别人」才问），没答时本规则不成立，正好后退到下一条。' },
  { id: 'loc_09', event: 'evt_0005', q: 'q043', in: ['recent', 'now'], basis: '「有过，时间不算久」/「现在还在里面」→ 重大创伤性经历尚未过去。教材：PTSD 诊断要点「遭受异乎寻常的创伤性事件或处境」（psy7.txt:7487）；同书 7416-7419「创伤性体验……第一，对未来的情绪体验具有创伤性影响」。⚠️ 同样是分支问（躯体型主诉才问）；`past`（已经过去很久）刻意**不**收进来——教材把「异乎寻常」与「仍在影响」并列，久已结束的创伤交给生活质量那一侧。' },
  { id: 'loc_10', event: 'evt_0002', q: 'q009', in: ['relation'], basis: '「有，是跟人的关系」→ 人际冲突作为诱因。教材：应激源（工作或学习因素：缺乏人际交流、缺乏被接纳和被认可感、工作伙伴之间竞争激烈）（psy7.txt:7276-7278）。' },
  { id: 'loc_11', event: 'evt_0002', q: 'q086', in: ['often_quarrel'], basis: '「经常吵」→ 长期的家庭冲突环境。教材：应激源之家庭因素「家庭矛盾如家庭几代成员之间的矛盾……以及家庭成员间……的重大分歧也可以成为应激的来源」（psy7.txt:7273-7274）。' },
  { id: 'loc_12', event: 'evt_0003', q: 'q086', in: ['strict'], basis: '「管得很严」→ 成长环境里的规矩。教材：应激源之家庭因素「教育子女的方式或目标等方面的重大分歧」（psy7.txt:7274）。⚠️ 强迫障碍「常在无明显诱因下缓慢起病」（psy7.txt:6253）——本事件正是「诱因不显」的那一类，所以它的定位靠成长环境而不是靠某一件大事。' },
  { id: 'loc_13', event: 'evt_0007', q: 'q086', in: ['cold'], basis: '「没人管」→ 被忽视。教材：创伤前变量「既往创伤史如童年期受歧视、受虐待、**被遗弃**」（psy7.txt:7290-7291）。' },
  { id: 'loc_14', event: 'evt_0004', q: 'q009', in: ['work_p'], basis: '「有，是工作或学习」→ 工作或学习压力。教材：应激源之工作或学习因素「对工作（学业）不满但无法改变」「缺乏被接纳和被认可感」（psy7.txt:7275-7278）。⚠️ 本事件是唯一一件事里带「向上冲」那一段的，教材不给「睡眠剥夺 → 躁狂发作」的因果条目（本次未检索到），所以这一条只能标 ⏳。' },
  { id: 'loc_15', event: 'evt_0009', q: 'q093', in: ['no', 'more'], basis: '「没有」/「不止一件」→ 兜底事件。教材自己承认这两种情形都存在：强迫障碍「常在无明显诱因下缓慢起病」（psy7.txt:6253）；惊恐障碍「多数患者不能找到相关的创伤性事件」（psy7.txt:5871-5872）；心境障碍「复发之前却常常找不到这种『诱因』」（psy7.txt:5463）。' },
]

const LOCATE_FALLBACK = 'evt_0009'

const LOCATE_WHY = '现行 114 问里能问「病前发生过什么」的只有这几问，逐条给对应关系：**q093 重大生活事件**（法定的「可能的原因或诱因」最近似的一问，值域含 death/split/job/disaster/money/legal/care/more）· **q009 诱因与加重缓解因素**（教材「发病条件及发病的相关因素……应估计是发病原因还是诱因」psy7.txt:2241-2243 的直译问法）· **q086 幼年家庭环境**（教材个人史「一般指从母亲妊娠到发病前的整个生活经历」psy7.txt:2259）· **q043 重大创伤性经历**（教材 PTSD「异乎寻常的威胁性、灾难性心理创伤」psy7.txt:7408）· **q074 被侵害**（教材创伤前变量「受虐待、被遗弃」psy7.txt:7290-7291）。**没有用任何症状问**——侦察报告 §12 点名过这条误接（症状闭集不能拿来筛事件）。q087/q089/q092/q011 不作定位用，它们只在事件内部当扩展位（那是「这件事留下的痕迹」，不是「这是哪件事」）。'

const LOCATE_NO_NEW = '**本阶段一问都不新增**，所以一局问数上限 40 的约束（design/presentation/开局门诊问诊.md §11.1 第 4 条）不受影响：现状 31–39 问（中位 35），逐分支数字见 `bun web/scripts/render-clinic.mjs --check`。若将来要补 `agency`（那时你能决定多少），必须先在门诊初诊口径里找到问法的一手出处，否则只能标 ⏳，不得自造（提示词 §一 第 6 条）。'

// ─────────────────────────────────────────────────────────────────────────────
// 三、从素材里挑 `source_experiences`：这几段素材的属性效果合计 = 这件事的效果
//     —— 这样 `profileOf().experiences`（= 素材 id，下游 opening-runtime 直接消费）
//        与事件的 `effects.attributes` **结算出同一个数**，不产生第二份权威。
// ─────────────────────────────────────────────────────────────────────────────

const ATTR_TERMS_MAX = 2   // = data/opening.json 的 event_rule.effects_terms_max
const MATERIAL_MIN = 2
const MATERIAL_MAX = 4

function materialCandidates(odb, activates) {
  const want = new Set(activates)
  return odb.experiences
    .filter((e) => (e.diseases ?? []).some((d) => want.has(d)))
    .map((e) => e.id)
    .sort()
}

function sumEffects(odb, ids) {
  const out = {}
  for (const id of ids) {
    const rec = odb.experiences.find((e) => e.id === id)
    for (const [k, v] of Object.entries(rec.effects.attributes)) out[k] = (out[k] ?? 0) + v
  }
  return out
}

/**
 * 挑素材。判据按优先级排成一个可比较的分数，取**字典序最小**的一组：
 *   ① 合计项数尽量等于 2（存量每段素材本来就是 ≤2 项，事件也跟着是 2 项——形状同源）；
 *   ② 两项都为正（这件事留下的是一样拿得走的东西，不是抵消掉的净值）；
 *   ③ 素材尽量多（0-rule：`material_max` 上限；素材多 = 这件事覆盖的纵深更足）；
 *   ④ 两项的落差错开（不要把点数堆在一项上）；
 *   ⑤ 素材的 diseases 必须与事件的 activates 相交（只从那个池子里挑，见 materialCandidates）。
 * **穷举** size = 4 → 2，所以结果确定：同一份数据必得同一结果，改数据才会变。
 * 阈值 ATTR_TERMS_MAX = data/opening.json 的 event_rule.effects_terms_max。
 */
function pickMaterials(odb, activates) {
  const pool = materialCandidates(odb, activates)
  if (pool.length < MATERIAL_MIN) throw new Error(`${activates.join('/')} 名下素材不足 ${MATERIAL_MIN} 段`)
  let best = null
  const consider = (ids) => {
    const effects = sumEffects(odb, ids)
    const terms = Object.keys(effects).sort()
    if (terms.length > ATTR_TERMS_MAX) return
    if (terms.some((k) => effects[k] === 0)) return
    if (!terms.every((k) => effects[k] > 0)) return
    const vals = terms.map((k) => effects[k])
    const score = [
      ATTR_TERMS_MAX - terms.length,      // ① 越接近 2 项越好
      -ids.length,                        // ③ 素材越多越好
      Math.abs(Math.max(...vals) - Math.min(...vals)), // ④ 落差错开
      ids.join(','),                      // ⑤ 稳定
    ]
    if (best === null || cmp(score, best.score) < 0) best = { score, ids: [...ids], effects }
  }
  for (const size of [MATERIAL_MAX, 3, MATERIAL_MIN]) recruit(pool, size, consider)
  if (!best) throw new Error(`${activates.join('/')} 名下找不到合计项数 ≤${ATTR_TERMS_MAX} 且各项为正的素材组合`)
  return { ids: best.ids, effects: best.effects }
}

function cmp(a, b) {
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] === b[i]) continue
    return a[i] < b[i] ? -1 : 1
  }
  return 0
}

function recruit(pool, size, cb) {
  const cur = []
  const walk = (start) => {
    if (cur.length === size) { cb([...cur]); return }
    for (let i = start; i < pool.length; i += 1) {
      cur.push(pool[i]); walk(i + 1); cur.pop()
    }
  }
  walk(0)
}

// ─────────────────────────────────────────────────────────────────────────────
// 四、组装
// ─────────────────────────────────────────────────────────────────────────────

function build() {
  const odb = JSON.parse(readFileSync(OPENING, 'utf8'))
  const cdb = JSON.parse(readFileSync(CLINIC, 'utf8'))
  const qById = new Map(cdb.questions.map((q) => [q.id, q]))
  const optionOf = (qid, vid) => {
    const spec = cdb.answers[qById.get(qid).answers]
    return spec?.values.find((v) => v.id === vid) ?? null
  }

  const events = SPEC.map((spec) => {
    const keys = spec.expansion_keys
    const seen = new Set()
    const expansions = keys.map((key, i) => {
      const [qid, vid] = key.split(':')
      if (seen.has(key)) throw new Error(`${spec.id}: 扩展位重复 ${key}`)
      seen.add(key)
      const mapped = EXPANSION_MAP[key]
      if (!mapped) throw new Error(`${spec.id}: 扩展位 ${key} 没有登记到 11 facet 坐标（EXPANSION_MAP 缺项）`)
      const [facet, value, why] = mapped
      if (!odb.vocab[facet]) throw new Error(`${spec.id}: 未知 facet ${facet}`)
      if (!odb.vocab[facet].values.some((v) => v.id === value)) throw new Error(`${spec.id}: ${facet} 里没有取值 ${value}`)
      const question = qById.get(qid)
      if (!question) throw new Error(`${spec.id}: 扩展位指向不存在的问 ${qid}`)
      if (question.ask_mode !== 'player') throw new Error(`${spec.id}: ${qid} 不是玩家能答的问`)
      const opt = optionOf(qid, vid)
      if (!opt) throw new Error(`${spec.id}: ${qid} 的闭集里没有取值 ${vid}`)
      // ⚠️ 两套数据合用时**不许按 id 跨文件认语义**：`value_id` 是 data/opening_clinic.json 的答案
      // 取值，`value` 是 data/opening.json 的词表取值；两者只是这一次显式映射的两端（映射表在
      // 本脚本的 EXPANSION_MAP，逐条带理由）。恰好同名的那几档必须留下 `same_id_note`，
      // 由 validateClinic 的 expansion_id_collision_unjustified 现场核。
      return {
        id: `${qid}.${vid}`,
        facet,
        value,
        q: qid,
        value_id: vid,
        label: opt.label,
        clause: opt.clause ?? opt.record ?? opt.label,
        column: question.column,
        basis: why,
        ...(vid === value ? { same_id_note: SAME_ID_NOTE[`${qid}:${vid}`] ?? null } : {}),
      }
    })
    if (expansions.length < 6) throw new Error(`${spec.id}: 扩展位只有 ${expansions.length} 档，低于下限 6`)
    const axes = new Set(expansions.map((e) => e.facet))
    for (const axis of ['context', 'relation', 'duration_pattern', 'consequence']) {
      if (!axes.has(axis)) throw new Error(`${spec.id}: 扩展位没有覆盖「${axis}」这一位`)
    }

    const { ids, effects } = pickMaterials(odb, spec.activates)
    return {
      id: spec.id,
      title: spec.title,
      summary: spec.summary,
      claim: spec.claim,
      spine: spec.spine,
      expansions,
      activates: spec.activates,
      effects: { attributes: effects },
      source_experiences: ids,
      basis: spec.basis,
    }
  })

  const eventRule = {
    what: '一局恰一件「那件事」。这件事直接激活它的病（owner 阶段 7 裁定第 2 条），不再由十段经历的并集诱发。',
    authority_note: '本块是阶段 7「那件事」的唯一权威。事件的扩展位文案（label / clause / column）与 effects.attributes 是 data/opening_clinic.json 与自身 source_experiences 的**重述**，由 validateClinic 现场比对，不许手改。',
    one_event_per_run: true,
    locate_rule: '按 data/opening_clinic.json 的 event_wiring.locate.rules 顺序判：第一条所有 when 条件都成立的胜出；都不成立取 fallback_event。**规则表本身是穷尽的（末条无条件），所以任何答案组合下恰好定位到一件**——这是 one_event_per_run 的结构保证，不是抽样结论。',
    expansions_min: 6,
    expansions_min_basis: 'owner 阶段 7 裁定第 4 条「这个经历要经得起扩展，而不是大海捞针一样的漫天撒网」，并列了六位：什么时候 / 在哪儿 / 身边有谁 / 那时你能决定多少 / 后来怎样 / 留下了什么。其中四位（在哪儿 · 身边有谁 · 后来怎样 · 留下了什么）在现行 114 问题库里有问可问，另两位（什么时候 · 那时你能决定多少）**一问都没有** ⇒ 取「至少 6 档」为下限，并要求覆盖那四位（expansion_axes_required）。六位的枚举是 owner 口径；「6」这个数是本阶段取的默认，标 ⏳ 见 design/presentation/开局经历疾病接回.md 待裁表。',
    expansion_axes_required: ['context', 'relation', 'duration_pattern', 'consequence'],
    expansion_axes_unavailable: {
      onset: '⏳ 现行 114 问里没有一问在问「这件事从什么时候开始」。q005 问的是病程长度（不到两个星期…一年以上）、q006 问的是起病缓急（突然 / 慢慢），两者都不是 facet `onset`（童年 / 少年 / 成年）。⇒ 本批由事件的 spine.onset 承载，不进 expansions。',
      agency: '⏳ 现行 114 问里没有一问在问「那时你能决定多少」（侦察报告核对 114 问全部答案闭集，命中 0）。⇒ 本批由事件的 spine.agency 承载，不进 expansions。这一条是硬缺口，见口径文档待裁表。',
    },
    material_min: MATERIAL_MIN,
    material_max: MATERIAL_MAX,
    material_note: '`source_experiences` 是这件事**扩写自**的那几段存量素材（data/opening.json 的 experiences）。用途有两个，都是调用方拿它做的：① `profileOf().experiences` 直接把它交给下游 opening-runtime.js 的 settleAttributes（所以它必须非空、且必须指得到真记录）；② 审计素材覆盖，数出「永不被任何事件用到的素材」有几条。它**不是**反查键——方向是 事件 → 素材。要求：素材的 diseases 必须与事件的 activates 相交（event_material_not_activating）。',
    effects_terms_max: ATTR_TERMS_MAX,
    effects_note: '`effects.attributes` = `source_experiences` 那几段素材属性效果的**合计**（event_effects_not_from_material 现场比对）。这样「那件事」的属性结算与下游 `settleAttributes(db, profile.experiences)` 结算出同一个数，不存在第二份权威。⇒ 净值和 = 素材数 × 2（effects_rule.net）。⚠️ 与存量「十段和 = +2」相比，一局的原始总和由 20 降到 4–8——这个变化对序章三条检定阈值（3 / 5 / 7，见 opening-runtime.js）的影响见口径文档待裁表。',
    activates_min: 1,
    activates_max: 4,
    activates_per_event_this_batch: 4,
    activates_basis: '⚠️ 这个 4 **不是随手取的上界**，是两条既定约束合起来钉死的：① 语言指纹有 **4** 套（owner 阶段 6 亲自选的那四套，见 data/opening_clinic.json 的 voices），② §7.3.3 要求在任意一局里「玩家认下的病」都必须与「他怎么说话」收敛到的病一致（判据 voice_disease_conflict）。而「他怎么说话」由玩家在对话里的选择决定，与「那件事」近乎独立 ⇒ 要让这条一致性**在任何答案组合下都成立**，那件事的 `activates` 就必须**每一套指纹各有一张病**。4 套指纹 ⇒ 每件事恰 4 张。上界若小于 4，就会出现「某几套指征收敛到的病不在候选里」的局（本批第一版取 2 张时实测：45 局里有 17 局无解）；大于 4 则越出 candidate_max。⇒ 本批每件事一律 4 张，并由判据 event_voice_per_event 逐件核「4 张病分属 4 套指纹、不重不漏」。',
    candidate_max: 4,
    candidate_max_basis: '候选 = 那件事的 activates（4 张，一套指纹一张）减去已答扩展位声明排除的病；一局说话的调子定下来之后，再按调子收窄到与之相符的那一张。所以玩家看到的是：还没显出调子时 4 张里挑，显出调子之后 1 张——「怎么说话就是在说哪张病」（owner 第 7 条）。上界 4 存在的意义是把内容批的 `exclude` 规则关在 4 以内（candidate_over_limit）。',
    candidate_and_voice: '一局里说话调子与候选的关系是**先收窄、后落笔**：① 候选 = activates − exclude；② 若 voiceTally 已显出调子（打标档 ≥ voices.min_tagged），候选再收窄到「该调子代言的那一张病」；③ 玩家在收窄后的候选里「认」，认下的那张必然与调子一致——所以 voice_disease_conflict 在数据自洽时**永远不会触发**，它是一道兜底判据（数据坏了才响）。若调子还没显出来（打标不足 3 档），4 张全摆出来由玩家挑，此时不设一致性要求（他还没怎么说话）。依据：owner 第 7 条「语言指纹现在挂在病上：怎么说话就是在说哪张病」+ 提示词 §7.3.3。',
    coverage: {
      what: '病覆盖：26 张名册病每张至少被一件事激活，否则就是死病。',
      target_full: 26,
      target_this_batch: 26,
      note: 'owner 待裁 2 的默认 (a) 只要求样板批 ≥8 件事 / ≥6 张病。本批实际做到 9 件事 / 26 张名册病全数覆盖——因为「每件事 4 张、一套指纹一张」这个结构让覆盖率天然很高（9 × 4 = 36 个位，装 26 张绰绰有余）。⇒ 26 张名册病没有一张是死病，判据 event_coverage 按全集核。⚠️ 这是样板批的**结构红利**，不是内容批做完了：事件数与每件事的纵深（扩展位 / 素材 / claim）仍是样板规模。',
    },
    untouched_material: '未被任何事件用到的素材**只报数、不报错**（owner 待裁 7 的默认 (a)）：288 段是素材库，不是每一段都必须有归宿。报数字段见 web/scripts/build-opening-events.mjs --census 与 validateClinic().numbers.material。',
  }

  return { eventRule, events }
}

// ─────────────────────────────────────────────────────────────────────────────
// 五、把两个块写进 data/opening.json（**只替换这两个块**，文件其余字节不动）
// ─────────────────────────────────────────────────────────────────────────────

const INDENT = '  '
function stringifyBlock(value, depth) {
  return JSON.stringify(value, null, 2).split('\n').map((line, i) => (i === 0 ? line : INDENT.repeat(depth) + line)).join('\n')
}

function spliceBlock(text, key, body, beforeKey) {
  const rendered = `${INDENT}${JSON.stringify(key)}: ${stringifyBlock(body, 1)},`
  const start = text.indexOf(`${INDENT}${JSON.stringify(key)}: `)
  if (start >= 0) {
    // 已有这个块：替换到它的结束（顶层块的结束 = 下一个 depth-1 的 "key": 之前）
    const rest = text.slice(start)
    const next = rest.slice(1).search(new RegExp(`\\n${INDENT}"`))
    const end = next < 0 ? rest.length : next + 1
    return text.slice(0, start) + rendered + '\n' + text.slice(start + end + 1)
  }
  const anchor = text.indexOf(`${INDENT}${JSON.stringify(beforeKey)}: `)
  if (anchor < 0) throw new Error(`找不到插入锚点 ${beforeKey}`)
  return text.slice(0, anchor) + rendered + '\n' + text.slice(anchor)
}

function census() {
  const { events, eventRule } = build()
  const odb = JSON.parse(readFileSync(OPENING, 'utf8'))
  const used = new Set(events.flatMap((e) => e.source_experiences))
  const diseaseMap = new Map()
  for (const e of events) for (const d of e.activates) diseaseMap.set(d, (diseaseMap.get(d) ?? 0) + 1)
  const sizes = events.map((e) => e.expansions.length).sort((a, b) => a - b)
  const med = sizes.length % 2 ? sizes[(sizes.length - 1) / 2] : (sizes[sizes.length / 2 - 1] + sizes[sizes.length / 2]) / 2
  const ax = {}
  for (const e of events) for (const x of new Set(e.expansions.map((p) => p.facet))) ax[x] = (ax[x] ?? 0) + 1
  const act = {}
  for (const e of events) act[e.activates.length] = (act[e.activates.length] ?? 0) + 1
  const mat = events.map((e) => e.source_experiences.length)
  return {
    events: events.length,
    diseases_covered: diseaseMap.size,
    activates_per_event: act,
    expansions: { min: sizes[0], median: med, max: sizes[sizes.length - 1] },
    expansion_axes: ax,
    materials_per_event: { min: Math.min(...mat), max: Math.max(...mat), total: used.size },
    materials_used: used.size,
    materials_unused: odb.experiences.length - used.size,
    materials_total: odb.experiences.length,
    effects_terms_max: eventRule.effects_terms_max,
    per_event_effects: events.map((e) => ({ id: e.id, effects: e.effects.attributes, materials: e.source_experiences })),
    diseases_per_event: events.map((e) => ({ id: e.id, activates: e.activates })),
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 六、data/opening_clinic.json 的 `event_wiring`（这一屏的接线口径，同样由脚本生成）
//     —— 一局的链条在这里闭合：问诊 → 那件事 → 候选 → 认 → 诊断栏落笔 → 言语与精神检查。
// ─────────────────────────────────────────────────────────────────────────────

function buildWiring() {
  const cdb = JSON.parse(readFileSync(CLINIC, 'utf8'))
  const odb = JSON.parse(readFileSync(OPENING, 'utf8'))
  const qById = new Map(cdb.questions.map((q) => [q.id, q]))
  const optionIds = (qid) => {
    const q = qById.get(qid)
    if (!q) throw new Error(`定位规则引用了不存在的问 ${qid}`)
    const spec = cdb.answers[q.answers]
    if (!spec) throw new Error(`${qid} 没有答案闭集`)
    return new Set(spec.values.map((v) => v.id))
  }
  const eventIds = new Set(odb.events.map((e) => e.id))

  // 定位规则自检（同一条判据在 validateClinic 里再核一遍，这里拦的是生成期的手误）
  const reachable = new Set()
  for (const r of LOCATE_RULES) {
    if (!eventIds.has(r.event)) throw new Error(`${r.id}: 指向不存在的事件 ${r.event}`)
    const ids = optionIds(r.q)
    for (const v of r.in) if (!ids.has(v)) throw new Error(`${r.id}: ${r.q} 的闭集里没有 ${v}`)
    reachable.add(r.event)
  }
  if (!eventIds.has(LOCATE_FALLBACK)) throw new Error(`兜底事件 ${LOCATE_FALLBACK} 不存在`)
  reachable.add(LOCATE_FALLBACK)
  const unreachable = [...eventIds].filter((id) => !reachable.has(id))
  if (unreachable.length) throw new Error(`这些事件没有任何规则能定位到：${unreachable.join(' / ')}`)

  // 扩展位用到的问（从事件数据现算，不手抄）
  const expandQuestions = [...new Set(odb.events.flatMap((e) => e.expansions.map((x) => x.q)))].sort()
  const composed = new Set(Object.values(cdb.compose ?? {})
    .flatMap((spec) => (spec.sentences ?? []).flatMap((s) => (s.parts ?? []).map((part) => part.q))))
  const offPaper = expandQuestions.filter((q) => !composed.has(q))
  if (offPaper.length) throw new Error(`这些扩展问不在任何拼句模板里，答了也上不了纸：${offPaper.join(' / ')}`)

  return {
    what: '阶段 7 的接线：一局的经历不再是十段散点，而是**那件事**——问诊答案定位出它，它直接激活它的病，玩家认下一张，医师把「初步诊断」写上纸。本块只写**规则与指针**，一切取值都在权威数据里：事件与素材在 data/opening.json 的 events / experiences，病卡在 data/diseases.json 的 items，上屏文案与逐档答案在本文件。',
    authority: {
      events: 'data/opening.json `events` + `event_rule`（那件事、扩展位、激活的病、属性效果）',
      materials: 'data/opening.json `experiences`（288 段素材库；事件的 `source_experiences` 指回它）',
      diseases: 'data/diseases.json `items`（26 张名册 + 1 条固有项 dis_0027）与 `candidate_rule`',
      voices: '本文件 `voices`（语言指纹挂病）· `record.columns` 的 diagnosis 栏（落笔方与笔迹）',
      note: '**同一事实只有一个权威。** 本块不含任何取值副本；事件的 expansions 里那份 label / clause / column 是逐档答案的重述，由 validateClinic 现场比对（expansion_label_mismatch / expansion_clause_mismatch / expansion_column_mismatch）。',
    },
    locate: {
      what: '一局恰一件那件事（owner 第 3 条裁定：疾病诱因围绕着一件事展开）。',
      rule: '按 `rules` 顺序判：一条规则的 when 条件（该问的答案落在 `in` 里）全部成立即胜出；一条都不成立时取 `fallback_event`。**规则表的末条是无条件兜底，所以「一局恰一件」是结构保证**——不是抽样统计出来的结论（机器判据 one_event_per_run 仍然枚举全部已答前缀再核一遍）。',
      fallback_event: LOCATE_FALLBACK,
      fallback_basis: '兜底件 evt_0009「说不上哪天起」承载「诱因不明确」这一类真实情形。它**不是**为了凑数：教材自己承认这一情形存在——强迫障碍「常在无明显诱因下缓慢起病」（psy7.txt:6253）、惊恐障碍「多数患者不能找到相关的创伤性事件」（psy7.txt:5871-5872）、心境障碍「复发之前却常常找不到这种『诱因』」（psy7.txt:5463）。⇒ 问卷里的 q009 `none`（没有明显的原因）/ `unsure`（说不上来）与 q093 `no` / `more` 两档**必须留着**，它们是这个兜底的入口，不是冗余选项。',
      why_these_questions: LOCATE_WHY,
      // ★★ 机器判据的地基：**定位只能问「发生过什么」，不许问「你现在什么症状」**。
      //    症状闭集不许拿来筛事件——`chief_complaints.anger`（症状：差点跟人吵起来）与
      //    `event.conflict`（经历：冲突）措辞相同、语义不同轴，这是全表最易误接的一处。
      //    下面这张白名单是**唯一**允许出现在 rules[].q 里的问，逐条写明它问的是什么；
      //    判据 locate_question_not_experience 会挡住白名单之外的一问。
      question_rule: '规则表的 `q` 只能在 `experience_questions` 里取。这几问的共同点是**问「发生过什么」**（事件 / 处境 / 生活条件），不是问「你现在什么症状」。这条不是文风要求，是判据：症状闭集与经历事件轴**措辞可能相同、语义不同轴**（见 symptom_traps），拿症状去定位那件事就是把因果方向反过来。',
      experience_questions: LOCATE_EXPERIENCE_QUESTIONS,
      symptom_traps: LOCATE_SYMPTOM_TRAPS,
      no_new_questions: LOCATE_NO_NEW,
      questions_used: [...new Set(LOCATE_RULES.map((r) => r.q))].sort(),
      rules: LOCATE_RULES,
    },
    expand: {
      what: '那件事的扩展位：围着它问下去，答完既写纸、又收敛病。',
      rule: '每个事件自带 `expansions`（在 data/opening.json 的 events[] 上），每一档写明它落在 11 facet 里的哪一个坐标、由哪一问的哪一档答出来、以及这一档患者嘴上说什么（label）与纸上写什么（clause / column）。已答的扩展位**必须出现在纸上**（expand_not_on_paper）。',
      questions: expandQuestions,
      questions_note: '这几个问**全部是现行题库里的原问**，没有新增一问。它们是每一局的必问骨架或答过才算的分支问：q009 · q011 · q043 · q074 · q086 · q087 · q089 · q092 · q093 · q007。',
      why_these_four: 'owner 第 4 条裁定列了六位（什么时候 / 在哪儿 / 身边有谁 / 那时你能决定多少 / 后来怎样 / 留下了什么）。在现行 114 问里能对上的是四位：**在哪儿** ← q086 / q087 · **身边有谁** ← q089 / q092 · **后来怎样** ← q007 · **留下了什么** ← q011 / q093(money)。另外两位没有问可问，见 axes_flagged。',
      axes_flagged: {
        onset: '⏳ 「什么时候」：现行题库里没有一问在问「这件事从什么时候开始」（q005 问病程长度、q006 问起病缓急，都不是 facet onset 的童年/少年/成年）。本批由事件的 `spine.onset` 承载。',
        agency: '⏳ 「那时你能决定多少」：**一问都没有**（侦察实测：114 问全部答案闭集对 11 facet 做过对照，`agency` 命中 0）。本批由事件的 `spine.agency` 承载。⚠️ 这是本阶段的硬缺口——凡要补这一问，必须先在门诊初诊口径里找到问法的一手出处，否则只能标 ⏳（提示词 §一 第 6 条：查不到出处的一律标 ⏳，不许自造）。',
      },
      paper_rule: '扩展位的字**不另写一套拼句引擎**：`clause` 就是该问该档在本文件 `compose` 模板里已经用到的那一段（与逐档 `clause` 同一个字符串），`column` 就是那一问答问时落笔的栏目。答一句 → 纸上多一句，由现有的 `composeColumn` 完成。',
      off_paper: '凡被事件选作扩展位的问，都必须出现在某个 `compose.<栏目>.sentences[].parts[].q` 里——否则就会出现「对话里说了、纸上没写」。这条由生成脚本在生成期拦一次、由 validateClinic 的 expand_not_on_paper 在运行期再拦一次。',
    },
    candidate: {
      rule: '候选 = 那件事的 `activates`（data/opening.json 的 events[].activates）减去已答扩展位声明排除的病；**一局说话的调子定下来之后，再收窄到该调子代言的那一张病**（「怎么说话就是在说哪张病」）；候选上界 = data/opening.json 的 event_rule.candidate_max，两边同值。',
      narrowing_by_voice: '收窄规则的权威在 data/opening.json 的 `event_rule.candidate_and_voice`（那里写了它为什么必须是这么收的）。本块只记一句：**每件事 activates 4 张、一套指纹一张**，所以「调子定下来」至多把候选收到 1 张；调子还没显出来（打标档 < voices.min_tagged）时 4 张全摆出来由玩家挑。⚠️ 实测（800 局随机采样）：显调子 589 局，候选数 1；没显调子 211 局，候选数 4；候选 > 4 的 0 局；「调子与候选一个都对不上」的 0 局。',
      candidate_max: 4,
      candidate_max_basis: '上界与 data/opening.json 的 event_rule.candidate_max 同值（同一件事的两侧口径）。顶到 4 时患者意见栏只剩「认哪一张」这一个动作；本批每件事恰激活 2 张，候选恒为 2，余量留给内容批。',
      exclusion: '扩展位可以带 `exclude: string[]`（病 id）；玩家把这一档答出来，这些病就从候选里去掉。**本批没有声明任何排除规则**（events[].expansions 上无 exclude），理由见 data/diseases.json 的 candidate_rule.exclusion.why_none。槽位与判据（candidate_empty / candidate_over_limit）从本批起就生效。',
      narrowing_basis: '收缩候选这件事本身有教材依据：同一件事落在不同人身上结局不同——教材「遭遇应激源……是否出现应激相关障碍以及障碍的表现形式和严重程度，除了与应激源的性质、强度和持续时间有关外，更重要地是与个体对事件的认知评价、主观体验和应对方式有关。同一事件对不同的个体会有不同的反应」（psy7.txt:7281-7284）。⚠️ 教材**不给**「哪一类事件 → 哪一张病」的逐病映射（见 design/spec/material/ref/诱因事件与生活事件-检索记录.md §七 7.1 第 1 条），所以 activates 与 exclude 都是设计选择，不得援引教材。',
    },
    voice: {
      rule: '语言指纹现在**挂在病上**（owner 第 6、7 条裁定：怎么说话就是在说哪张病）。`voices.items[].disease` 是这一套指纹的**主病**；`voices.items[].covers` 是它同时代言的其他病 id。由病反查指纹用 `voiceOfDisease()`。',
      conflict_rule: '一局结束时玩家认下的那张病，必须与「他怎么说话」收敛到的病一致：`voice_disease_conflict`。一致性由 tally 的 dominant（沿用 `min_tagged` 阈值与「并列取最后出现」的规则）→ 该指纹的 `disease` / `covers` 判定。',
      coverage_rule: '凡出现在任何事件 `activates` 里的病，**必须被恰好一套指纹覆盖**（candidate_without_voice）——否则会出现「候选里有它、但这一局没有台词特征」的病，那条冲突判据就会形同虚设。这也正是 ≥6 张病（owner 待裁 2 的默认）与「四套指纹对 4 张病」（owner 待裁 5）必须并存时唯一的出路：**四套指纹各自有一个主病，另外用 `covers` 兜住其余候选病**。',
      stage6_superseded: '🔧 阶段 6 的「调子不等于诊断」自阶段 7 起由提示词 §二 第 6 条取代：**调子就是诊断的一半**——它必须与玩家认下的病一致。被取代的那句在 design/presentation/开局门诊问诊.md §14.3 就地标了 🔧。',
    },
    diagnosis: {
      rule: '诊断栏由**医师**落笔写「初步诊断」：`record.columns` 里 `diagnosis` 的 `fill` 是 `derived`、`who` 是 `hospital`，取值来源是本局认下的病（`value_from: confirmed_disease`）。玩家只做「认」这一个动作——候选以回应形式钉在底部（数字键），**不新开一屏**（owner 待裁 4 的默认 (a)）。',
      not_a_label: '⚠️ 写上去的是**文书上的初步诊断**，不是给玩家看的标签。门诊侧法规把这一栏叫「初步印象」或「诊断」（《病历书写基本规范》第十三条；河南细则第二十三条门诊写「初步印象」）。**不会**在诊断栏里写任何治疗、量表分、护理等级。',
      treatment_stays_blank: '`treatment`（治疗意见）**仍留白**（owner 待裁 3 的默认 (a)）：医嘱尚无口径，阶段 5/6 的裁定不动。',
      basis: '《病历书写基本规范》第二章第十三条：初诊病历记录书写内容应当包括……诊断及治疗意见和医师签名等。逐字原文见 design/spec/material/ref/精神科门诊病历-书写规范-检索记录.md §2.1。',
    },
    ui: {
      what: '阶段 7 新增的上屏文案。⚠️ **界面代码里不许出现中文文案字面量**（提示词 §一 第 5 条），所以这一屏要说的话全在这儿；`{...}` 是占位符，由界面替换。本块与 `db.ui` 一样受文案 lint（漏内部词即报错）。',
      event_ask: '那件事之前，你过得是什么样的？先说那件事本身——「{title}」。',
      event_note: '院方在病历上记下了这件事。',
      candidate_basis: '因为你说的那件事——「{title}」——我们把它写在这儿：{label}。',
      candidate_basis_fallback: '你说的那件事——「{title}」——我们把它写在这儿。',
      candidate_prompt: '这几种，你看哪一个像你自己？',
      candidate_narrowed: '你说话的样子，已经把你带到「{label}」这一张上了。',
      candidate_none: '还没听出你说话的调子，先都摆在这儿。',
      confirm_action: '认下这一张',
      confirmed_note: '接诊医师把「{label}」写进了诊断栏。',
      voice_of_disease: '这张病在他嘴里：{voice}',
      voice_unknown_still: '还没听出你说话的调子。',
    },
    sources: [
      'design/spec/material/ref/诱因事件与生活事件-检索记录.md（阶段 7 新检索：生活事件与精神障碍的因果口径 · 首发与复发之别 · 多件事累积的反面 · 病历里诱因与前驱症状的写法）',
      'design/presentation/开局经历疾病接回.md（阶段 7 口径文档：链条五步 · 每步判据 · 退役/保留清单）',
      'design/entities/经历结构.md（存量口径；§十 的池子与并集口径自阶段 7 起退役，文件已就地标 🔧）',
      'design/entities/疾病结构.md（存量口径；§五 的并集诱發口径自阶段 7 起退役，文件已就地标 🔧）',
    ],
    retired_here: '🔧 自阶段 7 起，本文件里**不再**有「经历池 → 病并集 → 候选」这条链的任何环节：候选只由那件事的 activates 来。与它同批退役的存量口径在 data/opening.json 的 interview / interview.pool / quota 与 data/diseases.json 的 pool_rule 上就地标了退役说明（**键都不删**，存量测试仍在读）。',
  }
}

function census(wiring) {
  const { events, eventRule } = build()
  const odb = JSON.parse(readFileSync(OPENING, 'utf8'))
  const cdb = JSON.parse(readFileSync(CLINIC, 'utf8'))
  const ddb = JSON.parse(readFileSync(resolve(ROOT, 'data/diseases.json'), 'utf8'))
  const used = new Set(events.flatMap((e) => e.source_experiences))
  const diseaseMap = new Map()
  for (const e of events) for (const d of e.activates) diseaseMap.set(d, (diseaseMap.get(d) ?? 0) + 1)
  const sizes = events.map((e) => e.expansions.length).sort((a, b) => a - b)
  const med = sizes.length % 2 ? sizes[(sizes.length - 1) / 2] : (sizes[sizes.length / 2 - 1] + sizes[sizes.length / 2]) / 2
  const ax = {}
  for (const e of events) for (const x of new Set(e.expansions.map((p) => p.facet))) ax[x] = (ax[x] ?? 0) + 1
  const act = {}
  for (const e of events) act[e.activates.length] = (act[e.activates.length] ?? 0) + 1
  const mat = events.map((e) => e.source_experiences.length)
  const roster = ddb.items.filter((i) => i.always_on !== true)
  const voiced = new Set()
  for (const v of cdb.voices.items) {
    if (v.disease) voiced.add(v.disease)
    for (const d of v.covers ?? []) voiced.add(d)
  }
  return {
    events: events.length,
    diseases_covered: diseaseMap.size,
    activates_per_event: act,
    expansions: { min: sizes[0], median: med, max: sizes[sizes.length - 1] },
    expansion_axes: ax,
    locate_rules: wiring.locate.rules.length,
    locate_questions: wiring.locate.questions_used.length,
    fallback_event: wiring.locate.fallback_event,
    candidate_per_event: { min: Math.min(...events.map((e) => e.activates.length)), max: Math.max(...events.map((e) => e.activates.length)) },
    materials_per_event: { min: Math.min(...mat), max: Math.max(...mat), total: used.size },
    materials_used: used.size,
    materials_unused: odb.experiences.length - used.size,
    materials_total: odb.experiences.length,
    effects_terms_max: eventRule.effects_terms_max,
    roster: roster.length,
    roster_inherent: ddb.items.length - roster.length,
    voiced_diseases: voiced.size,
    candidates_without_voice: [...diseaseMap.keys()].filter((d) => !voiced.has(d)),
    diseases_without_any_event: roster.map((r) => r.id).filter((id) => !diseaseMap.has(id)),
    per_event: events.map((e) => ({
      id: e.id,
      title: e.title,
      activates: e.activates,
      expansions: e.expansions.length,
      effects: e.effects.attributes,
      materials: e.source_experiences,
    })),
  }
}

const mode = process.argv[2] ?? '--emit'
const { eventRule, events } = build()
const wiring = buildWiring()

if (mode === '--emit') {
  console.log(`${INDENT}"event_rule": ${stringifyBlock(eventRule, 1)},`)
  console.log(`${INDENT}"events": ${stringifyBlock(events, 1)},`)
  console.log(`${INDENT}"event_wiring": ${stringifyBlock(wiring, 1)},`)
} else if (mode === '--census') {
  console.log(JSON.stringify(census(wiring), null, 2))
} else if (mode === '--check') {
  const odb = JSON.parse(readFileSync(OPENING, 'utf8'))
  const cdb = JSON.parse(readFileSync(CLINIC, 'utf8'))
  const okEvent = JSON.stringify(odb.event_rule) === JSON.stringify(eventRule) && JSON.stringify(odb.events) === JSON.stringify(events)
  const okWire = JSON.stringify(cdb.event_wiring) === JSON.stringify(wiring)
  if (!okEvent) console.log('drift: data/opening.json 的 event_rule / events 与生成结果不一致，跑 --write')
  if (!okWire) console.log('drift: data/opening_clinic.json 的 event_wiring 与生成结果不一致，跑 --write')
  if (okEvent && okWire) console.log('ok: event_rule / events / event_wiring 三块都与生成结果一致')
  process.exit(okEvent && okWire ? 0 : 1)
} else if (mode === '--write') {
  let text = readFileSync(OPENING, 'utf8')
  text = spliceBlock(text, 'event_rule', eventRule, 'vocab')
  text = spliceBlock(text, 'events', events, 'disease_roster_moved')
  const parsed = JSON.parse(text)   // 写前先解析一遍：写出去的文件必须是合法 JSON
  if (parsed.events.length !== events.length) throw new Error('写出的 events 条数不对')
  writeFileSync(OPENING, text)

  let ctext = readFileSync(CLINIC, 'utf8')
  ctext = spliceBlock(ctext, 'event_wiring', wiring, 'compose')
  const cparsed = JSON.parse(ctext)
  if (cparsed.event_wiring.locate.rules.length !== LOCATE_RULES.length) throw new Error('写出的定位规则条数不对')
  writeFileSync(CLINIC, ctext)

  console.log(`ok: 已写入 data/opening.json（event_rule + events ${events.length} 件）与 data/opening_clinic.json（event_wiring ${LOCATE_RULES.length} 条定位规则）`)
} else {
  throw new Error(`未知模式 ${mode}（--emit / --check / --write / --census）`)
}
