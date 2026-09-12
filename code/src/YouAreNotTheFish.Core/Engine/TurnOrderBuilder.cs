using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 回合行动顺序构建——csharp-speed spec@v1.1（../../../规格/引擎/csharp-speed.md）§三 3.2。
/// 职责：speed 分数降序排序；同速（逐位相等 float ==）组内 Fisher-Yates 洗牌破平
/// （回合战斗流程 §3.4「同速时掷硬币，每回合重新破平」——每次调用重新破平）。
/// RNG 消费序契约（AC-10 镜像依赖，实现侧禁改动）：
///   1. 组内索引保持输入升序；2. for i = m−1 downto 1: j = rng.NextInt(i+1); swap(group[i], group[j])；
///   3. m = 1 时不消费 rng。组间顺序 = 分数降序；组内 = 洗牌结果。
/// 纯静态工具：无状态、无隐式随机（RNG 经参数注入）。
/// 来源：spec@v1.1 §三 3.2；回合战斗流程 §3.4；任务issue D9（草案 NextFloat 作废——以 spec NextInt 为准）。
/// </summary>
public static class TurnOrderBuilder
{
    /// <summary>
    /// 构建行动顺序索引数组，[0] = 最快。
    /// 排序：score 降序（稳定——同分保持输入升序，.NET OrderBy 稳定性契约）；
    /// 平局 = 逐位相等（float ==，声明：无 epsilon 合并——demo 平局来自相同状态，天然精确相等）。
    /// 异常：scores/rng 为 null → ArgumentNullException（分别校验）。长度 0 → 空数组；长度 1 → [0]（不消费 rng）。
    /// 未定义行为：输入含 NaN。
    /// </summary>
    public static int[] BuildOrder(float[] scores, IRng rng)
    {
        ArgumentNullException.ThrowIfNull(scores);
        ArgumentNullException.ThrowIfNull(rng);

        int n = scores.Length;
        int[] order = Enumerable.Range(0, n).ToArray();

        // 分数降序（稳定排序——同分组内保持输入升序，RNG 消费序契约第 1 条的前提）
        order = order.OrderByDescending(i => scores[i]).ToArray();

        // 破平：每个平局组内 Fisher-Yates（算法写死——RNG 消费序契约第 2/3 条；m=1 不消费 rng）
        int start = 0;
        while (start < n)
        {
            int end = start + 1;
            while (end < n && scores[order[end]] == scores[order[start]])
            {
                end++; // float == 逐位相等平局
            }

            int m = end - start;
            for (int i = m - 1; i >= 1; i--)
            {
                int j = rng.NextInt(i + 1);
                (order[start + i], order[start + j]) = (order[start + j], order[start + i]);
            }

            start = end;
        }

        return order;
    }
}
