namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 单环路 salience 对——运行时状态模型 §6.2/§6.3。再审计 C-C2 产物：
/// CstcGating.Step（step 6）返回三元组含本类型。
/// </summary>
/// <param name="C">c_loop = mean(a(ci)) ∈ [0,1]。来源：§6.2。</param>
/// <param name="Da">DA_loop ∈ [0,1]。来源：§6.3 DA 混合。</param>
public sealed record LoopValue(float C, float Da);

/// <summary>
/// 三环路 salience 三元组。DA 混合逐字段显式公式（spec@v1.1 §二 2.9——
/// §6.3 文档序为 limbic→cognitive→somatic，与字段序不同，按字段名配对不得按位置直配）：
/// Somatic.Da = 0.2×DA_VTA + 0.8×DA_SNc（运动执行主导）；
/// Cognitive.Da = 0.4×DA_VTA + 0.6×DA_SNc；
/// Limbic.Da = 0.8×DA_VTA + 0.2×DA_SNc（动机主导）。
/// </summary>
/// <param name="Somatic">somatic 环路 salience。</param>
/// <param name="Cognitive">cognitive 环路 salience。</param>
/// <param name="Limbic">limbic 环路 salience。</param>
public sealed record LoopSalience(LoopValue Somatic, LoopValue Cognitive, LoopValue Limbic);
