/**
 * 开发夹具：少点十次的「开发默认人物」。
 *
 * 它只用于快速进入医院，**不是正典主角**，也不改变任何正式选择规则：
 * 一组合法的八问答案（含患者自述的那一句）+ 那一池里核对属实的十段 + 一张已解锁的疾病，
 * 全部由 `interviewPool` / `canSelect` / `diseaseCandidates` 跑出来。
 *
 * 生产构建不显示该入口（界面按 `import.meta.env.DEV` 判定）。
 * ⚠️ 记录 id 是数据层的主键，内容批一旦改动它们，这里必须同步——
 * `interview.test.js` 会用契约接口复核这组选择仍然合法。
 */

export const developmentDefaultCharacter = Object.freeze({
  label: '长期上夜班的那十年',
  /** 八问的答案（第 1 问自述与时间三问只写病历；第 2–5 问决定池子）。 */
  answers: Object.freeze({
    self_report: 'cannot_sleep',
    event: Object.freeze(['threat', 'failure']),
    context: 'work',
    relation: Object.freeze(['authority']),
    agency: 'coerced',
    onset: 'adulthood',
    duration_pattern: 'continuous',
    duration_span: 'long',
  }),
  experiences: Object.freeze([
    'exp_0003', // 签字的人是你
    'exp_0011', // 被人念出来的方案
    'exp_0122', // 口袋被翻过来
    'exp_0013', // 讲台边的位置
    'exp_0101', // 断了的粉笔
    'exp_0149', // 念到一半
    'exp_0246', // 回头看的人
    'exp_0407', // 门口的脚步声
    'exp_0108', // 末班车开走了
    'exp_0243', // 床底下的夜
  ]),
  diseases: Object.freeze(['dis_0011']), // 广泛性焦虑障碍
});
