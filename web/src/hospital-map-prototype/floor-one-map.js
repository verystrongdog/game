// PROTOTYPE — semantic layer for the 500-bed, scheme-one, floor-one map.
// Coordinates are approximate percentages calibrated for interaction, not CAD measurements.
// 来源：design/presentation/500床一层跑团地图原型.md §一、§三—§四；design/presentation/开局剧情逻辑原型.md §3.4—§3.5。
const sensory = ([sight, sound, smell]) => ({ sight, sound, smell })
const atmosphere = (morning, afternoon, night) => ({ morning: sensory(morning), afternoon: sensory(afternoon), night: sensory(night) })

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
    { id: 'entrance', name: '门诊入口', x: 86.2, y: 36, region: '84,32 87.5,32 87.5,40 84,40', summary: '图纸南侧的门诊外门；由此进入门诊诊室与候诊空间。', atmosphere: atmosphere(
      ['雨棚边缘还挂着水，地砖刚拖过。', '挂号窗口的叫号声隔着玻璃传出来。', '门口潮气压着一层消毒水味。'],
      ['玻璃门反光发白，塑料椅被不断挪动。', '鞋底、门轴和叫号器轮流响起。', '晒热的塑料混着消毒水。'],
      ['外门已经落锁，门缝仍往里送风。', '大厅深处只剩自动门偶尔自检的轻响。', '潮气比白天重，消毒水味变淡。'],
    ) },
    { id: 'outpatient', name: '门诊区', x: 79, y: 38, region: '74.5,31 83,31 83,44 74.5,44', summary: '图纸明确标注的门诊诊室与内部候诊空间。', atmosphere: atmosphere(
      ['病历纸在窗口后堆成几摞。', '叫号器盖过了压低的问询声。', '酒精棉和旧纸的味道贴在一起。'],
      ['候诊椅空出一半，诊室门的开合更显眼。', '偶尔一声名字穿过整条走廊。', '旧纸味里多了一点暖气灰尘。'],
      ['日光灯隔排关闭，空椅排列得过分整齐。', '值班室里有纸页翻动，走廊没有回应。', '酒精味退下去，只剩封闭房间的纸味。'],
    ) },
    { id: 'emergency', name: '急诊区', x: 81, y: 55, region: '77.5,50 85,50 85,59 77.5,59', summary: '图纸急诊入口内侧的诊室、护士与抢救空间。', atmosphere: atmosphere(
      ['推床和金属托盘从帘子前连续经过。', '轮子接缝声、水池滴水声挤在一起。', '强消毒剂里有橡胶手套的味道。'],
      ['一块蓝帘始终没有完全拉严。', '帘后偶尔传出一句短促指令。', '消毒剂和刚拆封的塑料混在一起。'],
      ['半掩门后亮着监护屏的冷光。', '提示音按固定间隔穿过空走廊。', '橡胶味变得比消毒剂更清楚。'],
    ) },
    { id: 'south_courtyard', name: '南侧景观庭院', x: 69, y: 41, region: '64,24 75,24 75,57 64,57', summary: '南病房楼与门诊建筑之间的椭圆景观庭院。', atmosphere: atmosphere(
      ['叶面带着水，石凳边落着一只裂开的柚子。', '果子落地时发出很闷的一声。', '湿土里冒出明显的柚子酸味。'],
      ['石凳被晒热，树影缩在脚边。', '远处篮球反复撞地。', '热石头、尘土和酸掉的果皮混在一起。'],
      ['树影被墙灯切成一段一段。', '风把落叶推向同一个墙角。', '湿土味重新压过白天的尘土。'],
    ) },
    // 来源：design/presentation/500床一层跑团地图原型.md §三·已校准房间。
    { id: 'nurse_station', name: '南病房护士站', x: 58, y: 60.8, region: '56.5,59.3 59.5,59.3 59.5,62.3 56.5,62.3', summary: '南病房公共端的弧形护士工作区；交接本、治疗盘和好日子本在这里相遇。', atmosphere: atmosphere(
      ['治疗盘与两本记录同时摊在台面上。', '早晚班的交接声压得很低。', '消毒水上浮着保温杯的热气。'],
      ['发药车停在弧形台边。', '抽屉、药瓶和钥匙依次响过。', '药片苦味混在消毒水里。'],
      ['台灯只照亮登记本，柜门全锁着。', '走廊声控灯随着脚步逐段亮起。', '凉掉的热水和消毒水几乎没有区别。'],
    ) },
    { id: 'south_ward', name: '南病房楼', x: 58.5, y: 41, region: '55,25 62.5,25 62.5,58 55,58', summary: '位于中央球场南侧的病房楼；在图面上是右侧住院单元。', atmosphere: atmosphere(
      ['床单正在换，几扇门只开到一半。', '量体温的提示声和软底鞋脚步交叠。', '洗衣粉里夹着药片的苦味。'],
      ['阳光停在走廊一侧，另一侧仍偏冷。', '广播声从不同床位漏出来。', '米饭蒸汽暂时盖过了药味。'],
      ['门下漏着细窄的灯线。', '暖气管偶尔一响，翻身声比说话清楚。', '洗衣粉和暖气烤灰的味道留在被褥间。'],
    ) },
    { id: 'basketball_court', name: '中央篮球活动场', x: 46.4, y: 40, region: '39,14 55,14 55,58 39,58', summary: '两栋病房之间有两块画出完整边线的篮球活动场。', atmosphere: atmosphere(
      ['边线还有潮痕，球架下积着昨夜的叶子。', '远处有人试着拍了两下球。', '湿尘和橡胶味贴着地面。'],
      ['白线被日光照得刺眼。', '球声、鞋底摩擦和来回计步声最密。', '晒热的橡胶和尘土发干。'],
      ['场灯已经熄灭，铁网只剩轮廓。', '风拨动铁网，发出不规则的轻响。', '橡胶味退去，土腥味重新上来。'],
    ) },
    { id: 'activity_room', name: '活动室', x: 45.3, y: 68.5, region: '43,65 48,65 48,71 43,71', summary: '病房西侧公共用房中明确标注为“活动”的房间。', atmosphere: atmosphere(
      ['折叠椅还没摆齐，窗台落着粉笔灰。', '桌脚拖动和收音机试台声断断续续。', '清洁剂盖不住旧木头味。'],
      ['桌上同时摊着毛线、报纸和拆开的轮椅刹车。', '纸页、工具和收音机混在一起响。', '木屑、旧布和清洁剂混在一起。'],
      ['桌椅全部归位，窗帘没有拉严。', '钟表走动显得比白天响。', '旧木头吸住了白天残下的清洁剂味。'],
    ) },
    { id: 'north_ward', name: '北病房楼', x: 34.5, y: 41, region: '30.5,25 38,25 38,58 30.5,58', summary: '位于中央球场北侧的病房楼；在图面上是左侧住院单元。', atmosphere: atmosphere(
      ['称重处的帘子没有完全合上。', '低声交谈后，总有水杯被放回桌面。', '早饭蒸汽混着暖气灰尘。'],
      ['窗边最亮，走廊有人沿同一路线来回。', '脚步经过相同地砖时节奏会变。', '饭味散去，只剩洗衣粉和暖气灰。'],
      ['门下漏出灯线，床边物件都收得很齐。', '被子摩擦声时断时续。', '封闭窗户让暖气灰的味道更重。'],
    ) },
    // 来源：design/presentation/500床一层跑团地图原型.md §三·已校准房间。
    { id: 'phone_bay', name: '探视房电话', x: 76, y: 61.9, region: '74.8,59.1 77.2,59.1 77.2,64.1 74.8,64.1', summary: '电话位于门诊建筑的探视房内；听筒、家属号码和不能当面说的话留在这里。', atmosphere: atmosphere(
      ['号码写在便签背面，听筒在人手间传递。', '电话铃、报号声和短促道别互相打断。', '受热塑料里留着一点爽身粉味。'],
      ['家属来电集中，第一声铃常没响完就被接起。', '听筒漏出的声音辨不清词句。', '塑料受热味更重，窗边仍有爽身粉残留。'],
      ['电话不再响，线缆影子落在墙上。', '远处门轴声经过这里会变得很空。', '房间凉下来，只剩旧塑料味。'],
    ) },
    { id: 'canteen', name: '职工食堂', x: 17, y: 64, region: '13.5,58 20,58 20,70 13.5,70', summary: '后勤建筑中图纸明确标注的职工食堂。', atmosphere: atmosphere(
      ['蒸汽蒙住玻璃，窗口前排着搪瓷饭盒。', '饭盒磕台面的声音有脆有哑。', '炖菜和米饭的热气挤满门口。'],
      ['窗口已经收起，后厨仍在冲洗。', '洗碗水声占满空食堂。', '油烟退去，洗洁精味浮上来。'],
      ['椅子倒扣在桌面，只有冰柜亮着。', '压缩机间歇启动，又突然停下。', '凉掉的油和洗洁精留在空气里。'],
    ) },
    { id: 'laundry', name: '洗衣房', x: 10.5, y: 48, region: '6.5,38 12.5,38 12.5,57 6.5,57', summary: '洗涤、整理、存放与烘干等房间组成的洗衣功能区。', atmosphere: atmosphere(
      ['湿床单挂满轨道，把视线切成窄条。', '洗衣机低频转动，推车轮偶尔压过地漏。', '漂白剂和潮布的味道很重。'],
      ['烘干机让空气发热，地上留着推车水线。', '滚筒声持续得让人忘记停顿。', '热布料暂时压住了漂白剂。'],
      ['机器停下，床单在暗处一动不动。', '管道回水声隔一会儿响一次。', '潮布味重新变冷，漂白剂仍刺鼻。'],
    ) },
  ],
  connections: [
    ['entrance', 'outpatient'], ['outpatient', 'emergency'], ['outpatient', 'south_courtyard'],
    ['south_courtyard', 'nurse_station'], ['south_courtyard', 'south_ward'], ['south_ward', 'basketball_court'],
    ['basketball_court', 'north_ward'], ['basketball_court', 'activity_room'], ['activity_room', 'nurse_station'],
    ['outpatient', 'phone_bay'], ['phone_bay', 'south_courtyard'], ['north_ward', 'canteen'],
    ['canteen', 'laundry'],
  ],
  actors: [
    { id: 'zheng_xiaomin', name: '郑晓敏', mark: '郑', hook: '白班记录与好日子本', schedule: {
      morning: { location: 'nurse_station', activity: '交班后量体温' }, afternoon: { location: 'south_ward', activity: '发药并擦门把手' },
    } },
    { id: 'tan_lijuan', name: '谭丽娟', mark: '谭', hook: '交接本与夜班投影', schedule: {
      morning: { location: 'nurse_station', activity: '完成夜班交接' }, night: { location: 'nurse_station', activity: '夜巡间隙登记' },
    } },
    { id: 'wu_tong', name: '吴桐', mark: '吴', hook: '控制、数字与配合', schedule: {
      morning: { location: 'north_ward', activity: '整理称重记录' }, afternoon: { location: 'basketball_court', activity: '沿边线计步' }, night: { location: 'north_ward', activity: '盖着被子核对数字' },
    } },
    { id: 'zhou_weiguo', name: '周卫国', mark: '周', hook: '手艺、疼痛与解释权', schedule: {
      morning: { location: 'south_ward', activity: '修走廊椅子' }, afternoon: { location: 'activity_room', activity: '修轮椅刹车' }, night: { location: 'south_ward', activity: '坐着等走廊天亮' },
    } },
    { id: 'tang_nianan', name: '唐念安', mark: '唐', hook: '探视电话与侵入念头', schedule: {
      morning: { location: 'phone_bay', activity: '听女儿的电话录音' }, afternoon: { location: 'activity_room', activity: '织一件小毛衣' }, night: { location: 'south_ward', activity: '在床边读小说' },
    } },
  ],
}
