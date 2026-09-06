// 结算层接口 + 临时白盒实现（Grilling #122）
// ⚠️ 决策 Q1：首版接引擎核结算。引擎桥接（Q6b 子集/全量定案）后，本文件以 EngineSolver 替换
// WhiteboxSolver——WhiteboxSolver 仅用于桥接落地前的编译/流程验证，数值**镜像**
// CalibrationConfig.Default（核心机制 §4.2/§4.3），保证替换透明（结算行为不变）。
using UnityEngine;

namespace YANTF.Demo
{
    public interface IDemoSolver
    {
        DemoActionResult Resolve(DemoActionRequest req);
    }

    /// <summary>
    /// 临时白盒结算（待 EngineSolver 替换）。数值镜像 CalibrationConfig.Default：
    /// 物理 = Round1(4 × (1+force0+motivation0) × gate1.0 × 防御0.5)；命中 = roll &lt; 0.85−0.10（L0 回避自动触发，引擎 0.75 精确）；
    /// 精神 = Round1(max(1.0, 2 − 忍耐被动1)) × pen（&lt;30% ×1.3 / &lt;15% ×2）；HP 成分 = Floor1(san×0.5)。
    /// gate 取 1.0（沙盘无脑干调质干扰的基线演示）。
    /// </summary>
    public sealed class WhiteboxSolver : IDemoSolver
    {
        public DemoActionResult Resolve(DemoActionRequest req)
        {
            var result = new DemoActionResult { Kind = req.Kind };
            var target = req.Target;
            switch (req.Kind)
            {
                case DemoActionKind.PhysicalAttack:
                {
                    float damage = Round1(4f * (target.Defending ? 0.5f : 1f));
                    bool hit = Random.value < 0.75f;                 // 0.85 − 0.10（L0 回避）
                    result.Hit = hit;
                    result.HpDamage = hit ? damage : 0f;
                    break;
                }
                case DemoActionKind.MentalAttack:
                {
                    float ratio = target.San / target.sanMax;
                    float pen = ratio < 0.15f ? 2f : (ratio < 0.30f ? 1.3f : 1f);
                    float san = Round1(Mathf.Max(1f, Round1(2f - 1f)) * pen);   // 2 − 忍耐被动 1，最低 1.0
                    result.Hit = true;
                    result.SanDamage = san;
                    result.HpDamage = Floor1(san * 0.5f);
                    break;
                }
            }
            return result;
        }

        private static float Round1(float x) => Mathf.Round(x * 10f) / 10f;
        private static float Floor1(float x) => Mathf.Floor(x * 10f) / 10f;
    }
}
