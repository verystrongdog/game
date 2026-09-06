// 演示战斗实体 — 运行时状态容器（Grilling #122）
// HP/SAN 初始值默认取 CalibrationConfig.Default（玩家 50/80，杂兵 15/60）。
// 结算值一位小数（引擎口径：Round1 半进位 / Floor1 向下取至 0.1）。
using System;
using UnityEngine;

namespace YANTF.Demo
{
    public sealed class DemoActor : MonoBehaviour
    {
        [Header("演示初始基线（引擎桥接后由结算层读写）")]
        public float hpMax = 50f;
        public float sanMax = 80f;
        public string displayName = "演示者";

        public float Hp { get; private set; }
        public float San { get; private set; }

        /// <summary>防御持续态：从选择防御的行动窗口到下次自己行动窗口（回合战斗流程 §7.1）。</summary>
        public bool Defending { get; private set; }

        /// <summary>防御冷却，行动窗口口径递减（回合战斗流程 §9.1）。</summary>
        public int DefenseCooldown { get; private set; }

        public bool Down => Hp <= 0f;

        private CharacterVisual _visual;

        /// <summary>懒加载：视觉子对象可能在 Awake 之后才被 Bootstrapper 建立。</summary>
        public CharacterVisual Visual
        {
            get
            {
                if (_visual == null) _visual = GetComponentInChildren<CharacterVisual>();
                return _visual;
            }
        }

        public event Action<DemoActor, float, float> Changed;      // (self, hp, san)
        public event Action<DemoActor, string> Logged;

        public void Init(float hp, float san, string name)
        {
            hpMax = hp;
            sanMax = san;
            displayName = name;
            Hp = hp;
            San = san;
        }

        public void ResetState()
        {
            Hp = hpMax;
            San = sanMax;
            Defending = false;
            DefenseCooldown = 0;
            if (Visual != null) { Visual.PlayDefend(false); Visual.PlayIdle(); }
            transform.rotation = Quaternion.identity;
            Changed?.Invoke(this, Hp, San);
        }

        public void ApplyPhysicalDamage(float dmg)
        {
            Hp = Mathf.Max(0f, Round1(Hp - dmg));
            Changed?.Invoke(this, Hp, San);
        }

        /// <summary>精神伤害：SAN 主伤害 + HP 成分（= SAN 伤害 × 0.5 向下取至 0.1，核心机制 §4.3）。</summary>
        public void ApplySanDamage(float sanDmg, float hpDmg)
        {
            San = Mathf.Max(0f, Round1(San - sanDmg));
            Hp = Mathf.Max(0f, Round1(Hp - hpDmg));
            Changed?.Invoke(this, Hp, San);
        }

        public bool CanDefend => DefenseCooldown <= 0 && !Defending;

        public void BeginDefend()
        {
            if (DefenseCooldown > 0)
            {
                Logged?.Invoke(this, $"防御冷却中（{DefenseCooldown} 行动窗口）");
                return;
            }
            Defending = true;
            Visual?.PlayDefend(true);
            Logged?.Invoke(this, $"{displayName} 进入防御（物理伤害 -50%，M1 占用）");
        }

        public void EndDefend()
        {
            if (!Defending) return;
            Defending = false;
            Visual?.PlayDefend(false);
        }

        /// <summary>自己行动窗口开始时推进：防御到期 + 冷却递减（回合战斗流程 §9）。</summary>
        public void TickOnOwnWindow()
        {
            EndDefend();                       // 防御覆盖到"下次自己行动"为止
            if (DefenseCooldown > 0) DefenseCooldown--;
        }

        public void OnDefendUsed()
        {
            DefenseCooldown = 1;               // 防御 CD=1（基础行动设计 §一）
        }

        public void PlayActionFeedback(DemoActionKind kind)
        {
            if (Visual == null) return;
            switch (kind)
            {
                case DemoActionKind.PhysicalAttack: Visual.PlayPhysicalAttack(); break;
                case DemoActionKind.MentalAttack: Visual.PlayMentalAttack(); break;
            }
        }

        public void PlayHitReaction() => Visual?.PlayHitReaction();

        public void PlayDown()
        {
            Visual?.PlayDown();
            Logged?.Invoke(this, $"{displayName} 被击倒（HP=0）");
        }

        private static float Round1(float x) => Mathf.Round(x * 10f) / 10f;
    }
}
