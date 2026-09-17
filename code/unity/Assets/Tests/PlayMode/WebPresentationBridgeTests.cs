using NUnit.Framework;
using UnityEngine;
using YANTF.Web;

namespace YANTF.Demo.Tests
{
    public sealed class WebPresentationBridgeTests
    {
        private GameObject _host;
        private WebPresentationBridge _bridge;

        [SetUp]
        public void SetUp()
        {
            _host = new GameObject("WebPresentationBridge Test");
            _bridge = _host.AddComponent<WebPresentationBridge>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_host);
        }

        [Test]
        public void Receive_InputModeSet_ChangesWorldInputState()
        {
            Assert.IsTrue(_bridge.WorldInputEnabled);

            _bridge.Receive("{\"v\":1,\"kind\":\"command\",\"type\":\"input.mode.set\",\"payload\":{\"mode\":\"ui\"}}");

            Assert.IsFalse(_bridge.WorldInputEnabled);
        }

        [Test]
        public void Receive_UnknownCommand_EmitsStructuredError()
        {
            string emitted = null;
            _bridge.MessageEmitted += message => emitted = message;

            _bridge.Receive("{\"v\":1,\"kind\":\"command\",\"type\":\"unknown\",\"requestId\":\"r1\",\"payload\":{}}");

            StringAssert.Contains("\"kind\":\"error\"", emitted);
            StringAssert.Contains("\"type\":\"runtime.error\"", emitted);
            StringAssert.Contains("\"requestId\":\"r1\"", emitted);
        }

        [Test]
        public void Receive_ChoiceSelection_EchoesWithoutNarrativeResolution()
        {
            string emitted = null;
            _bridge.MessageEmitted += message => emitted = message;

            _bridge.Receive("{\"v\":1,\"kind\":\"command\",\"type\":\"dialogue.choice.selected\",\"payload\":{\"choiceId\":\"choice-01\"}}");

            StringAssert.Contains("\"kind\":\"snapshot\"", emitted);
            StringAssert.Contains("\"choiceId\":\"choice-01\"", emitted);
        }
    }
}
