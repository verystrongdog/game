// 动作目录（Grilling #123 规格 §二/§3.2；机器源唯一真相）
// 词条元数据：category / level / loop / priority / fade / clipFbxPath（资产存在性 → 防漂移分档）。
// 消费方（ActionPlayer、ActionLabBuilder、测试、HUD）一律查本目录，禁止各自硬编码。
using System.Collections.Generic;

namespace YANTF.ActionLab
{
    /// <summary>分类枚举（受控词表，规格 §3.2）。</summary>
    public enum ActionCategory
    {
        Locomotion, // 走跑跳待机等基础运动
        Combat,     // 物攻/精攻/防御
        Reaction,   // 受击/倒下
        Social,     // 对话言语等
        Interaction,// 坐/站等环境交互
        Status,     // 状态姿态（本期无词条，留扩展）
    }

    /// <summary>
    /// 单个词条的只读元数据。
    /// clipFbxPath：该词条 clip 所在 FBX 资产路径（取其中第一个 AnimationClip）；
    /// 资产是否存在 = "现成/缺口" 的机器判据（#124 Q-B5 分档断言依据），缺口时状态仍建、clip 留空。
    /// </summary>
    public sealed class ActionEntry
    {
        public readonly string Id;
        public readonly string DisplayName;   // 中文呈现词（HUD/日志）
        public readonly ActionCategory Category;
        public readonly int Level;            // 1 = L1 落地（接线）；2 = L2 登记（不接线）
        public readonly bool Loop;            // 循环（Idle/Walk/Run/Defend）；false = 一次性
        public readonly int Priority;         // 契约 A 优先级：Down(4) > HitReaction(3) > 一次性(2) > Defend(1) > locomotion(0)
        public readonly float Fade;           // CrossFade 融合时长 s（规格 §七：locomotion 0.12 / 动作类 0.10 / Jump 0.06）
        public readonly string ClipFbxPath;   // null = 无资产锚（L2 登记期或待导入填写）

        public ActionEntry(string id, string displayName, ActionCategory category, int level,
                           bool loop, int priority, float fade, string clipFbxPath)
        {
            Id = id;
            DisplayName = displayName;
            Category = category;
            Level = level;
            Loop = loop;
            Priority = priority;
            Fade = fade;
            ClipFbxPath = clipFbxPath;
        }
    }

    /// <summary>
    /// 动作目录：12 词条（L1=9 + L2=3）。
    /// 数值说明：fade 默认值来源 动作库规格.md §七（0.06–0.15，locomotion 0.12 / 动作类 0.10）。
    /// clipFbxPath 说明：KI 路径与 KiWalkerLabBuilder 一致（用户本机导入位置，工程先例）；
    /// Mixamo 路径 = 规格 §五 约定（Assets/Animations/Mixamo/Combat/<id>.fbx，复制时改名 = 词表 id）。
    /// </summary>
    public static class ActionCatalog
    {
        public const string IdleFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Idles/HumanM@Idle01.fbx";
        public const string WalkFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Walk/HumanM@Walk01_Forward.fbx";
        public const string RunFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Run/HumanM@Run01_Forward.fbx";
        public const string JumpFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Jump/HumanM@Jump01.fbx";
        public const string MixamoCombatDir = "Assets/Animations/Mixamo/Combat/";

        private static readonly ActionEntry[] AllEntries =
        {
            // L1 locomotion
            new ActionEntry(ActionIds.Idle, "待机", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipFbxPath: IdleFbx),
            new ActionEntry(ActionIds.Walk, "走", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipFbxPath: WalkFbx),
            new ActionEntry(ActionIds.Run, "跑", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipFbxPath: RunFbx),
            new ActionEntry(ActionIds.Jump, "跳", ActionCategory.Locomotion, 1, loop: false, priority: 0, fade: 0.06f, clipFbxPath: JumpFbx),
            // L1 combat
            new ActionEntry(ActionIds.PhysicalAttack, "物攻", ActionCategory.Combat, 1, loop: false, priority: 2, fade: 0.10f, clipFbxPath: MixamoCombatDir + ActionIds.PhysicalAttack + ".fbx"),
            new ActionEntry(ActionIds.MentalAttack, "精攻", ActionCategory.Combat, 1, loop: false, priority: 2, fade: 0.10f, clipFbxPath: MixamoCombatDir + ActionIds.MentalAttack + ".fbx"),
            new ActionEntry(ActionIds.Defend, "防御", ActionCategory.Combat, 1, loop: true, priority: 1, fade: 0.10f, clipFbxPath: MixamoCombatDir + ActionIds.Defend + ".fbx"),
            // L1 reaction
            new ActionEntry(ActionIds.HitReaction, "受击", ActionCategory.Reaction, 1, loop: false, priority: 3, fade: 0.10f, clipFbxPath: MixamoCombatDir + ActionIds.HitReaction + ".fbx"),
            new ActionEntry(ActionIds.Down, "倒下", ActionCategory.Reaction, 1, loop: false, priority: 4, fade: 0.10f, clipFbxPath: MixamoCombatDir + ActionIds.Down + ".fbx"),
            // L2 登记（不接线；clipFbxPath 资产锚在 L2→L1 迁移时填写）
            new ActionEntry(ActionIds.Sit, "坐", ActionCategory.Interaction, 2, loop: false, priority: 0, fade: 0.10f, clipFbxPath: null),
            new ActionEntry(ActionIds.Stand, "站起", ActionCategory.Interaction, 2, loop: false, priority: 0, fade: 0.10f, clipFbxPath: null),
            new ActionEntry(ActionIds.Talk, "对话言语", ActionCategory.Social, 2, loop: true, priority: 0, fade: 0.12f, clipFbxPath: null),
        };

        private static readonly Dictionary<string, ActionEntry> ById = BuildIndex();

        private static Dictionary<string, ActionEntry> BuildIndex()
        {
            var d = new Dictionary<string, ActionEntry>(AllEntries.Length);
            foreach (var e in AllEntries) d[e.Id] = e;
            return d;
        }

        /// <summary>全部 12 词条（目录顺序）。</summary>
        public static IReadOnlyList<ActionEntry> All => AllEntries;

        /// <summary>L1 落地 9 词条（controller 接线集）。</summary>
        public static IReadOnlyList<ActionEntry> Level1 => _level1 ??= BuildLevel1();

        /// <summary>L2 登记 3 词条。</summary>
        public static IReadOnlyList<ActionEntry> Level2 => _level2 ??= BuildLevel2();

        private static IReadOnlyList<ActionEntry> _level1;
        private static IReadOnlyList<ActionEntry> _level2;

        private static IReadOnlyList<ActionEntry> BuildLevel1()
        {
            var list = new List<ActionEntry>();
            foreach (var e in AllEntries) if (e.Level == 1) list.Add(e);
            return list;
        }

        private static IReadOnlyList<ActionEntry> BuildLevel2()
        {
            var list = new List<ActionEntry>();
            foreach (var e in AllEntries) if (e.Level == 2) list.Add(e);
            return list;
        }

        public static bool TryGet(string id, out ActionEntry entry) => ById.TryGetValue(id, out entry);

        public static ActionEntry Get(string id)
        {
            if (!TryGet(id, out var e)) throw new System.ArgumentException("词表外动作 id: " + id + "（新增须走扩展协议）");
            return e;
        }
    }
}
