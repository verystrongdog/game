// PlayMode 断言 — Animation Rigging 接入点（基础设施，2026-09-14）
//
// 本文件断言两类事实，**都在真实基准场景 `ActionLab.unity` 上测**（不是另搭一个合成 Rig）：
//   ① **结构**：场景里的接入点按契约存在——RigBuilder + 恰 1 个 Rig + 左臂 TwoBoneIK，
//      骨链三个绑定非空，且权重恒为 0（惰性——该接入目前**没有消费方**）。
//   ② **能力**：约束在本载体（Humanoid X Bot / Mixamo 骨架）上**真的求值**——权重拉满并重建图后，
//      手被拉到目标上；对照项：权重全 0 时手留在原处。
//
// ⚠️ 本文件**不实现、也不验证**被暂停的持椅副手 IK：owner 已裁定「手里有东西」整条线暂停
//    （code/unity/README.md §二·N 未闭合 1′），规格 §戊·2 的副手 IK 属该线。
//    探针目标是挂在约束节点下的**哑目标**，不指向椅子上任何锚点。
//
// ⚠️ 三条实测口径（2026-09-14，都是踩过才知道）：
//   1. **必须测真场景、别自己搭**：`RigBuilder` 在 `Awake`/`OnEnable` 里建图。合成路径（运行时先
//      AddComponent、后 Add layer）那一轮 Awake 看到的 layers 是空的（`Build()` 直接 `return false`），
//      事后在同一实例上再 `Build()` **返回 true**、层也 `IsValid()=true`、`constraints=1`，
//      但约束**始终不生效**——实测四组组合（`animator.speed` 0/1 × rig 权重 0/1 × ik 权重 0/1）读数
//      **逐位相同**，恒等于初始偏移 187.1 mm；连"建好模板再整体 `Instantiate`（克隆体 Awake 拿到已序列化
//      layers）"也一样不生效。而真场景里同一套东西是好的（实测手↔目标 = **0.0 mm**）。差异未定位 ⇒
//      本文件只认场景路径，**不要**为省事改回合成搭建。
//   2. **判据取「手↔目标距离」**：不要用 `animator.speed = 0` 冻结换确定性，也别拿"手的位移量"当判据——
//      距离对动画本身不敏感，冻结反而多一个自变量。Animation Rigging 由 RigBuilder 自己的 PlayableGraph
//      （`DirectorUpdateMode.GameTime`）求值，不走「Animator.Play + Update(0f)」那条确定性姿势路径
//      （unity-cli README §五）→ 用 [UnityTest] 真帧。
//   3. **驱动方式**：改权重后调一次 `RigBuilder.Build()`（真场景实测：改完权重 + 重建 → 生效）。
//      场景须在 build settings 里（`SceneManager.LoadScene` 按名加载；已登记为 index 0，
//      见 `ProjectSettings/EditorBuildSettings.asset`）。
using System;
using System.Collections;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Animations.Rigging;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using YANTF.ActionLab;

public class AnimationRiggingProbeTests
{
    private const string BaseSceneName = "ActionLab";

    // 演示常量（本探针用；非正典、非规格参数）
    private const float TargetOffsetX = 0.15f;     // 目标相对手的位置偏移：模长 0.19 m，确定在臂长可达范围内
    private const float TargetOffsetY = 0.10f;
    private const float TargetOffsetZ = 0.05f;
    private const float ReachedTolerance = 0.030f; // 权重拉满时手与目标距离容差 30 mm（两骨 IK 收敛残差）
    private const float InertMinDistance = 0.050f; // 对照项：权重 0 时手与目标**至少**应差这么远

    /// <summary>加载基准场景并等两帧（让 Awake/OnEnable 建图跑完）。</summary>
    private static IEnumerator LoadBaseScene()
    {
        SceneManager.LoadScene(BaseSceneName);
        yield return null;
        yield return null;
    }

    private static RigBuilder FindRigBuilder()
    {
        var rb = UnityEngine.Object.FindFirstObjectByType<RigBuilder>();
        Assert.IsNotNull(rb, "场景里找不到 RigBuilder——接入未落（场景被重建过？builder 改回旧版了？）");
        return rb;
    }

    private static TwoBoneIKConstraint FindLeftArmIK(RigBuilder rb)
    {
        var ik = rb.GetComponentInChildren<TwoBoneIKConstraint>();
        Assert.IsNotNull(ik, "场景里找不到 TwoBoneIKConstraint");
        return ik;
    }

    /// <summary>
    /// 测完把基准场景卸掉、留一个空场景。**不清理会连累别人**：本类按名字排序在 `WalkerLabSmokeTests`
    /// 之前跑，残留的 `ActionLab` 场景让它读到落地 y = **1.730**（它假设自己在干净场景里落体）——
    /// 2026-09-14 实测：53 条里就红这一条。
    /// </summary>
    [UnityTearDown]
    public IEnumerator TearDownScene()
    {
        if (!SceneManager.GetSceneByName(BaseSceneName).isLoaded) yield break;
        var empty = SceneManager.CreateScene("RigProbeEmpty");
        SceneManager.SetActiveScene(empty);
        yield return SceneManager.UnloadSceneAsync(BaseSceneName);
    }

    // ---------------- ① 结构 ----------------

    [UnityTest]
    public IEnumerator SceneRigInfrastructure_BindsLeftArmChain_AndStaysInert()
    {
        yield return LoadBaseScene();

        var rb = FindRigBuilder();
        Assert.AreEqual(1, rb.layers.Count, "Rig 层数应为 1（手工往场景加 Rig 会被下次重建冲掉）");

        var rig = rb.layers[0].rig;
        Assert.IsNotNull(rig, "layer[0].rig 为空");

        var animator = rb.GetComponent<Animator>();
        Assert.IsNotNull(animator, "载体上没有 Animator");
        var ik = FindLeftArmIK(rb);

        Assert.IsNotNull(ik.data.root, "骨链 root 为空（Humanoid 载体换过？FBX 开了 Optimize Game Objects？）");
        Assert.IsNotNull(ik.data.mid, "骨链 mid 为空");
        Assert.IsNotNull(ik.data.tip, "骨链 tip 为空");
        Assert.IsNotNull(ik.data.target, "约束目标为空");

        // 绑的必须是**左臂**真正的骨（绑错骨也能编译通过，故按 Humanoid 骨名对拍）
        Assert.AreEqual(animator.GetBoneTransform(HumanBodyBones.LeftUpperArm), ik.data.root, "root 不是 LeftUpperArm");
        Assert.AreEqual(animator.GetBoneTransform(HumanBodyBones.LeftLowerArm), ik.data.mid, "mid 不是 LeftLowerArm");
        Assert.AreEqual(animator.GetBoneTransform(HumanBodyBones.LeftHand), ik.data.tip, "tip 不是 LeftHand");

        // 惰性口径：本次接入**不产生行为**（消费方待定）
        Assert.AreEqual(0f, rig.weight, "Rig 权重应为 0（惰性）");
        Assert.AreEqual(0f, ik.weight, "约束权重应为 0（惰性）");
    }

    // ==================== #157：接触修正 lab（真场景 · 关/开同帧 · 派生件复现）====================
    //
    // 与上面两条的关系：上面两条测 **ActionLab** 的惰性接入点（基础设施）；下面四条测 **AnimationRiggingLab**
    // 这条独立 lab 上的**能力**（右手/双脚目标 + 关开对照 + 派生件复现）。两条线的场景不同、判据不重叠。
    //
    // ⚠️ 容差是**探针局部常量**（非正典、非规格参数），来源是 2026-09-14 的实测读数：
    //   M1 关 = 187.12 mm（= 固定目标偏移模长 187.08 mm）、M1 开 = 96.45 mm、M2 开 = 2.83 / 2.77 mm、
    //   派生件复现 = 96.45 / 2.82 / 2.72 mm。断言只判"读数落在实测值附近"与"方向对"，**不引入无来源阈值**。

    private const string LabSceneName = "AnimationRiggingLab";
    private const float LabOffsetTolerance = 0.001f;    // M1 关 vs 目标偏移模长（实测差 0.04 mm）
    private const float LabSoleTolerance = 0.003f;      // M2 开 vs soleMargin（实测差 0.03 mm）
    private const float LabBakedTolerance = 0.001f;     // 派生件复现 vs 约束开（实测差 0.06 mm）
    private const float LabReachImprovedMin = 0.050f;   // M1 开 至少比关近这么多（实测近 90.7 mm）

    private static IEnumerator LoadLabScene()
    {
        SceneManager.LoadScene(LabSceneName);
        yield return null;
        yield return null;
    }

    [UnityTearDown]
    public IEnumerator TearDownLabScene()
    {
        if (!SceneManager.GetSceneByName(LabSceneName).isLoaded) yield break;
        var empty = SceneManager.CreateScene("RigLabProbeEmpty");
        SceneManager.SetActiveScene(empty);
        yield return SceneManager.UnloadSceneAsync(LabSceneName);
    }

    private static AnimationRiggingProbe FindLabProbe()
    {
        var probe = UnityEngine.Object.FindFirstObjectByType<AnimationRiggingProbe>();
        Assert.IsNotNull(probe, "lab 场景里找不到 AnimationRiggingProbe（场景被重建过？builder 改回旧版了？）");
        return probe;
    }

    [UnityTest]
    public IEnumerator LabScene_HasThreeBoundConstraints_SerializedContactFrame_AndNoFootGroundingIK()
    {
        yield return LoadLabScene();
        var probe = FindLabProbe();

        Assert.AreEqual(1, probe.rigBuilder.layers.Count, "lab 的 Rig 层数应为 1");
        Assert.IsNotNull(probe.rightArmIK, "缺右手约束");
        Assert.IsNotNull(probe.leftLegIK, "缺左腿约束");
        Assert.IsNotNull(probe.rightLegIK, "缺右腿约束");

        foreach (var ik in new[] { probe.rightArmIK, probe.leftLegIK, probe.rightLegIK })
        {
            Assert.IsNotNull(ik.data.root, ik.name + "：root 空（Humanoid 载体换过？）");
            Assert.IsNotNull(ik.data.mid, ik.name + "：mid 空");
            Assert.IsNotNull(ik.data.tip, ik.name + "：tip 空");
            Assert.IsNotNull(ik.data.target, ik.name + "：target 空");
        }

        Assert.AreEqual(probe.animator.GetBoneTransform(HumanBodyBones.RightHand), probe.rightArmIK.data.tip, "右手链 tip 不是 RightHand");
        Assert.AreEqual(probe.animator.GetBoneTransform(HumanBodyBones.LeftFoot), probe.leftLegIK.data.tip, "左腿链 tip 不是 LeftFoot");
        Assert.AreEqual(probe.animator.GetBoneTransform(HumanBodyBones.RightFoot), probe.rightLegIK.data.tip, "右腿链 tip 不是 RightFoot");

        // 取帧结果与目标必须**序列化在场景里**（Play 期不能再算，见探针头注）
        Assert.GreaterOrEqual(probe.contactFrame, 0, "场景里没有接触帧（contactFrame < 0）——重新跑 builder 菜单");
        Assert.IsNotNull(probe.rightHandTarget, "右手目标为空");
        Assert.IsNotNull(probe.leftFootTarget, "左脚目标为空");
        Assert.IsNotNull(probe.rightFootTarget, "右脚目标为空");

        // §3.1 读数归属唯一：lab 内**不得**挂运行时足部贴地组件
        Assert.IsNull(probe.GetComponent<FootGroundingIK>(),
            "lab 载体上挂了 FootGroundingIK——§3.1 要求双脚贴地只由 rig 约束负责，否则 M2 无法归属");
    }

    [UnityTest]
    public IEnumerator LabScene_ConstraintOff_vs_On_AtSameFrame_MovesHandAndGroundsFeet()
    {
        yield return LoadLabScene();
        var probe = FindLabProbe();
        var clip = (AnimationClip)CallEditor("AnimationRiggingLabBuilder", "LoadSourceClip");
        Assert.IsNotNull(clip, "取不到源 clip（PhysicalAttack.fbx）");

        // ---- 关：权重 0，真帧等约束图求值 ----
        probe.PoseAtFrame(clip, probe.contactFrame);
        probe.SetWeights(0f);
        for (int i = 0; i < 3; i++) yield return null;
        var off = probe.Measure(probe.contactFrame, 0f, "off");

        // ---- 开：同一帧、只差权重（§3.1）----
        probe.SetWeights(1f);
        for (int i = 0; i < 3; i++) yield return null;
        var on = probe.Measure(probe.contactFrame, 1f, "on");

        float offsetMagnitudeMm = new Vector3(
            AnimationRiggingProbe.TargetOffsetRight,
            AnimationRiggingProbe.TargetOffsetUp,
            AnimationRiggingProbe.TargetOffsetForward).magnitude * 1000f;

        Assert.AreEqual(offsetMagnitudeMm / 1000f, off.m1_handTargetMm / 1000f, LabOffsetTolerance,
            $"约束关时手↔目标应为目标偏移模长 {offsetMagnitudeMm:F1} mm，实测 {off.m1_handTargetMm:F1} mm" +
            "——目标不是在接触帧上手位 + 偏移处（取帧/目标布置跑偏了？）");

        Assert.Less(on.m1_handTargetMm, off.m1_handTargetMm - LabReachImprovedMin * 1000f,
            $"约束开后手没有明显靠近目标：关 {off.m1_handTargetMm:F1} mm → 开 {on.m1_handTargetMm:F1} mm");

        Assert.AreEqual(AnimationRiggingProbe.SoleMargin, on.m2_leftSoleMm / 1000f, LabSoleTolerance,
            $"约束开后左足底应停在 soleMargin={AnimationRiggingProbe.SoleMargin * 1000f:F1} mm，实测 {on.m2_leftSoleMm:F1} mm");
        Assert.AreEqual(AnimationRiggingProbe.SoleMargin, on.m2_rightSoleMm / 1000f, LabSoleTolerance,
            $"约束开后右足底应停在 soleMargin={AnimationRiggingProbe.SoleMargin * 1000f:F1} mm，实测 {on.m2_rightSoleMm:F1} mm");
        Assert.Less(off.m2_leftSoleMm, 0f, "对照项失效：约束关时左脚本该陷入地面（实测 -24.0 mm）");
        Assert.Less(off.m2_rightSoleMm, 0f, "对照项失效：约束关时右脚本该陷入地面（实测 -34.9 mm）");

        // 根与骨长不应被约束改动（M3/M4 不变量）
        Assert.AreEqual(off.m3a_hipDriftMm, on.m3a_hipDriftMm, 0.01f, "约束改了根水平位置（应当不动）");
        Assert.AreEqual(off.m3b_hipYawDeg, on.m3b_hipYawDeg, 0.01f, "约束改了根朝向（应当不动）");
        Assert.AreEqual(off.m4_upperArmMm, on.m4_upperArmMm, 0.1f, "约束改了上臂骨长（应当不动）");
        Assert.AreEqual(off.m4_upperLegMm, on.m4_upperLegMm, 0.1f, "约束改了大腿骨长（应当不动）");
    }

    [UnityTest]
    public IEnumerator BakedClip_ReproducesCorrectedReadings_WithoutConstraints()
    {
        yield return LoadLabScene();
        var probe = FindLabProbe();
        var clip = (AnimationClip)CallEditor("AnimationRiggingLabBuilder", "LoadSourceClip");
        var baked = (AnimationClip)CallEditor("AnimationRiggingLabBuilder", "LoadBakedForProbe");
        Assert.IsNotNull(baked, "派生件缺失：Assets/Animations/Derived/PhysicalAttack_ContactCorrected.anim（跑烘焙菜单）");

        // ---- 参照读数：约束开 ----
        probe.PoseAtFrame(clip, probe.contactFrame);
        probe.SetWeights(1f);
        for (int i = 0; i < 3; i++) yield return null;
        var on = probe.Measure(probe.contactFrame, 1f, "on");

        // ---- 派生件：关约束、只采派生 clip ----
        probe.SetWeights(0f);
        baked.SampleAnimation(probe.gameObject, probe.contactFrame / (baked.frameRate > 0f ? baked.frameRate : 30f));
        var hand = probe.animator.GetBoneTransform(HumanBodyBones.RightHand);
        float bakedM1 = Vector3.Distance(hand.position, probe.rightHandTarget.position) * 1000f;
        float bakedM2L = probe.SoleHeight(HumanBodyBones.LeftFoot, HumanBodyBones.LeftToes) * 1000f;
        float bakedM2R = probe.SoleHeight(HumanBodyBones.RightFoot, HumanBodyBones.RightToes) * 1000f;

        Assert.AreEqual(on.m1_handTargetMm / 1000f, bakedM1 / 1000f, LabBakedTolerance,
            $"派生件（约束关）未复现约束开的右手距离：开 {on.m1_handTargetMm:F2} mm vs 派生 {bakedM1:F2} mm");
        Assert.AreEqual(on.m2_leftSoleMm / 1000f, bakedM2L / 1000f, LabBakedTolerance,
            $"派生件左脚底高度未复现：开 {on.m2_leftSoleMm:F2} mm vs 派生 {bakedM2L:F2} mm");
        Assert.AreEqual(on.m2_rightSoleMm / 1000f, bakedM2R / 1000f, LabBakedTolerance,
            $"派生件右脚底高度未复现：开 {on.m2_rightSoleMm:F2} mm vs 派生 {bakedM2R:F2} mm");
    }

    // ---------------- 反射桥（只用于"取资产"这一步；口径同 ActionLabGripTests 头注）----------------

    private static object CallEditor(string typeName, string method, params object[] args)
    {
        Type t = null;
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            t = asm.GetType("YANTF.EditorTools." + typeName, false);
            if (t != null) break;
        }
        Assert.IsNotNull(t, "找不到 YANTF.EditorTools." + typeName + "（Editor 侧程序集未加载？）");
        var m = t.GetMethod(method, BindingFlags.Public | BindingFlags.Static);
        Assert.IsNotNull(m, "找不到 " + typeName + "." + method);
        return m.Invoke(null, args);
    }

    // ---------------- ② 能力（约束真的求值）＋ 对照项 ----------------

    [UnityTest]
    public IEnumerator SceneRigConstraint_EvaluatesOnHumanoidCarrier_AndMovesHand()
    {
        yield return LoadBaseScene();

        var rb = FindRigBuilder();
        var rig = rb.layers[0].rig;
        var ik = FindLeftArmIK(rb);
        var animator = rb.GetComponent<Animator>();
        var hand = animator.GetBoneTransform(HumanBodyBones.LeftHand);
        Assert.IsNotNull(hand, "取不到 LeftHand 骨");

        // 目标挪到手附近 0.19 m 处（可达范围内）——场景里的哑目标原本就在手位，先挪开才有对照
        ik.data.target.position = hand.position + new Vector3(TargetOffsetX, TargetOffsetY, TargetOffsetZ);
        for (int i = 0; i < 3; i++) yield return null;
        var distInert = Vector3.Distance(hand.position, ik.data.target.position);

        // ---- 就位：权重拉满 + 重建图 ----
        rig.weight = 1f;
        ik.weight = 1f;
        Assert.IsTrue(rb.Build(), "权重拉满后 RigBuilder.Build() 返回 false：没建出有效 PlayableGraph");
        for (int i = 0; i < 12; i++) yield return null;
        var distOn = Vector3.Distance(hand.position, ik.data.target.position);

        Assert.Greater(distInert, InertMinDistance,
            $"对照项失效：权重 0 时手离目标仅 {distInert * 1000f:F1} mm（应 >= {InertMinDistance * 1000f:F0} mm）" +
            "——手本来就贴着目标，本测试区分不出约束是否生效");

        Assert.Less(distOn, ReachedTolerance,
            $"权重拉满（重建后）手与目标距离 {distOn * 1000f:F1} mm（应 <= {ReachedTolerance * 1000f:F0} mm）；" +
            $"对照：权重 0 时 {distInert * 1000f:F1} mm；目标偏移 " +
            $"{new Vector3(TargetOffsetX, TargetOffsetY, TargetOffsetZ).magnitude * 1000f:F0} mm" +
            "——约束没求值（骨链未绑？载体不是 Humanoid？场景里的 RigBuilder 没建图？）");
    }
}
