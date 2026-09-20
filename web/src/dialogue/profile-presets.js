// 试玩视角用于显式验证经历与疾病如何改变同一段对话；不替代开局人物确认。
export const dialogueProfilePresets = [
  { id: 'normal', label: '普通视角', experiences: [], diseases: [] },
  { id: 'night_watch', label: '夜班 · 焦虑', experiences: ['night-shifts', 'guard-work', 'family-patient'], diseases: ['广泛性焦虑障碍'] },
  { id: 'checker', label: '核对 · 强迫', experiences: ['checking-work', 'strict-home', 'good-child-role'], diseases: ['强迫症'] },
  { id: 'body', label: '身体 · 厌食', experiences: ['body-policed', 'weighed-work', 'hunger', 'major-illness'], diseases: ['神经性厌食症', '躯体症状障碍'] },
  { id: 'threat', label: '危险 · PTSD', experiences: ['dangerous-work', 'unsafe-place', 'heavy-labor', 'work-injury'], diseases: ['PTSD'] },
]
