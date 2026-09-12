using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>
/// SpeedWeights.FromCalibration — csharp-speed spec@v1.1 §六 AC-15。
/// 权重只作用于合成层（spec §二 2.2）；映射 = CalibrationConfig.SpeedW1/2/3（1:1，无变换）。
/// 「逐位」标注者精确相等（默认 1/3 为 f32 常量运算）。
/// </summary>
public class SpeedComponentsTests
{
    [Fact]
    public void FromCalibration_DefaultConfig_ThirdWeights()
    {
        var w = SpeedWeights.FromCalibration(CalibrationConfig.Default);
        Assert.Equal(1f / 3f, w.W1); // 逐位——同源 f32 常量
        Assert.Equal(1f / 3f, w.W2);
        Assert.Equal(1f / 3f, w.W3);
    }

    [Fact]
    public void FromCalibration_CustomConfig_FieldMapping()
    {
        var cal = new CalibrationConfig { SpeedW1 = 0.5f, SpeedW2 = 0.25f, SpeedW3 = 0.25f };
        var w = SpeedWeights.FromCalibration(cal);
        Assert.Equal(0.5f, w.W1);
        Assert.Equal(0.25f, w.W2);
        Assert.Equal(0.25f, w.W3);
    }

    [Fact]
    public void FromCalibration_Null_Throws()
    {
        Assert.Throws<ArgumentNullException>(() => SpeedWeights.FromCalibration(null!));
    }
}
