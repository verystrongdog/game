// 派生动画生成器（Editor）— 规格 §五「派生件」
// 派生件 = 从 Mixamo 下载件（Assets/Animations/Mixamo/）算出来的工程内 clip，放 Assets/Animations/Derived/。
//
// 变换：**时间反转**——SitDown.anim = Sit To Stand.fbx 反转。
//   为什么需要它：坐立三段要同源同基准。实测（2026-09-12）——
//   · Sit To Stand 与 Sitting Idle 的坐姿端接缝 ≤1.9 mm（同一套坐面基准）；
//   · 而 Stand To Sit 的坐姿端是另一套腿的构型（踝前后差 149 mm、膝角差 17.6°），接上 Sitting Idle 会跳。
//   反转 Sit To Stand 得到与另两条同族的坐下段（实测接缝 1.8/0.0/0.4 mm），且**不需要**负 AnimatorState.speed
//   ——后者实测在非循环状态下时间被钳在 [0, length]，状态卡死在 clip 首帧（见 unity-cli README §五）。
//
// ⚠️ 第二种变换「镜像」**已于 2026-09-14 退役**（owner 裁定，规格 §四·戊·5）：
//   格挡变体的姿势来源改用 `2hand Idle`（两手间距实测 17.1–17.4 cm、左手落在靠背面上 0.2–0.7 cm、
//   局部坐标漂移 3.8 mm ⇒ 三条判据全绿），镜像件 `Defend_Carry1H_Mirrored.anim` 因此**失去消费者**，
//   连同 `DeriveMirrored` / `FixRootTranslation` / `MirrorCheck` / `VerifyMirrorInvolution` 一并删除。
//   历史读数（肌肉空间符号口径、根位移实测解、逐骨镜像 0.069 mm）**不删**，保留在三处：
//   design/presentation/动作库规格.md §四·戊·3 · code/unity/README.md §二·M · design/engineering/危险点表.md §七。
//
// 非破坏：派生件是纯函数产物，没有手调成分（与 ActionLab.controller 的非破坏补齐不同，那种要保手调值）。
// 漂移自检：VerifyDerived() 现场重算并与磁盘上的资产逐曲线比对；不一致即报错——
//   能抓住两类问题：① 源 clip 的导入设置被改（如 Y 烘焙/末帧裁剪），② 有人手改了派生件。
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using YANTF.ActionLab;

namespace YANTF.EditorTools
{
    public static class DerivedClipBuilder
    {
        public const string DerivedDir = "Assets/Animations/Derived";
        public const string SitDownPath = ActionCatalog.SitDownDerived;   // Assets/Animations/Derived/SitDown.anim
        public const string SourceClipName = "mixamo.com";                // Mixamo 单 take 的默认 take 名


        private const float KeyTimeEps = 1e-4f;
        private const float ValueEps = 1e-5f;

        // ---------------- 菜单 ----------------

        [MenuItem("YANTF/动作演示/重建派生动画（SitDown 倒放）")]
        public static void RebuildMenu()
        {
            var clip = BuildSitDown();
            if (clip == null) Debug.LogError("[Derived] SitDown 派生失败");
            else Debug.Log("[Derived] 已重建 " + SitDownPath + " — len=" + clip.length.ToString("F4")
                           + " 曲线=" + AnimationUtility.GetCurveBindings(clip).Length);
        }


        // ---------------- ① 时间反转（既有） ----------------

        /// <summary>确保派生件在磁盘上且与源一致；缺失或漂移则重建。返回该 clip（失败 null）。供 ActionLabBuilder 调用。</summary>
        public static AnimationClip EnsureSitDown()
        {
            var existing = AssetDatabase.LoadAssetAtPath<AnimationClip>(SitDownPath);
            if (existing != null && VerifyCurves(existing, DeriveReversed(LoadClip(ActionCatalog.SitToStandFbx)), "SitDown", log: false) == 0)
                return existing;
            if (existing != null) Debug.LogWarning("[Derived] SitDown 与源不一致 → 重建");
            return BuildSitDown();
        }

        /// <summary>从源 FBX 读源 clip → 反转 → 写盘。返回写出的 clip。</summary>
        public static AnimationClip BuildSitDown()
        {
            var src = LoadClip(ActionCatalog.SitToStandFbx);
            if (src == null) return null;
            var derived = DeriveReversed(src);
            if (derived == null) return null;
            return WriteAsset(derived, SitDownPath);
        }

        /// <summary>
        /// 纯函数：把一条 clip 的每条曲线做时间反转（t → length − t，关键帧倒序，切矢取反）。
        /// 保住 humanMotion / frameRate / 曲线集——Humanoid 的肌肉曲线与 RootT/RootQ 都是普通浮点曲线，可直接反转。
        /// </summary>
        public static AnimationClip DeriveReversed(AnimationClip src)
        {
            if (src == null) return null;
            var dst = new AnimationClip
            {
                frameRate = src.frameRate,
                legacy = false,
                wrapMode = WrapMode.Clamp,
            };

            foreach (var b in AnimationUtility.GetCurveBindings(src))
            {
                var curve = AnimationUtility.GetEditorCurve(src, b);
                if (curve == null) continue;
                var k = curve.keys;
                var rk = new Keyframe[k.Length];
                for (int i = 0; i < k.Length; i++)
                {
                    var s = k[k.Length - 1 - i];
                    // 时间镜像；切矢随之取反（in↔out 互换并变号），否则首末段斜率会反
                    rk[i] = new Keyframe(src.length - s.time, s.value, -s.outTangent, -s.inTangent);
                }
                AnimationUtility.SetEditorCurve(dst, b, new AnimationCurve(rk));
            }

            var settings = AnimationUtility.GetAnimationClipSettings(src);
            settings.loopTime = false;   // 坐下是一次性动作
            settings.loopBlend = false;
            AnimationUtility.SetAnimationClipSettings(dst, settings);
            return dst;
        }

        // ---------------- ② 镜像（#150） ----------------










        // ---------------- 自检 ----------------

        /// <summary>漂移自检：现场重算并与磁盘资产逐曲线比对。返回不一致条数（0 = 一致）。</summary>
        public static int VerifyDerived()
        {
            int bad = 0;
            var sitOnDisk = AssetDatabase.LoadAssetAtPath<AnimationClip>(SitDownPath);
            if (sitOnDisk == null)
            {
                Debug.LogError("[Derived] 派生件缺失: " + SitDownPath + "（跑菜单 YANTF/动作演示/重建派生动画（SitDown 倒放））");
                bad++;
            }
            else
            {
                bad += VerifyCurves(sitOnDisk, DeriveReversed(LoadClip(ActionCatalog.SitToStandFbx)), "SitDown", log: true);
            }

            if (bad == 0) Debug.Log("[Derived] 派生件与源一致（逐曲线逐点比对通过）");
            return bad;
        }

        /// <summary>逐曲线比对（length + 曲线集 + 关键帧数 + 逐帧时间/值）。返回不一致条数。</summary>
        private static int VerifyCurves(AnimationClip onDisk, AnimationClip fresh, string label, bool log)
        {
            if (onDisk == null || fresh == null)
            {
                if (log) Debug.LogError("[Derived] " + label + "：一边为空（磁盘=" + (onDisk == null) + " 重算=" + (fresh == null) + "）");
                return 1;
            }
            int bad = 0;
            if (Mathf.Abs(onDisk.length - fresh.length) > KeyTimeEps)
            {
                if (log) Debug.LogError("[Derived] " + label + " length 不一致: " + onDisk.length + " vs " + fresh.length);
                bad++;
            }
            var a = AnimationUtility.GetCurveBindings(onDisk);
            var b = AnimationUtility.GetCurveBindings(fresh);
            if (a.Length != b.Length)
            {
                if (log) Debug.LogError("[Derived] " + label + " 曲线数不一致: " + a.Length + " vs " + b.Length);
                return bad + 1;
            }

            var freshMap = new Dictionary<string, EditorCurveBinding>();
            foreach (var bd in b) freshMap[Key(bd)] = bd;

            foreach (var bd in a)
            {
                if (!freshMap.TryGetValue(Key(bd), out var bd2))
                {
                    if (log) Debug.LogError("[Derived] " + label + " 磁盘多出曲线: " + Key(bd));
                    bad++; continue;
                }
                var c1 = AnimationUtility.GetEditorCurve(onDisk, bd);
                var c2 = AnimationUtility.GetEditorCurve(fresh, bd2);
                if (c1 == null || c2 == null) { if (c1 != c2) bad++; continue; }
                var k1 = c1.keys; var k2 = c2.keys;
                if (k1.Length != k2.Length)
                {
                    if (log) Debug.LogError("[Derived] " + label + " " + Key(bd) + " 关键帧数不一致: " + k1.Length + " vs " + k2.Length);
                    bad++; continue;
                }
                for (int i = 0; i < k1.Length; i++)
                {
                    if (Mathf.Abs(k1[i].time - k2[i].time) > KeyTimeEps || Mathf.Abs(k1[i].value - k2[i].value) > ValueEps)
                    {
                        if (log) Debug.LogError("[Derived] " + label + " " + Key(bd) + " 第 " + i + " 帧不一致");
                        bad++; break;
                    }
                }
            }
            return bad;
        }






        // ---------------- 读写 ----------------

        private static AnimationClip WriteAsset(AnimationClip clip, string path)
        {
            if (!Directory.Exists(DerivedDir)) Directory.CreateDirectory(DerivedDir);
            AssetDatabase.DeleteAsset(path);   // 派生件无手调成分 → 先删再建，避免残留曲线
            AssetDatabase.CreateAsset(clip, path);
            AssetDatabase.SaveAssets();
            AssetDatabase.ImportAsset(path);
            return AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        }

        private static string Key(EditorCurveBinding b) => b.path + "|" + b.type.Name + "|" + b.propertyName;

        /// <summary>取一条 FBX 里的源 clip（Mixamo 单 take；take 名不叫 mixamo.com 时退回第一条非预览曲线集）。</summary>
        private static AnimationClip LoadClip(string fbxPath)
        {
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath(fbxPath))
            {
                var c = o as AnimationClip;
                if (c == null || c.name.StartsWith("__preview__")) continue;
                if (c.name == SourceClipName) return c;
            }
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath(fbxPath))
            {
                var c = o as AnimationClip;
                if (c != null && !c.name.StartsWith("__preview__")) return c;
            }
            Debug.LogError("[Derived] 取不到源 clip: " + fbxPath);
            return null;
        }
    }
}
