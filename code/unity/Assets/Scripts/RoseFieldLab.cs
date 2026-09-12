// 玫瑰花海实验场 — 地块高度场 + 商业化密度玫瑰株丛（Grilling #126）
//
// 口径来源（逐项可核）：
//   地块    100×100 m，USGS 3DEP 1 m lidar DEM（Konza Prairie 高草草原，公有领域）
//           relief 3.1075 m / std 0.5665 m / 最大 1 m 高差 0.1145 m（6.53°）
//   密度    平阴玫瑰密植园 180–330 株/亩（平阴县人民政府栽培技术 + 农博数据中心，两源互印），取 300 株/亩
//   布置    六角错行间距 s = 1.602 m → 单株占地 (√3/2)s² = 2.2222 m² → N = 4563 株 / 10⁴ m²
//   覆盖率  三角格覆盖半径 = s/√3 → 几何全覆盖判据 D ≥ 2s/√3 = 1.850 m（本实验 D = 1.85 m → 覆盖率 1.0）
//
// 渲染：每株一个 GameObject（MeshFilter + MeshRenderer，共享同一网格与材质）。
//   共享材质开了 GPU Instancing → Unity 自动合批。**不用** Graphics.DrawMesh* 即时模式：
//   即时模式绘制不进 Camera.Render() 抓帧路径（#126 实测：source=camera 抓到 0% 玫瑰像素，
//   而 MeshRenderer 对象正常可见），且无法在编辑器的 Scene View 里直接看到。
// 株丛不设碰撞体（「穿行」语义）。
using System.Collections.Generic;
using UnityEngine;

namespace YANTF.RoseField
{
    /// <summary>玫瑰花海实验场：程序化地面 + 六角错行玫瑰株丛。挂在场景内一个空物体上即可。</summary>
    [DisallowMultipleComponent]
    public sealed class RoseFieldLab : MonoBehaviour
    {
        public const string GroundName = "Ground";
        public const string RosesName = "Roses";

        [Header("地块（USGS 3DEP 1m lidar · Konza Prairie 高草草原 · 公有领域）")]
        [Tooltip("Resources 下的高度图（.bytes，LE uint16，行 0 = 北）")]
        public string heightmapResource = "YANTF/konza_plot_101x101_r16";
        [Tooltip("每边采样数")]
        public int heightmapSamples = 101;
        [Tooltip("地块边长 m")]
        public float fieldSize = 100f;
        [Tooltip("高度图高差 m（解码系数）")]
        public float heightmapReliefMeters = 3.1075f;

        [Header("玫瑰株丛（商业化种植密度 180–330 株/亩，取 300）")]
        [Tooltip("六角错行间距 s，m")]
        public float latticeSpacing = 1.602f;
        [Tooltip("蓬径 D，m（几何全覆盖判据 D ≥ 2s/√3）")]
        public float roseCanopyDiameter = 1.85f;
        [Tooltip("株高 m")]
        public float roseHeight = 1.25f;

        [Header("地面")]
        [Tooltip("自动构建地面网格（已烘焙进场景时存在同名子物体则跳过）")]
        public bool buildGround = true;
        public Color groundColor = new Color(0.42f, 0.47f, 0.33f);

        [Header("渲染")]
        [Tooltip("玫瑰朝向随机种子（确定性）")]
        public uint roseSeed = 20260912u;
        [Tooltip("关闭逐株阴影投射（4500+ 株，开销大）")]
        public bool disableRoseShadows = true;

        [Header("引用（可选，仅供 HUD 显示小人坐标）")]
        public Transform walkerView;

        // ---- 运行时数据 ----
        public HeightField Field { get; private set; }
        public Vector3[] RosePositions { get; private set; }
        public Mesh RoseMesh { get; private set; }
        public Material RoseMaterial { get; private set; }
        public int LatticeRows { get; private set; }
        public int LatticeCols { get; private set; }

        /// <summary>株数密度（株/亩，1 亩 = 666.6667 m²）。</summary>
        public float PlantsPerMu =>
            RosePositions == null || fieldSize <= 0f ? 0f : RosePositions.Length / (fieldSize * fieldSize / 666.6667f);

        /// <summary>几何全覆盖所需最小蓬径 m = 2s/√3（三角格覆盖半径 = s/√3）。</summary>
        public float MinCanopyForFullCoverage => 2f * latticeSpacing / Mathf.Sqrt(3f);

        /// <summary>冠层投影面积比 = π(D/2)² ÷ 单株占地 (√3/2)s²。≥ 1 表示冠层闭合。</summary>
        public float CanopyCoverRatio
        {
            get
            {
                float perPlant = Mathf.Sqrt(3f) * 0.5f * latticeSpacing * latticeSpacing;
                return perPlant <= 0f ? 0f : Mathf.PI * (roseCanopyDiameter * 0.5f) * (roseCanopyDiameter * 0.5f) / perPlant;
            }
        }

        /// <summary>是否满足几何全覆盖（地面无裸露）。</summary>
        public bool IsFullCoverage => roseCanopyDiameter >= MinCanopyForFullCoverage - 1e-4f;

        private Transform _rosesRoot;
        private bool _built;

        private void Awake()
        {
            Build();
        }

        /// <summary>幂等构建：高度场 → 株丛网格 → 六角错行株位 → 地面 → 玫瑰对象。失败 fail-fast。</summary>
        public void Build()
        {
            if (_built) return;

            var asset = Resources.Load<TextAsset>(heightmapResource);
            if (asset == null)
                throw new System.InvalidOperationException(
                    "找不到高度图资源：Resources/" + heightmapResource + ".bytes（应在 code/unity/Assets/Resources/YANTF/ 下）");

            Field = HeightField.FromTextAsset(asset, heightmapSamples, fieldSize, heightmapReliefMeters);
            RoseMesh = RoseMeshFactory.Build(roseCanopyDiameter, roseHeight);
            RosePositions = GenerateHexLattice(out int rows, out int cols);
            LatticeRows = rows;
            LatticeCols = cols;

            RoseMaterial = MakeRoseMaterial();
            EnsureGround();
            // 株丛对象只在运行时生成：4563 个 GameObject 烘焙进场景会让 .unity 膨胀到数 MB、
            // 层级面板卡顿；运行时生成还能保证布局始终跟随 Inspector 当前参数。
            if (Application.isPlaying) BuildRoseObjects();

            _built = true;
        }

        /// <summary>六角错行株位：行距 s·√3/2，奇行横向偏移 s/2。y 取地块实际高度。</summary>
        public Vector3[] GenerateHexLattice(out int rows, out int cols)
        {
            float s = latticeSpacing;
            float dz = s * Mathf.Sqrt(3f) * 0.5f;
            rows = Mathf.FloorToInt(fieldSize / dz) + 1;
            cols = Mathf.FloorToInt(fieldSize / s) + 1;
            float z0 = (fieldSize - (rows - 1) * dz) * 0.5f;
            float x0 = (fieldSize - (cols - 1) * s) * 0.5f;

            var list = new List<Vector3>(rows * cols);
            for (int r = 0; r < rows; r++)
            {
                bool odd = (r & 1) == 1;
                float z = z0 + r * dz;
                float xs = x0 + (odd ? s * 0.5f : 0f);
                int n = odd ? cols - 1 : cols;
                for (int c = 0; c < n; c++)
                {
                    float x = xs + c * s;
                    if (x > fieldSize) continue;
                    list.Add(new Vector3(x, Field.HeightAtWorld(x, z), z));
                }
            }
            return list.ToArray();
        }

        /// <summary>逐株生成确定性偏航（0–360°）与 1.00–1.15 缩放（缩放 ≥ 1 保证蓬径不低于判据 D）。</summary>
        public void GetInstanceTransform(int index, out Quaternion rotation, out float scale)
        {
            uint h = unchecked(roseSeed + (uint)index * 2654435761u);
            rotation = Quaternion.Euler(0f, (h % 3600u) * 0.1f, 0f);
            scale = 1f + ((h >> 12) % 1000u) * 0.00015f;
        }

        // ---- 构建辅助 ----

        private void BuildRoseObjects()
        {
            var existing = transform.Find(RosesName);
            if (existing != null)
            {
                if (Application.isPlaying) Destroy(existing.gameObject);
                else DestroyImmediate(existing.gameObject);
            }

            var root = new GameObject(RosesName);
            root.transform.SetParent(transform, false);
            _rosesRoot = root.transform;

            var shadow = disableRoseShadows
                ? UnityEngine.Rendering.ShadowCastingMode.Off
                : UnityEngine.Rendering.ShadowCastingMode.On;

            for (int i = 0; i < RosePositions.Length; i++)
            {
                var go = new GameObject("Rose");
                go.transform.SetParent(_rosesRoot, false);
                GetInstanceTransform(i, out Quaternion rot, out float scale);
                go.transform.SetPositionAndRotation(RosePositions[i], rot);
                go.transform.localScale = Vector3.one * scale;

                var mf = go.AddComponent<MeshFilter>();
                mf.sharedMesh = RoseMesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = RoseMaterial;
                mr.shadowCastingMode = shadow;
                mr.receiveShadows = true;
            }
        }

        private void EnsureGround()
        {
            if (!buildGround) return;
            if (transform.Find(GroundName) != null) return; // 已烘焙进场景 → 跳过

            var go = new GameObject(GroundName);
            go.transform.SetParent(transform, false);

            var mesh = Field.BuildGroundMesh();
            var mf = go.AddComponent<MeshFilter>();
            mf.sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = MakeGroundMaterial();
            var mc = go.AddComponent<MeshCollider>();
            mc.sharedMesh = mesh;
        }

        private Material MakeRoseMaterial()
        {
            var shader = Shader.Find("YANTF/RoseInstanced");
            bool fallback = shader == null;
            if (fallback) shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Diffuse");

            var mat = new Material(shader) { name = "RoseInstanced" };
            mat.enableInstancing = true; // 4563 个共享材质的 Renderer → 自动实例化合批
            if (mat.HasProperty("_Tint")) mat.SetColor("_Tint", Color.white);
            if (fallback && mat.HasProperty("_Color")) mat.color = new Color(0.72f, 0.15f, 0.22f);
            return mat;
        }

        private Material MakeGroundMaterial()
        {
            var shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Diffuse");
            var mat = new Material(shader) { name = "RoseFieldGround" };
            if (mat.HasProperty("_Color")) mat.color = groundColor;
            if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", 0.05f);
            return mat;
        }

        // ---- 目视/HUD ----

        private void OnGUI()
        {
            if (!_built || Field == null) return;
            Vector3 wp = walkerView != null ? walkerView.position : Vector3.zero;

            GUILayout.BeginArea(new Rect(12f, 12f, 470f, 200f));
            GUILayout.Label("玫瑰花海实验场 (Grilling #126)");
            GUILayout.Label($"地块 {fieldSize:F0}×{fieldSize:F0} m  高度图 {Field.Samples}×{Field.Samples} @ {fieldSize / (Field.Samples - 1):F1} m");
            GUILayout.Label($"地块高差 {Field.Relief:F4} m   最大 1m 高差 {Field.MaxSlopePerMeter():F4} m ({Mathf.Atan(Field.MaxSlopePerMeter()) * Mathf.Rad2Deg:F2}°)");
            GUILayout.Label($"株数 {RosePositions.Length}   密度 {PlantsPerMu:F0} 株/亩   错行间距 {latticeSpacing:F3} m   行数 {LatticeRows}");
            GUILayout.Label($"蓬径 D {roseCanopyDiameter:F2} m   全覆盖判据 2s/√3 {MinCanopyForFullCoverage:F3} m → {(IsFullCoverage ? "覆盖率 1.0 ✅" : "覆盖率<1 ⚠")}   投影比 {CanopyCoverRatio:F3}");
            GUILayout.Label(walkerView != null
                ? $"小人位置 ({wp.x:F1}, {wp.y:F2}, {wp.z:F1})"
                : "小人位置 —（未接线 walkerView）");
            GUILayout.Label("WASD 移动 / Shift 跑 / Space 跳");
            GUILayout.EndArea();
        }
    }
}
