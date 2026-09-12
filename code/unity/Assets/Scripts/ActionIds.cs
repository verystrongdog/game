// 动作受控词表 13 词条常量（规格 §二；机器源锚）
// 三面对一：ActionIds 常量 = ActionCatalog 词条 Id = AnimatorController 状态名 = 代码字符串。
// 扩展协议：命名只增不删；新增走快轨（正典来源 + 命名规范 + 声明状态与来源）。
using System;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 词表 13 词条 id（L1 落地 12 + L2 登记 1）。
    /// 中文呈现词与元数据见 ActionCatalog；本类只锁 id 常量。
    /// </summary>
    public static class ActionIds
    {
        // ---- L1 落地（controller 接线）----
        public const string Idle = "Idle";                    // 待机
        public const string Walk = "Walk";                    // 走
        public const string Run = "Run";                      // 跑
        public const string Jump = "Jump";                    // 跳（locomotion 空中态）
        public const string PhysicalAttack = "PhysicalAttack"; // 物攻（空手直拳，M1 出拳）
        public const string MentalAttack = "MentalAttack";     // 精攻（A 前指宣言）
        public const string Defend = "Defend";                // 防御（循环护前格挡）
        public const string HitReaction = "HitReaction";      // 受击（单型通用）
        public const string Down = "Down";                    // 倒下（终态停留至重置）
        public const string Sit = "Sit";                      // 坐下（播完切 SitIdle，不停回站姿）
        public const string SitIdle = "SitIdle";              // 坐姿待机（循环持续态）
        public const string Stand = "Stand";                  // 站起

        // ---- L2 登记（锁名 + 资产锚，不接线；消费端就绪时 L2→L1）----
        public const string Talk = "Talk";                    // 对话言语
    }
}
