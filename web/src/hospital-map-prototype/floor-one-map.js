// PROTOTYPE — measured coordinate layer for the 500-bed, scheme-one, floor-one plan.
// Semantic rooms, routes and actor placements remain intentionally empty until the
// owner-authored interior-wall topology can provide their spatial basis.
// 来源：design/presentation/500床一层跑团地图原型.md §一—§二。

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
  // No semantic geography is authored before the interior-wall trace is complete.
  initialLocation: null,
  locations: [],
  connections: [],
  actors: [],
}
