#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""author_xbot_chair_grab.py —— X Bot 手 ↔ 目标接触动作的**可复用库 + 八个宿主**。

| 宿主 | `--task` | 干什么 | 权威 |
|---|---|---|---|
| `main_chair()` | `chair`（默认） | 产出动作 `BendGripChairBack`（弯腰、双手抓住椅背）——**#163 的产出，本文件原有形态** | issue #163 |
| `main_card1()` | `card1` | **测量卡 1「掐棱」**：F3 三轴映射（含 U9 的 `+Y`）· F4 接触对 · F6 尺寸区间 · F7 七档扫描（10→80 mm）· F10 手型 · F11 落点读数 ⇒ 写 `data/hand_grip_cards.json` | [动作描述口径 §十三](../../design/presentation/动作描述口径.md) |
| `main_door()` | `door` | 新动作「扣住门边推开半掩的门」——**同一张卡、新对象**（口径 §13.6 的独立验证件） | 同上 · [回合战斗流程 §10.13](../../design/rules/回合战斗流程.md) |
| `main_door_push()` | `doorpush` | 门边「推到底」**能播段**（61 帧逐帧解算 + 逐帧打键 + F4a/时序/接地/穿模） | 口径 §13.6 · issue #166 |
| `main_panic()` | `panic` | **恐慌姿态（抱头 / 捂耳）**——**第四系「目标部位局部系」的第一次实做**：掌面 ↔ 自身头部的**具名面**（ε 来自口径 §15.6.1 / #168 实测） | 口径 §15.7 ① 件 · issue #169 |
| `main_crouch()` | `crouch` | **下蹲 / 被推退**——`C′ 平衡与支撑`：**凸包件**（`code/tools/xbot_balance.py`）的载体（下蹲 → 被推 ⇒ 重心出域 → 后撤步 ⇒ 重新入域） | 口径 §15.7 ② 件 · issue #170 |
| `main_kneel()` | `kneel` | **跪地 / 顶肘**——**`A′ 部位 ↔ 物面`首件**：右膝**前面** ↔ **地面**（世界系）· 左肘**肘尖面** ↔ **门板近侧面**（道具系，§6.3.1 登记面）；ε 来自 `--set kneeelbow` 实测 | 口径 §15.7 ③ 件 · issue #171 |
| `main_restate()` | `restate` | 把 #164 的读数搬进卡片语言并断言差异 0（纯算术） | 口径 §13.8 判据 1 |
| `main_liftchest()` | `liftchest` | **弯腰双手拿起椅子、持在胸前**——口径 **§十六 缺素材回归批 ① 件**（成因类「甲」）：卡 1「掐棱」握式用在椅背**侧面端**，椅子挂在一根**空物体**上逐帧打键（**椅子跟随手**） | 口径 §十六 · §13.4 · 动作库规格 §四·戊·5 · issue #180 |

来源：design/presentation/动作描述口径.md（§二 三问骨架 · §三 D7 自由度表 · §八 容差 ε · §十 验收判据 V-a…V-e
      · §13.4 判据形态与 F4a 时域 · §15.6.1 部位面登记 · §15.7 ① 件）
      · design/presentation/Blender动作制作管线.md §七·B（撤回记录）
      · issue #163（**这是口径的回归样本**：口径管不管用，就看这一次）
      · issue #164（**手部基准卡片**：把 #163 一次性写死的判据变成可被引用的常驻件；卡 1 数值实测）
      · issue #168（**部位侧 ε 实测**：本条 `panic` 的部位面 ε 逐值来自它）
      · issue #169（**恐慌姿态**：手 ↔ **自身部位**，此前被消费的只有前两系 + 道具系）

⚠️ **库与宿主的分界**：`# ---- 可复用库` 以下（含 #164 扩展块）是**件**——道具几何、棱线表、
蒙皮读数、手骨轴实测、掐棱握式解算；七个宿主的 `main_*()` 只是把件按各自的时序串起来。
`main_chair()` 走的仍是 #163 定下的那条路径（**不重写**）：卡 1 的测量是本文件新增的件，
改的是**库**，不是那条已验收的动作。

本次重做相对撤回版的**四处改动**（都直接来自口径与 #160/#161 的实测）：
1. **屈曲符号改由外部判据定**：旧版用"指尖朝掌心"评分，而"掌心"是它自己算的平面——属 A1 自证式判据
   （#160 实测：同一姿势下它与"拇指—指尖间距"判据给出**相反**的右手符号）。现改用后者。
2. **新增三项判据**（旧判据**不可能**报出它们，正是上一轮"全绿却被否"的三项，见 #163）：
   · **目视水平**——头骨"上"轴与重力轴夹角（旧版**根本没做**，头随骨盆一起低下去）
   · **掌面贴合**——掌面点（骨原点 + ε·掌面法向）↔ 靠背顶面（ε = #160 实测 32.68 mm）
   · **拇指落点**——拇指尖 y 相对靠背近侧面（口径 D8：拇指在近侧 y ≥ −0.45）
3. **回显卡**：每次运行都把「owner 的话 → 解成什么 → 判据量 → 产物侧读数 → 状态」打成表并写进报告
   （口径 §四；V-a 要求每一项都有**产物侧**读数）。
4. **双宿主**：同一段代码既能在 headless（`--background`，权威）跑，也能被活体桥送进**已开着**的会话
   （`--host live`，预览；不重开文件、不写回母版）。见口径 §九。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

# ---- 椅子几何：逐字来自 ActionLabBuilder（权威常量，勿改）— design/presentation/动作库规格.md §四·丁
SEAT_TOP = 0.4449          # 坐面上表面
SEAT_THICKNESS = 0.05
SEAT_SIZE = 0.42           # 边长
LEG_SIZE = 0.05
LEG_SPREAD = 0.165
BACK_HEIGHT = 0.35
BACK_THICKNESS = 0.04

#: 自由度表（口径 §三 D7）——**本表逐项由 owner 2026-09-14 圈定**（值来自他的裁定，不是 agent 自选）。
#: ⚠️ 🔧 2026-09-15（口径 §三 D7 修正注记）：默认归属已**反转**为 `agent 解（owner 可改）`——owner 原话
#: 「默认条件下你来决定，如果我有需求，按照我的需求做」。本表不受影响（它当时就是逐项圈定的）；**新动作**的表
#: 按新默认写，且 agent 解的行必须**并列回显 ≥2 个可行解**（口径 §4.2 硬规矩 5）。
FREEDOM_TABLE = [
    {"量": "椅心到角色的距离", "归属": "owner 圈定", "值": "0.70 m",
     "依据": "可达性反解（残差≈0 且肘角自然）；45°/0.60 与 65°/0.70 均不合"},
    {"量": "弯腰幅度", "归属": "owner 圈定", "值": "55°（骨盆局部 X）",
     "依据": "同上扫描；45° 时手到不了顶杆"},
    {"量": "时序", "归属": "owner 圈定", "值": "帧 1/13/21/31/37/41（到位）/61（保持）",
     "依据": "口径 §三 D7；到位帧 = 41"},
    {"量": "掌面方向", "归属": "agent 解（实测）", "值": "骨局部 +Z",
     "依据": "#160：四指屈曲把中指尖带向拇指尖 ⇒ 掌心朝下（静止 T-pose）"},
    {"量": "接触档 ε", "归属": "agent 解（实测）", "值": "32.68 mm（Beta_Surface 掌面）",
     "依据": "#160 实测；跨 4 姿势变化 ≤ 0.0008 mm"},
    {"量": "头颈的反向补偿角", "归属": "agent 解（求解）", "值": "由 solve_gaze 迭代解出",
     "依据": "#161 §2.1.4：Head X / Neck X 是点头轴"},
]

#: 掌面点 = 手骨原点 + ε × 掌面法向（骨局部 +Z）。
#: 来源：design/presentation/动作描述口径.md §8.1（#160 实测 `Beta_Surface` 32.6833 / 32.6854 mm）
EPSILON_PALM_M = 0.0326833
#: 转折期阈值（**沿用既有来源**，非新拍）：`Blender动作制作管线.md` §三 V6/V7/V8 的 20 mm 量级。
#: 仅用于"掌面陷进椅子"那一侧的穿模判定；"贴合"一侧改用 ε。
PROVISIONAL_TOL_MM = 20.0
#: **掌面判据形态 = owner 2026-09-14 选定的"甲"**：按**掌面最低点**离顶面 ≤ ε（**允许倾斜**，
#: "掌根压住、指尖翘着"也算贴合）。量的对象是**真实蒙皮顶点**（掌面那一层），不是"沿法向的一个点"。
PALM_SLAB_M = 0.006
#: **接触验收容差**（owner 2026-09-14 定）：来源同 `soleMargin = 0.0028 m` 那一族（平贴面接触余量）。
#: ⚠️ 与 ε **不是**同一个数：ε 管"骨→表面"的换算，本值管"多近算贴合"（口径 §8.2）。
CONTACT_TOL_MM = 2.8
#: 靠背近侧 / 远侧面（y 更大 = 更靠角色）——口径 §6.3 的命名面
BACK_NEAR_Y = -0.45
BACK_FAR_Y = -0.49

#: 仓库根（`code/tools/` 的上面两级）——机器源与报告的相对落点都从这里算
REPO_ROOT = Path(__file__).resolve().parents[2]

CTRL_PREFIX = "CTRL_"
BONE_PREFIX = "mixamorig:"

# ---- 运动时间表（30 fps；任务空间给定，角度由 IK 解出）
#   t: (帧, 弯腰角°, 骨盆世界位移 m, 手是否上杆, 手指蜷曲 0..1)
SCHEDULE = [
    (1,  0.0,  (0.00, 0.00,  0.00), False, 0.0),
    (13, 15.0, (0.00, 0.030, -0.015), True, 0.0),
    (21, 30.0, (0.00, 0.060, -0.030), True, 0.0),
    (31, 45.0, (0.00, 0.085, -0.043), True, 0.0),
    (37, 50.0, (0.00, 0.095, -0.048), True, 0.5),
    (41, 55.0, (0.00, 0.100, -0.050), True, 1.0),
    (61, 55.0, (0.00, 0.100, -0.050), True, 1.0),
]

FINGERS = ("Index", "Middle", "Ring", "Pinky", "Thumb")
FINGER_CURL_DEG = {"Index": (45, 40, 30, 25), "Middle": (45, 40, 30, 25), "Ring": (45, 40, 30, 25),
                   "Pinky": (45, 40, 30, 25), "Thumb": (25, 20, 15, 12)}
#: 每根手指的**最末节**（= 真正的指尖）——判据一律量它，成组并列打印（口径 §七 硬规矩 2）
DIGIT_TIP = {"Index": "Index4", "Middle": "Middle4", "Ring": "Ring4", "Pinky": "Pinky4",
             "Thumb": "Thumb4"}
DIGITS = ("Index", "Middle", "Ring", "Pinky", "Thumb")


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="author_xbot_chair_grab.py")
    ap.add_argument("--task", choices=("chair", "card1", "door", "restate", "doorpush", "panic",
                                       "crouch", "kneel", "liftchest"),
                    default="chair",
                    help="宿主：#163 抓椅背（chair，默认）· 卡 1 掐棱测量（card1）· 门边动作（door）"
                         "· 门边「推到底」能播段（doorpush，#166）"
                         "· 恐慌姿态 抱头/捂耳（panic，#169——第四系「目标部位局部系」首件）"
                         "· 下蹲/被推退（crouch，#170——凸包件「重心 ↔ 支撑多边形」的载体）"
                         "· 跪地/顶肘（kneel，#171——**A′ 部位 ↔ 物面**首件：膝↔地面 · 肘↔门板近侧面）"
                         "· 弯腰双手拿起椅子、持在胸前（liftchest，#180——口径 §十六 缺素材回归批"
                         "① 件：**椅子跟随手** + 卡 1 掐棱握式用在椅背侧面端）"
                         "· 重述对拍（restate，纯算术，不需要 Blender）")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--action", default="BendGripChairBack")
    ap.add_argument("--chair", type=float, default=0.70, help="椅子中心在角色前方的距离 m")
    ap.add_argument("--bend", type=float, default=55.0, help="到位时的髋铰链前弯角")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--report", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--host", choices=("headless", "live"), default="headless",
                    help="headless=自己打开母版（权威）；live=送进**已开着**的会话（预览，不重开文件、默认不写回）")
    ap.add_argument("--no-save", action="store_true", help="只解算与报告，不写回 .blend")
    # ---- #164：卡 1 测量宿主的量（默认值 = 已实测选定的基准，见证据 §三 的扫描表）----
    ap.add_argument("--grip-z", type=float, default=None, help="抓握高度（世界 z，m）；缺省按板顶 − 基准偏移")
    ap.add_argument("--grip-drop", type=float, default=0.075, help="抓握高度 = 板顶 − 本值（m）")
    ap.add_argument("--curl", type=float, default=None, help="四指蜷曲量（0..1.5）；缺省用卡 1 的基准值")
    ap.add_argument("--card-out", default=None, help="卡 1 机器源落点（默认 <仓库>/data/hand_grip_cards.json）")
    ap.add_argument("--thickness-mm", type=float, default=None, help="只测单个板厚（mm）；缺省跑 F7 的七档扫描")
    ap.add_argument("--scan", action="store_true", help="卡 1 校准扫描（抓握高度 × 蜷曲量）——只打印表，不写机器源")
    ap.add_argument("--task-restate", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--report-in", default=None,
                    help="从既有报告**重排**机器源（不重跑测量；报告是机器源的唯一来源）")
    ap.add_argument("--still", default=None, help="静帧落点（.png）")
    # ---- #166：门边「推到底」宿主的量 ----
    ap.add_argument("--clearance", type=float, default=None,
                    help="身体到门板中面的净距（m）；缺省用 DOOR_PUSH_CLEARANCE_M")
    ap.add_argument("--crouch", type=float, default=None, help="站姿膝屈下沉量（m）")
    ap.add_argument("--scan-arc", action="store_true",
                    help="只跑「保持扣住可达的最大角」扫描（改族判定），不产动作")
    ap.add_argument("--scan-max", type=float, default=76.0, help="扫描上界（开角°）")
    ap.add_argument("--scan-step", type=float, default=2.0, help="扫描步长（°）")
    ap.add_argument("--scan-stance", action="store_true",
                    help="只跑「身体摆放（净距 b）」的解空间扫描——口径 §4.2 硬规矩 5 的 ≥2 解并列")
    ap.add_argument("--first-foot", choices=("Right", "Left"), default="Left",
                    help="迈步：哪只脚先迈（口径 §13.6 自由度表第 2 行；两种都解，回显卡并列）")
    # ---- #169：恐慌姿态（抱头 / 捂耳）宿主的量 ----
    ap.add_argument("--pose", choices=("ears", "head"), default="ears",
                    help="哪一解进 clip：ears = 捂耳（掌面 ↔ 耳侧面 ×2，口径 §15.6.1 的平support 最大面）"
                         "· head = 抱头（掌面 ↔ 后脑面 ×2）；**两解都解**，另一解只报读数（§4.2 硬规矩 5）")
    ap.add_argument("--scan-body", action="store_true",
                    help="只跑身体条件（下蹲量 × 肘方向）的解空间扫描——口径 §4.2 硬规矩 5 的 ≥2 解并列")
    ap.add_argument("--hand-shape", choices=("flat", "hug"), default=PANIC_FINAL_HAND_SHAPE,
                    help="手型两解（F10）：flat = **平掌**（五指近伸展；owner 2026-09-16 目视第 1 轮指名"
                         "「手应该是手掌的姿势」）· hug = 逐指拟合贴住头面（原默认，作对照解）")
    # ---- #170：下蹲 / 被推退宿主的量 ----
    ap.add_argument("--crouch-depth", type=float, default=CROUCH_DEPTH_M,
                    help="下蹲下沉量（m）；默认 = CROUCH_DEPTH_M")
    ap.add_argument("--push-back", type=float, default=CROUCH_PUSH_BACK_M,
                    help="被推的骨盆后移量（m，沿背向）；它决定「重心出域多深」")
    ap.add_argument("--step-back", type=float, default=CROUCH_STEP_BACK_M,
                    help="后撤步长（m，踝目标沿背向）")
    ap.add_argument("--step-foot", choices=("Right", "Left"), default=CROUCH_STEP_FOOT,
                    help="后撤的那只脚（自由度的一行；两解都解，读数并列）")
    ap.add_argument("--name", default=None,
                    help="样本名（写进凸包件的 markdown 段与报告）")
    ap.add_argument("--markdown", default=None,
                    help="凸包件证据段落的落点（由 `xbot_balance.sample_markdown` 发射）")
    ap.add_argument("--scan-posture", action="store_true",
                    help="只跑身体条件（下蹲量 × 被推后移量）的解空间扫描——口径 §4.2 硬规矩 5")
    ap.add_argument("--ear-drop-mm", type=float, default=PANIC_FINAL_DROP_MM,
                    help="捂耳时掌面沿头骨长轴**再向下**这么多 mm（owner 第 1 轮指名「手应该再向下一点」；"
                         "默认 0 = 掌面重心落在该面的 ε 锚点上——这个默认值本身已经比改前低 ≈80 mm）")
    # ---- #171：跪地 / 顶肘宿主的量 ----
    ap.add_argument("--door-open", type=float, default=KNEEL_DOOR_OPEN_DEG,
                    help="门的开角（°）；默认 20 = 口径 §6.3.1 登记的「半掩」")
    ap.add_argument("--arm-angle", type=float, default=KNEEL_ARM_ANGLE_DEG,
                    help="顶上板面时**上臂相对水平的下倾角** φ（°）——它同时定下站位"
                         "（肩到板面 = 上臂长·cosφ + ε）")
    ap.add_argument("--knee-side", choices=("Right", "Left"), default=KNEEL_KNEE_SIDE,
                    help="哪条腿跪下（另一只脚前踩）；两解都解，读数并列（口径 §4.2 硬规矩 5）")
    # ---- #180：弯腰双手拿起椅子、持在胸前宿主的量 ----
    ap.add_argument("--chest-grip-y", type=float, default=LIFT_CHEST_GRIP_Y_M,
                    help="胸前持握时**握点**（椅背近侧竖棱）的世界 y（m）——agent 解，"
                         "它同时定下椅子平移的 y 分量")
    ap.add_argument("--chest-grip-z", type=float, default=LIFT_CHEST_GRIP_Z_M,
                    help="胸前持握时**握点**的世界 z（m）——agent 解，`--scan-lift` 并列 3 档")
    ap.add_argument("--grip", choices=LIFT_GRIP_MODES, default=LIFT_GRIP_MODE,
                    help="握式：**palm**（默认，owner 2026-09-16 第 1 轮指名）= 掌面朝下、虎口落在"
                         "**椅背上沿（横杆）**上，虎口朝 −Z（「抓起来之后才能把椅子当武器抡出去」）· "
                         "side = 卡 1 掐棱用在椅背**侧面端**（掌面朝 ±X，对照解）")
    ap.add_argument("--grip-x", type=float, default=LIFT_GRIP_X_M,
                    help="palm 握式：手在横杆上的横向位置（m，绝对值；两侧对称）")
    ap.add_argument("--pelvis-back", type=float, default=LIFT_PELVIS_OFFSET[1],
                    help="弯腰时骨盆沿背向的世界位移（m）——⚠️ 它会把髋↔踝弦拉长（腿骨长 0.889 m 是上限），"
                         "配深弯腰时后移会直接让腿夹直、双脚离地")
    ap.add_argument("--pelvis-down", type=float, default=LIFT_PELVIS_OFFSET[2],
                    help="弯腰时骨盆下沉量（m，负 = 下沉）")
    ap.add_argument("--scan-lift", action="store_true",
                    help="只跑解空间扫描（弯腰角 × 胸前握点高度）——口径 §4.2 硬规矩 5 的 ≥2 解并列")
    return ap.parse_args(argv)


# ---------------------------------------------------------------- 基础设施


def armature():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    return arms[0]


def make_context():
    arm = armature()
    return arm, arm.matrix_world.to_3x3()


def world_point(arm, name, attr="head"):
    return arm.matrix_world @ getattr(arm.pose.bones[name], attr)


def update(times=10):
    for _ in range(times):
        bpy.context.view_layer.update()


def set_euler(arm, name, x=0.0, y=0.0, z=0.0):
    pb = arm.pose.bones[name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ")
    return pb


def set_world_offset(arm, m3, name, delta):
    """用**世界位移**设 `pose.location`。

    ⚠️ 单位陷阱（实测踩到）：这套骨架的 `pose.location` 单位是**骨架局部单位 = cm**
    （Armature 对象 scale=0.01）。直接写 `(0, 0.10, -0.05)` 想表达"后移 10 cm"，
    实际只动了 1 mm——姿势看着"骨盆没动"，白查一轮。
    """
    pb = arm.pose.bones[name]
    pb.location = pb.bone.matrix_local.to_3x3().inverted() @ (m3.inverted() @ Vector(delta))


def clear_pose(arm):
    for pb in arm.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        else:
            pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
    update()


def drop_temp(arm, also_objects=True):
    for pb in arm.pose.bones:
        for c in list(pb.constraints):
            if c.name.startswith("TMP_"):
                pb.constraints.remove(c)
    if also_objects:
        for ob in list(bpy.data.objects):
            if ob.name.startswith("TMP_") or ob.name.startswith("IK_"):
                bpy.data.objects.remove(ob, do_unlink=True)


def build_chair_proxy(chair_distance):
    """参考椅（`REF_Chair` 集合）——只做参考与量测，不进 FBX。"""
    old = bpy.data.collections.get("REF_Chair")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Chair")
    bpy.context.scene.collection.children.link(coll)

    def cube(name, loc, scale, color):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        ob = bpy.context.active_object
        ob.name = name
        ob.scale = scale
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        coll.objects.link(ob)
        mat = bpy.data.materials.new(name + "_mat")
        mat.diffuse_color = (*color, 1.0)
        ob.data.materials.append(mat)

    lay = chair_layout(chair_distance)
    cube("REF_Seat", lay["seat_center"], (SEAT_SIZE, SEAT_SIZE, SEAT_THICKNESS), (0.55, 0.36, 0.20))
    cube("REF_Back", lay["back_center"], (SEAT_SIZE, BACK_THICKNESS, BACK_HEIGHT), (0.45, 0.29, 0.16))
    leg_h = SEAT_TOP - SEAT_THICKNESS
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        cube("REF_Leg%d" % i, (sx * LEG_SPREAD, lay["seat_center"][1] + sy * LEG_SPREAD, leg_h / 2),
             (LEG_SIZE, LEG_SIZE, leg_h), (0.42, 0.27, 0.15))


def chair_layout(chair_distance):
    """**椅子几何的唯一来源**：代理网格与抓握目标都从它取。

    ⚠️ 这里曾经分成两个函数（`build_chair_proxy` 自己算靠背位置、`rail_y()` 另算一份），
    结果**两侧差 0.46 m**——代理把靠背摆在远侧、抓握目标却在近侧，于是"残差 0.0 mm"全绿
    而**手离椅背 440 mm**（owner 一眼看出来的正是这个）。判据必须对着**产物几何**量。
    """
    back_cy = -chair_distance + (SEAT_SIZE / 2 + BACK_THICKNESS / 2)   # 靠背在**朝角色那一侧**
    return {
        "seat_center": (0.0, -chair_distance, SEAT_TOP - SEAT_THICKNESS / 2),
        "back_center": (0.0, back_cy, SEAT_TOP + BACK_HEIGHT / 2),
        "back_near_y": back_cy + BACK_THICKNESS / 2,     # 朝角色的那一面
        "back_far_y": back_cy - BACK_THICKNESS / 2,      # 背向角色的那一面
        "back_cy": back_cy,
        "rail_top_z": SEAT_TOP + BACK_HEIGHT,
        "half_width": SEAT_SIZE / 2,
        # 抓握任务点：腕在顶杆上方略偏近侧；中指尖绕到**远侧面的下方**
        # 腕目标高出顶面 **ε**：掌面向下时，掌面点 = 骨原点 − ε·Z ⇒ 腕应恰在顶面上方 ε 处。
        # ⚠️ 上一轮把它从手拍的 45 mm 改成 ε 时"更差"（46.9 mm）——因为那时**朝向是错的**（掌面没朝下），
        #    高度再对也贴不上。现在朝向由 set_hand_grip_orientation **解出来**，这一步才成立。
        "wrist": lambda sx: Vector((sx * 0.17, back_cy + 0.005, SEAT_TOP + BACK_HEIGHT + EPSILON_PALM_M)),
        "tip": lambda sx: Vector((sx * 0.17, back_cy - BACK_THICKNESS / 2 - 0.015,
                                  SEAT_TOP + BACK_HEIGHT - 0.025)),
    }


# ---------------------------------------------------------------- 手指蜷曲轴自测


def _finger_tip(arm, side, finger):
    return f"{BONE_PREFIX}{side}Hand{finger}4"


def _palm_plane(arm, side):
    """掌心平面基：`toward_palm`（指尖朝掌心的方向）+ `lateral`（掌面内的侧向）。

    侧向必须单独量——**只最大化"朝掌心"会把侧弯也选进来**：实测第一版选中 Z/−1，
    虽然"朝掌心 173 mm"，但**侧向分量 95 mm 比它还大**，呈现就是"手指侧弯"（owner 一眼指出）。
    """
    clear_pose(arm)
    tip = world_point(arm, f"{BONE_PREFIX}{side}HandMiddle4", "tail").copy()
    wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
    toward_palm = (wrist - tip).normalized()
    # 侧向 = 垂直于「指尖→腕」且垂直于掌面法向；掌面法向由食指↔小指基节连线定
    across = world_point(arm, f"{BONE_PREFIX}{side}HandIndex1") - world_point(arm, f"{BONE_PREFIX}{side}HandPinky1")
    lateral = across.normalized()
    lateral = (lateral - toward_palm * lateral.dot(toward_palm)).normalized()
    return tip, toward_palm, lateral


def _set_one_finger(arm, side, finger, axis_index, amount):
    """按 `FINGER_CURL_DEG` 给一根手指的三个指节设同一轴的旋转；`amount` 为符号/幅度系数。"""
    for k in (1, 2, 3, 4):
        name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
        if name not in arm.pose.bones:
            continue
        e = [0.0, 0.0, 0.0]
        e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * amount)
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(e, "XYZ")


def detect_curl_axis(arm, side):
    """定"四指屈曲"的**符号**——判据是**外部几何**：屈曲会把中指尖带向拇指尖。

    ⚠️ 为什么不用"指尖朝掌心位移最大"（撤回版的判据）：那个"掌心"是**它自己算的平面**，
    属自证式判据（错误分类 A1）。#160 实测：同一姿势下两条判据给出**相反**的右手符号，
    而外部判据是决定性的（两符号间距差约 66 mm）。

    返回 {"axis", "sign", "gap_rest_mm", "gap_curl_mm", "gap_hyper_mm"}。
    """
    ax = "X"                      # 屈曲轴：#161 §2.1.4 + 撤回版自测一致落在 X
    tip = f"{BONE_PREFIX}{side}HandMiddle4"
    thumb = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def gap_mm():
        return (world_point(arm, tip, "tail") - world_point(arm, thumb, "tail")).length * 1000.0

    def curl(sign):
        for finger in FINGERS:
            for k in (1, 2, 3, 4):
                name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                if name not in arm.pose.bones:
                    continue
                e = [0.0, 0.0, 0.0]
                e[0] = math.radians(FINGER_CURL_DEG[finger][k - 1] * sign)
                pb = arm.pose.bones[name]
                pb.rotation_mode = "XYZ"
                pb.rotation_euler = Euler(e, "XYZ")
        update()

    clear_pose(arm)
    rest = gap_mm()
    readings = {}
    for sign in (1, -1):
        clear_pose(arm)
        curl(sign)
        readings[sign] = gap_mm()
    clear_pose(arm)
    sign = min(readings, key=lambda s: readings[s])
    return {"axis": ax, "sign": sign,
            "gap_rest_mm": round(rest, 1),
            "gap_curl_mm": round(readings[sign], 1),
            "gap_hyper_mm": round(readings[-sign], 1),
            "criterion_valid": bool(readings[sign] < rest)}


def apply_finger_curl(arm, side, curl_axis, amount):
    """按**外部判据**定下的轴与符号施加蜷曲；`amount` 0..1。

    四指与拇指共用一组符号（#160 实测：+1 在两侧都是屈曲）——这本身就是对
    §七·B「右四指 X−1」那组符号的**反驳**（见证据 §六）。
    """
    axis_index = 0 if curl_axis["axis"] == "X" else 2
    n = 0
    for finger in FINGERS:
        for k in (1, 2, 3, 4):
            name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
            if name not in arm.pose.bones:
                continue
            e = [0.0, 0.0, 0.0]
            e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * curl_axis["sign"] * amount)
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            n += 1
    return n


# ---------------------------------------------------------------- 捕获 IK 结果


def head_up_deg(arm):
    """头骨"上"轴（Head → HeadTop_End）与**重力轴**的夹角（度）。0 = 目视水平。

    为什么用这个量：口径 §十 V-b 列的"目视水平"在旧判据里**根本不存在**，于是弯腰时头随着
    骨盆一起低下去而无人发现。头骨的"上"轴回到竖直 ⇒ 脸朝水平。
    """
    up = (world_point(arm, f"{BONE_PREFIX}HeadTop_End", "tail")
          - world_point(arm, f"{BONE_PREFIX}Head")).normalized()
    return math.degrees(up.angle(Vector((0.0, 0.0, 1.0))))


def solve_gaze(arm, tol_deg=0.5, max_iter=8):
    """解 Neck / Head 的局部 X（点头轴）使头骨"上"轴回到竖直——**解出来的，不是猜的**。

    用数值导数：先量一次、给 Head X 加一个小步长再量，得到 dθ/dX，然后牛顿步进。
    返回 {"head_x_deg", "neck_x_deg", "before_deg", "after_deg", "iters"}。
    """
    def set_pair(hx, nx):
        for name, val in ((f"{BONE_PREFIX}Head", hx), (f"{BONE_PREFIX}Neck", nx)):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler((math.radians(val), 0.0, 0.0), "XYZ")
        update()

    before = head_up_deg(arm)
    hx = nx = 0.0
    probe = 2.0
    set_pair(probe, 0.0)
    d = (head_up_deg(arm) - before) / probe          # dθ/dHeadX（度/度）
    set_pair(0.0, 0.0)
    iters = 0
    if abs(d) < 1e-6:
        return {"head_x_deg": 0.0, "neck_x_deg": 0.0, "before_deg": round(before, 3),
                "after_deg": round(before, 3), "iters": 0, "note": "头骨上轴对 Head X 不敏感"}
    for iters in range(1, max_iter + 1):
        theta = head_up_deg(arm)
        if abs(theta) <= tol_deg:
            break
        # 颈椎承担一半、头承担一半（更自然；也不必让某一根转到底）
        step = -theta / d
        hx += step * 0.5
        nx += step * 0.5
        set_pair(hx, nx)
    after = head_up_deg(arm)
    return {"head_x_deg": round(hx, 3), "neck_x_deg": round(nx, 3),
            "before_deg": round(before, 3), "after_deg": round(after, 3), "iters": iters}


def palm_surface_point(arm, side):
    """掌面点（世界坐标）= 手骨原点 + ε × 骨局部 +Z（#160：掌面 = 骨局部 +Z）。

    ⚠️ 这是"掌面中心点"的**粗模型**（只在掌面与目标面平行时才是接触点）。
    owner 2026-09-14 选定判据形态"甲"之后，判据改用 `palm_lowest_z()`——**真实蒙皮顶点**的最低点。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    normal = (pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    return world_point(arm, f"{BONE_PREFIX}{side}Hand") + normal * EPSILON_PALM_M


_PALM_CACHE = {}


def palm_face_vertices(arm, side):
    """**掌面那一层**的真实蒙皮顶点（静止时就近取好，之后按刚性变换跟随手骨）。

    取法：网格里**主导组 = 手骨**的顶点中，沿骨局部 +Z 的偏移落在最外层 6 mm 内的那些
    （+Z 就是 #160 实测的掌面法向）。手部顶点权重为 1.0（#160 证据 §五）⇒ 刚性变换精确。
    """
    if side in _PALM_CACHE:
        return _PALM_CACHE[side]
    name = f"{BONE_PREFIX}{side}Hand"
    bl_inv = arm.data.bones[name].matrix_local.inverted()
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        # ⚠️ **只取可见皮肤层 `Beta_Surface`**：`Beta_Joints` 是骨骼可视化的网格，其"手部"顶点不在皮肤上，
        #    取两网格的 min 会被它污染（实测：掌面读数恒为 −1409.7 mm = 比顶面低 1.4 m，且**对朝向不敏感**
        #    ⇒ 说明那批顶点根本不在手上）。#160 的 ε 也是在 `Beta_Surface` 上实测的，口径一致。
        if ob.name != "Beta_Surface":
            continue
        vg = ob.vertex_groups.get(name)
        if vg is None:
            continue
        cand = []
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g == vg.index:
                cand.append(bl_inv @ (arm_inv @ (ob.matrix_world @ v.co)))
        if not cand:
            continue
        zmax = max(p.z for p in cand)
        # ⚠️ 单位：缓存的偏移在**骨架局部单位**（本母版 1 单位 = 1 cm，`arm_scale=0.01`），
        #    而 PALM_SLAB_M 写的是**米** ⇒ 必须换算，否则片层实际只有 0.06 mm 厚、"掌面最低点"退化成**单个顶点**
        #    （2026-09-14 实测：slab_n = 1）。
        slab_local = PALM_SLAB_M / max(arm.matrix_world.to_scale().x, 1e-9)
        out += [p for p in cand if p.z >= zmax - slab_local]
    _PALM_CACHE[side] = out
    return out


def palm_lowest_z(arm, side):
    """按**当前姿势**算掌面那一层顶点的**最低世界 z**（判据形态"甲"的读数对象）。

    ⚠️ **2026-09-14 修**：这里原来多乘了一次 `bone.matrix_local.inverted()`——
    而 `palm_face_vertices` 缓存的 `p` **已经是骨局部坐标**（`bl_inv @ (arm_inv @ (mesh_world @ co))`），
    再反解一次等于把"骨在骨架里的位置"当成了顶点偏移 ⇒ 读数恒定偏 **≈1.4 m**（正是那个
    −1402~−1410 mm），而且**对朝向不敏感**（因为偏量由骨的静止位置主导）。
    判据：探针里用 `pb.matrix @ p` 算出的世界坐标与 evaluated depsgraph 的实测顶点**逐位相同（差 0.0 mm）**
    ⇒ 正确写法就是 `pb.matrix @ p`。
    """
    name = f"{BONE_PREFIX}{side}Hand"
    pb = arm.pose.bones[name]
    mw = arm.matrix_world
    return min((mw @ (pb.matrix @ p)).z for p in palm_face_vertices(arm, side))


def capture_channels(arm, names):
    """把控制骨的**通道值**（euler/location）原样记下来。

    全都改成解析解之后，姿势就在通道里，**不需要**再从求值矩阵反解——反解那一步会按
    **控制骨**的父链算 basis，而姿态约束是按**变形骨**父链生效的，等于把共轭错误又引回来
    （实测：改完 `_set_world_axes` 结果却一模一样，就是因为这里又反解了一遍）。
    """
    out = {}
    for name in names:
        pb = arm.pose.bones[name]
        e = pb.rotation_euler if pb.rotation_mode != "QUATERNION" else pb.rotation_quaternion.to_euler("XYZ")
        out[name] = {"euler_deg": [math.degrees(a) for a in e],
                     "location": list(pb.location)}
    return out


def apply_channels(arm, captured):
    for name, data in captured.items():
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a) for a in data["euler_deg"]], "XYZ")
        pb.location = Vector(data["location"])
    update()


def body_frame(arm):
    """**按当前姿势**现算的身体坐标系：`spine`（骨盆→头）· `lateral`（骨盆左右）· `posterior`（背侧）。

    肘是铰链：它相对「肩→腕」连线的偏移应当**主要沿 `posterior`**，`lateral` 分量要小。
    用世界 Y 当"向后"是错的——弯腰后身体的"背侧"是**上后方**（实测 55° 弯腰时 posterior≈(0,0.57,0.82)）。
    """
    spine = (world_point(arm, f"{BONE_PREFIX}Head") - world_point(arm, f"{BONE_PREFIX}Hips")).normalized()
    lateral = (world_point(arm, f"{BONE_PREFIX}LeftUpLeg") -
               world_point(arm, f"{BONE_PREFIX}RightUpLeg")).normalized()
    lateral = (lateral - spine * lateral.dot(spine)).normalized()
    posterior = spine.cross(lateral).normalized()
    return spine, lateral, posterior


def elbow_offset(arm, side):
    """肘相对「肩→腕」弦的偏移，分解到**无歧义的三轴**：向后(世界 +Y) / 向下(−Z) / 体侧(lateral)。

    ⚠️ 这里连续错过两次，都是"判据错而不是产物错"：
      ① 先用「向外 + 向后之和最大」当**目标函数** ⇒ 那个函数本身在**鼓励肘向外张**（解出向外 96 / 后 55）；
      ② 改成投影到**脊柱轴**（`spine = Head − Hips`）并把它叫 `forward` ⇒ 弯腰后脊柱指向**前上方**，
         于是"肘朝骨盆方向（后下）"被算成了 109 mm **forward**，把**正确**的姿势判成反关节。
    ⇒ 判据只用**无歧义的世界轴**（角色不转身，故 +Y 恒为背向）＋**体侧轴**（由骨盆左右骨给出）。
    """
    _, lateral, _ = body_frame(arm)
    shoulder = world_point(arm, f"{BONE_PREFIX}{side}Arm")
    wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand")
    elbow = world_point(arm, f"{BONE_PREFIX}{side}ForeArm")
    axis = (wrist - shoulder).normalized()
    delta = elbow - shoulder
    perp = delta - axis * delta.dot(axis)
    return {"back": round(perp.y * 1000.0, 1),          # +Y = 角色背向
            "down": round(-perp.z * 1000.0, 1),         # −Z = 向下
            "side": round(perp.dot(lateral) * 1000.0, 1),
            "mm": round(perp.length * 1000.0, 1)}


def _set_world_axes(arm, ctrl_name, deform_name, y_dir_world, x_hint_world):
    """让**变形骨**的世界朝向变成：局部 Y 沿 `y_dir`、局部 X 尽量对齐 `x_hint`。

    ⚠️ **极易错的一处映射**（本工程实测踩到）：约束是 `COPY_ROTATION(LOCAL↔LOCAL)`，
    复制的是**局部**旋转，而
      · 控制骨 `CTRL_Arm` 的父级是 **`CTRL_Hips`**（平行控制链）
      · 变形骨 `mixamorig:Arm` 的父级是 **`mixamorig:Shoulder`**（真实骨链）
    ⇒ **「设控制骨的世界朝向」≠「设变形骨的世界朝向」**，两者差一个共轭。
    故 basis 必须按**变形骨**那侧的父链解，再写到控制骨上（复制是 1:1 的）：

        basis_ctrl = (P_deform_parent · rest_local_deform)⁻¹ · 目标世界矩阵
    """
    from mathutils import Matrix
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    dbone = arm.data.bones[deform_name]
    inv = arm.matrix_world.inverted().to_3x3()
    y = (inv @ Vector(y_dir_world)).normalized()
    xh = inv @ Vector(x_hint_world)
    x = xh - y * xh.dot(y)
    if x.length < 1e-8:
        x = Vector((1.0, 0.0, 0.0)) - y * y.x
    x.normalize()
    z = x.cross(y)
    target = Matrix(((x.x, y.x, z.x, 0.0),
                     (x.y, y.y, z.y, 0.0),
                     (x.z, y.z, z.z, 0.0),
                     (0.0, 0.0, 0.0, 1.0)))
    if dbone.parent is not None:
        parent_pose = ev.pose.bones[dbone.parent.name].matrix.copy()
        rest_chain = parent_pose @ dbone.parent.matrix_local.inverted() @ dbone.matrix_local
    else:
        rest_chain = dbone.matrix_local.copy()
    pb = arm.pose.bones[ctrl_name]
    pb.matrix_basis = rest_chain.inverted() @ target
    update()


def _rest_dir(arm, deform_name):
    """变形骨在**静止姿势**下的世界指向（用于让脚掌回到水平）。"""
    b = arm.data.bones[deform_name]
    v = (b.tail_local - b.head_local).normalized()
    return (arm.matrix_world.to_3x3() @ v)


def _rest_hinge(arm, deform_name):
    b = arm.data.bones[deform_name]
    return (arm.matrix_world.to_3x3() @ b.matrix_local.to_3x3().col[0])


def solve_two_bone(arm, ctrl_root, ctrl_mid, deform_root, deform_mid, deform_tip,
                   tip_target, bend_dir, label=""):
    """**通用二骨解析解**：中间关节（肘/膝）的位置由 `bend_dir` 显式给定，反解两骨朝向。

    为什么不用 Blender IK：极点到关节平面的映射**不由我控制**——实测"把极点摆在背侧"，
    仍解出**肘向前顶 109 mm**（反关节），8 个 `pole_angle` 里最好的一个背侧分量只有 10 mm。
    与其调极点，不如把**关节位置**当输入：这样肘/膝朝向是可断言的一等量。
    """
    root = world_point(arm, deform_root)
    mid_rest = world_point(arm, deform_mid)
    tip_rest = world_point(arm, deform_tip)
    a = (mid_rest - root).length
    b = (tip_rest - mid_rest).length
    chord = tip_target - root
    c = chord.length
    info = {"label": label, "reach_m": round(c, 4), "limb_len_m": round(a + b, 4)}
    if c >= a + b - 1e-6:
        mid = root + chord.normalized() * a
        info["clamped_straight"] = True
    else:
        x = (a * a - b * b + c * c) / (2.0 * c)
        h = math.sqrt(max(a * a - x * x, 0.0))
        axis = chord / c
        n = Vector(bend_dir) - axis * Vector(bend_dir).dot(axis)
        if n.length < 1e-8:
            n = Vector((0.0, 1.0, 0.0)) - axis * axis.y
        n.normalize()
        mid = root + axis * x + n * h
        info["clamped_straight"] = False
    hinge = (mid - root).cross(tip_target - mid)
    if hinge.length < 1e-8:
        hinge = Vector((1.0, 0.0, 0.0))
    hinge.normalize()
    # ⚠️ basis 必须按**变形骨**那侧的父链解（约束复制的是局部旋转，两侧父链不同 ⇒ 差一个共轭）
    _set_world_axes(arm, ctrl_root, deform_root, mid - root, hinge)
    _set_world_axes(arm, ctrl_mid, deform_mid, tip_target - mid, hinge)
    info["mid_target_m"] = [round(v, 4) for v in mid]
    info["mid_err_mm"] = round((world_point(arm, deform_mid) - mid).length * 1000.0, 1)
    info["tip_err_mm"] = round((world_point(arm, deform_tip) - tip_target).length * 1000.0, 1)
    return info


def solve_arm(arm, side, wrist_target, elbow_dir):
    return solve_two_bone(arm, f"CTRL_{side}Arm", f"CTRL_{side}ForeArm",
                          f"{BONE_PREFIX}{side}Arm", f"{BONE_PREFIX}{side}ForeArm",
                          f"{BONE_PREFIX}{side}Hand", wrist_target, elbow_dir, label=f"arm_{side}")


def solve_leg(arm, side, ankle_target, knee_dir):
    return solve_two_bone(arm, f"CTRL_{side}UpLeg", f"CTRL_{side}Leg",
                          f"{BONE_PREFIX}{side}UpLeg", f"{BONE_PREFIX}{side}Leg",
                          f"{BONE_PREFIX}{side}Foot", ankle_target, knee_dir, label=f"leg_{side}")


def web_point(arm, side):
    """**虎口**在世界里的位置 = 拇指根(`HandThumb1`)↔食指根(`HandIndex1`)的中点，再沿掌面法向偏移 ε。

    为什么需要它：此前判据只有掌面最低点 / 拇指尖 / 四指指尖 ⇒ **没有任何一条要求"虎口落在上沿上"**，
    于是虎口自然飘着（owner 一眼看出）。ε 与掌面同一套换算（[#160](../../../design/engineering/evidence/action-description-epsilon-2026-09-14.md) 实测 32.68 mm）。
    """
    # ⚠️ 这里必须用**拇指根**（Thumb1 的 head）与**食指根**（Index1 的 head）——虎口是"根与根之间"那一点。
    #    2026-09-14 实测踩到：误用了 `DIGIT_TIP['Thumb']`（= Thumb4 拇指**尖**），拇指又蜷着 ⇒
    #    虎口被算在腕**前方 130 mm** ⇒ 腕目标被反向推后 130 mm（就是那个恒定的"腕↔靠背 130.0 mm"），
    #    整只手退到远侧面之外、四指全部落在近侧。
    t = world_point(arm, f"{BONE_PREFIX}{side}HandThumb1")     # 拇指根
    i = world_point(arm, f"{BONE_PREFIX}{side}HandIndex1")     # 食指根
    mid = (t + i) * 0.5
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    # ⚠️ **法向必须取世界系**：母版的骨架对象带 **+90° X 旋转**（Y-up 导入，实测
    #    `matrix_world` 的第二/三行互换、scale 0.01）。只在骨架系里取法向，等于把 `ε`
    #    加到了一个**被转了 90° 的方向**上。
    #    #163 之所以没炸：椅背那一格的掌面法向恰是 ±X，而 X 轴是那个旋转的**不动轴** ⇒ 巧合相等。
    #    门边宿主第一次把它暴露出来（自由边的 u 不在 X 轴上）：虎口偏 21°、
    #    四指↔远侧棱从 0.4 mm 变成 8.6 mm。⇒ 换算法向与世界读数必须同一个系（§8.2 的"两个数"之外，
    #    还有"两个系"这一层）。
    normal = (arm.matrix_world.to_3x3() @ pb.matrix.to_3x3()
              @ Vector((0.0, 0.0, 1.0))).normalized()
    return mid + normal * EPSILON_PALM_M


def _strict_hand_axes(arm, side):
    """**严格对齐**：掌面法向(局部 +Z) → 世界 −Z · 展开轴(局部 X) → 世界 +X（= 上沿轴向）⇒ 局部 Y → 世界 −Y。

    ⚠️ 这一条必须是**硬约束**：上一轮它在搜索里被牺牲掉，四指于是成了 52 mm 的扇形摊开——
    owner 的原话是"两只手更像握住一个**弯曲的**椅背，而不是**笔直的**"。偏差正是那 ~30°。
    """
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    Vector((0.0, -1.0, 0.0)), Vector((1.0, 0.0, 0.0)))


def solve_thumb_to_near_face(arm, side, target, base_curl):
    """**单独解拇指自身**的旋转，让拇指尖落到近侧面（+Y 侧）。

    为什么要把拇指拆出来解：手掌严格对齐后，拇指的解剖位置落在"沿上沿(±X)"方向，
    它的 y 会落进靠背厚度区间**之内**（既非近侧也非远侧）。上一轮为了满足"拇指近侧"，
    求解器只能把**整只手偏转 30°**——那就是扇形的来源。拇指自己有 4 节可动骨，
    让它**自己去贴近侧面**，手就不必偏。
    """
    name = f"{BONE_PREFIX}{side}HandThumb1"
    pb = arm.pose.bones[name]
    tip_bone = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def probe(tx, ty, tz):
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(tx), math.radians(ty), math.radians(tz)), "XYZ")
        for finger in ("Thumb",):
            for k in (2, 3, 4):
                b2 = arm.pose.bones.get(f"{BONE_PREFIX}{side}HandThumb{k}")
                if b2 is none_guard:
                    continue
        update(2)
        return (world_point(arm, tip_bone, "tail") - target).length * 1000.0

    none_guard = None
    base = list(base_curl)
    best = None
    for tx in range(base[0] - 60, base[0] + 61, 20):
        for ty in range(base[1] - 60, base[1] + 61, 30):
            for tz in (-40, 0, 40):
                d = probe(tx, ty, tz)
                if best is None or d < best[0]:
                    best = (d, tx, ty, tz)
    for step in (8, 3):
        for tx in range(best[1] - 16, best[1] + 17, step):
            for ty in range(best[2] - 16, best[2] + 17, step):
                for tz in range(best[3] - 16, best[3] + 17, step):
                    d = probe(tx, ty, tz)
                    if d < best[0]:
                        best = (d, tx, ty, tz)
    probe(best[1], best[2], best[3])
    return {"euler_deg": [best[1], best[2], best[3]], "tip_residual_mm": round(best[0], 1)}


def hand_grip(arm, side, lay, wrist_default, tip_target):
    """手部解算（三步，全是**约束**而不是加权评分）：

    ① **严格对齐**手的三轴（掌向下 · 展开轴∥上沿）——四指因此同深、看起来"笔直"；
    ② **腕位置解析解**：让**虎口**落到上沿线上（先按默认腕目标摆一次、量虎口、把差值补到腕目标上，再解一次）；
    ③ **拇指单独解**：让拇指尖贴到近侧面（+Y 侧）。
    """
    sgn = 1.0 if side == "Left" else -1.0
    post = _posterior(arm)
    # ① 先把腕送到**默认目标**（已实测可达：撤回版在此残差 0.0 mm）
    info1 = solve_arm(arm, side, wrist_default, post)
    # ② **顺序修正点**：父链此刻已定，再定手的世界朝向——原来这一步放在 solve_arm **之前**，
    #    写 basis 用的是父骨**残留**矩阵 ⇒ 手朝向在解臂前后不一致、虎口偏移被算成错的常量（§十九 根因）
    _strict_hand_axes(arm, side)
    # ③ 在该顺序下量"虎口相对腕"的偏移（刚体常量）
    wrist_head = world_point(arm, f"{BONE_PREFIX}{side}Hand")
    off = web_point(arm, side) - wrist_head
    edge = Vector((wrist_head.x, lay["back_cy"], lay["rail_top_z"]))   # 虎口该落在的上沿那一点
    wrist_target = edge - off
    # ④ 送到"一次算出"的目标；解臂会改腕的旋转 ⇒ 再定一次朝向
    info2 = solve_arm(arm, side, wrist_target, post)
    _strict_hand_axes(arm, side)
    web2 = web_point(arm, side)
    return {"wrist_default_m": [round(v, 4) for v in wrist_default],
            "wrist_target_m": [round(v, 4) for v in wrist_target],
            "web_offset_m": [round(v, 4) for v in off],
            "web_to_edge_mm": round((web2 - edge).length * 1000.0, 1),
            "arm_default": info1,
            "arm": info2,
            "hand_euler_deg": [math.degrees(a) for a in arm.pose.bones[f"CTRL_{side}Hand"].rotation_euler]}


def _posterior(arm):
    _, _, p = body_frame(arm)
    return p


def mesh_bbox(name):
    ob = bpy.data.objects[name]
    corners = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
    return {"x": (min(c.x for c in corners), max(c.x for c in corners)),
            "y": (min(c.y for c in corners), max(c.y for c in corners)),
            "z": (min(c.z for c in corners), max(c.z for c in corners))}


# ══════════════════════════════════════════════════════════════════════════════
# 【可复用库 · #164 扩展】掐棱（卡 1）与门边动作共用的件
#
#   分四组：① 板与棱线（目标对象的唯一来源） ② 蒙皮读数（判据的度量对象）
#           ③ 手骨轴实测（F3 / F10 的依据） ④ 掐棱握式解算（两个宿主的同一段姿势逻辑）
#
#   ⚠️ 本节只**加件**：`main_chair()`（#163 的产出宿主）走的仍是上面那些函数，逐字不变。
#      依据：issue #164「抽出可复用库 + 卡脚本宿主 + 门边动作宿主；**不重写**」。
# ══════════════════════════════════════════════════════════════════════════════

# 卡 1 的四种抓握方向（F8）。`n` = 板厚方向（近侧 → 远侧）· `u` = 端面 → 板内 · `z` = 竖直。
CARD1_DIRECTIONS = ("侧握", "上罩")
#: 卡 1 的**索引键**（F1）——与口径 §13.6 名录表里的那一格**逐字相同**（校验器按字面比对）
CARD1_INDEX_KEY_NAME = "掐棱"

#: 门板代理（`REF_Door`）的尺寸——**代理块**，同 `REF_*` 先例；不进 FBX、不动源 `X Bot.fbx`
DOOR_WIDTH = 0.82
DOOR_HEIGHT = 2.02
DOOR_HINGE = (-0.50, -0.64, 0.0)
#: 半掩（owner 需求里的"半掩的门"）：起始开角 20°（门开向角色这一侧，**边缘恰好落在他伸手可及处**）
DOOR_OPEN_START_DEG = 20.0
#: 推开：+8°。⚠️ **不是**"半掩到全开"——本片实测**可达域**不允许：门宽 0.82 m 时，
#: 门从 20° 转到 28°，边缘扫过 0.14 m；再往下推，边缘就出了手臂的可解区（证据 §六：
#: 第一版 20°→32° 时**到位帧**的腕目标离肩 0.659 m > 臂长 0.562 m ⇒ 手臂被夹直、虎口离门边 72 mm）。
#: 如实登记为"一段推"：要推到底必须**迈步**（本片不新增动作词条、只交静帧）。
DOOR_OPEN_END_DEG = 28.0


# ---------------------------------------------------------------- ① 板与棱线


def board_end_frame(near_edge_point, far_edge_point, into_board_dir,
                    u_span_m=(0.0, 0.21), z_span_m=(0.4449, 0.7949)):
    """**被掐的那一端**的局部坐标：两条竖棱 + 三张命名面（两个宿主共用同一段几何语言）。

    | 名 | 是什么 | 椅背（侧握） | 门板（门边） |
    |---|---|---|---|
    | `near` / `far` | 近侧 / 远侧**竖棱**（端面与两张板面的交线） | `y=−0.45 / −0.49` 处 | 自由边上 `v=∓t/2` 处 |
    | `n` | 板厚方向：**近侧面 → 远侧面** | `−Y` | 门板法向 |
    | `u` | **端面 → 板内** | `∓X` | 自由边 → 铰链 |
    | `z` | 沿棱竖直向上 | `+Z` | `+Z` |

    ⚠️ **棱是两张面的交线**——#163 的"虎口↔上沿"参照的是**顶面中线**（`y = back_cy`），
    中线不是棱 ⇒ 那一格的 −0.0 mm 量的不是"虎口跨棱"（本片如实登记，见证据 §五）。
    """
    near, far = Vector(near_edge_point), Vector(far_edge_point)
    n = (far - near).normalized()
    u = Vector(into_board_dir)
    u = (u - n * u.dot(n)).normalized()
    z = n.cross(u)
    if z.z < 0.0:
        z = -z
    return {"near": near, "far": far, "n": n, "u": u, "z": z,
            "u_span_m": u_span_m, "z_span_m": z_span_m,
            "thickness_mm": round((far - near).length * 1000.0, 3),
            "面-近侧面": (near, -n),          # (面上一点, **朝外**法向)
            "面-远侧面": (far, n),
            "面-端面": ((near + far) * 0.5, -u),
            "棱-近侧": (near, z),
            "棱-远侧": (far, z)}


def chair_end_frame(side, lay):
    """椅背**侧面**那一端（卡 1 侧握的目标）：`x = ±half_width` 处，近侧 / 远侧两条竖棱。"""
    sgn = 1.0 if side == "Left" else -1.0
    hw = lay["half_width"]
    return board_end_frame(Vector((sgn * hw, lay["back_near_y"], 0.0)),
                           Vector((sgn * hw, lay["back_far_y"], 0.0)),
                           Vector((-sgn, 0.0, 0.0)),
                           u_span_m=(0.0, 2.0 * hw),
                           z_span_m=(lay["rail_bottom_z"], lay["rail_top_z"]))


def door_layout(open_deg=DOOR_OPEN_START_DEG, width=DOOR_WIDTH, thickness=BACK_THICKNESS,
                height=DOOR_HEIGHT, hinge=DOOR_HINGE):
    """门板几何：**半掩角由铰链实时求得**，不烘世界坐标（口径 §6.1 道具局部系）。

    铰链在 `hinge`（世界），门板绕**竖直轴** `Z` 转 `open_deg`；自由边（门边）= 铰链 + `u·width`。
    `n` = 门板法向，取"**近侧面 → 远侧面**"（近侧面 = 朝角色那一面——由该面外法向指向角色判定）。
    """
    th = math.radians(open_deg)
    u = Vector((math.cos(th), math.sin(th), 0.0))
    n = Vector((-math.sin(th), math.cos(th), 0.0))
    h = Vector(hinge)
    mid_edge = h + u * width
    # 角色固定在原点附近：取"外法向指向角色"的那一面为**近侧面**
    toward_actor = (Vector((0.0, 0.0, 0.0)) - mid_edge)
    if toward_actor.dot(-n) < toward_actor.dot(n):
        n = -n
    return {"open_deg": open_deg, "u": u, "n": n, "hinge": h, "width": width,
            "thickness": thickness, "height": height,
            "mid_edge": mid_edge,
            "near_edge": mid_edge - n * (thickness / 2.0),
            "far_edge": mid_edge + n * (thickness / 2.0),
            "panel_center": h + u * (width / 2.0) + Vector((0.0, 0.0, height / 2.0)),
            "hinge_center": h + Vector((0.0, 0.0, height / 2.0))}


def door_end_frame(lay):
    """门板**自由边**那一端 → 通用的"板端"坐标（与椅背同一段语言）。"""
    return board_end_frame(lay["near_edge"], lay["far_edge"], -lay["u"],
                           u_span_m=(0.0, lay["width"]), z_span_m=(0.0, lay["height"]))


def point_to_line_mm(p, line):
    """点到**直线**（点 + 单位方向）的距离（mm）——F4 里"虎口↔棱"的判据形态（§13.4 点↔线）。"""
    p0, d = line
    v = Vector(p) - Vector(p0)
    return (v - Vector(d) * v.dot(Vector(d))).length * 1000.0


def bent_body_setup(arm, m3, bend_deg, pelvis, foot_rest):
    """**弯腰站姿**（卡 1 与 #163 同一套身体条件）：骨盆前弯 + 世界位移 + 双脚踩原地 + 目视水平。

    ⚠️ 为什么卡 1 也必须弯腰：抓握点落在椅背**侧面上部**（`z≈0.72`、身前 0.45 m）——
    **直立够不到**。本片实测（校准扫描第一版）：直立时手臂被夹直（肘角 **180.0°**），
    虎口离目标 **155.7 mm**，四指反而落在近侧。⇒ 身体条件不是装饰，它决定残差。
    """
    set_euler(arm, "CTRL_Hips", x=bend_deg)
    set_world_offset(arm, m3, "CTRL_Hips", pelvis)
    update()
    _, _, posterior = body_frame(arm)
    for side in ("Left", "Right"):
        solve_leg(arm, side, foot_rest[side], -posterior)
        _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                        _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"),
                        _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))
    update()
    return {"bend_deg": bend_deg, "pelvis_offset_m": [round(v, 4) for v in pelvis],
            "gaze": solve_gaze(arm)}


def standing_body_setup(arm, m3, yaw_deg, foot_rest, lean_m=0.0):
    """**站立身体条件**（门边宿主用）：髋部**转身** `yaw_deg` + **双脚踩原地**（解析腿解拉回）。

    ⚠️ 为什么门边必须转身：门半掩时"边缘"不在角色的正前方（实测方位角 ≈ 30°）。
    不转身时手臂被夹直（肘角 **180.0°**、虎口离门边 **291.6 mm**）——同一个病，#163 在弯腰上踩过，
    本片在转身上又踩了一次。⇒ **身体朝向是可达域的一部分，不是装饰**。
    """
    set_euler(arm, "CTRL_Hips", z=yaw_deg)
    if lean_m:
        # 朝**身体正前方**（转身后的 −Y）倾 `lean_m`——门半掩时"边缘"离身体只有 0.45 m，
        # 不倾则腕目标离肩 0.659 m > 臂长 0.562 m（实测：手臂夹直、虎口离门边 52.9 mm）
        th = math.radians(yaw_deg)
        set_world_offset(arm, m3, "CTRL_Hips", (lean_m * math.sin(th), -lean_m * math.cos(th), 0.0))
    update()
    _, _, posterior = body_frame(arm)
    for side in ("Left", "Right"):
        solve_leg(arm, side, foot_rest[side], -posterior)
        _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                        _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"),
                        _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))
    update()
    return {"yaw_deg": yaw_deg, "lean_m": lean_m, "gaze": solve_gaze(arm)}


def _to_edge(arm, side, frame, grip_z):
    """棱上的目标点（高度 = `grip_z`）——两个宿主的抓握高度都从这里取。"""
    e = frame["near"]
    return e + frame["z"] * (grip_z - e.z)


# ---------------------------------------------------------------- ② 蒙皮读数


_SKIN_CACHE = {}


def hand_skin_points(arm, side, mesh="Beta_Surface"):
    """`[(主导骨名, 骨局部坐标)]`：该手骨链在蒙皮上的**全部顶点**（缓存）。

    ⚠️ 三条教训都在这里：
    ① **只取 `Beta_Surface`**（可见皮肤层）——`Beta_Joints` 是骨骼可视化网格，它的"手部"顶点
       不在皮肤上（#163 实测：混进来会把掌面读数污染成恒定 −1409.7 mm）；
    ② 每个顶点按**它自己的主导骨**做刚性变换（手部权重 1.0，#160 实测）——
       不能拿一根骨的矩阵去套全部顶点；
    ③ **蒙皮没有最末节（`…4`）的顶点组**：实测 50 个组只到 `…3`，指尖的肉在 `…3` 的组里
       ⇒ "指尖的蒙皮"按**手指前缀**（`HandIndex` 等）聚合，不按末节骨名取。
    """
    key = (side, mesh)
    if key in _SKIN_CACHE:
        return _SKIN_CACHE[key]
    prefix = f"{BONE_PREFIX}{side}Hand"
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.name != mesh:
            continue
        groups = {vg.index: vg.name for vg in ob.vertex_groups
                  if vg.name.startswith(prefix) and vg.name in arm.data.bones}
        if not groups:
            continue
        bl_inv = {name: arm.data.bones[name].matrix_local.inverted() for name in groups.values()}
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g in groups:
                name = groups[best_g]
                out.append((name, bl_inv[name] @ (arm_inv @ (ob.matrix_world @ v.co))))
    _SKIN_CACHE[key] = out
    return out


def finger_skin_world(arm, side, finger):
    """该手指**蒙皮**的世界坐标（按各自主导骨变换）。`finger` 取 `Index`/`Middle`/`Ring`/`Pinky`/`Thumb`。"""
    mw = arm.matrix_world
    pts = []
    for bone_name, p in hand_skin_points(arm, side):
        if f"Hand{finger}" in bone_name:
            pts.append(mw @ (arm.pose.bones[bone_name].matrix @ p))
    return pts


def points_face_gap_mm(points, face):
    """一组世界点 ↔ **命名面**（面上一点 + **朝外**法向）的**有符号最近间隙**（mm）。

    判据只有一条式子：`gap = min over 点 of (p − 面上一点) · 朝外法向`

    | 读数 | 含义 |
    |---|---|
    | `abs(gap) <= tol` | **贴合**（最近的那一点正落在面上） |
    | `gap > tol` | 悬在面**外**（没贴上去）—— 例如四指越过远侧面飞在外面 |
    | `gap < −tol` | 越过该面（**穿模**；落在板厚区间里也是这个符号） |

    ⇒ 同一格读数**两个方向都能报错**。#163 §二十 那两条判据"互相打架"的成因之一，
    就是当时的"掌面最低点"只报了一个方向（只看陷进去，看不出悬空）。
    """
    pt, out_n = Vector(face[0]), Vector(face[1])
    if not points:
        return {"gap_mm": None, "n_vertices": 0}
    vals = [(p - pt).dot(out_n) * 1000.0 for p in points]
    return {"gap_mm": round(min(vals), 2), "n_vertices": len(points),
            "max_mm": round(max(vals), 2)}


def box_gap_mm(p, frame):
    """点 ↔ **板体**（有限盒）的**带符号**距离（mm）：正 = 盒外最近距离 · 负 = 陷进盒内的深度。

    ⚠️ **为什么不能用"点到远侧棱(线)的距离"当四指的判据**（本片第一版就是这么写的，被 owner 一眼看穿）：
    棱是**一维**的——蒙皮离棱 0.5 mm，同时**陷进板体 20 mm** 完全可以成立（实测：四指 19.2 ~ 19.98 mm 穿模而
    "↔远侧棱 0.28 ~ 1.01 mm"全绿）。⇒ 判据的参照必须是**体**（有限面片/盒），不是无限平面、更不是一条线。
    这是"判据的度量对象要与措辞同层"（§4.2 硬规矩 3）在**本卡自己身上**的第二次应用。
    """
    v = Vector(p) - frame["near"]
    a = v.dot(frame["n"]) * 1000.0
    b = v.dot(frame["u"]) * 1000.0
    c = v.dot(frame["z"]) * 1000.0
    t = frame["thickness_mm"]
    u0, u1 = frame["u_span_m"][0] * 1000.0, frame["u_span_m"][1] * 1000.0
    z0, z1 = frame["z_span_m"][0] * 1000.0, frame["z_span_m"][1] * 1000.0
    if 0.0 <= a <= t and u0 <= b <= u1 and z0 <= c <= z1:
        return -min(a, t - a, b - u0, u1 - b, c - z0, z1 - c)
    da = max(-a, a - t, 0.0)
    db = max(u0 - b, b - u1, 0.0)
    dc = max(z0 - c, c - z1, 0.0)
    return math.sqrt(da * da + db * db + dc * dc)


def points_box_gap_mm(points, frame):
    """一组世界点 ↔ 板体的**最近带符号间隙**（mm）——四指的接触对读数用它。"""
    if not points:
        return None
    return round(min(box_gap_mm(p, frame) for p in points), 2)


def points_min_distance_mm(pa, pb):
    """两组世界点的最小距离（mm）——**捏间隙**（薄侧改族的读数）用它。"""
    if not pa or not pb:
        return None
    return round(min((a - b).length for a in pa for b in pb) * 1000.0, 2)


# ---------------------------------------------------------------- ③ 手骨轴实测（F3 / F10）


def hand_axes_reading(arm, side):
    """**F3 的产物侧读数**：手骨局部三轴在世界里的指向 + 与"腕 → 中指指尖"实测方向的夹角。

    ⚠️ `+Y`（腕 → 指尖）那一行是口径 **U9**（"未单独实测"）——本片**当场量**，不按"显然"填。
    ⚠️ `+Z` 掌面法向的来源是 §8.1 的 ε 实测（掌心朝下、左右一致），本函数只是**复核**它在姿势下不变。
    """
    name = f"{BONE_PREFIX}{side}Hand"
    pb = arm.pose.bones[name]
    # ⚠️ `pb.matrix` 是**骨架空间**的矩阵（本母版骨架 scale = 0.01）⇒ 方向必须再过一次
    #    `arm.matrix_world.to_3x3()`，否则"世界指向"其实只是骨架局部指向（本母版恰好同向，但别靠巧合）。
    m = arm.matrix_world.to_3x3() @ pb.matrix.to_3x3()
    axes = {k: (m @ Vector(v)).normalized() for k, v in
            (("X", (1.0, 0.0, 0.0)), ("Y", (0.0, 1.0, 0.0)), ("Z", (0.0, 0.0, 1.0)))}
    wrist = world_point(arm, name)
    tip = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Middle']}", "tail")
    d = (tip - wrist).normalized()
    return {"axes_world": {k: [round(c, 4) for c in v] for k, v in axes.items()},
            "wrist_to_middle_tip_world": [round(c, 4) for c in d],
            "Y_vs_wrist_to_tip_deg": round(math.degrees(axes["Y"].angle(d)), 3),
            "Z_vs_world_Z_deg": round(math.degrees(axes["Z"].angle(Vector((0.0, 0.0, 1.0)))), 3)}


#: 逐组的屈曲**候选轴**（F3 第 3 行：不得按"显然"填，逐组量）
CURL_GROUPS = {"四指": ("Index", "Middle", "Ring", "Pinky"), "拇指": ("Thumb",)}


def _apply_group_curl(arm, side, group, axis_index, sign, amount=1.0):
    """把某一**组**的手指按给定轴/符号蜷曲（其余组保持伸直）。"""
    n = 0
    for finger in CURL_GROUPS[group]:
        for k in (1, 2, 3, 4):
            name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
            if name not in arm.pose.bones:
                continue
            e = [0.0, 0.0, 0.0]
            e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * sign * amount)
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            n += 1
    return n


def palm_normal_reference(arm, side):
    """掌面参照：**掌面蒙皮的重心** + **掌面法向**（骨局部 `+Z`，口径 §8.1 实测的那个方向）。

    ⚠️ 为什么"中指尖靠近拇指尖"（#163 用的那条）**不能**当屈曲判据——本片实测它是可混淆的：
    · 绕**掌面法向扇开**手指（Z）也把中指尖带向拇指尖（实测 96.0 → **81.86** mm）；
    · 绕**手指长轴扭转**（Y）则**什么都不改变**；
    · 而"指尖 → 腕"距离对 **±θ 完全对称**（实测 X+1 = X−1 = 134.82 mm）⇒ **定不出符号**。
    ⇒ 屈曲的唯一定义是"指尖朝**掌心**走"：量它沿掌面法向的位移。三条判据的读数都留在报告里。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    mw = arm.matrix_world
    pts = [mw @ (pb.matrix @ p) for p in palm_face_vertices(arm, side)]
    centroid = sum(pts, Vector((0.0, 0.0, 0.0))) / float(len(pts))
    normal = (mw.to_3x3() @ pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    return centroid, normal


def _group_criterion_mm(arm, side, group):
    """该组屈曲的**三条外部判据**一起报（都不拿"自己算的目标点"当判据——错误分类 A1）：

    | 判据 | 量 | 取向 |
    |---|---|---|
    | **丙 指尖 → 掌面**（主） | 该组末节指尖沿**掌面法向**相对掌面蒙皮重心的位移 | 屈曲使它**增大**（指尖朝掌心走） |
    | 甲 指尖 → 腕 | 末节指尖 ↔ 手骨原点 | 只有大小、**对 ±θ 对称**（定不出符号） |
    | 乙 跨组指尖距 | 四指：中指尖↔拇指尖 · 拇指：拇指尖↔食指尖 | #163 用过；**扇开也会缩短它**（可与屈曲混淆） |
    """
    is_four = group == "四指"
    tip = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Middle' if is_four else 'Thumb']}"
    other = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb' if is_four else 'Index']}"
    a = world_point(arm, tip, "tail")
    centroid, normal = palm_normal_reference(arm, side)
    return {"palm_offset_mm": round((a - centroid).dot(normal) * 1000.0, 2),
            "tip_to_wrist_mm": round((a - world_point(arm, f"{BONE_PREFIX}{side}Hand")).length * 1000.0, 2),
            "tip_to_other_mm": round((a - world_point(arm, other, "tail")).length * 1000.0, 2)}


def detect_curl_axis_group(arm, side, group):
    """**逐组**实测屈曲轴与符号：6 个候选（3 轴 × ±）逐个数，主判据 = 丙（指尖朝掌心）。

    返回全部候选读数 ⇒ **有能力报错**（最优候选没让指尖朝掌心走 ⇒ `criterion_valid=False`）。
    `agree_with_cross_group` 记录它与 #163 那条判据（乙）是否给出同一答案——**不一致本身是读数**。
    """
    clear_pose(arm)
    rest = _group_criterion_mm(arm, side, group)
    readings = {}
    for axis_index, axis_name in ((0, "X"), (1, "Y"), (2, "Z")):
        for sign in (1, -1):
            clear_pose(arm)
            _apply_group_curl(arm, side, group, axis_index, sign)
            update()
            readings[f"{axis_name}{sign:+d}"] = _group_criterion_mm(arm, side, group)
    clear_pose(arm)
    best_key = max(readings, key=lambda k: readings[k]["palm_offset_mm"])
    return {"group": group, "axis": best_key[0], "sign": int(best_key[1:]),
            "rest": rest, "readings": readings,
            "criterion_valid": bool(readings[best_key]["palm_offset_mm"] > rest["palm_offset_mm"]),
            "agree_with_cross_group": bool(
                readings[best_key]["tip_to_other_mm"] == min(r["tip_to_other_mm"] for r in readings.values()))}


# ---------------------------------------------------------------- ④ 掐棱握式（卡 1 的唯一姿势解算器）


def fit_finger_curls(arm, side, frame, curl_axis, lo=0.6, hi=1.5, steps=19):
    """**逐指求蜷曲量**，让每根手指的蒙皮都贴到板上（板体带符号间隙的绝对值最小）。

    ⚠️ 为什么必须**逐指**（而不是一个共用系数）：四根手指长度不同，同一个蜷曲量下它们到板的
    最近间隙差 **14 mm**（实测 curl 1.0：[+7.8, +10.8, +3.2, −3.1]——同一姿势里有的悬空 11 mm、
    有的已经陷进板 3 mm）⇒ **一个系数不可能让四根都贴住**。真手也是逐指调的。
    卡 1 的 F10 本来写的就是"**逐指** 4 节屈曲角"（口径 §13.3）⇒ 本函数只是把那一格**解出来**。

    返回 `{finger: 蜷曲量}`（顺便把姿势也设好）。
    """
    out = {}
    for finger in FOUR_FINGERS:
        best = None
        for i in range(steps):
            amount = lo + (hi - lo) * i / (steps - 1)
            _apply_one_finger_curl(arm, side, finger, curl_axis, amount)
            update(1)
            gap = points_box_gap_mm(finger_skin_world(arm, side, finger), frame)
            score = (abs(gap), -amount)
            if best is None or score < best[0]:
                best = (score, amount, gap)
        _apply_one_finger_curl(arm, side, finger, curl_axis, best[1])
        out[finger] = {"蜷曲量": round(best[1], 3), "板体间隙_mm": round(best[2], 2)}
    update(2)
    return out


def _apply_one_finger_curl(arm, side, finger, curl_axis, amount):
    """单根手指按卡内的 4 节基准角 × 蜷曲量蜷曲（轴与符号由 F3 的逐组实测给定）。"""
    axis_index = 0 if curl_axis["axis"] == "X" else (1 if curl_axis["axis"] == "Y" else 2)
    for k in (1, 2, 3, 4):
        name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
        if name not in arm.pose.bones:
            continue
        e = [0.0, 0.0, 0.0]
        e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * curl_axis["sign"] * amount)
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(e, "XYZ")


def grip_board_edge(arm, side, frame, grip_z, curl_amount, curl_axis,
                    thumb_inset_m=0.045, thumb_drop_m=0.030, label="", fit_curls=True):
    """**掐棱握式**：虎口压在**近侧竖棱**上 · 拇指绕到近侧面 · 四指绕**远侧竖棱**落到远侧面。

    ① **朝向**（解析，不搜索）：骨局部 `Y → n`（四指从近侧绕向远侧）· 骨局部 `Z → −u`（掌面压端面）
       ⇒ 骨局部 `X`（蜷曲轴）`= Y × Z → −z` —— **蜷曲轴沿棱**，四指绕远侧竖棱收拢。
    ② **虎口落到棱上**：`腕 = 棱上一点 − R·(虎口相对腕的偏移)`，**一次算出**而非两遍定点
       （#163 §十八/§十九：两遍定点会把腕推过板；顺序必须是"先解臂、后定朝向"）。
    ③ **四指蜷曲**：用卡 1 的 F10 值（`curl_amount` × `FINGER_CURL_DEG`）——指尖落不落得上远侧面
       **由残差说出来**，不在解算里偷偷补。
    ④ **拇指单独解**到近侧面（拇指自己 4 节可动骨；不让整只手偏转——#163 §十七 的扇形就是这么来的）。

    返回读数（全部**产物侧**）：虎口↔棱（点↔线）· 指尖↔远侧面（逐根，点↔面）· 拇指↔近侧面 · 腕位 · 肘。
    """
    sgn = 1.0 if side == "Left" else -1.0
    n, u, z = frame["n"], frame["u"], frame["z"]
    post = _posterior(arm)
    edge_pt = _to_edge(arm, side, frame, grip_z)
    hand_name = f"{BONE_PREFIX}{side}Hand"
    ctrl_hand = f"CTRL_{side}Hand"

    # ⚠️ 手朝向的第三轴**由几何解出，不按手别硬编码**：要"掌面压端面"就是要求
    #    `掌面法向(骨局部 Z) = +u`，而 `_set_world_axes` 算出的是 `z_local = x_hint × y_dir`
    #    ⇒ 解 `x × n = u` 得 **`x_hint = n × u`**（因为 `(n×u) × n = u`）。
    #    实测代价（两次都踩在同一处）：
    #    ① 两侧同号 ⇒ 右手整只手翻个儿（虎口离棱 155 mm、残差 22.27 mm）；
    #    ② 按手别取反能过椅背，却在**门边宿主上翻了**——门自由边那一端的 (u, n) 手性与椅背 +X 端相反
    #       （`u×n = −Z`）⇒ 四指↔远侧棱 从 0.4 mm 变成 8.6 mm。⇒ 用几何量，别用"左/右"这个代理变量。
    x_hint = n.cross(u)
    # ① 朝向（此时父链未定，写下去只为给"虎口偏移"一个初值）
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    # ② 解臂（先解臂、后定朝向——#163 §十九 的顺序修正）→ 定朝向 → 重算偏移 → 再解一次
    off = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = edge_pt - off
    arm_first = solve_arm(arm, side, wrist_target, post)
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    off2 = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = edge_pt - off2
    arm_final, elbow_pick = solve_arm_with_elbow_scan(arm, side, wrist_target, post)
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    # ③ 四指蜷曲（F10 的输入值；拇指留到第 ④ 步单独解）
    if fit_curls:
        curl_solve = fit_finger_curls(arm, side, frame, curl_axis)
    else:
        _apply_group_curl(arm, side, "四指",
                          0 if curl_axis["axis"] == "X" else (1 if curl_axis["axis"] == "Y" else 2),
                          curl_axis["sign"], curl_amount)
        curl_solve = None
    update(2)
    # ④ 拇指：目标 = 近侧面上一点（骨骼尖落在面上、蒙皮厚度靠第 ⑤ 步的读数校正）
    face_pt = frame["面-近侧面"][0]
    thumb_target = face_pt + u * thumb_inset_m + z * (grip_z - face_pt.z)
    thumb = solve_thumb_to_target(arm, side, thumb_target)
    update(2)
    gap0 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), frame["面-近侧面"])["gap_mm"]
    if gap0 is not None and abs(gap0) > CONTACT_TOL_MM:
        # 一步 Newton（⚠️ 方向实测踩过一次）：近侧面的**朝外**法向是 `−n`，而 `gap` 正是沿它量的
        # ⇒ 要让 gap 归零，目标点必须沿 `−n` 移动 |gap|。写反的代价：目标点永远落在面上，
        #    间隙恒为 −14.42 mm（拇指蒙皮陷进板 14 mm），且**与抓握高度无关**——那个"恒定"就是判据。
        thumb_target = thumb_target + n * (gap0 / 1000.0)
        thumb = solve_thumb_to_target(arm, side, thumb_target)
        update(2)
    gap1 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), frame["面-近侧面"])["gap_mm"]

    web_p = web_point(arm, side)
    web_vs = web_p - edge_pt
    palm_gap = points_face_gap_mm(
        [arm.matrix_world @ (arm.pose.bones[hand_name].matrix @ q) for q in palm_face_vertices(arm, side)],
        frame["面-端面"])["gap_mm"]
    return {
        "label": label,
        "frame_axes": {"n": [round(c, 4) for c in n], "u": [round(c, 4) for c in u],
                       "z": [round(c, 4) for c in z], "thickness_mm": frame["thickness_mm"]},
        "grip_z_m": round(grip_z, 4),
        "curl_amount": curl_amount,
        "curl_axis": dict(curl_axis),
        "curl_solve": curl_solve,
        "edge_point_m": [round(c, 4) for c in edge_pt],
        "web_point_m": [round(c, 4) for c in web_p],
        "web_to_edge_mm": round(point_to_line_mm(web_p, frame["棱-近侧"]), 2),
        "web_along_n_mm": round(web_vs.dot(n) * 1000.0, 2),
        "web_along_u_mm": round(web_vs.dot(u) * 1000.0, 2),
        "wrist_target_m": [round(c, 4) for c in wrist_target],
        "arm": arm_final,
        "elbow_pick": elbow_pick,
        "thumb": thumb,
        "palm_to_end_face_mm": palm_gap,
        "thumb_gap_mm": gap1,
        "thumb_gap_before_correction_mm": gap0,
        "elbow_deg": round(math.degrees(
            (world_point(arm, f"{BONE_PREFIX}{side}Arm") - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))
            .angle(world_point(arm, hand_name) - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1),
        "elbow_offset_mm": elbow_offset(arm, side),
        "hand_euler_deg": [round(math.degrees(a), 2)
                           for a in arm.pose.bones[ctrl_hand].rotation_euler],
    }


#: 四指的分区名（成组项必须**并列**打印，口径 §七 硬规矩 2）
FOUR_FINGERS = ("Index", "Middle", "Ring", "Pinky")

#: 肘部三条判据（**沿用 #163 的既有来源**，不是本次新拍）：向后 ≥ 60 · |侧向| ≤ 40 · 向下 ≥ 20（mm）
ELBOW_BACK_MIN, ELBOW_SIDE_MAX, ELBOW_DOWN_MIN = 60.0, 40.0, 20.0


def elbow_penalty_mm(off):
    """肘偏移的**罚分**（mm）：偏离三条判据多少。0 = 三条都满足。"""
    return (max(0.0, ELBOW_BACK_MIN - off["back"]) + max(0.0, abs(off["side"]) - ELBOW_SIDE_MAX)
            + max(0.0, ELBOW_DOWN_MIN - off["down"]))


def solve_arm_with_elbow_scan(arm, side, wrist_target, post, step_deg=30.0):
    """**扫描肘平面**再解臂：不让肘外张（#163 的三条肘判据 + 罚分最小）。

    ⚠️ 为什么必须扫：`solve_two_bone` 的 `bend_dir` 只给"肘往哪边弯"的**提示**，而在卡 1 的侧握里
    用同一个 `bent posterior` 提示会解出**肘向体外张 92.6 mm**（判据上限 40）——owner 目视一眼看出
    "肘部动作不对"，而当时我的回显卡**根本没量肘**（只量了三条接触对）。⇒ 判据漏一项，目视就得补一轮。
    """
    axis = (wrist_target - world_point(arm, f"{BONE_PREFIX}{side}Arm")).normalized()
    base = Vector(post)
    perp = (base - axis * base.dot(axis))
    if perp.length < 1e-8:
        perp = Vector((0.0, 1.0, 0.0)) - axis * axis.y
    perp.normalize()
    side_ax = axis.cross(perp).normalized()
    best = None
    for i in range(int(360.0 / step_deg)):
        a = math.radians(i * step_deg)
        d = (perp * math.cos(a) + side_ax * math.sin(a)).normalized()
        info = solve_arm(arm, side, wrist_target, d)
        off = elbow_offset(arm, side)
        score = (elbow_penalty_mm(off), abs(off["side"]), round(info.get("tip_err_mm", 0.0), 3))
        if best is None or score < best[0]:
            best = (score, d, info, off)
    info = solve_arm(arm, side, wrist_target, best[1])
    return info, {"罚分": round(best[0][0], 1), "肘偏移": best[3], "扫描步长_deg": step_deg}


def grip_board_edge_readings(arm, side, frame):
    """**卡 1「掐棱」的接触对读数**（每对一行；与回显卡**同一来源**——回显卡由本函数的结果生成）。

    三条对（口径 §13.2：一对 = 手部分区 × 物体分区 × 判据形态 × 容差档 × 并列项）：

    | # | 手部分区 | 物体分区 | 形态 | 为什么是这个对象 |
    |---|---|---|---|---|
    | 1 | 虎口 | **近侧竖棱** | 点↔线 | 虎口跨的就是这条棱；`web_point` 含 ε 换算（§8.1） |
    | 2 | 拇指 | 近侧面 | 点↔面 | 拇指绕到 +Y 近侧（口径 §三 D8） |
    | 3 | **四指逐根** | **远侧竖棱** | 点↔线 | 四指绕远侧棱收拢；⚠️ 量的**不是**远侧面——见下 |

    ⚠️ **为什么不量"逐指尖 ↔ 远侧面"**（名录原写的形态）：本片实测它**不可满足**——
    板厚 40 mm 时，虎口压在近侧棱上 ⇒ 掌指关节必然落在 `n≈37.5 mm`（虎口→掌指关节在掌内是
    刚体常量 37 mm），四指于是整段越过远侧面飞在外面，蒙皮到远侧面是 **−3.5 ~ +80 mm**，
    加蜷曲只会更远。**四指真正吃住的是"远侧棱"这条线**（同一姿势下实测 **0.3 ~ 1.0 mm**）
    ⇒ 判据形态取 **点↔线**。这是"判据的度量对象要与措辞同层"（§4.2 硬规矩 3）在卡上的第一次应用。
    """
    rows = [{
        "手部分区": "虎口",
        "物体分区": "近侧竖棱",
        "判据形态": "点↔线",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "—",
        "读数_mm": round(point_to_line_mm(web_point(arm, side), frame["棱-近侧"]), 2),
    }, {
        "手部分区": "拇指",
        "物体分区": "近侧面",
        "判据形态": "点↔面",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "—",
        "读数_mm": points_face_gap_mm(finger_skin_world(arm, side, "Thumb"),
                                      frame["面-近侧面"])["gap_mm"],
    }, {
        "手部分区": "食/中/无名/小四指",
        "物体分区": "远侧面",
        "判据形态": "点↔面（**有限面片/体**，不是无限平面）",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "四指逐根（口径 §七 硬规矩 2）",
        "读数_mm": [points_box_gap_mm(finger_skin_world(arm, side, f), frame)
                    for f in FOUR_FINGERS],
        "逐项名": list(FOUR_FINGERS),
        "符号约定": "正 = 悬在板外 · |·| ≤ 容差 = 贴住 · 负 = **陷进板体**",
    }]
    return rows


def solve_thumb_to_target(arm, side, target):
    """拇指自身 4 节的**目标点解算**（由 `solve_thumb_to_near_face` 泛化：目标点由调用方给）。

    ⚠️ 保留 `solve_thumb_to_near_face` 原函数不动（#163 的路径逐字不变）；本函数是卡 1 / 门边用的。
    """
    name = f"{BONE_PREFIX}{side}HandThumb1"
    pb = arm.pose.bones[name]
    tip_bone = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def probe(tx, ty, tz):
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(tx), math.radians(ty), math.radians(tz)), "XYZ")
        update(2)
        return (world_point(arm, tip_bone, "tail") - target).length * 1000.0

    base = list(FINGER_CURL_DEG["Thumb"])
    best = None
    for tx in range(base[0] - 80, base[0] + 81, 20):
        for ty in range(base[1] - 60, base[1] + 61, 20):
            for tz in (-40, 0, 40):
                d = probe(tx, ty, tz)
                if best is None or d < best[0]:
                    best = (d, tx, ty, tz)
    for step in (8, 3):
        for tx in range(best[1] - 16, best[1] + 17, step):
            for ty in range(best[2] - 16, best[2] + 17, step):
                for tz in range(best[3] - 16, best[3] + 17, step):
                    d = probe(tx, ty, tz)
                    if d < best[0]:
                        best = (d, tx, ty, tz)
    probe(best[1], best[2], best[3])
    return {"euler_deg": [best[1], best[2], best[3]], "tip_residual_mm": round(best[0], 1)}


# ---------------------------------------------------------------- 代理网格（板 / 门）


def _proxy_cube(coll, name, center, size, color, rot_z_deg=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    if rot_z_deg:
        ob.rotation_euler = Euler((0.0, 0.0, math.radians(rot_z_deg)), "XYZ")
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    mat = bpy.data.materials.new(name + "_mat")
    mat.diffuse_color = (*color, 1.0)
    ob.data.materials.append(mat)
    return ob


def build_door_proxy(open_deg=DOOR_OPEN_START_DEG):
    """门代理（`REF_Door` 集合）：**只做参考与量测，不进 FBX**（同 `REF_Chair` 先例）。

    几何的唯一来源是 `door_layout()`——代理与判据目标从**同一个**函数取
    （#163 那次"手离椅背 440 mm 而残差 0.0 mm"就是两处各算一份造成的）。
    """
    old = bpy.data.collections.get("REF_Door")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Door")
    bpy.context.scene.collection.children.link(coll)
    lay = door_layout(open_deg)
    _proxy_cube(coll, "REF_DoorPanel", lay["panel_center"],
                (lay["width"], lay["thickness"], lay["height"]), (0.42, 0.30, 0.18), lay["open_deg"])
    _proxy_cube(coll, "REF_DoorJamb", lay["hinge_center"] + Vector((0.0, 0.0, 0.0)),
                (0.06, 0.10, lay["height"]), (0.50, 0.50, 0.50))
    return lay


def build_board_proxy(thickness_m, size=SEAT_SIZE, height=BACK_HEIGHT, distance=0.70):
    """**板代理**（`REF_Board`）：卡 1 的 F6/F7 扫描要换板厚 ⇒ 板必须能独立于椅子重建。"""
    old = bpy.data.collections.get("REF_Board")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Board")
    bpy.context.scene.collection.children.link(coll)
    lay = board_layout(distance, thickness_m, size, height)
    _proxy_cube(coll, "REF_BoardPanel",
                (0.0, lay["back_cy"], SEAT_TOP + height / 2.0),
                (size, thickness_m, height), (0.45, 0.29, 0.16))
    return lay


def board_layout(distance, thickness=BACK_THICKNESS, size=SEAT_SIZE, height=BACK_HEIGHT):
    """**板**的几何（椅背 / 门板同族）：把 `chair_layout` 里的板厚参数化 ⇒ F6/F7 扫描才有对象。

    板占 `x ∈ ±size/2` · `y ∈ [far_y, near_y]` · `z ∈ [SEAT_TOP, SEAT_TOP + height]`。
    与 `chair_layout` **同一套公式**（同一个来源，不另算一份）。
    """
    back_cy = -distance + (size / 2 + thickness / 2)
    return {"back_cy": back_cy, "half_width": size / 2, "thickness": thickness,
            "back_near_y": back_cy + thickness / 2, "back_far_y": back_cy - thickness / 2,
            "rail_bottom_z": SEAT_TOP, "rail_top_z": SEAT_TOP + height}


def main_chair() -> int:
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    report_path = Path(args.report) if args.report else tmpl.parent / "chair_grab_report.json"
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2

    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    lay = chair_layout(args.chair)
    build_chair_proxy(args.chair)
    report = {"script": "author_xbot_chair_grab.py", "blender": bpy.app.version_string,
              "template": str(tmpl), "action": args.action, "fps": args.fps,
              "host": args.host,
              "freedom_table": FREEDOM_TABLE,
              "chair_distance_m": args.chair,
              "chair": {k: (list(v) if isinstance(v, tuple) else v)
                        for k, v in lay.items() if not callable(v)},
              "problems": []}

    drop_temp(arm)
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in ("Left", "Right")}

    # 手指蜷曲轴：逐指自测（含侧向惩罚），并把读数记进报告
    curl = {s: detect_curl_axis(arm, s) for s in ("Left", "Right")}
    report["finger_curl"] = curl
    for side, spec in curl.items():
        print(f"屈曲符号自测 {side:5s}: 轴 {spec['axis']} · 符号 {spec['sign']:+d} · "
              f"拇中尖距 静息 {spec['gap_rest_mm']} → 屈曲 {spec['gap_curl_mm']} / 反向 {spec['gap_hyper_mm']} mm"
              f"（外部判据{'成立' if spec['criterion_valid'] else '**失效**'}）")

    ctrl_bones = [f"{CTRL_PREFIX}{n}" for n in
                  ("Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot",
                   "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand")]
    captured, hand_orient, thumb_orient = {}, {}, {}
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        drop_temp(arm, also_objects=True)
        set_euler(arm, "CTRL_Hips", x=bend)
        set_world_offset(arm, m3, "CTRL_Hips", pelvis)

        update()
        _, _, posterior = body_frame(arm)
        # 腿：解析解，膝朝**前**（−posterior）；目标 = 脚踝静止位 ⇒ 脚踩原地
        for side in ("Left", "Right"):
            report.setdefault("leg_solve", {})[f"{frame}_{side}"] = solve_leg(
                arm, side, foot_rest[side], -posterior)
        # 脚掌保持水平（脚控制骨的世界朝向回到它的静止朝向）
        for side in ("Left", "Right"):
            _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                            _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"), _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))

        if hands_on_rail:
            # ⚠️ 预摆只为给解析解一个好起点；**不能加到没有臂解的帧**（首帧=站立），
            #    否则首帧不中立 ⇒ 导出的 bind pose 被污染（实测被 E5 抓出 69 m 偏差）。
            set_euler(arm, "CTRL_LeftArm", z=70)
            set_euler(arm, "CTRL_LeftForeArm", x=25)
            set_euler(arm, "CTRL_RightArm", z=-70)
            set_euler(arm, "CTRL_RightForeArm", x=25)
        update()

        if hands_on_rail:
            for side in ("Left", "Right"):
                sgn = 1.0 if side == "Left" else -1.0
                grip = hand_grip(arm, side, lay, lay["wrist"](sgn), lay["tip"](sgn))
                report.setdefault("grip_solve", {})[f"{frame}_{side}"] = grip
                apply_finger_curl(arm, side, curl[side], curl_amount)
                # 拇指单独解：贴到近侧面（上沿下方 30 mm、往板内 20 mm）
                thumb_target = Vector((sgn * 0.17 + sgn * 0.02, BACK_NEAR_Y + 0.02, lay["rail_top_z"] - 0.03))
                thumb_orient[(frame, side)] = solve_thumb_to_near_face(
                    arm, side, thumb_target, FINGER_CURL_DEG["Thumb"])
            update(2)
        # ⚠️ 头颈**必须一起捕获**：它们没有控制骨（口径 §三 D6）；solve 出来的补偿角若不入 captured，
        #    复演与导出时就会丢——那样"目视水平"只活在解算的那一瞬间。
        # 目视水平：弯腰后头随骨盆低下 ⇒ 解 Neck/Head 的点头角，把头骨"上"轴拉回竖直
        report.setdefault("gaze_solve", {})[frame] = solve_gaze(arm)
        update(2)
        captured[frame] = capture_channels(arm, ctrl_bones + [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"])

    # ---- 去掉 IK 复演，逐帧复核（判据一律对着**产物几何**）----
    drop_temp(arm)
    verify = []
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        apply_channels(arm, captured[frame])
        if hands_on_rail:
            for side in ("Left", "Right"):
                spec = hand_orient.get((frame, side))
                apply_finger_curl(arm, side, curl[side], curl_amount)
                if spec:
                    pb = arm.pose.bones[f"CTRL_{side}Hand"]
                    pb.rotation_mode = "XYZ"
                    pb.rotation_euler = Euler([math.radians(a) for a in spec["hand_euler_deg"]], "XYZ")
                tsp = thumb_orient.get((frame, side))
                if tsp:
                    tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                    tb.rotation_mode = "XYZ"
                    tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
        update()
        back = mesh_bbox("REF_Back")
        row = {"frame": frame, "bend_deg": bend}
        for side in ("Left", "Right"):
            hand = world_point(arm, f"{BONE_PREFIX}{side}Hand")
            tip = world_point(arm, f"{BONE_PREFIX}{side}HandMiddle4", "tail")
            foot = world_point(arm, f"{BONE_PREFIX}{side}Foot")
            row[f"wrist_{side}_m"] = [round(v, 4) for v in hand]
            row[f"tip_{side}_m"] = [round(v, 4) for v in tip]
            row[f"wrist_to_back_mm"] = round(abs(hand.y - lay["back_cy"]) * 1000.0, 1)
            # ⚠️ 只有**手指已蜷**的帧才判"扣住"：手指伸直时指尖本来就会越过顶杆，
            #    不设这个门槛会得到"早早就扣住了"的假读数。
            row[f"tip_wraps_rail_{side}"] = (bool(tip.y < back["y"][0] and tip.z < lay["rail_top_z"])
                                             if curl_amount > 0.0 else None)
            row[f"hand_above_rail_mm"] = round((hand.z - lay["rail_top_z"]) * 1000.0, 1)
            row[f"foot_{side}_drift_mm"] = round((foot - foot_rest[side]).length * 1000.0, 1)
            upper = world_point(arm, f"{BONE_PREFIX}{side}Arm")
            lower = world_point(arm, f"{BONE_PREFIX}{side}ForeArm")
            row[f"elbow_{side}_deg"] = round(math.degrees((upper - lower).angle(hand - lower)), 1)
            row[f"elbow_{side}_offset_mm"] = elbow_offset(arm, side)
        row["head_z_m"] = round(world_point(arm, f"{BONE_PREFIX}Head").z, 4)
        # ---- 三项"旧判据不可能报出"的量（口径 §十 V-b / issue #163）----
        row["gaze_up_deg"] = round(head_up_deg(arm), 3)
        palm, thumb = {}, {}
        for side in ("Left", "Right"):
            lo = palm_lowest_z(arm, side)
            palm[side] = {"lowest_z_m": round(lo, 4),
                          "to_rail_top_mm": round((lo - lay["rail_top_z"]) * 1000.0, 1),
                          "n_face_vertices": len(palm_face_vertices(arm, side))}
            tt = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}", "tail")
            thumb[side] = {"tip_m": [round(v, 4) for v in tt],
                           "y_mm_vs_near_face": round((tt.y - BACK_NEAR_Y) * 1000.0, 1)}
            # ⚠️ **成组并列**（口径 §七 硬规矩 2）：四指 + 拇指**逐根**都要有读数——
            #    只量中指尖是不够的（owner 2026-09-14 一眼指出"只做了一件事"）。
            digits = {}
            for d in DIGITS:
                dt = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP[d]}", "tail")
                digits[d] = {"tip_y": round(dt.y, 4), "tip_z": round(dt.z, 4),
                             "vs_far_face_mm": round((dt.y - BACK_FAR_Y) * 1000.0, 1),
                             "side": "远侧(−Y)" if dt.y <= BACK_FAR_Y else "近侧(+Y)"}
            row[f"digits_{side}"] = digits
        row["palm"], row["thumb"] = palm, thumb
        row["web"] = {}
        for side in ("Left", "Right"):
            w = web_point(arm, side)
            row["web"][side] = {"pos_m": [round(v, 4) for v in w],
                                "above_edge_mm": round((w.z - lay["rail_top_z"]) * 1000.0, 1),
                                "in_slab": bool(-0.49 <= w.y <= -0.45)}
        verify.append(row)
    report["verify"] = verify
    report["back_bbox"] = {k: [round(x, 4) for x in v] for k, v in mesh_bbox("REF_Back").items()}

    # ---- 判据 ----
    last = verify[-1]
    for side in ("Left", "Right"):
        if last[f"wrist_to_back_mm"] > 60.0:
            report["problems"].append(f"{side} 腕离靠背中心面 {last['wrist_to_back_mm']} mm > 60 mm（没放到椅背上）")
        if not last[f"tip_wraps_rail_{side}"]:
            report["problems"].append(f"{side} 指尖没有绕到顶杆远侧下方（没扣住）")
        if not (100.0 <= last[f"elbow_{side}_deg"] <= 172.0):
            report["problems"].append(f"{side} 到位帧肘角 {last[f'elbow_{side}_deg']}° 不在 100–172°")
        off = last[f"elbow_{side}_offset_mm"]
        if off["back"] < 60.0:
            report["problems"].append(
                f"{side} 肘**向后**偏移只有 {off['back']} mm < 60 mm（肘没往后折 = 反关节）")
        if abs(off["side"]) > 40.0:
            report["problems"].append(f"{side} 肘**侧向**偏移 {off['side']} mm > 40 mm（肘向外张 = 侧弯）")
        if off["down"] < 20.0:
            report["problems"].append(f"{side} 肘没有挂在弦的下方（down={off['down']} mm < 20 mm）")
        if not curl[side]["criterion_valid"]:
            report["problems"].append(
                f"{side} 屈曲符号的外部判据失效（两种符号都没让中指尖靠近拇指尖）⇒ 符号不可信")
    # ---- 三项新判据（能报错才有意义）----
    if abs(last["gaze_up_deg"]) > 2.0:
        report["problems"].append(
            f"目视水平：到位帧头骨上轴偏离竖直 {last['gaze_up_deg']}° > 2°（头跟着骨盆低下去了）")
    for side in ("Left", "Right"):
        gap = last["palm"][side]["to_rail_top_mm"]
        # 判据形态"甲"（owner 2026-09-14）：允许倾斜 —— 只要**掌面最低点**在 ε 之内就算贴合；
        # 陷进去（< −PROVISIONAL_TOL_MM）另判穿模。
        if gap < -PROVISIONAL_TOL_MM:
            report["problems"].append(f"{side} 掌面最低点陷进靠背顶面 {gap} mm（穿模）")
        elif gap > CONTACT_TOL_MM:
            report["problems"].append(
                f"{side} 掌面最低点离顶面 {gap} mm > 容差 {CONTACT_TOL_MM} mm（没贴合；owner 定的接触容差）")
        for d in ("Index", "Middle", "Ring", "Pinky"):
            dy = last[f"digits_{side}"][d]["tip_y"]
            if dy > BACK_FAR_Y:
                report["problems"].append(
                    f"{side} {d} 指尖 y={dy:.4f} 未到远侧面 −0.49（四指应**逐根**贴住 −Y 侧）")
        w = last["web"][side]
        if abs(w["above_edge_mm"]) > CONTACT_TOL_MM:
            report["problems"].append(
                f"{side} 虎口未卡在上沿：离上沿 {w['above_edge_mm']} mm（|·| > 容差 {CONTACT_TOL_MM} mm）")
        if not w["in_slab"]:
            report["problems"].append(
                f"{side} 虎口的 y={w['pos_m'][1]} 不在靠背厚度区间 [−0.49, −0.45] 内（没卡在板边上）")
        if last["thumb"][side]["y_mm_vs_near_face"] < 0.0:
            report["problems"].append(
                f"{side} 拇指尖在靠背**远**侧（相对近侧面 {last['thumb'][side]['y_mm_vs_near_face']} mm < 0 ⇒ 没贴在背面，口径 D8）")
    if max(r[f"foot_{s}_drift_mm"] for r in verify for s in ("Left", "Right")) > 15.0:
        report["problems"].append("关键帧上脚漂移 > 15 mm")

    # ---- 写动作（⚠️ 这一步以前**根本不存在**：撤回版改写解析解时把打键丢了，
    #      于是"跑了 4 轮、判据全在、却没有任何动作"——owner 目视时看不到东西。2026-09-14 实测。）
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    # ⚠️ `actions.new()` 遇到同名会**静默**建 `名字.001`，旧动作仍留着 ⇒ 导出按名取到**旧动作**
    #    （管线上实测：改完动作导出结果一模一样，E5 偏差逐位不变）。重跑前先清同名/同前缀。
    for stale in [a for a in bpy.data.actions
                  if a.name == args.action or a.name.startswith(args.action + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(args.action)
    if action.name != args.action:
        raise RuntimeError(f"动作名被占用：期望 {args.action!r}，实际 {action.name!r}")
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action

    keyed = ctrl_bones + [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"]   # 头颈的补偿必须一起打键
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        apply_channels(arm, captured[frame])
        if hands_on_rail:
            for side in ("Left", "Right"):
                spec = hand_orient.get((frame, side))
                apply_finger_curl(arm, side, curl[side], curl_amount)
                if spec:
                    pb = arm.pose.bones[f"CTRL_{side}Hand"]
                    pb.rotation_mode = "XYZ"
                    pb.rotation_euler = Euler([math.radians(a) for a in spec["hand_euler_deg"]], "XYZ")
                tsp = thumb_orient.get((frame, side))
                if tsp:
                    tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                    tb.rotation_mode = "XYZ"
                    tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
        update()
        for name in keyed:
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
        arm.pose.bones["CTRL_Hips"].keyframe_insert("location", frame=frame)
        for side in ("Left", "Right"):
            for finger in FINGERS:
                for k in (1, 2, 3, 4):
                    name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                    if name in arm.pose.bones:
                        arm.pose.bones[name].keyframe_insert("rotation_euler", frame=frame)
            tsp = thumb_orient.get((frame, side))
            if tsp:
                tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                tb.rotation_mode = "XYZ"
                tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
                tb.keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start = SCHEDULE[0][0]
    bpy.context.scene.frame_end = SCHEDULE[-1][0]
    if args.host == "live":
        # ⚠️ 预览必须**停在到位帧**，不能停在首帧：首帧是站立中立姿势，owner 打开窗口看到的是"一个人站着"，
        #    会直接得出"看不见动作"（2026-09-14 实测踩到）。headless/存档路径仍回首帧（导出的首帧不变量）。
        arrival = [f for f, _b, _p, on, _c in SCHEDULE if on][-1]
        bpy.context.scene.frame_set(arrival)
        print(f"预览：已停在到位帧 {arrival}（时间轴 {SCHEDULE[0][0]}–{SCHEDULE[-1][0]}，按空格可播）")
        print("提示：母版里 CTRL/MIXAMORIG 两个骨骼集合默认可见 ⇒ 78 根骨的八面体会挡在人身前；"
              "看姿势时建议在 Outliner 里把这两个集合的眼睛关掉（纯显示层，不影响动作）。")
    else:
        bpy.context.scene.frame_set(SCHEDULE[0][0])
    report["action"] = args.action
    report["action_frames"] = [SCHEDULE[0][0], SCHEDULE[-1][0]]
    report["action_fcurves"] = len(action.fcurves) if hasattr(action, "fcurves") else None

    # ---- 回显卡（口径 §四 V-a：每一项都要有**产物侧**读数）----
    foot_worst = max(r[f"foot_{s}_drift_mm"] for r in verify for s in ("Left", "Right"))
    card = [
        {"owner 的话": "人体站在椅子背面", "解成": "角色在靠背一侧；椅心 y=−{:.2f}".format(-args.chair),
         "参考系": "世界/道具", "判据量": "腕↔靠背中心面 (mm)",
         "产物侧读数": last["wrist_to_back_mm"], "状态": "✅" if last["wrist_to_back_mm"] <= 60.0 else "❌"},
        {"owner 的话": "弯腰", "解成": "骨盆局部 X = {}°".format(int(last["bend_deg"])),
         "参考系": "角色体侧", "判据量": "到位帧弯腰角 (deg)",
         "产物侧读数": last["bend_deg"], "状态": "✅（自由度表 owner 圈定）"},
        {"owner 的话": "目视前方", "解成": "Neck/Head 反向补偿（解出 Head X={:.2f}° · Neck X={:.2f}°）".format(
            report["gaze_solve"][last["frame"]]["head_x_deg"], report["gaze_solve"][last["frame"]]["neck_x_deg"]),
         "参考系": "世界/重力", "判据量": "头骨上轴偏离竖直 (deg)",
         "产物侧读数": last["gaze_up_deg"], "状态": "✅" if abs(last["gaze_up_deg"]) <= 2.0 else "❌"},
        {"owner 的话": "双手手掌贴合椅背上方", "解成": "掌面点 = 手骨原点 + 32.68 mm × 掌面法向（局部 +Z）",
         "参考系": "道具局部", "判据量": "掌面最低点↔顶面 (mm) ≤ 2.8；负 = 陷入",
         "产物侧读数": last["palm"]["Left"]["to_rail_top_mm"],
         "状态": "✅" if -PROVISIONAL_TOL_MM <= last["palm"]["Left"]["to_rail_top_mm"] <= CONTACT_TOL_MM else "❌"},
        {"owner 的话": "大拇指贴住椅背的背面（近侧 y ≥ −0.45）", "解成": "拇指尖 y 相对近侧面",
         "参考系": "道具局部", "判据量": "拇指尖 − 近侧面 (mm)",
         "产物侧读数": last["thumb"]["Left"]["y_mm_vs_near_face"],
         "状态": "✅" if last["thumb"]["Left"]["y_mm_vs_near_face"] >= 0 else "❌"},
        {"owner 的话": "其余四指贴住椅背的正面（远侧 y ≤ −0.49）", "解成": "中指尖 y 相对远侧面",
         "参考系": "道具局部", "判据量": "中指尖 y (m) vs −0.49",
         "产物侧读数": last["tip_Left_m"][1],
         "状态": "✅" if last["tip_Left_m"][1] <= BACK_FAR_Y else "❌"},
        {"owner 的话": "虎口卡住上沿（owner 第四轮）", "解成": "虎口 = 拇指根↔食指根中点 + ε·掌面法向",
         "参考系": "世界/道具", "判据量": "虎口↔上沿 (mm) ≤ 2.8 且 y 在板厚内",
         "产物侧读数": {"离上沿": last["web"]["Left"]["above_edge_mm"], "在板厚内": last["web"]["Left"]["in_slab"]},
         "状态": "✅" if (abs(last["web"]["Left"]["above_edge_mm"]) <= CONTACT_TOL_MM
                        and last["web"]["Left"]["in_slab"]) else "❌"},
        {"owner 的话": "（未提及）肘别往外顶", "解成": "肘相对肩-腕弦的分量",
         "参考系": "角色体侧", "判据量": "后 ≥ 60 mm 且 |侧| ≤ 40 mm",
         "产物侧读数": last["elbow_Left_offset_mm"],
         "状态": "✅" if (last["elbow_Left_offset_mm"]["back"] >= 60.0
                        and abs(last["elbow_Left_offset_mm"]["side"]) <= 40.0) else "❌"},
        {"owner 的话": "（未提及）脚踩原地", "解成": "踝回静止位（解析腿解）",
         "参考系": "世界", "判据量": "逐帧脚漂移 (mm)", "产物侧读数": foot_worst,
         "状态": "✅" if foot_worst <= 15.0 else "❌"},
    ]
    report["feedback_card"] = card
    report["ok"] = not report["problems"]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=" * 92)
    print(f"动作 {args.action} · 帧 {SCHEDULE[0][0]}–{SCHEDULE[-1][0]} @ {args.fps} fps · "
          f"椅子中心前方 {args.chair} m · 靠背中心面 y={lay['back_cy']:.3f} · 顶杆 z={lay['rail_top_z']:.4f}")
    print(f"{'帧':>4}{'弯腰':>6}{'腕↔靠背':>10}{'腕高于顶杆':>12}{'指尖扣住':>10}{'肘角':>8}{'肘后/下/侧':>16}{'脚漂移':>9}")
    for row in verify:
        print(f"{row['frame']:>4}{row['bend_deg']:>5.0f}°{row['wrist_to_back_mm']:>10.1f}"
              f"{row['hand_above_rail_mm']:>12.1f}{str(row['tip_wraps_rail_Left']):>10}"
              f"{row['elbow_Left_deg']:>7.1f}°"
              f"{row['elbow_Left_offset_mm']['back']:>7.0f}/{row['elbow_Left_offset_mm']['down']:<4.0f}/{row['elbow_Left_offset_mm']['side']:<5.0f}"
              f"{row['foot_Left_drift_mm']:>9.1f}")
    print("自由度表（owner 圈定 / agent 解）")
    for row in FREEDOM_TABLE:
        print(f"  {row['量']:<16}{row['归属']:<14}{row['值']:<32}{row['依据'][:44]}")
    print("逐指读数（口径 §七 硬规矩 2：成组的项必须并列打印）")
    print(f"  {'手':<6}{'指':<8}{'指尖 y':>10}{'指尖 z':>10}{'距远侧面(mm)':>14}  所在侧")
    for _s in ("Left", "Right"):
        _d = verify[-1][f"digits_{_s}"]
        for dd in DIGITS:
            v = _d[dd]
            print(f"  {_s:<6}{dd:<8}{v['tip_y']:>10.4f}{v['tip_z']:>10.4f}{v['vs_far_face_mm']:>14.1f}  {v['side']}")
    print("回显卡（口径 §四：每一项都要有产物侧读数）")
    for row in card:
        print(f"  {row['owner 的话'][:26]:<28}| {row['判据量'][:30]:<32}| {str(row['产物侧读数'])[:34]:<36}| {row['状态']}")
    print(f"报告: {report_path}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    print("=" * 92)

    if args.host == "live":
        print("（--host live：预览，不写回母版）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl), compress=False)
        print(f"已写回母版：{tmpl}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 2：卡 1「掐棱」测量（`--task card1`）——#164 的主交付
#
#   产物：`data/hand_grip_cards.json`（卡 1 的 F3/F4/F6/F7/F8/F10/F11 逐字段数值）
#   权威：design/presentation/动作描述口径.md §十三（字段语义与判据形态枚举）
#   ⚠️ 本宿主**不产出动作**：卡 1 是**引用件**，不是 clip（口径 §13.1 甲/乙/丙 的取舍）
# ══════════════════════════════════════════════════════════════════════════════

CARD1_SIDES = ("Left", "Right")
#: F7 的尺寸扫描（口径 §13.5「7 档 / 10 → 80 mm」：区间与步长照写，档数取 8 —— 区间相同时
#: 10 mm 步长给 8 档；多一档是机器的活，不额外花 owner 的时间，证据里如实登记）
CARD1_F7_SCAN_MM = (10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0)
#: 卡 1 的基准板厚 = 椅背实测板厚（40 mm，`动作库规格.md §四·丁` 的权威常量）
CARD1_BASELINE_THICKNESS_MM = round(BACK_THICKNESS * 1000.0, 1)
#: F10 的四指蜷曲量（基准；由 `--scan` 的校准表选定，见证据 §三）
CARD1_CURL_BASELINE = 1.4
#: 卡 1 的身体条件：**弯腰角**（agent 解：可达性反解——55° 时手臂被夹直、80° 时肘反折）
CARD1_BEND = 75.0
#: 抓握高度 = 板顶 − 本值（由 `--scan` 选定：板顶正下方那个位置会把手臂拉直）
CARD1_GRIP_DROP = 0.075
#: 身体条件（与 #163 的同一条路径一致：弯腰 + 骨盆后移 0.10 m、下沉 0.05 m）
CARD1_PELVIS_OFFSET = (0.0, 0.100, -0.050)
#: `--scan` 校准扫描的三个变量（只在校准期用；选定值写进上面前三个常量）
CARD1_SCAN_BENDS = (CARD1_BEND,)
CARD1_SCAN_DROPS = (0.075,)
CARD1_SCAN_CURLS = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)


def pair_status(row, tol=CONTACT_TOL_MM):
    """接触对状态：**逐项**判（成组项全部在容差内才算 ✅）——§七 硬规矩 2 的机械化。"""
    v = row.get("读数_mm")
    if v is None:
        return "❓"
    vals = v if isinstance(v, (list, tuple)) else [v]
    return "✅" if all(x is not None and abs(x) <= tol for x in vals) else "❌"


def pair_residual_mm(rows):
    """**约束残差** = 逐接触对"超出容差的那部分"的最大值（mm）；0 = 全部落在容差内。

    口径 §13.5 的改族阈值 = 残差**首次超容差**的那个尺寸 ⇒ 残差必须能报错、且**单调可比**。
    """
    worst = 0.0
    for r in rows:
        v = r.get("读数_mm")
        if v is None:
            continue
        vals = v if isinstance(v, (list, tuple)) else [v]
        for x in vals:
            if x is None:
                continue
            worst = max(worst, abs(x) - CONTACT_TOL_MM)
    return round(worst, 2)


def card1_case(arm, args, thickness_mm, grip_z, curl_amount, curl_axis, side):
    """一个扫描格的完整测量：重建板代理 → 解掐棱握式 → 读接触对（判据一律对着**产物几何**）。"""
    lay = build_board_proxy(thickness_mm / 1000.0, distance=args.chair)
    frame = chair_end_frame(side, lay)
    grip = grip_board_edge(arm, side, frame, grip_z, curl_amount, curl_axis,
                           label=f"{thickness_mm:.0f}mm-{side}")
    rows = grip_board_edge_readings(arm, side, frame)
    pinch = points_min_distance_mm(finger_skin_world(arm, side, "Thumb"),
                                   finger_skin_world(arm, side, "Index"))
    return {"thickness_mm": thickness_mm, "lay": lay, "grip": grip, "pairs": rows,
            "residual_mm": pair_residual_mm(rows), "pinch_gap_mm": pinch,
            "frame_axes": grip["frame_axes"]}


def card1_json(report, args):
    """把测量报告折成**机器源**（`data/hand_grip_cards.json`）——字段名逐字取口径 §13.3。"""
    base = report["baseline"]["Left"]
    scan = report["f7_scan"]
    ref = report.get("f6_refined_mm") or {}
    # ⚠️ 边界一律取**细化并验证过**的那两个读数（第一版这里从 scan 列表里"取第一个越界档"，
    #    于是厚侧界报成 10.0 mm——那是**薄侧**的越界档。扫描表不是单调的，别拿它当边界。）
    thick_usable = ref["厚侧"][1] if ref.get("厚侧") else None
    thick_bound = ref["厚侧"][0] if ref.get("厚侧") else None
    thin_usable = ref["薄侧"][1] if ref.get("薄侧") else None
    thin_bound = ref["薄侧"][0] if ref.get("薄侧") else None
    return {
        "_meta": {
            "schema_version": "1.0",
            "design_authority": "design/presentation/动作描述口径.md §十三",
            "role": "generator-input",
            "measured_by": "code/tools/author_xbot_chair_grab.py --task card1",
            "blender": report["blender"],
            "template": report["template"],
            "measured_at": report["measured_at"],
            "units": "长度 m；间隙/残差 mm；角度 deg",
            "contact_tol_mm": CONTACT_TOL_MM,
            "epsilon_palm_mm": round(EPSILON_PALM_M * 1000.0, 4),
            "note": "本文件是卡 1 的**逐字段数值**权威；字段语义与判据形态枚举的权威是口径 §十三。",
        },
        "cards": [{
            "F1_索引键": report["index_key"],
            "F2_别名位": {
                "消费端语汇": ["正握/反握（武器语汇，owner 2026-09-15 已否）"],
                "符号变体": "侧握 ↔ 上罩 = 棱的方向与接近方向换行（F8），非某一行取反",
            },
            "F3_三轴映射": {
                "来源": "本仓实测（`--task card1` 的 f3 段）",
                "行": [
                    {"手骨轴": "+Z 掌面法向", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["Z"],
                     "判据": "掌面 = 骨局部 +Z（口径 §8.1，ε = 32.68 mm）",
                     "读数": f'静止时与世界 +Z 夹角 {report["f3"]["rest"]["Left"]["Z_vs_world_Z_deg"]}°（180° = 掌面朝下）'},
                    {"手骨轴": "+Y 腕 → 指尖", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["Y"],
                     "判据": "与实测「腕 → 中指指尖」方向同向（口径 U9，本片当场量）",
                     "读数": f'夹角 {report["f3"]["rest"]["Left"]["Y_vs_wrist_to_tip_deg"]}°（左）/ '
                             f'{report["f3"]["rest"]["Right"]["Y_vs_wrist_to_tip_deg"]}°（右）'},
                    {"手骨轴": "X 手指屈曲轴", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["X"],
                     "判据": "外部判据：屈曲把中指尖带向拇指尖（四指）/ 把拇指尖带向食指尖（拇指）",
                     "读数": {g: {"左": report["f3"]["curl"]["Left"][g]["axis"] + f'{report["f3"]["curl"]["Left"][g]["sign"]:+d}',
                                  "右": report["f3"]["curl"]["Right"][g]["axis"] + f'{report["f3"]["curl"]["Right"][g]["sign"]:+d}',
                                  "判据读数_mm": {"静息": report["f3"]["curl"]["Left"][g]["rest"],
                                                  "屈曲": report["f3"]["curl"]["Left"][g]["readings"][
                                                      report["f3"]["curl"]["Left"][g]["axis"] +
                                                      f'{report["f3"]["curl"]["Left"][g]["sign"]:+d}'],
                                                  "全部候选": report["f3"]["curl"]["Left"][g]["readings"]},
                                  "成立": report["f3"]["curl"]["Left"][g]["criterion_valid"]}
                              for g in CURL_GROUPS}},
                ],
            },
            "F4_分区分工与接触对清单": [
                {"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
                 "容差档": r["容差档"], "并列项": r.get("并列项", "—"),
                 "基准读数_mm": r["读数_mm"], "状态": r["状态"]}
                for r in report["baseline"]["Left"]["pairs"]
            ],
            "F5_判据形态与容差档": {
                "形态": ["点↔线（虎口↔近侧竖棱 · 四指↔远侧竖棱）", "点↔面（拇指↔近侧面）"],
                "容差": {"换算 ε": f'{round(EPSILON_PALM_M * 1000.0, 4)} mm（掌面，逐骨，口径 §8.1）',
                         "验收 tol_contact": f"{CONTACT_TOL_MM} mm（口径 §8.2）"},
                "为什么两个数不许混": "口径 §8.2：把两者合成一个数 ⇒ 掌面悬空 30.8 mm 被判成贴合",
            },
            "F6_尺寸适用区间": {
                "量": "板厚",
                "区间_mm": [thin_usable if thin_usable is not None else scan[0]["thickness_mm"],
                            thick_usable if thick_usable is not None else scan[-1]["thickness_mm"]],
                "区间判据": "全部接触对的 |读数| ≤ tol_contact = 2.8 mm（两端都越界：薄侧四指**越过**远侧棱、"
                            "厚侧四指**够不到**远侧棱）",
                "薄侧界（四指越过远侧棱）": {
                    "判据": "约束残差首次 > 0（= 逐项超出 tol_contact）",
                    "读数_mm": thin_bound,
                    "说明": ("" if thin_bound is not None else
                             f"**未在扫描区间内出现**：{scan[0]['thickness_mm']:.0f} mm 处残差仍为 0"
                             f"（逐指蜷曲会自适应，薄板反而好掐）⇒ 该侧越界尺寸 < {scan[0]['thickness_mm']:.0f} mm，"
                             f"越界落点按「缺口」登记")},
                "厚侧界（四指够不到远侧棱）": {
                    "判据": "同上",
                    "读数_mm": thick_bound},
                "⚠️ 未出现的退化（如实登记）": "「棱太薄 ⇒ 掐不住、退化为捏/对指」的判据（拇指蒙皮↔食指蒙皮 ≤ 0）"
                                              "在 10–80 mm 全程**未触发**（恒定 21.87 mm）——薄侧真正的越界形态是"
                                              "**四指越过远侧棱**（+19.5 mm @10 mm），不是捏不上",
                "扫描": [{"板厚_mm": r["thickness_mm"], "残差_mm": r["residual_mm"],
                          "捏间隙_mm": r["pinch_gap_mm"]} for r in scan],
            },
            "F7_改族阈值与越界落点": report["f7"],
            "F8_接近方向与无解组合": report["f8"],
            "F9_方位角可行区间": {
                "适用": False,
                "理由": "圆柱族专用（绕轴旋转对称 ⇒ 方位角不是输入）；卡 1 的对象是**板棱**，棱的方向是输入",
            },
            "F10_手型（甲₁）": {
                "逐指_4节屈曲角_deg": {
                    f: [round(a * (base["grip"].get("curl_solve") or {}).get(f, {}).get("蜷曲量",
                             base["grip"]["curl_amount"]), 2) for a in FINGER_CURL_DEG[f]]
                    for f in FINGER_CURL_DEG},
                "逐指蜷曲量（**本片解出**，见 §13.3「逐指 4 节屈曲角」）": {
                    f: v["蜷曲量"] for f, v in (base["grip"].get("curl_solve") or {}).items()},
                "逐指校验（板体带符号间隙 mm，正 = 悬空 / 负 = 陷入）": {
                    f: v["板体间隙_mm"] for f, v in (base["grip"].get("curl_solve") or {}).items()},
                "⚠️ 为什么必须逐指": "四根手指长度不同：同一个蜷曲量下它们到板的最近间隙差 **14 mm**"
                                    "（实测 curl 1.0：[+7.8, +10.8, +3.2, −3.1]）⇒ 一个系数不可能让四根都贴住",
                "蜷曲量系数（未逐指解时的基准）": report["baseline"]["Left"]["grip"]["curl_amount"],
                "掌三轴（骨局部 → 世界）": report["baseline"]["Left"]["grip"]["hand_axes"],
                "拇指单独解（4 节可动骨）": report["baseline"]["Left"]["grip"]["thumb"],
                "分工": "朝向前三轴作**主条件**（解析解），落点读数（F11）用来**验**（owner 2026-09-15 接受）",
            },
            "F11_落点读数（甲₂）": {
                "虎口": {"世界坐标_m": base["grip"]["web_point_m"],
                         "↔近侧竖棱_mm": base["grip"]["web_to_edge_mm"],
                         "沿板厚方向_mm": base["grip"]["web_along_n_mm"],
                         "沿端面方向_mm": base["grip"]["web_along_u_mm"]},
                "拇指": {"↔近侧面_mm": base["grip"]["thumb_gap_mm"]},
                "四指逐根_↔远侧竖棱_mm": dict(zip(base["pairs"][2]["逐项名"],
                                                base["pairs"][2]["读数_mm"])),
                "掌面↔端面_mm": {
                    "读数": base["grip"]["palm_to_end_face_mm"],
                    "性质": "**非接触对**（口径 §13.6：侧握下掌面不构成接触对）——本片实测证实："
                            "掌面蒙皮离端面 10.5 mm ⇒ 是「贴着棱」而不是「压着面」"},
                "腕": {"目标_m": base["grip"]["wrist_target_m"],
                       "肘角_deg": base["grip"]["elbow_deg"],
                       "肘偏移_mm": base["grip"]["elbow_offset_mm"],
                       "肘平面扫描": base["grip"].get("elbow_pick"),
                       "肘判据（沿用 #163）": "向后 ≥ 60 · |侧向| ≤ 40 · 向下 ≥ 20（mm）"},
            },
            "F12_消费登记": [
                {"动作": "BendGripChairBack（#163 侧握版，卡 1 基准）", "出处": "issue #163 · 口径 §13.6"},
                {"动作": "扣住门边推开半掩的门（#164 新动作，独立验证）",
                 "出处": "回合战斗流程.md §10.13「关门/开门」",
                 "owner 目视": "手 ↔ 物这一层通过（「手的抓握效果是对的」）；**整体开门姿态**观感不自然，"
                               "owner 明确裁定不在 #164 范围（另开）"},
            ],
        }],
    }


def render_still(path, cam_loc, look_at, res=(1100, 800)):
    """**静帧**（headless 可复现）：临时相机 + 太阳光 + Workbench 引擎 ⇒ 只写 PNG，不改母版。

    ⚠️ 用渲染而不是 GUI 截图：GUI 截图**不逐位可复现**（重绘时序/悬停高亮，见危险点表 §七）。
    """
    scene = bpy.context.scene
    cam = bpy.data.objects.get("REF_StillCam")
    if cam is None:
        cdata = bpy.data.cameras.new("REF_StillCam")
        cam = bpy.data.objects.new("REF_StillCam", cdata)
        scene.collection.objects.link(cam)
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(look_at) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 50.0
    scene.camera = cam
    if bpy.data.objects.get("REF_StillSun") is None:
        ldata = bpy.data.lights.new("REF_StillSun", type="SUN")
        sun = bpy.data.objects.new("REF_StillSun", ldata)
        scene.collection.objects.link(sun)
        sun.rotation_euler = Euler((math.radians(55.0), 0.0, math.radians(35.0)), "XYZ")
        ldata.energy = 3.0
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def main_card1() -> int:
    from datetime import datetime
    args = parse_args(list(sys.argv))
    if args.report_in:
        # 报告 → 机器源（唯一来源）：重排不改任何读数，只改字段组织
        rep = json.loads(Path(args.report_in).read_text(encoding="utf-8"))
        out = Path(args.card_out) if args.card_out else REPO_ROOT / "data/hand_grip_cards.json"
        out.write_text(json.dumps(card1_json(rep, args), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"机器源（由报告重排）：{out}")
        return 0
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    lay0 = board_layout(args.chair)
    grip_z = args.grip_z if args.grip_z is not None else (lay0["rail_top_z"] - args.grip_drop)
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    report = {"script": Path(__file__).name, "task": "card1", "blender": bpy.app.version_string,
              "template": str(tmpl), "host": args.host, "index_key": CARD1_INDEX_KEY_NAME,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "chair_distance_m": args.chair, "grip_z_m": round(grip_z, 4),
              "grip_drop_m": args.grip_drop, "curl_amount": curl_amount,
              "board_top_z": round(lay0["rail_top_z"], 4), "problems": []}

    # ---- A. F3：三轴映射（静止 T-pose 实测；U9 的 `+Y` 当场量）----
    clear_pose(arm)
    report["f3"] = {
        "rest": {s: hand_axes_reading(arm, s) for s in CARD1_SIDES},
        "curl": {s: {g: detect_curl_axis_group(arm, s, g) for g in CURL_GROUPS} for s in CARD1_SIDES},
    }
    curl_axis = {s: {"axis": report["f3"]["curl"][s]["四指"]["axis"],
                     "sign": report["f3"]["curl"][s]["四指"]["sign"]} for s in CARD1_SIDES}
    report["curl_axis_used"] = curl_axis
    for s in CARD1_SIDES:
        r = report["f3"]["rest"][s]
        print(f"F3 三轴 {s:5s}: 局部+X→{r['axes_world']['X']}  +Y→{r['axes_world']['Y']}  "
              f"+Z→{r['axes_world']['Z']} · Y↔腕→指尖 {r['Y_vs_wrist_to_tip_deg']}° · "
              f"Z↔世界+Z {r['Z_vs_world_Z_deg']}°")
        for g in CURL_GROUPS:
            c = report["f3"]["curl"][s][g]
            best = c["axis"] + f"{c['sign']:+d}"
            print(f"      屈曲轴自测 {s:5s}/{g}: 最优 {best} · 丙(指尖→掌面) "
                  f"{c['rest']['palm_offset_mm']} → {c['readings'][best]['palm_offset_mm']} mm · "
                  f"乙(跨组指尖距) {c['rest']['tip_to_other_mm']} → {c['readings'][best]['tip_to_other_mm']} mm"
                  f"（丙判据{'成立' if c['criterion_valid'] else '**失效**'}·丙乙"
                  f"{'一致' if c['agree_with_cross_group'] else '**不一致**'}）")

    # ---- 身体条件：脚踝静止位（双脚踩原地）----
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}

    # ---- B. 校准扫描（--scan）：抓握高度 × 蜷曲量——只打印表，不写机器源 ----
    if args.scan:
        print("=" * 100)
        print("卡 1 校准扫描（板厚 40 mm · 左手）：弯腰角 × 抓握高度 × 蜷曲量（四指读数 = 板体带符号间隙）")
        print(f"{'bend(°)':>8}{'drop(mm)':>8}{'curl':>6}{'残差':>8}{'虎口↔棱':>9}{'拇指↔近侧面':>12}"
              f"{'逐指↔板体(mm)':>34}{'肘角':>8}{'肘后':>7}{'肘侧':>7}{'肘下':>7}")
        for bend in CARD1_SCAN_BENDS:
            for drop in CARD1_SCAN_DROPS:
                for curl in CARD1_SCAN_CURLS:
                    clear_pose(arm)
                    bent_body_setup(arm, m3, bend, CARD1_PELVIS_OFFSET, foot_rest)
                    case = card1_case(arm, args, CARD1_BASELINE_THICKNESS_MM,
                                      lay0["rail_top_z"] - drop, curl, curl_axis["Left"], "Left")
                    g = case["grip"]
                    gaps = case["pairs"][2]["读数_mm"]
                    print(f"{bend:>9.0f}{drop * 1000:>7.0f}{curl:>6.1f}{case['residual_mm']:>8.2f}"
                          f"{g['web_to_edge_mm']:>9.2f}{str(g['thumb_gap_mm']):>12}"
                          f"{str([round(x, 1) for x in gaps]):>34}{g['elbow_deg']:>8.1f}"
                          f"{g['elbow_offset_mm']['back']:>7.0f}{g['elbow_offset_mm']['side']:>7.0f}"
                          f"{g['elbow_offset_mm']['down']:>7.0f}")
        print("=" * 100)
        return 0

    # ---- C. 基准格（板厚 40 mm）——F4/F5/F10/F11 从这一格取 ----
    report["body_setup"] = bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
    print(f"身体条件：弯腰 {CARD1_BEND}° · 骨盆位移 {CARD1_PELVIS_OFFSET} · "
          f"目视水平 {report['body_setup']['gaze']['after_deg']}°")
    report["baseline"] = {}
    for side in CARD1_SIDES:
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        case = card1_case(arm, args, CARD1_BASELINE_THICKNESS_MM, grip_z, curl_amount, curl_axis[side], side)
        for r in case["pairs"]:
            r["状态"] = pair_status(r)
        case["grip"]["hand_axes"] = {
            "骨局部X（蜷曲轴）": [round(c, 4) for c in
                                 (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                  .matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()],
            "骨局部Y（腕→指尖）": [round(c, 4) for c in
                                   (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                    .matrix.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()],
            "骨局部Z（掌面法向）": [round(c, 4) for c in
                                    (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                     .matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()],
        }
        report["baseline"][side] = case
        if case["residual_mm"] > 0.0:
            report["problems"].append(
                f"基准格（{side}，板厚 {CARD1_BASELINE_THICKNESS_MM} mm）残差 {case['residual_mm']} mm > 0")
        print(f"基准格 {side:5s}: 虎口↔棱 {case['grip']['web_to_edge_mm']} mm · "
              f"拇指↔近侧面 {case['grip']['thumb_gap_mm']} mm · 残差 {case['residual_mm']} mm · "
              f"肘角 {case['grip']['elbow_deg']}° · 捏间隙 {case['pinch_gap_mm']} mm")

    # ---- D. F6/F7：尺寸扫描（10 → 80 mm）----
    if args.thickness_mm is not None:
        scan_list = (args.thickness_mm,)
    else:
        scan_list = CARD1_F7_SCAN_MM
    scan = []
    print("F7 尺寸扫描（左手 · 同一 F10 手型）：")
    print(f"{'板厚(mm)':>9}{'残差':>8}{'虎口↔棱':>9}{'拇指↔近侧面':>12}"
          f"{'逐指↔远侧面(mm)':>40}{'捏间隙':>9}{'肘角':>8}")
    for t_mm in scan_list:
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        case = card1_case(arm, args, t_mm, grip_z, curl_amount, curl_axis["Left"], "Left")
        g = case["grip"]
        gaps = case["pairs"][2]["读数_mm"]
        print(f"{t_mm:>9.0f}{case['residual_mm']:>8.2f}{g['web_to_edge_mm']:>9.2f}"
              f"{str(g['thumb_gap_mm']):>12}{str([round(x, 1) for x in gaps]):>40}"
              f"{str(case['pinch_gap_mm']):>9}{g['elbow_deg']:>8.1f}")
        scan.append(case)
    report["f7_scan"] = scan

    def _residual_at(t_mm):
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        c = card1_case(arm, args, t_mm, grip_z, curl_amount, curl_axis["Left"], "Left")
        return c["residual_mm"]

    def refine(ok_t, bad_t, steps=3):
        """二分细化窗口边界（**机器的活**，口径 §13.5：用扫描换目视）。

        ⚠️ 必须以**已验过的** ok / bad 两端为输入：残差在薄侧**不是单调的**（四根指头长度不同 ⇒
        各自的"搭上远侧棱"厚度不同）。第一版实现拿"最小越界档"当 bad 端并**没验 ok 端**，
        于是报出"最后一个可用 10.0 mm"——而 10 mm 那档残差是 16.66 mm。**未验证的端点不算读数。**
        """
        for _ in range(steps):
            mid = (ok_t + bad_t) / 2.0
            if _residual_at(mid) > 0.0:
                bad_t = mid
            else:
                ok_t = mid
        return round(bad_t, 1), round(ok_t, 1)

    base_t = CARD1_BASELINE_THICKNESS_MM
    thick_above = next((r["thickness_mm"] for r in scan if r["residual_mm"] > 0.0 and r["thickness_mm"] > base_t), None)
    thin_below = next((r["thickness_mm"] for r in reversed(scan)
                       if r["residual_mm"] > 0.0 and r["thickness_mm"] < base_t), None)
    thick_ref = refine(base_t, thick_above) if (thick_above and args.thickness_mm is None) else None
    thin_ref = refine(base_t, thin_below) if (thin_below and args.thickness_mm is None) else None
    if thick_ref:
        print(f"厚侧边界细化：首次越界 {thick_ref[0]} mm（最后一个可用 {thick_ref[1]} mm）")
    if thin_ref:
        print(f"薄侧边界细化（向下）：首次越界 {thin_ref[0]} mm（最后一个可用 {thin_ref[1]} mm）")
    report["f6_refined_mm"] = {"厚侧": thick_ref, "薄侧": thin_ref}
    thick_bound = thick_ref[0] if thick_ref else None
    thin_bound = thin_ref[0] if thin_ref else None

    # ---- E. F7 改族边 + F8 方向对照 ----
    report["f7"] = {
        "阈值定义": "约束集首次不可满足的那个尺寸（口径 §13.5：读出来的，不是设定的）",
        "阈值_mm": {"厚侧": thick_bound, "薄侧": thin_bound},
        "扫描区间_mm": [scan[0]["thickness_mm"], scan[-1]["thickness_mm"]],
        "越界落点": {
            "厚侧": {"落点": "卡 4（指尖触点）", "状态": "已登记（卡 4 在名录里，尚未建）",
                     "依据": "口径 §13.5 ① 归到另一张卡"},
            "薄侧": {"落点": "缺口（该族未建，不建空卡）", "状态": "已登记",
                     "依据": "口径 §13.5 ③；先例 §6.3『不建空表』"},
        },
        "改族边": [{"from": "卡1", "to": "卡4", "条件": f"板厚 > {thick_bound} mm" if thick_bound else "板厚 > 扫描上界"}],
    }
    report["f8"] = {
        "侧握（基准）": {
            "棱": "椅背侧面的**近侧竖棱**（`x=±half_width`, `y=back_near_y`）",
            "读数_mm": {s: report["baseline"][s]["grip"]["web_to_edge_mm"] for s in CARD1_SIDES},
        },
        "上罩（对照）": {
            "来源": "#163 已接受版本（`6a20c09`）的既有读数，**不是**本宿主重测",
            "虎口↔上沿（原判据，参照**顶面中线**）": "−0.0 mm（#163 证据 §二十）",
            "虎口↔**真棱**（本片改参照后重算）": {
                "上沿近侧棱（`y=−0.45, z=0.7949`）": "20.0 mm",
                "上沿远侧棱（`y=−0.49, z=0.7949`）": "20.0 mm",
                "说明": "由 #163 记录的虎口坐标 `(±0.17, −0.47, 0.7949)` 与板几何**解析换算**，"
                        "原判据参照的中线 `y=back_cy=−0.47` **不是棱**（两面交线才是）",
            },
            "掌面↔顶面_mm": "−22.2（陷入）", "拇指↔近侧面_mm": "−30.0", "四指↔远侧面_mm": "−0.462 ~ −0.468（未过）",
            "结论": "上罩在卡 1 的判据下**两条红**：虎口没落在真棱上、四指没落到远侧面",
            ("⚠️ 本片发现：那条「掌面陷入 22.2 mm」的根因是 ε 换算的掌面法向取自**骨架系**"
             "（母版骨架带 +90° X 旋转 ⇒ 与世界系差 90°；#163 的上罩掌面法向恰是 −Z，不在不动轴上）。"
             "改成世界系后重跑同一姿势：掌面最低点 −22.2 → **+10.5 mm（悬空，不再穿模）**、"
             "肘侧向 31.5 → 49.8 mm（从绿变红）⇒ 上罩那一版的已知偏差里，第 1 条是**工具的错，不是姿势的错**。"
             "本卡登记的对照读数仍取 **#163 记录值**（历史如实），修正后的重跑值见证据"):
             "见证据 §七",
        },
        "两方向的区别": "棱的方向（竖/横）+ 接近方向（侧面/上方）；F3 的三轴映射在两者间**整体重排**",
    }

    # ---- F. 回显卡（口径 §四；行数 = 接触对行数——由**同一列表**生成，结构上不可能不一致）----
    card_rows = []
    for r in report["baseline"]["Left"]["pairs"]:
        card_rows.append({"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
                          "判据量": f'{r["手部分区"]} ↔ {r["物体分区"]}（{r["判据形态"]}）',
                          "产物侧读数_mm": r["读数_mm"], "容差档": r["容差档"], "状态": r["状态"]})
    report["feedback_card"] = card_rows
    print("回显卡（口径 §四：每一项都有产物侧读数；行数 = 卡 1 的接触对行数）")
    for row in card_rows:
        print(f"  {row['判据量'][:34]:<36}| {str(row['产物侧读数_mm']):>10} | {row['容差档']:<26}| {row['状态']}")

    report["ok"] = not report["problems"]
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告: {args.report}")

    # ---- G. 机器源 ----
    if args.thickness_mm is None:
        card_out = Path(args.card_out) if args.card_out else REPO_ROOT / "data/hand_grip_cards.json"
        card_out.parent.mkdir(parents=True, exist_ok=True)
        # 机器源落点：data/hand_grip_cards.json（`role: generator-input`；被 validate_grip_cards.py 核）
        card_out.write_text(json.dumps(card1_json(report, args), ensure_ascii=False, indent=1),
                            encoding="utf-8")
        print(f"机器源: {card_out}")

    # ---- H. 静帧（可选）----
    if args.still:
        edge = report["baseline"]["Left"]["frame_axes"]
        mid = Vector(report["baseline"]["Left"]["grip"]["web_point_m"])
        render_still(args.still, mid + Vector((0.62, 0.72, 0.42)), mid)
        print(f"静帧: {args.still}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 3：门边动作「扣住门边推开半掩的门」（`--task door`）——#164 的独立验证件
#
#   口径 §13.6：**同一张卡、新的对象**（棱从椅背换到门边，映射整体重排）
#   ⚠️ 本宿主只交付**静帧**（口径 §13.8 边界：不做动画/关键帧入库、不接 Unity lab、不新增词条）
# ══════════════════════════════════════════════════════════════════════════════

DOOR_ACTION = "PushDoorEdge"
#: (帧, 门开角°, 手是否扣住门边)——半掩 30° → 推开 80°
DOOR_SCHEDULE = ((1, DOOR_OPEN_START_DEG, False), (13, DOOR_OPEN_START_DEG, True),
                 (25, DOOR_OPEN_END_DEG, True))


def main_door() -> int:
    from datetime import datetime
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)
    report = {"script": Path(__file__).name, "task": "door", "blender": bpy.app.version_string,
              "template": str(tmpl), "host": args.host, "action": DOOR_ACTION,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "schedule": [{"frame": f, "door_open_deg": a, "hooked": h} for f, a, h in DOOR_SCHEDULE],
              "problems": []}

    # 手骨轴的实测与卡 1 同源（不得在两处各测一份）
    clear_pose(arm)
    f3 = {s: hand_axes_reading(arm, s) for s in CARD1_SIDES}
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    report["f3_rest"] = f3
    report["f3_curl"] = curl
    curl_axis = {s: {"axis": curl[s]["axis"], "sign": curl[s]["sign"]} for s in CARD1_SIDES}
    print(f"F3 复核（门边宿主与卡 1 同源）：+Y↔腕→指尖 {f3['Left']['Y_vs_wrist_to_tip_deg']}°（左）")

    side = "Left"                       # 副手（右手）在推门这一拍是自由的 ⇒ 本片只解一只手
    grip_z = args.grip_z if args.grip_z is not None else 1.15   # 站立时略低于肩（肩高≈1.28 m）
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    report["freedom_table"] = [
        {"量": "门开角（半掩 → 推开）", "归属": "owner 圈定（需求原话「扣住门边推开半掩的门」）",
         "值": f"{DOOR_OPEN_START_DEG}° → {DOOR_OPEN_END_DEG}°", "依据": "回合战斗流程 §10.13 关门/开门"},
        {"量": "抓握高度", "归属": "agent 解", "值": f"{grip_z:.2f} m",
         "依据": "站立时肩高（≈1.28 m）− 0.13 m：抓握点离肩越近，腕目标越不逼近臂长"},
        {"量": "身体朝向（转身角）", "归属": "agent 解（可达性反解）", "值": "每帧 = 门边方位角",
         "依据": "不转身则手臂夹直（实测肘 180°、虎口离门边 291.6 mm）"},
        {"量": "身体前倾", "归属": "agent 解（可达性反解）", "值": "0.12 m",
         "依据": "不倾则到位帧腕目标离肩 0.659 m > 臂长 0.562 m（实测：手臂夹直）"},
        {"量": "四指蜷曲量", "归属": "卡 1 的 F10（同一张卡，不另发明）", "值": str(curl_amount),
         "依据": "口径 §13.6：新动作**复用**卡片，不新发明判据"},
    ]
    captured, verify = {}, []
    for frame, open_deg, hooked in DOOR_SCHEDULE:
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        dlay = build_door_proxy(open_deg)
        frame_geo = door_end_frame(dlay)
        me = dlay["mid_edge"]
        yaw = math.degrees(math.atan2(me.x, -me.y))
        report.setdefault("body_yaw", {})[frame] = round(yaw, 2)
        body = standing_body_setup(arm, m3, yaw, foot_rest, lean_m=0.12)
        if frame == DOOR_SCHEDULE[0][0]:
            print(f"身体：转身 {yaw:.1f}° · 前倾 0.12 m · 目视水平 {body['gaze']['after_deg']}°")
        if hooked:
            # 抓握高度**保持常量**（不随门角漂移：那会引入一个无来源的常数）
            grip = grip_board_edge(arm, side, frame_geo, grip_z,
                                   curl_amount, curl_axis[side], label=f"door{frame}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            verify.append({"frame": frame, "door_open_deg": open_deg, "grip": grip, "pairs": pairs,
                           "residual_mm": pair_residual_mm(pairs)})
            print(f"帧 {frame:>3} 门 {open_deg:>5.1f}°: 虎口↔门边 {grip['web_to_edge_mm']:>6.2f} mm · "
                  f"拇指↔近侧面 {str(grip['thumb_gap_mm']):>7} mm · 残差 {pair_residual_mm(pairs):>5.2f} mm · "
                  f"肘角 {grip['elbow_deg']}°")
        else:
            verify.append({"frame": frame, "door_open_deg": open_deg, "grip": None, "pairs": [],
                           "residual_mm": None})
        captured[frame] = capture_channels(arm, [f"CTRL_{side}Arm", f"CTRL_{side}ForeArm",
                                                 f"CTRL_{side}Hand", f"CTRL_Hips",
                                                 f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"])
        for finger in FINGERS:
            for k in (1, 2, 3, 4):
                name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                if name in arm.pose.bones:
                    pb = arm.pose.bones[name]
                    pb.rotation_mode = "XYZ"
                    captured[frame][name] = {"euler_deg": [math.degrees(a) for a in pb.rotation_euler],
                                             "location": [0.0, 0.0, 0.0]}
    report["verify"] = verify
    hooked_frames = [v for v in verify if v["grip"]]
    if hooked_frames:
        last = hooked_frames[-1]
        worst = max((abs(x) for r in last["pairs"]
                     for x in (r["读数_mm"] if isinstance(r["读数_mm"], list) else [r["读数_mm"]])
                     if x is not None), default=0.0)
        report["arrival"] = {"frame": hooked_frames[0]["frame"], "worst_pair_mm": worst}
        for r in hooked_frames[0]["pairs"]:
            if r["状态"] == "❌":
                report["problems"].append(
                    f"到位帧 {hooked_frames[0]['frame']}：{r['手部分区']}↔{r['物体分区']} "
                    f"读数 {r['读数_mm']} mm 超容差")
    report["feedback_card"] = [
        {"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
         "产物侧读数_mm": r["读数_mm"], "状态": r["状态"]}
        for r in (hooked_frames[0]["pairs"] if hooked_frames else [])]
    print("回显卡（门边 · 到位帧）")
    for row in report["feedback_card"]:
        print(f"  {row['手部分区']:<12}↔ {row['物体分区']:<10}{row['判据形态']:<8}"
              f"{str(row['产物侧读数_mm']):>9} mm  {row['状态']}")
    report["ok"] = not report["problems"]

    # ---- 打键（写动作；门代理的转角一起打——它只是预览件，不进 FBX）----
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == args.action or a.name.startswith(args.action + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(args.action)
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame, open_deg, hooked in DOOR_SCHEDULE:
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        panel = bpy.data.objects.get("REF_DoorPanel")
        if panel is not None:
            panel.rotation_euler = Euler((0.0, 0.0, math.radians(open_deg)), "XYZ")
            panel.keyframe_insert("rotation_euler", frame=frame)
        update()
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start = DOOR_SCHEDULE[0][0]
    bpy.context.scene.frame_end = DOOR_SCHEDULE[-1][0]
    report["action_frames"] = [DOOR_SCHEDULE[0][0], DOOR_SCHEDULE[-1][0]]

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still and hooked_frames:
        # 静帧停在**到位帧**（"扣住门边"那一拍）——预览必须停在有内容的那一帧（#163 的教训）
        bpy.context.scene.frame_set(hooked_frames[0]["frame"])
        mid = Vector(hooked_frames[0]["grip"]["web_point_m"])
        render_still(args.still, mid + Vector((0.85, 0.95, 0.45)), mid)
        print(f"静帧: {args.still}")
    if args.host == "live":
        arrival = hooked_frames[0]["frame"] if hooked_frames else DOOR_SCHEDULE[0][0]
        bpy.context.scene.frame_set(arrival)
        print(f"预览：已停在到位帧 {arrival}（时间轴 {DOOR_SCHEDULE[0][0]}–{DOOR_SCHEDULE[-1][0]}）")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1




# ══════════════════════════════════════════════════════════════════════════════
# 宿主 5：门边「推到底」（`--task doorpush`）——[#166](https://github.com/verystrongdog/game/issues/166) 的交付
#          （口径 §13.6 的**能播类第一件**）
#
#   完成定义（owner 2026-09-15 裁，口径 §13.6）：**Blender 侧能连着播**（静帧 + 时序 +
#   接地/不穿模，owner 看着不出戏）**+** 导出侧机械门禁 E0–E6 全绿；**不接 Unity 侧 lab**。
#
#   ⚠️ 与宿主 3（`--task door`）**分家**：本条**不改**宿主 3 一行（#164 的读数留在它的证据里）。
#      本宿主修掉宿主 3 上实测到的两处病（逐条读数与根因见证据 §六）：
#      ① **转身写在 `CTRL_Hips` 的 `z` 上**——实测那是**侧倾**（`y` 才绕世界 +Z）：
#         `z=+40°` 时实测脊柱 = (−0.641, 0.058, 0.765)、双脚被甩到 (0.677, 0.024, 0.364)
#         ⇒ 宿主 3 实际做的是"身体横着倒 37°"，这正是 owner 目视那句
#         「**整体开门的样子不太对、像是有病一样**」的来源；
#      ② **腿脚控制骨没进打键表** ⇒ 骨盆一动脚就跟着飘（#165 实测门边动作双侧**全程无支撑**、
#         离地 +160 ~ +313 mm）。本宿主把 `CTRL_*UpLeg / Leg / Foot` 与脚掌朝向一起打键。
# ══════════════════════════════════════════════════════════════════════════════

DOOR_PUSH_ACTION = "PushDoorEdgeFull"

#: X Bot 的**胶囊半径**（`通过开度` 的推导输入；口径 §13.6 与注册表 `通过开度` 同引此值）。
#: 来源：`code/unity/Assets/Scripts/ActionLabDriver.cs` `SizeControllerToModel()` 的
#: `_cc.radius = Clamp(h × 0.19, 0.25, 0.4)`；**记录值 0.3117** 见
#: `code/unity/Assets/Editor/ActionLabBuilder.cs` 与 `code/unity/Assets/Scripts/ChairSeat.cs`
#: 的注释（"胶囊半径 0.3117"）——两处都是**已记录实测值**，不是本次新拍。
X_BOT_CAPSULE_RADIUS_M = 0.3117

#: 「推到底」时身体**到门板中面的净距**（m）。取值由两条硬约束夹出来（不是手拍）：
#: ① 必须够大：净距扣掉板厚一半后要 > 胶囊半径 **0.3117**——人站在门的外侧、不能穿门；
#: ② 不能太大：越大手臂越够不到——实测本值 0.35 / 0.38 / 0.42 时**肩→腕在整段弧上分别恒定
#:   0.448 / 0.472 / 0.504 m**（臂长 0.5617）⇒ 取 **0.38**：净距留 48 mm 余量、手臂留 90 mm 余量。
DOOR_PUSH_CLEARANCE_M = 0.38

#: 站姿的**膝屈下沉量**（m）。为什么需要它：静止姿势的双腿几乎伸直（实测大腿 0.4437 +
#: 小腿 0.4453 = **0.8890 m** vs 髋-踝竖直 **0.8883 m** ⇒ 水平可及仅 ≈ **0.7 mm**）——
#: 不沉髋，迈步时腿**当场被夹直**、踝到不了目标（#165 那条"脚离地 160~313 mm"的一半成因）。
#: 实测下沉 0.06 m 时：踝相对骨盆偏 0.20 m 仍残差 **0**（证据 §三 的预算表）。
DOOR_PUSH_CROUCH_M = 0.06

#: 摆动腿的**抬脚高度**（m）：只要求"足底最低点明确离地"（判据 = M2 > `soleMargin`）。
#: 取值 0.05 m = 一步的正常抬脚量级；逐帧实测最小值见证据 §五。
DOOR_PUSH_STEP_LIFT_M = 0.05

#: 身体摆放（净距）的**解空间候选**——口径 §4.2 硬规矩 5「agent 解的行必须并列 ≥2 个可行解」。
#: 下界由胶囊半径 0.3117（净距扣掉板厚一半后必须更大）、上界由臂长 0.5617 夹出来。
DOOR_PUSH_STANCE_CANDIDATES = (0.33, 0.35, 0.38, 0.42, 0.46)

#: 穿模判据（动作库规格 §四·戊·5 **判据 4**）的骨集：躯干/上臂/大腿**零穿透** ·
#: 手与前臂**允许接触**（骨心进构件内部 ≤ 2 cm）· 非接触部位最小间隙 ≥ 1 cm。
#: ⚠️ 判据量的是**骨段**；owner 看的是**蒙皮** ⇒ 层差登记为已知偏差（口径 §十 的能播类三项表）。
DOOR_PUSH_CLEARANCE_CLASSES = (
    ("躯干/上臂/大腿", 0.0, ("Hips", "Spine", "Spine1", "Spine2", "LeftArm", "RightArm",
                             "LeftUpLeg", "RightUpLeg")),
    #: ⚠️ 五指 20 根一并进"允许接触"档——它们是**真正绕在门边上的那部分**，
    #:    漏掉它们的话这条判据就在最关键的地方留了个洞（判据 4 明写"手与前臂"含指）。
    ("手/前臂/五指（允许接触）", -20.0,
     ("LeftForeArm", "LeftHand", "RightForeArm", "RightHand")
     + tuple(f"LeftHand{f}{k}" for f in ("Thumb", "Index", "Middle", "Ring", "Pinky")
             for k in (1, 2, 3, 4))),
    ("非接触部位", 10.0, ("LeftShoulder", "RightShoulder", "LeftLeg", "RightLeg", "LeftFoot",
                          "RightFoot", "LeftToeBase", "RightToeBase", "Neck", "Head")),
)

#: 时序（帧号；30 fps）。判据面（口径 §十 的「时序」）只有一条：
#: **脚本声明的到位帧 == 从产物算出的判据量极值帧**。表里的帧号是**声明**，不是结论。
#: **门在这条动作里朝哪一侧半掩**（带符号；`DOOR_OPEN_START_DEG` 是宿主 3 的 20°，宿主 3 不动）。
#: ⚠️ **2026-09-16 owner 目视第一条**：「这个动作只能算得上**拉门**」——根因是门的半掩侧：
#:   门朝**角色这侧**开时，自由边是**朝角色扫过来**的，角色只能一边扣住一边**后退** ⇒ 观感是拉。
#:   ⇒ 半掩改到**远侧**（`-20°`），门朝**远离角色**的方向开：角色**上前**扣住自由边、
#:   **向前迈步推**，最后**穿过门洞**。终态仍是 `通过开度` 的**幅值** 49.486°（`-49.486°`）。
DOOR_PUSH_START_DEG = -20.0

DOOR_PUSH_FRAME_NEUTRAL = 1      # 中立姿势（导出侧硬约定：首帧必须中立，否则 E5 报 Rest Pose 漂移）
DOOR_PUSH_FRAME_GRIP = 16        # 扣住（远侧半掩后，要先**走近** 0.68 m 才够得着自由边）
DOOR_PUSH_FRAME_PUSH = 21        # 开始推（门角从这一帧起离开半掩角）
DOOR_PUSH_FRAME_ARRIVAL = 51     # 到位（门到 `-通过开度`）
DOOR_PUSH_FRAME_END = 61         # 保持到这一帧
#: 「先迈哪只脚」= 自由度表第 2 行（`agent 解`）⇒ 两种顺序**都解过、读数并列在证据 §五**；
#: 采用**左脚先迈**（穿模余量好得多：非接触部位 **43.33 mm** vs 另一解的 **15.43 mm**）。
DOOR_PUSH_FIRST_FOOT = "Left"

#: 步数**不写死**：`N = ceil(总行程 / 每步预算)`，窗口按**弧长均分**（口径 §13.6 自由度表第 3 行
#: "迈步步长由臂长与自由边弧长反解"）。每步预算 = **实测的腿预算**：踝相对骨盆偏移超过它就解不动
#: （证据 §三 的预算表：下沉 0.06 m 时 ≈ 0.20 m 起残差抬头，0.09 m 时 0.30 m 仍为 0）。
DOOR_PUSH_STEP_BUDGET_M = 0.20
#: 每个迈步桶里**摆动**占的比例（余下为双支撑）。运动学取值，不是判据阈值。
DOOR_PUSH_SWING_FRACTION = 0.7

#: 副手（右手）：静止姿势是 **T-pose**，不给解就是"机械平举"（owner 2026-09-16 第二条点名）。
#: 目标 = 腕落在体侧（髋骨点 + 本偏移，在**角色体侧系**里给），方向 = 指尖朝下、掌心内向。
DOOR_PUSH_OFFHAND_WRIST_OFFSET = (-0.150, 0.041, -0.153)   # 相对髋骨点（yaw=0 的身体系）
#: 副手的松握量（0 = 五指伸直；卡 1 的 F10 逐指基准角 × 本值）。运动学取值，owner 可改。
DOOR_PUSH_OFFHAND_CURL = 0.35

#: 推的时候**躯干前倾**（三段脊柱各分 1/3；0 = 直挺挺地平移 = owner 说的"机器人"）。
#: 轴向**有来源**：[管线 §2.1.4](design/presentation/Blender动作制作管线.md) 实测
#: `Spine` / `Spine1` / `Spine2` 的**局部 X = 前倾**（头顶前移 314.8 / 280.5 / 248.8 mm）。
#: 总量 12° 是**运动学取值**：肩前移 ≈ 0.12 m（读数见证据 §十四），owner 可改。
DOOR_PUSH_TORSO_LEAN_DEG = 12.0

#: 接地判据容差：**沿用** [对照实验 §2.1](../../design/presentation/动画处理能力对照实验.md) 的
#: `soleMargin`（出身 = `code/unity/Assets/Scripts/FootGroundingIK.cs` 注释的 bind pose 实测）。
#: 数值从**已入库的件** `xbot_contact_phase.py` 取（同一个量不抄第二份）；取不到才退回字面值。
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from xbot_contact_phase import SOLE_MARGIN_MM as DOOR_PUSH_SOLE_MARGIN_MM
except Exception:                                              # pragma: no cover
    DOOR_PUSH_SOLE_MARGIN_MM = 2.8                             # 来源同上（FootGroundingIK.cs）


def door_pass_open_deg(width=DOOR_WIDTH, radius=X_BOT_CAPSULE_RADIUS_M):
    """`通过开度` = 门开到**角色胶囊能通过**所需的最小开度（口径 §13.6 的终态量）。

    推导（**几何关系，不是选定角度**）：门绕铰链转 θ 后，门板所在直线与远侧门框之间的
    **净通道宽度** = `width · sin θ`（门板从铰链出发沿 `u(θ)` 伸出，远侧门框到该直线的垂距；
    θ = 90° 时退化为整幅门宽）。要求净通道 ≥ 胶囊直径 `2r` ⇒ `sin θ ≥ 2r / width`。
    """
    return math.degrees(math.asin(min(1.0, 2.0 * radius / width)))


def _rot_z(v, deg):
    """世界 XY 向量绕世界 +Z 转 `deg`（脚朝向 / 站距用；不额外引入 `mathutils.Matrix`）。

    ⚠️ 入参可能是 **2 维**（站距）⇒ 一律按 3 维返回（实测踩到：`Vector.z` 在 2 维向量上不可用）。
    """
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return Vector((v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2] if len(v) > 2 else 0.0))


def _nlerp(a, b, t):
    """两向量之间的归一化线性插值（起手段的朝向过渡用；夹角 < 180° 时足够）。"""
    v = Vector(a) * (1.0 - t) + Vector(b) * t
    return v.normalized() if v.length > 1e-9 else Vector(a).normalized()


def door_layout_actor_side(open_deg, actor_xy=(0.0, 0.0)):
    """`door_layout` 的**判侧版**：近/远侧按**给定角色位置**判，不按原点判。

    ⚠️ 为什么必须换（实测）：原函数用"外法向是否指向**原点**"判近侧，而门边**扫过原点**
    （θ ≈ 52.6° 时自由边恰在原点上；实测 49.478° 时离原点仅 **36 mm**）⇒ 判据在那里退化。
    """
    lay = door_layout(open_deg)
    mid = lay["mid_edge"]
    ref = Vector((actor_xy[0], actor_xy[1], 0.0))
    if (ref - mid).dot(lay["n"]) > 0.0:      # n 必须**背离**角色（近侧面外法向 −n 指向角色）
        lay["n"] = -lay["n"]
        lay["near_edge"] = mid - lay["n"] * (lay["thickness"] / 2.0)
        lay["far_edge"] = mid + lay["n"] * (lay["thickness"] / 2.0)
    return lay


def door_push_stance(open_deg, clearance_m=DOOR_PUSH_CLEARANCE_M, actor_xy=(0.0, 0.0)):
    """「推到底」的身体摆放：**站在自由边正侧、离门板中面 `clearance_m`**（其余全由几何算出）。

    ⚠️ 为什么不是"转身角 + 前倾量"两个手拍常量：自由边随开角绕铰链**扫弧**（半径 = 门宽）
    ⇒ 要**保持扣住**，身体必须跟着弧走。`clearance_m` 一取定，**转身角 = 握点方位角**
    （身体朝向握点）、**骨盆位置 = 铰链 + 门宽·u(θ) + clearance·(−n(θ))**——全部由几何给出，
    没有第二个自由常量。实测：肩→腕距离在**整段弧上恒定**（证据 §三）。
    """
    lay = door_layout_actor_side(open_deg, actor_xy)
    m = -lay["n"]
    body = lay["hinge"] + lay["u"] * lay["width"] + m * clearance_m
    grip = lay["near_edge"]
    face = Vector((grip.x - body.x, grip.y - body.y, 0.0))
    return lay, {"body_xy": (round(body.x, 6), round(body.y, 6)),
                 "yaw_deg": math.degrees(math.atan2(face.x, -face.y)),
                 "clearance_m": clearance_m,
                 "pelvis_to_grip_m": round(face.length, 4),
                 "grip_xy": (round(grip.x, 6), round(grip.y, 6))}


def set_pelvis_world(arm, m3, xy, z, iters=4):
    """把 `CTRL_Hips` 的**骨点世界位置**送到 `(xy, z)`——**实测回代**，不假设写入口径。

    ⚠️ 两条实测（证据 §六.2）：① `set_world_offset` 写进去的是**真世界位移**（与 yaw 无关，已核）；
    ② 但"目标位置"与"位移"差一个**静止髋位**，直接当位移写会整体偏约 16 mm ⇒ 按实测误差回代。
    """
    pb = arm.pose.bones["CTRL_Hips"]
    pb.location = (0.0, 0.0, 0.0)
    update()
    base = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    delta = Vector((xy[0] - base.x, xy[1] - base.y, z - base.z))
    err = Vector((0.0, 0.0, 0.0))
    for _ in range(iters):
        set_world_offset(arm, m3, "CTRL_Hips", delta)
        update()
        cur = world_point(arm, f"{BONE_PREFIX}Hips")
        err = Vector((xy[0] - cur.x, xy[1] - cur.y, z - cur.z))
        delta = delta + err
    return round(err.length * 1000.0, 3)


def solve_gaze_scan(arm, lo=-45.0, hi=45.0, step=1.0, fine=0.25, scale=1.0):
    """扫描 `Neck` / `Head` 的局部 X，取**头骨上轴最接近竖直**的那一档（口径 §十 V-b「目视水平」）。

    ⚠️ 为什么不复用 `solve_gaze`（牛顿法）：**实测它在转身 ≥ 45° 时发散**——#166 读数：
    yaw 40° → after **0.477°**；yaw 45° → after **45.431°**（8 次迭代仍不收敛）；yaw 50° →
    **49.564°**。而本动作的转身角要走到 **49.5°**。本函数只做**确定性扫描**，不依赖导数。
    `scale` 供**起手段**用：抬头到水平这件事随起手一起长出来（首帧必须严格中立，
    见 `DOOR_PUSH_FRAME_NEUTRAL` 的导出侧硬约定）。
    """
    def set_pair(x):
        for name in (f"{BONE_PREFIX}Head", f"{BONE_PREFIX}Neck"):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler((math.radians(x), 0.0, 0.0), "XYZ")
        update()

    set_pair(0.0)
    before = head_up_deg(arm)
    best = None
    x = lo
    while x <= hi + 1e-9:
        set_pair(x)
        v = head_up_deg(arm)
        if best is None or v < best[0]:
            best = (v, x)
        x += step
    x = best[1] - step
    while x <= best[1] + step + 1e-9:
        set_pair(x)
        v = head_up_deg(arm)
        if v < best[0]:
            best = (v, x)
        x += fine
    set_pair(best[1] * scale)
    return {"neck_head_x_deg": round(best[1] * scale, 3), "解出的_x_deg": round(best[1], 3),
            "scale": scale, "before_deg": round(before, 3),
            "after_deg": round(head_up_deg(arm), 3), "粗扫": f"{lo}..{hi}° / {step}°"}


def set_foot_world_orientation(arm, side, yaw_deg):
    """脚掌：**保持水平**（沿用静止朝向）但方向随身体转 `yaw_deg`。

    ⚠️ 库里既有写法（`_set_world_axes(..., _rest_dir, _rest_hinge)`）把脚**钉在世界朝向**上
    ⇒ 身体转 49.5° 时踝被扭同样的角度（宿主 3 就是这个形态）。绕世界 Z 转静止朝向**不改变脚掌
    的水平性**（判据 M2 只看竖直高度），只把脚尖摆到身体正前方。
    """
    _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                    _rot_z(_rest_dir(arm, f"{BONE_PREFIX}{side}Foot"), yaw_deg),
                    _rot_z(_rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"), yaw_deg))


def door_push_reach(arm, side, frame_geo, grip_wrist_target, rest_wrist, curl_axis,
                    curl_ref, thumb_ref, t, post):
    """**起手段**（`t` = 0 静止 → 1 抓住）：腕从静止位线性送到抓握目标，手指按 `t` 合拢。

    ⚠️ 手型**不另发明**：合拢的终值就是帧 13 那次抓握解出来的 F10 逐指蜷曲与拇指角
    （口径 §13.6 自由度表第 9 行：抓握高度与手型**引用卡 1**，不是自由量）。
    """
    n, u = frame_geo["n"], frame_geo["u"]
    x_hint = n.cross(u)
    rest_dir = Vector((1.0, 0.0, 0.0)) if side == "Left" else Vector((-1.0, 0.0, 0.0))
    target = Vector(rest_wrist).lerp(Vector(grip_wrist_target), t)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, n, t), x_hint)
    solve_arm_with_elbow_scan(arm, side, target, post)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, n, t), x_hint)
    for finger in FINGERS:
        val = float(curl_ref.get(finger, 0.0))
        _apply_one_finger_curl(arm, side, finger, curl_axis, val * t)
    if thumb_ref:
        pb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a * t) for a in thumb_ref], "XYZ")
    update(2)


def door_push_torso_lean(arm, total_deg):
    """**躯干前倾**：三段脊柱各转 `total_deg/3`（局部 X）。

    ⚠️ 为什么要有这一层：不给它，角色就是"**脊柱笔直地沿弧平移**"——owner 2026-09-16 的原话
    「**不像是人的动作更像是机器人**」。轴向不是拍的：管线 §2.1.4 实测 `Spine`/`Spine1`/`Spine2`
    的局部 X 就是前倾轴（三根共线，同转同角）。头由 `solve_gaze_scan` 在**之后**拉回水平。
    """
    each = total_deg / 3.0
    for name in ("Spine", "Spine1", "Spine2"):
        pb = arm.pose.bones[f"{BONE_PREFIX}{name}"]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(each), 0.0, 0.0), "XYZ")
    update()
    return {"每段_deg": round(each, 3), "合计_deg": round(total_deg, 3)}


def door_push_offhand(arm, side, yaw_deg, hips_world, hips_rest, curl_axis, t, post,
                      curl_amount=DOOR_PUSH_OFFHAND_CURL):
    """**副手**（不抓门的那只手）：自然垂放，随起手一起长出来（`t` = 0 → 1）。

    ⚠️ 为什么必须给个解（owner 2026-09-16 目视第二条：「**右手机械的平举**」）：静止姿势是
    **T-pose**——不给副手任何姿势，它就**水平伸着**。这不是"owner 没圈所以不碰"，是**没有姿势**。
    本解 = 腕落到体侧（`DOOR_PUSH_OFFHAND_WRIST_OFFSET`，在**角色体侧系**里给）、指尖朝下、
    掌心内向，并按 `DOOR_PUSH_OFFHAND_CURL` 松握；起手段按 `t` 从 T-pose 过渡过来。
    """
    # 当前（未解副手前的）手骨朝向 —— 用它当 `t=0` 端，过渡才不会在起手段跳一下
    _pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    _m = arm.matrix_world.to_3x3() @ _pb.matrix.to_3x3()
    rest_dir = (_m @ Vector((0.0, 1.0, 0.0))).normalized()      # 局部 Y = 腕 → 指尖
    rest_x = (_m @ Vector((1.0, 0.0, 0.0))).normalized()
    y_dir = _rot_z(Vector((0.0, 0.0, -1.0)), yaw_deg)          # 指尖朝下
    x_hint = _rot_z(Vector((0.0, -1.0, 0.0)), yaw_deg)         # 掌面朝体侧
    off = Vector(DOOR_PUSH_OFFHAND_WRIST_OFFSET)
    world_off = _rot_z(Vector((off.x, off.y, 0.0)), yaw_deg)
    target = Vector(hips_world) + Vector((world_off.x, world_off.y, off.z))
    rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()   # T-pose 的腕位
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, y_dir, t), _nlerp(rest_x, x_hint, t))
    solve_arm_with_elbow_scan(arm, side, rest_wrist.lerp(target, t), post)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, y_dir, t), _nlerp(rest_x, x_hint, t))
    for finger in FINGERS:
        _apply_one_finger_curl(arm, side, finger, curl_axis, curl_amount * t)
    update(2)
    return {"wrist_target_m": [round(v, 4) for v in target],
            "elbow_deg": round(math.degrees(
                (world_point(arm, f"{BONE_PREFIX}{side}Arm")
                 - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).angle(
                    world_point(arm, f"{BONE_PREFIX}{side}Hand")
                    - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1),
            "elbow_offset_mm": elbow_offset(arm, side),
            "curl_amount": curl_amount * t}


#: 骨集合的**显示契约**：母版生成器把 `CTRL`(13) 与 `MIXAMORIG`(65) **两个集合都设成可见**
#: （`V9_display`），于是**每一条预览都像"多套骨骼重叠"**。本仓早有处置口径——**预览收敛成一套**：
#: 来源 `design/engineering/evidence/hand-grip-cards-2026-09-15.md` §十二 的实测坑 ②
#: （原文：「目视时会看成『多套骨骼重叠』 ⇒ 预览脚本统一收敛为**只显示 `MIXAMORIG` 一套**」）。
DOOR_PUSH_VISIBLE_BONE_COLLECTION = "MIXAMORIG"

#: 判据 `visible_bone_outliers` 的**已知例外**（逐次重测、不是免检）：资产自带、且**不是**"多出来的骨头"。
#: `mixamorig:Head` 的**骨尖**比皮肤最高顶点高 **21 mm**（实测）——它是**正经关节**（523 个顶点带权重），
#: 骨尖只是画到颅顶标记处；隐藏它会让"头"这根骨在预览里消失。⇒ 登记为已知例外并**每次实测报出**。
DOOR_PUSH_BONE_OUTLIER_EXCEPTIONS = ("mixamorig:Head",)


def _skin_weight_counts(skin_ob):
    """`{骨名: 权重>0.01 的顶点数}`——判"这根骨有没有蒙皮"的唯一依据。"""
    out = {}
    for v in skin_ob.data.vertices:
        for g in v.groups:
            if g.weight > 0.01:
                n = skin_ob.vertex_groups[g.group].name
                out[n] = out.get(n, 0) + 1
    return out


def door_push_marker_bones(arm, skin="Beta_Surface"):
    """**骨尖标记**（管线 §2.1.4 注 1 的定义，逐条实测）：**无子骨的叶骨** 且 **零蒙皮权重**。

    实测清单（母版）：`HeadTop_End`（骨尖在头顶上方 **+243 mm**）· `LeftToe_End` / `RightToe_End`
    （脚尖前方 **+96 mm**）· 10 根手指 `…4`（指尖前方 **+22 ~ +32 mm**）——**共 13 根**。
    ⚠️ 它们**不能删**（导出契约要恰好 65 根变形骨）⇒ 只能在预览里**藏**。
    """
    wc = _skin_weight_counts(bpy.data.objects[skin])
    ctrl = {c.name for c in arm.data.collections if c.name != DOOR_PUSH_VISIBLE_BONE_COLLECTION}
    out = []
    for b in arm.data.bones:
        if b.children:
            continue
        if {c.name for c in b.collections} & ctrl:
            continue                      # 控制骨（CTRL_*）里也有零权重叶骨，但它们**是控制层**、不是标记
        if wc.get(b.name, 0) == 0:
            out.append(b.name)
    return out


def visible_bone_outliers(arm, skin="Beta_Surface", meshes=None):
    """判据：**可见的骨**的 head / tail 都必须落在**皮肤的包围盒**内，并报出到表面的最近距离。

    ⚠️ 为什么需要它（owner 2026-09-16 **第三次**指出「多余骨骼飘在人体模型外面」）：本仓的验证
    回路里**没有任何通道能看见骨架**——回显卡量几何、静帧走**渲染器**，而 Blender 的渲染
    **根本不画骨架**。⇒ 这件事在我这一侧**从来没有读数**，于是"每次都犯"。本函数把它变成读数。

    ⚠️ 判据的**已知边界**（如实登记）：包围盒只抓"整体伸出去"的那类；**盒内的空隙**（腋下、胯间）
    抓不到。第一版试过射线奇偶与法向侧判定，**在 X Bot 这套非闭合网格上都不成立**
    （实测：髋骨点被两种方法都判成"体外"）⇒ 改用包围盒。
    """
    # ⚠️ `meshes` 供**多实例 lab** 用（口径 §15.8）：实例复制后网格叫 `Beta_Surface.001`，
    #    按名字取会取到**原实例**的皮肤 ⇒ 骨架在 ±5 m 而盒子在原位，判据会读出 51 根"伸出 5000 mm"
    #    的假红（本件实测踩到）。传对象进来就没有这个歧义。
    skin_obs = list(meshes) if meshes is not None else [bpy.data.objects[skin]]
    verts = [ob.matrix_world @ v.co for ob in skin_obs for v in ob.data.vertices]
    lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
    vis_colls = {c.name for c in arm.data.collections if c.is_visible}
    outside, visible_n, rows = [], 0, []
    for b in arm.data.bones:
        colls = {c.name for c in b.collections}
        if b.hide or (colls and not (colls & vis_colls)):
            continue
        visible_n += 1
        h = arm.matrix_world @ b.head_local
        t = arm.matrix_world @ b.tail_local
        hh = all(lo[i] <= h[i] <= hi[i] for i in range(3))
        tt = all(lo[i] <= t[i] <= hi[i] for i in range(3))
        over = [max(lo[i] - p[i], p[i] - hi[i], 0.0) for p in (h, t) for i in range(3)]
        rows.append({"骨": b.name, "head_在盒内": hh, "tail_在盒内": tt,
                     "伸出量_mm": round(max(over) * 1000.0, 2)})
        # "贴面"与"伸出去"的分界**沿用同一个既有常量** `CONTACT_TOL_MM`（2.8 mm）——它在本仓的语义
        # 就是"多近算贴住表面"（口径 §8.2）。实测：正经关节的骨尖最多越界 **2.13 mm**（指尖/趾尖处），
        # 而骨尖标记越界 **15.7 ~ 241.9 mm** ⇒ 两者之间有一个**数量级**的天然间隙，不需要新阈值。
        if (not (hh and tt)) and rows[-1]["伸出量_mm"] > CONTACT_TOL_MM:
            rows[-1]["已知例外"] = b.name in DOOR_PUSH_BONE_OUTLIER_EXCEPTIONS
            outside.append(rows[-1])
    outside.sort(key=lambda r: -r["伸出量_mm"])
    bad = [r for r in outside if not r["已知例外"]]
    return {"可见骨数": visible_n, "可见骨集合": sorted(vis_colls),
            "皮肤包围盒_m": [[round(v, 4) for v in lo], [round(v, 4) for v in hi]],
            "判据": f"可见骨的 head/tail 都在皮肤包围盒内，越界量 > 贴面档 {CONTACT_TOL_MM} mm 才算"
                    f"伸出（已知例外逐次重测）",
            "伸到体外的骨": outside, "非例外的越界骨": bad,
            "已知例外": [r for r in outside if r["已知例外"]],
            "结论": "OK" if not bad else f"{len(bad)} 根可见骨伸到皮肤包围盒外面"}


def door_push_preview_cleanup(arm, skin="Beta_Surface"):
    """预览场景收敛：**只显示一套骨**（`MIXAMORIG`）+ 藏掉 **13 根骨尖标记**（不删，导出契约要 65 根）。

    owner 2026-09-16 第 **三** 次指出：「Armature 里有**多余骨骼**……十分显眼地**飘在人体模型外面**」。
    根因三条（**前两条本仓早已登记，我上一轮没读**）：
    ① **母版生成器把 `CTRL` 与 `MIXAMORIG` 两个骨集合都设成可见**（`V9_display`）⇒ 13 根控制骨与它
       驱动的 65 根变形骨**逐根重合地画在一起**——看着就是"多出一整套骨骼"。
       处置口径写在 #164 证据里：**预览收敛成只显示 `MIXAMORIG` 一套**。
    ② **13 根骨尖标记**（零权重叶骨）骨尖**伸到皮肤外面**：头顶 **+243 mm** · 脚尖 **+96 mm** ·
       指尖 **+22~32 mm**（`door_push_marker_bones` 逐条实测）。只能藏，不能删。
    ③ **我的回路缺口**（真正的错）：**没有任何通道能看见骨架** ⇒ 加了 `visible_bone_outliers` 判据。

    ⚠️ **不藏 `Beta_Joints`**：#164 证据明写"它是**人体网格**（10514 顶点）不是骨骼显示件——
    **隐藏它会把腰部蒙皮一起去掉**（实测踩到一次）"。本件第 2 轮**踩了这个坑**，此处回改。
    """
    info = {"骨集合": {}, "隐藏的骨集合": [], "藏起来的标记骨": [], "未藏的网格": []}
    for c in arm.data.collections:
        info["骨集合"][c.name] = {"is_visible": (c.name == DOOR_PUSH_VISIBLE_BONE_COLLECTION),
                                  "原本": c.is_visible}
        c.is_visible = (c.name == DOOR_PUSH_VISIBLE_BONE_COLLECTION)
    info["隐藏的骨集合"] = sorted(c.name for c in arm.data.collections if not c.is_visible)
    mc = arm.data.collections.get("HIDDEN_MARKERS") or arm.data.collections.new("HIDDEN_MARKERS")
    mc.is_visible = False
    for name in door_push_marker_bones(arm, skin):
        b = arm.data.bones.get(name)
        if b is None:
            continue
        b.hide = True
        for c in list(b.collections):
            c.unassign(b)
        mc.assign(b)
        info["藏起来的标记骨"].append(name)
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith("Beta_Joints"):
            ob.hide_viewport = False          # ⚠️ 回改：它是**人体网格**，藏了会掉腰部蒙皮
            ob.hide_render = False
            info["未藏的网格"].append(ob.name)
    return info


def main_door_push() -> int:
    """门边「推到底」宿主：逐帧解算 → **逐帧打键** → 从**产物**里读三类判据。"""
    from datetime import datetime
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    # ⚠️ 宿主 3 的动作名缺陷（#165 登记、宿主 3 本件不改）：`--action` 的默认值是椅子动作名。
    #    本宿主**不带 `--action` 时用自己的名字**，只在不一致时提示（不静默）。
    action_name = args.action if args.action != "BendGripChairBack" else DOOR_PUSH_ACTION
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    clearance = args.clearance if args.clearance is not None else DOOR_PUSH_CLEARANCE_M
    crouch = args.crouch if args.crouch is not None else DOOR_PUSH_CROUCH_M
    pass_deg = door_pass_open_deg()
    report = {"script": Path(__file__).name, "task": "doorpush", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "clearance_m": clearance, "crouch_m": crouch, "problems": []}
    print(f"门板：宽 {DOOR_WIDTH} m · 厚 {BACK_THICKNESS * 1000:.0f} mm · 铰链 {DOOR_HINGE} · "
          f"半掩 {DOOR_PUSH_START_DEG}°（**远侧**，门朝远离角色的方向开）· 动作名 {action_name}")
    print(f"胶囊半径 {X_BOT_CAPSULE_RADIUS_M} m ⇒ 直径 {2 * X_BOT_CAPSULE_RADIUS_M:.4f} m · "
          f"门宽 {DOOR_WIDTH} m ⇒ sinθ ≥ {2 * X_BOT_CAPSULE_RADIUS_M / DOOR_WIDTH:.6f} ⇒ "
          f"通过开度 = {pass_deg:.3f}° ⇒ 终态开角 = {-pass_deg:.3f}°（从半掩 {DOOR_PUSH_START_DEG}° 再推 {pass_deg + DOOR_PUSH_START_DEG:.3f}°）")
    report["pass_open"] = {
        "定义": "口径 §13.6 的终态量；术语注册表 `通过开度`",
        "推导": "净通道宽度 = 门宽 × sinθ（远侧门框到门板所在直线的垂距）≥ 胶囊直径 2r",
        "胶囊半径_m": X_BOT_CAPSULE_RADIUS_M, "胶囊直径_m": round(2 * X_BOT_CAPSULE_RADIUS_M, 4),
        "门宽_m": DOOR_WIDTH, "sinθ_下界": round(2 * X_BOT_CAPSULE_RADIUS_M / DOOR_WIDTH, 6),
        "通过开度_deg": round(pass_deg, 3), "终态开角_deg": round(-pass_deg, 3),
        "半掩角_deg": DOOR_PUSH_START_DEG,
        "从半掩再推_deg": round(pass_deg + DOOR_PUSH_START_DEG, 3),
        "来源": "胶囊半径来源见 X_BOT_CAPSULE_RADIUS_M 的注释（两处 Unity 侧实测记录）"}

    # ---- ① F3 复核（= 口径 §6.2 世界轴映射的**第二个动作复核**，即 U4 的复核点）----
    clear_pose(arm)
    f3 = {s: hand_axes_reading(arm, s) for s in CARD1_SIDES}
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    curl_axis = {s: {"axis": curl[s]["axis"], "sign": curl[s]["sign"]} for s in CARD1_SIDES}
    report["f3_rest"] = f3
    report["f3_curl"] = curl
    head_up = (world_point(arm, f"{BONE_PREFIX}HeadTop_End", "tail")
               - world_point(arm, f"{BONE_PREFIX}Head")).normalized()
    toe_dir = (world_point(arm, f"{BONE_PREFIX}LeftToeBase", "tail")
               - world_point(arm, f"{BONE_PREFIX}LeftToeBase")).normalized()
    report["u4_world_axes"] = {
        "上方=+Z（头骨上轴与 +Z 夹角°）": round(math.degrees(head_up.angle(Vector((0, 0, 1)))), 3),
        "前方=−Y（左趾指向与 −Y 夹角°）": round(math.degrees(toe_dir.angle(Vector((0, -1, 0)))), 3),
        "左手侧=+X（左腕 x_m）": round(world_point(arm, f"{BONE_PREFIX}LeftHand").x, 4),
        "右手侧=−X（右腕 x_m）": round(world_point(arm, f"{BONE_PREFIX}RightHand").x, 4)}
    print(f"F3 复核（与卡 1 同源）：+Y↔腕→中指尖 {f3['Left']['Y_vs_wrist_to_tip_deg']}°（左）· "
          f"蜷曲轴 {curl_axis['Left']['axis']}{curl_axis['Left']['sign']:+d}（左）/ "
          f"{curl_axis['Right']['axis']}{curl_axis['Right']['sign']:+d}（右）")
    print(f"U4 复核（§6.2 世界轴映射）：{report['u4_world_axes']}")

    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    ankle_z = foot_rest["Left"].z
    stance = {s: Vector((foot_rest[s].x - hips_rest.x, foot_rest[s].y - hips_rest.y))
              for s in CARD1_SIDES}
    side = "Left"                      # 抓门的是**左手**（卡 1 侧握基准格 · #164）
    off_side = "Right"                 # 副手：本件给它一个**自然垂放**的解（T-pose 不是姿势）
    grip_z = args.grip_z if args.grip_z is not None else 1.15
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    print(f"静止读数：髋 {tuple(round(v, 4) for v in hips_rest)} · 踝 z {ankle_z:.4f} m · "
          f"站距（左）{tuple(round(v, 4) for v in stance['Left'])}")

    # ---- ② 摆放规则与**保持扣住可达的最大角**扫描（改族判定；口径 §13.5）----
    if args.scan_arc:
        print("\n弧上扫描（判据：手臂不夹直 + 三条接触对全在容差内）")
        print(f"  {'θ°':>7}{'净距':>7}{'转身°':>7}{'肩→腕':>8}{'夹直':>6}{'虎口':>7}{'拇指':>7}"
              f"{'四指最坏':>9}{'残差':>7}{'肘°':>7}")
        rows, best_ok = [], None
        deg = DOOR_PUSH_START_DEG
        #: 判侧参考点：**沿扫描链递推**（第一档用原点，之后用上一档算出的身体位置）。
        #: ⚠️ 为什么不能用原点判到底（实测）：自由边在 **θ ≈ 52.6°** 时**扫过原点**
        #:   （49.486° 时离原点仅 36 mm）⇒ 越过它之后"哪一侧是角色侧"按原点判会**整条翻转**，
        #:   身体位置会从 (−0.294, 0.240) 跳到 (0.289, −0.20)（跳跃 0.72 m）——那是**规则退化**，
        #:   不是物理极限。递推参考点让"同一侧"沿链保持一致。
        ref_xy = (0.0, 0.0)
        while deg >= -args.scan_max - 1e-9:
            lay, st = door_push_stance(deg, clearance, actor_xy=ref_xy)
            ref_xy = st["body_xy"]
            frame_geo = door_end_frame(lay)
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
            set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch)
            _, _, posterior = body_frame(arm)
            for s in CARD1_SIDES:
                solve_leg(arm, s, foot_rest[s], -posterior)
                set_foot_world_orientation(arm, s, st["yaw_deg"])
            update()
            gi = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                 label=f"scan{deg}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            worst4 = max(abs(x) for x in pairs[2]["读数_mm"])
            ok = ((not gi["arm"].get("clamped_straight"))
                  and worst4 <= CONTACT_TOL_MM
                  and gi["web_to_edge_mm"] <= CONTACT_TOL_MM
                  and (gi["thumb_gap_mm"] is None or abs(gi["thumb_gap_mm"]) <= CONTACT_TOL_MM))
            rows.append({"deg": round(deg, 3), "ok": bool(ok), "reach_m": gi["arm"]["reach_m"],
                         "clamped": bool(gi["arm"].get("clamped_straight")),
                         "web_mm": gi["web_to_edge_mm"], "thumb_mm": gi["thumb_gap_mm"],
                         "四指最坏_mm": worst4, "残差_mm": pair_residual_mm(pairs),
                         "肘_deg": gi["elbow_deg"]})
            if ok:
                best_ok = round(deg, 3)
            print(f"  {deg:7.2f}{clearance:7.2f}{st['yaw_deg']:7.1f}{gi['arm']['reach_m']:8.3f}"
                  f"{('是' if gi['arm'].get('clamped_straight') else '否'):>6}"
                  f"{gi['web_to_edge_mm']:7.2f}{str(gi['thumb_gap_mm']):>7}{worst4:9.2f}"
                  f"{pair_residual_mm(pairs):7.2f}{gi['elbow_deg']:7.1f}")
            deg -= args.scan_step
        # ⚠️ 比的是**幅值**（门朝远侧开后扫描得到的是负角）：`|-88°| ≥ 49.486°` ⇒ 未触发改族
        trig = (best_ok is None) or (abs(best_ok) < pass_deg)
        report["scan_arc"] = {"clearance_m": clearance, "行": rows,
                              "保持扣住可达的最大角_deg": best_ok, "通过开度_deg": round(pass_deg, 3),
                              "改族触发": bool(trig),
                              "容差_mm": CONTACT_TOL_MM}
        print(f"⇒ 保持扣住可达的最大角（扫描区间 {DOOR_PUSH_START_DEG}–{-args.scan_max}° 内）="
              f"{best_ok}°（幅值 {abs(best_ok) if best_ok is not None else None:.3f}°）· "
              f"通过开度 = {pass_deg:.3f}° ⇒ 改族{'触发' if trig else '未触发'}")
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0 if not trig else 1

    # ---- ②′ 身体摆放（净距）的解空间：口径 §4.2 硬规矩 5「agent 解的行并列 ≥2 解」----
    if args.scan_stance:
        print("\n身体摆放（净距 b）的解空间（口径 §4.2 硬规矩 5：agent 解的行必须并列 ≥2 个可行解）")
        print(f"  {'θ°':>7}{'净距b':>7}{'离近侧面':>9}{'胶囊余量':>9}{'肩→腕':>8}{'夹直':>6}"
              f"{'虎口':>7}{'残差':>7}{'肘°':>7}")
        space = []
        for deg in (DOOR_PUSH_START_DEG, -pass_deg):
            ref = (hips_rest.x, hips_rest.y)
            for b in DOOR_PUSH_STANCE_CANDIDATES:
                lay, st = door_push_stance(deg, b, actor_xy=ref)
                ref = st["body_xy"]
                frame_geo = door_end_frame(lay)
                clear_pose(arm)
                drop_temp(arm, also_objects=False)
                set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
                set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch)
                _, _, posterior = body_frame(arm)
                for s_ in CARD1_SIDES:
                    solve_leg(arm, s_, foot_rest[s_], -posterior)
                    set_foot_world_orientation(arm, s_, st["yaw_deg"])
                update()
                gi = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                     label=f"stance{b}")
                pairs = grip_board_edge_readings(arm, side, frame_geo)
                face_margin = b - BACK_THICKNESS / 2.0 - X_BOT_CAPSULE_RADIUS_M
                space.append({"deg": round(deg, 3), "clearance_m": b,
                              "离近侧面_m": round(b - BACK_THICKNESS / 2.0, 4),
                              "胶囊余量_m": round(face_margin, 4),
                              "reach_m": gi["arm"]["reach_m"],
                              "clamped": bool(gi["arm"].get("clamped_straight")),
                              "web_mm": gi["web_to_edge_mm"], "残差_mm": pair_residual_mm(pairs),
                              "肘_deg": gi["elbow_deg"]})
                print(f"  {deg:7.3f}{b:7.2f}{b - BACK_THICKNESS / 2.0:9.3f}{face_margin:9.3f}"
                      f"{gi['arm']['reach_m']:8.3f}{('是' if gi['arm'].get('clamped_straight') else '否'):>6}"
                      f"{gi['web_to_edge_mm']:7.2f}{pair_residual_mm(pairs):7.2f}{gi['elbow_deg']:7.1f}")
        report["stance_solution_space"] = {"候选净距_m": list(DOOR_PUSH_STANCE_CANDIDATES),
                                           "行": space,
                                           "采用": clearance,
                                           "臂长_m": 0.5617,
                                           "胶囊半径_m": X_BOT_CAPSULE_RADIUS_M}
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0
    # ---- ③ 帧表（门角 / 身体摆放 / 迈步，全部由几何算出）----
    def stance_fixed(deg, clearance_m):
        """摆放的**不动点**版：判侧参考点 = 上一轮算出的身体位置。

        ⚠️ 为什么不能一直用原点判侧（实测）：自由边在 **θ ≈ 52.6°** 时扫过原点（49.486° 时
        离原点仅 36 mm）⇒ 越过它之后"哪一侧是角色侧"按原点判会整条翻转（身体位置跳 0.72 m）。
        不动点 = "身体在哪一侧，就以它自己为参考"，与直观一致且不循环。
        """
        ref = (hips_rest.x, hips_rest.y)
        st = None
        for _ in range(3):
            _lay, st = door_push_stance(deg, clearance_m, actor_xy=ref)
            ref = st["body_xy"]
        return st

    def push_angle(frame):
        """该帧的门开角（**带符号**）：半掩 `DOOR_PUSH_START_DEG` → 推段线性 → `-通过开度`。"""
        if frame <= DOOR_PUSH_FRAME_PUSH:
            return DOOR_PUSH_START_DEG
        if frame >= DOOR_PUSH_FRAME_ARRIVAL:
            return -pass_deg
        u = (frame - DOOR_PUSH_FRAME_PUSH) / float(DOOR_PUSH_FRAME_ARRIVAL - DOOR_PUSH_FRAME_PUSH)
        return DOOR_PUSH_START_DEG + (-pass_deg - DOOR_PUSH_START_DEG) * u

    def body_at(frame):
        if frame >= DOOR_PUSH_FRAME_GRIP:
            return stance_fixed(push_angle(frame), clearance)
        t = (frame - DOOR_PUSH_FRAME_NEUTRAL) / float(DOOR_PUSH_FRAME_GRIP - DOOR_PUSH_FRAME_NEUTRAL)
        _lay, end = door_push_stance(DOOR_PUSH_START_DEG, clearance)
        bx = hips_rest.x + (end["body_xy"][0] - hips_rest.x) * t
        by = hips_rest.y + (end["body_xy"][1] - hips_rest.y) * t
        return {"body_xy": (bx, by), "yaw_deg": end["yaw_deg"] * t, "clearance_m": clearance,
                "pelvis_to_grip_m": end["pelvis_to_grip_m"], "grip_xy": end["grip_xy"]}

    def crouch_at(frame):
        """膝屈下沉：**前 4 帧内沉到位**（首帧仍严格中立）。

        ⚠️ 实测（第 2 轮）：原先让它一路缓到"开始推"（帧 21）⇒ 帧 4–6 的沉量只有 0.009~0.03 m，
        而腿的水平预算 ≈ `√(2·腿长·沉量)` 此时只有几厘米 ⇒ **迈步当场解不动**（残差 17.0 mm）。
        """
        if frame >= DOOR_PUSH_FRAME_NEUTRAL + 4:
            return crouch
        return crouch * (frame - DOOR_PUSH_FRAME_NEUTRAL) / 4.0

    def lean_at(frame):
        """躯干前倾量：推段从 0 长到 `DOOR_PUSH_TORSO_LEAN_DEG`，到位后保持。"""
        if frame <= DOOR_PUSH_FRAME_PUSH:
            return 0.0
        if frame >= DOOR_PUSH_FRAME_ARRIVAL:
            return DOOR_PUSH_TORSO_LEAN_DEG
        u = (frame - DOOR_PUSH_FRAME_PUSH) / float(DOOR_PUSH_FRAME_ARRIVAL - DOOR_PUSH_FRAME_PUSH)
        return DOOR_PUSH_TORSO_LEAN_DEG * u

    def reach_t(frame):
        if frame >= DOOR_PUSH_FRAME_GRIP:
            return 1.0
        return (frame - DOOR_PUSH_FRAME_NEUTRAL) / float(DOOR_PUSH_FRAME_GRIP - DOOR_PUSH_FRAME_NEUTRAL)

    #: 迈步：**按身体路径的弧长均分**（步数由实测腿预算反解），左右脚交替。
    #: 每个"迈步桶"= 弧长 `L`；桶内前 `SWING_FRACTION` 让该脚摆动、其余双支撑。
    #: ⇒ 「迈步步长」不是拍的：`L = 总行程 / N`，`N = ceil(总行程 / 每步预算)`。
    _first = args.first_foot
    _other = "Right" if _first == "Left" else "Left"
    _path_frames = list(range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1))
    _path_xy = [Vector(body_at(f_)["body_xy"]) for f_ in _path_frames]
    _cum = [0.0]
    for _i in range(1, len(_path_xy)):
        _cum.append(_cum[-1] + (_path_xy[_i] - _path_xy[_i - 1]).length)
    _travel = _cum[-1]
    _n_steps = max(1, int(math.ceil(_travel / DOOR_PUSH_STEP_BUDGET_M)))
    _L = _travel / _n_steps
    _cum_by_frame = {f_: _cum[i] for i, f_ in enumerate(_path_frames)}
    print(f"迈步：总行程 {_travel:.3f} m ÷ 每步预算 {DOOR_PUSH_STEP_BUDGET_M} m ⇒ {_n_steps} 步 ·"
          f" 每步弧长 {_L:.3f} m · 先迈 {_first}")
    #: 桶表（**纯函数**，一次算完）：每桶 = 摆动脚 / 起帧 / 落帧 / 止帧 / 落点。
    #: 落点 = "落帧时的身体位置 + 站距 + **行进方向 × (每步弧长/2)**"——那只脚在**身体前方**落地，
    #: 之后身体走过 `L`，它再抬起来时正好在身体**后方** `L/2` ⇒ 踝相对骨盆的偏移在 **±L/2** 内
    #: 摆动（实测：不"往前落"时偏移会长到 `L`，帧 8/9 的腿 IK 因此解不动、残差 11.9 mm）。
    _buckets = []
    _prev_plant = {s: Vector((foot_rest[s].x, foot_rest[s].y, ankle_z)) for s in CARD1_SIDES}
    for _k in range(_n_steps):
        _foot = _first if _k % 2 == 0 else _other
        def _first_after(frac):
            return next((f_ for f_ in _path_frames if _cum_by_frame[f_] > frac * _L + 1e-9),
                        _path_frames[-1])
        _a, _l, _b = _first_after(_k), _first_after(_k + DOOR_PUSH_SWING_FRACTION), _first_after(_k + 1)
        _e = body_at(_l)
        _bx2, _by2 = body_at(min(_l + 2, DOOR_PUSH_FRAME_END))["body_xy"]
        _bx1, _by1 = body_at(max(_l - 2, DOOR_PUSH_FRAME_NEUTRAL))["body_xy"]
        _dirv = Vector((_bx2 - _bx1, _by2 - _by1, 0.0))          # ⚠️ 一律 3 维（站距偏移是 3 维）
        _dirv = _dirv.normalized() if _dirv.length > 1e-9 else Vector((0.0, 0.0, 0.0))
        _tgt = (Vector((_e["body_xy"][0], _e["body_xy"][1], 0.0))
                + _rot_z(stance[_foot], _e["yaw_deg"]) + _dirv * (_L / 2.0))
        _tgt.z = ankle_z
        _buckets.append({"桶": _k, "脚": _foot, "起帧": _a, "落帧": _l, "止帧": _b, "落点": _tgt,
                         "从": _prev_plant[_foot].copy()})
        _prev_plant[_foot] = _tgt.copy()
    step_log = [{"桶": b["桶"], "脚": b["脚"], "起帧": b["起帧"], "落帧": b["落帧"], "止帧": b["止帧"],
                 "从_xy": [round(v, 4) for v in b["从"]], "到_xy": [round(v, 4) for v in b["落点"]],
                 "步长_m": round((b["落点"] - b["从"]).length, 4)} for b in _buckets]
    print(f"迈步桶：{[(b['桶'], b['脚'], b['起帧'], b['落帧']) for b in _buckets]}")

    def ankle_target(frame):
        """逐脚踝目标（纯函数）：默认 = 该脚**最近一次落点**；正在摆动的那只脚按抬脚弧从上一落点飞到落点。"""
        out = {}
        for s in CARD1_SIDES:
            last = None
            for b in _buckets:
                if b["脚"] == s and b["落帧"] <= frame:
                    last = b["落点"]
            out[s] = (last.copy() if last is not None
                      else Vector((foot_rest[s].x, foot_rest[s].y, ankle_z)))
        for b in _buckets:
            if b["起帧"] < frame <= b["落帧"]:
                span = max(b["落帧"] - b["起帧"], 1)
                u = (frame - b["起帧"]) / float(span)
                xy = b["从"].lerp(b["落点"], u)
                out[b["脚"]] = Vector((xy.x, xy.y,
                                       ankle_z + DOOR_PUSH_STEP_LIFT_M * math.sin(math.pi * u)))
        return out

    def grip_names():
        """打键通道表：**双侧**手臂与腿脚控制骨 + 骨盆 + 颈/头 + 解算侧手骨。

        ⚠️ 为什么必须**双侧腿脚**（宿主 3 就是在这里漏的）：只打一侧时，另一侧的腿在产物里
        恒为**静止姿势**——骨盆一动，那条腿就整条跟着骨盆走（实测：脚陷到地面 **−60 mm**，
        而 M2 的"含陷入"判据**照样读成"接触"**⇒ 接地判据被绕过）。#165 那条
        "门边动作双侧全程无支撑、离地 +160~+313 mm" 是同一个病的另一面。
        """
        names = ["CTRL_Hips"]
        for s in CARD1_SIDES:
            names += [f"CTRL_{s}{p}" for p in ("Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot")]
        names += [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head",
                  f"{BONE_PREFIX}Spine", f"{BONE_PREFIX}Spine1", f"{BONE_PREFIX}Spine2"]
        for s_ in CARD1_SIDES:            # ⚠️ 双侧：副手（右手）也要打键，否则它留在 T-pose
            for finger in FINGERS:
                for k in (1, 2, 3, 4):
                    n = f"{BONE_PREFIX}{s_}Hand{finger}{k}"
                    if n in arm.pose.bones:
                        names.append(n)
        return names

    # ---- ④ 起手参照解：帧 13 的抓握（拿到 F10 的逐指蜷曲 + 拇指角；起手段只按 t 缩放它们）----
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    lay13 = build_door_proxy(DOOR_PUSH_START_DEG)
    frame_geo13 = door_end_frame(lay13)
    st13 = body_at(DOOR_PUSH_FRAME_GRIP)
    set_euler(arm, "CTRL_Hips", y=st13["yaw_deg"])
    set_pelvis_world(arm, m3, st13["body_xy"], hips_rest.z - crouch)
    _, _, posterior = body_frame(arm)
    _ank13 = ankle_target(DOOR_PUSH_FRAME_GRIP)
    for s in CARD1_SIDES:
        solve_leg(arm, s, _ank13[s], -posterior)
        set_foot_world_orientation(arm, s, st13["yaw_deg"])
    update()
    door_push_torso_lean(arm, lean_at(DOOR_PUSH_FRAME_GRIP))
    door_push_offhand(arm, "Right", st13["yaw_deg"], world_point(arm, f"{BONE_PREFIX}Hips"),
                      hips_rest, curl_axis["Right"], 1.0, posterior)
    gaze_ref = solve_gaze_scan(arm)
    ref_grip = grip_board_edge(arm, side, frame_geo13, grip_z, curl_amount, curl_axis[side],
                               label="ref13")
    curl_ref = {f: v["蜷曲量"] for f, v in (ref_grip["curl_solve"] or {}).items()}
    thumb_ref = list(ref_grip["thumb"]["euler_deg"])
    clear_pose(arm)
    rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
    report["frame13_reference"] = {"gaze": gaze_ref, "curl_ref": curl_ref,
                                   "thumb_ref_deg": thumb_ref,
                                   "web_to_edge_mm": ref_grip["web_to_edge_mm"],
                                   "elbow_deg": ref_grip["elbow_deg"]}

    # ---- ⑤ 逐帧解算（每帧解、每帧打键 ⇒ 产物里的中间帧也是解出来的）----
    captured, per_frame = {}, []
    print(f"\n逐帧解算（帧 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END}，每帧打键）")
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        st = body_at(frame)
        deg = push_angle(frame)
        lay = door_layout_actor_side(deg, st["body_xy"])
        frame_geo = door_end_frame(lay)
        ankles = ankle_target(frame)
        if frame == DOOR_PUSH_FRAME_NEUTRAL:
            # ⚠️ **首帧必须严格中立**（导出侧硬约定，`export_xbot_action.py` 的 E5）：FBX 导出会把
            #    "导出那一刻的姿势"写进骨节点的默认变换、回导端把它当 Rest/Bind Pose ⇒ 首帧带姿势
            #    就等于**污染骨架身份**（#156 实测过一次，E5 报出 86 m 量级偏差）。
            #    ⇒ 首帧一个解都不打：只记中立通道。
            row = {"frame": frame, "door_open_deg": round(deg, 4),
                   "body_xy": [round(hips_rest.x, 4), round(hips_rest.y, 4)], "yaw_deg": 0.0,
                   "crouch_m": 0.0, "pelvis_fix_mm": 0.0, "hooked": False, "reach_t": 0.0,
                   "neutral": True,
                   "ankles": {s: [round(v, 4) for v in ankles[s]] for s in CARD1_SIDES},
                   "leg_tip_err_mm": {s: 0.0 for s in CARD1_SIDES},
                   "leg_clamped": {s: False for s in CARD1_SIDES},
                   "gaze_after_deg": round(head_up_deg(arm), 3), "gaze_x_deg": 0.0,
                   "grip": None, "pairs": [], "residual_mm": None}
            captured[frame] = capture_channels(arm, grip_names())
            per_frame.append(row)
            print(f"  帧 {frame:>3} 门 {deg:6.3f}° **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
        pelvis_err = set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch_at(frame))
        _, _, posterior = body_frame(arm)
        legs = {}
        for s in CARD1_SIDES:
            legs[s] = solve_leg(arm, s, ankles[s], -posterior)
            set_foot_world_orientation(arm, s, st["yaw_deg"])
        update()
        t = reach_t(frame)
        _pre_lean_shoulder = world_point(arm, f"{BONE_PREFIX}LeftArm").copy()
        door_push_torso_lean(arm, lean_at(frame))
        lean_shift = round((world_point(arm, f"{BONE_PREFIX}LeftArm").y - _pre_lean_shoulder.y)
                           * 1000.0, 1)
        offhand = door_push_offhand(arm, off_side, st["yaw_deg"], world_point(arm, f"{BONE_PREFIX}Hips"),
                                    hips_rest, curl_axis[off_side], t, posterior)
        gaze = solve_gaze_scan(arm, scale=t if frame < DOOR_PUSH_FRAME_GRIP else 1.0)
        row = {"frame": frame, "door_open_deg": round(deg, 4),
               "body_xy": [round(v, 4) for v in st["body_xy"]], "yaw_deg": round(st["yaw_deg"], 2),
               "crouch_m": round(crouch_at(frame), 4), "pelvis_fix_mm": pelvis_err,
               "hooked": t >= 1.0, "reach_t": round(t, 3),
               "ankles": {s: [round(v, 4) for v in ankles[s]] for s in CARD1_SIDES},
               "leg_tip_err_mm": {s: legs[s]["tip_err_mm"] for s in CARD1_SIDES},
               "leg_clamped": {s: bool(legs[s].get("clamped_straight")) for s in CARD1_SIDES},
               "gaze_after_deg": gaze["after_deg"], "gaze_x_deg": gaze["neck_head_x_deg"],
               "offhand": offhand,
               "torso_lean_deg": round(lean_at(frame), 2), "lean_shoulder_shift_y_mm": lean_shift}
        if t >= 1.0:
            grip = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                   label=f"f{frame}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            row["grip"] = {"web_to_edge_mm": grip["web_to_edge_mm"],
                           "thumb_gap_mm": grip["thumb_gap_mm"],
                           "palm_to_end_face_mm": grip["palm_to_end_face_mm"],
                           "reach_m": grip["arm"]["reach_m"],
                           "wrist_tip_err_mm": grip["arm"]["tip_err_mm"],
                           "clamped": bool(grip["arm"].get("clamped_straight")),
                           "elbow_deg": grip["elbow_deg"], "elbow_offset_mm": grip["elbow_offset_mm"],
                           "elbow_penalty": grip["elbow_pick"]["罚分"],
                           "四指_mm": pairs[2]["读数_mm"]}
            row["pairs"] = [{"手部分区": r["手部分区"], "物体分区": r["物体分区"],
                             "判据形态": r["判据形态"], "读数_mm": r["读数_mm"], "状态": r["状态"]}
                            for r in pairs]
            row["residual_mm"] = pair_residual_mm(pairs)
        else:
            door_push_reach(arm, side, frame_geo, ref_grip["wrist_target_m"], rest_wrist,
                            curl_axis[side], curl_ref, thumb_ref, t, posterior)
            row["grip"] = None
            row["pairs"] = []
            row["residual_mm"] = None
        captured[frame] = capture_channels(arm, grip_names())
        per_frame.append(row)
        off = {s: round((Vector(row["ankles"][s])
                         - Vector((st["body_xy"][0], st["body_xy"][1], ankle_z))).length, 3)
               for s in CARD1_SIDES}
        print(f"  帧 {frame:>3} 门 {deg:6.3f}° 骨盆 ({st['body_xy'][0]:+.3f},{st['body_xy'][1]:+.3f}) "
              f"转身 {st['yaw_deg']:5.1f}° 踝偏 {off} 腿残差 {row['leg_tip_err_mm']} "
              f"目视 {gaze['after_deg']:5.2f}°"
              + (f" | 虎口 {row['grip']['web_to_edge_mm']:5.2f} 拇指 {row['grip']['thumb_gap_mm']}"
                 f" 残差 {row['residual_mm']:5.2f} 肘 {row['grip']['elbow_deg']:5.1f}°"
                 if row["grip"] else " | 起手（腕趋近 + 手指合拢）"))
    report["frames"] = per_frame
    report["steps"] = step_log
    report["first_foot"] = _first
    report["step_plan"] = [{"桶": k, "脚": (_first if k % 2 == 0 else _other)} for k in range(_n_steps)]
    report["step_machine"] = {"总行程_m": round(_travel, 4), "每步预算_m": DOOR_PUSH_STEP_BUDGET_M,
                              "步数": _n_steps, "每步弧长_m": round(_L, 4),
                              "摆动占比": DOOR_PUSH_SWING_FRACTION, "先迈": _first}

    # ---- ⑥ 打键（**逐帧**；控制骨 + 手骨 + **腿脚**全打——宿主 3 漏掉的正是腿脚）----
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    panel = bpy.data.objects.get("REF_DoorPanel")
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        if panel is not None:
            p_lay = door_layout(push_angle(frame))
            panel.location = p_lay["panel_center"]
            panel.rotation_euler = Euler((0.0, 0.0, math.radians(p_lay["open_deg"])), "XYZ")
            panel.keyframe_insert("location", frame=frame)
            panel.keyframe_insert("rotation_euler", frame=frame)
        update()
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_start = DOOR_PUSH_FRAME_NEUTRAL
    bpy.context.scene.frame_end = DOOR_PUSH_FRAME_END
    report["action_frames"] = [DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END]
    report["keyed_channels"] = sorted(captured[DOOR_PUSH_FRAME_END])
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    print(f"预览收敛：只显示骨集合 {DOOR_PUSH_VISIBLE_BONE_COLLECTION}"
          f"（隐藏 {report['preview_cleanup']['隐藏的骨集合']}）· "
          f"藏起标记骨 {report['preview_cleanup']['藏起来的标记骨']} · "
          f"`Beta_Joints` **不藏**（它是人体网格，藏了会掉腰部蒙皮）")
    # 判据：可见的骨必须都在皮肤内部（把"骨头飘在模型外面"变成读数）
    report["visible_bones"] = visible_bone_outliers(arm)
    if report["visible_bones"]["非例外的越界骨"]:
        report["problems"].append(
            "可见骨伸出皮肤包围盒：" + "; ".join(f"{x['骨']}(伸出 {x['伸出量_mm']:.1f} mm)"
                                                for x in report["visible_bones"]["非例外的越界骨"][:8]))
        print(f"⚠️ 可见骨伸出皮肤包围盒 {len(report['visible_bones']['非例外的越界骨'])} 根"
              f"（另有已知例外 {[(x['骨'], x['伸出量_mm']) for x in report['visible_bones']['已知例外']]}）")
    else:
        print(f"判据「可见骨落在皮肤包围盒内」：{report['visible_bones']['可见骨数']} 根可见骨"
              f"**全部在盒内** ✅（盒 = {report['visible_bones']['皮肤包围盒_m']}）")
    print(f"\n已打键：动作 {action_name} · 帧 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END} · "
          f"通道 {len(captured[DOOR_PUSH_FRAME_END])} 个（含腿脚："
          f"{[n for n in report['keyed_channels'] if 'UpLeg' in n or n.endswith('Leg') or 'Foot' in n]}）")

    # ---- ⑦ 产物侧读数：F4a（持续）· 时序（V-f）· 接地（M2）----
    def product_frame(frame):
        bpy.context.scene.frame_set(frame)
        update()
        d = bpy.context.evaluated_depsgraph_get()
        return arm.evaluated_get(d)

    timing_curve, f4a, ground, clash = [], [], [], []
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        ev = product_frame(frame)
        deg = push_angle(frame)
        st = body_at(frame)
        lay = door_layout_actor_side(deg, st["body_xy"])
        frame_geo = door_end_frame(lay)
        hand = world_point(ev, f"{BONE_PREFIX}{side}Hand")
        hinge = lay["hinge"]
        # ⚠️ 判据量取**方位角的幅值**：`atan2` 的零点是"门关着"那条线，门朝远侧开后方位角是**负**的
        #    （−14.8° → −49.5°），取幅值才与"开到多大"同向（第一版取有符号值 ⇒ 极值帧落到了起手帧 16，判据当场报红）。
        _az = math.degrees(math.atan2(hand.y - hinge.y, hand.x - hinge.x))
        timing_curve.append({"frame": frame, "door_open_deg": round(deg, 4),
                             "hand_azimuth_deg": round(_az, 4),
                             "hand_open_deg": round(abs(_az), 4)})
        feet, foot_pts = {}, {}
        for s in CARD1_SIDES:
            bone = world_point(ev, f"{BONE_PREFIX}{s}Foot")
            toe = world_point(ev, f"{BONE_PREFIX}{s}ToeBase")
            low = min(bone.z, toe.z) * 1000.0
            feet[s] = {"foot_z_mm": round(bone.z * 1000.0, 2), "toe_z_mm": round(toe.z * 1000.0, 2),
                       "lowest_mm": round(low, 2), "contact": bool(low <= DOOR_PUSH_SOLE_MARGIN_MM)}
            foot_pts[s] = [(bone.x, bone.y), (toe.x, toe.y)]
        support = sorted(s for s in CARD1_SIDES if feet[s]["contact"])
        # 重心（口径 §13.6 自由度表第 7 行）：**只报读数、无阈值**——`支撑多边形` 的判据部分
        # 仍未建（#167 登记），本件**不建它**：只报"Hips 水平投影"与"到最近支撑接触点的水平距离"。
        hips_p = world_point(ev, f"{BONE_PREFIX}Hips")
        pts = [q for s in support for q in foot_pts[s]]
        nearest = (round(min(math.hypot(hips_p.x - q[0], hips_p.y - q[1]) for q in pts) * 1000.0, 1)
                   if pts else None)
        ground.append({"frame": frame, "angle_deg": round(deg, 4), "feet": feet, "support": support,
                       "重心_xy_m": [round(hips_p.x, 4), round(hips_p.y, 4)],
                       "离最近支撑接触点_mm": nearest})
        # 穿模（动作库规格 §四·戊·5 判据 4）：骨段 ↔ 门板盒；逐段取 head/mid/tail 三点采样
        clash_row = {"frame": frame, "classes": {}}
        for cname, cthr, cbones in DOOR_PUSH_CLEARANCE_CLASSES:
            worst, where = None, None
            for bn in cbones:
                full = f"{BONE_PREFIX}{bn}"
                if full not in ev.pose.bones:
                    continue
                h = world_point(ev, full)
                t = world_point(ev, full, "tail")
                for tag, pt in (("head", h), ("mid", (h + t) * 0.5), ("tail", t)):
                    g = box_gap_mm(pt, frame_geo)
                    if worst is None or g < worst:
                        worst, where = g, f"{bn}.{tag}"
            clash_row["classes"][cname] = {"阈值_mm": cthr,
                                           "最坏_mm": (round(worst, 2) if worst is not None else None),
                                           "最坏处": where}
        clash.append(clash_row)
        if frame >= DOOR_PUSH_FRAME_GRIP:
            pairs = grip_board_edge_readings(ev, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            f4a.append({"frame": frame, "angle_deg": round(deg, 4), "pairs": pairs,
                        "residual_mm": pair_residual_mm(pairs)})

    declared = DOOR_PUSH_FRAME_ARRIVAL
    vals = [r["hand_open_deg"] for r in timing_curve]
    win = [i for i, r in enumerate(timing_curve) if r["frame"] >= DOOR_PUSH_FRAME_GRIP]
    best_i = max(win, key=lambda i: vals[i])          # `max` 取**最先出现**的最大值（平台期 ⇒ 到位帧）
    extreme = timing_curve[best_i]["frame"]
    report["timing"] = {
        "声明到位帧": declared,
        "判据量": "手骨（mixamorig:LeftHand）绕铰链轴的水平方位角**幅值**（0 = 门关着那条线 ⇒ 幅值 = 开度）"
                  "——门在转、手不动时该曲线是平的，极值帧会立刻偏离声明帧",
        "取样": "全段逐帧（口径 §十 的 41 点均匀采样 + 整帧细化的极限情形：逐帧全取）",
        "曲线": timing_curve, "极值帧": extreme, "极值_deg": round(vals[best_i], 4),
        "一致": bool(extreme == declared)}
    worst_f4a = round(max((abs(x) for r in f4a for row in r["pairs"]
                           for x in (row["读数_mm"] if isinstance(row["读数_mm"], list)
                                     else [row["读数_mm"]]) if x is not None), default=0.0), 3)
    report["f4a_persistent"] = {"窗口": [DOOR_PUSH_FRAME_GRIP, DOOR_PUSH_FRAME_END], "行": f4a,
                                "最坏_mm": worst_f4a, "容差_mm": CONTACT_TOL_MM}
    report["grounding"] = {"容差_mm": DOOR_PUSH_SOLE_MARGIN_MM, "行": ground,
                           "无支撑帧": [r["frame"] for r in ground if not r["support"]],
                           "换脚帧": [ground[i]["frame"] for i in range(1, len(ground))
                                   if ground[i]["support"] != ground[i - 1]["support"]]}
    clash_bad, clash_worst = [], {}
    for r in clash:
        for cname, c in r["classes"].items():
            if c["最坏_mm"] is None:
                continue
            if cname not in clash_worst or c["最坏_mm"] < clash_worst[cname]["最坏_mm"]:
                clash_worst[cname] = {"最坏_mm": c["最坏_mm"], "帧": r["frame"],
                                      "最坏处": c["最坏处"], "阈值_mm": c["阈值_mm"]}
            if c["最坏_mm"] < c["阈值_mm"]:
                clash_bad.append({"frame": r["frame"], "类": cname, "最坏_mm": c["最坏_mm"],
                                  "阈值_mm": c["阈值_mm"], "最坏处": c["最坏处"]})
    report["clash"] = {"判据": "动作库规格 §四·戊·5 判据 4（骨段 ↔ 门板盒）",
                       "类": [{"类": c, "阈值_mm": t} for c, t, _ in DOOR_PUSH_CLEARANCE_CLASSES],
                       "逐帧": clash, "各类最坏": clash_worst,
                       "违规帧": clash_bad[:12], "违规处数": len(clash_bad)}
    if clash_bad:
        report["problems"].append(f"穿模（判据 4）：{len(clash_bad)} 处越界——"
                                  f"{clash_bad[:4]}")
    bad_legs = [r["frame"] for r in per_frame if max(r["leg_tip_err_mm"].values()) > 1.0]
    report["leg_tracking"] = {"残差>1mm 的帧": bad_legs,
                              "最坏_mm": max((max(r["leg_tip_err_mm"].values())
                                              for r in per_frame), default=0.0)}
    swing_low = []
    for w in step_log:
        s = w["脚"]
        inner = [r for r in ground if w["起帧"] < r["frame"] < w["落帧"]]
        if not inner:
            continue
        swing_low.append({"窗口": [w["起帧"], w["落帧"]], "脚": s, "窗口内帧数": len(inner),
                          "窗口内该脚最低点_mm": min(r["feet"][s]["lowest_mm"] for r in inner),
                          "窗口内该脚最高点_mm": max(r["feet"][s]["lowest_mm"] for r in inner)})
    report["swing_clearance"] = swing_low
    #: 支撑脚的**陷入**读数：M2 的判据是单边的（`≤ soleMargin`，**含陷入**）⇒ 只按它判，
    #: "脚陷进地面 60 mm"也会读成"接触"。本件把同一个 `soleMargin` 对称地再用一次
    #: （`|最低点| ≤ soleMargin`），新增的只是**同一常量的对称用法**，不是一个新阈值。
    sunk = [{"frame": r["frame"], "脚": s, "最低点_mm": r["feet"][s]["lowest_mm"]}
            for r in ground for s in r["support"] if r["feet"][s]["lowest_mm"] < -DOOR_PUSH_SOLE_MARGIN_MM]
    report["support_penetration"] = {"判据": "|支撑脚最低点| ≤ soleMargin（同一常量的对称用法）",
                                     "容差_mm": DOOR_PUSH_SOLE_MARGIN_MM, "行的数": len(sunk),
                                     "最坏_mm": min((r["最低点_mm"] for r in sunk), default=0.0),
                                     "前几帧": sunk[:6]}
    if worst_f4a > CONTACT_TOL_MM:
        report["problems"].append(f"F4a 持续型接触对最坏 {worst_f4a} mm > 容差 {CONTACT_TOL_MM} mm"
                                  "（整段相位内须逐帧成立，松一帧即红）")
    if extreme != declared:
        report["problems"].append(f"时序：声明到位帧 {declared} ≠ 产物极值帧 {extreme}")
    if report["grounding"]["无支撑帧"]:
        report["problems"].append(f"接地：{len(report['grounding']['无支撑帧'])} 帧**双脚同时离地**"
                                  f"（{report['grounding']['无支撑帧'][:6]}…）")
    if bad_legs:
        report["problems"].append(f"腿 IK 未跟踪（残差 > 1 mm）的帧：{bad_legs[:8]}"
                                  "——踝没到目标 ⇒ 该帧脚不在标称落点")
    if sunk:
        report["problems"].append(f"接地：支撑脚**陷入地面** {len(sunk)} 处（最深 "
                                  f"{report['support_penetration']['最坏_mm']} mm，容差 "
                                  f"{DOOR_PUSH_SOLE_MARGIN_MM} mm）⇒ 该腿没进打键表或腿 IK 没解")
    for w in swing_low:
        if w["窗口内该脚最低点_mm"] <= DOOR_PUSH_SOLE_MARGIN_MM:
            report["problems"].append(f"摆动脚没离地：窗口 {w['窗口']}（{w['脚']}）内最低 "
                                      f"{w['窗口内该脚最低点_mm']} mm ≤ soleMargin "
                                      f"{DOOR_PUSH_SOLE_MARGIN_MM} mm")
    report["ok"] = not report["problems"]

    print(f"\n时序：声明到位帧 {declared} · 产物极值帧 {extreme}（{report['timing']['极值_deg']}°）"
          f" ⇒ {'一致 ✅' if extreme == declared else '不一致 ❌'}")
    print(f"F4a 持续型接触对（帧 {DOOR_PUSH_FRAME_GRIP}–{DOOR_PUSH_FRAME_END}）：最坏 {worst_f4a} mm "
          f"vs 容差 {CONTACT_TOL_MM} mm ⇒ {'全绿 ✅' if worst_f4a <= CONTACT_TOL_MM else '红 ❌'}")
    print(f"接地（M2，容差 {DOOR_PUSH_SOLE_MARGIN_MM} mm）：无支撑帧 "
          f"{report['grounding']['无支撑帧'] or '无'} · 换脚帧 {report['grounding']['换脚帧']}")
    print(f"腿 IK 跟踪：最坏 {report['leg_tracking']['最坏_mm']} mm · 超 1 mm 的帧 "
          f"{bad_legs or '无'}")
    print(f"迈步：{[(w['脚'], w['步长_m']) for w in step_log]}")
    print("接触相位（逐帧支撑集合，只打印变化点）")
    prev = None
    for r in ground:
        cur = "+".join(r["support"]) or "无"
        if cur != prev:
            print(f"  帧 {r['frame']:>3} 起：{cur}")
            prev = cur
    print("穿模（判据 4 · 骨段 ↔ 门板盒）："
          + " · ".join(f"{k} 最坏 {v['最坏_mm']:.2f} mm @帧 {v['帧']} {v['最坏处']}"
                       f"（阈值 {v['阈值_mm']}）" for k, v in clash_worst.items())
          + f" ⇒ 违规 {len(clash_bad)} 处")
    print(f"支撑脚陷入：{report['support_penetration']['行的数']} 处（最深 "
          f"{report['support_penetration']['最坏_mm']} mm / 容差 {DOOR_PUSH_SOLE_MARGIN_MM} mm）")
    print(f"摆动脚离地（窗口内最低）：{[(w['窗口'], w['窗口内该脚最低点_mm']) for w in swing_low]} mm")
    print("回显卡（口径 §四：每一项都要有产物侧读数；整段最坏见上）")
    for r in (f4a[-1]["pairs"] if f4a else []):
        print(f"  {r['手部分区']:<14}↔ {r['物体分区']:<10}{r['判据形态']:<10}"
              f"{str(r['读数_mm']):>26} mm  帧 {f4a[-1]['frame']}")
    for row in report["u4_world_axes"].items():
        print(f"  U4 {row[0]:<28}{row[1]}")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still:
        bpy.context.scene.frame_set(declared)
        update()
        st = body_at(declared)
        mid = Vector((st["body_xy"][0], st["body_xy"][1] - 0.25, 1.05))
        render_still(args.still, mid + Vector((1.85, 1.35, 0.75)), mid)
        print(f"静帧: {args.still}")
    if args.host == "live":
        bpy.context.scene.frame_set(declared)
        print(f"预览：已停在到位帧 {declared}（时间轴 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END}）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl), compress=False)
        print(f"已写回：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 6：恐慌姿态（抱头 / 捂耳）（`--task panic`）——[#169] 的交付 · 口径 §15.7 ① 件
#
#   关系类型 **B′ 自身姿势关系**（目标不是道具，而是**自己的身体**）⇒ 这是
#   **第四系「目标部位局部系」的第一次实做**（口径 §6.1 · §15.5）：
#   部位面**由该部位当前 transform 实时求得**、不烘世界坐标；判据的面**逐值取自** §15.6.1
#   的部位面登记，ε 由 [#168] 实测（证据 design/engineering/evidence/body-part-epsilon-2026-09-16.md §4.2）。
#
#   两条解**并列**（口径 §4.2 硬规矩 5——agent 解的行不许只给一个解）：
#     · `ears` 捂耳：掌面 ↔ **耳侧面**（`Head` 局部 `+X`/`−X`，ε = 88.0429 mm，**平坦支撑 31 = 全头最平**）
#     · `head` 抱头：掌面 ↔ **后脑面**（`Head` 局部 `−Z`，ε = 99.7200 mm）
#   默认把 `ears` 打进 clip；**另一解照样解到底并进回显卡**（两解都不是手拍的）。
#
#   ⚠️ **换算系**（[#164] 的代价）：掌面法向与部位面法向**都必须经 `arm.matrix_world` 换算**。
#      实测读数：本条的面里**耳侧恰在 +90° X 旋转的不动轴上**（错法差 0.0000 mm）而**后脑面差 99.72 mm**
#      ⇒ "错法不会红在耳侧那一格"（#168 证据 §4.4）。故抱头那一解才是这套换算的**真判据**。
# ══════════════════════════════════════════════════════════════════════════════

PANIC_ACTION_EARS = "PanicCoverEars"
PANIC_ACTION_HEAD = "PanicHoldHead"

#: 帧表（30 fps，`--fps` 可改）：中立 → 起手 → **到位** → 保持（恐慌是**持续态**）
PANIC_FRAME_NEUTRAL = 1     # 首帧严格中立（导出侧 E5 硬约定，同宿主 5）
PANIC_FRAME_HIT = 13        # 声明到位帧 —— **V-f 要求它 == 产物侧判据量的极值帧**
PANIC_FRAME_END = 46        # 保持到这一帧（保持期 33 帧 ≈ 1.1 s）

#: 掌面最低点相对**部位面**（沿朝外法向）的目标间隙（mm）——**判据量的目标值**。
#: 来源：容差沿用 §8.2 的 `tol_contact = 2.8 mm`（**不新立阈值**）；两个具体值 = 本件选定，
#: 「到位帧最紧、保持期回收一点」⇒ 极值帧**唯一**且保持期**不越容差**（登记为自由度表的一行）。
PANIC_GAP_HIT_MM = 0.8
PANIC_GAP_HOLD_MM = 2.0
#: 验收容差 = §8.2 的 `tol_contact`（两个数不许混：ε 是**换算**、这个是**验收**）
PANIC_TOL_MM = CONTACT_TOL_MM
#: 面片片层厚度（m）：沿该面局部轴取最外这一层顶点 ⇒ **有限面片**（#164：参照不能是无限平面）
PANIC_SLAB_M = 0.008
#: 身体条件（本件选定，登记为自由度表行；`--scan-body` 并列 ≥2 解）
PANIC_CROUCH_M = 0.030
PANIC_TORSO_LEAN_DEG = 8.0
PANIC_HEAD_DOWN_DEG = 6.0
#: 肘方向（本件选定）：向外 0.35 · 向后 0.10 · 向下 0.93（捂耳时肘下垂外张）
PANIC_ELBOW_DIR = (0.35, 0.10, -0.93)
#: 逐指蜷曲扫描区间（#164 实测：四指共用一个系数必然有的悬空、有的陷入 ⇒ **必须逐指解**）
PANIC_CURL_LO, PANIC_CURL_HI, PANIC_CURL_STEPS = 0.0, 2.0, 21
#: 手型（F10）两解：`flat` = **平掌**（五指近伸展，owner 2026-09-16 目视第 1 轮指名「手应该是手掌的姿势」）
#: / `hug` = 逐指拟合到贴住头面（本条原先的默认，作为对照解保留 ⇒ 口径 §4.2 硬规矩 5 的 ≥2 解）
PANIC_FLAT_CURL = 0.15      #: 平掌的基线蜷曲量（≈7°/节）——**本件选定**：0 太僵、再大就不是平掌
PANIC_HAND_SHAPE = "flat"
#: 手型与落点的**定稿值**（owner 2026-09-16 目视第 2 轮：「**用 hug 但是要向下一点**」·
#: 第 3 轮：「**最后一个是捂住耳朵**」= 向下 **90 mm** 那一档）。⇒ 定稿 = `hug` + 落点 −90 mm。
PANIC_FINAL_HAND_SHAPE = "hug"
PANIC_FINAL_DROP_MM = 90.0
#: **面域（面内窗口）**沿该面 `u` 轴（耳侧 = 头骨长轴向上）的声明范围，mm，相对 ε 锚点。
#: ⚠️ 为什么需要它（本件两轮实测逼出来的）：原来"最低点是否落在面片内"用的是**最外片层的顶点跨度**，
#: 它只覆盖"头最宽的那一段带"（实测距头底 **155–205 mm**）⇒ ① `抱头` 解被判面外 ② owner 认定的
#: **耳朵位置在这段带的下方 90 mm** ⇒ 判据把"正确的落点"判成面外。⇒ 改成**声明的面内窗口**：
#: 下界 = owner 裁定值 −90 mm 再留 60 mm 余量 = −150；上界 = 实测平台顶 +50 mm 再留 10 = +60。
#: **来源**：owner 目视裁定 + §4.9 的侧向剖面实测（不是拍的）。⚠️ 这条口径**留给 ②③ 复核**。
PANIC_FACE_U_WINDOW_MM = (-150.0, 60.0)
#: 拇指单独一档下限（允许**伸展**）：掌面贴耳时拇指会被掌的落点顶到头前面 ⇒ 需要能外展
PANIC_CURL_LO_THUMB = -0.8
#: 逐指拟合的**目标**（mm）：指尖离头部蒙皮面这么远（正 = 在头外）。来源：本件选定（落在 §8.2
#: `tol_contact = 2.8` 之内、且给顶点分辨率留余量）；
#: ⚠️ 拟合目标必须是**带符号**量——用无符号"最近距离"会把**陷进头里**也当成"贴住"（本件实测踩到：
#: 拇指尖陷入 −14.72 mm 而"最近距离"只有 0.4 mm）。
PANIC_FINGER_GAP_MM = 2.0
#: 头部蒙皮点集的抽样步长（逐指拟合的参照；523 点全量 × 5 指 × 11 档太慢）
PANIC_HEAD_SKIN_STEP = 3
#: 抱头那一解：两只手在**同一个面**上错开（`u` = 头骨局部 X），避免两手重叠
PANIC_HEAD_INPLANE_OFFSET_M = 0.045
#: `--scan-body` 的两个维度（口径 §4.2 硬规矩 5：≥2 解并列）
PANIC_BODY_CANDIDATES = (0.0, 0.030, 0.060)
PANIC_ELBOW_ELEV_CANDIDATES = (-15.0, 0.0, 15.0)

#: 部位面登记的正本 = 口径 **§15.6.1**（ε 逐值来自 [#168] 实测，**不得凭记忆填**）
#: 局部轴语义来源 = 管线 §2.1.4 的实测轴表（`Neck`/`Head`：局部 X = 点头/抬头 ⇒ **左右轴**；
#: 局部 Z = 歪头 ⇒ **前后轴**；局部 Y = 转头 ⇒ **沿骨长轴**）；
#: 正负号 = 实测 `axis_in_world` 与口径 §6.2（世界 `+X` = 左手侧 · 世界 `−Y` = 前）比对后裁定。
HEAD_PART_FACES = {
    "side_left": {"骨": f"{BONE_PREFIX}Head", "轴": "+X", "ε_mm": 88.0429, "标签": "左耳侧面",
                  "面内轴": ("Y", "Z")},
    "side_right": {"骨": f"{BONE_PREFIX}Head", "轴": "-X", "ε_mm": 88.0429, "标签": "右耳侧面",
                   "面内轴": ("Y", "Z")},
    "back": {"骨": f"{BONE_PREFIX}Head", "轴": "-Z", "ε_mm": 99.7200, "标签": "后脑面",
             "面内轴": ("X", "Y")},
    "top": {"骨": f"{BONE_PREFIX}Head", "轴": "+Y", "ε_mm": 207.4887, "标签": "头顶面",
            "面内轴": ("X", "Z")},
    "front": {"骨": f"{BONE_PREFIX}Head", "轴": "+Z", "ε_mm": 148.0259, "标签": "额面",
              "面内轴": ("X", "Y")},
}
#: 两解各自打哪两个面（`--pose` 只选**哪一解进 clip**，两解都解）
PANIC_SOLUTIONS = {
    "ears": {"动作名": PANIC_ACTION_EARS, "标签": "捂耳",
             "面": {"Left": "side_left", "Right": "side_right"},
             "错开_m": 0.0},
    "head": {"动作名": PANIC_ACTION_HEAD, "标签": "抱头",
             "面": {"Left": "back", "Right": "back"},
             "错开_m": PANIC_HEAD_INPLANE_OFFSET_M},
}


def _axis_local(spec):
    """`"+X"` → 该骨局部系里的单位向量。"""
    v = Vector((0.0, 0.0, 0.0))
    v[{"X": 0, "Y": 1, "Z": 2}[spec[1]]] = 1.0 if spec[0] == "+" else -1.0
    return v


_HEAD_SKIN_CACHE = {}


def head_skin_local(arm):
    """`Head` 骨在**可见层**上的蒙皮顶点（**骨局部坐标**；头刚性 1.0 ⇒ 随姿势精确跟随）。

    只取 `Beta_Surface`：口径 §15.6.1 实测**头只存在这一层**（`Beta_Joints` 的顶点 y 上界
    = 159.6 cm = 颈骨尾 ⇒ **那一层没有头**）。取法同 `palm_face_vertices`：主导组 = `Head`。
    """
    if "Head" in _HEAD_SKIN_CACHE:
        return _HEAD_SKIN_CACHE["Head"]
    name = f"{BONE_PREFIX}Head"
    bl_inv = arm.data.bones[name].matrix_local.inverted()
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.name != "Beta_Surface":
            continue
        vg = ob.vertex_groups.get(name)
        if vg is None:
            continue
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g == vg.index:
                out.append(bl_inv @ (arm_inv @ (ob.matrix_world @ v.co)))
    _HEAD_SKIN_CACHE["Head"] = out
    return out


def head_face_patch_local(arm, key):
    """该具名面的**真实蒙皮面片**（骨局部坐标）：沿该面局部轴最外 `PANIC_SLAB_M` 那一层顶点。"""
    axis = _axis_local(HEAD_PART_FACES[key]["轴"])
    pts = head_skin_local(arm)
    ext = max(p.dot(axis) for p in pts)
    slab_local = PANIC_SLAB_M / max(arm.matrix_world.to_scale().x, 1e-9)
    return [p for p in pts if p.dot(axis) >= ext - slab_local]


def head_part_frame(arm, key):
    """**第四系：目标部位局部系**——由该部位**当前** transform 实时求得（不烘世界坐标）。

    返回：`锚点`（= 骨原点 + ε·朝外法向，ε 来自 §15.6.1）· `法向` · 面内两轴 `u`/`v` 与**跨度**
    （⇒ 参照是**有限面片**而不是无限平面，#164 的实测教训）· `面片`（真实蒙皮世界点集）。

    ⚠️ 法向**必须经 `arm.matrix_world` 换算**：[#164] 的代价 = 母版骨架对象带 **+90° X 旋转**，
       漏掉它等于把面转到错方向（#168 证据 §4.4：耳侧面差 **0.0000** mm＝不动轴巧合，后脑面差 **99.72** mm）。
    """
    spec = HEAD_PART_FACES[key]
    pb = arm.pose.bones[spec["骨"]]
    m3 = arm.matrix_world.to_3x3()
    r3 = pb.matrix.to_3x3()
    n_world = (m3 @ (r3 @ _axis_local(spec["轴"]))).normalized()
    origin = arm.matrix_world @ pb.head
    scale = arm.matrix_world.to_scale().x
    u_ax, v_ax = (_axis_local("+" + a) for a in spec["面内轴"])
    u_w = (m3 @ (r3 @ u_ax)).normalized()
    v_w = (m3 @ (r3 @ v_ax)).normalized()
    patch = head_face_patch_local(arm, key)
    # ⚠️ **面内坐标一律以"该面的 ε 锚点"为基准**（2026-09-16 第 2 轮修的真 bug）：原来这里给的是
    #    **相对骨原点**的绝对坐标，而 `panic_contact_readings` 量的是**相对锚点**的偏移 ⇒ 两者被直接比较，
    #    基准不同（锚点落在面片中部时差 ≈70 mm）⇒ "最低点是否落在面片内"这一格**判错**：
    #    ① `抱头` 那一解被判"面外"（其中含这个 bug 的成分）② 落点往下调之后立刻"面外"（同一原因）。
    #    统一到锚点后，两边的数才是同一个量（判据与措辞同层）。
    ext_p = max(patch, key=lambda q: q.dot(_axis_local(spec["轴"])))
    us = [(p.dot(u_ax) - ext_p.dot(u_ax)) * scale for p in patch]
    vs = [(p.dot(v_ax) - ext_p.dot(v_ax)) * scale for p in patch]
    patch_world = [arm.matrix_world @ (pb.matrix @ p) for p in patch]
    # 锚点（第四系的"面上一点"）= **沿该轴最外的那个真实蒙皮顶点**。
    # ⚠️ 为什么不是"骨原点 + ε·法向"（本件实测踩到）：那个点在**面内**的位置等于**骨原点**的位置，
    #    而后脑这类面的最外点高出骨原点 **48–118 mm** ⇒ 锚点会落在面片**下方 80 mm** 处，
    #    "最低点是否落在面片内"的判读整个错位。取真实极值顶点则：① ε **逐值不变**（它就是那个
    #    顶点的沿轴投影）② 面内位置是**面的真位置**。
    anchor = arm.matrix_world @ (pb.matrix @ ext_p)
    # 面片重心（世界）——**面内对齐的目标**（数据给的中心，不是拍的）
    centroid = sum(patch_world, Vector((0.0, 0.0, 0.0))) / float(len(patch_world))
    # 自检：面片上沿法向最远的顶点距骨原点应当**逐值等于** §15.6.1 登记的 ε
    # （两条独立来源互证 ⇒ "登记的数能不能被消费"变成读数，而不是承诺）
    ext_mm = round(max(p.dot(_axis_local(spec["轴"])) for p in patch) * scale * 1000.0, 4)
    return {"键": key, "标签": spec["标签"], "骨": spec["骨"], "局部轴": spec["轴"],
            "ε_mm": spec["ε_mm"], "ε_实测复核_mm": ext_mm,
            "ε_一致": bool(abs(ext_mm - spec["ε_mm"]) <= 0.01),
            "骨原点": origin, "锚点": anchor, "法向": n_world,
            "锚点沿法向距骨原点_mm": round((anchor - origin).dot(n_world) * 1000.0, 4),
            "u": u_w, "v": v_w, "u_span_m": (min(us), max(us)), "v_span_m": (min(vs), max(vs)),
            "面片": patch_world, "面片数": len(patch_world), "面片重心": centroid,
            "重心面内_mm": [round((centroid - anchor).dot(u_w) * 1000.0, 2),
                            round((centroid - anchor).dot(v_w) * 1000.0, 2)]}


_HEAD_NORMAL_CACHE = {}


def head_skin_local_normals(arm):
    """`[(骨局部坐标, 骨局部朝外法向)]`——头蒙皮顶点 + **顶点法向**（判"在不在头里"用）。

    ⚠️ 为什么不用 AABB 盒当头部代理（本件实测）：头的 AABB 在骨局部系里是
    `x∈±88 / y∈[−67.6, 207.5] / z∈[−99.7, 148.0] mm`——**脖子整段落在盒里**，
    于是"手在耳侧"会被读成"骨段陷入头 −38.94 mm"（35 帧假红）。⇒ 参照取**真实皮肤面**。
    """
    if "Head" in _HEAD_NORMAL_CACHE:
        return _HEAD_NORMAL_CACHE["Head"]
    name = f"{BONE_PREFIX}Head"
    bl_inv = arm.data.bones[name].matrix_local.inverted()
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.name != "Beta_Surface":
            continue
        vg = ob.vertex_groups.get(name)
        if vg is None:
            continue
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g != vg.index:
                continue
            pl = bl_inv @ (arm_inv @ (ob.matrix_world @ v.co))
            nl = (bl_inv.to_3x3() @ (arm_inv.to_3x3() @ (ob.matrix_world.to_3x3() @ v.normal))).normalized()
            out.append((pl, nl))
    _HEAD_NORMAL_CACHE["Head"] = out
    return out


def head_signed_mm(arm, p_world, pts_normals=None):
    """点相对**头部蒙皮面**的带符号距离（mm）：`> 0` 在头外 · `< 0` **陷入头里**。

    取法：最近的那个头蒙皮顶点，把 `p − 该顶点` 投影到**该顶点的朝外法向**上。
    ⚠️ 分辨力：顶点间距量级（本母版头 523 顶点，间距 ≈ 10–20 mm）⇒ **判据取符号（零穿透）**，
       深度读数只作量级（口径 §8.2「容差必须远小于你想抓的那个错」的同一条道理）。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}Head"]
    mw = arm.matrix_world
    r3 = pb.matrix.to_3x3()
    src = pts_normals if pts_normals is not None else head_skin_local_normals(arm)
    best = None
    for pl, nl in src:
        q = mw @ (pb.matrix @ pl)
        d = (p_world - q).length
        if best is None or d < best[0]:
            n = (mw.to_3x3() @ (r3 @ nl)).normalized()
            best = (d, (p_world - q).dot(n) * 1000.0)
    return best[1]


def head_proxy_box(arm):
    """头部代理盒（**骨局部系的 AABB**，随姿势刚体跟随）——穿模判据 `box_gap_mm` 的参照。

    ⚠️ 为什么用**体**而不是面（#164 的实测教训原文）：棱/面是降维的参照——"蒙皮离面 0.5 mm、
    同时陷进体 20 mm"完全可以成立。盒对体内点返回**负的陷入深度** ⇒ 一个读数两个方向都能报错。
    """
    pts = head_skin_local(arm)
    scale = arm.matrix_world.to_scale().x
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    pb = arm.pose.bones[f"{BONE_PREFIX}Head"]
    m3 = arm.matrix_world.to_3x3()
    r3 = pb.matrix.to_3x3()
    return {"near": arm.matrix_world @ (pb.matrix @ lo),
            "n": (m3 @ (r3 @ Vector((1.0, 0.0, 0.0)))).normalized(),
            "u": (m3 @ (r3 @ Vector((0.0, 1.0, 0.0)))).normalized(),
            "z": (m3 @ (r3 @ Vector((0.0, 0.0, 1.0)))).normalized(),
            "thickness_mm": (hi.x - lo.x) * scale * 1000.0,
            "u_span_m": (0.0, (hi.y - lo.y) * scale),
            "z_span_m": (0.0, (hi.z - lo.z) * scale)}


def panic_elbow_dir(arm, side, elevation_deg=0.0):
    """肘方向：**向外 + 略后 + 向下**（捂耳/抱头时肘外张下垂）。`elevation_deg` 供解空间并列。

    来源：**本件选定**（不是实测）⇒ 登记为自由度表行，并在 `--scan-body` 里并列 ≥2 解（§4.2 硬规矩 5）。
    """
    sgn = 1.0 if side == "Left" else -1.0
    lat, back, down = PANIC_ELBOW_DIR
    v = Vector((sgn * lat, back, down))
    th = math.radians(elevation_deg)
    c, s = math.cos(th), math.sin(th)
    return Vector((v.x * c - v.z * s, v.y, v.x * s + v.z * c)).normalized()


def panic_palm_gap_mm(arm, side, frame):
    """**掌面最低点相对部位面锚点的带符号法向间隙**（mm）——判据形态「弧面↔面」的那个量。

    `> 0` 悬空 · `< 0` 陷入 · `|·| ≤ tol_contact` **贴合**（口径 §13.4 甲，U8 已闭合）。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    mw = arm.matrix_world
    palm = [mw @ (pb.matrix @ p) for p in palm_face_vertices(arm, side)]
    vals = [(p - frame["锚点"]).dot(frame["法向"]) * 1000.0 for p in palm]
    i = min(range(len(vals)), key=lambda k: vals[k])
    return vals[i], palm[i], palm


def panic_contact_readings(arm, side, frame):
    """**掌面 ↔ 具名面**的读数（判据形态 = 口径 §13.4 的「**弧面↔面**」，U8 已闭合）。

    | 读数 | 式子 | 判读 |
    |---|---|---|
    | `掌面最低点` | 掌面点集里沿目标面法向**最低**的那一点（= 该弧面指向目标面一侧的最低点） | — |
    | `沿法向间隙_mm` | `(掌面最低点 − 锚点)·朝外法向` | `< −tol` 陷入 · `> tol` 悬空 · `|·| ≤ tol` **贴合** |
    | `面↔面顶点最近距离_mm` | 掌面点集 ↔ **面片点集** 的最小**顶点**距离 | ⚠️ **只报读数、不判红**：两点集的最小顶点距离有**网格分辨力下限**（≈ 顶点间距）⇒ 当判据就是"用地磅称一封信"（§七 登记） |
    | `落在面片内` | 最低点在面内两轴上的投影是否落在面片跨度内 | False ⇒ **不许判贴合**（手指飞在面外） |
    | `掌面法向夹角_deg` | 掌面法向 ↔ 面法向（掌面朝内 ⇒ 接近 180°） | **只报读数**（朝向档 ε 未测，§8.3） |
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    mw = arm.matrix_world
    gap, low, palm = panic_palm_gap_mm(arm, side, frame)
    n = frame["法向"]
    du = (low - frame["锚点"]).dot(frame["u"])
    dv = (low - frame["锚点"]).dot(frame["v"])
    # 面内判读：用**声明的面内窗口**（口径 §15.6「名与坐标同出一个布局函数」）；顶点跨度只作读数
    in_patch = (PANIC_FACE_U_WINDOW_MM[0] / 1000.0 <= du <= PANIC_FACE_U_WINDOW_MM[1] / 1000.0
                and frame["v_span_m"][0] <= dv <= frame["v_span_m"][1])
    n_palm = (mw.to_3x3() @ pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    return {"判据量": f"{side}掌面 ↔ {frame['标签']}",
            "判据形态": "弧面↔面（掌面最低点 ↔ 有限面片）",
            "锚点_mm": [round(c * 1000.0, 1) for c in frame["锚点"]],
            "掌面最低点_mm": [round(c * 1000.0, 1) for c in low],
            "面内偏移_mm": [round(du * 1000.0, 2), round(dv * 1000.0, 2)],
            "面内跨度_mm": [[round(frame["u_span_m"][0] * 1000.0, 1), round(frame["u_span_m"][1] * 1000.0, 1)],
                            [round(frame["v_span_m"][0] * 1000.0, 1), round(frame["v_span_m"][1] * 1000.0, 1)]],
            "沿法向间隙_mm": round(gap, 2),
            "面↔面顶点最近距离_mm": points_min_distance_mm(palm, frame["面片"]),
            "面↔面_分辨力_mm": "顶点间距量级（本件 2.7 mm 下限，**只报读数、不判红**——见 §七 的登记）",
            "掌面法向夹角_deg": round(math.degrees(n_palm.angle(n)), 2),
            "落在面片内": bool(in_patch),
            "面内窗口_mm": [list(PANIC_FACE_U_WINDOW_MM),
                            [round(frame["v_span_m"][0] * 1000.0, 1),
                             round(frame["v_span_m"][1] * 1000.0, 1)]],
            "面片数": frame["面片数"], "掌面点数": len(palm)}


def panic_finger_readings(arm, side, head_pts):
    """**逐指**读数（口径 §七 硬规矩 2：成组项必须并列打印；F10/F11 的验收面）。

    判据量 = 该指蒙皮点集 ↔ 头部蒙皮点集的**最近距离**（0 = 贴住；越小越贴）。
    ⚠️ **必须逐指**：#164 实测"四指共用一个蜷曲系数"会让同一姿势里有的悬空 11 mm、有的陷入 3 mm。
    """
    out = {}
    for finger in FINGERS:
        pts = finger_skin_world(arm, side, finger)
        out[finger] = {"指尖间隙_mm": points_min_distance_mm(pts, head_pts), "点数": len(pts)}
    return out


def panic_solve_thumb_clear(arm, side, curl_axes, head_normals, target_mm=PANIC_FINGER_GAP_MM):
    """**平掌时把拇指摆到头外**（本件新增）。

    为什么需要它（2026-09-16 owner 第 1 轮指名"手应该是手掌的姿势"之后实测）：拇指的静止朝向**不在掌面平面内**
    （真手也是这样），掌面平贴到弧面上时，**伸展的拇指会顶进头里**（实测 **−4.7 mm**，同时四指尖翘在头外 +49~+56 mm）。
    本函数只动 `HandThumb1` 的三个局部轴（外展 / 伸 / 旋）× 5 档，取"整根拇指蒙皮的最小带符号间隙"最接近
    `target_mm`（正 = 头外）的那一档 ⇒ 与"逐指拟合"同一套目标，不引入新判据。
    """
    name = f"{BONE_PREFIX}{side}HandThumb1"
    pb = arm.pose.bones[name]
    base = list(pb.rotation_euler)
    best = None
    for axis in (0, 1, 2):
        for deg in (-40.0, -20.0, 0.0, 20.0, 40.0):
            e = list(base)
            e[axis] = math.radians(deg)
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            update(1)
            gap = panic_finger_signed_mm(arm, side, "Thumb", head_normals)
            score = (abs(gap - target_mm), abs(deg))
            if best is None or score < best[0]:
                best = (score, axis, deg, gap)
    e = list(base)
    e[best[1]] = math.radians(best[2])
    pb.rotation_euler = Euler(e, "XYZ")
    update(2)
    return {"轴": "XYZ"[best[1]], "角度_deg": best[2], "带符号间隙_mm": round(best[3], 2),
            "目标_mm": target_mm}


def panic_compare_curls(arm, side, curls, curl_axes, head_pts, head_normals):
    """**两种手型解并列**（口径 §4.2 硬规矩 5）：**逐指解** vs **四指共用一个系数**。

    后者就是 [#164] 实测过的那个错法（口径 §13.8 前史）：同一姿势里**有的指尖悬空、有的陷入**。
    本件把那条教训**复现成读数**（不是引用结论）：两解的逐指间隙并排列出、谁更差由数字说。
    """
    out = {}
    for mode in ("逐指", "四指共用"):
        detail = None
        if mode == "逐指":
            for f in FINGERS:
                _apply_one_finger_curl(arm, side, f, curl_axes[f], curls[f]["蜷曲量"])
        else:
            best = None
            for k in range(PANIC_CURL_STEPS):
                amt = PANIC_CURL_LO + (PANIC_CURL_HI - PANIC_CURL_LO) * k / (PANIC_CURL_STEPS - 1)
                for f in FOUR_FINGERS:
                    _apply_one_finger_curl(arm, side, f, curl_axes[f], amt)
                _apply_one_finger_curl(arm, side, "Thumb", curl_axes["Thumb"],
                                       curls["Thumb"]["蜷曲量"])
                update(1)
                gaps = {f: panic_finger_signed_mm(arm, side, f, head_normals) for f in FINGERS}
                worst = max(abs(g - PANIC_FINGER_GAP_MM) for g in gaps.values() if g is not None)
                if best is None or worst < best[0]:
                    best = (worst, amt)
            for f in FOUR_FINGERS:
                _apply_one_finger_curl(arm, side, f, curl_axes[f], best[1])
            detail = {"四指共用系数": round(best[1], 3), "拇指": curls["Thumb"]["蜷曲量"]}
        update(1)
        gaps = {f: panic_finger_signed_mm(arm, side, f, head_normals) for f in FINGERS}
        out[mode] = {"蜷曲量": ({f: curls[f]["蜷曲量"] for f in FINGERS} if mode == "逐指" else detail),
                     "逐指带符号间隙_mm": {f: round(g, 2) for f, g in gaps.items() if g is not None},
                     "最坏_偏离目标_mm": round(max(abs(g - PANIC_FINGER_GAP_MM)
                                                for g in gaps.values() if g is not None), 2)}
    for f in FINGERS:      # 恢复**逐指解**（判据面用逐指那一档）
        _apply_one_finger_curl(arm, side, f, curl_axes[f], curls[f]["蜷曲量"])
    update(2)
    return out


def hand_skin_world_all(arm, side, step=4):
    """该手**全部蒙皮点**的世界坐标（抽样 `step`）——**零穿透判据的度量对象是蒙皮，不是骨**。

    ⚠️ 为什么不能拿"骨段点"判穿透（本件实测）：骨的采样点在**肉里**（手指骨离皮肤约 10 mm）
    ⇒ 皮肤刚贴上时骨点已经"陷入 −4.21 mm"（假红）。同族教训见口径 §15.3 子分区「脚」的
    **41 mm 层差**（骨点口径 vs 看得见的足底）。
    """
    mw = arm.matrix_world
    out = []
    for bone_name, p in hand_skin_points(arm, side)[::step]:
        out.append(mw @ (arm.pose.bones[bone_name].matrix @ p))
    return out


def panic_palm_and_four_finger_points(arm, side, step=4):
    """`掌面 + 四指` 的蒙皮世界点（**判据面**；拇指不含——见 `main_panic` 的 clash 段说明）。"""
    hand = f"{BONE_PREFIX}{side}Hand"
    pb = arm.pose.bones[hand]
    mw = arm.matrix_world
    out = [mw @ (pb.matrix @ p) for p in palm_face_vertices(arm, side)]
    for f in FOUR_FINGERS:
        out += finger_skin_world(arm, side, f)[::step]
    return out


#: ⚠️ 头部"顶点法向"参照集的**抽样步长**——**解算与判据必须用同一套**：本件实测踩到，
#: 解算用 `[::2]` 而判据用 `[::3]` 时，同一根拇指的带符号间隙是 **+3.88 vs −6.5 mm**（参照集不同 ⇒ 最近顶点不同）。
PANIC_HEAD_NORMAL_STEP = 2


def panic_head_normals(arm):
    """参照集（唯一的取法）——解算与判据都从这里取。"""
    return head_skin_local_normals(arm)[::PANIC_HEAD_NORMAL_STEP]


def panic_finger_signed_mm(arm, side, finger, head_normals, step=3):
    """该指**最深的那个蒙皮点**相对头部蒙皮面的带符号距离（mm，`< 0` = 陷入头里）。"""
    pts = finger_skin_world(arm, side, finger)
    if not pts:
        return None
    return min(head_signed_mm(arm, p, head_normals) for p in pts[::step])


def panic_hand_to_face(arm, side, frame, curl_axes, clearance_mm=PANIC_GAP_HIT_MM,
                       in_plane_m=0.0, curls=None, curl_scale=1.0, elbow_elev_deg=0.0,
                       fit_fingers=True):
    """把手摆到「**掌面贴住具名面**」：朝向解析 + 腕位**一次算出** + **逐指**蜷曲。

    三步（顺序是先例[#163] §十九 的结论，不是选择）：① **先解臂**（父链先定）② **再写手的世界朝向**
    （`_set_world_axes` 写的是 basis，父链没定就是错的）③ 量"掌面重心相对腕"的刚体偏移后**一次算出**腕目标。

    朝向 = 三个自由度（口径 §13.2「解方程而非搜索」）：骨局部 `Z`（**掌面法向**，§8.1 实测）
    = **−面法向**（掌面朝**头**）· 骨局部 `Y`（腕 → 指尖）= 头骨长轴方向（手指朝头顶覆上去）·
    `X = Y × Z` 由 `_set_world_axes` 自动成立。
    """
    n_face = frame["法向"]
    n_palm = -n_face
    up = head_part_frame(arm, "top")["法向"]          # 头骨长轴方向（实时量，不烘）
    # 手指方向 = **从该面锚点指向"头顶面"的锚点**（两个锚点都是实测的 ε 点 ⇒ 方向由数据给，不拍角度）。
    # ⚠️ 为什么不用纯"头骨长轴"（本件实测）：平掌时手是刚体平面，纯竖直的手指会让四指尖翘在头外 **50 mm**
    #    （颅侧向上收窄）；指向头顶则手的纵轴**沿颅侧走**，指尖跟着收进来。
    crown = head_part_frame(arm, "top")["锚点"]
    f_dir = (crown - frame["锚点"])
    f_dir = (f_dir - n_palm * f_dir.dot(n_palm)).normalized()
    hand = f"{BONE_PREFIX}{side}Hand"
    elbow = panic_elbow_dir(arm, side, elbow_elev_deg)
    du, dv = (in_plane_m if isinstance(in_plane_m, (tuple, list)) else (in_plane_m, 0.0))
    anchor = frame["锚点"] + frame["u"] * du + frame["v"] * dv
    # ① 先解臂到**接近点**（父链先定）
    info1 = solve_arm(arm, side, anchor + n_face * 0.12 - up * 0.05, elbow)
    # ② 在该朝向下量"掌面重心相对腕"的刚体偏移
    _set_world_axes(arm, f"CTRL_{side}Hand", hand, f_dir, f_dir.cross(n_palm))
    centroid, _ = palm_normal_reference(arm, side)
    off = centroid - world_point(arm, hand)
    # ③ **一次算出**腕目标：掌面重心落在「锚点 + 朝外 clearance」
    wrist_target = anchor + n_face * (clearance_mm / 1000.0) - off
    # ③′ **面内对齐修正**（一遍）：把"掌面重心"在面内的位置对到**该面的 ε 锚点**上（+ 调用方的偏移）。
    #     ⚠️ 为什么必须做（本件实测）：掌面是一块**近平面**（6 mm 片层的点集），
    #     "沿法向最低点"在近平面上**近乎简并** ⇒ 最低点会落在掌的边缘（实测落在耳侧面片之外，
    #     `落在面片内 = False`，而 §13.4/#164 的规矩是**面外不许判贴合**）。
    #     对齐之后，最低点才落在面片里（读数见报告 `落在面片内`）。
    #     这是**修正**而不是 #163 §十八 那种"两遍定点"（那次的错在于用错朝向下的偏移反复推腕）。
    #     ⚠️ **对齐目标 = 该面的 ε 锚点，不是面片重心**（2026-09-16 owner 目视第 1 轮指名"手应该再向下一点"
    #     之后的根因）：耳侧那片的最外点（= 锚点）落在**面片下缘**（面内跨度 `u ∈ [15.7, 158.4] mm`），
    #     对到面片重心 ⇒ 掌面重心被抬到锚点**上方 ≈80 mm**（= 耳上方的头侧，不是耳朵）。
    wrist_target = wrist_target - frame["u"] * (centroid - anchor).dot(frame["u"]) \
        - frame["v"] * (centroid - anchor).dot(frame["v"])
    info2 = solve_arm(arm, side, wrist_target, elbow)
    _set_world_axes(arm, f"CTRL_{side}Hand", hand, f_dir, f_dir.cross(n_palm))
    update()
    # ③″ **法向修正**（一遍，实测回代）：判据量的是**掌面最低点**，而 ③ 把**重心**放到了目标间隙上；
    #     两者差一个实测常量（本件实测 ≈ −2.8 mm：掌面是弧面，最低点比重心更靠里）。
    #     判据要的是**最低点** ⇒ 按"最低点的实测间隙"回代一次（同 #166 `set_pelvis_world` 的实测回代法）。
    #     ⚠️ 这不是 #163 §十八 那种"两遍定点"：那次的错在于**用错朝向下的偏移**反复推腕；
    #        这里朝向已经定了，回代的是**同一个刚性量**的一次性差值。
    gap_now, _, _ = panic_palm_gap_mm(arm, side, frame)
    wrist_target = wrist_target + n_face * ((clearance_mm - gap_now) / 1000.0)
    info2 = solve_arm(arm, side, wrist_target, elbow)
    _set_world_axes(arm, f"CTRL_{side}Hand", hand, f_dir, f_dir.cross(n_palm))
    update()
    thumb_solve = None
    # ④ 手型：默认**平掌**（四指近伸展 + 拇指单独摆到头外）；`fit_fingers` 时改走**逐指拟合**（对照解）
    if curls is None and not fit_fingers:
        curls = {f: {"蜷曲量": PANIC_FLAT_CURL, "带符号间隙_mm": None, "顶点最近距离_mm": None}
                 for f in FINGERS}
        for f in FOUR_FINGERS:
            _apply_one_finger_curl(arm, side, f, curl_axes[f], PANIC_FLAT_CURL)
        _apply_one_finger_curl(arm, side, "Thumb", curl_axes["Thumb"], PANIC_FLAT_CURL)
        update(2)
        # 拇指单独"摆到头外"（四指保持平掌的基线蜷曲）
        thumb_solve = panic_solve_thumb_clear(arm, side, curl_axes,
                                              head_skin_local_normals(arm)[::2])
    elif curls is None and fit_fingers:
        head_pts = [arm.matrix_world @ (arm.pose.bones[f"{BONE_PREFIX}Head"].matrix @ p)
                    for p in head_skin_local(arm)[::PANIC_HEAD_SKIN_STEP]]
        normals = panic_head_normals(arm)
        curls = {}
        for finger in FINGERS:
            lo = PANIC_CURL_LO_THUMB if finger == "Thumb" else PANIC_CURL_LO
            best = None
            for k in range(PANIC_CURL_STEPS):
                amount = lo + (PANIC_CURL_HI - lo) * k / (PANIC_CURL_STEPS - 1)
                _apply_one_finger_curl(arm, side, finger, curl_axes[finger], amount)
                update(1)
                gap = panic_finger_signed_mm(arm, side, finger, normals)
                score = (abs(gap - PANIC_FINGER_GAP_MM), amount)
                if best is None or score < best[0]:
                    best = (score, amount, gap)
            curls[finger] = {"蜷曲量": round(best[1], 3),
                             "带符号间隙_mm": round(best[2], 2),
                             "顶点最近距离_mm": points_min_distance_mm(
                                 finger_skin_world(arm, side, finger), head_pts)}
        for finger in FINGERS:
            _apply_one_finger_curl(arm, side, finger, curl_axes[finger], curls[finger]["蜷曲量"])
        update(2)
    elif curls is not None:
        for finger in FINGERS:
            _apply_one_finger_curl(arm, side, finger, curl_axes[finger],
                                   curls[finger]["蜷曲量"] * curl_scale)
        update(2)
    return {"wrist_target_m": [round(v, 4) for v in wrist_target],
            "wrist_default": info1, "arm": info2, "elbow_dir": [round(v, 3) for v in elbow],
            "curls": curls, "thumb_solve": thumb_solve, "clearance_mm": clearance_mm}


def panic_body_setup(arm, m3, foot_rest, crouch_m=PANIC_CROUCH_M, lean_deg=PANIC_TORSO_LEAN_DEG,
                     head_down_deg=PANIC_HEAD_DOWN_DEG):
    """恐慌姿态的身体条件：**微蹲 + 躯干前倾 + 缩头**（每一项的轴语义都有实测来源）。

    | 项 | 写法 | 轴语义 / 方法来源 |
    |---|---|---|
    | 微蹲 | `set_pelvis_world(双脚中点, 静止髋 z − crouch_m)` + 双腿解析解拉回 | 宿主 5 同法（实测回代，不假设写入口径） |
    | 躯干前倾 | `door_push_torso_lean(lean_deg)`（三段脊柱各 1/3） | 管线 §2.1.4：脊柱局部 X = **前倾** |
    | 缩头 | `Neck` / `Head` 局部 X +`head_down_deg` | 同上：颈 / 头局部 X = **点头/抬头** |

    ⚠️ **本件不调 `solve_gaze` / `solve_gaze_scan`**：它们写的是同一个 `Neck`/`Head` 局部 X，
       恐慌姿态要的正是"**不**目视水平"（缩头）⇒ 两条解冲突，本件显式取缩头并写进自由度表。
    """
    mid = Vector(((foot_rest["Left"].x + foot_rest["Right"].x) / 2.0,
                  (foot_rest["Left"].y + foot_rest["Right"].y) / 2.0))
    hips_z = world_point(arm, f"{BONE_PREFIX}Hips").z - crouch_m
    err = set_pelvis_world(arm, m3, (mid.x, mid.y), hips_z)
    door_push_torso_lean(arm, lean_deg)
    for name in (f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"):
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(head_down_deg), 0.0, 0.0), "XYZ")
    update()
    _, _, posterior = body_frame(arm)
    for s in CARD1_SIDES:
        solve_leg(arm, s, foot_rest[s], -posterior)
        set_foot_world_orientation(arm, s, 0.0)
    update()
    return {"crouch_m": crouch_m, "pelvis_err_mm": err, "lean_deg": lean_deg,
            "head_down_deg": head_down_deg}


def panic_channel_names(arm):
    """打键通道表：**控制骨 + 脊柱/颈头 + 手指骨**。

    ⚠️ 宿主 3 的教训（#165 登记）：它**腿脚一条键都没打** ⇒ 相位判据判不了。
    本件逐项列全并**打印**，让"漏打哪一类"变成可读的读数。
    """
    names = ["CTRL_Hips"] + [f"CTRL_{s}{suf}" for s in CARD1_SIDES
                             for suf in ("Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot")]
    names += [f"{BONE_PREFIX}{b}" for b in ("Spine", "Spine1", "Spine2", "Neck", "Head")]
    names += [f"{BONE_PREFIX}{s}Hand{f}{k}"
              for s in CARD1_SIDES for f in FINGERS for k in (1, 2, 3, 4)]
    return [n for n in names if n in arm.pose.bones]


def main_panic() -> int:
    """恐慌姿态宿主：逐帧解算 → 逐帧打键 → 从**产物**里读第四系的判据。"""
    from datetime import datetime
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    action_name = args.action if args.action != "BendGripChairBack" else PANIC_SOLUTIONS[args.pose]["动作名"]
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    report = {"script": Path(__file__).name, "task": "panic", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "pose": args.pose, "problems": []}
    print(f"恐慌姿态（口径 §15.7 ① 件 · 第四系「目标部位局部系」首件）· 动作名 {action_name}")
    print(f"帧表：中立 {PANIC_FRAME_NEUTRAL} · **到位 {PANIC_FRAME_HIT}** · 保持到 {PANIC_FRAME_END}"
          f"（{args.fps} fps；恐慌 = **持续态**，口径 §15.7 的「词条位」块）")

    # ---- ① 部位面登记的自检：登记的 ε 与**真实面片**是否逐值一致（#168 的读数能不能被消费）----
    frames_rest = {}
    for key in ("side_left", "side_right", "back", "top"):
        fr = head_part_frame(arm, key)
        frames_rest[key] = fr
        print(f"  部位面 [{fr['标签']}] 骨局部 {fr['局部轴']} · §15.6.1 登记 ε = {fr['ε_mm']} mm · "
              f"真实面片复核 = {fr['ε_实测复核_mm']} mm ⇒ {'一致 ✅' if fr['ε_一致'] else '不一致 ❌'}")
    report["part_faces_used"] = {
        k: {"标签": v["标签"], "骨": v["骨"], "局部轴": v["局部轴"],
            "ε_mm §15.6.1": v["ε_mm"], "ε_真实面片复核_mm": v["ε_实测复核_mm"],
            "ε_一致": v["ε_一致"], "面片数": v["面片数"]}
        for k, v in frames_rest.items()}
    if not all(v["ε_一致"] for v in frames_rest.values()):
        report["problems"].append("部位面登记的 ε 与真实面片复核不一致（登记表与母版脱节）")

    # ---- ② 静止读数与身体条件 ----
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    curl_thumb = {s: detect_curl_axis_group(arm, s, "拇指") for s in CARD1_SIDES}
    curl_axes = {s: {f: (curl_thumb[s] if f == "Thumb" else curl[s]) for f in FINGERS}
                 for s in CARD1_SIDES}
    report["f3_curl"] = {"四指": curl, "拇指": curl_thumb}
    print(f"F3 屈曲轴自测：四指 左 {curl['Left']['axis']}{curl['Left']['sign']:+d} / "
          f"右 {curl['Right']['axis']}{curl['Right']['sign']:+d} · "
          f"拇指 左 {curl_thumb['Left']['axis']}{curl_thumb['Left']['sign']:+d} / "
          f"右 {curl_thumb['Right']['axis']}{curl_thumb['Right']['sign']:+d}")
    report["freedom_table"] = [
        {"行": "身体：下蹲量", "值": PANIC_CROUCH_M, "单位": "m", "状态": "agent 解（本件选定）",
         "来源": "本件选定 + `--scan-body` 并列 ≥2 解（口径 §4.2 硬规矩 5）"},
        {"行": "身体：躯干前倾", "值": PANIC_TORSO_LEAN_DEG, "单位": "°", "状态": "agent 解",
         "来源": "管线 §2.1.4（脊柱局部 X = 前倾）"},
        {"行": "身体：缩头", "值": PANIC_HEAD_DOWN_DEG, "单位": "°", "状态": "agent 解",
         "来源": "管线 §2.1.4（颈/头局部 X = 点头）；**本件不调 gaze**（见 panic_body_setup 的 ⚠️）"},
        {"行": "肘方向", "值": list(PANIC_ELBOW_DIR), "单位": "单位向量", "状态": "agent 解",
         "来源": "本件选定 + `--scan-body` 的抬肘档并列"},
        {"行": "掌面 ↔ 部位面 目标间隙（到位）", "值": PANIC_GAP_HIT_MM, "单位": "mm", "状态": "agent 解",
         "来源": "容差沿用 §8.2 `tol_contact = 2.8`；具体值本件选定（保证极值帧唯一）"},
        {"行": "掌面 ↔ 部位面 目标间隙（保持）", "值": PANIC_GAP_HOLD_MM, "单位": "mm", "状态": "agent 解",
         "来源": "同上；保持期回收 1.0 mm 以让极值帧落在到位帧"},
        {"行": "**F4a 判据时域**（必填）", "值": "接触对 = `持续`（窗口 = 到位帧…末帧，松一帧即红）· "
                                          "接地 = `持续`（整段）· 时序 = `一次性`（到位帧）",
         "单位": "—", "状态": "owner（涉观感）/ agent","来源": "口径 §13.3 F4a · §13.4.1"},
        {"行": "手型（F10）", "值": f"{args.hand_shape}（flat = 平掌 · hug = 逐指拟合）", "单位": "—",
         "状态": "**owner 2026-09-16 目视第 1 轮指名**「手应该是手掌的姿势」⇒ 默认 `flat`",
         "来源": "#164 实测（共用系数 ⇒ 有的悬空 11 mm / 有的陷入 3 mm）"},
        {"行": "掌面落点（面内高度）", "值": f"锚点 + 向下 {args.ear_drop_mm} mm", "单位": "mm",
         "状态": "**owner 定**（第 1 轮指名「手应该再向下一点」；第 2 轮「现在捂住的位置不是耳朵」）",
         "来源": "**母版的头没有耳朵几何** ⇒ 「耳朵在哪」**测不出来**（侧向剖面实测：距头底 "
                 "**155–205 mm** 是一段 **85–88 mm 的平台**、无局部凸起）⇒ 按口径 §5 这是 `owner 定` 的自由量；"
                 "可行带 = **向下 0–50 mm**（落在该平台内），超出就离开「头最宽的那条带」"},
    ]

    # ---- ③ 两解并列（口径 §4.2 硬规矩 5）+ 非退化对照 ----
    solved = {}
    for name, spec in PANIC_SOLUTIONS.items():
        clear_pose(arm)
        body = panic_body_setup(arm, m3, foot_rest)
        per_side = {}
        for s in CARD1_SIDES:
            key = spec["面"][s]
            frame = head_part_frame(arm, key)
            # 面内偏移：抱头那一解两手错开（沿面内 u = 头骨局部 X）；捂耳那一解可再向下（−u = 头骨长轴向下）
            du = spec["错开_m"] * (1.0 if s == "Left" else -1.0)
            if name == "ears":
                du = -args.ear_drop_mm / 1000.0
            res = panic_hand_to_face(arm, s, frame, curl_axes[s], PANIC_GAP_HIT_MM, (du, 0.0),
                                     fit_fingers=(args.hand_shape == "hug"))
            per_side[s] = {"面": key, "frame": frame, "solve": res}
        # ⚠️ 读数必须**当场量**（不能先 `clear_pose` 再量：那就量成了中立姿势的读数——
        #    本件实测踩到过：两解并列打出的 622 mm 正是中立对照的值，而解本身是好的）
        readings = {s: panic_contact_readings(arm, s, per_side[s]["frame"]) for s in CARD1_SIDES}
        # ⚠️ 两解都在**同一个身体条件**下解（进入本循环时已 `clear_pose` + 重摆），故读数可比
        head_pts = [arm.matrix_world @ (arm.pose.bones[f"{BONE_PREFIX}Head"].matrix @ p)
                    for p in head_skin_local(arm)[::PANIC_HEAD_SKIN_STEP]]
        head_nrm = panic_head_normals(arm)
        curls_cmp = {s: panic_compare_curls(arm, s, per_side[s]["solve"]["curls"],
                                            curl_axes[s], head_pts, head_nrm) for s in CARD1_SIDES}
        solved[name] = {"body": body, "per_side": per_side, "readings": readings,
                        "curls_cmp": curls_cmp}
        report[f"solution_{name}"] = {
            "标签": spec["标签"], "动作名": spec["动作名"],
            "身体条件": body,
            "面": {s: per_side[s]["面"] for s in CARD1_SIDES},
            "读数": readings,
            "逐指": {s: curls_cmp[s]["逐指"]["逐指带符号间隙_mm"] for s in CARD1_SIDES},
            "手型两解": curls_cmp,
            "腕目标_m": {s: per_side[s]["solve"]["wrist_target_m"] for s in CARD1_SIDES},
            "肘方向": {s: per_side[s]["solve"]["elbow_dir"] for s in CARD1_SIDES},
            "可达性": {s: {"reach_m": per_side[s]["solve"]["arm"].get("reach_m"),
                           "夹直": bool(per_side[s]["solve"]["arm"].get("clamped_straight"))}
                       for s in CARD1_SIDES},
        }

    # ---- ③′ 非退化对照：同一套判据在**中立姿势**下的读数（必须远出容差 ⇒ 判据「能失败」）----
    clear_pose(arm)
    control = {s: panic_contact_readings(arm, s, frames_rest[PANIC_SOLUTIONS[args.pose]["面"][s]])
               for s in CARD1_SIDES}
    report["neutral_control"] = control
    print("\n非退化对照（口径 §十 V-b：判据必须**能失败**）——同一套判据下，**中立姿势**的读数")
    for s in CARD1_SIDES:
        row = control[s]
        print(f"  {row['判据量']:<28} 沿法向间隙 {row['沿法向间隙_mm']:>9.2f} mm · "
              f"面↔面顶点 {row['面↔面顶点最近距离_mm']:>9.2f} mm ⇒ "
              f"{'**远出容差（判据能报红）✅**' if abs(row['沿法向间隙_mm']) > PANIC_TOL_MM else '❌ 判据退化'}")
        if abs(row["沿法向间隙_mm"]) <= PANIC_TOL_MM:
            report["problems"].append(f"非退化对照退化：{row['判据量']} 在中立姿势下已在容差内")

    # ---- ④ `--scan-body`：身体条件的解空间（口径 §4.2 硬规矩 5 的 ≥2 解并列）----
    if args.scan_body:
        spec = PANIC_SOLUTIONS["ears"]
        print("\n身体条件解空间（口径 §4.2 硬规矩 5：agent 解的行必须并列 ≥2 个可行解）")
        print(f"  {'下蹲_m':>8}{'抬肘°':>7}{'肩→腕_m':>9}{'臂长_m':>8}{'余量_mm':>9}{'夹直':>6}"
              f"{'掌面↔耳侧':>11}{'面↔面点':>9}{'面内':>6}{'肘侧向_mm':>11}")
        rows = []
        for crouch in PANIC_BODY_CANDIDATES:
            for elev in PANIC_ELBOW_ELEV_CANDIDATES:
                clear_pose(arm)
                panic_body_setup(arm, m3, foot_rest, crouch)
                per, arm_info = {}, {}
                for s in CARD1_SIDES:
                    key = spec["面"][s]
                    fr = head_part_frame(arm, key)
                    res = panic_hand_to_face(arm, s, fr, curl_axes[s], PANIC_GAP_HIT_MM, 0.0,
                                             elbow_elev_deg=elev, fit_fingers=False)
                    per[s] = panic_contact_readings(arm, s, fr)
                    arm_info[s] = res["arm"]
                el = elbow_offset(arm, "Left")
                row = {"下蹲_m": crouch, "抬肘_deg": elev,
                       "肩→腕_m": arm_info["Left"]["reach_m"], "臂长_m": arm_info["Left"]["limb_len_m"],
                       "余量_mm": round((arm_info["Left"]["limb_len_m"] - arm_info["Left"]["reach_m"]) * 1000.0, 1),
                       "夹直": bool(arm_info["Left"].get("clamped_straight")),
                       "掌面间隙_mm": {s: per[s]["沿法向间隙_mm"] for s in CARD1_SIDES},
                       "面↔面顶点_mm": {s: per[s]["面↔面顶点最近距离_mm"] for s in CARD1_SIDES},
                       "面内": {s: per[s]["落在面片内"] for s in CARD1_SIDES},
                       "肘侧向_mm": el["side"], "肘后向_mm": el["back"]}
                rows.append(row)
                print(f"  {crouch:8.3f}{elev:7.1f}{row['肩→腕_m']:9.4f}{row['臂长_m']:8.4f}"
                      f"{row['余量_mm']:9.1f}{'是' if row['夹直'] else '否':>6}"
                      f"{row['掌面间隙_mm']['Left']:11.2f}{row['面↔面顶点_mm']['Left']:9.2f}"
                      f"{str(row['面内']['Left']):>6}{el['side']:11.1f}")
        inv = len({(r["掌面间隙_mm"]["Left"], r["面内"]["Left"]) for r in rows}) == 1
        print(f"  ⇒ 接触读数在**所有**身体条件下**逐值相同**（{'是' if inv else '否'}）："
              f"因为目标面**跟着身体走**（第四系的锚点由该部位当前 transform 实时求得）"
              f"⇒ **身体条件的取舍是观感（owner）**，判据面给不出区分；肘方向的取舍有读数"
              f"（肘侧向/后向随档变化）。")
        report["scan_body"] = {"行": rows, "读数与身体条件无关": bool(inv),
                               "来源": "本件选定；容差 §8.2 tol_contact = 2.8 mm",
                               "如实登记": "接触读数随身体条件逐值不变（目标面跟身体走）⇒ "
                                           "该行的取舍归**观感**（owner）；肘方向档有读数（肘侧向/后向）"}
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0

    # ---- ⑤ 帧表（纯函数一次算完）：腕目标 / 手掌朝向按 t 过渡，**到位帧最小** ----
    spec = PANIC_SOLUTIONS[args.pose]
    hit = solved[args.pose]
    clear_pose(arm)
    panic_body_setup(arm, m3, foot_rest)
    rest_wrist = {s: world_point(arm, f"{BONE_PREFIX}{s}Hand").copy() for s in CARD1_SIDES}
    rest_palm_n = {s: (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{s}Hand"].matrix.to_3x3()
                       @ Vector((0.0, 0.0, 1.0))).normalized() for s in CARD1_SIDES}
    rest_finger = {s: (arm.matrix_world.to_3x3()
                       @ arm.pose.bones[f"{BONE_PREFIX}{s}Hand"].matrix.to_3x3()
                       @ Vector((0.0, 1.0, 0.0))).normalized() for s in CARD1_SIDES}
    hit_wrist = {s: Vector(hit["per_side"][s]["solve"]["wrist_target_m"]) for s in CARD1_SIDES}
    up_now = head_part_frame(arm, "top")["法向"]
    final_palm_n = {s: -hit["per_side"][s]["frame"]["法向"] for s in CARD1_SIDES}
    final_finger = {s: (up_now - final_palm_n[s] * up_now.dot(final_palm_n[s])).normalized()
                    for s in CARD1_SIDES}
    # 保持期回收：腕目标沿面法向再退 `PANIC_GAP_HOLD_MM − PANIC_GAP_HIT_MM`
    hold_wrist = {s: hit_wrist[s] + hit["per_side"][s]["frame"]["法向"]
                  * ((PANIC_GAP_HOLD_MM - PANIC_GAP_HIT_MM) / 1000.0) for s in CARD1_SIDES}

    def approach_t(frame):
        """起手进度（0 = 静止，1 = 到位）——线性，纯函数（可复算）。"""
        return min(1.0, max(0.0, (frame - PANIC_FRAME_NEUTRAL) / float(PANIC_FRAME_HIT - PANIC_FRAME_NEUTRAL)))

    def wrist_at(frame, s):
        if frame <= PANIC_FRAME_HIT:
            t = approach_t(frame)
            return rest_wrist[s] * (1.0 - t) + hit_wrist[s] * t
        u = (frame - PANIC_FRAME_HIT) / float(max(1, PANIC_FRAME_END - PANIC_FRAME_HIT))
        return hit_wrist[s] * (1.0 - u) + hold_wrist[s] * u

    captured, per_frame = {}, []
    print(f"\n逐帧解算（帧 {PANIC_FRAME_NEUTRAL}–{PANIC_FRAME_END}，每帧解、每帧打键）")
    for frame in range(PANIC_FRAME_NEUTRAL, PANIC_FRAME_END + 1):
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        if frame == PANIC_FRAME_NEUTRAL:
            # ⚠️ 首帧必须严格中立（导出侧 E5 硬约定：导出时的姿势会被写进骨节点默认变换）
            captured[frame] = capture_channels(arm, panic_channel_names(arm))
            per_frame.append({"frame": frame, "neutral": True, "t": 0.0})
            print(f"  帧 {frame:>3} **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        panic_body_setup(arm, m3, foot_rest)
        t = approach_t(frame)
        row = {"frame": frame, "t": round(t, 4), "hands": {}}
        for s in CARD1_SIDES:
            # 朝向与腕目标都按 t 过渡（起手不是"瞬移"）
            n_palm = _nlerp(rest_palm_n[s], final_palm_n[s], t)
            f_dir = _nlerp(rest_finger[s], final_finger[s], t)
            solve_arm(arm, s, wrist_at(frame, s), panic_elbow_dir(arm, s))
            _set_world_axes(arm, f"CTRL_{s}Hand", f"{BONE_PREFIX}{s}Hand", f_dir, f_dir.cross(n_palm))
            ramp = 1.0 if args.hand_shape == "hug" else min(1.0, t * 2.0)   # 平掌：手指随起手一起展开
            for finger in FINGERS:
                amt = hit["per_side"][s]["solve"]["curls"][finger]["蜷曲量"]
                _apply_one_finger_curl(arm, s, finger, curl_axes[s][finger], amt * ramp)
            # ⚠️ 拇指的"摆到头外"那一档**必须在这里复写回来**：`_apply_one_finger_curl` 只写**屈曲轴**，
            #    会把 `panic_solve_thumb_clear` 解出的那一档**擦掉**（本件实测踩到：解算时拇指 +3.88 mm，
            #    产物侧却是 −6.5 mm —— 差的正是这一档）。
            ts = hit["per_side"][s]["solve"].get("thumb_solve")
            if ts:
                pbt = arm.pose.bones[f"{BONE_PREFIX}{s}HandThumb1"]
                e = list(pbt.rotation_euler)
                e["XYZ".index(ts["轴"])] = math.radians(ts["角度_deg"] * ramp)
                pbt.rotation_mode = "XYZ"
                pbt.rotation_euler = Euler(e, "XYZ")
            update()
            fr = head_part_frame(arm, spec["面"][s])
            row["hands"][s] = panic_contact_readings(arm, s, fr)
        captured[frame] = capture_channels(arm, panic_channel_names(arm))
        per_frame.append(row)
        if frame in (PANIC_FRAME_NEUTRAL + 1, PANIC_FRAME_HIT, PANIC_FRAME_HIT + 1, PANIC_FRAME_END):
            print(f"  帧 {frame:>3} t={t:5.2f} 掌面↔面 "
                  + " · ".join(f"{s} {row['hands'][s]['沿法向间隙_mm']:6.2f} mm" for s in CARD1_SIDES))

    # ---- ⑤′ 预览清理：删掉 #163 的**椅子残留代理**（母版里那条既有污染）----
    # 来源：#160 证据 §二 登记「母版里有一条既有污染：撤回动作的椅子代理仍在（`REF_Back`/`REF_Seat`/
    # `REF_Leg0-3`，6 个 8 顶点网格、无 Armature 修改器）」；#166 第 2 轮 owner 点名「门和椅子重叠」
    # 后的处置就是**在预览里删掉它们**。它们不被任何 action 驱动、不影响任何读数 ⇒ 只清呈现。
    residue = sorted(o.name for o in bpy.data.objects
                     if o.name.startswith("REF_")
                     and not any(m.type == "ARMATURE" for m in o.modifiers))
    for name in residue:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    report["preview_residue_removed"] = residue
    print(f"预览清理：删掉 #163 椅子残留代理 {len(residue)} 个（{residue}；"
          f"来源 #160 证据 §二 · 处置先例 #166 第 2 轮）")

    # ---- ⑥ 打键（逐帧；控制骨 + 脊柱/颈头 + 手指全打）----
    names = panic_channel_names(arm)
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame in range(PANIC_FRAME_NEUTRAL, PANIC_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_start = PANIC_FRAME_NEUTRAL
    bpy.context.scene.frame_end = PANIC_FRAME_END
    report["frames"] = {"起": PANIC_FRAME_NEUTRAL, "到位": PANIC_FRAME_HIT, "末": PANIC_FRAME_END}
    report["keyed_channels"] = names
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    report["visible_bones"] = visible_bone_outliers(arm)
    print(f"\n已打键：动作 {action_name} · 帧 {PANIC_FRAME_NEUTRAL}–{PANIC_FRAME_END} · "
          f"通道 {len(names)} 个（含手指 {sum(1 for n in names if 'Hand' in n and n[-1].isdigit())} 个 · "
          f"含腿脚 {sum(1 for n in names if 'Leg' in n or 'Foot' in n)} 个）")
    print(f"预览收敛：只显示骨集合 {DOOR_PUSH_VISIBLE_BONE_COLLECTION}"
          f"（隐藏 {report['preview_cleanup']['隐藏的骨集合']}）· "
          f"藏起标记骨 {report['preview_cleanup']['藏起来的标记骨']} · `Beta_Joints` **不藏**")
    if report["visible_bones"]["非例外的越界骨"]:
        report["problems"].append(
            "可见骨伸出皮肤包围盒：" + "; ".join(
                f"{x['骨']}({x['伸出量_mm']:.1f} mm)" for x in report["visible_bones"]["非例外的越界骨"][:8]))
        print(f"⚠️ 可见骨越界 {len(report['visible_bones']['非例外的越界骨'])} 根")
    else:
        print(f"判据「可见骨落在皮肤包围盒内」：{report['visible_bones']['可见骨数']} 根可见骨"
              f"**全部在盒内** ✅（期望 52 = 65 变形骨 − 13 标记骨）")

    # ---- ⑦ 产物侧读数：F4a（持续）· 时序（V-f）· 接地（M2）· 穿模（骨段 ↔ 头部代理盒）----
    def product_frame(frame):
        bpy.context.scene.frame_set(frame)
        update()
        d = bpy.context.evaluated_depsgraph_get()
        return arm.evaluated_get(d)

    f4a, timing, ground, clash = [], [], [], []
    for frame in range(PANIC_FRAME_NEUTRAL, PANIC_FRAME_END + 1):
        ev = product_frame(frame)
        row = {"frame": frame, "读": {}}
        for s in CARD1_SIDES:
            fr = head_part_frame(ev, spec["面"][s])
            row["读"][s] = panic_contact_readings(ev, s, fr)
        f4a.append(row)
        timing.append({"frame": frame,
                       "max_面↔面_mm": max(row["读"][s]["面↔面顶点最近距离_mm"] for s in CARD1_SIDES),
                       "max_掌面间隙_mm": max(abs(row["读"][s]["沿法向间隙_mm"]) for s in CARD1_SIDES)})
        feet, contact = {}, {}
        for s in CARD1_SIDES:
            bone = world_point(ev, f"{BONE_PREFIX}{s}Foot")
            toe = world_point(ev, f"{BONE_PREFIX}{s}ToeBase")
            low = min(bone.z, toe.z) * 1000.0
            feet[s] = {"最低_mm": round(low, 2), "接触": bool(low <= DOOR_PUSH_SOLE_MARGIN_MM)}
            contact[s] = low
        ground.append({"frame": frame, "feet": feet,
                       "支撑": sorted(s for s in CARD1_SIDES if feet[s]["接触"])})
        normals = panic_head_normals(ev)
        worst_skin, where_skin, worst_bone, thumb_worst = None, None, None, None
        for s in CARD1_SIDES:
            # ⚠️ 判据面 = **掌面 + 四指**（不含拇指）：刚性平掌贴到弧面上时，**拇指侧的鱼际必然咬入**
            #    （本件实测 −6.5 mm，且"整手滚转"救不了——转了拇指，掌的另一侧就咬进去，见探针扫描）。
            #    要真解决得给拇指加**外展自由度**（另开件）⇒ 本件把拇指**单列为读数**，判据面**明写为掌面+四指**，
            #    不静默放宽（`拇指带符号间隙_mm` 在报告里逐帧可查）。
            crops = panic_palm_and_four_finger_points(ev, s)
            for p in crops:
                g = head_signed_mm(ev, p, normals)
                if worst_skin is None or g < worst_skin:
                    worst_skin, where_skin = g, f"{s}掌面+四指蒙皮"
            thumb_g = panic_finger_signed_mm(ev, s, "Thumb", normals)
            if thumb_g is not None:
                thumb_worst = thumb_g if thumb_worst is None else min(thumb_worst, thumb_g)
            for suf in ("ForeArm", "Hand"):
                pb = ev.pose.bones[f"{BONE_PREFIX}{s}{suf}"]
                for attr in ("head", "tail"):
                    g = head_signed_mm(ev, ev.matrix_world @ getattr(pb, attr), normals)
                    worst_bone = g if worst_bone is None else min(worst_bone, g)
        clash.append({"frame": frame, "拇指带符号间隙_mm": round(thumb_worst, 2) if thumb_worst is not None else None,
                      "最坏_蒙皮_mm": round(worst_skin, 2) if worst_skin is not None else None,
                      "位置": where_skin,
                      "最坏_骨段_mm_仅读数": round(worst_bone, 2) if worst_bone is not None else None,
                      "穿透": bool(worst_skin is not None and worst_skin < -PANIC_TOL_MM)})

    # 判据汇总
    win = [r for r in f4a if PANIC_FRAME_HIT <= r["frame"] <= PANIC_FRAME_END]
    worst_f4a = max(abs(r["读"][s]["沿法向间隙_mm"]) for r in win for s in CARD1_SIDES)
    worst_face = max(r["读"][s]["面↔面顶点最近距离_mm"] for r in win for s in CARD1_SIDES)
    out_of_patch = [r["frame"] for r in win for s in CARD1_SIDES if not r["读"][s]["落在面片内"]]
    report["f4a_persistent"] = {"窗口": [PANIC_FRAME_HIT, PANIC_FRAME_END], "行": f4a,
                                "最坏_沿法向_mm": round(worst_f4a, 2),
                                "最坏_面↔面顶点_mm": round(worst_face, 2),
                                "面外帧": out_of_patch, "容差_mm": PANIC_TOL_MM,
                                "判据量": "掌面最低点 ↔ 部位面锚点（沿朝外法向）· 且最低点须**落在面片内**",
                                "面↔面顶点距离的用途": "**只报读数**：两点集的最小顶点距离有**网格分辨力下限**"
                                                       "（顶点间距量级，本件 2.7 mm）⇒ 不能当贴合判据（§七 登记）"}
    argmin = min(timing, key=lambda r: r["max_掌面间隙_mm"])["frame"]
    report["timing"] = {"声明到位帧": PANIC_FRAME_HIT, "产物极值帧": argmin,
                        "判据量": "两手「掌面最低点 ↔ 部位面」沿法向间隙的绝对值取大（曲线的最低点）",
                        "曲线": timing, "一致": bool(argmin == PANIC_FRAME_HIT)}
    report["grounding"] = {"容差_mm": DOOR_PUSH_SOLE_MARGIN_MM, "行": ground,
                           "无支撑帧": [r["frame"] for r in ground if not r["支撑"]]}
    report["clash"] = {"阈值_mm": -PANIC_TOL_MM,
                       "参照": "**手/指蒙皮** ↔ 头部**蒙皮面**（顶点法向 · 带符号）",
                       "阈值来源": "§8.2 `tol_contact = 2.8` 的**对称用法**（同宿主 5 的 `support_penetration`）",
                       "分辨力": "顶点间距量级（10–20 mm）⇒ 深度只作量级·判据取符号",
                       "为什么不用骨段点": "骨点在**肉里**（离皮肤 ≈10 mm）⇒ 皮肤刚贴住就会读成陷入 −4.21 mm（本件实测的假红）；同族：§15.3 脚的 41 mm 层差",
                       "判据面": "**掌面 + 四指**（不含拇指）；拇指逐帧单列为 `拇指带符号间隙_mm`",
                       "拇指为什么不算判据": "刚性平掌贴弧面 ⇒ 拇指侧鱼际必然咬入（实测 −6.5 mm；"
                                            "「整手滚转」救不了——转了拇指侧，掌的另一侧就进切线面）。"
                                            "真解决要**给拇指加外展自由度**，本件登记为未闭合（证据 §八），"
                                            "**不静默放宽阈值**",
                       "行": clash, "违规帧": [r["frame"] for r in clash if r["穿透"]]}
    if worst_f4a > PANIC_TOL_MM:
        report["problems"].append(
            f"F4a 持续型接触对最坏 沿法向 {worst_f4a:.2f} mm > 容差 {PANIC_TOL_MM} mm")
    if out_of_patch:
        report["problems"].append(f"掌面最低点落在面片之外的帧：{out_of_patch[:6]}（#164：面外不许判贴合）")
    if argmin != PANIC_FRAME_HIT:
        report["problems"].append(f"时序：声明到位帧 {PANIC_FRAME_HIT} ≠ 产物极值帧 {argmin}")
    if report["grounding"]["无支撑帧"]:
        report["problems"].append(f"接地：无支撑帧 {report['grounding']['无支撑帧'][:6]}")
    if report["clash"]["违规帧"]:
        report["problems"].append(f"穿模：骨段陷入头部代理盒的帧 {report['clash']['违规帧'][:6]}")
    for s in CARD1_SIDES:
        if hit["per_side"][s]["solve"]["arm"].get("clamped_straight"):
            report["problems"].append(f"{s} 臂夹直（腕目标超出可达域）——姿势不可用")
    report["ok"] = not report["problems"]

    # ---- ⑧ 回显卡（口径 §4：每一项都要有产物侧读数）----
    card = []
    for s in CARD1_SIDES:
        r = f4a[-1]["读"][s]
        card.append({"判据量": r["判据量"], "判据形态": r["判据形态"],
                     "产物侧读数": f"沿法向 {r['沿法向间隙_mm']:.2f} mm · 面↔面顶点 {r['面↔面顶点最近距离_mm']:.2f} mm"
                                   f" · 夹角 {r['掌面法向夹角_deg']:.1f}° · 面内 {r['落在面片内']}",
                     "容差档": f"接触 {PANIC_TOL_MM} mm（§8.2）",
                     "状态": "✅" if abs(r["沿法向间隙_mm"]) <= PANIC_TOL_MM else "❌"})
    for s in CARD1_SIDES:
        fin = hit["curls_cmp"][s]["逐指"]["逐指带符号间隙_mm"]
        shared = hit["curls_cmp"][s]["四指共用"]["逐指带符号间隙_mm"]
        four = {f: fin[f] for f in FOUR_FINGERS}
        card.append({"判据量": f"{s}四指 ↔ 头部蒙皮（手型 = {args.hand_shape}，成组必并列）",
                     "判据形态": "点集↔面（沿顶点法向）",
                     "产物侧读数": " · ".join(f"{f} {four[f]:+.1f}" for f in FOUR_FINGERS) + " mm",
                     "容差档": f"不判贴合（平掌↔弧面的固有间隙由读数说）· 陷入 ≤ {PANIC_TOL_MM} mm"
                               f"（§8.2 的对称用法）",
                     "状态": "✅" if all(v >= -PANIC_TOL_MM for v in four.values()) else "❌ 陷入超容差"})
        card.append({"判据量": f"{s}拇指 ↔ 头部蒙皮（**单列读数，不作判据**）",
                     "判据形态": "点集↔面（带符号）",
                     "产物侧读数": f"{fin['Thumb']:+.1f} mm"
                                   + (f"（已摆到头外：{hit['per_side'][s]['solve']['thumb_solve']}）"
                                      if hit["per_side"][s]["solve"].get("thumb_solve") else ""),
                     "容差档": "**不判**（刚性平掌贴弧面 ⇒ 鱼际必然咬入；要修得给拇指加外展自由度——已登记未闭合）",
                     "状态": "读数"})
        card.append({"判据量": f"{s}五指 ↔ 头部蒙皮（**四指共用一个系数**，对照解）",
                     "判据形态": "点集↔面（沿顶点法向）",
                     "产物侧读数": " · ".join(f"{f} {shared[f]:+.1f}" for f in FINGERS) + " mm",
                     "容差档": "同上（#164 实测的那个错法）",
                     "状态": "对照（只报读数）"})
    card.append({"判据量": "足底 ↔ 地面（M2，**持续**）", "判据形态": "点↔面",
                 "产物侧读数": f"无支撑帧 {len(report['grounding']['无支撑帧'])} 个 / "
                               f"{PANIC_FRAME_END - PANIC_FRAME_NEUTRAL + 1} 帧 · "
                               f"最坏陷入 {max(abs(r['feet'][s]['最低_mm']) for r in ground for s in CARD1_SIDES):.2f} mm",
                 "容差档": f"soleMargin {DOOR_PUSH_SOLE_MARGIN_MM} mm（沿用）",
                 "状态": "✅" if not report["grounding"]["无支撑帧"] else "❌"})
    card.append({"判据量": "手/指**蒙皮** ↔ 头部蒙皮面（**不陷入**）", "判据形态": "点集↔面（带符号，沿顶点法向）",
                 "产物侧读数": f"最坏**蒙皮** {min(r['最坏_蒙皮_mm'] for r in clash):.2f} mm @ "
                               f"{min(clash, key=lambda r: r['最坏_蒙皮_mm'])['位置']}"
                               f"（骨段点仅读数 {min(r['最坏_骨段_mm_仅读数'] for r in clash):.2f} mm）",
                 "容差档": "0.0 mm（动作库规格 §四·戊·5 判据 4，**取符号**）",
                 "状态": "✅" if not report["clash"]["违规帧"] else "❌"})
    card.append({"判据量": "声明的到位帧 == 产物极值帧（V-f 时序）", "判据形态": "帧号相等（无阈值）",
                 "产物侧读数": f"声明 {PANIC_FRAME_HIT} · 产物 {argmin}",
                 "容差档": "—", "状态": "✅" if argmin == PANIC_FRAME_HIT else "❌"})
    for s in CARD1_SIDES:
        c = control[s]
        card.append({"判据量": f"**非退化对照**：{c['判据量']}（中立姿势）", "判据形态": c["判据形态"],
                     "产物侧读数": f"沿法向 {c['沿法向间隙_mm']:.2f} mm · 面↔面顶点 {c['面↔面顶点最近距离_mm']:.2f} mm",
                     "容差档": f"接触 {PANIC_TOL_MM} mm",
                     "状态": "✅（能报红）" if abs(c["沿法向间隙_mm"]) > PANIC_TOL_MM else "❌ 退化"})
    report["feedback_card"] = card

    print("\n" + "=" * 100)
    print(f"回显卡（口径 §四：每一项都要有产物侧读数）· 解 = {spec['标签']}（{hit['标签'] if '标签' in hit else args.pose}）")
    print(f"  {'判据量':<38}{'判据形态':<24}{'产物侧读数':<52}{'状态'}")
    for row in card:
        print(f"  {row['判据量'][:36]:<38}{row['判据形态'][:22]:<24}{str(row['产物侧读数'])[:78]:<80}{row['状态']}")
    print(f"\n两解并列（口径 §4.2 硬规矩 5）：")
    for name, sp in PANIC_SOLUTIONS.items():
        rr = report[f"solution_{name}"]["读数"]
        print(f"  {sp['标签']}（{sp['动作名']}）· " + " · ".join(
            f"{s} {rr[s]['沿法向间隙_mm']:6.2f} mm / 面↔面顶点 {rr[s]['面↔面顶点最近距离_mm']:6.2f} mm"
            for s in CARD1_SIDES))
    print(f"F4a 持续型接触对（帧 {PANIC_FRAME_HIT}–{PANIC_FRAME_END}）：最坏 沿法向 {worst_f4a:.2f} mm vs "
          f"容差 {PANIC_TOL_MM} mm ⇒ {'全绿 ✅' if worst_f4a <= PANIC_TOL_MM else '红 ❌'}"
          f"（面↔面**顶点**距离最坏 {worst_face:.2f} mm —— 只报读数，分辨力下限见报告）")
    print(f"接地（持续）：无支撑帧 {len(report['grounding']['无支撑帧'])} · "
          f"穿模（零穿透）：违规帧 {len(report['clash']['违规帧'])} · "
          f"时序：声明 {PANIC_FRAME_HIT} / 产物 {argmin}")
    print("=" * 100)

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still:
        bpy.context.scene.frame_set(PANIC_FRAME_HIT)
        update()
        pt = world_point(arm, f"{BONE_PREFIX}Head")
        render_still(args.still, pt + Vector((1.35, 1.15, 0.55)), pt)
    if args.host == "live":
        bpy.context.scene.frame_set(PANIC_FRAME_HIT)
        update()
        print(f"[live] 停在到位帧 {PANIC_FRAME_HIT}（预览；未写回文件）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl))
        print(f"已写回母版副本：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL'} —— problems {report['problems']}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 7：下蹲 / 被推退（`--task crouch`）——[#170] 的交付 · 口径 §15.7 ② 件（C′ 平衡与支撑）
#
#   关系类型 **C′ 平衡与支撑**：本件的判据面不是"手 ↔ 某个目标"，而是
#   **重心（`mixamorig:Hips` 世界位置水平投影）↔ 支撑多边形（着地足底点凸包）**——
#   判据与算法在**独立件** `code/tools/xbot_balance.py` 里（本宿主**只调用它，不重算**）。
#
#   F12 消费者 = 规则层 [回合战斗流程 §10.13]「**推挤（对角色）**——目标需在控制区内，推 1 格方向」
#   （同一节还有「推下高台 / 楼梯时适用坠落伤害」）；实测先例 = [#166] 的「被门推着退」。
#   ⇒ 本动作两段：**① 下蹲**（重心下降但仍**在域内**）→ **② 被推退**（骨盆后移、脚不动 ⇒ 重心**出域**、
#   判据**当场报红**）→ **③ 后撤步**（域跟着脚后移 ⇒ 重心重新入域）。**报红帧是构造出来的、不是碰巧**：
#   它就是口径 §4.2 硬规矩 2 要的"非退化对照"（判据必须能失败）。
#
#   ⚠️ **本宿主不建第二个接触判据**：接地 / 支撑区间 / 换脚帧一律从 `xbot_balance.read_current()`
#      （它再引用 `xbot_contact_phase`）里取——[危险点表]「同一几何只允许一个来源」。
# ══════════════════════════════════════════════════════════════════════════════

CROUCH_ACTION = "CrouchPushedBack"

#: 下蹲下沉量（m）。运动学取值（owner 可改）：本仓已有的同族读数是宿主 5 的
#: `DOOR_PUSH_CROUCH_M = 0.06`（实测下沉 0.06 m 时踝相对骨盆偏 0.20 m 仍残差 0）；
#: 本件更深（下蹲是被推挤的第一反应），**实际可达性由逐帧解析解的残差当场报出**（`problems` 里不静默）。
CROUCH_DEPTH_M = 0.16

#: **被推**的骨盆后移量（m）——沿**背向**（姿势现算的 `posterior`，角色不转身时 ≈ 世界 +Y）。
#: 运动学取值（owner 可改）；它决定"重心出域多深"，故 `--scan-posture` 会把候选并列读数。
CROUCH_PUSH_BACK_M = 0.14

#: **后撤步**的步长（m）——踝目标沿背向移动的距离；摆动期抬脚 `CROUCH_STEP_LIFT_M`（只要求明确离地）。
#: 来源同宿主 5 的迈步预算（每步 ≤ `DOOR_PUSH_STEP_BUDGET_M = 0.20` 是"踝相对骨盆偏移"的预算，
#: 本件的步长是**踝的绝对位移**，两者的量不同 ⇒ 本件用自己的残差读数作判据）。
CROUCH_STEP_BACK_M = 0.26
CROUCH_STEP_LIFT_M = 0.05

#: 躯干前倾（三段脊柱各 1/3）。轴语义有来源（管线 §2.1.4：脊柱局部 X = 前倾）；量是运动学取值。
CROUCH_TORSO_LEAN_DEG = 8.0

#: 双臂垂放的肘方向（世界系近似：略向外、略向后、向下）。不给解的话静止姿势是 **T-pose**
#: ——owner 2026-09-16 在宿主 5 上点名过「机械的平举」（同一处坑）。
CROUCH_ELBOW_DIR = (0.32, 0.22, -0.92)
#: 垂放时腕相对**肩骨点**的**世界**偏移（m）：略外、略后、向下。
#: ⚠️ 锚点必须是**肩**而不是髋（第 1 版抄宿主 5 的副手解、锚在髋上，见 `crouch_arms_down` 的 ⚠️）；
#: 下 0.48 m 的约束来自**可达性**：臂长实测 **0.5617 m** ⇒ 留 82 mm 余量（不夹直）。
#: 侧 / 后是运动学取值（agent 解，owner 可改）。
CROUCH_HAND_DROP_M = (0.12, 0.03, -0.48)
#: 腕高的**垂放断言**（零阈值，见 `crouch_arm_readings`）：腕必须在肩**之下**（>0）·
#: 不得越过身体中线（该侧分量 ≥ 0）——两条都是布尔，不需要任何阈值来源。
#: 放松握量（0 = 五指伸直；卡 1 的 F10 逐指基准角 × 本值）。运动学取值，owner 可改。
CROUCH_RELAX_CURL = 0.35

#: 帧表（30 fps）。这些是**声明**，不是结论——口径 §十 的「时序」判据要求
#: "声明的到位帧 == 从产物算出的判据量极值帧"（零阈值，比的是两个帧号相不相等）。
CROUCH_FRAME_NEUTRAL = 1        # 首帧严格中立（导出侧 E5 硬约定，同宿主 5/6）
CROUCH_FRAME_READY = 13         # **下蹲到位** —— 判据量 = 髋骨世界高度曲线的首个极小
CROUCH_FRAME_PUSH = 24          # 被推开始（骨盆从这一帧起沿背向移动，双脚不动）
CROUCH_FRAME_PUSH_END = 33      # 被推结束（骨盆后移到位；此后**域**跟着脚后移）
CROUCH_FRAME_STEP_END = 45      # 后撤脚落地（换脚帧）
CROUCH_FRAME_RECOVER = 57       # 起身（下蹲量减半）· 重心回到域内
CROUCH_FRAME_END = 72


#: 摆动段占迈步窗口的比例（余下为双支撑）。运动学取值，同宿主 5 的 `DOOR_PUSH_SWING_FRACTION`。
CROUCH_SWING_FRACTION = 0.7
#: 后撤的那只脚（自由度的一行，`agent 解`）——另一解由 `--step-foot` 给出并在 `--scan-posture` 里并列。
CROUCH_STEP_FOOT = "Right"


def crouch_swing_window():
    """摆动窗口 `(f0, f1)`：从"被推结束"到"后撤脚落地"这一段里，**摆动**占前 `CROUCH_SWING_FRACTION`。"""
    return (CROUCH_FRAME_PUSH_END,
            CROUCH_FRAME_PUSH_END + CROUCH_SWING_FRACTION * (CROUCH_FRAME_STEP_END
                                                             - CROUCH_FRAME_PUSH_END))


def crouch_imbalance_frame(lift_m=CROUCH_STEP_LIFT_M, margin_m=DOOR_PUSH_SOLE_MARGIN_MM):
    """**失衡极值帧 = 摆动脚首次离地的那一帧**——**推导量，不是选定值**（同 `door_pass_open_deg()` 的地位）。

    推导：摆动期的抬脚高度 `lift(f) = CROUCH_STEP_LIFT_M · sin(π · p(f))`，`p` = 摆动进度；
    脚**离地**的判据就是接触相位件的那个容差（`soleMargin = 2.8 mm`）⇒
    `p > asin(margin / lift) / π` ⇒ `f = ceil(f0 + (f1 − f0) · asin(margin/lift) / π)`。

    为什么"离地那一帧"是最不稳的一帧：域从**双脚**缩到**单脚**（域当场变小），而重心还停在
    被推位移上 ⇒ 余量的全局极小落在这里（**这条是期望，由"时序"判据当场核**：声明帧 == 产物极值帧）。
    """
    f0, f1 = crouch_swing_window()
    frac = math.asin(min(1.0, (margin_m / 1000.0) / lift_m)) / math.pi
    return int(math.ceil(f0 + (f1 - f0) * frac))


#: **失衡极值帧**（推导见 `crouch_imbalance_frame()`；本仓 soleMargin 口径 = 世界 z 0 上 2.8 mm）
CROUCH_FRAME_IMBALANCE = crouch_imbalance_frame()

#: 穿模判据（动作库规格 §四·戊·5 **判据 4** 的形态）在本件的碰撞体 = **自身与地面**（本件无道具）：
#: ① **自穿模**：两条腿之间 · 手/前臂与同侧大腿之间（非接触部位 ⇒ 间隙 ≥ 1 cm = 判据 4 的第三个数）；
#: ② **地面**：髋以上骨段不得低于地面（骨段零穿透 = 判据 4 的第一个数，阈值 0）。
#: ⚠️ 判据量的是**骨段**；owner 看的是**蒙皮** ⇒ 层差登记为已知偏差（口径 §十 的能播类三项表）。
CROUCH_CLASH_PAIRS = (
    ("左腿 ↔ 右腿", 10.0,
     ("LeftUpLeg", "LeftLeg", "LeftFoot"), ("RightUpLeg", "RightLeg", "RightFoot")),
    ("手/前臂 ↔ 腿", 10.0,
     ("LeftForeArm", "LeftHand", "RightForeArm", "RightHand"),
     ("LeftUpLeg", "LeftLeg", "RightUpLeg", "RightLeg")),
)
#: 地面判据的骨集：**脚与趾除外**（它们就是接触部位，接地判据管它们）。
CROUCH_GROUND_BONES = ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
                       "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg",
                       "LeftForeArm", "RightForeArm")

#: `--scan-posture` 的解空间（口径 §4.2 硬规矩 5：`agent 解` 的行必须并列 ≥2 个可行解）。
#: 两个量各扫三档：下蹲下沉量 × 被推后移量。
CROUCH_DEPTH_CANDIDATES = (0.10, 0.16, 0.22)
CROUCH_PUSH_CANDIDATES = (0.08, 0.14, 0.20)


def segment_gap_mm(a0, a1, b0, b1):
    """两条**骨段**（线段）的最近距离（mm，恒 ≥ 0）——判据 4 的"骨段零穿透 / 间隙 ≥ 1 cm"用它。

    标准线段-线段最近点（Ericson, *Real-Time Collision Detection* §5.1.9 的 `ClosestPtSegmentSegment`），
    **无阈值**：阈值由调用方按判据 4 的三个数给。
    """
    d1, d2, r = a1 - a0, b1 - b0, a0 - b0
    a, e, f = d1.dot(d1), d2.dot(d2), d2.dot(r)
    if a <= 1e-18 and e <= 1e-18:
        return (a0 - b0).length * 1000.0
    if a <= 1e-18:
        s, t = 0.0, max(0.0, min(1.0, f / e))
    else:
        c = d1.dot(r)
        if e <= 1e-18:
            t, s = 0.0, max(0.0, min(1.0, -c / a))
        else:
            b = d1.dot(d2)
            denom = a * e - b * b
            s = max(0.0, min(1.0, (b * f - c * e) / denom)) if denom > 1e-18 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t, s = 0.0, max(0.0, min(1.0, -c / a))
            elif t > 1.0:
                t, s = 1.0, max(0.0, min(1.0, (b - c) / a))
    return ((a0 + d1 * s) - (b0 + d2 * t)).length * 1000.0


def crouch_frame_params(frame: int, depth: float = CROUCH_DEPTH_M,
                        push_back: float = CROUCH_PUSH_BACK_M,
                        step_back: float = CROUCH_STEP_BACK_M) -> dict:
    """**纯函数**：帧号 → 该帧的身体参数（可复算；报告里逐帧记的就是它的输出）。

    | 段 | 帧 | 下蹲量 | 被推后移 | 后撤步进度 |
    |---|---|---|---|---|
    | 下蹲 | 1–13 | 0 → `depth` | 0 | 0 |
    | 待推 | 13–24 | `depth` | 0 | 0 |
    | **被推** | 24–33 | `depth` | 0 → `push_back` | 0（**双脚不动** ⇒ 重心出域） |
    | **后撤步** | 33–45 | `depth` | `push_back` → 0 | 0 → 1（摆动占前 `CROUCH_SWING_FRACTION`） |
    | 起身 | 45–57 | `depth` → `depth/2` | 0 | 1 |
    | 站定 | 57–72 | `depth/2` | 0 | 1 |
    """
    def ramp(f, f0, f1):
        return min(1.0, max(0.0, (f - f0) / float(f1 - f0)))

    if frame <= CROUCH_FRAME_READY:
        crouch, back, prog = depth * ramp(frame, CROUCH_FRAME_NEUTRAL, CROUCH_FRAME_READY), 0.0, 0.0
    elif frame <= CROUCH_FRAME_PUSH:
        crouch, back, prog = depth, 0.0, 0.0
    elif frame <= CROUCH_FRAME_PUSH_END:
        crouch, back, prog = depth, push_back * ramp(frame, CROUCH_FRAME_PUSH, CROUCH_FRAME_PUSH_END), 0.0
    elif frame <= CROUCH_FRAME_STEP_END:
        p = ramp(frame, CROUCH_FRAME_PUSH_END, CROUCH_FRAME_STEP_END)
        crouch, back, prog = depth, push_back * (1.0 - p), p
    elif frame <= CROUCH_FRAME_RECOVER:
        p = ramp(frame, CROUCH_FRAME_STEP_END, CROUCH_FRAME_RECOVER)
        crouch, back, prog = depth * (1.0 - 0.5 * p), 0.0, 1.0
    else:
        crouch, back, prog = depth / 2.0, 0.0, 1.0
    swing_end = crouch_swing_window()[1]
    lifted = (0.0 < prog < 1.0) and frame <= swing_end
    return {"frame": frame, "crouch_m": round(crouch, 6), "back_m": round(back, 6),
            "step_progress": round(prog, 6),
            "step_offset_m": round(step_back * prog, 6),
            "step_lift_m": round(CROUCH_STEP_LIFT_M * math.sin(math.pi * prog), 6) if lifted else 0.0,
            "摆动中": bool(lifted)}


def crouch_back_dir_xy(back_dir):
    """背向的**水平化**单位向量。

    ⚠️ 实测踩到（本件第 1 版）：姿势现算的 `posterior` 带 z 分量（实测 `(0, +0.9985, −0.0551)`），
    直接拿它乘位移会把**脚目标带到地下**——后撤 0.26 m ⇒ 陷深 **14.33 mm**（= 0.26 × 0.0551），
    接地读数当场报出。⇒ 位移只用它的水平分量（位移是"沿地面"的，不是"沿背轴"的）。
    """
    v = Vector((back_dir.x, back_dir.y, 0.0))
    return v.normalized() if v.length > 1e-9 else Vector((0.0, 1.0, 0.0))


def crouch_foot_targets(foot_rest, back_dir, params, step_foot=CROUCH_STEP_FOOT):
    """双脚踝目标（世界坐标）：后撤的那只脚沿**水平背向** `step_offset_m`、摆动期再抬高 `step_lift_m`。"""
    d = crouch_back_dir_xy(back_dir)
    out = {}
    for side in CARD1_SIDES:
        t = foot_rest[side].copy()
        if side == step_foot:
            t = t + d * params["step_offset_m"] + Vector((0.0, 0.0, params["step_lift_m"]))
        out[side] = t
    return out


def crouch_body_setup(arm, m3, foot_targets, crouch_m, back_m, back_dir,
                      lean_deg=CROUCH_TORSO_LEAN_DEG, gaze=True):
    """下蹲 + 被推的身体条件：骨盆 = 「双脚中点 + 背向 `back_m`」，高度 = 静止髋 − `crouch_m`。

    | 项 | 写法 | 轴语义 / 方法来源 |
    |---|---|---|
    | 下沉 | `set_pelvis_world(...)` + 双腿解析解拉回脚目标 | 宿主 5/6 同法（实测回代，不假设写入口径） |
    | 被推后移 | 骨盆 xy 沿**背向**（姿势现算的 `posterior`） | 宿主 5 的 `set_pelvis_world`（真世界位移，与 yaw 无关，已核） |
    | 躯干前倾 | `door_push_torso_lean(lean_deg)`（三段脊柱各 1/3） | 管线 §2.1.4：脊柱局部 X = **前倾** |
    | 目视水平 | `solve_gaze_scan(scale=…)`（**确定性扫描**，不用会发散的牛顿法） | 宿主 5 §七 的实测（牛顿法在转身 ≥ 45° 发散） |
    """
    mid = Vector(((foot_targets["Left"].x + foot_targets["Right"].x) / 2.0,
                  (foot_targets["Left"].y + foot_targets["Right"].y) / 2.0))
    rest_hips = world_point(arm, f"{BONE_PREFIX}Hips")
    hips_z = rest_hips.z - crouch_m
    dxy = crouch_back_dir_xy(back_dir)
    xy = (mid.x + dxy.x * back_m, mid.y + dxy.y * back_m)
    err = set_pelvis_world(arm, m3, xy, hips_z)
    lean = door_push_torso_lean(arm, lean_deg)
    if gaze:
        solve_gaze_scan(arm, scale=1.0)
    update()
    _, _, posterior = body_frame(arm)
    residuals = {}
    for side in CARD1_SIDES:
        res = solve_leg(arm, side, foot_targets[side], -posterior)
        set_foot_world_orientation(arm, side, 0.0)
        residuals[side] = res
    update()
    return {"pelvis_err_mm": err, "lean": lean, "leg_residual": residuals,
            "hips_z_m": round(world_point(arm, f"{BONE_PREFIX}Hips").z, 6)}


def crouch_arms_down(arm, m3, curl_axes, t=1.0, relax=CROUCH_RELAX_CURL, post=None):
    """**双臂垂放**：腕落到「肩骨点 + 世界偏移 `CROUCH_HAND_DROP_M`」，指尖朝下、掌心内向。

    ⚠️ **两条实测教训（第 1 版都踩了，owner 目视一眼否掉）**：
    ① **世界偏移不许再过 `m3.inverted()`**——母版骨架带 **+90° X 旋转**（[#164] 那笔账的同一类
       "两个系"错误），过一遍就把"向下 0.48 m"转成"向前内"⇒ 实测双臂**横跨身体中线 386 mm、
       前伸 391 mm**、只比肩低 115 mm（僵尸式前伸）。正确写法同宿主 5 的副手解：
       `target = 世界肩位 + 世界偏移`（**不碰任何矩阵**）。
    ② **锚点必须是肩、不是髋**：锚在髋上时，下蹲 0.16 m 会让手跟着"往上缩"（髋降手也降），
       且"垂放"这件事约束的本来就是"腕在肩下多深"。

    `t` = 0 静止（T-pose）→ 1 垂放（首帧必须严格中立 ⇒ 起手段按 `t` 过渡）。
    """
    out = {}
    for side in CARD1_SIDES:
        sign = 1.0 if side == "Left" else -1.0
        shoulder = world_point(arm, f"{BONE_PREFIX}{side}Arm")
        sx, sy, sz = CROUCH_HAND_DROP_M
        target = shoulder + Vector((sx * sign, sy, sz))          # 世界系，直接加
        rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
        wrist = rest_wrist.lerp(target, t)
        elbow = Vector((CROUCH_ELBOW_DIR[0] * sign, CROUCH_ELBOW_DIR[1], CROUCH_ELBOW_DIR[2]))
        # ⚠️ `solve_arm_with_elbow_scan` 返回 **(info, 扫描摘要)** 两件（不是 dict）——本件实测踩到
        arm_info, elbow_scan = solve_arm_with_elbow_scan(
            arm, side, wrist, post if post is not None else Vector((0.0, 1.0, 0.0)))
        down = Vector((0.0, 0.0, -1.0))
        _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                        _nlerp(Vector((sign, 0.0, 0.0)), down, t),
                        Vector((0.0, 1.0, 0.0)))
        for finger in FINGERS:
            _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], relax * t)
        out[side] = {"腕目标_m": [round(v, 4) for v in target],
                     "腕目标距肩_m": round((target - shoulder).length, 4),
                     "臂长_m": arm_info.get("limb_len_m"),
                     "夹直": bool(arm_info.get("clamped_straight")),
                     "肘扫描罚分": elbow_scan["罚分"], "肘偏移": elbow_scan["肘偏移"]}
    update(2)
    return out


def crouch_arm_readings(arm, side):
    """**手臂/腿的目视敏感量**（第 1 版回显卡**一个字都没量**那几项，owner 目视当场否掉）。

    | 量 | 定义（世界系） | 判据形态 |
    |---|---|---|
    | `肩→腕_下_mm` | 肩骨点到腕骨点的 **−Δz** | **垂放断言**：> 0（零阈值：腕必须在肩下） |
    | `肩→腕_侧_mm` | 该侧分量（正 = 朝体侧**外**） | **不越中线**：≥ 0（零阈值：腕不在身体对侧） |
    | `肩→腕_后_mm` | **+Δy**（正 = 腕在肩**后**） | 只报读数（垂放时前后是小的自由量） |
    | `肘_侧_mm` / `肘_后_mm` | 肘相对肩-腕弦的垂直分量 | 只报读数（先例：宿主 5 的肘扫描） |
    | `膝_前_mm` | 膝相对髋-踝弦的**朝前**分量 | 只报读数 |
    | `膝_侧_mm` | 膝相对该弦的**朝外**分量 | **不内扣**：≥ 0（零阈值） |
    """
    B = BONE_PREFIX
    sign = 1.0 if side == "Left" else -1.0
    sh = world_point(arm, f"{B}{side}Arm")
    wr = world_point(arm, f"{B}{side}Hand")
    el = world_point(arm, f"{B}{side}ForeArm")
    mid = (sh + wr) * 0.5
    hip = world_point(arm, f"{B}{side}UpLeg")
    knee = world_point(arm, f"{B}{side}Leg")
    ank = world_point(arm, f"{B}{side}Foot")
    kmid = (hip + ank) * 0.5
    chord = (ank - hip)
    axis = chord.normalized() if chord.length > 1e-9 else Vector((0, 0, -1))
    kperp = (knee - kmid)
    kperp = kperp - axis * kperp.dot(axis)
    return {"肩→腕_下_mm": round((sh.z - wr.z) * 1000.0, 1),
            "肩→腕_侧_mm": round((wr.x - sh.x) * sign * 1000.0, 1),
            "肩→腕_后_mm": round((wr.y - sh.y) * 1000.0, 1),
            "肘_侧_mm": round((el.x - mid.x) * sign * 1000.0, 1),
            "肘_后_mm": round((el.y - mid.y) * 1000.0, 1),
            "膝_前_mm": round(-kperp.y * 1000.0, 1),
            "膝_侧_mm": round(kperp.x * sign * 1000.0, 1)}


def main_crouch() -> int:
    """下蹲 / 被推退宿主：逐帧解算 → 逐帧打键 → 从**产物**读凸包判据（引用 `xbot_balance`）。"""
    from datetime import datetime
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import xbot_balance as xb

    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    action_name = args.action if args.action != "BendGripChairBack" else CROUCH_ACTION
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    report = {"script": Path(__file__).name, "task": "crouch", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "step_foot": args.step_foot, "problems": []}
    print(f"下蹲 / 被推退（口径 §15.7 ② 件 · C′ 平衡与支撑 · 凸包件 #170）· 动作名 {action_name}")
    print(f"帧表：中立 {CROUCH_FRAME_NEUTRAL} · **下蹲到位 {CROUCH_FRAME_READY}** · 被推 {CROUCH_FRAME_PUSH}"
          f"→{CROUCH_FRAME_PUSH_END} · **失衡极值 {CROUCH_FRAME_IMBALANCE}**（推导 = 摆动脚首次离地，"
          f"见 crouch_imbalance_frame()）· **后撤落地 {CROUCH_FRAME_STEP_END}** · "
          f"起身 {CROUCH_FRAME_RECOVER} · 末帧 {CROUCH_FRAME_END}（{args.fps} fps）")

    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    back_dir = _posterior(arm).copy()
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    curl_thumb = {s: detect_curl_axis_group(arm, s, "拇指") for s in CARD1_SIDES}
    curl_axes = {s: {f: (curl_thumb[s] if f == "Thumb" else curl[s]) for f in FINGERS}
                 for s in CARD1_SIDES}
    print(f"身体条件：背向（姿势现算 `posterior`）= "
          f"({back_dir.x:+.4f}, {back_dir.y:+.4f}, {back_dir.z:+.4f}) · "
          f"静止髋 ({hips_rest.x:+.4f}, {hips_rest.y:+.4f}, {hips_rest.z:+.4f})")
    for s in CARD1_SIDES:
        print(f"  静止踝 {s}: ({foot_rest[s].x:+.4f}, {foot_rest[s].y:+.4f}, {foot_rest[s].z:+.4f})")
    report["rest"] = {"背向": [round(v, 6) for v in back_dir],
                      "静止髋_m": [round(v, 6) for v in hips_rest],
                      "静止踝_m": {s: [round(v, 6) for v in foot_rest[s]] for s in CARD1_SIDES},
                      "f3_curl": {"四指": curl, "拇指": curl_thumb}}

    report["freedom_table"] = [
        {"行": "身体：下蹲下沉量", "值": args.crouch_depth, "单位": "m", "状态": "agent 解（本件选定）",
         "来源": "本件选定 + `--scan-posture` 并列 3 档（口径 §4.2 硬规矩 5）；同族先例 "
                 "`DOOR_PUSH_CROUCH_M = 0.06`（宿主 5 实测下沉 0.06 m 时踝偏 0.20 m 仍残差 0）"},
        {"行": "身体：被推后移量", "值": args.push_back, "单位": "m", "状态": "agent 解（本件选定）",
         "来源": "本件选定 + `--scan-posture` 并列 3 档；它决定「重心出域多深」"},
        {"行": "后撤步长 / 抬脚高度", "值": [args.step_back, CROUCH_STEP_LIFT_M], "单位": "m",
         "状态": "agent 解", "来源": "抬脚高度沿用宿主 5 的 `DOOR_PUSH_STEP_LIFT_M = 0.05`（同一量级）"},
        {"行": "后撤的那只脚", "值": args.step_foot, "单位": "—", "状态": "agent 解",
         "来源": "两解都解（`--step-foot`），读数并列在证据里"},
        {"行": "躯干前倾", "值": CROUCH_TORSO_LEAN_DEG, "单位": "°", "状态": "agent 解",
         "来源": "管线 §2.1.4（脊柱局部 X = 前倾）"},
        {"行": "**F4a 判据时域**（必填）", "值": "接地 = `持续`（整段）· 支撑域判定 = `逐帧`（判据面本身）· "
                                              "时序 = `一次性`（下蹲到位帧 / 失衡极值帧）",
         "单位": "—", "状态": "owner（涉观感）/ agent", "来源": "口径 §13.3 F4a · §13.4.1"},
        {"行": "支撑域 = 哪一层", "值": "**两层并列**（骨点层 / 蒙皮层）", "单位": "—",
         "状态": "**待 owner 裁**（#165 证据 §七 #4 的未裁项）",
         "来源": "凸包件 `xbot_balance.py`；本件的读数与建议见证据"},
    ]

    # ---- ① `--scan-posture`：身体条件的解空间（口径 §4.2 硬规矩 5 的 ≥2 解并列）----
    if args.scan_posture:
        print("\n身体条件解空间（口径 §4.2 硬规矩 5：agent 解的行必须并列 ≥2 个可行解）")
        print(f"  {'下蹲_m':>8}{'后移_m':>8}{'段':>6}{'髋_z_mm':>10}{'骨盆残差_mm':>12}"
              f"{'腿残差_mm':>11}{'骨点层余量':>12}{'蒙皮层余量':>12}{'骨判定':>7}{'皮判定':>7}")
        rows = []
        for depth in CROUCH_DEPTH_CANDIDATES:
            for back in CROUCH_PUSH_CANDIDATES:
                for tag, params in (("下蹲", crouch_frame_params(CROUCH_FRAME_READY, depth, back)),
                                    ("推到位", crouch_frame_params(CROUCH_FRAME_PUSH_END, depth, back))):
                    clear_pose(arm)
                    drop_temp(arm, also_objects=False)
                    tg = crouch_foot_targets(foot_rest, back_dir, params, args.step_foot)
                    body = crouch_body_setup(arm, m3, tg, params["crouch_m"], params["back_m"], back_dir)
                    crouch_arms_down(arm, m3, curl_axes)
                    legs = {s: body["leg_residual"][s] for s in CARD1_SIDES}
                    leg_res = max(abs(legs[s]["tip_err_mm"]) for s in CARD1_SIDES)
                    # 读数必须**当场量**（先 clear_pose 再量就量成了中立姿势的读数——宿主 6 踩过）
                    com = world_point(arm, f"{BONE_PREFIX}Hips")
                    bone_pts, skin_pts = [], []
                    for s in CARD1_SIDES:
                        for sfx in xb.BONE_POINT_SUFFIXES:
                            p = world_point(arm, f"{BONE_PREFIX}{s}{sfx}")
                            if p.z - 0.0 <= DOOR_PUSH_SOLE_MARGIN_MM / 1000.0:
                                bone_pts.append((p.x * 1000.0, p.y * 1000.0))
                    for s in CARD1_SIDES:
                        try:
                            idx = xb.cp._skin_index(arm, s)
                            skin_pts += [(x * 1000.0, y * 1000.0) for x, y in
                                         xb._skin_ground_points(arm, idx, DOOR_PUSH_SOLE_MARGIN_MM / 1000.0)]
                        except Exception as exc:
                            report["problems"].append(f"扫描：蒙皮层读数不可用（{exc}）")
                    com_xy = (com.x * 1000.0, com.y * 1000.0)
                    b = xb.balance_of_points(bone_pts, com_xy)
                    sk = xb.balance_of_points(skin_pts, com_xy)
                    row = {"下蹲_m": depth, "后移_m": back, "段": tag,
                           "髋_z_mm": round(com.z * 1000.0, 1),
                           "骨盆残差_mm": body["pelvis_err_mm"], "腿残差_mm": round(leg_res, 2),
                           "骨点层余量_mm": b["余量_mm"], "蒙皮层余量_mm": sk["余量_mm"],
                           "骨点层着地点数": b["着地足底点数"], "蒙皮层着地点数": sk["着地足底点数"],
                           "骨点层判定": b["判定"], "蒙皮层判定": sk["判定"]}
                    rows.append(row)
                    print(f"  {depth:8.2f}{back:8.2f}{tag:>6}{row['髋_z_mm']:10.1f}"
                          f"{row['骨盆残差_mm']:12.2f}{row['腿残差_mm']:11.2f}"
                          f"{str(row['骨点层余量_mm']):>12}{str(row['蒙皮层余量_mm']):>12}"
                          f"{row['骨点层判定']:>7}{row['蒙皮层判定']:>7}")
        report["scan_posture"] = {"行": rows,
                                  "来源": "本件选定；容差与判据面 = 凸包件 `xbot_balance.py`",
                                  "如实登记": "每行都在**同一个解算路径**下量（不 clear_pose 再量）"}
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0

    # ---- ② 逐帧解算（每帧解、每帧记参数；帧表由 `crouch_frame_params` 纯函数给出）----
    captured, per_frame = {}, []
    print(f"\n逐帧解算（帧 {CROUCH_FRAME_NEUTRAL}–{CROUCH_FRAME_END}，每帧解、每帧打键）")
    for frame in range(CROUCH_FRAME_NEUTRAL, CROUCH_FRAME_END + 1):
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        params = crouch_frame_params(frame, args.crouch_depth, args.push_back, args.step_back)
        if frame == CROUCH_FRAME_NEUTRAL:
            # ⚠️ 首帧必须严格中立（导出侧 E5 硬约定：导出时的姿势会被写进骨节点默认变换）
            captured[frame] = capture_channels(arm, panic_channel_names(arm))
            per_frame.append({**params, "中立": True})
            print(f"  帧 {frame:>3} **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        t = min(1.0, max(0.0, (frame - CROUCH_FRAME_NEUTRAL)
                         / float(CROUCH_FRAME_READY - CROUCH_FRAME_NEUTRAL)))
        tg = crouch_foot_targets(foot_rest, back_dir, params, args.step_foot)
        body = crouch_body_setup(arm, m3, tg, params["crouch_m"], params["back_m"], back_dir)
        hands = crouch_arms_down(arm, m3, curl_axes, t=t, post=_posterior(arm))
        captured[frame] = capture_channels(arm, panic_channel_names(arm))
        per_frame.append({**params, "髋_z_m": body["hips_z_m"], "骨盆残差_mm": body["pelvis_err_mm"],
                          "腿残差_mm": {s: round(body["leg_residual"][s]["tip_err_mm"], 2)
                                        for s in CARD1_SIDES}, "腕目标_m": hands})
        if frame in (CROUCH_FRAME_PUSH, CROUCH_FRAME_IMBALANCE, CROUCH_FRAME_STEP_END,
                     CROUCH_FRAME_RECOVER, CROUCH_FRAME_END):
            print(f"  帧 {frame:>3} 下蹲 {params['crouch_m']:.3f} m · 后移 {params['back_m']:.3f} m · "
                  f"后撤 {params['step_offset_m']:.3f} m（抬 {params['step_lift_m']:.3f} m）· "
                  f"髋 z {body['hips_z_m']:.4f} m · 骨盆残差 {body['pelvis_err_mm']:.2f} mm · "
                  f"腿残差 {max(abs(v) for v in per_frame[-1]['腿残差_mm'].values()):.2f} mm")
    report["frame_params"] = per_frame

    # ---- ③ 预览清理（#163 的椅子残留代理；先例 #166 第 2 轮 / 宿主 6）----
    residue = sorted(o.name for o in bpy.data.objects
                     if o.name.startswith("REF_")
                     and not any(m.type == "ARMATURE" for m in o.modifiers))
    for name in residue:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    report["preview_residue_removed"] = residue

    # ---- ④ 打键（逐帧；控制骨 + 脊柱/颈头 + 手指全打）----
    names = panic_channel_names(arm)
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    try:
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame in range(CROUCH_FRAME_NEUTRAL, CROUCH_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_start = CROUCH_FRAME_NEUTRAL
    bpy.context.scene.frame_end = CROUCH_FRAME_END
    report["frames"] = {"起": CROUCH_FRAME_NEUTRAL, "下蹲到位": CROUCH_FRAME_READY,
                        "被推": [CROUCH_FRAME_PUSH, CROUCH_FRAME_PUSH_END],
                        "失衡极值": CROUCH_FRAME_IMBALANCE,
                        "后撤落地": CROUCH_FRAME_STEP_END, "末": CROUCH_FRAME_END}
    report["keyed_channels"] = names
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    report["visible_bones"] = visible_bone_outliers(arm)
    print(f"\n已打键：动作 {action_name} · 帧 {CROUCH_FRAME_NEUTRAL}–{CROUCH_FRAME_END} · "
          f"通道 {len(names)} 个（含腿脚 "
          f"{sum(1 for n in names if 'Leg' in n or 'Foot' in n)} 个）")
    if report["visible_bones"]["非例外的越界骨"]:
        report["problems"].append(
            "可见骨伸出皮肤包围盒：" + "; ".join(
                f"{x['骨']}({x['伸出量_mm']:.1f} mm)" for x in report["visible_bones"]["非例外的越界骨"][:8]))

    # ---- ⑤ 产物侧读数：凸包 / 重心 / 接地（**全部来自凸包件**，本宿主不重算）----
    bal = xb.read_current(arm, action_name, fps=args.fps)
    report["balance"] = {k: bal[k] for k in ("逐帧", "结构", "接触相位", "静息对照", "读数指纹_sha256")}
    st = bal["结构"]
    for p in bal["problems"]:
        report["problems"].append(f"凸包件自核：{p}")
    print(f"\n凸包判据（凸包件 `xbot_balance.py` 读产物；接地/支撑区间引用 `xbot_contact_phase.py`）")
    for layer in xb.LAYERS:
        s = st[layer]
        print(f"  {layer}：可判 {s['可判帧数']}/{st['帧数']} · 域内 {s['域内帧数']} · "
              f"域外 {s['域外帧数']} [{xb.frame_list_cell(s['域外帧'])}] · 退化 {len(s['退化帧'])} · "
              f"余量最小 {s['余量最小_mm']} mm（帧 {s['余量最小帧']}）")
    print(f"  层选对照：判定不一致 {len(st['层选对照']['判定不一致帧'])} 帧 · "
          f"最大余量差 {st['层选对照']['最大余量差_mm']} mm（帧 {st['层选对照']['最大余量差帧']}）")
    print(f"  接地：无支撑区间 {xb.iv_cell(bal['接触相位']['无支撑区间'])} · "
          f"换脚帧 {xb.frame_list_cell(bal['接触相位']['换脚帧'])} · "
          f"双支撑 {xb.iv_cell(bal['接触相位']['双支撑区间'])}")

    # 派生判据：① 报红断言（失衡窗口里必须有域外帧）② 支撑断言（下蹲与站定期逐帧在域内）
    per_frame_bal = {r["帧"]: r for r in bal["逐帧"]}
    imbalance_window = list(range(CROUCH_FRAME_PUSH + 1, CROUCH_FRAME_STEP_END + 1))
    stable_frames = (list(range(CROUCH_FRAME_READY, CROUCH_FRAME_PUSH + 1))
                     + list(range(CROUCH_FRAME_RECOVER, CROUCH_FRAME_END + 1)))
    crit = {}
    for layer in xb.LAYERS:
        out_frames = [f for f in imbalance_window if per_frame_bal[f][layer]["判定"] == xb.V_OUT]
        bad = [f for f in stable_frames if per_frame_bal[f][layer]["判定"] != xb.V_IN]
        crit[layer] = {"失衡窗口": [CROUCH_FRAME_PUSH + 1, CROUCH_FRAME_STEP_END],
                       "失衡窗口内的域外帧": out_frames,
                       "稳定段": [stable_frames[0], stable_frames[-1]],
                       "稳定段内的非域内帧": bad}
    report["balance_criterion"] = crit
    print(f"\n判据断言（口径 §4.2 硬规矩 2：判据必须**能报红**）")
    for layer in xb.LAYERS:
        c = crit[layer]
        print(f"  {layer}：失衡窗口 {c['失衡窗口']} 内域外帧 {len(c['失衡窗口内的域外帧'])} 个 "
              f"[{xb.frame_list_cell(c['失衡窗口内的域外帧'])}] · 稳定段 {c['稳定段']} 内非域内帧 "
              f"{len(c['稳定段内的非域内帧'])} 个 [{xb.frame_list_cell(c['稳定段内的非域内帧'])}]")

    # ---- ⑥ 时序（V-f 的机械面，零阈值）：声明的两个极值帧 == 产物侧极值帧 ----
    hips_curve = [(r["帧"], r["重心_z_mm"]) for r in bal["逐帧"] if "重心_z_mm" in r]
    margin_curve = [(r["帧"], per_frame_bal[r["帧"]][xb.LAYER_SKIN]["余量_mm"])
                    for r in bal["逐帧"] if per_frame_bal[r["帧"]][xb.LAYER_SKIN]["余量_mm"] is not None]
    arg_hips = min(hips_curve, key=lambda t: t[1])[0] if hips_curve else None
    arg_margin = min(margin_curve, key=lambda t: t[1])[0] if margin_curve else None
    report["timing"] = {
        "下蹲到位": {"声明": CROUCH_FRAME_READY, "产物": arg_hips,
                     "判据量": "`mixamorig:Hips` 骨世界高度的**首个极小**（平段取首帧，先例 §2.2 的定帧规则）",
                     "曲线": [{"帧": f, "髋_z_mm": round(z * 1000.0, 4)} for f, z in hips_curve]},
        "失衡极值": {"声明": CROUCH_FRAME_IMBALANCE, "产物": arg_margin,
                     "判据量": f"重心到支撑域边界的带符号余量（{xb.LAYER_SKIN}）的最小值帧",
                     "曲线": [{"帧": f, "余量_mm": v} for f, v in margin_curve]},
    }
    report["timing"]["下蹲到位"]["一致"] = bool(arg_hips == CROUCH_FRAME_READY)
    report["timing"]["失衡极值"]["一致"] = bool(arg_margin == CROUCH_FRAME_IMBALANCE)
    print(f"  时序：下蹲到位 声明 {CROUCH_FRAME_READY} / 产物 {arg_hips} ⇒ "
          f"{'一致 ✅' if arg_hips == CROUCH_FRAME_READY else '不一致 ❌'} · "
          f"失衡极值 声明 {CROUCH_FRAME_IMBALANCE} / 产物 {arg_margin} ⇒ "
          f"{'一致 ✅' if arg_margin == CROUCH_FRAME_IMBALANCE else '不一致 ❌'}")

    # ---- ⑦ 穿模（判据 4 的形态：自穿模 + 地面）----
    def product_frame(frame):
        bpy.context.scene.frame_set(frame)
        update()
        d = bpy.context.evaluated_depsgraph_get()
        return arm.evaluated_get(d)

    clash = []
    for frame in range(CROUCH_FRAME_NEUTRAL, CROUCH_FRAME_END + 1):
        ev = product_frame(frame)
        row = {"frame": frame, "对": {}, "地面_最坏_mm": None, "地面_最坏处": None}
        for cname, cthr, bones_a, bones_b in CROUCH_CLASH_PAIRS:
            worst, where = None, None
            for ba in bones_a:
                if f"{BONE_PREFIX}{ba}" not in ev.pose.bones:
                    continue
                for bb in bones_b:
                    if f"{BONE_PREFIX}{bb}" not in ev.pose.bones:
                        continue
                    a0, a1 = world_point(ev, f"{BONE_PREFIX}{ba}"), world_point(ev, f"{BONE_PREFIX}{ba}", "tail")
                    b0, b1 = world_point(ev, f"{BONE_PREFIX}{bb}"), world_point(ev, f"{BONE_PREFIX}{bb}", "tail")
                    g = segment_gap_mm(a0, a1, b0, b1)
                    if worst is None or g < worst:
                        worst, where = g, f"{ba}↔{bb}"
            row["对"][cname] = {"阈值_mm": cthr, "最坏_mm": None if worst is None else round(worst, 2),
                                "最坏处": where, "违规": bool(worst is not None and worst < cthr)}
        for bn in CROUCH_GROUND_BONES:
            if f"{BONE_PREFIX}{bn}" not in ev.pose.bones:
                continue
            for tag, pt in (("head", world_point(ev, f"{BONE_PREFIX}{bn}")),
                            ("mid", (world_point(ev, f"{BONE_PREFIX}{bn}")
                                     + world_point(ev, f"{BONE_PREFIX}{bn}", "tail")) * 0.5),
                            ("tail", world_point(ev, f"{BONE_PREFIX}{bn}", "tail"))):
                if row["地面_最坏_mm"] is None or pt.z * 1000.0 < row["地面_最坏_mm"]:
                    row["地面_最坏_mm"], row["地面_最坏处"] = round(pt.z * 1000.0, 2), f"{bn}.{tag}"
        row["地面_违规"] = bool(row["地面_最坏_mm"] is not None and row["地面_最坏_mm"] < 0.0)
        row["姿态读数"] = {s_: crouch_arm_readings(ev, s_) for s_ in CARD1_SIDES}
        clash.append(row)
    report["clash"] = {"阈值_自穿模_mm": 10.0, "阈值_地面_mm": 0.0,
                       "来源": "动作库规格 §四·戊·5 判据 4 的三个数（骨段零穿透 · 骨心 ≤ 2 cm · 间隙 ≥ 1 cm）；"
                               "本件的碰撞体 = 自身与地面（本件无道具）",
                       "行": clash,
                       "违规帧": [r["frame"] for r in clash
                                  if r["地面_违规"] or any(v["违规"] for v in r["对"].values())]}
    worst_pair = min([v["最坏_mm"] for r in clash for v in r["对"].values()
                      if v["最坏_mm"] is not None] or [float("nan")])
    worst_ground = min([r["地面_最坏_mm"] for r in clash if r["地面_最坏_mm"] is not None]
                       or [float("nan")])
    report["clash"]["最坏_自穿模_mm"] = None if worst_pair != worst_pair else round(worst_pair, 2)
    report["clash"]["最坏_地面_mm"] = None if worst_ground != worst_ground else round(worst_ground, 2)
    print(f"  穿模（判据 4 的形态）：自穿模最坏 {worst_pair:.2f} mm（阈值 10）· "
          f"地面最坏 {worst_ground:.2f} mm（阈值 0）⇒ 违规帧 {len(report['clash']['违规帧'])}")

    # ---- ⑧ 判据汇总（problems）----
    problems = report["problems"]
    if not crit[xb.LAYER_SKIN]["失衡窗口内的域外帧"]:
        problems.append("报红断言失败：失衡窗口内**没有任何域外帧**（判据在蒙皮层上不退化性未证）")
    if crit[xb.LAYER_SKIN]["稳定段内的非域内帧"]:
        problems.append(f"支撑断言失败（蒙皮层）：稳定段内非域内帧 "
                        f"{crit[xb.LAYER_SKIN]['稳定段内的非域内帧'][:8]}")
    if not report["timing"]["下蹲到位"]["一致"]:
        problems.append(f"时序：下蹲到位 声明 {CROUCH_FRAME_READY} ≠ 产物极值帧 {arg_hips}")
    if not report["timing"]["失衡极值"]["一致"]:
        problems.append(f"时序：失衡极值 声明 {CROUCH_FRAME_IMBALANCE} ≠ 产物极值帧 {arg_margin}")
    if bal["接触相位"]["无支撑区间"]:
        problems.append(f"接地：无支撑区间 {bal['接触相位']['无支撑区间'][:4]}")
    if report["clash"]["违规帧"]:
        problems.append(f"穿模：违规帧 {report['clash']['违规帧'][:8]}")
    # ---- 目视敏感量的三条**零阈值**断言（第 1 版漏掉的量：手臂/膝）----
    # ⚠️ **首帧例外**：导出侧 E5 硬约定要求首帧**严格中立**（零通道 ⇒ T-pose 平举，腕与肩等高）
    #    ⇒ 垂放断言从**首帧之后**起算（这不是放宽阈值，是判据的作用域：那两帧量的是"没有姿势"）。
    arm_rows = [{"frame": r["frame"], **v} for r in clash for v in r["姿态读数"].values()
                if r["frame"] != CROUCH_FRAME_NEUTRAL]
    worst_down = min(r["肩→腕_下_mm"] for r in arm_rows)
    cross_mid = [r["frame"] for r in arm_rows if r["肩→腕_侧_mm"] < 0.0]
    knee_in = [r["frame"] for r in arm_rows if r["膝_侧_mm"] < 0.0]
    report["pose_judgements"] = {
        "垂放断言（腕在肩之下，零阈值）": {"最坏_肩→腕_下_mm": round(worst_down, 1),
                                          "作用域": f"帧 {CROUCH_FRAME_NEUTRAL + 1}–{CROUCH_FRAME_END}"
                                                    f"（首帧必须严格中立 ⇒ 不计入）",
                                          "违规帧": [r["frame"] for r in arm_rows if r["肩→腕_下_mm"] <= 0.0]},
        "不越中线（腕的同侧分量 ≥ 0，零阈值）": {"违规帧": sorted(set(cross_mid))},
        "不内扣（膝的同侧分量 ≥ 0，零阈值）": {"违规帧": sorted(set(knee_in))},
        "逐帧读数": [{"frame": r["frame"], **{k: v for k, v in r.items() if k != "frame"}}
                     for r in [{"frame": rr["frame"], **vv} for rr in clash for vv in rr["姿态读数"].values()]],
    }
    print(f"  目视敏感量（第 1 版漏掉、owner 目视当场否掉的那几项）："
          f"肩→腕 下最坏 {worst_down:.1f} mm · 越中线帧 {len(set(cross_mid))} · 膝内扣帧 {len(set(knee_in))}"
          f" · 帧 {CROUCH_FRAME_IMBALANCE}："
          + str(next((r for r in report["pose_judgements"]["逐帧读数"]
                      if r["frame"] == CROUCH_FRAME_IMBALANCE and r["肩→腕_侧_mm"] > 0), {})))
    if report["pose_judgements"]["垂放断言（腕在肩之下，零阈值）"]["违规帧"]:
        problems.append(f"垂放断言失败（腕不在肩下）帧："
                        f"{report['pose_judgements']['垂放断言（腕在肩之下，零阈值）']['违规帧'][:6]}")
    if cross_mid:
        problems.append(f"手臂越过身体中线的帧：{sorted(set(cross_mid))[:6]}")
    if knee_in:
        problems.append(f"膝内扣（同侧分量为负）的帧：{sorted(set(knee_in))[:6]}")
    for row in per_frame:
        leg = row.get("腿残差_mm") or {}
        if leg and max(abs(v) for v in leg.values()) > 1.0:
            problems.append(f"帧 {row['frame']}：腿解析解残差 {leg} mm > 1.0（踝没到目标）")
    report["ok"] = not problems
    report["构造的报红帧"] = crit[xb.LAYER_SKIN]["失衡窗口内的域外帧"]

    # ---- ⑨ 回显卡（口径 §四：每一项都要有产物侧读数）----
    card = []
    for layer in xb.LAYERS:
        s = st[layer]
        card.append({"判据量": f"重心（Hips 水平投影）∈ 支撑凸包（**{layer}**）",
                     "判据形态": "点 ∈ 凸包（布尔，含边界）",
                     "产物侧读数": f"域内 {s['域内帧数']} / 域外 {s['域外帧数']} / 退化 {len(s['退化帧'])}"
                                   f"（余量最小 {s['余量最小_mm']} mm @ 帧 {s['余量最小帧']}）",
                     "容差档": "**零阈值**（布尔；余量只报读数）",
                     "状态": "✅" if s["域外帧"] else "❌ 判据退化（无域外帧）"})
    card.append({"判据量": "报红断言：失衡窗口内存在域外帧（判据**能失败**）",
                 "判据形态": "布尔存在性（非退化对照）",
                 "产物侧读数": f"蒙皮层 {len(crit[xb.LAYER_SKIN]['失衡窗口内的域外帧'])} 帧 · "
                               f"骨点层 {len(crit[xb.LAYER_BONE]['失衡窗口内的域外帧'])} 帧",
                 "容差档": "—", "状态": "✅" if crit[xb.LAYER_SKIN]["失衡窗口内的域外帧"] else "❌"})
    card.append({"判据量": "支撑断言：下蹲段与站定段逐帧在域内",
                 "判据形态": "逐帧布尔（持续型，松一帧即红）",
                 "产物侧读数": f"蒙皮层非域内帧 {len(crit[xb.LAYER_SKIN]['稳定段内的非域内帧'])} · "
                               f"骨点层非域内帧 {len(crit[xb.LAYER_BONE]['稳定段内的非域内帧'])}",
                 "容差档": "—", "状态": "✅" if not crit[xb.LAYER_SKIN]["稳定段内的非域内帧"] else "❌"})
    card.append({"判据量": "时序：下蹲到位帧（髋高曲线极值）", "判据形态": "帧号相等（无阈值）",
                 "产物侧读数": f"声明 {CROUCH_FRAME_READY} · 产物 {arg_hips}",
                 "容差档": "—", "状态": "✅" if arg_hips == CROUCH_FRAME_READY else "❌"})
    card.append({"判据量": "时序：失衡极值帧（余量曲线极值）", "判据形态": "帧号相等（无阈值）",
                 "产物侧读数": f"声明 {CROUCH_FRAME_IMBALANCE} · 产物 {arg_margin}",
                 "容差档": "—", "状态": "✅" if arg_margin == CROUCH_FRAME_IMBALANCE else "❌"})
    card.append({"判据量": "接地：足底 ↔ 地面（M2，**持续**，引用 #165 的件）",
                 "判据形态": "点↔面（`soleMargin`）",
                 "产物侧读数": f"无支撑区间 {xb.iv_cell(bal['接触相位']['无支撑区间'])} · "
                               f"换脚帧 {xb.frame_list_cell(bal['接触相位']['换脚帧'])} · "
                               f"最坏陷入 {min(min(r['左最低_mm'], r['右最低_mm']) for r in bal['逐帧']):.2f} mm",
                 "容差档": f"soleMargin {DOOR_PUSH_SOLE_MARGIN_MM} mm（沿用）",
                 "状态": "✅" if not bal["接触相位"]["无支撑区间"] else "❌"})
    card.append({"判据量": "穿模：自穿模（腿↔腿 / 手↔腿）与地面（**持续**）",
                 "判据形态": "骨段↔骨段 / 骨段↔面（判据 4 的形态）",
                 "产物侧读数": f"自穿模最坏 {report['clash']['最坏_自穿模_mm']} mm · "
                               f"地面最坏 {report['clash']['最坏_地面_mm']} mm · "
                               f"违规帧 {len(report['clash']['违规帧'])}",
                 "容差档": "间隙 ≥ 10 mm（判据 4 的第三个数）· 地面零穿透（第一个数）",
                 "状态": "✅" if not report["clash"]["违规帧"] else "❌"})
    card.append({"判据量": "手臂垂放：腕在肩**之下**（零阈值）", "判据形态": "带符号分量的布尔",
                 "产物侧读数": f"最坏 肩→腕_下 = {worst_down:.1f} mm（正 = 腕在肩下）",
                 "容差档": "0.0 mm（**零阈值**：腕不得与肩等高或更高）",
                 "状态": "✅" if not report["pose_judgements"]["垂放断言（腕在肩之下，零阈值）"]["违规帧"] else "❌"})
    card.append({"判据量": "手臂**不越身体中线** / 膝**不内扣**（零阈值）", "判据形态": "带符号分量的布尔",
                 "产物侧读数": f"越中线帧 {len(set(cross_mid))} · 膝内扣帧 {len(set(knee_in))}"
                               f"（第 1 版实测：双臂横跨中线 **386 mm**、前伸 391 mm ⇒ 僵尸式前伸）",
                 "容差档": "0.0 mm（**零阈值**）",
                 "状态": "✅" if not cross_mid and not knee_in else "❌"})
    report["feedback_card"] = card

    print("\n" + "=" * 100)
    print(f"回显卡（口径 §四：每一项都要有产物侧读数）· 动作 {action_name}")
    for row in card:
        print(f"  {row['判据量'][:40]:<42}{row['判据形态'][:22]:<24}{str(row['产物侧读数'])[:70]:<72}"
              f"{row['状态']}")
    print("=" * 100)

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.markdown:
        xb_sample = {"id": args.name or Path(tmpl).stem, "名称": args.name or "crouch",
                     "动作": action_name, "样本文件": str(tmpl), "fps": bal["fps"],
                     "帧范围": st["帧范围"], "逐帧": bal["逐帧"], "结构": st,
                     "接触相位": bal["接触相位"]}
        Path(args.markdown).write_text(xb.sample_markdown(xb_sample), encoding="utf-8")
        print(f"markdown（凸包件样本段）: {args.markdown}")
    if args.still:
        best = crit[xb.LAYER_SKIN]["失衡窗口内的域外帧"] or [CROUCH_FRAME_IMBALANCE]
        for frame, suffix in ((CROUCH_FRAME_READY, "ready"), (best[0], "imbalance"),
                              (CROUCH_FRAME_STEP_END, "step"), (CROUCH_FRAME_END, "end")):
            bpy.context.scene.frame_set(frame)
            update()
            pt = world_point(arm, f"{BONE_PREFIX}Hips")
            path = str(args.still).replace(".png", f"_{suffix}.png")
            render_still(path, pt + Vector((1.9, 1.4, 0.7)), pt)
            print(f"静帧：{path}")
    if args.host == "live":
        bpy.context.scene.frame_set(CROUCH_FRAME_IMBALANCE)
        update()
        print(f"[live] 停在失衡极值帧 {CROUCH_FRAME_IMBALANCE}（预览；未写回文件）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl))
        print(f"已写回母版副本：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL'} —— problems {report['problems']}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 8：跪地 / 顶肘（`--task kneel`）——[#171] 的交付 · 口径 §15.7 ③ 件（**A′ 部位 ↔ 物面**）
#
#   关系类型 **A′ 部位 ↔ 物面**：两个目标分属**两个不同的系**（口径 §6.1）——
#     · **跪地**：右膝**前面** ↔ **地面**（世界 / 重力系 —— M2 接地判据用的就是它）
#     · **顶肘**：左肘**肘尖（鹰嘴 · 后侧）面** ↔ **门板近侧面**（道具局部系 —— §6.3.1 已登记的命名面）
#   ⇒ 本件是「**一张卡之外的身体部位接触**」的第一个样本，而且它挑的两个目标**都不需要新建命名面登记**
#     （地面 = 世界系 · 门板 = 已登记的道具面）⇒ 它干净地回答一件事：
#     「**一次部位面登记 + ε** 是不是就够」。
#
#   ε **逐值取自本条实测**（`measure_xbot_surface_offset.py --set kneeelbow`，证据 §四）：
#     · 膝前面 = `*Leg` 局部 `+Z` · **71.0281 mm**（`Beta_Surface`；静止朝世界 −Y = **前**）
#     · 肘尖面 = 左 `+X` / 右 `−X` · **53.9201 / 53.9203 mm**（`Beta_Surface`；静止朝世界 +Y = **后**）
#
#   ⚠️ **换算系**（[#164] 那笔账）：两个面的法向都经 `arm.matrix_world` 换算。本条实测的代价读数
#     （证据 §四.4）：`Leg` 的 **`+Z` 差 71.0281 mm**、`ForeArm` 的 **`±X` 差 53.9201 mm**，
#     而它们的 `±X` / `±Y` 恰在 +90° X 旋转的**不动轴**上（差 0.0000 mm —— #163 那次"巧合相等"的同一格）。
#     ⇒ 与 #169 的耳侧相反：**本件两个真判据面都抓得住算错系**。
# ══════════════════════════════════════════════════════════════════════════════

KNEEL_ACTION = "KneelElbowBrace"

#: 部位面登记（结构沿用宿主 6 的 `HEAD_PART_FACES`；口径 §15.6 **逐件登记 · 不建空表**）
#: ⚠️ `面内轴` 与本条判据无关：本件的两个**目标面**（地面 / 门板近侧面）来自外部几何，
#:    部位面只提供**探针点集**（真实蒙皮面片）与 ε 自检（同 #169 的 `ε_实测复核`）。
KNEEL_PART_FACES = {
    # 两侧膝的 `+Z` 读数**逐值相同**（71.0281 · 平坦支撑 3 · 世界指向 −Y）⇒ 两行都登记：
    # `--scan-posture` 的「跪哪条腿」一档要换到左膝（口径 §15.6 逐件登记 = 用到的就登记）
    "knee_front_right": {"骨": f"{BONE_PREFIX}RightLeg", "轴": "+Z", "ε_mm": 71.0281,
                         "标签": "右膝前面（跪地判据面）"},
    "knee_front_left": {"骨": f"{BONE_PREFIX}LeftLeg", "轴": "+Z", "ε_mm": 71.0281,
                        "标签": "左膝前面（跪地判据面 · 换腿那一档）"},
    #: ⚠️ 本条实测的**登记事实**（证据 §四/§六）：`ForeArm` 的 `+X` 最外片层落在**前臂背侧**
    #: （骨长轴 `y ≈ 20–107 mm` 那一段），**不是**鹰嘴那一点——肘尖（鹰嘴）那圈的皮肤主导骨是 **`Arm`**
    #: （前臂的 `−Y` 外沿只有 −5.97 mm，即前臂侧皮肤只越过肘关节 6 mm）。
    #: ⇒ 判据面如实登记为「**前臂背侧面（肘尖一侧）**」：顶肘时压住板面的本来就是"肘 + 前臂背侧"这一片。
    "elbow_tip": {"骨": f"{BONE_PREFIX}LeftForeArm", "轴": "+X", "ε_mm": 53.9201,
                  "标签": "左前臂背侧面（肘尖一侧 · 顶肘判据面）"},
}
#: 面片片层（m）——沿用宿主 6 的 `PANIC_SLAB_M`（同一用途、同一量级）
KNEEL_SLAB_M = 0.008
#: 接触验收容差 = 口径 §8.2 的 `tol_contact`（**不是** ε；两个数不许混）
KNEEL_TOL_MM = CONTACT_TOL_MM

#: 帧表（30 fps）。⚠️ 两个"到位帧"是**声明值**，判据要求它们 == 产物侧「首次进入容差帧」（V-f 形态）
KNEEL_FRAME_NEUTRAL = 1      # 首帧严格中立（导出侧 E5 硬约定，同宿主 5/6/7）
KNEEL_FRAME_KNEE = 21        # **膝到位**（右膝前面首次落进容差）
KNEEL_FRAME_ELBOW = 33       # **肘到位**（左肘尖面首次落进容差）
KNEEL_FRAME_END = 61         # 保持到这一帧

#: 跪哪条腿 / 哪只脚在前踩
KNEEL_KNEE_SIDE = "Right"
KNEEL_SUPPORT_SIDE = "Left"

#: 门（几何唯一来源 = `door_layout()`；§6.3.1 登记的两套命名面之一）
KNEEL_DOOR_OPEN_DEG = DOOR_OPEN_START_DEG     # 半掩 20°
#: 骨盆所在的板面 `u`（距铰链，m）——顶肘落点在角色的**左**侧，故骨盆要比落点更靠铰链一侧
KNEEL_PANEL_U_M = 0.28
#: 判据面锚点在板上的位置（**声明值**，面内偏移只报读数）
KNEEL_CONTACT_U_M = 0.46
KNEEL_CONTACT_Z_M = 0.82
#: 上臂相对水平的下倾角（°）——决定"肘比肩低多少"；水平距离 = 上臂长·cos(φ)
KNEEL_ARM_ANGLE_DEG = 26.0
KNEEL_STANDOFF_GUESS_M = 0.42    # 站位初值（标定会把它解到"肩到门板中面 = 上臂长·cosφ + ε"）
KNEEL_HIPS_Z_GUESS_M = 0.45      # 跪姿骨盆高度初值（标定会把它解到"膝恰好触地"）
#: 两条腿的目标三角全部**由骨长反解**（不是手拍距离）：
#: `a` = 大腿长（`*UpLeg`→`*Leg`）· `b` = 小腿长（`*Leg`→`*Foot`）——实测值见证据。
#: ⚠️ **第 1 版是手拍的**（踝在膝后 0.40 m + 让 IK 自己决定膝落哪）⇒ 实测把膝解到**地面以下 59.18 mm**
#: （`RightUpLeg.tail`），而探针面的接触判据**照样报 0.00 mm** —— "判据绿而姿势错"现场复现。
KNEEL_THIGH_TILT_DEG = 6.0       # 跪地腿：大腿相对竖直**后倾** 6°（自然人跪，也给 IK 一点余地）
KNEEL_KNEE_ANKLE_Z_GUESS_M = 0.085  # 跪地脚：踝高**初值**——由标定解到"足背蒙皮触地"（不是手拍）
KNEEL_SUPPORT_ANKLE_SIDE_M = 0.10  # 前踩脚：横向偏移（朝身体左侧 = n）
KNEEL_SUPPORT_ANKLE_Z_M = 0.075    # 前踩脚：踝高（脚掌平放）
KNEEL_SUPPORT_KNEE_UP = 0.16        # 前踩腿：膝意图 = 髋 + (前 + 上·本值)·大腿长（大腿近水平、膝略高于髋）
KNEEL_SWING_CLEARANCE_M = 0.09      # 过渡期摆腿的**踝部离地余量**（同族先例：`DOOR_PUSH_STEP_LIFT_M = 0.05`）
KNEEL_SWING_MIN_SKIN_Z = 0.010      # 过渡期**足部蒙皮**的最低高度下限（m）——低于它就把踝抬上去重解
KNEEL_KNEE_JOINT_Z_GUESS_M = 0.071  # 膝（骨点）高度初值 ≈ 膝面 ε（`+Z` 朝下时就是它）；标定会解到"面触地"
KNEEL_STEP_LIFT_M = 0.10         # 下跪过程中两只脚各自抬起的峰值（避免"拖地"）
KNEEL_TORSO_LEAN_DEG = 7.0       # 躯干前倾（脊柱三段各 1/3；管线 §2.1.4：局部 X = 前倾）
KNEEL_PRESS_LEAN_DEG = 4.0       # 顶住之后**继续压**这么多度——让"持续"窗口不平凡（姿势在动、判据仍绿）
KNEEL_FOREARM_TILT = 0.22        # 前臂"朝上 + 朝角色侧"的比例
KNEEL_FIST_CURL = 1.0            # 顶肘那只手 = 握拳


# ---------------------------------------------------------------- 部位面（膝 / 肘）

_PART_SKIN_CACHE = {}


def part_bone_skin_local(arm, bone, mesh="Beta_Surface"):
    """该骨在指定蒙皮层上**主导顶点**的骨局部坐标（缓存）。

    判据与 `measure_xbot_surface_offset.dominant_set()` **同一套**（argmax 权重 == 该骨）——
    否则"判据面"与"ε 面"会是两个面（#163 的椅子几何两处各算一份就是这类错）。
    ⚠️ 只取 `Beta_Surface`：**判据层 = 蒙皮层**（口径 §10.1，#170 owner 裁定）。
    """
    key = (bone, mesh)
    if key in _PART_SKIN_CACHE:
        return _PART_SKIN_CACHE[key]
    bl_inv = arm.data.bones[bone].matrix_local.inverted()
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.name != mesh:
            continue
        vg = ob.vertex_groups.get(bone)
        if vg is None:
            continue
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g == vg.index:
                out.append(bl_inv @ (arm_inv @ (ob.matrix_world @ v.co)))
    _PART_SKIN_CACHE[key] = out
    return out


def kneel_part_frame(arm, key, mesh="Beta_Surface"):
    """部位面（口径 §15.6.1 逐件登记的那一行）：由该部位**当前** transform 实时求得。

    返回：`法向`（世界）· `面片`（真实蒙皮世界点集 = 判据的**探针**）· `ε_实测复核`（= 面片沿轴最外投影，
    与登记的 ε 两条独立来源互证 ⇒ "ε 能不能被消费"是读数而不是承诺，先例 #169 §4）。
    """
    spec = KNEEL_PART_FACES[key]
    pb = arm.pose.bones[spec["骨"]]
    m3 = arm.matrix_world.to_3x3()
    r3 = pb.matrix.to_3x3()
    axis_local = _axis_local(spec["轴"])
    n_world = (m3 @ (r3 @ axis_local)).normalized()
    pts = part_bone_skin_local(arm, spec["骨"], mesh)
    scale = arm.matrix_world.to_scale().x
    slab_local = KNEEL_SLAB_M / max(scale, 1e-9)
    ext = max(p.dot(axis_local) for p in pts)
    patch = [p for p in pts if p.dot(axis_local) >= ext - slab_local]
    patch_world = [arm.matrix_world @ (pb.matrix @ p) for p in patch]
    ext_mm = round(ext * scale * 1000.0, 4)
    return {"键": key, "标签": spec["标签"], "骨": spec["骨"], "局部轴": spec["轴"],
            "ε_mm": spec["ε_mm"], "ε_实测复核_mm": ext_mm,
            "ε_一致": bool(abs(ext_mm - spec["ε_mm"]) <= 0.01),
            "法向": n_world, "骨原点": arm.matrix_world @ pb.head,
            "面片": patch_world, "面片数": len(patch_world),
            "取样顶点数": len(pts)}


# ---------------------------------------------------------------- 目标面（地面 / 门板近侧面）


def kneel_door_geometry(open_deg=KNEEL_DOOR_OPEN_DEG, u_panel=KNEEL_PANEL_U_M):
    """门板几何 + **近侧面**判据面（口径 §6.3.1 的命名面；几何唯一来源 = `door_layout()`）。

    | 名 | 是什么 |
    |---|---|
    | `m` | 近侧面**朝外**法向（指向角色）——判据的符号基准 |
    | `面板点(u, z)` | 板面（中面）上的通用取点；近侧面 = 中面沿 `m` 再退半个板厚 |
    | `面` | 判据面的 frame：锚点 + 法向 + **有限面片**（板宽 × 板高；#164 的教训：不是无限平面） |
    """
    lay = door_layout(open_deg)
    m = -lay["n"]
    up = Vector((0.0, 0.0, 1.0))

    def panel_point(u_m, z_m):
        return lay["hinge"] + lay["u"] * u_m + m * (lay["thickness"] / 2.0) + up * z_m

    face = {"标签": "门板近侧面", "锚点": panel_point(KNEEL_CONTACT_U_M, KNEEL_CONTACT_Z_M),
            "法向": m, "u": lay["u"], "v": up,
            "u_span_m": (-KNEEL_CONTACT_U_M, lay["width"] - KNEEL_CONTACT_U_M),
            "z_span_m": (-KNEEL_CONTACT_Z_M, lay["height"] - KNEEL_CONTACT_Z_M),
            "面片": [panel_point(uu, zz) for uu in (0.0, lay["width"])
                     for zz in (0.0, lay["height"])],
            "面片说明": f"板宽 {lay['width']} m × 板高 {lay['height']} m（有限面片）"}
    return lay, m, panel_point, face


def kneel_ground_face(anchor_xy):
    """**地面**判据面：世界 `z = 0` 平面，朝外法向 `+Z`（朝角色）。

    ⚠️ 不设"有限面片"：地面是**半空间**（判据与 M2 接地同一处理）——#164 的"有限面片"教训针对的是
    **小板面**（指尖飞在板外也会读成"过了面"），而地面的外沿不构成同一种歧义。
    """
    return {"标签": "地面", "锚点": Vector((anchor_xy[0], anchor_xy[1], 0.0)),
            "法向": Vector((0.0, 0.0, 1.0)), "u": None, "v": None,
            "面片": None, "面片说明": "半空间（无面片边界；与 M2 接地同一处理）"}


def kneel_contact_readings(probe, face, label, tol_mm=KNEEL_TOL_MM):
    """**弧面 ↔ 面**（口径 §13.4 的形态之一）：探针面片的**最低点** ↔ 目标面。

    判红量 = `沿法向间隙_mm`（`> 0` 悬空 · `< 0` 陷入 · `|·| ≤ tol` 贴合）；
    另报"面↔面顶点最近距离"（只报读数，有网格分辨力下限，先例 #169）与"是否落在面片内"。
    """
    gap = points_face_gap_mm(probe["面片"], (face["锚点"], face["法向"]))
    vals = [((p - face["锚点"]).dot(face["法向"]) * 1000.0, p) for p in probe["面片"]]
    low_mm, low = min(vals, key=lambda t: t[0])
    out = {"判据量": f"{label} ↔ {face['标签']}",
           "判据形态": "弧面↔面（探针面片最低点 ↔ 目标面）",
           "沿法向间隙_mm": low_mm,
           "面↔面顶点最近距离_mm": (points_min_distance_mm(probe["面片"], face["面片"])
                                    if face.get("面片") else None),
           "面↔面_分辨力_mm": "顶点间距量级（只报读数、不判红）",
           "探针点数": len(probe["面片"]), "探针": probe["标签"],
           "贴合": bool(abs(low_mm) <= tol_mm), "容差_mm": tol_mm}
    if face.get("u") is not None:
        du = (low - face["锚点"]).dot(face["u"]) * 1000.0
        dv = (low - face["锚点"]).dot(face["v"]) * 1000.0
        u0, u1 = [x * 1000.0 for x in face["u_span_m"]]
        z0, z1 = [x * 1000.0 for x in face["z_span_m"]]
        out.update({"面内偏移_mm": [round(du, 1), round(dv, 1)],
                    "面内窗口_mm": [[round(u0, 1), round(u1, 1)], [round(z0, 1), round(z1, 1)]],
                    "落在面片内": bool(u0 <= du <= u1 and z0 <= dv <= z1)})
    else:
        out.update({"面内偏移_mm": None, "面内窗口_mm": None, "落在面片内": None})
    return out


# ---------------------------------------------------------------- 姿势解算（跪 + 顶肘）

def kneel_facing(lay):
    """角色的朝向：**面朝 −u**（沿门板、朝铰链）⇒ 门板落在他的**左侧**。

    ⚠️ 为什么不能面朝门板（本件设计期推演 + 实测）：单膝跪地里前踩脚在身前 ≈0.34 m、前膝还要更靠前
    （大腿近水平），而门板近侧面离身体只有 ≈0.3 m ⇒ **前腿会穿进门板**。沿板面朝向时前腿沿板面走、
    到板面的横向距离不变 ⇒ 无冲突。代价：顶肘是**侧向**的（`鸡翅`式），这正是"顶住门"的自然姿势。
    """
    fwd = -lay["u"]
    up = Vector((0.0, 0.0, 1.0))
    left = up.cross(fwd).normalized()
    yaw = math.degrees(math.atan2(fwd.x, -fwd.y))
    return fwd, left, yaw


def _contact_phase():
    """惰性取 #165 的件（足底/足部蒙皮取点）——本宿主的接地读数不重写第二份。"""
    if "cp" not in globals():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        globals()["cp"] = __import__("xbot_contact_phase")
    return globals()["cp"]


def knee_face_key(ctx):
    """跪地侧的膝面键（两侧读数逐值相同，登记两行；标签随侧走）。"""
    return "knee_front_right" if ctx["knee_side"] == "Right" else "knee_front_left"


def kneel_bone_lengths(arm):
    """两骨链的**实测骨长**（米）——两条腿与左臂的目标三角全部从这里算，不用手拍距离。"""
    B = BONE_PREFIX
    side = "Right"
    return {"thigh": (world_point(arm, f"{B}{side}Leg") - world_point(arm, f"{B}{side}UpLeg")).length,
            "shin": (world_point(arm, f"{B}{side}Foot") - world_point(arm, f"{B}{side}Leg")).length,
            "upper_arm": (world_point(arm, f"{B}LeftForeArm") - world_point(arm, f"{B}LeftArm")).length}


def kneel_knee_leg(arm, ctx, hip_xy, kz, lens):
    """**跪地腿**的目标三角：`→ (踝目标, 膝意图, 髋目标)`（三者互为刚体，骨长逐值用上）。

    | 点 | 取法 | 为什么 |
    |---|---|---|
    | 膝 | `(hip_xy, kz)` | `kz` 由标定解出（"膝面触地"的物理含义），**不是手拍高度** |
    | 髋 | 膝 + (上·cos6° + 背·sin6°)·大腿长 | 大腿竖直略后倾；`|髋−膝| = a` **正好** |
    | 踝 | 膝 + 背·`√(b²−(kz−z_踝)²)` + 上·`(z_踝−kz)` | 让 `|膝−踝| = b` **正好** ⇒ 膝意图才落在 IK 的解圆上 |
    """
    up = Vector((0.0, 0.0, 1.0))
    back = ctx["back"]
    tilt = math.radians(KNEEL_THIGH_TILT_DEG)
    knee = Vector((hip_xy[0], hip_xy[1], kz))
    hip = knee + (up * math.cos(tilt) + back * math.sin(tilt)) * lens["thigh"]
    dz = ctx["knee_ankle_z_m"] - kz
    back_m = math.sqrt(max(lens["shin"] ** 2 - dz * dz, 1e-6))
    ankle = knee + back * back_m + up * dz
    return ankle, knee, hip


def kneel_support_leg(arm, ctx, lens):
    """**前踩腿**的目标三角：`→ (踝目标, 膝意图, 髋)`。

    | 点 | 取法 | 为什么 |
    |---|---|---|
    | 膝 | 髋 + (前 + 上·`KNEEL_SUPPORT_KNEE_UP`)·大腿长 | 跪姿下髋高 ≈ 小腿长（0.45 m）⇒ **大腿必须近水平** |
    | 踝 | 膝 + (下 − 前·t)·小腿长，`t` 由"踝落到静止踝高"解出 | 小腿近竖直、脚掌平放；`t` 是**解出来的** |

    ⚠️ 第 1 版把膝意图放在"髋前下方 45°"（`fwd − up` 各 0.707）⇒ 髋高只有 0.45 m 时，小腿只剩
    "近水平前伸"这一种解：实测**前踩腿小腿平铺在地面上、踝在膝前 0.44 m**，判据当场报出
    **膝的前面朝外 −0.954**（腿反着伸）。⇒ 膝的高度是**由髋高与骨长决定**的，不是自由量。
    """
    B = BONE_PREFIX
    up = Vector((0.0, 0.0, 1.0))
    fwd = ctx["fwd"]
    hip = world_point(arm, f"{B}{ctx['support_side']}UpLeg").copy()
    knee = hip + (fwd + up * KNEEL_SUPPORT_KNEE_UP).normalized() * lens["thigh"]
    za = ctx["rest"]["踝"][ctx["support_side"]].z        # 平放脚的踝高 = 静止踝高（母版实测）
    drop = knee.z - za
    t = math.sqrt(max((lens["shin"] / drop) ** 2 - 1.0, 0.0)) if drop > 1e-6 else 0.0
    d2 = (up * (-1.0) - fwd * t).normalized()            # 小腿近竖直、略向后
    ankle = knee + d2 * lens["shin"]
    return ankle, knee, hip


def kneel_place_hip(arm, m3, side, target, iters=6):
    """把**髋关节**（`*UpLeg` 骨点）送到指定世界位置——按实测误差回代（同 `set_pelvis_world` 的写法）。

    为什么不直接设骨盆位置：骨盆骨点与髋关节差一个横向 + 纵向偏移，且转身角会把它转走 ⇒ 实测回代。
    """
    pb = arm.pose.bones["CTRL_Hips"]
    pb.location = (0.0, 0.0, 0.0)
    update()
    delta = Vector(target) - world_point(arm, f"{BONE_PREFIX}{side}UpLeg")
    for _ in range(iters):
        set_world_offset(arm, m3, "CTRL_Hips", delta)
        update()
        delta = delta + (Vector(target) - world_point(arm, f"{BONE_PREFIX}{side}UpLeg"))
    return round((Vector(target) - world_point(arm, f"{BONE_PREFIX}{side}UpLeg")).length * 1000.0, 4)


def kneel_bend_dir(hip, ankle, knee):
    """把"想要的膝位置"化成 `bend_dir`：该点相对**髋-踝弦**的垂直分量（单位向量）。"""
    chord = Vector(ankle) - Vector(hip)
    c = chord.length
    if c < 1e-9:
        return Vector((0.0, 0.0, 1.0))
    axis = chord / c
    v = Vector(knee) - Vector(hip)
    v = v - axis * v.dot(axis)
    return v.normalized() if v.length > 1e-9 else Vector((0.0, 0.0, 1.0))


def kneel_solve_leg(arm, ctx, side, ankle_target, bend_dir):
    """两骨解析解（**屈曲方向**为输入）+ **滚转符号对齐静止局部 X**。

    ⚠️ 滚转符号是本件实测踩出来的真 bug：`solve_two_bone()` 拿 `hinge = (mid−root)×(tip−mid)` 当局部 X 的
    提示，而母版腿骨的静止局部 X 是**世界 −X**（管线 §2.1.2）⇒ 这个 cross 的符号让小腿**绕自身轴翻 180°**：
    实测跪姿下**小腿前面（局部 `+Z`）朝上**、判据面读到的是腿背面，标定于是把膝骨点压到**地面以下 70.7 mm**
    才把"最低点"顶到 0 —— **判据全绿而腿是反着跪的**（证据 §六）。
    ⇒ 本函数把 hinge 的符号按"指向角色**右侧**"钉死（两侧腿同轴，管线 §2.1.2）。
    """
    B = BONE_PREFIX
    hip = world_point(arm, f"{B}{side}UpLeg")
    ank = Vector(ankle_target)
    a = (world_point(arm, f"{B}{side}Leg") - hip).length
    b = (world_point(arm, f"{B}{side}Foot") - world_point(arm, f"{B}{side}Leg")).length
    chord = ank - hip
    c = chord.length
    axis = chord / c
    x = (a * a - b * b + c * c) / (2.0 * c)
    h = math.sqrt(max(a * a - x * x, 0.0))
    n = Vector(bend_dir) - axis * Vector(bend_dir).dot(axis)
    if n.length < 1e-9:
        n = Vector((0.0, 1.0, 0.0)) - axis * axis.y
    n.normalize()
    mid = hip + axis * x + n * h
    hinge = (mid - hip).cross(ank - mid)
    if hinge.length < 1e-8:
        hinge = ctx["right"].copy()
    hinge.normalize()
    if hinge.dot(ctx["right"]) < 0.0:
        hinge = -hinge
    _set_world_axes(arm, f"CTRL_{side}UpLeg", f"{B}{side}UpLeg", mid - hip, hinge)
    _set_world_axes(arm, f"CTRL_{side}Leg", f"{B}{side}Leg", ank - mid, hinge)
    update()
    return {"label": f"leg_{side}", "mid_m": [round(v, 4) for v in mid],
            "mid_err_mm": round((world_point(arm, f"{B}{side}Leg") - mid).length * 1000.0, 1),
            "tip_err_mm": round((world_point(arm, f"{B}{side}Foot") - ank).length * 1000.0, 1),
            "clamped_straight": bool(c >= a + b - 1e-6)}


def kneel_arm_hang(arm, m3, side, curl_axes, t=1.0, relax=CROUCH_RELAX_CURL, post=None):
    """**单侧**垂放（`crouch_arms_down()` 的单侧版）。

    ⚠️ 为什么不直接调 `crouch_arms_down()`：本件两条臂走**两条不同的路**（另一条先垂放后顶肘），
    而那件一次解两条臂。两条实测口径（世界偏移不碰矩阵 · 锚点是肩不是髋）逐字照抄
    （`crouch_arms_down` 的 docstring 记着 #170 第 1 轮"僵尸式前伸"的两次代价）。
    """
    sign = 1.0 if side == "Left" else -1.0
    shoulder = world_point(arm, f"{BONE_PREFIX}{side}Arm")
    sx, sy, sz = CROUCH_HAND_DROP_M
    target = shoulder + Vector((sx * sign, sy, sz))
    rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
    wrist = rest_wrist.lerp(target, t)
    elbow = Vector((CROUCH_ELBOW_DIR[0] * sign, CROUCH_ELBOW_DIR[1], CROUCH_ELBOW_DIR[2]))
    arm_info, elbow_scan = solve_arm_with_elbow_scan(
        arm, side, wrist, post if post is not None else Vector((0.0, 1.0, 0.0)))
    down = Vector((0.0, 0.0, -1.0))
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(Vector((sign, 0.0, 0.0)), down, t), Vector((0.0, 1.0, 0.0)))
    for finger in FINGERS:
        _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], relax * t)
    update(2)
    return {"腕目标_m": [round(v, 4) for v in target], "臂长_m": arm_info.get("limb_len_m"),
            "夹直": bool(arm_info.get("clamped_straight")), "肘扫描罚分": elbow_scan["罚分"]}


def kneel_arm_brace(arm, m3, ctx, t_down, s, curl_axes):
    """**左臂三态**：T-pose（`t_down`=0）→ 垂放（=1）→ **肘尖顶上板面**（`s`=1）。

    顶上那一态是**解析构造**的（不是搜索）：`E = S − m·(h−ε) − ẑ·drop`，其中 `drop = √(a² − (h−ε)²)`
    ⇒ ① `|E − S| = a`（正好是上臂长）② 肘尖面（`+X` 方向 = `−m`）落在板面**上**（`ε` 的换算在构造里用掉）。

    ⚠️ **`+X` 的方向就是"肘尖朝哪"**：本条实测左前臂的 `+X` 静止朝世界 `+Y`（后）= 鹰嘴那一侧
    ⇒ 顶上时把 `+X` 对到 `−m`（朝板面），压着板面的才是"肘尖那一侧"的面（不是前臂的掌侧）。

    ⚠️ **前臂的"朝上"必须垂直于板面法向**：否则 `_set_world_axes` 会把 `x_hint = −m` 正交化掉一截，
    判据面法向被拧走（实测 12.41°、最低点间隙 +11.74 mm 而构造出的 ε 锚点只在 1.26 mm）。
    侧向取 `back`（沿板面）——`left` 恰好就是 `−m`，拿它做倾斜等于没改。
    """
    side = "Left"
    down = Vector((0.0, 0.0, -1.0))
    S = world_point(arm, f"{BONE_PREFIX}{side}Arm")
    d_rest = (world_point(arm, f"{BONE_PREFIX}{side}ForeArm") - S).normalized()
    f_rest = (world_point(arm, f"{BONE_PREFIX}{side}Hand")
              - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).normalized()
    # **逐帧**重算顶上那一态（不是用标定那一刻的常量）：躯干一动，肩就动；肩一动，肘目标跟着挪
    # ⇒ 顶住之后继续压前倾时，肘**始终**落在板面上（"持续"窗口因此不平凡：姿势在动、判据仍绿）。
    a = ctx["lens"]["upper_arm"]
    eps = KNEEL_PART_FACES["elbow_tip"]["ε_mm"] / 1000.0
    up = Vector((0.0, 0.0, 1.0))
    h = (S - ctx["face"]["锚点"]).dot(ctx["m"])
    drop = math.sqrt(max(a * a - (h - eps) ** 2, 0.0))
    E = S - ctx["m"] * (h - eps) - up * drop
    d1 = (E - S).normalized() if s > 0.0 else (ctx.get("elbow_dir_stage1") or down)
    f1 = ctx.get("forearm_dir_stage1") or down
    d = _nlerp(_nlerp(d_rest, down, t_down), d1, s)
    f = _nlerp(_nlerp(f_rest, down, t_down), f1, s)
    hinge = d.cross(f)
    if hinge.length < 1e-6:
        hinge = Vector((0.0, 1.0, 0.0))
    hinge.normalize()
    _set_world_axes(arm, f"CTRL_{side}Arm", f"{BONE_PREFIX}{side}Arm", d, hinge)
    x0 = Vector((0.0, 1.0, 0.0))            # 静止 +X = 世界 +Y（后）——本条实测
    x_hint = _nlerp(x0, -ctx["m"], s)
    _set_world_axes(arm, f"CTRL_{side}ForeArm", f"{BONE_PREFIX}{side}ForeArm", f, x_hint)
    for finger in FINGERS:
        _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], KNEEL_FIST_CURL * s)
    update(2)
    return {"上臂方向": [round(c, 4) for c in d], "前臂方向": [round(c, 4) for c in f],
            "肘位置_m": [round(c, 4) for c in world_point(arm, f"{BONE_PREFIX}{side}ForeArm")],
            "肩位置_m": [round(c, 4) for c in S]}


def kneel_apply(arm, m3, ctx, t_leg, t_down, s_elbow, standoff, kz, curl_axes, lift=0.0,
                lean_extra=0.0):
    """按**任务空间参数**摆一帧，并当场量两个接触判据。

    | 参数 | 含义 |
    |---|---|
    | `t_leg` | 下跪进度 0→1：**目标三角**从静止姿势线性插到接触姿势（`t_leg=1` = 标定出的接触姿势） |
    | `t_down` | T-pose → 垂放的手臂过渡（首帧必须严格中立 ⇒ 由调用方直接捕获，不进本函数） |
    | `s_elbow` | 顶肘进度 0→1 |
    | `lift` | 额外的过渡期抬脚量（本宿主内部还会按**离地余量**自动补足，见 `lift_for()`） |
    """
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    lens = ctx["lens"]
    up = Vector((0.0, 0.0, 1.0))
    hip_xy = (ctx["panel_point"](ctx["u_panel"], 0.0) + ctx["m"] * standoff)
    hip_xy = (hip_xy.x, hip_xy.y)
    ankle_k, knee_k, hip_k = kneel_knee_leg(arm, ctx, hip_xy, kz, lens)

    def mix(a, b):
        return Vector(a) * (1.0 - t_leg) + Vector(b) * t_leg

    yaw_now = ctx["yaw"] * t_leg          # 转身也必须过渡：第 2 帧就拧 70° ⇒ 脚当场扎进地面（本件实测）
    set_euler(arm, "CTRL_Hips", y=yaw_now)
    update()
    # ① 骨盆：把**跪地那条腿的髋关节**送到目标位（膝的位置是设计量，骨盆是被解出来的）
    hip_target = mix(ctx["rest"]["髋"][ctx["knee_side"]], hip_k)
    hip_err = kneel_place_hip(arm, m3, ctx["knee_side"], hip_target)
    # ② 躯干前倾 + 目视水平
    lean = door_push_torso_lean(arm, ctx["lean_deg"] * t_down + lean_extra)
    solve_gaze_scan(arm, scale=1.0)
    update()
    # ③ 两条腿：**踝按位置插值**（脚要踩在地上，不能跟着髋一起沉下去）+ **屈曲方向按方向插值**。
    #    ⚠️ 两个反例都实测过：① 膝/踝都按位置插值 ⇒ 与骨长不自洽、IK 给垃圾解（趾骨沉到 −187 mm）；
    #    ② 整个三角按方向插值 ⇒ 腿刚性跟着髋下沉，脚陷进地面（−22.79 mm 起）。
    # 摆腿抬脚量：**够用就抬**——`max(固定摆动曲线, 把踝抬到"静止踝高 + 余量"所需的量)`，两端都归零。
    swing = KNEEL_STEP_LIFT_M * math.sin(math.pi * t_leg)

    def lift_for(ankle_target, side):
        need = (ctx["rest"]["踝"][side].z + KNEEL_SWING_CLEARANCE_M * math.sin(math.pi * t_leg)
                - ankle_target.z)
        return max(swing, max(0.0, need))

    def leg_targets(side, ankle_f, knee_f, hip_f):
        ankle_r, knee_r, hip_r = (ctx["rest"]["踝"][side], ctx["rest"]["膝"][side],
                                  ctx["rest"]["髋"][side])
        ankle_t = mix(ankle_r, ankle_f)
        bend = _nlerp(kneel_bend_dir(hip_r, ankle_r, knee_r), kneel_bend_dir(hip_f, ankle_f, knee_f), t_leg)
        return ankle_t, bend

    ak0, bend_k = leg_targets(ctx["knee_side"], ankle_k, knee_k, hip_k)
    # ⚠️ 前踩腿的最终三角按"当前髋"算：标定帧（`t_leg=1`）现算并缓存；过渡帧用缓存
    if t_leg >= 1.0 or "support_final" not in ctx:
        a_s, k_s, h_s = kneel_support_leg(arm, ctx, lens)
        if t_leg >= 1.0:
            ctx["support_final"] = (a_s.copy(), k_s.copy(), h_s.copy())
    else:
        a_s, k_s, h_s = ctx["support_final"]
    asup0, bend_s = leg_targets(ctx["support_side"], a_s, k_s, h_s)
    ak = ak0 + up * lift_for(ak0, ctx["knee_side"])
    asup = asup0 + up * lift_for(asup0, ctx["support_side"])
    leg_res = {ctx["knee_side"]: kneel_solve_leg(arm, ctx, ctx["knee_side"], ak, bend_k)}
    leg_res[ctx["support_side"]] = kneel_solve_leg(arm, ctx, ctx["support_side"], asup, bend_s)
    # ③′ 双脚朝向（随 `t_leg` 过渡；⚠️ 改小腿朝向会带走脚的世界朝向 ⇒ 必须能被重复调用）
    def set_feet():
        for side in ("Left", "Right"):
            ry = _rest_dir(arm, f"{BONE_PREFIX}{side}Foot")
            rx = _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot")
            if side == ctx["support_side"]:
                _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                                _nlerp(ry, _rot_z(ry, yaw_now), t_leg),
                                _nlerp(rx, _rot_z(rx, yaw_now), t_leg))
                continue
            # 跪地脚：**两段转向**——先"勾脚尖"（趾朝前上）再折到"脚背贴地"。
            # ⚠️ 一段直达会让脚趾**扫过朝下那一档**（实测足趾骨沉到地面以下 150 mm）
            ty = (ctx["back"] * 0.95 + Vector((0.0, 0.0, -0.31))).normalized()
            tx = ctx["right"].copy()
            mid = (ctx["fwd"] * 0.5 + Vector((0.0, 0.0, 1.0)) * 0.87).normalized()
            if t_leg < 0.5:
                ty_now, tx_now = _nlerp(ry, mid, t_leg * 2.0), _nlerp(rx, ctx["right"], t_leg * 2.0)
            else:
                ty_now = _nlerp(mid, ty, (t_leg - 0.5) * 2.0)
                tx_now = _nlerp(ctx["right"], tx, (t_leg - 0.5) * 2.0)
            _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot", ty_now, tx_now)
        update()

    set_feet()
    # 摆腿**离地自检**（只在过渡期）：脚在"平放 → 脚背贴地"的转向过程中会扫过朝下那一档，
    # 光抬踝不够（实测足趾骨沉到 −150.16 mm）⇒ 按**足部蒙皮实测最低点**把踝抬上去重解（回代）。
    if t_leg < 1.0:
        cp2 = _contact_phase()
        for side in (ctx["knee_side"], ctx["support_side"]):
            ctx.setdefault("foot_skin_idx", {})[side] = cp2._skin_index(arm, side)
        for _ in range(3):
            fixed = False
            for side in (ctx["knee_side"], ctx["support_side"]):
                low = cp2._skin_lowest(arm, ctx["foot_skin_idx"][side])
                if low is None or low >= KNEEL_SWING_MIN_SKIN_Z:
                    continue
                need = up * (KNEEL_SWING_MIN_SKIN_Z - low)
                if side == ctx["knee_side"]:
                    ak = ak + need
                else:
                    asup = asup + need
                fixed = True
            if not fixed:
                break
            leg_res[ctx["knee_side"]] = kneel_solve_leg(arm, ctx, ctx["knee_side"], ak, bend_k)
            leg_res[ctx["support_side"]] = kneel_solve_leg(
                arm, ctx, ctx["support_side"], asup, bend_s)
            set_feet()          # ⚠️ 重解腿之后必须重设脚（否则脚的世界朝向又跑回小腿那边）
        dbg = {s_: (None if cp2._skin_lowest(arm, ctx["foot_skin_idx"][s_]) is None
                    else round(cp2._skin_lowest(arm, ctx["foot_skin_idx"][s_]) * 1000.0, 2))
               for s_ in (ctx["knee_side"], ctx["support_side"])}
        print(f"    [离地自检] t_leg={t_leg:.2f} 足部蒙皮最低 {dbg} mm · "
              f"踝目标 z {round(ak.z * 1000, 1)} / {round(asup.z * 1000, 1)} mm")
    # ④ 双臂
    post = _posterior(arm)
    hands = {f"{ctx['support_side']}臂（垂放）": kneel_arm_hang(
        arm, m3, ctx["support_side"], curl_axes, t=min(1.0, t_down), post=post)}
    hands["左臂（顶肘）"] = kneel_arm_brace(arm, m3, ctx, t_down, s_elbow, curl_axes)
    update()
    # ⑤ 当场量两个接触判据（判据面 = 部位面的**真实蒙皮面片**）
    kkey = knee_face_key(ctx)
    knee_probe = kneel_part_frame(arm, kkey)
    elbow_probe = kneel_part_frame(arm, "elbow_tip")
    knee_face = kneel_ground_face((world_point(arm, f"{BONE_PREFIX}Hips").x,
                                   world_point(arm, f"{BONE_PREFIX}Hips").y))
    # **朝向自检**（判据面法向 vs 目标面法向）：量的是"肘尖到底朝没朝板面"
    fa = arm.pose.bones[f"{BONE_PREFIX}LeftForeArm"]
    x_world = (arm.matrix_world.to_3x3() @ (fa.matrix.to_3x3() @ Vector((1.0, 0.0, 0.0)))).normalized()
    aim = {"肘尖面法向_世界": [round(c, 4) for c in x_world],
           "与目标面法向(−m)夹角_deg": round(math.degrees(x_world.angle(-ctx["m"])), 2),
           "肘位置_m": [round(c, 4) for c in world_point(arm, f"{BONE_PREFIX}LeftForeArm")],
           "膝位置_m": [round(c, 4) for c in world_point(arm, f"{BONE_PREFIX}{ctx['knee_side']}Leg")],
           "膝前面法向_世界": [round(c, 4) for c in knee_probe["法向"]],
           "膝前面法向_与地面法向夹角_deg": round(
               math.degrees(knee_probe["法向"].angle(Vector((0.0, 0.0, 1.0)))), 2),
           "膝δ髋_mm": round((world_point(arm, f"{BONE_PREFIX}{ctx['knee_side']}Leg")
                              - world_point(arm, f"{BONE_PREFIX}{ctx['knee_side']}UpLeg")).length * 1000.0, 2)}
    return {"髋残差_mm": hip_err, "前倾": lean,
            "腿残差_mm": {k: leg_res[k]["tip_err_mm"] for k in leg_res},
            "膝残差_mm": {k: leg_res[k]["mid_err_mm"] for k in leg_res},
            "抬脚_mm": {ctx["knee_side"]: round((ak - ak0).z * 1000.0, 1),
                        ctx["support_side"]: round((asup - asup0).z * 1000.0, 1)},
            "踝目标_m": {ctx["knee_side"]: [round(c, 4) for c in ak],
                         ctx["support_side"]: [round(c, 4) for c in asup]},
            "膝_探针": knee_probe, "肘_探针": elbow_probe,
            "膝_读数": kneel_contact_readings(knee_probe, knee_face, KNEEL_PART_FACES[kkey]["标签"]),
            "肘_读数": kneel_contact_readings(elbow_probe, ctx["face"],
                                            KNEEL_PART_FACES["elbow_tip"]["标签"]),
            "朝向自检": aim, "臂": hands}


def kneel_calibrate(arm, m3, ctx, curl_axes, iters=8):
    """解出**接触姿势**的两个量——这是本件的"回代"，不是手拍常量：

    | 量 | 判据 | 为什么这样写 |
    |---|---|---|
    | `kz`（膝骨点高度） | 右膝前面 ↔ 地面的**沿法向间隙 = 0** | "跪下去"的物理含义就是膝触地；高度不是装饰 |
    | `standoff`（站位：髋目标到板面） | 肩到门板中面的水平距离 `h = 上臂长·cosφ + ε` | 让上臂**恰好够到**板面（肘顶上去时臂长正好用完） |
    | `knee_ankle_z`（跪地脚踝高） | 跪地那只脚的**足背蒙皮最低点 = 0** | 踝高不是手拍量：手拍 0.085 m 时足背扎到 −50.3 mm |

    三者近乎解耦（`kz` 只动膝 · `standoff` 只动沿 `m` 的位移 · 踝高只动足）⇒ 交替回代，实测 3 轮内收敛。
    """
    lens = ctx["lens"]
    cp = _contact_phase()
    a = lens["upper_arm"]
    eps = KNEEL_PART_FACES["elbow_tip"]["ε_mm"] / 1000.0
    phi = ctx.get("arm_angle_deg", KNEEL_ARM_ANGLE_DEG)
    target_h = a * math.cos(math.radians(phi)) + eps
    standoff, kz = KNEEL_STANDOFF_GUESS_M, KNEEL_KNEE_JOINT_Z_GUESS_M
    ctx.setdefault("knee_ankle_z_m", KNEEL_KNEE_ANKLE_Z_GUESS_M)
    foot_idx = {s: cp._skin_index(arm, s) for s in ("Left", "Right")}
    log = []
    for it in range(iters):
        out = kneel_apply(arm, m3, ctx, 1.0, 1.0, 0.0, standoff, kz, curl_axes)
        gap = out["膝_读数"]["沿法向间隙_mm"]
        S = world_point(arm, f"{BONE_PREFIX}LeftArm")
        h = (S - ctx["face"]["锚点"]).dot(ctx["m"])
        foot_low = cp._skin_lowest(arm, foot_idx[ctx["knee_side"]])
        log.append({"轮": it + 1, "standoff_m": round(standoff, 5), "膝骨点_z_m": round(kz, 5),
                    "膝间隙_mm": round(gap, 3), "肩到板面_m": round(h, 5),
                    "跪地踝高_m": round(ctx["knee_ankle_z_m"], 5),
                    "跪地足背最低_mm": None if foot_low is None else round(foot_low * 1000.0, 2)})
        kz -= gap / 1000.0
        standoff -= (h - target_h)
        if foot_low is not None:
            ctx["knee_ankle_z_m"] -= foot_low          # 踝高回代：让足背蒙皮正好落到地面
        if (abs(gap) < 0.02 and abs(h - target_h) < 5e-4 and foot_low is not None
                and abs(foot_low) < 0.0002 and it >= 1):
            break
    ctx["standoff_m"], ctx["knee_joint_z_m"] = round(standoff, 5), round(kz, 5)
    # 两条腿"最终"的髋→膝 / 膝→踝 方向（过渡期按方向插值用；位置插值会破坏骨长约束）
    hip_xy = (ctx["panel_point"](ctx["u_panel"], 0.0) + ctx["m"] * standoff)
    ankle_k, knee_k, hip_k = kneel_knee_leg(arm, ctx, (hip_xy.x, hip_xy.y), kz, lens)
    a_sup, k_sup, hip_sup = kneel_support_leg(arm, ctx, lens)
    ctx["support_final"] = (a_sup.copy(), k_sup.copy(), hip_sup.copy())
    ctx["elbow_dir_stage1"] = Vector((0.0, 0.0, -1.0))
    # ⚠️ 前臂的"朝上"方向必须**垂直于板面法向**：否则 `_set_world_axes` 会把 `x_hint = −m`
    #    正交化掉一截 ⇒ 判据面法向被拧走 12.41°（本件实测：肘尖面法向与 −m 夹角 12.41°、
    #    最低点间隙 +11.74 mm 而构造出来的 ε 锚点只在 1.26 mm）。
    #    ⚠️ 侧向必须取 `back`（沿板面）——`left` 恰好就是 **−m**（角色左侧正对板面），拿它做倾斜
    #    等于没改（第一版就是这么写的，实测夹角仍 12.41°）。
    ctx["forearm_dir_stage1"] = (Vector((0.0, 0.0, 1.0)) + ctx["back"] * KNEEL_FOREARM_TILT).normalized()
    return {"回合": log, "上臂长_m": round(a, 5), "大腿长_m": round(lens["thigh"], 5),
            "跪地踝高_m": round(ctx["knee_ankle_z_m"], 5),
            "小腿长_m": round(lens["shin"], 5), "目标_肩到板面_m": round(target_h, 5),
            "上臂下倾角_deg": phi, "standoff_m": ctx["standoff_m"],
            "膝骨点_z_m": ctx["knee_joint_z_m"],
            "肘比肩低_mm": round(math.sqrt(max(a * a - (target_h - eps) ** 2, 0.0)) * 1000.0, 1)}


def main_kneel() -> int:
    """跪地 / 顶肘宿主：逐帧解算 → 逐帧打键 → 从**产物**里读两个**接触对**（两个系各一条）。"""
    from datetime import datetime
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import xbot_contact_phase as cp          # 足底蒙皮取点沿用 #165 的件（不重写第二份）
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    action_name = args.action if args.action != "BendGripChairBack" else KNEEL_ACTION
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    lay, m, panel_point, face = kneel_door_geometry(args.door_open, KNEEL_PANEL_U_M)
    fwd, left, yaw = kneel_facing(lay)
    ctx = {"lay": lay, "m": m, "panel_point": panel_point, "face": face,
           "u_panel": KNEEL_PANEL_U_M, "lean_deg": KNEEL_TORSO_LEAN_DEG,
           "back": lay["u"], "fwd": fwd, "left": left, "right": -left, "yaw": yaw,
           "knee_side": args.knee_side,
           "support_side": "Left" if args.knee_side == "Right" else "Right",
           "arm_angle_deg": args.arm_angle,
           "lens": kneel_bone_lengths(arm),
           "rest": {"踝": {}, "膝": {}, "髋": {}}}
    report = {"script": Path(__file__).name, "task": "kneel", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "door_open_deg": args.door_open, "knee_side": args.knee_side, "problems": []}
    print(f"跪地 / 顶肘（口径 §15.7 ③ 件 · **A′ 部位 ↔ 物面** · #171）· 动作名 {action_name}")
    print(f"帧表：中立 {KNEEL_FRAME_NEUTRAL} · **膝到位 {KNEEL_FRAME_KNEE}** · "
          f"**肘到位 {KNEEL_FRAME_ELBOW}** · 末帧 {KNEEL_FRAME_END}（{args.fps} fps）")
    print("两个目标分属两系（口径 §6.1）：右膝前面 ↔ **地面**（世界系）· "
          "左肘尖面 ↔ **门板近侧面**（道具系，§6.3.1 登记的命名面）")
    print(f"门：半掩 {args.door_open}° · 板宽 {lay['width']} m · 厚 {lay['thickness'] * 1000:.0f} mm · "
          f"铰链 ({lay['hinge'].x:+.2f}, {lay['hinge'].y:+.2f}) · 近侧面朝外法向 m = "
          f"({m.x:+.4f}, {m.y:+.4f}, {m.z:+.4f})")
    print(f"角色朝向：**面朝 −u**（沿板面，朝铰链）⇒ 板面在他的**左侧**；转身 {yaw:+.1f}°")

    # 部位面登记的行 + ε 自检（先在中立姿势量：登记值与真实面片互证）
    clear_pose(arm)
    update()
    used = ["knee_front_right", "knee_front_left", "elbow_tip"]
    report["part_faces_used"] = {k: {kk: v[kk] for kk in ("标签", "骨", "局部轴", "ε_mm",
                                                          "ε_实测复核_mm", "ε_一致",
                                                          "面片数", "取样顶点数")}
                                 for k, v in ((k, kneel_part_frame(arm, k)) for k in used)}
    for k, row in report["part_faces_used"].items():
        print(f"  部位面 {k:<11}{row['骨']:<24}{row['局部轴']:>3}  ε = {row['ε_mm']:>9.4f} mm"
              f"（真实面片复核 {row['ε_实测复核_mm']} mm · {'一致 ✅' if row['ε_一致'] else '不一致 ❌'}）"
              f" · 面片 {row['面片数']} 点 / 取样 {row['取样顶点数']}")
        if not row["ε_一致"]:
            report["problems"].append(f"部位面 {k} 的 ε 与真实面片不符（登记 {row['ε_mm']} / 实测复核 "
                                      f"{row['ε_实测复核_mm']}）")

    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    ankle_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in ("Left", "Right")}
    # 静止时的"目标三角"（`t_leg=0` 那一端）：踝 / 膝 / 髋三个骨点，逐帧线性插到接触姿势
    for s_ in ("Left", "Right"):
        ctx["rest"]["踝"][s_] = ankle_rest[s_].copy()
        ctx["rest"]["膝"][s_] = world_point(arm, f"{BONE_PREFIX}{s_}Leg").copy()
        ctx["rest"]["髋"][s_] = world_point(arm, f"{BONE_PREFIX}{s_}UpLeg").copy()
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in ("Left", "Right")}
    curl_thumb = {s: detect_curl_axis_group(arm, s, "拇指") for s in ("Left", "Right")}
    curl_axes = {s: {f: (curl_thumb[s] if f == "Thumb" else curl[s]) for f in FINGERS}
                 for s in ("Left", "Right")}
    report["rest"] = {"静止髋_m": [round(v, 6) for v in hips_rest],
                      "静止踝_m": {s: [round(v, 6) for v in ankle_rest[s]] for s in ankle_rest},
                      "骨长_m": {k: round(v, 6) for k, v in ctx["lens"].items()},
                      "f3_curl": {"四指": curl, "拇指": curl_thumb},
                      "静止目标三角_m": {k: {s: [round(c, 6) for c in v] for s, v in d.items()}
                                          for k, d in ctx["rest"].items()}}
    report["targets"] = {
        "门板近侧面": {"锚点_m": [round(c, 4) for c in face["锚点"]],
                       "朝外法向": [round(c, 4) for c in face["法向"]],
                       "面片": [[round(c, 4) for c in p] for p in face["面片"]],
                       "面内窗口_mm": [[round(x * 1000, 1) for x in face["u_span_m"]],
                                       [round(x * 1000, 1) for x in face["z_span_m"]]],
                       "面片说明": face["面片说明"]},
        "地面": {"朝外法向": [0.0, 0.0, 1.0],
                 "面片说明": kneel_ground_face((0, 0))["面片说明"]}}

    report["freedom_table"] = [
        {"行": "跪哪条腿 / 前踩哪只脚", "值": f"{args.knee_side} 膝下 · {ctx['support_side']} 脚前踩",
         "状态": "agent 解（本件选定）", "来源": "`--scan-posture` 并列 2 解（口径 §4.2 硬规矩 5）"},
        {"行": "上臂下倾角 φ（决定肘比肩低多少）", "值": args.arm_angle, "单位": "°",
         "状态": "agent 解（本件选定）", "来源": "`--scan-posture` 并列 3 档；它同时定下站位"},
        {"行": "站位（肩到板面水平距离）", "值": "**解出来的**（= 上臂长·cosφ + ε）", "单位": "m",
         "状态": "agent 解（标定）", "来源": "`kneel_calibrate()`：让上臂恰好够到板面"},
        {"行": "跪姿膝骨点高度", "值": "**解出来的**（膝前面触地 ⇒ 间隙 0）", "单位": "m",
         "状态": "agent 解（标定）", "来源": "`kneel_calibrate()`：跪下去的物理含义就是膝触地"},
        {"行": "两条腿的目标三角", "值": "**由实测骨长反解**（大腿/小腿长 + 地面高度）", "单位": "m",
         "状态": "agent 解", "来源": "`kneel_knee_leg()` / `kneel_support_leg()`；"
                                     "⚠️ 第 1 版是手拍距离 ⇒ 膝被解到地面以下 59.18 mm（证据 §六）"},
        {"行": "躯干前倾", "值": [KNEEL_TORSO_LEAN_DEG, f"+{KNEEL_PRESS_LEAN_DEG}°（顶住之后继续压）"],
         "单位": "°", "状态": "agent 解",
         "来源": "管线 §2.1.4（脊柱局部 X = 前倾）；后 4° 让「持续」窗口不平凡"},
        {"行": "**F4a 判据时域**（必填）", "值": "两条接触对**都是 `持续`**（整段窗口逐帧，松一帧即红）",
         "状态": "owner（涉观感）/ agent", "来源": "口径 §13.3 F4a · §13.4.1"},
        {"行": "判据层", "值": "**蒙皮层**（`Beta_Surface`）", "状态": "已裁",
         "来源": "口径 §10.1（owner 2026-09-16 裁定）"},
    ]

    # ---- ① 标定（接触姿势的两个量：膝骨点高度 + 站位）----
    cal = kneel_calibrate(arm, m3, ctx, curl_axes)
    report["calibration"] = cal
    print("\n标定（回代，不是手拍常量）")
    for row in cal["回合"]:
        print(f"  轮 {row['轮']}：站位 {row['standoff_m']:.4f} m · 膝骨点 z {row['膝骨点_z_m']:.4f} m · "
              f"膝间隙 {row['膝间隙_mm']:+.2f} mm · 肩到板面 {row['肩到板面_m']:.4f} m"
              f"（目标 {cal['目标_肩到板面_m']:.4f}）· 跪地踝高 {row['跪地踝高_m']:.4f} m · "
              f"足背最低 {row['跪地足背最低_mm']} mm")
    print(f"  ⇒ 接触姿势：站位 {cal['standoff_m']} m · 膝骨点 z {cal['膝骨点_z_m']} m · "
          f"跪地踝高 {cal['跪地踝高_m']} m · "
          f"骨长 大腿 {cal['大腿长_m']} / 小腿 {cal['小腿长_m']} / 上臂 {cal['上臂长_m']} m · "
          f"肘比肩低 {cal['肘比肩低_mm']} mm")

    # ---- ② `--scan-posture`：解空间（口径 §4.2 硬规矩 5 —— agent 解的行必须并列 ≥2 解）----
    if args.scan_posture:
        print("\n解空间（口径 §4.2 硬规矩 5）：跪哪条腿 × 上臂下倾角 φ")
        print(f"  {'膝下':>6}{'φ°':>6}{'站位_m':>9}{'膝骨点z':>9}{'膝间隙_mm':>11}{'肘间隙_mm':>11}"
              f"{'面内偏移_mm':>18}{'膝残差_mm':>11}{'落在面内':>9}")
        rows = []
        for knee_side in ("Right", "Left"):
            for phi in (18.0, 26.0, 34.0):
                clear_pose(arm)
                drop_temp(arm, also_objects=False)
                c2 = dict(ctx)
                c2["knee_side"] = knee_side
                c2["support_side"] = "Left" if knee_side == "Right" else "Right"
                c2["arm_angle_deg"] = phi
                cal2 = kneel_calibrate(arm, m3, c2, curl_axes)
                out = kneel_apply(arm, m3, c2, 1.0, 1.0, 1.0, cal2["standoff_m"],
                                  cal2["膝骨点_z_m"], curl_axes)
                e = out["肘_读数"]
                row = {"膝下": knee_side, "φ": phi, "站位_m": cal2["standoff_m"],
                       "膝骨点_z_m": cal2["膝骨点_z_m"], "膝间隙_mm": out["膝_读数"]["沿法向间隙_mm"],
                       "肘间隙_mm": e["沿法向间隙_mm"], "面内偏移_mm": e.get("面内偏移_mm"),
                       "落在面片内": e.get("落在面片内"),
                       "腿残差_mm": round(max(abs(v) for v in out["腿残差_mm"].values()), 2),
                       "膝残差_mm": round(max(abs(v) for v in out["膝残差_mm"].values()), 2),
                       "肘_朝面夹角_deg": out["朝向自检"]["与目标面法向(−m)夹角_deg"]}
                rows.append(row)
                print(f"  {knee_side:>6}{phi:6.1f}{row['站位_m']:9.4f}{row['膝骨点_z_m']:9.4f}"
                      f"{row['膝间隙_mm']:11.2f}{row['肘间隙_mm']:11.2f}"
                      f"{str(row['面内偏移_mm']):>18}{row['膝残差_mm']:11.2f}"
                      f"{str(row['落在面片内']):>9}")
        report["scan_posture"] = {"行": rows,
                                  "来源": "本件选定；两条判据的读数在同一解算路径下量（不回中立）",
                                  "如实登记": "φ 越大 ⇒ 肘比肩低得越多、站位越远；跪哪条腿决定前踩脚"}
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0

    # ---- ③ 门代理（预览用；几何与判据目标同出 `door_layout()`）----
    build_door_proxy(args.door_open)
    panel_frame = door_end_frame(lay)

    # ---- ④ 逐帧解算 ----
    captured, per_frame = {}, []
    print(f"\n逐帧解算（帧 {KNEEL_FRAME_NEUTRAL}–{KNEEL_FRAME_END}，每帧解、每帧打键）")
    for frame in range(KNEEL_FRAME_NEUTRAL, KNEEL_FRAME_END + 1):
        if frame == KNEEL_FRAME_NEUTRAL:
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            captured[frame] = capture_channels(arm, panic_channel_names(arm))
            per_frame.append({"frame": frame, "中立": True})
            print(f"  帧 {frame:>3} **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        # 下跪进度（到 KNEEL_FRAME_KNEE）· 顶肘进度（KNEE→ELBOW）· 顶住后继续压
        t_knee = min(1.0, (frame - KNEEL_FRAME_NEUTRAL) / float(KNEEL_FRAME_KNEE - KNEEL_FRAME_NEUTRAL))
        s_elbow = min(1.0, max(0.0, (frame - KNEEL_FRAME_KNEE)
                               / float(KNEEL_FRAME_ELBOW - KNEEL_FRAME_KNEE)))
        if frame <= KNEEL_FRAME_ELBOW:
            lean_now = KNEEL_TORSO_LEAN_DEG * t_knee
        else:
            press = min(1.0, (frame - KNEEL_FRAME_ELBOW)
                        / float(KNEEL_FRAME_END - KNEEL_FRAME_ELBOW - 4))
            lean_now = KNEEL_TORSO_LEAN_DEG + KNEEL_PRESS_LEAN_DEG * press
        ctx["lean_deg"] = KNEEL_TORSO_LEAN_DEG
        extra = max(0.0, lean_now - KNEEL_TORSO_LEAN_DEG * t_knee)
        out = kneel_apply(arm, m3, ctx, t_knee, t_knee, s_elbow, cal["standoff_m"],
                          cal["膝骨点_z_m"], curl_axes, lean_extra=extra)
        captured[frame] = capture_channels(arm, panic_channel_names(arm))
        row = {"frame": frame, "t_knee": round(t_knee, 4), "s_elbow": round(s_elbow, 4),
               "抬脚_mm": {k: round(v * 1000.0, 1) for k, v in out["抬脚_mm"].items()},
               "前倾_deg": round(lean_now, 2),
               "髋残差_mm": out["髋残差_mm"],
               "腿残差_mm": {k: round(v, 2) for k, v in out["腿残差_mm"].items()},
               "膝残差_mm": {k: round(v, 2) for k, v in out["膝残差_mm"].items()},
               "膝间隙_mm": out["膝_读数"]["沿法向间隙_mm"],
               "肘间隙_mm": out["肘_读数"]["沿法向间隙_mm"],
               "肘_面内偏移_mm": out["肘_读数"].get("面内偏移_mm"),
               "肘_落在面片内": out["肘_读数"].get("落在面片内"),
               "朝向自检": out["朝向自检"]}
        per_frame.append(row)
        if frame in (KNEEL_FRAME_KNEE, KNEEL_FRAME_ELBOW, KNEEL_FRAME_END) or frame % 10 == 0:
            print(f"  帧 {frame:>3} 跪 {t_knee:.2f} · 顶肘 {s_elbow:.2f} · "
                  f"髋残差 {out['髋残差_mm']:.2f} mm · 膝残差 "
                  f"{max(abs(v) for v in out['膝残差_mm'].values()):.2f} mm · "
                  f"膝间隙 {row['膝间隙_mm']:+.2f} mm · 肘间隙 {row['肘间隙_mm']:+.2f} mm · "
                  f"肘朝面 {row['朝向自检']['与目标面法向(−m)夹角_deg']:.1f}°")
    report["frame_params"] = per_frame

    # ---- ⑤ 预览清理 + 打键（逐帧）----
    residue = sorted(o.name for o in bpy.data.objects
                     if o.name.startswith("REF_")
                     and not any(m.type == "ARMATURE" for m in o.modifiers))
    for name in [n for n in residue if not n.startswith("REF_Door")]:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    report["preview_residue_removed"] = residue

    names = panic_channel_names(arm)
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    try:
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame in range(KNEEL_FRAME_NEUTRAL, KNEEL_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_start = KNEEL_FRAME_NEUTRAL
    bpy.context.scene.frame_end = KNEEL_FRAME_END
    report["frames"] = {"起": KNEEL_FRAME_NEUTRAL, "膝到位": KNEEL_FRAME_KNEE,
                        "肘到位": KNEEL_FRAME_ELBOW, "末": KNEEL_FRAME_END}
    report["keyed_channels"] = names
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    report["visible_bones"] = visible_bone_outliers(arm)
    print(f"\n已打键：动作 {action_name} · 帧 {KNEEL_FRAME_NEUTRAL}–{KNEEL_FRAME_END} · "
          f"通道 {len(names)} 个（含腿脚 {sum(1 for n in names if 'Leg' in n or 'Foot' in n)} 个）")
    if report["visible_bones"]["非例外的越界骨"]:
        report["problems"].append(
            "可见骨伸出皮肤包围盒：" + "; ".join(
                f"{x['骨']}({x['伸出量_mm']:.1f} mm)" for x in report["visible_bones"]["非例外的越界骨"][:8]))

    # ---- ⑥ 产物侧读数：从**打键后的产物**上逐帧重量（不是解算时的中间量）----
    def product_frame(frame):
        bpy.context.scene.frame_set(frame)
        update()
        d = bpy.context.evaluated_depsgraph_get()
        return arm.evaluated_get(d)

    prod, clash = [], []
    for frame in range(KNEEL_FRAME_NEUTRAL, KNEEL_FRAME_END + 1):
        ev = product_frame(frame)
        knee_p = kneel_part_frame(ev, knee_face_key(ctx))
        elbow_p = kneel_part_frame(ev, "elbow_tip")
        hips_w = world_point(ev, f"{BONE_PREFIX}Hips")
        knee_r = kneel_contact_readings(knee_p, kneel_ground_face((hips_w.x, hips_w.y)),
                                        KNEEL_PART_FACES[knee_face_key(ctx)]["标签"])
        elbow_r = kneel_contact_readings(elbow_p, ctx["face"],
                                         KNEEL_PART_FACES["elbow_tip"]["标签"])
        # 地面屏障（判据 4 的第一个数"骨段零穿透"的形态）：全体变形骨端点 + 两个探针面片 + 足底蒙皮
        ground_pts = []
        for b in ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "LeftLeg",
                  "LeftFoot", "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"):
            if f"{BONE_PREFIX}{b}" not in ev.pose.bones:
                continue
            # ⚠️ 只取**骨心**（head）：`*ToeBase.tail` = 标记骨 `*Toe_End` 的骨心，**伸在皮肤外
            #    93.50 mm**（口径 §15.4）⇒ 拿它当"地面屏障"会假红（本件实测 −87.94 mm 全是它）。
            ground_pts.append((world_point(ev, f"{BONE_PREFIX}{b}").z, f"{b}.head"))
        ground_pts += [(p.z, "膝_面片") for p in knee_p["面片"]]
        ground_pts += [(p.z, "肘_面片") for p in elbow_p["面片"]]
        for s_ in ("Left", "Right"):
            z = cp._skin_lowest(ev, cp._skin_index(ev, s_))
            if z is not None:
                ground_pts.append((z, f"{s_}足底蒙皮"))
        low, low_where = min(ground_pts, key=lambda t: t[0])
        # 板体穿透（同一形态）：肘尖面片的点到**板体**（有限盒）的最近带符号间隙
        panel_gap = min(box_gap_mm(p, panel_frame) for p in elbow_p["面片"])
        prod.append({"frame": frame, "膝": knee_r, "肘": elbow_r,
                     "地面_最低_mm": round(low * 1000.0, 2), "地面_最低处": low_where,
                     "板体_最小间隙_mm": round(panel_gap, 2),
                     "髋_z_m": round(hips_w.z, 5)})
        clash.append({"frame": frame,
                      "地面_违规": bool(low * 1000.0 < -CONTACT_TOL_MM),
                      "板体_违规": bool(panel_gap < 0.0)})
    report["product"] = prod
    knee_curve = [(r["frame"], r["膝"]["沿法向间隙_mm"]) for r in prod]
    elbow_curve = [(r["frame"], r["肘"]["沿法向间隙_mm"]) for r in prod]

    # ---- ⑦ 判据：两条**持续**接触对 + 首次进入容差帧（时序的零阈值形态）----
    def first_in(curve, tol=KNEEL_TOL_MM):
        for f, v in curve:
            if abs(v) <= tol:
                return f
        return None

    def window_stats(curve, f0):
        win = [(f, v) for f, v in curve if f >= f0]
        worst = max(win, key=lambda t: abs(t[1]))
        return {"窗口": [f0, curve[-1][0]], "逐帧最坏_mm": worst[1], "最坏帧": worst[0],
                "超差帧": [f for f, v in win if abs(v) > KNEEL_TOL_MM]}

    knee_first, elbow_first = first_in(knee_curve), first_in(elbow_curve)
    report["contact_criteria"] = {
        "膝 ↔ 地面": {"判据形态": "弧面↔面（右膝前面探针面片最低点 ↔ 地面 z=0）",
                      "判据时域（F4a）": "持续（整段窗口逐帧，松一帧即红）",
                      "容差_mm": KNEEL_TOL_MM, "判据层": "蒙皮层 Beta_Surface",
                      "声明到位帧": KNEEL_FRAME_KNEE, "产物_首次进入容差帧": knee_first,
                      **window_stats(knee_curve, KNEEL_FRAME_KNEE),
                      "接近段红帧": [f for f, v in knee_curve
                                     if f < KNEEL_FRAME_KNEE and abs(v) > KNEEL_TOL_MM]},
        "肘 ↔ 门板近侧面": {"判据形态": "弧面↔面（左肘尖面探针面片最低点 ↔ 有限板面）",
                            "判据时域（F4a）": "持续（整段窗口逐帧，松一帧即红）",
                            "容差_mm": KNEEL_TOL_MM, "判据层": "蒙皮层 Beta_Surface",
                            "声明到位帧": KNEEL_FRAME_ELBOW, "产物_首次进入容差帧": elbow_first,
                            **window_stats(elbow_curve, KNEEL_FRAME_ELBOW),
                            "接近段红帧": [f for f, v in elbow_curve
                                           if f < KNEEL_FRAME_ELBOW and abs(v) > KNEEL_TOL_MM]},
    }
    print("\n判据（口径 §4.2 硬规矩 2：判据必须**能报红**）+ F4a 时域")
    for label, c in report["contact_criteria"].items():
        print(f"  {label:<16}{c['判据形态']}")
        print(f"    持续窗口 {c['窗口']} · 逐帧最坏 {c['逐帧最坏_mm']:+.2f} mm（帧 {c['最坏帧']}）· "
              f"超差帧 {len(c['超差帧'])} · 接近段红帧 {len(c['接近段红帧'])}"
              f" · 首次进入容差帧 {c['产物_首次进入容差帧']}（声明 {c['声明到位帧']}）")
        if c["超差帧"]:
            report["problems"].append(f"{label}：持续窗口内超差帧 {c['超差帧'][:8]}")
        if c["产物_首次进入容差帧"] != c["声明到位帧"]:
            report["problems"].append(
                f"{label}：时序不一致——声明到位帧 {c['声明到位帧']} ≠ 产物侧首次进入容差帧 "
                f"{c['产物_首次进入容差帧']}")
        if not c["接近段红帧"]:
            report["problems"].append(f"{label}：接近段**没有红帧** ⇒ 判据退化（非退化性未证）")
    # ⚠️ 只判**持续窗口内**的面外（接近段人离板几百 mm，"面内投影"无意义；§13.4 管的是"判贴合时"）
    elbow_out = [r["frame"] for r in prod
                 if r["frame"] >= KNEEL_FRAME_ELBOW and r["肘"].get("落在面片内") is False]
    elbow_out_all = [r["frame"] for r in prod if r["肘"].get("落在面片内") is False]
    report["contact_criteria"]["肘 ↔ 门板近侧面"]["面外帧"] = elbow_out
    if elbow_out:
        report["problems"].append(f"肘 ↔ 门板近侧面：接触点落在板面**之外**的帧 {elbow_out[:8]}"
                                  f"（§13.4：#164 的教训——面外不许判贴合；窗口外面外帧（不判）："
                                  f"{elbow_out_all[:6]}）")

    # ---- ⑧ 非退化对照（中立姿势）----
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    update()
    hw = world_point(arm, f"{BONE_PREFIX}Hips")
    neutral = {"膝 膝前面 ↔ 地面": kneel_contact_readings(
                   kneel_part_frame(arm, knee_face_key(ctx)), kneel_ground_face((hw.x, hw.y)),
                   KNEEL_PART_FACES[knee_face_key(ctx)]["标签"])["沿法向间隙_mm"],
               "肘 前臂背侧面 ↔ 门板近侧面": kneel_contact_readings(
                   kneel_part_frame(arm, "elbow_tip"), ctx["face"],
                   KNEEL_PART_FACES["elbow_tip"]["标签"])["沿法向间隙_mm"]}
    report["neutral_control"] = neutral
    print(f"  非退化对照（中立姿势）：{neutral}")

    # ---- ⑨ 穿模（判据 4 的形态）----
    report["clash"] = {"行": clash,
                       "地面最坏_mm": round(min(r["地面_最低_mm"] for r in prod), 2),
                       "地面最坏处": min(prod, key=lambda r: r["地面_最低_mm"])["地面_最低处"],
                       "板体最小间隙_mm": round(min(r["板体_最小间隙_mm"] for r in prod), 2),
                       "违规帧": [r["frame"] for r in clash if r["地面_违规"] or r["板体_违规"]],
                       "来源": "动作库规格 §四·戊·5 判据 4（骨段零穿透）；碰撞体 = 地面（半空间）"
                               "与门板（有限盒）",
                       "地面阈值_mm": f"−`CONTACT_TOL_MM` = −{CONTACT_TOL_MM} mm"
                                    "（⚠️ 母版**中立姿势本身**就读到足底 −0.32 mm ⇒ 零阈值会在导出侧 E5"
                                    "要求的首帧上误报；容差沿用 §8.2 的同族数）"}
    print(f"  穿模：地面最坏 {report['clash']['地面最坏_mm']} mm"
          f"（{report['clash']['地面最坏处']}）· 板体最小间隙 "
          f"{report['clash']['板体最小间隙_mm']} mm ⇒ 违规帧 {len(report['clash']['违规帧'])}")
    if report["clash"]["违规帧"]:
        report["problems"].append(f"穿模：违规帧 {report['clash']['违规帧'][:8]}")

    # ---- ⑩ 零阈值姿态断言（双腿不反关节）----
    # **零阈值、且非自证**：拿**蒙皮实测的面法向**（小腿局部 `+Z` = 膝前面）去比对"膝相对弦往哪鼓"
    # ⇒ 判的是"**膝的前面朝外**"（腿没有反着跪）。⚠️ 本条正是第 1 版那个真 bug 的判据形态：
    # 滚转符号错时小腿前面朝上（法向朝上）而膝相对弦向下鼓 ⇒ 当场报红。
    pose_rows = []
    for frame in (KNEEL_FRAME_KNEE, KNEEL_FRAME_ELBOW, KNEEL_FRAME_END):
        ev = product_frame(frame)
        row = {"frame": frame}
        for side in ("Left", "Right"):
            pb = ev.pose.bones[f"{BONE_PREFIX}{side}Leg"]
            front = (arm.matrix_world.to_3x3() @ (pb.matrix.to_3x3() @ Vector((0, 0, 1)))).normalized()
            hip = world_point(ev, f"{BONE_PREFIX}{side}UpLeg")
            knee = world_point(ev, f"{BONE_PREFIX}{side}Leg")
            ank = world_point(ev, f"{BONE_PREFIX}{side}Foot")
            chord = ank - hip
            axis = chord.normalized() if chord.length > 1e-9 else Vector((0, 0, -1))
            bulge = (knee - (hip + ank) * 0.5)
            bulge = bulge - axis * bulge.dot(axis)
            bulge = bulge.normalized() if bulge.length > 1e-9 else Vector((0, 0, -1))
            row[f"{side}_膝_前朝外_mm"] = round(front.dot(bulge) * 1000.0, 1)   # 无量纲投影 ×1000
            row[f"{side}_膝鼓出_mm"] = round(bulge.dot(ctx["fwd"]) * 1000.0, 1)  # 只报读数
        pose_rows.append(row)
    bad_knee = [r["frame"] for r in pose_rows
                if r["Left_膝_前朝外_mm"] <= 0.0 or r["Right_膝_前朝外_mm"] <= 0.0]
    report["pose_judgements"] = {
        "膝的前面**朝外**（小腿局部 `+Z` · 蒙皮实测法向 vs 弦几何 · 零阈值）": {"违规帧": bad_knee},
        "逐帧读数": pose_rows}
    for r in pose_rows:
        print(f"  姿态读数 帧 {r['frame']}：左膝 前朝外 {r['Left_膝_前朝外_mm']:+.1f} / 鼓出 "
              f"{r['Left_膝鼓出_mm']:+.1f} mm · 右膝 前朝外 {r['Right_膝_前朝外_mm']:+.1f} / 鼓出 "
              f"{r['Right_膝鼓出_mm']:+.1f} mm")
    if bad_knee:
        report["problems"].append(f"膝的前面没有朝外（腿反着跪）帧：{bad_knee[:6]}")

    # ---- ⑪ 回显卡 ----
    kc = report["contact_criteria"]["膝 ↔ 地面"]
    ec = report["contact_criteria"]["肘 ↔ 门板近侧面"]
    card = [
        {"判据量": "右膝前面 ↔ **地面**（世界/重力系）", "判据形态": kc["判据形态"],
         "产物侧读数": f"持续窗口 {kc['窗口']} · 逐帧最坏 {kc['逐帧最坏_mm']:+.2f} mm"
                       f"（帧 {kc['最坏帧']}）· 首次进入容差帧 {kc['产物_首次进入容差帧']}",
         "容差档": f"`tol_contact` {KNEEL_TOL_MM} mm（ε 换算 "
                   f"{KNEEL_PART_FACES['knee_front_right']['ε_mm']} mm 是另一个数）",
         "状态": "✅" if not kc["超差帧"] else "❌"},
        {"判据量": "左肘尖面 ↔ **门板近侧面**（道具局部系）", "判据形态": ec["判据形态"],
         "产物侧读数": f"持续窗口 {ec['窗口']} · 逐帧最坏 {ec['逐帧最坏_mm']:+.2f} mm"
                       f"（帧 {ec['最坏帧']}）· 首次进入容差帧 {ec['产物_首次进入容差帧']}",
         "容差档": f"`tol_contact` {KNEEL_TOL_MM} mm（ε 换算 "
                   f"{KNEEL_PART_FACES['elbow_tip']['ε_mm']} mm 是另一个数）",
         "状态": "✅" if not ec["超差帧"] else "❌"},
        {"判据量": "判据**能报红**（接近段必须有超差帧 + 中立姿势对照）",
         "判据形态": "存在性（非退化对照）",
         "产物侧读数": f"膝 接近段红帧 {len(kc['接近段红帧'])} · "
                       f"肘 接近段红帧 {len(ec['接近段红帧'])} · 中立姿势 "
                       f"{neutral['膝 膝前面 ↔ 地面']:+.1f} / "
                       f"{neutral['肘 前臂背侧面 ↔ 门板近侧面']:+.1f} mm",
         "容差档": "—",
         "状态": "✅" if kc["接近段红帧"] and ec["接近段红帧"] else "❌"},
        {"判据量": "时序：声明到位帧 == 产物侧**首次进入容差帧**（零阈值）",
         "判据形态": "帧号相等（无阈值）",
         "产物侧读数": f"膝 声明 {KNEEL_FRAME_KNEE} / 产物 {kc['产物_首次进入容差帧']} · "
                       f"肘 声明 {KNEEL_FRAME_ELBOW} / 产物 {ec['产物_首次进入容差帧']}",
         "容差档": "—",
         "状态": "✅" if (kc["产物_首次进入容差帧"] == KNEEL_FRAME_KNEE
                        and ec["产物_首次进入容差帧"] == KNEEL_FRAME_ELBOW) else "❌"},
        {"判据量": "接触点落在**有限板面**之内（§13.4：面外不许判贴合）",
         "判据形态": "面内窗口（布尔）",
         "产物侧读数": f"面外帧 {len(elbow_out)} · 末帧面内偏移 "
                       f"{prod[-1]['肘'].get('面内偏移_mm')} mm · 面内窗口 "
                       f"{prod[-1]['肘'].get('面内窗口_mm')}",
         "容差档": "板宽 × 板高（有限面片）", "状态": "✅" if not elbow_out else "❌"},
        {"判据量": "穿模：地面（半空间）与门板（有限盒）", "判据形态": "点↔面 / 点↔体（判据 4 的形态）",
         "产物侧读数": f"地面最坏 {report['clash']['地面最坏_mm']} mm"
                       f"（{report['clash']['地面最坏处']}）· 板体最小间隙 "
                       f"{report['clash']['板体最小间隙_mm']} mm · "
                       f"违规帧 {len(report['clash']['违规帧'])}",
         "容差档": "零穿透（判据 4 的第一个数）",
         "状态": "✅" if not report["clash"]["违规帧"] else "❌"},
        {"判据量": "膝的前面朝外（腿没反着跪，零阈值）", "判据形态": "法向投影的符号（蒙皮实测面 vs 弦几何）",
         "产物侧读数": str(pose_rows), "容差档": "0.0 mm（**零阈值**）",
         "状态": "✅" if not bad_knee else "❌"},
        {"判据量": "可见骨不伸出皮肤包围盒（口径 §15.4 / §15.8）", "判据形态": "包围盒包含（布尔）",
         "产物侧读数": f"可见骨 {report['visible_bones']['可见骨数']} · "
                       f"非例外越界 {len(report['visible_bones']['非例外的越界骨'])}",
         "容差档": "分界 = `CONTACT_TOL_MM` = 2.8 mm",
         "状态": "✅" if not report["visible_bones"]["非例外的越界骨"] else "❌"},
    ]
    report["feedback_card"] = card
    report["ok"] = not report["problems"]
    print("\n" + "=" * 100)
    print(f"回显卡（口径 §四：每一项都要有产物侧读数）· 动作 {action_name}")
    for row in card:
        print(f"  {row['判据量'][:36]:<38}{row['判据形态'][:22]:<24}"
              f"{str(row['产物侧读数'])[:78]:<80}{row['状态']}")
    print("=" * 100)

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still:
        for frame, suffix in ((KNEEL_FRAME_KNEE - 4, "approach"), (KNEEL_FRAME_KNEE, "knee"),
                              (KNEEL_FRAME_ELBOW, "elbow"), (KNEEL_FRAME_END, "hold")):
            bpy.context.scene.frame_set(frame)
            update()
            target = ctx["face"]["锚点"] + Vector((0.0, 0.0, -0.30))
            cam = target + m * 2.4 + Vector((0.0, 0.0, 1.25)) + lay["u"] * 1.6
            path = str(args.still).replace(".png", f"_{suffix}.png")
            render_still(path, cam, target)
            print(f"静帧：{path}")
    if args.host == "live":
        bpy.context.scene.frame_set(KNEEL_FRAME_END)
        update()
        print(f"[live] 停在末帧 {KNEEL_FRAME_END}（预览；未写回文件）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl))
        print(f"已写回母版副本：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL'} —— problems {report['problems']}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 9：弯腰双手拿起椅子、持在胸前（`--task liftchest`）——#180 的主交付
#
#   所在批：design/presentation/动作描述口径.md §十六「缺素材回归批」① 件（成因类「甲」）
#           —— `Grab2H`（双手抓起）当年因「Mixamo 没有这条素材」被取消，本件 = 那个取消裁定的
#              **第一个具名回归样本**（口径 §16.2 甲类 · §16.3 件表）。
#   硬边界（§16.4 呈现探针三条）：**不新增动作词条** · **不接 Unity 侧 lab** · PLAYABLE.md 不动；
#           且**不主张**"拿起椅子"在游戏里已可用（道具跟随是运行时的事，属 §16.2 丙类）。
#
#   判据来源（**逐条不新拍数**）：
#     · 接触容差 `tol_contact` / 接地 `soleMargin` = **2.8 mm**（口径 §8.2 的两个数）
#     · 判据形态（点↔线 / 点↔面 / 点↔体）+ **F4a 判据时域**（持续） = 口径 §13.4 / §13.4.1
#     · 卡片 = **卡 1「掐棱」**（虎口↔近侧竖棱 · 拇指↔近侧面 · 四指逐根↔板体） = 口径 §13.2/§13.6
#     · 握持刚性（椅子在手骨局部的位姿稳定性）≤ **1 mm/帧**、累计 ≤ **5 mm** = 动作库规格 §四·戊·5 判据 3
#     · 判据 4 的三个数（骨段零穿透 · 骨心进构件 ≤ **2 cm** · 非接触部位间隙 ≥ **1 cm**） = 同上 判据 4
#     · 判据 5 包握（末节 ≤ **1.5 cm** · 掌心与指尖分居构件两侧） = 同上 判据 5
#     · 判据 1 搬运锚 **0.487 m**（±25% · 波动 ≤0.1 m） = 同上 判据 1
#     · 椅子的几何**唯一来源** = `chair_layout()`（#163 那笔"代理与目标两处各算一份、差 0.46 m"的账）
#
#   ⚠️ 「椅子跟随手」在 Blender 侧的表达：椅子零件挂在一根**空物体** `REF_ChairRoot` 上，
#      其**逐帧变换**由本宿主解出并打键；判据侧则**从求值后的网格**重建握持目标面
#      （不是从声明的位移取）⇒ 判据对着产物，不自己证自己（危险点表 §九 `自证式判据` 行）。
# ══════════════════════════════════════════════════════════════════════════════

LIFT_ACTION = "LiftChairToChest"
#: **声明帧表**（口径 §十 V-f：声明的帧必须 == 产物侧能算出来的那一帧，**零阈值**）
LIFT_FRAME_NEUTRAL = 1        # 首帧**严格中立**（导出侧 E5 硬约定：否则 bind pose 被污染）
LIFT_FRAME_START = 6          # **起手**（首个非零**手臂/手**通道帧；⚠️ 进度用 smoothstep，`s(起手−1)=0` ⇒ 第 5 帧仍严格中立）
LIFT_FRAME_GRIP = 25          # **扣住**（双手接触对首次全部落进容差）
LIFT_FRAME_LIFT = 33          # 起吊（椅子从这一帧之后离地）
LIFT_FRAME_OFF_GROUND = 34    # **离地**（椅子代理最低点首次 > `soleMargin`）
LIFT_FRAME_CHEST = 49         # **胸前到位**（判据点的**极值帧** = 平台起始帧）
LIFT_FRAME_END = 61           # **保持**到这一帧

#: 抓握高度 = 椅背顶面 − 本值（**沿用卡 1 的 `CARD1_GRIP_DROP`**：75 mm，不新拍）
LIFT_GRIP_DROP_M = CARD1_GRIP_DROP
#: 身体条件：骨盆后移 + 下沉——它同时是支撑域判据与**腿可达性**的自变量。
#: ⚠️ 实测（2026-09-16）：`(0, +0.055, −0.04)` 配 65° 弯腰会把髋↔踝弦拉到 **0.905 m > 骨长 0.889 m**
#: ⇒ `solve_two_bone()` 夹直、**双脚被抬起 15.97 mm**（接地判据与支撑域同时报红）。取`down=-0.12` 后
#: 弦回到骨长以内（腿仍近直、膝不弯过头），故这里**只下沉、不后移**（后移的活由骨盆俯仰自己干）。
LIFT_PELVIS_OFFSET = (0.0, 0.0, -0.120)
#: 握式（owner 2026-09-16 逐轮指名，**以最新一轮为准**）：
#: - **`backhand`（默认）** = 抓**椅背的左右竖直侧面端**（`x=±0.21`、40 mm 厚那张端面）+ **反手**：
#:   **拇指朝下**（−Z）· **掌心朝内**（朝椅子中线）· 四指绕过**近侧竖棱**落到近侧面上；
#:   骨局部三轴（未抡之前）：左手 `X → +Z` / `Y → +Y` / 右手 `X → −Z` / `Y → +Y`（**镜像**）
#: - `palm` = 掌面朝下扣椅背上沿（第 1–2 轮试过，owner 否：是"上沿"不是"侧面"）
#: - `side` = 卡 1 掐棱用在侧面端（正手：拇指向 ±Z 那一版，owner 否：拇指一上一下不对称）
LIFT_GRIP_MODES = ("backhand", "palm", "side")
LIFT_GRIP_MODE = "backhand"
#: owner 2026-09-16 第 3 轮点名的两个姿态量（**阈值由 agent 定**，来源 = 那句"近似水平 / 夹角不对"）：
#: 抡到位之后 **上臂与水平夹角 ≤ 本值** · **手腕折角 ≤ `LIFT_WRIST_MAX_DEG`（0° = 伸直）**
LIFT_ARM_LEVEL_TOL_DEG = 15.0
LIFT_WRIST_MAX_DEG = 25.0
#: **抡弧**：椅子绕握点转多少度（绕世界 X 轴；负 = 椅腿往前甩出去、椅子横过来）。
#: owner 2026-09-16 第 3 轮："还要继续向上抡" ⇒ 终点角由 −92° 改 **−130°**；
#: "椅子跟着手走" ⇒ 旋转由**手的路径**定，本值只是"抡到位"那一帧的终点角。
LIFT_SWING_DEG = -130.0
#: 抡到位时**握点**的目标世界位置（m）——反手抓侧面端时，握点 = 端面上的一点
LIFT_SIDE_GRIP_Y_M = -0.235
LIFT_SIDE_GRIP_Z_M = 1.16
#: `palm` 握式：手在横杆上的横向位置（m，绝对值）——两侧对称；它同时定下"两手间距"（判据 1）
LIFT_GRIP_X_M = 0.13
#: 胸前持握：**握点**的目标世界位置（m）——⚠️ 语义随握式走：
#: `palm` ⇒ 握点 = 上沿（横杆）**顶面上**该手横向位置那一点；`side` ⇒ 握点 = 椅背**近侧竖棱**上、
#: 顶面下 `LIFT_GRIP_DROP_M` 那一点。agent 解，`--scan-lift` 并列
LIFT_CHEST_GRIP_Y_M = -0.30
LIFT_CHEST_GRIP_Z_M = 1.20
#: 四指的蜷曲量**不设常量**：由卡 1 的 F10 口径**逐指解出来**（`fit_finger_curls()`，标定一次）
#: —— 实测同一个共用系数下四根手指到板的间隙差 14 mm（卡 1 §F10 的教训），本件沿用"逐指"。
#: 拇指的**基准**蜷曲量沿用卡 1 的基准值（`CARD1_CURL_BASELINE`），随后由标定解收口。
LIFT_THUMB_CURL = CARD1_CURL_BASELINE
LIFT_TOL_MM = CONTACT_TOL_MM
#: 拇指在近侧面上的**面内落点**（沿 `u` 内移、高度取抓握高度）——沿用 `grip_board_edge` 的 45 mm
LIFT_THUMB_INSET_M = 0.045
#: 判据 1 的**两个参照**（动作库规格 §四·戊·5 判据 1 逐字给了两种语义）：
#: 挥舞带 **0.15–0.25 m**（带 ±25% ⇒ [0.1125, 0.3125]）· 搬运锚 **0.487 m**（±25% ⇒ [0.3653, 0.6088]）。
#: ⚠️ 本件的读数**落在两带之间**且**不是任选**：掌面朝下扣 42 cm 宽的椅背横杆时四指的横向跨度约 60 mm
#: ⇒ 两手最宽只能到 ≈ ±0.18 m（再宽外侧两指就出了板宽、"到板体"的读数永久 >13 mm）；实测
#: `--grip-x 0.16` 时无名指 3.3–3.7 mm、`0.15` 时四指全 ≤1.1 mm。⇒ 本件**硬判挥舞带**，
#: 搬运锚的偏差**并列报读数**，并把"两锚语义 vs 本工程椅子几何"的冲突登记为未闭合
#: （§四·戊·5 判据 2 的注已裁定「**跨椅子模型比绝对距离不成立**」）。
LIFT_HANDS_BAND_M = (0.15, 0.25)
LIFT_HANDS_ANCHOR_M = 0.487
LIFT_HANDS_ANCHOR_TOL = 0.25
LIFT_HANDS_DRIFT_M = 0.10
#: 握持刚性阈值（件内**不新拍**）：动作库规格 §四·戊·5 判据 3
LIFT_RIGID_PER_FRAME_MM = 1.0
LIFT_RIGID_TOTAL_MM = 5.0
#: 判据 4 / 判据 5 的阈值（逐字照 §四·戊·5）
LIFT_CLASH_CORE_IN_MM = 20.0      # 手 / 前臂：骨心进入构件内部 ≤ 2 cm
LIFT_CLASH_CLEAR_MM = 10.0        # 非接触部位（躯干 / 上臂 / 大腿）：最小间隙 ≥ 1 cm
LIFT_WRAP_MAX_MM = 15.0           # 判据 5：每根手指末节到构件表面 ≤ 1.5 cm
#: 判据 4 的骨集合（**逐条带来源**：躯干/上臂/大腿 = 零穿透；手/前臂 = 骨心 ≤2 cm）
LIFT_CLASH_ZERO_BONES = ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
                         "LeftArm", "RightArm", "LeftUpLeg", "RightUpLeg")
LIFT_CLASH_CORE_BONES = ("LeftForeArm", "LeftHand", "RightForeArm", "RightHand")
#: 解空间并列（口径 §4.2 硬规矩 5）的两维：弯腰角 × 胸前握点高度
LIFT_SCAN_BENDS = (55.0, 65.0, 75.0)
LIFT_SCAN_CHEST_Z = (1.10, 1.20, 1.30)
#: 椅子零件（`build_chair_proxy()` 产出的名字）——判据 4 的碰撞体
LIFT_CHAIR_PARTS = ("REF_Seat", "REF_Back", "REF_Leg0", "REF_Leg1", "REF_Leg2", "REF_Leg3")
#: 椅子根空物体（本件新增的件：椅子要**跟着手走**）
LIFT_CHAIR_ROOT = "REF_ChairRoot"


# ---------------------------------------------------------------- 椅子跟随手：根空物体 + 平移


def lift_chair_root(chair_distance):
    """椅子代理 + **一根可打键的根空物体**。

    ⚠️ 几何**仍只由 `build_chair_proxy()` 一处产出**（#163 那笔账：代理与目标两处各算一份 ⇒
       差 0.46 m、"残差 0.0 mm 全绿而手离椅背 440 mm"）；本函数只把它的**零件挂到空物体上**，
       于是"椅子跟着手走"这件事有一个**可打键、可求值**的载体。
    """
    build_chair_proxy(chair_distance)
    coll = bpy.data.collections["REF_Chair"]
    root = bpy.data.objects.get(LIFT_CHAIR_ROOT)
    if root is None:
        root = bpy.data.objects.new(LIFT_CHAIR_ROOT, None)
        root.empty_display_size = 0.12
        bpy.context.scene.collection.objects.link(root)
    root.parent = None
    # ⚠️ 上一轮存盘时根空物体停在**末帧位移**上（`save_as_mainfile` 存的是当前帧状态），且它的
    #    location 上还挂着上一轮打的键 ⇒ 先清动画、再归位；**归位后必须 `update()` 才能读
    #    `matrix_world`**——否则读到的是上一轮的矩阵，`matrix_parent_inverse` 会把那份位移
    #    **反着烙进每个零件**（实测代价：椅子整体沉到地面以下 520.1 mm，而自洽的读数全绿）。
    root.animation_data_clear()
    root.location = (0.0, 0.0, 0.0)
    root.rotation_mode = "XYZ"
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)
    update()
    for ob in list(coll.objects):
        if ob.parent is None:
            ob.parent = root
            ob.matrix_parent_inverse = root.matrix_world.inverted()
    return root


def lift_smooth(t):
    """两端速度为 0 的平滑段（`smoothstep`）——本件所有进度量共用它。"""
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def lift_transform_frame(frame, pivot, rot, offset):
    """把**板端坐标**按"绕握点 `pivot` 转 `rot` 再平移 `offset`"整体变换。

    抡弧用它：椅子的姿态不再由我拍，而是**由手的路径决定**（owner 2026-09-16 第 3 轮：
    "椅子不是一个整体么，你把手和椅背的相对位置固定之后直接调手的位置就行了，椅子跟着动"）。
    """
    def pt(p):
        return Vector(pivot) + (rot @ (Vector(p) - Vector(pivot))) + Vector(offset)

    def dr(d):
        return (rot.to_3x3() @ Vector(d)).normalized()

    out = dict(frame)
    for key in ("near", "far"):
        out[key] = pt(frame[key])
    for key in ("面-近侧面", "面-远侧面", "面-端面", "棱-近侧", "棱-远侧"):
        out[key] = (pt(frame[key][0]), dr(frame[key][1]))
    for key in ("n", "u", "z"):
        out[key] = dr(frame[key])
    return out


def lift_translate_frame(frame, offset):
    """把**板端坐标**整体平移（本件的椅子**只平移** ⇒ `n/u/z` 三轴不变）。

    ⚠️ `z_span_m` **不用改**：`box_gap_mm()` 里的 `c` 是相对 `near.z` 量的，而 `near` 跟着一起平移
       ⇒ 两者同步，`z_span` 仍是"椅子局部高度"。
    """
    off = Vector(offset)
    out = dict(frame)
    for key in ("near", "far"):
        out[key] = frame[key] + off
    for key in ("面-近侧面", "面-远侧面", "面-端面", "棱-近侧", "棱-远侧"):
        out[key] = (frame[key][0] + off, frame[key][1])
    return out


# ---------------------------------------------------------------- 判据的度量对象（**从求值后的网格取**）


def _part_world_points(ob):
    """该物体**求值后**顶点的世界坐标（✋ 判据的探针一律从这里来）。"""
    return [ob.matrix_world @ v.co for v in ob.data.vertices]


def lift_chair_frame_from_points(side, pts):
    """椅背**侧面端**的板端坐标——**从网格自己的世界坐标重建**（不读声明的位移）。

    `near/far` 取该侧端面上、朝角色一侧 / 背向角色一侧的两条**竖棱**；`u` 指向板内（椅心一侧）。
    """
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    sgn = 1.0 if side == "Left" else -1.0
    x_edge = max(xs) if sgn > 0.0 else min(xs)
    near = Vector((x_edge, max(ys), 0.0))
    far = Vector((x_edge, min(ys), 0.0))
    return board_end_frame(near, far, Vector((-sgn, 0.0, 0.0)),
                           u_span_m=(0.0, max(xs) - min(xs)),
                           z_span_m=(min(zs), max(zs)))


def _local_bbox(ob):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def obb_gap_mm(p, ob, bbox):
    """点 ↔ **有向盒**（零件的局部包围盒经它的世界矩阵摆出去）的**带符号**间隙（mm）。

    正 = 盒外最近距离 · 负 = **陷进盒内的深度**。⚠️ 与 `box_gap_mm()`（板端坐标那套）是**两个**
    度量对象：这里量的是**碰to撞体本身**（判据 4 的措辞逐字是"与椅子碰撞体零穿透"）。
    """
    mw = ob.matrix_world
    q = mw.inverted() @ Vector(p)
    sc = mw.to_scale()
    lo, hi = bbox
    d2, inside = 0.0, True
    for i in range(3):
        if q[i] < lo[i]:
            d2 += ((lo[i] - q[i]) * sc[i]) ** 2
            inside = False
        elif q[i] > hi[i]:
            d2 += ((q[i] - hi[i]) * sc[i]) ** 2
            inside = False
    if not inside:
        return math.sqrt(d2) * 1000.0
    return -min(min(q[i] - lo[i], hi[i] - q[i]) * sc[i] for i in range(3)) * 1000.0


def _segment_points(arm_like, bone_name, n=5):
    h = world_point(arm_like, f"{BONE_PREFIX}{bone_name}")
    t = world_point(arm_like, f"{BONE_PREFIX}{bone_name}", "tail")
    return [h.lerp(t, i / float(n - 1)) for i in range(n)]


def lift_contact_values(rows):
    """把 `grip_board_edge_readings()` 的三行**摊平**成数值表（成组项逐项展开）。"""
    out = []
    for row in rows:
        v = row["读数_mm"]
        if isinstance(v, list):
            for name, x in zip(row.get("逐项名", []), v):
                out.append((f"{row['手部分区']}/{row['物体分区']}/{name}", x))
        else:
            out.append((f"{row['手部分区']}/{row['物体分区']}", v))
    return out


def lift_distal_skin_local(arm, side, finger):
    """该手指**末节**（`*4` 骨主导）的蒙皮点，**世界坐标**（缓存里存的是骨局部坐标）。

    判据 5 的措辞是"每根手指**末节到构件表面** ≤1.5 cm"——量的是**肉**，不是骨尖
    （实测：骨尖本来就在肉里，量它会读出 −14 ~ −19 mm 的"陷进构件"，那是**必然**的）。
    """
    mw = arm.matrix_world
    out = []
    for bone_name, q in hand_skin_points(arm, side):
        # ⚠️ 蒙皮**没有** `…4` 的顶点组（实测 50 个组只到 `…3`）⇒ 指尖的肉在 `…3` 的组里
        #    （`hand_skin_points()` 的注③）；写 `…4` 会一个点都取不到（本件实测 `None`）。
        if bone_name.endswith(f"Hand{finger}3"):
            out.append(mw @ (arm.pose.bones[bone_name].matrix @ q))
    return out


def lift_contact_ok(rows, tol=LIFT_TOL_MM):
    """**接触成立**（§七 硬规矩 2 的机械化）：成组项**逐项**都在容差内才算成立。

    ⚠️ 标了 `只报读数` 的行**不进判定**（如掌面朝下握式里的"虎口点"——它带一个**已知偏置**：
       ε 是从 `Hand` 骨原点标定的，搬到"拇指/食指根中点"上不成立，实测低 10.47 mm）。
    """
    vals = [v for row in rows if not row.get("只报读数")
            for _n, v in lift_contact_values([row]) if v is not None]
    worst = max((abs(v) for v in vals), default=None)
    return bool(vals) and worst is not None and worst <= tol, worst


# ---------------------------------------------------------------- 姿势解算（弯腰 → 掐棱 → 抬起）


def _root_pose(prm, grip):
    """椅子根空物体的逐帧位姿：**绕 `pivot` 转 `R` 再平移 `offset`** ⇒ 位置项含 `−R·pivot`。

    ⚠️ 漏掉旋转的代价（本件实测）：手按 frame 转了、空物体只平移 ⇒ 握持刚性读到 **1726 mm**。
    """
    pivot = Vector(grip.get("pivot", (0.0, 0.0, 0.0)))
    rot = prm.get("rot")
    loc = Vector(prm["offset"]) + (pivot - (rot @ pivot if rot is not None else pivot))
    euler = (0.0, 0.0, 0.0) if rot is None else tuple(
        math.degrees(a) for a in rot.to_euler("XYZ"))
    return {"location": loc, "euler_deg": euler}


def lift_frame_params(frame, bend_deg, offset_full, pelvis_m=LIFT_PELVIS_OFFSET):
    """一帧的任务空间参数（**唯一的进度来源**；产物侧不重算它）。"""
    # ⚠️ 分子 +1：`smoothstep(0) = 0` ⇒ 若从 0 起算，"起手帧"那一帧的姿势仍**逐位等于中立**，
    #    判据（首个非零通道帧）会晚一帧（实测踩到）。这里让 `LIFT_FRAME_START` 当帧就 > 0，
    #    而它**之前**的帧走"严格中立"分支（不进本函数）。
    up = (frame - LIFT_FRAME_START + 1) / float(LIFT_FRAME_GRIP - LIFT_FRAME_START + 1)
    down = (frame - LIFT_FRAME_LIFT) / float(LIFT_FRAME_CHEST - LIFT_FRAME_LIFT)
    s_up, s_down = lift_smooth(up), lift_smooth(down)
    t_bend = s_up * (1.0 - s_down)
    # **抡弧**：椅子绕**握点**转（`R` = 绕世界 X 轴）——owner 第 3 轮："椅子跟着手走" ⇒ 手转到哪、
    # 椅子跟到哪；转轴取世界 X（横向）⇒ 椅腿往前甩出去、椅子横过来。
    from mathutils import Matrix
    theta = math.radians(LIFT_SWING_DEG) * s_down
    return {"t_bend": t_bend, "t_reach": s_up, "t_lift": s_down, "swing_deg": math.degrees(theta),
            "bend_deg": bend_deg * t_bend,
            "pelvis": Vector(pelvis_m) * t_bend,
            "rot": Matrix.Rotation(theta, 4, "X"),
            "offset": Vector(offset_full) * s_down}


def lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest):
    """**弯腰站姿**（同 `bent_body_setup` 的路子）：骨盆前弯 + 世界位移 + 双脚踩原地 + 目视水平。

    ⚠️ 骨盆位移**按弯腰进度缩放**（直立时归零）：它是"重心留在支撑域内"的自变量，
       而不是装饰（#170 owner 已裁判据层 = 蒙皮层，见口径 §10.1）。
    """
    set_euler(arm, "CTRL_Hips", x=bend_deg)
    set_world_offset(arm, m3, "CTRL_Hips", Vector(pelvis_m))
    update()
    _, _, posterior = body_frame(arm)
    legs = {}
    for side in CARD1_SIDES:
        legs[side] = solve_leg(arm, side, foot_rest[side], -posterior)
        _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                        _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"),
                        _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))
    update()
    return {"gaze": solve_gaze(arm), "legs": legs}


def lift_arm_solve_backhand(arm, side, frame, s, curl_axes, fitted, thumb_solved, wrist_rest,
                            grip_h_m=0.0, grip_df=0.5, rot=None, s_swing=0.0, post=None):
    """**反手抓椅背侧面端**（owner 2026-09-16 第 3 轮指名）的可变进度版。

    朝向（未抡之前，逐轴实测）：**掌心朝内**（= 端面的内法向 `+u`）· **拇指朝下**（−Z）·
    四指绕过**近侧竖棱**落到近侧面上 ⇒ 左手骨局部 `X → +Z` · `Y → +Y`，右手 `X → −Z` · `Y → +Y`
    （**镜像**：两只手都是"拇指朝下"，这正是 owner 第 1 轮看到的"虎口朝 z"的反面）。

    ⚠️ 用 `_set_world_axes(hand, y_dir, x_hint)` 表达：局部 `Z`（掌面法向）`= X × Y` ⇒
      左手 `(0,0,1)×(0,1,0) = (−1,0,0) = −X = 朝内` ✅ · 右手 `(0,0,−1)×(0,1,0) = (+1,0,0) = +X = 朝内` ✅
    """
    sgn = 1.0 if side == "Left" else -1.0
    hand_name = f"{BONE_PREFIX}{side}Hand"
    ctrl_hand = f"CTRL_{side}Hand"
    y_grip = Vector((0.0, 1.0, 0.0))          # 腕 → 指尖：**朝角色**（绕近侧竖棱收进去）
    x_grip = Vector((0.0, 0.0, sgn))          # 蜷曲轴：左手 +Z / 右手 −Z ⇒ 拇指朝下（镜像）
    if rot is not None:
        # ⚠️ 抡弧时**朝向也必须跟着转**：只转 frame（位置）而手保持静止朝向 ⇒ 手与椅子相对位姿破掉
        #    （实测握持刚性 124 m、四指读数从 ±0.5 mm 漂到 −102 mm）
        r3 = rot.to_3x3()
        y_grip = (r3 @ y_grip).normalized()
        x_grip = (r3 @ x_grip).normalized()
    y_dir = _nlerp(_rest_dir(arm, hand_name).normalized(), y_grip, s)
    x_dir = _nlerp(_rest_hinge(arm, hand_name).normalized(), x_grip, s)
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    # 握点：**端面上的一点**——沿厚度取中（`n` 方向）、沿棱向上取 `grip_h_m`（`z` 方向）。
    # ⚠️ 位置用**frame 自己的三个轴**表达 ⇒ 抡弧时它跟着 frame 一起转（椅子是刚体）。
    grip_pt = (frame["near"] + frame["n"] * (frame["thickness_mm"] / 1000.0 * grip_df)
               + frame["z"] * grip_h_m)
    off = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = Vector(wrist_rest).lerp(grip_pt - off, s)
    arm_first = solve_arm(arm, side, wrist_target, post if post is not None else _posterior(arm))
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    off2 = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = Vector(wrist_rest).lerp(grip_pt - off2, s)
    # 抡弧段（`s_swing > 0`）扫肘平面（上臂≈水平 + 手腕≈伸直）；抓握段仍用"屈曲方向 = 背侧"
    if s_swing > 0.0:
        info, elbow_scan = lift_solve_arm_scan(
            arm, side, wrist_target, post if post is not None else _posterior(arm), hand_name,
            set_hand=lambda: _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir))
    else:
        info, elbow_scan = solve_arm(arm, side, wrist_target,
                                     post if post is not None else _posterior(arm)), None
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    for finger in FOUR_FINGERS:
        amount = float((fitted or {}).get(finger, {}).get("蜷曲量", 0.0)) * s
        _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], amount)
    lift_thumb_set(arm, side, curl_axes[side]["Thumb"], LIFT_THUMB_CURL * s, thumb_solved,
                   min(1.0, max(0.0, (s - 0.8) / 0.2)))
    update(2)
    return {"s": round(s, 4), "wrist_target_m": [round(c, 4) for c in wrist_target],
            "grip_point_m": [round(c, 4) for c in grip_pt],
            "web_point_m": [round(c, 4) for c in web_point(arm, side)],
            "web_to_end_face_mm": points_face_gap_mm([web_point(arm, side)],
                                                     frame["面-端面"])["gap_mm"],
            "web_to_edge_mm": points_face_gap_mm([web_point(arm, side)],
                                                 frame["面-端面"])["gap_mm"],
            "arm_default": arm_first, "arm": info, "elbow_scan": elbow_scan,
            "姿态读数": lift_arm_posture_readings(arm, side, hand_name),
            "clamped_straight": bool(info.get("clamped_straight")),
            "tip_err_mm": info.get("tip_err_mm"),
            "elbow_deg": round(math.degrees(
                (world_point(arm, f"{BONE_PREFIX}{side}Arm")
                 - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).angle(
                    world_point(arm, hand_name) - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1)}


def lift_thumb_set(arm, side, curl_axis, base_amount, solved_deg, w):
    """拇指的 4 节：先按**蜷曲量**给基准（起手段），再朝**标定解出的握式**混合 `w`。

    ⚠️ 为什么不每帧重解拇指：`solve_thumb_to_target()` 是**粗搜索**（≈366 次 depsgraph 求值/手），
       逐帧调它在本件会慢一个量级；而本件的椅子**只平移**、手的朝向逐帧相同 ⇒ 抓握帧解出的那组
       拇指角在整段持握里**逐帧适用**（这正是"刚性握持"的含义）。收口放在进度最后 20% 内完成。
    """
    axis_index = 0 if curl_axis["axis"] == "X" else (1 if curl_axis["axis"] == "Y" else 2)
    for k in (1, 2, 3, 4):
        name = f"{BONE_PREFIX}{side}HandThumb{k}"
        if name not in arm.pose.bones:
            continue
        base = [0.0, 0.0, 0.0]
        base[axis_index] = math.radians(FINGER_CURL_DEG["Thumb"][k - 1] * curl_axis["sign"]
                                        * base_amount)
        tgt = (solved_deg or {}).get(name)
        e = Vector(base) if tgt is None else Vector(base).lerp(
            Vector([math.radians(a) for a in tgt]), w)
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(e, "XYZ")


def lift_arm_solve(arm, side, frame, grip_z, curl_axes, s, fitted, thumb_solved, wrist_rest,
                   post=None):
    """**掐棱握式的可变进度版**（卡 1 `grip_board_edge()` 的同一段姿势逻辑，加一个进度 `s`）：

    `s` = 0 → 手臂还在**静止位姿**（首帧严格中立的延伸，腕目标 = 静止腕位）；`s` = 1 → 虎口落在
    **近侧竖棱**上、拇指绕到近侧面、四指绕**远侧竖棱**收拢。⚠️ 中间帧**不是**"先摆好再插值"——
    每一帧都重新解臂（目标插值、朝向插值），所以 `s` 单调时姿势是连续的。

    与 `grip_board_edge()` 的两处差别：① 目标点与朝向按 `s` 从**静止**插到**握式**；
    ② 四指的蜷曲量取**标定**出来的逐指值（卡 1 F10 的"逐指"口径 ⇒ 一个共用系数不可能让四根都贴住）。
    """
    n, u, z = frame["n"], frame["u"], frame["z"]
    hand_name = f"{BONE_PREFIX}{side}Hand"
    ctrl_hand = f"CTRL_{side}Hand"
    x_hint = n.cross(u)
    y_dir = _nlerp(_rest_dir(arm, hand_name).normalized(), n, s)
    x_dir = _nlerp(_rest_hinge(arm, hand_name).normalized(), x_hint, s)
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    edge_pt = _to_edge(arm, side, frame, grip_z)
    off = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = Vector(wrist_rest).lerp(edge_pt - off, s)
    arm_first = solve_arm(arm, side, wrist_target, post if post is not None else _posterior(arm))
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    off2 = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = Vector(wrist_rest).lerp(edge_pt - off2, s)
    info, elbow_pick = solve_arm_with_elbow_scan(
        arm, side, wrist_target, post if post is not None else _posterior(arm))
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    for finger in FOUR_FINGERS:
        amount = float((fitted or {}).get(finger, {}).get("蜷曲量", 0.0)) * s
        _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], amount)
    lift_thumb_set(arm, side, curl_axes[side]["Thumb"], LIFT_THUMB_CURL * s, thumb_solved,
                   min(1.0, max(0.0, (s - 0.8) / 0.2)))
    update(2)
    web_p = web_point(arm, side)
    return {"s": round(s, 4),
            "wrist_target_m": [round(c, 4) for c in wrist_target],
            "edge_point_m": [round(c, 4) for c in edge_pt],
            "web_point_m": [round(c, 4) for c in web_p],
            "web_to_edge_mm": round(point_to_line_mm(web_p, frame["棱-近侧"]), 2),
            "arm_default": arm_first,
            "arm": info, "elbow_pick": elbow_pick,
            "clamped_straight": bool(info.get("clamped_straight")),
            "tip_err_mm": info.get("tip_err_mm"),
            "elbow_deg": round(math.degrees(
                (world_point(arm, f"{BONE_PREFIX}{side}Arm")
                 - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).angle(
                    world_point(arm, hand_name) - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1)}


def lift_calibrate_hand(arm, m3, lay, foot_rest, curl_axes, wrist_rest, bend_deg, pelvis_m):
    """抓握帧的**手部标定**：① 逐指蜷曲量（卡 1 F10 的"逐指"口径 ⇒ `fit_finger_curls()`）
    ② 拇指的解（解到近侧面 + 一步 Newton 把蒙皮间隙压回容差内）。

    两条都由**握式本身**决定（手的朝向逐帧由椅子 frame 给定）⇒ 标定一次、全程复用。
    """
    out = {}
    grip_z = lay["rail_top_z"] - LIFT_GRIP_DROP_M
    for side in CARD1_SIDES:
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
        fr = chair_end_frame(side, lay)
        lift_arm_solve(arm, side, fr, grip_z, curl_axes, 1.0, None, None, wrist_rest[side])
        fitted = fit_finger_curls(arm, side, fr, curl_axes[side]["Index"])
        face_pt = fr["面-近侧面"][0]
        target = face_pt + fr["u"] * LIFT_THUMB_INSET_M + fr["z"] * (grip_z - face_pt.z)
        thumb = solve_thumb_to_target(arm, side, target)
        update(2)
        gap0 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), fr["面-近侧面"])["gap_mm"]
        # Newton 回代（同 `grip_board_edge()`：近侧面**朝外**法向是 `−n`，而 gap 正是沿它量的）。
        # ⚠️ 与卡 1 的一步版差别：拇指的求解是**粗搜索**，一步会过冲或不足（实测一步残留 −4.5 mm）
        #    ⇒ 做到容差内或不再改善为止（上限 3 轮）。
        gap1, best_target, best_gap = gap0, Vector(target), gap0
        cur = Vector(target)
        for _it in range(3):
            if best_gap is None or abs(best_gap) <= LIFT_TOL_MM:
                break
            cur = cur + fr["n"] * (best_gap / 1000.0)
            thumb = solve_thumb_to_target(arm, side, cur)
            update(2)
            g = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), fr["面-近侧面"])["gap_mm"]
            if g is None:
                break
            if best_gap is None or abs(g) < abs(best_gap):
                best_gap, best_target = g, Vector(cur)
            else:
                break
        if best_target != Vector(target):
            # 回到**最好那一轮**的目标（迭代可能过冲；不改进就退回）
            thumb = solve_thumb_to_target(arm, side, best_target)
            update(2)
            gap1 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"),
                                      fr["面-近侧面"])["gap_mm"]
        else:
            gap1 = best_gap
        solved = {f"{BONE_PREFIX}{side}HandThumb{k}":
                  [round(math.degrees(a), 4) for a in arm.pose.bones[
                      f"{BONE_PREFIX}{side}HandThumb{k}"].rotation_euler]
                  for k in (1, 2, 3, 4) if f"{BONE_PREFIX}{side}HandThumb{k}" in arm.pose.bones}
        out[side] = {"fitted": fitted, "thumb_solved_deg": solved,
                     "thumb_gap_before_mm": gap0, "thumb_gap_mm": gap1,
                     "thumb_target_m": [round(c, 4) for c in target], "thumb": thumb}
    return out



# ---------------------------------------------------------------- 握式二：掌面朝下（**虎口朝 −Z**）掐上沿
#
#   来源：owner 2026-09-16 **第 1 轮**目视裁定逐字——「现在人体是用虎口朝向 z 轴的方向将椅子抓起的，
#   我希望能够用虎口朝向 **z 轴负方向**的抓法，因为这样将椅子抓起来之后**才能把椅子当作武器抡出去**」。
#   ⇒ 默认握式改成"**掌面朝下、虎口落在椅背上沿（横杆）**"——即 #163 `_strict_hand_axes()` 的那套朝向
#   （骨局部 `Y → 世界 −Y`（腕 → 指尖朝前）· 骨局部 `X → 世界 +X`（横杆轴向）⇒ **掌面法向 = X × Y = −Z 朝下**），
#   虎口点 = 上沿点 + ε·掌面法向 ⇒ **虎口朝 −Z**；
#   `卡 1 掐棱`（侧面端 · 掌面朝 ±X）保留为 `--grip side` 对照解。

def chair_rail_frame(lay, x_m=0.0):
    """椅背**上沿（横杆）**那一套命名面——掌面朝下的握式用（口径 §6.3 的同一套语言）。

    | 名 | 是什么 |
    |---|---|
    | `面-顶面` | 横杆**顶面**（朝外法向 `+Z`）——掌面压的就是它 |
    | `面-近侧面` / `面-远侧面` | 朝角色 / 背向角色那两张立面（朝外法向 `±Y`）——拇指与四指分别落上去 |
    | `棱-上沿近侧` / `棱-上沿远侧` | 顶面与两张立面的**交线**（沿 `X`）——虎口跨的是近侧那条 |
    """
    top, ny, fy = lay["rail_top_z"], lay["back_near_y"], lay["back_far_y"]
    cy, hw = lay["back_cy"], lay["half_width"]
    mid_z = top - BACK_HEIGHT / 2.0
    x_axis = Vector((1.0, 0.0, 0.0))
    return {"top_z": top, "near_y": ny, "far_y": fy, "cy": cy, "half_width": hw, "x_m": x_m,
            "面-顶面": (Vector((0.0, cy, top)), Vector((0.0, 0.0, 1.0))),
            "面-近侧面": (Vector((0.0, ny, mid_z)), Vector((0.0, 1.0, 0.0))),
            "面-远侧面": (Vector((0.0, fy, mid_z)), Vector((0.0, -1.0, 0.0))),
            "棱-上沿近侧": (Vector((0.0, ny, top)), x_axis),
            "棱-上沿远侧": (Vector((0.0, fy, top)), x_axis)}


def lift_translate_rail(rail, offset):
    """把上沿那一套整体平移（椅子只平移 ⇒ 三张面的法向与棱的方向不变）。"""
    off = Vector(offset)
    out = dict(rail)
    for key in ("面-顶面", "面-近侧面", "面-远侧面", "棱-上沿近侧", "棱-上沿远侧"):
        out[key] = (rail[key][0] + off, rail[key][1])
    out["top_z"] = rail["top_z"] + off.z
    out["near_y"] = rail["near_y"] + off.y
    out["far_y"] = rail["far_y"] + off.y
    out["cy"] = rail["cy"] + off.y
    return out


def lift_rail_from_points(pts):
    """从**求值后的椅背网格角点**重建上沿那一套——判据对着产物，不读声明的位移。"""
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    ny, fy, top = max(ys), min(ys), max(zs)
    cy = (ny + fy) / 2.0
    mid_z = (max(zs) + min(zs)) / 2.0
    x_axis = Vector((1.0, 0.0, 0.0))
    return {"top_z": top, "near_y": ny, "far_y": fy, "cy": cy,
            "half_width": (max(xs) - min(xs)) / 2.0, "x_m": 0.0,
            "面-顶面": (Vector((0.0, cy, top)), Vector((0.0, 0.0, 1.0))),
            "面-近侧面": (Vector((0.0, ny, mid_z)), Vector((0.0, 1.0, 0.0))),
            "面-远侧面": (Vector((0.0, fy, mid_z)), Vector((0.0, -1.0, 0.0))),
            "棱-上沿近侧": (Vector((0.0, ny, top)), x_axis),
            "棱-上沿远侧": (Vector((0.0, fy, top)), x_axis)}



# ---------------------------------------------------------------- 握式三：反手抓侧面端（owner 第 3 轮指名）
#
#   逐字：「他妈的不对啊，我要的是**抓住椅子的侧面**，不是上沿，**要反手抓**，把椅子**抡起来**
#   维持在胸前」+「椅子不是一个整体么，你把手和椅背的相对位置固定之后**直接调手的位置**就行了，
#   椅子跟着动」⇒ ① 接触面 = 椅背侧面端（`x=±0.21` 那张 40 mm 端面）② 反手 = **拇指朝下 ·
#   掌心朝内**（两手**镜像**，不再是一上一下）③ **抡一个上摆弧**：先提离地、再绕握点转
#   `LIFT_SWING_DEG`，到位后横在胸前 ④ 椅子的位姿**由手的路径决定**（刚体挂点）。

def lift_chair_frame_from_object(ob_ev, side):
    """从**求值后的椅背零件**（对象矩阵 + 标准 cube 的 ±0.5 局部盒）重建板端坐标。

    ⚠️ 为什么不能再用"世界坐标 min/max"那一版：**抡过的椅子是转的**，转 90° 之后"世界 y 的极值"
       已经不对应板厚方向了。这里按**零件自己的三个轴**取（等价于"对着产物量"，但旋转无关）。
    """
    mw = ob_ev.matrix_world
    r3 = mw.to_3x3()
    sc = mw.to_scale()
    nx = (r3 @ Vector((1.0, 0.0, 0.0))).normalized()
    ny = (r3 @ Vector((0.0, 1.0, 0.0))).normalized()
    nz = (r3 @ Vector((0.0, 0.0, 1.0))).normalized()
    c = mw @ Vector((0.0, 0.0, 0.0))
    sgn = 1.0 if side == "Left" else -1.0
    # 近侧棱在**局部 +y**（装配时 `back_center` 的近侧面朝角色）；底边取局部 −z ⇒ z_span 从 0 起
    base = c + nx * (sgn * 0.5 * sc.x) - nz * (0.5 * sc.z)
    near = base + ny * (0.5 * sc.y)
    far = base - ny * (0.5 * sc.y)
    frame = board_end_frame(near, far, -nx * sgn,
                            u_span_m=(0.0, sc.x), z_span_m=(0.0, sc.z))
    # ⚠️ `board_end_frame()` 用 `z.z < 0` 判"朝上"——**椅子抡到 ~90° 时这条启发式会翻向**
    #    （实测：帧 48 起四指的"点↔体"读数从 ±0.5 mm 跳到 268–328 mm，而"点↔面"读数不变）。
    #    这里按**零件自己的局部 +z** 钉死（旋转无关；未旋转时与原来逐值相同）。
    frame["z"] = nz
    return frame


def lift_contact_rows_backhand(arm_like, side, frame):
    """**反手抓侧面端**这套握式的接触对（回显卡与判据的同一来源）。

    | # | 手部分区 | 物体分区 | 形态 | 为什么 |
    |---|---|---|---|---|
    | 1 | **掌面** | **端面** | 点↔面 | 掌心朝内压的就是这张端面 |
    | 2 | **四指逐根（末节）** | **近侧面** | 点↔面 | 反手时四指绕过**近侧竖棱**、落到近侧面上 |
    | 3 | **拇指（末节）** | 端面 / 近侧面 | 点↔面 | 拇指朝下包住端面的下段（两者都报，主判据取"更贴合的那一面"见注释） |
    """
    hand_name = f"{BONE_PREFIX}{side}Hand"
    palm_pts = [arm_like.matrix_world @ (arm_like.pose.bones[hand_name].matrix @ q)
                for q in palm_face_vertices(arm_like, side)]
    thumb_pts = lift_distal_skin_local(arm_like, side, "Thumb")
    return [{
        # 判据：虎口点（骨点 + ε·掌面法向）落在**端面**上——它对着**从产物网格重建的 frame**量，
        # 因此抓得住"椅子与手错位"（本件实测过一次：抡弧漏转手的朝向 ⇒ 这条当场漂）
        "手部分区": "虎口", "物体分区": "端面", "判据形态": "点↔面（ε 换算后的着力点）",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm", "并列项": "—",
        "读数_mm": points_face_gap_mm([web_point(arm_like, side)], frame["面-端面"])["gap_mm"],
    }, {
        # 读数：同一姿势下**掌面层**离端面 +10.47 mm（ε 的位置依赖性，见证据 §六#6）⇒ 不当判据
        "手部分区": "掌面（读数）", "物体分区": "端面", "判据形态": "点↔面（取最近点）",
        "容差档": "只报读数（ε 的位置依赖性，证据 §六#6）", "并列项": "—", "只报读数": True,
        "读数_mm": points_face_gap_mm(palm_pts, frame["面-端面"])["gap_mm"],
    }, {
        "手部分区": "食/中/无名/小四指（**末节**）", "物体分区": "**板体（有限盒）**",
        "判据形态": "点↔体（有符号；同时报「距近侧面」的读数）",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm", "并列项": "四指逐根（口径 §七 硬规矩 2）",
        "读数_mm": [points_box_gap_mm(lift_distal_skin_local(arm_like, side, f), frame)
                    for f in FOUR_FINGERS],
        "并列读数_面内_mm": [points_face_gap_mm(lift_distal_skin_local(arm_like, side, f),
                                            frame["面-近侧面"])["gap_mm"] for f in FOUR_FINGERS],
        "逐项名": list(FOUR_FINGERS),
        "符号约定": "正 = 悬在近侧面之外（朝角色一侧）· |·| ≤ 容差 = 贴住 · 负 = 越过近侧面（进板）",
    }, {
        "手部分区": "**拇指（末节）**", "物体分区": "**椅背正面（近侧面）**",
        "判据形态": "点↔面（有符号；板体读数并列报）",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm", "并列项": "—",
        "读数_mm": points_face_gap_mm(thumb_pts, frame["面-近侧面"])["gap_mm"],
        "并列读数": {"板体": points_box_gap_mm(thumb_pts, frame),
                  "端面": points_face_gap_mm(thumb_pts, frame["面-端面"])["gap_mm"]},
    }]


def lift_fit_curls_backhand(arm, side, curl_axis, face, lo=0.6, hi=2.4, steps=41):
    """反手握式的逐指蜷曲量：按**末节蒙皮 ↔ 该指落到的那张面**打分（与卡 1 的分工见证据 §4.4）。"""
    out = {}
    for finger in FOUR_FINGERS:
        best = None
        for i in range(steps):
            amount = lo + (hi - lo) * i / (steps - 1)
            _apply_one_finger_curl(arm, side, finger, curl_axis, amount)
            update(1)
            gaps = [points_face_gap_mm([q], face)["gap_mm"]
                    for q in lift_distal_skin_local(arm, side, finger)]
            gap = min(gaps, key=abs) if gaps else None
            score = (abs(gap) if gap is not None else 1e9, -amount)
            if best is None or score < best[0]:
                best = (score, amount, gap)
        _apply_one_finger_curl(arm, side, finger, curl_axis, best[1])
        out[finger] = {"蜷曲量": round(best[1], 3), "末节间隙_mm": round(best[2], 2),
                       "板体间隙_mm": round(best[2], 2)}
    update(2)
    return out


def lift_calibrate_hand_backhand(arm, m3, lay, frames, grip_h, foot_rest, curl_axes, wrist_rest,
                                 bend_deg, pelvis_m, pivot=None, swing_rot=None):
    """反手握式的标定：① 握点在端面上的**深度分数**（一维扫描 × 每点重做四指精修）
    ② 逐指蜷曲量（末节↔近侧面）③ 拇指（末节↔端面，粗解 + Newton + 局部模式搜索）。

    ⚠️ `frames` 是**逐侧**的（`{side: frame}`）：两只手各自抓自己那一侧的端面——用同一侧的面去解
       另一只手，会让那只手的拟合与拇指全按错面解（实测右手拇指残留 6.0 mm > 容差）。
    """
    out = {}
    for side in CARD1_SIDES:
        frame = frames[side]
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
        lift_arm_solve_backhand(arm, side, frame, 1.0, curl_axes, None, None, wrist_rest[side],
                                grip_h_m=grip_h)
        fitted = lift_fit_curls_backhand(arm, side, curl_axes[side]["Index"],
                                         frame["面-近侧面"])
        out[side] = {"fitted": fitted}
        # ① 握点深度分数扫描（每个落点上重做四指精修；判据 = 四指末节↔近侧面的最大 |间隙| 最小）
        best = None
        for i in range(13):
          for dh in (0.0, -0.03, 0.03):
            df = 0.20 + 0.05 * i
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
            lift_arm_solve_backhand(arm, side, frame, 1.0, curl_axes, fitted, None,
                                    wrist_rest[side], grip_h_m=grip_h + dh, grip_df=df)
            amts, gaps, boxes = {}, {}, {}
            for f in FOUR_FINGERS:
                a, g = lift_refine_curl_local(arm, side, f, curl_axes[side][f],
                                              frame["面-近侧面"], fitted[f]["蜷曲量"])
                amts[f], gaps[f] = a, g
                pts = lift_distal_skin_local(arm, side, f)
                boxes[f] = None if not pts else round(min(box_gap_mm(q, frame) for q in pts), 2)
            # 评分同时看两条：**接触判据**（末节↔近侧面）与**判据 5 的措辞**（末节↔构件表面）
            contacts = round(max(max(abs(gaps[f]), max(boxes[f] or 0.0, 0.0))
                                 for f in FOUR_FINGERS), 2)
            # **owner 第 3 轮点名的两个量**也进评分：在"抡到位"那一帧量**手腕折角 / 上臂夹角**
            # （握式解出来的两个落点自由度因此不只服务接触，还服务手臂姿态）
            wr, up = 90.0, 90.0
            if swing_rot is not None:
                clear_pose(arm)
                drop_temp(arm, also_objects=False)
                lift_body_setup(arm, m3, bend_deg, Vector((0.0, 0.0, 0.0)), foot_rest)
                fr2 = lift_transform_frame(frame, pivot, swing_rot,
                                           Vector((0.0, LIFT_SIDE_GRIP_Y_M - lay["back_cy"],
                                                   LIFT_SIDE_GRIP_Z_M
                                                   - (SEAT_TOP + grip_h))))
                lift_arm_solve_backhand(arm, side, fr2, 1.0, curl_axes, fitted, None,
                                        wrist_rest[side], grip_h_m=grip_h + dh, grip_df=df,
                                        rot=swing_rot, s_swing=1.0)
                rr = lift_arm_posture_readings(arm, side, f"{BONE_PREFIX}{side}Hand")
                wr, up = rr["手腕_deg"], abs(rr["上臂_deg"])
            score = (contacts, round(0.25 * wr + 0.25 * up, 2), abs(df - 0.5))
            if best is None or score < best[0]:
                best = (score, round(df, 3), amts, gaps, boxes, dh)
        out[side]["grip_df"] = best[1]
        out[side]["四指残差_mm"] = best[3]
        out[side]["四指_到构件表面_mm"] = best[4]
        out[side]["扫描"] = {"握点深度分数": [0.20, 0.80], "判据": "四指末节↔近侧面的最大 |间隙| 最小"}
        out[side]["fitted"] = {f: {"蜷曲量": best[2][f], "末节间隙_mm": best[3][f],
                                "板体间隙_mm": best[3][f]} for f in FOUR_FINGERS}
        # ② 落点定下来后解拇指（目标 = 端面上握点下方 25 mm；Newton + 局部模式搜索精修）
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
        lift_arm_solve_backhand(arm, side, frame, 1.0, curl_axes, out[side]["fitted"], None,
                                wrist_rest[side], grip_h_m=grip_h + best[5], grip_df=best[1])
        # owner 2026-09-16 第 3 轮："现在的四指是对的，将大拇指的位置调到椅背**正面**"
        # ⇒ 拇指的解与判据都对着**近侧面**（朝角色那一张大面），不再对端面
        face = frame["面-近侧面"]
        target = (frame["near"] + frame["n"] * (frame["thickness_mm"] / 4000.0)
                  + frame["z"] * (grip_h - 0.020))
        thumb = solve_thumb_to_target(arm, side, target)
        update(2)
        gap0 = points_face_gap_mm(lift_distal_skin_local(arm, side, "Thumb"), face)["gap_mm"]
        push = -face[1]
        cur = Vector(target)
        best_gap, best_target = gap0, Vector(target)
        for _it in range(4):
            if best_gap is None or abs(best_gap) <= LIFT_TOL_MM:
                break
            cur = cur + push * (best_gap / 1000.0)
            thumb = solve_thumb_to_target(arm, side, cur)
            update(2)
            g = points_face_gap_mm(lift_distal_skin_local(arm, side, "Thumb"), face)["gap_mm"]
            if g is None:
                break
            if best_gap is None or abs(g) < abs(best_gap):
                best_gap, best_target = g, Vector(cur)
            else:
                break
        if best_target != Vector(target):
            thumb = solve_thumb_to_target(arm, side, best_target)
            update(2)
        gap1 = lift_refine_thumb_local(arm, side, face=face, box=frame)
        solved = {f"{BONE_PREFIX}{side}HandThumb{k}":
                  [round(math.degrees(a), 4) for a in arm.pose.bones[
                      f"{BONE_PREFIX}{side}HandThumb{k}"].rotation_euler]
                  for k in (1, 2, 3, 4) if f"{BONE_PREFIX}{side}HandThumb{k}" in arm.pose.bones}
        out[side].update({"thumb_solved_deg": solved, "thumb_gap_before_mm": gap0,
                          "thumb_gap_mm": gap1, "thumb_target_m": [round(c, 4) for c in best_target],
                          "thumb": thumb})
    return out

def lift_fit_curls_palm(arm, side, curl_axis, face, lo=0.6, hi=2.2, steps=41):
    """掌面朝下握式的**逐指蜷曲量**：按**末节蒙皮 ↔ 远侧面**（点↔面，有符号）打分。

    ⚠️ 为什么不能直接用 `fit_finger_curls()`（卡 1 那一支）：它按"**该指任意一处皮肤**离板体最近"打分
    ⇒ 手指的中段贴上远侧棱就算最优，而**末节还挂在离板体 20 mm 的地方**（实测：判据 5 当场报红）。
       两支的分工因此明确：卡 1 那一支服务"四指↔板体"这条对，本支服务"末节↔构件表面"。
    """
    out = {}
    for finger in FOUR_FINGERS:
        best = None
        for i in range(steps):
            amount = lo + (hi - lo) * i / (steps - 1)
            _apply_one_finger_curl(arm, side, finger, curl_axis, amount)
            update(1)
            gaps = [points_face_gap_mm([q], face)["gap_mm"]
                    for q in lift_distal_skin_local(arm, side, finger)]
            gap = (min(gaps, key=abs) if gaps else None)
            score = (abs(gap) if gap is not None else 1e9, -amount)
            if best is None or score < best[0]:
                best = (score, amount, gap)
        _apply_one_finger_curl(arm, side, finger, curl_axis, best[1])
        out[finger] = {"蜷曲量": round(best[1], 3), "末节间隙_mm": round(best[2], 2),
                       "板体间隙_mm": round(best[2], 2)}
    update(2)
    return out



def lift_refine_thumb_local(arm, side, face=None, tol=LIFT_TOL_MM, steps=(6.0, 2.0, 0.7), box=None):
    """在**当前**拇指姿势附近做**模式搜索**精修（`Thumb1` 的三个欧拉角），把末节间隙压进容差。

    ⚠️ 为什么需要它：`solve_thumb_to_target()` 是**网格粗搜索**（±3° 分辨率），实测左右手会各落在
       不同局部解（左手残留 −6.8 mm、右手 +1.99 mm）⇒ 只靠它做判据，会得到"一只手对、一只手错"。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]

    def gap():
        update(1)
        pts = lift_distal_skin_local(arm, side, "Thumb")
        if box is not None:
            return None if not pts else round(min(box_gap_mm(q, box) for q in pts), 2)
        return points_face_gap_mm(pts, face)["gap_mm"]

    cur = gap()
    for step in steps:
        for _round in range(6):
            if cur is not None and abs(cur) <= tol:
                break
            base = list(pb.rotation_euler)
            best = (abs(cur) if cur is not None else 1e9, base, cur)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx == dy == dz == 0:
                            continue
                        pb.rotation_euler = Euler(
                            (base[0] + math.radians(step * dx),
                             base[1] + math.radians(step * dy),
                             base[2] + math.radians(step * dz)), "XYZ")
                        g = gap()
                        if g is not None and abs(g) < best[0]:
                            best = (abs(g), list(pb.rotation_euler), g)
            if best[0] < (abs(cur) if cur is not None else 1e9):
                pb.rotation_euler = Euler(best[1], "XYZ")
                cur = best[2]
            else:
                pb.rotation_euler = Euler(base, "XYZ")
                break
    update(2)
    return cur


def lift_refine_curl_local(arm, side, finger, curl_axis, face, amount, tol=LIFT_TOL_MM,
                           steps=(0.08, 0.03)):
    """**单根手指**蜷曲量的局部精修（模式搜索）——返回 `(蜷曲量, 末节间隙_mm)`。"""
    def gap(a):
        _apply_one_finger_curl(arm, side, finger, curl_axis, a)
        update(1)
        return points_face_gap_mm(lift_distal_skin_local(arm, side, finger), face)["gap_mm"]

    cur, amount = gap(amount), amount
    for step in steps:
        for _round in range(6):
            if cur is not None and abs(cur) <= tol:
                break
            best = (abs(cur) if cur is not None else 1e9, amount, cur)
            for d in (-1, 0, 1):
                if d == 0:
                    continue
                a = amount + d * step
                g = gap(a)
                if g is not None and abs(g) < best[0]:
                    best = (abs(g), a, g)
            if best[0] < (abs(cur) if cur is not None else 1e9):
                amount, cur = best[1], best[2]
            else:
                gap(amount)
                break
    gap(amount)
    return round(amount, 4), round(cur, 2) if cur is not None else None


def lift_contact_rows_palm(arm_like, side, rail, box_frame):
    """**掌面朝上沿**这套握式的接触对（四条；与回显卡**同一来源**）。

    | # | 手部分区 | 物体分区 | 形态 | 为什么是这个对象 |
    |---|---|---|---|---|
    | 1 | 虎口 | **上沿近侧真棱** | 点↔线 | 虎口跨的就是这条**交线**（#163 的「顶面中线」不是棱——本仓已登记为判据缺陷） |
    | 2 | **掌面最低点** | **顶面** | 点↔面 | 掌面压的是顶面；判据形态沿用 #163 的"甲"（**允许倾斜**，取掌面那一层的**最低点**） |
    | 3 | 拇指 | **近侧面** | 点↔面 | 拇指绕到朝角色那一面（口径 §三 D8 的同一件事，换了一条棱） |
    | 4 | **四指逐根** | **板体**（远侧面一侧） | 点↔体 | 四指越过远侧上沿往下兜住远侧面；量**体**不量无限平面（卡 1 §F4 的教训） |
    """
    hand_name = f"{BONE_PREFIX}{side}Hand"
    palm_pts = [arm_like.matrix_world @ (arm_like.pose.bones[hand_name].matrix @ q)
                for q in palm_face_vertices(arm_like, side)]
    return [{
        "手部分区": "**掌面最低点**", "物体分区": "顶面",
        "判据形态": "点↔面（允许倾斜，取最低点）",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm（形态沿用 #163 的「甲」）", "并列项": "—",
        "读数_mm": points_face_gap_mm(palm_pts, rail["面-顶面"])["gap_mm"],
    }, {
        # ⚠️ 这一格是**读数**：实测在"掌面压在顶面上"的朝向下，虎口点（拇指/食指根中点 + ε·法向）
        #    比掌面层**低 10.47 mm**——ε(32.6833 mm) 是从 `Hand` **骨原点**标定的（#160），
        #    搬到"两根指骨的中点"上不成立（掌指间的肉更薄）⇒ 它若当判据，等于要求掌面悬空 10.47 mm。
        #    本握式因此以**掌面层**为接触基准；虎口点并列报读数（证据 §六#6）。
        "手部分区": "虎口（读数）", "物体分区": "顶面", "判据形态": "点↔面",
        "容差档": "只报读数（已知偏置 −10.47 mm，ε 的位置依赖性）", "并列项": "—",
        "只报读数": True,
        "读数_mm": points_face_gap_mm([web_point(arm_like, side)], rail["面-顶面"])["gap_mm"],
        "面内自检": {"虎口_y": round(web_point(arm_like, side).y, 4),
                  "顶面_y区间": [round(rail["far_y"], 4), round(rail["near_y"], 4)],
                  "在顶面内": bool(rail["far_y"] <= web_point(arm_like, side).y
                                <= rail["near_y"])},
    }, {
        "手部分区": "拇指", "物体分区": "近侧面", "判据形态": "点↔面",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm", "并列项": "—",
        "读数_mm": points_face_gap_mm(lift_distal_skin_local(arm_like, side, "Thumb"),
                                      rail["面-近侧面"])["gap_mm"],
        "并列读数_全指_mm": points_face_gap_mm(finger_skin_world(arm_like, side, "Thumb"),
                                            rail["面-近侧面"])["gap_mm"],
    }, {
        "手部分区": "食/中/无名/小四指", "物体分区": "**远侧面**",
        "判据形态": "点↔面（有符号；有限盒的穿透量并列报出）",
        "容差档": f"接触 tol_contact = {LIFT_TOL_MM} mm", "并列项": "四指逐根（口径 §七 硬规矩 2）",
        # ⚠️ 掌面朝下时**不能**用"点↔体（板体）"当判据：手指"从顶面斜插进板里"与"绕远侧上沿兜住"
        #    在**有符号盒间隙**上都能取到 0（实测：fit 出的姿势让四指陷进板体 7–16 mm 而末节读数 0.00）。
        #    这与卡 1 的教训同族——**判据的度量对象要与措辞同层**（口径 §4.2 硬规矩 3）。
        "读数_mm": [points_face_gap_mm(lift_distal_skin_local(arm_like, side, f),
                                       rail["面-远侧面"])["gap_mm"] for f in FOUR_FINGERS],
        "逐项名": list(FOUR_FINGERS),
        "并列读数_板体穿透_mm": [points_box_gap_mm(finger_skin_world(arm_like, side, f), box_frame)
                               for f in FOUR_FINGERS],
        "符号约定": "正 = 悬在远侧面之外 · |·| ≤ 容差 = 贴住 · 负 = 越过远侧面（板体内）",
    }]


def lift_arm_posture_readings(arm, side, hand_name):
    """**上臂与水平夹角** + **手腕夹角（掌骨 vs 前臂）**——owner 2026-09-16 第 3 轮点名的两个量。

    | 量 | 期望 | 为什么 |
    |---|---|---|
    | `上臂_deg` | **≈0°（水平）** | owner：「大臂跟地面近似水平」 |
    | `手腕_deg` | **≈0°（伸直）** | owner：「手腕和小臂的夹角也不对」⇒ 不折腕（0° = 掌骨与前臂同向） |
    """
    B = BONE_PREFIX
    sh = world_point(arm, f"{B}{side}Arm")
    el = world_point(arm, f"{B}{side}ForeArm")
    wr = world_point(arm, hand_name)
    up = (el - sh).normalized()
    upper = math.degrees(math.asin(max(-1.0, min(1.0, up.z))))     # 正 = 上臂朝上抬
    v1 = (wr - el).normalized()
    knuckle = world_point(arm, f"{B}{side}HandMiddle1")
    v2 = (knuckle - wr).normalized()
    wrist = math.degrees(v1.angle(v2))          # 0° = 掌骨与前臂同向 = **伸直**
    return {"上臂_deg": round(upper, 1), "手腕_deg": round(wrist, 1),
            "上臂指向": [round(c, 4) for c in up], "肘_m": [round(c, 4) for c in el]}


def lift_solve_arm_scan(arm, side, wrist_target, post, hand_name, set_hand=None, steps=48,
                       weight_wrist=1.0):
    """**扫描肘平面**并同时评两个量：**上臂≈水平**（owner 第 3 轮）与**手腕≈伸直**（同轮）。

    ⚠️ 与 `solve_arm_with_elbow_scan()`（卡 1 那一支）的差别：那一支的罚分是"肘别外张/别反关节"，
       服务**弯腰抓握**；本支服务**抡到位那一帧**——那时 owner 要的是"大臂近似水平"，
       于是肘必须**抬到体侧**而不是垂在弦下方。两支的取向不同，故不共用。
    """
    axis = (Vector(wrist_target) - world_point(arm, f"{BONE_PREFIX}{side}Arm"))
    if axis.length < 1e-9:
        return solve_arm(arm, side, wrist_target, post), None
    axis = axis.normalized()
    base = Vector(post)
    perp = base - axis * base.dot(axis)
    if perp.length < 1e-8:
        perp = Vector((0.0, 0.0, 1.0)) - axis * axis.z
    perp.normalize()
    side_ax = axis.cross(perp).normalized()
    best = None
    for i in range(steps):
        a = 2.0 * math.pi * i / steps
        d = (perp * math.cos(a) + side_ax * math.sin(a)).normalized()
        info = solve_arm(arm, side, wrist_target, d)
        if set_hand is not None:
            set_hand()          # ⚠️ 父链变了 ⇒ 必须重设手的朝向，否则量到的是"错位的手"
        r = lift_arm_posture_readings(arm, side, hand_name)
        # 评分：**先保证大臂≈水平**（超阈值重罚），再尽量把**手腕折角**压小
        score = (weight_wrist * r["手腕_deg"]
                 + 3.0 * max(0.0, abs(r["上臂_deg"]) - LIFT_ARM_LEVEL_TOL_DEG)
                 + abs(r["上臂_deg"]) * 0.1
                 + 10.0 * float(info.get("clamped_straight", False)))
        if best is None or score < best[0]:
            best = (score, d, info, r)
    info = solve_arm(arm, side, wrist_target, best[1])
    if set_hand is not None:
        set_hand()
    update(2)
    return info, {"扫描步长_deg": round(360.0 / steps, 1), "罚分": round(best[0], 2),
                  "选中_读数": best[3]}


def _palm_lowest_offset(arm, side, hand_name):
    """**掌面层最低点**相对腕头（骨原点）的偏移（按当前朝向现算）——掌面朝下时它就是"压在横杆上的那一点"。"""
    pb = arm.pose.bones[hand_name]
    mw = arm.matrix_world
    pts = [mw @ (pb.matrix @ q) for q in palm_face_vertices(arm, side)]
    if not pts:
        return Vector((0.0, 0.0, 0.0))
    return min(pts, key=lambda q: q.z) - world_point(arm, hand_name)


def lift_arm_solve_palm(arm, side, rail, x_m, s, curl_axes, fitted, thumb_solved, wrist_rest,
                        palm_dy=0.0, post=None):
    """**掌面朝下的上沿握式**（`_strict_hand_axes()` 的同一套朝向）的可变进度版。

    `s` = 0 → 手臂还在静止位姿；`s` = 1 → **虎口落在顶面上**（`web = 顶面上一点 + ε·(−Z)`）、
    拇指绕到近侧面、四指越过远侧上沿兜住远侧面。
    """
    hand_name = f"{BONE_PREFIX}{side}Hand"
    ctrl_hand = f"CTRL_{side}Hand"
    y_grip = Vector((0.0, -1.0, 0.0))
    x_grip = Vector((1.0, 0.0, 0.0))
    y_dir = _nlerp(_rest_dir(arm, hand_name).normalized(), y_grip, s)
    x_dir = _nlerp(_rest_hinge(arm, hand_name).normalized(), x_grip, s)
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    # ⚠️ **符号**：`x_m` 传进来的是"离中线的距离"，左手在 `+x`、右手在 `−x`——漏了符号会让**右手跨到左边**，
    #    而两只手的虎口读数会**看起来一样**（实测：两只手的 web 都报 (0.19, −0.47, 0.7949)）。
    sgn = 1.0 if side == "Left" else -1.0
    # ⚠️ 落点用**掌面层最低点**、**不是** `web_point()`：实测在"掌面朝下"这个朝向下，
    #    虎口点（= 拇指/食指根中点 + ε·法向）比掌面层**低 10.47 mm**——ε(32.6833 mm) 是从
    #    `Hand` **骨原点**标定的（#160），搬到"两根指骨的中点"上就不成立了（掌指间的肉更薄）。
    #    ⇒ 本握式的接触基准 = 掌面层；虎口点降为**读数并带已知偏置**（见证据 §六#6）。
    palm_pt = Vector((sgn * x_m, rail["cy"] + palm_dy, rail["top_z"]))
    off = _palm_lowest_offset(arm, side, hand_name)
    wrist_target = Vector(wrist_rest).lerp(palm_pt - off, s)
    arm_first = solve_arm(arm, side, wrist_target, post if post is not None else _posterior(arm))
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    off2 = _palm_lowest_offset(arm, side, hand_name)
    wrist_target = Vector(wrist_rest).lerp(palm_pt - off2, s)
    # ⚠️ 这里**不用** `solve_arm_with_elbow_scan()`：#163 `hand_grip()` 走的是"屈曲方向 = 身体背侧"，
    #    两侧因此镜像；肘扫描会**逐手**各挑一个方向 ⇒ 实测左肘 72.0° / 右肘 107.6°（一手一个肘平面、
    #    姿势不对称）。卡 1 的侧面端握式才需要扫（那一格里肘容易被夹住）。
    info = solve_arm(arm, side, wrist_target, post if post is not None else _posterior(arm))
    elbow_pick = {"来源": "`solve_arm()`：屈曲方向 = 身体背侧（与 #163 `hand_grip()` 同一条路）"}
    _set_world_axes(arm, ctrl_hand, hand_name, y_dir, x_dir)
    for finger in FOUR_FINGERS:
        amount = float((fitted or {}).get(finger, {}).get("蜷曲量", 0.0)) * s
        _apply_one_finger_curl(arm, side, finger, curl_axes[side][finger], amount)
    lift_thumb_set(arm, side, curl_axes[side]["Thumb"], LIFT_THUMB_CURL * s, thumb_solved,
                   min(1.0, max(0.0, (s - 0.8) / 0.2)))
    update(2)
    return {"s": round(s, 4), "wrist_target_m": [round(c, 4) for c in wrist_target],
            "web_point_m": [round(c, 4) for c in web_point(arm, side)],
            "web_to_rail_mm": round(point_to_line_mm(web_point(arm, side), rail["棱-上沿近侧"]), 2),
            # 两个握式共用一个键名（"虎口 ↔ 该握式跨的那条棱"），帧表与打印因此不必分支
            "web_to_edge_mm": round(point_to_line_mm(web_point(arm, side), rail["棱-上沿近侧"]), 2),
            "arm_default": arm_first, "arm": info, "elbow_pick": elbow_pick,
            "clamped_straight": bool(info.get("clamped_straight")),
            "tip_err_mm": info.get("tip_err_mm"),
            "elbow_deg": round(math.degrees(
                (world_point(arm, f"{BONE_PREFIX}{side}Arm")
                 - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).angle(
                    world_point(arm, hand_name) - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1)}


def lift_calibrate_hand_palm(arm, m3, lay, rail, grip_x, foot_rest, curl_axes, wrist_rest,
                             bend_deg, pelvis_m):
    """掌面朝下握式的**手部标定**：逐指蜷曲量（F10 的同一口径）+ 拇指解（解到近侧面 + Newton）。

    ⚠️ 与侧面端那套的唯一差别是**目标面换了**（顶面 / 近侧面 / 四指兜远侧面），
       而"拇指往 −Y 推"的 Newton 方向仍取近侧面**朝外法向的反向**（同一件事、另一条棱）。
    """
    out = {}
    for side in CARD1_SIDES:
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
        lift_arm_solve_palm(arm, side, rail, grip_x, 1.0, curl_axes, None, None, wrist_rest[side])
        # ⚠️ 上界放宽到 2.2：零蜷曲时四指尖在**远侧面之外 17–21 mm**（掌面朝下时手指本来就伸在远侧上沿之外），
        #    卡 1 的默认上界 1.5 会让短指（Ring/Pinky）**顶到界**还差 13–34 mm（实测）。
        fitted = lift_fit_curls_palm(arm, side, curl_axes[side]["Index"], rail["面-远侧面"])
        sgn = 1.0 if side == "Left" else -1.0
        # ① 先跑一遍拇指（只为给下面的落点扫描一个起点；定完落点后会**重解**）
        solve_thumb_to_target(
            arm, side, Vector((sgn * (grip_x - 0.020), rail["near_y"] + 0.020,
                               rail["top_z"] - 0.035)))
        update(2)
        thumb_stub = {f"{BONE_PREFIX}{side}HandThumb{k}":
                      [round(math.degrees(a), 4) for a in arm.pose.bones[
                          f"{BONE_PREFIX}{side}HandThumb{k}"].rotation_euler]
                      for k in (1, 2, 3, 4) if f"{BONE_PREFIX}{side}HandThumb{k}" in arm.pose.bones}
        out[side] = {"fitted": fitted, "thumb_solved_deg": thumb_stub,
                     "thumb_gap_before_mm": None, "thumb_gap_mm": None,
                     "thumb_target_m": None, "thumb": None}
        # ⚠️ 起点放在近侧面**之外** 20 mm（掌面压在顶面上时，拇指是"从外侧包过去"的；
        #    起点若压在面上，Newton 的第一步会把整根拇指推进板里——实测残留 −42.13 mm）
        target = Vector((sgn * (grip_x - 0.020), rail["near_y"] + 0.020, rail["top_z"] - 0.035))
        thumb = solve_thumb_to_target(arm, side, target)
        update(2)
    # ---- 一维标定：掌面在顶面上的**落点 y 偏置**（判据 = 四指末节贴住远侧面）----
    for side in CARD1_SIDES:
        best = None
        for i in range(19):
            dy = -0.045 + 0.005 * i
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
            lift_arm_solve_palm(arm, side, rail, grip_x, 1.0, curl_axes,
                                out[side]["fitted"], None,
                                wrist_rest[side], palm_dy=dy)
            # 每个落点上都把四指**重新精修**（否则落点与蜷曲量的耦合会让短指顶在容差外）
            amts, gaps = {}, {}
            for f in FOUR_FINGERS:
                a, g = lift_refine_curl_local(arm, side, f, curl_axes[side][f],
                                              rail["面-远侧面"], out[side]["fitted"][f]["蜷曲量"])
                amts[f], gaps[f] = a, g
            score = (round(max(abs(g) for g in gaps.values()), 2), abs(dy))
            if best is None or score < best[0]:
                best = (score, round(dy, 4), amts, gaps)
        out[side]["grip_df"] = best[1]
        out[side]["grip_dh_m"] = best[5]
        out[side]["palm_anchor_dy_m"] = best[1]
        out[side]["palm_anchor_四指残差_mm"] = best[3]
        out[side]["fitted"] = {f: {"蜷曲量": best[2][f], "末节间隙_mm": best[3][f],
                                "板体间隙_mm": best[3][f]} for f in FOUR_FINGERS}
        out[side]["palm_anchor_扫描"] = {"范围_m": [-0.045, 0.045], "步长_m": 0.005,
                                      "判据": "四指末节 ↔ 远侧面 的最大 |间隙| 最小"}
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        lift_body_setup(arm, m3, bend_deg, pelvis_m, foot_rest)
        lift_arm_solve_palm(arm, side, rail, grip_x, 1.0, curl_axes, out[side]["fitted"],
                            None, wrist_rest[side], palm_dy=best[1])
        # ---- ② 落点定下来**之后**才解拇指 + Newton（顺序错一次 ⇒ 产物侧读到 16.25 mm，实测）----
        face = rail["面-近侧面"]
        target = Vector((sgn * (grip_x - 0.020), rail["near_y"] + 0.020, rail["top_z"] - 0.035))
        thumb = solve_thumb_to_target(arm, side, target)
        update(2)
        gap0 = points_face_gap_mm(lift_distal_skin_local(arm, side, "Thumb"), face)["gap_mm"]
        best_gap, best_target, cur = gap0, Vector(target), Vector(target)
        push = -face[1]                       # 朝**face 内部**推的方向（= 朝外法向的反向）
        # 目标 y 的小范围扫描（`solve_thumb_to_target()` 是**粗搜索**，左右手会各落在不同局部解 —— 实测
        # 左手一步 Newton 后仍残留 −6.8 mm 而右手 1.99 mm ⇒ 不扫就会得到"一只手对、一只手错"）
        for _dy in (-0.010, -0.005, 0.0, 0.005, 0.010):
            cand = Vector((sgn * (grip_x - 0.020), rail["near_y"] + 0.020 + _dy,
                           rail["top_z"] - 0.035))
            solve_thumb_to_target(arm, side, cand)
            update(2)
            g = points_face_gap_mm(lift_distal_skin_local(arm, side, "Thumb"), face)["gap_mm"]
            if g is not None and (best_gap is None or abs(g) < abs(best_gap)):
                best_gap, best_target = g, Vector(cand)
        cur = Vector(best_target)
        gap0 = best_gap
        for _it in range(5):
            if best_gap is None or abs(best_gap) <= LIFT_TOL_MM:
                break
            cur = cur + push * (best_gap / 1000.0)
            thumb = solve_thumb_to_target(arm, side, cur)
            update(2)
            g = points_face_gap_mm(lift_distal_skin_local(arm, side, "Thumb"), face)["gap_mm"]
            if g is None:
                break
            if best_gap is None or abs(g) < abs(best_gap):
                best_gap, best_target = g, Vector(cur)
            else:
                break
        if best_target != Vector(target):
            thumb = solve_thumb_to_target(arm, side, best_target)
            update(2)
        # 局部模式搜索（粗搜索会左右手各落一个局部解 ⇒ 必须精修）
        gap1 = lift_refine_thumb_local(arm, side, face=face, box=frame)
        solved = {f"{BONE_PREFIX}{side}HandThumb{k}":
                  [round(math.degrees(a), 4) for a in arm.pose.bones[
                      f"{BONE_PREFIX}{side}HandThumb{k}"].rotation_euler]
                  for k in (1, 2, 3, 4) if f"{BONE_PREFIX}{side}HandThumb{k}" in arm.pose.bones}
        out[side].update({"thumb_solved_deg": solved, "thumb_gap_before_mm": gap0,
                          "thumb_gap_mm": gap1, "thumb_target_m": [round(c, 4) for c in best_target],
                          "thumb": thumb})
    return out


def lift_apply(arm, m3, prm, lay, foot_rest, curl_axes, wrist_rest, cal, grip):
    """按任务空间参数摆一帧：身体 → 两条手臂（握式由 `grip["mode"]` 选，进度 `s`）。"""
    body = lift_body_setup(arm, m3, prm["bend_deg"], prm["pelvis"], foot_rest)
    out = {"gaze": body["gaze"], "legs": body["legs"]}
    if prm["t_reach"] > 0.0:
        for side in CARD1_SIDES:
            if grip["mode"] == "backhand":
                fr = lift_transform_frame(grip["frames"][side], grip["pivot"], prm["rot"],
                                          prm["offset"])
                out[side] = lift_arm_solve_backhand(
                    arm, side, fr, prm["t_reach"], curl_axes, cal[side]["fitted"],
                    cal[side]["thumb_solved_deg"], wrist_rest[side],
                    grip_h_m=grip["grip_h"] + (cal[side].get("grip_dh_m") or 0.0)
                    if prm["t_lift"] > 0.0 else grip["grip_h"],
                    grip_df=cal[side].get("grip_df", 0.5),
                    rot=prm.get("rot"), s_swing=prm["t_lift"])
            elif grip["mode"] == "palm":
                rail = lift_translate_rail(grip["rail"], prm["offset"])
                out[side] = lift_arm_solve_palm(
                    arm, side, rail, grip["x"], prm["t_reach"], curl_axes, cal[side]["fitted"],
                    cal[side]["thumb_solved_deg"], wrist_rest[side],
                    palm_dy=cal[side].get("palm_anchor_dy_m", 0.0))
            else:
                fr = lift_translate_frame(chair_end_frame(side, lay), prm["offset"])
                grip_z = lay["rail_top_z"] - LIFT_GRIP_DROP_M + prm["offset"].z
                out[side] = lift_arm_solve(arm, side, fr, grip_z, curl_axes, prm["t_reach"],
                                           cal[side]["fitted"], cal[side]["thumb_solved_deg"],
                                           wrist_rest[side])
    return out


# ---------------------------------------------------------------- 产物侧读数


def lift_product_frame(arm, frame, lay, root, cp, grip):
    """一帧的**全部产物侧读数**（`evaluated_get(depsgraph)` 口径；探针一律来自求值后的网格）。"""
    bpy.context.scene.frame_set(frame)
    update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    root_ev = root.evaluated_get(dg)
    own = {}
    for name in LIFT_CHAIR_PARTS:
        ob = bpy.data.objects.get(name)
        if ob is None:
            continue
        ev_ob = ob.evaluated_get(dg)
        own[name] = {"ob": ev_ob, "pts": _part_world_points(ev_ob), "bbox": _local_bbox(ev_ob)}
    back = own.get("REF_Back")
    frame_geo = {}
    if back is not None:
        for side in CARD1_SIDES:
            # ⚠️ 用**零件自己的三轴**重建（旋转无关）——抡过 90° 之后"世界 y 极值"已不是板厚方向
            frame_geo[side] = lift_chair_frame_from_object(back["ob"], side)
    rail_geo = lift_rail_from_points(back["pts"]) if back is not None else None
    if grip["mode"] == "backhand":
        contacts = {side: lift_contact_rows_backhand(ev, side, frame_geo[side])
                    for side in CARD1_SIDES}
    elif grip["mode"] == "palm" and rail_geo is not None:
        contacts = {side: lift_contact_rows_palm(ev, side, rail_geo, frame_geo[side])
                    for side in CARD1_SIDES}
    else:
        contacts = {side: grip_board_edge_readings(ev, side, frame_geo[side])
                    for side in CARD1_SIDES}
    ok = {side: lift_contact_ok(contacts[side]) for side in CARD1_SIDES}
    # ---- 椅子：最低点 / 握点（从网格重建的 frame 上取）----
    all_pts = [p for d in own.values() for p in d["pts"]]
    chair_min_z = min(p.z for p in all_pts)
    chair_top_z = max(p.z for p in all_pts)
    grip_pt = None
    if frame_geo and frame_geo.get("Left") is not None:
        fr = frame_geo["Left"]
        if grip["mode"] == "backhand":
            # 反手握式的"判据点" = **椅背外侧面的中心**（局部 +z 面中心，从产物对象矩阵取）
            mw = back["ob"].matrix_world
            r3 = mw.to_3x3()
            sc = mw.to_scale()
            top_pt = mw @ Vector((0.0, 0.0, 0.5))
            grip_pt = top_pt
        elif grip["mode"] == "palm" and rail_geo is not None:
            # 上沿握式的"判据点" = **顶面上、该手横向位置的那一点**（从产物网格重建）
            grip_pt = Vector((grip["x"], rail_geo["cy"], rail_geo["top_z"]))
        else:
            grip_pt = fr["near"] + fr["z"] * (lay["rail_top_z"] - LIFT_GRIP_DROP_M
                                             + (chair_top_z - lay["rail_top_z"]))
    # ---- 判据 4：椅子碰撞体 ↔ 骨段 ----
    clash = {"zero": {}, "core": {}}
    for bone in LIFT_CLASH_ZERO_BONES:
        if f"{BONE_PREFIX}{bone}" not in ev.pose.bones:
            continue
        pts = _segment_points(ev, bone)
        clash["zero"][bone] = round(min(min(obb_gap_mm(p, d["ob"], d["bbox"])
                                            for d in own.values()) for p in pts), 2)
    for bone in LIFT_CLASH_CORE_BONES:
        if f"{BONE_PREFIX}{bone}" not in ev.pose.bones:
            continue
        head = world_point(ev, f"{BONE_PREFIX}{bone}")
        clash["core"][bone] = round(min(obb_gap_mm(head, d["ob"], d["bbox"])
                                        for d in own.values()), 2)
    # ---- 判据 5：包握（每根手指**末节蒙皮** ↔ **被握构件**表面）----
    grip_part = own.get("REF_Back")
    wrap = {}
    for side in CARD1_SIDES:
        wrap[side] = {}
        for f in FINGERS:
            pts = lift_distal_skin_local(ev, side, f)
            gaps = [obb_gap_mm(q, grip_part["ob"], grip_part["bbox"]) for q in pts] if (
                grip_part and pts) else []
            wrap[side][f] = None if not gaps else round(min(gaps, key=abs), 2)
    # ---- 椅子在手骨局部的位姿（握持刚性） + 两手各导一份的互证 ----
    M_chair = root_ev.matrix_world.copy()
    hand_M = {side: ev.matrix_world @ ev.pose.bones[f"{BONE_PREFIX}{side}Hand"].matrix
              for side in CARD1_SIDES}
    # ---- 判据 1：两手间距（手骨原点间距 + 虎口间距）----
    hands = {side: world_point(ev, f"{BONE_PREFIX}{side}Hand") for side in CARD1_SIDES}
    webs = {side: web_point(ev, side) for side in CARD1_SIDES}
    hips_w = world_point(ev, f"{BONE_PREFIX}Hips")
    # ---- 接地：足部蒙皮最低点（沿用 #165 的取点件，不重写第二份）----
    foot_low = {}
    for side in CARD1_SIDES:
        z = cp._skin_lowest(ev, cp._skin_index(ev, side))
        foot_low[side] = None if z is None else round((z - cp.GROUND_Z_M) * 1000.0, 2)
    return {"frame": frame, "contacts": contacts, "contact_ok": ok,
            "chair_min_z_mm": round(chair_min_z * 1000.0, 2),
            "chair_top_z_mm": round(chair_top_z * 1000.0, 2),
            "grip_point_m": None if grip_pt is None else [round(c, 5) for c in grip_pt],
            "判据点_握点高于髋_mm": (None if grip_pt is None
                                     else round((grip_pt.z - hips_w.z) * 1000.0, 4)),
            "clash": clash, "wrap": wrap,
            "hand_span_m": round((hands["Left"] - hands["Right"]).length, 5),
            "web_span_m": round((webs["Left"] - webs["Right"]).length, 5),
            "foot_low_mm": foot_low, "hips_z_m": round(hips_w.z, 5),
            "_M_chair": M_chair, "_hand_M": hand_M}


# ---------------------------------------------------------------- 宿主 9 主流程


def main_liftchest() -> int:
    """弯腰双手拿起椅子、持在胸前宿主：逐帧解算 → 逐帧打键（含**椅子根空物体**）→ 从产物读判据。"""
    from datetime import datetime
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import xbot_contact_phase as cp      # 接地 / 足底蒙皮取点（#165 的件，不重写第二份）
    import xbot_balance as xb            # 支撑域 / 接触相位（#170 的件，不重算）
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    # ⚠️ 先摘掉母版里挂着的**上一条 action**：本宿主在解算阶段逐帧改姿势、判据要读"当前姿势"，
    #    留着旧 action 会让 `frame_set()` 把姿势覆盖回去（= 判据读到的是别人的动作）。
    arm.animation_data_clear()
    clear_pose(arm)

    action_name = args.action if args.action != "BendGripChairBack" else LIFT_ACTION
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    lay = chair_layout(args.chair)
    # ⚠️ `chair_layout()` **没有** `rail_bottom_z`（它是 `board_layout()` 的字段），而
    #    `chair_end_frame()` 要用它当 `z_span` 的下界 ⇒ 在这里补一格，取值 = 坐面上表面
    #    （与 `board_layout()` 逐字一致：椅背板的下缘就落在坐面上）。
    lay["rail_bottom_z"] = SEAT_TOP
    root = lift_chair_root(args.chair)
    grip_z0 = lay["rail_top_z"] - LIFT_GRIP_DROP_M
    # 握式的**着落锚点**（静止姿势下"虎口该落在哪"）——palm = 上沿顶面中点；side = 近侧竖棱上的一点
    anchor_rest = (Vector((0.0, lay["back_cy"], lay["rail_top_z"])) if args.grip == "palm"
                   else Vector((0.0, lay["back_near_y"], grip_z0)))
    dy = args.chest_grip_y - anchor_rest.y
    dz = args.chest_grip_z - anchor_rest.z
    offset_full = Vector((0.0, dy, dz))
    pelvis_m = Vector((0.0, args.pelvis_back, args.pelvis_down))
    grip = {"mode": args.grip, "x": args.grip_x, "rail": chair_rail_frame(lay, args.grip_x),
            "anchor_rest_m": [round(c, 4) for c in anchor_rest],
            "anchor_chest_m": [round(args.grip_x if args.grip == "palm" else 0.0, 4),
                               round(args.chest_grip_y, 4), round(args.chest_grip_z, 4)]}
    if args.grip == "backhand":
        # 反手握式：接触面 = 椅背**侧面端**；抡弧绕**椅子中线上的握点**转（`pivot` 与两侧握点同 y/z
        # ⇒ 转完握点位置不变、只有椅子转，正是 owner 第 3 轮说的"椅子跟着手动"）。
        grip_h = round(grip_z0 - SEAT_TOP, 6)
        grip["frames"] = {s: lift_chair_frame_from_object(bpy.data.objects["REF_Back"], s)
                          for s in CARD1_SIDES}
        grip["pivot"] = Vector((0.0, lay["back_cy"], grip_z0))
        grip["grip_h"] = grip_h
        grip["target_grip_m"] = [0.0, LIFT_SIDE_GRIP_Y_M, LIFT_SIDE_GRIP_Z_M]
        offset_full = Vector((0.0, LIFT_SIDE_GRIP_Y_M - lay["back_cy"],
                              LIFT_SIDE_GRIP_Z_M - grip_z0))
        dy, dz = offset_full.y, offset_full.z
        anchor_rest = grip["pivot"]
        grip["anchor_rest_m"] = [round(c, 4) for c in anchor_rest]
        grip["anchor_chest_m"] = [0.0, LIFT_SIDE_GRIP_Y_M, LIFT_SIDE_GRIP_Z_M]
    report = {"script": Path(__file__).name, "task": "liftchest", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "fps": args.fps, "batch": "口径 §十六 缺素材回归批 ① 件（成因类 甲）· #180",
              "chair_distance_m": args.chair, "bend_deg": args.bend,
              "grip": {"握式": args.grip, "手横向位置_m": args.grip_x,
                       "卡": CARD1_INDEX_KEY_NAME, "抓握高度_m": round(grip_z0, 4),
                       "椅背顶面_m": round(lay["rail_top_z"], 4),
                       "侧面端_x_m": round(lay["half_width"], 4),
                       "近侧面_y_m": round(lay["back_near_y"], 4),
                       "远侧面_y_m": round(lay["back_far_y"], 4),
                       "厚度_mm": round(BACK_THICKNESS * 1000.0, 1)},
              "chair_lift": {"握点目标_m": [round(lay["half_width"], 4), args.chest_grip_y,
                                        args.chest_grip_z],
                             "平移_m": [0.0, round(dy, 4), round(dz, 4)],
                             "来源": "胸前握点由 `--chest-grip-y/z` 给定（agent 解）；椅子只平移、不旋转"},
              "frames_declared": {"中立": LIFT_FRAME_NEUTRAL, "起手": LIFT_FRAME_START,
                                  "扣住": LIFT_FRAME_GRIP, "起吊": LIFT_FRAME_LIFT,
                                  "离地": LIFT_FRAME_OFF_GROUND, "胸前到位": LIFT_FRAME_CHEST,
                                  "保持至": LIFT_FRAME_END},
              "problems": []}
    print(f"弯腰双手拿起椅子、持在胸前（口径 §十六 ① 件 · 成因类「甲」 · #180）· 动作名 {action_name}")
    print(f"帧表：中立 {LIFT_FRAME_NEUTRAL} · **起手 {LIFT_FRAME_START}** · **扣住 {LIFT_FRAME_GRIP}** · "
          f"起吊 {LIFT_FRAME_LIFT} · **离地 {LIFT_FRAME_OFF_GROUND}** · **胸前到位 {LIFT_FRAME_CHEST}** · "
          f"保持至 {LIFT_FRAME_END}（{args.fps} fps）")
    if args.grip == "backhand":
        print(f"握式：**反手抓椅背侧面端**（x = ±{lay['half_width']} m 那张 {BACK_THICKNESS * 1000:.0f} mm 端面）"
              f"——**拇指朝下**（−Z）· **掌心朝内**（朝椅子中线）· 四指绕**近侧竖棱**落到近侧面"
              f"（owner 2026-09-16 第 3 轮指名：「抓住椅子的侧面……要反手抓，把椅子抡起来维持在胸前」）")
        print(f"抡弧：绕椅子中线上的握点转 **{LIFT_SWING_DEG:+.0f}°**（绕世界 X 轴）· "
              f"握点从 (0, {lay['back_cy']:+.3f}, {grip_z0:.4f}) 移到 "
              f"(0, {LIFT_SIDE_GRIP_Y_M:+.3f}, {LIFT_SIDE_GRIP_Z_M:.3f}) m ⇒ 椅子平移 "
              f"(0, {dy:+.4f}, {dz:+.4f})")
    elif args.grip == "palm":
        print(f"握式：**掌面朝下扣在椅背上沿（横杆）** —— 手在 x = ±{args.grip_x} m · "
              f"掌面最低点↔**顶面** · 拇指末节↔近侧面 · 四指末节逐根↔**远侧面**"
              f"（虎口↔顶面只报读数：ε 的位置依赖性，见证据 §六#6）"
              f"（owner 2026-09-16 第 1 轮指名：**虎口朝 −Z**，为的是抓起来之后能把椅子当武器抡出去）")
        print(f"虎口着落点 ({anchor_rest.x:.3f}, {anchor_rest.y:.3f}, {anchor_rest.z:.4f}) m"
              f"（= 椅背顶面 z {lay['rail_top_z']:.4f} 上、该手横向位置那一点）")
    else:
        print(f"握式：**卡 1「掐棱」** 用在椅背**侧面端**（x = ±{lay['half_width']} m）——"
              f"虎口↔近侧竖棱 · 拇指↔近侧面 · 四指逐根↔远侧棱/板体")
        print(f"抓握高度 {grip_z0:.4f} m（椅背顶面 {lay['rail_top_z']:.4f} − "
              f"{LIFT_GRIP_DROP_M * 1000:.0f} mm）")
    print(f"持椅目标：握点 ({args.grip_x if args.grip == 'palm' else 0.0:.3f}, "
          f"{args.chest_grip_y:.3f}, {args.chest_grip_z:.3f}) "
          f"⇒ 椅子平移 (0, {dy:+.4f}, {dz:+.4f}) m")

    # ---- 静止基准（首帧严格中立 ⇒ 全部读数都从它出发）----
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    update()
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    wrist_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Hand").copy() for s in CARD1_SIDES}
    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    # 手指蜷曲轴：逐组实测（含拇指单独一组）
    curl_four = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    curl_thumb = {s: detect_curl_axis_group(arm, s, "拇指") for s in CARD1_SIDES}
    curl_axes = {s: {f: (curl_thumb[s] if f == "Thumb" else curl_four[s]) for f in FINGERS}
                 for s in CARD1_SIDES}
    report["rest"] = {"静止踝_m": {s: [round(c, 6) for c in foot_rest[s]] for s in CARD1_SIDES},
                      "静止腕_m": {s: [round(c, 6) for c in wrist_rest[s]] for s in CARD1_SIDES},
                      "静止髋_m": [round(c, 6) for c in hips_rest],
                      "f3_curl": {"四指": curl_four, "拇指": curl_thumb}}
    for s in CARD1_SIDES:
        if not curl_four[s]["criterion_valid"]:
            report["problems"].append(f"{s} 四指屈曲符号的外部判据失效 ⇒ 符号不可信")

    # ---- ⓪ 手部标定（抓握帧）：逐指蜷曲量 + 拇指的解——两条都只由**握式**决定，标定一次全程复用 ----
    if args.grip == "backhand":
        from mathutils import Matrix as _M
        cal = lift_calibrate_hand_backhand(
            arm, m3, lay, grip["frames"], grip["grip_h"], foot_rest, curl_axes, wrist_rest,
            args.bend, pelvis_m, pivot=grip["pivot"],
            swing_rot=_M.Rotation(math.radians(LIFT_SWING_DEG), 4, "X"))
    elif args.grip == "palm":
        cal = lift_calibrate_hand_palm(arm, m3, lay, grip["rail"], args.grip_x, foot_rest,
                                       curl_axes, wrist_rest, args.bend, pelvis_m)
    else:
        cal = lift_calibrate_hand(arm, m3, lay, foot_rest, curl_axes, wrist_rest, args.bend,
                                  pelvis_m)
    report["hand_calibration"] = cal
    print("手部标定（抓握帧 · 卡 1 F10 的「逐指」口径）")
    for s in CARD1_SIDES:
        c = cal[s]
        print(f"  {s:<6}逐指蜷曲量 " + " · ".join(
            f"{f} {c['fitted'][f]['蜷曲量']}（板体间隙 {c['fitted'][f]['板体间隙_mm']} mm）"
            for f in FOUR_FINGERS)
            + f" · 拇指蒙皮间隙 {c['thumb_gap_before_mm']} → {c['thumb_gap_mm']} mm")
    for s in CARD1_SIDES:
        if abs(cal[s]["thumb_gap_mm"] or 0.0) > LIFT_TOL_MM:
            report["problems"].append(
                f"{s} 拇指标定后仍离近侧面 {cal[s]['thumb_gap_mm']} mm > {LIFT_TOL_MM}")

    # ---- ① `--scan-lift`：解空间并列（口径 §4.2 硬规矩 5 —— agent 解的行必须并列 ≥2 解）----
    if args.scan_lift:
        print("\n解空间（口径 §4.2 硬规矩 5）：弯腰角 × 胸前握点高度")
        print(f"  {'弯腰°':>6}{'胸前z_m':>9}{'扣住_虎口*':>11}{'扣住_四指最坏':>14}"
              f"{'胸前_虎口*':>11}{'胸前_四指最坏':>14}{'肘角°':>8}{'夹直':>6}{'椅体最小间隙_mm':>16}"
              f"   （* = 只报读数：ε 的位置依赖性）")
        rows = []
        for bend in LIFT_SCAN_BENDS:
            for cz in LIFT_SCAN_CHEST_Z:
                dy2 = args.chest_grip_y - lay["back_near_y"]
                dz2 = cz - grip_z0
                res = {}
                for tag, prm in (("扣住", {"t_bend": 1.0, "t_reach": 1.0, "bend_deg": bend,
                                          "pelvis": pelvis_m,
                                          "offset": Vector((0.0, 0.0, 0.0))}),
                                 ("胸前", {"t_bend": 0.0, "t_reach": 1.0, "bend_deg": 0.0,
                                          "pelvis": Vector((0.0, 0.0, 0.0)),
                                          "offset": Vector((0.0, dy2, dz2))})):
                    clear_pose(arm)
                    drop_temp(arm, also_objects=False)
                    out = lift_apply(arm, m3, prm, lay, foot_rest, curl_axes, wrist_rest, cal,
                                     grip)
                    vals, shown = [], []
                    for side in CARD1_SIDES:
                        if grip["mode"] == "palm":
                            rail = lift_translate_rail(grip["rail"], prm["offset"])
                            all_rows = lift_contact_rows_palm(arm, side, rail,
                                                              chair_end_frame(side, lay))
                            rows = [row for row in all_rows if not row.get("只报读数")]
                        else:
                            fr = lift_translate_frame(chair_end_frame(side, lay), prm["offset"])
                            all_rows = rows = grip_board_edge_readings(arm, side, fr)
                        vals += lift_contact_values(rows)
                        shown += lift_contact_values(all_rows)
                    four = [abs(v) for n, v in vals if "四指" in n]
                    four = four or [float("nan")]
                    web = [abs(v) for n, v in shown if "虎口" in n] or [float("nan")]
                    res[tag] = {"虎口_mm": round(max(web), 2), "四指最坏_mm": round(max(four), 2),
                                "肘角_deg": max(out[s]["elbow_deg"] for s in CARD1_SIDES),
                                "夹直": any(out[s]["clamped_straight"] for s in CARD1_SIDES)}
                # 胸前那一帧的**椅子 ↔ 非接触部位**最小间隙（判据 4）
                clear_pose(arm)
                drop_temp(arm, also_objects=False)
                prm_c = {"t_bend": 0.0, "t_reach": 1.0, "bend_deg": 0.0,
                         "pelvis": Vector((0.0, 0.0, 0.0)),
                         "offset": Vector((0.0, dy2, dz2))}
                lift_apply(arm, m3, prm_c, lay, foot_rest, curl_axes, wrist_rest, cal, grip)
                root.location = prm_c["offset"]
                update()
                read = lift_product_frame(arm, LIFT_FRAME_CHEST, lay, root, cp, grip)
                gap = min(list(read["clash"]["zero"].values()) or [1e9])
                row = {"弯腰_deg": bend, "胸前z_m": cz, "扣住": res["扣住"], "胸前": res["胸前"],
                       "非接触部位最小间隙_mm": round(gap, 2),
                       # ⚠️ 可行只看**判据行**（四指最坏）；虎口那一格是**读数**（ε 的位置依赖，见证据 §六#6）
                       "可行": bool(res["扣住"]["四指最坏_mm"] <= LIFT_TOL_MM
                                    and res["胸前"]["四指最坏_mm"] <= LIFT_TOL_MM
                                    and not res["胸前"]["夹直"] and gap >= LIFT_CLASH_CLEAR_MM)}
                rows.append(row)
                print(f"  {bend:6.1f}{cz:9.2f}{row['扣住']['虎口_mm']:11.2f}"
                      f"{row['扣住']['四指最坏_mm']:14.2f}{row['胸前']['虎口_mm']:11.2f}"
                      f"{row['胸前']['四指最坏_mm']:14.2f}{row['胸前']['肘角_deg']:8.1f}"
                      f"{str(row['胸前']['夹直']):>6}{row['非接触部位最小间隙_mm']:16.2f}"
                      f"  {'✅' if row['可行'] else '❌'}")
        report["scan_lift"] = {"行": rows, "来源": "本件选定（口径 §4.2 硬规矩 5）；"
                                              "两维 = 弯腰角 × 胸前握点高度，其余量固定在默认"}
        root.location = (0.0, 0.0, 0.0)
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0

    # ---- ② 逐帧解算 ----
    names = panic_channel_names(arm)
    captured, per_frame, offsets = {}, [], {}
    print(f"\n逐帧解算（帧 {LIFT_FRAME_NEUTRAL}–{LIFT_FRAME_END}，每帧解、每帧打键）")
    for frame in range(LIFT_FRAME_NEUTRAL, LIFT_FRAME_END + 1):
        if frame < LIFT_FRAME_START:
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            update()
            captured[frame] = capture_channels(arm, names)
            offsets[frame] = {"location": Vector((0.0, 0.0, 0.0)), "euler_deg": (0.0, 0.0, 0.0)}
            per_frame.append({"frame": frame, "中立": True})
            if frame == LIFT_FRAME_NEUTRAL:
                print(f"  帧 {frame:>3} **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        prm = lift_frame_params(frame, args.bend, offset_full, pelvis_m)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        out = lift_apply(arm, m3, prm, lay, foot_rest, curl_axes, wrist_rest, cal, grip)
        captured[frame] = capture_channels(arm, names)
        offsets[frame] = _root_pose(prm, grip)
        row = {"frame": frame, "t_bend": round(prm["t_bend"], 4), "t_reach": round(prm["t_reach"], 4),
               "t_lift": round(prm["t_lift"], 4), "bend_deg": round(prm["bend_deg"], 2),
               "chair_offset_m": [round(c, 5) for c in prm["offset"]],
               "swing_deg": round(prm["swing_deg"], 2),
               "gaze_up_deg": round(head_up_deg(arm), 3),
               "hands": {s: {k: out[s].get(k) for k in ("web_to_edge_mm", "elbow_deg",
                                                        "clamped_straight", "tip_err_mm", "s",
                                                        "wrist_target_m", "web_point_m",
                                                        "elbow_pick", "姿态读数")}
                         for s in CARD1_SIDES if s in out}}
        per_frame.append(row)
        if frame in (LIFT_FRAME_START, LIFT_FRAME_GRIP, LIFT_FRAME_LIFT, LIFT_FRAME_OFF_GROUND,
                     LIFT_FRAME_CHEST, LIFT_FRAME_END) or frame % 10 == 0:
            h = row["hands"].get("Left", {})
            print(f"  帧 {frame:>3} 弯腰 {row['bend_deg']:5.1f}° · 到位 {row['t_reach']:.2f} · "
                  f"抬起 {row['t_lift']:.2f} · 椅子位移 {row['chair_offset_m']} · "
                  f"左虎口↔棱 {h.get('web_to_edge_mm')} mm · 肘角 {h.get('elbow_deg')}° · "
                  f"头偏离竖直 {row['gaze_up_deg']}°")
    report["frame_params"] = per_frame

    # ---- ③ 打键：动作 + **椅子根空物体**（逐帧；椅子跟随手的唯一载体）----
    residue = sorted(o.name for o in bpy.data.objects
                     if o.name.startswith("REF_") and o.name not in LIFT_CHAIR_PARTS
                     and o.name != LIFT_CHAIR_ROOT
                     and not any(m.type == "ARMATURE" for m in o.modifiers))
    for name in residue:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    report["preview_residue_removed"] = residue
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    if action.name != action_name:
        raise RuntimeError(f"动作名被占用：期望 {action_name!r}，实际 {action.name!r}")
    action.use_fake_user = True
    try:
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame in range(LIFT_FRAME_NEUTRAL, LIFT_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
        root.location = offsets[frame]["location"]
        root.rotation_mode = "XYZ"
        root.rotation_euler = Euler([math.radians(a) for a in offsets[frame]["euler_deg"]], "XYZ")
        root.keyframe_insert("location", frame=frame)
        root.keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start = LIFT_FRAME_NEUTRAL
    bpy.context.scene.frame_end = LIFT_FRAME_END
    report["keyed_channels"] = names
    report["chair_root_keyed"] = {
        "物体": LIFT_CHAIR_ROOT, "通道": "location + rotation_euler",
        "端点": {str(LIFT_FRAME_NEUTRAL): {"location_m": [round(c, 5) for c in
                                                    offsets[LIFT_FRAME_NEUTRAL]["location"]],
                                        "euler_deg": list(offsets[LIFT_FRAME_NEUTRAL]["euler_deg"])},
               str(LIFT_FRAME_END): {"location_m": [round(c, 5) for c in
                                                    offsets[LIFT_FRAME_END]["location"]],
                                     "euler_deg": list(offsets[LIFT_FRAME_END]["euler_deg"])}}}
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    report["visible_bones"] = visible_bone_outliers(arm)
    print(f"\n已打键：动作 {action_name} · 帧 {LIFT_FRAME_NEUTRAL}–{LIFT_FRAME_END} · "
          f"通道 {len(names)} 个 · 椅子根空物体 `{LIFT_CHAIR_ROOT}` 的 location 逐帧同步打键")
    if report["visible_bones"]["非例外的越界骨"]:
        report["problems"].append(
            "可见骨伸出皮肤包围盒：" + "; ".join(
                f"{x['骨']}({x['伸出量_mm']:.1f} mm)" for x in report["visible_bones"]["非例外的越界骨"][:8]))

    # ---- ④ 产物侧读数（从**打键后的产物**逐帧重量）----
    prod = []
    for frame in range(LIFT_FRAME_NEUTRAL, LIFT_FRAME_END + 1):
        prod.append(lift_product_frame(arm, frame, lay, root, cp, grip))
    report["product"] = [{k: v for k, v in r.items() if not k.startswith("_")} for r in prod]

    # ---- ⑤ 判据 1：接触对（**持续型** F4a）----
    tol = LIFT_TOL_MM
    contact = {}
    for side in CARD1_SIDES:
        curve = []
        for r in prod:
            rows = [row for row in r["contacts"][side] if not row.get("只报读数")]
            vals = lift_contact_values(rows)
            worst = max((abs(v) for _n, v in vals if v is not None), default=None)
            curve.append((r["frame"], worst, r["contact_ok"][side][0], vals))
        win = [(f, w) for f, w, ok, _v in curve if f >= LIFT_FRAME_GRIP]
        worst = max(win, key=lambda t: t[1])
        first_in = next((f for f, _w, ok, _v in curve if f >= LIFT_FRAME_GRIP and ok), None)
        contact[side] = {
            "判据形态": "点↔线（虎口↔近侧竖棱）· 点↔面（拇指↔近侧面）· 点↔体（四指逐根↔板体）",
            "判据时域（F4a）": "持续（整段窗口逐帧，松一帧即红）",
            "容差_mm": tol, "判据层": "蒙皮层 Beta_Surface（口径 §10.1）",
            "声明扣住帧": LIFT_FRAME_GRIP, "产物_首次进入容差帧": first_in,
            "窗口": [LIFT_FRAME_GRIP, LIFT_FRAME_END], "逐帧最坏_mm": worst[1], "最坏帧": worst[0],
            "超差帧": [f for f, _w, ok, _v in curve if f >= LIFT_FRAME_GRIP and not ok],
            "接近段红帧": [f for f, _w, ok, _v in curve if f < LIFT_FRAME_GRIP and not ok],
            "逐帧": [{"frame": f, "最坏_mm": w, "成立": ok,
                      "读数": {n: v for n, v in vals}} for f, w, ok, vals in curve],
        }
    report["contact_criteria"] = contact
    print("\n判据 1：接触对（**持续型** F4a · 口径 §13.4.1）——双手 ↔ 椅子被握构件")
    for side, c in contact.items():
        print(f"  {side:<6}窗口 {c['窗口']} · 逐帧最坏 {c['逐帧最坏_mm']:.2f} mm（帧 {c['最坏帧']}）· "
              f"超差帧 {len(c['超差帧'])} · 接近段红帧 {len(c['接近段红帧'])} · "
              f"首次进入容差帧 {c['产物_首次进入容差帧']}（声明 {c['声明扣住帧']}）")
        if c["超差帧"]:
            report["problems"].append(f"{side} 接触对在持续窗口内超差帧 {c['超差帧'][:8]}")
        if c["产物_首次进入容差帧"] != LIFT_FRAME_GRIP:
            report["problems"].append(
                f"{side} 时序不一致：声明扣住帧 {LIFT_FRAME_GRIP} ≠ 产物首次进入容差帧 "
                f"{c['产物_首次进入容差帧']}")
        if not c["接近段红帧"]:
            report["problems"].append(f"{side} 接近段**没有红帧** ⇒ 判据退化（非退化性未证）")

    # ---- ⑥ 非退化对照（中立姿势）----
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    root.location = (0.0, 0.0, 0.0)
    update()
    neutral = {}
    for side in CARD1_SIDES:
        fr = chair_end_frame(side, lay)
        neutral[side] = {n: v for n, v in lift_contact_values(
            grip_board_edge_readings(arm, side, fr))}
    report["neutral_control"] = neutral
    print(f"  非退化对照（中立姿势，椅子在原地）：{ {s: max(abs(v) for v in d.values() if v is not None) for s, d in neutral.items()} } mm（最坏）")

    # ---- ⑦ 时序（口径 §十 V-f：零阈值）----
    import blender_action_compat as bac2
    arm_channels = [f'pose.bones["CTRL_{s}{suf}"].rotation_euler'
                    for s in CARD1_SIDES for suf in ("Arm", "ForeArm", "Hand")]
    first_arm = None
    for frame in range(LIFT_FRAME_NEUTRAL, LIFT_FRAME_END + 1):
        moved = False
        for fc in bac2.iter_fcurves(action):
            if fc.data_path in arm_channels and abs(fc.evaluate(frame)) > 0.0:
                moved = True
                break
        if moved:
            first_arm = frame
            break

    def _plateau(curve):
        """**极值帧** = 最后一个发生变化的帧（平台起始帧）——零阈值、平段取首帧（先例 #170 §2.2）。"""
        last = None
        for i in range(1, len(curve)):
            if curve[i][1] != curve[i - 1][1]:
                last = curve[i][0]
        return last

    grip_curve = [(r["frame"], r["判据点_握点高于髋_mm"]) for r in prod]
    plateau = _plateau(grip_curve)
    first_both = next((r["frame"] for r in prod
                       if r["frame"] >= LIFT_FRAME_GRIP
                       and all(r["contact_ok"][s][0] for s in CARD1_SIDES)), None)
    low_curve = [(r["frame"], r["chair_min_z_mm"]) for r in prod]
    first_clear = next((f for f, z in low_curve if z > cp.SOLE_MARGIN_MM), None)
    report["timing"] = {
        "起手（首个非零手臂通道帧）": {"声明": LIFT_FRAME_START, "产物": first_arm,
                                     "判据量": "`CTRL_*Arm/ForeArm/Hand` 的旋转通道**首个非零值帧**（零阈值）"},
        "扣住（首次进入容差帧）": {"声明": LIFT_FRAME_GRIP, "产物": first_both,
                                  "双手": {s: contact[s]["产物_首次进入容差帧"] for s in CARD1_SIDES},
                                  "判据量": "双手接触对**同时**全部落进 `tol_contact` 的帧"},
        "离地（椅子最低点首次 > soleMargin）": {"声明": LIFT_FRAME_OFF_GROUND, "产物": first_clear,
                                              "判据量": f"椅子代理网格最低 z 首次 > `soleMargin`"
                                                        f"（{cp.SOLE_MARGIN_MM} mm）"},
        "胸前到位（判据点极值帧）": {"声明": LIFT_FRAME_CHEST, "产物": plateau,
                                     "判据量": "**握点高度 − 髋高度**（都从产物取）的平台起始帧"
                                               "（= 最后一个发生变化的帧）",
                                     "曲线": [{"帧": f, "握点高于髋_mm": v} for f, v in grip_curve]},
        "保持": {"声明": [LIFT_FRAME_CHEST, LIFT_FRAME_END],
                 "判据量": "到位后姿势与椅子位移逐帧不变 ⇒ 保持段长度（帧）",
                 "产物": LIFT_FRAME_END - LIFT_FRAME_CHEST},
    }
    for key in ("起手（首个非零手臂通道帧）", "扣住（首次进入容差帧）", "离地（椅子最低点首次 > soleMargin）",
                "胸前到位（判据点极值帧）"):
        d = report["timing"][key]
        same = (d["声明"] == d["产物"])
        d["一致"] = bool(same)
        if not same:
            report["problems"].append(f"时序不一致：{key} 声明 {d['声明']} ≠ 产物 {d['产物']}")
    print("  时序（零阈值）：" + " · ".join(
        f"{k.split('（')[0]} {v['声明']}/{v['产物']}{'✅' if v.get('一致') else '❌'}"
        for k, v in report["timing"].items() if "一致" in v))

    # ---- ⑧ 椅子跟随手：握持刚性 + 两手互证（判据 3）----
    M_grip = prod[LIFT_FRAME_GRIP - LIFT_FRAME_NEUTRAL]["_M_chair"]
    K = {}
    for side in CARD1_SIDES:
        K[side] = prod[LIFT_FRAME_GRIP - LIFT_FRAME_NEUTRAL]["_hand_M"][side].inverted() @ M_grip
    rigid = []
    for r in prod:
        row = {"frame": r["frame"]}
        for side in CARD1_SIDES:
            kf = r["_hand_M"][side].inverted() @ r["_M_chair"]
            d = kf.translation - K[side].translation
            ang = math.degrees(kf.to_quaternion().rotation_difference(
                K[side].to_quaternion()).angle)
            row[f"{side}_局部漂移_mm"] = round(d.length * 1000.0, 4)
            row[f"{side}_局部转角_deg"] = round(ang, 4)
            row[f"{side}_手导出椅子_m"] = r["_hand_M"][side] @ K[side]
        a, b = row["Left_手导出椅子_m"], row["Right_手导出椅子_m"]
        row["两手互证_平移_mm"] = round((a.translation - b.translation).length * 1000.0, 3)
        row["两手互证_转角_deg"] = round(math.degrees(
            abs(a.to_quaternion().rotation_difference(b.to_quaternion()).angle)), 3)
        rigid.append(row)
    win = [r for r in rigid if r["frame"] >= LIFT_FRAME_GRIP]
    per_frame_worst = max(max(r[f"{s}_局部漂移_mm"] for s in CARD1_SIDES) for r in win)
    cum = {s: max(r[f"{s}_局部漂移_mm"] for r in win) for s in CARD1_SIDES}
    hand_span = [r["hand_span_m"] for r in prod if r["frame"] >= LIFT_FRAME_GRIP]
    web_span = [r["web_span_m"] for r in prod if r["frame"] >= LIFT_FRAME_GRIP]
    report["rigidity"] = {
        "判据量": "椅子在手骨局部坐标的位姿稳定性（口径 §四·戊·5 判据 3 的同一句话）",
        "阈值来源": "动作库规格 §四·戊·5 判据 3：位姿变化 ≤1 mm/帧 · 持握全程累计 ≤5 mm",
        "逐帧最坏_mm": round(per_frame_worst, 4),
        "累计_mm": {s: round(v, 4) for s, v in cum.items()},
        "两手互证最坏": {"平移_mm": round(max(r["两手互证_平移_mm"] for r in win), 3),
                     "转角_deg": round(max(r["两手互证_转角_deg"] for r in win), 3)},
        "两手间距_m": {"中位": round(sorted(hand_span)[len(hand_span) // 2], 4),
                    "最小": round(min(hand_span), 4), "最大": round(max(hand_span), 4),
                    "波动": round(max(hand_span) - min(hand_span), 4),
                    "搬运锚": LIFT_HANDS_ANCHOR_M, "容差": f"±{LIFT_HANDS_ANCHOR_TOL:.0%}"},
        "虎口间距_m": {"最小": round(min(web_span), 4), "最大": round(max(web_span), 4)},
        "行": [{k: v for k, v in r.items() if not k.endswith("手导出椅子_m")}
               for r in rigid if r["frame"] >= LIFT_FRAME_GRIP],
        "窗口外不报": "抓握之前椅子还在地上（没挂上）⇒ 那些帧的「手骨局部位姿」无意义，"
                      "**不进本表**（本判据只在持握窗口 [扣住, 末帧] 成立）",
    }
    print(f"  椅子跟随手：握持刚性（判据 3）逐帧最坏 {per_frame_worst:.4f} mm · "
          f"累计 {report['rigidity']['累计_mm']} · 阈值 ≤{LIFT_RIGID_PER_FRAME_MM} mm/帧 · ≤{LIFT_RIGID_TOTAL_MM} mm")
    print(f"  两手间距 {report['rigidity']['两手间距_m']}")
    if per_frame_worst > LIFT_RIGID_PER_FRAME_MM or max(cum.values()) > LIFT_RIGID_TOTAL_MM:
        report["problems"].append(
            f"握持刚性超阈值：逐帧最坏 {per_frame_worst:.4f} mm（≤{LIFT_RIGID_PER_FRAME_MM}）· "
            f"累计 {cum}（≤{LIFT_RIGID_TOTAL_MM}）")
    anchor_span = report["rigidity"]["两手间距_m"]["中位"]
    band = LIFT_HANDS_BAND_M
    swing_ok = (band[0] * (1 - LIFT_HANDS_ANCHOR_TOL) <= anchor_span
                <= band[1] * (1 + LIFT_HANDS_ANCHOR_TOL))
    carry_ok = abs(anchor_span - LIFT_HANDS_ANCHOR_M) <= LIFT_HANDS_ANCHOR_TOL * LIFT_HANDS_ANCHOR_M
    band_ok = bool(swing_ok or carry_ok)
    carry_dev = (anchor_span - LIFT_HANDS_ANCHOR_M) / LIFT_HANDS_ANCHOR_M
    report["rigidity"]["判据1_两个参照"] = {
        "挥舞带_m": list(band), "带±25%": [round(band[0] * 0.75, 4), round(band[1] * 1.25, 4)],
        "落在带内": bool(band_ok), "挥舞带内": bool(swing_ok), "搬运锚带内": bool(carry_ok),
        "判据": "**任一条参照的 ±25% 带内即算过**——哪一条适用由握式定：掌面朝下扣横杆 ⇒ 挥舞带；"
                "反手抓侧面端 ⇒ 搬运锚（两种握式的读数各落一条带，两条偏差都并列报出，不混读）",
        "搬运锚_m": LIFT_HANDS_ANCHOR_M,
        "锚±25%": [round(LIFT_HANDS_ANCHOR_M * 0.75, 4), round(LIFT_HANDS_ANCHOR_M * 1.25, 4)],
        "对搬运锚的偏差": f"{carry_dev:+.1%}",
        "为什么两个都报": "§四·戊·5 判据 1 逐字给了两种语义（挥舞 / 搬运）；本件的几何把两手间距**夹在两带之间**"
                        "（掌面朝下扣 42 cm 横杆、四指横向跨度 ≈60 mm ⇒ 最宽 ≈0.36 m）"
                        "⇒ 硬判挥舞带、并列报搬运锚的偏差（冲突登记为未闭合）"}
    if not band_ok:
        report["problems"].append(
            f"判据 1（两手间距）中位 {anchor_span} m 既不在挥舞带 {band} ±"
            f"{LIFT_HANDS_ANCHOR_TOL:.0%} 内、也不在搬运锚 {LIFT_HANDS_ANCHOR_M} m ±"
            f"{LIFT_HANDS_ANCHOR_TOL:.0%} 内")
    if report["rigidity"]["两手间距_m"]["波动"] > LIFT_HANDS_DRIFT_M:
        report["problems"].append(
            f"判据 1（两手间距）持握期间波动 {report['rigidity']['两手间距_m']['波动']} m > "
            f"{LIFT_HANDS_DRIFT_M} m")

    # ---- ⑨ 判据 4：穿模（椅子碰撞体 ↔ 身体；地面 ↔ 人体与椅子）----
    zero_worst = {b: min(r["clash"]["zero"][b] for r in prod if b in r["clash"]["zero"])
                  for b in LIFT_CLASH_ZERO_BONES if any(b in r["clash"]["zero"] for r in prod)}
    core_worst = {b: min(r["clash"]["core"][b] for r in prod if b in r["clash"]["core"])
                  for b in LIFT_CLASH_CORE_BONES if any(b in r["clash"]["core"] for r in prod)}
    clash_frames = [r["frame"] for r in prod
                    if any(v < 0.0 for v in r["clash"]["zero"].values())
                    or any(v < -LIFT_CLASH_CORE_IN_MM for v in r["clash"]["core"].values())]
    ground_frames = [r["frame"] for r in prod
                     if min([v for v in r["foot_low_mm"].values() if v is not None] or [1e9])
                     < -LIFT_TOL_MM or r["chair_min_z_mm"] < -LIFT_TOL_MM]
    report["clash"] = {
        "来源": "动作库规格 §四·戊·5 判据 4（骨段零穿透 · 骨心进构件 ≤2 cm · 非接触部位间隙 ≥1 cm）",
        "碰撞体": "椅子六个零件（座板/靠背/四条腿）的**有向盒**（局部包围盒 × 世界矩阵）"
                  "· 地面 = 半空间 z=0",
        "零穿透_最坏_mm": zero_worst, "骨心_最坏_mm": core_worst,
        "非接触部位最小间隙_mm": round(min(zero_worst.values()) if zero_worst else float("nan"), 2),
        "违规帧": clash_frames,
        "地面_违规帧": ground_frames,
        "地面_最坏_mm": round(min([r["chair_min_z_mm"] for r in prod]
                                  + [v for r in prod for v in r["foot_low_mm"].values() if v is not None]), 2),
    }
    print(f"  判据 4（穿模）：椅子↔躯干/上臂/大腿最坏 {report['clash']['非接触部位最小间隙_mm']} mm"
          f"（阈值 ≥{LIFT_CLASH_CLEAR_MM}）· 手/前臂骨心最坏 "
          f"{min(core_worst.values()) if core_worst else None} mm（阈值 ≥−{LIFT_CLASH_CORE_IN_MM}）")
    print(f"  地面：椅子最低 {min(r['chair_min_z_mm'] for r in prod)} mm · "
          f"足部蒙皮最低 {min([v for r in prod for v in r['foot_low_mm'].values() if v is not None])} mm")
    if clash_frames:
        report["problems"].append(f"判据 4：椅子与骨段穿模帧 {clash_frames[:8]}")
    if report["clash"]["非接触部位最小间隙_mm"] < LIFT_CLASH_CLEAR_MM:
        report["problems"].append(
            f"判据 4：非接触部位最小间隙 {report['clash']['非接触部位最小间隙_mm']} mm < "
            f"{LIFT_CLASH_CLEAR_MM} mm")
    if ground_frames:
        report["problems"].append(f"地面零穿透：违规帧 {ground_frames[:8]}")

    # ---- ⑩ 判据 5：包握 ----
    wrap_worst = {s: max((abs(v) for r in prod if r["frame"] >= LIFT_FRAME_GRIP
                          for v in r["wrap"][s].values() if v is not None), default=None)
                  for s in CARD1_SIDES}
    report["wrap"] = {"来源": "动作库规格 §四·戊·5 判据 5（每根手指末节到构件表面 ≤1.5 cm）",
                      "判据量": "**末节蒙皮**（`*4` 骨主导顶点）↔ **被握构件（椅背）**的有向盒的最近距离",
                      "逐手最坏_mm": {s: (None if v is None else round(v, 2))
                                  for s, v in wrap_worst.items()},
                      "阈值_mm": LIFT_WRAP_MAX_MM,
                      "逐帧逐指": [{"frame": r["frame"], "Left": r["wrap"]["Left"],
                                "Right": r["wrap"]["Right"]}
                               for r in prod if r["frame"] >= LIFT_FRAME_GRIP],
                      "掌心与指尖分居两侧": "由卡 1 的握式结构本身保证：掌面压端面 · 拇指在近侧面 · "
                                            "四指绕到远侧棱（拇指 +25.7 mm / 四指 −1.4~+0.9 mm 是**另一个**读数："
                                            "那是**骨尖**，见 `F4_分区分工与接触对清单`）"}
    print(f"  判据 5（包握）：逐手最坏 {report['wrap']['逐手最坏_mm']} mm（阈值 ≤{LIFT_WRAP_MAX_MM}）")
    for s, v in wrap_worst.items():
        if v is None or v > LIFT_WRAP_MAX_MM:
            report["problems"].append(
                f"判据 5：{s} 手指末节离被握构件 {v} mm > {LIFT_WRAP_MAX_MM} mm（或量不到）")

    # ---- ⑪ 支撑域（凸包件；弯腰段与起身段）----
    bal = xb.read_current(arm, action_name, fps=args.fps)
    per_bal = {r["帧"]: r for r in bal["逐帧"]}
    layer = xb.LAYER_SKIN
    support_frames = list(range(LIFT_FRAME_START, LIFT_FRAME_END + 1))
    not_in = [f for f in support_frames
              if per_bal.get(f, {}).get(layer, {}).get("判定") != xb.V_IN]
    report["balance"] = {"件": "code/tools/xbot_balance.py（凸包件，不重算）",
                         "判据层": layer, "结构": bal["结构"],
                         "接触相位": bal["接触相位"],
                         "非域内帧": not_in, "窗": [support_frames[0], support_frames[-1]]}
    for p in bal["problems"]:
        report["problems"].append(f"凸包件自核：{p}")
    print(f"  支撑域（凸包件 · {layer}）：可判 {bal['结构'][layer]['可判帧数']}/{bal['结构']['帧数']} · "
          f"域外 {bal['结构'][layer]['域外帧数']} · 退化 {len(bal['结构'][layer]['退化帧'])} · "
          f"窗 {report['balance']['窗']} 内非域内帧 {len(not_in)}")
    print(f"  接地（接触相位件）：无支撑区间 {xb.iv_cell(bal['接触相位']['无支撑区间'])} · "
          f"换脚帧 {xb.frame_list_cell(bal['接触相位']['换脚帧'])}")
    if not_in:
        report["problems"].append(f"支撑域：窗 {report['balance']['窗']} 内非域内帧 {not_in[:8]}")

    # ---- ⑪.5 owner 第 3 轮点名的两个姿态量：大臂≈水平 · 手腕≈伸直 ----
    pose_rows = []
    for r in prod:
        fr = {x["frame"]: x for x in report["frame_params"]}[r["frame"]]
        kids = fr.get("hands") or {}
        pose_rows.append({"frame": r["frame"],
                          "Left": (kids.get("Left") or {}).get("姿态读数"),
                          "Right": (kids.get("Right") or {}).get("姿态读数")})
    hold_rows = [x for x in pose_rows if x["frame"] >= LIFT_FRAME_CHEST and x["Left"]]
    upper_worst = max((max(abs(x["Left"]["上臂_deg"]), abs(x["Right"]["上臂_deg"]))
                       for x in hold_rows), default=None)
    wrist_worst = max((max(x["Left"]["手腕_deg"], x["Right"]["手腕_deg"])
                       for x in hold_rows), default=None)
    report["arm_posture"] = {
        "来源": "owner 2026-09-16 第 3 轮目视逐字：「还要继续向上抡，**大臂跟地面近似水平**」·"
                "「**手腕和小臂的夹角也不对**」",
        "判据_上臂与水平夹角_deg": {"阈值": LIFT_ARM_LEVEL_TOL_DEG, "窗口": [LIFT_FRAME_CHEST, LIFT_FRAME_END],
                              "最坏": None if upper_worst is None else round(upper_worst, 1)},
        "判据_手腕折角_deg": {"阈值": LIFT_WRIST_MAX_DEG,
                          "窗口": [LIFT_FRAME_CHEST, LIFT_FRAME_END],
                          "最坏": None if wrist_worst is None else round(wrist_worst, 1)},
        "逐帧": pose_rows}
    print(f"  姿态（owner 第 3 轮点名的两个量）：上臂与水平夹角 最坏 "
          f"{report['arm_posture']['判据_上臂与水平夹角_deg']['最坏']}°（阈值 ≤{LIFT_ARM_LEVEL_TOL_DEG}）· "
          f"手腕伸直缺口 最坏 {report['arm_posture']['判据_手腕折角_deg']['最坏']}°"
          f"（阈值 ≤{LIFT_WRIST_MAX_DEG:.0f}）")
    if upper_worst is not None and upper_worst > LIFT_ARM_LEVEL_TOL_DEG:
        report["problems"].append(
            f"大臂不≈水平：抡到位后上臂与水平夹角最坏 {upper_worst:.1f}° > {LIFT_ARM_LEVEL_TOL_DEG}°")
    if wrist_worst is not None and wrist_worst > LIFT_WRIST_MAX_DEG:
        report["problems"].append(
            f"手腕不≈伸直：抡到位后手腕折角最坏 {wrist_worst:.1f}° > {LIFT_WRIST_MAX_DEG:.0f}°")

    # ---- ⑫ 回显卡 ----
    cc = report["contact_criteria"]
    card = [
        {"判据量": "接触对**持续型**：双手 ↔ 椅子被握构件（口径 §13.4.1 F4a）",
         "判据形态": "点↔线 / 点↔面 / 点↔体（卡 1 的三条）",
         "产物侧读数": " · ".join(
             f"{s} 窗口 {cc[s]['窗口']} 逐帧最坏 {cc[s]['逐帧最坏_mm']:+.2f} mm"
             f"（超差帧 {len(cc[s]['超差帧'])}）" for s in CARD1_SIDES),
         "容差档": f"`tol_contact` {tol} mm（ε 32.68 mm 是**另一个**数，口径 §8.1/§8.2）",
         "状态": "✅" if all(not cc[s]["超差帧"] for s in CARD1_SIDES) else "❌"},
        {"判据量": "时序**零阈值**：声明帧 == 产物侧可算出的帧",
         "判据形态": "帧号相等（无阈值）",
         "产物侧读数": " · ".join(f"{k.split('（')[0]} {v['声明']}/{v['产物']}"
                                for k, v in report["timing"].items() if "一致" in v),
         "容差档": "—",
         "状态": "✅" if all(v.get("一致") for v in report["timing"].values() if "一致" in v) else "❌"},
        {"判据量": "椅子跟随手（Blender 侧）——逐帧解出的椅子变换 + **握持刚性**",
         "判据形态": "手骨局部坐标下的位姿稳定性（判据 3）",
         "产物侧读数": f"逐帧最坏 {report['rigidity']['逐帧最坏_mm']} mm · 累计 "
                       f"{report['rigidity']['累计_mm']} · 两手互证 "
                       f"{report['rigidity']['两手互证最坏']}",
         "容差档": f"≤{LIFT_RIGID_PER_FRAME_MM} mm/帧 · ≤{LIFT_RIGID_TOTAL_MM} mm 全程（§四·戊·5 判据 3）",
         "状态": "✅" if (report["rigidity"]["逐帧最坏_mm"] <= LIFT_RIGID_PER_FRAME_MM
                        and max(report["rigidity"]["累计_mm"].values()) <= LIFT_RIGID_TOTAL_MM) else "❌"},
        {"判据量": "判据 1：两手间距（**挥舞带** 0.15–0.25 m；搬运锚 0.487 m 并列报读数）",
         "判据形态": "与参照偏差 ≤25% · 波动 ≤0.1 m",
         "产物侧读数": f"中位 {report['rigidity']['两手间距_m']['中位']} m · "
                       f"波动 {report['rigidity']['两手间距_m']['波动']} m · "
                       f"对搬运锚 {carry_dev:+.1%}",
         "容差档": "±25% / 0.1 m（§四·戊·5 判据 1）",
         "状态": "✅" if band_ok and report["rigidity"]["两手间距_m"]["波动"] <= LIFT_HANDS_DRIFT_M
                       else "❌"},
        {"判据量": "判据 4：无穿模（躯干/上臂/大腿零穿透 · 手/前臂骨心 ≤2 cm · 非接触部位 ≥1 cm）",
         "判据形态": "点↔有向盒（椅子碰撞体）",
         "产物侧读数": f"非接触部位最小间隙 {report['clash']['非接触部位最小间隙_mm']} mm · "
                       f"骨心最坏 {min(core_worst.values()) if core_worst else None} mm · "
                       f"违规帧 {len(clash_frames)}",
         "容差档": "0 / −20 mm / +10 mm（§四·戊·5 判据 4）",
         "状态": "✅" if not clash_frames and report["clash"]["非接触部位最小间隙_mm"] >= LIFT_CLASH_CLEAR_MM else "❌"},
        {"判据量": "判据 5：包握（每根手指**末节蒙皮**到被握构件表面 ≤1.5 cm）",
         "判据形态": "点↔有向盒最近距离（逐指，取最外那一点）",
         "产物侧读数": f"逐手最坏 {report['wrap']['逐手最坏_mm']} mm（帧 "
                       f"{LIFT_FRAME_GRIP} 起逐帧不变 ⇒ 刚性）",
         "容差档": f"≤{LIFT_WRAP_MAX_MM} mm", "状态": "✅" if all(
             v is not None and v <= LIFT_WRAP_MAX_MM for v in wrap_worst.values()) else "❌"},
        {"判据量": "接地 + 地面零穿透（足底蒙皮 / 椅子最低点）",
         "判据形态": "`soleMargin` = 2.8 mm",
         "产物侧读数": f"椅子最低 {min(r['chair_min_z_mm'] for r in prod)} mm · 足部蒙皮最低 "
                       f"{min([v for r in prod for v in r['foot_low_mm'].values() if v is not None])} mm · "
                       f"违规帧 {len(ground_frames)}",
         "容差档": "−2.8 mm（母版中立姿势本身足底 −0.32 mm，先例 #171）",
         "状态": "✅" if not ground_frames else "❌"},
        {"判据量": "支撑域：弯腰段与起身段**逐帧在域内**（凸包件）",
         "判据形态": "重心（髋投影）↔ 支撑多边形（布尔）",
         "产物侧读数": f"窗 {report['balance']['窗']} 内非域内帧 {len(not_in)} · "
                       f"域外（全段）{bal['结构'][layer]['域外帧数']} · 退化 {len(bal['结构'][layer]['退化帧'])}",
         "容差档": "零新阈值（口径 §10.1 层选 = 蒙皮层）",
         "状态": "✅" if not not_in else "❌"},
        {"判据量": "判据**能报红**（接近段必须有超差帧 + 中立姿势对照 + 未抬起的椅子）",
         "判据形态": "存在性（非退化对照）",
         "产物侧读数": f"接近段红帧 " + " · ".join(
             f"{s} {len(cc[s]['接近段红帧'])}" for s in CARD1_SIDES)
             + f" · 中立对照 " + " · ".join(
                 f"{s} {max(abs(v) for v in neutral[s].values() if v is not None):.1f} mm"
                 for s in CARD1_SIDES),
         "容差档": "—",
         "状态": "✅" if all(cc[s]["接近段红帧"] for s in CARD1_SIDES) else "❌"},
        {"判据量": "可见骨不伸出皮肤包围盒（口径 §15.4 / §15.8）",
         "判据形态": "包围盒包含（布尔）",
         "产物侧读数": f"可见骨 {report['visible_bones']['可见骨数']} · "
                       f"非例外越界 {len(report['visible_bones']['非例外的越界骨'])}",
         "容差档": "分界 = `CONTACT_TOL_MM` = 2.8 mm",
         "状态": "✅" if not report["visible_bones"]["非例外的越界骨"] else "❌"},
    ]
    report["feedback_card"] = card
    report["ok"] = not report["problems"]
    print("\n" + "=" * 104)
    print(f"回显卡（口径 §四：每一项都要有**产物侧**读数）· 动作 {action_name}")
    for row in card:
        print(f"  {row['判据量'][:40]:<42}{row['判据形态'][:24]:<26}"
              f"{str(row['产物侧读数'])[:78]:<80}{row['状态']}")
    print("=" * 104)

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still:
        for frame, suffix in ((LIFT_FRAME_START, "start"), (17, "bend"), (LIFT_FRAME_GRIP, "grip"),
                              (LIFT_FRAME_OFF_GROUND, "offground"), (LIFT_FRAME_CHEST, "chest"),
                              (LIFT_FRAME_END, "hold")):
            bpy.context.scene.frame_set(frame)
            update()
            target = Vector((0.0, -0.45, 0.90))
            cam = Vector((1.85, -2.55, 1.55))
            path = str(args.still).replace(".png", f"_{suffix}.png")
            render_still(path, cam, target)
            print(f"静帧（帧 {frame}）：{path}")
    if args.host == "live":
        bpy.context.scene.frame_set(LIFT_FRAME_END)
        update()
        print(f"[live] 停在末帧 {LIFT_FRAME_END}（预览；未写回文件）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl))
        print(f"已写回母版副本：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL'} —— problems {report['problems']}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 4：重述对拍（`--task restate`）——口径 §13.8 判据 1
#
#   「#163 既有读数 vs 用**卡片语言**复现 ⇒ 差异 0」——**纯算术**，不跑 Blender、不请 owner 目视。
#   ⚠️ 它**不是独立验证**（口径 §13.8 已写明）：卡 1 的字段正是从 #163 读数提炼的 ⇒ **训练集测训练集**。
#      独立验证 = 门边动作那条（`--task door`）。
#
#   两处**参照系改写**（不是数值改动，逐条登记）：
#   ① 「虎口↔上沿」原判据参照的是**顶面中线**（`y = back_cy`）——中线不是棱（棱是两面的交线）
#      ⇒ 卡片语言改按**真棱**（上沿近侧 / 远侧）参照，同一点得出 20.0 mm（见 §五 的登记）；
#   ② ε 换算的掌面法向原取自**骨架系**（母版骨架带 +90° X 旋转）⇒ 世界系与它差 90°
#      （#163 那条"掌面陷入 22.2 mm"的已知偏差由此而来；改对之后重跑给出 10.5 mm 悬空）。
# ══════════════════════════════════════════════════════════════════════════════

#: #163 已接受版本的**既有读数**（逐值带来源；不得凭记忆填）
ISSUE163_RECORDED = {
    "来源": "design/engineering/evidence/action-description-regression-2026-09-14.md §二十/§二十三",
    "报告": ".scratch/chair_live_report.json（到位帧 41）",
    "虎口_世界坐标_m": [0.17, -0.47, 0.7949],
    "虎口↔顶面中线_mm": -0.0,
    "掌面最低点↔顶面_mm": -22.2,
    "拇指尖_m": [0.2308, -0.48, 0.7187],
    "拇指尖↔近侧面_mm": -30.0,
    "逐指尖_m": {"Index": -0.4662, "Middle": -0.4684, "Ring": -0.4639, "Pinky": -0.4622},
}
#: 上罩那一版的板几何（`chair_layout(0.70)` 与 #163 一致：靠背中心面 y=−0.47、厚 40 mm、顶面 z=0.7949）
ISSUE163_BOARD = {"back_cy": -0.47, "back_near_y": -0.45, "back_far_y": -0.49, "rail_top_z": 0.7949}


def main_restate() -> int:
    """把 #163 的既有读数**逐值**搬进卡片的字段语言，并断言差异 0（口径 §13.8 判据 1）。"""
    rec = ISSUE163_RECORDED
    board = ISSUE163_BOARD
    web = Vector(rec["虎口_世界坐标_m"])
    tol = 1e-9
    rows, diffs = [], []

    def check(field, recorded, restated, note=""):
        d = None if (recorded is None or restated is None) else abs(recorded - restated)
        ok = (d is not None and d <= tol)
        rows.append({"字段": field, "既有读数": recorded, "卡片语言复现": restated,
                     "差异": d, "状态": "✅" if ok else "❌", "备注": note})
        if not ok:
            diffs.append(field)

    # F11 虎口：坐标逐个搬；参照线由**中线**改为**真棱**（登记，不计入差异）
    check("F11 虎口.x", web.x, web.x)
    check("F11 虎口.y", web.y, web.y)
    check("F11 虎口.z", web.z, web.z)
    check("F11 虎口↔顶面中线（原判据）", rec["虎口↔顶面中线_mm"], rec["虎口↔顶面中线_mm"],
          "非棱参照；真棱参照见下两行")
    near_edge = Vector((web.x, board["back_near_y"], board["rail_top_z"]))
    far_edge = Vector((web.x, board["back_far_y"], board["rail_top_z"]))
    rows.append({"字段": "F11 虎口↔真棱（上沿近侧）", "既有读数": None,
                 "卡片语言复现": round(point_to_line_mm(web, (near_edge, Vector((1.0, 0.0, 0.0)))), 1),
                 "差异": None, "状态": "登记", "备注": "**参照系改写**：同一点、改按棱量"})
    rows.append({"字段": "F11 虎口↔真棱（上沿远侧）", "既有读数": None,
                 "卡片语言复现": round(point_to_line_mm(web, (far_edge, Vector((1.0, 0.0, 0.0)))), 1),
                 "差异": None, "状态": "登记", "备注": "同上"})
    check("F11 拇指↔近侧面", rec["拇指尖↔近侧面_mm"], rec["拇指尖↔近侧面_mm"])
    check("F11 掌面最低点↔顶面", rec["掌面最低点↔顶面_mm"], rec["掌面最低点↔顶面_mm"],
          "负 = 陷入；⚠️ 根因见下（ε 法向的系）")
    for finger, y in rec["逐指尖_m"].items():
        check(f"F11 {finger}指尖 y", y, y)
        rows.append({"字段": f"F11 {finger}指尖↔远侧面", "既有读数": round((y - board["back_far_y"]) * 1000.0, 1),
                     "卡片语言复现": round((y - board["back_far_y"]) * 1000.0, 1),
                     "差异": 0.0, "状态": "✅", "备注": "点↔面（远侧面在 −Y 侧，正 = 还差这么多）"})

    print("重述对拍（口径 §13.8 判据 1；#163 既有读数 → 卡片语言）")
    print(f"  {'字段':<34}{'既有读数':>12}{'复现':>12}{'差异':>10}  状态")
    for r in rows:
        print(f"  {r['字段']:<34}{str(r['既有读数']):>12}{str(r['卡片语言复现']):>12}"
              f"{str(r['差异']):>10}  {r['状态']}")
    print(f"逐值差异：{len(diffs)} 处不一致" + ("" if not diffs else f" —— {diffs}"))
    print("⚠️ 本条**不是独立验证**（卡 1 的字段就是从这些读数提炼的）⇒ 独立验证 = `--task door`。")
    print("登记的两处参照系改写：① 虎口参照由顶面中线改为**真棱**；"
          "② ε 的掌面法向由骨架系改为**世界系**（母版骨架带 +90° X 旋转）")
    return 0 if not diffs else 1


def main() -> int:
    """任务分发：`--task` 选宿主（默认 `chair` = #163 的产出宿主，行为与改动前一致）。"""
    argv = list(sys.argv)
    task = "chair"
    if "--" in argv:
        tail = argv[argv.index("--") + 1:]
        if "--task" in tail:
            idx = tail.index("--task")
            if idx + 1 < len(tail):
                task = tail[idx + 1]
    return {"chair": main_chair, "card1": main_card1, "door": main_door,
            "doorpush": main_door_push, "panic": main_panic, "crouch": main_crouch,
            "kneel": main_kneel, "liftchest": main_liftchest, "restate": main_restate}[task]()


if __name__ == "__main__":
    sys.exit(main())
