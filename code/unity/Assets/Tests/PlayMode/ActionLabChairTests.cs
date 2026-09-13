// PlayMode 断言 — 就座交互「先找到椅子才能坐」（规格 §四·丁 / issue #141）
//
// 改前是什么样：按 6 无条件播 Sit——不看有没有椅子、也不看人在哪；场景里只有一张**无碰撞体**的凳子，
// 位置是烘死常量（角色 transform 在原点时的实测落点）。于是"坐在椅子上"只在出生点成立。
//
// 本文件断言三件事：
//   ① 判定口径（距离 + 前侧 + 空闲；多张取最近）——纯函数与场景件两层
//   ② 锚点是**实时**的（椅子被搬动后落点跟随），占用锁切换刚体与碰撞
//   ③ 驱动层链路：无椅子 → 不切态 + 提示；在锚点旁 → 对齐到锚点 → 播 Sit；坐姿下移动 → 先起身
// 几何落点（臀部是否真落在坐面上）属**实测读数**，在 Editor Play 会话里量（见 code/unity/README.md §二·J）。
using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using YANTF.ActionLab;

public class ActionLabChairTests
{
    private readonly List<GameObject> _created = new List<GameObject>();

    [TearDown]
    public void TearDown()
    {
        foreach (var go in _created) if (go != null) Object.DestroyImmediate(go);
        _created.Clear();
    }

    private GameObject Track(GameObject go) { _created.Add(go); return go; }

    /// <summary>测试地面：没有它 CharacterController 不会 isGrounded，动作层会按"空中"拒绝动作。</summary>
    private void EnsureGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "TestGround";
        ground.transform.localScale = new Vector3(4f, 1f, 4f);
        Track(ground);
    }

    /// <summary>造一张椅子（builder 的 AddChair 的最小版：Root + Rigidbody + ChairSeat + 坐板碰撞体）。</summary>
    private ChairSeat MakeChair(Vector3 position, float yaw)
    {
        var root = Track(new GameObject("TestChair"));
        root.transform.position = position;
        root.transform.rotation = Quaternion.Euler(0f, yaw, 0f);

        var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);   // 带 BoxCollider = 实心
        seat.name = "Seat";
        seat.transform.SetParent(root.transform, false);
        seat.transform.localPosition = new Vector3(0f, 0.4199f, 0f);
        seat.transform.localScale = new Vector3(0.42f, 0.05f, 0.42f);

        var rb = root.AddComponent<Rigidbody>();
        rb.mass = 6f;
        rb.useGravity = false;   // 测试件不建腿，故关重力（否则刚体会先落到地面，锚点读数漂掉）
        rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;

        var chair = root.AddComponent<ChairSeat>();
        chair.anchorDistance = ChairSeat.DefaultAnchorDistance;
        chair.interactRadius = ChairSeat.DefaultInteractRadius;
        return chair;
    }

    /// <summary>造一个可被驱动的角色（CC + ActionPlayer + ActionLabDriver；无 Animator → 只验状态逻辑与对齐位移）。</summary>
    private ActionLabDriver MakePlayer(Vector3 position)
    {
        var go = Track(new GameObject("TestActor"));
        go.transform.position = position + Vector3.up * 0.1f;   // 略高于地面，让 CC 落到接触面
        go.AddComponent<CharacterController>();
        go.AddComponent<ActionPlayer>();
        return go.AddComponent<ActionLabDriver>();
    }

    private static float Flat(Vector3 a, Vector3 b) => new Vector2(a.x - b.x, a.z - b.z).magnitude;

    /// <summary>等角色落地：动作层对空中请求一律拒绝（否则断言测到的会是那条守卫，而不是就座链路）。</summary>
    private static IEnumerator WaitGrounded(ActionLabDriver driver, float timeout = 3f)
    {
        float t = 0f;
        while (driver.player.IsAirborne && t < timeout)
        {
            yield return null;
            t += Time.deltaTime;
        }
    }

    // ---- ① 判定口径 ----

    /// <summary>三条件：站在锚点上可坐；超出半径不可坐；已占用不可坐。</summary>
    [Test]
    public void IsUsable_RequiresRangeAndFree()
    {
        Vector3 center = Vector3.zero, forward = Vector3.forward;
        Vector3 anchor = center + forward * ChairSeat.DefaultAnchorDistance;

        Assert.IsTrue(ChairSeat.IsUsable(center, forward, ChairSeat.DefaultAnchorDistance, ChairSeat.DefaultInteractRadius,
            anchor, false, out float d0), "站在锚点上必须判定可坐");
        Assert.Less(d0, 1e-4f, "锚点处的距离读数应为 0");

        // 距锚点 0.30 m > 半径 0.25 m：仍**在椅子前侧**，故这一条只可能被"距离"否掉
        Vector3 farButInFront = anchor + forward * 0.30f;
        Assert.IsFalse(ChairSeat.IsUsable(center, forward, ChairSeat.DefaultAnchorDistance, ChairSeat.DefaultInteractRadius,
            farButInFront, false, out float d1), "超出交互半径不得判定可坐（改前：无条件可坐）");
        Assert.AreEqual(0.30f, d1, 1e-4f, "距离读数应等于到锚点的水平距离");

        Assert.IsFalse(ChairSeat.IsUsable(center, forward, ChairSeat.DefaultAnchorDistance, ChairSeat.DefaultInteractRadius,
            anchor, true, out _), "已占用的椅子不得被第二人选中");
    }

    /// <summary>「在椅子前侧」这一条单独起作用（半径放大到超过锚点距离时才不被距离条件蕴含）。</summary>
    [Test]
    public void IsUsable_BehindChair_RejectedEvenWithinLargerRadius()
    {
        Vector3 center = Vector3.zero, forward = Vector3.forward;
        Vector3 behind = center - forward * 0.15f;    // 坐面中心**后方**
        const float bigRadius = 0.60f;

        float dist = Vector3.Distance(behind, center + forward * ChairSeat.DefaultAnchorDistance);
        Assert.Less(dist, bigRadius, "前提：该点落在放大后的半径内（否则这条断言测的不是「前侧」）");

        Assert.IsFalse(ChairSeat.IsUsable(center, forward, ChairSeat.DefaultAnchorDistance, bigRadius, behind, false, out _),
            "椅子后方的点即使在上半径内也不得判定可坐（否则会隔着椅子坐进去）");
    }

    // ---- ② 场景件：实时锚点 / 最近选取 / 占用锁 ----

    /// <summary>锚点由椅子 transform 实时求得——搬动椅子后落点跟随同样的位移（"烘死常量"的反面）。</summary>
    [Test]
    public void Anchor_FollowsChairTransform()
    {
        var chair = MakeChair(new Vector3(2f, 0f, 1f), 90f);
        Vector3 before = chair.AnchorPosition;

        chair.transform.position += new Vector3(-1.5f, 0f, 0.75f);

        Vector3 moved = chair.AnchorPosition - before;
        Assert.AreEqual(-1.5f, moved.x, 1e-4f, "锚点 x 必须随椅子一起移动");
        Assert.AreEqual(0.75f, moved.z, 1e-4f, "锚点 z 必须随椅子一起移动");
        Assert.AreEqual(chair.transform.position + chair.transform.forward * ChairSeat.DefaultAnchorDistance,
            chair.AnchorPosition, "锚点 = 坐面中心 + forward × 锚点距离（规格 §四·丁）");
    }

    /// <summary>多张椅子取最近；最近的那张被占用后退而取次近的空闲椅。</summary>
    [Test]
    public void FindBest_PicksNearest_ThenSkipsOccupied()
    {
        var near = MakeChair(new Vector3(1f, 0f, 0f), 0f);
        var far = MakeChair(new Vector3(4f, 0f, 0f), 0f);

        Assert.AreSame(near, ChairSeat.FindBest(near.AnchorPosition), "站在近椅锚点上必须选近椅");
        Assert.IsNull(ChairSeat.FindBest(new Vector3(20f, 0f, 20f)), "远离所有椅子时必须返回 null（而非随便挑一张）");

        near.Occupy(null);
        Assert.AreSame(far, ChairSeat.FindBest(far.AnchorPosition), "近椅被占用后应选次近的空闲椅");
        near.Release(null);
    }

    /// <summary>占用锁：kinematic 切换（就座期间椅子不可推，规格 §四·丁#6）。</summary>
    [Test]
    public void Occupy_And_Release_ToggleKinematic()
    {
        var chair = MakeChair(Vector3.zero, 0f);
        Assert.IsFalse(chair.Body.isKinematic, "空闲椅子应为动态刚体（可被角色推开）");

        chair.Occupy(null);
        Assert.IsTrue(chair.IsOccupied);
        Assert.IsTrue(chair.Body.isKinematic, "占用期间椅子必须锁定（不可推）");

        chair.Release(null);
        Assert.IsFalse(chair.IsOccupied);
        Assert.IsFalse(chair.Body.isKinematic, "解除占用后椅子恢复可推");
    }

    // ---- ③ 词表契约与动作层离座口径 ----

    /// <summary>坐立三段声明 XZ 根位移；SitIdle 声明 ExitVia=Stand；其余词条两字段必须为空/false。</summary>
    [Test]
    public void Catalog_SitChain_DeclaresRootMotionXZ_And_ExitVia()
    {
        Assert.IsTrue(ActionCatalog.Get(ActionIds.Sit).RootMotionXZ, "Sit 必须声明 XZ 根位移（退到坐面上）");
        Assert.IsTrue(ActionCatalog.Get(ActionIds.SitIdle).RootMotionXZ, "SitIdle 必须声明 XZ 根位移");
        Assert.IsTrue(ActionCatalog.Get(ActionIds.Stand).RootMotionXZ, "Stand 必须声明 XZ 根位移（起身离椅）");
        Assert.AreEqual(ActionIds.Stand, ActionCatalog.Get(ActionIds.SitIdle).ExitVia,
            "SitIdle 必须声明 ExitVia=Stand：离座要先起身（规格 §四·丁#7）");

        foreach (var entry in ActionCatalog.All)
        {
            if (entry.Id == ActionIds.Sit || entry.Id == ActionIds.SitIdle || entry.Id == ActionIds.Stand) continue;
            Assert.IsFalse(entry.RootMotionXZ, entry.Id + " 不应声明 XZ 根位移（locomotion 位移全由输入驱动）");
            Assert.IsNull(entry.ExitVia, entry.Id + " 不应声明 ExitVia");
        }
    }

    /// <summary>坐姿下收到移动意图 → 先播 Stand（改前：无起身动画，直接弹回 locomotion）。</summary>
    [UnityTest]
    public IEnumerator SeatedWithMoveIntent_PlaysStandFirst()
    {
        var go = Track(new GameObject("TestActionPlayer"));
        var player = go.AddComponent<ActionPlayer>();          // 无 Animator：只验状态选择与计时

        Assert.IsTrue(player.Play(ActionIds.Sit), "站在地面上的 Idle 应能进入 Sit");
        Assert.IsTrue(player.IsLocked, "坐下是一次性动作：播放期间锁移动切态");
        Assert.IsTrue(player.ApplyRootMotionXZ, "Sit 声明了 XZ 根位移 → 驱动层应据此施加 clip 根位移");

        // 无 Animator 时动作层用兜底时长（1.05 s）计时；等到它按 nextState 续切到 SitIdle
        float waited = 0f;
        while (player.CurrentActionId != ActionIds.SitIdle && waited < 3f)
        {
            yield return null;
            waited += Time.deltaTime;
        }

        Assert.AreEqual(ActionIds.SitIdle, player.CurrentActionId, "Sit 播完必须续切 SitIdle（坐得住）");
        Assert.IsFalse(player.IsLocked, "SitIdle 是持续态：不锁移动切态");
        Assert.IsTrue(player.ApplyRootMotionXZ, "SitIdle 声明了 XZ 根位移");

        player.TickLocomotion(true, 0.5f);                     // 坐姿下按 W
        Assert.AreEqual(ActionIds.Stand, player.CurrentActionId,
            "坐姿下收到移动意图必须先起身（改前：无起身动画直接弹回走路）");
        Assert.IsTrue(player.IsLocked, "起身是一次性动作 → 锁移动切态");
        // 不断言 LastRequestedState：它由 CrossFadeState 记账，而 StartAction 只在**有 controller** 时才发
        // CrossFade（本测试无 Animator）→ 该字段会停留在上一次续切 SitIdle 的记录上，不是本断言的判据。
    }

    /// <summary>离座口径按词表字段判定，不硬编码 id：Defend 没声明 ExitVia → 仍直接回 locomotion。</summary>
    [Test]
    public void DefendExit_WithoutExitVia_GoesStraightToLocomotion()
    {
        var go = Track(new GameObject("TestActionPlayer2"));
        var player = go.AddComponent<ActionPlayer>();

        Assert.IsTrue(player.Play(ActionIds.Defend), "防御应能进入（持续态）");

        player.TickLocomotion(true, 0.5f);                     // 移动意图 → 退出持续态
        Assert.IsNull(player.CurrentActionId, "未声明 ExitVia 的持续态应直接回 locomotion（不得插播动作）");
        Assert.AreEqual(ActionIds.Walk, player.LastRequestedState);
    }

    // ---- ④ 驱动层链路 ----

    /// <summary>没有椅子 → 按 6 不切态、只留提示（改前：无条件播 Sit）。</summary>
    [UnityTest]
    public IEnumerator Driver_WithoutChair_RejectsSit()
    {
        EnsureGround();
        var driver = MakePlayer(Vector3.zero);
        yield return null;                                     // 等 Awake
        yield return WaitGrounded(driver);                     // 等落地（空中请求会被另一条守卫拒掉）
        Assert.IsFalse(driver.player.IsAirborne, "前提：角色已落地（否则被拒的理由会是空中不能就座）");

        Assert.IsFalse(driver.TrySitOnNearestChair(), "附近没有椅子时必须拒绝就座");
        Assert.IsNull(driver.player.CurrentActionId, "被拒后不得产生任何动作（不得原地坐下）");
        Assert.IsNotNull(driver.LastSitHint, "被拒必须留下 HUD 提示");
        StringAssert.Contains("没有椅子", driver.LastSitHint);
        Assert.IsNull(driver.OccupiedChair, "被拒不得占用任何椅子");
    }

    /// <summary>在锚点旁 → 命中 → 对齐到锚点 → 播 Sit 且锁定该椅；链上重复触发被拒。</summary>
    [UnityTest]
    public IEnumerator Driver_NearAnchor_SitsOnThatChair_AndLocksIt()
    {
        EnsureGround();
        var chair = MakeChair(new Vector3(2.5f, 0f, -0.5f), 35f);
        // 起点取"椅子挡得住的最远处外侧"：锚点再沿椅子 forward 外移 0.15 m（实心椅子把角色挡在
        // 离坐面中心 0.522 m 处，故贴不到锚点上；这也正是对齐段存在的理由）
        var driver = MakePlayer(chair.AnchorPosition + chair.Forward * 0.15f);
        yield return null;
        yield return WaitGrounded(driver);                     // 等落地（空中请求会被守卫拒掉）

        Assert.LessOrEqual(Flat(driver.transform.position, chair.AnchorPosition), chair.interactRadius,
            "前提：测试起点在交互半径内");

        Assert.IsTrue(driver.TrySitOnNearestChair(), "锚点旁按 6 必须命中");
        Assert.AreSame(chair, driver.OccupiedChair, "命中后该椅进入占用态");
        Assert.IsTrue(chair.IsOccupied);
        Assert.IsTrue(chair.Body.isKinematic, "占用期间椅子锁定（不可推）");
        Assert.IsFalse(driver.TrySitOnNearestChair(), "已在坐立链上时不得重复触发");

        float waited = 0f;
        while (driver.IsAligning && waited < 3f)
        {
            yield return null;
            waited += Time.deltaTime;
        }

        Assert.IsFalse(driver.IsAligning, "对齐段应在 alignSeconds 内结束");
        Assert.Less(Flat(driver.transform.position, chair.AnchorPosition), 0.02f,
            "对齐后角色应站在就座锚点上（只有站在锚点上，坐下后臀部才落在坐面上）");
        Assert.AreEqual(ActionIds.Sit, driver.player.CurrentActionId, "对齐完成后必须播 Sit");
        Assert.IsTrue(driver.player.IsLocked, "Sit 播放期间锁移动切态");
    }
}
