namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 行归一化连接权重矩阵契约——运行时状态模型 §4.3（W_norm）/§4.4（τ）。
/// 由 WMatrixBuilder（step 3）构建；本 feature 仅定义契约。
/// 行序 = canonical 69 = WsensoryMatrix.RegionIds（约束 C1，spec@v1.1 §2.8 行序契约：
/// 不得按 graph_nodes 迭代序——实测三数据文件 key 序互不相同，graph_nodes 为 51 个 dk_name 空间）。
/// 构造时防御性拷贝（约束 C7）。
/// </summary>
public sealed record WMatrix
{
    /// <summary>W_norm[j][k]：行归一化后的 69×69 权重。来源：运行时状态模型 §4.3。</summary>
    public float[,] W { get; }

    /// <summary>τ_j：四档时间常数（0.01/0.05/0.15/0.05）。来源：§4.4。</summary>
    public float[] Tau { get; }

    /// <summary>fid→行序映射（canonical 69）。来源：plan §三。承担 fid→行校验职责（step 3 测试断言 RowFids == RegionIds）。</summary>
    public string[] RowFids { get; }

    /// <summary>从外部数组构造——三维数据各拷贝一份。</summary>
    public WMatrix(float[,] w, float[] tau, string[] rowFids)
    {
        W = (float[,])w.Clone();
        Tau = (float[])tau.Clone();
        RowFids = (string[])rowFids.Clone();
    }
}
