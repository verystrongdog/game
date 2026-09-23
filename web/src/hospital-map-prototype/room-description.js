// 原型模块：按几何自动生成的房间描述。
//
// 来源：design/presentation/500床一层跑团地图原型.md §2.2（owner 2026-09-23 口径：
// 房间尚未命名，描述只按几何分类生成，不落正典）。
//
// 输入只有 data/hospital_ref/floor-one-enclosures.json 的边界顶点与面积。本模块
// 不读取图纸文字、不引用房间名称或用途、不产生地点 ID，也不建立通行关系。输出的
// 文本是原型呈现占位，任何"这是护士站/这是病房"的断言都超出它的依据。
//
// 分类判据全部是可比对的几何量：面积、短边、长边、长宽比、顶点数。不引入图纸
// 文字目视辨认结果——那需要 owner 逐间确认，见上文 §二 的边界条款。

export const ROOM_DESCRIPTION_STATUS = 'geometry-derived-placeholder-not-canon'

// 图纸北向为图面左侧（来源：上文 §一·校图坐标系），因此 +X 向图纸右侧即向南，
// +Y 向图纸上方即向东。分区只用来给出方位措辞，不声明建筑功能。
const NORTH_SUPPLY_SEAM_MILLIMETRES = -57700

const number = value => {
  const text = value.toFixed(1)
  return text.endsWith('.0') ? text.slice(0, -2) : text
}

function fnv1a(value) {
  let hash = 0x811c9dc5
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 0x01000193)
  }
  return hash >>> 0
}

function signedMillimetres(value) {
  const metres = number(Math.abs(value) / 1000)
  return `${value >= 0 ? '+' : '−'}${metres}`
}

function districtOf(centroid) {
  if (centroid.x < NORTH_SUPPLY_SEAM_MILLIMETRES) return '主体建筑以北的供应中心'
  const northSouth = centroid.x >= 0 ? '南半' : '北半'
  const eastWest = centroid.y >= 0 ? '东侧' : '西侧'
  return `主体建筑${northSouth}·${eastWest}`
}

export function measureEnclosure(enclosure) {
  if (!enclosure || !Array.isArray(enclosure.boundary) || enclosure.boundary.length < 3) {
    throw new TypeError('闭环必须提供至少三个边界顶点')
  }
  if (!Number.isFinite(enclosure.areaSquareMillimetres) || enclosure.areaSquareMillimetres <= 0) {
    throw new TypeError('闭环必须提供正的整数平方毫米面积')
  }
  const xs = enclosure.boundary.map(point => point.x)
  const ys = enclosure.boundary.map(point => point.y)
  const widthMillimetres = Math.max(...xs) - Math.min(...xs)
  const heightMillimetres = Math.max(...ys) - Math.min(...ys)
  const shortSideMillimetres = Math.min(widthMillimetres, heightMillimetres)
  const longSideMillimetres = Math.max(widthMillimetres, heightMillimetres)
  return {
    areaSquareMetres: enclosure.areaSquareMillimetres / 1_000_000,
    shortSideMetres: shortSideMillimetres / 1000,
    longSideMetres: longSideMillimetres / 1000,
    // 零宽闭环只可能来自退化几何；用 1 毫米兜底，避免出现 Infinity 进入文案。
    aspectRatio: longSideMillimetres / Math.max(shortSideMillimetres, 1),
    vertexCount: enclosure.boundary.length,
    centroid: {
      x: (Math.min(...xs) + Math.max(...xs)) / 2,
      y: (Math.min(...ys) + Math.max(...ys)) / 2,
    },
  }
}

// 判据按顺序取第一个命中项；最后一项永远命中，保证 189 个闭环都有分类。
// 顺序本身是口径：先看形状（长宽比），再看尺度（面积）。一层最长的走道面积
// 达到 144.9 m²，若面积优先就会被读成"大跨空间"；反过来，452.9 m² 的空场
// 长宽比 3.09，若形状优先且不设面积下限又会被读成"短通道"。
//
// 导出整张表供测试逐条变体检查措辞：分类词与描述文案都不得出现房间名称。
export const roomCategories = [
  {
    id: 'corridor',
    label: '长走道',
    matches: measured => measured.aspectRatio >= 5,
    variants: [
      measured => `一条狭长的通行空间：${number(measured.longSideMetres)} 米长、${number(measured.shortSideMetres)} 米宽，长宽比约 ${number(measured.aspectRatio)} 比 1，面积 ${number(measured.areaSquareMetres)} 平方米。两端和侧面都由墙线收口——形状上更接近一段通过用的距离，而不是一个停留用的房间。`,
      measured => `${number(measured.longSideMetres)} 米 × ${number(measured.shortSideMetres)} 米的长条闭环，两端都封在墙里，中间没有房间级别的分隔。它是这一层里最像通道的几种几何形状之一。`,
      measured => `窄而直的一段，${number(measured.areaSquareMetres)} 平方米，宽度只有 ${number(measured.shortSideMetres)} 米。把它读成一段距离而不是一个房间，更符合它现在的形状。`,
    ],
  },
  {
    id: 'open-hall',
    label: '大跨空间',
    matches: measured => measured.areaSquareMetres >= 100,
    variants: [
      measured => `这一层的墙线在这里让开了一大片：${number(measured.areaSquareMetres)} 平方米，最长的一边 ${number(measured.longSideMetres)} 米，短边 ${number(measured.shortSideMetres)} 米。${measured.vertexCount} 个顶点围出一个基本不转折的轮廓，内部没有任何隔墙穿过。站在其中，几何上最直接的印象是空——视线可以从一端走到另一端。`,
      measured => `一片大跨度空间，${number(measured.longSideMetres)} 米 × ${number(measured.shortSideMetres)} 米，${number(measured.areaSquareMetres)} 平方米。墙线在四周绕成一圈完整闭环，里面没有再分出小间。这个尺度在这一层属于少数几处。`,
      measured => `${number(measured.areaSquareMetres)} 平方米的无隔断空间，短边 ${number(measured.shortSideMetres)} 米、长边 ${number(measured.longSideMetres)} 米。边界只有 ${measured.vertexCount} 个转折点，说明四周墙线基本是直着走完的。`,
    ],
  },
  {
    id: 'passage',
    label: '短通道',
    matches: measured => measured.aspectRatio >= 2.5,
    variants: [
      measured => `一个不方正的闭环：${number(measured.longSideMetres)} 米 × ${number(measured.shortSideMetres)} 米，${number(measured.areaSquareMetres)} 平方米，长宽比约 ${number(measured.aspectRatio)} 比 1。它介于房间与通道之间——够宽，可以停人；够长，不像一个终点。`,
      measured => `${number(measured.areaSquareMetres)} 平方米的长方形空间，进深 ${number(measured.shortSideMetres)} 米、面宽 ${number(measured.longSideMetres)} 米。这种比例通常出现在门厅、过厅，或者把两处空间接起来的地方。`,
      measured => `长条形闭环，${number(measured.areaSquareMetres)} 平方米。墙线沿长边直走了 ${number(measured.longSideMetres)} 米才收口，短边只有 ${number(measured.shortSideMetres)} 米。`,
    ],
  },
  {
    id: 'standard-room',
    label: '标准房间模块',
    matches: measured => measured.areaSquareMetres >= 40,
    variants: [
      measured => `一个接近方正的房间：${number(measured.shortSideMetres)} 米 × ${number(measured.longSideMetres)} 米，${number(measured.areaSquareMetres)} 平方米，边界 ${measured.vertexCount} 个顶点。尺寸正落在这一层反复出现的那种房间模块上。`,
      measured => `${number(measured.areaSquareMetres)} 平方米的方形空间，两边分别是 ${number(measured.shortSideMetres)} 米和 ${number(measured.longSideMetres)} 米。四壁完整闭合，边界上没有超出矩形范围的凹口。`,
      measured => `长方形房间模块，${number(measured.longSideMetres)} 米 × ${number(measured.shortSideMetres)} 米。和这一层其他同尺寸闭环相比，它没有多出任何凹口，是被完整围住的一格。`,
    ],
  },
  {
    id: 'room',
    label: '常规房间',
    matches: measured => measured.areaSquareMetres >= 18,
    variants: [
      measured => `一个常规大小的空间：${number(measured.areaSquareMetres)} 平方米，${number(measured.shortSideMetres)} 米 × ${number(measured.longSideMetres)} 米。四面墙线把它围成一个干净的闭环，没有多余的转角。`,
      measured => `${number(measured.areaSquareMetres)} 平方米，进深 ${number(measured.shortSideMetres)} 米、面宽 ${number(measured.longSideMetres)} 米。按尺寸推，这里放得下一张床、一张桌子和一条走动的通道——但"放得下"是从数字推的，不是屋里真的有什么。`,
      measured => `中等大小的闭环，${number(measured.areaSquareMetres)} 平方米，边界 ${measured.vertexCount} 个顶点。形状简单，长宽比 ${number(measured.aspectRatio)} 比 1，没有明显的异形段。`,
    ],
  },
  {
    id: 'small-room',
    label: '小房间',
    matches: measured => measured.areaSquareMetres >= 10,
    variants: [
      measured => `一个小闭环：${number(measured.areaSquareMetres)} 平方米，${number(measured.shortSideMetres)} 米 × ${number(measured.longSideMetres)} 米。空间窄，转一次身就能把四周看遍。`,
      measured => `${number(measured.areaSquareMetres)} 平方米的窄小空间。墙线转折很少（${measured.vertexCount} 个顶点），形状简单到不像一个能待很久的地方。`,
      measured => `紧凑的围合，${number(measured.areaSquareMetres)} 平方米。短边 ${number(measured.shortSideMetres)} 米，长边 ${number(measured.longSideMetres)} 米。`,
    ],
  },
  {
    id: 'shaft',
    label: '极小围合',
    matches: () => true,
    variants: [
      measured => `一个很小的围合：${number(measured.areaSquareMetres)} 平方米。这个尺度通常只够竖井、管井或设备检修口，但当前没有任何依据能确认它具体是什么。`,
      measured => `${number(measured.areaSquareMetres)} 平方米的极小闭环，${number(measured.shortSideMetres)} 米 × ${number(measured.longSideMetres)} 米。人在里面无法活动，墙线数据只能说明它被围起来了。`,
      measured => `${number(measured.areaSquareMetres)} 平方米。${measured.vertexCount} 个顶点围出的一个几乎没有余量的空腔。`,
    ],
  },
]

export function roomCategoryOf(measured) {
  return roomCategories.find(category => category.matches(measured))
}

export function describeRoom(enclosure) {
  const measured = measureEnclosure(enclosure)
  const category = roomCategoryOf(measured)
  const variantIndex = fnv1a(enclosure.id) % category.variants.length
  const areaText = `${number(measured.areaSquareMetres)} m²`
  return {
    status: ROOM_DESCRIPTION_STATUS,
    enclosureId: enclosure.id,
    categoryId: category.id,
    categoryLabel: category.label,
    areaText,
    shapeText: `${number(measured.shortSideMetres)} × ${number(measured.longSideMetres)} m`,
    district: districtOf(measured.centroid),
    description: category.variants[variantIndex](measured),
    facts: [
      `面积 ${areaText}`,
      `短边 ${number(measured.shortSideMetres)} m · 长边 ${number(measured.longSideMetres)} m · 长宽比 ${number(measured.aspectRatio)} 比 1`,
      `边界 ${measured.vertexCount} 个顶点`,
      `位置 ${districtOf(measured.centroid)}`,
      `图纸坐标 X ${signedMillimetres(measured.centroid.x)} m · Y ${signedMillimetres(measured.centroid.y)} m`,
    ],
    basis: '依据：data/hospital_ref/floor-one-enclosures.json 的边界顶点与面积（平面闭环计算输出）。短边、长边与长宽比取边界包围盒，不是逐段墙长；本描述不含房间名称与用途。',
    unknown: '房间名称、用途、开口位置、家具、光线与声音都没有依据，尚未确定。',
    centroid: measured.centroid,
  }
}

export function createRoomDescriptionIndex(enclosures) {
  return new Map(enclosures.map(enclosure => [enclosure.id, describeRoom(enclosure)]))
}
