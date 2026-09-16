# 定位裁定：叙事驱动的心理 CRPG（[#181](https://github.com/verystrongdog/game/issues/181) 选项 A）

> **阶段性质**：**设计面**变化——本阶段**只改 `design/` 与两份根文档**，不动 `data/`、`code/`、门禁与历史证据（对应 #181 §预期差分）。
> **一句话结论**：owner 在「叙事优先 / 叙事与战斗并重 / 战斗优先」之间选定**叙事优先**，CP-01 保留为候选并**按叙事优先重写合同**，回合战斗被裁定为**并列解决路径之一**；8 个注册文件全部落到正典，`new_finding` 为空，`git revert` 逐字节恢复 base。

| 字段 | 值 |
|---|---|
| issue | [#181](https://github.com/verystrongdog/game/issues/181)（RFC · owner 决策 = **选项 A**） |
| base SHA | `f4152f6`（`feat+docs: #180 第 3 轮按 owner 指名的四个量返工…`） |
| head SHA | `32770e4`（8 文件落地的最后一个改动提交；记录提交见 §四 的绑定说明） |
| 工具版本 | Python 3.10.12 · git 2.34.1 · `gh` 2.100.0 |
| 工作树 | 检查后干净（`git status --short` 无输出） |

## 一、本阶段的提交组（一个提交一种变化）

| # | SHA | 主题 | 改了什么 |
|---|---|---|---|
| 1 | `aaad0c9` | 产品定位 | `README.md` 定位句 + 当前阶段 + 页脚 |
| 2 | `9e24f96` | 核心循环与战斗职责 | `design/events/游戏循环.md` **新增 §1.3**、§2.2 休息动机去战斗化；`design/events/世界观与叙事.md` §战斗逻辑 新增「战斗在核心循环中的职责」 |
| 3 | `a0e11df` | 叙事后果边界 | `design/events/剧情系统设计.md` **新增 §3.1.1**（六类后果 + `m/SAN/HP` 只走既有通道）、§五 关系表两行；`design/events/任务目标系统.md` §1.2 两行 |
| 4 | `737dcb5` | 动作生产边界 | `design/presentation/动作库规格.md` **新增 §1.1**（冻结自研泛化 · 保留存量 · 外部工具生产 · 接口不变）+ 与 #173 §7.8 的读法 |
| 5 | `a03b5ce` | CP-01 去向与合同 | `design/slices/CP-01-ward-1f/slice.md` §1.1/§1.2/§1.3 重写 + §二 `探索与接敌` 行 `Design: UNRESOLVED → ACCEPTED`；`PLAYABLE.md` 同步 |

**预期差分核对**：#181 §预期差分列出的 **8 个文件全部**落地；**未超出**——本阶段**没有**修改预期差分之外的任何正典文件（含未被列出的候选：见 §四 未闭合项 3）。

## 二、七条验收标准逐条对照

| # | 标准 | 落地位置（改后） |
|---|---|---|
| 1 | owner 选一个选项并写明理由 | 决策 = **A**；理由与代价见 #181 §owner 决策（本阶段回填）。依据：与 owner 已声明的方向一致 · 仓库仍 `NO_AUTHORIZED_PLAYABLE`、CP-01 只是候选 ⇒ 回滚成本最低 · B 的制作量、C 的目标落空、D 让已 E2E 的回合结算失去消费方 |
| 2 | CP-01 去向一致 | **保留 + 重写合同**（不标 `SUPERSEDED`）：`PLAYABLE.md` §候选切片 与 `slice.md` §1.1/§1.2/§1.3 同步；`NO_AUTHORIZED_PLAYABLE` **不变** |
| 3 | 战斗职责 | `游戏循环 §1.3` + `世界观与叙事 §战斗逻辑`：**并列解决路径之一**、**冲突升级后的可选解决器** |
| 4 | 非战斗行为是否进入休息与时段推进 | `游戏循环 §2.2`：推进时段的动作**仍是休息**（公式/恢复量不变），但**休息动机不再绑在战斗上**——对话/调查/异常暴露/检定失败/空间爬深同样构成动机 |
| 5 | 叙事后果边界 | `剧情系统设计 §3.1.1`：六类后果（关系 · 世界状态 · 感知版本 · 空间访问 · 自问演化 · 结局映射）+ `m/SAN/HP` **不进表**、只经 `核心机制 §8.2/§8.3` 的巩固窗口或战斗/休息结算 |
| 6 | 自研动作生成的停止边界 | `动作库规格 §1.1`：冻结**泛化目标** · 既有资产与研究**全保留** · 外部工具生产 · **接口不变只换产出方**；与 #173 §7.8 的关系写明读法（管线保留为**判定与接缝**工具） |
| 7 | 决策落正典 + 后续 issue | 决策落 8 文件（上表）；**后续 issue 尚未建立**——见 §四 未闭合项 1 |

## 三、门禁读数（逐条实跑）

| 命令 | 退出码 | 读数 |
|---|---|---|
| `python3 code/tools/validate_cross_refs.py` | **0** | `2152 refs: 2151 passed, **0 dead, 0 section warnings**`（base 为 2144/2143/0/0） |
| `python3 code/tools/validate_trash_isolation.py` | **0** | ✅ 全部通过；关闭档欠账分布与改前**逐条相同**（态度 29 · AP 28 · 意志力 17 · 预烘焙 3 · 5模块 2 · 7驱动 1 · L0-L6 1 · w_perception 1 · w_execution 1）；只登记档命中 67 处不变 |
| `python3 code/tools/validate_params.py` | **0** | `56 checks: 49 passed, 0 failed, 7 warnings`（与 base 逐条相同） |
| `python3 code/tools/validate_issues.py --from-github` | **0** | `14 rules: 10 passed, 0 failed, 4 warnings, 0 skipped`（4 条警告与改前同一集合：`consumed-by: 待建:` ×2 与 I13 文件相交 ×2） |
| `dotnet test` | 未跑 | 本阶段不改 `code/`（按 [AGENTS.md §三](../../../AGENTS.md)：改代码才跑） |

**问题差分**：`new_finding = after − mapped(before) − expected_delta` = **空**（三个校验器的失败数与警告集合与 base 逐条相同；新增的 8 处引用全部解析成功）。

## 四、回滚演练（实做）

```bash
git worktree add --detach .scratch/revert-drill2 HEAD     # HEAD = 记录提交，含本证据文件与索引行
git -C .scratch/revert-drill2 revert -n --no-edit f4152f6..HEAD
git -C .scratch/revert-drill2 diff --quiet f4152f6 ; echo $?   # → 0
```

**结论：可干净回滚**——**`f4152f6..a770215` 范围内的全部 9 个提交**（正典改动 6 条 + 证据文件/索引/引用口径/补漏 3 条）逆序 revert 后，工作树与 base `f4152f6` **逐字节相同**（`git diff` 退出码 0）。本阶段全部为设计面文本改动，无数据迁移、无删除、无玩家行为，故回滚不需要额外方案。演练后 `git worktree remove --force` + `prune`，主工作树未受影响（`git status --short` 无输出）。

> 绑定：本证据的**内容**对应 head `32770e4`（8 文件落地的最后一个改动提交）；`c75c866` / `0945988` / `a770215` 只改本文件、证据索引，以及 §五·6 登记的三处补漏（`任务目标系统 §九` 的门控承诺措辞 · `游戏循环 §2.2` 的「恢复量不因动机而变」一句）。**演练范围止于 `a770215`**：其后只改本文件与 GitHub issue 正文（不在仓库内），不改任何正典内容与结论。

## 五、未闭合项（如实登记）

1. **后续 issue 未建立**：#181 验收第 7 条要求「通过导入门后按 `design → data → code → unity` 建立必要的后续 issue」。当前**不具备**建立条件——CP-01 的 M1 前置（叙事解释器 `StoryEngine`、`data/` 侧的对话树契约与 `validate_story.py`）都要靠新 issue，而 [issue-process §六·R7](issue-process.md) 明令：`PLAYABLE.md` 仍是 `NO_AUTHORIZED_PLAYABLE` 时**不得**开"实现并试玩 CP-01"。⇒ 下一步是 **owner 的 CP-01 准入决策**（`PLAYABLE.md` 改 `AUTHORIZED_PLAYABLE: CP-01`），此后才可按 frontier 分解。本项不是本阶段欠账，是**流程上的下一道门**。
2. **`PLAYABLE.md` 仍是 `CANDIDATE`**：定位裁定**不**构成准入；未准入期间不得新增正式玩家行为。
3. **判定为「不必改」的三个候选文件（登记理由，非欠账）**：
   - `design/rules/回合战斗流程.md` §八：读过全文——它只定义战斗的**开始/结束/逃跑**，**没有**"战斗必经"的表述（§8.2 已含投降/逃跑/全员退出三条非歼灭终止路径）⇒ 与选项 A 不冲突，**不改**。
   - `design/rules/核心机制.md` §8.2/§8.3：它已经是**非战斗事件强度 → 巩固窗口 → Δm** 的唯一权威 ⇒ `§3.1.1` **只引用不复制**，不改。
   - `design/presentation/Blender动作制作管线.md` §7.8：与 §1.1 冻结的**不是**同一件事（该节保的是**受控研发管线**，本节冻的是**泛化推进方向**）⇒ 读法已写进 `动作库规格 §1.1`，**不改该文件**（超出预期差分）。
4. **`design/space/空间与关卡设计.md` §6.1/§6.2 与选项 A 有张力（未处理）**：该处写「L1 扭曲房间内部是**单节点（一个战斗场景）**」、「进入后门关上 → **战斗**/探索结束」。战斗既已裁为并列路径，扭曲房间的**非战斗解法**在该文件里没有对应表述 ⇒ **超出** #181 预期差分，本阶段未改，登记为缺口（建议随 CP-01 准入后的空间设计 issue 一并处理）。
5. **动作线口径**：`#180` 已按 owner 指示标 `state:blocked`（等 owner 目视），`#181` 接管全仓唯一 `in-progress`；两条的「预期差分」在 `动作库规格.md` / `slice.md` 上相交（I13 警告），故必须串行——本阶段已在 #180 未能动的前提下落地。
6. **定位变更后会漂移、但超出预期差分、本阶段未改的三处**（登记，供 CP-01 准入后一并处理）：
   - `design/framework/six-dimensions.md` §六维定义与分拣标准 / §规则：路由表以战斗轴为主，定位改为叙事优先后**「这个游戏设计到哪一步」的入口读数即漂移**（本阶段只登记了其中「SAN恢复规则」行的缺陷）。
   - `design/rules/核心机制.md` §2.3 构建层 vs 战斗层：既已区分「构建层（非战斗）」，选项 A 下**构建层是否升为一个可玩的独立环节**尚无表述。
   - `design/rules/skill-tree/NPC AI 行为模型.md` §七 行动生成：NPC 的**非战斗行为是否走同一套 salience 选择**未答（战斗侧行动生成仍有效、不解除消费）。
7. **两处与 #181 无关的正典缺陷（本阶段发现，未处理）**：
   - `design/framework/six-dimensions.md` §规则·「已完成」表的「SAN恢复规则」行写「内省+5/自省+3/休息+5/**叙事+10**」并引 `核心机制 §5.2`——**该节无此项**，且与 `剧情系统设计 §3.1.1` 的正交约束**互斥**（已在 §3.1.1 末尾写为反向约束）。
   - `design/engineering/issue-process.md` §三 Step 2 / §六 R8 仍写「Unity 门禁本机 `NOT_AVAILABLE`」，与 `gates.json`（`available: true`）和 [build-and-test.md §五](build-and-test.md)（「本机已可跑」）**直接矛盾**；真正阻塞试玩的是 `PLAYABLE.md` 的准入状态，不是门禁。

---
*创建: 2026-09-16 | 关联: [#181](https://github.com/verystrongdog/game/issues/181), [证据索引](README.md), [PLAYABLE.md](../../../PLAYABLE.md), [WORKFLOW.md §五](../../../WORKFLOW.md)*
