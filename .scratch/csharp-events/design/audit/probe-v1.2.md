# csharp-events spec v1.2 探针实测记录

> 2026-08-14，本地 /tmp/eventsprobe2 临时工程引用 YouAreNotTheFish.Core（runtime 8.0.29），真实 ToneUpdater.Step 实测。补 v1.1 探针（probe-v1.1.md）未覆盖的击杀窗口场景（复查审计 F3 出处归因）。

| # | 场景 | 实测值 | 用途 |
|---|------|--------|------|
| Q1 | 击杀窗口 B1 m=1.0：δ=(1,0,0,−1) → Step(baseline) | (0.5593994, 0.4, 0.5, 0.35402513) | AC-15（与 AC-6 C1 同 δ pattern 同值——一致） |
| Q2 | 击杀窗口 B1 s[Postcentral]：α=(1,0,1,1,0,0) × m_α=1.0 → soma(1)+pain(1) | 2.0 | AC-15（双模态 ×1.0） |
| Q3 | AC-15 参与者数值自洽（python 复算）：A1 m = 15f/4f | 3.75（≥0.01 且有限 → δ 必发；VTA/SNc clip） | AC-15 p1 攻击者声明（复查审计 F1 依据） |
| Q4 | W_sensory.json B1 非零行核算（python，probe-v1.1.md P13 同法） | 20 行 | AC-15 s 行数 |
