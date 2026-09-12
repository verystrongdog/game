// ActionLab 场景/controller 生成器（Editor）— Grilling #123 规格 §六 Batch0 + #124 Q-B2/Q-B5
// - 幂等：controller 存在则加载并在其上补齐（状态按 ActionCatalog 构造成立，状态名 = 词表 id）
// - 防漂移（#124 Q-B5 分档）：clip 按 catalog.ClipFbxPath 资产存在性接线——
//     资产存在 → 必须挂上 clip（找不到 → 警告）；资产不存在 → 状态留空，计入缺口清单（Console）
// - 用法：菜单 YANTF → 动作演示 → 创建 ActionLab 场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.ActionLabBuilder.CreateSceneBatch
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.ActionLab;

namespace YANTF.EditorTools
{
    public static class ActionLabBuilder
    {
        private const string ScenePath = "Assets/Scenes/ActionLab.unity";
        private const string ControllerPath = "Assets/ActionLab/ActionLab.controller";
        private const string XBotPath = "Assets/Mixamo/Characters/X Bot.fbx";
        private const string YBotPath = "Assets/Mixamo/Characters/Y Bot.fbx";

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

            var sunGo = new GameObject("Sun");
            var light = sunGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            sunGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            // ---- AnimatorController：L1 9 态（状态名 = 词表 id），clip 按资产存在性接线 ----
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

            // ---- 相机 ----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            camGo.transform.position = new Vector3(0f, 3.2f, -6f);
            camGo.transform.rotation = Quaternion.Euler(18f, 0f, 0f);

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);

            Debug.Log($"[ActionLab] 场景已保存: {ScenePath} — Play：WASD 走 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 / R 重置");
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
                var clip = LoadClip(entry.ClipFbxPath, entry.Id);
                if (clip != null)
                {
                    st.motion = clip;
                    wired++;
                }
                else
                {
                    st.motion = null;
                    if (entry.ClipFbxPath != null && AssetDatabase.LoadAssetAtPath<Object>(entry.ClipFbxPath) != null)
                    {
                        // 资产在但没取到 clip → 真异常，报错而非静默
                        Debug.LogError("[ActionLab] 状态 " + entry.Id + " 资产存在但未取到 clip: " + entry.ClipFbxPath);
                    }
                    gaps.Add(entry.Id);
                }
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

        /// <summary>取 FBX 内 clip：优先名字匹配 词表 id / 文件主干，否则取第一个 AnimationClip（Mixamo 单 take）。</summary>
        private static AnimationClip LoadClip(string fbxPath, string entryId)
        {
            if (string.IsNullOrEmpty(fbxPath)) return null;
            var assets = AssetDatabase.LoadAllAssetsAtPath(fbxPath);
            AnimationClip first = null;
            string stem = Path.GetFileNameWithoutExtension(fbxPath);
            foreach (var sub in assets)
            {
                if (!(sub is AnimationClip clip)) continue;
                if (first == null) first = clip;
                if (clip.name == entryId || clip.name == stem) return clip;
            }
            return first;
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
