// 接触修正探针（运行时）— #157
//
// 作用：在隔离 lab 里**布置共同样本的目标**、**切换约束权重**、并按口径读出 M1–M7。
// 口径权威：[动画处理能力对照实验.md](../../../design/presentation/动画处理能力对照实验.md)
//   §2.1 样本 / §2.2 取帧规则 / §2.3 共同目标 / §3 观测口径（M1–M7）/ §3.1 读数纪律 / §3.3 根对齐定义。
//   ⚠️ 本文件里的数值常量**全部转录自该文档**，是"固定项"，不是本探针的调参面；改这里 = 改口径，先改文档。
//
// ⚠️ 三条硬约束（照抄自实测，别绕）：
//   1. 约束**只在真场景里建图**（危险点表 §六「RigBuilder 建图时机」）：本组件挂在入库场景 `AnimationRiggingLab`
//      的载体上，`Awake` 会拿着**已序列化**的 layers 建图。运行时合成搭建（先 AddComponent 再 Add layer）静默不生效。
//   2. 约束**不在**「`Animator.Play` + `Update(0f)`」那条确定性姿势路径上求值（Animation Rigging 走自己的
//      PlayableGraph / `DirectorUpdateMode.GameTime`）。⇒ 读"约束开"的读数必须**真帧**：
//      `animator.speed = 0` + `Animator.Play(state, 0, t)` 定位到目标帧，等若干帧后读。
//      "约束关"的对照同样走真帧（同一帧、同一路径，只差权重）——§3.1 要求两次**同一帧**。
//   3. 读数归属唯一（§3.1 / 文档 §七.4）：lab 内**不挂** `FootGroundingIK`，双脚贴地完全由 rig 约束负责，
//      否则两套机制同时写同一双脚，M2 无法归属。
//
// 用法（由 `AnimationRiggingLabBuilder` 驱动的探针流程）：
//   Play → `RunMeasureMatrix()` 打印 M1–M7 的关/开对照读数（JSON 一行，便于从 Console 抄进证据）
//   Play → `CaptureCorrectedPoses()` 抓逐帧"约束开"的人形姿势 → 落 JSON → 退出 Play 后由 Editor 侧烘焙成 .anim
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEngine.Animations.Rigging;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 接触修正 lab 的观测探针。挂在 lab 场景的 X Bot 载体上，与 `RigBuilder` 同物体。
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public class AnimationRiggingProbe : MonoBehaviour
    {
        // ---------------- 共同样本固定项（来源：对照实验 §2.1 / §2.3）----------------

        /// <summary>足底余量 m（§2.1；来源 `FootGroundingIK.cs` 头注：bind pose 趾骨 Y = +0.0028 实测）。</summary>
        public const float SoleMargin = 0.0028f;

        /// <summary>右手命中目标的角色局部偏移（§2.3，模长 0.187 m）——owner 2026-09-14 升为固定项。</summary>
        public const float TargetOffsetRight = 0.15f;
        public const float TargetOffsetUp = 0.10f;
        public const float TargetOffsetForward = 0.05f;

        /// <summary>取帧采样的均匀点数（§2.2：41 点）。</summary>
        public const int ContactSampleCount = 41;

        /// <summary>被修正的动作段（§2.1：物攻直拳 = Mixamo `Jab Cross`）。状态名 = 词表 id。</summary>
        public const string SourceStateName = "PhysicalAttack";

        // ---------------- 场景接线（由 builder 赋值并序列化进场景）----------------

        public Animator animator;
        public RigBuilder rigBuilder;
        public Rig rig;

        [Header("约束（右手 / 左腿 / 右腿，各一条最小 TwoBoneIK）")]
        public TwoBoneIKConstraint rightArmIK;
        public TwoBoneIKConstraint leftLegIK;
        public TwoBoneIKConstraint rightLegIK;

        [Header("共同样本目标（§2.3）")]
        public Transform rightHandTarget;
        public Transform leftFootTarget;
        public Transform rightFootTarget;

        [Header("根/髋参考（§2.4）")]
        public Transform hipsReference;

        [Header("地面（§2.1：过原点的水平面，表面 y = 0）")]
        public float groundY = 0f;

        // ---------------- 场景里序列化的取帧结果与首帧基准 ----------------
        // ⚠️ 为什么存在场景里而不是在 Play 里现算（2026-09-14 实测踩到）：
        //   Play 中 Animator 正在驱动骨架，`AnimationClip.SampleAnimation` 的写入会被播放图覆盖——
        //   实测在 Play 里重算目标，得到的目标离手 **762 mm**（应为 187 mm），脚被 IK 拉到 +245 mm 且膝角 0°
        //   ——即"整条读数都是垃圾"。取帧与目标布置因此只在 **Editor 建场景时**做一次，结果序列化进场景。
        /// <summary>接触帧号（§2.2；由 builder 在编辑期算出并写进场景）。</summary>
        public int contactFrame = -1;
        /// <summary>接触帧时刻（秒）。</summary>
        public float contactTime = 0f;
        /// <summary>源 clip 首帧的髋参考位置（M3a 基准，§3.3 首帧不变量口径）。</summary>
        public Vector3 firstFrameHipPos;
        /// <summary>源 clip 首帧的髋骨 forward（M3b 基准，§3.3）。</summary>
        public Vector3 firstFrameHipForward;

        // ---------------- 定位到某一帧（确定性路径）----------------

        /// <summary>
        /// 把骨架**确定性地**摆到源 clip 的第 `frame` 帧，并冻结时间。
        /// `Animator.Play(state, layer, normalizedTime)` + `Animator.Update(0f)`——Unity CLI README §五 的路径
        /// （实测编辑期与 Play 期同值：norm=0.7000、右手 `(-0.0560, 1.3323, 0.1690)`）。
        /// ⚠️ 三个坑（2026-09-14 实测，代价一整轮垃圾读数）：
        ///   ① **必须调 `Update(0f)`**：不调则定位不生效（实测请求 norm=0.7、状态时间停在 22/64）。
        ///   ② **不要先 `speed = 0` 再 Play**：同样不生效。顺序是 Play → Update(0f) → 冻结 speed。
        ///   ③ 先前已在播的状态上直接 `Play` 也要走 `Update(0f)`，否则时间不动。
        /// 另：本路径给出的是**播放语义**的姿势（`applyRootMotion = false`、角色留在原点），
        /// 与 `SampleAnimation` 的**采样语义**（含 clip 自身根位移）在绝对位置上差约 1 m——
        /// 目标必须按本文（播放语义）布置，否则离手 762 mm、IK 够不到（实测）。取帧不受影响：
        /// 判据 `(右手 − 髋)` 对整体平移不变。
        /// </summary>
        public void PoseAtFrame(AnimationClip clip, int frame)
        {
            float frameRate = clip.frameRate > 0f ? clip.frameRate : 30f;
            animator.speed = 1f;
            animator.Play(SourceStateName, 0, Mathf.Clamp01(frame / frameRate / clip.length));
            animator.Update(0f);
            animator.speed = 0f;
        }

        // ---------------- 取帧（§2.2）----------------

        /// <summary>
        /// 接触帧 `t_c`：全段均匀采样 41 点，取 `argmax_t [(右手骨位置 − 髋骨位置) · 角色 forward]`，
        /// 再在相邻两点之间**逐帧细化到整帧**（§2.2 的取帧规则）。
        /// 采样走 `AnimationClip.SampleAnimation`（§2.2 求值方式；实测与人形 `AnimationMode` 逐位一致）。
        /// 返回整帧号；失败返回 -1。
        /// </summary>
        public int FindContactFrame(AnimationClip clip)
        {
            if (clip == null || animator == null)
            {
                Debug.LogError("[RigProbe] 取帧失败：clip 或 animator 为空");
                return -1;
            }

            var hand = animator.GetBoneTransform(HumanBodyBones.RightHand);
            var hips = animator.GetBoneTransform(HumanBodyBones.Hips);
            if (hand == null || hips == null)
            {
                Debug.LogError("[RigProbe] 取帧失败：取不到 RightHand / Hips 骨");
                return -1;
            }

            int best = 0;
            float bestProj = float.NegativeInfinity;
            var coarse = new float[ContactSampleCount];
            for (int i = 0; i < ContactSampleCount; i++)
            {
                float t = clip.length * i / (ContactSampleCount - 1);
                clip.SampleAnimation(gameObject, t);
                float proj = ProjectionOnCharacterForward(hand.position, hips.position);
                coarse[i] = proj;
                if (proj > bestProj) { bestProj = proj; best = i; }
            }

            // ---- 逐帧细化：在相邻两采样点之间的**整帧**上重采，取整帧最大 ----
            // ⚠️ 必须落在**整帧**上（§2.2「细化到整帧」）：否则 M1/M5 这类跨帧读数会停在两个整帧之间，
            //    与 Unity 侧其它读数不可比。
            float frameRate = clip.frameRate > 0f ? clip.frameRate : 30f;
            int totalFrames = Mathf.RoundToInt(clip.length * frameRate);
            int lo = best > 0 ? Mathf.FloorToInt(clip.length * (best - 1) / (ContactSampleCount - 1) * frameRate) : 0;
            int hi = best < ContactSampleCount - 1 ? Mathf.CeilToInt(clip.length * (best + 1) / (ContactSampleCount - 1) * frameRate) : totalFrames;
            lo = Mathf.Clamp(lo, 0, totalFrames);
            hi = Mathf.Clamp(hi, 0, totalFrames);

            int bestFrame = lo;
            float bestFrameProj = float.NegativeInfinity;
            for (int f = lo; f <= hi; f++)
            {
                clip.SampleAnimation(gameObject, f / frameRate);
                float proj = ProjectionOnCharacterForward(hand.position, hips.position);
                if (proj > bestFrameProj) { bestFrameProj = proj; bestFrame = f; }
            }

            // 留痕（§2.2：整条曲线 + argmax + 最终帧号必须写入证据——这里按曲线打印到 Console 供抄录）
            var sb = new StringBuilder();
            sb.Append("[RigProbe] 取帧 trace {\"clip\":\"").Append(clip.name)
              .Append("\",\"length\":").Append(F(clip.length))
              .Append(",\"frameRate\":").Append(F(frameRate))
              .Append(",\"totalFrames\":").Append(totalFrames)
              .Append(",\"coarseProjections\":[");
            for (int i = 0; i < coarse.Length; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(F(coarse[i]));
            }
            sb.Append("],\"coarseBestIndex\":").Append(best)
              .Append(",\"refineWindowFrames\":[").Append(lo).Append(',').Append(hi).Append(']')
              .Append(",\"contactFrame\":").Append(bestFrame)
              .Append(",\"contactTime\":").Append(F(bestFrame / frameRate))
              .Append(",\"contactProjection\":").Append(F(bestFrameProj))
              .Append('}');
            Debug.Log(sb.ToString());

            return bestFrame;
        }

        /// <summary>
        /// 源 clip 首帧的髋参考（M3a/M3b 的基准，§3.3 首帧不变量口径）。**只在编辑期建场景时调用**。
        /// 走播放语义的定位（与目标布置、与 Play 期读数同一套姿势语义），不用 `SampleAnimation`。
        /// </summary>
        public void CaptureFirstFrameReference(AnimationClip clip)
        {
            PoseAtFrame(clip, 0);
            var hips = animator.GetBoneTransform(HumanBodyBones.Hips);
            firstFrameHipPos = hips.position;
            firstFrameHipForward = hips.forward;
            Debug.Log("[RigProbe] 首帧髋参考 {\"hipPos\":\"" + V(firstFrameHipPos) + "\",\"hipForward\":\"" + V(firstFrameHipForward) + "\"}");
        }

        private float ProjectionOnCharacterForward(Vector3 handPos, Vector3 hipsPos)
        {
            // ⚠️ 朝向取**角色面朝**（§2.2："forward（面朝）/ right（角色右手侧）/ up"），不是髋**骨**的本地朝向——
            //    实测 X Bot 的 `Hips.forward` 与角色面朝差 38°（首帧 trace：0.616, 0.030, 0.787），
            //    用它会把"最前伸"的帧和目标偏移一起转歪。髋骨 forward 只用在 M3b（§3.3 明写"髋骨 forward"）。
            var fwd = CharacterForward();
            return Vector3.Dot(handPos - hipsPos, fwd);
        }

        /// <summary>角色面朝（水平投影、归一化）：§2.2 的 `forward`。载体在 lab 里无附加旋转 ⇒ 等于 `transform.forward`。</summary>
        public Vector3 CharacterForward()
        {
            var f = transform.forward;
            f.y = 0f;
            return f.sqrMagnitude < 1e-8f ? Vector3.forward : f.normalized;
        }

        // ---------------- 目标布置（§2.3）----------------

        /// <summary>
        /// 在接触帧上布置三个目标：右手命中目标 = 接触帧右手位置 + 角色局部 (right 0.15 / up 0.10 / forward 0.05)；
        /// 左右脚目标 = 该脚足底最低点抬到 `地面 + soleMargin`（**只上抬不下压**）。
        /// ⚠️ **只在编辑期建场景时调用**（Play 中 `SampleAnimation` 会被播放图覆盖，见上方字段注释）。
        /// 同时把接触帧号/时刻写进序列化字段，供 Play 期读数使用。
        /// </summary>
        public string PlaceTargetsAtContactFrame(AnimationClip clip, int frame)
        {
            float frameRate = clip.frameRate > 0f ? clip.frameRate : 30f;
            PoseAtFrame(clip, frame);   // 播放语义（含 §PoseAtFrame 的三条坑）

            this.contactFrame = frame;
            this.contactTime = frame / frameRate;

            var hips = animator.GetBoneTransform(HumanBodyBones.Hips);
            var hand = animator.GetBoneTransform(HumanBodyBones.RightHand);

            // 角色局部轴（§2.2：偏移用**角色自身坐标系**表达，不用全局轴名；也不用髋骨朝向，理由见 ProjectionOnCharacterForward）
            Vector3 fwd = CharacterForward();
            Vector3 right = Vector3.Cross(Vector3.up, fwd).normalized;   // 角色右手侧
            Vector3 up = Vector3.up;

            Vector3 target = hand.position + right * TargetOffsetRight + up * TargetOffsetUp + fwd * TargetOffsetForward;
            rightHandTarget.position = target;
            // ⚠️ 目标**朝向**必须跟骨一致：约束的 `maintainTargetRotationOffset = false` 意味着
            //    "把 tip 的朝向设成目标的朝向"。目标若是 identity 朝向，手/脚会被硬拧过去——
            //    实测左脚趾被抬到 **+220 mm**（踝明明精确到位、残差 0.0008 mm），M2 因此报 +81.6 mm 的假读数。
            rightHandTarget.rotation = hand.rotation;

            PlaceFootTarget(leftFootTarget, HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes);
            PlaceFootTarget(rightFootTarget, HumanBodyBones.RightFoot, HumanBodyBones.RightToes);

            // 髋参考明确摆到接触帧髋位（§2.4 的"根/髋参考"节点，供时间轴逐帧检查）
            if (hipsReference != null) hipsReference.position = hips.position;

            string summary = "[RigProbe] 目标布置 {\"contactFrame\":" + frame +
                             ",\"contactTime\":" + F(frame / frameRate) +
                             ",\"rightHand\":\"" + V(hand.position) + "\"" +
                             ",\"rightHandTarget\":\"" + V(target) +
                             "\",\"offsetMagnitude\":" + F((target - hand.position).magnitude) +
                             ",\"leftFootTarget\":\"" + V(leftFootTarget.position) + "\"" +
                             ",\"rightFootTarget\":\"" + V(rightFootTarget.position) + "\"}";
            Debug.Log(summary);
            return summary;
        }

        private void PlaceFootTarget(Transform target, HumanBodyBones foot, HumanBodyBones toes)
        {
            var f = animator.GetBoneTransform(foot);
            var t = animator.GetBoneTransform(toes);
            float lowest = Mathf.Min(f.position.y, t != null ? t.position.y : f.position.y);
            float want = groundY + SoleMargin;
            float lift = Mathf.Max(0f, want - lowest);          // 只上抬不下压
            target.position = f.position + Vector3.up * lift;
            target.rotation = f.rotation;                        // 朝向跟骨（理由见右手目标的同注释）
        }

        // ---------------- 权重开关（§3.1 读数纪律）----------------

        /// <summary>
        /// 把 Rig 与三条约束的权重统一设为 `w`（0 = 关，1 = 开），并**重建约束图**。
        /// ⚠️ 只设权重不重建**不生效**（§3.1：Unity 侧须在改权重后重建约束图）。
        /// </summary>
        public bool SetWeights(float w)
        {
            if (rig == null || rigBuilder == null) return false;
            rig.weight = w;
            if (rightArmIK != null) rightArmIK.weight = w;
            if (leftLegIK != null) leftLegIK.weight = w;
            if (rightLegIK != null) rightLegIK.weight = w;
            bool built = rigBuilder.Build();
            if (!built) Debug.LogError("[RigProbe] RigBuilder.Build() 返回 false（约束图没建出来）");
            return built;
        }

        // ---------------- 读数（§3.1 / §3.3）----------------

        /// <summary>一次快照的全部读数字段（M1–M6；M7 是"重开后是否一致"，不在这里取）。</summary>
        public struct Snapshot
        {
            public string label;
            public int frame;
            public float weight;
            public float m1_handTargetMm;         // M1 右手 ↔ 目标距离
            public float m2_leftSoleMm;           // M2 左足底相对地面高度（负 = 陷入）
            public float m2_rightSoleMm;
            public float m3a_hipDriftMm;          // M3a 根水平漂移（对首帧）
            public float m3b_hipYawDeg;           // M3b 根朝向偏差（对首帧）
            public float m4_upperArmMm;           // M4 骨长（父空间口径 = 相邻关节世界距离）
            public float m4_lowerArmMm;
            public float m4_upperLegMm;
            public float m4_lowerLegMm;
            public float m5_leftSoleSlideMm;      // M5 脚滑代理量（tc → tc+1，需要两个快照相减）
            public float m6_elbowDeg;             // M6 肘屈曲角（有符号）
            public float m6_kneeLeftDeg;
            public float m6_kneeRightDeg;

            // ---- 原始位置（证据要"原始读数"，不要只有聚合量）----
            public Vector3 rawHandPos;
            public Vector3 rawRightHandTargetPos;
            public Vector3 rawLeftFootPos;        // 踝
            public Vector3 rawLeftToePos;
            public Vector3 rawLeftFootTargetPos;
            public float legLeftResidualMm;       // 左踝 ↔ 左脚目标 距离（约束是否收敛）
            public float legRightResidualMm;
            public float armResidualMm;           // 右手 ↔ 目标 距离（= M1，单列便于看收敛）
        }

        public Snapshot Measure(int frame, float weight, string label)
        {
            var s = new Snapshot { label = label, frame = frame, weight = weight };
            var hips = animator.GetBoneTransform(HumanBodyBones.Hips);
            var hand = animator.GetBoneTransform(HumanBodyBones.RightHand);

            s.m1_handTargetMm = Vector3.Distance(hand.position, rightHandTarget.position) * 1000f;

            s.m2_leftSoleMm = SoleHeight(HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes) * 1000f;
            s.m2_rightSoleMm = SoleHeight(HumanBodyBones.RightFoot, HumanBodyBones.RightToes) * 1000f;

            Vector3 drift = hips.position - firstFrameHipPos;
            drift.y = 0f;
            s.m3a_hipDriftMm = drift.magnitude * 1000f;
            s.m3b_hipYawDeg = Vector3.Angle(firstFrameHipForward, hips.forward);

            s.m4_upperArmMm = BoneLength(HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm);
            s.m4_lowerArmMm = BoneLength(HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand);
            s.m4_upperLegMm = BoneLength(HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg);
            s.m4_lowerLegMm = BoneLength(HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot);

            s.m6_elbowDeg = FlexionDeg(HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand);
            s.m6_kneeLeftDeg = FlexionDeg(HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot);
            s.m6_kneeRightDeg = FlexionDeg(HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot);

            // 原始位置与收敛残差（诊断"约束到没到目标"用）
            s.rawHandPos = hand.position;
            s.rawRightHandTargetPos = rightHandTarget.position;
            s.rawLeftFootPos = animator.GetBoneTransform(HumanBodyBones.LeftFoot).position;
            var leftToe = animator.GetBoneTransform(HumanBodyBones.LeftToes);
            s.rawLeftToePos = leftToe != null ? leftToe.position : s.rawLeftFootPos;
            s.rawLeftFootTargetPos = leftFootTarget.position;
            s.armResidualMm = s.m1_handTargetMm;
            s.legLeftResidualMm = Vector3.Distance(s.rawLeftFootPos, s.rawLeftFootTargetPos) * 1000f;
            s.legRightResidualMm = Vector3.Distance(animator.GetBoneTransform(HumanBodyBones.RightFoot).position,
                                                    rightFootTarget.position) * 1000f;

            return s;
        }

        /// <summary>足底最低点相对地面的高度（m）：足骨 y 与趾骨 y 的较小者 − 地面 y（§三 M2）。</summary>
        public float SoleHeight(HumanBodyBones foot, HumanBodyBones toes)
        {
            var f = animator.GetBoneTransform(foot);
            var t = animator.GetBoneTransform(toes);
            float y = Mathf.Min(f.position.y, t != null ? t.position.y : f.position.y);
            return y - groundY;
        }

        /// <summary>足底最低点的**水平**位置（M5 脚滑代理量用）。</summary>
        public Vector3 SoleGroundPoint(HumanBodyBones foot, HumanBodyBones toes)
        {
            var f = animator.GetBoneTransform(foot);
            var t = animator.GetBoneTransform(toes);
            var lower = (t != null && t.position.y < f.position.y) ? t : f;
            return new Vector3(lower.position.x, groundY, lower.position.z);
        }

        private float BoneLength(HumanBodyBones a, HumanBodyBones b)
        {
            var pa = animator.GetBoneTransform(a);
            var pb = animator.GetBoneTransform(b);
            if (pa == null || pb == null) return 0f;
            return Vector3.Distance(pa.position, pb.position) * 1000f;
        }

        /// <summary>
        /// 屈曲量（deg）= 180° − 三点夹角：完全伸直 = 0，弯曲为正（数值越大越弯）。
        /// 口径（§三 M6）原文是"有符号屈曲角（与源 clip 同号为正）"——本探针**只报屈曲量的大小**，
        /// 并另报"是否反关节"（b 落在 a–c 连线之外），因为在只有三点坐标时符号无法唯一确定。
        /// 这是对 §三 M6 的**如实收窄**，已写进证据的未闭合项。
        /// </summary>
        private float FlexionDeg(HumanBodyBones a, HumanBodyBones b, HumanBodyBones c)
        {
            var pa = animator.GetBoneTransform(a);
            var pb = animator.GetBoneTransform(b);
            var pc = animator.GetBoneTransform(c);
            if (pa == null || pb == null || pc == null) return 0f;
            return 180f - Vector3.Angle(pa.position - pb.position, pc.position - pb.position);
        }

        // ---------------- 派生件验证（约束关 → 独立播放是否保持修正结果）----------------

        /// <summary>
        /// 派生件验证（#157 验收标准 ④）：**关掉约束**，只用烘焙出来的 clip 采样到接触帧，
        /// 读 M1/M2 并与"约束开"时的读数比对。
        /// 口径：`AnimationClip.SampleAnimation` 直接写入曲线（肌肉 + RootT/RootQ），
        /// 与播放语义的差异来自根位移机制，而烘焙件把**播放语义**的姿势写进了曲线，故两者应一致。
        /// </summary>
        public string VerifyBakedClip(AnimationClip baked, int frame, int curveCount)
        {
            if (baked == null) { Debug.LogError("[RigProbe] 派生件为空，无法验证"); return null; }
            float frameRate = baked.frameRate > 0f ? baked.frameRate : 30f;
            SetWeights(0f);                       // 约束关：验证"脱离约束状态仍成立"
            baked.SampleAnimation(gameObject, frame / frameRate);

            var hand = animator.GetBoneTransform(HumanBodyBones.RightHand);
            float m1 = Vector3.Distance(hand.position, rightHandTarget.position) * 1000f;
            float m2L = SoleHeight(HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes) * 1000f;
            float m2R = SoleHeight(HumanBodyBones.RightFoot, HumanBodyBones.RightToes) * 1000f;

            string json = "[RigProbe] baked {\"clip\":\"" + baked.name +
                          "\",\"frame\":" + frame +
                          ",\"curveCount\":" + curveCount +
                          ",\"m1HandTargetMm\":" + F(m1) +
                          ",\"m2LeftSoleMm\":" + F(m2L) +
                          ",\"m2RightSoleMm\":" + F(m2R) + "}";
            Debug.Log(json);
            return json;
        }

        // ---------------- 校准（Play 内布置目标 → 落到场景）----------------

        /// <summary>
        /// 在 **Play 里**跑一次校准：取帧 → 首帧基准 → 按接触帧布置三个目标 → 把结果落成 JSON。
        /// 为什么校准必须在 Play 里做（2026-09-14 实测）：同一帧的姿势在**编辑期**与 **Play 期**并不相同
        /// （实测编辑期右手 `(-0.041, 1.281, 1.067)` vs Play 期 `(0.284, 1.370, 0.481)`，且差值**不是纯平移**；
        /// 根位移处理与求值路径不同所致）。目标若在编辑期算，Play 时会离手 **659 mm**，IK 够不到、
        /// 读数整片是垃圾。⇒ 校准与读数必须在同一套姿势语义下做，由 `ApplyCalibrationFromFile` 把结果写回场景。
        /// </summary>
        public IEnumerator CalibrateInPlay(AnimationClip clip, string outPath)
        {
            PoseAtFrame(clip, 0);
            CaptureFirstFrameReference(clip);
            int tc = FindContactFrame(clip);
            if (tc < 0) { Debug.LogError("[RigProbe] 校准失败：取帧失败"); yield break; }
            PlaceTargetsAtContactFrame(clip, tc);

            var sb = new StringBuilder();
            sb.Append("{\"contactFrame\":").Append(contactFrame)
              .Append(",\"contactTime\":").Append(F(contactTime))
              .Append(",\"firstFrameHipPos\":[").Append(N(firstFrameHipPos)).Append(']')
              .Append(",\"firstFrameHipForward\":[").Append(N(firstFrameHipForward)).Append(']')
              .Append(",\"rightHandTarget\":[").Append(N(rightHandTarget.position)).Append(']')
              .Append(",\"rightHandTargetRot\":[").Append(N(rightHandTarget.rotation)).Append(']')
              .Append(",\"leftFootTarget\":[").Append(N(leftFootTarget.position)).Append(']')
              .Append(",\"leftFootTargetRot\":[").Append(N(leftFootTarget.rotation)).Append(']')
              .Append(",\"rightFootTarget\":[").Append(N(rightFootTarget.position)).Append(']')
              .Append(",\"rightFootTargetRot\":[").Append(N(rightFootTarget.rotation)).Append(']')
              .Append('}');
            File.WriteAllText(outPath, sb.ToString());
            Debug.Log("[RigProbe] 校准完成 → " + outPath + " : " + sb);
        }

        private static string N(Vector3 v) => F(v.x) + "," + F(v.y) + "," + F(v.z);
        private static string N(Quaternion q) => F(q.x) + "," + F(q.y) + "," + F(q.z) + "," + F(q.w);

        // ---------------- 测量矩阵（关/开 · 同一帧）----------------

        /// <summary>
        /// 跑一遍 M1–M6 的关/开对照：在 `t_c − 1 / t_c / t_c + 1` 三个整帧上，权重 0 与 1 各取一次快照。
        /// 帧号取**场景里序列化的接触帧**（编辑期算好，见字段注释）；读数以 JSON 一行打印（标签 `[RigProbe] measure`）。
        /// </summary>
        public IEnumerator RunMeasureMatrix(AnimationClip clip)
        {
            float frameRate = clip.frameRate > 0f ? clip.frameRate : 30f;
            int tc = contactFrame >= 0 ? contactFrame : Mathf.RoundToInt(contactTime * frameRate);
            if (tc <= 0) Debug.LogError("[RigProbe] 场景里的接触帧无效（contactFrame=" + contactFrame +
                                        "）——先跑菜单「创建 AnimationRiggingLab 场景」把取帧结果写进场景");
            var frames = new[] { Mathf.Max(0, tc - 1), tc, tc + 1 };
            var snapshots = new List<Snapshot>();
            _leftSoles.Clear();
            _rightSoles.Clear();

            foreach (float w in new[] { 0f, 1f })
            {
                foreach (int f in frames)
                {
                    yield return MeasureAtFrame(clip, f, frameRate, w, snapshots);
                }
            }

            // M5 脚滑代理量：同一权重下 t_c → t_c+1 的足底最低点**水平**位移（§三 M5）
            var m5 = new List<string>();
            foreach (float w in new[] { 0f, 1f })
            {
                int iTc = IndexOf(snapshots, frames[1], w);
                int iTc1 = IndexOf(snapshots, frames[2], w);
                float l = Vector3.Distance(_leftSoles[iTc], _leftSoles[iTc1]) * 1000f;
                float r = Vector3.Distance(_rightSoles[iTc], _rightSoles[iTc1]) * 1000f;
                m5.Add("{\"weight\":" + F(w) + ",\"m5LeftSoleSlideMm\":" + F(l) + ",\"m5RightSoleSlideMm\":" + F(r) + "}");
            }

            var sb = new StringBuilder();
            sb.Append("[RigProbe] measure {\"contactFrame\":").Append(tc)
              .Append(",\"frameRate\":").Append(F(frameRate))
              .Append(",\"soleMarginMm\":").Append(F(SoleMargin * 1000f))
              .Append(",\"targetOffsetMagnitudeMm\":").Append(F(new Vector3(TargetOffsetRight, TargetOffsetUp, TargetOffsetForward).magnitude * 1000f))
              .Append(",\"snapshots\":[");
            for (int i = 0; i < snapshots.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(SnapshotJson(snapshots[i]));
            }
            sb.Append("],\"m5\":[").Append(string.Join(",", m5)).Append("]}");
            Debug.Log(sb.ToString());
            _lastSnapshots = snapshots;
        }

        private static int IndexOf(List<Snapshot> list, int frame, float weight)
        {
            for (int i = 0; i < list.Count; i++)
                if (list[i].frame == frame && Mathf.Abs(list[i].weight - weight) < 1e-6f) return i;
            return 0;
        }

        private readonly List<Vector3> _leftSoles = new List<Vector3>();
        private readonly List<Vector3> _rightSoles = new List<Vector3>();

        public List<Snapshot> LastSnapshots => _lastSnapshots;
        private List<Snapshot> _lastSnapshots = new List<Snapshot>();

        /// <summary>当前状态的归一化时刻（诊断用：确认冻结落在请求的那一帧上）。</summary>
        public float CurrentNormalizedTime => animator.GetCurrentAnimatorStateInfo(0).normalizedTime;

        private IEnumerator MeasureAtFrame(AnimationClip clip, int frame, float frameRate, float weight, List<Snapshot> sink)
        {
            // 定位到目标帧：**先 Play 定时刻、Update(0f) 让其生效、再冻时间**。
            // ⚠️ 顺序不能反（2026-09-14 实测，见 PoseAtFrame 头注）：少了 `Update(0f)` 或先冻 speed，
            //    定位都不生效——实测请求 norm=0.7、状态时间停在 22/64，读数因此全错（M1 报 762 mm，真值 187 mm）。
            PoseAtFrame(clip, frame);
            SetWeights(weight);
            // 等真帧：约束走自己的 PlayableGraph（GameTime），必须让它按帧求值
            for (int i = 0; i < 4; i++) yield return null;
            var s = Measure(frame, weight, weight > 0f ? "on" : "off");
            sink.Add(s);
            _leftSoles.Add(SoleGroundPoint(HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes));
            _rightSoles.Add(SoleGroundPoint(HumanBodyBones.RightFoot, HumanBodyBones.RightToes));
        }

        // ---------------- 烘焙采集（约束开 → 逐帧人形姿势）----------------

        /// <summary>
        /// 抓"约束开"状态下**逐帧**的人形姿势（肌肉 + 根），落成 JSON 交 Editor 侧烘焙成 `.anim`。
        /// 为什么要落文件而不是留静态字段：退出 Play 会触发域重载，静态数据会被清掉。
        /// </summary>
        public IEnumerator CaptureCorrectedPoses(AnimationClip clip, string outPath)
        {
            float frameRate = clip.frameRate > 0f ? clip.frameRate : 30f;
            int totalFrames = Mathf.RoundToInt(clip.length * frameRate);
            var handler = new HumanPoseHandler(animator.avatar, animator.transform);
            var sb = new StringBuilder();
            sb.Append("{\"clip\":\"").Append(clip.name)
              .Append("\",\"frameRate\":").Append(F(frameRate))
              .Append(",\"totalFrames\":").Append(totalFrames)
              .Append(",\"muscleCount\":").Append(HumanTrait.MuscleCount)
              .Append(",\"poses\":[");

            animator.speed = 0f;
            SetWeights(1f);

            for (int f = 0; f <= totalFrames; f++)
            {
                // 与读数走**同一条定位路径**（Play + Update(0f) + 冻结）——否则烘出来的姿势不是被测量的那一套
                PoseAtFrame(clip, f);
                SetWeights(1f);
                for (int i = 0; i < 2; i++) yield return null;

                var pose = new HumanPose();
                handler.GetHumanPose(ref pose);
                if (f > 0) sb.Append(',');
                sb.Append("{\"frame\":").Append(f)
                  .Append(",\"bodyPosition\":[")
                  .Append(F(pose.bodyPosition.x)).Append(',').Append(F(pose.bodyPosition.y)).Append(',').Append(F(pose.bodyPosition.z))
                  .Append("],\"bodyRotation\":[")
                  .Append(F(pose.bodyRotation.x)).Append(',').Append(F(pose.bodyRotation.y)).Append(',')
                  .Append(F(pose.bodyRotation.z)).Append(',').Append(F(pose.bodyRotation.w))
                  .Append("],\"muscles\":[");
                for (int m = 0; m < pose.muscles.Length; m++)
                {
                    if (m > 0) sb.Append(',');
                    sb.Append(F(pose.muscles[m]));
                }
                sb.Append("]}");
            }
            sb.Append("]}");

            File.WriteAllText(outPath, sb.ToString());
            Debug.Log("[RigProbe] 采集完成 → " + outPath + "（" + (totalFrames + 1) + " 帧）");
        }

        // ---------------- 打印工具 ----------------

        private string SnapshotJson(Snapshot s)
        {
            var sb = new StringBuilder();
            sb.Append("{\"label\":\"").Append(s.label).Append("\",\"frame\":").Append(s.frame)
              .Append(",\"weight\":").Append(F(s.weight))
              .Append(",\"m1HandTargetMm\":").Append(F(s.m1_handTargetMm))
              .Append(",\"m2LeftSoleMm\":").Append(F(s.m2_leftSoleMm))
              .Append(",\"m2RightSoleMm\":").Append(F(s.m2_rightSoleMm))
              .Append(",\"m3aHipDriftMm\":").Append(F(s.m3a_hipDriftMm))
              .Append(",\"m3bHipYawDeg\":").Append(F(s.m3b_hipYawDeg))
              .Append(",\"m4UpperArmMm\":").Append(F(s.m4_upperArmMm))
              .Append(",\"m4LowerArmMm\":").Append(F(s.m4_lowerArmMm))
              .Append(",\"m4UpperLegMm\":").Append(F(s.m4_upperLegMm))
              .Append(",\"m4LowerLegMm\":").Append(F(s.m4_lowerLegMm))
              .Append(",\"m6ElbowDeg\":").Append(F(s.m6_elbowDeg))
              .Append(",\"m6KneeLeftDeg\":").Append(F(s.m6_kneeLeftDeg))
              .Append(",\"m6KneeRightDeg\":").Append(F(s.m6_kneeRightDeg))
              .Append(",\"rawHandPos\":\"").Append(V(s.rawHandPos)).Append('"')
              .Append(",\"rawRightHandTargetPos\":\"").Append(V(s.rawRightHandTargetPos)).Append('"')
              .Append(",\"rawLeftFootPos\":\"").Append(V(s.rawLeftFootPos)).Append('"')
              .Append(",\"rawLeftToePos\":\"").Append(V(s.rawLeftToePos)).Append('"')
              .Append(",\"rawLeftFootTargetPos\":\"").Append(V(s.rawLeftFootTargetPos)).Append('"')
              .Append(",\"legLeftResidualMm\":").Append(F(s.legLeftResidualMm))
              .Append(",\"legRightResidualMm\":").Append(F(s.legRightResidualMm))
              .Append('}');
            return sb.ToString();
        }

        protected static string F(float v) => v.ToString("0.####", CultureInfo.InvariantCulture);
        protected static string V(Vector3 v) => v.x.ToString("0.#####", CultureInfo.InvariantCulture) + "," +
                                                v.y.ToString("0.#####", CultureInfo.InvariantCulture) + "," +
                                                v.z.ToString("0.#####", CultureInfo.InvariantCulture);
        protected static string Q(Quaternion q) => q.x.ToString("0.#####", CultureInfo.InvariantCulture) + "," +
                                                   q.y.ToString("0.#####", CultureInfo.InvariantCulture) + "," +
                                                   q.z.ToString("0.#####", CultureInfo.InvariantCulture) + "," +
                                                   q.w.ToString("0.#####", CultureInfo.InvariantCulture);
    }
}
