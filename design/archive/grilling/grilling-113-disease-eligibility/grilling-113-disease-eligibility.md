# [Grilling] 疾病资格层 Eligibility(d) 解耦 — 创伤负荷 ≠ 疾病资格

Type: grilling
Status: ✅ 闭合（2026-09-03）
维度: 规则（转化接口 §3.2/§3.3）
前置: #88 转化接口 ✅ / #87 创伤记忆语义 ✅ / #90 记忆内容层 ✅ / #89 素材库（触发来源）
阻塞: ~~顾维扬草稿 BD-II 去留（冻结等待本 issue 定案后回放）~~ → ✅ 已解（回放裁决：BD-II 降 MDD）
创建: 2026-09-03
闭合: 2026-09-03
GitHub: [#113](https://github.com/verystrongdog/game/issues/113)

## 话题

#89 顾维扬草稿外部评审（t6a96e985 + t6a96ecd6，两份评审均归档于 `../../../规格/素材`）暴露的生成器资格层结构问题：**创伤负荷聚合 L_agg(d) 被当作疾病资格**，导致"十次丧失→BD-II""事件负荷→环性障碍""经济剥夺→SUD 幽灵候选"等荒谬输出。

**本轮不审查**（已定案，不重开）：
- 创伤 = 唯一触发路径（决策树 :3980 D1）
- 双阈值病理化门 I_max ≥ 0.7β ∨ L ≥ 1.0β（转化接口 §3.1）

**本轮只审查**：
```
Pathological(x) ⇏ Disease(d)
L_agg(d) ⇏ Eligibility(d)
```
即：疾病候选从创伤负荷进入疾病选择后，是否存在独立于 L_agg 的 Eligibility(d) 资格层，以及该资格层与档位计算之间的职责边界。

## 当前状态

- Step 1 验证完成（2026-09-03）：决策树无同名决策/被否决记录；本地无重复 open issue；GitHub open grilling 无重复
- Step 2 本文件
- GitHub 镜像：gh token 已恢复（2026-09-03 验证），创建后同步

## 证据链（外部评审 + 我方核查一致）

| 反例 | 表现 | 缺失的资格证据 |
|------|------|---------------|
| BD-II | E2/E3 丧失聚合 → BD-II L_agg=1.085 | 躁狂/轻躁狂发作史（丧失事件给不了） |
| 环性障碍 | E2+E3+E4 聚合 → 环性 L_agg=1.575 | 心境周期性（事件负荷 ≠ 周期性） |
| SUD | E1 经济/剥夺召回 SUD，L_agg=0.84 | 物质使用/失控/耐受/戒断（最干净的资格门反例，无临床争议） |

## 建议执行顺序（外部评审七步，我方采纳）

```
① 定义 Eligibility(d) 的地位（前置硬门 vs L_agg 组成因素）
② 定义 Eligibility(d) 与 L_agg 的关系
③ 定义各疾病的必要资格证据
④ 检查候选集是否允许"无资格候选"
⑤ 检查档位是否只能在 Eligibility=1 后计算
⑥ 回放顾维扬（作为回归测试，不是设计依据）
⑦ 决定顾维扬 BD-II / MDD / 其他
```

## 待讨论问题（grilling 逐题展开）

1. **Eligibility(d) 是前置硬门还是 L_agg 组成因素？**（第一刀，先锁死）
   - 前置硬门 → `Candidate(d) → Eligibility(d) → L_agg(d) → Severity(d)`
   - 参与 L_agg → 资格和负荷重新混回（危险）
   - 建议基线：**Eligibility(d) ⊥ L_agg(d)**（概念职责分离：Eligibility 判"有没有资格成为 d"，L_agg 判"已经是 d 的情况下负荷多大"）
   - **✅ 已答（Q1）**：方案 A 前置硬门 + ⊥ 锁死。窄锁定：门位置 + `Eligibility=0 ⟹ 不参与疾病竞争`；呈现层延迟。
2. 各疾病资格证据清单怎么定？（BD-II=躁狂史事件、SUD=物质使用行为、OCD=强迫症状簇、环性=周期性证据……）
   - **✅ 已答（Q2-Q2-12）**：受控枚举 + 五步核验协议 + 资格语义锚（DSM/ICD 优先）；五基础原子核验闭合；SUD 三原子/19 病 → 后续批次。
3. 候选集 C(e) 语义：召回 vs 资格是否要分开标注？（§3.2.1 的"主/卫"标注是否足够）
   - **✅ 已答（#1）**：主/卫 = 召回级语义，Eligibility = 资格级语义，**正交**；候选集不加资格标注，资格由各病归位表承担。
4. 档位计算前置条件：Eligibility=0 的候选是否直接 ∅？
   - **✅ 已答（Q1/Q2-7/Q2-8 + §3.3）**：INELIGIBLE 不参与聚合（非"档位 ∅"——∅ 是 ELIGIBLE 但负荷不足的档位）；UNDETERMINED 由 input_source 处置。§3.3 前置条件已写。
5. 对现有已落盘 NPC/生成输出的兼容性（资格门是只影响新生成，还是回溯校验？）
   - **✅ 已答（#2）**：只作用新生成；已落盘 NPC 不批量回溯；顾维扬草稿作为回放验证对象。

## 决策记录（2026-09-03 闭合，详见决策树 Grilling #113）

### 机制层（全量锁定）

- **Q1**：方案 A 前置硬门；Eligibility ⊥ L_agg；ELIGIBLE ≠ 已诊断（准入非确诊，P5 防后门）
- **Q2**：证据域 B——E_d = E_d^mem ∪ E_d^hist；H 为专门定义的资格证据域
- **Q2-2**：受控枚举（非自由文本解析）；证据原子 ≠ 疾病—证据映射；新增映射附权威依据
- **Q2-3**：产出方 A——#87 规范化声明字段；转化接口不解析叙事
- **Q2-4**：MANIA/HYPOMANIA 分离；BD-II → {HYPOMANIA, DEPRESSIVE}；铁律 `L_agg 不能充当任何发作史原子`
- **Q2-5**：必要条件门（Signature ⊆ Necessary 可共享；BD-II 多必要条件 HYPOMANIA ∧ DEPRESSIVE ∧ ¬MANIA）
- **Q2-6/Q2-7**：三值两层（证据 {1,0,MISSING} × 状态 {ELIGIBLE,INELIGIBLE,UNDETERMINED}）+ 组合规则 + ELIGIBLE 仅准入
- **Q2-8/9/10/11**：归位原则（d⟹P_i / N_j⟹¬d 方向不可交换）；五步协议（方法先锁结果后锁）；资格语义锚独立层；A′ 原子依赖优先 + 疾病级分别核验
- **G1-G4**：原子语义≠成立依据 / DSM=语义锚≠输入清单 / 暂不拆分≠无需拆分 / 逻辑地位≠临床存在性
- **五基础原子核验闭合**：DEPRESSIVE（MDD/BD-II 必要）/ SUBSTANCE_USE（SUD 必要候选）/ MANIA（BD-I 必要、BD-II 排除）/ HYPOMANIA（BD-II 必要，环性不适用）/ CYCLIC（环性必要候选，=#87 病程声明）
- **#1**：主/卫召回级 vs Eligibility 资格级，正交
- **#2**：资格门只作用新生成，已落盘不回溯
- **过度设计刹车**：机制层 + 五基础原子 = 收敛点；SUD 三原子/19 病 → 延迟项

### 顾维扬回放（七步⑥⑦）

证据声明 {DEPRESSIVE=1, HYPOMANIA=0, MANIA=0, SUBSTANCE=0, CYCLIC=0} → BD-II/环性/SUD INELIGIBLE，MDD ELIGIBLE → **主病 MDD 轻**（BD-II 排除 = 必要原子 HYPOMANIA 未由 #87 声明成立，非叙事判断）。**顾维扬 BD-II 去留：降为 MDD。**

### 外审存档（19 份）

`chatgpt_share_t6a96e985.html`（顾维扬草稿审查）、`chatgpt_share_t6a96ecd6.html`（资格层解耦）、`chatgpt_share_t6a96f10e.html` ~ `chatgpt_share_t6a970c9a37.html`（同源会话 17 轮）——全部归档于本目录。

## 受影响文件（实际写入）

- `design/rules/skill-tree/创伤记忆转化接口.md`（§3.2.2 资格层新增 + §3.2.3 顺延 + §3.3 前置条件 + §四 + 头部/文末）
- `design/decisions/`（Grilling #113 条目）
- `design/framework/six-dimensions.md`（规则维度转化接口条目）
- `data/term_registry.json`（+5 术语：Eligibility(d) 疾病资格层/资格语义锚/资格证据原子/资格状态三值/资格核验全局不变量）
- `reference/灵感收件箱.md`（2026-09-01 两条灵感）
- memory（`疾病资格层-grilling-113.md`）
- 本项目文件（决策记录）

## 24 病分类框架表（工作地图，⚠️ 全部为初判/待核验——调查路线 ≠ 调查结论）

> 按证据通道对 24 经历型疾病的初判归类（依据 §3.2.2 表征偏好表 + 疾病目录 frontmatter）。**仅表示后续核验优先检查哪个证据域，不构成资格机制结论**（外审 t6a96fefc19 护栏）。逐病核验 = #113 后续批次。

| 通道 | 疾病（初判） | 核验优先检查 |
|------|-------------|------------|
| A 临床史病（E_d^hist 主导） | BD-I, BD-II, 环性, SUD, MDD, PDD（持续性抑郁）, AN, BN, BED, ASPD, 拖延 | 各病诊断标准的发作史/行为模式原子（如 MANIA/HYPOMANIA/DEPRESSIVE/SUBSTANCE_USE/CYCLIC + 待核验） |
| B 表征病（E_d^mem 主导） | PTSD, DID, 惊恐, 特定恐惧, 社交焦虑, 躯体症状, 偏执型 SZ, 分裂型, 未分化 SZ, GAD, OCD | 表征域资格化（DID→D_seg、PTSD→F 阈值化）——是否足以承担资格判定待核验 |
| C 混合（双通道） | 分裂情感, BPD | 逐病定：临床史原子 + 表征域组合 |

**备注**：A 类偏好点集中在中低 F 区（资格本质 = 发作史/行为史而非表征）；B 类高 F（表征域已部分门控主病选择，但卫星聚合仍可绕过——E_d^mem 阈值化批次）；ASPD/拖延/进食障碍是否需新增行为模式原子（非发作史类）→ 逐病核验时裁决。**首批五病（BD-I/BD-II/环性/SUD/MDD）已完成核验，其余为待核验地图。**

## 受影响文件（预判）

- `design/rules/skill-tree/创伤记忆转化接口.md`（§3.2 候选集 + §3.3 档位——可能新增资格门层）→ ✅ 已写入（§3.2.2 资格层 + §3.2.3 顺延 + §3.3 前置条件）
- `data/term_registry.json`（新术语：Eligibility(d) / 资格门 / 资格证据）→ ✅ 已写入（+5 术语）
- `design/decisions/`（本议题）→ ✅ 已写入（Grilling #113 条目）
- `design/framework/six-dimensions.md`（规则维度状态）→ ✅ 已写入
- `../../../规格/素材/drafts/顾维扬.gen.json`（回放后定 BD-II 去留）→ ✅ 回放裁决：BD-II 降 MDD（gen.json 本体更新归 #89 后续）

---
*创建: 2026-09-03 | 闭合: 2026-09-03*
*关联: [grilling-89](../grilling-89-npc-material/grilling-89-npc-material.md), [评审-顾维扬草稿-外部AI审查-t6a96e985](../../../spec/material/评审-顾维扬草稿-外部AI审查-t6a96e985.md), [评审-资格层解耦-外部AI审查-t6a96ecd6](../../../spec/material/评审-资格层解耦-外部AI审查-t6a96ecd6.md), [创伤记忆转化接口](../../../rules/skill-tree/%E5%88%9B%E4%BC%A4%E8%AE%B0%E5%BF%86%E8%BD%AC%E5%8C%96%E6%8E%A5%E5%8F%A3.md)*
