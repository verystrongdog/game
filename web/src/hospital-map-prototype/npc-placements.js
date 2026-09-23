// 原型模块：一层地图上的"开局人物"落位。
//
// 来源：design/presentation/500床一层跑团地图原型.md §2.3（owner 2026-09-23 口径：
// 房间尚未命名，人物先落在与驻地几何相称的闭环上；落位是原型占位，不是正典）。
//
// 驻地依据：design/spec/material/NPC生态台账.md（1F 员工队列、患者床号登记与
// 病区归属）。时段与活动取值必须与 web/src/dialogue/npcs/*.js 的 situations
// 逐字一致，否则对应节点永远不会命中——那是数据错误，不是内容缺失。
//
// 未做的事：这里不建立通行关系、不写玩家出生点、不声明"这个闭环就是护士站"。
// 每个落位只声称两件事：该 NPC 此刻在哪个语义地点（来自人物数据），以及地图上
// 先用哪个几何闭环来表示它（占位，待房间命名后替换）。

export const NPC_PLACEMENT_STATUS = 'prototype-placeholder-not-canon'

// 语义地点来自对话数据的 locations 取值；标签只用于呈现。
export const locationLabels = {
  nurse_station: '护士站',
  north_ward: '北侧病区',
  south_ward: '南侧病区',
  activity_room: '活动室',
  basketball_court: '篮球场',
}

/**
 * 一处落位。
 * - npcId     必须存在于 web/src/dialogue/npcs/index.js 的 npcDialogues
 * - time      morning / afternoon / night，与对话数据的时段取值一致
 * - locationId 语义地点，用于喂给对话运行时的 situations 求值
 * - activity  可选；只有与人物数据 situations 完全一致时才写，否则留空
 * - enclosureId 几何占位闭环，必须存在于 floor-one-enclosures.json
 * - offset    毫米偏移，用于把同一闭环内的多个人物标记错开
 */
export const npcPlacements = [
  // 郑晓敏：住院楼 1F 护士站（NPC生态台账 §员工侧）。夜里不做落位——她夜间是否仍在
  // 护士站是台账 §七⑬ 明确挂着的未决项，原型不替它作答。
  {
    npcId: 'zheng_xiaomin',
    time: 'morning',
    locationId: 'nurse_station',
    enclosureId: 'f1-enclosure-1a35886b',
    basis: '驻地=1F 护士站；占位闭环取主体建筑中央、贴近两翼走道的中等房间（30.9 m²）。',
  },
  {
    npcId: 'zheng_xiaomin',
    time: 'afternoon',
    locationId: 'south_ward',
    enclosureId: 'f1-enclosure-72d0ab2d',
    activity: '发药并擦门把手',
    basis: '人物数据 situations 指定下午在南侧病区查房；占位闭环取南翼标准房间模块（47.6 m²）。',
  },
  // 谭丽娟：唯一的落位是夜班护士站——台账称她是"夜晚护士站投影的原型"。
  {
    npcId: 'tan_lijuan',
    time: 'night',
    locationId: 'nurse_station',
    enclosureId: 'f1-enclosure-1a35886b',
    offset: { x: 1200, y: -1200 },
    basis: '驻地=1F 夜班；占位闭环与郑晓敏同一处护士站闭环，用偏移区分两个标记。',
  },
  // 吴桐：B2 女区 11 床（床号登记行）。下午的 basketball_court 没有几何候选，故意留空。
  {
    npcId: 'wu_tong',
    time: 'morning',
    locationId: 'north_ward',
    enclosureId: 'f1-enclosure-c5bb30f9',
    basis: '人物数据 situations 指定夜间在北侧病区；白天沿用同一病区闭环。',
  },
  {
    npcId: 'wu_tong',
    time: 'night',
    locationId: 'north_ward',
    enclosureId: 'f1-enclosure-c5bb30f9',
    activity: '盖着被子核对数字',
    basis: '人物数据 situations 的夜间入口；占位闭环取北翼标准房间模块（47.6 m²）。',
  },
  // 周卫国：B1 男区 7 床。下午在活动室修轮椅刹车，夜间在南区等走廊天亮。
  {
    npcId: 'zhou_weiguo',
    time: 'morning',
    locationId: 'south_ward',
    enclosureId: 'f1-enclosure-6dd35469',
    basis: '床号登记：B1 男区 7 床；占位闭环取南翼标准房间模块（47.6 m²）。',
  },
  {
    npcId: 'zhou_weiguo',
    time: 'afternoon',
    locationId: 'activity_room',
    enclosureId: 'f1-enclosure-3f7c5248',
    offset: { x: 0, y: 2500 },
    activity: '修轮椅刹车',
    basis: '人物数据 situations 的下午入口；占位闭环取南翼大房间（117.5 m²，9.6×22.5 m），与空间文档「活动室 8×12 m+」的尺度相称。',
  },
  {
    npcId: 'zhou_weiguo',
    time: 'night',
    locationId: 'south_ward',
    enclosureId: 'f1-enclosure-6dd35469',
    activity: '坐着等走廊天亮',
    basis: '人物数据 situations 的夜间入口；与同病区白天落位同一闭环。',
  },
  // 唐念安：B2 女区。下午在活动室织毛衣，夜间在南区床边读小说。
  {
    npcId: 'tang_nianan',
    time: 'morning',
    locationId: 'south_ward',
    enclosureId: 'f1-enclosure-f89b4687',
    basis: '病区归属：B2 女区；占位闭环取南翼标准房间模块（47.6 m²），与周卫国隔一间。',
  },
  {
    npcId: 'tang_nianan',
    time: 'afternoon',
    locationId: 'activity_room',
    enclosureId: 'f1-enclosure-3f7c5248',
    offset: { x: 0, y: -2500 },
    activity: '织一件小毛衣',
    basis: '人物数据 situations 的下午入口；与周卫国共用活动室闭环，用偏移错开标记。',
  },
  {
    npcId: 'tang_nianan',
    time: 'night',
    locationId: 'south_ward',
    enclosureId: 'f1-enclosure-f89b4687',
    activity: '在床边读小说',
    basis: '人物数据 situations 的夜间入口；与同病区白天落位同一闭环。',
  },
]

// 没有几何候选的语义地点：写在这里，避免以后被当成漏做。
export const unmappedLocations = [
  {
    locationId: 'basketball_court',
    npcId: 'wu_tong',
    reason: '篮球场是户外场地，当前 189 个几何闭环全部来自楼内墙线，没有可用的候选闭环。',
  },
]

// 身份边界：人物数据里的 displayName 在玩家未取得身份前是"陌生人"。原型保留这一层，
// 只把未识状态降级显示（标记变暗 + 未识角标），以免原型连测试都无法操作。
export function placementLabel(npc) {
  return npc?.identityKnown ? npc.displayName : npc?.displayName || npc?.name || ''
}

export function validatePlacements({ placements = npcPlacements, npcIds, enclosureIds } = {}) {
  const knownNpcs = npcIds ? new Set(npcIds) : null
  const knownEnclosures = enclosureIds ? new Set(enclosureIds) : null
  const seen = new Set()
  for (const placement of placements) {
    if (knownNpcs && !knownNpcs.has(placement.npcId)) {
      throw new TypeError(`落位引用了不存在的人物：${placement.npcId}`)
    }
    if (knownEnclosures && !knownEnclosures.has(placement.enclosureId)) {
      throw new TypeError(`落位引用了不存在的几何闭环：${placement.enclosureId}`)
    }
    if (!locationLabels[placement.locationId]) {
      throw new TypeError(`落位使用了未登记的语义地点：${placement.locationId}`)
    }
    if (!['morning', 'afternoon', 'night'].includes(placement.time)) {
      throw new TypeError(`落位使用了未登记的时段：${placement.time}`)
    }
    const key = `${placement.npcId}@${placement.time}`
    if (seen.has(key)) throw new TypeError(`同一人物在同一时段只能有一处落位：${key}`)
    seen.add(key)
    if (!placement.basis) throw new TypeError(`落位缺少依据说明：${key}`)
  }
  return placements
}

export function placementsAtTime(time, placements = npcPlacements) {
  return placements.filter(placement => placement.time === time)
}

export function placementFor(npcId, time, placements = npcPlacements) {
  return placements.find(placement => placement.npcId === npcId && placement.time === time) || null
}
