// ActionLab 场景/controller 生成器（Editor）— 规格 §六 + #124 Q-B2/Q-B5
// - 幂等：controller 存在则加载并在其上补齐（状态按 ActionCatalog 构造成立，状态名 = 词表 id）
// - 防漂移（#124 Q-B5 分档）：clip 按 catalog.ClipAssetPath 资产存在性接线——
//     资产存在 → 必须挂上 clip（找不到 → 警告）；资产不存在 → 状态留空，计入缺口清单（Console）
// - 派生件：建场景前 EnsureSitDown()（SitDown = Sit To Stand 反转），并 VerifyDerived() 自检漂移
// - 足部贴地（规格 §四·乙）：打开 controller Base Layer 的 iKPass 并挂 FootGroundingIK——
//     不开 iKPass 则 OnAnimatorIK 不会被调用，足 IK 静默失效
// - 凳子：坐面高 = 坐姿网格实测（见 StoolSeatTopY 注释），摆在坐姿髋落点正下方，**不带碰撞体**
// - 用法：菜单 YANTF → 动作演示 → 创建 ActionLab 场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.ActionLabBuilder.CreateSceneBatch
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
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

        // ---- 凳子几何（全部来自 2026-09-12 实测，非目视估计）----
        /// <summary>坐面高度 m = 坐姿（Sitting Idle + 足 IK）下髋部半径 0.30 m 内蒙皮网格最低点。
        /// 实测 r=0.10/0.15/0.20/0.30 四档全部收敛到 0.4449（r=0.40 起会把小腿顶点算进来 → 失真）。</summary>
        private const float StoolSeatTopY = 0.4449f;
        /// <summary>坐姿髋部落点（相对角色 transform，角色朝 +z）——凳子坐面中心应在此正下方。</summary>
        private const float StoolCenterX = 0.0f;      // 实测坐姿 hips.x = 0.0027 ≈ 0
        private const float StoolCenterZ = -0.104f;   // 实测坐姿 hips.z = −0.1040
        private const float StoolSeatThickness = 0.05f;
        private const float StoolSeatSize = 0.42f;    // 边长：容下两侧臀部（实测接触点 x 偏 +0.084）
        private const float StoolLegSize = 0.05f;

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

            // ---- 凳子（坐立三段的落点；几何全部来自实测，见 StoolSeatTopY 注释）----
            AddStool();

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

            Debug.Log($"[ActionLab] 场景已保存: {ScenePath} — Play：WASD 走 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 6坐 7起身 / R 重置");
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
        /// 凳子：坐板 + 四条腿（Cube 原语）。坐板**上表面**落在 StoolSeatTopY。
        /// 不带碰撞体——角色 transform 在原点、坐姿髋落点在 z=−0.104，凳子占地范围内正站着人；
        /// 留了碰撞体会把起身与移动卡死。
        /// </summary>
        private static void AddStool()
        {
            var root = new GameObject("Stool(凳子)");
            root.transform.position = new Vector3(StoolCenterX, 0f, StoolCenterZ);

            float seatCenterY = StoolSeatTopY - StoolSeatThickness * 0.5f;
            var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);
            seat.name = "Seat";
            seat.transform.SetParent(root.transform, false);
            seat.transform.localPosition = new Vector3(0f, seatCenterY, 0f);
            seat.transform.localScale = new Vector3(StoolSeatSize, StoolSeatThickness, StoolSeatSize);
            SetColor(seat, new Color(0.55f, 0.36f, 0.20f));
            StripCollider(seat);

            float legH = seatCenterY - StoolSeatThickness * 0.5f;  // 地面 → 坐板底面
            float half = StoolSeatSize * 0.5f - StoolLegSize * 0.5f - 0.02f;
            var offs = new[]
            {
                new Vector3(-half, 0f, -half), new Vector3(half, 0f, -half),
                new Vector3(-half, 0f,  half), new Vector3(half, 0f,  half),
            };
            for (int i = 0; i < offs.Length; i++)
            {
                var leg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                leg.name = "Leg" + (i + 1);
                leg.transform.SetParent(root.transform, false);
                leg.transform.localPosition = new Vector3(offs[i].x, legH * 0.5f, offs[i].z);
                leg.transform.localScale = new Vector3(StoolLegSize, legH, StoolLegSize);
                SetColor(leg, new Color(0.42f, 0.27f, 0.15f));
                StripCollider(leg);
            }
        }

        /// <summary>演示道具不留碰撞体（理由见 AddStool 注释）。</summary>
        private static void StripCollider(GameObject go)
        {
            var col = go.GetComponent<Collider>();
            if (col != null) UnityEngine.Object.DestroyImmediate(col);
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
