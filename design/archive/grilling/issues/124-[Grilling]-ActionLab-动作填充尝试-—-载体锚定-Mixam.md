# #124 [Grilling] ActionLab 动作填充尝试 — 载体锚定 Mixamo X Bot + 执行形态

> 状态：关闭 · 创建 2026-09-08 · 关闭 2026-09-08
> 标签：维度:呈现, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/124

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

启动 #123 推迟清单第一项「ActionLab 实施（Batch 0-2）」：以「尝试根据动作词表填充动作」为题，定 **演示载体**（Mixamo X Bot）与 **执行形态**（AI 操作边界 / 粒度 / 验收），并按 #123 规格 §六 批次推进 Batch0（`ActionIds` 机器源 + `ActionPlayer` + 防漂移 PlayMode 断言 + 手动手册）。

**动机（用户原话要点）**：AI 通过 cli 直驱 Unity 很方便，但复杂任务不可靠也是事实；用户担心"成规模的 AI 操作"——需用可控粒度/自证/验收机制化解，而非直接放弃直驱。上午 ChatGPT 会话总结（共享链接 6a9f893d）经攻击审查后**无可采纳的新机制/修改**，本次严格按 #123 规格原样推进。

**维度定位**：呈现（角色动作呈现/演示载体）+ 管线（Editor 操作分工、动画资产接入方式、资产与代码的版本管理）。

**依赖**：#123 动作库规格（✅ 词表 12 词条 / 契约 A / 批次 Q5 / 防漂移 §3.3-4）；KiWalkerLab 工程先例（AI 产 builder + 用户点菜单 + Play 验收）；用户本机已下载 Mixamo 资产（Taunt.fbx / X Bot.fbx / Y Bot.fbx）。

**阻塞解除对象**：呈现空缺「反馈动画」（依赖动作底子落成）；#123 推迟清单首项闭环。

**边界（已累计确认）**：
- 上午总结（6a9f893d）→ 无可采纳新机制/修改，不动词表结构与契约 A；
- **载体变更（闭合后修正 #123 规格 §一/§五 的默认载体）**：ActionLab 演示载体 = Mixamo **X Bot（默认）/ Y Bot（备用）**，替换 KI dummy（`Human_BasicMotionsDummy_M`）；KiWalkerLab 与 KI dummy **保留不动**（对照场景 + KI clip 数据源）。理由：词表 12 条中 7 条（物攻/精攻/防御/受击/倒下/坐/站）来自 Mixamo，载体锚 Mixamo 侧 → 高风险接触动作全原生，仅 5 条 KI 通用动作 retarget（低风险）；Taunt.fbx 内 Beta 角色不作载体；
- `Taunt`（嘲讽）**不入词表**（扩展协议三条件不满足：正典来源/呈现形态未定义），仅作候选素材保留。

**当前事实基线（已核验）**：
- unity/Assets 无 .fbx/.anim/.controller 资产入库（资产全部在用户本机工程，未提交）；KiWalkerLabBuilder.cs 幂等四状态 controller（状态名=id，clip 取自导入 FBX，`HumanM@Idle01/Walk01_Forward/Run01_Forward/Jump01`）；
- 用户本机 Downloads：`X Bot.fbx`（1.75MB，mixamorig 标准人形，含网格+皮肤+内置 Take）、`Y Bot.fbx`（1.98MB，同）、`Taunt.fbx`（2.06MB = Beta 角色蒙皮 + Taunt 动画，已解析核验）；
- unity-cli 当前未连接 Editor（No Pipeline instance；manifest.json 未含 com.unity.pipeline，首次需 `unity pipeline install`）；
- 白盒程序化兜底现成：CharacterVisual.cs 已实现 5 缺口动作（PhysicalAttack/MentalAttack/Defend/HitReaction/Down）+ Idle/Walk。

## 决策域（预排）

1. 执行形态 Q0：Batch0 代码先行（AI 零 Editor 操作）vs AI 单步直驱试点（Jump 1 词条闭环）vs 全手动
2. Batch0 代码结构：ActionIds 常量类命名 / ActionPlayer 优先级与计时口径 / controller builder（12 态）/ 防漂移测试断言集 / 手动手册格式与验收
3. 载体导入手册：X Bot 导入路径与 Rig Humanoid 配置、KI 5 clip retarget 目视试点（走/跑）

---

## 评论（1 条）

### verystrongdog · 2026-09-08

## ✅ 关闭总结（Grilling #124 决策闭合）

### 决策表

| # | 决策 | 摘要 |
|---|------|------|
| Q0 | 执行形态 | Batch0 代码先行（AI 零 Editor 操作）→ 用户 pull → 本机导入/生成/Play → Editor+pipeline 就绪后 **Jump 1 词条 AI 直驱试点**（分域原则 + 粒度闸门 + 试点校准） |
| 上午总结审查 | 无可采纳新机制/修改 | 共享会话 6a9f893d 攻击审查后用户裁定：严格按 #123 规格原样推进 |
| Q-v | 载体锚定（🔧 #123 修正） | ActionLab 演示载体 = **Mixamo X Bot（默认）/ Y Bot（备用）**；KiWalkerLab 保留 KI dummy；Taunt/Beta 不入表 |
| Q-B1 | 机器源 | `ActionIds` 12 词条常量 + `ActionCatalog` 元数据（{category, loop, priority, fade, clipFbxPath}） |
| Q-B2 | controller 生成 | 幂等 `ActionLabBuilder`（菜单触发）；状态名=id 由构造成立；缺口状态留空+警告 |
| Q-B3 | ActionPlayer | locomotion 通道 + Play(id) 优先级覆盖；CC 位移 applyRootMotion=false |
| Q-B4 | L2 落点 | Catalog 12 词条全量；controller 仅 L1 9 态；Play(L2) → warning |
| Q-B5 | 防漂移分档断言 | 按 clipFbxPath 资产存在性分档；随导入自动升级 |
| Q-m | 来源实证映射 | Jab Cross→物攻 / Charge→精攻(A 前指) / Short Left Side Step→防御(循环格挡) / Head Hit→受击 / Dying→倒下（5 条无蒙皮核验，文件名≠语义） |

### 受影响文件

- `.scratch/grilling-124-actionlab/决策记录.md`（新建）
- `unity/动作库规格.md`（🔧 闭合后修正：载体 + 来源矩阵实证）
- `docs/决策树.md`（#124 条目 + #123 推迟项注记）
- `docs/设计框架-六维状态.md`（呈现 +1 → 6）
- `unity/README.md`（§二·D 更新 + §二·E 实施手册 + §三 结构树）
- `项目总览.md`（入口）
- memory `动作集实施-grilling-124.md`

### 写入验证表

| 决策 | 写入位置 | 验证 |
|------|---------|------|
| Q0-Q-m | 决策记录.md 全表 | ✅ |
| Q-v/Q-m | 动作库规格.md 注记 + §一/§二 | ✅ |
| 决策树/六维状态/项目总览/memory | 见上 | ✅ |

### 推迟清单

- Jump 1 词条 AI 直驱试点（依赖本机 Editor + pipeline 就绪）
- Batch1 用户执行（X Bot/Y Bot 导入 + 5 clip 改名 + 菜单生成 + Play 目视）
- 物攻单次直拳语义 / HitReaction 通用性（Play 后判）
- L2（Sit/Stand/Talk）接线（消费端就绪时）
- Batch0 代码实施（同会话交付中）

---
*导出: 2026-09-12 | 来源: GitHub issue*
