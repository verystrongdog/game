// PlayMode 断言 — Blender 回导样本与调试载体（#156，2026-09-14）
//
// 断言四类事实（#156 交付物清单最后一条）：
//   ① **Rig**：探针 FBX 是一条 Humanoid **回导**样本——`clip.humanMotion` 为真，Avatar 人形且有效，
//      五个读数点骨全部解析得到，并且它在 X Bot 载体上**真的重定向出姿势**（帧间差异 > 阈值）。
//   ② **采样稳定性**：同一 clip 同一帧重复定位，读数**逐次一致**（验收标准第 5 条）。
//   ③ **调试控制**：播放/暂停/前后单帧/回首帧四个动作的**帧号**行为（验收标准第 4 条）。
//   ④ **资产身份**：X Bot.fbx 字节哈希不变、15 条既有 Mixamo FBX 一个不少、已入库基准场景与
//      controller 仍在（验收标准第 6 条）。
//
// ⚠️ **为什么本文件不 `using UnityEditor`**：`YANTF.Demo.Tests.asmdef` 的 `includePlatforms` 是空的，
//    引 `UnityEditor` 会把它变成"只能在 Editor 编译"的装配件，与仓库既有口径冲突
//    （见 ActionLabSmokeTests 文件头：#124 起 controller/资产级断言落在 builder 自检里）。
//    但本条的断言必须**真的加载**探针资产与 X Bot 载体 —— 故经 `System.Reflection` 调
//    `Assembly-CSharp-Editor` 里的 `BlenderAnimationDebugBuilder`（Editor 装配件无法被 asmdef 直接引用），
//    **不复制一份装配逻辑**：测试与菜单走的是同一个 `EnsureController` / `CreateActor`。
//
// ⚠️ 载体的装配与读数走 `BlenderAnimationDebugger.Attach(...)` + `SampleAtFrame(...)`——即
//    「`Animator.Play(state, 0, normalized)` + `Update(0f)`」那条确定性路径（unity-cli README §五，
//    三个坑见组件文件头）。**不要**改成 `animator.speed = 0` 先冻结再 Play：那样定位不生效。
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using YANTF.ActionLab;

public class BlenderAnimationDebugTests
{
    private const string ProbeFbxAsset = "Assets/Animations/Blender/RigRoundTripProbe.fbx";
    private const string XBotAssetPath = "Assets/Mixamo/Characters/X Bot.fbx";
    private const string ProbeClipName = "RigRoundTripProbe";

    /// <summary>验收标准第 6 条的锚：X Bot.fbx 的字节哈希（母版输入，本条不得改动）。</summary>
    private const string XBotSha256 = "cd60e51571bb7c0c1988ec58b3be174c91bd193b6372a9064f1ec2553bc8deab";

    /// <summary>15 条既有 Mixamo FBX（#149 起入库；本条既不重导也不改名）。</summary>
    private static readonly string[] MixamoFbxNames =
    {
        "Stand To Sit.fbx", "Sitting Idle.fbx", "Sit To Stand.fbx",
        "Chairhold/Carry1H.fbx", "Chairhold/Defend_Carry1H.fbx", "Chairhold/Lift1H.fbx",
        "Chairhold/PhysicalAttack_Carry1H.fbx", "Chairhold/PhysicalAttack_Wield2H.fbx",
        "Chairhold/PutDown.fbx", "Chairhold/Wield2H.fbx",
        "Combat/Defend.fbx", "Combat/Down.fbx", "Combat/HitReaction.fbx",
        "Combat/MentalAttack.fbx", "Combat/PhysicalAttack.fbx",
    };

    /// <summary>
    /// 逐读数点的帧间最小位移（防"恒定姿势"式假绿）。**阈值按实测填**，两条口径不同不能一刀切：
    ///   · 双手/双脚是**骨内姿势**，Unity 与 Blender 同口径 ⇒ 数百 mm（实测 677 / 551 mm 量级）；
    ///   · Hips 是**人形 body position**（`RootT`）经 Unity 重定向后落到 Hips 节点的结果，
    ///     与 Blender 侧髋骨世界位移不是同一个量（Blender 40.0 mm vs Unity 16.96 mm，见管线文档 §五·4）
    ///     ⇒ 只要求"确实在动"的量级。
    /// </summary>
    private static readonly System.Collections.Generic.Dictionary<HumanBodyBones, float> MotionMinMm =
        new System.Collections.Generic.Dictionary<HumanBodyBones, float>
        {
            { HumanBodyBones.Hips, 10f },
            { HumanBodyBones.LeftHand, 300f },
            { HumanBodyBones.RightHand, 300f },
            { HumanBodyBones.LeftFoot, 200f },
            { HumanBodyBones.RightFoot, 200f },
        };

    private GameObject _actor;

    // ================= 装配（与菜单共用同一条路径）=================

    private static Type EditorBuilderType()
    {
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            var t = asm.GetType("YANTF.EditorTools.BlenderAnimationDebugBuilder", false);
            if (t != null) return t;
        }
        Assert.Fail("找不到 YANTF.EditorTools.BlenderAnimationDebugBuilder（Assembly-CSharp-Editor 未加载？）");
        return null;
    }

    private static object CallEditor(string method, params object[] args)
    {
        var mi = EditorBuilderType().GetMethod(method, BindingFlags.Public | BindingFlags.Static);
        Assert.IsNotNull(mi, "builder 上没有静态方法 " + method);
        return mi.Invoke(null, args);
    }

    /// <summary>按菜单同一路径装配载体：EnsureController() → CreateActor(controller)。</summary>
    private BlenderAnimationDebugger BuildActor()
    {
        var controller = (RuntimeAnimatorController)CallEditor("EnsureController");
        Assert.IsNotNull(controller, "EnsureController 返回空——探针 FBX 或 Assets/Temp 不可写？");
        _actor = (GameObject)CallEditor("CreateActor", controller);
        Assert.IsNotNull(_actor, "CreateActor 返回空——找不到 X Bot 载体？");

        var dbg = _actor.GetComponent<BlenderAnimationDebugger>();
        Assert.IsNotNull(dbg, "载体上没有 BlenderAnimationDebugger");
        dbg.AutoPlay = false;          // 断言自己控时间轴，不要与自动播放抢
        dbg.SampleAtFrame(0);
        return dbg;
    }

    [UnityTearDown]
    public System.Collections.IEnumerator TearDown()
    {
        if (_actor != null) UnityEngine.Object.Destroy(_actor);
        _actor = null;
        yield return null;
    }

    // ================= ① Rig =================

    [Test]
    public void Rig_ProbeClip_IsHumanMotion_AndRetargetsOntoXBotAvatar()
    {
        var dbg = BuildActor();
        var animator = dbg.Animator;

        Assert.IsNotNull(animator.avatar, "载体 Animator 没有 Avatar");
        Assert.IsTrue(animator.avatar.isValid, "X Bot Avatar 无效");
        Assert.IsTrue(animator.avatar.isHuman, "X Bot Avatar 不是人形");

        var clip = dbg.Clip;
        Assert.IsNotNull(clip, "controller 里找不到探针 clip " + ProbeClipName);
        Assert.IsTrue(clip.humanMotion, "探针 clip 的 humanMotion 为 false（不是 Humanoid 回导样本）");
        Assert.AreEqual(30f, clip.frameRate, 0.001f, "探针 clip 帧率应为 30");
        Assert.AreEqual(2.0f, clip.length, 0.001f, "探针 clip 时长应为 2.000 s（61 帧 @30fps）");
        Assert.AreEqual(60, dbg.FrameCount, "帧数应为 60（0..60 共 61 个采样点）");

        foreach (var bone in BlenderAnimationDebugger.ReadoutBones)
            Assert.IsNotNull(animator.GetBoneTransform(bone), "读数点骨解析不到: " + bone);
    }

    /// <summary>
    /// 回导保真的**载体侧**判据：同一 clip 在不同帧上必须给出**不同**的姿势。
    /// 这条是防空转的——2026-09-14 实测踩到过"FBX 有时长、Unity 侧 130 条曲线全 constant"的假完成
    /// （根因是 Blender 侧烘焙把控制骨 action 摘掉了，见管线文档 §四·2）。
    /// </summary>
    [UnityTest]
    public System.Collections.IEnumerator Rig_ProbeClip_ActuallyMovesTheBody()
    {
        var dbg = BuildActor();
        var frames = new[] { 0, 20, 40 };
        var poses = new Dictionary<int, Vector3[]>();

        foreach (var f in frames)
        {
            dbg.SampleAtFrame(f);
            poses[f] = BlenderAnimationDebugger.ReadoutBones
                .Select(b => dbg.Animator.GetBoneTransform(b).position).ToArray();
            yield return null;
        }

        for (int i = 0; i < BlenderAnimationDebugger.ReadoutBones.Length; i++)
        {
            float maxMm = 0f;
            foreach (var a in frames)
                foreach (var b in frames)
                    if (b > a) maxMm = Mathf.Max(maxMm, Vector3.Distance(poses[a][i], poses[b][i]) * 1000f);
            float minMm = MotionMinMm[BlenderAnimationDebugger.ReadoutBones[i]];
            Assert.Greater(maxMm, minMm,
                $"读数点 {BlenderAnimationDebugger.ReadoutBones[i]} 在探针里几乎不动" +
                $"（实测 {maxMm:F2} mm，下限 {minMm} mm）");
        }
    }

    /// <summary>导出物形状：animation-only · 零控制骨 · 单根骨 · 骨数 65（控制骨不得外泄）。</summary>
    [Test]
    public void Rig_ProbeFbx_IsAnimationOnly_WithoutControlBones()
    {
        var model = (GameObject)CallEditor("LoadProbeModel");
        Assert.IsNotNull(model, "取不到探针模型: " + ProbeFbxAsset);

        var all = model.GetComponentsInChildren<Transform>(true);
        var ctrl = all.Where(t => t.name.Contains("CTRL_")).Select(t => t.name).ToArray();
        int bones = all.Count(t => t.name.StartsWith("mixamorig:"));
        int meshRenderers = all.Count(t => t.GetComponent<MeshRenderer>() != null ||
                                            t.GetComponent<SkinnedMeshRenderer>() != null);

        Assert.IsEmpty(ctrl, "导出物里有控制骨（Blender 侧 use_armature_deform_only 失效？）: " +
                             string.Join(", ", ctrl));
        Assert.AreEqual(65, bones, "mixamorig 骨数应为 65（多出来的是 Leaf Bone / 额外 Root 骨）");
        Assert.AreEqual(0, meshRenderers, "导出物含网格——不是 animation-only");
    }

    // ================= ② 采样稳定性 =================

    [Test]
    public void Sampling_SameClipSameFrame_IsBitwiseRepeatable()
    {
        var dbg = BuildActor();
        var runs = new List<string>();
        for (int i = 0; i < 3; i++)
        {
            dbg.SampleAtFrame(20);
            runs.Add(dbg.ReadoutLine());
        }
        Assert.AreEqual(runs[0], runs[1], "同一帧第二次采样读数不同（Hips/双手/双脚）");
        Assert.AreEqual(runs[1], runs[2], "同一帧第三次采样读数不同（Hips/双手/双脚）");
        Assert.AreEqual(20, dbg.CurrentFrame);
        Assert.IsFalse(dbg.IsPlaying, "逐帧定位后不应处于播放态");
    }

    // ================= ③ 调试控制 =================

    [UnityTest]
    public System.Collections.IEnumerator DebugControls_PlayPauseStepReset()
    {
        var dbg = BuildActor();
        Assert.AreEqual(0, dbg.CurrentFrame, "初始应在首帧");
        Assert.IsFalse(dbg.IsPlaying, "AutoPlay=false 时不应自动播放");

        // 单帧前进 / 后退
        dbg.StepFrames(1);
        Assert.AreEqual(1, dbg.CurrentFrame, "前进一帧后帧号应为 1");
        dbg.StepFrames(1);
        Assert.AreEqual(2, dbg.CurrentFrame, "再前进一帧后帧号应为 2");
        dbg.StepFrames(-1);
        Assert.AreEqual(1, dbg.CurrentFrame, "后退一帧后帧号应为 1");

        // 边界夹紧：不得越出 0..FrameCount
        dbg.SampleAtFrame(0);
        dbg.StepFrames(-1);
        Assert.AreEqual(0, dbg.CurrentFrame, "首帧再后退应夹在 0");
        dbg.SampleAtFrame(dbg.FrameCount);
        dbg.StepFrames(1);
        Assert.AreEqual(dbg.FrameCount, dbg.CurrentFrame, "末帧再前进应夹在 FrameCount");

        // 播放 / 暂停
        dbg.ResetToFirstFrame();
        Assert.AreEqual(0, dbg.CurrentFrame, "回首帧后帧号应为 0");
        dbg.Play();
        Assert.IsTrue(dbg.IsPlaying, "Play 后应处于播放态");
        Assert.AreEqual(1f, dbg.Animator.speed, 0.0001f, "Play 应把 speed 放回 1");
        yield return null;
        yield return null;
        dbg.Pause();
        Assert.IsFalse(dbg.IsPlaying, "Pause 后不应处于播放态");
        Assert.AreEqual(0f, dbg.Animator.speed, 0.0001f, "Pause 应把 speed 冻结为 0");
    }

    /// <summary>到末帧后再 Play 必须从头来，而不是停在末帧（否则 lab 里按空格像"没反应"）。</summary>
    [Test]
    public void DebugControls_PlayFromLastFrame_Restarts()
    {
        var dbg = BuildActor();
        dbg.SampleAtFrame(dbg.FrameCount);
        Assert.AreEqual(dbg.FrameCount, dbg.CurrentFrame);
        dbg.Play();
        Assert.AreEqual(0, dbg.CurrentFrame, "末帧后 Play 应回到首帧续播");
    }

    /// <summary>
    /// 连续播放必须**接成环**：走到末帧后自己回到首帧，而不是停在末帧。
    /// 理由（2026-09-14 实测）：探针首末帧同为静止姿势 ⇒ 不接环的话按 Play 一秒后画面就"没动静"，
    /// 而 lab 的用途正是逐帧目视。接环只在**播放层面**做：不改 FBX、不改导入设置，样本仍是一次性。
    /// </summary>
    [UnityTest]
    public System.Collections.IEnumerator DebugControls_PlaybackWrapsAtLastFrame()
    {
        var dbg = BuildActor();
        Assert.IsTrue(dbg.LoopInPlay, "lab 默认应接环（关掉它等于让 lab 停在末帧）");
        dbg.Play();

        // 把状态直接推到末帧之后（不必真等 2 秒）
        dbg.Animator.Play(Animator.StringToHash(ProbeClipName), 0, 1f);
        dbg.Animator.Update(0f);
        yield return null;   // 让 BlenderAnimationDebugger.Update 跑一次
        yield return null;

        Assert.IsTrue(dbg.IsPlaying, "接环不应把播放态关掉");
        Assert.Less(dbg.CurrentFrame, dbg.FrameCount,
            $"末帧后应接回首帧，实测停在 frame={dbg.CurrentFrame}/{dbg.FrameCount}");
    }

    // ================= ④ 资产身份 =================

    [Test]
    public void AssetIdentity_XBotBytesUnchanged_AndMixamoIntact()
    {
        Assert.AreEqual(XBotSha256, Sha256OfAsset(XBotAssetPath),
            "X Bot.fbx 字节变了——本条的母版输入不得改动（验收标准第 6 条）");

        var dir = Path.Combine(Application.dataPath, "Animations/Mixamo");
        var found = new List<string>();
        foreach (var name in MixamoFbxNames)
            if (File.Exists(Path.Combine(dir, name))) found.Add(name);
        Assert.AreEqual(MixamoFbxNames.Length, found.Count,
            "既有 Mixamo FBX 少了 " + (MixamoFbxNames.Length - found.Count) + " 条：" +
            string.Join(", ", MixamoFbxNames.Except(found)));

        // 已入库基准场景与 controller 仍在（本条不改它们）
        Assert.IsTrue(File.Exists(Path.Combine(Application.dataPath, "Scenes/ActionLab.unity")),
            "ActionLab.unity 不见了");
        Assert.IsTrue(File.Exists(Path.Combine(Application.dataPath, "ActionLab/ActionLab.controller")),
            "ActionLab.controller 不见了");
    }

    private static string Sha256OfAsset(string assetRelativePath)
    {
        var full = Path.Combine(Application.dataPath, assetRelativePath.Substring("Assets/".Length));
        using (var sha = SHA256.Create())
        using (var fs = File.OpenRead(full))
            return BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToLowerInvariant();
    }
}
