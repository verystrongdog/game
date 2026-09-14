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
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Animations.Rigging;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

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
        var rb = Object.FindFirstObjectByType<RigBuilder>();
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
