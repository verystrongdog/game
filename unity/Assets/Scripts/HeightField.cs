// 高度场 — 玫瑰花海地块的高度图解码 / 双线性采样 / 地面网格构建（Grilling #126）
// 数据来源：USGS 3DEP 1 m lidar DEM（Konza Prairie 高草草原，美国公有领域）
//   raw 口径：little-endian uint16，行主序，行 0 = 北边缘，[0,65535] 线性映射到 [0, reliefMeters]
//   世界口径：x ∈ [0, Size] 向东，z ∈ [0, Size] 向北（raw 行 0 ↔ z = Size）
// 该口径由 tools 侧一次性导出脚本产出，见 呈现/地块数据-Konza草原.md 的复现命令。
using System;
using UnityEngine;

namespace YANTF.RoseField
{
    /// <summary>100×100 m 地块的采样高度场。构造失败一律 fail-fast 抛异常，不静默回退。</summary>
    public sealed class HeightField
    {
        public readonly int Samples;   // 每边采样数
        public readonly float Size;    // 边长 m
        public readonly float Relief;  // 最小→最大高差 m

        private readonly float[] _h;   // 相对最低点的抬升 m，索引 [row * Samples + col]

        private HeightField(int samples, float size, float relief, float[] h)
        {
            Samples = samples;
            Size = size;
            Relief = relief;
            _h = h;
        }

        /// <summary>从 16 位 raw 解码。字节数不符 → 抛异常（防止静默错位）。</summary>
        public static HeightField FromRaw16(byte[] raw, int samples, float size, float relief)
        {
            if (samples < 2) throw new ArgumentException("samples 至少为 2，实际 " + samples);
            if (size <= 0f) throw new ArgumentException("size 必须为正，实际 " + size);
            if (relief < 0f) throw new ArgumentException("relief 不可为负，实际 " + relief);

            int need = samples * samples * 2;
            if (raw == null || raw.Length != need)
                throw new ArgumentException("高度图字节数不符：期望 " + need + "，实际 " + (raw == null ? 0 : raw.Length));

            var h = new float[samples * samples];
            for (int i = 0; i < h.Length; i++)
                h[i] = (raw[i * 2] | (raw[i * 2 + 1] << 8)) / 65535f * relief;
            return new HeightField(samples, size, relief, h);
        }

        /// <summary>从 Resources 载入的 TextAsset（.bytes）解码。</summary>
        public static HeightField FromTextAsset(TextAsset asset, int samples, float size, float relief)
        {
            if (asset == null) throw new ArgumentException("高度图 TextAsset 为 null");
            return FromRaw16(asset.bytes, samples, size, relief);
        }

        /// <summary>raw 网格高度 m（row 0 = 北边缘）。</summary>
        public float HeightAtSample(int row, int col)
        {
            if (row < 0 || row >= Samples || col < 0 || col >= Samples)
                throw new ArgumentOutOfRangeException("采样下标越界：" + row + "," + col);
            return _h[row * Samples + col];
        }

        /// <summary>世界坐标 (x,z) → 高度 m。双线性插值；域外钳制到边缘。</summary>
        public float HeightAtWorld(float x, float z)
        {
            float fx = Mathf.Clamp01(x / Size) * (Samples - 1);
            float fz = Mathf.Clamp01(1f - z / Size) * (Samples - 1); // raw 行 0 = 北 = z 最大
            int c0 = Mathf.Min((int)fx, Samples - 2);
            int r0 = Mathf.Min((int)fz, Samples - 2);
            float tx = fx - c0;
            float tz = fz - r0;

            float h00 = _h[r0 * Samples + c0];
            float h01 = _h[r0 * Samples + c0 + 1];
            float h10 = _h[(r0 + 1) * Samples + c0];
            float h11 = _h[(r0 + 1) * Samples + c0 + 1];
            return Mathf.Lerp(Mathf.Lerp(h00, h01, tx), Mathf.Lerp(h10, h11, tx), tz);
        }

        /// <summary>最大 1 m 间距内的高差（m/m），用于坡度核验（须 &lt; tan(CharacterController.slopeLimit)）。</summary>
        public float MaxSlopePerMeter()
        {
            float m = 0f;
            for (int r = 0; r < Samples; r++)
            {
                for (int c = 0; c < Samples; c++)
                {
                    float v = _h[r * Samples + c];
                    if (c + 1 < Samples) m = Mathf.Max(m, Mathf.Abs(_h[r * Samples + c + 1] - v));
                    if (r + 1 < Samples) m = Mathf.Max(m, Mathf.Abs(_h[(r + 1) * Samples + c] - v));
                }
            }
            return m;
        }

        /// <summary>构建地面网格：Samples×Samples 顶点，(Samples−1)² 四边形，法线朝上。</summary>
        public Mesh BuildGroundMesh()
        {
            int n = Samples;
            var verts = new Vector3[n * n];
            var uvs = new Vector2[n * n];
            float d = Size / (n - 1);

            for (int r = 0; r < n; r++)
            {
                for (int c = 0; c < n; c++)
                {
                    int i = r * n + c;
                    verts[i] = new Vector3(c * d, _h[i], Size - r * d); // raw 行 0 = 北
                    uvs[i] = new Vector2((float)c / (n - 1), 1f - (float)r / (n - 1));
                }
            }

            var tris = new int[(n - 1) * (n - 1) * 6];
            int t = 0;
            for (int r = 0; r < n - 1; r++)
            {
                for (int c = 0; c < n - 1; c++)
                {
                    int i = r * n + c;
                    // z 随行下标递减 → 下列绕序的法线朝上
                    tris[t++] = i;
                    tris[t++] = i + 1;
                    tris[t++] = i + n;
                    tris[t++] = i + 1;
                    tris[t++] = i + n + 1;
                    tris[t++] = i + n;
                }
            }

            var m = new Mesh { name = "RoseFieldGround" };
            if (verts.Length > 65000)
                m.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
            m.vertices = verts;
            m.uv = uvs;
            m.triangles = tris;
            m.RecalculateNormals();
            m.RecalculateBounds();
            return m;
        }
    }
}
