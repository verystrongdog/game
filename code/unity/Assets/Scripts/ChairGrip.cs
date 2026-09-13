// 持椅挂点（YANTF.ActionLab）— 规格 §四·戊 §戊·2 的三个机制件的**第一次落地**
//
// 为什么需要它：全工程此前**没有任何挂点代码**（唯一 OnAnimatorIK 在 FootGroundingIK.cs），
// 而规格 §一 早已裁过道具口径——「面具、武器等**不换模型**，作为**骨骼挂点道具**（attach 到 Head/手骨）实现」。
// 于是 `Lift1H` / `Carry1H` / `Wield2H` / 格挡四条状态都**没有道具可持**。
//
// 本组件实现 §戊·2 的三件（编号同规格）：
//   #8  可握锚点 + 自动对齐 —— 锚点在**椅子局部**坐标上定义（`anchors`，由 builder 按椅子几何算），
//       世界位由 `transform` **实时**求出（不烘世界坐标）；**逐状态一张表**（`poses`）解析"挂哪只手 /
//       握椅子哪一处 / 椅子相对手骨的基准朝向"。
//   #9  阻尼摆动 —— 刚性挂点（A）是弹簧阻尼（B）的退化情形：`swayStiffness <= 0` 即直接对齐；
//       否则从**挂点当帧的实际位姿**出发、按弹簧阻尼收敛到基准位姿（重量感来自这里，不是修正）。
//       介入判据明写：残差（位移 ≤ `settleDistance`、夹角 ≤ `settleAngleDeg`）以内 → 弹簧归零并**精确定位**
//       （口径与足 IK「需要量 ≤ 0 时权重归 0」同族，但**判据另立**：手侧是主动拉向目标，不是只上抬不下压）。
//   #10 在"手到位帧"挂点 —— 切换帧由「手骨 ↔ 锚点距离曲线」的**最低点**求（`MeasureHandArrival`），
//       不是固定值；切换时**三者同时**发生：父子到 Hand / 椅子 isKinematic / 忽略与角色 CharacterController 的碰撞。
//
// 求值路径：`AnimationClip.SampleAnimation`（**运行时** API）。实测（2026-09-13）它对 Humanoid 肌肉曲线
// 与 `AnimationMode.SampleAnimationClip` **逐位一致**（差 0.000 mm），故"手到位帧"的读数在 Editor 与
// Play 两侧同源，且不必依赖 controller 里有对应状态。
//
// 数值来源：design/presentation/动作库规格.md §七（演示常量，非正典）· §四·戊 §戊·2。
using System.Collections.Generic;
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>持握状态（挂点表按此解析）。值 = 触发该状态的词条 id，供链接线按当前词条查表。</summary>
    public enum GripState
    {
        None = 0,
        Carry1H = 1,          // 单手提携（垂下在手侧）
        Wield2H = 2,          // 双手持握准备（横在身前）
        DefendCarry1H = 3,    // 持椅格挡（椅背当盾）
    }

    /// <summary>可握锚点（**椅子局部**坐标；不烘世界坐标）。</summary>
    [System.Serializable]
    public struct GripAnchor
    {
        public string id;
        public Vector3 localPosition;
        public Vector3 localEuler;
    }

    /// <summary>逐状态挂点定义（§戊·2 的"逐状态挂点表"）。</summary>
    [System.Serializable]
    public struct GripPose
    {
        public GripState state;
        public HumanBodyBones hand;
        public string anchorId;
        [Tooltip("椅子相对**手骨**的基准朝向（度）。三组各不相同：垂下 / 横在身前 / 当盾。演示常量，待 owner 目视调")]
        public Vector3 chairEulerInHand;
    }

    /// <summary>「手到位帧」读数（#10）：距离曲线的采样值 + 最低点。留痕可读。</summary>
    public struct HandArrivalReading
    {
        public GripState state;
        public string hand;
        public string anchorId;
        public int samples;
        public float[] distancesMm;      // 逐采样点的「手骨 ↔ 锚点」距离
        public float NormalizedTime;     // 最低点的归一化时刻 = **切换帧**
        public float DistanceMm;         // 最低点距离
        public float StartMm;            // 曲线两端读数（判"是不是真最低点"用）
        public float EndMm;

        public override string ToString()
            => $"state={state} hand={hand} anchor={anchorId} 切换帧 t={NormalizedTime:F3}（{DistanceMm:F1} mm）"
             + $" 曲线 {samples} 点：首 {StartMm:F1} / 末 {EndMm:F1} mm";
    }

    /// <summary>
    /// 椅子的**持握**侧（与 <see cref="ChairSeat"/> 的就座侧共用同一把椅子）。
    /// 两种占用**不得互相抢占**：椅子已被就座占用时拒绝挂点（`Seat.IsOccupied`），
    /// 反向由驱动层看 <see cref="IsHeld"/>（链接线 issue）。
    /// </summary>
    [RequireComponent(typeof(ChairSeat))]
    public sealed class ChairGrip : MonoBehaviour
    {
        [Header("可握锚点（椅子局部坐标；来源：builder 按椅子几何算出）")]
        public GripAnchor[] anchors = new GripAnchor[0];

        [Header("逐状态挂点表（§戊·2）")]
        public GripPose[] poses = new GripPose[0];

        [Header("阻尼摆动（§戊·2#9；演示常量，非正典）")]
        [Tooltip("刚度。<= 0 → 刚性挂点（A，退化情形）；> 0 → 弹簧阻尼收敛（B）")]
        public float swayStiffness = 0f;
        [Tooltip("阻尼系数")]
        public float swayDamping = 18f;
        [Tooltip("介入判据：夹角残差 ≤ 此值（度）**且**位移残差 ≤ settleDistance 时弹簧归零、精确定位")]
        public float settleAngleDeg = 1.5f;
        [Tooltip("介入判据：位移残差阈值 m")]
        public float settleDistance = 0.002f;

        [Header("「手到位帧」采样")]
        [Tooltip("距离曲线的采样点数（含两端）")]
        public int arrivalSamples = 41;

        /// <summary>当前是否被持握（父级在手上）。驱动层用它避免与就座抢占同一把椅子。</summary>
        public bool IsHeld { get; private set; }
        public GripState HeldState { get; private set; } = GripState.None;
        /// <summary>挂点当帧的手骨（解除时用）。</summary>
        public Transform HeldHand { get; private set; }

        /// <summary>最近一次挂点的读数留痕（#10：切换时刻必须可读）。</summary>
        public string LastAttachReport { get; private set; } = "（尚未挂点）";
        /// <summary>最近一次「手到位帧」读数。</summary>
        public HandArrivalReading LastArrival { get; private set; }
        /// <summary>最近一次阻尼收敛耗时 s（刚性挂点记 0）。</summary>
        public float LastSwaySettleSeconds { get; private set; }

        private ChairSeat _seat;
        private CharacterController _occupant;
        private bool _ignoredCollision;

        // 阻尼摆动的状态（全部在**手骨局部坐标系**里积分，故"跟随椅子局部旋转"）
        private Vector3 _baseLocalPos;
        private Quaternion _baseLocalRot = Quaternion.identity;
        private Vector3 _vel;
        private float _angVel;
        private bool _settled = true;

        public ChairSeat Seat => _seat != null ? _seat : (_seat = GetComponent<ChairSeat>());

        private void Awake()
        {
            _seat = GetComponent<ChairSeat>();
        }

        // ---------------- #8 可握锚点：由椅子 transform 实时求得 ----------------

        /// <summary>锚点在**世界**中的位置（实时；椅子被推动后自动跟随）。</summary>
        public bool TryGetAnchor(string id, out Vector3 worldPos, out Quaternion worldRot)
        {
            foreach (var a in anchors)
            {
                if (a.id != id) continue;
                worldPos = transform.TransformPoint(a.localPosition);
                worldRot = transform.rotation * Quaternion.Euler(a.localEuler);
                return true;
            }
            worldPos = transform.position;
            worldRot = transform.rotation;
            return false;
        }

        /// <summary>锚点的世界位置（取不到时退回椅子原点并留警告）。</summary>
        public Vector3 AnchorPosition(string id)
        {
            if (TryGetAnchor(id, out Vector3 p, out _)) return p;
            Debug.LogWarning("[Grip] 未定义的锚点 id: " + id + "（退回椅子原点）");
            return transform.position;
        }

        /// <summary>某状态的挂点定义（取不到 → false）。</summary>
        public bool TryGetPose(GripState state, out GripPose pose)
        {
            foreach (var p in poses)
            {
                if (p.state != state) continue;
                pose = p;
                return true;
            }
            pose = default;
            return false;
        }

        /// <summary>状态所用的可握锚点世界位（#8）。</summary>
        public Vector3 AnchorFor(GripState state)
            => TryGetPose(state, out var pose) ? AnchorPosition(pose.anchorId) : transform.position;

        /// <summary>
        /// 自动对齐（#8）：给定手骨，算出椅子应有的世界位姿——**锚点落在手骨原点上**、朝向 = 手骨朝向 × 基准朝向。
        /// 因此"椅子的哪一处握在手里"由锚点定义决定，不需要手摆坐标。
        /// </summary>
        public bool TrySolveHandPose(Transform hand, GripState state, out Vector3 worldPos, out Quaternion worldRot)
        {
            worldPos = transform.position;
            worldRot = transform.rotation;
            if (hand == null || !TryGetPose(state, out var pose)) return false;
            if (!TryGetAnchor(pose.anchorId, out Vector3 _, out _) && anchors.Length > 0) return false;

            GripAnchor anchor = default;
            foreach (var a in anchors) if (a.id == pose.anchorId) { anchor = a; break; }

            worldRot = hand.rotation * Quaternion.Euler(pose.chairEulerInHand);
            worldPos = hand.position - worldRot * anchor.localPosition;   // 锚点落到手骨原点
            return true;
        }

        // ---------------- #10 「手到位帧」：由距离曲线最低点求 ----------------

        /// <summary>
        /// 量「手骨 ↔ 锚点」距离曲线并取**最低点** = 切换帧（#10；不是固定值）。
        /// 用 `AnimationClip.SampleAnimation` 把人形 clip 采到载体上（实测与 AnimationMode 逐位一致）。
        /// ⚠️ 采样会把载体停在曲线末点对应的姿势上——调用方若要"切到最低点那一帧"，接着调 <see cref="AttachAtHandArrival"/>。
        /// </summary>
        public HandArrivalReading MeasureHandArrival(Animator animator, AnimationClip clip, GripState state)
        {
            var reading = new HandArrivalReading { state = state, samples = 0 };
            if (animator == null || clip == null) { Debug.LogWarning("[Grip] 手到位帧：animator/clip 缺失"); return reading; }
            if (!TryGetPose(state, out var pose))
            {
                Debug.LogWarning("[Grip] 手到位帧：状态未定义挂点 " + state);
                return reading;
            }

            int n = Mathf.Max(2, arrivalSamples);
            var handBone = animator.GetBoneTransform(pose.hand);
            if (handBone == null) { Debug.LogWarning("[Grip] 手到位帧：载体没有骨骼 " + pose.hand); return reading; }

            Vector3 anchorWorld = AnchorPosition(pose.anchorId);
            var d = new float[n];
            int best = 0;
            for (int i = 0; i < n; i++)
            {
                float nt = (float)i / (n - 1);
                clip.SampleAnimation(animator.gameObject, nt * clip.length);
                d[i] = Vector3.Distance(animator.GetBoneTransform(pose.hand).position, anchorWorld) * 1000f;
                if (d[i] < d[best]) best = i;
            }

            reading.hand = pose.hand.ToString();
            reading.anchorId = pose.anchorId;
            reading.samples = n;
            reading.distancesMm = d;
            reading.NormalizedTime = (float)best / (n - 1);
            reading.DistanceMm = d[best];
            reading.StartMm = d[0];
            reading.EndMm = d[n - 1];
            LastArrival = reading;
            Debug.Log("[Grip] 手到位帧读数 ← " + reading);
            return reading;
        }

        // ---------------- #10 挂点：三者同时发生 ----------------

        /// <summary>
        /// 量出「手到位帧」→ 把载体摆到那一帧 → 挂点。**切换时刻与读数同时留痕**（`LastArrival` / `LastAttachReport`）。
        /// </summary>
        public bool AttachAtHandArrival(Animator animator, AnimationClip clip, GripState state, CharacterController occupant)
        {
            var reading = MeasureHandArrival(animator, clip, state);
            if (reading.samples == 0) return false;
            clip.SampleAnimation(animator.gameObject, reading.NormalizedTime * clip.length);
            bool ok = Attach(animator, state, occupant);
            if (ok && LastArrival.samples > 0)
                LastAttachReport += $" ｜ 切换帧 t={LastArrival.NormalizedTime:F3}（手骨↔锚点 {LastArrival.DistanceMm:F1} mm）";
            return ok;
        }

        /// <summary>
        /// 挂点（§戊·2#10：**三者同时**）——① 父子到指定手骨 ② 椅子 isKinematic ③ 忽略与角色 CC 的碰撞。
        /// 已被就座占用（`ChairSeat.IsOccupied`）或已挂点时拒绝：两种占用不得互相抢占。
        /// </summary>
        public bool Attach(Animator animator, GripState state, CharacterController occupant)
        {
            if (!TryGetPose(state, out var pose)) { LastAttachReport = "状态未定义挂点: " + state; return false; }
            var hand = animator != null ? animator.GetBoneTransform(pose.hand) : null;
            if (hand == null) { LastAttachReport = "载体没有骨骼 " + pose.hand; return false; }
            return AttachTo(hand, state, occupant);
        }

        /// <summary>挂到手骨（同上三条同时发生）。分开一层是为了让 PlayMode 断言不必造 Animator。</summary>
        public bool AttachTo(Transform hand, GripState state, CharacterController occupant)
        {
            if (IsHeld) { LastAttachReport = "已在持握中（" + HeldState + "）"; return false; }
            if (Seat != null && Seat.IsOccupied)
            {
                LastAttachReport = "椅子正被就座占用 → 拒绝挂点（两种占用不得互抢）";
                Debug.LogWarning("[Grip] " + LastAttachReport);
                return false;
            }
            if (!TrySolveHandPose(hand, state, out Vector3 p, out Quaternion q))
            {
                LastAttachReport = "解不出手部位姿（状态 " + state + " / 锚点缺失）";
                return false;
            }

            // ① 父子（保世界位姿：从当帧实际位姿出发，阻尼把它收敛到基准）
            transform.SetParent(hand, true);
            _baseLocalPos = hand.InverseTransformPoint(p);
            _baseLocalRot = Quaternion.Inverse(hand.rotation) * q;

            bool rigid = swayStiffness <= 0f;
            if (rigid) transform.SetPositionAndRotation(p, q);
            _vel = Vector3.zero; _angVel = 0f;
            _settled = rigid;
            LastSwaySettleSeconds = 0f;
            SwayElapsed = 0f;

            // ② 刚体锁；③ 忽略与占用者的碰撞
            if (Seat != null && Seat.Body != null) Seat.Body.isKinematic = true;
            if (Seat != null && occupant != null) { Seat.SetCollisionIgnored(occupant, true); _ignoredCollision = true; }

            _occupant = occupant;
            IsHeld = true;
            HeldState = state;
            HeldHand = hand;
            LastAttachReport = $"已挂到 {hand.name}（状态 {state}，锚点 {(TryGetPose(state, out var pp) ? pp.anchorId : "?")}）"
                             + $"｜isKinematic={Seat?.Body?.isKinematic} 碰撞忽略={_ignoredCollision} 刚性={rigid}";
            Debug.Log("[Grip] " + LastAttachReport);
            return true;
        }

        /// <summary>解除挂点：还原父级（保世界位姿）、恢复刚体与碰撞。</summary>
        public void Detach()
        {
            if (!IsHeld) return;
            transform.SetParent(null, true);
            if (Seat != null)
            {
                if (Seat.Body != null) Seat.Body.isKinematic = false;
                if (_ignoredCollision && _occupant != null) Seat.SetCollisionIgnored(_occupant, false);
            }
            _ignoredCollision = false;
            _occupant = null;
            IsHeld = false;
            HeldState = GripState.None;
            HeldHand = null;
            _settled = true;
            LastAttachReport = "已解除挂点（父级/刚体/碰撞均已还原）";
        }

        // ---------------- #9 阻尼摆动 ----------------

        /// <summary>挂点后经过的时间 s（收敛耗时的分母）。</summary>
        public float SwayElapsed { get; private set; }
        /// <summary>当前残差（位移 m）。读数用。</summary>
        public float SwayPositionResidual { get; private set; }
        /// <summary>当前残差（夹角 度）。读数用。</summary>
        public float SwayAngleResidual { get; private set; }

        private void LateUpdate()
        {
            if (!IsHeld || HeldHand == null || _settled) return;

            Transform hand = HeldHand;
            Vector3 pos = hand.InverseTransformPoint(transform.position);
            Quaternion rot = Quaternion.Inverse(hand.rotation) * transform.rotation;

            SwayPositionResidual = (pos - _baseLocalPos).magnitude;
            SwayAngleResidual = Quaternion.Angle(rot, _baseLocalRot);
            SwayElapsed += Time.deltaTime;

            // 介入判据：残差进入阈值 → 弹簧归零 + **精确定位**（不留残差）
            if (SwayPositionResidual <= settleDistance && SwayAngleResidual <= settleAngleDeg)
            {
                transform.SetPositionAndRotation(hand.TransformPoint(_baseLocalPos), hand.rotation * _baseLocalRot);
                _vel = Vector3.zero; _angVel = 0f;
                _settled = true;
                LastSwaySettleSeconds = SwayElapsed;
                return;
            }

            float dt = Mathf.Max(Time.deltaTime, 1e-4f);
            float k = swayStiffness;
            float c = Mathf.Max(0f, swayDamping);
            float decay = 1f / (1f + c * dt);

            // 位移：半隐式弹簧
            _vel += (_baseLocalPos - pos) * (k * dt);
            _vel *= decay;
            pos += _vel * dt;

            // 旋转：绕"最短修正轴"的标量弹簧
            Quaternion dq = _baseLocalRot * Quaternion.Inverse(rot);
            dq.ToAngleAxis(out float ang, out Vector3 axis);
            if (ang > 180f) ang -= 360f;
            if (Mathf.Abs(ang) > 1e-4f)
            {
                _angVel += ang * (k * dt);
                _angVel *= decay;
                rot = Quaternion.AngleAxis(_angVel * dt, axis) * rot;
            }

            transform.SetPositionAndRotation(hand.TransformPoint(pos), hand.rotation * rot);
        }

        /// <summary>
        /// 读数式收敛演练（PlayMode 断言用，也可在 Play 里按需调用）：从当前（挂点后）位姿出发，
        /// 以固定步长推进阻尼并返回耗时；返回 true 表示在 maxSeconds 内**归零精确到位**。
        /// </summary>
        public bool StepSwayToSettle(Transform hand, float stepSeconds, float maxSeconds, out float settleSeconds)
        {
            settleSeconds = 0f;
            if (!IsHeld || hand == null) return false;
            _settled = false;
            SwayElapsed = 0f;
            int steps = Mathf.CeilToInt(maxSeconds / stepSeconds);
            for (int i = 0; i < steps; i++)
            {
                SwayStep(hand, stepSeconds);
                if (_settled) { settleSeconds = SwayElapsed; return true; }
            }
            settleSeconds = SwayElapsed;
            return false;
        }

        private void SwayStep(Transform hand, float dt)
        {
            Vector3 pos = hand.InverseTransformPoint(transform.position);
            Quaternion rot = Quaternion.Inverse(hand.rotation) * transform.rotation;
            SwayPositionResidual = (pos - _baseLocalPos).magnitude;
            SwayAngleResidual = Quaternion.Angle(rot, _baseLocalRot);
            SwayElapsed += dt;

            if (SwayPositionResidual <= settleDistance && SwayAngleResidual <= settleAngleDeg)
            {
                transform.SetPositionAndRotation(hand.TransformPoint(_baseLocalPos), hand.rotation * _baseLocalRot);
                _vel = Vector3.zero; _angVel = 0f;
                _settled = true;
                LastSwaySettleSeconds = SwayElapsed;
                return;
            }

            float k = swayStiffness;
            float decay = 1f / (1f + Mathf.Max(0f, swayDamping) * dt);
            _vel += (_baseLocalPos - pos) * (k * dt);
            _vel *= decay;
            pos += _vel * dt;

            Quaternion dq = _baseLocalRot * Quaternion.Inverse(rot);
            dq.ToAngleAxis(out float ang, out Vector3 axis);
            if (ang > 180f) ang -= 360f;
            if (Mathf.Abs(ang) > 1e-4f)
            {
                _angVel += ang * (k * dt);
                _angVel *= decay;
                rot = Quaternion.AngleAxis(_angVel * dt, axis) * rot;
            }
            transform.SetPositionAndRotation(hand.TransformPoint(pos), hand.rotation * rot);
        }

        /// <summary>持握中椅子在手骨局部坐标下的位姿（基准解析的读数；断言"组内稳定"用它）。</summary>
        public void GetLocalPoseInHand(Transform hand, out Vector3 localPos, out Quaternion localRot)
        {
            localPos = hand.InverseTransformPoint(transform.position);
            localRot = Quaternion.Inverse(hand.rotation) * transform.rotation;
        }

        private void OnDrawGizmosSelected()
        {
            foreach (var a in anchors)
            {
                Gizmos.color = new Color(0.2f, 0.8f, 1f, 0.9f);
                Gizmos.DrawWireSphere(transform.TransformPoint(a.localPosition), 0.03f);
            }
        }
    }
}
