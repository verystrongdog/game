// PlayMode 断言 — 持椅交互（手里有东西）的资产侧机械检查（规格 §四·戊 / issue #150）
//
// 本条断言的是**镜像派生件**（`Assets/Animations/Derived/Defend_Carry1H_Mirrored.anim`）：
//   ① 逐曲线非破坏：磁盘上的两件派生件与「现场重算」逐曲线一致（`VerifyDerived()`）
//   ② 骨骼级镜像正确性：镜像件在若干归一化时刻的骨骼世界位姿 == 原件同刻**对侧**骨骼的镜像（x → −x，≤1 mm）
//   ③ 播放口径：humanMotion == true（不是 Generic 曲线），loopTime 与源件一致，且关键帧时间与源件逐曲线一致
//      ——后者证明镜像**不是倒放**实现（口径同规格 §二 修正块：负 speed 在非循环状态下会被 Unity 钳在首帧）
//
// ⚠️ **为什么经反射调 Editor 侧**：本 asmdef（`YANTF.Demo.Tests`）的引用集实测为
//   `netstandard, UnityEngine.CoreModule, nunit.framework, YANTF.Demo, UnityEngine.TestRunner, UnityEngine.PhysicsModule`
//   ——**没有 UnityEditor**。而资产级检查（读 .anim / 建载体 / 采样求值）必须用 UnityEditor API。
//   项目既有口径是「controller 与资产级断言落 Editor 侧 builder」（见 ActionLabSmokeTests 头注），
//   本条沿用该口径：真正的检查在 `DerivedClipBuilder.MirrorCheck()` / `VerifyDerived()` 里，
//   本文件只做**反射桥 + 断言**，把读数变成门禁可跑的绿/红。
using System;
using System.Reflection;
using NUnit.Framework;

public class ActionLabGripTests
{
    private const string BuilderType = "YANTF.EditorTools.DerivedClipBuilder";

    private static Type FindBuilder()
    {
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            var t = asm.GetType(BuilderType, false);
            if (t != null) return t;
        }
        return null;
    }

    private static object Call(string method, params object[] args)
    {
        var t = FindBuilder();
        Assert.IsNotNull(t, "找不到 " + BuilderType + "（Editor 侧编辑器程序集未加载？）——镜像断言无从执行");
        var m = t.GetMethod(method, BindingFlags.Public | BindingFlags.Static);
        Assert.IsNotNull(m, "找不到 " + BuilderType + "." + method);
        return m.Invoke(null, args);
    }

    /// <summary>从 `k=v k=v …` 单行读数里取一个键的值（读数是 Editor 侧给的，不引 JSON 依赖）。</summary>
    private static string Field(string report, string key)
    {
        foreach (var part in report.Split(' '))
        {
            int eq = part.IndexOf('=');
            if (eq > 0 && part.Substring(0, eq) == key) return part.Substring(eq + 1);
        }
        Assert.Fail("读数里没有字段 " + key + "：" + report);
        return null;
    }

    private static float Float(string report, string key) => float.Parse(Field(report, key),
        System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>
    /// 镜像正确性（验收标准 #3）：源件与镜像件在同一载体（X Bot）上逐采样时刻比骨骼世界位姿的**镜像**。
    /// 同时断言**对照项**：不做左右对拍的原始读数必须很大——否则这条断言是空的（对拍写错也能"通过"）。
    /// </summary>
    [Test]
    public void MirroredClip_PoseIsExactMirror_OnCarrier()
    {
        var report = (string)Call("MirrorCheck", 1f);

        Assert.AreEqual("0", Field(report, "bad"),
            "镜像件与源件的骨骼世界位姿不是精确镜像（超差项 > 0）：" + report);
        // 字面项：验收标准点名的 LeftHand ↔ RightHand
        Assert.LessOrEqual(Float(report, "handMaxPosMm"), 1f, "LeftHand/RightHand 镜像位置差必须 ≤1 mm：" + report);
        // 全骨：扣掉骨架自身左右不对称（Mixamo 无名指骨实测 2.28 mm）后的超出量
        Assert.LessOrEqual(Float(report, "maxExcessMm"), 1f,
            "全骨镜像超出「骨架自身不对称」的部分必须 ≤1 mm：" + report);
        Assert.LessOrEqual(Float(report, "maxRotDeg"), 0.01f, "镜像的骨骼世界旋转应逐骨一致：" + report);

        Assert.Greater(Float(report, "controlMaxPosMm"), 100f,
            "对照项太小 —— 说明「对拍」没真的换左右，这条断言是空的：" + report);
        Assert.AreEqual("6", Field(report, "times"), "应在 6 个归一化时刻上采样：" + report);
    }

    /// <summary>播放口径（验收标准 #4）：humanMotion、循环设置与源件一致，且**关键帧时间逐曲线一致**（镜像不是倒放）。</summary>
    [Test]
    public void MirroredClip_IsHumanoidLoop_AndNotTimeReversed()
    {
        var report = (string)Call("MirrorCheck", 1f);

        Assert.AreEqual("True", Field(report, "humanMotion"),
            "镜像件必须是 Humanoid（humanMotion=true），否则挂不上人形载体：" + report);
        Assert.AreEqual("True", Field(report, "loopTime"),
            "格挡是循环持续态：loopTime 应随源件保持为真：" + report);
        Assert.AreEqual("True", Field(report, "keyTimesMatch"),
            "镜像件的关键帧时间应与源件逐曲线一致（镜像不是倒放、不靠负 speed）：" + report);
    }

    /// <summary>非破坏（验收标准 #2/#5）：磁盘上的派生件 == 现场重算，且两件都被覆盖。</summary>
    [Test]
    public void DerivedAssets_MatchFreshDerivation()
    {
        var bad = (int)Call("VerifyDerived");
        Assert.AreEqual(0, bad,
            "派生件与现场重算不一致 " + bad + " 处（源 clip 导入设置被改？或派生件被手改？跑菜单重建）");
    }

    /// <summary>镜像的第二条独立判据：镜像两次回到原件——曲线级可自检（规格 §戊·3「镜像同样可自检」）。</summary>
    [Test]
    public void MirrorTwice_ReturnsToSourceCurves()
    {
        var ok = (bool)Call("VerifyMirrorInvolution");
        Assert.IsTrue(ok, "二次镜像未逐曲线回到源件 —— 说明符号表或换名规则不自洽");
    }
}
