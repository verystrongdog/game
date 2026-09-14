// 持握**调台**（运行时；非正典、非机制）— 给 owner 手调姿势用（规格 §四·戊·5 补记 / §戊·6）
//
// 为什么需要它：owner 目视两条点名——「格挡的姿势不对（双手持械 ≠ 格挡）」「椅子一直在穿模、
// 手没包住构件」。这两件事**判据量得出、但改不了**：判据 4/5 只给读数，改姿势得靠手。
//
// 用法（**Inspector 驱动**，不在代码里塞一堆键位）：
//   1. 进 Play → 按 `8` 持椅（椅子挂到右手）→ 按 `9` 打判据 4/5 读数（Console + HUD）
//   2. 选中带本组件的对象（ActionLab 演示者），按 `0` 打开调台 → 手臂 IK 权重由 0 提到 1
//   3. 在 Inspector 里拖下面三组数（**Play 中实时生效**），每调一次按 `9` 读一次尺子：
//      · `armTarget*`  — 直接**拖场景里的 `LeftHandTarget`** 也一样（IK 会带着左臂跟过去）
//      · `chairYaw/Pitch/Roll` — **绕挂点**转椅子（挂点不动，所以不会脱离手）
//      · `curl*`       — 手指闭合度（按节施加，用来包住构件）
//   4. 满意后按 `Capture()`（Inspector 按钮）把当前值打到 Console —— 那是要回填到
//      `ActionLabBuilder.DefaultGripPoses()` 与手指基线的数值。
//
// ⚠️ 三条边界，别误读：
//   ① **这是调台，不是机制**：手指闭合是"按节旋转骨架"，不是手指肌肉曲线，也不是最终方案；
//   ② **`curlAxis` / `curlAngleDeg` 可能需按实际骨架调**：轴向没有权威来源，我按右手系默认
//      取 (1,0,0) 并给左右手反向符号 —— **请目视确认手指是往掌心方向合拢**，不对就把轴/符号翻过来；
//   ③ 打开调台会**破坏 §二·O 的"接入点保持惰性"**（IK 权重 1），所以只允许运行时开、场景里
//      `Rig`/约束权重必须仍是 0（`ActionLabBuilder.VerifyRigInfrastructure` 会拦）。
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Animations.Rigging;

namespace YANTF.ActionLab
{
    [DisallowMultipleComponent]
    public sealed class GripTuningStand : MonoBehaviour
    {
        [Header("开关（键 0）：把 Animation Rigging 接入点的权重由 0 提到 1，让左臂跟着目标走")]
        public bool tuning;

        [Header("椅子：绕挂点旋转（度）。挂点固定不动，所以椅子不会脱手")]
        public float chairYaw;
        public float chairPitch;
        public float chairRoll;

        [Header("手指闭合：0 = 原姿势，1 = 全屈（按节旋转，非肌肉曲线）")]
        [Range(0f, 1f)] public float curl;
        public float curlAngleDeg = 70f;
        public Vector3 curlAxis = Vector3.right;
        public bool curlLeft = true;    // 左手也闭合（副手包握）
        public bool curlRight = true;   // 主手
        public bool invertCurlSign;     // 手指往手背方向翻时勾这个

        private RigBuilder _rigBuilder;
        private TwoBoneIKConstraint _ik;
        private Animator _animator;
        private ChairGrip _grip;
        private readonly Dictionary<HumanBodyBones, Quaternion> _baseline = new Dictionary<HumanBodyBones, Quaternion>();
        private bool _baselineCaptured;

        // 每根手指的 3 节（拇指 3 节：Proximal/Intermediate/Distal）
        private static readonly HumanBodyBones[][] FingerChains =
        {
            new[] { HumanBodyBones.LeftThumbProximal, HumanBodyBones.LeftThumbIntermediate, HumanBodyBones.LeftThumbDistal },
            new[] { HumanBodyBones.LeftIndexProximal, HumanBodyBones.LeftIndexIntermediate, HumanBodyBones.LeftIndexDistal },
            new[] { HumanBodyBones.LeftMiddleProximal, HumanBodyBones.LeftMiddleIntermediate, HumanBodyBones.LeftMiddleDistal },
            new[] { HumanBodyBones.LeftRingProximal, HumanBodyBones.LeftRingIntermediate, HumanBodyBones.LeftRingDistal },
            new[] { HumanBodyBones.LeftLittleProximal, HumanBodyBones.LeftLittleIntermediate, HumanBodyBones.LeftLittleDistal },
            new[] { HumanBodyBones.RightThumbProximal, HumanBodyBones.RightThumbIntermediate, HumanBodyBones.RightThumbDistal },
            new[] { HumanBodyBones.RightIndexProximal, HumanBodyBones.RightIndexIntermediate, HumanBodyBones.RightIndexDistal },
            new[] { HumanBodyBones.RightMiddleProximal, HumanBodyBones.RightMiddleIntermediate, HumanBodyBones.RightMiddleDistal },
            new[] { HumanBodyBones.RightRingProximal, HumanBodyBones.RightRingIntermediate, HumanBodyBones.RightRingDistal },
            new[] { HumanBodyBones.RightLittleProximal, HumanBodyBones.RightLittleIntermediate, HumanBodyBones.RightLittleDistal },
        };

        /// <summary>驱动层在持椅挂点后调用（或让它自己找）——用于拿到椅子与状态。</summary>
        public void Bind(ChairGrip grip) => _grip = grip;

        private void Awake()
        {
            _animator = GetComponent<Animator>();
            _rigBuilder = GetComponent<RigBuilder>();
            _ik = GetComponentInChildren<TwoBoneIKConstraint>();
        }

        /// <summary>开关调台：IK 权重 0 ↔ 1。**改动后必须 `Build()`**（§二·O 实测：只设权重不重建不生效）。</summary>
        public void ToggleTuning()
        {
            tuning = !tuning;
            ApplyWeights();
            if (tuning) CaptureBaseline();
            Debug.Log($"[调台] {(tuning ? "开" : "关")}：rig/IK 权重 = {(tuning ? 1 : 0)}" +
                      "（Play 中拖 Inspector 的 chairYaw/curl 等字段实时生效；按 9 读判据 4/5）");
        }

        private void ApplyWeights()
        {
            float w = tuning ? 1f : 0f;
            if (_rigBuilder != null && _rigBuilder.layers.Count > 0 && _rigBuilder.layers[0].rig != null)
                _rigBuilder.layers[0].rig.weight = w;
            if (_ik != null) _ik.weight = w;
            if (_rigBuilder != null) _rigBuilder.Build();
        }

        /// <summary>把当前姿势下各手指节的局部旋转记为基线（curl=0 的形状）。</summary>
        public void CaptureBaseline()
        {
            _baseline.Clear();
            if (_animator == null) return;
            foreach (var chain in FingerChains)
                foreach (var bone in chain)
                {
                    var t = _animator.GetBoneTransform(bone);
                    if (t != null) _baseline[bone] = t.localRotation;
                }
            _baselineCaptured = _baseline.Count > 0;
        }

        /// <summary>把调台当前值打成可回填的读数（Console）。</summary>
        public void Capture()
        {
            string anchorId = _grip != null ? _grip.HeldState.ToString() : "?";
            Debug.Log($"[调台·回填用] 状态 {anchorId}｜椅子绕挂点 yaw/pitch/roll = " +
                      $"{chairYaw:F1}/{chairPitch:F1}/{chairRoll:F1}｜curl = {curl:F2}（{curlAngleDeg:F0}°，轴 {curlAxis}，反转 {invertCurlSign}）");
        }

        private void LateUpdate()
        {
            if (!tuning) return;
            if (!_baselineCaptured) CaptureBaseline();
            ApplyChairRotation();
            ApplyCurl();
        }

        /// <summary>**绕挂点**转椅子：挂点在椅子局部坐标里是固定的，所以转换后要把它挪回原位。</summary>
        private void ApplyChairRotation()
        {
            if (_grip == null || !_grip.IsHeld) return;
            if (chairYaw == 0f && chairPitch == 0f && chairRoll == 0f) return;

            var chair = _grip.transform;
            var hand = _grip.HeldHand;
            if (hand == null) return;

            Vector3 anchorLocal = _grip.AnchorFor(_grip.HeldState);          // 椅子局部
            Vector3 anchorHandLocal = hand.InverseTransformPoint(chair.TransformPoint(anchorLocal));

            var rot = Quaternion.Euler(chairPitch, chairYaw, chairRoll);
            chair.localRotation = rot * chair.localRotation;
            Vector3 now = chair.localPosition + chair.localRotation * anchorLocal;
            chair.localPosition += anchorHandLocal - now;                    // 锚点回到手骨原点
        }

        /// <summary>按节施加手指闭合（相对基线的局部旋转）。</summary>
        private void ApplyCurl()
        {
            if (_animator == null || curl <= 0f) return;
            for (int i = 0; i < FingerChains.Length; i++)
            {
                bool left = i < 5;
                if (left && !curlLeft) continue;
                if (!left && !curlRight) continue;
                float sign = (left ? 1f : -1f) * (invertCurlSign ? -1f : 1f);
                var chains = FingerChains[i];
                for (int j = 0; j < chains.Length; j++)
                {
                    var t = _animator.GetBoneTransform(chains[j]);
                    if (t == null || !_baseline.TryGetValue(chains[j], out var b)) continue;
                    t.localRotation = b * Quaternion.AngleAxis(sign * curl * curlAngleDeg, curlAxis.normalized);
                }
            }
        }
    }
}
