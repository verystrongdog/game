import * as THREE from 'three'
import { GLTFLoader } from '/three-addons/loaders/GLTFLoader.js'
import { findAssetInstancePrefix } from './catalog-utils.js'

const PACKS = [
  {
    id: 'reception',
    label: '门诊',
    url: new URL('../../../design/presentation/assets/hospital/reception-waiting-hall.glb', import.meta.url).href,
    assets: [
      ['reception-desk', '接待台'], ['queue-display', '叫号屏'],
      ['single-chair-with-arms', '单人椅'], ['waiting-bench-row', '候诊排椅'],
      ['waiting-bench-two-seat', '双人候诊椅'], ['magazine-table', '阅读桌'],
      ['planter', '绿植'], ['water-cooler', '饮水机'], ['vending-machine', '自助机'],
      ['information-board', '信息栏'], ['wayfinding-sign', '导向牌'], ['waste-bin-set', '垃圾桶']
    ]
  },
  {
    id: 'ward',
    label: '病房',
    url: new URL('../../../design/presentation/assets/hospital/six-bed-ward-bay.glb', import.meta.url).href,
    assets: [
      ['adjustable-ward-bed', '病床'], ['ward-bed-head-raised', '升起病床'],
      ['bedside-cabinet', '床头柜'], ['over-bed-table', '跨床桌'], ['iv-stand', '输液架'],
      ['patient-monitor', '监护仪'], ['oxygen-outlet-panel', '供氧面板'],
      ['curtain-rail-with-drape', '隔帘'], ['wheelchair', '轮椅'],
      ['patient-trolley', '转运床'], ['patient-hoist', '移位机']
    ]
  },
  {
    id: 'theatre',
    label: '手术',
    url: new URL('../../../design/presentation/assets/hospital/operating-theatre.glb', import.meta.url).href,
    assets: [
      ['operating-table', '手术台'], ['surgical-lamp', '无影灯'],
      ['theatre-light-column', '手术灯柱'], ['anaesthesia-machine', '麻醉机'],
      ['instrument-trolley', '器械车'], ['suction-unit', '吸引器'],
      ['sterile-supply-cart', '无菌物品车'], ['scrub-sink', '洗手池'],
      ['patient-monitor', '手术监护仪'], ['ecg-trolley', '心电图车'],
      ['recovery-bay-chair', '恢复椅']
    ]
  }
]

function cloneMeshInWorldSpace(mesh) {
  const clone = new THREE.Mesh(
    mesh.geometry,
    Array.isArray(mesh.material) ? mesh.material.map(material => material.clone()) : mesh.material.clone()
  )
  clone.name = mesh.name
  clone.applyMatrix4(mesh.matrixWorld)
  clone.castShadow = true
  clone.receiveShadow = true
  return clone
}

function extractAsset(scene, definition, pack) {
  scene.updateMatrixWorld(true)
  const root = new THREE.Group()
  root.name = definition[0]
  const meshNames = []
  scene.traverse(child => { if (child.isMesh) meshNames.push(child.name) })
  // A room pack can contain six copies of the same bed or chair. The numeric
  // prefix is the source asset's instance id, so keep exactly one instance as
  // the reusable prototype instead of accidentally extracting the whole set.
  const instancePrefix = findAssetInstancePrefix(meshNames, definition[0])
  if (!instancePrefix) return null
  scene.traverse(child => {
    if (child.isMesh && child.name.startsWith(instancePrefix)
      && child.name.toLowerCase().includes(definition[0])) {
      root.add(cloneMeshInWorldSpace(child))
    }
  })
  if (root.children.length === 0) return null

  const bounds = new THREE.Box3().setFromObject(root)
  const center = bounds.getCenter(new THREE.Vector3())
  const origin = new THREE.Vector3(center.x, bounds.min.y, center.z)
  root.children.forEach(child => child.position.sub(origin))
  root.userData.assetId = `${pack.id}:${definition[0]}`
  root.userData.assetLabel = definition[1]
  root.userData.packLabel = pack.label
  return root
}

export async function loadHospitalAssetCatalog() {
  const loader = new GLTFLoader()
  const catalog = []
  for (const pack of PACKS) {
    const gltf = await loader.loadAsync(pack.url)
    for (const definition of pack.assets) {
      const prototype = extractAsset(gltf.scene, definition, pack)
      if (prototype) catalog.push({
        id: prototype.userData.assetId,
        label: prototype.userData.assetLabel,
        category: prototype.userData.packLabel,
        create: () => prototype.clone(true)
      })
    }
  }
  return catalog
}

export function groupCatalogByCategory(catalog) {
  return catalog.reduce((groups, asset) => {
    const group = groups.get(asset.category) || []
    group.push(asset)
    groups.set(asset.category, group)
    return groups
  }, new Map())
}
