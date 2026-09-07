// 移动实验沙盘 — 几何体白盒人体 + 实时走/跑/跳控制器（Grilling #122 之外的呈现验证载体）
// 与回合战斗沙盘（DemoCombatDriver）解耦：此组件演示"自由移动"层（locomotion），
// 供 3D 技能树/空间呈现验证走位手感；不触碰回合结算/态度等引擎口径。
// 仅用 Unity 图元（Capsule/Sphere）拼装，零外部资产；骨骼引用由 BuildBody 建立。
using UnityEngine;

namespace YANTF.WalkerLab
{
    /// <summary>
    /// 几何体人体 + CharacterController 移动。
    /// 输入：WASD/方向键移动、LeftShift 奔跑、Space 跳跃；移动方向相对相机水平朝向。
    /// 程序动画按速度摆臂摆腿（Walk 幅度小频率低，Run 幅度大频率高），空中收腿姿态。
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public sealed class WalkerController : MonoBehaviour
    {
        [Header("移动参数（演示常量，非正典数值）")]
        [Tooltip("行走速度 m/s")]
        public float walkSpeed = 3.2f;
        [Tooltip("奔跑速度 m/s（与行走区分：≥1.6×行走）")]
        public float runSpeed = 6.4f;
        [Tooltip("跳跃初速对应的抬升高度 m（v = sqrt(2 g h)）")]
        public float jumpHeight = 1.5f;
        [Tooltip("重力加速度 m/s^2（向下）")]
        public float gravity = -22f;
        [Tooltip("空中转向灵敏度系数")]
        public float airTurnFactor = 0.35f;

        [Header("相机跟随（可关）")]
        public bool followCamera = true;
        public Vector3 cameraOffset = new Vector3(0f, 2.6f, -5.6f);
        public float cameraLerp = 8f;

        // ---- 运行时状态 ----
        public bool IsGrounded => _cc != null && _cc.isGrounded;
        public float HorizontalSpeed { get; private set; }
        public bool IsRunning { get; private set; }
        public bool IsAirborne { get; private set; }

        private CharacterController _cc;
        private float _vSpeed;          // 垂直速度（重力/跳跃积分）
        private Transform _hips;        // 髋部根（身体朝向 / 程序动画根）
        private Transform _armL, _armR, _legL, _legR;
        private Color _tint = new Color(0.55f, 0.7f, 1f, 1f);
        private float _airTime;

        // ---- 测试/脚本驱动输入（SetMoveInput），供 PlayMode 冒烟测试与未来 AI 驱动 ----
        private Vector3 _scriptDir;
        private float _scriptSpeed;
        private bool _scriptRun;
        private bool _scriptJumpQueued;

        private static readonly Quaternion IdleArmL = Quaternion.Euler(4f, 0f, -6f);
        private static readonly Quaternion IdleArmR = Quaternion.Euler(4f, 0f, 6f);

        private void Awake()
        {
            _cc = GetComponent<CharacterController>();
            // 统一碰撞胶囊口径：高 1.85m 覆盖人体（脚底≈transform.position.y 贴地）
            _cc.height = 1.85f;
            _cc.radius = 0.35f;
            _cc.center = new Vector3(0f, 0.92f, 0f);
            _cc.slopeLimit = 45f;
            _cc.stepOffset = 0.3f;
        }

        // ============ 对外接口 ============

        /// <summary>构建几何体人体骨架（幂等：先清空已有子物体）。Editor 场景生成器与运行时皆可调用。</summary>
        public void BuildBody(Color tint)
        {
            _tint = tint;
            foreach (Transform child in transform)
            {
                if (Application.isPlaying) Destroy(child.gameObject);
                else DestroyImmediate(child.gameObject);
            }

            // 尺寸口径：总高 ~1.8m（对齐 CharacterVisual 白盒），单位米
            float hipH = 0.95f;
            var mat = MakeMat(tint);

            _hips = new GameObject("hips").transform;
            _hips.SetParent(transform, false);
            _hips.localPosition = new Vector3(0f, hipH, 0f);

            // 躯干（Capsule 以髋为底座向上半段）
            var torso = MakePrimitive(PrimitiveType.Capsule, "torso", mat, new Vector3(0.36f, 0.3f, 0.22f));
            torso.SetParent(_hips, false);
            torso.localPosition = new Vector3(0f, 0.34f, 0f);

            // 头
            var head = MakePrimitive(PrimitiveType.Sphere, "head", MakeMat(Lighten(tint, 0.15f)), Vector3.one * 0.2f);
            head.SetParent(_hips, false);
            head.localPosition = new Vector3(0f, 0.95f, 0f);

            // 四肢：枢轴放在关节处，图元向远端偏移 → 摆动绕关节
            _armR = MakeLimb("armR", mat, new Vector3(0.26f, 0.78f, 0f), new Vector3(0.09f, 0.34f, 0.09f));
            _armL = MakeLimb("armL", mat, new Vector3(-0.26f, 0.78f, 0f), new Vector3(0.09f, 0.34f, 0.09f));
            _legR = MakeLimb("legR", mat, new Vector3(0.12f, -0.13f, 0f), new Vector3(0.11f, 0.4f, 0.11f));
            _legL = MakeLimb("legL", mat, new Vector3(-0.12f, -0.13f, 0f), new Vector3(0.11f, 0.4f, 0.11f));

            ApplyPose(Quaternion.identity, IdleArmL, IdleArmR, Quaternion.identity, Quaternion.identity);
        }

        /// <summary>脚本/测试驱动：给定移动方向（世界水平向）、速度 m/s 与奔跑/跳跃标记。</summary>
        public void SetMoveInput(Vector3 worldDir, float speed, bool run, bool jump)
        {
            _scriptDir = worldDir;
            _scriptSpeed = speed;
            _scriptRun = run;
            if (jump) _scriptJumpQueued = true;
        }

        // ============ 生命周期 ============

        private void Update()
        {
            if (_cc == null) return;

            // 键盘输入（旧 Input Manager；工程设置启用 Active Input Handling=旧版见 README）
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

        private void LateUpdate()
        {
            if (!followCamera) return;
            var cam = Camera.main;
            if (cam == null) return;
            Vector3 target = transform.position + cameraOffset;
            cam.transform.position = Vector3.Lerp(cam.transform.position, target, Time.deltaTime * cameraLerp);
            cam.transform.LookAt(transform.position + Vector3.up * 1.2f);
        }

        // ============ 移动/动画核心 ============

        private void TickMove(Vector3 dir, float speed, bool run, bool jumpQueued)
        {
            float dt = Time.deltaTime;
            dir = Vector3.ClampMagnitude(dir, 1f);

            bool grounded = _cc.isGrounded;
            if (grounded)
            {
                _vSpeed = -1f; // 轻微贴地
                _airTime = 0f;
                if (jumpQueued)
                {
                    _vSpeed = Mathf.Sqrt(2f * Mathf.Abs(gravity) * jumpHeight);
                    IsAirborne = true;
                }
                else IsAirborne = false;
            }
            else
            {
                _airTime += dt;
                IsAirborne = true;
            }

            _vSpeed += gravity * dt;
            _vSpeed = Mathf.Max(_vSpeed, -40f);

            // 移动：水平方向 + 垂直速度
            Vector3 horizontal = dir * speed;
            IsRunning = run && horizontal.sqrMagnitude > 0.01f && grounded;

            Vector3 motion = new Vector3(horizontal.x, _vSpeed, horizontal.z);
            _cc.Move(motion * dt);

            HorizontalSpeed = new Vector3(_cc.velocity.x, 0f, _cc.velocity.z).magnitude;

            // 朝向：水平移动方向平滑转向
            if (horizontal.sqrMagnitude > 0.01f)
            {
                float turnFactor = grounded ? 1f : airTurnFactor;
                Quaternion targetRot = Quaternion.LookRotation(horizontal.normalized, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, Time.deltaTime * 10f * turnFactor);
            }

            UpdatePose();
        }

        private void UpdatePose()
        {
            if (_hips == null) return;

            Quaternion body = Quaternion.identity;
            Quaternion aL = IdleArmL, aR = IdleArmR;
            Quaternion lL = Quaternion.identity, lR = Quaternion.identity;

            if (IsAirborne)
            {
                // 空中：收腿屈膝姿态，双臂略展平衡
                float k = Mathf.Clamp01(_airTime * 1.5f);
                lL = Quaternion.Euler(28f * k, 0f, 4f);
                lR = Quaternion.Euler(28f * k, 0f, -4f);
                aL = Quaternion.Euler(-20f * k, 0f, -25f * k);
                aR = Quaternion.Euler(-20f * k, 0f, 25f * k);
            }
            else if (HorizontalSpeed > 0.15f)
            {
                // 走/跑摆臂摆腿：频率随速度上升；幅度跑 > 走
                float s = Mathf.Clamp01(HorizontalSpeed / runSpeed);
                float freq = 0.9f + 0.6f * s;             // 一个完整周期=左右各一步；走 ~1.2Hz、跑 ~1.5Hz
                float ph = Time.time * freq * Mathf.PI * 2f;
                float legAmp = (18f + 26f * s) * Mathf.Deg2Rad;
                float armAmp = (22f + 30f * s) * Mathf.Deg2Rad;
                // 腿与对侧臂同相（人形步态）
                lL = Quaternion.Euler(Mathf.Sin(ph) * legAmp * Mathf.Rad2Deg, 0f, 0f);
                lR = Quaternion.Euler(Mathf.Sin(ph + Mathf.PI) * legAmp * Mathf.Rad2Deg, 0f, 0f);
                aR = Quaternion.Euler(Mathf.Sin(ph) * armAmp * Mathf.Rad2Deg, 0f, 8f);
                aL = Quaternion.Euler(Mathf.Sin(ph + Mathf.PI) * armAmp * Mathf.Rad2Deg, 0f, -8f);
                body = Quaternion.Euler(0f, 0f, Mathf.Sin(ph * 2f) * 1.5f * s); // 轻微身体侧摆
            }
            else
            {
                // Idle：呼吸微动
                float breathe = Mathf.Sin(Time.time * 2.2f) * 0.6f;
                aL = Quaternion.Euler(IdleArmL.eulerAngles.x + breathe, 0f, IdleArmL.eulerAngles.z);
                aR = Quaternion.Euler(IdleArmR.eulerAngles.x + breathe, 0f, IdleArmR.eulerAngles.z);
            }

            ApplyPose(body, aL, aR, lL, lR);
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

        // ============ 骨骼构建工具 ============

        /// <summary>关节枢轴（空节点）+ 向远端偏移的图元：旋转枢轴即绕关节摆动。</summary>
        private Transform MakeLimb(string name, Material mat, Vector3 jointPos, Vector3 limbScale)
        {
            var joint = new GameObject(name).transform;
            joint.SetParent(_hips, false);
            joint.localPosition = jointPos;
            // 图元中心放到 limb 中点（关节 + 半长向下）
            var limb = MakePrimitive(PrimitiveType.Capsule, name + "_mesh", mat, limbScale);
            limb.SetParent(joint, false);
            limb.localPosition = new Vector3(0f, -limbScale.y, 0f);
            return joint;
        }

        private void ApplyPose(Quaternion body, Quaternion aL, Quaternion aR, Quaternion lL, Quaternion lR)
        {
            _hips.localRotation = Quaternion.Slerp(_hips.localRotation, body, 10f * Time.deltaTime);
            _armL.localRotation = Quaternion.Slerp(_armL.localRotation, aL, 12f * Time.deltaTime);
            _armR.localRotation = Quaternion.Slerp(_armR.localRotation, aR, 12f * Time.deltaTime);
            _legL.localRotation = Quaternion.Slerp(_legL.localRotation, lL, 12f * Time.deltaTime);
            _legR.localRotation = Quaternion.Slerp(_legR.localRotation, lR, 12f * Time.deltaTime);
        }

        private static Transform MakePrimitive(PrimitiveType type, string name, Material mat, Vector3 scale)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.localScale = scale;
            var col = go.GetComponent<Collider>();
            if (col != null)
            {
                if (Application.isPlaying) Object.Destroy(col);
                else Object.DestroyImmediate(col);
            }
            var r = go.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = mat;
            return go.transform;
        }

        private static Material MakeMat(Color c)
        {
            var shader = Shader.Find("Standard");
            var mat = new Material(shader != null ? shader : Shader.Find("Diffuse"));
            if (mat.HasProperty("_Color")) mat.color = c;
            return mat;
        }

        private static Color Lighten(Color c, float f)
        {
            return new Color(c.r + f, c.g + f, c.b + f, c.a);
        }
    }
}
