// 动作播放驱动 — 契约 A（动作库规格.md §四）：纯状态集 + 运行时 CrossFade
// - 状态名 = 词表 id = 代码字符串（三面对一，由 ActionLabBuilder 按 ActionCatalog 构造成立）
// - 衔接优先级：Down(4) > HitReaction(3) > 一次性动作(2) > Defend(1) > locomotion(0)
// - 一次性动作播完（clip.length + 0.05s）→ 回退 locomotion 目标（规格 §七 计时口径）
// - 空中 Jump → 落地：显式补发一次回切（Jump 这次切态不进 _locomotionTarget 的账，
//   否则落地目标与起跳前同档时守卫判"无变化"→ 状态机停在 Jump，身体平移而腿不动）
// - Defend 循环持续态：TickLocomotion 收到移动意图(speed>0) 即退出；或更高优先级动作打断
// - Down 终态停留末帧：不自动回退，须 Reset()（演示 R 键）
// - 位移全走 CharacterController（本组件不移动物体），applyRootMotion=false 由场景侧保证
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 契约 A 的运行时驱动。只负责"状态选择 + CrossFade + 优先级/计时"，不碰物理。
    /// 物理（CharacterController 移动/跳跃）由 ActionLabDriver 负责，每帧把落地/速度喂进来。
    /// </summary>
    public sealed class ActionPlayer : MonoBehaviour
    {
        /// <summary>一次性动作回退尾时 s（规格 §七：clip.length + 0.05）。</summary>
        public const float OneShotTailSeconds = 0.05f;

        [Tooltip("Animator（builder/场景注入；缺省时从自身获取）")]
        public Animator animator;

        // ---- 只读状态（HUD/测试）----
        public string CurrentActionId { get; private set; }
        public string CurrentActionDisplay => CurrentActionId != null ? ActionCatalog.Get(CurrentActionId).DisplayName : "—";
        public bool IsLocked { get; private set; }          // 一次性动作播放期间（含 Down 终态）锁移动切态
        public bool IsAirborne { get; private set; }
        public float HorizontalSpeed01 { get; private set; } // 0..1（0=静止, 1=满速跑）

        /// <summary>最近一次切态请求的目标态名（决策层留痕：无 Animator 时同样记录 → 断言与排障面）。</summary>
        public string LastRequestedState { get; private set; }
        /// <summary>切态请求累计次数（守卫应只在"档位变化/落地/退出防御"边沿请求，不逐帧刷）。</summary>
        public int StateRequestCount { get; private set; }

        private ActionEntry _activeEntry;   // 当前动作（一次性/Defend/Down）；null = locomotion 控制
        private bool _returnFromJumpPending; // 空中发过 Jump（缓存 _locomotionTarget 未跟账）→ 落地必须补发一次回切
        private float _activeTime;
        private float _plannedDuration;     // 一次性动作：clip.length + 0.05（未知时按 1.05 兜底）
        private string _locomotionTarget = ActionIds.Idle;
        private bool _jumpFired;
        private float _fallbackDuration = 1.05f;

        private void Awake()
        {
            if (animator == null) animator = GetComponent<Animator>();
            if (animator == null) Debug.LogWarning("[ActionPlayer] 无 Animator：仅状态逻辑生效，不播动画", this);
        }

        /// <summary>
        /// 每帧喂 locomotion 意图（由驱动/测试调用）。
        /// grounded=false → 空中：触发一次 Jump 状态，直到落地前不响应切态；
        /// grounded=true → 按 speed01 选 Idle/Walk/Run；若 Defend 持续中且 speed01=0 保持防御。
        /// </summary>
        public void TickLocomotion(bool grounded, float speed01)
        {
            IsAirborne = !grounded;
            HorizontalSpeed01 = speed01;
            // 注意：无 Animator/controller 时**不提前 return**——状态选择是决策层，须始终成立并留痕
            // （CrossFade 的落地由 CrossFadeState 自行判空）。否则整段逻辑在无资产时不可测（见 ActionLabLocomotionTests）。

            if (!grounded)
            {
                // 空中：Jump 一次性（KiWalkerLab 口径：离地触发一次，播完定格末帧，落地切回）
                if (IsLocked) return; // 动作播放期间不切 Jump（地面动作被打断→跌落仍播原动作，落地再回）
                if (!_jumpFired)
                {
                    _jumpFired = true;
                    _returnFromJumpPending = true; // Jump 不进 _locomotionTarget 的账 → 落地须补发回切
                    CrossFadeState(ActionIds.Jump, ActionCatalog.Get(ActionIds.Jump).Fade);
                }
                return; // 空中不再改写状态
            }

            _jumpFired = false;

            if (IsLocked) return; // 一次性动作/终态播放期间锁移动切态（契约 A）

            string target;
            if (_activeEntry != null && _activeEntry.Id == ActionIds.Defend && speed01 <= 0.001f)
            {
                return; // Defend 持续态：原地保持
            }

            // locomotion 目标（Defend 会被移动意图退出）
            _activeEntry = null;
            CurrentActionId = null; // Defend 退出 / 常规 locomotion 路径清动作显示
            target = speed01 < 0.05f ? ActionIds.Idle
                   : speed01 < 0.55f ? ActionIds.Walk
                   : ActionIds.Run;

            // 守卫：档位变化 || 刚从空中落地（补发）|| 当前停在 Defend（移动意图退出防御）
            if (target != _locomotionTarget || _returnFromJumpPending || IsCurrentState(ActionIds.Defend))
            {
                _locomotionTarget = target;
                _returnFromJumpPending = false;
                CrossFadeState(target, ActionCatalog.Get(target).Fade);
            }
        }

        /// <summary>
        /// 请求播放动作（L1 一次性/Defend/Down）。成功返回 true。
        /// 优先级规则（严格大于才打断）：Down(4) > HitReaction(3) > 一次性(2) > Defend(1) > locomotion(0)。
        /// L2 词条：登记未接线 → LogWarning + 返回 false。
        /// </summary>
        public bool Play(string id)
        {
            if (!ActionCatalog.TryGet(id, out var entry))
            {
                Debug.LogWarning("[ActionPlayer] 词表外动作: " + id + "（新增须走扩展协议）", this);
                return false;
            }
            if (entry.Level == 2)
            {
                Debug.LogWarning("[ActionPlayer] L2 登记未接线: " + id + "（" + entry.DisplayName + "；消费端就绪后走 L2→L1）", this);
                return false;
            }
            if (entry.Category == ActionCategory.Locomotion && entry.Id != ActionIds.Jump)
            {
                Debug.LogWarning("[ActionPlayer] locomotion 词条走 TickLocomotion 通道: " + id, this);
                return false;
            }
            if (entry.Id == ActionIds.Jump)
            {
                Debug.LogWarning("[ActionPlayer] Jump 由 locomotion 空中态触发，不走 Play()", this);
                return false;
            }
            if (!groundedOk()) return false;

            int current = _activeEntry != null ? _activeEntry.Priority : 0; // locomotion/无动作 = 0
            if (entry.Priority <= current) return false; // 严格大于才打断（Down 终态不可被同级打断）

            StartAction(entry);
            return true;
        }

        /// <summary>演示/场景重置：清除动作锁，回 Idle（Down 终态后使用）。</summary>
        public void ResetToIdle()
        {
            _activeEntry = null;
            IsLocked = false;
            _activeTime = 0f;
            _returnFromJumpPending = false; // 显式重置：不留待补发的落地回切
            _locomotionTarget = ActionIds.Idle;
            if (animator != null && animator.runtimeAnimatorController != null)
            {
                CrossFadeState(ActionIds.Idle, ActionCatalog.Get(ActionIds.Idle).Fade);
            }
        }

        private bool groundedOk() => !IsAirborne || _activeEntry != null && !_activeEntry.Loop;

        private void StartAction(ActionEntry entry)
        {
            _activeEntry = entry;
            _activeTime = 0f;
            CurrentActionId = entry.Id;
            IsLocked = !entry.Loop; // 一次性动作（含 Down 终态）锁移动切态；Defend 循环不锁

            if (entry.Loop)
            {
                _plannedDuration = 0f;
            }
            else
            {
                float clipLen = ReadTargetClipLength();
                _plannedDuration = clipLen > 0f ? clipLen + OneShotTailSeconds : _fallbackDuration;
            }

            if (animator != null && animator.runtimeAnimatorController != null)
            {
                CrossFadeState(entry.Id, entry.Fade);
            }
            else
            {
                Debug.LogWarning("[ActionPlayer] 无 controller：动作状态已记录但不播动画: " + entry.Id, this);
            }
        }

        private void Update()
        {
            if (_activeEntry == null) return;

            if (!_activeEntry.Loop && IsLocked)
            {
                _activeTime += Time.deltaTime;
                if (_activeTime >= _plannedDuration)
                {
                    if (_activeEntry.Id == ActionIds.Down)
                    {
                        // Down 终态停留末帧（规格 §二）：不自动回退，等待 Reset（演示 R 键）
                        IsLocked = true;
                        return;
                    }
                    FinishOneShot();
                }
            }
        }

        private void FinishOneShot()
        {
            _activeEntry = null;
            IsLocked = false;
            _activeTime = 0f;
            CurrentActionId = null;
            if (animator != null && animator.runtimeAnimatorController != null)
            {
                CrossFadeState(_locomotionTarget, ActionCatalog.Get(_locomotionTarget).Fade);
            }
        }

        /// <summary>一次性动作目标态 clip 长度（CrossFade 目标态在 GetNext 中可读；兜底 0 → 用 fallback）。</summary>
        private float ReadTargetClipLength()
        {
            if (animator == null || animator.runtimeAnimatorController == null) return 0f;
            var next = animator.GetNextAnimatorStateInfo(0);
            if (next.length > 0f) return next.length;
            var cur = animator.GetCurrentAnimatorStateInfo(0);
            return cur.length;
        }

        private void CrossFadeState(string stateName, float fade)
        {
            // 决策先记账（无 controller 也留痕）→ 断言/排障不依赖资产存在
            LastRequestedState = stateName;
            StateRequestCount++;
            if (animator == null || animator.runtimeAnimatorController == null) return;
            animator.CrossFade(stateName, fade);
        }

        /// <summary>Animator 当前是否停在该状态（无 Animator/controller → false）。</summary>
        private bool IsCurrentState(string stateName)
        {
            if (animator == null || animator.runtimeAnimatorController == null) return false;
            return animator.GetCurrentAnimatorStateInfo(0).IsName(stateName);
        }

        /// <summary>纯逻辑：一次性动作是否到点回退（规格 §七：elapsed >= clipLength + 0.05）。测试直接断言。</summary>
        public static bool OneShotElapsed(float elapsed, float clipLength)
        {
            return elapsed >= clipLength + OneShotTailSeconds;
        }
    }
}
