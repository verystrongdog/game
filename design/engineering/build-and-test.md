# 构建与测试

> 「怎么把仓库跑起来、怎么验证」的**唯一权威**。工具版本、命令、判据以本文为准。
>
> 对应 owner 方案 P4a（锁定当前切片所需环境 + 建立最小 CI）。

## 目录

1. [一、环境锁定](#一环境锁定)
2. [二、命令](#二命令)
3. [三、CI](#三ci)
4. [四、判据](#四判据)
5. [五、已知缺口](#五已知缺口)

---

## 一、环境锁定

| 生态 | 版本 | 锁在哪 | 备注 |
|---|---|---|---|
| .NET SDK | **10.0.400** | [`global.json`](../../global.json)（`rollForward: latestFeature`） | 工程目标框架是 **net8.0**；SDK 10 可编译。**本机无 net8.0 runtime**，跑测试需 `DOTNET_ROLL_FORWARD=Major` |
| NuGet 源 | nuget.org | [`NuGet.config`](../../NuGet.config) | 此前包路径被烘焙进 `obj/*.nuget.g.props` 指向开发机（`/home/dog/game/.nuget-pkgs`），**干净检出无法复现**——本文件修掉该问题 |
| Python | **3.10.12** | CI 的 `setup-python` | 校验器与 sim 脚本 |
| 校验器依赖 | `PyYAML==6.0.3` | [`code/tools/requirements.txt`](../../code/tools/requirements.txt) | 9 个校验器里**只有 `validate_disease.py`** 需要第三方库 |
| 数值实验依赖 | `numpy==2.2.6` · `scipy==1.15.3` · `numba==0.67.0` | [`code/sim/requirements.txt`](../../code/sim/requirements.txt) | 15 个 sim 脚本里只有 3 个需要 |
| Unity Editor | **6000.5.2f1** | [`code/unity/ProjectSettings/ProjectVersion.txt`](../../code/unity/ProjectSettings/ProjectVersion.txt) | ⚠️ 见 §五 |

**锁定原则**：**不在锁定提交中升级**任何运行时或软件包。上表版本即当前实测版本。

### 1.1 引擎第三方包（nuget）

| 包 | 版本 |
|---|---|
| `Microsoft.NET.Test.Sdk` | 17.8.0 |
| `xunit` | 2.5.3 |
| `xunit.runner.visualstudio` | 2.5.3 |
| `coverlet.collector` | 6.0.0 |

`YouAreNotTheFish.Core`（逻辑库）**无第三方依赖**——这是刻意的：逻辑核要能被 Unity 稳定引用。

## 二、命令

### 2.1 设计正典与数据契约（改文档或数据后必跑）

```bash
pip install -r code/tools/requirements.txt

python3 code/tools/validate_cross_refs.py        # 跨文件引用：死链 / 段引用
python3 code/tools/validate_trash_isolation.py   # 归档隔离 + 废弃术语残留
python3 code/tools/validate_params.py            # 跨文件同名参数一致性
python3 code/tools/validate_spatial.py           # 空间坐标
python3 code/tools/validate_disease.py           # 疾病目录 ↔ pathology_edges
python3 code/tools/validate_cards.py             # 卡牌参数（已废弃系统，参考）
python3 code/tools/validate_eligibility.py       # 疾病资格门
python3 code/tools/validate_situation_fids.py    # 情境原型 fid
python3 code/tools/validate_tripartite_annotations.py  # 三体模型注释
```

**干净检出检查**（CI 已纳入）：

```bash
python3 code/tools/check_clean_checkout.py
```

查两件事：① 受控文件是否引用了**未受控**路径（本地因残留文件而通过、干净检出必然断）② **代码**里是否有开发机绝对路径。
文档/数据中的机器路径只报提示——那是出处引用（某文献来自某下载目录、某结论据某路径核查），不参与运行。

> 为何需要它：2026-09-12 CI 首跑失败的三类缺陷，**全部**是这一类——本地有残留产物与残留文件，模拟测试无法发现。

编排器：`python3 code/tools/run_all_checks.py`（⚠️ **有副作用**——写 `.checks-state.json`，CI 里不要用）

### 2.2 引擎（改代码后必跑）

```bash
# 本机无 net8.0 runtime，需 roll-forward
export DOTNET_ROLL_FORWARD=Major

dotnet restore code/src/YouAreNotTheFish.sln
dotnet build   code/src/YouAreNotTheFish.sln --no-restore -c Release
dotnet test    code/src/YouAreNotTheFish.sln --no-build  -c Release
```

**离线环境**：设 `NUGET_PACKAGES=<repo>/.nuget-pkgs` 复用仓库内缓存（该目录被 gitignore，非干净检出可依赖）。

### 2.3 数值实验（**不在切片关键路径**，按需跑）

```bash
pip install -r code/sim/requirements.txt
python3 code/sim/sim_consciousness_v7_rb_test.py      # 例：判别三角自检
```

sim 脚本用**扁平 import**（`from sim_consciousness_cs4_test import ...`），必须**以 `code/sim/` 为工作目录**运行，否则 import 失败。

## 三、CI

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — 三个 job，对应切片三轴：

| job | 覆盖 | 本机可复现 |
|---|---|---|
| `docs-integrity` | 9 个校验器（与 §2.1 同一循环） | ✅ |
| `engine` | SDK 版本核对 → restore → Release build → Release test → trx artifact | ✅ |
| `unity` | **显式报告 `NOT_AVAILABLE`** | ❌ 需 Editor |

**为何 `unity` job 是一个"什么也不做"的 job**：按 [WORKFLOW.md §五](../../WORKFLOW.md)，**未运行不是通过**。若直接省略该 job，整个 workflow 会全绿，而 Unity 门禁（P4b/P4d/P5）实际未执行——那是静默跳过。因此它存在、具名标注 `NOT_AVAILABLE`、并在作业摘要里列出受影响的门禁。

## 四、判据

| 判据 | 要求 |
|---|---|
| 校验器 | 9/9 退出码 0 |
| `validate_cross_refs` | **0 死链 / 0 段引用警告** |
| 引擎测试 | **353 passed / 0 failed** |
| 干净检出 | 无本地缓存（`.nuget-pkgs`）也能 restore + 构建 + 测试 |
| SDK 版本 | 与 `global.json` 一致，不一致即失败（CI 有显式断言） |
| 工作树 | 跑完检查后**无非预期变化**（校验器不写工作树） |

## 五、已知缺口

| 缺口 | 影响 | 解除条件 |
|---|---|---|
| **Unity 门禁未执行** | 阻塞 P4b（资产身份）、P4d（Core→Unity 接缝）、P5（实现并试玩） | 有 Editor + 许可证的机器 |
| `code/unity/Packages/packages-lock.json` 缺失 | 包版本不可复现 | P4b |
| `.meta` 0 个 / 场景 0 个 | Unity 工程不完整，场景靠 Editor 菜单运行时生成 | P4b |
| 无 `NuGet.lock`（packages.lock.json） | 传递依赖版本可漂移 | 待定：需在 `dotnet restore --use-lock-file` 后提交 |

### 5.1 未验证项（诚实清单）

- CI **未在 GitHub 上真实跑过**——本机只逐条模拟了各 step 的命令与退出码。首次 push 后的 CI 结果才是真证据
- 数值实验（sim）**不在 CI 中**——它们不在切片关键路径上，且成本高（部分脚本需数分钟）
- Blender 相关工具（`code/tools/*blender*.py`）**无环境验证**——本机有 `/snap/bin/blender`，但未纳入 CI

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [工程文档索引](README.md), [WORKFLOW.md](../../WORKFLOW.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), [证据](evidence/README.md)*
