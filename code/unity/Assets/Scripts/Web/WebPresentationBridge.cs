// Unity Web 的唯一跨浏览器消息接缝。
// 来源：design/presentation/Unity Web集成设计.md §四—§六。
using System;
using System.Runtime.InteropServices;
using UnityEngine;

namespace YANTF.Web
{
    [DisallowMultipleComponent]
    public sealed class WebPresentationBridge : MonoBehaviour
    {
        private const int ProtocolVersion = 1;
        private const string WorldMode = "world";
        private const string UiMode = "ui";

        [Serializable]
        private sealed class Envelope
        {
            public int v;
            public string kind;
            public string type;
            public string requestId;
            public Payload payload;
        }

        [Serializable]
        private sealed class Payload
        {
            public string mode;
            public string choiceId;
            public string code;
            public string message;
            public string adapter;
        }

        public static WebPresentationBridge Instance { get; private set; }

        public bool WorldInputEnabled => _inputMode == WorldMode;

        /// <summary>Editor 与测试适配器监听同一出站信封；WebGL 构建另经 .jslib 转发。</summary>
        public event Action<string> MessageEmitted;

        /// <summary>场景输入层只需订阅是否允许世界输入，不需要解析网页消息。</summary>
        public event Action<bool> WorldInputChanged;

        private string _inputMode = WorldMode;
        private bool _readyEmitted;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Debug.LogError("[WebBridge] 场景中只允许一个 WebPresentationBridge。", this);
                enabled = false;
                return;
            }
            Instance = this;
            gameObject.name = nameof(WebPresentationBridge);
        }

        private void Start() => EmitReady();

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        /// <summary>JavaScript 经 unityInstance.SendMessage 调用的唯一入站方法。</summary>
        public void Receive(string envelopeJson)
        {
            if (string.IsNullOrWhiteSpace(envelopeJson))
            {
                EmitError("invalid-envelope", "消息不能为空。", null);
                return;
            }

            Envelope envelope;
            try
            {
                envelope = JsonUtility.FromJson<Envelope>(envelopeJson);
            }
            catch (Exception exception)
            {
                EmitError("invalid-json", exception.Message, null);
                return;
            }

            if (envelope == null || envelope.v != ProtocolVersion)
            {
                EmitError("unsupported-version", "不支持的消息协议版本。", envelope?.requestId);
                return;
            }
            if (envelope.kind != "command" || string.IsNullOrEmpty(envelope.type))
            {
                EmitError("invalid-envelope", "Unity 只接受带 type 的 command。", envelope.requestId);
                return;
            }

            switch (envelope.type)
            {
                case "input.mode.set":
                    SetInputMode(envelope.payload?.mode, envelope.requestId);
                    break;
                case "dialogue.choice.selected":
                    EchoDialogueChoice(envelope.payload?.choiceId, envelope.requestId);
                    break;
                default:
                    EmitError("unknown-command", "未知命令：" + envelope.type, envelope.requestId);
                    break;
            }
        }

        private void EmitReady()
        {
            if (_readyEmitted) return;
            _readyEmitted = true;
            Emit(new Envelope
            {
                v = ProtocolVersion,
                kind = "event",
                type = "runtime.ready",
                payload = new Payload { adapter = "unity-web" }
            });
        }

        private void SetInputMode(string mode, string requestId)
        {
            if (mode != WorldMode && mode != UiMode)
            {
                EmitError("invalid-input-mode", "input mode 必须是 world 或 ui。", requestId);
                return;
            }
            if (_inputMode == mode) return;

            _inputMode = mode;
            WorldInputChanged?.Invoke(WorldInputEnabled);
        }

        private void EchoDialogueChoice(string choiceId, string requestId)
        {
            if (string.IsNullOrEmpty(choiceId))
            {
                EmitError("invalid-choice", "choiceId 不能为空。", requestId);
                return;
            }

            // 阶段 A 只证明消息往返，不执行剧情判定。
            Emit(new Envelope
            {
                v = ProtocolVersion,
                kind = "snapshot",
                type = "dialogue.choice.selected",
                requestId = requestId,
                payload = new Payload { choiceId = choiceId }
            });
        }

        private void EmitError(string code, string message, string requestId)
        {
            Emit(new Envelope
            {
                v = ProtocolVersion,
                kind = "error",
                type = "runtime.error",
                requestId = requestId,
                payload = new Payload { code = code, message = message }
            });
        }

        private void Emit(Envelope envelope)
        {
            string json = JsonUtility.ToJson(envelope);
            MessageEmitted?.Invoke(json);

#if UNITY_WEBGL && !UNITY_EDITOR
            YantfWebEmit(json);
#else
            Debug.Log("[WebBridge] " + json, this);
#endif
        }

#if UNITY_WEBGL && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void YantfWebEmit(string envelopeJson);
#endif
    }
}
