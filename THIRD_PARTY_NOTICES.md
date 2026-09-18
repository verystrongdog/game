# Third-Party Notices / 第三方材料声明

> 本文件记录仓库内或项目流程中使用的第三方材料及当前许可审查状态。它不是第三方许可文本的替代品，也不扩大任何上游授权。

## 一、适用原则

1. [`LICENSE.md`](LICENSE.md) 只覆盖项目权利人原创且有权许可的项目材料，不覆盖本文件列出的第三方材料。
2. 第三方名称、商标、模型、动画、数据、论文、网页、图片及软件包的权利归各自权利人所有。
3. 标为 `REVIEW_REQUIRED` 的材料不得进入对外发行包，也不得由本项目向下游提供再利用授权，直至取得并保存可适用的许可文本、版本、归属要求和再分发依据。
4. 仓库可访问不等于第三方材料可被提取、复制或另作他用。使用者必须自行取得上游权利人的许可。
5. 若本文件与上游许可或服务条款冲突，以上游条款为准；发现冲突时应停止分发相关材料并通知仓库所有者。

## 二、材料登记

| 材料 | 仓库位置或用途 | 当前依据 | 状态与限制 |
|---|---|---|---|
| Adobe Mixamo 角色与动画 | `code/unity/Assets/Mixamo/**`、`code/unity/Assets/Animations/Mixamo/**` | Adobe Mixamo FAQ 说明角色和动画可免版税用于个人、商业及非营利项目，包括电子游戏；仍须遵守 Adobe/Mixamo 的完整适用条款 | **REVIEW_REQUIRED（原始文件再分发）**：游戏内使用与在公开源码仓库分发原始 FBX 是不同问题。原始 FBX 不受本项目许可覆盖，不得从本仓库提取或单独再分发；对外发布源码前须复核 Adobe 对源资产再分发的限制 |
| 基于 Mixamo 输入生成的派生动画资产 | `code/unity/Assets/Animations/Blender/RigRoundTripProbe.fbx`、`code/unity/Assets/Animations/Derived/PhysicalAttack_ContactCorrected.anim` 及后续由 X Bot/其动作烘焙、约束修正或导出的资产 | 由项目工具加工，但输入骨架、角色或动作来自 Mixamo | **REVIEW_REQUIRED / MIXAMO TERMS APPLY**：技术加工不自动消除上游权利。此类文件不受项目专有许可或 Blender 脚本 GPL 例外覆盖，不得作为独立模型、动画包或训练数据再分发 |
| Blender 与使用 `bpy` 的项目脚本 | `code/tools/**/*.py` 中带 `SPDX-License-Identifier: GPL-3.0-or-later` 的文件；包括动作母版、导出、测量、建模及活体桥 Blender 端 | Blender 官方许可页说明 Blender 为 GPL，公开发布的 Blender Python API 脚本须采用 GPL 兼容许可；Blender 生成的美术和数据输出本身不因 Blender GPL 自动变为 GPL | **GPL-3.0-or-later（脚本代码）**：许可文本见 `LICENSES/GPL-3.0-or-later.txt`。脚本输入输出另按其自身权利与上游条款处理；`bb.py`、启动脚本等不调用 `bpy` 的外部客户端仍采用项目专有许可 |
| ENIGMA Toolbox / HCP 派生连接数据 | `data/connectivity/enigma_*` | ENIGMA Toolbox 仓库声明 BSD 3-Clause；论文：Larivière et al. (2021) | **PARTIAL**：软件仓库许可已识别，但仍须确认本仓具体数据文件及其上游 HCP 数据是否全部落在同一授权范围。再分发时须保留适用版权与 BSD 条款 |
| Yeo 2011 / FreeSurfer 数据 | `data/connectivity/yeo2011/**` | 通过 nilearn 获取；FreeSurfer 使用其 BSD-like 软件/数据条款 | **REVIEW_REQUIRED**：发布前核对所下载文件对应的准确许可版本、归属和再分发条件 |
| Hansen 2024 brainstem 数据 | `data/connectivity/hansen2024/**` | Hansen et al. (2024) 论文及 `netneurolab/hansen_brainstemfc` 数据仓库 | **REVIEW_REQUIRED**：仓库内尚未保存明确适用的许可文本；不得假定“公开可下载”等于可再分发 |
| CAB-NP v1.1 | `data/connectivity/cab-np/**` | Ji et al. (2019) 论文及 Cole Neurocognition Lab 发布内容 | **REVIEW_REQUIRED**：尚未确认本仓文件的准确再分发条款 |
| Kroell 14 网络资料 | `data/connectivity/kroell14_networks.json` 及相关设计引用 | Kroell et al. (2024) 论文/研究机构发布记录 | **REVIEW_REQUIRED**：项目整理数据与论文事实的边界及许可条件须在发行前复核 |
| Kevin Iglesias — Human Basic Motions 2.4 FREE（走/跑/跳/待机 4 条 clip + Avatar 源模型 + Avatar Mask） | `code/unity/Assets/Kevin Iglesias/**`（2026-09-17 起入库**最小依赖闭包** 3.5 MB，整包 68 MB 仍不入库——见 `.gitignore`） | 资产包随附文档原文（`Human Basic Motions 2.4 FREE.pdf` 末页）：「License: Standard Asset Store EULA \| Fab Standard License ● Royalty-free and allowed for commercial use. ● **Resale not allowed.** ● Attribution not required.」作者站：<https://www.keviniglesias.com/#license> | **REVIEW_REQUIRED（原始文件再分发）**：许可明写允许**商业使用**、**无需署名**，但**禁止转售**。⚠️ 与上一条 Mixamo 同理——「在游戏里用」与「把原始 FBX 放进公开源码仓库」是两件事。本次入库是 owner 2026-09-17 的显式裁定（目的是让干净检出下 ActionLab 能播），**不构成对该条的许可审查结论**；对外发布源码前须复核 Asset Store EULA / Fab Standard License 对源资产再分发的限制 |
| 3DAssets.dev — Hospital Wards and Clinic Operations | `design/presentation/assets/hospital/*.glb` | 资产页及 API 清单标注 **CC0 1.0 Universal**；本仓采用 `Six Bed Ward Bay`（asset `23663`，SHA-256 `acb96a49db883d14aabdfc95367a9add20618df16ec346f3b15407f69689beb5`）、`Reception And Waiting Hall`（asset `23664`，SHA-256 `a198032c503e223e61ec9b1fa2411c6c5f5501dd1af84dc252af000bb0102a06`）、`Operating Theatre`（asset `23665`，SHA-256 `d4708d3d0297e81ce63a606d5aac2db637613dcc101b88659f19e7c436a7d94d`） | **CC0-1.0**：允许使用、修改与再分发，无署名要求；资产页：<https://3dassets.dev/packs/hospital-wards-and-clinic-operations>。上游声明该包由生成式 AI 产出，仍须进行人工形态与内容审查 |
| AWS RoboMaker Hospital World（仓库内自带模型） | `web/public/hospital-floor/**` | `TeamSOBITS/aws-hospital-world` 的 `ros2` 分支提交 `7161eb8448f5cba6a469da7a79ae5d660b0b7f58`；本仓仅提取上游仓库自带的一层楼板、墙体、护士站、电梯、坡道和隔帘，保留其 `LICENSE` 与 `NOTICE` | **MIT-0**：允许使用、修改与再分发，版权与许可声明随资产保留。没有复制 `hospital.world` 引用的 Gazebo Fuel 外部模型；这些外部模型不得被本条许可概括覆盖。上游仓库：<https://github.com/TeamSOBITS/aws-hospital-world> |
| 医院参考图片与页面材料 | `data/hospital_ref/**` | 仓库内参考素材及处理结果 | **REVIEW_REQUIRED**：来源与许可未形成完整登记，不得进入公开发行包 |
| 外部论文、书籍、网页快照与参考材料 | `reference/**`、`docs/reference/**` | 各文件对应作者、出版商或网站的条款 | **REVIEW_REQUIRED / REFERENCE ONLY**：仅作为研究参考保存；不受项目许可覆盖，不得随游戏或 SDK 发行。部分材料可能需要从公开仓库移除或改为仅保存引用信息 |
| Unity Editor 与 Unity Packages | `code/unity/Packages/**`、Unity 工程配置及运行环境 | Unity Software Terms、Unity Package Manager 中各包附带的许可 | **UPSTREAM TERMS APPLY**：本项目不授予 Unity 软件或包的权利；使用者需自行满足 Unity 的许可条件 |
| NuGet / Python 第三方依赖 | `code/src/**/packages.lock.json`、`code/tools/requirements.txt`、`code/sim/requirements.txt` | 各软件包随附的许可证和包元数据 | **UPSTREAM TERMS APPLY**：锁文件只记录版本，不改变各依赖的许可 |

更细的数据来源、论文 DOI、文件清单与消费方见 [`data/connectivity/external-sources.md`](data/connectivity/external-sources.md)。

## 三、发布门禁

任何公开源码发布、可执行游戏发布、素材包发布或商业发行前，至少应完成：

1. 对每个 `REVIEW_REQUIRED` 项取得并保存准确的许可文本或书面授权；
2. 区分“允许在成品游戏中使用”与“允许公开再分发源文件/原始数据”；
3. 按上游要求补齐版权声明、作者归属、论文引用、许可证副本和修改说明；
4. 从发行包及公开仓库移除不能确认再分发权的原始素材、网页快照、书籍内容、图片和数据；
5. 为最终发行物生成与实际文件一一对应的第三方清单，不以本文件中的概括代替逐文件审计；
6. 由项目权利人或合格法律专业人士完成最终复核。

## 四、已核对的官方入口

- Adobe Mixamo FAQ: <https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html>
- Blender License: <https://www.blender.org/about/license/>
- Blender FAQ（输出物与 Python 脚本）: <https://www.blender.org/support/faq/>
- ENIGMA Toolbox: <https://github.com/MICA-MNI/ENIGMA>
- Hansen brainstem FC: <https://github.com/netneurolab/hansen_brainstemfc>
- CAB-NP: <https://github.com/ColeLab/ColeAnticevicNetPartition>
- FreeSurfer license information: <https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferSoftwareLicense>

## 五、权利主张与移除请求

如你认为本仓库中的材料侵犯了你的权利，或归属/许可记录有误，请通过 GitHub 联系仓库所有者，并提供材料路径、权利依据及期望处理方式。项目所有者应在核实期间暂停对相关材料的进一步分发；此流程不限制任何适用法律赋予权利人的正式救济途径。

---

*首次登记：2026-09-15。许可状态会随上游条款和仓库内容变化；发行前必须重新核对。*
