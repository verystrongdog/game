// PlayMode 断言 — 持椅交互（手里有东西）的资产侧与挂点侧机械检查（规格 §四·戊 / issue #150 · #152）
//
// 本文件断言两类事实：
//   ① 派生件（只剩 SitDown 时间反转；#150 的镜像变换已于 2026-09-14 退役，见规格 §戊·5）：
//   ② 持椅挂点（#152）：锚点实时性、挂点"三者同时"、逐状态基准朝向、手到位帧读数、阻尼收敛、与就座不互抢
//
// ⚠️ **为什么一部分经反射调 Editor 侧**：本 asmdef（`YANTF.Demo.Tests`）的引用集实测为
//   `netstandard, UnityEngine.CoreModule, nunit.framework, YANTF.Demo, UnityEngine.TestRunner, UnityEngine.PhysicsModule`
//   ——**没有 UnityEditor**。凡要读 .anim/.fbx 资产或建 Humanoid 载体，都必须用 UnityEditor API。
//   项目既有口径是「controller 与资产级断言落 Editor 侧 builder」（见 ActionLabSmokeTests 头注），
//   本条沿用该口径：真正的检查在 `DerivedClipBuilder.VerifyDerived()` / `ActionLabBuilder` 的资产读取里，
//   本文件只做**反射桥 + 断言**，把读数变成门禁可跑的绿/红。
//   ⚠️ 挂点组件本身（`ChairGrip`）是运行时代码 → 直接调，不走桥。
using System;
using System.Collections.Generic;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using YANTF.ActionLab;

public class ActionLabGripTests
{
    private readonly List<GameObject> _created = new List<GameObject>();

    [TearDown]
    public void TearDown()
    {
        foreach (var go in _created) if (go != null) UnityEngine.Object.DestroyImmediate(go);
        _created.Clear();
    }

    private GameObject Track(GameObject go) { _created.Add(go); return go; }

    // ---------------- 反射桥（只用于"取资产"这一步） ----------------

    private static Type FindType(string simpleName)
    {
        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            var t = asm.GetType("YANTF.EditorTools." + simpleName, false);
            if (t != null) return t;
        }
        return null;
    }

    private static object Call(string typeName, string method, params object[] args)
    {
        var t = FindType(typeName);
        Assert.IsNotNull(t, "找不到 YANTF.EditorTools." + typeName + "（Editor 侧程序集未加载？）");
        var m = t.GetMethod(method, BindingFlags.Public | BindingFlags.Static);
        Assert.IsNotNull(m, "找不到 " + typeName + "." + method);
        return m.Invoke(null, args);
    }

    /// <summary>从 `k=v k=v …` 单行读数里取一个键的值（读数是 Editor 侧给的，不引 JSON 依赖）。</summary>
    private static string Field(string report, string key)
    {
        foreach (var part in report.Split(' '))
        {
            int eq = part.IndexOf('=');
            if (eq > 0 && part.Substring(0, eq) == key) return part.Substring(eq + 1);
        }
        Assert.Fail("读数里没有字段 " + key + "：" + report);
        return null;
    }

    private static float Float(string report, string key) => float.Parse(Field(report, key),
        System.Globalization.CultureInfo.InvariantCulture);

    /// <summary>载体（X Bot）实例——挂点与"手到位帧"求值都要真骨架 + Humanoid Avatar。</summary>
    private GameObject MakeCarrier(Vector3 position)
    {
        var prefab = (GameObject)Call("ActionLabBuilder", "LoadCarrierForProbe");
        Assert.IsNotNull(prefab, "取不到载体预制（Assets/Mixamo/Characters/X Bot.fbx）");
        var go = (GameObject)UnityEngine.Object.Instantiate(prefab);
        go.name = "GripTestCarrier";
        go.transform.position = position;
        return Track(go);
    }

    private static AnimationClip LoadClip(string fbxPath, string preferredName)
        => (AnimationClip)Call("ActionLabBuilder", "LoadClipForProbe", fbxPath, preferredName);

    /// <summary>造一张带挂点的椅子：几何与 `ActionLabBuilder.AddChair` 的最小版一致，锚点/挂点表**取自 builder**（同一份定义）。</summary>
    private ChairGrip MakeChairWithGrip(Vector3 position, float yaw)
    {
        var root = Track(new GameObject("GripTestChair"));
        root.transform.position = position;
        root.transform.rotation = Quaternion.Euler(0f, yaw, 0f);

        var seat = GameObject.CreatePrimitive(PrimitiveType.Cube);
        seat.name = "Seat";
        seat.transform.SetParent(root.transform, false);
        seat.transform.localPosition = new Vector3(0f, 0.4199f, 0f);
        seat.transform.localScale = new Vector3(0.42f, 0.05f, 0.42f);

        var rb = root.AddComponent<Rigidbody>();
        rb.mass = 6f;
        rb.useGravity = false;    // 测试件不建腿，关重力（否则椅子先落地、锚点读数漂）
        rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;

        var chair = root.AddComponent<ChairSeat>();
        chair.anchorDistance = ChairSeat.DefaultAnchorDistance;
        chair.interactRadius = ChairSeat.DefaultInteractRadius;

        var grip = root.AddComponent<ChairGrip>();
        grip.anchors = (GripAnchor[])Call("ActionLabBuilder", "BuildGripAnchors");
        grip.poses = (GripPose[])Call("ActionLabBuilder", "DefaultGripPoses");
        grip.swayStiffness = 0f;   // 默认刚性（A）；要验阻尼（B）的测试自行设刚度
        return grip;
    }

    private Transform MakeHand(Vector3 position, Quaternion rotation)
    {
        var hand = Track(new GameObject("TestHandBone"));
        hand.transform.SetPositionAndRotation(position, rotation);
        return hand.transform;
    }

    private CharacterController MakeOccupant()
    {
        var go = Track(new GameObject("GripTestOccupant"));
        return go.AddComponent<CharacterController>();
    }

    // =====================================================================================
    /// <summary>非破坏（#150 验收标准 #2/#5）：磁盘上的派生件 == 现场重算（**现只覆盖 SitDown**）。</summary>
    [Test]
    public void DerivedAssets_MatchFreshDerivation()
    {
        var bad = (int)Call("DerivedClipBuilder", "VerifyDerived");
        Assert.AreEqual(0, bad,
            "派生件与现场重算不一致 " + bad + " 处（源 clip 导入设置被改？或派生件被手改？跑菜单重建）");
    }

    // =====================================================================================
    // ② 持椅挂点（#152）
    // =====================================================================================

    /// <summary>
    /// 锚点由椅子 `transform` **实时**求得（#152 验收标准 #2）：推动椅子后锚点位移 == 椅子位移。
    /// 对照：锚点必须**不等于**椅子原点——否则"实时求解"退化成"直接用椅子原点"。
    /// </summary>
    [Test]
    public void GripAnchor_FollowsChairTransform()
    {
        var grip = MakeChairWithGrip(new Vector3(1.5f, 0f, -1f), 40f);
        Vector3 before = grip.AnchorPosition("leg_front");
        Vector3 chairBefore = grip.transform.position;

        Assert.Greater(Vector3.Distance(before, chairBefore), 0.05f,
            "前提：可握锚点不是椅子原点（否则这条断言测的是原点跟随）");

        var delta = new Vector3(-0.8f, 0f, 0.35f);
        grip.transform.position += delta;

        Vector3 moved = grip.AnchorPosition("leg_front") - before;
        Assert.AreEqual(delta.x, moved.x, 1e-3f, "锚点 x 必须随椅子一起移动（实时求解）");
        Assert.AreEqual(delta.z, moved.z, 1e-3f, "锚点 z 必须随椅子一起移动");
        Assert.AreEqual(0f, moved.y, 1e-4f, "水平推动不应改变锚点高度");

        // 旋转后锚点仍跟着椅子几何走（锚点是椅子局部坐标，不是"椅子原点 + 固定偏移"）
        grip.transform.rotation = Quaternion.Euler(0f, 130f, 0f);
        Vector3 rotated = grip.AnchorPosition("leg_front");
        Assert.Greater(Vector3.Distance(rotated, grip.transform.position), 0.05f,
            "转向后锚点仍应在椅子几何上（不应塌回原点）");
        Assert.AreNotEqual(before.x, rotated.x, "转向后锚点世界位应改变（局部锚点随椅子旋转）");
    }

    /// <summary>
    /// 挂点"**三者同时**"（#152 验收标准 #1）：父子到 RightHand / 椅子 isKinematic / 忽略与角色 CC 的碰撞。
    /// </summary>
    [Test]
    public void GripAttach_IsThreeInOne()
    {
        var grip = MakeChairWithGrip(new Vector3(0.5f, 0f, 0.5f), 0f);
        var cc = MakeOccupant();
        var hand = MakeHand(new Vector3(1.1f, 1.0f, 0.4f), Quaternion.Euler(0f, 0f, 0f));
        var seatCollider = grip.GetComponentInChildren<Collider>();

        Assert.IsFalse(grip.IsHeld, "前提：初始未持握");
        Assert.IsTrue(grip.AttachTo(hand, GripState.Carry1H, cc), "挂点应成功：" + grip.LastAttachReport);

        Assert.AreEqual(hand, grip.transform.parent, "① 椅子必须挂到手上");
        Assert.IsTrue(grip.Seat.Body.isKinematic, "② 挂点期间椅子必须 isKinematic");
        Assert.IsTrue(Physics.GetIgnoreCollision(cc, seatCollider), "③ 挂点期间必须忽略与角色 CC 的碰撞");

        grip.Detach();
        Assert.IsFalse(grip.IsHeld);
        Assert.IsNull(grip.transform.parent, "解除后应还原父级");
        Assert.IsFalse(grip.Seat.Body.isKinematic, "解除后恢复刚体");
        Assert.IsFalse(Physics.GetIgnoreCollision(cc, seatCollider), "解除后恢复碰撞");
    }

    /// <summary>
    /// 逐状态挂点表（#152 验收标准 #3）：三组**基准朝向两两不同**；挂点后椅子在手骨局部坐标下的位姿
    /// **组内稳定**（手骨怎么动都不变），且锚点始终落在手骨原点上（自动对齐）。
    /// </summary>
    [Test]
    public void GripPoses_AreDistinctPerState_AndStableInHand()
    {
        var grip = MakeChairWithGrip(Vector3.zero, 0f);
        var cc = MakeOccupant();

        var states = new[] { GripState.Carry1H, GripState.Wield2H, GripState.DefendCarry1H };
        var baseRot = new Quaternion[states.Length];
        for (int i = 0; i < states.Length; i++)
        {
            Assert.IsTrue(grip.TryGetPose(states[i], out var pose), "挂点表应含 " + states[i]);
            baseRot[i] = Quaternion.Euler(pose.chairEulerInHand);
        }
        for (int i = 0; i < states.Length; i++)
            for (int j = i + 1; j < states.Length; j++)
                Assert.Greater(Quaternion.Angle(baseRot[i], baseRot[j]), 20f,
                    $"{states[i]} 与 {states[j]} 的基准朝向必须不同（组间不同）");

        var hand = MakeHand(new Vector3(0.9f, 1.2f, 0.3f), Quaternion.identity);
        foreach (var state in states)
        {
            Assert.IsTrue(grip.AttachTo(hand, state, cc), "挂点 " + state + " 应成功：" + grip.LastAttachReport);

            grip.GetLocalPoseInHand(hand, out Vector3 lp0, out Quaternion lr0);
            // 手骨动起来（平移 + 旋转），组内位姿必须稳定
            for (int k = 0; k < 4; k++)
            {
                hand.position += new Vector3(0.05f, -0.03f, 0.02f);
                hand.rotation = Quaternion.Euler(10f * k, 25f * k, -5f * k);
                grip.GetLocalPoseInHand(hand, out Vector3 lp, out Quaternion lr);
                Assert.Less(Vector3.Distance(lp, lp0), 1e-4f, state + " 组内椅子在手骨局部的位置必须稳定");
                Assert.Less(Quaternion.Angle(lr, lr0), 0.01f, state + " 组内椅子在手骨局部的朝向必须稳定");
                // 自动对齐：锚点应落在手骨原点上
                Assert.Less(Vector3.Distance(grip.AnchorFor(state), hand.position), 1e-3f,
                    state + " 挂点后锚点必须落在手骨原点上（自动对齐）");
            }
            grip.Detach();
        }
    }

    /// <summary>
    /// 「手到位帧」**由读数求出**（#152 验收标准 #4）：切换帧 = 手骨↔锚点距离曲线的最低点，且读数留痕。
    /// 非空判据：把椅子挪近后，曲线最低点距离必须显著变小（说明读数真的是量出来的，不是常量）。
    /// </summary>
    [Test]
    public void HandArrival_ComesFromDistanceCurveMinimum()
    {
        var carrier = MakeCarrier(new Vector3(0f, 0f, 0f));
        var animator = carrier.GetComponent<Animator>();
        Assert.IsNotNull(animator, "载体应有 Animator");
        Assert.IsNotNull(animator.avatar, "载体应有 Humanoid Avatar");
        var clip = LoadClip("Assets/Animations/Mixamo/Chairhold/Carry1H.fbx", "Carry1H");
        Assert.IsNotNull(clip, "取不到 Carry1H 源 clip");

        var far = MakeChairWithGrip(new Vector3(0f, 0f, 3.2f), 0f);
        var readingFar = far.MeasureHandArrival(animator, clip, GripState.Carry1H);
        Assert.Greater(readingFar.samples, 2, "应有距离曲线读数");
        Assert.AreEqual(readingFar.samples, far.LastArrival.samples, "读数必须留痕（LastArrival）");

        // 最低点是**这条曲线**的真实最低点
        float min = float.MaxValue;
        foreach (var d in readingFar.distancesMm) min = Mathf.Min(min, d);
        Assert.AreEqual(min, readingFar.DistanceMm, 1e-3f, "切换帧的距离必须等于曲线最低点");
        int argmin = Mathf.RoundToInt(readingFar.NormalizedTime * (readingFar.samples - 1));
        Assert.AreEqual(min, readingFar.distancesMm[argmin], 1e-3f, "NormalizedTime 必须指向 argmin");

        // 非空判据：把椅子挪近 → 最低点距离显著变小
        var near = MakeChairWithGrip(new Vector3(0f, 0f, 1.1f), 0f);
        var readingNear = near.MeasureHandArrival(animator, clip, GripState.Carry1H);
        Assert.Less(readingNear.DistanceMm, readingFar.DistanceMm - 100f,
            $"椅子挪近 2.1 m 后最低点距离应显著变小（远 {readingFar.DistanceMm:F1} mm → 近 {readingNear.DistanceMm:F1} mm）");

        // 切换时刻随读数一起留痕
        Assert.IsTrue(near.AttachAtHandArrival(animator, clip, GripState.Carry1H, null),
            "按读数挂点应成功：" + near.LastAttachReport);
        StringAssert.Contains("切换帧", near.LastAttachReport, "挂点报告必须记录切换时刻（留痕可读）");
        Assert.IsTrue(near.IsHeld);
    }

    /// <summary>
    /// 阻尼摆动（#152 验收标准 #5）：介入判据明写（残差进阈值 → 弹簧归零 + **精确定位**），
    /// 且有收敛耗时读数。刚性挂点（A）是它的退化情形。
    /// </summary>
    [Test]
    public void GripSway_SettlesToExactBasePose()
    {
        var grip = MakeChairWithGrip(new Vector3(-0.6f, 0f, -0.6f), 15f);
        grip.swayStiffness = 120f;
        grip.swayDamping = 18f;
        var hand = MakeHand(new Vector3(0.8f, 1.1f, 0.2f), Quaternion.Euler(0f, 20f, 0f));

        Assert.IsTrue(grip.AttachTo(hand, GripState.Carry1H, null), "挂点应成功：" + grip.LastAttachReport);
        // 非刚性：挂点当帧椅子仍在原处 → 残差很大（重量感的来源）
        Assert.Greater(Vector3.Distance(grip.transform.position, hand.position), 0.5f,
            "前提：阻尼挂点当帧椅子尚未到位（残差非零）");

        Assert.IsTrue(grip.StepSwayToSettle(hand, 1f / 60f, 3f, out float seconds),
            $"阻尼应在 3 s 内收敛（实际 {grip.SwayPositionResidual:F4} m / {grip.SwayAngleResidual:F3}°）");
        Assert.Greater(seconds, 0f, "收敛耗时应是正数（读数留痕）");
        Assert.AreEqual(seconds, grip.LastSwaySettleSeconds, 1e-6f, "收敛耗时必须留痕");
        Assert.LessOrEqual(grip.SwayPositionResidual, grip.settleDistance + 1e-6f, "收敛后残差必须为 0（精确定位）");

        // 收敛后 == 基准位姿（不是"接近"）
        grip.TrySolveHandPose(hand, GripState.Carry1H, out Vector3 wantPos, out Quaternion wantRot);
        Assert.Less(Vector3.Distance(grip.transform.position, wantPos), 1e-4f, "收敛后位置应精确等于基准");
        Assert.Less(Quaternion.Angle(grip.transform.rotation, wantRot), 0.02f, "收敛后朝向应精确等于基准");

        // 刚性退化：刚度 0 → 直接到位、耗时为 0
        grip.Detach();
        grip.swayStiffness = 0f;
        Assert.IsTrue(grip.AttachTo(hand, GripState.Carry1H, null));
        Assert.Less(Vector3.Distance(grip.transform.position, wantPos), 1e-4f, "刚性挂点（A）必须直接精确到位");
        Assert.AreEqual(0f, grip.LastSwaySettleSeconds, 1e-6f, "刚性挂点耗时应为 0");
    }

    /// <summary>
    /// 两种占用**不得互抢**（#152 接入位置）：椅子已被就座占用时拒绝挂点；解除就座后可以挂。
    /// </summary>
    [Test]
    public void Grip_RefusesWhenSeated_AndSeatLockIsShared()
    {
        var grip = MakeChairWithGrip(new Vector3(1f, 0f, 1f), 0f);
        var hand = MakeHand(new Vector3(1.4f, 1.1f, 1.2f), Quaternion.identity);

        grip.Seat.Occupy(null);                    // 就座占用（§四·丁 已闭合的占用锁）
        Assert.IsFalse(grip.AttachTo(hand, GripState.Carry1H, null), "椅子被就座占用时不得挂点");
        Assert.IsFalse(grip.IsHeld, "被拒后不得进入持握态");
        StringAssert.Contains("就座占用", grip.LastAttachReport, "拒绝理由必须留痕可读");

        grip.Seat.Release(null);
        Assert.IsTrue(grip.AttachTo(hand, GripState.Carry1H, null), "解除就座后应可挂点");
        Assert.IsTrue(grip.Seat.Body.isKinematic, "挂点期间椅子同样锁成 kinematic（两种占用共用同一把锁的语义）");
    }
}
