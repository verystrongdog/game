## 关联 Issue

<!-- 引用受本 PR 影响的 issue（类型见 WORKFLOW.md §三：Task / Implementation / Bug / Experiment / RFC / Slice）。
     issue 的创建与分解约束见 design/engineering/issue-process.md -->
Closes #

## 变更类型

<!-- 勾选适用的类型 -->

- [ ] 设计文档（新增/修改 .md）
- [ ] 模拟脚本（新增/修改 sim_*.py）
- [ ] 数据文件（data/ 下的 JSON/CSV/NPY）
- [ ] 工具/资产（code/tools/ 或 Blender 文件）
- [ ] 项目结构（目录调整/文件移动）
- [ ] 仓库治理（.github/ CI/模板）

## 六维影响

<!-- 勾选受影响的维度 -->

- [ ] 规则
- [ ] 实体
- [ ] 空间
- [ ] 事件
- [ ] 呈现
- [ ] 管线

## 设计决策摘要

<!-- 这个 PR 包含的关键设计决策（如有） -->

## 一致性检查

<!-- 填表确认 -->

- [ ] `design/README.md` 是否需要同步？→ 已检查
- [ ] `design/framework/six-dimensions.md` 的「维度 → 文档列表」是否需要更新？→ 已检查
- [ ] 是否 `grep` 了受影响的关键术语，清理了跨文件残留引用？→ 已完成
- [ ] 所有交叉引用路径是否有效？（`python3 code/tools/validate_cross_refs.py` 报 0 死链）→ 已验证

## Review Checklist

<!-- Reviewer: 确认以下项目 -->

- [ ] 变更与关联 Issue 的结论一致
- [ ] 无已废弃概念（轮回/局/颜色系统/态度晶体/卡牌）被重新引入
- [ ] 数值参数有来源注释
- [ ] 文档格式符合 design/conventions/README.md 规范（头部/尾部/目录/废弃标记）
