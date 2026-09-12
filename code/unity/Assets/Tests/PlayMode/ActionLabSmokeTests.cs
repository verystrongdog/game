// PlayMode 冒烟测试 — ActionLab（Grilling #124 Batch0）
// 覆盖面（#124 Q-B5 防漂移分档的机器侧）：
//   ① 目录真值：12 词条（L1=9 / L2=3）与规格 §二 一致，ActionIds 常量与目录三面对一
//   ② 元数据一致性：loop/priority/category 按契约 A 与规格 §二 的口径
//   ③ clipFbxPath 形态：L1 每词条有资产锚（KI → Kevin Iglesias 目录；Mixamo → Combat/<id>.fbx）
//   ④ ActionPlayer 纯逻辑：一次性回退计时阈值（规格 §七）、优先级严格大于才打断、L2 拒播
// 说明：controller 资产级断言（状态覆盖 L1、每状态有 clip）依赖 UnityEditor.Animations，
//       放 Editor 侧由 ActionLabBuilder 构造时自检（菜单重跑幂等 + Console 缺口清单），
//       不在 PlayMode 断言（#124 记录：防漂移分档断言的 controller 侧检查落 builder）。
using System.Collections.Generic;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using YANTF.ActionLab;

public class ActionLabSmokeTests
{
    private static List<string> Ids(IEnumerable<ActionEntry> entries)
    {
        var list = new List<string>();
        foreach (var e in entries) list.Add(e.Id);
        return list;
    }

    private static ActionEntry Cat(string id) => ActionCatalog.Get(id);

    // ---------- ① 词表真值 ----------

    private static readonly string[] SpecL1 = {
        ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Jump,
        ActionIds.PhysicalAttack, ActionIds.MentalAttack, ActionIds.Defend,
        ActionIds.HitReaction, ActionIds.Down,
        ActionIds.Sit, ActionIds.SitIdle, ActionIds.Stand,
    };

    private static readonly string[] SpecL2 = {
        ActionIds.Talk,
    };

    [Test]
    public void Catalog_L1_L2_MatchSpecWordList()
    {
        CollectionAssert.AreEquivalent(SpecL1, Ids(ActionCatalog.Level1), "L1 应等于规格 §二 落地 12 词条");
        CollectionAssert.AreEquivalent(SpecL2, Ids(ActionCatalog.Level2), "L2 应等于规格 §二 登记 1 词条（Talk）");
        Assert.AreEqual(13, ActionCatalog.All.Count, "词表应为 13 词条");
        foreach (var e in ActionCatalog.All)
        {
            Assert.IsFalse(string.IsNullOrWhiteSpace(e.DisplayName), "词条需有中文呈现词: " + e.Id);
            Assert.IsTrue(e.Level == 1 || e.Level == 2, "level ∈ {1,2}: " + e.Id);
        }
    }

    [Test]
    public void ActionIds_Constants_MirrorCatalog()
    {
        var consts = new List<string>();
        foreach (var f in typeof(ActionIds).GetFields(BindingFlags.Public | BindingFlags.Static))
        {
            if (f.IsLiteral && f.FieldType == typeof(string)) consts.Add((string)f.GetValue(null));
        }
        CollectionAssert.AreEquivalent(consts, Ids(ActionCatalog.All),
            "ActionIds 常量应与 ActionCatalog 词条一一对应（三面对一锚）");
    }

    // ---------- ② 元数据一致性（契约 A 优先级 / 循环口径） ----------

    [Test]
    public void Catalog_Priority_MatchContractA()
    {
        Assert.AreEqual(4, Cat(ActionIds.Down).Priority, "Down(4) 最高，终态不可同级打断");
        Assert.AreEqual(3, Cat(ActionIds.HitReaction).Priority, "HitReaction(3) 可打断一次性动作");
        Assert.AreEqual(2, Cat(ActionIds.PhysicalAttack).Priority);
        Assert.AreEqual(2, Cat(ActionIds.MentalAttack).Priority);
        Assert.AreEqual(1, Cat(ActionIds.Defend).Priority, "Defend(1) 高于 locomotion");
        Assert.AreEqual(2, Cat(ActionIds.Sit).Priority, "Sit(2) 与一次性动作同级");
        Assert.AreEqual(1, Cat(ActionIds.SitIdle).Priority, "SitIdle(1) 是持续态，与 Defend 同级");
        Assert.AreEqual(2, Cat(ActionIds.Stand).Priority, "Stand(2) 须严格大于 SitIdle(1)，否则无法从坐姿切出");
        foreach (var loco in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Jump })
        {
            Assert.AreEqual(0, Cat(loco).Priority, "locomotion 优先级 0: " + loco);
        }
    }

    [Test]
    public void Catalog_LoopFlags_MatchSpec()
    {
        foreach (var id in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Defend, ActionIds.SitIdle })
            Assert.IsTrue(Cat(id).Loop, "应循环: " + id);
        foreach (var id in new[] { ActionIds.Jump, ActionIds.PhysicalAttack, ActionIds.MentalAttack,
                                   ActionIds.HitReaction, ActionIds.Down, ActionIds.Sit, ActionIds.Stand })
            Assert.IsFalse(Cat(id).Loop, "应一次性（播完定格/回退/续切）: " + id);
    }

    // ---------- ③b 坐立三段（同源方案，规格 §二 修正块） ----------

    [Test]
    public void Catalog_SitSegment_NextStateAndSources()
    {
        // 坐下播完必须续切到坐姿待机，否则会被一次性回退弹回站姿（"坐不住"）
        Assert.AreEqual(ActionIds.SitIdle, Cat(ActionIds.Sit).NextState,
            "Sit 的 NextState 必须是 SitIdle（坐得住）");
        Assert.IsNull(Cat(ActionIds.Stand).NextState, "Stand 播完回 locomotion 目标态，不续切");
        Assert.IsNull(Cat(ActionIds.SitIdle).NextState, "SitIdle 是循环持续态，无续切");

        // 坐下段用派生件（Sit To Stand 反转），不是 Mixamo 原件
        Assert.AreEqual("Assets/Animations/Derived/SitDown.anim", Cat(ActionIds.Sit).ClipAssetPath,
            "Sit 应锚派生件（反转 Sit To Stand），而非 Mixamo 原件");
        // 起身与坐姿待机用 Mixamo 原件，且与派生件同源同基准
        StringAssert.Contains("Sit To Stand.fbx", Cat(ActionIds.Stand).ClipAssetPath, "Stand 应锚 Sit To Stand.fbx");
        StringAssert.Contains("Sitting Idle.fbx", Cat(ActionIds.SitIdle).ClipAssetPath, "SitIdle 应锚 Sitting Idle.fbx");
    }

    // ---------- ③ clipAssetPath 形态 ----------

    [Test]
    public void Catalog_ClipAssetPath_Shape()
    {
        foreach (var e in ActionCatalog.Level1)
        {
            Assert.IsNotNull(e.ClipAssetPath, "L1 词条需有 clip 资产锚: " + e.Id);
            Assert.IsTrue(e.ClipAssetPath.StartsWith("Assets/"), "资产锚须为 Assets 相对路径: " + e.Id);
        }
        // locomotion 4 条 → KI 目录（工程先例路径，已知作废项归 #139）
        foreach (var id in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Jump })
            StringAssert.Contains("Kevin Iglesias", Cat(id).ClipAssetPath, id + " 应锚 KI 包（#139 后整条切 Mixamo）");
        // combat/reaction 5 条 → Mixamo Combat/<id>.fbx（导入时改名 = 词表 id）
        foreach (var id in new[] { ActionIds.PhysicalAttack, ActionIds.MentalAttack, ActionIds.Defend,
                                   ActionIds.HitReaction, ActionIds.Down })
        {
            StringAssert.Contains("/Combat/" + id + ".fbx", Cat(id).ClipAssetPath, id + " 应锚 Mixamo Combat/<id>.fbx（改名=词表 id）");
        }
        // 坐立三段 → 2 个 Mixamo 原件 + 1 个派生件
        foreach (var id in new[] { ActionIds.Sit, ActionIds.SitIdle, ActionIds.Stand })
            Assert.IsNotNull(Cat(id).ClipAssetPath, id + " 需有 clip 资产锚");
    }

    // ---------- ④ ActionPlayer 纯逻辑 ----------

    [Test]
    public void ActionPlayer_OneShotElapsed_Threshold()
    {
        // 规格 §七：回退计时 = clip.length + 0.05 s
        const float clipLen = 1.0f;
        Assert.IsFalse(ActionPlayer.OneShotElapsed(0.99f * (clipLen + 0.05f), clipLen), "未到点不应回退");
        Assert.IsTrue(ActionPlayer.OneShotElapsed(clipLen + 0.05f, clipLen), "到点即回退");
        Assert.IsTrue(ActionPlayer.OneShotElapsed(3f, clipLen), "超时回退");
        Assert.IsFalse(ActionPlayer.OneShotElapsed(0.049f, 0f), "clip 未知时仍按 0.05 尾时");
        Assert.IsTrue(ActionPlayer.OneShotElapsed(0.05f, 0f));
    }

    [Test]
    public void ActionPlayer_Play_PriorityAndLevelRules()
    {
        var go = new GameObject("TestActionPlayer");
        var player = go.AddComponent<ActionPlayer>(); // 无 Animator/controller：只验状态逻辑
        try
        {
            // 词表外 / L2 登记 → 拒绝
            Assert.IsFalse(player.Play("NotAWord"));
            Assert.IsFalse(player.Play(ActionIds.Talk), "L2 登记未接线应拒播");
            Assert.IsFalse(player.Play(ActionIds.Jump), "Jump 走 locomotion 空中通道，不走 Play()");

            // Defend(1) 可进入（当前 locomotion 0）
            Assert.IsTrue(player.Play(ActionIds.Defend));
            Assert.AreEqual(ActionIds.Defend, player.CurrentActionId);

            // 一次性(2) 打断 Defend
            Assert.IsTrue(player.Play(ActionIds.PhysicalAttack));
            Assert.AreEqual(ActionIds.PhysicalAttack, player.CurrentActionId);
            Assert.IsTrue(player.IsLocked, "一次性动作应锁移动切态");

            // 同级不打断（物攻中再按物攻 → 拒绝）
            Assert.IsFalse(player.Play(ActionIds.MentalAttack), "优先级须严格大于才打断");
            Assert.AreEqual(ActionIds.PhysicalAttack, player.CurrentActionId);

            // HitReaction(3) 打断物攻；Down(4) 打断受击
            Assert.IsTrue(player.Play(ActionIds.HitReaction));
            Assert.IsTrue(player.Play(ActionIds.Down));
            Assert.AreEqual(ActionIds.Down, player.CurrentActionId);

            // Down 终态：同级/低优先级不可打断
            Assert.IsFalse(player.Play(ActionIds.HitReaction), "Down 终态不可被受击打断");
            Assert.IsFalse(player.Play(ActionIds.PhysicalAttack));

            // 重置回 Idle
            player.ResetToIdle();
            Assert.IsNull(player.CurrentActionId);
            Assert.IsFalse(player.IsLocked);

            // 坐立三段（已升 L1）：Sit 可播且锁移动；同级不打断；起身须严格高于 SitIdle
            Assert.IsTrue(player.Play(ActionIds.Sit), "Sit 已升 L1，应可播（NextState=SitIdle）");
            Assert.AreEqual(ActionIds.Sit, player.CurrentActionId);
            Assert.IsTrue(player.IsLocked, "Sit 是一次性动作，应锁移动切态");
            Assert.IsFalse(player.Play(ActionIds.Stand), "Stand(2) 与 Sit(2) 同级 → 坐下过程中不可打断");
            Assert.IsFalse(player.Play(ActionIds.Sit), "同级不打断（Sit 播放中再按 Sit 应拒）");
        }
        finally
        {
            Object.DestroyImmediate(go);
        }
    }

    [Test]
    public void ActionPlayer_SitIdle_IsSustainedState()
    {
        var go = new GameObject("TestActionPlayer2");
        var player = go.AddComponent<ActionPlayer>();
        try
        {
            // 从坐姿待机（持续态，priority 1）起身：Stand(2) 严格大于 → 允许
            Assert.IsTrue(player.Play(ActionIds.SitIdle), "SitIdle 是 L1 循环持续态，应可播");
            Assert.IsFalse(player.IsLocked, "SitIdle 是循环持续态，不锁移动切态（与 Defend 同口径）");
            Assert.AreEqual(ActionIds.SitIdle, player.CurrentActionId);
            Assert.IsTrue(player.Play(ActionIds.Stand), "Stand(2) > SitIdle(1) → 应从坐姿切出起身");
            Assert.AreEqual(ActionIds.Stand, player.CurrentActionId);
        }
        finally
        {
            Object.DestroyImmediate(go);
        }
    }
}
