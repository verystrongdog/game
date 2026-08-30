# 外部 AI 评审 — Q13 fid 一致性校验器形态

> 来源: ChatGPT 分享页 t_6a94548453888191bdd78647142ce8cd（同会话分支）。
> 页面正文登录受限；已从 SSR 嵌入 JSON 提取评审最终回复。

---

Q13 定案：**选 A——管线校验器 + 引擎侧消费即断言。**

这比只做管线检查更完整，而且与前面已经建立的 fail-fast 家族一致。

### 锁定两层防线

**第一层：管线侧**

`tools/validate_situation_fids.py`

固定检查：

1. `key_brain_regions` 中每个名称都存在于 `region_name_map.regions`；
2. `name == functional_id`；
3. 27 个原型展开后，**37 个去重名称 100% 命中**；
4. 输出覆盖/命中报告；
5. 任一失败 → 非零退出；
6. 新增 prototype 自动随数据读取纳入检查，不维护第二份硬编码名单。

这里仍然**不建立 dk → fid 翻译表**。

**第二层：引擎侧**

`SituationSelector` 构造/加载阶段，对实际加载的全部 `key_brain_regions` 做存在性断言：

```text
prototype
   ↓
key_brain_regions
   ↓
已知 fid 集？
   ├─ 是 → 正常
   └─ 否 → 加载期异常
```

这样即使有人绕过 Python 管线校验器直接替换数据文件，也不会出现：

```text
未知 fid
  ↓
找不到节点
  ↓
静默注入 0
```

这种情况。

### 三个边界同时锁死

**不要求 `key_brain_regions ⊆ W_sensory/W_active`。**

情境 prototype 的 fid 是直接情境节点注入，不是 W_sensory 的活跃节点。因此不能把 Q9 的 moonlight 落点约束错误套过来。

**fid 校验器与 moonlight 校验分离。**

```text
validate_situation_fids.py
        ↓
situation_primitives / region_name_map
```

而：

```text
moonlight_landing
        ↓
引擎加载期四项校验
```

两者职责不混合。

**`G` 的成员合法性也不需要再造一套名单。**

Q6 已经锁定 G 是从注册的 27 个 prototype **构造期计算**出来的，因此 `G ⊆ 27` 是构造保证；真正有意义的硬断言是 `G ≠ ∅`。

### Q13 正式定案

> **Q13：选 A。** 实施 `tools/validate_situation_fids.py` 作为管线侧只读校验器，断言 `key_brain_regions` 名称存在于 `region_name_map.regions`，且 `name == functional_id`；输出 27 原型展开后的 37 个去重名称 100% 命中报告，失败非零退出，并自动覆盖未来新增原型。
>
> SituationSelector 加载全部 27 个 prototype 时，在引擎侧再次断言 `key_brain_regions` 中 fid 均属于已知 fid 集；未知 fid → 加载期异常，不允许静默降级或零注入。
>
> 不建立 dk→fid 翻译映射；不要求情境 fid 属于 W_sensory/W_active；situation fid 校验与 moonlight_landing 校验保持独立。

**Q13 闭合，A。**

---

If you want, I can:

- Explain how the two-layer defense design improves system robustness
- Detail the differences between situation fid validation and moonlight landing checks
- Describe the rationale for not establishing a dk to fid translation map
