// 场景生成器（Editor）— 代码生成 Demo 场景（含空场景引导对象）
// 用法：菜单 YANTF → 呈现沙盘 → 创建 Demo 场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.SceneBuilder.CreateDemoSceneBatch
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.Demo;

namespace YANTF.EditorTools
{
    public static class SceneBuilder
    {
        private const string ScenePath = "Assets/Scenes/DemoSandbox.unity";

        [MenuItem("YANTF/呈现沙盘/创建 Demo 场景")]
        public static void CreateDemoSceneMenu()
        {
            CreateDemoScene();
        }

        public static void CreateDemoScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("DemoBootstrapper");
            go.AddComponent<DemoBootstrapper>();   // Awake 时 BuildAll() 构建整个世界
            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"[YANTF] Demo 场景已保存: {ScenePath} — 打开后按 Play");
        }

        /// <summary>headless 批量入口（-executeMethod）。</summary>
        public static void CreateDemoSceneBatch()
        {
            CreateDemoScene();
        }
    }
}
