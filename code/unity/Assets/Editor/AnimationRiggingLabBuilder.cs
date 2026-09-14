// AnimationRigging lab 场景生成器（Editor）— #157
//
// 目标：给「Unity 动画约束与接触修正」这条能力一个**隔离的、可重复生成的**工作面，并按共同口径产出读数。
// 口径权威：design/presentation/动画处理能力对照实验.md
//   §2.4 场景最小构成（地面 · 载体 · 右手命中目标 · 左右脚目标 · 根/髋参考 · **约束权重可切**）
//   §3.1 读数纪律（lab 内**不挂**运行时足部贴地组件 —— 双脚贴地完全由 rig 约束负责，M2 归属才唯一）
//   §五 产物去向（lab 场景**入库**，并登记进 EditorBuildSettings —— 按名 LoadScene 的前提）
//
// ⚠️ 为什么场景必须入库、而其它 lab 场景不入库：`RigBuilder` 只在真场景的 `Awake` 拿到**已序列化**的 layers
//    时才会建图；运行时合成搭建（先 AddComponent、后 Add layer）**静默不生效**（危险点表 §六，2026-09-14 实测
//    代价 4 轮测试）。而 PlayMode 断言只能按名 `SceneManager.LoadScene` 加载 ⇒ lab 必须是仓库内场景资产。
//
// 用法：
//   菜单 YANTF → 动作演示 → 创建 AnimationRiggingLab 场景        （幂等重建 + 目标布置 + 自检）
//   headless: Unity -batchmode -quit -executeMethod YANTF.EditorTools.AnimationRiggingLabBuilder.CreateSceneBatch
//   Play 中经 eval 驱动探针：StartMeasureInPlay() / StartCaptureInPlay()
//   退出 Play 后：BakeFromCapture() 把采集到的人形姿势烘成 Assets/Animations/Derived/PhysicalAttack_ContactCorrected.anim
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Animations.Rigging;
using YANTF.ActionLab;
using YANTF.WalkerLab;   // CameraOrbit

namespace YANTF.EditorTools
{
    public static class AnimationRiggingLabBuilder
    {
        public const string SceneName = "AnimationRiggingLab";
        public const string ScenePath = "Assets/Scenes/AnimationRiggingLab.unity";
        public const string XBotPath = "Assets/Mixamo/Characters/X Bot.fbx";
        public const string SourceFbxPath = "Assets/Animations/Mixamo/Combat/PhysicalAttack.fbx";
        public const string SourceTakeName = "mixamo.com";
        public const string DerivedDir = "Assets/Animations/Derived";
        public const string DerivedPath = DerivedDir + "/PhysicalAttack_ContactCorrected.anim";
        /// <summary>采集过程物（被 .gitignore 的 `_` 前缀约定排除；只在本机 Play→烘焙之间传递）。</summary>
        public const string CapturePath = DerivedDir + "/_contact_capture.json";
        /// <summary>校准过程物（同上；Play 期布置的目标 → 写回场景的中间文件）。</summary>
        public const string CalibrationPath = DerivedDir + "/_lab_calibration.json";

        // 场景内的稳定标识（改名等于破坏下游断言与文档）
        public const string ActorName = "AnimationRiggingLab演示者(X Bot)";
        public const string RigRootName = "Rig(AnimationRigging)";
        public const string RightArmIKName = "RightArmIK";
        public const string LeftLegIKName = "LeftLegIK";
        public const string RightLegIKName = "RightLegIK";
        public const string RightHandTargetName = "RightHandTarget";
        public const string LeftFootTargetName = "LeftFootTarget";
        public const string RightFootTargetName = "RightFootTarget";
        public const string HipsRefName = "HipsRef";

        // ================= 场景生成 =================

        [MenuItem("YANTF/动作演示/创建 AnimationRiggingLab 场景")]
        public static void CreateSceneMenu() => CreateScene();

        public static void CreateSceneBatch() => CreateScene();

        /// <summary>
        /// 幂等重建 lab 场景：地面 + 载体（X Bot + `ActionLab.controller`）+ 三条最小 IK 约束 + 探针 + 相机，
        /// 并把三个目标**按接触帧口径**摆好（§2.3），最后跑自检。
        /// </summary>
        public static void CreateScene()
        {
            var xBot = AssetDatabase.LoadAssetAtPath<GameObject>(XBotPath);
            if (xBot == null)
            {
                Debug.LogError("[RigLab] 找不到载体模型: " + XBotPath + "（先按 code/unity/README.md §二·E 导入 X Bot.fbx）");
                return;
            }

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 地面：过原点的水平面，表面 y = 0（§2.1 共同样本固定项）----
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

            // ---- 载体：站在原点、面向该引擎的 forward、无附加旋转（§2.1）----
            var (controller, _, _) = ActionLabBuilder.BuildOrLoadController();
            var actor = (GameObject)PrefabUtility.InstantiatePrefab(xBot);
            actor.name = ActorName;
            actor.transform.position = Vector3.zero;
            actor.transform.rotation = Quaternion.identity;

            var animator = actor.GetComponent<Animator>();
            if (animator == null) animator = actor.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller;
            animator.applyRootMotion = false;

            // ⚠️ 刻意**不加** `FootGroundingIK` / `CharacterController` / `ActionLabDriver`：
            //    §3.1 裁定 lab 内替换运行时足部贴地——双脚贴地完全由 rig 约束负责，否则 M2 读数无法归属。
            var probe = actor.GetComponent<AnimationRiggingProbe>();
            if (probe == null) probe = actor.AddComponent<AnimationRiggingProbe>();
            probe.animator = animator;
            probe.groundY = 0f;

            BuildRig(actor, animator, probe);

            // ---- 髋参考（§2.4 的"根/髋参考"节点；只作参考，不驱动任何东西）----
            var hipsRefGo = new GameObject(HipsRefName);
            hipsRefGo.transform.SetParent(actor.transform, false);
            probe.hipsReference = hipsRefGo.transform;

            // ---- 相机（能看见角色即可；lab 的用途是时间轴逐帧检查，不追求观感）----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            var orbit = camGo.AddComponent<CameraOrbit>();
            orbit.target = actor.transform;   // ⚠️ 必须显式设：留空会兜底成自身 transform
            orbit.Snap();

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            RegisterInBuildSettings();

            // ---- 目标布置（§2.3）：按接触帧口径把三个目标摆到场景里，随后序列化 ----
            var clip = LoadSourceClip();
            if (clip == null)
            {
                Debug.LogError("[RigLab] 取不到源 clip，目标布置跳过: " + SourceFbxPath);
            }
            else
            {
                probe.CaptureFirstFrameReference(clip);
                int tc = probe.FindContactFrame(clip);
                if (tc < 0) Debug.LogError("[RigLab] 取帧失败，目标未布置");
                else probe.PlaceTargetsAtContactFrame(clip, tc);
                // 布置完把姿势还原到源 clip 首帧，避免把探针的采样姿势留在场景里
                clip.SampleAnimation(actor, 0f);
                // ⚠️ 必须显式标脏：接触帧号与首帧基准是**序列化字段**，Play 期的读数全靠它们——
                //    不标脏就只改了内存对象、存盘的场景里还是默认值（实测踩到：Play 里 M1 = 762 mm 的垃圾读数）
                EditorUtility.SetDirty(probe);
                EditorSceneManager.MarkSceneDirty(scene);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }

            VerifyLabInfrastructure();
            Debug.Log("[RigLab] 场景已生成: " + ScenePath);
        }

        /// <summary>建「RigBuilder + Rig + 右手/左腿/右腿三条最小 TwoBoneIK + 三个目标」。幂等。</summary>
        private static void BuildRig(GameObject actor, Animator animator, AnimationRiggingProbe probe)
        {
            var rigBuilder = actor.GetComponent<RigBuilder>();
            if (rigBuilder == null) rigBuilder = actor.AddComponent<RigBuilder>();

            rigBuilder.layers.Clear();
            var stale = actor.transform.Find(RigRootName);
            if (stale != null) UnityEngine.Object.DestroyImmediate(stale.gameObject);

            var rigGo = new GameObject(RigRootName);
            rigGo.transform.SetParent(actor.transform, false);
            var rig = rigGo.AddComponent<Rig>();

            var rightArm = AddTwoBoneIK(rigGo.transform, RightArmIKName, RightHandTargetName,
                animator, HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand);
            var leftLeg = AddTwoBoneIK(rigGo.transform, LeftLegIKName, LeftFootTargetName,
                animator, HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot);
            var rightLeg = AddTwoBoneIK(rigGo.transform, RightLegIKName, RightFootTargetName,
                animator, HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot);

            // 场景随附权重 = 1：lab 的用途就是"看修正后的姿势"；探针在读数时把 0/1 两态各取一次（§3.1）
            rig.weight = 1f;
            if (rightArm != null) rightArm.weight = 1f;
            if (leftLeg != null) leftLeg.weight = 1f;
            if (rightLeg != null) rightLeg.weight = 1f;

            rigBuilder.layers.Add(new RigLayer(rig, true));

            probe.rigBuilder = rigBuilder;
            probe.rig = rig;
            probe.rightArmIK = rightArm;
            probe.leftLegIK = leftLeg;
            probe.rightLegIK = rightLeg;
            probe.rightHandTarget = rigGo.transform.Find(RightArmIKName + "/" + RightHandTargetName);
            probe.leftFootTarget = rigGo.transform.Find(LeftLegIKName + "/" + LeftFootTargetName);
            probe.rightFootTarget = rigGo.transform.Find(RightLegIKName + "/" + RightFootTargetName);
        }

        private static TwoBoneIKConstraint AddTwoBoneIK(Transform rigRoot, string ikName, string targetName,
            Animator animator, HumanBodyBones rootBone, HumanBodyBones midBone, HumanBodyBones tipBone)
        {
            var ikGo = new GameObject(ikName);
            ikGo.transform.SetParent(rigRoot, false);
            var ik = ikGo.AddComponent<TwoBoneIKConstraint>();

            var targetGo = new GameObject(targetName);
            targetGo.transform.SetParent(ikGo.transform, false);
            var tip = animator.GetBoneTransform(tipBone);
            targetGo.transform.position = tip != null ? tip.position : animator.transform.position;

            ik.data.root = animator.GetBoneTransform(rootBone);
            ik.data.mid = animator.GetBoneTransform(midBone);
            ik.data.tip = tip;
            ik.data.target = targetGo.transform;
            ik.data.maintainTargetRotationOffset = false;
            ik.data.hintWeight = 0f;

            var missing = new List<string>();
            if (ik.data.root == null) missing.Add(rootBone.ToString());
            if (ik.data.mid == null) missing.Add(midBone.ToString());
            if (ik.data.tip == null) missing.Add(tipBone.ToString());
            if (missing.Count > 0)
                Debug.LogError("[RigLab] " + ikName + " 骨链绑定为空 → " + string.Join(" / ", missing) +
                               "（Humanoid 载体换过？FBX 是否开了 Optimize Game Objects？）");
            return ik;
        }

        /// <summary>把 lab 场景登记进 build settings（幂等；`ActionLab` 保持 index 0）。</summary>
        public static void RegisterInBuildSettings()
        {
            var scenes = EditorBuildSettings.scenes.ToList();
            if (scenes.Any(s => s.path == ScenePath)) return;
            scenes.Add(new EditorBuildSettingsScene(ScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
            Debug.Log("[RigLab] 已登记进 build settings: " + ScenePath + "（index " + (scenes.Count - 1) + "）");
        }

        // ================= 自检（口径同 ActionLabBuilder.VerifyRigInfrastructure）=================

        /// <summary>
        /// 三类漂移都 LogError：① 骨链静默失效（载体换过 / FBX 开了 Optimize Game Objects）；
        /// ② layers 数不对（有人手工往场景加 Rig）；③ 探针的目标引用丢了（builder 被绕过）。
        /// </summary>
        public static bool VerifyLabInfrastructure()
        {
            var probe = UnityEngine.Object.FindFirstObjectByType<AnimationRiggingProbe>();
            if (probe == null) { Debug.LogError("[RigLab] 自检失败：场景里找不到 AnimationRiggingProbe"); return false; }

            var rb = probe.rigBuilder;
            if (rb == null) { Debug.LogError("[RigLab] 自检失败：探针未接 RigBuilder"); return false; }
            if (rb.layers.Count != 1)
            {
                Debug.LogError("[RigLab] 自检失败：layers 应为 1，实测 " + rb.layers.Count + "（手工加 Rig 会被下次重建冲掉）");
                return false;
            }

            int bad = 0;
            foreach (var ik in new[] { probe.rightArmIK, probe.leftLegIK, probe.rightLegIK })
            {
                if (ik == null) { Debug.LogError("[RigLab] 自检失败：少一条约束"); bad++; continue; }
                if (ik.data.root == null || ik.data.mid == null || ik.data.tip == null || ik.data.target == null)
                { Debug.LogError("[RigLab] 自检失败：" + ik.name + " 骨链/目标有空引用"); bad++; }
            }

            if (probe.rightHandTarget == null || probe.leftFootTarget == null || probe.rightFootTarget == null)
            { Debug.LogError("[RigLab] 自检失败：三个目标节点引用不全"); bad++; }
            if (probe.animator.GetBoneTransform(HumanBodyBones.RightHand) == null)
            { Debug.LogError("[RigLab] 自检失败：载体取不到 RightHand（不是 Humanoid？）"); bad++; }
            // 归属唯一（§3.1）：lab 内**不得**挂运行时足部贴地组件
            if (probe.GetComponent<FootGroundingIK>() != null)
            { Debug.LogError("[RigLab] 自检失败：lab 载体上挂了 FootGroundingIK——§3.1 要求双脚贴地只由 rig 约束负责"); bad++; }

            if (bad == 0)
                Debug.Log("[RigLab] 自检 ✅ RigBuilder 层 1 · 三条约束骨链非空 · 三目标齐 · 无 FootGroundingIK（§3.1 归属唯一）");
            return bad == 0;
        }

        // ================= Play 中驱动探针 =================

        /// <summary>Play 中调用：跑 M1–M6 的关/开对照矩阵（读数以 JSON 一行打到 Console）。</summary>
        public static void StartMeasureInPlay()
        {
            var probe = RequireProbe();
            var clip = LoadSourceClip();
            if (probe == null || clip == null) return;
            // ⚠️ 这里**不重算**取帧与目标：它们已在建场景时算好并序列化进场景。
            //    Play 中 `SampleAnimation` 的写入会被动画播放图覆盖（实测：目标落到离手 762 mm 处），
            //    唯一的例外是"跑一遍矩阵"，那是靠 `Animator.Play` 定位帧，走的是真播放图，不受影响。
            if (probe.contactFrame < 0)
            {
                Debug.LogError("[RigLab] 场景里没有接触帧（contactFrame < 0）——先跑菜单「创建 AnimationRiggingLab 场景」");
                return;
            }
            probe.StartCoroutine(probe.RunMeasureMatrix(clip));
            Debug.Log("[RigLab] 测量已启动（contactFrame=" + probe.contactFrame + "）");
        }

        /// <summary>Play 中调用：抓逐帧"约束开"的人形姿势到 JSON（退出 Play 后由 BakeFromCapture 烘焙）。</summary>
        public static void StartCaptureInPlay()
        {
            var probe = RequireProbe();
            var clip = LoadSourceClip();
            if (probe == null || clip == null) return;
            if (!Directory.Exists(DerivedDir)) Directory.CreateDirectory(DerivedDir);
            var abs = Path.GetFullPath(CapturePath);
            if (File.Exists(abs)) File.Delete(abs);
            probe.StartCoroutine(probe.CaptureCorrectedPoses(clip, abs));
            Debug.Log("[RigLab] 采集已启动 → " + abs);
        }

        private static AnimationRiggingProbe RequireProbe()
        {
            var probe = UnityEngine.Object.FindFirstObjectByType<AnimationRiggingProbe>();
            if (probe == null) { Debug.LogError("[RigLab] 场景里找不到 AnimationRiggingProbe（先跑菜单创建 lab 场景）"); return null; }
            return probe;
        }

        public static AnimationClip LoadSourceClip()
            => ActionLabBuilder.LoadClipForProbe(SourceFbxPath, SourceTakeName);

        /// <summary>供 PlayMode 断言经反射桥取派生件（该 asmdef 无 UnityEditor 引用，口径同 ActionLabGripTests 头注）。</summary>
        public static AnimationClip LoadBakedForProbe()
            => AssetDatabase.LoadAssetAtPath<AnimationClip>(DerivedPath);

        /// <summary>Play 中调用：跑校准（取帧 + 按 Play 期姿势布置目标），结果落 JSON 供写回场景。</summary>
        public static void StartCalibrateInPlay()
        {
            var probe = RequireProbe();
            var clip = LoadSourceClip();
            if (probe == null || clip == null) return;
            var abs = Path.GetFullPath(CalibrationPath);
            if (File.Exists(abs)) File.Delete(abs);
            probe.StartCoroutine(probe.CalibrateInPlay(clip, abs));
            Debug.Log("[RigLab] 校准已启动 → " + abs);
        }

        /// <summary>Play 中调用：关约束、只采派生件，验证"脱离约束状态仍保持修正结果"（验收标准 ④）。</summary>
        public static void VerifyBakedInPlay()
        {
            var probe = RequireProbe();
            if (probe == null) return;
            var baked = AssetDatabase.LoadAssetAtPath<AnimationClip>(DerivedPath);
            if (baked == null) { Debug.LogError("[RigLab] 派生件不存在: " + DerivedPath + "（先烘焙）"); return; }
            int curves = AnimationUtility.GetCurveBindings(baked).Length;
            int frame = probe.contactFrame >= 0 ? probe.contactFrame : 0;
            probe.VerifyBakedClip(baked, frame, curves);
        }

        [Serializable] private class Calibration
        {
            public int contactFrame;
            public float contactTime;
            public float[] firstFrameHipPos;
            public float[] firstFrameHipForward;
            public float[] rightHandTarget;
            public float[] rightHandTargetRot;
            public float[] leftFootTarget;
            public float[] leftFootTargetRot;
            public float[] rightFootTarget;
            public float[] rightFootTargetRot;
        }

        /// <summary>
        /// 退出 Play 后调用：把校准结果写进 lab 场景（探针的接触帧号/首帧基准 + 三个目标的世界位置），存盘。
        /// ⚠️ 目标与基准必须与 Play 期的**姿势语义**一致，否则约束够不到目标（见探针 CalibrateInPlay 头注）。
        /// </summary>
        [MenuItem("YANTF/动作演示/把校准结果写回 lab 场景")]
        public static bool ApplyCalibrationFromFile()
        {
            var abs = Path.GetFullPath(CalibrationPath);
            if (!File.Exists(abs)) { Debug.LogError("[RigLab] 校准文件不存在: " + abs + "（先 StartCalibrateInPlay）"); return false; }
            var cal = JsonUtility.FromJson<Calibration>(File.ReadAllText(abs));
            if (cal == null) { Debug.LogError("[RigLab] 校准文件解析失败"); return false; }

            var probe = RequireProbe();
            if (probe == null) return false;

            probe.contactFrame = cal.contactFrame;
            probe.contactTime = cal.contactTime;
            probe.firstFrameHipPos = ToVector3(cal.firstFrameHipPos);
            probe.firstFrameHipForward = ToVector3(cal.firstFrameHipForward);
            probe.rightHandTarget.position = ToVector3(cal.rightHandTarget);
            probe.rightHandTarget.rotation = ToQuaternion(cal.rightHandTargetRot);
            probe.leftFootTarget.position = ToVector3(cal.leftFootTarget);
            probe.leftFootTarget.rotation = ToQuaternion(cal.leftFootTargetRot);
            probe.rightFootTarget.position = ToVector3(cal.rightFootTarget);
            probe.rightFootTarget.rotation = ToQuaternion(cal.rightFootTargetRot);

            // 布置完把骨架摆到源 clip 首帧：避免把"采样姿势"留在场景里
            var clip = LoadSourceClip();
            if (clip != null) probe.PoseAtFrame(clip, 0);

            EditorUtility.SetDirty(probe);
            EditorUtility.SetDirty(probe.rightHandTarget);
            EditorUtility.SetDirty(probe.leftFootTarget);
            EditorUtility.SetDirty(probe.rightFootTarget);
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log("[RigLab] 校准已写回场景: contactFrame=" + probe.contactFrame +
                      " handTarget=" + probe.rightHandTarget.position.ToString("F4") +
                      " footL=" + probe.leftFootTarget.position.ToString("F4") +
                      " footR=" + probe.rightFootTarget.position.ToString("F4"));
            return true;
        }

        private static Vector3 ToVector3(float[] a)
            => (a != null && a.Length >= 3) ? new Vector3(a[0], a[1], a[2]) : Vector3.zero;

        private static Quaternion ToQuaternion(float[] a)
            => (a != null && a.Length >= 4) ? new Quaternion(a[0], a[1], a[2], a[3]) : Quaternion.identity;

        // ================= 烘焙：采集 → 独立 Animation Sequence =================

        [Serializable] private class CaptureFile
        {
            public string clip;
            public float frameRate;
            public int totalFrames;
            public int muscleCount;
            public PoseEntry[] poses;
        }

        [Serializable] private class PoseEntry
        {
            public int frame;
            public float[] bodyPosition;
            public float[] bodyRotation;
            public float[] muscles;
        }

        [MenuItem("YANTF/动作演示/烘焙接触修正 clip（需先采集）")]
        public static void BakeMenu()
        {
            var clip = BakeFromCapture();
            if (clip == null) Debug.LogError("[RigLab] 烘焙失败");
            else Debug.Log("[RigLab] 已烘焙 " + DerivedPath + " — len=" + clip.length.ToString("F4") +
                           " 曲线=" + AnimationUtility.GetCurveBindings(clip).Length);
        }

        /// <summary>
        /// 把采集到的人形姿势（肌肉 + 根）写成一条独立 AnimationClip。
        /// 绑定口径：肌肉曲线绑到 `Animator` 上、属性名取 `HumanTrait.MuscleName[i]`；根取 `RootT.x/y/z` 与 `RootQ.x/y/z/w`
        /// ——这正是 Humanoid clip 的曲线形态（与 FBX 导入件同形），故能在 Humanoid 载体上独立播放。
        /// </summary>
        public static AnimationClip BakeFromCapture()
        {
            var abs = Path.GetFullPath(CapturePath);
            if (!File.Exists(abs)) { Debug.LogError("[RigLab] 采集文件不存在: " + abs + "（先 StartCaptureInPlay）"); return null; }

            var cap = JsonUtility.FromJson<CaptureFile>(File.ReadAllText(abs));
            if (cap == null || cap.poses == null || cap.poses.Length == 0)
            { Debug.LogError("[RigLab] 采集文件解析失败或为空"); return null; }

            float frameRate = cap.frameRate > 0f ? cap.frameRate : 30f;
            var clip = new AnimationClip { frameRate = frameRate, legacy = false, wrapMode = WrapMode.Clamp };

            int muscleCount = HumanTrait.MuscleCount;
            var names = HumanTrait.MuscleName;

            // 肌肉曲线
            for (int m = 0; m < muscleCount; m++)
            {
                var keys = new Keyframe[cap.poses.Length];
                for (int i = 0; i < cap.poses.Length; i++)
                {
                    var p = cap.poses[i];
                    float v = (p.muscles != null && m < p.muscles.Length) ? p.muscles[m] : 0f;
                    keys[i] = new Keyframe(p.frame / frameRate, v);
                }
                var binding = EditorCurveBinding.FloatCurve(string.Empty, typeof(Animator), names[m]);
                AnimationUtility.SetEditorCurve(clip, binding, new AnimationCurve(keys));
            }

            // 根曲线（RootT / RootQ）——Humanoid 的位移与朝向都在这两条上
            string[] rootT = { "RootT.x", "RootT.y", "RootT.z" };
            for (int a = 0; a < 3; a++)
            {
                var keys = new Keyframe[cap.poses.Length];
                for (int i = 0; i < cap.poses.Length; i++)
                {
                    var bp = cap.poses[i].bodyPosition;
                    keys[i] = new Keyframe(cap.poses[i].frame / frameRate, bp != null && a < bp.Length ? bp[a] : 0f);
                }
                AnimationUtility.SetEditorCurve(clip,
                    EditorCurveBinding.FloatCurve(string.Empty, typeof(Animator), rootT[a]), new AnimationCurve(keys));
            }
            string[] rootQ = { "RootQ.x", "RootQ.y", "RootQ.z", "RootQ.w" };
            for (int a = 0; a < 4; a++)
            {
                var keys = new Keyframe[cap.poses.Length];
                for (int i = 0; i < cap.poses.Length; i++)
                {
                    var bq = cap.poses[i].bodyRotation;
                    keys[i] = new Keyframe(cap.poses[i].frame / frameRate, bq != null && a < bq.Length ? bq[a] : (a == 3 ? 1f : 0f));
                }
                AnimationUtility.SetEditorCurve(clip,
                    EditorCurveBinding.FloatCurve(string.Empty, typeof(Animator), rootQ[a]), new AnimationCurve(keys));
            }

            var settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = false;
            settings.loopBlend = false;
            AnimationUtility.SetAnimationClipSettings(clip, settings);

            if (!Directory.Exists(DerivedDir)) Directory.CreateDirectory(DerivedDir);
            AssetDatabase.DeleteAsset(DerivedPath);
            AssetDatabase.CreateAsset(clip, DerivedPath);
            AssetDatabase.SaveAssets();
            AssetDatabase.ImportAsset(DerivedPath);
            return AssetDatabase.LoadAssetAtPath<AnimationClip>(DerivedPath);
        }

        // ================= 小工具 =================

        private static void SetColor(GameObject go, Color c)
        {
            var r = go.GetComponent<Renderer>();
            if (r == null) return;
            var mat = new Material(Shader.Find("Standard"));
            mat.color = c;
            r.sharedMaterial = mat;
        }
    }
}
