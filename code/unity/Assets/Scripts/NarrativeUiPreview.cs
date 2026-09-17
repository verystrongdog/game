// 叙事 UI 的纯展示壳。
// 只在 ActionLab 运行时挂载静态 UXML/USS，便于在 StoryEngine 接入前评审页面；
// 不读取剧情数据、不判定条件、不写回任何游戏状态。
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

namespace YANTF.NarrativeUI
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(UIDocument))]
    public sealed class NarrativeUiPreview : MonoBehaviour
    {
        private const string SceneName = "ActionLab";
        private const string VisualTreePath = "NarrativeUI/NarrativeHud";
        private const float NarrowWidth = 1050f;
        private const float CompactHeight = 760f;

        private UIDocument _document;
        private PanelSettings _ownedPanelSettings;
        private VisualElement _shell;
        private VisualElement _dialoguePage;
        private VisualElement _notebookPage;
        private Button _dialogueTab;
        private Button _notebookTab;

        /// <summary>供旧 IMGUI HUD 避让；不代表剧情会话状态。</summary>
        public static bool IsVisible { get; private set; }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void MountInActionLab()
        {
            if (SceneManager.GetActiveScene().name != SceneName) return;
            if (FindFirstObjectByType<NarrativeUiPreview>() != null) return;

            var visualTree = Resources.Load<VisualTreeAsset>(VisualTreePath);
            var styleSheet = Resources.Load<StyleSheet>(VisualTreePath);
            if (visualTree == null || styleSheet == null)
            {
                Debug.LogError("[NarrativeUI] 找不到展示资源 Resources/" + VisualTreePath + ".uxml/.uss");
                return;
            }

            var host = new GameObject("Narrative UI Preview");
            host.SetActive(false);

            var panelSettings = ScriptableObject.CreateInstance<PanelSettings>();
            panelSettings.name = "Narrative UI Runtime Panel Settings";
            panelSettings.scaleMode = PanelScaleMode.ScaleWithScreenSize;
            panelSettings.referenceResolution = new Vector2Int(1920, 1080);
            panelSettings.match = 0.5f;

            var document = host.AddComponent<UIDocument>();
            document.panelSettings = panelSettings;
            document.visualTreeAsset = visualTree;
            document.sortingOrder = 100;

            var preview = host.AddComponent<NarrativeUiPreview>();
            preview._ownedPanelSettings = panelSettings;

            host.SetActive(true);
            document.rootVisualElement.styleSheets.Add(styleSheet);
        }

        private void OnEnable()
        {
            IsVisible = true;
            _document = GetComponent<UIDocument>();
            _shell = _document.rootVisualElement.Q<VisualElement>("narrative-shell");
            _dialoguePage = _document.rootVisualElement.Q<VisualElement>("dialogue-page");
            _notebookPage = _document.rootVisualElement.Q<VisualElement>("notebook-page");
            _dialogueTab = _document.rootVisualElement.Q<Button>("dialogue-tab");
            _notebookTab = _document.rootVisualElement.Q<Button>("notebook-tab");

            if (_shell == null || _dialoguePage == null || _notebookPage == null ||
                _dialogueTab == null || _notebookTab == null)
            {
                Debug.LogError("[NarrativeUI] UXML 层级不完整，展示页无法初始化。", this);
                enabled = false;
                return;
            }

            // 左侧是 3D 世界的透明观察窗，不应吞掉镜头拖拽或世界交互。
            var worldPane = _shell.Q<VisualElement>("world-pane");
            if (worldPane != null)
            {
                worldPane.Query<VisualElement>().ForEach(element => element.pickingMode = PickingMode.Ignore);
            }

            _dialogueTab.clicked += ShowDialogue;
            _notebookTab.clicked += ShowNotebook;
            _shell.RegisterCallback<GeometryChangedEvent>(OnGeometryChanged);
            ApplyResponsiveClasses(_shell.resolvedStyle.width, _shell.resolvedStyle.height);
        }

        private void OnDisable()
        {
            IsVisible = false;
            if (_dialogueTab != null) _dialogueTab.clicked -= ShowDialogue;
            if (_notebookTab != null) _notebookTab.clicked -= ShowNotebook;
            if (_shell != null) _shell.UnregisterCallback<GeometryChangedEvent>(OnGeometryChanged);
        }

        private void OnDestroy()
        {
            if (_ownedPanelSettings != null) Destroy(_ownedPanelSettings);
        }

        private void ShowDialogue() => ShowPage(true);

        private void ShowNotebook() => ShowPage(false);

        private void ShowPage(bool dialogue)
        {
            _dialoguePage.EnableInClassList("is-hidden", !dialogue);
            _notebookPage.EnableInClassList("is-hidden", dialogue);
            _dialogueTab.EnableInClassList("rail-tab-active", dialogue);
            _notebookTab.EnableInClassList("rail-tab-active", !dialogue);
        }

        private void OnGeometryChanged(GeometryChangedEvent evt)
            => ApplyResponsiveClasses(evt.newRect.width, evt.newRect.height);

        private void ApplyResponsiveClasses(float width, float height)
        {
            _shell.EnableInClassList("narrow", width > 0f && width < NarrowWidth);
            _shell.EnableInClassList("compact", height > 0f && height < CompactHeight);
        }
    }
}
