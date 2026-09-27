import { describe, expect, test } from 'bun:test'
import db from '../../../data/opening.json'
import ddb from '../../../data/diseases.json'
import {
  clauseHitsOnDisease,
  closedDoors,
  describeDisease,
  diseaseById,
  diseaseCanStillPick,
  diseaseCandidates,
  diseaseCoverage,
  diseaseEmptyLabel,
  diseaseLabel,
  diseaseValues,
  diseaseViewIndex,
  diseasesOfExperience,
  doorVisible,
  evalDiseaseView,
  formOf,
  migrationCoverage,
  openDoors,
  queryDiseases,
  renderDiseaseTable,
  rosterOf,
  sourcesOf,
  validateDiseases,
} from './diseases.js'

/**
 * 开局疾病契约。
 *
 * 这些断言是契约的**可执行形式**——全仓门禁已于 2026-09-17 撤销，这是唯一的机械补偿。
 * 来源：design/entities/疾病结构.md §六（不变量）与 §七（反例清单）。
 */

const CROSS_CODES = ['dead_disease', 'disease_unknown', 'experience_without_disease', 'experience_too_many_profiles', 'inherent_not_a_candidate']
const structural = (r) => r.errors.filter((e) => !CROSS_CODES.includes(e.code)).map((e) => e.code)

describe('契约自洽', () => {
  test('结构校验零错误（不看经历契约）', () => {
    expect(structural(validateDiseases(null, ddb))).toEqual([])
  })

  test('全文校验零错误：26 张病全部有来源经历（21 条 dead_disease 已闭合）', () => {
    const r = validateDiseases(db, ddb)
    expect(structural(r)).toEqual([])
    // 内容批落地后，26 张病每张都有 ≥2 条经历指向（filter_rule.experiences_per_profile_min）。
    expect(r.errors).toEqual([])
  })

  test('警告只有两类，且都被记录在案', () => {
    const r = validateDiseases(db, ddb)
    const codes = r.warnings.map((w) => w.code).sort()
    // paused_door_present —— 7 扇遭遇门原样保留、界面不渲染（战斗内容暂不碰）
    // thin_view ×2 —— 接管式只有 DID 一张、固有项只有《无法离开医院》一张（canon 事实）
    expect(codes).toEqual(['paused_door_present', 'thin_view', 'thin_view'])
  })
})

describe('26 病逐条迁移', () => {
  test('名册 26 条 + 固有项 1 条', () => {
    expect(ddb.items).toHaveLength(27)
    expect(rosterOf(ddb)).toHaveLength(26)
  })

  test('id 与 §4.1 行号一一对应，首尾正确', () => {
    expect(diseaseById(ddb, 'dis_0001').label).toBe('PTSD')
    expect(diseaseById(ddb, 'dis_0026').label).toBe('ADHD')
    for (const r of rosterOf(ddb)) {
      const n = Number(r.id.slice(4))
      expect(r.source).toContain(`第 ${n} 行`)
    }
  })

  test('形态派生复现 §4.2 的 9 / 8 / 1 / 8', () => {
    expect(migrationCoverage(ddb).byForm).toEqual({ intrusive: 9, belief: 8, takeover: 1, swing: 8 })
  })

  test('开门 / 关门分布复现 §4.1 的括号', () => {
    const c = migrationCoverage(ddb)
    expect(c.byOpenKind).toEqual({ dialogue: 8, investigation: 11, space: 2, encounter: 5 })
    expect(c.byCloseKind).toEqual({ investigation: 5, space: 11, dialogue: 8, encounter: 2 })
  })

  test('24 张有加成、2 张没有（未分化型 SZ 与分裂情感）', () => {
    const c = migrationCoverage(ddb)
    expect(c.withBonus).toBe(24)
    expect(c.withoutBonus).toEqual(['dis_0007', 'dis_0022'])
  })

  test('加成属性分布复现 观察10 · 巧手5 · 沟通4 · 意志3 · 体格2', () => {
    const n = {}
    for (const r of rosterOf(ddb)) if (r.bonus) n[r.bonus.attr] = (n[r.bonus.attr] ?? 0) + 1
    expect(n).toEqual({ observation: 10, finesse: 5, communication: 4, will: 3, physique: 2 })
  })

  test('只有 ADHD 带「连做 ≥3 次」门槛', () => {
    const withAtLeast = rosterOf(ddb).filter((r) => r.bonus?.at_least !== null && r.bonus !== null)
    expect(withAtLeast.map((r) => r.id)).toEqual(['dis_0026'])
    expect(diseaseById(ddb, 'dis_0026').bonus.at_least).toBe(3)
  })

  test('开门文案是 canon 原文（抽查）', () => {
    expect(diseaseById(ddb, 'dis_0005').doors.find((d) => d.open).what).toBe('别人想干什么你比他自己先知道')
    expect(diseaseById(ddb, 'dis_0024').doors.find((d) => !d.open).what).toBe('你越来越不想解释：每累积一次羞耻，「解释/辩解」少一个')
  })
})

describe('形态是派生的，不是字段', () => {
  test('记录里没有 form / form_id 这类归属键', () => {
    for (const r of ddb.items) {
      for (const k of ['form', 'form_id', 'category', 'theme', 'parent', 'lineage', 'class', 'tags']) {
        expect(Object.keys(r)).not.toContain(k)
      }
    }
  })

  test('形态判据只用玩家看得见的三件事', () => {
    expect(ddb.form_rule.derived_from).toEqual(['break_in', 'speaker_change', 'phase_cycle'])
    expect(formOf(ddb, 'dis_0001').label).toBe('闯入式')
    expect(formOf(ddb, 'dis_0008').label).toBe('接管式')
    expect(formOf(ddb, 'dis_0017').label).toBe('摆荡式')
    expect(formOf(ddb, 'dis_0009').label).toBe('信念式')
  })

  test('形态可以作为查询条件（伪 facet）', () => {
    const rec = diseaseById(ddb, 'dis_0008')
    expect(clauseHitsOnDisease(ddb, rec, { facet: 'form', in: ['takeover'] })).toBe(true)
    expect(clauseHitsOnDisease(ddb, rec, { facet: 'form', not_in: ['takeover'] })).toBe(false)
  })
})

describe('门', () => {
  test('每张候选病卡恰好一开一关', () => {
    for (const r of rosterOf(ddb)) {
      expect(r.doors.filter((d) => d.open)).toHaveLength(1)
      expect(r.doors.filter((d) => !d.open)).toHaveLength(1)
    }
  })

  test('关门必须可见：生效的每扇门都有撞到点', () => {
    for (const r of rosterOf(ddb)) {
      for (const d of r.doors) {
        if (doorVisible(ddb, d.kind).active) expect(d.where.length).toBeGreaterThan(0)
      }
    }
  })

  test('暂停的门不建模撞到点（战斗内容暂不碰）', () => {
    const paused = rosterOf(ddb).flatMap((r) => r.doors.filter((d) => !doorVisible(ddb, d.kind).active))
    expect(paused).toHaveLength(7)
    for (const d of paused) expect(d.where).toEqual([])
    expect(paused.every((d) => d.kind === 'encounter')).toBe(true)
  })

  test('PTSD 是「开遭遇门 + 关调查门」，且关门指向自问页', () => {
    expect(openDoors(ddb, 'dis_0001')[0].kindLabel).toBe('遭遇门')
    expect(openDoors(ddb, 'dis_0001')[0].paused).toBe(true)
    const close = closedDoors(ddb, 'dis_0001')[0]
    expect(close.what).toBe('慌起来时自问页不响应')
    expect(close.whereLabels).toEqual(['自问页'])
  })

  test('门类的启用状态来自词表，不写死在代码里', () => {
    expect(ddb.vocab.door_kind.values.find((v) => v.id === 'encounter').status).toBe('paused')
    expect(doorVisible(ddb, 'encounter').active).toBe(false)
    expect(doorVisible(ddb, 'dialogue').active).toBe(true)
  })
})

describe('视图（替代已删的 8 个父类）', () => {
  test('按门类浏览：说话 / 看得见的东西 / 走得进走不进', () => {
    expect(evalDiseaseView(ddb, 'view_by_door_dialogue')).toHaveLength(8)
    expect(evalDiseaseView(ddb, 'view_by_door_investigation')).toHaveLength(11)
    expect(evalDiseaseView(ddb, 'view_by_door_space')).toHaveLength(2)
  })

  test('形态视图合计 26', () => {
    const total = ['view_form_intrusive', 'view_form_belief', 'view_form_takeover', 'view_form_swing']
      .reduce((n, v) => n + evalDiseaseView(ddb, v).length, 0)
    expect(total).toBe(26)
  })

  test('视图计数与求值一致；无空视图', () => {
    for (const entry of diseaseViewIndex(ddb)) {
      expect(evalDiseaseView(ddb, entry.id)).toHaveLength(entry.count)
      expect(entry.count).toBeGreaterThan(0)
    }
  })

  test('「没有固定情境」正好是那两张（固有项不算）', () => {
    expect(evalDiseaseView(ddb, 'view_no_bonus').map((r) => r.id)).toEqual(['dis_0007', 'dis_0022'])
  })

  test('空值怎么念来自词表', () => {
    expect(diseaseEmptyLabel(ddb, 'visible')).toBe('没有固定情境')
    expect(diseaseEmptyLabel(ddb, 'speaker')).toBe('还是你')
    expect(diseaseEmptyLabel(ddb, 'door_kind')).toBeNull()
  })
})

describe('与经历契约的接缝', () => {
  test('候选 = 已选经历指向的并集，固有项不进候选', () => {
    const cands = diseaseCandidates(db, ddb, ['exp_0001', 'exp_0004']).map((d) => d.id)
    expect(cands.sort()).toEqual(['dis_0003', 'dis_0004', 'dis_0012'])
    expect(cands).not.toContain('dis_0027')
  })

  test('反查是现算的，病记录里没有反向键', () => {
    // 反查是现算的：结果必须与逐条扫一遍 records 完全一致（顺序即 db 顺序）。
    expect(sourcesOf(db, ddb, 'dis_0004')).toEqual(
      db.experiences.filter((r) => r.diseases.includes('dis_0004')).map((r) => r.id),
    )
    expect(sourcesOf(db, ddb, 'dis_0004').length).toBeGreaterThanOrEqual(ddb.filter_rule.experiences_per_profile_min)
    for (const r of ddb.items) expect(Object.keys(r)).not.toContain('from')
  })

  test('经历的 diseases 引用与疾病文件对得上', () => {
    for (const r of db.experiences) {
      expect(r.diseases.length).toBeGreaterThan(0)
      for (const d of r.diseases) expect(() => diseaseById(ddb, d)).not.toThrow()
    }
    expect(diseasesOfExperience(db, 'exp_0001')).toEqual(['dis_0003', 'dis_0004'])
  })

  test('候选筛选力：上界 20 < 名册 26 ⇒ 本局至少 6 张病不可能出现', () => {
    const cov = diseaseCoverage(db, ddb)
    expect(cov.roster).toBe(26)
    expect(cov.upperBound).toBe(20)
    expect(cov.ruledOutMin).toBe(6)
    expect(cov.upperBound).toBeLessThan(cov.roster)
  })

  test('屏 4 可点性：候选外不可点；未设上限时不报 selection_full', () => {
    expect(ddb.presentation.selected_diseases_max).toBeNull()
    const sel = ['exp_0001', 'exp_0004']
    expect(diseaseCanStillPick(db, ddb, sel, 'dis_0003').ok).toBe(true)
    expect(diseaseCanStillPick(db, ddb, sel, 'dis_0020').reasons.map((r) => r.code)).toEqual(['not_in_candidates'])
  })
})

describe('渲染', () => {
  test('describeDisease 给出卡面所需的一切，且不猜字符串', () => {
    const d = describeDisease(db, ddb, 'dis_0001')
    expect(d.label).toBe('PTSD')
    expect(d.plain).toBe('那件事结束了。它没有。')
    expect(d.formLabel).toBe('闯入式')
    expect(d.bonus.visibleLabel).toBe('危险可能重现')
    expect(d.bonus.amount).toBe(1)
    expect(d.bonus.amount).toBe(ddb.tiers.base_amount) // 数值只在 tiers
    expect(d.bonus.attrLabel).toBe('观察')
    expect(d.doors).toHaveLength(2)
    expect(d.cost).toBe('闪回：L5 全锁 + 目标锁死')
  })

  test('没有固定情境的两张读词表的空值文案', () => {
    const d = describeDisease(db, ddb, 'dis_0007')
    expect(d.bonus).toBeNull()
    expect(d.bonusEmptyLabel).toBe('没有固定情境')
  })

  test('固有项：不占候选、无门无加成、四条症状来自 §4.6', () => {
    const d = describeDisease(db, ddb, 'dis_0027')
    expect(d.alwaysOn).toBe(true)
    expect(d.doors).toEqual([])
    expect(d.signs.map((s) => s.label)).toEqual(['边界失效', '身份黏着', '夜晚保留', '证言失效'])
  })

  test('renderDiseaseTable 是派生视图，不是第二份数据', () => {
    const t = renderDiseaseTable(ddb)
    expect(t.split('\n')).toHaveLength(27)
    expect(t).toContain('dis_0001')
  })
})

describe('反例：这些写法必须被拒绝', () => {
  const mutate = (fn) => {
    const clone = JSON.parse(JSON.stringify(ddb))
    fn(clone)
    return validateDiseases(db, clone).errors.map((e) => e.code)
  }

  test('加单值归属键 → record_unknown_field', () => {
    expect(mutate((d) => { d.items[0].parent = '焦虑谱系' })).toContain('record_unknown_field')
    expect(mutate((d) => { d.items[0].form = 'intrusive' })).toContain('record_unknown_field')
  })

  test('语义藏回文案 → text_has_facet_word / text_has_digit', () => {
    expect(mutate((d) => { d.items[0].plain = '触发情境是对话门。' })).toContain('text_has_facet_word')
    expect(mutate((d) => { d.items[0].plain = '你数了 3 遍。' })).toContain('text_has_digit')
  })

  test('给没有形状的病加加成 → forbidden_combo', () => {
    expect(mutate((d) => { d.items[6].bonus = { visible: 'env_odd', attr: 'observation', at_least: null } }))
      .toContain('forbidden_combo')
  })

  test('固有项挂门 → forbidden_combo / inherent_has_doors', () => {
    const codes = mutate((d) => {
      d.items[26].doors = [{ kind: 'dialogue', open: true, what: 'x', where: ['ward'], used_for_group: ['kind'] }]
    })
    expect(codes).toContain('inherent_has_doors')
  })

  test('生效的门没有撞到点 → live_door_without_where（关门必须可见）', () => {
    expect(mutate((d) => { d.items[0].doors[1].where = [] })).toContain('live_door_without_where')
  })

  test('给暂停的门建模撞到点 → paused_door_models_where（战斗内容暂不碰）', () => {
    expect(mutate((d) => { d.items[0].doors[0].where = ['corridor'] })).toContain('paused_door_models_where')
  })

  test('关门被当成开门的去重键 → closed_door_has_group_key', () => {
    expect(mutate((d) => { d.items[0].doors[1].used_for_group = ['kind'] })).toContain('closed_door_has_group_key')
  })

  test('未登记取值 → door_kind_unknown，并让该门类成为死值', () => {
    const codes = mutate((d) => { d.items[0].doors[0].kind = 'fight' })
    expect(codes).toContain('door_kind_unknown')
  })

  test('候选筛选力失守（每条经历放宽到 3）→ candidate_filter_too_weak', () => {
    expect(mutate((d) => { d.filter_rule.profiles_per_experience_max = 3 })).toContain('candidate_filter_too_weak')
  })

  test('形态计数对不上 §4.2 → form_count_mismatch', () => {
    expect(mutate((d) => { d.items[0].break_in = false })).toContain('form_count_mismatch')
  })

  test('配置块丢掉 source → config_without_source', () => {
    expect(mutate((d) => { delete d.tiers.source })).toContain('config_without_source')
  })

  test('词表出现通配取值 → vocab_wildcard_forbidden', () => {
    expect(mutate((d) => { d.vocab.visible.values.push({ id: 'unknown', label: '未知' }) }))
      .toContain('vocab_wildcard_forbidden')
  })

  test('经历指向固有项 → inherent_not_a_candidate', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.experiences[0].diseases = ['dis_0027']
    expect(validateDiseases(clone, ddb).errors.map((e) => e.code)).toContain('inherent_not_a_candidate')
  })

  test('一条经历指向超过 2 张病 → experience_too_many_profiles（候选筛选力的前提）', () => {
    const clone = JSON.parse(JSON.stringify(db))
    clone.experiences[0].diseases = ['dis_0001', 'dis_0002', 'dis_0003']
    expect(validateDiseases(clone, ddb).errors.map((e) => e.code)).toContain('experience_too_many_profiles')
  })

  test('id 复用墓碑 → id_reused', () => {
    expect(mutate((d) => { d.tombstones = ['dis_0001'] })).toContain('id_reused')
  })
})
