// 动画驱动移动沙盘 — Humanoid 模型 + Animator 播放入库动作（Kevin Iglesias Human Basic Motions）
// 与几何体 Walker 对照：此组件用 Animator 播放 Idle/Walk/Run/Jump 真人动画，
// 位移仍由 CharacterController 计算（非 RootMotion，见 README 已知简化）。
// AnimatorController 由 Editor 场景生成器构建（4 状态：Idle/Walk/Run/Jump），本组件只管切态。
using UnityEngine;

namespace YANTF.WalkerLab
{
    /// <summary>
    /// Animator + CharacterController 走/跑/跳。
    /// 输入：WASD/方向键移动、Shift 奔跑、Space 跳跃；移动方向相对相机。
    /// 动画状态由水平速度 + 落地状态决定：Idle/Walk/Run 循环，跳跃一次性播放。
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public sealed class AnimatorWalker : MonoBehaviour
    {
        [Header("移动参数（演示常量，非正典数值）")]
        [Tooltip("行走速度 m/s")]
        public float walkSpeed = 3.0f;
        [Tooltip("奔跑速度 m/s")]
        public float runSpeed = 6.0f;
        [Tooltip("跳跃初速抬升高度 m（v = sqrt(2 g h)）")]
        public float jumpHeight = 1.4f;
        [Tooltip("重力 m/s^2（向下）")]
        public float gravity = -22f;
        [Tooltip("空中方向修正系数 0..1（0=完全惯性不可控，1=空中满速跟手）")]
        public float airControl = 0.15f;
        [Tooltip("空中水平速度衰减 /s（0=无衰减）")]
        public float airDrag = 0.5f;

        [Header("引用（Editor 场景生成器注入）")]
        public Animator animator;

        // ---- 运行时状态 ----
        public bool IsGrounded => _cc != null && _cc.isGrounded;
        public float HorizontalSpeed { get; private set; }
        public bool IsRunning { get; private set; }
        public string CurrentAnimState { get; private set; } = "Idle";

        private CharacterController _cc;
        private float _vSpeed;
        private bool _jumpAnimStarted;
        private Vector3 _airVelocity;   // 空中水平速度（起跳惯性 + 弱修正）

        // 测试/脚本驱动
        private Vector3 _scriptDir;
        private float _scriptSpeed;
        private bool _scriptRun;
        private bool _scriptJumpQueued;

        private void Awake()
        {
            _cc = GetComponent<CharacterController>();
            if (animator == null) animator = GetComponent<Animator>();
            float h = EstimateHeight();
            _cc.height = h;
            _cc.radius = Mathf.Clamp(h * 0.19f, 0.25f, 0.4f);
            _cc.center = new Vector3(0f, h * 0.5f, 0f);
            _cc.slopeLimit = 45f;
            _cc.stepOffset = 0.3f;
        }

        /// <summary>脚本/测试驱动：给定移动方向（世界水平向）、速度与奔跑/跳跃标记。</summary>
        public void SetMoveInput(Vector3 worldDir, float speed, bool run, bool jump)
        {
            _scriptDir = worldDir;
            _scriptSpeed = speed;
            _scriptRun = run;
            if (jump) _scriptJumpQueued = true;
        }

        private void Update()
        {
            if (_cc == null) return;

            Vector3 dir = _scriptDir;
            float speed = _scriptSpeed;
            bool run = _scriptRun;
            bool jumpQueued = _scriptJumpQueued;
            _scriptJumpQueued = false;

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

            TickMove(dir, speed, run, jumpQueued);
        }

        private void TickMove(Vector3 dir, float speed, bool run, bool jumpQueued)
        {
            float dt = Time.deltaTime;
            dir = Vector3.ClampMagnitude(dir, 1f);

            bool grounded = _cc.isGrounded;
            Vector3 horizontal;
            if (grounded)
            {
                // 落地：水平速度直接由键盘/脚本输入驱动（全速可控）
                _vSpeed = -1f;
                horizontal = dir * speed;
                if (jumpQueued)
                {
                    _vSpeed = Mathf.Sqrt(2f * Mathf.Abs(gravity) * jumpHeight);
                    _jumpAnimStarted = false;
                    // 起跳：水平保留当前地面速度 → 空中惯性
                    _airVelocity = horizontal;
                }
                IsRunning = run && horizontal.sqrMagnitude > 0.01f;
            }
            else
            {
                // 空中：仅惯性 + 轻微方向修正，避免"按住方向键跳跃=平移"
                Vector3 want = dir * speed;
                _airVelocity = Vector3.Lerp(_airVelocity, want, airControl * dt);
                float drag = Mathf.Clamp01(1f - airDrag * dt);
                _airVelocity *= drag;
                if (_airVelocity.sqrMagnitude < 0.0001f) _airVelocity = Vector3.zero;
                horizontal = _airVelocity;
                IsRunning = false;
            }

            _vSpeed += gravity * dt;
            _vSpeed = Mathf.Max(_vSpeed, -40f);

            Vector3 motion = new Vector3(horizontal.x, _vSpeed, horizontal.z);
            _cc.Move(motion * dt);
            HorizontalSpeed = new Vector3(_cc.velocity.x, 0f, _cc.velocity.z).magnitude;

            if (horizontal.sqrMagnitude > 0.01f)
            {
                Quaternion targetRot = Quaternion.LookRotation(horizontal.normalized, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * 10f);
            }

            UpdateAnimState();
        }

        private void UpdateAnimState()
        {
            if (animator == null) return;
            bool airborne = !_cc.isGrounded;

            string target;
            if (airborne)
            {
                target = "Jump";
                // Jump 非循环：只触发一次，播完定格末帧；落地后切回地面状态
                if (!_jumpAnimStarted)
                {
                    _jumpAnimStarted = true;
                    animator.CrossFade("Jump", 0.06f);
                }
                return; // 空中不再改写状态
            }

            _jumpAnimStarted = false;
            if (HorizontalSpeed < 0.4f) target = "Idle";
            else if (HorizontalSpeed < (walkSpeed + runSpeed) * 0.5f) target = "Walk";
            else target = "Run";

            if (target != CurrentAnimState)
            {
                CurrentAnimState = target;
                animator.CrossFade(target, 0.12f);
            }
        }

        private float EstimateHeight()
        {
            var smr = GetComponentInChildren<SkinnedMeshRenderer>();
            if (smr != null) return Mathf.Max(0.5f, smr.bounds.size.y);
            return 1.8f;
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
    }
}
