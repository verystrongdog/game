// Blender 回导调试 lab 生成器（Editor）— #156
//
// 目标：给「Blender 人形动作制作与回导调试」这条能力一个**隔离、可重复生成**的观察面：
//   X Bot 载体 + 从 Blender 回导的 animation-only clip + `BlenderAnimationDebugger`（播放/暂停/单帧/复位 + 关键骨读数）。
//
// 口径权威：design/presentation/Blender动作制作管线.md §六（Unity 回导 lab）
//   §六·1 探针 FBX 必须是 Humanoid + `CreateFromThisModel`（与既有 17 条受控 FBX 同口径）。
//          🔧 2026-09-17：原子句写「由 `code/tools/validate_unity_assets.py` 的 A4 机械守着」——
//          该门禁已于 2026-09-17 随全部门禁一并撤销（脚本已删），**现在这句口径只能靠人工核**。
//   §六·2 **产物只落 `Assets/Temp/`**——该目录被 `.gitignore` 的 `[Tt]emp/` 排除，lab 生成物不入库；
//          入库的只有探针 FBX 与三份源码（#156 验收标准第 6 条）。
//   §六·3 幂等：每次从零重建 controller 与场景，重复执行得到同一份场景。
//
// ⚠️ 与 `ActionLab` / `AnimationRiggingLab` 的关系：**互不引用、互不修改**。本条不改已入库基准场景，
//    调试载体独立生成（#156「预期不变」第 4 条）。
//
// 用法：
//   菜单 YANTF → 动作演示 → 创建 Blender 回导调试 lab     （幂等重建 + 自检）
//   headless: Unity -batchmode -quit -executeMethod YANTF.EditorTools.BlenderAnimationDebugBuilder.CreateSceneBatch
//   Play 内读数（unity-cli）：`BlenderAnimationDebugBuilder.Actor()` → `BlenderAnimationDebugger`
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.ActionLab;
using YANTF.WalkerLab;   // CameraOrbit

namespace YANTF.EditorTools
{
    public static class BlenderAnimationDebugBuilder
    {
        // ---- 入库件（探针）----
        public const string ProbeFbxPath = "Assets/Animations/Blender/RigRoundTripProbe.fbx";
        public const string ProbeClipName = "RigRoundTripProbe";
        public const string XBotPath = "Assets/Mixamo/Characters/X Bot.fbx";

        // ---- 生成物（全部落在被 gitignore 的 Assets/Temp/ 下）----
        public const string TempDir = "Assets/Temp";
        public const string TempControllerPath = TempDir + "/BlenderRoundTripDebug.controller";
        public const string TempScenePath = TempDir + "/BlenderRoundTripDebug.unity";

        // 场景内的稳定标识（改名等于破坏断言与文档）
        public const string ActorName = "Blender回导调试载体(X Bot)";
        public const string DebuggerName = "BlenderAnimationDebugger";

        // ================= 菜单 / headless 入口 =================

        [MenuItem("YANTF/动作演示/创建 Blender 回导调试 lab")]
        public static void CreateSceneMenu() => CreateScene();

        public static void CreateSceneBatch() => CreateScene();

        /// <summary>
        /// 幂等重建 lab：地面 + 光 + 相机 + 载体（X Bot + Temp controller + `BlenderAnimationDebugger`），
        /// 存到 `Assets/Temp/BlenderRoundTripDebug.unity`，最后跑自检。
        /// </summary>
        public static void CreateScene()
        {
            if (!EnsureProbeImporter()) return;
            var controller = EnsureController();
            if (controller == null) return;

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(24f, 1f, 24f);
            ground.transform.position = Vector3.zero;
            SetColor(ground, new Color(0.55f, 0.6f, 0.5f));

            var sunGo = new GameObject("Sun");
            var light = sunGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            sunGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            var actor = CreateActor(controller);
            if (actor == null) return;

            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            var orbit = camGo.AddComponent<CameraOrbit>();
            orbit.target = actor.transform;   // ⚠️ 必须显式设：留空会兜底成自身 transform
            orbit.Snap();

            Directory.CreateDirectory(TempDir);
            EditorSceneManager.SaveScene(scene, TempScenePath);
            EditorUtility.SetDirty(actor);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, TempScenePath);

            Debug.Log("[BlenderLab] 场景已生成: " + TempScenePath + "\n" + VerifyLabInfrastructure(actor));
        }

        // ================= 生成物（test 与菜单共用）=================

        /// <summary>
        /// 把探针 FBX 的导入设置**修成并核成** Humanoid + `CreateFromThisModel`（幂等）。
        /// 探针是入库资产，导入设置由它的 `.fbx.meta` 承载——这里只负责在 Meta 漂移时报错并纠正。
        /// </summary>
        public static bool EnsureProbeImporter()
        {
            var importer = AssetImporter.GetAtPath(ProbeFbxPath) as ModelImporter;
            if (importer == null)
            {
                Debug.LogError("[BlenderLab] 找不到探针 FBX: " + ProbeFbxPath +
                               "（先跑 code/tools/export_xbot_action.py 并入库，见管线文档 §四）");
                return false;
            }

            bool dirty = false;
            if (importer.animationType != ModelImporterAnimationType.Human)
            {
                importer.animationType = ModelImporterAnimationType.Human;
                dirty = true;
            }
            if (importer.avatarSetup != ModelImporterAvatarSetup.CreateFromThisModel)
            {
                importer.autoGenerateAvatarMappingIfUnspecified = true;
                importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                dirty = true;
            }
            // ⚠️ **回导样本必须关掉关键帧压缩**（2026-09-14 实测，代价：一整轮"骨盆不动"的假结论）：
            //    Unity 默认 `KeyframeReduction` + `animationPositionError = 0.5` 会把
            //    `RootT.y`（人形 body position，即骨盆位移）从 61 个键**降到 3 个**——峰值还在、
            //    低谷被抹平，于是"探针覆盖骨盆"这条在 Unity 侧读出来只剩 17 mm（Blender 侧 42 mm）。
            //    探针的用途是**逐帧比对**，压缩会让"差异"无法归属到回导本身。
            if (importer.animationCompression != ModelImporterAnimationCompression.Off)
            {
                importer.animationCompression = ModelImporterAnimationCompression.Off;
                dirty = true;
            }
            if (dirty) importer.SaveAndReimport();
            return true;
        }

        /// <summary>
        /// 幂等生成 `Assets/Temp/BlenderRoundTripDebug.controller`（单状态 = 探针 clip）。
        ///
        /// ⚠️ **内容已经对就不重建**（2026-09-14 实测踩到）：早先的实现无条件
        /// `DeleteAsset` + `CreateAnimatorControllerAtPath`，于是每次调用都给资产换一个新 GUID——
        /// **已存盘的 lab 场景里那条 controller 引用随之变成 missing**，症状是"场景在、Animator 在、
        /// clip=(none) frameCount=0"，姿势永远不动。内容不匹配时才重建（此时调用方会重新装配载体）。
        /// </summary>
        public static AnimatorController EnsureController()
        {
            var clip = LoadProbeClip();
            if (clip == null)
            {
                Debug.LogError("[BlenderLab] 探针 FBX 里没有 AnimationClip: " + ProbeFbxPath);
                return null;
            }

            Directory.CreateDirectory(TempDir);

            var existing = AssetDatabase.LoadAssetAtPath<AnimatorController>(TempControllerPath);
            if (existing != null && ControllerMatches(existing, clip)) return existing;
            if (existing != null) AssetDatabase.DeleteAsset(TempControllerPath);

            var controller = AnimatorController.CreateAnimatorControllerAtPath(TempControllerPath);
            controller.AddMotion(clip, 0);
            EditorUtility.SetDirty(controller);
            AssetDatabase.SaveAssets();
            return controller;
        }

        /// <summary>
        /// controller 是否已是"单层单状态、状态 motion 就是这条 clip"。
        /// **按名字比对而不是引用**：探针 FBX 重导后 clip 实例可能换对象，引用比对会误判成"要重建"，
        /// 而重建会换 GUID、连带把已存盘 lab 场景里的引用打成 missing（见上面那条 ⚠️）。
        /// </summary>
        private static bool ControllerMatches(AnimatorController controller, AnimationClip clip)
        {
            var layers = controller.layers;
            if (layers == null || layers.Length != 1) return false;
            var states = layers[0].stateMachine.states;
            if (states == null || states.Length != 1) return false;
            var motion = states[0].state.motion;
            return motion != null && motion.name == clip.name;
        }

        /// <summary>
        /// 在**当前场景**里装一个调试载体：X Bot 实例 + Animator（avatar 取自 X Bot）+ 指定 controller
        /// + `BlenderAnimationDebugger`。装配逻辑在运行时组件 `Attach(...)` 里，菜单路径与断言共用同一条。
        /// </summary>
        public static GameObject CreateActor(AnimatorController controller)
        {
            var xBot = AssetDatabase.LoadAssetAtPath<GameObject>(XBotPath);
            if (xBot == null)
            {
                Debug.LogError("[BlenderLab] 找不到载体模型: " + XBotPath);
                return null;
            }

            var actor = (GameObject)PrefabUtility.InstantiatePrefab(xBot);
            actor.name = ActorName;
            actor.transform.position = Vector3.zero;
            actor.transform.rotation = Quaternion.identity;

            BlenderAnimationDebugger.Attach(actor, controller, ProbeClipName);

            // 序列化字段同步到实例（`Attach` 只改内存，场景存盘要靠这两个字段）
            var dbg = actor.GetComponent<BlenderAnimationDebugger>();
            var so = new SerializedObject(dbg);
            so.FindProperty("_animator").objectReferenceValue = actor.GetComponent<Animator>();
            so.FindProperty("_clipName").stringValue = ProbeClipName;
            so.ApplyModifiedPropertiesWithoutUndo();
            return actor;
        }

        /// <summary>取探针 FBX 的模型根（animation-only，无网格；断言用它核"无控制骨/单根骨"）。</summary>
        public static GameObject LoadProbeModel()
        {
            return AssetDatabase.LoadAssetAtPath<GameObject>(ProbeFbxPath);
        }

        /// <summary>取探针 clip（按名；clips 里还含 Import 生成的 `__preview__` 条目，须按名挑）。</summary>
        public static AnimationClip LoadProbeClip()
        {
            return AssetDatabase.LoadAllAssetsAtPath(ProbeFbxPath)
                .OfType<AnimationClip>()
                .FirstOrDefault(c => c.name == ProbeClipName);
        }

        /// <summary>取探针 Avatar（Editor 由 `CreateFromThisModel` 生成）。</summary>
        public static Avatar LoadProbeAvatar()
        {
            return AssetDatabase.LoadAllAssetsAtPath(ProbeFbxPath).OfType<Avatar>().FirstOrDefault();
        }

        /// <summary>场景里当前那个调试载体（断言与 eval 读数用）。</summary>
        public static GameObject Actor()
        {
            return UnityEngine.Object.FindObjectsByType<BlenderAnimationDebugger>(
                FindObjectsInactive.Include, FindObjectsSortMode.None)
                .Select(d => d.gameObject).FirstOrDefault();
        }

        // ================= 自检 =================

        /// <summary>
        /// 四类漂移都 LogError：① 探针导入设置非 Humanoid（A4 会红）；② controller/clip 未接上；
        /// ③ avatar 没建出来 / 非人形；④ 读数点骨找不到（载体换过或 FBX 开了 Optimize Game Objects）。
        /// 返回一段可粘贴的报告（同一串也由测试消费）。
        /// </summary>
        public static string VerifyLabInfrastructure(GameObject actor)
        {
            var sb = new StringBuilder();
            var clip = LoadProbeClip();
            var avatar = LoadProbeAvatar();
            var importer = AssetImporter.GetAtPath(ProbeFbxPath) as ModelImporter;

            // ---- 导入设置与三条导入告警（#156 验收标准第 3 条）----
            // 三条告警串是 ModelImporter 的**内部序列化字段**（没有公开属性），只能经 SerializedObject 读；
            // 它们同时落在 `RigRoundTripProbe.fbx.meta` 里，是"无 animation import/retarget warning"的机器判据。
            var so = importer != null ? new SerializedObject(importer) : null;
            string importErrors = ReadSerializedString(so, "animationImportErrors", "m_AnimationImportErrors");
            string importWarnings = ReadSerializedString(so, "animationImportWarnings", "m_AnimationImportWarnings");
            string retargetWarnings = ReadSerializedString(so, "animationRetargetingWarnings",
                "m_AnimationRetargetingWarnings");

            sb.AppendLine($"探针 FBX: {ProbeFbxPath}");
            sb.AppendLine($"  animationType={importer?.animationType} (期望 Human) · " +
                          $"avatarSetup={importer?.avatarSetup} (期望 CreateFromThisModel) · " +
                          $"animationCompression={importer?.animationCompression} (期望 Off)");
            sb.AppendLine($"  clip={clip?.name ?? "(none)"} humanMotion={clip?.humanMotion} " +
                          $"length={clip?.length:F4}s frameRate={clip?.frameRate}");
            sb.AppendLine($"  avatar={avatar?.name ?? "(none)"} isValid={avatar?.isValid} isHuman={avatar?.isHuman}");
            sb.AppendLine($"  导入告警: errors=\"{importErrors}\" warnings=\"{importWarnings}\" " +
                          $"retarget=\"{retargetWarnings}\"");
            sb.AppendLine($"生成物: {TempControllerPath} / {TempScenePath}（均在 Assets/Temp/，不入库）");

            if (importer == null)
                Debug.LogError("[BlenderLab] 自检失败：探针 FBX 没有 ModelImporter");
            else if (importer.animationType != ModelImporterAnimationType.Human)
                Debug.LogError("[BlenderLab] 自检失败：animationType ≠ Human（A4 会红）");
            else if (importer.avatarSetup != ModelImporterAvatarSetup.CreateFromThisModel)
                Debug.LogError("[BlenderLab] 自检失败：avatarSetup ≠ CreateFromThisModel（A4 会红）");
            else if (importer.animationCompression != ModelImporterAnimationCompression.Off)
                Debug.LogError("[BlenderLab] 自检失败：animationCompression ≠ Off" +
                               "——压缩会把骨盆位移降采样掉，逐帧比对失去意义");
            if (!string.IsNullOrEmpty(importErrors) || !string.IsNullOrEmpty(importWarnings) ||
                !string.IsNullOrEmpty(retargetWarnings))
                Debug.LogError($"[BlenderLab] 自检失败：导入告警非空 → errors=\"{importErrors}\" " +
                               $"warnings=\"{importWarnings}\" retarget=\"{retargetWarnings}\"");

            // ---- 导出物形状：animation-only · 单根骨 · 零控制骨（#156 验收标准第 2 条）----
            var model = LoadProbeModel();
            if (model == null) Debug.LogError("[BlenderLab] 自检失败：取不到探针模型");
            else
            {
                var all = model.GetComponentsInChildren<Transform>(true);
                int ctrl = all.Count(t => t.name.Contains("CTRL_"));
                int bones = all.Count(t => t.name.StartsWith("mixamorig:"));
                int roots = all.Count(t => t.name == "mixamorig:Hips" && t.parent == model.transform);
                int meshes = all.Count(t => t.GetComponent<MeshRenderer>() != null ||
                                            t.GetComponent<SkinnedMeshRenderer>() != null);
                sb.AppendLine($"导出物形状: 骨 {bones} · 控制骨 {ctrl} · 根 mixamorig:Hips {roots} · 网格 {meshes}");
                if (ctrl != 0) Debug.LogError($"[BlenderLab] 自检失败：导出物含控制骨 {ctrl} 个");
                if (bones != 65) Debug.LogError($"[BlenderLab] 自检失败：骨数 {bones} ≠ 65（新增 Leaf Bone？）");
                if (roots != 1) Debug.LogError($"[BlenderLab] 自检失败：mixamorig:Hips 根数 {roots} ≠ 1（额外 Root 骨？）");
                if (meshes != 0) Debug.LogError($"[BlenderLab] 自检失败：导出物含网格 {meshes} 个（不是 animation-only）");
            }

            if (clip == null) Debug.LogError("[BlenderLab] 自检失败：取不到探针 clip");
            else if (!clip.humanMotion) Debug.LogError("[BlenderLab] 自检失败：clip.humanMotion = false");
            if (avatar == null || !avatar.isValid || !avatar.isHuman)
                Debug.LogError("[BlenderLab] 自检失败：探针 Avatar 未生成或非人形（avatarSetup 不是 CreateFromThisModel？）");

            if (actor == null)
            {
                Debug.LogError("[BlenderLab] 自检失败：场景里没有调试载体");
                return sb.ToString();
            }

            var animator = actor.GetComponent<Animator>();
            var dbg = actor.GetComponent<BlenderAnimationDebugger>();
            sb.AppendLine($"载体: {actor.name} animator={(animator != null)} debugger={(dbg != null)} " +
                          $"controller={animator?.runtimeAnimatorController?.name ?? "(none)"}");
            if (animator == null || dbg == null)
            {
                Debug.LogError("[BlenderLab] 自检失败：载体缺 Animator 或 BlenderAnimationDebugger");
                return sb.ToString();
            }
            if (animator.runtimeAnimatorController == null)
                Debug.LogError("[BlenderLab] 自检失败：Animator 没接 controller");

            int missing = 0;
            foreach (var bone in BlenderAnimationDebugger.ReadoutBones)
            {
                if (animator.GetBoneTransform(bone) == null)
                {
                    Debug.LogError("[BlenderLab] 自检失败：读数点骨缺失 → " + bone);
                    missing++;
                }
            }
            sb.AppendLine($"读数点: {BlenderAnimationDebugger.ReadoutBones.Length} 个，缺失 {missing}");
            return sb.ToString();
        }

        // ---- 小工具（口径同 AnimationRiggingLabBuilder.SetColor）----

        /// <summary>
        /// 读 ModelImporter 的内部序列化字符串。**没有公开属性**，且属性名在不同 Unity 版本里
        /// 带不带 `m_` 前缀不一致（`.meta` 里写的是 `animationImportErrors`）——故按多个候选名依次试。
        /// 找不到时返回 `"(n/a)"`（区别于"读到了空串"= 无告警）。
        /// </summary>
        private static string ReadSerializedString(SerializedObject so, params string[] names)
        {
            if (so == null) return "(n/a)";
            foreach (var n in names)
            {
                var p = so.FindProperty(n);
                if (p != null) return p.stringValue;
            }
            return "(n/a)";
        }

        private static void SetColor(GameObject go, Color color)
        {
            var mr = go.GetComponent<MeshRenderer>();
            if (mr == null) return;
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard"));
            mat.color = color;
            mr.sharedMaterial = mat;
        }
    }
}
