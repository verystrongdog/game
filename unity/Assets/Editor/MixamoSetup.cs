// Mixamo 资产一键导入 + ActionLab 生成（Editor，Grilling #124 Batch1 执行工具）
// 职责（把 README §二·E 的手动步骤 1-3 收成一个菜单）：
//   ① 从下载目录复制 7 个 FBX 到工程（角色 → Assets/Mixamo/Characters/；5 条动画改名=词表 id → Assets/Animations/Mixamo/Combat/）
//   ② 全部设 Rig = Humanoid → Apply（SaveAndReimport）
//   ③ 调 ActionLabBuilder.CreateScene()：幂等建 12 态 controller（L1 9，按资产存在性挂 clip）+ X Bot 场景
// 用法：pull 后打开工程 → 菜单 YANTF → 动作演示 → 一键导入 Mixamo 资产并生成 ActionLab → Play 测试。
using System.IO;
using UnityEditor;
using UnityEngine;

namespace YANTF.EditorTools
{
    public static class MixamoSetup
    {
        /// <summary>下载源目录（用户本机；可改指向你的下载位置）。</summary>
        public const string SourceDir = @"C:\Users\9527\Downloads";

        /// <summary>源文件名 → 目标资产路径（目标文件名 = 词表 id 或角色名）。</summary>
        private static readonly (string src, string dest)[] Files =
        {
            // 载体角色（Rig Humanoid；Y Bot 备用）
            ("X Bot.fbx", "Assets/Mixamo/Characters/X Bot.fbx"),
            ("Y Bot.fbx", "Assets/Mixamo/Characters/Y Bot.fbx"),
            // 5 条战斗/反馈 clip（文件名 ≠ 语义，按 #124 实证映射改名）
            ("Jab Cross.fbx", "Assets/Animations/Mixamo/Combat/PhysicalAttack.fbx"),           // 物攻：直拳
            ("Charge.fbx", "Assets/Animations/Mixamo/Combat/MentalAttack.fbx"),                // 精攻：伸手指人（A 前指宣言）
            ("Short Left Side Step.fbx", "Assets/Animations/Mixamo/Combat/Defend.fbx"),        // 防御：循环格挡
            ("Head Hit.fbx", "Assets/Animations/Mixamo/Combat/HitReaction.fbx"),               // 受击
            ("Dying.fbx", "Assets/Animations/Mixamo/Combat/Down.fbx"),                         // 倒下
        };

        [MenuItem("YANTF/动作演示/一键导入 Mixamo 资产并生成 ActionLab（首次）")]
        public static void SetupAllMenu() => SetupAll();

        /// <summary>headless：Unity -batchmode -quit -executeMethod YANTF.EditorTools.MixamoSetup.SetupAllBatch</summary>
        public static void SetupAllBatch() => SetupAll();

        public static void SetupAll()
        {
            int copied = CopyFiles();
            if (copied == 0)
            {
                Debug.LogWarning("[MixamoSetup] 没有需要复制的文件（可能已导入）。继续 Rig 配置与场景生成……");
            }
            ConfigureHumanoidAll();
            ActionLabBuilder.CreateScene();
            Debug.Log("[MixamoSetup] 完成。打开 Assets/Scenes/ActionLab.unity → Play：WASD 走 / Shift 跑 / Space 跳 / 1物攻 2精攻 3防御 4受击 5倒下 / R 重置");
        }

        private static readonly string ProjectRoot =
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private static int CopyFiles()
        {
            int copied = 0;
            foreach (var (src, dest) in Files)
            {
                string fullSrc = Path.Combine(SourceDir, src);
                string fullDest = Path.Combine(ProjectRoot, dest);
                if (!File.Exists(fullSrc))
                {
                    Debug.LogWarning("[MixamoSetup] 源文件缺失（跳过）: " + fullSrc);
                    continue;
                }
                if (File.Exists(fullDest))
                {
                    Debug.Log("[MixamoSetup] 目标已存在（跳过复制，仍会重设 Rig）: " + dest);
                    continue;
                }
                Directory.CreateDirectory(Path.GetDirectoryName(fullDest));
                File.Copy(fullSrc, fullDest);
                copied++;
                Debug.Log("[MixamoSetup] 复制: " + src + " → " + dest);
            }
            if (copied > 0) AssetDatabase.Refresh(); // 让 Unity 生成 .meta 并首次导入
            return copied;
        }

        private static void ConfigureHumanoidAll()
        {
            foreach (var (_, dest) in Files)
            {
                var importer = AssetImporter.GetAtPath(dest) as ModelImporter;
                if (importer == null)
                {
                    Debug.LogWarning("[MixamoSetup] 找不到 importer（资产未导入?）: " + dest);
                    continue;
                }
                importer.animationType = ModelImporterAnimationType.Human;
                importer.SaveAndReimport();
                Debug.Log("[MixamoSetup] Rig=Humanoid: " + dest);
            }
        }
    }
}
