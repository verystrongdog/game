# Grilling #95 — #6 estimator-validity 完整实验（2026-08-27）

> 来源：用户 ChatGPT 分享链接 ×20（#94 收尾总结 + 逐题裁决）。决策树 #95 条目 + `../../../../设计归档/grilling/grilling-95-estimator-validity/grilling-95.md` 完整记录。

## 关键决策摘要（Q1-Q19）

- **实验**：estimator-validity = 观测估计器恢复结构 𝒞 的成立域（`F_known → 𝒞_exact → synthetic → Ĉ_obs`），v6 #5「TE≠因果」落地为可测试问题。
- **Q1-Q4**：20 系统全覆盖；目标 = 结构恢复；plug-in 主 + TE 对照；A_pair 主判（无 θ_valid）+ P/R/F1 诊断 + CS′̂ 对照。
- **Q5-Q6**：六梯度（N/p_n/d/p_m/h/c）分梯度扫描 + 关键格全因子；R=32 + 条件置换检验 α=0.01。
- **Q7-Q8**：CS′̂ = Ĉ_obs 上 exact-primitive replay（无 SM̂ 观测近似）；scaled 轨独立推迟、复用 estimator stack。
- **Q9-Q10**：双变量 TE 复用 cs4（cTE 推迟）；μ₀=Unif、无 burn-in、逐轨迹独立。
- **Q11**：脚本 4 `sim_consciousness_v7_estimator_validity.py`，benchmark.py 零改动，无失败线。
- **Q12-Q19**：预注册选格（R1-R4，0.15 选格阈值）；h 投影 truth（component-connectivity projection）；逐边族 ∃ 聚合；p_n→d→p_m→h 缺失不拼接；观测 Reacĥ（exact 仅评估侧）；三值边状态 not_testable。

## 后续

- 脚本 4 实现 → GitHub issue #96
- scaled observation 轨（n≫8）启动前置 = 本批成立域结论
- 全观测估计版 CS′̂ / cTE 变体 → 独立后续轨

## 入库

- term_registry：estimator-validity / Ĉ_obs / A_pair / synthetic observation 轨 / not_testable / scaled observation 轨（220 条）
- 参数 [NEW] #95：选格阈值 0.15、统计层 α=0.01、R=32
