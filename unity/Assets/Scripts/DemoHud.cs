// 演示 HUD（Grilling #122 Q7 UI 集）— 代码构建，uGUI Canvas
// 布局对齐 呈现/战斗界面布局.md §4 底部 HUD 雏形：
//   左下状态面板（HP/SAN 条+数值、防御/冷却/倒地状态标签）
//   右下行动栏（1/2/3 按钮 + 执行回合 + 重置）＋ 冷却灰显
//   日志区（最近事件）+ 受击浮动数字（红=HP 物理、蓝=SAN）
// ⚠️ 陪练头顶精确 HP/SAN 为调试显示（验证引擎结算），不代表正典敌方模糊信息规则（§3.8）。
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace YANTF.Demo
{
    public sealed class DemoHud : MonoBehaviour
    {
        private DemoCombatDriver _driver;
        private DemoActor _player;

        private Text _nameText, _hpText, _sanText, _statusText;
        private Image _hpFill, _sanFill;
        private Text _enemyDebugText, _logText;
        private Button _defendBtn;

        private readonly List<string> _logLines = new List<string>();
        private const int MaxLogLines = 6;

        public void Init(DemoCombatDriver driver)
        {
            _driver = driver;
            _player = driver.player;
            BuildCanvas();
            Bind();
        }

        private void Bind()
        {
            _driver.Logged += OnLog;
            _driver.StatsChanged += Refresh;
            _player.Changed += OnActorChanged;
            _driver.enemy.Changed += OnEnemyChanged;
            Refresh();
        }

        private void BuildCanvas()
        {
            var canvasGo = new GameObject("DemoHudCanvas");
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            canvasGo.AddComponent<GraphicRaycaster>();

            // ---- 左下：状态面板 ----
            var panel = MakePanel(canvasGo.transform, "PlayerPanel", new Vector2(30f, -560f), new Vector2(420f, 150f));
            _nameText = MakeText(panel, "Name", new Vector2(12f, 108f), new Vector2(396f, 30f), 22, TextAnchor.MiddleLeft);
            _hpText = MakeText(panel, "HpText", new Vector2(12f, 78f), new Vector2(396f, 24f), 18, TextAnchor.MiddleLeft);
            _sanText = MakeText(panel, "SanText", new Vector2(12f, 44f), new Vector2(396f, 24f), 18, TextAnchor.MiddleLeft);
            _statusText = MakeText(panel, "Status", new Vector2(12f, 12f), new Vector2(396f, 22f), 16, TextAnchor.MiddleLeft);

            // HP/SAN 条（数值文字右侧显示条）
            _hpFill = MakeBar(panel, "HpBar", new Vector2(260f, 80f), new Vector2(148f, 18f), new Color(0.75f, 0.2f, 0.2f));
            _sanFill = MakeBar(panel, "SanBar", new Vector2(260f, 46f), new Vector2(148f, 18f), new Color(0.25f, 0.45f, 0.8f));

            // ---- 右下：行动栏 ----
            var actionPanel = MakePanel(canvasGo.transform, "ActionPanel", new Vector2(1210f, -560f), new Vector2(680f, 150f));
            float y = 100f;
            MakeButton(actionPanel, "物理攻击 (1)", new Vector2(20f, y), new Vector2(200f, 40f), () => _driver.QueueAction(DemoActionKind.PhysicalAttack));
            _defendBtn = MakeButton(actionPanel, "防御 (2)", new Vector2(240f, y), new Vector2(200f, 40f), () => _driver.QueueAction(DemoActionKind.Defend));
            MakeButton(actionPanel, "精神攻击 (3)", new Vector2(460f, y), new Vector2(200f, 40f), () => _driver.QueueAction(DemoActionKind.MentalAttack));
            MakeButton(actionPanel, "执行回合 (Space)", new Vector2(20f, 48f), new Vector2(300f, 40f), () => _driver.ExecuteRound());
            MakeButton(actionPanel, "重置 (R)", new Vector2(340f, 48f), new Vector2(140f, 40f), () => _driver.ResetFight());

            // ---- 顶部右侧：陪练调试数值 ----
            var enemyPanel = MakePanel(canvasGo.transform, "EnemyDebug", new Vector2(1240f, 30f), new Vector2(650f, 70f));
            _enemyDebugText = MakeText(enemyPanel, "EnemyDebugText", new Vector2(12f, 14f), new Vector2(620f, 42f), 22, TextAnchor.MiddleRight);
            _enemyDebugText.color = new Color(0.9f, 0.6f, 0.6f);

            // ---- 底部中：日志 ----
            _logText = MakeText(canvasGo.transform, "Log", new Vector2(560f, -880f), new Vector2(800f, 160f), 17, TextAnchor.LowerLeft);
            _logText.alignment = TextAnchor.LowerLeft;
            _logText.color = new Color(0.9f, 0.9f, 0.85f);
        }

        // ---- 事件 ----
        private void OnLog(string s)
        {
            _logLines.Add(s);
            while (_logLines.Count > MaxLogLines) _logLines.RemoveAt(0);
            _logText.text = string.Join("\n", _logLines);
        }

        private void OnActorChanged(DemoActor actor, float hp, float san)
        {
            Refresh();
        }

        private void OnEnemyChanged(DemoActor actor, float hp, float san)
        {
            _enemyDebugText.text = $"[调试] {actor.displayName}  HP {hp:F1}/{actor.hpMax:F1}  SAN {san:F1}/{actor.sanMax:F1}";
            Refresh();
        }

        private void Refresh()
        {
            if (_player == null) return;
            _nameText.text = _player.displayName;
            _hpText.text = $"HP {_player.Hp:F1}/{_player.hpMax:F1}";
            _sanText.text = $"SAN {_player.San:F1}/{_player.sanMax:F1}";
            _hpFill.fillAmount = _player.hpMax <= 0f ? 0f : Mathf.Clamp01(_player.Hp / _player.hpMax);
            _sanFill.fillAmount = _player.sanMax <= 0f ? 0f : Mathf.Clamp01(_player.San / _player.sanMax);
            var tags = new List<string>();
            if (_player.Defending) tags.Add("防御中 (物理-50%)");
            if (_player.DefenseCooldown > 0) tags.Add($"防御冷却 {_player.DefenseCooldown}");
            if (_player.Down) tags.Add("被击倒");
            if (_driver != null)
            {
                tags.Add($"第 {_driver.RoundNumber} 回合");
                tags.Add(_driver.M1Selection == DemoActionKind.None ? "M1: 未选" : $"M1: {_driver.M1Selection}");
                tags.Add(_driver.BrocaSelection == DemoActionKind.None ? "Broca: 未选" : "Broca: 精神攻击");
            }
            _statusText.text = string.Join("  |  ", tags);
            if (_defendBtn != null) _defendBtn.interactable = _player.CanDefend;
        }

        // ---- 控件工厂 ----
        private static RectTransform MakePanel(Transform parent, string name, Vector2 pos, Vector2 size)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = go.GetComponent<Image>();
            img.color = new Color(0f, 0f, 0f, 0.55f);
            return rt;
        }

        private static Text MakeText(Transform parent, string name, Vector2 pos, Vector2 size, int fontSize, TextAnchor align)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var text = go.GetComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = align;
            text.color = Color.white;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            return text;
        }

        private static Image MakeBar(Transform parent, string name, Vector2 pos, Vector2 size, Color color)
        {
            var go = new GameObject(name, typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = go.GetComponent<Image>();
            img.type = Image.Type.Filled;
            img.fillMethod = Image.FillMethod.Horizontal;
            img.color = color;
            return img;
        }

        private static Button MakeButton(Transform parent, string label, Vector2 pos, Vector2 size, UnityEngine.Events.UnityAction onClick)
        {
            var go = new GameObject(label, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            var img = go.GetComponent<Image>();
            img.color = new Color(0.18f, 0.18f, 0.22f, 0.9f);
            var btn = go.GetComponent<Button>();
            var colors = btn.colors;
            colors.highlightedColor = new Color(0.3f, 0.3f, 0.38f, 0.9f);
            btn.colors = colors;
            btn.onClick.AddListener(onClick);
            MakeText(go.transform, "label", Vector2.zero, size, 18, TextAnchor.MiddleCenter);
            return btn;
        }
    }
}
