using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// NpcSalience spec@v1.2 §三 3.2：3 行动 salience 竞争（Softmax + T_SAN 判定序 + 目标选择）。
/// 锚点：salience 公式逐字对照 NPC AI §3.2/§3.3；行为断言（同种子确定性、目标=异队、SAN=0 均匀）。
/// </summary>
public class NpcSalienceTests
{
    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..", "data")),
        "/home/dog/game/data",
    ];

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    private static CombatState State2P() => CombatState.Create(
        new[] { ParticipantState.CreateDefault(50f, 80f), ParticipantState.CreateDefault(15f, 60f) },
        new[] { 1, 2 }, Data(), CalibrationConfig.Default);

    private static CombatContext Ctx(ulong seed) => new(new DeterministicRng(seed), Data(), CalibrationConfig.Default);

    // ---- AC-11 ----

    [Fact]
    public void Target_FirstEnemyTeam()
    {
        var state = State2P(); // teams=[1,2]
        var action = NpcSalience.SelectAction(0, state, Ctx(1uL));
        // 目标 = 第一个异队参与者（p1）
        var target = action.M1?.TargetId ?? action.Broca!.TargetId;
        Assert.Equal(1, target);

        // selfIndex 越界
        Assert.Throws<ArgumentOutOfRangeException>(() => NpcSalience.SelectAction(9, state, Ctx(1uL)));
    }

    [Fact]
    public void Action_IsOneOfThreeBasics_WithChannelMapping()
    {
        // 行动 ∈ {physical(M1), mental(Broca), defend(M1)}（通道映射 W5）
        var state = State2P();
        for (ulong seed = 0; seed < 50; seed++)
        {
            var action = NpcSalience.SelectAction(0, state, Ctx(seed));
            if (action.M1 is not null)
                Assert.Contains(action.M1.Kind, new[] { ActionKind.PhysicalAttack, ActionKind.Defend });
            if (action.Broca is not null)
                Assert.Equal(ActionKind.MentalAttack, action.Broca.Kind);
            Assert.True(action.M1 is not null || action.Broca is not null); // 三候选必有 winner
        }
    }

    [Fact]
    public void Determinism_SameSeedSameAction()
    {
        var state = State2P();
        for (ulong seed = 0; seed < 10; seed++)
        {
            var a1 = NpcSalience.SelectAction(0, state, Ctx(seed));
            var a2 = NpcSalience.SelectAction(0, state, Ctx(seed));
            Assert.Equal(a1, a2);
        }
    }

    [Fact]
    public void SanZero_UniformRandom_DifferentSeedsDiffer()
    {
        // SAN=0 → T=∞ 均匀随机（判定序 SAN==0 最先——Δ审计 F4）
        var state = State2P();
        state.ApplyDamage(1, state.Participants[1].Hp, 0f);

        var seen = new HashSet<CombatAction>();
        for (ulong seed = 0; seed < 20; seed++)
            seen.Add(NpcSalience.SelectAction(1, state, Ctx(seed)));
        Assert.True(seen.Count >= 2, $"SAN=0 应有多样行动（实际 {seen.Count} 种）");
    }
}
