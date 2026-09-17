// Unity Web 的唯一 JavaScript 出站适配器。
// 来源：design/presentation/Unity Web集成设计.md §四·2；
//       docs/reference/unity-webgl.md §七（.jslib 必须使用 ES5 语法）。
mergeInto(LibraryManager.library, {
  YantfWebEmit: function (envelopePtr) {
    var envelopeJson = UTF8ToString(envelopePtr);
    var bridge = window.yantfUnityBridge;
    if (bridge && typeof bridge.emit === 'function') {
      bridge.emit(envelopeJson);
      return;
    }
    console.error('[WebBridge] No active SceneHost for Unity message:', envelopeJson);
  }
});
