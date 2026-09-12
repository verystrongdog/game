// 环绕跟随相机（第三人称 RPG 式，类似博德之门/神界原罪的观察方式）
// 操作：按住鼠标右键拖拽 = 环绕角色旋转视角；滚轮 = 缩放远近；
// 相机始终注视目标（胸口高度），平滑跟随。移动输入仍走"相对相机"（见 AnimatorWalker），
// 因此旋转视角后 WASD 的前进方向会跟着相机朝向变化。
using UnityEngine;

namespace YANTF.WalkerLab
{
    /// <summary>
    /// 环绕相机：目标角色 + 轨道（yaw/pitch/距离）。右键拖拽转视角、滚轮缩放。
    /// 用途：KiWalkerLab 演示中自由观察角色的坐/起动画与行走。
    /// 手感参数（rotateSpeed/zoomSpeed）可在 Inspector 中随时微调。
    /// </summary>
    public sealed class CameraOrbit : MonoBehaviour
    {
        [Header("目标与轨道")]
        [Tooltip("跟随目标（角色）")]
        public Transform target;
        [Tooltip("相机到注视点的距离 m")]
        public float distance = 6f;
        [Tooltip("初始水平角 deg（0=角色正后方）")]
        public float yaw = 0f;
        [Tooltip("初始俯仰角 deg（>0 从上方俯视）")]
        public float pitch = 22f;
        [Tooltip("注视点相对目标脚底的高度 m（约胸口）")]
        public float lookHeight = 1.2f;

        [Header("范围与手感")]
        [Tooltip("最近距离 m")]
        public float minDistance = 1.5f;
        [Tooltip("最远距离 m")]
        public float maxDistance = 14f;
        [Tooltip("俯仰角下限 deg")]
        public float minPitch = -20f;
        [Tooltip("俯仰角上限 deg（接近垂直俯视）")]
        public float maxPitch = 85f;
        [Tooltip("右键拖拽旋转灵敏度 deg/轴单位（约 100px 拖拽 ≈ 20°；觉得慢可调大）")]
        public float rotateSpeed = 2.0f;
        [Tooltip("滚轮缩放速度 m/格（约 1 格 ≈ 0.8m）")]
        public float zoomSpeed = 8f;
        [Tooltip("跟随平滑系数（越大越跟手）")]
        public float followSmooth = 14f;

        private Vector3 _desiredPos;

        private void Start()
        {
            if (target == null) target = transform; // 兜底：无目标时原地自转（调试用）
            Snap();
        }

        private void Update()
        {
            // 右键拖拽：环绕（Yaw 水平转、Pitch 俯仰转）
            if (Input.GetMouseButton(1))
            {
                yaw += Input.GetAxis("Mouse X") * rotateSpeed;
                pitch -= Input.GetAxis("Mouse Y") * rotateSpeed;
                pitch = Mathf.Clamp(pitch, minPitch, maxPitch);
            }

            // 滚轮：缩放距离
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.0001f)
            {
                distance = Mathf.Clamp(distance - scroll * zoomSpeed, minDistance, maxDistance);
            }

            // 目标可能被销毁/切换：脱落后停止
            if (target == null) return;

            Vector3 lookAt = target.position + Vector3.up * lookHeight;
            Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
            _desiredPos = lookAt + orbit * Vector3.back * distance;
        }

        private void LateUpdate()
        {
            if (target == null) return;
            Vector3 lookAt = target.position + Vector3.up * lookHeight;
            float t = 1f - Mathf.Exp(-followSmooth * Time.deltaTime);
            transform.position = Vector3.Lerp(transform.position, _desiredPos, t);
            transform.rotation = Quaternion.LookRotation(lookAt - transform.position);
        }

        /// <summary>立即把相机放到目标轨道位置（测试/初始化用）。</summary>
        public void Snap()
        {
            if (target == null) return;
            Vector3 lookAt = target.position + Vector3.up * lookHeight;
            Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
            _desiredPos = lookAt + orbit * Vector3.back * distance;
            transform.position = _desiredPos;
            transform.rotation = Quaternion.LookRotation(lookAt - transform.position);
        }

        /// <summary>程序化旋转（测试/手柄预留）：dyaw/dpitch 为增量角度。</summary>
        public void RotateBy(float dyaw, float dpitch)
        {
            yaw += dyaw;
            pitch = Mathf.Clamp(pitch - dpitch, minPitch, maxPitch);
        }

        /// <summary>程序化缩放（测试/手柄预留）。</summary>
        public void ZoomBy(float delta)
        {
            distance = Mathf.Clamp(distance + delta, minDistance, maxDistance);
        }
    }
}
