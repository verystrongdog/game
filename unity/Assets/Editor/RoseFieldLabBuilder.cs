// 玫瑰花海场景生成器（Editor）— Grilling #126
// 用法：菜单 YANTF → 玫瑰实验 → 创建玫瑰花海场景；或 headless:
//   Unity -batchmode -quit -executeMethod YANTF.EditorTools.RoseFieldLabBuilder.CreateRoseFieldSceneBatch
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using YANTF.RoseField;
using YANTF.WalkerLab;

namespace YANTF.EditorTools
{
    public static class RoseFieldLabBuilder
    {
        private const string ScenePath = "Assets/Scenes/RoseFieldLab.unity";

        [MenuItem("YANTF/玫瑰实验/创建玫瑰花海场景")]
        public static void CreateRoseFieldSceneMenu()
        {
            CreateRoseFieldScene();
        }

        public static void CreateRoseFieldScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // ---- 花海：地块高度场 + 六角错行株丛（Editor 模式实体化地面网格，保存进场景）----
            var labGo = new GameObject("RoseField(玫瑰花海)");
            var lab = labGo.AddComponent<RoseFieldLab>();
            lab.Build();

            // ---- 小人：出生在地块中心的地表上 ----
            Vector3 spawn = new Vector3(lab.fieldSize * 0.5f, 0f, lab.fieldSize * 0.5f);
            spawn.y = lab.Field.HeightAtWorld(spawn.x, spawn.z) + 0.15f;

            var walkerGo = new GameObject("Walker(小人)");
            walkerGo.transform.position = spawn;
            var cc = walkerGo.AddComponent<CharacterController>();
            cc.height = 1.85f;
            cc.radius = 0.35f;
            cc.center = new Vector3(0f, 0.92f, 0f);
            cc.slopeLimit = 45f;
            cc.stepOffset = 0.3f;
            var walker = walkerGo.AddComponent<WalkerController>();
            walker.BuildBody(new Color(0.95f, 0.82f, 0.35f)); // 暖黄，与玫瑰红/草地绿区分
            walker.followCamera = true;
            walker.cameraOffset = new Vector3(0f, 3.0f, -6.5f); // 略高于冠层，便于俯瞰花海
            walkerGo.transform.position = spawn;
            lab.walkerView = walkerGo.transform;

            // ---- 平行光 ----
            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.15f;
            sun.color = new Color(1f, 0.96f, 0.88f);
            sunGo.transform.rotation = Quaternion.Euler(42f, -35f, 0f);

            // ---- 相机 ----
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            camGo.transform.position = spawn + new Vector3(0f, 3.0f, -6.5f);
            camGo.transform.rotation = Quaternion.Euler(14f, 0f, 0f);

            if (!Directory.Exists("Assets/Scenes")) Directory.CreateDirectory("Assets/Scenes");
            // 关掉「失焦暂停」：编辑器窗口失去焦点时若不后台运行，玩家循环会冻结（Update 不再执行），
            // 场景看起来正常但动态内容全停 —— 现场排查过一次，代价很大。
            PlayerSettings.runInBackground = true;
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"[YANTF] 玫瑰花海场景已保存: {ScenePath}\n" +
                      $"  株数 {lab.RosePositions.Length} / 密度 {lab.PlantsPerMu:F0} 株/亩 / 错行间距 {lab.latticeSpacing:F3} m\n" +
                      $"  蓬径 {lab.roseCanopyDiameter:F2} m / 全覆盖判据 {lab.MinCanopyForFullCoverage:F3} m → " +
                      (lab.IsFullCoverage ? "覆盖率 1.0" : "覆盖率 < 1") +
                      $"\n  地块 {lab.fieldSize:F0}×{lab.fieldSize:F0} m / 高差 {lab.Field.Relief:F4} m\n" +
                      "  打开后按 Play（WASD 走 / Shift 跑 / Space 跳）");
        }

        /// <summary>headless 批量入口（-executeMethod）。</summary>
        public static void CreateRoseFieldSceneBatch()
        {
            CreateRoseFieldScene();
        }
    }
}
