// 派生动画生成器（Editor）— 规格 §五「派生件」/ §四·戊·3
// 派生件 = 从 Mixamo 下载件（Assets/Animations/Mixamo/）算出来的工程内 clip，放 Assets/Animations/Derived/。
//
// 两种变换（#150 加第二种）：
//   ① 时间反转：SitDown.anim = Sit To Stand.fbx 反转。
//      为什么需要它：坐立三段要同源同基准。实测（2026-09-12）——
//      · Sit To Stand 与 Sitting Idle 的坐姿端接缝 ≤1.9 mm（同一套坐面基准）；
//      · 而 Stand To Sit 的坐姿端是另一套腿的构型（踝前后差 149 mm、膝角差 17.6°），接上与 Sitting Idle 会跳。
//      反转 Sit To Stand 得到与另两条同族的坐下段（实测接缝 1.8/0.0/0.4 mm），且**不需要**负 AnimatorState.speed
//      ——后者实测在非循环状态下时间被钳在 [0, length]，状态卡死在 clip 首帧（见 unity-cli README §五）。
//   ② 镜像（#150）：Defend_Carry1H_Mirrored.anim = Chairhold/Defend_Carry1H.fbx 的 Humanoid L/R 重映射。
//      为什么需要它：规格 §四·戊·1#6——单手链统一右手，而格挡 clip 的盾手在左手（实测：左手−髋 上 +0.447 /
//      前 −0.245 = 举高且更靠前），不镜像则"椅子要从右手跳到左手"。
//
// 非破坏：派生件是纯函数产物，没有手调成分（与 ActionLab.controller 的非破坏补齐不同，那种要保手调值）。
// 漂移自检：VerifyDerived() 现场重算并与磁盘上的资产逐曲线比对；不一致即报错——
//   能抓住两类问题：① 源 clip 的导入设置被改（如 Y 烘焙/末帧裁剪），② 有人手改了派生件。
//
// ⚠️ 镜像的两条取值来源（**均为本机实测**，2026-09-13；读数见 design/engineering/evidence/P4c-...md）
//   ① 肌肉空间：把肌肉名左↔右互换；**肢体肌肉符号一律 +1**，中轴肌肉（名字不以 Left/Right 开头）
//      凡含 "Left-Right" 者取 −1、其余取 +1。
//      判据：逐肌肉把「同名符号」与「反号」两种镜像候选各设到两块同样的 X Bot 上按 x→−x 比骨骼世界位姿——
//      46 条肢体肌肉的「同名符号」读数落在 4.98–5.54 mm 基线内（该基线与符号无关，是骨架自身的不对称），
//      而「反号」读数是 30–1400 mm；中轴的 "Left-Right" 族反过来（4.98 mm vs 30–400 mm）。
//   ② 根：RootQ 按 (x,−y,−z,w)、RootT.x 取负——**但只做这一步不够**。Unity 的
//      bodyPosition → 根节点世界位 是**按 Avatar 不同的仿射映射**（实测 X Bot：∂Hips/∂p = 1.050·I，
//      且 p=0 时 Hips 不在原点而在 (−1.67, −25.0, −18.2) mm），故朴素镜像会留下**恒定世界位移**
//      （实测 4.59 mm，全骨一致、旋转误差 0.00000°）。⇒ 根位移改为**实测解**（FixRootTranslation）：
//      以「源件 Hips 世界位的镜像」为目标迭代修 RootT 三轴，实测残差 0.0002 mm。
//      ⚠️ 该解按**目标载体**（CarrierModelPath）求得——换载体需重跑生成器（镜像件与载体绑定，见证据）。
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

        /// <summary>镜像件的源（规格 §戊·3 命名：变体 clip = 词条 id_变体键）。</summary>
        public const string MirrorSourceFbx = "Assets/Animations/Mixamo/Chairhold/Defend_Carry1H.fbx";
        /// <summary>镜像件落库路径（规格 §戊·3：镜像派生件 = 来源 id_Mirrored.anim）。</summary>
        public const string MirroredPath = DerivedDir + "/Defend_Carry1H_Mirrored.anim";
        /// <summary>根位移实测解所用的**目标载体**（ActionLab 的 X Bot；换载体需重跑生成器）。</summary>
        public const string CarrierModelPath = "Assets/Mixamo/Characters/X Bot.fbx";
        /// <summary>镜像件的机械断言容差（规格 §四·戊·3 / issue #150 验收标准）：≤1 mm。</summary>
        public const float MirrorTolMm = 1f;
        /// <summary>镜像断言的旋转口径（实测 0.00000°，留一点浮点余量）。</summary>
        public const float MirrorRotTolDeg = 0.01f;

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

        [MenuItem("YANTF/动作演示/重建派生动画（格挡镜像）")]
        public static void RebuildMirrorMenu()
        {
            var clip = BuildDefendMirrored();
            if (clip == null) Debug.LogError("[Derived] 镜像派生失败");
            else Debug.Log("[Derived] 已重建 " + MirroredPath + " — len=" + clip.length.ToString("F4")
                           + " 曲线=" + AnimationUtility.GetCurveBindings(clip).Length
                           + " humanMotion=" + clip.humanMotion);
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

        /// <summary>
        /// 纯函数：Humanoid 曲线级镜像（x → −x 平面反射）。**不含**根位移实测修正——那一层要载体，见 FixRootTranslation。
        /// 曲线集与关键帧时间**原样保留**（镜像不是倒放，不靠负 speed），只改属性名与值符号。
        /// </summary>
        public static AnimationClip DeriveMirrored(AnimationClip src)
        {
            if (src == null) return null;
            var dst = new AnimationClip { frameRate = src.frameRate, legacy = false, wrapMode = src.wrapMode };

            foreach (var b in AnimationUtility.GetCurveBindings(src))
            {
                var curve = AnimationUtility.GetEditorCurve(src, b);
                if (curve == null) continue;
                float sign;
                string prop = MirrorPropertyName(b.propertyName, out sign);
                var k = curve.keys;
                var rk = new Keyframe[k.Length];
                for (int i = 0; i < k.Length; i++)
                    rk[i] = new Keyframe(k[i].time, k[i].value * sign, k[i].inTangent * sign, k[i].outTangent * sign);
                AnimationUtility.SetEditorCurve(dst,
                    new EditorCurveBinding { path = b.path, type = b.type, propertyName = prop }, new AnimationCurve(rk));
            }

            // 循环/相位/烘焙等设置**原样保留**：镜像只改左右，不改播放口径（格挡是循环持续态 → loopTime 保持 1）
            AnimationUtility.SetAnimationClipSettings(dst, AnimationUtility.GetAnimationClipSettings(src));
            return dst;
        }

        /// <summary>
        /// 曲线名 → 镜像后的曲线名，并给出值的符号。覆盖三类：Root T/Q、手/脚 T/Q、肌肉。
        /// 规则与取值来源见文件头「镜像的两条取值来源」。
        /// </summary>
        public static string MirrorPropertyName(string prop, out float sign)
        {
            sign = 1f;
            int dot = prop.LastIndexOf('.');
            char comp = prop.Length > 0 ? prop[prop.Length - 1] : '\0';
            bool isComponent = dot == prop.Length - 2 && (comp == 'x' || comp == 'y' || comp == 'z' || comp == 'w');

            if (isComponent)
            {
                string baseName = prop.Substring(0, dot);      // RootT / RootQ / LeftHandT / RightFootQ …
                bool isRoot = baseName == "RootT" || baseName == "RootQ";
                bool isLimbTQ = baseName.EndsWith("HandT") || baseName.EndsWith("HandQ")
                             || baseName.EndsWith("FootT") || baseName.EndsWith("FootQ");
                if (isRoot || isLimbTQ)
                {
                    bool isQ = baseName.EndsWith("Q");
                    // 位置点：x 取负；旋转四元数：按 x→−x 的反射，y/z 取负
                    sign = isQ ? ((comp == 'y' || comp == 'z') ? -1f : 1f) : (comp == 'x' ? -1f : 1f);
                    string newBase = isRoot ? baseName : SwapLeftRight(baseName);
                    return newBase + "." + comp;
                }
            }

            // 肌肉曲线：左↔右互换；中轴肌肉含 "Left-Right" 者取负
            bool center = !(prop.StartsWith("Left") || prop.StartsWith("Right"));
            sign = (center && prop.Contains("Left-Right")) ? -1f : 1f;
            return SwapLeftRight(prop);
        }

        private static string SwapLeftRight(string name)
        {
            if (name.StartsWith("Left")) return "Right" + name.Substring(4);
            if (name.StartsWith("Right")) return "Left" + name.Substring(5);
            return name;
        }

        /// <summary>重算镜像件（含根位移实测修正），不写盘。VerifyDerived 与生成共用同一条路径。</summary>
        public static AnimationClip RecomputeDefendMirrored()
        {
            var src = LoadClip(MirrorSourceFbx);
            if (src == null) return null;
            var dst = DeriveMirrored(src);
            if (dst == null) return null;
            FixRootTranslation(src, dst);
            return dst;
        }

        /// <summary>镜像件缺失或漂移则重建（幂等）。</summary>
        public static AnimationClip EnsureDefendMirrored()
        {
            var existing = AssetDatabase.LoadAssetAtPath<AnimationClip>(MirroredPath);
            if (existing != null && VerifyCurves(existing, RecomputeDefendMirrored(), "镜像件", log: false) == 0) return existing;
            if (existing != null) Debug.LogWarning("[Derived] 镜像件与源不一致 → 重建");
            return BuildDefendMirrored();
        }

        /// <summary>从源 clip 算镜像 + 根位移实测修正 → 写盘。</summary>
        public static AnimationClip BuildDefendMirrored()
        {
            var dst = RecomputeDefendMirrored();
            if (dst == null) return null;
            return WriteAsset(dst, MirroredPath);
        }

        /// <summary>
        /// 根位移实测修正（**为什么不能只靠公式**见文件头）。以「源件 Hips 世界位的镜像」为目标，
        /// 在目标载体上迭代修 RootT 三轴；Unity 的 bodyPosition→世界位映射是仿射的（∂Hips/∂p ≈ 1.05·I），
        /// 故两轮迭代即收敛（每轮残差 ×0.05）。返回参与修正的帧数（0 = 未做，如源件根本没有 RootT 曲线）。
        /// </summary>
        public static int FixRootTranslation(AnimationClip src, AnimationClip dst)
        {
            if (src == null || dst == null) return 0;
            var carrier = AssetDatabase.LoadAssetAtPath<GameObject>(CarrierModelPath);
            if (carrier == null)
            {
                Debug.LogError("[Derived] 取不到目标载体 " + CarrierModelPath + " → 根位移未修正（镜像会留恒定世界位移）");
                return 0;
            }
            var rootBindings = new List<EditorCurveBinding>();
            foreach (var b in AnimationUtility.GetCurveBindings(src))
                if (b.propertyName == "RootT.x" || b.propertyName == "RootT.y" || b.propertyName == "RootT.z")
                    rootBindings.Add(b);
            if (rootBindings.Count == 0) { Debug.LogWarning("[Derived] 源件无 RootT 曲线 → 无需根位移修正"); return 0; }

            // 采样时刻 = **逐帧**（修正量随 RootQ 变化，实测按源件键时粗采会让手部位姿差从 0.07 mm 涨到 1.11 mm）
            float fps = dst.frameRate > 0f ? dst.frameRate : 30f;
            var times = new List<float>();
            for (int f = 0; ; f++)
            {
                float t = f / fps;
                if (t >= dst.length - KeyTimeEps) break;
                times.Add(t);
            }
            times.Add(dst.length);
            var corr = new Vector3[times.Count];

            var rigSrc = Object.Instantiate(carrier);
            var rigDst = Object.Instantiate(carrier);
            var anSrc = rigSrc.GetComponentInChildren<Animator>();
            var anDst = rigDst.GetComponentInChildren<Animator>();
            try
            {
                if (anSrc == null || anDst == null || anSrc.avatar == null || !anSrc.avatar.isHuman)
                {
                    Debug.LogError("[Derived] 载体 " + CarrierModelPath + " 不是 Humanoid → 根位移未修正");
                    return 0;
                }
                AnimationMode.StartAnimationMode();
                for (int pass = 0; pass < 2; pass++)
                {
                    WriteRootTranslation(src, dst, rootBindings, times, corr);
                    for (int f = 0; f < times.Count; f++)
                    {
                        float t = times[f];
                        Vector3 hSrc = SampleHips(anSrc, src, t);
                        Vector3 hDst = SampleHips(anDst, dst, t);
                        Vector3 target = new Vector3(-hSrc.x, hSrc.y, hSrc.z);
                        corr[f] += target - hDst;      // 世界量当 p 量用 → 迭代收敛（S≈1.05）
                    }
                }
                WriteRootTranslation(src, dst, rootBindings, times, corr);
                AnimationMode.StopAnimationMode();
            }
            finally
            {
                Object.DestroyImmediate(rigSrc);
                Object.DestroyImmediate(rigDst);
            }
            return times.Count;
        }

        /// <summary>按「源件 RootT 的镜像 + 逐键修正量」重写 dst 的 RootT 三轴（键时沿用源件）。</summary>
        private static void WriteRootTranslation(AnimationClip src, AnimationClip dst, List<EditorCurveBinding> rootBindings,
                                                 List<float> times, Vector3[] corr)
        {
            foreach (var b in rootBindings)
            {
                var srcCurve = AnimationUtility.GetEditorCurve(src, b);
                if (srcCurve == null) continue;
                char comp = b.propertyName[b.propertyName.Length - 1];
                float sign = comp == 'x' ? -1f : 1f;      // 根位移：x 取负，y/z 不变
                var keys = new Keyframe[times.Count];
                for (int f = 0; f < times.Count; f++)
                {
                    float t = times[f];
                    float c = comp == 'x' ? corr[f].x : (comp == 'y' ? corr[f].y : corr[f].z);
                    keys[f] = new Keyframe(t, srcCurve.Evaluate(t) * sign + c);
                }
                AnimationUtility.SetEditorCurve(dst, b, new AnimationCurve(keys));
            }
        }

        /// <summary>在采样窗口**内**读 Hips 世界位（EndSampling 会回滚上一次采样，故必须窗口内读）。</summary>
        private static Vector3 SampleHips(Animator an, AnimationClip clip, float t)
        {
            AnimationMode.BeginSampling();
            AnimationMode.SampleAnimationClip(an.gameObject, clip, t);
            var hips = an.GetBoneTransform(HumanBodyBones.Hips);
            Vector3 p = hips != null ? hips.position : Vector3.zero;
            AnimationMode.EndSampling();
            return p;
        }

        // ---------------- 自检 ----------------

        /// <summary>漂移自检：现场重算并与磁盘资产逐曲线比对（**两件派生件都覆盖**）。返回不一致条数（0 = 一致）。</summary>
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

            var mirOnDisk = AssetDatabase.LoadAssetAtPath<AnimationClip>(MirroredPath);
            if (mirOnDisk == null)
            {
                Debug.LogError("[Derived] 派生件缺失: " + MirroredPath + "（跑菜单 YANTF/动作演示/重建派生动画（格挡镜像））");
                bad++;
            }
            else
            {
                bad += VerifyCurves(mirOnDisk, RecomputeDefendMirrored(), "镜像件", log: true);
            }

            if (bad == 0) Debug.Log("[Derived] 两件派生件均与源一致（逐曲线逐点比对通过）");
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

        /// <summary>
        /// 镜像件的**骨骼级**机械断言：同一载体上，镜像件在若干归一化时刻的骨骼世界位姿 == 原件同刻对侧骨骼的镜像。
        /// 返回单行可断言的读数（供 PlayMode 断言经反射调用；本 asmdef 无 UnityEditor 引用，资产级检查落 Editor 侧）。
        /// 三条口径：
        ///   · `handMaxPosMm` —— 验收标准的**字面项**：LeftHand/RightHand 的世界位置差（≤1 mm）
        ///   · `maxExcessMm`  —— 全骨：扣掉**骨架自身左右不对称**（rest 姿势按同一对拍口径量；Mixamo 无名指骨实测 2.28 mm）
        ///                        后的超出量（≤1 mm）——不扣的话，任何镜像都会在不对称骨上"超差"
        ///   · `controlMaxPosMm` —— **对照项**：不做左右对拍的原始读数，必须很大，否则这条断言是空的
        /// </summary>
        public static string MirrorCheck(float tolMm = MirrorTolMm)
        {
            var src = LoadClip(MirrorSourceFbx);
            var mir = AssetDatabase.LoadAssetAtPath<AnimationClip>(MirroredPath);
            var carrier = AssetDatabase.LoadAssetAtPath<GameObject>(CarrierModelPath);
            if (src == null || mir == null || carrier == null)
                return "MIRROR-CHECK bad=1 error=缺源件/镜像件/载体";

            var rigS = Object.Instantiate(carrier);
            var rigD = Object.Instantiate(carrier);
            var anS = rigS.GetComponentInChildren<Animator>();
            var anD = rigD.GetComponentInChildren<Animator>();
            var result = new System.Text.StringBuilder();
            float worstPos = 0f, worstRot = 0f, worstHand = 0f, worstExcess = 0f, control = 0f, restMax = 0f;
            int bad = 0; string worstBone = "-"; int sampled = 0;
            try
            {
                var bones = new List<HumanBodyBones>();
                for (int i = 0; i < (int)HumanBodyBones.LastBone; i++)
                {
                    var b = (HumanBodyBones)i;
                    if (anD.GetBoneTransform(b) != null) bones.Add(b);
                }
                var pS = new Dictionary<HumanBodyBones, Vector3>();
                var qS = new Dictionary<HumanBodyBones, Quaternion>();
                var pD = new Dictionary<HumanBodyBones, Vector3>();
                var qD = new Dictionary<HumanBodyBones, Quaternion>();

                // 骨架自身的不对称基线（rest 姿势、同一对拍口径）——此刻两 rig 都还没被采样过
                var restAsym = new Dictionary<HumanBodyBones, float>();
                foreach (var b in bones)
                {
                    var tD = anD.GetBoneTransform(b);
                    var tS = anS.GetBoneTransform(MirrorBone(b));
                    if (tD == null || tS == null) continue;
                    Vector3 ps = tS.position; ps.x = -ps.x;
                    restAsym[b] = Vector3.Distance(tD.position, ps) * 1000f;
                    if (restAsym[b] > restMax) restMax = restAsym[b];
                }

                AnimationMode.StartAnimationMode();
                foreach (float tn in new[] { 0f, 0.125f, 0.25f, 0.5f, 0.75f, 1f })
                {
                    ReadPose(anS, src, tn * src.length, bones, pS, qS);
                    ReadPose(anD, mir, tn * mir.length, bones, pD, qD);
                    sampled++;
                    foreach (var b in bones)
                    {
                        var partner = MirrorBone(b);
                        if (!pS.ContainsKey(partner) || !pD.ContainsKey(b)) continue;
                        Vector3 exp = pS[partner]; exp.x = -exp.x;
                        float d = Vector3.Distance(pD[b], exp) * 1000f;
                        Quaternion qexp = qS[partner];
                        float ang = Quaternion.Angle(qD[b], new Quaternion(qexp.x, -qexp.y, -qexp.z, qexp.w));
                        float excess = d - (restAsym.ContainsKey(b) ? restAsym[b] : 0f);
                        if (d > worstPos) { worstPos = d; worstBone = b.ToString(); }
                        if (excess > worstExcess) worstExcess = excess;
                        if (ang > worstRot) worstRot = ang;
                        if ((b == HumanBodyBones.LeftHand || b == HumanBodyBones.RightHand) && d > worstHand) worstHand = d;
                        if (excess > tolMm || ang > MirrorRotTolDeg) bad++;
                        // 对照：不对拍左右（必须很大，证明断言非空）
                        control = Mathf.Max(control, Vector3.Distance(pD[b], pS[b]) * 1000f);
                    }
                }
                AnimationMode.StopAnimationMode();
            }
            finally
            {
                Object.DestroyImmediate(rigS);
                Object.DestroyImmediate(rigD);
            }

            bool keysMatch = KeyTimesMatch(src, mir);
            result.Append("MIRROR-CHECK tolMm=").Append(tolMm.ToString("F3"))
                  .Append(" times=").Append(sampled)
                  .Append(" handMaxPosMm=").Append(worstHand.ToString("F4"))
                  .Append(" maxExcessMm=").Append(worstExcess.ToString("F4"))
                  .Append(" maxPosMm=").Append(worstPos.ToString("F4"))
                  .Append(" maxRotDeg=").Append(worstRot.ToString("F5"))
                  .Append(" restAsymMaxMm=").Append(restMax.ToString("F3"))
                  .Append(" worstBone=").Append(worstBone)
                  .Append(" controlMaxPosMm=").Append(control.ToString("F2"))
                  .Append(" humanMotion=").Append(mir != null && mir.humanMotion)
                  .Append(" loopTime=").Append(mir != null && AnimationUtility.GetAnimationClipSettings(mir).loopTime)
                  .Append(" keyTimesMatch=").Append(keysMatch)
                  .Append(" curves=").Append(mir != null ? AnimationUtility.GetCurveBindings(mir).Length : 0)
                  .Append(" bad=").Append(bad);
            Debug.Log("[Derived] " + result);
            return result.ToString();
        }

        /// <summary>
        /// 镜像的第二条独立判据（规格 §戊·3「镜像同样可自检」）：**镜像两次回到原件**，逐曲线一致。
        /// 它只需要纯函数 DeriveMirrored（不含根位移修正——那一步在镜像两次后自然抵消）。
        /// </summary>
        public static bool VerifyMirrorInvolution()
        {
            var src = LoadClip(MirrorSourceFbx);
            if (src == null) return false;
            var back = DeriveMirrored(DeriveMirrored(src));
            if (back == null) return false;
            return VerifyCurves(back, src, "二次镜像", log: true) == 0;
        }

        /// <summary>
        /// 镜像件的**关键帧时间**判据（证明镜像不是倒放、也不靠负 speed/重采样）：
        /// · 非根曲线：键时与源件逐曲线一致；· RootT 三轴：键时**单调不减**且覆盖 [0, length]
        ///   （它们按实测根位移修正重写过，键时沿用源件 RootT 三曲线的并集）。
        /// </summary>
        private static bool KeyTimesMatch(AnimationClip src, AnimationClip mirror)
        {
            if (src == null || mirror == null) return false;
            var map = new Dictionary<string, EditorCurveBinding>();
            foreach (var b in AnimationUtility.GetCurveBindings(mirror)) map[Key(b)] = b;
            foreach (var b in AnimationUtility.GetCurveBindings(src))
            {
                bool isRootT = b.propertyName == "RootT.x" || b.propertyName == "RootT.y" || b.propertyName == "RootT.z";
                float sign;
                string prop = MirrorPropertyName(b.propertyName, out sign);
                var key = b.path + "|" + b.type.Name + "|" + prop;
                if (!map.TryGetValue(key, out var mb)) return false;
                var c1 = AnimationUtility.GetEditorCurve(src, b);
                var c2 = AnimationUtility.GetEditorCurve(mirror, mb);
                if (c1 == null || c2 == null) return false;
                var k1 = c1.keys; var k2 = c2.keys;
                if (isRootT)
                {
                    if (k2.Length == 0) return false;
                    if (k2[0].time > KeyTimeEps || Mathf.Abs(k2[k2.Length - 1].time - mirror.length) > KeyTimeEps) return false;
                    for (int i = 1; i < k2.Length; i++) if (k2[i].time < k2[i - 1].time - KeyTimeEps) return false;
                    continue;   // 键时由实测修正重写 → 只判「不倒放且覆盖全段」
                }
                if (k1.Length != k2.Length) return false;
                for (int i = 0; i < k1.Length; i++)
                    if (Mathf.Abs(k1[i].time - k2[i].time) > KeyTimeEps) return false;
            }
            return true;
        }

        private static void ReadPose(Animator an, AnimationClip clip, float t, List<HumanBodyBones> bones,
                                     Dictionary<HumanBodyBones, Vector3> ps, Dictionary<HumanBodyBones, Quaternion> qs)
        {
            AnimationMode.BeginSampling();
            AnimationMode.SampleAnimationClip(an.gameObject, clip, t);
            foreach (var b in bones)
            {
                var tr = an.GetBoneTransform(b);
                if (tr == null) { ps.Remove(b); qs.Remove(b); continue; }
                ps[b] = tr.position; qs[b] = tr.rotation;
            }
            AnimationMode.EndSampling();
        }

        private static HumanBodyBones MirrorBone(HumanBodyBones b)
        {
            string s = b.ToString();
            string sw = s.StartsWith("Left") ? "Right" + s.Substring(4)
                      : (s.StartsWith("Right") ? "Left" + s.Substring(5) : s);
            return (HumanBodyBones)System.Enum.Parse(typeof(HumanBodyBones), sw);
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
