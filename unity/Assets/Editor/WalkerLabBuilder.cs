// Walker 实验场景生成器（Editor）— 几何体人体移动沙盘（走/跑/跳验证）
// 用法：菜单 YANTF → 移动实验 → 创建 Walker 场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.WalkerLabBuilder.CreateWalkerSceneBatch
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.WalkerLab;

namespace YANTF.EditorTools
{
    public static class WalkerLabBuilder
    {
        private const string ScenePath = "Assets/Scenes/WalkerLab.unity";

        [MenuItem("YANTF/移动实验/创建 Walker 场景")]
        public static void CreateWalkerSceneMenu()
        {
            CreateWalkerScene();
        }

        public static void CreateWalkerScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 地面（平面放大 + 材质，另加参照柱便于观察位移）----
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(24f, 1f, 24f);
            ground.transform.position = new Vector3(0f, 0f, 0f);
            SetMaterialColor(ground, new Color(0.55f, 0.6f, 0.5f));

            AddMarker(new Vector3(0f, 0f, 3f), new Color(0.9f, 0.35f, 0.35f));
            AddMarker(new Vector3(3f, 0f, 0f), new Color(0.35f, 0.8f, 0.4f));
            AddMarker(new Vector3(0f, 0f, -3f), new Color(0.4f, 0.5f, 0.9f));
            AddMarker(new Vector3(-3f, 0f, 0f), new Color(0.95f, 0.8f, 0.3f));

            // ---- 平行光 ----
            var sunGo = new GameObject("Sun");
            var light = sunGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            sunGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            // ---- 几何体人体 + 移动控制器（Editor 模式实体化，保存进场景）----
            var walkerGo = new GameObject("Walker(演示者)");
            walkerGo.transform.position = new Vector3(0f, 0f, 0f);
            var cc = walkerGo.AddComponent<CharacterController>(); // 先加 CC 再 Add Walker（RequireComponent 也会补）
            cc.height = 1.85f;
            cc.radius = 0.35f;
            cc.center = new Vector3(0f, 0.92f, 0f);
            cc.slopeLimit = 45f;
            cc.stepOffset = 0.3f;
            var walker = walkerGo.AddComponent<WalkerController>();
            walker.BuildBody(new Color(0.35f, 0.65f, 1f)); // 蓝色调，与战斗沙盘 Player 视觉区分
            walker.transform.position = new Vector3(0f, 0f, 0f); // CC center 上抬后胶囊底部≈地面

            // ---- 相机（tag MainCamera；WalkerController.followCamera 驱动跟随）----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            camGo.transform.position = new Vector3(0f, 3.2f, -6f);
            camGo.transform.rotation = Quaternion.Euler(18f, 0f, 0f);

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"[YANTF] Walker 实验场景已保存: {ScenePath} — 打开后按 Play（WASD 走 / Shift 跑 / Space 跳）");
        }

        /// <summary>headless 批量入口（-executeMethod）。</summary>
        public static void CreateWalkerSceneBatch()
        {
            CreateWalkerScene();
        }

        // ---- 小工具 ----
        private static void AddMarker(Vector3 pos, Color c)
        {
            var m = GameObject.CreatePrimitive(PrimitiveType.Cube);
            m.name = "Marker";
            m.transform.position = pos + Vector3.up * 0.5f;
            m.transform.localScale = new Vector3(0.4f, 1f, 0.4f);
            SetMaterialColor(m, c);
        }

        private static void SetMaterialColor(GameObject go, Color c)
        {
            var shader = Shader.Find("Standard");
            var mat = new Material(shader != null ? shader : Shader.Find("Diffuse"));
            if (mat.HasProperty("_Color")) mat.color = c;
            var r = go.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = mat;
        }
    }
}
