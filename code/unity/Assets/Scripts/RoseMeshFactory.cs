// 程序化低模玫瑰株丛网格（玫瑰花海实验，Grilling #126）
// 口径：单株 = 5 茎（三棱柱）+ 8 叶（四边形）+ 5 花（每花 6 瓣），共 53 个四边形 = 106 三角形。
// 零外部资产 —— 与 WalkerController.BuildBody 同口径，保证实验自包含。
// 蓬径口径：茎尖水平半径 = canopyDiameter / 2，用于几何全覆盖判据 D ≥ 2s/√3（见 RoseFieldLab）。
// 法线显式指定（不依赖绕序），配合 Cull Off 材质实现双面可见。
using System.Collections.Generic;
using UnityEngine;

namespace YANTF.RoseField
{
    public static class RoseMeshFactory
    {
        public const int StemCount = 5;
        public const int LeafCount = 8;
        public const int PetalsPerFlower = 6;
        public const int StemSides = 3;

        private static readonly Color StemColor = new Color(0.20f, 0.36f, 0.14f, 1f);
        private static readonly Color LeafColor = new Color(0.30f, 0.52f, 0.20f, 1f);
        private static readonly Color PetalColor = new Color(0.78f, 0.13f, 0.22f, 1f);

        /// <summary>构建单株玫瑰株丛网格。canopyDiameter = 蓬径 m，height = 株高 m。</summary>
        public static Mesh Build(float canopyDiameter, float height)
        {
            if (canopyDiameter <= 0f) throw new System.ArgumentException("canopyDiameter 必须为正，实际 " + canopyDiameter);
            if (height <= 0f) throw new System.ArgumentException("height 必须为正，实际 " + height);

            var v = new List<Vector3>(256);
            var nrm = new List<Vector3>(256);
            var col = new List<Color>(256);
            var tri = new List<int>(512);

            float spread = canopyDiameter * 0.5f;
            var stemBase = new Vector3[StemCount];
            var stemTip = new Vector3[StemCount];
            var stemAng = new float[StemCount];

            // ---- 茎：从基部向外斜出，茎尖水平半径达到蓬径半径 ----
            for (int k = 0; k < StemCount; k++)
            {
                float ang = (k / (float)StemCount) * Mathf.PI * 2f + 0.4f;
                float leanT = 0.62f + 0.38f * (((k * 7) % 5) / 4f); // 0.62 → 1.00 蓬径半径
                float tipT = 0.78f + 0.22f * (((k * 3) % 4) / 3f);  // 0.78 → 1.00 株高
                stemAng[k] = ang;
                stemBase[k] = new Vector3(Mathf.Cos(ang) * spread * 0.06f, 0.01f, Mathf.Sin(ang) * spread * 0.06f);
                stemTip[k] = new Vector3(Mathf.Cos(ang) * spread * leanT, height * tipT, Mathf.Sin(ang) * spread * leanT);
                AddTaperedPrism(v, nrm, col, tri, stemBase[k], stemTip[k], 0.030f, 0.012f, StemSides, StemColor);
            }

            // ---- 叶：沿茎分布，叶面朝上（法线强制 y ≥ 0，避免背面发黑）----
            for (int l = 0; l < LeafCount; l++)
            {
                int k = l % StemCount;
                float t = 0.30f + 0.45f * ((l % 3) / 2f); // 0.30 / 0.525 / 0.75
                Vector3 pos = Vector3.Lerp(stemBase[k], stemTip[k], t);
                float outAng = stemAng[k] + ((l % 2 == 0) ? 0.8f : -0.8f);
                AddLeaf(v, nrm, col, tri, pos, outAng, 0.075f, 0.045f);
            }

            // ---- 花：每茎尖一朵，6 瓣外倾 ----
            for (int k = 0; k < StemCount; k++)
                for (int p = 0; p < PetalsPerFlower; p++)
                    AddPetal(v, nrm, col, tri, stemTip[k], (p / (float)PetalsPerFlower) * Mathf.PI * 2f, 0.105f, 0.080f);

            var mesh = new Mesh { name = "RoseClump" };
            mesh.SetVertices(v);
            mesh.SetNormals(nrm);
            mesh.SetColors(col);
            mesh.SetTriangles(tri, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        // ---- 图元 ----

        private static void AddLeaf(List<Vector3> v, List<Vector3> n, List<Color> c, List<int> t,
                                    Vector3 pos, float outAng, float len, float width)
        {
            Vector3 dir = new Vector3(Mathf.Cos(outAng), 0f, Mathf.Sin(outAng));
            Vector3 perp = new Vector3(-dir.z, 0f, dir.x);
            Vector3 lift = Vector3.up * (len * 0.55f); // 叶面上翘

            Vector3 a = pos + perp * (-width * 0.5f);
            Vector3 b = pos + perp * (width * 0.5f);
            Vector3 d = pos + dir * len + lift + perp * (width * 0.18f);
            Vector3 e = pos + dir * len + lift + perp * (-width * 0.18f);
            AddQuad(v, n, c, t, a, b, d, e, UpFacing(b - a, d - a), LeafColor);
        }

        private static void AddPetal(List<Vector3> v, List<Vector3> n, List<Color> c, List<int> t,
                                     Vector3 tip, float ang, float len, float width)
        {
            Vector3 dir = new Vector3(Mathf.Cos(ang), 0f, Mathf.Sin(ang));
            Vector3 perp = new Vector3(-dir.z, 0f, dir.x);
            Vector3 inner = tip - dir * (len * 0.20f);
            Vector3 lift = Vector3.up * (len * 0.75f); // 花瓣外倾上翘

            Vector3 a = inner + perp * (-width * 0.25f);
            Vector3 b = inner + perp * (width * 0.25f);
            Vector3 d = tip + dir * (len * 0.80f) + lift + perp * (width * 0.50f);
            Vector3 e = tip + dir * (len * 0.80f) + lift + perp * (-width * 0.50f);
            AddQuad(v, n, c, t, a, b, d, e, UpFacing(b - a, d - a), PetalColor);
        }

        private static void AddTaperedPrism(List<Vector3> v, List<Vector3> n, List<Color> c, List<int> t,
                                            Vector3 a, Vector3 b, float ra, float rb, int sides, Color color)
        {
            Vector3 ab = b - a;
            float len = ab.magnitude;
            if (len < 1e-4f) return;
            Vector3 dir = ab / len;
            Vector3 refAxis = Mathf.Abs(dir.y) > 0.9f ? Vector3.right : Vector3.up;
            Vector3 t1 = Vector3.Cross(refAxis, dir).normalized;
            Vector3 t2 = Vector3.Cross(dir, t1).normalized;

            for (int i = 0; i < sides; i++)
            {
                float a0 = (i / (float)sides) * Mathf.PI * 2f;
                float a1 = ((i + 1) / (float)sides) * Mathf.PI * 2f;
                Vector3 o0 = t1 * Mathf.Cos(a0) + t2 * Mathf.Sin(a0);
                Vector3 o1 = t1 * Mathf.Cos(a1) + t2 * Mathf.Sin(a1);
                Vector3 fn = (o0 + o1).sqrMagnitude > 1e-8f ? (o0 + o1).normalized : t1;

                AddQuad(v, n, c, t, a + o0 * ra, a + o1 * ra, b + o1 * rb, b + o0 * rb, fn, color);
            }
        }

        /// <summary>四边形 (a→b→d→e 环)。法线取 (b−a)×(d−a)，强制朝上分量。</summary>
        private static void AddQuad(List<Vector3> v, List<Vector3> n, List<Color> c, List<int> t,
                                    Vector3 a, Vector3 b, Vector3 d, Vector3 e, Vector3 normal, Color color)
        {
            int i0 = v.Count;
            v.Add(a); v.Add(b); v.Add(d); v.Add(e);
            for (int k = 0; k < 4; k++) { n.Add(normal); c.Add(color); }
            t.Add(i0); t.Add(i0 + 1); t.Add(i0 + 2);
            t.Add(i0); t.Add(i0 + 2); t.Add(i0 + 3);
        }

        /// <summary>取面法线并强制朝上（叶片/花瓣单面几何 + Cull Off，防止背面全黑）。</summary>
        private static Vector3 UpFacing(Vector3 e1, Vector3 e2)
        {
            Vector3 fn = Vector3.Cross(e1, e2);
            if (fn.sqrMagnitude < 1e-8f) return Vector3.up;
            fn.Normalize();
            return fn.y < 0f ? -fn : fn;
        }
    }
}
