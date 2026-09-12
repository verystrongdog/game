// 椅子就座点（YANTF.WalkerLab）
// 挂在"椅子座位"的锚点上：transform.position = 坐姿臀部落点在地面的投影（y≈0），
// transform.forward = 椅子正面朝向（= 角色坐下后胸口朝向）。
// 参数取自 Mixamo StandToSit/SitToStand 实测（2026-09-07，见 KiWalkerLabBuilder 注释）：
//   起点与臀部落点水平差 ≈ 0.49m（沿 forward），坐姿臀高 0.525 → 坐面高 ≈ 0.465。
using UnityEngine;

namespace YANTF.WalkerLab
{
    /// <summary>
    /// 椅子就座锚点。角色站到 <see cref="ApproachPosition"/>（椅子前方 0.49m）、
    /// 面向 <see cref="transform.forward"/> 后按 E，AnimatorWalker 会吸附到就座起点并
    /// 用 clip root motion 把角色送入坐姿。数值按本包角色比例实测，换模型需重测。
    /// </summary>
    public sealed class SitPoint : MonoBehaviour
    {
        [Header("就座几何（Mixamo 实测默认值）")]
        [Tooltip("就座起点到臀部落点的水平距离 m（沿 forward 前方为椅子）")]
        [SerializeField] private float approachDistance = 0.49f;
        [Tooltip("坐面高度 m（只用于 Gizmo 可视化，逻辑不依赖）")]
        [SerializeField] private float seatHeight = 0.465f;
        [Tooltip("就座整体抬高量 m：修正坐姿脚部轻微陷入地面（椅子需同量加高）")]
        [SerializeField] private float poseRaise = 0.04f;
        [Tooltip("触发半径 m：角色与就座起点水平距离小于此值才响应 E")]
        [SerializeField] private float interactRadius = 0.55f;
        [Tooltip("朝向要求：角色 forward 与椅子 forward 点积 >= 此值才响应 E（1=必须正对）")]
        [SerializeField] private float facingDotMin = 0.35f;

        public Vector3 ApproachPosition => transform.position + transform.forward * approachDistance;
        public float PoseRaise => poseRaise;
        public Quaternion ApproachRotation => transform.rotation;

        /// <summary>在世界中找"可就座"的 SitPoint：距玩家 ≤ interactRadius 且朝向达标，返回最近者。</summary>
        public static SitPoint FindBest(Vector3 playerPos, Vector3 playerForward)
        {
            SitPoint best = null;
            float bestDist = float.MaxValue;
            foreach (var sp in FindObjectsByType<SitPoint>(FindObjectsSortMode.None))
            {
                Vector3 ap = sp.ApproachPosition;
                float dist = Vector3.Distance(playerPos, ap);
                if (dist > sp.interactRadius) continue;
                float dot = Vector3.Dot(playerForward.normalized, sp.transform.forward);
                if (dot < sp.facingDotMin) continue;
                if (dist < bestDist)
                {
                    bestDist = dist;
                    best = sp;
                }
            }
            return best;
        }

        private void OnDrawGizmosSelected()
        {
            var ap = ApproachPosition;
            Gizmos.color = new Color(0.2f, 1f, 0.4f, 0.9f);
            Gizmos.DrawWireSphere(ap, 0.12f);
            Gizmos.DrawRay(ap, transform.forward * 0.5f);
            Gizmos.color = new Color(1f, 0.8f, 0.2f, 0.6f);
            Gizmos.DrawWireSphere(transform.position, interactRadius);

            // 坐面示意线（臀部应落在椅子上）
            Gizmos.color = new Color(0.9f, 0.5f, 0.2f, 0.8f);
            Vector3 seat = transform.position + Vector3.up * seatHeight;
            Gizmos.DrawWireCube(seat, new Vector3(0.6f, 0.04f, 0.6f));
        }
    }
}
