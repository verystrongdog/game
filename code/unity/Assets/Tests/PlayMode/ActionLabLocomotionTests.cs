// PlayMode 回归断言 — ActionPlayer 落地回切（2026-09-12 发现：按住方向键起跳 → 落地后角色"平移"）
//
// 症状：按住方向键（走/跑）起跳，落地后角色沿该方向平移，腿部不走——身体动、动画不动。
// 根因（代码级）：ActionPlayer.TickLocomotion 的地面守卫比较「目标态 vs 缓存 _locomotionTarget」，
//   而空中播 Jump 的那次 CrossFade 不进缓存 → 落地目标与起跳前同档时守卫判「无变化」→ 一次切态都不发；
//   同时 ActionLab.controller 零 transition/零参数（契约 A：切态只由 C# 发 CrossFade），
//   Animator 不可能自己离开 Jump（Jump clip loopTime=0 → 定格末帧），
//   而 ActionLabDriver 落地帧就按 dir*speed 全速位移 → 呈现为"平移"。
//
// 断言面：ActionPlayer.LastRequestedState / StateRequestCount（决策层留痕，无 Animator 亦记录）
//   —— 本 asmdef 无 UnityEditor 引用，controller 资产级检查仍归 ActionLabBuilder（见 ActionLabSmokeTests 头注）。
using NUnit.Framework;
using UnityEngine;
using YANTF.ActionLab;

public class ActionLabLocomotionTests
{
    private GameObject _go;
    private ActionPlayer _player;

    [SetUp]
    public void SetUp()
    {
        _go = new GameObject("TestActionPlayer");
        _player = _go.AddComponent<ActionPlayer>(); // 无 Animator/controller：只验状态选择逻辑
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(_go);
    }

    /// <summary>核心回归：按住方向键（走档）起跳 → 落地必须再请求一次地面目标态 Walk。</summary>
    [Test]
    public void Landing_AfterWalkJump_RequestsWalk_EvenWhenTargetUnchanged()
    {
        _player.TickLocomotion(true, 0.5f);   // 地面走：0.5 → Walk
        Assert.AreEqual(ActionIds.Walk, _player.LastRequestedState, "地面走档应请求 Walk");

        _player.TickLocomotion(false, 0.5f);  // 起跳（按住键不放）：请求 Jump
        Assert.AreEqual(ActionIds.Jump, _player.LastRequestedState, "离地应请求 Jump");

        _player.TickLocomotion(true, 0.5f);   // 落地：目标仍是 Walk（与起跳前同档）→ 修前漏发，状态机停在 Jump
        Assert.AreEqual(ActionIds.Walk, _player.LastRequestedState,
            "落地必须回切地面目标态：否则状态机停在 Jump，落地后角色平移而腿部不动");
    }

    /// <summary>同源症状：原地起跳（不按键）落地后也必须回切 Idle（否则卡在跳的末帧）。</summary>
    [Test]
    public void Landing_AfterIdleJump_RequestsIdle()
    {
        _player.TickLocomotion(true, 0f);     // 站立：目标 = 初始缓存 Idle → 不发切态
        Assert.AreEqual(0, _player.StateRequestCount, "站立且已在 Idle 缓存档：不该发切态");

        _player.TickLocomotion(false, 0f);    // 原地起跳
        Assert.AreEqual(ActionIds.Jump, _player.LastRequestedState);

        _player.TickLocomotion(true, 0f);     // 落地：目标仍 Idle（与起跳前同档）
        Assert.AreEqual(ActionIds.Idle, _player.LastRequestedState, "原地跳落地必须回切 Idle");
    }

    /// <summary>跑档同理（起跳前 Run → 落地仍 Run）。</summary>
    [Test]
    public void Landing_AfterRunJump_RequestsRun()
    {
        _player.TickLocomotion(true, 1f);     // 跑档：1.0 → Run
        Assert.AreEqual(ActionIds.Run, _player.LastRequestedState);

        _player.TickLocomotion(false, 1f);    // 起跳
        Assert.AreEqual(ActionIds.Jump, _player.LastRequestedState);

        _player.TickLocomotion(true, 1f);     // 落地
        Assert.AreEqual(ActionIds.Run, _player.LastRequestedState, "跑档落地必须回切 Run");
    }

    /// <summary>补发只发生在落地边沿：随后持续按住同档不得逐帧刷切态（否则 CrossFade 融合被反复重启）。</summary>
    [Test]
    public void Landing_Refade_IsIssuedOnce_NotEveryFrame()
    {
        _player.TickLocomotion(true, 0.5f);
        _player.TickLocomotion(false, 0.5f);
        _player.TickLocomotion(true, 0.5f);   // 落地补发

        int afterLanding = _player.StateRequestCount;
        for (int i = 0; i < 10; i++) _player.TickLocomotion(true, 0.5f);

        Assert.AreEqual(afterLanding, _player.StateRequestCount,
            "同档持续按住不应重复请求切态（守卫只在该发的时候发）");
        Assert.AreEqual(ActionIds.Walk, _player.LastRequestedState);
    }

    /// <summary>原有守卫语义不得回退：地面档位变化（走↔跑↔停）仍必须发切态。</summary>
    [Test]
    public void GearChange_OnGround_StillRequests()
    {
        _player.TickLocomotion(true, 0.5f);
        Assert.AreEqual(ActionIds.Walk, _player.LastRequestedState);

        _player.TickLocomotion(true, 1f);     // 走 → 跑
        Assert.AreEqual(ActionIds.Run, _player.LastRequestedState, "地面换挡应发切态");

        _player.TickLocomotion(true, 0f);     // 跑 → 停
        Assert.AreEqual(ActionIds.Idle, _player.LastRequestedState, "停步应回 Idle");
    }
}
