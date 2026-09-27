/**
 * 池子口径的实测脚本：跑一遍**全部已答前缀**，报四个数。
 *
 *   node web/scripts/pool-census.mjs          # 只报数
 *   node web/scripts/pool-census.mjs --json    # 连最坏前缀一起打印
 *
 * 四个数（design/entities/经历结构.md §十.4）：
 *   ① 分支总数            ② 需要放宽的分支数
 *   ③ 放宽后最坏池子规模   ④ 最坏情况下的地方跨度
 * 外加：池病并集的上下界、起手种子换过的分支数、每一级放宽各占多少分支。
 *
 * 它不估任何数：全部由 `poolCensus(db, ddb)` 枚举出来（第 4–7 问的每一种答案状态）。
 */
import db from '../../data/opening.json' with { type: 'json' }
import ddb from '../../data/diseases.json' with { type: 'json' }
import { answerCardinality, interviewQuestions, poolCensus, poolFloors } from '../src/character-creation/opening.js'

const t0 = Date.now()
const census = poolCensus(db, ddb)
const ms = Date.now() - t0

const floors = poolFloors(db, ddb)
const reachable = ddb ? ddb.filter_rule.roster_size - census.maxDiseaseUnion : null

const lines = [
  `池子口径实测 · 数据 data/opening.json（${db.experiences.length} 段）· data/diseases.json`,
  `参与相符判断的问：${census.questions.join(' · ')}`,
  `① 分支总数（合法答案状态，含「还没答」）  ${census.branches}`,
  `   被非法组合判掉的状态                ${census.illegalStates}（按钮上就灰掉，不算分支）`,
  `② 需要放宽的分支数                    ${census.relaxedBranches}`
    + `（${((census.relaxedBranches / census.branches) * 100).toFixed(1)}%）`,
  `③ 放宽后最坏池子规模                  ${census.minSize} 段（下限 ${floors.minSize}）`,
  `④ 最坏情况下地方跨度                  ${census.minContexts} 个地方（下限 ${floors.minContexts}）`,
  `池病并集                              ${census.minDiseaseUnion}–${census.maxDiseaseUnion}`
    + `（pool_rule ${floors.minDiseases}–${floors.maxDiseases}）`,
  `每条候选池子的规模上限（display_size） ${db.interview.pool.display_size}`,
  `起手种子换过的分支                    ${census.seedRetries}`,
  `池子撑不起一局的分支                  ${census.floorBreaks}`,
  `每一级放宽各占多少分支                ${Object.entries(census.levelCounts).map(([k, v]) => `${k} ${v}`).join(' · ')}`,
  `名册 ${ddb.filter_rule.roster_size} 张病 · 池病并集最大 ${census.maxDiseaseUnion}`
    + ` ⟹ 本局至少 ${reachable} 张病结构性不可达`,
  `枚举耗时 ${ms} ms`,
]

console.log(lines.join('\n'))

if (process.argv.includes('--json')) {
  console.log('\n最坏池子（规模最小 / 跨度最小）：')
  console.log(JSON.stringify({
    worstSize: { answers: census.worstSize?.answers, pool: census.worstSize?.pool?.ids, level: census.worstSize?.pool?.level },
    worstContexts: { answers: census.worstContexts?.answers, pool: census.worstContexts?.pool?.ids, level: census.worstContexts?.pool?.level },
  }, null, 2))
}

console.log('\n八问的答案闭集规模：')
for (const q of answerCardinality(db)) {
  console.log(`  ${q.id.padEnd(20)} ${q.matches ? '参与池子' : '只写病历'} · ${q.values} 个取值`
    + `${q.multi ? ` · ${q.answers} 种多选组合` : ''}`)
}
console.log(`问数 ${interviewQuestions(db).length}`)
