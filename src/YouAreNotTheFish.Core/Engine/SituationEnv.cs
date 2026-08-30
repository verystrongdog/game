using YouAreNotTheFish.Core.Data;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// s_env 合成——Grilling #108 Q4 神经落点 + Q12 Phase 1 注入。
/// 公式：s_env_j = (W_sensory × α_env)_j + Σ_原型注入（strength × 1[j ∈ key_brain_regions]）
/// - 环境基调：W_sensory[j][k] × α_env[k]（8 模态）
/// - 原型注入：选中原型的 key_brain_regions 节点直接加 strength（fid 直用，无翻译）
/// 纯函数；空间级、所有参与者同值（Q4）。
/// </summary>
public static class SituationEnv
{
    /// <summary>
    /// 计算 s_env[69]。
    /// </summary>
    /// <param name="wsensory">W_sensory 矩阵（69×8）。</param>
    /// <param name="envTones">环境基调表（alpha_env + situation.primary）。</param>
    /// <param name="primitives">27 情境原型（key_brain_regions）。</param>
    /// <param name="environment">环境 id（须存在）。</param>
    /// <param name="archetypeId">选中原型 name。</param>
    /// <param name="strength">情境强度（Q7 双档：恐慌假 1.0 / 恐慌真 s_neg）。</param>
    /// <returns>float[69] s_env（RegionIds 序，与 W_sensory 行序一致）。</returns>
    /// <exception cref="KeyNotFoundException">environment 或 archetypeId 不存在。</exception>
    public static float[] Compute(
        WsensoryMatrix wsensory, EnvTones envTones, SituationPrimitives primitives,
        string environment, string archetypeId, float strength)
    {
        ArgumentNullException.ThrowIfNull(wsensory);
        ArgumentNullException.ThrowIfNull(envTones);
        ArgumentNullException.ThrowIfNull(primitives);

        if (!envTones.Environments.TryGetValue(environment, out var env))
            throw new KeyNotFoundException($"环境 id \"{environment}\" 不在 env_tones.json");
        var archetype = primitives.Archetypes.FirstOrDefault(a => a.Name == archetypeId)
            ?? throw new KeyNotFoundException($"情境原型 \"{archetypeId}\" 不在 situation_primitives.json");

        var sEnv = new float[wsensory.Matrix.Length];

        // ① 环境基调：W_sensory × α_env（8 模态，k 升序）
        var alpha = env.AlphaEnv;
        var matrix = wsensory.Matrix;
        for (var j = 0; j < sEnv.Length; j++)
        {
            var row = matrix[j];
            float s = 0f;
            for (var k = 0; k < alpha.Length; k++)
            {
                if (row[k] != 0 && alpha[k] != 0f)
                    s += (float)alpha[k]; // W∈{0,1}，乘为精确
            }
            sEnv[j] = s;
        }

        // ② 原型注入：key_brain_regions 直接加 strength（fid 直用，Q4 神经落点）
        var fidIndex = wsensory.RegionIds.Select((fid, i) => (fid, i))
            .ToDictionary(x => x.fid, x => x.i);
        foreach (var fid in archetype.KeyBrainRegions)
        {
            if (fidIndex.TryGetValue(fid, out var j))
                sEnv[j] += strength;
        }

        return sEnv;
    }
}
