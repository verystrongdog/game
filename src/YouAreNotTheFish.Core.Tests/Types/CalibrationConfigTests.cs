using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>AC-9（CalibrationConfig.Default 逐常量 = plan §七 表）。</summary>
public class CalibrationConfigTests
{
    [Fact]
    public void Default_MatchesPlanSection7Table()
    {
        // AC-9: 逐常量断言——值来源 plan §七（spec@v1.1 §四 4.2）
        var c = CalibrationConfig.Default;

        Assert.Equal(1f / 3f, c.SpeedW1);
        Assert.Equal(1f / 3f, c.SpeedW2);
        Assert.Equal(1f / 3f, c.SpeedW3);
        Assert.Equal(0.3f, c.MDefault);
        Assert.Equal(0.15f, c.TBase);
        Assert.Equal(0.3f, c.DeltaScale);   // [NEW] 待校准
        Assert.Equal(1.0f, c.ScaleMental);  // 未启用（demo 固定 base 2），1.0 为禁用占位
        Assert.Equal(4, c.ExpectedDamage);
        Assert.Equal(-0.1f, c.M1SustainPenalty);      // [NEW] 待校准
        Assert.Equal(0.15f, c.PerceptionThreshold);   // [NEW] 待校准
        Assert.Equal(50, c.PlayerHp);                 // [NEW]
        Assert.Equal(80, c.PlayerSan);                // [NEW]
        Assert.Equal(15, c.NpcHp);                    // [NEW]
        Assert.Equal(60, c.NpcSan);                   // [NEW]
    }
}
