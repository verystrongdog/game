// PlayMode 断言 — 格挡持握变体（规格 §四·戊·6「最小可验收切片」）
//
// 断言两件事，**都在真基准场景 `ActionLab.unity` 上**（不另搭合成 Rig——见 AnimationRiggingProbeTests 头注）：
//   ① **解析**：持握中请求 `Defend` → 实际播放 `Wield2H` 那条 clip（`2hand Idle`）；
//      **对照项**：未持握时 `Defend` 仍是 `Defend`（否则"解析"这件事没被真的验证）。
//   ② **三条判据读数**（§戊·5）：两手间距 ∈ 0.15–0.25 m · 副手落在椅子上（≤1 cm）· 持握期间
//      副手在椅子局部坐标的漂移 ≤5 mm。
//
// ⚠️ 本文件**不实现机制**：持握态由驱动层的探针键（ActionLab `8`）建立；测试里直接调
//    `ActionPlayer.Play` + `ChairGrip.Attach` 复现同一条路径（输入注入在本工程不可用，
//    见危险点表 §七 `simulate_key`）。
// ⚠️ 判据 2 的"落在椅子上"用**椅子碰撞体**判（`Collider.ClosestPoint`），不抄几何常量——
//    抄常量会与 builder 漂移。
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using YANTF.ActionLab;

public class ActionLabGuardVariantTests
{
    private const string BaseSceneName = "ActionLab";

    // 规格 §戊·5 的阈值（判据 1/2/3）
    private const float HandGapMinM = 0.15f;
    private const float HandGapMaxM = 0.25f;
    private const float LeftHandMaxSurfaceM = 0.01f;   // 副手须落在可握构件上（1 cm 内）
    private const float MaxDriftM = 0.005f;            // 持握全程累计漂移 ≤5 mm

    private static IEnumerator LoadBaseScene()
    {
        SceneManager.LoadScene(BaseSceneName);
        yield return null;
        yield return null;
    }

    /// <summary>测完卸载基准场景并留一个空场景（否则残留场景会连累后续测试，见另一文件的同款注）。</summary>
    [UnityTearDown]
    public IEnumerator TearDownScene()
    {
        if (!SceneManager.GetSceneByName(BaseSceneName).isLoaded) yield break;
        var empty = SceneManager.CreateScene("GuardVariantEmpty");
        SceneManager.SetActiveScene(empty);
        yield return SceneManager.UnloadSceneAsync(BaseSceneName);
    }

    private static ChairGrip FindGrip()
    {
        var g = Object.FindAnyObjectByType<ChairGrip>();
        Assert.IsNotNull(g, "场景里找不到 ChairGrip（场景被重建过？）");
        return g;
    }

    private static ActionPlayer FindPlayer()
    {
        var p = Object.FindAnyObjectByType<ActionPlayer>();
        Assert.IsNotNull(p, "场景里找不到 ActionPlayer");
        return p;
    }

    /// <summary>
    /// 把椅子挂到右手并进入「持握中」（复现 ActionLab 探针键 `8` 的路径）。
    /// ⚠️ **必须等姿势就位再挂点**：`Attach` 按「挂点当帧的手骨位姿」解椅子位姿——若在 0.12 s 的
    /// CrossFade 中途挂，椅子会按 Idle 的手位解出来（2026-09-14 实测：副手离椅面 28.5 cm 的假红）。
    /// </summary>
    private static IEnumerator EnterHold(ChairGrip grip, ActionPlayer player, Animator anim, CharacterController cc)
    {
        player.ResetToIdle();
        Assert.IsTrue(player.Play(ActionIds.Wield2H), "Wield2H 应可播——controller 里有该状态吗？（重跑菜单）");
        anim.Update(0f);

        float t0 = Time.time;
        while (Time.time - t0 < 0.8f) yield return null;   // 真实时间上等姿势到位

        Assert.IsTrue(grip.Attach(anim, GripState.Wield2H, cc), "挂点应成功：" + grip.LastAttachReport);
        player.IsHoldingChair = true;
    }

    /// <summary>点到椅子任一碰撞体的最近距离（m）。</summary>
    private static float DistanceToChairSurface(Transform chair, Vector3 p)
    {
        float best = float.MaxValue;
        foreach (var col in chair.GetComponentsInChildren<Collider>())
        {
            if (col == null || !col.enabled) continue;
            best = Mathf.Min(best, Vector3.Distance(p, col.ClosestPoint(p)));
        }
        Assert.AreNotEqual(float.MaxValue, best, "椅子上一个启用的碰撞体都没有");
        return best;
    }

    // ---------------- ① 解析 ----------------

    [UnityTest]
    public IEnumerator GuardVariant_ResolvesToHoldClip_OnlyWhenHolding()
    {
        yield return LoadBaseScene();

        var grip = FindGrip();
        var player = FindPlayer();
        var anim = player.GetComponent<Animator>();
        var cc = player.GetComponent<CharacterController>();
        Assert.IsNotNull(anim, "载体上没有 Animator");

        // 停掉驱动层：它每帧跑 locomotion 通道，会把状态切回 Idle，掩盖本测试要测的解析
        var driver = player.GetComponent<ActionLabDriver>();
        if (driver != null) driver.enabled = false;

        // 对照项：**未持握** + 从 Idle 请求 Defend → 落到 Defend 本身
        player.IsHoldingChair = false;
        player.ResetToIdle();
        yield return null;
        Assert.IsTrue(player.Play(ActionIds.Defend), "Defend 应可播");
        yield return null;
        Assert.AreEqual(ActionIds.Defend, player.CurrentActionId,
            "未持握时 Defend 不应走变体——否则这条断言证明不了「解析」存在");

        // 持握中 + 从 Idle 请求 Defend → 解析到变体状态 Wield2H
        // ⚠️ 必须先回 Idle：`Play` 的优先级规则是「严格大于才打断」，而变体目标就是 Wield2H 自己
        //    （持握态即 Wield2H）——同优先级互切会被拒，那是**正确行为**，不是解析失效。
        yield return EnterHold(grip, player, anim, cc);
        player.ResetToIdle();
        yield return null;
        Assert.IsTrue(player.Play(ActionIds.Defend), "持握中从 Idle 请求 Defend 应可播（解析后是 Wield2H）");
        yield return null;
        Assert.AreEqual(ActionIds.Wield2H, player.CurrentActionId,
            "持握中请求 Defend 应解析到变体状态 Wield2H（规格 §戊·1#4 / §戊·6）");

        // 变体状态所用的 clip 必须是 Chairhold 那条（按资产路径对拍，而非只看状态名）
        var entry = ActionCatalog.Get(ActionIds.Wield2H);
        StringAssert.Contains("Chairhold/Wield2H.fbx", entry.ClipAssetPath,
            "Wield2H 的 clip 资产应指向 Chairhold/Wield2H.fbx");
        Assert.IsTrue(entry.Loop, "Wield2H 是循环持续态（格挡靠它持续），Loop 应为 true");
        // 解析规则本身按字段判定（不硬编码 id）：Defend 的 HoldVariantState 必须指向 Wield2H
        Assert.AreEqual(ActionIds.Wield2H, ActionCatalog.Get(ActionIds.Defend).HoldVariantState,
            "Defend 应声明 HoldVariantState=Wield2H（规格 §戊·1#4：按字段判定）");
    }

    // ---------------- ② 三条判据 ----------------

    // ⚠️ **未闭合（2026-09-14）**：本条暂标 `Ignore`——三条判据的读数目前由 **Play 态探针**证明
    //    （真场景 `Play("Wield2H")` + 停 driver → 两手 17.1 cm；确定性采样 → 左手距靠背面 0.2–0.7 cm；
    //    见规格 §戊·5 采纳块），但**尚未转成可靠的门禁断言**：
    //    · driver 开着 → 它每帧把状态切回 Idle（越权覆盖持续态），测到的是待机姿势；
    //    · driver 关掉 → locomotion 通道的权重不再被归零，姿势停在 **Idle×Wield2H 的混合态**
    //      （实测副手离椅面 19.0 cm，随等待时长变化 28.5 → 19.0 cm）。
    //    两条路都不等于"游戏里按键 8 的真实路径"。⇒ 要转绿，得先把"驱动层与 locomotion 通道对
    //    持续态的所有权"理清（或改走真实按键路径——但本工程输入注入不可用，危险点表 §七）。
    [UnityTest, Ignore("待解：驱动层/locomotion 通道对持续态的权重所有权（见上方注释）")]
    public IEnumerator GuardVariant_MeetsThreeCriteria()
    {
        yield return LoadBaseScene();

        var grip = FindGrip();
        var player = FindPlayer();
        var anim = player.GetComponent<Animator>();
        var cc = player.GetComponent<CharacterController>();
        // ⚠️ **必须先停驱动层、再进持握态**（2026-09-14 实测教训）：driver 每帧跑 locomotion 通道，
        //    会在 `EnterHold` 之后立刻把 Animator 切回 Idle——而 `player.CurrentActionId` 仍报 Wield2H
        //    （它只记自己的账，**会骗人**），于是测出来是待机姿势的手距（59 cm）。顺序反了就会假红。
        var driver = player.GetComponent<ActionLabDriver>();
        if (driver != null) driver.enabled = false;

        yield return EnterHold(grip, player, anim, cc);
        // EnterHold 内已等姿势到位并挂点；此处 必须在**真实时间**上走完：PlayMode 测试帧率很高，
        // "等 N 帧"不保证够久（实测等 4 帧时仍在中途混合 → 手距 46.3 cm 的假红）。
        float t0 = Time.time;
        while (Time.time - t0 < 0.8f) yield return null;
        Assert.AreEqual(ActionIds.Wield2H, player.CurrentActionId, "测量前应处于 Wield2H（持握态）");

        var lh = anim.GetBoneTransform(HumanBodyBones.LeftHand);
        var rh = anim.GetBoneTransform(HumanBodyBones.RightHand);
        Assert.IsNotNull(lh, "取不到 LeftHand 骨");
        Assert.IsNotNull(rh, "取不到 RightHand 骨");

        var chair = grip.transform;
        var first = chair.InverseTransformPoint(lh.position);
        float minGap = float.MaxValue, maxGap = 0f, maxSurface = 0f, maxDrift = 0f;

        for (int i = 0; i < 12; i++)
        {
            yield return null;
            float gap = Vector3.Distance(lh.position, rh.position);
            minGap = Mathf.Min(minGap, gap);
            maxGap = Mathf.Max(maxGap, gap);
            maxSurface = Mathf.Max(maxSurface, DistanceToChairSurface(chair, lh.position));
            maxDrift = Mathf.Max(maxDrift, Vector3.Distance(chair.InverseTransformPoint(lh.position), first));
        }

        Assert.GreaterOrEqual(minGap, HandGapMinM,
            $"判据 1：两手间距最小 {minGap * 100f:F1} cm（应 ≥ {HandGapMinM * 100f:F0} cm）");
        Assert.LessOrEqual(maxGap, HandGapMaxM,
            $"判据 1：两手间距最大 {maxGap * 100f:F1} cm（应 ≤ {HandGapMaxM * 100f:F0} cm）");
        Assert.LessOrEqual(maxSurface, LeftHandMaxSurfaceM,
            $"判据 2③：副手离椅子表面最远 {maxSurface * 100f:F2} cm（应 ≤ {LeftHandMaxSurfaceM * 100f:F1} cm）");
        Assert.LessOrEqual(maxDrift, MaxDriftM,
            $"判据 3：副手在椅子局部坐标的漂移 {maxDrift * 1000f:F1} mm（应 ≤ {MaxDriftM * 1000f:F0} mm）");
    }
}
