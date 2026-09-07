// PlayMode 冒烟测试 — Walker 移动实验沙盘（几何体人体走/跑/跳验证）
// 验证：① BuildBody 骨架完整 ② 重力落地（CC 贴地） ③ 走/跑速度差 ④ 跳跃离地后回落。
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using YANTF.WalkerLab;

public class WalkerLabSmokeTests
{
    private const float Tolerance = 0.001f;

    /// <summary>建一个 y=0 的大地面（100×100m，容纳走+跑总位移）+ 空 Walker（未 BuildBody）。</summary>
    private static WalkerController SpawnWalker(float y)
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "TestGround";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(10f, 1f, 10f); // Plane 10m 单位 → 100×100m

        var go = new GameObject("TestWalker");
        go.transform.position = new Vector3(0f, y, 0f);
        return go.AddComponent<WalkerController>(); // RequireComponent 自动补 CharacterController
    }

    [UnityTest]
    public IEnumerator Walker_BuildBody_CreatesFullSkeleton()
    {
        var walker = SpawnWalker(0f);
        walker.BuildBody(new Color(0.35f, 0.65f, 1f));
        yield return null;

        // 根 + hips(1) + 肢体(armR/armL/legR/legL 各含 mesh 子节点) 均在 hips 层级下
        var hips = walker.transform.Find("hips");
        Assert.IsNotNull(hips, "应存在 hips 髋部节点");
        Assert.IsNotNull(hips.Find("torso"), "应存在 torso");
        Assert.IsNotNull(hips.Find("head"), "应存在 head");
        foreach (var limb in new[] { "armR", "armL", "legR", "legL" })
        {
            var j = hips.Find(limb);
            Assert.IsNotNull(j, $"应存在 {limb} 关节");
            Assert.IsNotNull(j.Find(limb + "_mesh"), $"{limb} 下应有几何体 mesh");
        }

        var cc = walker.GetComponent<CharacterController>();
        Assert.IsNotNull(cc, "应有 CharacterController");
        Assert.AreEqual(1.85f, cc.height, Tolerance, "CC 高度应对齐 1.8m 人体");
        Assert.IsTrue(Mathf.Abs(cc.center.y - 0.92f) < Tolerance, "CC 中心应上抬使底部≈地面");

        Object.Destroy(walker.gameObject);
        Object.Destroy(GameObject.Find("TestGround"));
    }

    [UnityTest]
    public IEnumerator Walker_FallsToGround_ThenWalkRunSpeedDiffers()
    {
        var walker = SpawnWalker(2.5f);
        yield return null;

        // 重力落地（CC 底≈transform.y，地面 y=0 → 落定 y≈0）
        float t0 = Time.time;
        while (!walker.IsGrounded && Time.time - t0 < 2f) yield return null;
        Assert.IsTrue(walker.IsGrounded, "应在 2s 内落到地面");
        Assert.IsTrue(Mathf.Abs(walker.transform.position.y) < 0.1f, $"落地 y 应≈0，实际 {walker.transform.position.y:F3}");

        // 走 0.8s：位移 ≈ walkSpeed × 0.8
        Vector3 startWalk = walker.transform.position;
        t0 = Time.time;
        while (Time.time - t0 < 0.8f)
        {
            walker.SetMoveInput(Vector3.forward, walker.walkSpeed, false, false);
            yield return null;
        }
        float walkDist = Vector3.Distance(startWalk, walker.transform.position);
        Assert.IsTrue(walkDist > walker.walkSpeed * 0.6f, $"行走位移应≈{walker.walkSpeed:F1}m/s×0.8s，实际 {walkDist:F2}m");
        Assert.IsFalse(walker.IsRunning, "行走时 IsRunning 应为 false");

        // 跑 0.8s：位移 > 行走（速度比 runSpeed/walkSpeed=2 → 距离应明显更大）
        Vector3 startRun = walker.transform.position;
        t0 = Time.time;
        while (Time.time - t0 < 0.8f)
        {
            walker.SetMoveInput(Vector3.forward, walker.runSpeed, true, false);
            yield return null;
        }
        float runDist = Vector3.Distance(startRun, walker.transform.position);
        Assert.IsTrue(runDist > walkDist * 1.3f, $"奔跑位移应显著大于行走（walk {walkDist:F2} / run {runDist:F2}）");
        Assert.IsTrue(walker.IsRunning, "奔跑时 IsRunning 应为 true");

        Object.Destroy(walker.gameObject);
        Object.Destroy(GameObject.Find("TestGround"));
    }

    [UnityTest]
    public IEnumerator Walker_Jump_RisesThenFallsBack()
    {
        var walker = SpawnWalker(0f);
        yield return null;

        float t0 = Time.time;
        while (!walker.IsGrounded && Time.time - t0 < 2f) yield return null;
        Assert.IsTrue(walker.IsGrounded, "起跳前应先落地");

        float startY = walker.transform.position.y;
        // 触发一次跳跃（jump=true 仅队列一帧，之后传 false）
        walker.SetMoveInput(Vector3.zero, 0f, false, true);
        yield return null;
        walker.SetMoveInput(Vector3.zero, 0f, false, false);

        float maxY = startY;
        t0 = Time.time;
        while (Time.time - t0 < 2.5f)
        {
            maxY = Mathf.Max(maxY, walker.transform.position.y);
            if (walker.IsGrounded && Time.time - t0 > 0.5f) break; // 上升后已回落
            yield return null;
        }
        Assert.IsTrue(maxY - startY > 0.5f, $"跳跃峰值应>0.5m，实际 {(maxY - startY):F2}m");
        Assert.IsTrue(walker.IsGrounded, "跳跃后应回落接地");

        Object.Destroy(walker.gameObject);
        Object.Destroy(GameObject.Find("TestGround"));
    }
}
