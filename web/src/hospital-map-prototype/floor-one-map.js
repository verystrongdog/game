// PROTOTYPE — semantic layer for the 500-bed, scheme-one, floor-one map.
// Coordinates are approximate percentages calibrated for interaction, not CAD measurements.
// 来源：design/presentation/500床一层跑团地图原型.md §一、§三—§四。
export const floorOneMap = {
  id: 'hospital_500_scheme_1_floor_1',
  source: {
    vector: 'data/hospital_ref/vector/page-26.svg',
    rasterReference: 'data/hospital_ref/full/page-26.png',
  },
  coordinateSystem: {
    // Intersection obtained by extending the corresponding perimeter dimension axes.
    origin: { x: 46.3933, y: 56.4691 },
    xPositive: 'page-right',
    yPositive: 'page-up',
    structuralGrid: {
      // East-west axes: continuous across the plan from the overall perimeter ruler.
      x: [
        { position: 8.6339, millimetres: -95200 }, { position: 11.616, millimetres: -87700 },
        { position: 14.588, millimetres: -80200 }, { position: 17.5599, millimetres: -72700 },
        { position: 20.542, millimetres: -65200 }, { position: 23.5039, millimetres: -57700 },
        { position: 25.9017, millimetres: -51700 }, { position: 30.2492, millimetres: -40700 },
        { position: 31.0397, millimetres: -38700 },
        { position: 33.6591, millimetres: -32100 }, { position: 34.8479, millimetres: -29100 },
        { position: 37.5882, millimetres: -22200 }, { position: 40.5702, millimetres: -14700 },
        { position: 43.5422, millimetres: -7200 }, { position: 46.3933, millimetres: 0 },
        { position: 49.3754, millimetres: 7500 }, { position: 52.3474, millimetres: 15000 },
        { position: 54.5269, millimetres: 20500 }, { position: 55.3194, millimetres: 22500 },
        { position: 57.9387, millimetres: 29100 },
        { position: 59.1275, millimetres: 32100 }, { position: 61.8678, millimetres: 39000 },
        { position: 64.8398, millimetres: 46500 }, { position: 67.8118, millimetres: 54000 },
        { position: 70.7939, millimetres: 61500 }, { position: 73.7659, millimetres: 69000 },
        { position: 76.7379, millimetres: 76500 }, { position: 78.9744, millimetres: 82125 },
        { position: 79.7199, millimetres: 84000 },
        { position: 82.4501, millimetres: 90900 }, { position: 83.6389, millimetres: 93900 },
        { position: 86.3792, millimetres: 100800 }, { position: 87.1751, millimetres: 102800 },
      ],
      // North-south axes: overall ruler only; excludes the north-side central-supply local grid.
      y: [
        { position: 20.1197, millimetres: 64800 }, { position: 23.8245, millimetres: 58200 },
        { position: 25.5058, millimetres: 55200 }, { position: 27.4366, millimetres: 51750 },
        { position: 29.3673, millimetres: 48300 },
        { position: 33.2431, millimetres: 41400 }, { position: 37.1188, millimetres: 34500 },
        { position: 40.9946, millimetres: 27600 }, { position: 44.8561, millimetres: 20700 },
        { position: 48.7318, millimetres: 13800 }, { position: 52.5933, millimetres: 6900 },
        { position: 54.5312, millimetres: 3450 }, { position: 56.4691, millimetres: 0 },
        { position: 58.1505, millimetres: -3000 },
        { position: 61.5133, millimetres: -9000 }, { position: 64.876, millimetres: -15000 },
        { position: 69.0938, millimetres: -22500 },
      ],
      // North-supply local north-south axes from the plan's northernmost ruler.
      northSupply: {
        northOfXMillimetres: -57700,
        y: [
          { position: 45.5258, millimetres: 19500 }, { position: 49.7435, millimetres: 12000 },
          { position: 53.947, millimetres: 4500 }, { position: 58.1505, millimetres: -3000 },
          { position: 62.3682, millimetres: -10500 }, { position: 66.5717, millimetres: -18000 },
          { position: 70.7751, millimetres: -25500 }, { position: 74.9929, millimetres: -33000 },
          { position: 79.1821, millimetres: -40500 },
        ],
      },
    },
  },
  initialLocation: 'entrance',
  locations: [
    // 来源：design/presentation/500床一层跑团地图原型.md §三·第二轮区域纠错。
    { id: 'entrance', name: '门诊入口', x: 86.2, y: 36, region: '84,32 87.5,32 87.5,40 84,40', summary: '图纸南侧的门诊外门；由此进入门诊诊室与候诊空间。' },
    { id: 'outpatient', name: '门诊区', x: 79, y: 38, region: '74.5,31 83,31 83,44 74.5,44', summary: '图纸明确标注的门诊诊室与内部候诊空间。' },
    { id: 'emergency', name: '急诊区', x: 81, y: 55, region: '77.5,50 85,50 85,59 77.5,59', summary: '图纸急诊入口内侧的诊室、护士与抢救空间。' },
    { id: 'south_courtyard', name: '南侧景观庭院', x: 69, y: 41, region: '64,24 75,24 75,57 64,57', summary: '南病房楼与门诊建筑之间的椭圆景观庭院。' },
    // 来源：design/presentation/500床一层跑团地图原型.md §三·已校准房间。
    { id: 'nurse_station', name: '南病房护士站', x: 58, y: 60.8, region: '56.5,59.3 59.5,59.3 59.5,62.3 56.5,62.3', summary: '南病房公共端的弧形护士工作区；交接本、治疗盘和好日子本在这里相遇。' },
    { id: 'south_ward', name: '南病房楼', x: 58.5, y: 41, region: '55,25 62.5,25 62.5,58 55,58', summary: '位于中央球场南侧的病房楼；在图面上是右侧住院单元。' },
    { id: 'basketball_court', name: '中央篮球活动场', x: 46.4, y: 40, region: '39,14 55,14 55,58 39,58', summary: '两栋病房之间有两块画出完整边线的篮球活动场。' },
    { id: 'activity_room', name: '活动室', x: 45.3, y: 68.5, region: '43,65 48,65 48,71 43,71', summary: '病房西侧公共用房中明确标注为“活动”的房间。' },
    { id: 'north_ward', name: '北病房楼', x: 34.5, y: 41, region: '30.5,25 38,25 38,58 30.5,58', summary: '位于中央球场北侧的病房楼；在图面上是左侧住院单元。' },
    // 来源：design/presentation/500床一层跑团地图原型.md §三·已校准房间。
    { id: 'phone_bay', name: '探视房电话', x: 76, y: 61.9, region: '74.8,59.1 77.2,59.1 77.2,64.1 74.8,64.1', summary: '电话位于门诊建筑的探视房内；听筒、家属号码和不能当面说的话留在这里。' },
    { id: 'canteen', name: '职工食堂', x: 17, y: 64, region: '13.5,58 20,58 20,70 13.5,70', summary: '后勤建筑中图纸明确标注的职工食堂。' },
    { id: 'laundry', name: '洗衣房', x: 10.5, y: 48, region: '6.5,38 12.5,38 12.5,57 6.5,57', summary: '洗涤、整理、存放与烘干等房间组成的洗衣功能区。' },
  ],
  connections: [
    ['entrance', 'outpatient'], ['outpatient', 'emergency'], ['outpatient', 'south_courtyard'],
    ['south_courtyard', 'nurse_station'], ['south_courtyard', 'south_ward'], ['south_ward', 'basketball_court'],
    ['basketball_court', 'north_ward'], ['basketball_court', 'activity_room'], ['activity_room', 'nurse_station'],
    ['outpatient', 'phone_bay'], ['phone_bay', 'south_courtyard'], ['north_ward', 'canteen'],
    ['canteen', 'laundry'],
  ],
  actors: [
    { id: 'zheng_xiaomin', name: '郑晓敏', mark: '郑', location: 'nurse_station', hook: '白班记录与好日子本' },
    { id: 'tan_lijuan', name: '谭丽娟', mark: '谭', location: 'nurse_station', hook: '交接本与夜班投影' },
    { id: 'wu_tong', name: '吴桐', mark: '吴', location: 'north_ward', hook: '控制、数字与配合' },
    { id: 'zhou_weiguo', name: '周卫国', mark: '周', location: 'south_ward', hook: '手艺、疼痛与解释权' },
    { id: 'tang_nianan', name: '唐念安', mark: '唐', location: 'phone_bay', hook: '探视电话与侵入念头' },
  ],
}
