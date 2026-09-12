using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 情境选择器——Grilling #108 Q4-Q8 契约（#75 D2/D4 落地）。
/// Select = 无状态纯函数（Q8）：候选池 = env_tones.situation.primary；SAN 调制 = 存在性恐慌布尔；
/// 恐慌真 → P(G 均匀随机)=p_panic / P(primary)=1−p_panic；恐慌假 → 确定性 primary。
/// G 组（诡异/负面）构造期计算（Q6）：negative_valence ≥ t_neg ∧ valence = negative（当前 17 成员）。
/// 强度双档（Q7）：恐慌假 1.0 / 恐慌真 s_neg（只作用于原型 fid 注入，与 α_env 正交）。
/// 确定性：组内均匀随机用注入 RNG（同 seed 同选择）。
/// </summary>
public sealed class SituationSelector
{
    private readonly EnvTones _envTones;
    private readonly SituationPrimitives _primitives;
    private readonly HashSet<string> _knownFids;
    private readonly string[] _gGroup;
    private readonly CalibrationConfig _cal;

    /// <summary>
    /// 构造——G 组构造期计算 + 引擎侧全量 fid 断言（Q13 第二层防线）。
    /// </summary>
    /// <param name="envTones">环境基调表（situation.primary 候选池）。</param>
    /// <param name="primitives">27 情境原型（G 组属性 + key_brain_regions）。</param>
    /// <param name="knownFids">已知 fid 集（region_name_map.regions 键 / brain_regions functional_ids）。</param>
    /// <param name="cal">校准常量（TNeg/PPanic/SNeg/SituationPanicShift 消费方）。</param>
    /// <exception cref="ArgumentNullException">任一参数 null。</exception>
    /// <exception cref="InvalidDataException">原型 key_brain_regions 含未知 fid（Q13：加载期异常，禁止静默零注入）。</exception>
    public SituationSelector(
        EnvTones envTones, SituationPrimitives primitives,
        IReadOnlyCollection<string> knownFids, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(envTones);
        ArgumentNullException.ThrowIfNull(primitives);
        ArgumentNullException.ThrowIfNull(knownFids);
        ArgumentNullException.ThrowIfNull(cal);

        _envTones = envTones;
        _primitives = primitives;
        _knownFids = knownFids.ToHashSet();
        _cal = cal;

        // Q13 第二层防线：引擎侧全量断言 key_brain_regions fid ∈ 已知集（未知 → 加载期异常）
        foreach (var archetype in primitives.Archetypes)
        {
            foreach (var fid in archetype.KeyBrainRegions)
            {
                if (!_knownFids.Contains(fid))
                    throw new InvalidDataException(
                        $"情境原型 {archetype.Name} key_brain_regions 含未知 fid: \"{fid}\"（不属 69 fid 集）");
            }
        }

        // Q6 G 组构造期计算：negative_valence ≥ t_neg ∧ valence = negative（当前实测 17 成员）
        _gGroup = primitives.Archetypes
            .Where(a => a.RdocProfile.NegativeValence is { } nv && nv >= cal.TNeg
                        && string.Equals(a.AppraisalProfile.Valence, "negative", StringComparison.Ordinal))
            .Select(a => a.Name)
            .ToArray();
        if (_gGroup.Length == 0)
            throw new InvalidDataException("SituationSelector G 组为空（t_neg 分组规则无成员——数据或阈值异常）");
    }

    /// <summary>当前 G 组（诊断/测试只读）。</summary>
    public IReadOnlyList<string> GGroup => _gGroup;

    /// <summary>
    /// 选择情境（纯函数，Q8）——候选池 = env_tones.situation.primary（Q5）。
    /// </summary>
    /// <param name="environment">环境 id（须存在于 env_tones.json；缺失 → KeyNotFoundException，Q3 禁止回退零向量）。</param>
    /// <param name="panic">存在性恐慌布尔（Q4：任意参与者 SAN&lt;30%，含敌方——判定在调用方/TurnManager）。</param>
    /// <param name="rng">注入 RNG（组内均匀随机，同 seed 同选择）。</param>
    /// <returns>情境选择（原型 id + 强度，Q7 双档）。</returns>
    /// <exception cref="KeyNotFoundException">environment 不在 env_tones.json。</exception>
    public SituationSelection Select(string environment, bool panic, IRng rng)
    {
        ArgumentNullException.ThrowIfNull(rng);

        if (!_envTones.Environments.TryGetValue(environment, out var env))
            throw new KeyNotFoundException($"环境 id \"{environment}\" 不在 env_tones.json（禁止回退零向量）");

        var primary = env.Situation.Primary;
        string archetypeId;
        float strength;

        if (!panic)
        {
            // 恐慌假 → 确定性 primary，强度 1.0
            archetypeId = primary;
            strength = 1.0f;
        }
        else
        {
            // 恐慌真 → P(G 均匀随机)=p_panic / P(primary)=1−p_panic（Q6）；强度 s_neg（Q7）
            archetypeId = rng.NextFloat() < _cal.PPanic
                ? _gGroup[rng.NextInt(_gGroup.Length)]
                : primary;
            strength = _cal.SNeg;
        }

        return new SituationSelection(archetypeId, strength);
    }
}

/// <summary>情境选择结果（原型 id + 强度；强度情境生命周期内恒定，Q7）。</summary>
public sealed record SituationSelection(string ArchetypeId, float Strength);
