// 运行时引导器 — 代码构建演示世界（Ground/Light/Camera/双方白盒人形/驱动/HUD）
// 供场景生成器（Editor SceneBuilder）与 PlayMode 测试复用；幂等（重复调用先清理）。
using UnityEngine;

namespace YANTF.Demo
{
    public sealed class DemoBootstrapper : MonoBehaviour
    {
        public DemoActor PlayerActor { get; private set; }
        public DemoActor EnemyActor { get; private set; }
        public DemoCombatDriver Driver { get; private set; }
        public DemoHud Hud { get; private set; }

        [Header("演示基线（镜像 CalibrationConfig.Default：玩家 50/80，杂兵 15/60）")]
        public float playerHp = 50f;
        public float playerSan = 80f;
        public float enemyHp = 15f;
        public float enemySan = 60f;

        private void Awake()
        {
            if (PlayerActor == null) BuildAll();
        }

        public void BuildAll()
        {
            ClearWorld();

            EnsureGroundAndLight();
            EnsureCamera();

            // ---- 双方白盒人形 ----
            PlayerActor = SpawnActor("Player(演示者)", new Vector3(0f, 0f, 0f), new Color(0.55f, 0.7f, 1f), playerHp, playerSan);
            EnemyActor = SpawnActor("Sparring(陪练)", new Vector3(5f, 0f, 2f), new Color(1f, 0.55f, 0.5f), enemyHp, enemySan);
            EnemyActor.transform.rotation = Quaternion.LookRotation(Vector3.back);

            // ---- 驱动 + HUD ----
            var driverGo = new GameObject("DemoCombatDriver");
            Driver = driverGo.AddComponent<DemoCombatDriver>();
            Driver.player = PlayerActor;
            Driver.enemy = EnemyActor;

            var hudGo = new GameObject("DemoHud");
            Hud = hudGo.AddComponent<DemoHud>();
            Hud.Init(Driver);

            PlayerActor.Logged += (actor, msg) => Debug.Log($"[沙盘] {actor.displayName}: {msg}");
            EnemyActor.Logged += (actor, msg) => Debug.Log($"[沙盘] {actor.displayName}: {msg}");
        }

        private DemoActor SpawnActor(string name, Vector3 pos, Color tint, float hp, float san)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            var actor = go.AddComponent<DemoActor>();
            var visualGo = new GameObject("Visual");
            visualGo.transform.SetParent(go.transform, false);
            var visual = visualGo.AddComponent<CharacterVisual>();
            visual.BuildWhitebox(tint);
            actor.Init(hp, san, name);
            return actor;
        }

        private void ClearWorld()
        {
            foreach (var name in new[] { "Ground", "Sun", "Player(演示者)", "Sparring(陪练)", "DemoCombatDriver", "DemoHud", "DemoHudCanvas" })
            {
                var go = GameObject.Find(name);
                if (go != null) Destroy(go);
            }
            var cam = Camera.main;
            if (cam != null && cam.GetComponent<DemoCameraTag>() == null) Destroy(cam.gameObject);
        }

        private static void EnsureGroundAndLight()
        {
            if (GameObject.Find("Ground") == null)
            {
                var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
                ground.name = "Ground";
                ground.transform.localScale = new Vector3(20f, 1f, 20f);
                ground.transform.position = new Vector3(0f, -0.01f, 0f);
            }
            if (GameObject.Find("Sun") == null)
            {
                var sunGo = new GameObject("Sun");
                var light = sunGo.AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 1.1f;
                sunGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            }
        }

        private static void EnsureCamera()
        {
            var cam = Camera.main;
            if (cam != null && cam.GetComponent<DemoCameraTag>() == null) return;
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            camGo.AddComponent<DemoCameraTag>();
            camGo.AddComponent<Camera>();
            camGo.AddComponent<AudioListener>();
            camGo.transform.position = new Vector3(6f, 4.2f, -7f);
            camGo.transform.rotation = Quaternion.Euler(24f, -32f, 0f);
        }
    }

    /// <summary>标记：ClearWorld 只删我们自己创建的相机（避免删掉用户场景相机）。</summary>
    public sealed class DemoCameraTag : MonoBehaviour { }
}
