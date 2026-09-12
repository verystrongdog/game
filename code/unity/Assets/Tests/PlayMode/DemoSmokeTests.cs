// PlayMode 冒烟测试 — 验证引导/结算/回合流程（Grilling #122）
// 精神攻击路径确定性断言（2 SAN − 忍耐被动 1 = 1.0 → SAN 59 / HP 14.5，与 CalibrationConfig.Default 镜像一致）。
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using YANTF.Demo;

public class DemoSmokeTests
{
    [UnityTest]
    public IEnumerator Demo_BootsAndMentalRoundResolvesDeterministically()
    {
        var go = new GameObject("TestBoot");
        var boot = go.AddComponent<DemoBootstrapper>(); // Awake → BuildAll()
        yield return null;
        yield return null;

        Assert.IsNotNull(boot.PlayerActor, "玩家实体应存在");
        Assert.IsNotNull(boot.EnemyActor, "陪练实体应存在");
        Assert.AreEqual(50f, boot.PlayerActor.Hp, 0.001f);
        Assert.AreEqual(80f, boot.PlayerActor.San, 0.001f);
        Assert.AreEqual(15f, boot.EnemyActor.Hp, 0.001f);
        Assert.AreEqual(60f, boot.EnemyActor.San, 0.001f);

        // 默认距离 5.39m ∈ (2, 6]：精攻可命中；精神攻击永远命中
        Assert.IsTrue(boot.Driver.QueueAction(DemoActionKind.MentalAttack), "应能排队精神攻击");
        boot.Driver.ExecuteRound();
        Assert.AreEqual(59f, boot.EnemyActor.San, 0.001f, "精攻 2−忍耐1=1.0 SAN");
        Assert.AreEqual(14.5f, boot.EnemyActor.Hp, 0.001f, "HP 成分 = SAN×0.5 向下取至 0.1");

        Object.Destroy(go);
    }

    [UnityTest]
    public IEnumerator Demo_DefendRoundAdvancesRound()
    {
        var go = new GameObject("TestBoot");
        var boot = go.AddComponent<DemoBootstrapper>(); // Awake → BuildAll()
        yield return null;
        yield return null;

        boot.Driver.player.transform.position = boot.Driver.enemy.transform.position + new Vector3(1f, 0f, 0f);
        Assert.IsTrue(boot.Driver.QueueAction(DemoActionKind.Defend), "应能排队防御（冷却 0）");
        boot.Driver.ExecuteRound();
        Assert.AreEqual(2, boot.Driver.RoundNumber, "回合应推进到 2");
        Assert.IsFalse(boot.Driver.player.Defending, "下回合自己行动窗口开始时防御应到期（§7.1）");
        Assert.AreEqual(0, boot.Driver.player.DefenseCooldown, "防御 CD=1 已在下个行动窗口递减 → 暴露一轮后可再防御");

        Object.Destroy(go);
    }
}
