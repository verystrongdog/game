// 持握接触测量（运行时，只读）— 规格 §四·戊·5 判据 4/5 的**尺子**
//
// 为什么需要它（2026-09-14）：owner 目视两条点名——「椅子一直在穿模」「手没有包构件」——
// 而当时的判据 1–3 **完全没覆盖**这两件事：判据 1 只量两手距离、判据 2② 只要求副手在
// 0.15–0.25 m 邻域（**手贴在旁边 2 mm 也算过**）、判据 3 只管椅子相对手骨漂不漂。
// 而挂点期间 `isKinematic` + 忽略碰撞是 §戊·2 的明写设计 ⇒ **物理也不会拦穿模**。
// ⇒ 补两把**几何尺子**，全部只用现成的量（椅子各部件是 BoxCollider、骨架是 Transform），
//   **不需要任何标定**（不依赖肌肉读数阈值）。
//
// 判据 4 · 无穿模：把骨架按"骨段"离散成采样点，逐点对椅子每个 BoxCollider 求
//   · 是否进入盒内 → 穿透深度 = 到最近面的距离（盒内为 min(halfExtent − |Δ|)）
//   · 盒外 → 到盒表面的最近距离（最小间隙）
//   分两组统计：**躯干/上臂/大腿**（本不该进椅子）与**手/前臂**（允许接触，但骨心入盒 ≤ 2 cm）。
// 判据 5 · 包握：每根手指**末节**到椅子最近表面的距离（贴上去）+ **掌心与指尖是否分居构件两侧**
//   （绕过去了）——两侧判定用最近的那个盒的"最大穿透轴"作分隔轴。
//
// ⚠️ 只读：不移动任何东西、不改权重。读数进 `LastReport`（可被 HUD/断言/eval 读）。
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace YANTF.ActionLab
{
    public static class GripContactMeasure
    {
        // ---- 判据 4 的阈值（规格 §戊·5）----
        /// <summary>躯干/上臂/大腿：允许的骨心入盒深度（m）。0 = 一律不得进入。</summary>
        public const float BodyPenetrationTolM = 0.0f;
        /// <summary>手与前臂：允许接触，但骨心不得深入盒内超过此值（m）。</summary>
        public const float HandPenetrationTolM = 0.02f;
        /// <summary>非接触部位的最小间隙下限（m）。</summary>
        public const float MinClearanceM = 0.01f;
        // ---- 判据 5 的阈值 ----
        /// <summary>指尖到构件表面的最大距离（m）：超了就是"没贴上去"。</summary>
        public const float FingerTipMaxM = 0.015f;

        /// <summary>骨段采样步长（m）。</summary>
        private const float SampleStepM = 0.03f;

        public sealed class Reading
        {
            public float BodyPenetrationM;        // 躯干/上臂/大腿 最大穿透（m）
            public string BodyPenetrationBone;    // 最深的那根骨
            public float HandPenetrationM;        // 手/前臂 最大穿透（m）
            public string HandPenetrationBone;
            public float MinClearanceM;           // 全体采样点的最小间隙（m；盒内记为 0）
            public float[] FingerTipDistM;        // 10 个指尖（左右手）到椅面的距离
            public bool[] FingerWrapped;          // 10 个指尖是否与掌心分居两侧
            public int SampleCount;

            public bool PassesCriterion4 => BodyPenetrationM <= BodyPenetrationTolM
                                            && HandPenetrationM <= HandPenetrationTolM;
            public bool PassesCriterion5
            {
                get
                {
                    for (int i = 0; i < FingerTipDistM.Length; i++)
                    {
                        if (FingerTipDistM[i] > FingerTipMaxM) return false;
                        if (!FingerWrapped[i]) return false;
                    }
                    return true;
                }
            }

            public override string ToString()
            {
                var sb = new StringBuilder();
                sb.Append($"判据4 躯干穿透 {BodyPenetrationM * 100f:F2} cm").Append(BodyPenetrationBone != null ? $"（{BodyPenetrationBone}）" : "")
                  .Append($" · 手/前臂穿透 {HandPenetrationM * 100f:F2} cm")
                  .Append($" · 最小间隙 {MinClearanceM * 100f:F2} cm")
                  .Append(BodyPenetrationM <= BodyPenetrationTolM && HandPenetrationM <= HandPenetrationTolM ? " ⇒ 过" : " ⇒ 红");
                sb.Append("\n判据5 指尖距椅面（cm）/包握：");
                for (int i = 0; i < FingerTipDistM.Length; i++)
                    sb.Append($" [{(i < 5 ? "L" : "R")}{i % 5}] {FingerTipDistM[i] * 100f:F1}{(FingerWrapped[i] ? "包" : "✗")}");
                sb.Append(PassesCriterion5 ? " ⇒ 过" : " ⇒ 红");
                sb.Append($"\n采样点 {SampleCount}");
                return sb.ToString();
            }
        }

        // 参与判据 4 的骨段（父 → 子）；手/前臂单独成组（允许接触）
        private static readonly (HumanBodyBones a, HumanBodyBones b, bool isBody)[] Segments =
        {
            (HumanBodyBones.Hips, HumanBodyBones.Spine, true),
            (HumanBodyBones.Spine, HumanBodyBones.Chest, true),
            (HumanBodyBones.Chest, HumanBodyBones.Neck, true),
            (HumanBodyBones.Neck, HumanBodyBones.Head, true),
            (HumanBodyBones.LeftShoulder, HumanBodyBones.LeftUpperArm, true),
            (HumanBodyBones.RightShoulder, HumanBodyBones.RightUpperArm, true),
            (HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, true),
            (HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, true),
            (HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot, true),
            (HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot, true),
            (HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm, false),
            (HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, false),
            (HumanBodyBones.LeftLowerArm, HumanBodyBones.LeftHand, false),
            (HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand, false),
        };

        private static readonly HumanBodyBones[] Fingertips =
        {
            HumanBodyBones.LeftThumbDistal, HumanBodyBones.LeftIndexDistal, HumanBodyBones.LeftMiddleDistal,
            HumanBodyBones.LeftRingDistal, HumanBodyBones.LeftLittleDistal,
            HumanBodyBones.RightThumbDistal, HumanBodyBones.RightIndexDistal, HumanBodyBones.RightMiddleDistal,
            HumanBodyBones.RightRingDistal, HumanBodyBones.RightLittleDistal,
        };

        /// <summary>
        /// 量一次接触（只读）。`chairRoot` 下需有启用的 BoxCollider；`animator` 需已求值到目标姿势。
        /// </summary>
        public static Reading Measure(Transform chairRoot, Animator animator)
        {
            var r = new Reading { BodyPenetrationM = 0f, HandPenetrationM = 0f, MinClearanceM = float.MaxValue,
                                  FingerTipDistM = new float[10], FingerWrapped = new bool[10] };
            if (chairRoot == null || animator == null) return r;

            var boxes = chairRoot.GetComponentsInChildren<BoxCollider>();
            if (boxes.Length == 0) return r;

            // ---- 判据 4：骨段采样 ----
            foreach (var (a, b, isBody) in Segments)
            {
                var ta = animator.GetBoneTransform(a);
                var tb = animator.GetBoneTransform(b);
                if (ta == null || tb == null) continue;

                float len = Vector3.Distance(ta.position, tb.position);
                int n = Mathf.Max(2, Mathf.CeilToInt(len / SampleStepM));
                for (int i = 0; i <= n; i++)
                {
                    var p = Vector3.Lerp(ta.position, tb.position, i / (float)n);
                    r.SampleCount++;
                    foreach (var box in boxes)
                    {
                        float depth = PenetrationDepth(box, p, out float clearance);
                        if (depth > 0f)
                        {
                            if (isBody && depth > r.BodyPenetrationM)
                            { r.BodyPenetrationM = depth; r.BodyPenetrationBone = a + "→" + b; }
                            if (!isBody && depth > r.HandPenetrationM)
                            { r.HandPenetrationM = depth; r.HandPenetrationBone = a + "→" + b; }
                        }
                        else if (clearance < r.MinClearanceM) r.MinClearanceM = clearance;
                    }
                }
            }
            if (r.MinClearanceM == float.MaxValue) r.MinClearanceM = 0f;

            // ---- 判据 5：指尖贴合 + 与掌心分居两侧 ----
            for (int i = 0; i < Fingertips.Length; i++)
            {
                var tip = animator.GetBoneTransform(Fingertips[i]);
                var palm = animator.GetBoneTransform(i < 5 ? HumanBodyBones.LeftHand : HumanBodyBones.RightHand);
                if (tip == null || palm == null) { r.FingerTipDistM[i] = float.MaxValue; r.FingerWrapped[i] = false; continue; }

                float best = float.MaxValue; BoxCollider bestBox = null;
                foreach (var box in boxes)
                {
                    float d = Vector3.Distance(tip.position, box.ClosestPoint(tip.position));
                    if (d < best) { best = d; bestBox = box; }
                }
                r.FingerTipDistM[i] = best;
                r.FingerWrapped[i] = bestBox != null && OppositeSides(bestBox, palm.position, tip.position);
            }
            return r;
        }

        /// <summary>点到盒：盒内返回穿透深度（&gt;0），盒外返回 0 并给出到表面的间隙。</summary>
        private static float PenetrationDepth(BoxCollider box, Vector3 worldPoint, out float clearance)
        {
            var lp = box.transform.InverseTransformPoint(worldPoint) - box.center;
            var h = box.size * 0.5f;
            var d = new Vector3(h.x - Mathf.Abs(lp.x), h.y - Mathf.Abs(lp.y), h.z - Mathf.Abs(lp.z));
            if (d.x > 0f && d.y > 0f && d.z > 0f)
            {
                clearance = 0f;
                return Mathf.Min(d.x, Mathf.Min(d.y, d.z));   // 盒内：到最近面的距离
            }
            var outside = new Vector3(Mathf.Max(-d.x, 0f), Mathf.Max(-d.y, 0f), Mathf.Max(-d.z, 0f));
            clearance = outside.magnitude;
            return 0f;
        }

        /// <summary>掌心与指尖是否分居该盒"最薄轴"两侧（= 手指绕过去了）。</summary>
        private static bool OppositeSides(BoxCollider box, Vector3 palmWorld, Vector3 tipWorld)
        {
            var h = box.size * 0.5f;
            int axis = h.x <= h.y && h.x <= h.z ? 0 : (h.y <= h.z ? 1 : 2);
            float S(Vector3 w)
            {
                var lp = box.transform.InverseTransformPoint(w) - box.center;
                return axis == 0 ? lp.x : (axis == 1 ? lp.y : lp.z);
            }
            return S(palmWorld) * S(tipWorld) < 0f;
        }
    }
}
