// 动作目录（规格 §二/§3.2；机器源唯一真相）
// 词条元数据：category / level / loop / priority / fade / clipAssetPath / nextState（资产存在性 → 防漂移分档）。
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
    /// clipAssetPath：该词条 clip 所在资产路径——FBX（取其中第一个 AnimationClip）或 .anim 派生件（直接取）；
    /// 资产是否存在 = "现成/缺口" 的机器判据，缺口时状态仍建、clip 留空。
    /// nextState：一次性动作播完后要切到的状态名；null = 回退 locomotion 目标态。
    ///   （用于 Sit → SitIdle：坐下播完要"坐住"，而不是弹回站姿。）
    /// </summary>
    public sealed class ActionEntry
    {
        public readonly string Id;
        public readonly string DisplayName;   // 中文呈现词（HUD/日志）
        public readonly ActionCategory Category;
        public readonly int Level;            // 1 = L1 落地（接线）；2 = L2 登记（不接线）
        public readonly bool Loop;            // 循环（Idle/Walk/Run/Defend/SitIdle）；false = 一次性
        public readonly int Priority;         // 契约 A 优先级：Down(4) > HitReaction(3) > 一次性(2) > 持续态(1) > locomotion(0)
        public readonly float Fade;           // CrossFade 融合时长 s（规格 §七：locomotion 0.12 / 动作类 0.10 / Jump 0.06）
        public readonly string ClipAssetPath; // null = 无资产锚（L2 登记期或待导入填写）
        public readonly string NextState;     // 一次性动作播完切到的状态；null = 回退 locomotion

        public ActionEntry(string id, string displayName, ActionCategory category, int level,
                           bool loop, int priority, float fade, string clipAssetPath,
                           string nextState = null)
        {
            Id = id;
            DisplayName = displayName;
            Category = category;
            Level = level;
            Loop = loop;
            Priority = priority;
            Fade = fade;
            ClipAssetPath = clipAssetPath;
            NextState = nextState;
        }
    }

    /// <summary>
    /// 动作目录：13 词条（L1=12 + L2=1）。
    /// 数值说明：fade 默认值来源 规格 §七（0.06–0.15，locomotion 0.12 / 动作类 0.10）。
    /// 路径说明：KI 路径与 KiWalkerLabBuilder 一致（用户本机导入位置，工程先例；已知作废项，归 #139）；
    /// Mixamo 路径 = 规格 §五 约定（Assets/Animations/Mixamo/...）；派生件 = 规格 §五 派生件约定
    /// （Assets/Animations/Derived/，由 DerivedClipBuilder 非破坏生成）。
    /// </summary>
    public static class ActionCatalog
    {
        // ---- locomotion 4 条：仍锚 KI 包（已知作废项，#139 整条切 Mixamo 后由生成表取代）----
        public const string IdleFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Idles/HumanM@Idle01.fbx";
        public const string WalkFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Walk/HumanM@Walk01_Forward.fbx";
        public const string RunFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Run/HumanM@Run01_Forward.fbx";
        public const string JumpFbx = "Assets/Kevin Iglesias/Human Animations/Animations/Male/Movement/Jump/HumanM@Jump01.fbx";

        // ---- 战斗/反应 5 条：Mixamo 下载件 ----
        public const string MixamoCombatDir = "Assets/Animations/Mixamo/Combat/";

        // ---- 坐立三段（同源，见规格 §二 修正块）----
        /// <summary>坐下段：`Sit To Stand.fbx` 的**反转派生件**（与 SitIdle / Stand 同坐姿基准，接缝 ≤1.9 mm）。</summary>
        public const string SitDownDerived = "Assets/Animations/Derived/SitDown.anim";
        /// <summary>坐姿待机循环（SitIdle）。</summary>
        public const string SittingIdleFbx = "Assets/Animations/Mixamo/Sitting Idle.fbx";
        /// <summary>站起 + 派生件之源。</summary>
        public const string SitToStandFbx = "Assets/Animations/Mixamo/Sit To Stand.fbx";
        /// <summary>未经采用的坐下原件：其坐姿端与另两条不同族（踝前后差 149 mm、膝角差 17.6°），见规格 §二 修正块。</summary>
        public const string StandToSitFbx = "Assets/Animations/Mixamo/Stand To Sit.fbx";

        private static readonly ActionEntry[] AllEntries =
        {
            // L1 locomotion
            new ActionEntry(ActionIds.Idle, "待机", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipAssetPath: IdleFbx),
            new ActionEntry(ActionIds.Walk, "走", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipAssetPath: WalkFbx),
            new ActionEntry(ActionIds.Run, "跑", ActionCategory.Locomotion, 1, loop: true, priority: 0, fade: 0.12f, clipAssetPath: RunFbx),
            new ActionEntry(ActionIds.Jump, "跳", ActionCategory.Locomotion, 1, loop: false, priority: 0, fade: 0.06f, clipAssetPath: JumpFbx),
            // L1 combat
            new ActionEntry(ActionIds.PhysicalAttack, "物攻", ActionCategory.Combat, 1, loop: false, priority: 2, fade: 0.10f, clipAssetPath: MixamoCombatDir + ActionIds.PhysicalAttack + ".fbx"),
            new ActionEntry(ActionIds.MentalAttack, "精攻", ActionCategory.Combat, 1, loop: false, priority: 2, fade: 0.10f, clipAssetPath: MixamoCombatDir + ActionIds.MentalAttack + ".fbx"),
            new ActionEntry(ActionIds.Defend, "防御", ActionCategory.Combat, 1, loop: true, priority: 1, fade: 0.10f, clipAssetPath: MixamoCombatDir + ActionIds.Defend + ".fbx"),
            // L1 reaction
            new ActionEntry(ActionIds.HitReaction, "受击", ActionCategory.Reaction, 1, loop: false, priority: 3, fade: 0.10f, clipAssetPath: MixamoCombatDir + ActionIds.HitReaction + ".fbx"),
            new ActionEntry(ActionIds.Down, "倒下", ActionCategory.Reaction, 1, loop: false, priority: 4, fade: 0.10f, clipAssetPath: MixamoCombatDir + ActionIds.Down + ".fbx"),
            // L1 interaction（坐立三段同源）
            new ActionEntry(ActionIds.Sit, "坐", ActionCategory.Interaction, 1, loop: false, priority: 2, fade: 0.10f,
                            clipAssetPath: SitDownDerived, nextState: ActionIds.SitIdle),
            new ActionEntry(ActionIds.SitIdle, "坐姿待机", ActionCategory.Interaction, 1, loop: true, priority: 1, fade: 0.12f,
                            clipAssetPath: SittingIdleFbx),
            new ActionEntry(ActionIds.Stand, "站起", ActionCategory.Interaction, 1, loop: false, priority: 2, fade: 0.10f,
                            clipAssetPath: SitToStandFbx),
            // L2 登记（不接线；clipAssetPath 资产锚在 L2→L1 迁移时填写）
            new ActionEntry(ActionIds.Talk, "对话言语", ActionCategory.Social, 2, loop: true, priority: 0, fade: 0.12f, clipAssetPath: null),
        };

        private static readonly Dictionary<string, ActionEntry> ById = BuildIndex();

        private static Dictionary<string, ActionEntry> BuildIndex()
        {
            var d = new Dictionary<string, ActionEntry>(AllEntries.Length);
            foreach (var e in AllEntries) d[e.Id] = e;
            return d;
        }

        /// <summary>全部 13 词条（目录顺序）。</summary>
        public static IReadOnlyList<ActionEntry> All => AllEntries;

        /// <summary>L1 落地 12 词条（controller 接线集）。</summary>
        public static IReadOnlyList<ActionEntry> Level1 => _level1 ??= BuildLevel1();

        /// <summary>L2 登记 1 词条。</summary>
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
