// 大脑视图（YANTF.BrainView）— 观察方式：**转模型本身**，相机固定
//
// 为什么不是相机绕行（#146 的原始做法，owner 2026-09-13 反馈后改）：
//   相机绕行会同时改变朝向与背景，盯住某个脑区时方位感难建立；模型自转时观察者始终在同一侧，
//   空间关系稳定。后续玩法面要在脑区上点选，这个手感会被继承。
//
// 结构（为什么自转要挂在外层包装对象上，而不是 BrainViewRig 上）：
//   Spin（本组件，identity + 用户 yaw/pitch）
//     └─ BrainView（BrainViewRig：**资产基线 −90° X** + 等比 1/90）
//          ├─ BrainShell / Links
//   自转若直接加在 BrainViewRig 上，就会与"资产躺着→立起"的基线旋转复合在一个 transform 里，
//   既难读也难验（分不清哪部分是资产口径、哪部分是观察角）。分开后：包装对象只表达**观察角**，
//   且在包装对象的局部轴 = 世界轴上旋转 → 水平拖动稳定地绕世界 Y、垂直拖动稳定地绕世界 X。
//
// 输入口径与 CameraOrbit 一致（旧版 Input；ProjectSettings.activeInputHandler = 0）：
//   右键拖动 / 滚轮 / R 复位。数值来源：design/presentation/visualization-3d/3D可视化设计规范.md §四.1
using UnityEngine;

namespace YANTF.BrainView
{
    public class BrainViewSpin : MonoBehaviour
    {
        /// <summary>拖动灵敏度（度/单位轴量）。来源：3D可视化设计规范 §四.1「鼠标拖动绕树旋转」的呈现层取值。</summary>
        [SerializeField] private float dragSpeed = 4.5f;

        /// <summary>俯仰夹取：防止转到上下颠倒后失去方向感。</summary>
        [SerializeField] private float minPitch = -85f;
        [SerializeField] private float maxPitch = 85f;

        /// <summary>缩放：改**相机距离**而不是模型缩放（后者会同时放大脑区间距，观感不同）。</summary>
        [SerializeField] private float zoomSpeed = 12f;
        [SerializeField] private float minDistance = 1.2f;
        [SerializeField] private float maxDistance = 12f;

        [SerializeField] private Camera targetCamera;
        [SerializeField] private KeyCode resetKey = KeyCode.R;

        private float _yaw;
        private float _pitch;
        private float _distance;

        public float Yaw => _yaw;
        public float Pitch => _pitch;
        public float Distance => _distance;

        /// <summary>俯仰夹取（**纯函数**，用例可直接判；不依赖任何场景状态）。</summary>
        public static float ClampPitch(float pitch, float min, float max)
        {
            return Mathf.Clamp(pitch, min, max);
        }

        /// <summary>观察角 → 旋转。绕世界 Y 的偏航 + 绕世界 X 的俯仰（顺序固定，故可断言）。</summary>
        public static Quaternion ObservationRotation(float yaw, float pitch)
        {
            return Quaternion.Euler(pitch, yaw, 0f);
        }

        public void Bind(Camera cam, float initialDistance)
        {
            targetCamera = cam;
            _distance = initialDistance;
            Apply();
        }

        private void Awake()
        {
            if (_distance <= 0f) _distance = targetCamera != null ? Vector3.Distance(targetCamera.transform.position, transform.position) : 3f;
        }

        private void Update()
        {
            if (Input.GetKeyDown(resetKey)) ResetView();

            if (Input.GetMouseButton(1))
            {
                _yaw += Input.GetAxis("Mouse X") * dragSpeed;
                _pitch = ClampPitch(_pitch - Input.GetAxis("Mouse Y") * dragSpeed, minPitch, maxPitch);
            }

            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.0001f)
                _distance = Mathf.Clamp(_distance - scroll * zoomSpeed, minDistance, maxDistance);

            Apply();
        }

        /// <summary>以代码设定观察角与距离（builder / 断言用）。
        /// ⚠️ 为什么需要它：本工程的输入是**旧版 Input**（`activeInputHandler: 0`），而 Unity 的
        /// `simulate_pointer` **只支持新输入系统**（实测报 "Legacy input injection is not supported."），
        /// 故"拖动 → 角度"这一段**无法机器注入验证**，只能目视。可机器验证的是本方法之后的链路：
        /// 角度 → 变换 → 相机是否真的不动。</summary>
        public void SetView(float yaw, float pitch, float distance)
        {
            _yaw = yaw;
            _pitch = ClampPitch(pitch, minPitch, maxPitch);
            _distance = Mathf.Clamp(distance, minDistance, maxDistance);
            Apply();
        }

        public void ResetView()
        {
            _yaw = 0f;
            _pitch = 0f;
            _distance = Mathf.Clamp(_distance, minDistance, maxDistance);
            Apply();
        }

        private void Apply()
        {
            transform.localRotation = ObservationRotation(_yaw, _pitch);
            if (targetCamera == null) return;
            // 相机固定朝向模型中心，只沿其本地 -Z 后退/前进（缩放）
            var dir = targetCamera.transform.rotation * Vector3.back;
            targetCamera.transform.position = transform.position + dir * _distance;
        }
    }
}
