// NarrativeWebScene 与 Unity Web 构建生成器。
// 来源：design/presentation/Unity Web集成设计.md §七—§十。
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using YANTF.Web;

namespace YANTF.EditorTools
{
    public static class NarrativeWebSceneBuilder
    {
        private const string ScenePath = "Assets/Scenes/NarrativeWebScene.unity";
        private const string WebOutputPath = "web/public/unity";

        [Serializable]
        private sealed class BuildManifest
        {
            // 来源：design/presentation/Unity Web集成设计.md §五的协议版本。
            public int v = 1;
            public string loaderUrl;
            public BuildConfig config;
        }

        [Serializable]
        private sealed class BuildConfig
        {
            public string dataUrl;
            public string frameworkUrl;
            public string codeUrl;
            public string streamingAssetsUrl = "StreamingAssets";
            public string companyName;
            public string productName;
            public string productVersion;
        }

        [MenuItem("YANTF/Web/创建最小 NarrativeWebScene")]
        public static void CreateScene()
        {
            Scene scene;
            if (File.Exists(ScenePath))
            {
                scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            }
            else
            {
                scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            }

            EnsureBridge();
            EnsureCamera();
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log("[NarrativeWeb] 最小场景已保存：" + ScenePath);
        }

        [MenuItem("YANTF/Web/构建阶段 A 到 web/public/unity")]
        public static void BuildWeb()
        {
            CreateScene();
            string output = Path.GetFullPath(Path.Combine(Application.dataPath, "../../..", WebOutputPath));
            Directory.CreateDirectory(output);

            var options = new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = output,
                target = BuildTarget.WebGL,
                options = BuildOptions.Development
            };
            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new InvalidOperationException("Unity Web 构建失败：" + report.summary.result);
            }

            WriteManifest(output);
            Debug.Log($"[NarrativeWeb] 构建完成：{output} ({report.summary.totalSize} bytes)");
        }

        private static void EnsureBridge()
        {
            var bridge = UnityEngine.Object.FindFirstObjectByType<WebPresentationBridge>();
            if (bridge != null) return;
            new GameObject(nameof(WebPresentationBridge)).AddComponent<WebPresentationBridge>();
        }

        private static void EnsureCamera()
        {
            Camera camera = Camera.main;
            if (camera == null)
            {
                var cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                camera = cameraObject.AddComponent<Camera>();
            }
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            camera.orthographic = true;
        }

        private static void WriteManifest(string output)
        {
            string buildDirectory = Path.Combine(output, "Build");
            var manifest = new BuildManifest
            {
                loaderUrl = AssetUrl(FindBuildFile(buildDirectory, ".loader.js")),
                config = new BuildConfig
                {
                    dataUrl = AssetUrl(FindBuildFile(buildDirectory, ".data")),
                    frameworkUrl = AssetUrl(FindBuildFile(buildDirectory, ".framework.js")),
                    codeUrl = AssetUrl(FindBuildFile(buildDirectory, ".wasm")),
                    companyName = PlayerSettings.companyName,
                    productName = PlayerSettings.productName,
                    productVersion = PlayerSettings.bundleVersion
                }
            };
            File.WriteAllText(Path.Combine(output, "manifest.json"), JsonUtility.ToJson(manifest, true));
        }

        private static string FindBuildFile(string directory, string marker)
        {
            string path = Directory.GetFiles(directory)
                .SingleOrDefault(candidate => Path.GetFileName(candidate).Contains(marker));
            if (path == null) throw new FileNotFoundException("Unity Web 产物缺少 " + marker, directory);
            return path;
        }

        private static string AssetUrl(string path)
            => "./Build/" + Path.GetFileName(path).Replace("\\", "/");
    }
}
