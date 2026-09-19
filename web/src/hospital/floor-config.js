const ROOT = '/hospital-floor/models'

function part(model, file, x, z, y, yaw, role) {
  return { url: `${ROOT}/${model}/meshes/${file}`, position: [x, y, -z], yaw, role }
}

const floor01 = [
  part('aws_robomaker_hospital_floor_01_floor', 'aws_robomaker_hospital_floor_01_floor_visual.dae', -.001425, -.014447, 0, 0, 'floor'),
  part('aws_robomaker_hospital_floor_01_walls', 'aws_robomaker_hospital_floor_01_walls_visual.dae', -.013823, -.013783, 0, 0, 'walls'),
  part('aws_robomaker_hospital_nursesstation_01', 'aws_robomaker_hospital_nursesstation_01_low.dae', 0, 1.5, 0, 0, 'furniture'),
  part('aws_robomaker_hospital_ramp_01', 'aws_robomaker_hospital_ramp_01_visual.dae', -1.70996, 16.3685, 0, 0, 'floor'),
  ...[
    [-11.022, -7.27757, 1.57907], [1.31506, -30.5771, 3.1401], [10.9586, .159483, -1.58306],
    [10.9819, -26.2149, -1.58306], [11.0303, -3.70124, -1.58306], [5.49659, -30.5364, 3.1401],
    [9.80048, -30.5918, 3.1401]
  ].map(([x, z, yaw]) => part('aws_robomaker_hospital_curtain_closed_01', 'aws_robomaker_hospital_curtain_closed_01_visual.dae', x, z, 0, yaw, 'furniture')),
  ...[
    [-11.0086, -21.7566, 1.55358], [-11.0216, -13.8069, 1.55358], [-11.0309, -3.75145, 1.56614],
    [-11.0332, -17.61, 1.55358], [-11.0426, .066126, 1.56614], [11.1068, -17.8472, -1.55117],
    [11.1374, -14.1551, -1.55117], [11.1417, -21.4039, -1.55117]
  ].map(([x, z, yaw]) => part('aws_robomaker_hospital_curtain_half_open_01', 'aws_robomaker_hospital_curtain_half_open_01_visual.dae', x, z, 0, yaw, 'furniture')),
  part('aws_robomaker_hospital_curtain_open_01', 'aws_robomaker_hospital_curtain_open_01_visual.dae', 11.0051, -6.91002, 0, -1.58737, 'furniture'),
  ...[-1.49587, 1.5407].map(x => part('aws_robomaker_hospital_elevator_01_car', 'aws_robomaker_hospital_elevator_01_car_low.dae', x, 19.35, .19, 0, 'furniture')),
  ...[-1.51, 1.52843].map(x => part('aws_robomaker_hospital_elevator_01_door', 'aws_robomaker_hospital_elevator_01_door_low.dae', x, 19.35, .19, 0, 'furniture')),
  ...[-1.50654, 1.51134].map(x => part('aws_robomaker_hospital_elevator_01_portal', 'aws_robomaker_hospital_elevator_01_portal_low.dae', x, 19.48, .19, 0, 'furniture'))
]

const floor02 = [
  part('aws_robomaker_hospital_floor_02_floor', 'aws_robomaker_hospital_floor_02_floor_visual.dae', 0, 0, 0, 0, 'floor'),
  part('aws_robomaker_hospital_floor_02_walls', 'aws_robomaker_hospital_floor_02_walls_visual.dae', 0, 0, 0, 0, 'walls'),
  ...floor01.filter(item => item.url.includes('elevator_01') && !item.url.includes('_car_'))
]

export const hospitalFloorConfigs = [
  {
    name: '一层', zone: '门诊与接待大厅', accent: 0x8fcbbb,
    objective: '比对好日子本与交接本，弄清昨夜发生了什么。', parts: floor01
  },
  {
    name: '二层', zone: '住院病区', accent: 0x9cc9a4,
    objective: '检查病房、护理通道和转运设备中的异常。', parts: floor02
  },
  {
    name: '三层', zone: '手术与检查区', accent: 0x91b9d5,
    objective: '进入手术区核查无影灯、监护仪和器械车留下的线索。', parts: floor02
  }
]
