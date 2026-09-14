# 阶段证据

> 每阶段一个文件：`<阶段>-<日期>.md`。**只放精简结论**，不放大段日志或原始报告。

## 必填字段

| 字段 | 说明 |
|---|---|
| base SHA / head SHA | 起止 commit |
| 工具版本 | dotnet / python / Unity 等实际版本 |
| 命令与退出码 | 逐条列出实际执行的命令 |
| 问题差分 | `new_finding = after − mapped(before) − expected_delta`，要求为空 |
| 测试报告定位 | 指向 artifact 或可复现命令 |
| 回滚演练结论 | `git revert` 是否恢复上一状态 |
| 工作树干净 | 检查后无非预期变化 |

判据见 [WORKFLOW.md §五/§六](../../../WORKFLOW.md)。

## 已有证据

| 文件 | 阶段 | 结论 | 未闭合项 |
|---|---|---|---|
| [action-description-live-loop-2026-09-14.md](action-description-live-loop-2026-09-14.md) | [#162](https://github.com/verystrongdog/game/issues/162) 活体桥预览回路 | **"关掉再打开 Blender"在技术上去掉了**：真实产姿势脚本在已开会话跑完 **66.96 s**（左手位移 **384.2 mm**，独立复现 README 既有读数）· 大输出 48172 字符落 `bb-outbox/` · 起桥**不再杀已有窗口**（旧行为转为 `BB_KILL_EXISTING=1`）· 与 headless **逐位一致**；三处于 1 死链 0 failed。**六条实测发现**：`id` 写死致超时残留污染下一次请求（静默错误）· socket 超时贴太近致"超时"退化成"连不上" · WSL→Windows 环境变量不自动传递致开关静默失效 · addon 热升级不可靠 · 状态文件路径不一致 · 超时不取消脚本 | 长任务冻结 GUI（无分片）· 超时不取消 · 桥自身升级要重起会话 · owner 目视未做 · 未做多动作并行 · 母版残留 `REF_*` |
| [action-description-deform-axes-2026-09-14.md](action-description-deform-axes-2026-09-14.md) | [#161](https://github.com/verystrongdog/game/issues/161) 无约束变形骨轴向语义 | 12 根骨 × 3 局部轴 = **36 格全部测完**：**31 可观察 · 2 仅蒙皮可见 · 3 不可观察**；`Head` X 点头 **157.6 mm**、`Neck` X **191.5 mm**（"目视水平"从此有映射）；头/颈扭转**只有蒙皮看得见**（骨尖恒 0）；肩左右符号相反 / 脚趾同号 ⇒ **独立复现 §2.1.2**；噪声底 **0.000000 mm**、两遍 **806 数值逐值相同**；三个校验器 0 failed；`new_finding` 空 | 40 根手指骨未测（符号分歧转 [#163](https://github.com/verystrongdog/game/issues/163)） · 单一幅度 20° · 未做整机重启 · 母版残留 `REF_*` · **本表尚未被真实动作消费** |
| [action-description-epsilon-2026-09-14.md](action-description-epsilon-2026-09-14.md) | [#160](https://github.com/verystrongdog/game/issues/160) 容差 ε 实测 | 手部「骨 → 蒙皮表面」6 方向剖面实测；**掌面 = 骨局部 `+Z`**（静止朝世界 −Z）⇒ **接触档 ε = 32.6833 mm**（`Beta_Surface`，左右差 0.002 mm；`Beta_Joints` 30.55 mm 作对照）；跨 4 个姿势变化 **≤ 0.0008 mm** ⇒ 假设**支持**（结构原因已查清：手部权重 1.0 刚性）；两遍运行 **13037 个数值逐值相同**；三个校验器 0 failed；`new_finding` 空 | 朝向档/到位档未测 · 手部以外未测 · 混合权重区稳定性不继承 · 未做整机重启复现 · **与 §七·B 的屈曲符号不一致未裁定**（转 [#163](https://github.com/verystrongdog/game/issues/163)）· 母版残留撤回动作的 `REF_*` 代理 |
| [unity-animation-rigging-2026-09-14.md](unity-animation-rigging-2026-09-14.md) | [#157](https://github.com/verystrongdog/game/issues/157) 接触修正 lab | 隔离 lab 入库 + 右手/左腿/右腿三条 `TwoBoneIK` + 探针 + 派生件：关/开同帧读数齐（M1 187.12→96.45 mm · M2 −24.01/−34.91→**+2.83/+2.77 mm** · M3/M4 逐位不变 · M5 10.66→0.0014 mm）；派生件关约束下复现差 **≤0.06 mm**；PlayMode **56 项 55 过/0 败/1 跳过** · docs-integrity 14/14 · unity-assets 0 违规 · `new_finding` 空 | **M1「开」≠ 0**（固定靶超出两骨链可达域 658 > 562 mm） · M7 未做完整 Editor 重启 · M6 符号口径收窄 · 派生件与载体绑定 · Windows 拷贝 git HEAD 落后 53 提交（内容 141/14/0） |
| [unreal-animation-probe-2026-09-14.md](unreal-animation-probe-2026-09-14.md) | [#158](https://github.com/verystrongdog/game/issues/158) Unreal 动画能力探针 | **证据不足**——本机从未安装 Unreal 引擎（六项独立检查全否）；硬约束实测：`C:` 是唯一卷且仅剩 51.4 GB、WSL 上限 7 GB、无 GPU 直通，源码路线估需 110–185 GB；六条验收标准仅第 6 条（证据形态）达成。owner 2026-09-14 裁定「Unreal 线不建」 | 原型**未创建**；M1–M7 与 C1–C8 无任何读数；Unity 对照（[#157](https://github.com/verystrongdog/game/issues/157)）尚未产出 |
| [P4a-2026-09-12.md](P4a-2026-09-12.md) | P4a 环境锁定与最小 CI | CI 首跑失败→三轮修复→四连 success · 抓出 6 类「本地通过、干净检出失败」缺陷 · `new_finding` 空 | 回滚演练**已实测**（2026-09-13）：逐字节恢复 base，但回滚态 `docs-integrity`/`engine` 均 FAIL——可回滚的是代码，回滚掉的是干净检出可复现性 · Unity `NOT_AVAILABLE` |
| [P4c-2026-09-12.md](P4c-2026-09-12.md) | P4c 数据契约 | 100 文件 manifest · runtime allowlist 双向 · 53 条跨语言 fixture **判定逐条相同零豁免** · 11/11 校验器 · 416 tests · 抓出 6 个真实缺陷 · Hansen 估计值标注如实化（27 份文档 + 6 个数据文件 + 2 个生成器，数值 0 改动） | hansen2024 数据集仍未接入读取 · 三项外部数据许可未登记 · Unity 阻塞 P4d 消费闭合 |

---
*创建: 2026-09-12 | 更新: 2026-09-14（新增 #160 容差 ε 实测、#161 无约束变形骨轴向语义、#162 活体桥预览回路三行；此前同批：#158 Unreal 探针一行、#157 接触修正 lab 一行）*
*关联: [工程文档](../README.md), [WORKFLOW.md](../../../WORKFLOW.md)*
