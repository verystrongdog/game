using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>
/// AC-10（WcState.A 长度 69 + CreateDefault 等值性——本 feature 测试范围；
/// 行序对齐验证由 step 3 WMatrixBuilder 测试承担，spec@v1.1 §六 AC-10）。
/// </summary>
public class WcStateTests
{
    [Fact]
    public void A_HasLength69()
    {
        // AC-10 第一部分：长度 69（约束 C1）
        var s = ParticipantState.CreateDefault(hpMax: 50, sanMax: 80);
        Assert.Equal(69, s.Wc.A.Length);
    }

    [Fact]
    public void CreateDefault_A_IsUniform()
    {
        // AC-10 第二部分：CreateDefault 等值性——全 0.10 则行序无关（初值不分行）
        var s = ParticipantState.CreateDefault(hpMax: 50, sanMax: 80);
        Assert.All(s.Wc.A, a => Assert.Equal(0.10f, a));
    }

    [Fact]
    public void A_ValuesRetainOrder()
    {
        // 构造时传入的数组序即状态行序（canonical 序由生产方保证，约束 C1）
        var src = new float[69];
        src[0] = 0.1f;
        src[68] = 0.9f;
        var state = new WcState(src);

        Assert.Equal(0.1f, state.A[0]);
        Assert.Equal(0.9f, state.A[68]);
    }
}
