import { createCharacterCreation } from '/character-creation/index.js'
import { createDisplaySettings } from '/character-creation/display-settings.js'
import { createDialogueUi } from '/dialogue/dialogue-ui.js'
import { createHospitalMapPrototype } from '/hospital-map-prototype/hospital-map-prototype.js'

// 来源：design/entities/疾病特长.md §二—§六。未决项在原型中显式保留，不写回正式游戏状态。
const characterCreation = createCharacterCreation({
  trigger: document.querySelector('#characterCreationLaunch'),
  required: true,
})
const dialoguePrototype = createDialogueUi()
characterCreation.subscribe(profile => dialoguePrototype.setProfile(profile))

window.dialoguePrototype = dialoguePrototype
const hospitalMapController = createHospitalMapPrototype({
  host: document.querySelector('#hospitalMapHost'),
  scene: document.querySelector('#scene'),
  getTime: () => dialoguePrototype.view().time,
  getNpcDossier: npcId => dialoguePrototype.dossier(npcId),
  onNpcInspect: (npcId, context) => dialoguePrototype.showDossier(npcId, context),
  onNpcSelect: (npcId, context) => dialoguePrototype.selectNpc(npcId, { nearby: true, ...context }),
  onMapContext: context => dialoguePrototype.showMapContext(context),
})
window.hospitalMapController = hospitalMapController

createDisplaySettings({
  trigger: document.querySelector('#displaySettingsLaunch'),
  panel: document.querySelector('#displaySettings'),
  input: document.querySelector('#brightnessRange'),
  output: document.querySelector('#brightnessOutput'),
})

const scene = document.querySelector('#scene')
const developerOptions = document.querySelector('#developerOptions')
const developerMapStatus = document.querySelector('#developerMapStatus')

function refreshDeveloperOptions(view = dialoguePrototype.view()) {
  const mapState = hospitalMapController.state()
  scene.dataset.time = view.time
  const tracing = mapState.wallTopology.activeAnchor ? ' · 描墙中' : ''
  const constraint = mapState.wallConstraint === 'horizontal' ? '水平' : mapState.wallConstraint === 'vertical' ? '垂直' : '自由'
  const interaction = mapState.interactionMode === 'snap' ? `吸附描墙 ${mapState.snapGridStep}mm/${constraint}` : '拖动画布'
  developerMapStatus.textContent = `${Math.round(mapState.zoom * 100)}% · 旋转 ${mapState.rotation}° · ${mapState.variant} · ${interaction} · ${mapState.wallTopology.walls.length} 段墙${tracing}`
  developerOptions.querySelectorAll('[data-dev-variant]').forEach(button => button.classList.toggle('active', button.dataset.devVariant === mapState.variant))
  developerOptions.querySelectorAll('[data-dev-time]').forEach(button => button.classList.toggle('active', button.dataset.devTime === view.time))
  developerOptions.querySelectorAll('[data-dev-wall-mode]').forEach(button => {
    const active = button.dataset.devWallMode === mapState.interactionMode
    button.classList.toggle('active', active)
    button.setAttribute('aria-pressed', String(active))
  })
  developerOptions.querySelectorAll('[data-dev-wall-constraint]').forEach(button => {
    const active = button.dataset.devWallConstraint === mapState.wallConstraint
    button.classList.toggle('active', active)
    button.setAttribute('aria-pressed', String(active))
  })
}

document.querySelector('#hospitalMapHost').addEventListener('walltracechange', () => refreshDeveloperOptions())

dialoguePrototype.subscribe(view => {
  hospitalMapController.render()
  refreshDeveloperOptions(view)
})

developerOptions.addEventListener('click', event => {
  if (event.target.closest('#hospitalPlacementLaunch')) hospitalMapController.setMapActive(false)
  const mapAction = event.target.closest('[data-dev-map]')?.dataset.devMap
  if (mapAction === 'zoom-in') hospitalMapController.zoomIn()
  if (mapAction === 'zoom-out') hospitalMapController.zoomOut()
  if (mapAction === 'rotate-left') hospitalMapController.rotateLeft()
  if (mapAction === 'rotate-right') hospitalMapController.rotateRight()
  if (mapAction === 'reset') hospitalMapController.resetView()

  const wallMode = event.target.closest('[data-dev-wall-mode]')?.dataset.devWallMode
  if (wallMode) hospitalMapController.setInteractionMode(wallMode)
  const wallConstraint = event.target.closest('[data-dev-wall-constraint]')?.dataset.devWallConstraint
  if (wallConstraint) hospitalMapController.setWallConstraint(wallConstraint)
  const wallAction = event.target.closest('[data-dev-wall]')?.dataset.devWall
  if (wallAction === 'undo') hospitalMapController.undoWall()
  if (wallAction === 'finish') hospitalMapController.finishWallTrace()
  if (wallAction === 'copy') hospitalMapController.copyWallTopology()
  if (wallAction === 'clear' && window.confirm('清空本次新增墙线？整体外墙会保留。')) hospitalMapController.clearWalls()

  const variant = event.target.closest('[data-dev-variant]')?.dataset.devVariant
  if (variant) hospitalMapController.setVariant(variant)

  const time = event.target.closest('[data-dev-time]')?.dataset.devTime
  if (time) dialoguePrototype.setTime(time)
  refreshDeveloperOptions()
})

refreshDeveloperOptions()
const startScreen = document.querySelector('#startScreen')
const startGameButton = document.querySelector('#startGameButton')

startGameButton.addEventListener('click', () => {
  startScreen.hidden = true
  characterCreation.open()
})
startGameButton.focus()
