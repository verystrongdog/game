namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// EventProcessor.ProcessEvents 的输出——csharp-events spec@v1.2.2 §二 2.3。
/// States：与输入同长度；每元素 = 输入副本，δ 接收者的 Tone 替换为 Step 后值
/// （零 delta 参与者 Tone 与输入逐位相同——偏差 B3）。
/// SensoryAccum[p]：参与者 p 的 s 增量，长度 69，索引序 = WsensoryMatrix.RegionIds 序
/// （canonical 69，wmatrix 约束 C1 承接）。本调用产生的增量（不含调用前累积——调用方 step 10 负责跨调用累加）。
/// </summary>
public sealed record EventProcessingResult(
    IReadOnlyList<ParticipantState> States,
    IReadOnlyList<float[]> SensoryAccum);
