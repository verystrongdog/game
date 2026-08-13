using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>AC-3（91 浮点组成）+ AC-5（CreateDefault 初始化值）+ C7（防御性拷贝）。</summary>
public class ParticipantStateTests
{
    [Fact]
    public void Composes91Floats()
    {
        // AC-3: 91 = 69 (Wc) + 4 (Tone) + 15 (Gurney 3×5) + 3 (Gate)
        var s = ParticipantState.CreateDefault(hpMax: 50, sanMax: 80);

        Assert.Equal(69, s.Wc.A.Length);
        Assert.Equal(5, s.Gurney.Somatic.Length);
        Assert.Equal(5, s.Gurney.Cognitive.Length);
        Assert.Equal(5, s.Gurney.Limbic.Length);
        // Tone (4 scalars) 与 Gates (3 scalars) 为命名字段，计数由类型形状保证——
        // 总浮点数 = 69 + 4 + 15 + 3 = 91（运行时状态模型 §三 表尾）
    }

    [Fact]
    public void CreateDefault_SetsDocumentedInitialValues()
    {
        // AC-5: a_j=0.10 / tone=baseline / Gurney=0（§7.3）+ gates=1.0（§6.3+§6.4 推导）
        var s = ParticipantState.CreateDefault(hpMax: 50, sanMax: 80);

        Assert.All(s.Wc.A, a => Assert.Equal(0.10f, a));
        Assert.Equal(0.3f, s.Tone.Ne);
        Assert.Equal(0.4f, s.Tone.DaVta);
        Assert.Equal(0.5f, s.Tone.DaSnc);
        Assert.Equal(0.5f, s.Tone.Ht5);
        Assert.All(s.Gurney.Somatic, v => Assert.Equal(0f, v));
        Assert.All(s.Gurney.Cognitive, v => Assert.Equal(0f, v));
        Assert.All(s.Gurney.Limbic, v => Assert.Equal(0f, v));
        Assert.Equal(1.0f, s.Gates.GateSomatic);
        Assert.Equal(1.0f, s.Gates.GateCognitive);
        Assert.Equal(1.0f, s.Gates.GateLimbic);
    }

    [Fact]
    public void CreateDefault_SetsCombatFields()
    {
        // AC-5 续: Hp/San/CD/IsDefending
        var s = ParticipantState.CreateDefault(hpMax: 50, sanMax: 80);

        Assert.Equal(50, s.Hp);
        Assert.Equal(50, s.HpMax);
        Assert.Equal(80, s.San);
        Assert.Equal(80, s.SanMax);
        Assert.False(s.IsDefending);
        Assert.Equal(0, s.EnduranceActiveCd);
        Assert.Equal(0, s.DefendCd);
    }

    [Fact]
    public void WcState_CopiesArrayOnConstruction()
    {
        // C7: 构造时防御性拷贝——外部修改不影响状态
        var src = new float[69];
        src[0] = 0.5f;
        var state = new WcState(src);

        src[0] = 0.99f;

        Assert.Equal(0.5f, state.A[0]);
    }

    [Fact]
    public void GurneyState_CopiesArraysOnConstruction()
    {
        // C7: 三个数组各拷贝一份
        var somatic = new float[5];
        somatic[4] = 0.7f;
        var state = new GurneyState(somatic, new float[5], new float[5]);

        somatic[4] = 0.0f;

        Assert.Equal(0.7f, state.Somatic[4]);
    }
}
