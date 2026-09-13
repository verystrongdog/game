// 动作播放驱动 — 契约 A（动作库规格.md §四）：纯状态集 + 运行时 CrossFade
// - 状态名 = 词表 id = 代码字符串（三面对一，由 ActionLabBuilder 按 ActionCatalog 构造成立）
// - 衔接优先级：Down(4) > HitReaction(3) > 一次性动作(2) > 持续态(1) > locomotion(0)
// - 一次性动作播完（clip.length + 0.05s）→ ① 若词条声明了 NextState 就切它（Sit → SitIdle「坐住」）；
//   ② 否则回退 locomotion 目标（规格 §七 计时口径）
// - 空中 Jump → 落地：显式补发一次回切（Jump 这次切态不进 _locomotionTarget 的账，
//   否则落地目标与起跳前同档时守卫判"无变化"→ 状态机停在 Jump，身体平移而腿不动）
// - 循环持续态（Loop=true 的动作词条：Defend / SitIdle）：TickLocomotion 收到移动意图(speed>0)
//   即退出；**若该词条声明了 `ExitVia`（SitIdle → Stand），则先播那条一次性动作、播完才回 locomotion**
//   （规格 §四·丁#7：离座也要走完整动作）；或更高优先级动作打断。**不硬编码具体 id**——新增持续态只改词表即可。
// - Down 终态停留末帧：不自动回退，须 Reset()（演示 R 键）
// - 位移全走 CharacterController（本组件不移动物体）；`Animator.applyRootMotion` **按词条状态**切换：
//   只有声明了 `RootMotionXZ` 的坐立三段为 true（驱动层据此施加 XZ 根位移，规格 §四·乙 再修正），其余为 false。
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

        /// <summary>
        /// 当前动作是否声明了 **XZ 根位移**（坐立三段：`Sit` / `SitIdle` / `Stand`）。
        /// 驱动层据此逐帧切 `Animator.applyRootMotion`，并在 `OnAnimatorMove` 里把
        /// `deltaPosition` 的 XZ 分量经 CharacterController 施加——角色由此从椅子前方的
        /// 就座锚点（0.423 m）退到坐面上。规格 §四·乙 再修正 / §四·丁#5。
        /// </summary>
        public bool ApplyRootMotionXZ => _activeEntry != null && _activeEntry.RootMotionXZ;

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

            // 持续态（Loop=true 的动作词条：Defend / SitIdle）：无移动意图 → 原地保持
            if (_activeEntry != null && _activeEntry.Loop && speed01 <= 0.001f)
            {
                return;
            }

            // 离开持续态时记名：下面要清 _activeEntry，但守卫需要知道"刚从哪个持续态出来"
            string sustainedExited = (_activeEntry != null && _activeEntry.Loop) ? _activeEntry.Id : null;

            // 🔧 离座口径（规格 §四·丁#7）：持续态声明了 exitVia（SitIdle → Stand）时，
            //    移动意图不直接弹回 locomotion，而是先把那条一次性动作播完——「先找到椅子才能坐」
            //    的对称面：坐下与离座都走完整动作，不出现"无起身动画地站起来"。按字段判定，不硬编码 id。
            if (_activeEntry != null && _activeEntry.Loop && _activeEntry.ExitVia != null
                && ActionCatalog.TryGet(_activeEntry.ExitVia, out var exitEntry))
            {
                StartAction(exitEntry);
                return;
            }

            // locomotion 目标（持续态被移动意图退出）
            _activeEntry = null;
            CurrentActionId = null; // 持续态退出 / 常规 locomotion 路径清动作显示
            string target = LocomotionTargetForSpeed(speed01);

            // 守卫：档位变化 || 刚从空中落地（补发）|| 刚从持续态退出（需显式切出去）
            if (target != _locomotionTarget || _returnFromJumpPending
                || (sustainedExited != null && IsCurrentState(sustainedExited)))
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
            _plannedDuration = 0f;
            // 必须清 CurrentActionId：否则重置后它仍留旧值，凡依赖它做输入守卫的路径都会被误导
            // （例：7 起身的守卫要求"当前是 SitIdle"——重置后不干净就会被误判为仍在坐姿）。
            // 这也是既有常红断言 ActionPlayer_Play_PriorityAndLevelRules 的第二处真因（2026-09-12 定位）。
            CurrentActionId = null;
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
                // 长度**延到下一帧**再读：CrossFade 当帧 GetNextAnimatorStateInfo 尚未填充，
                // 此处读会拿到**上一个状态**的 clip 长度（实测 2026-09-12：从 Idle(2.7s) 坐
                // →锁 2.75s 而非 1.85s；从 SitIdle(4.3s) 起身 →锁 4.35s 而非 1.85s，
                // 人已站起却多锁 2.5s）。负值 = 待定，Update 里补读。
                _plannedDuration = -1f;
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
                if (_plannedDuration < 0f)
                {
                    // 目标 clip 长度未定 → 逐帧重试，读到为止（不阻塞计时，_activeTime 一直在走）。
                    // 超过 0.5 s 还读不到才用兜底时长，避免永久卡在"未定"。
                    float clipLen = ReadTargetClipLength();
                    if (clipLen > 0f) _plannedDuration = clipLen + OneShotTailSeconds;
                    else if (_activeTime > 0.5f) _plannedDuration = _fallbackDuration;
                    else return;
                }
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
            _activeTime = 0f;

            // 一次性动作可声明播完后切到哪（Sit → SitIdle：坐下播完要"坐住"，不回站姿）。
            // 未声明 → 回退 locomotion 目标态（原口径）。
            string next = _activeEntry != null ? _activeEntry.NextState : null;
            if (next != null && ActionCatalog.TryGet(next, out var nextEntry))
            {
                _activeEntry = nextEntry;
                _plannedDuration = 0f;
                CurrentActionId = nextEntry.Id;
                IsLocked = !nextEntry.Loop;   // 续接的若是循环持续态（SitIdle），则不锁移动切态
                CrossFadeState(nextEntry.Id, nextEntry.Fade);
                return;
            }

            _activeEntry = null;
            IsLocked = false;
            CurrentActionId = null;
            // 回退档位按**当前速度**取（锁定期间 speed01 照常由驱动层喂进来）：
            // 若这里沿用旧缓存，坐姿下按 W → Stand 播完 → 先淡回 Idle、下一帧才淡到 Walk（多一次融合）。
            _locomotionTarget = LocomotionTargetForSpeed(HorizontalSpeed01);
            if (animator != null && animator.runtimeAnimatorController != null)
            {
                CrossFadeState(_locomotionTarget, ActionCatalog.Get(_locomotionTarget).Fade);
            }
        }

        /// <summary>locomotion 档位阈值（唯一来源：0.05 起走 / 0.55 起跑）。</summary>
        private static string LocomotionTargetForSpeed(float speed01)
            => speed01 < 0.05f ? ActionIds.Idle
             : speed01 < 0.55f ? ActionIds.Walk
             : ActionIds.Run;

        /// <summary>
        /// 一次性动作**目标态**的 clip 长度（未定则返回 0，调用方下一帧再试）。
        /// 关键：**只接受 shortNameHash 与目标状态一致的读数**——不能回退去读"当前状态"的长度。
        /// 实测 2026-09-12：`CrossFade` 发起的当帧过渡尚未注册，此时 `GetNext.length == 0`（无过渡）
        /// 且 `GetCurrent` 仍是**源状态**，若回退读它就会得到源 clip 长度
        /// （从 Idle(2.7s) 坐 → 锁 2.75s 而非 1.85s；从 SitIdle(4.3s) 起身 → 锁 4.35s 而非 1.85s，
        /// 人已站起却多锁 2.5s）。
        /// </summary>
        private float ReadTargetClipLength()
        {
            if (animator == null || animator.runtimeAnimatorController == null) return 0f;
            int want = Animator.StringToHash(_activeEntry.Id);   // 三面对一：状态名 = 词表 id
            var next = animator.GetNextAnimatorStateInfo(0);
            if (next.shortNameHash == want && next.length > 0f) return next.length;
            var cur = animator.GetCurrentAnimatorStateInfo(0);
            if (cur.shortNameHash == want && cur.length > 0f) return cur.length;
            return 0f;
        }

        private void CrossFadeState(string stateName, float fade)
        {
            // 决策先记账（无 controller 也留痕）→ 断言/排障不依赖资产存在
            LastRequestedState = stateName;
            StateRequestCount++;
            if (animator == null || animator.runtimeAnimatorController == null) return;
            // ⚠️ 必须用**秒制**变体。`Animator.CrossFade(name, fade)` 的第二参是
            //    「**源状态归一化时长的比例**」，不是秒（官方参数名 normalizedTransitionDuration；
            //    Manual「Fixed Duration」条：不勾选时过渡时长按"源状态归一化时长的比例"解释）。
            //    实测（2026-09-12，确定性 5 ms 步进量 IsInTransition 持续时长，fade 一律传 0.10）：
            //      Defend(0.8s)→0.085s / Jump(1.533s)→0.155s / Sit(1.8s)→0.180s
            //      / Idle(2.7s)→0.275s / SitIdle(4.3s)→0.430s   —— 逐行 = 0.10 × 源 clip 长度
            //    改用 CrossFadeInFixedTime 后，五种源一律 0.100 s。
            //    规格 §七 的 fade 口径是**秒**，故以秒制为准（AGENTS.md：设计与代码冲突以 design/ 为准并修代码）。
            animator.CrossFadeInFixedTime(stateName, fade);
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
            // 显式落回 float 再比较。C# 允许浮点运算使用高于结果类型的精度：若直接写
            //   elapsed >= clipLength + OneShotTailSeconds
            // 右侧可能以 double 中间值参与比较，与外部按 float 算出的同一个和相差 1 ulp
            // → 恰好到点被判为"未到点"。这就是既有常红断言
            // ActionLabSmokeTests.ActionPlayer_OneShotElapsed_Threshold 的真因（2026-09-12 定位）。
            float threshold = (float)((double)clipLength + (double)OneShotTailSeconds);
            return elapsed >= threshold;
        }
    }
}
