// Kevin Iglesias 动画角色场景生成器（Editor）
// 组装：Human_BasicMotionsDummy_M prefab（Humanoid Avatar）→ Animator 挂
// 新建 AnimatorWalker.controller（Idle/Walk/Run/Jump 四状态，clip 取自导入 FBX）→
// 根上挂 CharacterController + AnimatorWalker → 地面/光/相机 → 保存场景。
// 用法：菜单 YANTF → 移动实验 → 创建 Kevin Iglesias 动画场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.KiWalkerLabBuilder.CreateSceneBatch
using System.IO;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.WalkerLab;

namespace YANTF.EditorTools
{
    public static class KiWalkerLabBuilder
    {
        private const string ScenePath = "Assets/Scenes/KiWalkerLab.unity";
        private const string ControllerPath = "Assets/Kevin Iglesias/AnimatorWalker.controller";
        private const string ModelPrefabPath = "Assets/Kevin Iglesias/Human Animations/Unity Demo Scenes/Human Basic Motions/Prefabs/Human_BasicMotionsDummy_M.prefab";

        private const string AnimBase = "Assets/Kevin Iglesias/Human Animations/Animations/Male/";
        private const string IdleFbx = AnimBase + "Idles/HumanM@Idle01.fbx";
        private const string WalkFbx = AnimBase + "Movement/Walk/HumanM@Walk01_Forward.fbx";
        private const string RunFbx = AnimBase + "Movement/Run/HumanM@Run01_Forward.fbx";
        private const string JumpFbx = AnimBase + "Movement/Jump/HumanM@Jump01.fbx";

        [MenuItem("YANTF/移动实验/创建 Kevin Iglesias 动画场景")]
        public static void CreateSceneMenu() => CreateScene();

        public static void CreateSceneBatch() => CreateScene();

        public static void CreateScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 地面 / 参照柱 / 光（复用 Walker 布局口径）----
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

            // ---- AnimatorController：四状态，clip 烘焙 ----
            var controller = BuildOrLoadController();

            // ---- 模型 prefab 实例 + 控制器 ----
            var modelPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPrefabPath);
            if (modelPrefab == null)
            {
                Debug.LogError("[YANTF] 找不到模型 prefab: " + ModelPrefabPath);
                return;
            }
            var actor = (GameObject)PrefabUtility.InstantiatePrefab(modelPrefab);
            actor.name = "KiWalker(动画演示者)";
            actor.transform.position = new Vector3(0f, 0f, 0f);

            var animator = actor.GetComponent<Animator>();
            if (animator == null) animator = actor.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller;
            animator.applyRootMotion = false; // 位移交给 CharacterController

            var cc = actor.AddComponent<CharacterController>(); // 参数由 AnimatorWalker.Awake 兜底
            var walker = actor.AddComponent<AnimatorWalker>();
            walker.animator = animator;

            // ---- 相机 ----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            camGo.transform.position = new Vector3(0f, 3.2f, -6f);
            camGo.transform.rotation = Quaternion.Euler(18f, 0f, 0f);

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"[YANTF] Ki 动画场景已保存: {ScenePath} — Play：WASD 走 / Shift 跑 / Space 跳");
        }

        private static AnimatorController BuildOrLoadController()
        {
            var existing = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
            if (existing != null) return existing;

            var controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
            var sm = controller.layers[0].stateMachine;

            // 清理默认 AnyState 相关默认状态，逐个建状态
            var stIdle = AddState(sm, "Idle", LoadClip(IdleFbx, "HumanM@Idle01"));
            var stWalk = AddState(sm, "Walk", LoadClip(WalkFbx, "HumanM@Walk01_Forward"));
            var stRun = AddState(sm, "Run", LoadClip(RunFbx, "HumanM@Run01_Forward"));
            var stJump = AddState(sm, "Jump", LoadClip(JumpFbx, "HumanM@Jump01"));

            sm.defaultState = stIdle;
            AssetDatabase.SaveAssets();
            AssetDatabase.ImportAsset(ControllerPath);
            return controller;
        }

        private static AnimatorState AddState(AnimatorStateMachine sm, string name, AnimationClip clip)
        {
            var st = sm.AddState(name);
            st.motion = clip;
            st.writeDefaultValues = true;
            if (clip != null)
            {
                // 走/跑/待机循环；跳一次性
                st.speed = 1f;
            }
            return st;
        }

        private static AnimationClip LoadClip(string fbxPath, string clipName)
        {
            foreach (var sub in AssetDatabase.LoadAllAssetsAtPath(fbxPath))
            {
                if (sub is AnimationClip c && c.name == clipName) return c;
            }
            Debug.LogWarning("[YANTF] 未找到 clip " + clipName + " @ " + fbxPath);
            return null;
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
