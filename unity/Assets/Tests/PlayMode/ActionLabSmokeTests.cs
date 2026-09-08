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
    };

    private static readonly string[] SpecL2 = {
        ActionIds.Sit, ActionIds.Stand, ActionIds.Talk,
    };

    [Test]
    public void Catalog_L1_L2_MatchSpecWordList()
    {
        CollectionAssert.AreEquivalent(SpecL1, Ids(ActionCatalog.Level1), "L1 应等于规格 §二 落地 9 词条");
        CollectionAssert.AreEquivalent(SpecL2, Ids(ActionCatalog.Level2), "L2 应等于规格 §二 登记 3 词条");
        Assert.AreEqual(12, ActionCatalog.All.Count, "词表应为 12 词条");
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
        foreach (var f in typeof(ActionIds).GetFields(BindingFlags.Public | BindingFlags.Static | BindingFlags.Literal))
        {
            if (f.FieldType == typeof(string)) consts.Add((string)f.GetValue(null));
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
        foreach (var loco in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Jump })
        {
            Assert.AreEqual(0, Cat(loco).Priority, "locomotion 优先级 0: " + loco);
        }
    }

    [Test]
    public void Catalog_LoopFlags_MatchSpec()
    {
        foreach (var id in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Defend })
            Assert.IsTrue(Cat(id).Loop, "应循环: " + id);
        foreach (var id in new[] { ActionIds.Jump, ActionIds.PhysicalAttack, ActionIds.MentalAttack,
                                   ActionIds.HitReaction, ActionIds.Down })
            Assert.IsFalse(Cat(id).Loop, "应一次性（播完定格/回退）: " + id);
    }

    // ---------- ③ clipFbxPath 形态 ----------

    [Test]
    public void Catalog_ClipFbxPath_Shape()
    {
        foreach (var e in ActionCatalog.Level1)
        {
            Assert.IsNotNull(e.ClipFbxPath, "L1 词条需有 clip 资产锚: " + e.Id);
            Assert.IsTrue(e.ClipFbxPath.StartsWith("Assets/"), "资产锚须为 Assets 相对路径: " + e.Id);
        }
        // locomotion 4 条 → KI 目录（工程先例路径）；combat/reaction 5 条 → Mixamo Combat/<id>.fbx
        foreach (var id in new[] { ActionIds.Idle, ActionIds.Walk, ActionIds.Run, ActionIds.Jump })
            StringAssert.Contains("Kevin Iglesias", Cat(id).ClipFbxPath, id + " 应锚 KI 包");
        foreach (var id in new[] { ActionIds.PhysicalAttack, ActionIds.MentalAttack, ActionIds.Defend,
                                   ActionIds.HitReaction, ActionIds.Down })
        {
            StringAssert.Contains("/Combat/" + id + ".fbx", Cat(id).ClipFbxPath, id + " 应锚 Mixamo Combat/<id>.fbx（改名=词表 id）");
        }
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
            Assert.IsFalse(player.Play(ActionIds.Sit), "L2 登记未接线应拒播");
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
        }
        finally
        {
            Object.DestroyImmediate(go);
        }
    }
}
