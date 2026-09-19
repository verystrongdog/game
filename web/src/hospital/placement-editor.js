import * as THREE from 'three'
import { TransformControls } from '/three-addons/controls/TransformControls.js'
import { groupCatalogByCategory, loadHospitalAssetCatalog } from './asset-catalog.js'
import { boxesOverlap } from './collision.js'
import './placement-editor.css'

const STORAGE_VERSION = 1

export function createHospitalPlacementEditor({
  scene, camera, renderer, host, getFloorContext, getPlacementOrigin,
  toggleButton = null, storageKey = 'ziyufei.hospital-layout.v1', onStateChange = () => {}
}) {
  const roots = []
  const raycaster = new THREE.Raycaster()
  const pointer = new THREE.Vector2()
  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)
  const planeHit = new THREE.Vector3()
  const dragOffset = new THREE.Vector3()
  const controls = new TransformControls(camera, renderer.domElement)
  const helper = controls.getHelper ? controls.getHelper() : controls
  const selectionBox = new THREE.Box3()
  const selectionHelper = new THREE.Box3Helper(selectionBox, 0x79d6b5)
  selectionHelper.material.depthTest = false
  selectionHelper.material.transparent = true
  selectionHelper.material.opacity = .95
  selectionHelper.renderOrder = 999
  const previousValid = { position: new THREE.Vector3(), quaternion: new THREE.Quaternion() }
  let catalog = []
  let selected = null
  let active = false
  let valid = true
  let serial = 0
  let directDragging = false
  let snapSize = .25

  helper.visible = false
  selectionHelper.visible = false
  scene.add(helper, selectionHelper)
  controls.setMode('translate')
  controls.showY = false
  controls.setTranslationSnap(snapSize)
  controls.setRotationSnap(THREE.MathUtils.degToRad(15))

  const panel = document.createElement('aside')
  panel.className = 'hospital-editor'
  panel.hidden = true
  panel.innerHTML = `
    <header><strong>医院布置</strong><button type="button" data-close aria-label="退出布置">×</button></header>
    <p class="hospital-editor__hint">点击物体选中，按住物体本身即可沿地面拖动。绿框可放置，红框表示冲突。</p>
    <div class="hospital-editor__tools">
      <button type="button" data-mode="translate">移动轴 W</button>
      <button type="button" data-mode="rotate">旋转轴 R</button>
      <button type="button" data-rotate="-1">左转 15°</button>
      <button type="button" data-rotate="1">右转 15°</button>
      <button type="button" data-delete disabled>删除</button>
      <button type="button" data-save>保存布局</button>
    </div>
    <div class="hospital-editor__snap">
      <label>吸附精度
        <select data-snap>
          <option value="0">关闭</option>
          <option value="0.1">0.1 m</option>
          <option value="0.25" selected>0.25 m</option>
          <option value="0.5">0.5 m</option>
          <option value="1">1 m</option>
        </select>
      </label>
      <span>方向键微移 · Shift 加速</span>
    </div>
    <div class="hospital-editor__status" data-status>正在解析单件素材…</div>
    <div class="hospital-editor__catalog" data-catalog></div>`
  host.append(panel)

  const toggle = toggleButton || document.createElement('button')
  toggle.type = 'button'
  if (!toggleButton) toggle.className = 'hospital-editor-toggle'
  toggle.textContent = '布置医院'
  toggle.disabled = false
  if (!toggleButton) host.append(toggle)

  const status = panel.querySelector('[data-status]')
  const catalogRoot = panel.querySelector('[data-catalog]')
  const deleteButton = panel.querySelector('[data-delete]')

  function floorRoots(floorIndex) {
    return roots.filter(root => root.userData.floorIndex === floorIndex)
  }

  function objectBounds(root) {
    root.updateMatrixWorld(true)
    return new THREE.Box3().setFromObject(root)
  }

  function cacheCollisionBox(root) {
    root.userData.collisionBox = objectBounds(root)
    return root.userData.collisionBox
  }

  function validate(root) {
    const context = getFloorContext()
    const box = objectBounds(root)
    const inside = box.min.x >= context.bounds.min.x && box.max.x <= context.bounds.max.x
      && box.min.z >= context.bounds.min.y && box.max.z <= context.bounds.max.y
    if (!inside) return false
    if (context.colliders.some(collider => boxesOverlap(box, collider))) return false
    if ((context.reservedColliders || []).some(collider => boxesOverlap(box, collider))) return false
    return !floorRoots(context.index).some(other => other !== root && boxesOverlap(box, objectBounds(other)))
  }

  function updateSelectionValidation() {
    if (!selected) return
    valid = validate(selected)
    selectionBox.copy(objectBounds(selected))
    selectionHelper.material.color.set(valid ? 0x79d6b5 : 0xe05a47)
    status.textContent = valid ? `${selected.userData.assetLabel} · 位置可用` : '位置冲突：请离开墙体或其他物体'
  }

  function snap(value) {
    return snapSize > 0 ? Math.round(value / snapSize) * snapSize : value
  }

  function rememberValidTransform() {
    if (!selected) return
    previousValid.position.copy(selected.position)
    previousValid.quaternion.copy(selected.quaternion)
  }

  function finishTransform() {
    if (!selected) return
    if (!valid) {
      selected.position.copy(previousValid.position)
      selected.quaternion.copy(previousValid.quaternion)
      updateSelectionValidation()
      status.textContent = '位置冲突，已恢复到上一个可用位置'
    } else {
      rememberValidTransform()
    }
    cacheCollisionBox(selected)
  }

  function select(root) {
    selected = root
    controls.attach(root)
    helper.visible = true
    selectionHelper.visible = true
    deleteButton.disabled = false
    rememberValidTransform()
    updateSelectionValidation()
  }

  function deselect() {
    selected = null
    controls.detach()
    helper.visible = false
    selectionHelper.visible = false
    deleteButton.disabled = true
  }

  function findOpenPosition(root) {
    const origin = getPlacementOrigin()
    root.position.set(origin.x, getFloorContext().y, origin.z)
    for (let radius = 0; radius <= 8; radius += .5) {
      const samples = Math.max(1, Math.ceil(radius * 8))
      for (let sample = 0; sample < samples; sample += 1) {
        const angle = sample / samples * Math.PI * 2
        root.position.set(origin.x + Math.cos(angle) * radius, getFloorContext().y, origin.z + Math.sin(angle) * radius)
        if (validate(root)) return true
      }
    }
    return false
  }

  function addAsset(asset, saved = null) {
    const root = asset.create()
    root.userData.assetId = asset.id
    root.userData.assetLabel = asset.label
    root.userData.placementRoot = root
    root.userData.floorIndex = saved?.floorIndex ?? getFloorContext().index
    root.userData.placementId = saved?.id || `placed-${Date.now()}-${serial += 1}`
    root.traverse(child => { child.userData.placementRoot = root })
    if (saved) {
      root.position.fromArray(saved.position)
      root.quaternion.fromArray(saved.quaternion)
    } else if (!findOpenPosition(root)) {
      status.textContent = '当前附近没有可用空间'
      return null
    }
    root.visible = root.userData.floorIndex === getFloorContext().index
    roots.push(root)
    scene.add(root)
    cacheCollisionBox(root)
    if (!saved) select(root)
    return root
  }

  function serialize() {
    return {
      version: STORAGE_VERSION,
      objects: roots.map(root => ({
        id: root.userData.placementId,
        assetId: root.userData.assetId,
        floorIndex: root.userData.floorIndex,
        position: root.position.toArray(),
        quaternion: root.quaternion.toArray()
      }))
    }
  }

  function save() {
    localStorage.setItem(storageKey, JSON.stringify(serialize()))
    status.textContent = `已保存 ${roots.length} 件布置物`
  }

  function restore() {
    const raw = localStorage.getItem(storageKey)
    if (!raw) return
    try {
      const snapshot = JSON.parse(raw)
      if (snapshot.version !== STORAGE_VERSION || !Array.isArray(snapshot.objects)) return
      snapshot.objects.forEach(item => {
        const asset = catalog.find(candidate => candidate.id === item.assetId)
        if (asset) addAsset(asset, item)
      })
    } catch (error) {
      console.warn('[HospitalPlacement] 忽略无法解析的本地布局', error)
    }
  }

  function renderCatalog() {
    catalogRoot.replaceChildren()
    for (const [category, assets] of groupCatalogByCategory(catalog)) {
      const section = document.createElement('section')
      const heading = document.createElement('h3')
      heading.textContent = category
      section.append(heading)
      const list = document.createElement('div')
      assets.forEach(asset => {
        const button = document.createElement('button')
        button.type = 'button'
        button.textContent = asset.label
        button.addEventListener('click', () => addAsset(asset))
        list.append(button)
      })
      section.append(list)
      catalogRoot.append(section)
    }
    status.textContent = `已识别 ${catalog.length} 种单件素材`
  }

  function setActive(next) {
    active = next
    panel.hidden = !active
    toggle.textContent = active ? '退出布置' : '布置医院'
    host.classList.toggle('hospital-placement-active', active)
    if (!active) deselect()
    onStateChange({ active })
  }

  function updatePointer(event) {
    const rect = renderer.domElement.getBoundingClientRect()
    pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1)
    raycaster.setFromCamera(pointer, camera)
  }

  function onPointerDown(event) {
    if (!active || event.button !== 0 || controls.dragging || controls.axis || event.target !== renderer.domElement) return
    updatePointer(event)
    const hit = raycaster.intersectObjects(floorRoots(getFloorContext().index), true)[0]
    const root = hit?.object.userData.placementRoot
    if (!root) {
      deselect()
      return
    }
    if (selected !== root) select(root)
    rememberValidTransform()
    floorPlane.constant = -getFloorContext().y
    if (!raycaster.ray.intersectPlane(floorPlane, planeHit)) return
    dragOffset.copy(selected.position).sub(planeHit)
    directDragging = true
    renderer.domElement.setPointerCapture?.(event.pointerId)
    host.classList.add('hospital-placement-dragging')
    event.preventDefault()
  }

  function onPointerMove(event) {
    if (!directDragging || !selected) return
    updatePointer(event)
    if (!raycaster.ray.intersectPlane(floorPlane, planeHit)) return
    selected.position.x = snap(planeHit.x + dragOffset.x)
    selected.position.z = snap(planeHit.z + dragOffset.z)
    selected.position.y = getFloorContext().y
    updateSelectionValidation()
  }

  function onPointerUp(event) {
    if (!directDragging) return
    directDragging = false
    renderer.domElement.releasePointerCapture?.(event.pointerId)
    host.classList.remove('hospital-placement-dragging')
    finishTransform()
  }

  function rotateSelected(direction) {
    if (!selected) return
    rememberValidTransform()
    selected.rotation.y += direction * THREE.MathUtils.degToRad(15)
    updateSelectionValidation()
    finishTransform()
  }

  function nudgeSelected(dx, dz, fast = false) {
    if (!selected) return
    rememberValidTransform()
    const distance = (snapSize || .1) * (fast ? 4 : 1)
    selected.position.x += dx * distance
    selected.position.z += dz * distance
    updateSelectionValidation()
    finishTransform()
  }

  controls.addEventListener('objectChange', updateSelectionValidation)
  controls.addEventListener('mouseDown', () => {
    if (!selected) return
    rememberValidTransform()
  })
  controls.addEventListener('mouseUp', finishTransform)
  renderer.domElement.addEventListener('pointerdown', onPointerDown)
  renderer.domElement.addEventListener('pointermove', onPointerMove)
  renderer.domElement.addEventListener('pointerup', onPointerUp)
  renderer.domElement.addEventListener('pointercancel', onPointerUp)
  toggle.addEventListener('click', () => setActive(!active))
  panel.querySelector('[data-close]').addEventListener('click', () => setActive(false))
  panel.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => controls.setMode(button.dataset.mode)))
  panel.querySelectorAll('[data-rotate]').forEach(button => button.addEventListener('click', () => rotateSelected(Number(button.dataset.rotate))))
  panel.querySelector('[data-snap]').addEventListener('change', event => {
    snapSize = Number(event.target.value)
    controls.setTranslationSnap(snapSize || null)
    status.textContent = snapSize ? `已启用 ${snapSize} m 网格吸附` : '已关闭网格吸附'
  })
  panel.querySelector('[data-save]').addEventListener('click', save)
  deleteButton.addEventListener('click', () => {
    if (!selected) return
    const index = roots.indexOf(selected)
    scene.remove(selected)
    if (index >= 0) roots.splice(index, 1)
    deselect()
    status.textContent = '已删除布置物'
  })
  window.addEventListener('keydown', event => {
    if (!active || event.target.matches('input, textarea')) return
    if (event.code === 'KeyW') controls.setMode('translate')
    if (event.code === 'KeyR') controls.setMode('rotate')
    const nudges = {
      ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1]
    }
    if (nudges[event.code] && selected) {
      nudgeSelected(...nudges[event.code], event.shiftKey)
      event.preventDefault()
    }
    if ((event.code === 'Delete' || event.code === 'Backspace') && selected) deleteButton.click()
  })

  loadHospitalAssetCatalog().then(loaded => {
    catalog = loaded
    renderCatalog()
    restore()
  }).catch(error => {
    console.error('[HospitalPlacement] 素材目录加载失败', error)
    status.textContent = `素材目录加载失败：${error.message}`
  })

  return {
    isActive: () => active,
    getCollisionBoxes(floorIndex) {
      return floorRoots(floorIndex).map(root => root.userData.collisionBox || cacheCollisionBox(root))
    },
    setFloor(floorIndex) {
      roots.forEach(root => { root.visible = root.userData.floorIndex === floorIndex })
      deselect()
    },
    serialize,
    save
  }
}
