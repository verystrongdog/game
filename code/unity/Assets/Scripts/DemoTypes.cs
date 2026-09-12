// YANTF 呈现沙盘 — 公共类型（Grilling #122，2026-09-06）
// 呈现验证载体，非正典实体模板。数值口径对齐 design/rules/核心机制.md + CalibrationConfig.Default。
using System;

namespace YANTF.Demo
{
    /// <summary>基础行动种类（对应 基础行动设计 §一：物理攻击/防御/精神攻击）。</summary>
    public enum DemoActionKind
    {
        None = 0,
        PhysicalAttack = 1, // M1 通道
        Defend = 2,         // M1 通道（与物攻互斥）
        MentalAttack = 3,   // Broca 通道
    }

    /// <summary>回合沙盘阶段（轻量手动回合，不触碰引擎 TurnManager 五阶段管线）。</summary>
    public enum DemoRoundPhase
    {
        PlayerInput,   // 玩家选择 M1 动作 + Broca 动作 + 移动，等待 [执行回合]
        Execute,       // 结算玩家动作（按选择顺序）→ 陪练动作 → 冷却/状态推进
        RoundEnd,      // 回合收束，回到 PlayerInput
    }

    /// <summary>一次行动的结算请求（结算层输入）。</summary>
    public struct DemoActionRequest
    {
        public DemoActionKind Kind;
        public DemoActor Source;
        public DemoActor Target;
    }

    /// <summary>一次行动的结算结果（结算层输出；伤害为引擎口径一位小数）。</summary>
    public struct DemoActionResult
    {
        public DemoActionKind Kind;
        public bool Hit;
        public float HpDamage;
        public float SanDamage;
    }
}
