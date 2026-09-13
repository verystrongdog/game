// 大脑视图（YANTF.BrainView）— 只读骨架的场景 builder（幂等：每次都从零重建）
//
// 为什么全部折进 builder：危险点表 §四「场景 builder 幂等性」——builder 每次新建场景会覆盖已入库
// 场景与手工挂载件，所以**任何场景件都必须在 CreateScene() 里生成**，不做"生成后再手挂"。
//
// 本条（#146）的边界：**零玩家可操作行为**。只做 脑壳 + 脑区（可见）+ 链路 + 相机绕看；
// 不做聚焦/情境分层（依赖 game state）、不做只读展示面板、不做技能上下文节点。
//
// 口径与数值来源：
//   design/presentation/visualization-3d/Unity接入设计.md §3.1（脑壳）/§3.3（连线）/§8.5（坐标系）
//   code/unity/README.md §二·K（脑壳资产身份与导入动线）
//   相机交互沿用 design/presentation/visualization-3d/3D可视化设计规范.md §四.1
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.BrainView;

namespace YANTF.EditorTools
{
    public static class BrainViewLabBuilder
    {
        private const string ModelPath = "Assets/SkillTree/Models/brain_shell.fbx";
        private const string ScenePath = "Assets/Scenes/BrainViewLab.unity";

        /// <summary>相机初始距离（世界单位）：整脑约 1.9 单位（§8.5 的 1/90），
        /// 按默认 60° 垂直 FOV 反算 2·d·tan30° ≈ 1.15d，取 d=2.8 使脑占画面高度约六成。</summary>
        private const float CameraDistance = 2.8f;

        [MenuItem("YANTF/大脑视图/创建 BrainViewLab 场景")]
        public static void CreateSceneMenu() => CreateScene();

        public static void CreateSceneBatch() => CreateScene();

        public static void CreateScene()
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                Debug.LogError($"[BrainView] 找不到脑壳资产: {ModelPath}\n" +
                               "请先按 code/unity/README.md §二·K 烘焙并导入（bake_brain_shell.py → import_asset）。");
                return;
            }

            string repoRoot = BrainLinkRenderer.RepoRoot;   // 单一来源，避免各算一遍（实测踩过层级错）
            var log = new List<string>();
            var links = BrainLinkRenderer.LoadLinksFromRepo(repoRoot, log);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 结构（#148）：Spin（观察角）→ BrainView（资产基线 −90°X + 等比 1/90）→ Shell/Links
            // 为什么分两层：自转与"资产躺着→立起"是两件事，复合在一个 transform 里既难读也难验。
            var spinGo = new GameObject("Spin");
            var spin = spinGo.AddComponent<BrainViewSpin>();

            var root = new GameObject("BrainView");
            root.transform.SetParent(spinGo.transform, false);
            var rig = root.AddComponent<BrainViewRig>();

            // ---- 脑壳（只消费 #143 入库的资产，不改它）----
            var shell = (GameObject)PrefabUtility.InstantiatePrefab(model);
            shell.name = "BrainShell";
            shell.transform.SetParent(root.transform, false);

            // ---- 链路（1049 条三体边 → 单个 Mesh，16 个材质槽）----
            var linkGo = new GameObject("Links");
            linkGo.transform.SetParent(root.transform, false);
            var renderer = linkGo.AddComponent<BrainLinkRenderer>();
            renderer.Build(links);

            rig.Bind(shell.transform, linkGo.transform);

            // ---- 相机 + 绕看（§四.1：拖动旋转 / 滚轮缩放）----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.03f, 0.04f, 0.06f);
            cam.nearClipPlane = 0.05f;
            camGo.AddComponent<AudioListener>();          // 恰好一个，避免 2 listeners 警告
            // 观察方式（#148）：相机**固定**机位，拖动旋转的是模型本身；缩放改相机距离。
            // 相机朝向：俯视 12°、正对模型中心（与 #146 的初始观感一致）。
            camGo.transform.rotation = Quaternion.Euler(12f, 0f, 0f);
            spin.Bind(cam, CameraDistance);
            spin.ResetView();

            // ---- 光（双光源：主光给形，补光防黑面）----
            var keyGo = new GameObject("Key Light");
            var key = keyGo.AddComponent<Light>();
            key.type = LightType.Directional;
            key.intensity = 1.1f;
            keyGo.transform.rotation = Quaternion.Euler(45f, -35f, 0f);
            RenderSettings.ambientLight = new Color(0.28f, 0.32f, 0.40f);

            EditorSceneManager.SaveScene(scene, ScenePath);

            // ---- 产出核对（数据驱动，不写死数字）----
            // 整脑覆盖（#147）：契约的 58 条 obj_file 全为左半球，烘焙侧按命名约定补了对侧
            // （lh.↔rh. / Left-↔Right-，实测 40/40 有真实对照），故期望 = 载体数 × 2。
            int carriers = CountDataCarriers(repoRoot);
            int expectedRegions = carriers * 2;
            int right = 0;
            foreach (var mf in shell.GetComponentsInChildren<MeshFilter>(true))
                if (mf.name.EndsWith("_R")) right++;
            Debug.Log($"[BrainView] 场景 → {ScenePath}\n" +
                      $"  脑壳：区域对象 {rig.RegionCount}（数据侧载体 {carriers} × 双侧 = {expectedRegions}；" +
                      $"左 {rig.RegionCount - right} / 右 {right}）· 材质 {rig.ShellMaterialCount}\n" +
                      $"  链路：{renderer.LinkCount} 条 · submesh {renderer.SubmeshCount} · 材质 {renderer.MaterialCount}\n" +
                      $"  根变换：rot {rig.transform.localRotation.eulerAngles} · scale {rig.transform.localScale.x:F5}");
            if (expectedRegions > 0 && rig.RegionCount != expectedRegions)
                Debug.LogWarning($"[BrainView] ⚠ 区域对象数 {rig.RegionCount} ≠ 期望 {expectedRegions}" +
                                 $"（载体 {carriers} × 双侧）——检烘焙是否按 §二·K 跑了双侧");
            if (right * 2 != rig.RegionCount)
                Debug.LogWarning($"[BrainView] ⚠ 左右半球对象数不等：左 {rig.RegionCount - right} / 右 {right}");
            foreach (var line in log) Debug.LogWarning("[BrainView] " + line);
        }

        /// <summary>数据侧期望的载体数 = brain_regions.json 里 obj_file 去重后的数量。</summary>
        private static int CountDataCarriers(string repoRoot)
        {
            string path = Path.Combine(repoRoot, "data/brain_regions.json");
            if (!File.Exists(path)) return 0;
            var doc = (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(path));
            if (!doc.TryGetValue("regions", out var raw) || !(raw is Dictionary<string, object> regions))
                return 0;
            var files = new HashSet<string>();
            foreach (var kv in regions)
            {
                var v = (Dictionary<string, object>)kv.Value;
                if (v.TryGetValue("obj_file", out var f) && f is string s && !string.IsNullOrEmpty(s))
                    files.Add(s);
            }
            return files.Count;
        }
    }
}
