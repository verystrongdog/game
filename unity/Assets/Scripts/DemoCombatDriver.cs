// 轻量手动回合沙盘驱动（Grilling #122 Q2）
// 每回合：玩家选 M1 动作（物攻/防御）+ Broca 动作（精攻），移动 WASD 自由走位（非战棋网格），
// [执行回合]（或 Space）→ 结算：玩家 M1 → 玩家 Broca → 陪练 AI → 下回合。
// 冷却/防御按行动窗口口径（回合战斗流程 §9）；不触碰引擎 TurnManager 五阶段。
// ⚠️ 简化注记（演示口径，非正典）：M1→Broca 固定顺序（正典由玩家自定顺序）；
// 物攻射程 2.0m / 精攻 6.0m 为演示常量；陪练 AI 为简单随机（非 NPC Affordance Competition）。
using System;
using UnityEngine;

namespace YANTF.Demo
{
    public sealed class DemoCombatDriver : MonoBehaviour
    {
        [Header("场景引用（Bootstrapper 注入）")]
        public DemoActor player;
        public DemoActor enemy;
        public IDemoSolver solver = new WhiteboxSolver();   // ⚠️ 桥接定案后换 EngineSolver

        public DemoRoundPhase Phase { get; private set; } = DemoRoundPhase.PlayerInput;

        public DemoActionKind M1Selection { get; private set; } = DemoActionKind.None;     // 物攻/防御
        public DemoActionKind BrocaSelection { get; private set; } = DemoActionKind.None;  // 精攻

        public int RoundNumber { get; private set; } = 1;

        public event Action StatsChanged;                 // HUD 刷新
        public event Action<string> Logged;               // 战斗日志

        private const float MeleeRange = 2.0f;
        private const float MentalRange = 6.0f;
        private float _moveSpeed = 3.2f;
        private Vector3 _moveInput;

        private void Update()
        {
            HandleMovementInput();
            if (Phase != DemoRoundPhase.PlayerInput) return;
            if (Input.GetKeyDown(KeyCode.Alpha1)) QueueAction(DemoActionKind.PhysicalAttack);
            if (Input.GetKeyDown(KeyCode.Alpha2)) QueueAction(DemoActionKind.Defend);
            if (Input.GetKeyDown(KeyCode.Alpha3)) QueueAction(DemoActionKind.MentalAttack);
            if (Input.GetKeyDown(KeyCode.Space)) ExecuteRound();
            if (Input.GetKeyDown(KeyCode.R)) ResetFight();
        }

        // ---- 玩家输入 ----
        private void HandleMovementInput()
        {
            _moveInput = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical")).normalized;
            if (player == null || player.Down) return;
            player.transform.position += _moveInput * _moveSpeed * Time.deltaTime;
            if (_moveInput.sqrMagnitude > 0.01f)
            {
                player.transform.rotation = Quaternion.LookRotation(new Vector3(_moveInput.x, 0f, _moveInput.z));
                player.Visual?.PlayWalk(1f);
            }
            else
            {
                player.Visual?.PlayIdle();
            }
        }

        /// <summary>排队一个基础行动（M1 通道：物攻/防御互斥；Broca 通道：精攻）。</summary>
        public bool QueueAction(DemoActionKind kind)
        {
            if (Phase != DemoRoundPhase.PlayerInput || player.Down || enemy.Down) return false;
            switch (kind)
            {
                case DemoActionKind.PhysicalAttack:
                    if (M1Selection == DemoActionKind.Defend) return false;
                    M1Selection = DemoActionKind.PhysicalAttack;
                    Log($"选定 M1: 物理攻击");
                    return true;
                case DemoActionKind.Defend:
                    if (!player.CanDefend) { Log("防御冷却中"); return false; }
                    if (M1Selection == DemoActionKind.PhysicalAttack) return false;
                    M1Selection = DemoActionKind.Defend;
                    Log("选定 M1: 防御");
                    return true;
                case DemoActionKind.MentalAttack:
                    BrocaSelection = DemoActionKind.MentalAttack;
                    Log("选定 Broca: 精神攻击");
                    return true;
                default:
                    return false;
            }
        }

        public void ClearSelection()
        {
            M1Selection = DemoActionKind.None;
            BrocaSelection = DemoActionKind.None;
            StatsChanged?.Invoke();
        }

        public void ExecuteRound()
        {
            if (Phase != DemoRoundPhase.PlayerInput) return;
            if (player.Down || enemy.Down) { ResetFight(); return; }
            Phase = DemoRoundPhase.Execute;
            StatsChanged?.Invoke();

            // 1) 玩家 M1 动作
            if (M1Selection == DemoActionKind.PhysicalAttack) DoPlayerAttack(DemoActionKind.PhysicalAttack);
            else if (M1Selection == DemoActionKind.Defend) { player.BeginDefend(); player.OnDefendUsed(); }

            // 2) 玩家 Broca 动作
            if (BrocaSelection == DemoActionKind.MentalAttack) DoPlayerAttack(DemoActionKind.MentalAttack);

            if (enemy.Down) { Log($"陪练被击倒 — 演示胜利（第 {RoundNumber} 回合）"); ClearSelection(); Phase = DemoRoundPhase.PlayerInput; return; }

            // 3) 陪练 AI 回合（简单随机：60% 物攻 / 40% 精攻）
            DoEnemyTurn();

            // 4) 回合收束：清选择、推进窗口口径状态（下回合自己的行动窗口开始时防御到期/CD 递减）
            ClearSelection();
            player.TickOnOwnWindow();
            enemy.TickOnOwnWindow();
            RoundNumber++;
            Phase = DemoRoundPhase.PlayerInput;
            Log($"—— 第 {RoundNumber} 回合 ——");
            StatsChanged?.Invoke();
        }

        private void DoPlayerAttack(DemoActionKind kind)
        {
            if (player.Down) return;
            float dist = Vector3.Distance(player.transform.position, enemy.transform.position);
            float need = kind == DemoActionKind.PhysicalAttack ? MeleeRange : MentalRange;
            if (dist > need)
            {
                Log($"距离 {dist:F1}m 超出{kind}射程（{need:F1}m）");
                player.PlayActionFeedback(kind);
                return;
            }
            player.transform.rotation = Quaternion.LookRotation(enemy.transform.position - player.transform.position);
            var result = solver.Resolve(new DemoActionRequest { Kind = kind, Source = player, Target = enemy });
            ApplyResult(result, player, enemy);
        }

        private void DoEnemyTurn()
        {
            if (enemy.Down || player.Down) return;
            enemy.transform.rotation = Quaternion.LookRotation(player.transform.position - enemy.transform.position);
            float dist = Vector3.Distance(enemy.transform.position, player.transform.position);
            bool useMental = dist > MeleeRange || UnityEngine.Random.value < 0.4f;
            var kind = useMental ? DemoActionKind.MentalAttack : DemoActionKind.PhysicalAttack;
            var result = solver.Resolve(new DemoActionRequest { Kind = kind, Source = enemy, Target = player });
            ApplyResult(result, enemy, player);
        }

        private void ApplyResult(DemoActionResult r, DemoActor source, DemoActor target)
        {
            switch (r.Kind)
            {
                case DemoActionKind.PhysicalAttack:
                    if (!r.Hit) { Log($"{source.displayName} 物理攻击未命中"); source.PlayActionFeedback(DemoActionKind.PhysicalAttack); return; }
                    target.ApplyPhysicalDamage(r.HpDamage);
                    target.PlayHitReaction();
                    Log($"{source.displayName} 物理攻击命中 {target.displayName} — HP −{r.HpDamage:F1}");
                    break;
                case DemoActionKind.MentalAttack:
                    target.ApplySanDamage(r.SanDamage, r.HpDamage);
                    target.PlayHitReaction();
                    Log($"{source.displayName} 精神攻击命中 {target.displayName} — SAN −{r.SanDamage:F1}, HP −{r.HpDamage:F1}");
                    break;
            }
            StatsChanged?.Invoke();
            if (target.Down) target.PlayDown();
        }

        public void ResetFight()
        {
            player.ResetState();
            enemy.ResetState();
            RoundNumber = 1;
            ClearSelection();
            Phase = DemoRoundPhase.PlayerInput;
            Log("—— 重新开始 ——");
            StatsChanged?.Invoke();
        }

        private void Log(string s) => Logged?.Invoke(s);
    }
}
