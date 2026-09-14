// BlenderAnimationDebugger —— Blender 回导 clip 的逐帧调试载体（运行时）
//
// 目标（#156 验收标准第 4/5 条）：给「从 Blender 回导的 animation-only FBX」一个**可暂停、可单帧步进、
// 可复位**的观察面，并把「当前 clip / 帧号 / Hips·双手·双脚姿势读数」显示出来，使"同一 clip 同一帧
// 重复采样逐次一致"这类判据可以被机械断言（而不是只看连续播放顺不顺眼）。
//
// 口径权威：design/presentation/Blender动作制作管线.md §五（回导判据）
//   §五·1 读数点固定为 Hips / LeftHand / RightHand / LeftFoot / RightFoot——与 Blender 侧
//          `export_xbot_action.py` 的 READOUT_BONES 同一组人形骨，两端可比。
//   §五·2 定位走「确定性姿势求值」：`Animator.Play(state, 0, normalized) + Animator.Update(0f)`。
//
// ⚠️ 三个实测坑（继承 AnimationRiggingProbe.PoseAtFrame，2026-09-14）：
//   ① 必须调 `Update(0f)`，否则定位不生效；
//   ② 顺序是 Play → Update(0f) → **再**冻结 `speed`；先冻结 speed 再 Play 同样不生效；
//   ③ 已在播的状态上直接 Play 也要走 `Update(0f)`。
using System;
using System.Text;
using UnityEngine;

namespace YANTF.ActionLab
{
    /// <summary>
    /// 逐帧检查一个从 Blender 回导的人形 clip：播放/暂停、前后单帧、回首帧，并输出关键骨读数。
    /// 只读姿势、不改状态机、不碰已入库的动作语义。
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class BlenderAnimationDebugger : MonoBehaviour
    {
        /// <summary>读数点——与 Blender 侧 `export_xbot_action.py` 的 `READOUT_BONES` 逐项对应。</summary>
        public static readonly HumanBodyBones[] ReadoutBones =
        {
            HumanBodyBones.Hips,
            HumanBodyBones.LeftHand,
            HumanBodyBones.RightHand,
            HumanBodyBones.LeftFoot,
            HumanBodyBones.RightFoot,
        };

        /// <summary>单根骨的读数。`LocalPosition` 相对父骨，`RootLocalPosition` 相对角色根（对整体平移不变）。</summary>
        public struct BoneReadout
        {
            public string Bone;
            public Vector3 LocalPosition;
            public Vector3 LocalEuler;
            public Vector3 RootLocalPosition;

            public override string ToString() =>
                $"{Bone} root={Fmt(RootLocalPosition)} local={Fmt(LocalPosition)} euler={Fmt(LocalEuler)}";

            private static string Fmt(Vector3 v) => $"({v.x:F5},{v.y:F5},{v.z:F5})";
        }

        [SerializeField] private Animator _animator;
        [SerializeField] private string _clipName = "RigRoundTripProbe";
        [SerializeField] private bool _playOnStart = true;
        [SerializeField] private bool _acceptInput = true;
        [SerializeField] private bool _loopInPlay = true;

        private int _stateHash;
        private AnimationClip _clip;
        private int _frame;
        private bool _playing;
        /// <summary>是否已被外部驱动过。`Start` 的自动播放/停首帧只在**没人驱动过**时才做。</summary>
        private bool _driven;
        private readonly BoneReadout[] _readout = new BoneReadout[ReadoutBones.Length];

        // ---------------- 只读面（供断言与 eval 读数）----------------

        public Animator Animator => _animator;
        public AnimationClip Clip => _clip;
        public string CurrentClipName => _clip != null ? _clip.name : "(none)";
        /// <summary>帧数 = `clip.length × clip.frameRate`（本 clip 实测 60；帧号域 0..60）。</summary>
        public int FrameCount => _clip != null && _clip.frameRate > 0f
            ? Mathf.RoundToInt(_clip.length * _clip.frameRate)
            : 0;
        public int CurrentFrame => _frame;
        public bool IsPlaying => _playing;
        /// <summary>最近一次读数（长度 = `ReadoutBones.Length`）。</summary>
        public BoneReadout[] LastReadout => _readout;

        // ---------------- 生命周期 ----------------

        private void Awake()
        {
            if (_animator == null) _animator = GetComponent<Animator>();
            // 场景加载路径也照报"controller/clip 找不到"——那正是引用 missing 的症状；
            // 但"还没有 Animator"在这一刻是正常的（Attach 会随后接线），故只有显式调用才报。
            ResolveClipInternal(verbose: false);
        }

        /// <summary>
        /// 把一个载体（模型实例）装成调试载体：接上 Animator（avatar 用载体自身的）+ controller
        /// + 本组件。**菜单路径与 PlayMode 断言共用这一条**，避免两处各写一份装配逻辑。
        /// </summary>
        public static BlenderAnimationDebugger Attach(GameObject carrier, RuntimeAnimatorController controller,
            string clipName)
        {
            if (carrier == null) return null;
            var animator = carrier.GetComponent<Animator>();
            if (animator == null) animator = carrier.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller;
            animator.applyRootMotion = false;
            // 调试面：角色跑出视野也不能停更（默认 CullUpdateTransforms 会让读数看不出变化）
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;

            var dbg = carrier.GetComponent<BlenderAnimationDebugger>();
            if (dbg == null) dbg = carrier.AddComponent<BlenderAnimationDebugger>();
            dbg._animator = animator;
            dbg._clipName = clipName;
            dbg.ResolveClip();
            return dbg;
        }

        /// <summary>是否在 `Start` 时自动开播（lab 用 true；断言用 false，避免与逐帧定位抢时间轴）。</summary>
        public bool AutoPlay
        {
            get => _playOnStart;
            set => _playOnStart = value;
        }

        /// <summary>连续播放时是否在末帧接回首帧（lab 用 true；逐帧定位路径不受影响）。</summary>
        public bool LoopInPlay
        {
            get => _loopInPlay;
            set => _loopInPlay = value;
        }

        private void Start()
        {
            // ⚠️ `Start` 在**下一帧**才跑：调用方（菜单装配、PlayMode 断言）可能已经在同一帧里
            //    Play / SampleAtFrame 过了。此时再按 `_playOnStart` 兜一次会**静默取消**刚开的播放
            //    ——2026-09-14 实测踩到（新增的接环断言就死在这条上，表现为"接环把播放态关掉了"）。
            if (_driven) return;
            if (_playOnStart) Play();
            else SampleAtFrame(0);
        }

        /// <summary>把 animator 上的目标 clip 找出来（按名字；找不到则退回第一个 humanMotion clip）。</summary>
        public void ResolveClip() => ResolveClipInternal(verbose: true);

        private void ResolveClipInternal(bool verbose)
        {
            _clip = null;
            if (_animator == null)
            {
                if (verbose) Debug.LogError("[BlenderDebugger] 没有 Animator——调试载体没装配好", this);
                return;
            }
            if (_animator.runtimeAnimatorController == null)
            {
                Debug.LogError("[BlenderDebugger] Animator 没有 RuntimeAnimatorController——" +
                               "lab 场景里的 controller 引用可能已 missing（资产被重建换过 GUID？）", this);
                return;
            }
            foreach (var c in _animator.runtimeAnimatorController.animationClips)
            {
                if (c == null) continue;
                if (c.name == _clipName) { _clip = c; break; }
                if (_clip == null && c.humanMotion) _clip = c;
            }
            if (_clip == null)
                Debug.LogError($"[BlenderDebugger] controller 里找不到 clip \"{_clipName}\"", this);
            _stateHash = string.IsNullOrEmpty(_clipName) ? 0 : Animator.StringToHash(_clipName);
        }

        private void Update()
        {
            if (_acceptInput) HandleInput();
            if (!_playing || _animator == null || _clip == null) return;

            var st = _animator.GetCurrentAnimatorStateInfo(0);
            if (_loopInPlay && st.normalizedTime >= 1f)
            {
                // 回导样本本身是**一次性**的（探针首末帧同为静止姿势），停在末帧等于"看起来没动静"——
                // lab 的用途是逐帧目视，故**播放层面**接成环（不改 FBX、不改导入设置，样本仍是一次性）。
                _frame = 0;
                _animator.Play(_stateHash, 0, 0f);
                _animator.Update(0f);
            }
            else
            {
                _frame = FrameFromNormalized(st.normalizedTime);
            }
            CaptureReadout();
        }

        /// <summary>lab 里的人手操作：空格播放/暂停 · ←/→ 单帧 · R 回首帧。</summary>
        private void HandleInput()
        {
            if (Input.GetKeyDown(KeyCode.Space)) TogglePlay();
            if (Input.GetKeyDown(KeyCode.LeftArrow)) StepFrames(-1);
            if (Input.GetKeyDown(KeyCode.RightArrow)) StepFrames(1);
            if (Input.GetKeyDown(KeyCode.R)) ResetToFirstFrame();
        }

        // ---------------- 调试控制（#156 验收标准第 4 条）----------------

        /// <summary>播放当前 clip（从当前帧续播；已停在末帧则从头再来一遍）。</summary>
        public void Play()
        {
            if (_animator == null || _clip == null) return;
            _driven = true;
            if (_frame >= FrameCount) _frame = 0;
            _animator.speed = 1f;
            _animator.Play(_stateHash, 0, NormalizedFromFrame(_frame));
            _animator.Update(0f);
            _playing = true;
        }

        /// <summary>暂停在当前帧。</summary>
        public void Pause()
        {
            _driven = true;
            if (_animator != null) _animator.speed = 0f;
            _playing = false;
        }

        /// <summary>前后单帧（边界内夹紧；不动就报 false 之外无副作用）。</summary>
        public void StepFrames(int delta) => SampleAtFrame(_frame + delta);

        /// <summary>回到首帧（第 0 帧）并停住。</summary>
        public void ResetToFirstFrame() => SampleAtFrame(0);

        /// <summary>播放/暂停切换。</summary>
        public void TogglePlay()
        {
            if (_playing) Pause();
            else Play();
        }

        /// <summary>
        /// 确定性地把骨架摆到第 `frame` 帧并冻结（unity-cli README §五 的路径）。
        /// 顺序固定为 Play → `Update(0f)` → 冻结 `speed`（见文件头三个坑）。
        /// </summary>
        public void SampleAtFrame(int frame)
        {
            if (_animator == null || _clip == null) return;
            _driven = true;
            _frame = Mathf.Clamp(frame, 0, FrameCount);
            _animator.speed = 1f;
            _animator.Play(_stateHash, 0, NormalizedFromFrame(_frame));
            _animator.Update(0f);
            _animator.speed = 0f;
            _playing = false;
            CaptureReadout();
        }

        // ---------------- 读数 ----------------

        /// <summary>读一次当前姿势，写进 `LastReadout`。</summary>
        public void CaptureReadout()
        {
            if (_animator == null) return;
            var root = _animator.transform;
            for (int i = 0; i < ReadoutBones.Length; i++)
            {
                var t = _animator.GetBoneTransform(ReadoutBones[i]);
                if (t == null)
                {
                    _readout[i] = new BoneReadout { Bone = ReadoutBones[i].ToString() };
                    continue;
                }
                _readout[i] = new BoneReadout
                {
                    Bone = ReadoutBones[i].ToString(),
                    LocalPosition = t.localPosition,
                    LocalEuler = t.localRotation.eulerAngles,
                    RootLocalPosition = root.InverseTransformPoint(t.position),
                };
            }
        }

        /// <summary>一行摘要：clip / 帧号 / 五个读数点（HUD、日志与 eval 共用同一串）。</summary>
        public string ReadoutLine()
        {
            var sb = new StringBuilder();
            sb.Append($"clip={CurrentClipName} frame={_frame}/{FrameCount} playing={_playing}");
            foreach (var r in _readout) sb.Append("\n  ").Append(r);
            return sb.ToString();
        }

        private float NormalizedFromFrame(int frame)
        {
            int n = FrameCount;
            return n <= 0 ? 0f : Mathf.Clamp01((float)frame / n);
        }

        private int FrameFromNormalized(float normalized)
        {
            int n = FrameCount;
            if (n <= 0) return 0;
            return Mathf.Clamp(Mathf.RoundToInt(normalized * n), 0, n);
        }

        // ---------------- HUD ----------------

        private void OnGUI()
        {
            if (_clip == null) return;
            GUI.Label(new Rect(10f, 10f, 620f, 150f), ReadoutLine());
        }
    }
}
