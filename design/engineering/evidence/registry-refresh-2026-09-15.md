# 注册表事实句刷新（#167 · 「接触相位已建」与三条引用者的前置重述）

> [#167](https://github.com/verystrongdog/game/issues/167) 的证据。权威 =
> [项目规约 §五](../../conventions/README.md)（注册表修订流程三条 + 口语判词三问）与 `data/term_registry.json` 的 `_maintenance`（三条入库触发）。
> 必填字段按 [阶段证据说明](README.md) 与 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 本轮结论 | [#165](https://github.com/verystrongdog/game/issues/165) 落地后，注册表里那句话——「**接触相位识别（未建）**」——在 **8 处**活着（**4 条 `definition`** + 1 处候选清单的**理由** + 2 处正典 + 1 条已完成却未标记的待办）。本件逐处刷新为「**✅ 件已建 · ⚠️ 消费方尚未接上**」**两分记**：**不增删任何术语、不改任何语义与边界、不动任何门禁判据代码** |
| 判据现场（本件最有价值的一条） | **R1 确实报了红**——改完注册表、未同步件 docstring 的那一版实测输出：`注册表 \`接触相位\` 定义**未逐字出现**：前 84 字一致，第 85 字起分歧（注册表：…'由它给出。✅ **件已建**（2026-'）`；同步件 docstring 后即绿 ⇒ 「**改一边必红、两边同改才绿**」这句设计意图**是实测的，不是声明的** |
| 计数 | `total_terms` **331** · `active_terms` **308** · `deprecated_terms` **23** —— **逐值不变**（本件不增删术语，只改 4 条的文本） |
| 门禁 | `xbot_contact_phase` **R1–R5 5/5** · `run_all_checks.py` **16/16 退出码 0** · 三个设计校验器 **0 失败** · `validate_issues.py --from-github` **0 违规** |
| 未闭合（§七） | `双支撑` 仍**没有**注册表条目（件按"逐脚区间的交集"给）· `重心` / `支撑多边形` 的**判据部分**（凸包与余量）仍未建 ⇒ 属 [#166](https://github.com/verystrongdog/game/issues/166) 与后续件 · `悬空` 仍在候选清单「暂不动」档 |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `fffc589`（#165 的收尾提交） |
| head SHA | 本提交（注册表 4 条 + 候选清单 + 两处正典 + 件 docstring + 三处登记） |
| 阶段 | [#167](https://github.com/verystrongdog/game/issues/167)（`Task` · 门禁 `docs-integrity` + `xbot_contact_phase.py`） |
| 工具版本 | Python **3.10.12**（校验器）。**本件不跑 Blender、不跑 `dotnet`、不碰 Unity** |
| 判定面 | `data/term_registry.json` · `data/term_registry_candidates.md` · `design/presentation/动作描述口径.md` · `design/presentation/Blender动作制作管线.md` · `code/tools/xbot_contact_phase.py`（docstring） |
| 产物 | 刷新后的 4 条注册表条目 + `_metadata`（第七批）· 候选清单 1 处理由 · 两处正典 3 行 · 件 docstring 同步 |
| 未改（逐字节） | `code/tools/run_all_checks.py` 与全部 `validate_*.py`（**判据代码一律不动**）· `data/hand_grip_cards.json` · `code/unity/**` · `design/conventions/README.md` · 术语条数与计数 |

## 三、逐处 before → after

| # | 位置 | 改前（现在时陈述） | 改后 | 为什么这么改 |
|---|---|---|---|---|
| 1 | 注册表 `接触相位.definition` | 「⚠️ **本仓未建**」 | 「✅ **件已建**（2026-09-15，[#165](https://github.com/verystrongdog/game/issues/165)；本句由 [#167](https://github.com/verystrongdog/game/issues/167) 刷新）：`code/tools/xbot_contact_phase.py`——逐帧从**产物**读、按 M2 取点口径 + `soleMargin = 0.0028 m` 判接触…⚠️ **消费方尚未接上**」 | 件已在册；同时**必须**把"消费方还没接"写在同一句里，否则会从"读成不存在"翻转成"读成已经在用"——两个方向的误读都要堵 |
| 2 | 注册表 `重心.definition` | 「**前置 = 接触相位识别，未建**」+「判据部分…**因缺接触相位**而按 §8.3 过渡态只报读数」 | 「**前置 = 接触相位识别 —— 2026-09-15 已建**（[#165](https://github.com/verystrongdog/game/issues/165)）」+「因**支撑多边形本身仍未建**（缺的是凸包，不再是相位）」 | **归因改回它自己**：过渡态的原因从来是凸包没建，不是相位没建（相位只是凸包的前置） |
| 3 | 注册表 `脚滑.definition` | 「**前置 = 接触相位识别（未建）**；现有读数是在 lab 里手选 `t_c` 算的，**容差档未测**」 | 「**前置 = 接触相位识别 —— 2026-09-15 已建**（[#165](https://github.com/verystrongdog/game/issues/165)）；⚠️ 但**本条读数还没接上它**：…**取帧范围未接件**、**容差档未测**」 | 同 #1 的两分记：**件已建 ≠ 本条已用它**（#165 的证据 §6.1 正是这条的读数） |
| 4 | 注册表 `支撑多边形.definition` | 「**前置 = 接触相位识别（未建）**…⚠️ **本仓尚无任何实现**」 | 「**前置 = … 已建**（[#165](https://github.com/verystrongdog/game/issues/165)）…⚠️ **本件（凸包本身）尚无任何实现**——前置已具备，缺的是本条的判据部分」 | 后半句**仍是真的**，只把主语点明（原来"本仓尚无任何实现"会被读成"连相位都没有"）；**没有顺手删掉它** |
| 5 | 注册表 `接触相位.deviation_reason` | （以"故本条目入库时 definition **明写未建**"收尾） | 追加「🔧 2026-09-15 第七批（[#167](https://github.com/verystrongdog/game/issues/167)）：#165 落地后本句的「未建」不再成立 ⇒ 改为「件已建 · 消费方未开工」两分记（**事实句刷新，语义与边界不变**）」 | 原句是**历史**（"入库时"），保留；加一条日期注记，免得被当成现状 |
| 6 | `data/term_registry_candidates.md`（`稳定`·`站得稳` 行） | 「…`重心` 条已写明判据部分的前置 = 接触相位（**未建**）⇒ 这两个词暂无独立可判内容」 | 「…其判据部分的前置是**支撑多边形**（凸包本身**仍未建**；接触相位这个前置已于 2026-09-15 建好，见 [#165](https://github.com/verystrongdog/game/issues/165)）⇒ 这两个词暂无独立可判内容」 | **结论对、理由错**：理由引用了假事实 ⇒ 只改理由，结论（暂不动）保持 |
| 7 | `动作描述口径.md` §13.6 自由度表「支撑相位」行 | 「接触相位识别（已入库、**未建**）」 | 「接触相位识别（已入库 · 🔧 **2026-09-15 已建** = [#165](https://github.com/verystrongdog/game/issues/165)）」 | 自由度表是 #166 开工第一手材料（它的第 6 行 = 本件的前置） |
| 8 | `动作描述口径.md` §13.6「机器侧待做」行 | 「· 建**接触相位识别**（独立件 = [#165](https://github.com/verystrongdog/game/issues/165)，按口径 §1.1 乙-触发器 ②）·」 | 同句追加「✅ **2026-09-15 已落地**（`code/tools/xbot_contact_phase.py`）」 | **不删行**——它是当时的账（本仓对"历史时点读数不改写"的既有口径）；只标已完成 |
| 9 | `Blender动作制作管线.md` §一 修正注记（`脚滑` 行） | 「⚠️ **前置 = 接触相位识别（未建）**，现有读数是在 lab 里**手选 `t_c`** 算的」 | 「⚠️ **前置 = 接触相位识别**（🔧 2026-09-15 **已建** = [#165](https://github.com/verystrongdog/game/issues/165)；**本条读数尚未接它**），现有读数…」 | 同 #3 |
| 10 | `code/tools/xbot_contact_phase.py` docstring | 引用旧 definition（含「本仓未建」）+ 一段"该句已过期、留后续"的说明 | 逐字同步新 definition + 一段"🔧 第七批已刷新；**刷新时 R1 确实报了红**"的现场记录 | **R1 逐字核两边** ⇒ 注册表与件必须**同一提交**改；这段记录把"判据真的会拦住漂移"留在代码旁边 |
| 11 | `design/slices/CP-01-ward-1f/slice.md` 的四轴行 | 「术语注册表 `接触相位` 条目（2026-09-15 入库，**definition 明写"本仓未建"**）」 | 「（…**入库时** definition 明写"本仓未建"——同日 [#167](https://github.com/verystrongdog/game/issues/167) 已刷新为「件已建 · 消费方未开工」）」 | 该句是**改前状态的证据**，必须标明时点，否则回滚/复盘时读不出"改前是什么样" |
| 12 | `design/engineering/evidence/xbot-contact-phase-2026-09-15.md`（§一 未闭合格 · §四 登记 · §七 第 1 条） | 三处把"注册表未刷新"记为**未闭合** | 标为 ✅ 已闭合并指向本证据 | 证据的账要自己结平——**否则本件自己就成了下一个"没结的账"** |

**一句话**：12 处改动全部落在**事实句与时点标记**上；**没有任何术语的边界、拆分、合并或新条目**，也没有一处动到判据代码。

## 四、R1 的现场报红（判据不是声明）

改完注册表、**尚未**同步件 docstring 的那一版，实跑：

```
$ python3 code/tools/xbot_contact_phase.py --only R1
FAIL  R1  注册表 `接触相位` 定义逐字一致 —— 注册表 `接触相位` 定义**未逐字出现**：
      前 84 字一致，第 85 字起分歧（注册表：…'由它给出。✅ **件已建**（2026-'）
```

同步件 docstring 之后：

```
$ python3 code/tools/xbot_contact_phase.py
PASS  R1  注册表 `接触相位` 定义逐字一致 —— 注册表 `接触相位` 定义（544 字）逐字出现在本件 docstring
```

⇒ 这条判据的价值**当场兑现**：注册表是"某能力有没有"的参考面，件是"它怎么算"的实现面，两边**逐字绑定**；任何一边单独改都会红。⚠️ **覆盖边界照旧**：R1 只核 `接触相位` **这一条**——本件改的另外三条（`重心` / `脚滑` / `支撑多边形`）没有对应判据，**它们的漂移只能靠人**（这条边界在 #165 证据 §七 第 1 条与第 10 条已登记）。

## 五、改后全项目复盘（`data/` `design/` `code/` 里「接触相位」与「未建」同现的行）

| 落点 | 形态 | 判定 |
|---|---|---|
| 注册表 `重心.definition` | 「因**支撑多边形本身仍未建**」 | ✅ 合法——说的是**凸包**，不是相位 |
| 注册表 `接触相位.deviation_reason` | 「入库时 definition **明写未建**」+ 🔧 注记 | ✅ 合法——**历史陈述 + 已刷新注记** |
| 注册表 `_metadata.last_batch` | 「第七批：事实句刷新 4 条——`接触相位`（自己那句「本仓未建」）…」 | ✅ 合法——批次记录本身在描述这次改动 |
| 候选清单 `稳定`·`站得稳` 行 | 「凸包本身**仍未建**；接触相位这个前置已于 2026-09-15 建好」 | ✅ 合法——改后正是这个形态 |
| 切片四轴行 | 「**入库时** definition 明写"本仓未建"——同日 #167 已刷新」 | ✅ 合法——时点已标明 |
| #165 证据（§一 / §四 / §七） | 「~~已过期~~ ✅ 2026-09-15 已闭合」 | ✅ 合法——已结平并指向本证据 |
| 证据索引行（[README.md](README.md)） | 「✅ 同日已由 [#167](https://github.com/verystrongdog/game/issues/167) 刷新」 | ✅ 合法——同一次收口 |
| `code/tools/xbot_contact_phase.py` docstring | 「该条目那句「本仓未建」不再成立 ⇒ 改为…；**刷新时 R1 确实报了红**」 | ✅ 合法——判据用法记录 |

⇒ **没有任何一行仍把"未建"当现在时的事实**（这是本件的验收标准第 6 条）。

## 六、门禁与退出码

| 命令 | 退出码 | 读数 |
|---|---|---|
| `python3 code/tools/xbot_contact_phase.py` | 0 | **R1–R5 5/5 passed**（R1 在同步前实测报红，见 §四） |
| `python3 code/tools/run_all_checks.py` | 0 | **16 validators: 16 passed, 0 failed, 0 errors** |
| `python3 code/tools/validate_cross_refs.py` | 0 | 1975 refs：**0 死链 / 0 段引用警告** |
| `python3 code/tools/validate_trash_isolation.py` | 0 | 全部通过（注册表三档 0 命中；本件未改任何 `status`） |
| `python3 code/tools/validate_params.py` | 0 | 56 checks：0 failed（7 条既有 WARN 与本件无关） |
| `python3 code/tools/validate_issues.py --from-github` | 0 | 14 rules：0 failed |
| `dotnet test` | **未跑** | 本件**未改 `code/src/`**、也未改任何代码行为（件只改 docstring 文本） |
| Blender 侧读数 | **未跑** | 本件不产生任何新读数；#165 的三份报告保持不变（`sha256` 见其证据 §5.1） |

## 七、回滚演练（实做）

```bash
git worktree add --detach .scratch/wt-167 dc492ee     # 本件的提交
cd .scratch/wt-167 && git revert --no-commit HEAD
git diff --stat fffc589                       # ⇒ 空（12 处逐文件回到 #165 收尾态）
python3 code/tools/xbot_contact_phase.py      # ⇒ R1–R5: 5/5 passed（注册表与件 docstring 一起回退 ⇒ 逐字一致重新成立）
python3 code/tools/run_all_checks.py          # ⇒ 16 validators: 16 passed, 0 failed, exit 0
cd .. && git worktree remove --force .scratch/wt-167  # 主工作树未被触碰
```

| 判据 | 预测 | **实测** |
|---|---|---|
| 文本面 | 12 处回到 base | ✅ **`git diff --stat fffc589` 为空** |
| R1 | **仍绿**（两边原子回退） | ✅ **R1–R5 5/5 passed** —— 逐字一致性在回退后重新成立，**没有"回滚留半个状态"** |
| 门禁 | 16/16 | ✅ **16 validators: 16 passed, 0 failed, 0 errors（退出码 0）** |
| 主工作树 | — | ✅ `git worktree remove` 后 `git status --short` 为空 |

⇒ **可回滚，且回滚不产生任何数据迁移**（本件不写 `data/` 之外的结构化契约、不动 manifest、无运行时消费方）。⚠️ 一条如实说明：**回滚会把"件已建"这件事从注册表里抹掉**（回到"未建"）——那不是 bug，是 revert 的定义；但它意味着**注册表文本与仓库里真实存在的件在回滚后会再度不一致**，与 #165 那次的形态相同（一次 `git revert` 只能回退文本，回退不掉"件在 `code/tools/` 里"这个事实）。真要把件也撤掉，得连 #165 一起 revert。

## 八、问题差分

```
new_finding = after − mapped(before) − expected_delta = ∅
```

- **before**：8 处把「接触相位识别（未建）」当**现在时的事实**（逐处见 §三 改前列）；其中 3 处是 `active` 术语的 `definition`。
- **expected_delta（#167 允许变化）**：`data/term_registry.json` · `data/term_registry_candidates.md` · `code/tools/xbot_contact_phase.py`（**只改 docstring**）· `design/presentation/动作描述口径.md` · `design/presentation/Blender动作制作管线.md` · `design/slices/CP-01-ward-1f/slice.md` · `design/engineering/evidence/xbot-contact-phase-2026-09-15.md` · `design/engineering/evidence/registry-refresh-2026-09-15.md`（新增）· `design/engineering/evidence/README.md`。
- **实际变化 = 上述集合**，无清单外文件（`git status --short` 逐条核对）。
- **没有把新问题倒填成"已知债务"**：§九 的三条未闭合都是**本件范围外**的既有条目（双支撑无定义 / 凸包未建 / 悬空候选档），本件**没有**顺手扩大范围去动它们。

## 九、未闭合与边界

| # | 项 | 为什么不在本件 |
|---|---|---|
| 1 | `双支撑` 仍无注册表条目（[#165](https://github.com/verystrongdog/game/issues/165) 的件按"逐脚区间交集"给） | 新增术语属 owner 裁决（本件只刷新**已有**条目的事实句） |
| 2 | `重心` / `支撑多边形` 的**判据部分**（凸包与余量）仍未建 | 属 [#166](https://github.com/verystrongdog/game/issues/166) 与后续件；本件只把"缺的是什么"写准 |
| 3 | `悬空` 仍在候选清单「暂不动」档 | owner 逐词裁决面（[项目规约 §五 第 4 条](../../conventions/README.md)） |
| 4 | **R1 只覆盖 `接触相位` 一条** | 另外三条没有对应的判据 ⇒ 它们的漂移**只能靠人**；这是 #165 那条判据的覆盖边界，本件如实重申 |
| 5 | 术语 `updated` 未变（4 条都已是 `2026-09-15`） | 同日多次修订 ⇒ 值相同；批次证据落在 `_metadata.last_batch`（第七批） |

## 十、复现（最短路径）

```bash
# ① 门禁（纯 Python，不需要 Blender / dotnet）
python3 code/tools/xbot_contact_phase.py && python3 code/tools/run_all_checks.py

# ② 看这次改了什么（逐处 before/after）
git diff fffc589 -- data/term_registry.json data/term_registry_candidates.md \
    design/presentation/动作描述口径.md design/presentation/Blender动作制作管线.md

# ③ 复盘：不该再有把"未建"当现在时的行
grep -rn "接触相位" data/ design/ code/ | grep "未建"
```

---
*创建: 2026-09-15（agent 执行 #167）*
*状态: 12 处事实句已刷新；**R1 现场报红后转绿**（判据用法实测成立）；术语条数与计数逐值不变*
*关联: [#167](https://github.com/verystrongdog/game/issues/167) · [#165](https://github.com/verystrongdog/game/issues/165) · [#166](https://github.com/verystrongdog/game/issues/166) · [项目规约 §五](../../conventions/README.md) · [xbot-contact-phase-2026-09-15.md](xbot-contact-phase-2026-09-15.md)*
