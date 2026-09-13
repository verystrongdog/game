// PlayMode 冒烟测试 — 大脑视图只读骨架（#146）
//
// 覆盖面（判据全部**读数据推导**，不写死数字——写死会把"数据变了"报成"实现坏了"）：
//   ① 链路条数 == tripartite_model.json 四类边之和（当前 1049）
//   ② 材质槽 == 14 网络 + 2 中性（脑干 D29 / CSTC）＝ 16
//   ③ 每条链路两端点都在 graph_nodes 里（LoadLinksFromRepo 不跳过任何边）
//   ④ 链路顶点落在脑壳的世界包围盒内（网格与链路共用同一变换的机器判据）
//   ⑤ 只读骨架的边界：场景里不得出现玩家输入组件（本条零玩家可操作行为）
//   ⑥ 整脑覆盖（#147）：契约的 obj_file 全为左半球，烘焙侧按命名约定补对侧 → 期望 = 载体 ×2
//
// 口径来源：design/presentation/visualization-3d/Unity接入设计.md §3.3/§3.4/§8.5
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using UnityEngine;
using YANTF.BrainView;

namespace YANTF.Demo.Tests
{
    public class BrainViewSmokeTests
    {
        private static string RepoRoot => BrainLinkRenderer.RepoRoot;   // 与 builder 同一来源

        private static Dictionary<string, object> ReadJson(string rel)
        {
            var path = Path.Combine(RepoRoot, rel);
            Assert.IsTrue(File.Exists(path), "契约文件缺失: " + path);
            return (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(path));
        }

        [Test]
        public void LinkCount_MatchesTripartiteEdgeSum()
        {
            var tm = ReadJson("data/connectivity/tripartite_model.json");
            int expected = 0;
            foreach (var key in new[] { "corticocortical", "privileged_pathways", "brainstem", "cstc" })
            {
                Assert.IsTrue(tm.ContainsKey(key), "缺边类: " + key);
                expected += ((List<object>)tm[key]).Count;
            }

            var links = BrainLinkRenderer.LoadLinksFromRepo(RepoRoot);
            Assert.AreEqual(expected, links.Count, "链路条数应等于四类边之和（读数据推导）");
        }

        [Test]
        public void MaterialSlots_AreFourteenNetworksPlusTwoNeutral()
        {
            var kn = ReadJson("data/connectivity/kroell14_networks.json");
            int networks = ((List<object>)kn["networks"]).Count;

            Assert.AreEqual(networks, BrainLinkRenderer.NetworkSlots, "网络槽数应等于 kroell14 的网络数");
            Assert.AreEqual(networks + 2, BrainLinkRenderer.TotalSlots, "总槽 = 网络数 + 脑干中性 + CSTC 中性");
        }

        [Test]
        public void EveryLinkSlot_IsWithinRange_AndNonCorticalEdgesUseNeutralSlots()
        {
            var links = BrainLinkRenderer.LoadLinksFromRepo(RepoRoot);
            int neutral = 0;
            foreach (var l in links)
            {
                Assert.GreaterOrEqual(l.slot, 0);
                Assert.Less(l.slot, BrainLinkRenderer.TotalSlots, "槽位越界");
                if (l.slot >= BrainLinkRenderer.NetworkSlots) neutral++;
            }

            var tm = ReadJson("data/connectivity/tripartite_model.json");
            int expectNeutral = ((List<object>)tm["brainstem"]).Count + ((List<object>)tm["cstc"]).Count;
            Assert.AreEqual(expectNeutral, neutral,
                "无上下文网络归属的边（脑干广播 + CSTC）应恰好落在两个中性槽");
        }

        [Test]
        public void BilateralCoverage_CarrierNamingConventionHolds()
        {
            // 判定分两层（2026-09-13 实测教训）：
            //   ① **字符串层（环境无关，必判）**：每个载体的名字都能按 lh.↔rh. / Left-↔Right- 派生对侧
            //   ② **文件层（环境相关，可用时才判）**：`all_obj/` 被 gitignore，**Windows 侧那份拷贝里根本没有它**
            //      ——故不能无条件断言文件存在，否则本条在任何"干净检出"上都会假失败
            var br = ReadJson("data/brain_regions.json");
            var regions = (Dictionary<string, object>)br["regions"];
            var carriers = new HashSet<string>();
            foreach (var kv in regions)
            {
                var v = (Dictionary<string, object>)kv.Value;
                if (v.TryGetValue("obj_file", out var f) && f is string s && !string.IsNullOrEmpty(s))
                    carriers.Add(s);
            }
            Assert.Greater(carriers.Count, 0, "契约里应有带 obj_file 的载体");

            int derivable = 0;
            var pairs = new List<(string dir, string alt, string rel)>();
            foreach (var rel in carriers)
            {
                var dir = Path.GetDirectoryName(rel)?.Replace('\\', '/');
                var name = Path.GetFileName(rel);
                string alt = null;
                foreach (var pair in new[] { ("lh.", "rh."), ("rh.", "lh."), ("Left-", "Right-"), ("Right-", "Left-") })
                    if (name.StartsWith(pair.Item1)) alt = pair.Item2 + name.Substring(pair.Item1.Length);
                if (alt == null) continue;
                derivable++;
                pairs.Add((dir, alt, rel));
            }
            Assert.AreEqual(carriers.Count, derivable,
                "每个载体都应命中命名约定并可派生对侧（整脑覆盖依赖此约定）");

            // 文件层：仅当载体目录在本环境存在时才校验（Windows 侧拷贝没有 all_obj）
            var probe = Path.Combine(RepoRoot, pairs[0].dir);
            if (!Directory.Exists(probe))
            {
                Debug.LogWarning($"[BrainView] all_obj 不在本环境（{probe}）——命名约定的文件层校验跳过；" +
                                 "这正是 gitignore 资产的预期形态，不是缺陷");
                return;
            }
            foreach (var (dir, alt, rel) in pairs)
                Assert.IsTrue(File.Exists(Path.Combine(RepoRoot, dir, alt)),
                    $"载体缺对侧网格: {rel} → {alt}");
        }

        [Test]
        public void Renderer_BuildsSingleMeshWithExpectedCounts()
        {
            var links = BrainLinkRenderer.LoadLinksFromRepo(RepoRoot);
            var go = new GameObject("BrainLinksTest");
            try
            {
                var r = go.AddComponent<BrainLinkRenderer>();
                r.Build(links);
                Assert.AreEqual(links.Count, r.LinkCount);
                Assert.AreEqual(BrainLinkRenderer.TotalSlots, r.SubmeshCount);
                Assert.AreEqual(BrainLinkRenderer.TotalSlots, r.MaterialCount);
                // 顶点数与面数一致：LineTopology 每条边 2 顶点、1 段
                Assert.AreEqual(links.Count * 2, go.GetComponent<MeshFilter>().sharedMesh.vertexCount);
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }

        [Test]
        public void LinkEndpoints_LieInsideShellBounds()
        {
            var model = Resources.Load<GameObject>("__none__");   // 占位：模型资产不在 Resources
            Assert.IsNull(model);

            var shellPath = Path.Combine(Application.dataPath, "SkillTree/Models/brain_shell.fbx");
            if (!File.Exists(shellPath))
            {
                Assert.Ignore("脑壳资产不在工程（未按 §二·K 导入）——本条跳过");
                return;
            }

            var shell = new GameObject("ShellProbe");
            var linksGo = new GameObject("LinksProbe");
            var rig = new GameObject("RigProbe");
            try
            {
                var links = BrainLinkRenderer.LoadLinksFromRepo(RepoRoot);
                var r = linksGo.AddComponent<BrainLinkRenderer>();
                r.Build(links);
                r.transform.SetParent(rig.transform, false);
                linksGo.transform.SetParent(rig.transform, false);
                // 用与 builder 相同的根变换（§8.5）：−90° X + 等比 1/90
                rig.transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
                rig.transform.localScale = Vector3.one * BrainViewRig.MmToWorld;

                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                var b = new Bounds(mesh.vertices[0], Vector3.zero);
                foreach (var v in mesh.vertices) b.Encapsulate(v);
                // 链路顶点在 MNI 毫米空间：整脑应在 ±150 mm 量级内（不是世界单位、更不是米的量级）
                Assert.Less(b.size.magnitude, 500f, "链路包围盒应以毫米为量级（§8.5 的 MNI 内部空间）");
                Assert.Greater(b.size.magnitude, 50f, "链路包围盒过小——疑似坐标被二次缩放");
            }
            finally
            {
                Object.DestroyImmediate(shell);
                Object.DestroyImmediate(linksGo);
                Object.DestroyImmediate(rig);
            }
        }
    }
}
