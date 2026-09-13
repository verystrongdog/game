// ActionLab 场景驱动 — CharacterController 物理 + 输入 → ActionPlayer（动作词表 13 词条演示场）
// 位移口径同 KiWalkerLab（AnimatorWalker）：CC 移动（无 RootMotion），动画状态由 ActionPlayer 决定。
// **例外**：坐立三段（Sit/SitIdle/Stand）声明了 RootMotionXZ —— 播放期间把 clip 的 XZ 根位移
//   经 cc.Move 施加（Y 丢弃、旋转不施加），角色由此从椅子前方的就座锚点退到坐面上（规格 §四·乙 再修正）。
//
// 按键：WASD/方向键 走位（相机相对）、Shift 跑、Space 跳（locomotion 空中态）；
//       1物攻 2精攻 3防御(再按退出) 4受击 5倒下 6坐 7起身（动作键）、R 重置（Down 终态后）。
//       **6 坐不再无条件生效**：先"找到椅子"（走到椅子前 · 椅子前侧 · 椅子空闲）→ 对齐到就座锚点 → 坐下；
//       找不到就不切态，HUD 给出最近距离（规格 §四·丁）。
// HUD：IMGUI 顶部显示当前动作名 + 椅子状态（目视清单 ② ⑧ 验收项）。
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>ActionLab 演示场驱动：物理归本类，状态选择归 ActionPlayer（契约 A）。</summary>
    [RequireComponent(typeof(CharacterController))]
    public sealed class ActionLabDriver : MonoBehaviour
    {
        [Header("移动参数（演示常量，非正典数值；口径同 AnimatorWalker）")]
        [Tooltip("行走速度 m/s")]
        public float walkSpeed = 3.0f;
        [Tooltip("奔跑速度 m/s")]
        public float runSpeed = 6.0f;
        [Tooltip("跳跃初速抬升高度 m")]
        public float jumpHeight = 1.4f;
        [Tooltip("重力 m/s^2（向下）")]
        public float gravity = -22f;
        [Tooltip("空中方向修正 0..1")]
        public float airControl = 0.15f;
        [Tooltip("空中水平速度衰减 /s")]
        public float airDrag = 0.5f;

        [Header("就座交互（来源：动作库规格.md §四·丁 / §七）")]
        [Tooltip("对齐时长 s：判定命中后把角色移到就座锚点并对齐椅子朝向所用的时间")]
        public float alignSeconds = 0.25f;
        [Tooltip("推椅冲量系数：被推开时椅子速度 = 角色水平速度 × 此值（0 = 推不动）")]
        public float pushImpulseScale = 0.6f;

        [Header("引用（builder 注入；缺省从自身/子级获取）")]
        public Animator animator;
        public ActionPlayer player;

        // 脚本/测试驱动
        private Vector3 _scriptDir;
        private float _scriptSpeed;
        private bool _scriptRun;
        private bool _scriptJumpQueued;
        private bool _useScriptInput;

        private CharacterController _cc;
        private float _vSpeed;
        private Vector3 _airVelocity;

        // ---- 就座交互状态 ----
        private ChairSeat _chair;              // 当前占用中的椅子（就座链上非 null）
        private ChairSeat _alignChair;         // 对齐段进行中（非 null = 正在就位）
        private float _alignElapsed;
        private Vector3 _alignFromPos, _alignToPos;
        private Quaternion _alignFromRot, _alignToRot;
        private ChairSeat _collisionPending;   // 已解除占用、但因角色仍在坐面内而暂缓恢复碰撞的椅子
        private string _hint;
        private float _hintUntil;
        private string _chairStatus = "—";

        /// <summary>当前占用中的椅子（无则 null）。测试/排障面。</summary>
        public ChairSeat OccupiedChair => _chair;
        /// <summary>最近一次"找不到椅子"或"被拒"的提示文本（HUD 与断言共用）。</summary>
        public string LastSitHint => _hint;
        /// <summary>对齐段是否进行中。</summary>
        public bool IsAligning => _alignChair != null;
        /// <summary>上一次对齐段的残差 m（对齐结束那一刻角色到锚点的水平距离）——读数面，供断言与实测记录用。</summary>
        public float LastAlignmentError { get; private set; }

        private void Awake()
        {
            _cc = GetComponent<CharacterController>();
            if (animator == null) animator = GetComponentInChildren<Animator>();
            if (player == null) player = GetComponent<ActionPlayer>();
            if (player != null && animator != null) player.animator = animator;
            SizeControllerToModel();
        }

        /// <summary>脚本/测试驱动移动：给定世界水平方向、速度与跑/跳标记。</summary>
        public void SetMoveInput(Vector3 worldDir, float speed, bool run, bool jump)
        {
            _useScriptInput = true;
            _scriptDir = worldDir;
            _scriptSpeed = speed;
            _scriptRun = run;
            if (jump) _scriptJumpQueued = true;
        }

        public void ClearScriptInput() => _useScriptInput = false;

        private void Update()
        {
            if (_cc == null || player == null) return;

            TickPendingCollisionRestore();

            // 对齐段优先：期间不响应移动输入（人正在"转身就位"）
            if (_alignChair != null)
            {
                RunAlignment(Time.deltaTime);
                return;
            }

            Vector3 dir = _useScriptInput ? _scriptDir : Vector3.zero;
            float speed = _useScriptInput ? _scriptSpeed : 0f;
            bool run = _useScriptInput && _scriptRun;
            bool jumpQueued = _useScriptInput && _scriptJumpQueued;
            _scriptJumpQueued = false;

            if (!_useScriptInput)
            {
                float h = Input.GetAxisRaw("Horizontal");
                float v = Input.GetAxisRaw("Vertical");
                if (Mathf.Abs(h) > 0.01f || Mathf.Abs(v) > 0.01f)
                {
                    dir = CameraRelativeDir(h, v);
                    speed = walkSpeed;
                    run = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
                    if (run) speed = runSpeed;
                }
                if (Input.GetKeyDown(KeyCode.Space)) jumpQueued = true;

                HandleActionKeys();
            }

            TickMove(dir, speed, run, jumpQueued);
            FeedPlayer();
            ReleaseChairWhenChainEnds();
        }

        private void HandleActionKeys()
        {
            // 演示键位：1物攻 2精攻 3防御 4受击 5倒下 6坐 7起身 R重置（对齐 DemoSandbox 1/2/3 肌肉记忆）
            if (Input.GetKeyDown(KeyCode.Alpha1)) player.Play(ActionIds.PhysicalAttack);
            if (Input.GetKeyDown(KeyCode.Alpha2)) player.Play(ActionIds.MentalAttack);
            if (Input.GetKeyDown(KeyCode.Alpha3))
            {
                if (player.CurrentActionId == ActionIds.Defend) player.ResetToIdle();
                else player.Play(ActionIds.Defend);
            }
            if (Input.GetKeyDown(KeyCode.Alpha4)) player.Play(ActionIds.HitReaction);
            if (Input.GetKeyDown(KeyCode.Alpha5)) player.Play(ActionIds.Down);
            // 坐立三段（同源）：6 坐下 → 由 NextState 自动续切 SitIdle 坐住；7 起身 → 回 locomotion
            // 6 **必须先找到椅子**（规格 §四·丁）：走到椅子前 + 站在椅子前侧 + 椅子空闲 → 对齐 → 坐下；
            //   找不到就不切态（原口径"按 6 无条件坐"已作废——那会让角色坐在空气里）。
            // 7 加输入层守卫：起身 clip 首帧就是坐姿，站姿下硬播会看到"瞬蹲再起"。
            // 动作层 ActionPlayer.Play() 不设该守卫——那层保持"按键即播"的宽松口径（规格 §四·甲）。
            if (Input.GetKeyDown(KeyCode.Alpha6)) TrySitOnNearestChair();
            if (Input.GetKeyDown(KeyCode.Alpha7) && player.CurrentActionId == ActionIds.SitIdle)
                player.Play(ActionIds.Stand);
            if (Input.GetKeyDown(KeyCode.R)) player.ResetToIdle();
        }

        /// <summary>
        /// 按 6 的完整链路：**判定命中 → 对齐（就位）→ 播 Sit**。命中失败不切态、只留 HUD 提示。
        /// 返回"是否已开始就座序列"（对齐段已启动或已进坐立链），供断言与脚本调用。
        /// </summary>
        public bool TrySitOnNearestChair()
        {
            if (_cc == null || player == null) return false;

            // 已在坐立链上（Sit 一次性锁定 / SitIdle 持续态 / Stand 一次性）：不重复触发
            if (player.IsLocked || player.ApplyRootMotionXZ || _alignChair != null) return false;
            if (player.IsAirborne) { SetHint("空中不能就座"); return false; }

            ChairSeat chair = ChairSeat.FindBest(transform.position);
            if (chair == null)
            {
                ChairSeat nearest = ChairSeat.FindNearest(transform.position, out float nd);
                SetHint(nearest == null
                    ? "附近没有椅子（场景里没有椅子）"
                    : $"附近没有椅子（最近锚点 {nd:F2} m，需 ≤ {ChairSeat.DefaultInteractRadius:F2} m 且在椅子前侧）");
                return false;
            }

            BeginSit(chair);
            return true;
        }

        private void BeginSit(ChairSeat chair)
        {
            _chair = chair;
            chair.Occupy(_cc);                 // 占用锁：kinematic + 忽略与本角色的碰撞
            _alignChair = chair;               // 对齐段：把角色移到锚点并对齐椅子 forward
            _alignElapsed = 0f;
            _alignFromPos = transform.position;
            _alignFromRot = transform.rotation;
            _alignToPos = chair.AnchorPosition;
            _alignToPos.y = transform.position.y;   // 垂直仍归 CC/重力
            _alignToRot = Quaternion.LookRotation(Flat(chair.Forward), Vector3.up);
            SetHint(null);
        }

        /// <summary>对齐段：alignSeconds 内把角色移到就座锚点、朝向对齐椅子 forward，然后播 Sit。</summary>
        private void RunAlignment(float dt)
        {
            _alignElapsed += dt;
            float t = alignSeconds <= 0f ? 1f : Mathf.Clamp01(_alignElapsed / alignSeconds);
            float s = t * t * (3f - 2f * t);   // smoothstep：起步与到位都不突兀

            Vector3 want = Vector3.Lerp(_alignFromPos, _alignToPos, s);
            Vector3 delta = want - transform.position;
            _cc.Move(new Vector3(delta.x, 0f, delta.z));   // 走 CC（该椅子的碰撞已忽略）
            transform.rotation = Quaternion.Slerp(_alignFromRot, _alignToRot, s);

            if (t < 1f) return;

            LastAlignmentError = FlatDistance(transform.position, _alignChair.AnchorPosition);
            _alignChair = null;
            if (!player.Play(ActionIds.Sit))
            {
                // 动作层拒绝（优先级/空中守卫）→ 不留占用：椅子与碰撞立即复原
                SetHint("就座被拒：当前动作优先级更高");
                ReleaseChair();
            }
        }

        /// <summary>坐立链结束（Stand 播完 / 被打断 / Reset）→ 解除占用，椅子恢复可推、碰撞恢复。</summary>
        private void ReleaseChairWhenChainEnds()
        {
            if (_chair == null || _alignChair != null) return;
            if (player.IsLocked || player.ApplyRootMotionXZ) return;
            ReleaseChair();
        }

        private void ReleaseChair()
        {
            if (_chair == null) return;
            ChairSeat chair = _chair;
            _chair = null;
            chair.Release(_cc);
            // 角色若仍在坐面 footprint 内（例：坐姿下按 R 重置），立即恢复碰撞会把角色挤出去 → 暂缓，
            // 走出交互半径后再恢复（TickPendingCollisionRestore）。
            if (FlatDistance(transform.position, chair.SeatCenter) < chair.interactRadius)
            {
                chair.SetCollisionIgnored(_cc, true);
                _collisionPending = chair;
            }
        }

        private void TickPendingCollisionRestore()
        {
            if (_collisionPending == null) return;
            if (FlatDistance(transform.position, _collisionPending.SeatCenter) < _collisionPending.interactRadius) return;
            _collisionPending.SetCollisionIgnored(_cc, false);
            _collisionPending = null;
        }

        private void TickMove(Vector3 dir, float speed, bool run, bool jumpQueued)
        {
            // 契约 A：一次性动作（含 Down 终态）播放期间锁移动切态 → 物理位移同步锁零，防滑步
            if (player != null && player.IsLocked)
            {
                dir = Vector3.zero;
                speed = 0f;
                run = false;
                jumpQueued = false;
            }

            float dt = Time.deltaTime;
            dir = Vector3.ClampMagnitude(dir, 1f);

            bool grounded = _cc.isGrounded;
            Vector3 horizontal;
            if (grounded)
            {
                _vSpeed = -1f;
                horizontal = dir * speed;
                if (jumpQueued)
                {
                    _vSpeed = Mathf.Sqrt(2f * Mathf.Abs(gravity) * jumpHeight);
                    _airVelocity = horizontal; // 起跳保留地面速度 → 空中惯性
                }
            }
            else
            {
                Vector3 want = dir * speed;
                _airVelocity = Vector3.Lerp(_airVelocity, want, airControl * dt);
                float drag = Mathf.Clamp01(1f - airDrag * dt);
                _airVelocity *= drag;
                if (_airVelocity.sqrMagnitude < 0.0001f) _airVelocity = Vector3.zero;
                horizontal = _airVelocity;
            }

            _vSpeed += gravity * dt;
            _vSpeed = Mathf.Max(_vSpeed, -40f);

            Vector3 motion = new Vector3(horizontal.x, _vSpeed, horizontal.z);
            _cc.Move(motion * dt);

            if (!grounded && _cc.isGrounded) _vSpeed = -1f; // 落地贴地

            if (horizontal.sqrMagnitude > 0.01f)
            {
                Quaternion targetRot = Quaternion.LookRotation(horizontal.normalized, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * 10f);
            }
        }

        private void FeedPlayer()
        {
            float horizSpeed = new Vector3(_cc.velocity.x, 0f, _cc.velocity.z).magnitude;
            float speed01 = Mathf.Clamp01(horizSpeed / Mathf.Max(0.01f, runSpeed));
            player.TickLocomotion(_cc.isGrounded, speed01);

            // 根位移按状态切换（规格 §四·乙 再修正）：只有坐立三段需要 clip 的 XZ 根位移；
            // 其余词条一律 false（locomotion 的位移全由输入驱动，防"动画自己走"）。
            if (animator != null) animator.applyRootMotion = player.ApplyRootMotionXZ;

            UpdateChairStatus();
        }

        /// <summary>
        /// 施加 clip 的 **XZ 根位移**（坐立三段）。Y 丢弃——垂直由姿势承载（Y 已烘入 clip，规格 §二 修法①）；
        /// 旋转不施加——朝向由对齐段锁在椅子 forward（Sit 的 RootQ 会让角色偏航 +7.08°，实测 2026-09-13）。
        /// 实现 OnAnimatorMove 后 Unity 不再自行把 root motion 写进 transform，位移由这里全权经 CC 施加。
        /// </summary>
        private void OnAnimatorMove()
        {
            if (animator == null || !animator.applyRootMotion) return;
            if (player == null || !player.ApplyRootMotionXZ || _cc == null) return;
            Vector3 d = animator.deltaPosition;
            _cc.Move(new Vector3(d.x, 0f, d.z));
        }

        /// <summary>推椅：CharacterController 不会自己推动刚体，接触时按速度匹配施加冲量（椅子可被推开）。</summary>
        private void OnControllerColliderHit(ControllerColliderHit hit)
        {
            Rigidbody rb = hit.rigidbody;
            if (rb == null || rb.isKinematic) return;

            Vector3 move = new Vector3(hit.moveDirection.x, 0f, hit.moveDirection.z);
            if (move.sqrMagnitude < 1e-6f) return;

            float want = new Vector3(_cc.velocity.x, 0f, _cc.velocity.z).magnitude * pushImpulseScale;
            Vector3 cur = new Vector3(rb.linearVelocity.x, 0f, rb.linearVelocity.z);   // Unity 6：velocity → linearVelocity
            if (cur.magnitude >= want) return;
            rb.AddForce(move.normalized * (want - cur.magnitude) * rb.mass, ForceMode.Impulse);
        }

        private void UpdateChairStatus()
        {
            ChairSeat nearest = ChairSeat.FindNearest(transform.position, out float nd);
            if (nearest == null) { _chairStatus = "椅子: 场景里没有椅子"; return; }

            bool usable = ChairSeat.FindBest(transform.position) != null;
            _chairStatus = usable
                ? $"椅子: 可就座（锚点距离 {nd:F2} m）— 按 6"
                : $"椅子: 未命中（锚点距离 {nd:F2} m · 需 ≤ {nearest.interactRadius:F2} m 且在椅子前侧）";
            if (nearest.IsOccupied) _chairStatus = _chair != null ? "椅子: 就座中" : "椅子: 已被占用";
        }

        private void SetHint(string text)
        {
            _hint = text;
            _hintUntil = Time.time + 3f;
        }

        private static float FlatDistance(Vector3 a, Vector3 b)
            => new Vector2(a.x - b.x, a.z - b.z).magnitude;

        private static Vector3 Flat(Vector3 v) => new Vector3(v.x, 0f, v.z);

        private void SizeControllerToModel()
        {
            float h = 1.8f;
            var smr = GetComponentInChildren<SkinnedMeshRenderer>();
            if (smr != null) h = Mathf.Max(0.5f, smr.bounds.size.y);
            _cc.height = h;
            _cc.radius = Mathf.Clamp(h * 0.19f, 0.25f, 0.4f);
            _cc.center = new Vector3(0f, h * 0.5f, 0f);
            _cc.slopeLimit = 45f;
            _cc.stepOffset = 0.3f;
            // 视觉接地（2026-09-13 实测，此事由就座交互暴露）：CC 静止时 transform.y ≈ **skinWidth**
            // （默认 0.08 = 半径的 10%）→ 整个角色被抬到地面上方 80 mm：足底悬浮 **45.8 mm**，
            // 坐姿臀部因此比坐面高 **80 mm**——用户目视即"椅子不够高"（实测 hips 0.6790 vs 期望 0.5990）。
            // 规格 §四·乙 的足 IK 假定 transform 贴地（`groundY = 0` + 只上抬不下压），故此处把 skinWidth
            // 收到 0.005：transform 落到地面上，余下的毫米级足底陷入由 FootGroundingIK 逐帧抬平。
            _cc.skinWidth = 0.005f;
        }

        private Vector3 CameraRelativeDir(float h, float v)
        {
            var cam = Camera.main;
            Vector3 fwd = cam != null ? cam.transform.forward : Vector3.forward;
            Vector3 right = cam != null ? cam.transform.right : Vector3.right;
            fwd.y = 0f; right.y = 0f;
            fwd.Normalize(); right.Normalize();
            return (fwd * v + right * h).normalized;
        }

        private void OnGUI()
        {
            string actionName = player != null ? player.CurrentActionDisplay : "—";
            string hint = "WASD 移动 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 / 6坐（需走到椅子前）7起身 / R 重置";
            GUILayout.BeginArea(new Rect(12f, 12f, 560f, 110f));
            GUILayout.Label("动作: " + actionName);
            GUILayout.Label(_chairStatus);
            if (_hint != null && Time.time < _hintUntil) GUILayout.Label("⚠ " + _hint);
            GUILayout.Label(hint);
            GUILayout.EndArea();
        }
    }
}
