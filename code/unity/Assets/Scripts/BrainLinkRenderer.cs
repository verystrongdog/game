// 大脑视图（YANTF.BrainView）— 链路渲染：三体边 → 单个 Mesh（LineTopology）+ 共享材质
//
// 为什么是单个 Mesh 而不是 1049 个 GameObject/LineRenderer：后者就是 1049 个 draw call 与
// 逐对象材质实例——正是 v2 世代 .blend「238 个逐对象材质」的翻版（脑模型资产登记.md §三）。
//
// 口径与数值来源：
//   design/presentation/visualization-3d/Unity接入设计.md §3.3 连线（四类原语分别渲染）
//   §3.4 染色：色相 = primary_network（14 网络 → 14 色相带，环绕色环均分，来源 §3.2 / D19+D23）
//              脑干广播 = 独立中性色系（D29）；CSTC 环路 = 同族中性色（本条口径，正典未定其色）
//   data/connectivity/tripartite_model.json — graph_nodes[*].mni_xyz + 四类边数组
//   data/connectivity/link_contexts_tripartite.json — edge_contexts[id].networks[0]（primary_network）
//   data/connectivity/kroell14_networks.json — 14 网络的名称→序号
//
// 坐标口径（实测，见 Unity接入设计 §8.5 与 2026-09-13 直驱实测）：
//   资产以 MNI 轴向存储，单位毫米；资产空间 = (−mni_X, mni_Y, mni_Z)。
//   本组件把顶点直接写在该空间里，与脑壳网格同空间 → 两者由同一个根变换统一取向与缩放。
using System.Collections.Generic;
using System.Globalization;   // MiniJson：数字解析用不变文化
using System.IO;
using System.Text;          // MiniJson：字符串缓冲
using UnityEngine;

namespace YANTF.BrainView
{
    /// <summary>一条待渲染的链路：两端点（资产空间，毫米）+ 材质槽。</summary>
    public struct BrainLink
    {
        public Vector3 a;
        public Vector3 b;
        public int slot;
    }

    public class BrainLinkRenderer : MonoBehaviour
    {
        /// <summary>材料槽 0..13 = 14 个网络色相；14 = 脑干广播中性；15 = CSTC 环路中性。</summary>
        public const int NetworkSlots = 14;
        public const int BrainstemSlot = 14;
        public const int CstcSlot = 15;
        public const int TotalSlots = 16;

        private const float HueSaturation = 0.65f;   // 呈现层取值（可调）：足够区分 14 个色相带
        private const float HueValue = 0.95f;

        private Mesh _mesh;
        private readonly List<Material> _materials = new List<Material>();

        public int LinkCount { get; private set; }
        public int SubmeshCount => _mesh != null ? _mesh.subMeshCount : 0;
        public int MaterialCount => _materials.Count;
        public Bounds LocalBounds => _mesh != null ? _mesh.bounds : new Bounds();

        /// <summary>把链路写进一个 Mesh：每边 2 个顶点，按材质槽分组为 16 个 submesh。</summary>
        public void Build(List<BrainLink> links)
        {
            var mesh = new Mesh { name = "BrainLinks" };
            mesh.indexFormat = links.Count * 2 > 65000
                ? UnityEngine.Rendering.IndexFormat.UInt32
                : UnityEngine.Rendering.IndexFormat.UInt16;

            var verts = new Vector3[links.Count * 2];
            var perSlot = new List<int>[TotalSlots];
            for (int s = 0; s < TotalSlots; s++) perSlot[s] = new List<int>();
            for (int i = 0; i < links.Count; i++)
            {
                verts[i * 2] = links[i].a;
                verts[i * 2 + 1] = links[i].b;
                int slot = Mathf.Clamp(links[i].slot, 0, TotalSlots - 1);
                perSlot[slot].Add(i * 2);
                perSlot[slot].Add(i * 2 + 1);
            }
            mesh.vertices = verts;
            mesh.subMeshCount = TotalSlots;
            for (int s = 0; s < TotalSlots; s++)
                mesh.SetIndices(perSlot[s].ToArray(), MeshTopology.Lines, s);
            mesh.RecalculateBounds();

            _mesh = mesh;
            LinkCount = links.Count;

            var mf = GetComponent<MeshFilter>();
            if (mf == null) mf = gameObject.AddComponent<MeshFilter>();
            mf.sharedMesh = mesh;
            var mr = GetComponent<MeshRenderer>();
            if (mr == null) mr = gameObject.AddComponent<MeshRenderer>();

            _materials.Clear();
            for (int s = 0; s < TotalSlots; s++) _materials.Add(SharedMaterial(s));
            mr.sharedMaterials = _materials.ToArray();
            mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            mr.receiveShadows = false;
        }

        /// <summary>槽位 → 共享材质（14 网络色相 + 2 中性）；同一槽永远复用同一个材质实例。</summary>
        private static readonly Dictionary<int, Material> _shared = new Dictionary<int, Material>();

        public static Material SharedMaterial(int slot)
        {
            if (_shared.TryGetValue(slot, out var cached) && cached != null) return cached;
            Color c;
            string name;
            if (slot < NetworkSlots)
            {
                // 14 色相带环绕色环均分（来源：§3.2「14 Kroell 网络 → 14 色相带，环绕色环均分」）
                c = Color.HSVToRGB((float)slot / NetworkSlots, HueSaturation, HueValue);
                name = $"brainlink_net{slot:00}";
            }
            else if (slot == BrainstemSlot)
            {
                c = new Color(0.42f, 0.50f, 0.60f);   // 灰蓝（D29：脑干链路独立中性色系）
                name = "brainlink_brainstem";
            }
            else
            {
                c = new Color(0.72f, 0.62f, 0.45f);   // 中性暖灰：与网络色相、脑干灰蓝都区分
                name = "brainlink_cstc";
            }
            var mat = new Material(Shader.Find("Unlit/Color")) { name = name };
            mat.color = c;
            _shared[slot] = mat;
            return mat;
        }

        /// <summary>仓库根（Editor 与 PlayMode 测试都用它定位 data/）。</summary>
        // 仓库根 = Assets 上三层（Assets → code/unity → code → 仓库根），2026-09-13 实测修正
        public static string RepoRoot => Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));

        /// <summary>读三体边 + 上下文归属，产出待渲染链路。<paramref name="log"/> 为 null 时静默。</summary>
        public static List<BrainLink> LoadLinksFromRepo(string repoRoot, List<string> log = null)
        {
            var links = new List<BrainLink>();
            var tm = (Dictionary<string, object>)MiniJson.Parse(
                File.ReadAllText(Path.Combine(repoRoot, "data/connectivity/tripartite_model.json")));
            var nodes = (Dictionary<string, object>)tm["graph_nodes"];

            var networkIndex = new Dictionary<string, int>();
            var kn = (Dictionary<string, object>)MiniJson.Parse(
                File.ReadAllText(Path.Combine(repoRoot, "data/connectivity/kroell14_networks.json")));
            var nets = (List<object>)kn["networks"];
            for (int i = 0; i < nets.Count; i++)
            {
                var n = (Dictionary<string, object>)nets[i];
                networkIndex[(string)n["name"]] = i;
            }

            var edgeNetworks = new Dictionary<string, string>();
            var lt = (Dictionary<string, object>)MiniJson.Parse(
                File.ReadAllText(Path.Combine(repoRoot, "data/connectivity/link_contexts_tripartite.json")));
            foreach (var kv in (Dictionary<string, object>)lt["edge_contexts"])
            {
                var e = (Dictionary<string, object>)kv.Value;
                var ns = e.TryGetValue("networks", out var nsv) ? nsv as List<object> : null;
                if (ns != null && ns.Count > 0) edgeNetworks[kv.Key] = (string)ns[0];
            }

            foreach (var spec in new[]
            {
                ("corticocortical", "cc"), ("privileged_pathways", "pp"),
                ("brainstem", "bs"), ("cstc", "cstc"),
            })
            {
                if (!tm.TryGetValue(spec.Item1, out var raw) || !(raw is List<object> arr)) continue;
                for (int i = 0; i < arr.Count; i++)
                {
                    var e = (Dictionary<string, object>)arr[i];
                    string src = (string)e["source"], dst = (string)e["target"];
                    if (!nodes.TryGetValue(src, out var sn) || !nodes.TryGetValue(dst, out var dn))
                    {
                        log?.Add($"⚠ 端点缺 graph_nodes 坐标：{spec.Item1}[{i}] {src}→{dst}（已跳过）");
                        continue;
                    }
                    int slot = spec.Item2 switch
                    {
                        "cc" or "pp" => EdgeNetworkSlot(edgeNetworks, $"{spec.Item2}:{i}", networkIndex, log, src, dst),
                        "bs" => BrainstemSlot,
                        _ => CstcSlot,
                    };
                    links.Add(new BrainLink
                    {
                        a = BrainViewRig.MniToAssetSpace(Mni(sn, src, log)),
                        b = BrainViewRig.MniToAssetSpace(Mni(dn, dst, log)),
                        slot = slot,
                    });
                }
            }
            return links;
        }

        private static int EdgeNetworkSlot(Dictionary<string, string> edgeNetworks, string id,
            Dictionary<string, int> networkIndex, List<string> log, string src, string dst)
        {
            if (edgeNetworks.TryGetValue(id, out var net) && networkIndex.TryGetValue(net, out var idx))
                return Mathf.Clamp(idx, 0, NetworkSlots - 1);
            log?.Add($"⚠ 链路 {id}（{src}→{dst}）无上下文网络归属，落中性槽");
            return CstcSlot;
        }

        private static Vector3 Mni(object nodeObj, string name, List<string> log)
        {
            var node = nodeObj as Dictionary<string, object>;
            if (node != null && node.TryGetValue("mni_xyz", out var v) && v is List<object> l && l.Count >= 3)
                return new Vector3((float)(double)l[0], (float)(double)l[1], (float)(double)l[2]);
            log?.Add($"⚠ 节点 {name} 缺 mni_xyz");
            return Vector3.zero;
        }
    }

    // ── 极简 JSON 解析器 ─────────────────────────────────────────────────────
    // 为什么不用 JsonUtility：三份契约数据都是**对象键控**（graph_nodes / regions /
    // edge_contexts），JsonUtility 不支持字典；引 Newtonsoft 会新增包依赖（Unity 侧当前无此包）。
    // 本解析器只支持 JSON 子集（对象/数组/字符串/数字/true/false/null）——足够读契约，且不猜。
    // 它是**只读**契约的读侧实现，不改数据；契约仍以 data/ 下的文件为唯一权威。

    public static class MiniJson
    {
        public static object Parse(string text)
        {
            int i = 0;
            var v = ParseValue(text, ref i);
            return v;
        }

        private static object ParseValue(string s, ref int i)
        {
            Skip(s, ref i);
            if (i >= s.Length) return null;
            switch (s[i])
            {
                case '{': return ParseObject(s, ref i);
                case '[': return ParseArray(s, ref i);
                case '"': return ParseString(s, ref i);
                case 't': i += 4; return true;
                case 'f': i += 5; return false;
                case 'n': i += 4; return null;
                default: return ParseNumber(s, ref i);
            }
        }

        private static Dictionary<string, object> ParseObject(string s, ref int i)
        {
            var d = new Dictionary<string, object>();
            i++;                       // '{'
            Skip(s, ref i);
            if (i < s.Length && s[i] == '}') { i++; return d; }
            while (i < s.Length)
            {
                Skip(s, ref i);
                string k = ParseString(s, ref i);
                Skip(s, ref i);
                i++;                   // ':'
                d[k] = ParseValue(s, ref i);
                Skip(s, ref i);
                if (i < s.Length && s[i] == ',') { i++; continue; }
                if (i < s.Length && s[i] == '}') { i++; break; }
                break;
            }
            return d;
        }

        private static List<object> ParseArray(string s, ref int i)
        {
            var a = new List<object>();
            i++;                       // '['
            Skip(s, ref i);
            if (i < s.Length && s[i] == ']') { i++; return a; }
            while (i < s.Length)
            {
                a.Add(ParseValue(s, ref i));
                Skip(s, ref i);
                if (i < s.Length && s[i] == ',') { i++; continue; }
                if (i < s.Length && s[i] == ']') { i++; break; }
                break;
            }
            return a;
        }

        private static string ParseString(string s, ref int i)
        {
            var sb = new StringBuilder();
            i++;                       // '"'
            while (i < s.Length && s[i] != '"')
            {
                if (s[i] == '\\')
                {
                    i++;
                    switch (s[i])
                    {
                        case 'n': sb.Append('\n'); break;
                        case 't': sb.Append('\t'); break;
                        case 'r': sb.Append('\r'); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'u':
                            sb.Append((char)int.Parse(s.Substring(i + 1, 4), NumberStyles.HexNumber));
                            i += 4;
                            break;
                        default: sb.Append(s[i]); break;
                    }
                }
                else sb.Append(s[i]);
                i++;
            }
            i++;                       // '"'
            return sb.ToString();
        }

        private static double ParseNumber(string s, ref int i)
        {
            int start = i;
            while (i < s.Length && (char.IsDigit(s[i]) || s[i] == '-' || s[i] == '+' ||
                                    s[i] == '.' || s[i] == 'e' || s[i] == 'E')) i++;
            return double.Parse(s.Substring(start, i - start), CultureInfo.InvariantCulture);
        }

        private static void Skip(string s, ref int i)
        {
            while (i < s.Length && char.IsWhiteSpace(s[i])) i++;
        }
    }
}
