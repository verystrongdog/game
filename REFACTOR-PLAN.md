# 仓库重构计划

> 把 `/home/dog/game` 从「设计文档 + 代码 + 数据 + 流程存档混在一起、且流程仪式已超过设计资产」的现状，重构为「设计与代码边界清晰、文档结构反映真实设计、流程约束按需可用」的单仓结构。本文档是执行依据，执行完毕后删除。

基线: HEAD `bce2ee5` (branch `main`) · 勘察日期 2026-09-12 · 全文数字均为实测

---

## 目录

1. [背景与目标](#一背景与目标)
2. [现状基线](#二现状基线)
3. [决策记录](#三决策记录)
4. [D2 分析结论：7驱动/5模块 与注册表的对立](#四d2-分析结论7驱动5模块-与注册表的对立)
5. [目标结构](#五目标结构)
6. [执行阶段](#六执行阶段)
7. [已知陷阱清单](#七已知陷阱清单)
8. [必须保留的约束](#八必须保留的约束)
9. [不做的事](#九不做的事)
10. [回滚方案](#十回滚方案)

---

## 一、背景与目标

### 1.1 四个痛点与它们的共同根因

| 痛点 | 根因（已核验） |
|---|---|
| 设计与代码该分开 | 边界客观存在（Unity `asmdef references: []`、`code/sim/` 零读 `data/`），但**无一处文档声明它**。反向污染点只有 `code/unity/Assets/Scripts/DemoSolver.cs:30-44` 手抄 `CalibrationConfig` 常量 |
| 文档结构没反映真实设计 | **六维是标签体系，却被当成分区体系用**。23 个文件带 `维度: X` 标签、4 个是双维度。后果：`design/presentation/` 只有 1 个文件（425 行 / 2026-08-09），而 20 天内全部呈现工作（Unity 沙盘 / ActionLab / 玫瑰实验 / 3D 可视化）落在 `code/unity/` 与 `design/presentation/visualization-3d/`；`design/pipeline/` 唯一内容自身标 ⚠️ 已废弃 |
| 仓库太脏太大找不到东西 | `.scratch/` 长成**第二文档层**：314 个 md / 45,076 行 = 全仓受控 md 行数 **47.4%**，被 **94 个仓内文件**引用（含 18 个 `code/src/` 文件约 90 处 XML 注释）。同时 `.git` 385M 从未 gc |
| 流程仪式太重 | `CLAUDE.md` 87 条规则中硬约束仅 27 条（31%），流程纪律 29 条（33%）、格式 31 条（36%）。**且仪式未防住 5 个真实正确性断裂**（见 §3 D2 与 §6 Phase 1） |

四者同链：`.scratch/` 膨胀 → 文档结构失真 → 六维框架承担不该承担的职责 → 仪式膨胀来管理混乱。

### 1.2 完成定义

- [ ] 设计与代码的边界有**单一文档声明**，且无反向污染点
- [ ] 活跃设计文档死链率 **0%**（当前 16.0%）
- [ ] `.scratch/` 不再被任何活跃文档当作正式文档位置
- [ ] 5 个正确性断裂全部修复，`code/tools/validate_*.py` 全部退出码 0
- [ ] `CLAUDE.md` 不存在；约束以厂商中立形式存于 `CONTRIBUTING.md` 与 `design/CONVENTIONS.md`
- [ ] 所有路径为英文；目录结构与六维标签**解耦**
- [ ] `git gc` 后 `.git` 体积显著下降（当前 385M / 6590 松散对象 / `size-pack: 0`）

---

## 二、现状基线

| 度量 | 值 |
|---|---|
| 受控文件 / 受控体积 | 1279 / 167 MB |
| 工作区体积（不含 `.git`） | **4.4 GB**（未受控占 96.2%） |
| `.git` | **385 MB**（6590 松散对象，从未 gc） |
| 受控 `.md` | 554 文件 / 95,177 行 |
| 其中 `.scratch/` | 314 文件 / 45,076 行（47.4%） |
| 设计正典（六目录） | 90 文件 / 19,181 行（20.2%） |
| 跨目录路径引用 | 2619 处 / 653 个 md 参与 |
| 活跃设计文档死链 | 142 / 890 = **16.0%** |
| GitHub issue | 122（106 关闭 / 16 开放），89 个带 `grilling` 标签 |
| 提交历史 | 616 commits，184 条（30%）提交信息含 grilling |
| `term_registry.json` | 311 条（`_metadata` 写 310，`data/README.md:54` 写 134） |
| `design/decisions/` | 4519 行 / 93 个 H2 / 502 个 H3 |
| `CLAUDE.md` | 379 行 / 13,301 字符 / 87 条规则 |
| 未推送 | `main` 领先 `origin/main` **6 个提交**（远端 `a48b3b8`） |

**未受控 4.2G 明细**：`data/sim_results/` 2.6G（1804 JSON，可再生）· `design/presentation/visualization-3d/blender_assets/` 743M（.obj/.blend/.glb，部分可重建）· `data/connectivity/` 406M（abagen 可重下）· `.nuget-pkgs/` 461M。

**`.git` 385M 成因**：历史中已删除但未回收的巨型 blob —— `治疗中心建模/svg/page.svg` 34.3MB、`CAD参考图/01-心脏病医院.svg` 33.7MB、`_废弃-旧AI项目/hospital_phase2.blend` 32.9MB + `.blend1` 31.4MB。已用 `git cat-file -e HEAD:<path>` 逐个确认**均不在 HEAD**；HEAD 最大受控文件仅 8.4MB。

---

## 三、决策记录

| ID | 决策 | 来源 |
|---|---|---|
| **D1** | **`CLAUDE.md` 整体删除**——不绑定固定 AI 厂商。约束改以厂商中立形式保留 | 用户 |
| **D2** | 7驱动/5模块/态度/CPM 的对立 → 用户要求先分析。**结论见 §四** | 用户指示分析 |
| **D3** | **全部改英文路径** | 用户 |
| **D4** | `.agents/skills/` 40 个 skill **全部保留** | 用户 |
| **D5** | `design/decisions/` **拆成目录** | 用户 |
| **D6** | 先产出本计划文档，确认后执行 | 用户 |
| **D7** | `design/conventions/agents/issue-tracker.md` 与 `domain.md` 的**死规范保留原样**，不改写不删除 | 用户裁定 |
| **D8** | **意志力以正典为准 → 标为 deprecated**。需改 `term_registry.json` 的 `意志力` 状态，并作废 CLAUDE.md 的「意志力 ≠ SAN」条款 | 用户裁定 |
| **D9** | **PAD 区分成立**：作为技能定位空间已废弃（已迁 MNI 解剖坐标）、作为情绪表示仍活跃。需修正 `脑功能层级模型.md:9` 措辞 | 用户裁定 |
| **D10** | **删除 `code/src/YouAreNotTheFish.Core.Unity/` 草稿**（从未构建成功，Q6b 定案时重建） | 用户裁定 |
| **D11** | `.scratch/` 纯存档部分**整体移出仓库**（承重部分先迁入 `design/spec/`） | 用户裁定 |
| — | **单仓**，不拆设计仓/代码仓 | 用户（前轮） |
| — | grilling 存量**归档保留、不再执行流程** | 用户（前轮） |
| — | 先**备份仓库**，再在分支上执行 | 用户（本轮指令） |

### 3.1 已完成的备份（2026-09-12）

| 项 | 位置 | 体积 |
|---|---|---|
| 完整 git bundle（全部 refs） | `.refactor-backup/game-pre-refactor.bundle` | 160 MB |
| 工作区快照（排除 `data/sim_results/`、`.nuget-pkgs/`、`__pycache__/`） | `.refactor-backup/tree-pre-refactor/` | 1.4 GB |
| 远端推送 | `origin/main` `a48b3b8..bce2ee5` | — |

> **限制说明**：`/tmp` 是 tmpfs（3.8G，重启即失），`/home/dog` 不在可写工作区内，故备份只能落在仓库内部（已加入 `.gitignore`）。**建议你另做一次外部备份**（另一块盘或云端），覆盖 `data/sim_results/` 之外的全部 1.4 GB——本次备份防的是重构误操作，不防磁盘故障。

> **D1 的连带影响**：本计划写入 `CLAUDE.md` 的「只增不删」自指铁律要求删规则前获明确同意——用户已明确授权删除整个文件，该铁律随文件一并终止。`CONTRIBUTING.md` 同样需要重写：其现行内容（76 行）通篇是「人类 vs AI 分工」「Grilling Issue 工作流」，与 D1 冲突。

---

## 四、D2 分析结论：7驱动/5模块 与注册表的对立

### 4.1 冲突规模：CLAUDE.md 术语表 9 条逐条核验

| 术语 | `CLAUDE.md` 立场 | `term_registry.json` | 正典 `脑功能层级模型.md` | 判定 |
|---|---|---|---|---|
| 态度 | 强制：「认知+情绪+行为 的组合结算结果」 | **deprecated**（2026-07-26） | L9 列入已废弃 | ❌ **CLAUDE.md 孤例** |
| 7 驱动 | 强制：「行为型技能必须归属一个驱动」 | **deprecated** | L9 列入已废弃 | ❌ **CLAUDE.md 孤例** |
| 5 模块 | 强制：「认知型技能必须归属一个模块」 | **deprecated** | L9 列入已废弃 | ❌ **CLAUDE.md 孤例** |
| CPM | 强制 | **deprecated** | L9 列入已废弃 | ❌ **CLAUDE.md 孤例** |
| PAD | 强制：用 PAD 不用离散标签 | **active** | **L9 列入已废弃** | ⚠️ **正典孤例**（2:1） |
| 意志力 | 强制：「意志力 ≠ SAN」 | **active** | **L567：「意志力(WP)已废弃，替换为认知负荷模型」** | ⚠️ **正典孤例**（2:1） |
| SAN | 精神护盾，不是血条 | active | — | ✅ 一致 |
| 意识外显效应 | active（原名观察者效应） | active | — | ✅ 一致 |
| 随身镜子 | active | active | — | ✅ 一致 |

**注册表在这 4 条上完全正确，CLAUDE.md 是唯一孤例**——因为注册表这几条的 `source` 字段写的正是 `CLAUDE.md §核心术语表`：注册表从 CLAUDE.md 建立，设计变更（2026-07-26 行为系统废弃）时更新了注册表，**没回写 CLAUDE.md**。

### 4.2 用户直觉中「部分对」的那部分——结构性直觉存活了

CLAUDE.md 的错误是**具体成员**，不是**结构**。旧结构与现结构的同构关系：

| 层面 | 旧（CLAUDE.md） | 现（注册表 active） |
|---|---|---|
| 行为侧分类 | **7 驱动**：反射/惩罚/奖励/道德/文化/价值/照护 | **8 行为角色**：`attack_physical` `attack_mental` `defend` `flee` `approach` `perceive` `support` `disrupt` |
| 认知侧分类 | **5 模块**：知觉与注意/记忆/知识表征/表象与语言/推理与决策 | **14 网络**（Kroell et al. 2024）：AM / CogAC / eMDN / EmoSF / EMP / ER / eSAD / MNS / MOT / Rew / … |
| 中间层 | 无 | **12 gameplay_domain**（Grilling #72 P1a D3） |
| 组合方式 | 硬归属：「必须归属一个」 | **加权打分取最大**：`role_scores(edge)[r] = Σ_domain w(domain,r) × [domain ∈ edge.gameplay_labels]`，`primary_role = argmax_r` |
| 空间 | 7 × 5 = 35 → 90 种态度 | 8 × 14 = 112 候选（技能从 60 候选池涌现） |

**结论**：CLAUDE.md 的**结构直觉（行为侧小集合 × 认知侧小集合的笛卡尔积）完全正确且被延续并深化**——现结构多了 12 domain 中间层，且从硬归属升级为权重矩阵。而 CLAUDE.md 那一列的**「禁止混淆」警告至今有效**（「情绪用 PAD 不用离散标签」「不要说态度卡」「SAN 不是血条」）。

### 4.3 处置

1. **以注册表为准**。CLAUDE.md:17,18,32 的 7驱动/5模块 强制条款作废，随 D1 随文件删除。
2. **保留警告语义**，以厂商中立形式写入 `design/CONVENTIONS.md`：
   - 技能分类当前口径 = `主导网络（14 网络）× 主导角色（8 行为角色）`，非 7驱动/5模块
   - 情绪表示用 PAD 向量，不用离散标签
   - 「态度」不是实体，不要说「态度卡」
   - SAN ≠ 血条；SAN 与 HP 可互相转化但有上限
3. **修 2 处新发现的三方矛盾**（勘察副产物，优先级高）：
   - **PAD**：`design/rules/skill-tree/脑功能层级模型.md:9` 把 PAD 列入已废弃，但注册表 active。真相需区分——`3D可视化/脑图谱数据管线.md:3,20-23,142-144` 记载技能坐标**已从 PAD 概念空间迁移至 MNI 解剖坐标**，故 PAD 在**技能定位**上退役、在**情绪表示**上仍活跃。正典 L9 的措辞需改为「PAD 作为技能定位空间已废弃」。
   - **意志力**：`脑功能层级模型.md:567` 声明已废弃并替换为认知负荷模型，但注册表把 `意志力` 标为 active。**需你裁定后同步两侧。**
4. **`data/README.md:54` 的「134 条」与 `_metadata.total_terms: 310` 均改为 311**（实测 `len(terms) == 311`）。

---

## 五、目标结构

### 5.1 骨架

```
/home/dog/game/
├── README.md                    ← 保留（53 行，导航表质量良好）
├── CONTRIBUTING.md              ← 重写：去掉 AI 厂商绑定与 grilling 流程
├── REFACTOR-PLAN.md             ← 本文件，执行完删除
│
├── design/                      【设计文档 = primary artifact】
│   ├── CONVENTIONS.md           ← 新建：厂商中立的文档规约（承接 CLAUDE.md 抢救内容）
│   ├── rules/                   ← design/rules/
│   │   └── skill-tree/          ← design/rules/skill-tree/
│   ├── entities/                ← design/entities/
│   ├── space/                   ← design/space/
│   ├── events/                  ← design/events/
│   ├── presentation/            ← design/presentation/ + code/unity/ 与 3D可视化/ 的呈现文档迁入
│   ├── pipeline/                ← design/pipeline/
│   ├── framework/               ← design/framework/six-dimensions.md + design/framework/dimensions/
│   ├── decisions/               ← design/decisions/ 拆分后（含 README 索引）
│   ├── spec/                    ← 新建：从 .scratch/ 迁入的承重规格
│   └── archive/
│       ├── trash/               ← design/archive/trash/
│       ├── deprecated/          ← reference/deprecated/
│       └── grilling/            ← grilling 方法论 4 份 + issue 导出
│
├── reference/                   ← reference/（文献 / 书籍 / 灵感收件箱）
│
├── code/                        【代码 = 验证与实现工具】
│   ├── code/src/                     ← code/src/（.NET 8）
│   ├── code/unity/                   ← code/unity/
│   ├── code/sim/                     ← code/sim/
│   └── code/tools/                   ← code/tools/
│
├── data/                        【数据契约】
│   ├── canon/                   ← 引擎消费的 8 + 支持 5 个 JSON
│   ├── archive/                 ← 态度/卡牌/旧链路 遗留 JSON
│   └── generated/               ← sim_results（gitignored）
│
└── process/                     ← .scratch/ 收缩为纯存档（或整体移出仓库）
```

### 5.2 旧 → 新 路径映射

| 旧路径 | 新路径 | 受控文件数 |
|---|---|---|
| `design/rules/` | `design/rules/` | 39 |
| `design/entities/` | `design/entities/` | 39 |
| `design/space/` | `design/space/` | 99 |
| `design/events/` | `design/events/` | 6 |
| `design/presentation/` | `design/presentation/` | 1 |
| `design/pipeline/` | `design/pipeline/` | 1 |
| `design/framework/six-dimensions.md` | `design/framework/six-dimensions.md` | 1 |
| `design/framework/dimensions/` | `design/framework/dimensions/` | 6 |
| `design/decisions/` | `design/decisions/`（拆分 + README） | 1 → ~4 |
| `design/framework/grilling-质量保障体系-v2*.md` | `design/archive/grilling/methodology/` | 4 |
| `design/conventions/agents/` | `code/tools/agents/` | 5 |
| `reference/` | `reference/` | 220 |
| `reference/deprecated/` | `design/archive/deprecated/` | 11 |
| `design/archive/trash/` | `design/archive/trash/` | 27 |
| `.scratch/` | `process/`（仅存档部分） | 341 → ~100 |
| `code/src/` | `code/src/` | 96 |
| `code/unity/` | `code/unity/` | 45 |
| `code/sim/` | `code/sim/` | 17 |
| `code/tools/` | `code/tools/` | 51 |
| `data/` | `data/canon/` + `data/archive/` + `data/generated/` | 166 |
| `练习/` | **删除**（空目录、未跟踪、零引用） | 0 |

### 5.3 关键结构决策

**① 六维降级为标签，与目录解耦**
`design/framework/six-dimensions.md` 只维护「维度 → 文档列表」映射表；不再要求目录与维度一致。依据：23 个文件带 `维度: X` 标签、4 个双维度、`3D可视化设计规范.md:3` 声明「呈现」却住 `design/rules/` 下。

**② `design/presentation/` 承接错位的呈现文档**
迁入 `code/呈现/动作库规格.md`、`地块数据-Konza草原.md`、`玫瑰株丛密度.md` + `design/rules/skill-tree/3d-visualization/`（3 份 / 831 行）。理由：这 20 天的呈现工作量大且活跃，却是 `design/presentation/` 维度的真实内容。

**③ `design/spec/` 承接 `.scratch/` 的承重部分**
它们**不是过程物**：

| 迁出对象 | 现有消费方 |
|---|---|
| `.scratch/csharp-*/design/spec.md` × 10 | ~90 处 `code/src/` XML 注释以 `spec@v1.1` 引用 |
| `grilling-89-npc-material/{患者生态索引,多样性记账表}.md`、`ref/books/社会演化矩阵.md` | `rules/skill-tree/素材起草规范.md:9-11` 要求起草前必读；共 10 处 |
| `grilling-88/*-pilot.md` × 26 | `entities/疾病目录/` 下 22 个文件的「关联」行；共 32 处 |
| `grilling-116/批次配额表-P1补充.md`、`grilling-90/数学建模-记忆过程.md` | 正典引用，共 18 处 |

**④ `design/decisions/` 拆分方式**
按轮次切分，**每个 H2 标题原样保留**（34 个活跃文件引用它、37 处是链接形式）：

```
design/decisions/
├── README.md                  总索引（话题 → 文件 → 锚点）
├── 01-numbered-6-41.md        #6  ~ #41
├── 02-numbered-86-126.md      #86 ~ #126
├── 03-topic-2026-07.md        话题命名轮次（2026-07-28 ~ 07-31）
├── 04-topic-2026-08.md        话题命名轮次（2026-08）
└── 05-archive-rejected.md     ⚠️ 被否决的方向（原文 L12 起）
```
注意：93 个 H2 中 65 个无编号（仅话题命名），拆分必须保持每段可寻址，不能只按日期切。

**⑤ `data/` 三层**
现状四类混在一层（正典 / 参考 / 历史备份 / 2.6G 生成物）是计数漂移的根因：

| 层 | 内容 |
|---|---|
| `data/canon/` | 引擎消费 8 个（`brain_regions` `tripartite_model` `W_sensory` `situation_primitives` `signal_types` `alpha_patterns` `env_tones` `moonlight_landing`）+ 支持 5 个（`term_registry` `pathology_edges` `region_name_map` `privileged_pathways` `link_contexts_tripartite`） |
| `data/archive/` | `attitudes` `drives` `emotions` `emotion_cards` `cognition_cards` `behavior_cards` `link_registry` `link_contexts` `personality_tag_links` `link_modulation_ceiling` `skill_coords` + 6 个孤儿 JSON |
| `data/generated/` | `sim_results/`（1804 JSON），gitignored |

---

## 六、执行阶段

每阶段独立可交付、可回滚、可单独验收。

### 执行进度总表

| 阶段 | 状态 | 分支/提交 |
|---|---|---|
| Phase 0 — 冻结与止血 | ✅ **完成** | `6832a78` |
| Phase 1 — 正确性修复（12 项） | ✅ **完成** | `dd5516a` `61b2d69` `77750aa` |
| Phase 2 — 内容归位 | ✅ **完成**（2.2–2.4） | `688629c` `7ecd2bb` `aff588a` |
| Phase 3 — 英文改名 | ⬜ 未开始 | — |
| Phase 4 — 约束拆除 | ⬜ 未开始 | — |
| Phase 5 — 终验与文档化 | ⬜ 未开始 | — |

### ⚠️ 勘误：Phase 1 的「死链 142 → 0」读数不可信

**如实记录**：Phase 1 报告的死链清零基于 `validate_cross_refs.resolve_target` 的一个缺陷——相对路径解析失败时，它会用 `ROOT.rglob(文件名)` 找**第一个同名文件**充当候选，**深层相对路径错误因此被判为通过**。

Phase 2 移除该回退后严格重扫：**真实失效率为 424 处**。已在 Phase 2 修正：

| 类别 | 处数 |
|---|---|
| 按唯一同名定位 + 相对路径重算 | 313 |
| 搬迁造成的深度漂移（累计） | 500+ |
| 链接路径含空格（`NPC AI 行为模型.md`）——此前从未被任何正则匹配到 | 30 |
| 目录链接指向 README、同目录同名消歧 | 11 |
| 补搬 csharp 实现记录子树（design/impl + 9 个 map.md，仅被 .scratch 内部引用而未搬出） | 58 文件 |

**顺带修出的真实数据错误**（原被回退掩盖）：`design/entities/diseases/躯体症状障碍.md` 的 `父类` 字段写成自身「躯体症状障碍」，应为「躯体症状」——回退靠 rglob 匹配到文件自身而"通过"。全量核验 26 个疾病文件，仅此 1 处。

**教训**：校验器的容错回退必须报告为 WARN 而非 PASS，否则会把真实错误变成绿灯。本次直接删除该回退并在代码注释中记录原因。

### Phase 2 实际结果

| 项 | 结果 |
|---|---|
| 新建 `design/spec/` | 49 文件（引擎 13 / 素材 34 / 数据源 3）——被代码或正典消费的承重内容 |
| 新建 `design/archive/grilling/` | 51+ 目录——各轮决策记录、任务计划、工作稿、实现记录 |
| `.scratch/` 受控文件 | 341 → **0**（移出版本控制；本地 510 文件 / 47M 保留） |
| `.scratch/` 引用 | 310 处重写；仍指向存在目标的引用 **0** |
| `design/presentation/` | 1 文件 → 5 条目（含 `3D可视化/` 整目录搬迁） |
| `design/framework/` | 混杂 17 文件 → 写作与引用规范 / 决策树/ / 设计框架-六维状态 / 维度/ / agents/ |
| `design/framework/决策树.md` | 4519 行单文件 → `design/decisions/` 6 片段 + README（**93 个 H2 逐一比对完全一致**） |
| 严格链接检查（无回退） | 2522 链接 / 失效 56（19 模板占位符 + 37 归档历史引用）；**活跃文档 0** |
| 9 个校验器 | 全部 exit=0（诚实版） |
| `dotnet test` | 353 passed / 0 failed |


分支：`refactor/repo-structure`（从 `main` @ `bce2ee5` 开出）· 备份见 §3.1

### Phase 0/1 实际结果

| 指标 | 重构前 | 现在 |
|---|---|---|
| `.git` 体积 | 385 MB（6590 松散对象，`size-pack: 0`） | **160 MB**（1 pack，158.85 MiB） |
| `validate_cross_refs` 死链 | 142 / 890 = 16.0 % | **0** |
| 段引用警告 | 2 | **0** |
| `validate_trash_isolation` | 10 处问题 | **全部通过** |
| `validate_params` | 37 checks / 26 passed / **7 failed** | 36 checks / 32 passed / **0 failed** |
| `validate_spatial` | 4 checks / 3 passed / **1 failed** | 4 checks / **4 passed** |
| 9 个校验器退出码 | 4 个非 0 | **全部 0** |
| `dotnet test` | — | **353 passed / 0 failed** |
| NPC 杂兵 HP | 代码 15 ↔ 权威表 20-30 | **25**（对齐权威表中值） |
| `W_sensory` 模态 | 数据 8 ↔ 注释/文档 6 | **8**（14 处同步） |
| `term_registry` 计数 | 实测 311 ↔ 声称 310 | **311 / 288 / 23 三方吻合** |
| `reference/` PDF 重复 | 8 组 | **0**（52 → 44 个） |
| `design/archive/trash/` 活跃引用 | 26 处 | **0** |

### Phase 0 — 冻结与止血（半天）

| # | 动作 | 依据 |
|---|---|---|
| 0.1 | `git push` 6 个未推送提交 | 本地领先 `origin/main`；先消除"只有本地有"的风险 |
| 0.2 | 建分支 `refactor/repo-structure` | 大改动先开分支 |
| 0.3 | 完整备份：`git bundle create ../game-backup.bundle --all` + `rsync` 未受控的 4.2G 到外部盘 | `blender_assets/` 743M 与 `data/hospital_ref/` 29M 无完整重建脚本 |
| 0.4 | `git gc --aggressive --prune=now` | `.git` 385M / 6590 松散对象 / `size-pack: 0` |
| 0.5 | ~~删垃圾受控文件：4 个 `PDF_page_*.png~RF*.TMP`~~ → **⚠️ 已修正：这 4 个文件不是垃圾**，而是 `raw/参考图/` 序列中第 26-29 页的**唯一副本**（正式文件名缺失，`.TMP` 是 Windows 提取工具未完成改名的残留名）。已 `git mv` 改名为 `PDF_page_26..29.png`，序列修复为 01-34 完整 | `design/space/treatment-center-modeling/references/raw/reference-images/` |
| 0.5b | 删除 `data/brain_regions_backup_20260712_—.json`（文件名含乱码破折号，零文档引用，已 grep 确认唯一"引用者"是本计划文档） | — |
| 0.5c | 删除空目录 `练习/`（0 文件、未跟踪、零引用） | — |
| 0.6 | 删除 `reference/literature/` 的 7 组 md5 重复 PDF + 1 组跨目录重复 | 省约 15 MB |
| 0.7 | 删除 `reference/session-archive/` 的 26 个 `raw.*_tmp.html`（~7 MB，已 ignore） | 抓取中间产物 |

**验收**：`git status` 干净；`.git` 体积下降；`git log` 完整。

### Phase 1 — 正确性修复（1 天）· 与结构无关，优先级最高

| # | 动作 | 位置 |
|---|---|---|
| 1.1 | `NpcHp = 15f` → 25（对齐 §4.1 权威表 20-30 中值），同步修正注释 | `code/src/YouAreNotTheFish.Core/Engine/CalibrationConfig.cs:49-50` |
| 1.2 | 69×6 → 69×8 文档与注释同步（T6b，已挂账） | `WsensoryMatrix.cs:6,13,17`、`GameDataLoader.cs:33`、`data/README.md:43,72`、`引擎数据关系规格.md:30`、`GameDataLoaderTests.cs:343`、`design/decisions/:2611` |
| 1.3 | 修 ≥21 处垃圾桶隔离违规 | 见下方明细 |
| 1.4 | 修 142 处死链（16.0%）——先批量修 `../` 层级 bug | 见 §7 |
| 1.5 | `data/README.md` 计数修正（134→311、引擎消费 5→8 文件） | `data/README.md:37,54` |
| 1.6 | `term_registry._metadata.total_terms` 310 → 311 | `data/term_registry.json` |
| 1.7 | 修 2 个断裂 sim 脚本（import 目标已进垃圾桶） | `code/sim/extract_formulas.py:10`、`code/sim/test_evolved_cog.py:72` |
| 1.8 | 修 `validate_spatial.py:77` 过时断言（`>=6` 设计节点，实际 0，因 #25 已删） | `code/tools/validate_spatial.py:77` |
| 1.9 | 修 `review-plan/SKILL.md:280` 链接层级（`../../` → `../../../`） | `.claude/skills/review-plan/SKILL.md:280` |
| 1.10 | 修 `code/unity/README.md:19` Unity 版本号（6000.0.83f1 → 6000.5.2f1） | `code/unity/README.md` |
| 1.11 | 裁定 §4.3 的 PAD / 意志力 三方矛盾并同步两侧 | `脑功能层级模型.md:9,567` + `term_registry.json` |
| 1.12 | 7 项 `validate_params` C1 失败：均为提取器把不同语境当同名参数的**假阳性**，修提取器或将 `L`/`k`/`ΔI`/`β(t)`/`β₀`/`ε`/`—` 加入例外清单 | `code/tools/validate_params.py` |

**1.3 垃圾桶违规明细（≥21 处）**

| 引用者 | 处数 | 处置 |
|---|---|---|
| `data/term_registry.json` L1178,1183-1185,1196,1201-1202,1216,1221,1231,1236-1237,1247,1252,1265,1270,1280,1285,4185 | **19** | 把月光场 v2 参数转正至 `design/archive/deprecated/moonlight-field/`（与态度/情绪/行为同构），或把 `source` 改为决策树段引用 |
| `entities/敌人与事件.md:445` | 1 | 活跃参数速查表内，改为纯文本注记 |
| `reference/灵感收件箱.md:73,664` | 2 | 改为「⚠️ 月光场 v2 已废弃（#38），见决策树 #38」 |

> **注意**：`code/tools/validate_trash_isolation.py` 只报了 2 处，因为其 `FILES_IN_TRASH`（L22-30）硬编码 7 个 L0-L6 文件、`EXEMPT_DIRS` 豁免 `.scratch/`、且只扫 `.md`（L113,128-134）——**它检查不了 `data/`、`reference/`**。Phase 1 应同时扩展该脚本的覆盖。

**验收**：`code/tools/validate_*.py` 全部退出码 0；死链扫描 0 失效。

### Phase 2 — 内容归位（2-3 天）· 仍用中文路径

| # | 动作 | 依据 |
|---|---|---|
| 2.1 | 新建 `design/spec/`，从 `.scratch/` 迁入 §5.3③ 的四类承重内容 | ~90 处 src 注释 + 60 处文档引用 |
| 2.2 | 呈现在文档归位到 `design/presentation/`（`code/unity/*.md` × 3 + `3D可视化/` × 3） | 呈现维度真实内容错位 |
| 2.3 | `design/framework/` 三分：设计留 `design/framework/`；流程方法论（4 份 1171 行 + `math-language-writing.md`）→ `流程/`；agent 工作流（4 份）→ `.agents/docs/` | 8 个文件与游戏设计无关却占 `design/framework/` |
| 2.4 | `design/decisions/` 拆分为目录（含 README 索引） | 4519 行 / 93 H2 |
| 2.5 | 合并三份重复的六维分类（`设计框架-六维状态.md:24-32` + `design/framework/dimensions/*.md` 头部 + `design/README.md:16`） | 三份重复维护、已不同步 |
| 2.6 | 重写 `CLAUDE.md` 文件地图 → 迁入 `design/CONVENTIONS.md` | **17 项失配**（见下） |
| 2.7 | `.scratch/` 收缩：18 个零外部引用目录归档出仓；`设计框架-六维状态.md:283,331,339` 与 `design/README.md:174-175` 的「位置」列改指 `design/spec/` | `README.md:35` 称其「过程物不入库」，实际被当正式位置 |
| 2.8 | 合并 `design/space/treatment-center-modeling/` 的 8 个占位 README（336 行，6 个仅 9-17 行）为 1 个 | — |

**2.6 文件地图 17 项失配明细**

| 类型 | 项 |
|---|---|
| 标"待建设"但已有内容 | `design/presentation/`（有 425 行）、`design/pipeline/`（有 397 行，自身已标废弃） |
| 描述与现状不符 | `操作层/` 只列 L0-L5（实际 L6 已进垃圾桶）、`激活系统/` 描述存在但**目录完全为空**、`技能树系统/` 列 6 项（实际 17 项） |
| 存在但未列 | `design/rules/时空结构数学框架.md`、`design/entities/` 4 项、`design/events/` 4 项、`reference/` 8 项、`design/decisions/`、`design/archive/trash/`、`.scratch/`、`code/src/`、`code/unity/`、`README.md`、`CONTRIBUTING.md` |
| 路径写错（Glob 恒空） | `行为系统/待解决问题.md`、`情绪系统/*.md`、`态度系统/*.md` —— 实际均在 `reference/deprecated/` 下 |

**验收**：`code/tools/validate_cross_refs.py` 0 死链；`设计框架-六维状态.md` 的「位置」列无 `.scratch/` 引用。

### Phase 3 — 英文改名（1-2 天）· 一次性机械完成

**必须最后做、且只做一次**——在 Phase 1-2 修完死链后再改名，否则在 16% 死链基线上搬迁会翻倍。

| # | 动作 |
|---|---|
| 3.1 | 写一次性迁移脚本 `code/tools/migrate_paths.py`：按 §5.2 映射 `git mv` 全部目录 |
| 3.2 | 同一脚本批量改写引用：2619 处 md 引用 + `code/tools/` 内 90 处硬编码路径 + `code/src/` 约 90 处 XML 注释 + 12 个文件名含中文的 md 内部链接 |
| 3.3 | 手工修 4 处**无法正则化**的路径基准（见 §7.1） |
| 3.4 | 改写 `code/tools/md_utils.py` 的 `SCAN_ROOTS` / `EXCLUDE_DIRS` / `EXCLUDE_FILE_KEYWORDS` |
| 3.5 | 逐目录验证后分组提交（按主题分批，不混 commit） |

**验收**：`code/tools/validate_cross_refs.py` 0 死链；`dotnet test` 通过；`python3 code/tools/run_all_checks.py` 全绿。

### Phase 4 — 约束拆除（1 天）

| # | 动作 | 依据 |
|---|---|---|
| 4.1 | 删除 `CLAUDE.md` | D1 |
| 4.2 | 重写 `CONTRIBUTING.md`：去掉 AI 厂商绑定与 grilling issue 工作流，保留 Git 工作流与提交规范 | 现行 76 行与其冲突 |
| 4.3 | 新建 `design/CONVENTIONS.md`：承接 §八 抢救的约束（厂商中立） | CLAUDE.md 里真有效的内容不能丢 |
| 4.4 | `.agents/skills/grilling/SKILL.md`(302 行) 与其方法论文档移入 `design/archive/grilling/`，降级为按需工具 | grilling 归档不执行 |
| 4.5 | 122 个 issue 导出为 md 存 `design/archive/grilling/issues/` | — |
| 4.6 | `data/term_registry.json` 从「准入门禁」降为「术语参考」：保留 `status` 字段，不再要求 Step 3.0 查询 | `_description` 现写明是「Grilling §3.0 定义基线声明的唯一数据源」 |
| 4.7 | 清理 **11 个调用 `/grilling` 的上游 skill** 中的调用点：`triage` `wayfinder` `loop-me` `grill-me` `grill-with-docs` `batch-grill-me` `ask-matt` `writing-fragments` `writing-shape` `improve-codebase-architecture` + `grilling` 本体 | D4 保留 skill 文件，但断掉 grilling 调用 |
| 4.8 | 改 `code/tools/sync_issues.py` 的 `TYPE_LABELS` 移除 `"grilling"` | — |
| 4.9 | 改 `.github/ISSUE_TEMPLATE/grilling.md` 与 `design/framework/dimensions/管线.md`、`design/framework/dimensions/规则.md` 的索引标题（去掉 grilling 措辞） | — |
| 4.10 | 修正 `design/conventions/agents/issue-tracker.md` 与 `domain.md` 的**死规范**：issue-tracker 描述的 `.scratch/<slug>/spec.md` + `issues/NN-slug.md` 实测**使用 0 次**；domain.md 要求的 `CONTEXT.md` + `design/framework/adr/` **不存在却被引用 10 次** | 决策点 D7 |

**验收**：全仓 `grep -ri grilling` 仅命中 `design/archive/grilling/`；无文件引用 `CLAUDE.md`。

### Phase 5 — 终验与文档化（半天）

| # | 动作 |
|---|---|
| 5.1 | `code/tools/validate_*.py` 全部退出码 0 |
| 5.2 | 死链扫描 0 失效（活跃设计文档） |
| 5.3 | `git gc` 后报告 `.git` 体积对比 |
| 5.4 | 重写 `README.md` 导航表与 `design/README.md` 使其匹配新结构 |
| 5.5 | **新增根目录 `ARCHITECTURE.md`**：明确声明设计与代码的边界（解决痛点①） |
| 5.6 | 删除 `REFACTOR-PLAN.md`；合并 `refactor/repo-structure` 到 `main` |

---

## 七、已知陷阱清单

### 7.1 路径基准（改名必断，需手工修）

| 位置 | 内容 | 修法 |
|---|---|---|
| `code/tools/md_utils.py:14` | `ROOT = Path(__file__).parent.parent` | 移到 `code/tools/` 后 → 需 `parent.parent.parent`，或改为向上查找 `.git` 的 `find_repo_root()` |
| `code/tools/md_utils.py:21` | `SCAN_ROOTS = ["规则","实体","空间","事件","呈现","管线","docs","参考"]` | 改为 `["design","reference"]` |
| `code/tools/md_utils.py:24-28` | `EXCLUDE_DIRS` 含 `"垃圾桶"`,`"reference/废弃"`,`"reference/书籍"` | 同步改名 |
| `code/tools/md_utils.py:31` | `EXCLUDE_FILE_KEYWORDS` 含 `"已废弃"`,`"决策树.md"` | 同步改名 |
| `code/tools/validate_cross_refs.py:99` | 硬编码 `design/entities/diseases/_parent-classes/{parent_name}.md` | 改为 `design/entities/diseases/_parent-classes/` |
| `code/src/…Tests/Data/GameDataLoaderTests.cs:9` | `AppContext.BaseDirectory` 上溯 **5 层** 到 `data` | `code/src/` → `code/src/` 后需 **6 层**；并删除 L20 的 `/home/dog/game/data/...` 绝对路径 fallback |
| `code/unity/Assets/Scripts/DemoSolver.cs:30-44` | 手抄 `CalibrationConfig` 常量 | Phase 1 改 `NpcHp` 时同步；建议标注为 demo 占位或直接删除 |

### 7.2 其他隐式耦合

| 耦合 | 位置 | 风险 |
|---|---|---|
| 生成物回写设计目录 | `sim_consciousness_v7_estimator_validity.py:1033` 写 `<outdir>/data/sim_results` | 研究脚本污染 `data/`（2.6G 来源）。改为 `--outdir` 默认落仓库外 |
| `code/sim/` 扁平 import | `sim_consciousness_v7_components.py:33,36` 等 | `code/sim/` 不能改成包结构，除非同步改 import |
| Unity 外部资产缺失 | `KiWalkerLabBuilder.cs:19-22`、`ActionCatalog.cs:57` 引用 `Assets/Kevin Iglesias/…`（不在仓库） | PlayMode 16 项中 2 项已因缺 clip 失败；`Assets/` 重组会放大 |
| Unity 工程不完整 | `ProjectSettings/` 仅 1 文件、`.meta` **0 个**、`.unity`/`.prefab` **0 个**、`Assets/Scenes/` 空 | 所有场景靠 Editor 菜单运行时生成；重开工程会重新生成全部 GUID |
| Windows 绝对路径 | `MixamoSetup.cs:16`、`code/tools/unity-cli/uc.sh:5`、`process_hospital_atlas.py:245` | 跨机不可复现 |
| `code/tools/` 硬编码脑区数 | `brain_atlas_to_blender.py` 自述「57 脑区」（现 69） | 工具未随 #25 更新，重跑产出错数据 |
| `run_all_checks.py:81` 有副作用 | 写 `.scratch/.last_check_state.json` | 无法在只读/CI 环境运行 |

### 7.3 不可复现资产（备份优先，对应 Phase 0.3）

`design/presentation/visualization-3d/blender_assets/` 743M 全部被 `.gitignore` 忽略，且**无生成脚本能完整重建当前状态**：

```
brain_skill_tree.glb              187M  ← 构建产物
brain_skill_tree_v1.glb           119M  ← 旧构建产物
brain_skill_tree_v1.blend          97M  ← 旧源文件
brain_skill_tree.blend             21M  ← 当前源文件
brain_skill_tree.blend1            21M  ← Blender 自动备份
brain_skill_tree_backup_20260719   21M  ← 手工备份
all_obj/                          278M  ← 中间网格
```
`code/tools/brain_atlas_to_blender.py` 重建的是脑图谱底图，**不是技能树布局**。这是本次勘察中**唯一的数据丢失风险**。

---

## 八、必须保留的约束

`CLAUDE.md` 删除后，以下内容**不能丢**——它们厂商中立、且被其它机制硬依赖。全部迁入 `design/CONVENTIONS.md`：

| 保留项 | 为什么不能删 |
|---|---|
| **md 文件格式规范**（头部 `# 标题` + `> 摘要`；尾部 `*创建/更新/关联*`；>200 行加目录；`[显示名](相对路径)`；一个文件一个 H1；`## 一、` 中文编号；参数速查表 `\| 参数 \| 符号 \| 默认值 \| 位置 \|`） | 现行 `task-checker` 的检查项**逐条镜像**这套规范，F1/F2 违反是阻断级 |
| **垃圾桶隔离**（活跃文档不得引用 `archive/trash/` 路径或已废弃术语） | `validate_trash_isolation.py` 的实现依据；当前被违反 21 处 |
| **引用即读取**（引用参数/公式/决策/路径前必须先读源文件） | 通用正确性原则，与任何流程无关 |
| **术语注册表**（新术语/定义变更时更新 `data/canon/term_registry.json`） | 原规则明文写「不等 grilling」，本就是去耦规则；且是术语一致性的执行基础 |
| **数学语言书写规范**（模糊量词/无阈值/枚举未受控 → 用符号与区间表达） | 原规则明文「全程生效，无场景豁免」 |
| **禁止事项**（颜色系统 / 离散态度晶体 / 态度当独立卡牌 / 战斗简化为削血 / 凭空添加机制 等 9 条） | 与 grilling 零耦合，是内容正确性的最后防线 |
| **Git 工作流**（小步提交 / 中文提交信息 `类型: 描述` / 大改动开分支 / 危险操作先确认） | 与 grilling 零耦合，14 条 |
| **数值参数必须有来源注释** | 硬约束，可机械核验 |
| **设计与代码边界声明** | 新增，解决痛点① |

**必须迁出后才能归档的**：`design/archive/grilling/methodology/grilling-质量保障体系-v2.md` §四（L251-326）是现行「项目级引用规范」的实际正文——`CLAUDE.md` 的引用格式、参数来源注释、交叉引用格式、决策引用格式四条规则均指向它。**先迁内容，再归档文件**，否则指针断裂。

---

## 九、不做的事

| 不做 | 理由 |
|---|---|
| 不重写 git 历史（`filter-repo` 去掉 385M 历史垃圾） | 需要 `push --force` 重写远端 `github.com/verystrongdog/game.git`，风险高于收益。`git gc` 可回收不可达对象，已删除的巨型 blob 仍在历史但压缩后收益有限 |
| 不删除 `.agents/skills/` 的 40 个 skill | D4 |
| 不删除 `design/archive/` 任何内容 | grilling 归档保留；`reference/deprecated/emotion-system/NRC-VAD-Lexicon.tsv`、`Ratings_Warriner_et_al.csv` 是 PAD 空间的原始数据源 |
| 不拆仓 | 用户已定单仓 |
| 不删除 `design/conventions/agents/` 的 4 份文档 | 保留文件，但修正其与现状不符的规范（Phase 4.10） |
| 不改任何设计内容（公式/参数/机制） | 除 Phase 1 的 5 个正确性修复外，本计划只动结构与引用 |
| 不重构 `code/unity/` 的资产组织 | `.meta` 全缺、场景不入库是既有状态，重组会放大已有 2 项失败测试 |

---

## 十、回滚方案

| 阶段 | 回滚方式 |
|---|---|
| Phase 0 | `git push` 后远端即备份；`git bundle` + `rsync` 双重离线备份 |
| Phase 1-2 | 每阶段独立 commit 组，`git revert` 该组即可 |
| Phase 3（改名） | 迁移脚本同时生成反向映射；`git revert` 单个 commit 可整体撤销；改名前后各打 tag（`pre-rename` / `post-rename`） |
| Phase 4 | `CLAUDE.md`、grilling skill、issue 导出均有归档副本 |
| 全局 | 分支 `refactor/repo-structure` 不合并前 `main` 始终可用 |

**提交粒度**：按主题分批，不混 commit。改名阶段每个顶层目录一个 commit，便于单独 revert。

---

## 附：决策点裁定结果（全部已定）

| ID | 决策点 | 裁定 | 落地动作 |
|---|---|---|---|
| **D2** | 7驱动/5模块/态度/CPM 与注册表对立 | **以注册表为准**，具体成员作废、结构口径与「禁止混淆」警告保留 | §4.3；随 `CLAUDE.md` 删除，警告语义迁入 `design/CONVENTIONS.md` |
| **D7** | `design/conventions/agents/issue-tracker.md` 与 `domain.md` 是死规范 | **保留原样**，不改写不删除 | 取消原 Phase 4.10 |
| **D8** | 意志力 active 还是已废弃 | **以正典为准 → deprecated** | Phase 1.11：改 `term_registry.json` 的 `意志力.status` |
| **D9** | PAD 的「技能定位空间 / 情绪表示」区分 | **区分成立** | Phase 1.11：修正 `脑功能层级模型.md:9` 措辞为「PAD 作为技能定位空间已废弃」 |
| **D10** | `code/src/YouAreNotTheFish.Core.Unity/` 草稿 | **删除** | Phase 0.8 |
| **D11** | `.scratch/` 纯存档部分 | **整体移出仓库** | Phase 2.7（承重内容先迁 `design/spec/`，其余移出） |
| — | 执行方式 | 先备份，再在分支 `refactor/repo-structure` 上执行 | §3.1 已完成 |

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [README](README.md), [CONTRIBUTING](CONTRIBUTING.md)*
