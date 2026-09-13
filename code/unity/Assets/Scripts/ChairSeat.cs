// 椅子（YANTF.ActionLab）— 就座交互的场景件：**实时**就座锚点 + 占用锁 + 碰撞忽略开关
//
// 为什么不是烘死的常量：原实现把凳子摆在「角色 transform 在原点」时实测的落点正下方
// （旧常量 StoolCenterZ = −0.104），于是"坐在椅子上"只在出生点成立，走开一步再按 6 就坐在空气里。
// 本组件把落点**从椅子当前的 transform 求出来**：搬动/推开椅子后锚点自动跟随。
//
// 数值来源：design/presentation/动作库规格.md
//   §四·丁 就座锚点距离 0.423 m（= Sit 段根位移 0.3201 + 姿势内髋后移 0.103，2026-09-13 直驱实测）
//   §四·丁 就座交互半径 0.25 m（≥ 贴椅残差 0.099；同时是对齐位移的上界）
//   §七    坐面高 0.4449 m（坐姿网格实测，仅用于 Gizmo 与场景件摆位）
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 椅子就座锚点。transform 位置 = **坐面中心在地面的投影**，transform.forward = 椅子正面朝向
    /// （= 角色坐下后胸口朝向），与 WalkerLab 的 <see cref="YANTF.WalkerLab.SitPoint"/> 同约定。
    ///
    /// 就座锚点 = transform.position + forward × <see cref="anchorDistance"/>：角色必须站到那里，
    /// 播 Sit 时 clip 的 XZ 根位移（0.3201 m）才会把臀部送到坐面正上方。
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public sealed class ChairSeat : MonoBehaviour
    {
        [Header("就座几何（来源：动作库规格.md §四·丁 / §七）")]
        [Tooltip("坐面中心 → 就座锚点的水平距离 m（实测 0.423：Sit 段根位移 + 姿势内髋后移）")]
        public float anchorDistance = 0.423f;
        [Tooltip("交互半径 m：角色到锚点的水平距离 ≤ 此值才判定「找到」（同时对应对齐位移上界）")]
        public float interactRadius = 0.25f;
        [Tooltip("坐面高 m（仅 Gizmo 可视化；逻辑不依赖——坐面几何在场景件里）")]
        public float seatTopY = 0.4449f;

        /// <summary>交互半径的规格默认值（规格 §四·丁 / §七）：提示文本与断言引用它，避免各处硬编码。</summary>
        public const float DefaultInteractRadius = 0.25f;
        /// <summary>就座锚点距离的规格默认值（实测 0.423 m）。</summary>
        public const float DefaultAnchorDistance = 0.423f;

        /// <summary>占用态：`Sit` → `SitIdle` → `Stand` 全程为真（规格 §四·丁#6）。</summary>
        public bool IsOccupied { get; private set; }

        public Rigidbody Body => _body != null ? _body : (_body = GetComponent<Rigidbody>());

        /// <summary>坐面中心（地面投影）。</summary>
        public Vector3 SeatCenter => transform.position;
        /// <summary>椅子正面朝向 = 坐下后角色胸口朝向。</summary>
        public Vector3 Forward => transform.forward;
        /// <summary>就座锚点：角色必须站到这里，坐下后臀部才落在坐面上。</summary>
        public Vector3 AnchorPosition => transform.position + transform.forward * anchorDistance;

        private Rigidbody _body;
        private Collider[] _colliders;

        private void Awake()
        {
            _body = GetComponent<Rigidbody>();
            _colliders = GetComponentsInChildren<Collider>(true);
        }

        /// <summary>角色到就座锚点的**水平**距离 m（垂直方向不参与判定）。</summary>
        public float AnchorDistanceTo(Vector3 worldPos)
        {
            Vector3 a = AnchorPosition;
            return new Vector2(worldPos.x - a.x, worldPos.z - a.z).magnitude;
        }

        /// <summary>角色是否位于椅子**前侧**（坐面中心 → 角色的水平向量与 forward 同向）。</summary>
        public bool IsInFront(Vector3 worldPos)
        {
            Vector3 d = worldPos - transform.position;
            return Vector3.Dot(new Vector3(d.x, 0f, d.z), new Vector3(transform.forward.x, 0f, transform.forward.z)) > 0f;
        }

        /// <summary>本椅子此刻是否"可坐"（判定纯函数，见 <see cref="IsUsable"/>）。</summary>
        public bool IsUsableNow(Vector3 worldPos, out float distance)
            => IsUsable(transform.position, transform.forward, anchorDistance, interactRadius, worldPos, IsOccupied, out distance);

        /// <summary>
        /// 判定纯函数（无场景依赖，PlayMode 断言直接调它）：「找到椅子」= 三条件同时成立——
        /// ① 到锚点水平距离 ≤ interactRadius；② 角色在椅子前侧；③ 椅子空闲。
        /// 规格 §四·丁#2。**朝向不参与判定**——驱动层每帧把角色转向移动方向，锚点在椅子正面一侧，
        /// 玩家走到那里必然"面朝椅子"（点积 ≈ −1），故原 SitPoint 的 facingDotMin 口径在此不可达；
        /// 朝向由对齐段（0.25 s 转身就位）负责。
        /// </summary>
        public static bool IsUsable(Vector3 seatCenter, Vector3 forward, float anchorDistance, float interactRadius,
                                    Vector3 worldPos, bool occupied, out float distance)
        {
            Vector3 anchor = seatCenter + forward * anchorDistance;
            distance = new Vector2(worldPos.x - anchor.x, worldPos.z - anchor.z).magnitude;
            if (occupied) return false;
            if (distance > interactRadius) return false;
            Vector3 d = worldPos - seatCenter;
            Vector3 f = new Vector3(forward.x, 0f, forward.z);
            return Vector3.Dot(new Vector3(d.x, 0f, d.z), f) > 0f;
        }

        /// <summary>最近的可坐椅子（无则 null）。半径/前侧/空闲三条件由本类判定，不散落到驱动层。</summary>
        public static ChairSeat FindBest(Vector3 worldPos)
        {
            ChairSeat best = null;
            float bestDist = float.MaxValue;
            foreach (var chair in FindObjectsByType<ChairSeat>())
            {
                if (!chair.IsUsableNow(worldPos, out float dist)) continue;
                if (dist < bestDist) { bestDist = dist; best = chair; }
            }
            return best;
        }

        /// <summary>最近的椅子（**不看可不可坐**，只看几何距离）——HUD 提示"最近 x.xx m"用。</summary>
        public static ChairSeat FindNearest(Vector3 worldPos, out float distance)
        {
            ChairSeat best = null;
            distance = float.MaxValue;
            foreach (var chair in FindObjectsByType<ChairSeat>())
            {
                float d = chair.AnchorDistanceTo(worldPos);
                if (d < distance) { distance = d; best = chair; }
            }
            return best;
        }

        /// <summary>
        /// 标记占用：椅子锁成 kinematic（不可被推、不可被第二人抢占），
        /// 并**忽略与占用者 CharacterController 的碰撞**——就座后角色整体在坐面 footprint 内
        /// （胶囊半径 0.3117 vs 坐面半深 0.21），不忽略则 clip 的根位移会被自己的椅子挡住。
        /// </summary>
        public void Occupy(CharacterController occupant)
        {
            IsOccupied = true;
            if (Body != null) Body.isKinematic = true;
            SetCollisionIgnored(occupant, true);
        }

        /// <summary>解除占用（`Stand` 播完后由驱动层调用）：恢复刚体与碰撞。</summary>
        public void Release(CharacterController occupant)
        {
            IsOccupied = false;
            if (Body != null) Body.isKinematic = false;
            SetCollisionIgnored(occupant, false);
        }

        /// <summary>
        /// 与占用者 CharacterController 的碰撞开关。占用期间必须为「忽略」——就座后角色整体在坐面
        /// footprint 内（胶囊半径 0.3117 vs 坐面半深 0.21），不忽略则 clip 的根位移被自己的椅子挡住。
        /// 解除占用后若角色仍在坐面内（例：坐姿下按 R 重置）也需继续忽略，走出交互半径再恢复。
        /// </summary>
        public void SetCollisionIgnored(CharacterController cc, bool ignore)
        {
            if (cc == null) return;
            if (_colliders == null || _colliders.Length == 0) _colliders = GetComponentsInChildren<Collider>(true);
            foreach (var col in _colliders)
            {
                if (col != null) Physics.IgnoreCollision(cc, col, ignore);
            }
        }

        private void OnDrawGizmosSelected()
        {
            Vector3 anchor = AnchorPosition;
            Gizmos.color = new Color(0.2f, 1f, 0.4f, 0.9f);
            Gizmos.DrawWireSphere(anchor, 0.12f);
            Gizmos.DrawRay(anchor, transform.forward * 0.5f);
            Gizmos.color = new Color(1f, 0.8f, 0.2f, 0.6f);   // 交互半径（以锚点为心）
            Gizmos.DrawWireSphere(anchor, interactRadius);
            Gizmos.color = new Color(0.9f, 0.5f, 0.2f, 0.8f); // 坐面示意
            Gizmos.DrawWireCube(transform.position + Vector3.up * seatTopY, new Vector3(0.42f, 0.04f, 0.42f));
        }
    }
}
