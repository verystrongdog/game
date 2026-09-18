# Three.js Character Animation Reference

> SDK: `three.js r160` (vendored)
> Sources: [FBXLoader docs](https://threejs.org/docs/pages/FBXLoader.html), [GLTFLoader docs](https://threejs.org/docs/pages/GLTFLoader.html), [AnimationMixer docs](https://threejs.org/docs/pages/AnimationMixer.html), [SkeletonUtils docs](https://threejs.org/docs/pages/module-SkeletonUtils.html), [r160 SkeletonUtils source](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/utils/SkeletonUtils.js), [r160 FBXLoader source](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/loaders/FBXLoader.js), [r160 GLTFLoader source](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/loaders/GLTFLoader.js)

---

## 1. FBXLoader

`FBXLoader` is an addon, not part of the core bundle:

```js
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js'

const object = await new FBXLoader().loadAsync('/character.fbx')
scene.add(object)
const clips = object.animations
```

- `load(url, onLoad, onProgress, onError)` loads asynchronously; `parse(arrayBuffer, resourcePath)` returns a `Group` synchronously.
- FBX may contain a skinned hierarchy and `AnimationClip[]` on the returned group's `animations` property.
- The official loader documents FBX 7.0+ ASCII and 6400+ binary support, with older files potentially loading incorrectly. FBX remains an interchange/source format with exporter-specific ambiguity; do not make it the project's canonical runtime asset.

## 2. GLTFLoader and GLB

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const gltf = await new GLTFLoader().loadAsync('/character.glb')
scene.add(gltf.scene)
const clips = gltf.animations
```

`GLTFLoader` loads glTF 2.0. Its result is not the scene directly: use `gltf.scene` (or `gltf.scenes`) for the object hierarchy and `gltf.animations` for `AnimationClip[]`. A `.glb` packages the glTF JSON, buffers, and normally textures into one binary file; loader usage is otherwise the same.

If the asset uses Draco, KTX2, or Meshopt compression, configure the corresponding decoder with `setDRACOLoader`, `setKTX2Loader`, or `setMeshoptDecoder`. For this project, prefer uncompressed GLB first; add compression only after the base pipeline is verified.

## 3. AnimationMixer

`AnimationMixer` plays clips against one root object. Create one mixer per independently animated character, bind clips with `clipAction`, and advance it every render frame:

```js
const mixer = new THREE.AnimationMixer(gltf.scene)
const action = mixer.clipAction(gltf.animations[0])
action.play()

// render loop
mixer.update(deltaSeconds)
```

The mixer root must contain the nodes addressed by the clip's track bindings. `clipAction(clip, optionalRoot)` caches and returns the same action for the same clip/root pair. On disposal, stop actions before calling `uncacheAction`, `uncacheClip`, or `uncacheRoot`.

## 4. SkeletonUtils.retargetClip

```js
import { retargetClip } from 'three/addons/utils/SkeletonUtils.js'

const converted = retargetClip(targetSkinnedMesh, sourceSkeleton, sourceClip, {
  names: { TargetHip: 'SourceHip' }, // target bone name -> source bone name
  hip: 'SourceHip',
  fps: 30,
  useFirstFramePosition: true,
})
```

The target must expose `.skeleton` (normally a `SkinnedMesh`). The source may be a skinned object with `.skeleton` or a `Skeleton`. The clip must be authored against the source skeleton. `names` maps **target bone names to source bone names**; unmapped bones fall back to identical names. The function returns a new `AnimationClip` and does not mutate the original clip into compatibility.

In the vendored r160 implementation, `retargetClip` samples the source through an internal `AnimationMixer` at `fps` (default `30`) and emits target quaternion tracks plus a hip position track. Its supported r160 options and names differ from current Three.js documentation: use the vendored source as the authority until Three.js is upgraded.

## 5. Runtime retargeting risks

- Bone-name mapping alone does not reconcile different rest poses, bone axes, proportions, hierarchy, scale, or missing/twist bones; failures often look like rotated limbs, sliding feet, displaced hips, or collapsed meshes rather than thrown errors.
- Retargeting is a sampled conversion. It adds startup CPU work and memory, can change clip duration/key density, and makes results depend on the selected `fps`.
- Root motion needs an explicit policy. Removing every `.position` track avoids double movement but also removes intentional vertical or local translation; keep or strip only the chosen root/hip track.
- FBX exporters may produce different hierarchy names and transforms. A hard-coded map is asset-pair-specific, not a general humanoid solution.
- Running the conversion in every browser repeats deterministic content work on every load and makes visual regressions harder to review.

Use runtime `retargetClip` only as a prototype bridge, a compatibility fallback, or for genuinely user-supplied assets. Validate bone coverage, source clip presence, bind/rest pose, scale, duration, and root motion before enabling an action.

## 6. Recommended offline unified-skeleton pipeline

Use Blender or another DCC/import tool to do the retarget once:

1. Select one canonical game skeleton, rest pose, scale, axis convention, and root-motion policy.
2. Import each FBX model and animation, retarget and visually correct it offline, then bake every action onto that canonical skeleton.
3. Export the character and named clips as glTF 2.0/GLB. Keep stable bone and clip names.
4. Validate the GLB in an independent glTF viewer and in the project, including loops, feet, hips, transitions, and mobile performance.
5. At runtime, load one GLB with `GLTFLoader` and play its `gltf.animations` directly with `AnimationMixer`—no bone map or `retargetClip` in the normal path.

This keeps the existing lightweight Three.js web architecture while solving the FBX-animation compatibility problem at the asset boundary. Unity Web is not required solely to obtain humanoid animation retargeting.

## Project Notes

<!-- Auto-appended by fetch-sdk skill. Lessons learned during implementation. -->
- 2026-09-17: The prototype vendors Three.js r160 under `design/presentation/vendor/three`; `web/vite.config.js` aliases `three` to that exact module so addons and core share one Three.js instance.
- 2026-09-17: The current narrative prototype loads X Bot and ActionLab FBX files separately, maps Mixamo target names to ActionLab source names, and calls the r160 `retargetClip` at 30 FPS in the browser.
- 2026-09-17: The prototype removes every generated `.position` track because locomotion is controller-driven. Preserve that policy intentionally during migration; do not apply it blindly to animations that need vertical/root translation.
- 2026-09-17: Preferred migration is offline retarget/bake to the X Bot canonical skeleton, export named clips in GLB, vendor the matching r160 `GLTFLoader`, and keep runtime retargeting only as a temporary fallback.
- 2026-09-17: The four KI locomotion files are animation-only FBX assets: they contain a bone hierarchy and clips but no `SkinnedMesh`. Build the `retargetClip` source with `new Skeleton(new SkeletonHelper(sourceObject).bones)` instead of requiring a source skinned mesh.
- 2026-09-17: KI limb names use suffixes without dots (`B-upperArmL`, `B-thighR`), not Blender-style dotted names. The asset probe must verify all 22 required X Bot-to-KI mappings before retargeting.
- 2026-09-17: KI clips also contain three `Rig.*` object tracks that cannot bind when r160 `retargetClip` wraps a bare `Skeleton` in a helper. Filter the input clip to source-bone tracks before sampling to avoid repeated `PropertyBinding` warnings.
- 2026-09-17: Uploaded Mixamo `Walking.fbx` and `Slow Run.fbx` each have the same 65 `mixamorig*` bones and 53 identically named tracks as X Bot. Bind these clips directly to an `AnimationMixer` rooted at the X Bot object; do not pass them through `retargetClip`.
- 2026-09-17: Uploaded Mixamo `Standing Idle.fbx` has the same 65 bones and 53 track names as X Bot (6.0 s). It uses the same direct-binding path as Walk and Run and loops as the default locomotion state.
- 2026-09-17: The CC0 `Reception And Waiting Hall` GLB uses `KHR_mesh_quantization` but no Draco/Meshopt/KTX2, so the matching r160 `GLTFLoader` loads it without additional decoders. Keep the asset local instead of depending on its CDN at runtime.
