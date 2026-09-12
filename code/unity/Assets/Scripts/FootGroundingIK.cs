// 足底接地 IK — 动作库规格.md §四·乙「足部贴地」
// 触发依据（2026-09-12 探针实测，Grilling #137 工作面）：坐姿足底陷入地面 左 62.8 mm / 右 11.9 mm、
//   坐下中段 28.7/6.9 mm、起身中段 63.5/54.9 mm、起身末态悬空 14.7/34.2 mm。
//   即「clip × X Bot 比例不符」导致脚悬空/陷入——正是 §四·乙 预留足 IK 的那格。
// 做法：每帧在 OnAnimatorIK 里逐帧设置目标（SetIKPosition 不是持久状态，Unity 每帧重置），
//   只上抬、不下压：需要量 <= 0（脚已贴地或悬空）时 IK 权重归 0、完全不介入；
//   需要量 > 0（足底陷入）时权重按 blendDistance 爬升到 weight，目标 = 脚当前位置 + 需要量。
//   ⚠️ 权重归零这一条是实测逼出来的：若需要量为 0 仍给权重 1，求解器会为「够到脚当前位置」这个目标
//   把腿拉弯（实测起身末帧膝角被拉弯 14.6°、脚反而扎入地面 9.5 mm）。
// 因此可常开：走/跑时摆动脚在上方（need<0）不受影响，支撑脚贴地（need≈0）不动；只有陷入地面的姿势会被修正。
// 前置：Animator 所在层的 IK Pass 必须打开（AnimatorControllerLayer.iKPass = true），否则 OnAnimatorIK 不被调用。
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 足底接地钳制：把每只脚的足底最低点抬到地面基准，只上抬不下压。
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public sealed class FootGroundingIK : MonoBehaviour
    {
        [Tooltip("地面高度 m（ActionLab 地面 = builder 建的 Plane 原语，表面在 y=0）")]
        public float groundY = 0f;                       // 来源：ActionLabBuilder.CreateScene 的 Ground 平面

        [Tooltip("足底相对地面的余量 m。模型自然站姿下足底最低点实测 +0.0028，故取该值使贴地不穿地")]
        public float soleMargin = 0.0028f;               // 来源：2026-09-12 探针 bind pose 实测（趾骨 Y=+0.0028）

        [Tooltip("IK 总权重 0..1")]
        [Range(0f, 1f)] public float weight = 1f;

        [Tooltip("朝向修正权重：0 = 只修位置不改脚掌朝向（当前采用），1 = 同时把脚掌转平")]
        [Range(0f, 1f)] public float rotationWeight = 0f;

        [Tooltip("单帧最大上抬量 m，限制突变。坐姿所需最大修正实测 62.8 mm，取 0.5 留足余量")]
        public float maxLiftPerFrame = 0.5f;             // 来源：探针实测最大修正量 0.0628 m × 8 倍安全余量

        [Tooltip("权重爬升距离 m：需要量低于此值时 IK 权重按比例衰减，需要量为 0 时权重归 0（IK 完全关闭）。" +
                 "取值依据见下方说明——若需要量为 0 仍给权重 1，求解器会为『够到脚当前位置』这个目标把腿拉弯，" +
                 "实测起身末帧膝角被拉弯 14.6°、脚反而扎入地面 9.5 mm")]
        public float blendDistance = 0.02f;              // 来源：2026-09-12 实测缺陷（见上），取 20 mm

        private Animator _animator;

        private void Awake()
        {
            _animator = GetComponent<Animator>();
        }

        private void OnAnimatorIK(int layerIndex)
        {
            if (_animator == null || weight <= 0f) return;
            Ground(AvatarIKGoal.LeftFoot, HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes);
            Ground(AvatarIKGoal.RightFoot, HumanBodyBones.RightFoot, HumanBodyBones.RightToes);
        }

        private void Ground(AvatarIKGoal goal, HumanBodyBones footBone, HumanBodyBones toeBone)
        {
            var foot = _animator.GetBoneTransform(footBone);
            if (foot == null) return;
            var toe = _animator.GetBoneTransform(toeBone);

            float lowest = foot.position.y;
            if (toe != null) lowest = Mathf.Min(lowest, toe.position.y);

            // 需要量 > 0 = 足底陷入地面，需上抬；<= 0 = 已贴地或悬空，不动它（只上抬不下压）
            float need = groundY + soleMargin - lowest;
            float ramp = blendDistance > 0f ? Mathf.Clamp01(need / blendDistance) : (need > 0f ? 1f : 0f);
            float w = weight * ramp;

            _animator.SetIKPositionWeight(goal, w);
            _animator.SetIKRotationWeight(goal, w * rotationWeight);
            if (w <= 0f) return;   // 无修正需求 → 完全不介入，避免求解器为"够到当前位置"而拉弯腿

            float lift = Mathf.Clamp(need, 0f, maxLiftPerFrame);
            _animator.SetIKPosition(goal, foot.position + Vector3.up * lift);
        }
    }
}
