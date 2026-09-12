// PlayMode 冒烟测试 — 玫瑰花海实验场（Grilling #126）
// 验证：① 高度图解码（101×101 / 高差 3.1075 m / 最大 1m 高差可走）
//       ② 地面网格（顶点数 / 尺寸 / 法线朝上 / MeshCollider）
//       ③ 六角错行株位（株数 / 最近邻间距 = s / 域内 / 几何全覆盖判据 D ≥ 2s/√3）
//       ④ 小人站上实际地形（CharacterController 与 MeshCollider 贴合）
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using YANTF.RoseField;
using YANTF.WalkerLab;

public class RoseFieldSmokeTests
{
    // 地块规格（与 RoseFieldLab 默认值一致；来源见 呈现/地块数据-Konza草原.md）
    private const int Samples = 101;
    private const float FieldSize = 100f;
    private const float Relief = 3.1075f;
    private const float Spacing = 1.602f;

    private static RoseFieldLab NewLab()
    {
        var go = new GameObject("TestRoseField");
        return go.AddComponent<RoseFieldLab>(); // Awake → Build()
    }

    [UnityTest]
    public IEnumerator RoseField_Heightmap_DecodesToExpectedRelief()
    {
        var lab = NewLab();
        yield return null;

        Assert.AreEqual(Samples, lab.Field.Samples, "高度图应为 101×101 采样");
        Assert.AreEqual(FieldSize, lab.Field.Size, 1e-3f, "地块边长应为 100 m");
        Assert.AreEqual(Relief, lab.Field.Relief, 1e-3f, "高差应为 3.1075 m");

        float min = float.MaxValue, max = float.MinValue;
        for (int r = 0; r < Samples; r++)
        {
            for (int c = 0; c < Samples; c++)
            {
                float v = lab.Field.HeightAtSample(r, c);
                if (v < min) min = v;
                if (v > max) max = v;
            }
        }
        Assert.AreEqual(0f, min, 1e-4f, "最低点应解码为 0");
        Assert.AreEqual(Relief, max, 1e-4f, "最高点应解码为 relief");

        // 可走判据：最大 1 m 高差须 < tan(45°) = 1.0（CharacterController.slopeLimit）
        float slope = lab.Field.MaxSlopePerMeter();
        Assert.Less(slope, 1.0f, $"最大 1m 高差 {slope:F4} m 必须小于 slopeLimit 45° 的正切");

        Object.Destroy(lab.gameObject);
    }

    [UnityTest]
    public IEnumerator RoseField_GroundMesh_HasGridBoundsAndUpNormals()
    {
        var lab = NewLab();
        yield return null;

        var ground = lab.transform.Find(RoseFieldLab.GroundName);
        Assert.IsNotNull(ground, "应生成 Ground 子物体");

        var mf = ground.GetComponent<MeshFilter>();
        Assert.IsNotNull(mf, "地面应有 MeshFilter");
        var mesh = mf.sharedMesh;
        Assert.IsNotNull(mesh, "地面应有网格");
        Assert.AreEqual(Samples * Samples, mesh.vertexCount, "顶点数应为 101×101");

        Assert.AreEqual(FieldSize, mesh.bounds.size.x, 0.01f, "网格 X 尺寸应为 100 m");
        Assert.AreEqual(FieldSize, mesh.bounds.size.z, 0.01f, "网格 Z 尺寸应为 100 m");
        Assert.AreEqual(Relief, mesh.bounds.size.y, 0.01f, "网格 Y 尺寸应等于高差");

        var normals = mesh.normals;
        Assert.AreEqual(mesh.vertexCount, normals.Length);
        for (int i = 0; i < normals.Length; i++)
            Assert.Greater(normals[i].y, 0.5f, $"顶点 {i} 法线应朝上，实际 {normals[i]}");

        Assert.IsNotNull(ground.GetComponent<MeshCollider>(), "地面应有 MeshCollider（供小人行走）");
        Assert.IsNotNull(ground.GetComponent<MeshRenderer>(), "地面应有 MeshRenderer");

        Object.Destroy(lab.gameObject);
    }

    [UnityTest]
    public IEnumerator RoseField_Lattice_MatchesCommercialDensitySpec()
    {
        var lab = NewLab();
        yield return null;

        var pts = lab.RosePositions;
        Assert.IsNotNull(pts);
        // 六角错行：行距 s√3/2 → 73 行（37 满行 × 63 + 36 错行 × 62 = 4563）；容 ±1% 浮点余量
        Assert.That(pts.Length, Is.InRange(4517, 4609), $"株数应≈4563，实际 {pts.Length}");

        // 全部株位在域内，且 y 取自地块高度
        foreach (var p in pts)
        {
            Assert.That(p.x, Is.InRange(0f, FieldSize));
            Assert.That(p.z, Is.InRange(0f, FieldSize));
            Assert.AreEqual(lab.Field.HeightAtWorld(p.x, p.z), p.y, 1e-3f, "株位 y 应贴合地块高度");
        }

        // 最近邻间距 = s（三角格 6 邻域距离恒为 s）；抽样 200 株核验
        int checkedCount = 0;
        for (int i = 0; i < pts.Length && checkedCount < 200; i += Mathf.Max(1, pts.Length / 200))
        {
            float nearest = float.MaxValue;
            for (int j = 0; j < pts.Length; j++)
            {
                if (j == i) continue;
                float d = Vector3.Distance(pts[i], pts[j]);
                if (d < nearest) nearest = d;
            }
            Assert.GreaterOrEqual(nearest, Spacing - 1e-3f, $"株 {i} 最近邻 {nearest:F4} m 不应小于错行间距");

            // 内部株（离边界 ≥ 2s）最近邻应恰为 s
            bool interior = pts[i].x > 2f * Spacing && pts[i].x < FieldSize - 2f * Spacing
                            && pts[i].z > 2f * Spacing && pts[i].z < FieldSize - 2f * Spacing;
            if (interior) Assert.AreEqual(Spacing, nearest, 1e-3f, $"内部株 {i} 最近邻应等于错行间距 s");

            checkedCount++;
        }

        // 商业化种植密度：平阴玫瑰密植园 180–330 株/亩
        Assert.That(lab.PlantsPerMu, Is.InRange(180f, 330f), $"密度 {lab.PlantsPerMu:F1} 株/亩 应落在文献区间 [180,330]");

        // 几何全覆盖判据：D ≥ 2s/√3（三角格覆盖半径 = s/√3）
        Assert.AreEqual(2f * Spacing / Mathf.Sqrt(3f), lab.MinCanopyForFullCoverage, 1e-3f);
        Assert.IsTrue(lab.IsFullCoverage,
            $"蓬径 {lab.roseCanopyDiameter:F2} m 应 ≥ 全覆盖判据 {lab.MinCanopyForFullCoverage:F3} m");
        Assert.GreaterOrEqual(lab.CanopyCoverRatio, 1f, "冠层投影比应 ≥ 1（冠层闭合）");

        Object.Destroy(lab.gameObject);
    }

    [UnityTest]
    public IEnumerator RoseField_Walker_StandsOnTerrainSurface()
    {
        var lab = NewLab();
        yield return null;

        float h = lab.Field.HeightAtWorld(FieldSize * 0.5f, FieldSize * 0.5f);

        var go = new GameObject("TestWalker");
        go.transform.position = new Vector3(FieldSize * 0.5f, h + 2f, FieldSize * 0.5f);
        go.AddComponent<CharacterController>();
        var walker = go.AddComponent<WalkerController>(); // Awake 校正 CC 胶囊
        walker.followCamera = false;

        float t0 = Time.time;
        while (!walker.IsGrounded && Time.time - t0 < 4f) yield return null;

        Assert.IsTrue(walker.IsGrounded, "小人应在 4s 内落到地面网格上");
        Assert.AreEqual(h, go.transform.position.y, 0.2f,
            $"小人应停在中心点地形高度 {h:F3} m 附近，实际 {go.transform.position.y:F3} m");

        Object.Destroy(go);
        Object.Destroy(lab.gameObject);
    }
}
