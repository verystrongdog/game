# DID 资格核验 — 收尾（裁决记录，2026-09-06 定案）

Type: 资格核验批次 1 记录
归属: [#116](https://github.com/verystrongdog/game/issues/116) 配额表驱动核验批次
前置: [DID-核验-证据收集](DID-%E6%A0%B8%E9%AA%8C-%E8%AF%81%E6%8D%AE%E6%94%B6%E9%9B%86.md)（236 行证据收集，子代理产出）
状态: ✅ 已裁决（2026-09-06 用户照准五项）

## 裁决结果（5 项照准）

1. **通道修正**：工作地图 B 表征 → **C 混合**（E_d^mem D_seg + E_d^hist 身份结构声明）。依据：DSM 双支柱（Criterion A 身份 + Criterion B 记忆空缺，不可见时靠"两簇"识别）；反样本镜像对称（遗忘无身份瓦解 = DA/PTSD 解离亚型 R1/R2；身份瓦解无遗忘 = OSDD/6B65 R3）；纯 D_seg 门误放 DA/PTSD 亚型；实证脱节（Huntjens 2006/Donath 2025：客观测验未支持真实提取障碍）——但项目 D_seg = #90 访问层受控（记录保留/可逆/访问受控），与 Reinders 2006 状态依赖访问同构，不受自报-客观脱节影响
2. **必要成分双原子**：
   - `IDENTITY_STATE_HISTORY = 1`（E_d^hist #87 声明：已声明的 ≥2 人格状态/自我感与自主感断裂存在性；CYCLIC 配方，非状态计数）
   - `∃ 相关记忆: D_seg ≥ θ_Dseg = 0.85`（E_d^mem，#90 COMPARTMENTALIZED 访问层标记承载，非自报；[NEW 初值可调]）
3. **召回门**：∃ 性创伤事件记忆（§3.2.1 已承载）。边界声明：DID 只在性创伤事件下被召回；若未来需 忽视/遗弃→DID 属 C(e) 映射变更，非本批次
4. **无硬排除原子**（共病合法）；诈病/医源性/文化附体（R6/R7）与"非他病所致" = #87 声明侧纪律（行为证据/目击/发现的证据 C2-C3 承载不自知侧）
5. **数值**：θ_Dseg = **0.85**（区间 0.8-0.9；DID 区隔化是系统性质，排除 0.5-0.7 噪声；[NEW 初值可调] + 边界样本测试）；`IDENTITY_STATE_HISTORY = 0` → INELIGIBLE、MISSING → UNDETERMINED

## 反样本自检（通过）

| 反样本 | 拦截机制 |
|--------|---------|
| 解离性遗忘 DA（R1） | IDENTITY_STATE_HISTORY=0 → 拦 |
| PTSD 解离亚型（R2） | identity=0 → 拦（走 PTSD 门） |
| OSDD/6B65（R3） | identity=1 但无区隔 → D_seg 门拦（项目无 OSDD 槽 → 无主病，语义正确） |
| 器质遗忘 癫痫/TGA/TBI（R4） | identity=0 → 拦（+声明侧 E 排除） |
| 表演性人格（R5）/ 文化附体（R6） | 声明侧纪律（Criterion D/E 排除） |
| 诈病/造作（R7） | 声明侧纪律（行为证据/目击侧，不自知性 C2-C3） |
| 正常遗忘/儿童期遗忘（R8） | D_seg 低 → 拦 |
| ASD 急性解离（R9） | 病程归呈现层 + identity=0 |

## 判定结构（定稿形式）

```
Eligibility(DID) =
    ① 召回门：∃ 记忆 m, m.event_type = 性创伤
    ∧ ② IDENTITY_STATE_HISTORY = 1（#87 声明：身份结构存在性）
    ∧ ③ ∃ 相关记忆: D_seg(m) ≥ 0.85（#90 访问层区隔标记）
    → ELIGIBLE
    IDENTITY_STATE_HISTORY = 0 → INELIGIBLE；MISSING → UNDETERMINED
    D_seg 均 < 0.85 → INELIGIBLE（有身份结构但无记忆区隔——DSM-5 Criterion B 必备语义）
```

---

*创建: 2026-09-06 | 状态: ✅ 已裁决*
*关联: [DID-核验-证据收集](DID-%E6%A0%B8%E9%AA%8C-%E8%AF%81%E6%8D%AE%E6%94%B6%E9%9B%86.md), [批次总览](%E6%80%BB%E8%A7%88.md), [转化接口 §3.2.2](../../../../rules/skill-tree/%E5%88%9B%E4%BC%A4%E8%AE%B0%E5%BF%86%E8%BD%AC%E5%8C%96%E6%8E%A5%E5%8F%A3.md), [记忆内容层](../../../../rules/skill-tree/%E8%AE%B0%E5%BF%86%E5%86%85%E5%AE%B9%E5%B1%82.md)*
