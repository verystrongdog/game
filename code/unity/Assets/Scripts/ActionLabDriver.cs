// ActionLab 场景驱动 — CharacterController 物理 + 输入 → ActionPlayer（动作词表 12 词条演示场）
// 位移口径同 KiWalkerLab（AnimatorWalker）：CC 移动（无 RootMotion），动画状态由 ActionPlayer 决定。
// 按键：WASD/方向键 走位（相机相对）、Shift 跑、Space 跳（locomotion 空中态）；
//       1物攻 2精攻 3防御(再按退出) 4受击 5倒下 6坐 7起身（动作键）、R 重置（Down 终态后）。
// HUD：IMGUI 顶部显示当前动作名（目视清单 ② 验收项）。
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
            // 7 加输入层守卫：起身 clip 首帧就是坐姿，站姿下硬播会看到"瞬蹲再起"。
            // 动作层 ActionPlayer.Play() 不设该守卫——那层保持"按键即播"的宽松口径（规格 §四·甲）。
            if (Input.GetKeyDown(KeyCode.Alpha6)) player.Play(ActionIds.Sit);
            if (Input.GetKeyDown(KeyCode.Alpha7) && player.CurrentActionId == ActionIds.SitIdle)
                player.Play(ActionIds.Stand);
            if (Input.GetKeyDown(KeyCode.R)) player.ResetToIdle();
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
        }

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
            string hint = "WASD 移动 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 6坐 7起身 / R 重置";
            GUILayout.BeginArea(new Rect(12f, 12f, 420f, 80f));
            GUILayout.Label("动作: " + actionName);
            GUILayout.Label(hint);
            GUILayout.EndArea();
        }
    }
}
