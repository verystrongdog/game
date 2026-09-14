// ActionLab 场景/controller 生成器（Editor）— 规格 §六 + #124 Q-B2/Q-B5
// - 幂等：controller 存在则加载并在其上补齐（状态按 ActionCatalog 构造成立，状态名 = 词表 id）
// - 防漂移（#124 Q-B5 分档）：clip 按 catalog.ClipAssetPath 资产存在性接线——
//     资产存在 → 必须挂上 clip（找不到 → 警告）；资产不存在 → 状态留空，计入缺口清单（Console）
// - 派生件：建场景前 EnsureSitDown()（SitDown = Sit To Stand 反转），并 VerifyDerived() 自检漂移
// - 足部贴地（规格 §四·乙）：打开 controller Base Layer 的 iKPass 并挂 FootGroundingIK——
//     不开 iKPass 则 OnAnimatorIK 不会被调用，足 IK 静默失效
// - 椅子（规格 §四·丁）：**三张**实心可推的椅子（坐板 + 四条腿 + 靠背 + Rigidbody + ChairSeat 锚点），
//     摆位是演示常量；就座锚点由 ChairSeat 从椅子 transform 实时求得（不再烘任何世界坐标）
// - 用法：菜单 YANTF → 动作演示 → 创建 ActionLab 场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.ActionLabBuilder.CreateSceneBatch
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Animations.Rigging;   // Animation Rigging 接入（2026-09-14）
using YANTF.ActionLab;
using YANTF.WalkerLab;   // CameraOrbit（环绕观察相机）

namespace YANTF.EditorTools
{
    public static class ActionLabBuilder
    {
        private const string ScenePath = "Assets/Scenes/ActionLab.unity";
        private const string ControllerPath = "Assets/ActionLab/ActionLab.controller";
        private const string XBotPath = "Assets/Mixamo/Characters/X Bot.fbx";
        private const string YBotPath = "Assets/Mixamo/Characters/Y Bot.fbx";

        // ---- 椅子几何（全部来自 2026-09-12/13 实测，非目视估计）----
        /// <summary>坐面高度 m = 坐姿（Sitting Idle + 足 IK）下髋部半径 0.30 m 内蒙皮网格最低点。
        /// 实测 r=0.10/0.15/0.20/0.30 四档全部收敛到 0.4449（r=0.40 起会把小腿顶点算进来 → 失真）。</summary>
        private const float ChairSeatTopY = 0.4449f;
        private const float ChairSeatThickness = 0.05f;
        private const float ChairSeatSize = 0.42f;    // 边长：容下两侧臀部（实测接触点 x 偏 +0.084）
        private const float ChairLegSize = 0.05f;
        private const float ChairLegSpread = 0.165f;  // = 坐板半边 − 腿半 − 0.02（同旧凳实测值）
        private const float ChairBackHeight = 0.35f;
        private const float ChairBackThickness = 0.04f;
        private const float ChairMass = 6f;           // 演示常量：轻到能被角色推开，重到不会自己滑走

        // ---- 持椅挂点参数（规格 §七；**演示常量，非正典**，手感待 Play / owner 目视调）----
        /// <summary>阻尼摆动刚度（§戊·2#9 的 B 情形）。> 0 即启用弹簧阻尼；= 0 退化为刚性挂点（A）。</summary>
        private const float GripSwayStiffness = 120f;
        /// <summary>阻尼摆动阻尼系数。ζ = c / (2√k) ≈ 0.82（略欠阻尼 → 有"重量感"但不抖）。</summary>
        private const float GripSwayDamping = 18f;

        /// <summary>
        /// 三张椅子的摆位（**演示摆位，非正典数值**）：由 builder 摆在出生点之外，逼出"走过去找"这件事。
        /// 朝向各不相同 → 「在椅子前侧」这条判定才有区分度（规格 §四·丁#2）。
        /// </summary>
        private static readonly Vector3[] ChairPositions =
        {
            new Vector3(-2.2f, 0f, 2.4f),
            new Vector3(2.6f, 0f, 1.4f),
            new Vector3(0.4f, 0f, -2.6f),
        };
        private static readonly float[] ChairYaws = { 200f, 330f, 90f };

        [MenuItem("YANTF/动作演示/创建 ActionLab 场景")]
        public static void CreateSceneMenu() => CreateScene();

        public static void CreateSceneBatch() => CreateScene();

        public static void CreateScene()
        {
            // ---- 载体前置检查：X Bot 须已按手册导入（Assets/Mixamo/Characters/X Bot.fbx, Rig=Humanoid）----
            var xBot = AssetDatabase.LoadAssetAtPath<GameObject>(XBotPath);
            if (xBot == null)
            {
                Debug.LogError("[ActionLab] 找不到载体模型: " + XBotPath +
                               "\n请先按 code/unity/README.md §二·E 步骤 1 导入 X Bot.fbx（Rig → Humanoid → Apply）。" +
                               "Y Bot 备用路径: " + YBotPath);
                return;
            }

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 地面 / 参照柱 / 光（复用 Walker/Ki 布局口径）----
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(24f, 1f, 24f);
            SetColor(ground, new Color(0.55f, 0.6f, 0.5f));
            AddMarker(new Vector3(0f, 0f, 3f), new Color(0.9f, 0.35f, 0.35f));
            AddMarker(new Vector3(3f, 0f, 0f), new Color(0.35f, 0.8f, 0.4f));

            // ---- 椅子（就座交互的落点；规格 §四·丁）----
            AddChairs();

            var sunGo = new GameObject("Sun");
            var light = sunGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            sunGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            // ---- 派生件：确保存在且与源一致（SitDown = Sit To Stand 反转）----
            DerivedClipBuilder.EnsureSitDown();
            DerivedClipBuilder.VerifyDerived();

            // ---- AnimatorController：L1 12 态（状态名 = 词表 id），clip 按资产存在性接线 ----
            var (controller, wired, gaps) = BuildOrLoadController();

            // ---- 载体实例 + 组件 ----
            var actor = (GameObject)PrefabUtility.InstantiatePrefab(xBot);
            actor.name = "ActionLab演示者(X Bot)";
            actor.transform.position = new Vector3(0f, 0f, 0f);

            var animator = actor.GetComponent<Animator>();
            if (animator == null) animator = actor.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller;
            animator.applyRootMotion = false; // 位移交给 CharacterController（契约 A）

            if (actor.GetComponent<CharacterController>() == null) actor.AddComponent<CharacterController>();
            if (actor.GetComponent<ActionPlayer>() == null) actor.AddComponent<ActionPlayer>();
            if (actor.GetComponent<ActionLabDriver>() == null) actor.AddComponent<ActionLabDriver>();
            // 足底接地（规格 §四·乙）：需 controller 层 iKPass 打开，二者缺一不生效
            if (actor.GetComponent<FootGroundingIK>() == null) actor.AddComponent<FootGroundingIK>();
            // Animation Rigging 接入点（2026-09-14）：**惰性**骨架，权重 0，不产生任何行为
            BuildRigInfrastructure(actor, animator);
            // 持握调台（2026-09-14，非正典）：Play 中拖 Inspector 手调姿势 + curl 包握；场景里保持惰性
            if (actor.GetComponent<GripTuningStand>() == null) actor.AddComponent<GripTuningStand>();

            // ---- 相机：环绕跟随（owner 裁定 2026-09-12 折进 builder —— 不再靠"每次重建手工挂"）----
            // 背景：观察相机原定"手动挂载、不改 builder"（README §二·G 裁定）。但场景自 #136 起已入库、
            //   而本 builder 每次都是**新建场景**，于是每次重建都会把手工挂载冲掉（2026-09-12 实测踩到）。
            //   既然"每次重建都自动挂上"正是当时的延期条件，此处折进 builder。
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            var orbit = camGo.AddComponent<CameraOrbit>();
            // ⚠️ 必须设 target：留空时 CameraOrbit.Start() 会兜底成自身 transform → 相机绕自己头顶打转
            orbit.target = actor.transform;
            orbit.Snap();   // 由轨道参数（distance/pitch/yaw）定初位，替掉原先写死的固定机位

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);

            // ---- 接入自检（口径同 VerifyDerived）：接入点必须在，且必须**仍是惰性**----
            VerifyRigInfrastructure(actor);

            Debug.Log($"[ActionLab] 场景已保存: {ScenePath} — Play：WASD 走 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 6坐（需走到椅子前）7起身 / R 重置");
            Debug.Log($"[ActionLab] 椅子 {ChairPositions.Length} 张（实心可推；就座锚点 = 坐面中心沿椅子 forward 前方 {ChairSeat.DefaultAnchorDistance} m，交互半径 {ChairSeat.DefaultInteractRadius} m）");
            var gripAnchors = BuildGripAnchors();
            var gripPoses = DefaultGripPoses();
            Debug.Log($"[ActionLab] 持椅挂点：锚点 {gripAnchors.Length} 个（{string.Join("/", System.Array.ConvertAll(gripAnchors, a => a.id))}，均为**椅子局部坐标**）"
                    + $" · 逐状态挂点 {gripPoses.Length} 组（Carry1H 垂下 / Wield2H 横在身前 / DefendCarry1H 当盾，均在 {HumanBodyBones.RightHand}）"
                    + $" · 阻尼摆动 刚度 {GripSwayStiffness} / 阻尼 {GripSwayDamping}（演示常量，非正典）");
            Debug.Log($"[ActionLab] controller 接线: {wired}/{ActionCatalog.Level1.Count} 态有 clip（防漂移分档：已导入资产 → 有 clip；缺口 {gaps.Count} 个 → 留空待填）");
            if (gaps.Count > 0)
            {
                var gapNames = string.Join(", ", gaps);
                Debug.LogWarning("[ActionLab] 缺口状态（clip 留空，导入后重跑菜单自动接线）: " + gapNames);
            }
        }

        /// <summary>
        /// 幂等构建 controller：加载或新建 → 保证 L1 全部状态存在（名 = id）→ 按资产存在性挂 clip。
        /// 返回 (controller, 有 clip 状态数, 缺口清单)。
        /// </summary>
        public static (AnimatorController, int, List<string>) BuildOrLoadController()
        {
            var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
            if (controller == null)
            {
                if (!Directory.Exists("Assets/ActionLab")) Directory.CreateDirectory("Assets/ActionLab");
                controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
            }
            var sm = controller.layers[0].stateMachine;

            int wired = 0;
            var gaps = new List<string>();

            foreach (var entry in ActionCatalog.Level1)
            {
                var st = EnsureState(sm, entry.Id);
                var clip = LoadClip(entry.ClipAssetPath, entry.Id);
                if (clip != null)
                {
                    st.motion = clip;
                    wired++;
                }
                else
                {
                    st.motion = null;
                    if (entry.ClipAssetPath != null && AssetDatabase.LoadAssetAtPath<Object>(entry.ClipAssetPath) != null)
                    {
                        // 资产在但没取到 clip → 真异常，报错而非静默
                        Debug.LogError("[ActionLab] 状态 " + entry.Id + " 资产存在但未取到 clip: " + entry.ClipAssetPath);
                    }
                    gaps.Add(entry.Id);
                }
            }

            // 足部贴地（规格 §四·乙）前置：层必须开 IK Pass，否则 OnAnimatorIK 不会被调用、足 IK 静默失效
            var layers = controller.layers;
            if (!layers[0].iKPass)
            {
                layers[0].iKPass = true;
                controller.layers = layers;
                Debug.Log("[ActionLab] 已打开 Base Layer 的 IK Pass（足 IK 前置）");
            }

            var defaultState = sm.defaultState;
            if (defaultState == null || defaultState.name != ActionIds.Idle)
            {
                var idleState = FindState(sm, ActionIds.Idle);
                if (idleState != null) sm.defaultState = idleState;
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.ImportAsset(ControllerPath);
            return (controller, wired, gaps);
        }

        private static AnimatorState EnsureState(AnimatorStateMachine sm, string name)
        {
            var existing = FindState(sm, name);
            if (existing != null) return existing;
            var st = sm.AddState(name);
            st.writeDefaultValues = true;
            return st;
        }

        private static AnimatorState FindState(AnimatorStateMachine sm, string name)
        {
            foreach (var child in sm.states)
            {
                if (child.state.name == name) return child.state;
            }
            return null;
        }

        /// <summary>
        /// 取 clip：路径是 .anim 派生件 → 直接取该 AnimationClip；
        /// 路径是 FBX → 取其中一条 clip（优先名字匹配 词表 id / 文件主干，否则第一条非预览曲线集）。
        /// </summary>
        private static AnimationClip LoadClip(string assetPath, string entryId)
        {
            if (string.IsNullOrEmpty(assetPath)) return null;

            if (assetPath.EndsWith(".anim"))
                return AssetDatabase.LoadAssetAtPath<AnimationClip>(assetPath);

            var assets = AssetDatabase.LoadAllAssetsAtPath(assetPath);
            AnimationClip first = null;
            string stem = Path.GetFileNameWithoutExtension(assetPath);
            foreach (var sub in assets)
            {
                if (!(sub is AnimationClip clip)) continue;
                if (clip.name.StartsWith("__preview__")) continue;   // 预览曲线集不是可用 take
                if (first == null) first = clip;
                if (clip.name == entryId || clip.name == stem) return clip;
            }
            if (first != null) return first;
            // 全是预览曲线集（无普通 take）时才退回第一条，避免整态留空
            foreach (var sub in assets)
                if (sub is AnimationClip clip) return clip;
            return null;
        }

        /// <summary>
        /// 供 PlayMode 断言经**反射桥**取资产（`YANTF.Demo.Tests` 的引用集实测无 UnityEditor，见
        /// `ActionLabGripTests.cs` 头注）：clip = FBX 里的一条 take 或 `.anim` 派生件。
        /// </summary>
        public static AnimationClip LoadClipForProbe(string assetPath, string preferredName)
            => LoadClip(assetPath, preferredName);

        /// <summary>同上：取载体预制（X Bot），断言侧再 Instantiate 得到带 Humanoid Avatar 的骨架。</summary>
        public static GameObject LoadCarrierForProbe()
            => AssetDatabase.LoadAssetAtPath<GameObject>(XBotPath);

        // ================= Animation Rigging 接入（2026-09-14）=================
        // 位置：`com.unity.animation.rigging` 1.4.1 已入库（Packages/manifest.json + lock，净 +3）。
        // 边界（重要，别绕过）：owner 已裁定「手里有东西」整条线**暂停**（code/unity/README.md §二·N
        //   未闭合 1′），而规格 §戊·2 #11 的副手 IK 正属该线。故本次**只接基础设施 + 能力探针**：
        //   Rig 与约束权重恒为 0 → 求值结果与「没有约束」一致；目标节点挂在约束节点下，**不指向椅子**。
        //   真正的约束（副手拉向椅子第二锚点）须等该线重新设计并形成新决策后再挂。

        /// <summary>Rig 层级根节点名（场景内可检索的稳定标识，改名等于破坏下游断言）。</summary>
        public const string RigRootName = "Rig(AnimationRigging)";
        /// <summary>接入点约束节点名（左臂 TwoBoneIK；肩不动，与 §戊·2 副手 IK 的链口径一致）。</summary>
        public const string LeftArmIKName = "LeftArmIK";
        /// <summary>探针目标节点名——挂在约束节点下的**哑目标**，不是椅子上任何锚点。</summary>
        public const string LeftArmIKTargetName = "LeftHandTarget";

        /// <summary>
        /// 接入 Animation Rigging：在载体上建「RigBuilder + Rig + 一条**权重 0** 的 TwoBoneIK 约束」。
        /// 幂等（可重复执行）；**折进 builder** 是硬要求——场景每次 `NewScene` 整文件重写，
        /// 手挂的 Rig 会被冲掉（危险点表 §四「场景 builder 幂等性」）。
        /// </summary>
        public static GameObject BuildRigInfrastructure(GameObject actor, Animator animator)
        {
            if (actor == null || animator == null)
            {
                Debug.LogError("[ActionLab] Animation Rigging 接入失败：actor 或 animator 为空");
                return null;
            }

            var rigBuilder = actor.GetComponent<RigBuilder>();
            if (rigBuilder == null) rigBuilder = actor.AddComponent<RigBuilder>();

            // 幂等：清掉旧 layers 引用与旧 Rig 层级（builder 会被反复执行）
            rigBuilder.layers.Clear();
            var stale = actor.transform.Find(RigRootName);
            if (stale != null) Object.DestroyImmediate(stale.gameObject);

            var rigGo = new GameObject(RigRootName);
            rigGo.transform.SetParent(actor.transform, false);
            var rig = rigGo.AddComponent<Rig>();

            var ikGo = new GameObject(LeftArmIKName);
            ikGo.transform.SetParent(rigGo.transform, false);
            var ik = ikGo.AddComponent<TwoBoneIKConstraint>();

            var targetGo = new GameObject(LeftArmIKTargetName);
            targetGo.transform.SetParent(ikGo.transform, false);
            targetGo.transform.position = animator.GetBoneTransform(HumanBodyBones.LeftHand) != null
                ? animator.GetBoneTransform(HumanBodyBones.LeftHand).position
                : actor.transform.position;

            ik.data.root = animator.GetBoneTransform(HumanBodyBones.LeftUpperArm);
            ik.data.mid = animator.GetBoneTransform(HumanBodyBones.LeftLowerArm);
            ik.data.tip = animator.GetBoneTransform(HumanBodyBones.LeftHand);
            ik.data.target = targetGo.transform;

            // 惰性口径：Rig 与约束权重都是 0 → 不改变任何既有姿势、不与足 IK 争骨链
            rig.weight = 0f;
            ik.weight = 0f;

            rigBuilder.layers.Add(new RigLayer(rig, true));

            // ⚠️ 运行时挂载必须**显式 Build**：RigBuilder 在 `Awake`/`OnEnable` 里建图，而此处是
            //   "先 AddComponent、后 Add layer"——那一轮 Awake 看到的 layers 还是空的，
            //   `Build()` 直接 `return false`，约束永不求值（2026-09-14 实测：手对目标距离恒为初始
            //   偏移 187.1 mm，四组权重/冻结组合读数**逐位相同**，看起来像"约束语法不对"）。
            //   编辑期建场景不调（此时不该建图）；Play 时的 Awake 会拿着**已序列化的 layers** 自己建。
            if (Application.isPlaying) rigBuilder.Build();

            return rigGo;
        }

        /// <summary>
        /// 接入自检（口径同 <see cref="DerivedClipBuilder.VerifyDerived"/>）：接入点按契约存在、骨链绑定非空、
        /// 且**仍然惰性**。三类漂移都会 LogError，因为它们都会让下游误判：
        /// ① Rig 静默失效（骨链为空——Humanoid 载体换过、或 FBX 开了 Optimize Game Objects）；
        /// ② 权重被谁改成非 0（那就在没人设计的情况下改动了角色姿势）；
        /// ③ layers 数不对（有人手工往场景里加了 Rig）。
        /// </summary>
        public static bool VerifyRigInfrastructure(GameObject actor)
        {
            if (actor == null) { Debug.LogError("[ActionLab] Rig 接入自检失败：actor 为空"); return false; }

            var rigBuilder = actor.GetComponent<RigBuilder>();
            if (rigBuilder == null)
            { Debug.LogError("[ActionLab] Rig 接入自检失败：载体上没有 RigBuilder"); return false; }

            if (rigBuilder.layers.Count != 1)
            {
                Debug.LogError($"[ActionLab] Rig 接入自检失败：layers 应为 1，实测 {rigBuilder.layers.Count}" +
                               "（手工往场景加 Rig 会被下次重建冲掉，应改 builder）");
                return false;
            }

            var rig = rigBuilder.layers[0].rig;
            if (rig == null) { Debug.LogError("[ActionLab] Rig 接入自检失败：layer[0].rig 为空"); return false; }

            var ik = rig.GetComponentInChildren<TwoBoneIKConstraint>();
            if (ik == null) { Debug.LogError("[ActionLab] Rig 接入自检失败：找不到 TwoBoneIKConstraint"); return false; }

            var missing = new List<string>();
            if (ik.data.root == null) missing.Add("root(LeftUpperArm)");
            if (ik.data.mid == null) missing.Add("mid(LeftLowerArm)");
            if (ik.data.tip == null) missing.Add("tip(LeftHand)");
            if (ik.data.target == null) missing.Add("target");
            if (missing.Count > 0)
            {
                Debug.LogError("[ActionLab] Rig 接入自检失败：骨链绑定为空 → " + string.Join(" / ", missing) +
                               "（Humanoid 载体换过？FBX 是否开了 Optimize Game Objects？）");
                return false;
            }

            if (ik.weight != 0f || rig.weight != 0f)
            {
                Debug.LogError($"[ActionLab] Rig 接入自检失败：惰性口径被破（rig.weight={rig.weight}, ik.weight={ik.weight}，" +
                               "应恒为 0）——本接入点尚未有消费方，非 0 权重等于在无人设计的情况下改动角色姿势");
                return false;
            }

            Debug.Log($"[ActionLab] Animation Rigging 接入自检 ✅ {RigRootName}/{LeftArmIKName}：" +
                      $"骨链 {ik.data.root.name} → {ik.data.mid.name} → {ik.data.tip.name} 绑定非空，" +
                      $"rig.weight={rig.weight} / ik.weight={ik.weight}（惰性：不产生行为，消费方待定）");
            return true;
        }

        /// <summary>
        /// 三张椅子（规格 §四·丁#8）：坐板 + 四条腿 + 靠背 + Rigidbody + `ChairSeat` 锚点组件。
        /// **实心**（各部件保留 BoxCollider）——角色会被挡在离坐面中心 0.522 m 处（实测 = 胶囊半径 0.3117
        /// + 坐面半深 0.21），"走到椅子前"这件事才看得见；就座序列期间与角色的碰撞由 `ChairSeat` 忽略。
        /// 刚体让椅子可被推开，从而验证锚点确实是**实时**求出来的（搬动椅子后落点跟随）。
        /// </summary>
        private static void AddChairs()
        {
            for (int i = 0; i < ChairPositions.Length; i++)
            {
                AddChair("Chair(椅子)" + (char)('A' + i), ChairPositions[i], ChairYaws[i % ChairYaws.Length]);
            }
        }

        private static void AddChair(string name, Vector3 position, float yaw)
        {
            var root = new GameObject(name);
            root.transform.position = position;
            root.transform.rotation = Quaternion.Euler(0f, yaw, 0f);

            // 坐板：上表面落在 ChairSeatTopY
            float seatCenterY = ChairSeatTopY - ChairSeatThickness * 0.5f;
            var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);
            seat.name = "Seat(坐板)";
            seat.transform.SetParent(root.transform, false);
            seat.transform.localPosition = new Vector3(0f, seatCenterY, 0f);
            seat.transform.localScale = new Vector3(ChairSeatSize, ChairSeatThickness, ChairSeatSize);
            SetColor(seat, new Color(0.55f, 0.36f, 0.20f));

            // 四条腿：地面 → 坐板底面
            float legH = seatCenterY - ChairSeatThickness * 0.5f;
            var offs = new[]
            {
                new Vector3(-ChairLegSpread, 0f, -ChairLegSpread), new Vector3(ChairLegSpread, 0f, -ChairLegSpread),
                new Vector3(-ChairLegSpread, 0f,  ChairLegSpread), new Vector3(ChairLegSpread, 0f,  ChairLegSpread),
            };
            for (int i = 0; i < offs.Length; i++)
            {
                var leg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                leg.name = "Leg" + (i + 1);
                leg.transform.SetParent(root.transform, false);
                leg.transform.localPosition = new Vector3(offs[i].x, legH * 0.5f, offs[i].z);
                leg.transform.localScale = new Vector3(ChairLegSize, legH, ChairLegSize);
                SetColor(leg, new Color(0.42f, 0.27f, 0.15f));
            }

            // 靠背：坐面**后方**（−z；椅子 forward = 坐下后角色胸口朝向，故靠背在 −z 侧）
            var back = GameObject.CreatePrimitive(PrimitiveType.Cube);
            back.name = "Back(靠背)";
            back.transform.SetParent(root.transform, false);
            back.transform.localPosition = new Vector3(0f, ChairSeatTopY + ChairBackHeight * 0.5f,
                                                        -(ChairSeatSize * 0.5f + ChairBackThickness * 0.5f));
            back.transform.localScale = new Vector3(ChairSeatSize, ChairBackHeight, ChairBackThickness);
            SetColor(back, new Color(0.45f, 0.29f, 0.16f));

            // 刚体：可被角色推开；锁住 X/Z 旋转（椅子不会翻倒），阻尼让推力停下后自然静止
            var rb = root.AddComponent<Rigidbody>();
            rb.mass = ChairMass;
            rb.linearDamping = 2.5f;
            rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            rb.interpolation = RigidbodyInterpolation.Interpolate;

            // 就座锚点（实时求解；组件自带默认值 = 规格 §四·丁 的实测值）
            var chair = root.AddComponent<ChairSeat>();
            chair.anchorDistance = ChairSeat.DefaultAnchorDistance;
            chair.interactRadius = ChairSeat.DefaultInteractRadius;
            chair.seatTopY = ChairSeatTopY;

            // 持握挂点（规格 §四·戊 §戊·2）：可握锚点 = **椅子局部坐标**（由上面的几何常量算出，不烘世界坐标）；
            // 逐状态挂点表 = 挂哪只手 / 握哪一处 / 椅子相对手骨的基准朝向（三组各不相同）
            var grip = root.AddComponent<ChairGrip>();
            grip.anchors = BuildGripAnchors();
            grip.poses = DefaultGripPoses();
            grip.swayStiffness = GripSwayStiffness;
            grip.swayDamping = GripSwayDamping;
        }

        /// <summary>
        /// 可握锚点表（**椅子局部**坐标，规格 §戊·2#8「锚点在椅子几何上实时求得」）：
        /// 前/后腿中段 + 靠背中腰。位置全部由本文件的椅子几何常量算出——改椅子尺寸则锚点自动跟随，
        /// 不需要手改任何世界坐标。
        /// </summary>
        public static GripAnchor[] BuildGripAnchors()
        {
            float seatCenterY = ChairSeatTopY - ChairSeatThickness * 0.5f;
            float legH = seatCenterY - ChairSeatThickness * 0.5f;      // 与 AddChair 的腿高同式
            float railZ = -(ChairSeatSize * 0.5f + ChairBackThickness * 0.5f);
            return new[]
            {
                new GripAnchor { id = "leg_front", localPosition = new Vector3(ChairLegSpread, legH * 0.5f, ChairLegSpread), localEuler = Vector3.zero },
                new GripAnchor { id = "leg_back", localPosition = new Vector3(-ChairLegSpread, legH * 0.5f, -ChairLegSpread), localEuler = Vector3.zero },
                new GripAnchor { id = "backrest_rail", localPosition = new Vector3(0f, ChairSeatTopY + ChairBackHeight * 0.5f, railZ), localEuler = Vector3.zero },
            };
        }

        /// <summary>
        /// 逐状态挂点表（规格 §戊·2 的"逐状态挂点表"）。三条的**基准朝向互不相同**——这正是"组间不同"的判据；
        /// 角度值是演示常量（待 owner 目视调），届时只改这张表即可。
        /// </summary>
        public static GripPose[] DefaultGripPoses()
        {
            return new[]
            {
                // 单手提携：握前腿、椅子**垂下**在手侧（绕手骨前向轴转 90°）
                new GripPose { state = GripState.Carry1H, hand = HumanBodyBones.RightHand, anchorId = "leg_front",
                               chairEulerInHand = new Vector3(0f, 0f, 90f) },
                // 双手持握准备：握靠背中腰、椅子**横在身前**（绕手骨长轴转 90°）
                new GripPose { state = GripState.Wield2H, hand = HumanBodyBones.RightHand, anchorId = "backrest_rail",
                               chairEulerInHand = new Vector3(90f, 0f, 0f) },
                // 持椅格挡：同握靠背中腰，但**椅背朝前当盾**——与 Wield2H 的基准朝向差 180°
                new GripPose { state = GripState.DefendCarry1H, hand = HumanBodyBones.RightHand, anchorId = "backrest_rail",
                               chairEulerInHand = new Vector3(90f, 0f, 180f) },
            };
        }

        private static void AddMarker(Vector3 pos, Color c)
        {
            var m = GameObject.CreatePrimitive(PrimitiveType.Cube);
            m.name = "Marker";
            m.transform.position = pos + Vector3.up * 0.5f;
            m.transform.localScale = new Vector3(0.4f, 1f, 0.4f);
            SetColor(m, c);
        }

        private static void SetColor(GameObject go, Color c)
        {
            var shader = Shader.Find("Standard");
            var mat = new Material(shader != null ? shader : Shader.Find("Diffuse"));
            if (mat.HasProperty("_Color")) mat.color = c;
            var r = go.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = mat;
        }
    }
}
