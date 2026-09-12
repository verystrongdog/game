#!/usr/bin/env python3
"""综合验证脚本：检查 emotion_cards.json 和 cognition_cards.json 的完整性、一致性和数值范围。

用法: python3 code/tools/validate_cards.py
"""

import json
import sys
from collections import Counter
from pathlib import Path


def validate_emotion_cards(data: dict) -> list[str]:
    """验证情绪卡数据，返回错误列表。"""
    errors = []
    cards = data.get("cards", [])

    # ── 基本结构 ──
    if not cards:
        return ["情绪卡列表为空"]
    if len(cards) != 15:
        errors.append(f"情绪卡数量: {len(cards)} ≠ 15")

    # 加载参考数据
    root = Path(__file__).parent.parent.parent
    with open(root / "data" / "emotions.json", encoding="utf-8") as f:
        ref = json.load(f)
    ref_emos = {e["id"]: e for e in ref.get("emotions", [])}

    ids = set()
    names = set()
    thrust_dirs = {
        "approach", "avoid", "approach_threat", "slight_approach", "neutral",
    }

    for card in cards:
        eid = card.get("id", "?")
        name = card.get("name", "?")
        prefix = f"[{name}] "

        # ── 字段存在性 ──
        required_top = [
            "id", "name", "type", "pad", "ap_cost", "tags",
            "play_effect", "hand_pressure", "residual", "acquisition",
            "linkages", "design_note",
        ]
        for field in required_top:
            if field not in card:
                errors.append(f"{prefix}缺少字段 '{field}'")

        if card.get("type") != "情绪":
            errors.append(f"{prefix}type 应为 '情绪'，实际为 '{card.get('type')}'")

        # ── PAD 一致性 ──
        if eid in ref_emos:
            src = ref_emos[eid]["pad"]
            pad = card.get("pad", {})
            for dim in ["V", "A", "D"]:
                if abs(pad.get(dim, 999) - src[dim]) > 0.001:
                    errors.append(
                        f"{prefix}PAD.{dim}={pad.get(dim)} ≠ emotions.json {src[dim]}"
                    )

        # ── 打出偏移范围 ──
        po = card.get("play_effect", {}).get("pad_offset", {})
        for dim in ["dV", "dA", "dD"]:
            val = po.get(dim, 999)
            if abs(val) > 0.3 + 0.001:
                errors.append(f"{prefix}打出偏移 {dim}={val} 超出 ±0.3")

        # ── 手牌压力 ≈ 打出偏移 / 5 ──
        hp = card.get("hand_pressure", {}).get("pad", {})
        for dim_key, hp_dim in [("dV", "dV"), ("dA", "dA"), ("dD", "dD")]:
            if abs(po.get(dim_key, 0)) > 0.001:
                expected = round(po[dim_key] / 5, 3)
                actual = hp.get(hp_dim, 999)
                if abs(actual - expected) > 0.002:
                    errors.append(
                        f"{prefix}手牌压力 {hp_dim}={actual}，预期 ≈ {expected}"
                    )

        # ── 残留量范围 ──
        ra = card.get("residual", {}).get("amount", -1)
        if ra < 0.009 or ra > 0.051:
            errors.append(f"{prefix}残留量 {ra} 不在 [0.01, 0.05]")

        # ── 残留方向 ──
        rd = card.get("residual", {}).get("direction", "")
        if rd not in ("positive", "negative", "neutral"):
            errors.append(f"{prefix}残留方向 '{rd}' 无效")

        # ── 获得难度 ──
        rarity = card.get("acquisition", {}).get("rarity", "")
        if rarity not in ("common", "uncommon", "rare"):
            errors.append(f"{prefix}获得难度 '{rarity}' 无效")

        # ── 获得方式非空 ──
        sources = card.get("acquisition", {}).get("sources", [])
        if not sources:
            errors.append(f"{prefix}获得方式为空")

        # ── 行为推力 ──
        bt_dir = card.get("play_effect", {}).get("behavior_thrust", {}).get("direction", "")
        if bt_dir not in thrust_dirs:
            errors.append(f"{prefix}行为推力方向 '{bt_dir}' 无效")

        # ── 联动一致性 ──
        if eid in ref_emos:
            src_ad = sorted(ref_emos[eid].get("activates_drives", []))
            card_ad = sorted(card.get("linkages", {}).get("activates_drives", []))
            if src_ad != card_ad:
                errors.append(
                    f"{prefix}activates_drives={card_ad} ≠ emotions.json {src_ad}"
                )

        # ── 必填文案非空 ──
        text_fields = [
            ("打出描述", card.get("play_effect", {}).get("description", "")),
            ("手牌压力描述", card.get("hand_pressure", {}).get("description", "")),
            ("残留倾向", card.get("residual", {}).get("tendency", "")),
            ("自然触发", card.get("acquisition", {}).get("natural_trigger", "")),
            ("塞入数量", card.get("acquisition", {}).get("count", "")),
            ("设计备忘", card.get("design_note", "")),
        ]
        for fname, val in text_fields:
            if not val or not str(val).strip():
                errors.append(f"{prefix}文案字段 '{fname}' 为空")

        # ── 唯一性 ──
        if eid in ids:
            errors.append(f"{prefix}ID '{eid}' 重复")
        if name in names:
            errors.append(f"{prefix}卡名 '{name}' 重复")
        ids.add(eid)
        names.add(name)

        # ── 共情特殊检查 ──
        if eid == "empathy":
            transfer = card.get("linkages", {}).get("transfer_emotions", [])
            if len(transfer) < 5:
                errors.append(f"{prefix}共情应包含传递情绪列表（至少 5 种）")

    # ── 覆盖检查 ──
    for ref_emo in ref.get("emotions", []):
        if ref_emo["id"] not in ids:
            errors.append(f"emotions.json 中的 '{ref_emo['id']}' 在情绪卡中缺失")

    return errors


def validate_cognition_cards(data: dict) -> list[str]:
    """验证认知卡数据，返回错误列表。"""
    errors = []
    cards = data.get("cards", [])

    if not cards:
        return ["认知卡列表为空"]
    if len(cards) != 25:
        errors.append(f"认知卡数量: {len(cards)} ≠ 25")

    valid_modules = {
        "知觉与注意", "记忆", "知识表征与分类", "表象与语言", "推理问题解决与决策",
    }
    strict_chain = [
        "知觉与注意", "知识表征与分类", "推理问题解决与决策", "表象与语言",
    ]
    valid_tendencies = {"唯物", "唯心"}
    valid_steps = {"Relevance", "Implications", "Coping", "Normative"}
    valid_secs = {
        "Novelty", "Intrinsic Pleasantness", "Goal Relevance",
        "Causal Attribution", "Outcome Probability", "Discrepancy",
        "Goal Conductiveness", "Urgency", "Control", "Power",
        "Adjustment", "Internal Standards", "External Standards",
    }
    valid_effect_types = {
        "揭示", "重评", "拓宽", "窄化", "重构", "预览", "回收", "命名", "归类", "推演", "检索",
    }

    # CPM 参与度矩阵
    module_step_map = {
        "知觉与注意": ["Relevance"],
        "记忆": ["Relevance", "Implications", "Coping"],
        "知识表征与分类": ["Relevance", "Implications", "Normative"],
        "表象与语言": ["Coping", "Normative"],
        "推理问题解决与决策": ["Implications", "Coping"],
    }

    ids = set()
    names = set()

    for card in cards:
        cid = card.get("id", "?")
        name = card.get("name", "?")
        module = card.get("module", "?")
        prefix = f"[{name}] "

        # ── 字段存在性 ──
        required = [
            "id", "name", "type", "module", "tendency", "time_orientation",
            "effect_description", "base_effect", "ap_cost", "cognitive_quality",
            "cpm", "effect", "linkages", "design_note",
        ]
        for field in required:
            if field not in card:
                errors.append(f"{prefix}缺少字段 '{field}'")

        if card.get("type") != "认知":
            errors.append(f"{prefix}type 应为 '认知'")

        # ── 模块有效性 ──
        if module not in valid_modules:
            errors.append(f"{prefix}模块 '{module}' 无效")

        # ── 倾向 ──
        if card.get("tendency") not in valid_tendencies:
            errors.append(f"{prefix}倾向 '{card.get('tendency')}' 无效")

        # ── C⁵ 数值范围 ──
        cq = card.get("cognitive_quality", {})
        checks = [
            ("d_prime", -1.0, 1.0),
            ("criterion", -1.0, 1.0),
            ("depth_alpha", 0.0, 1.0),
        ]
        for fname, lo, hi in checks:
            val = cq.get(fname, 999)
            if val < lo or val > hi:
                errors.append(f"{prefix}{fname}={val} 超出 [{lo}, {hi}]")

        # ── CPM 步骤 ──
        cpm_step = card.get("cpm", {}).get("step", "")
        if cpm_step not in valid_steps:
            errors.append(f"{prefix}CPM 步骤 '{cpm_step}' 无效")
        elif module in module_step_map and cpm_step not in module_step_map[module]:
            errors.append(
                f"{prefix}模块 '{module}' 不在 CPM '{cpm_step}' 参与模块中（矩阵: {module_step_map[module]}）"
            )

        # ── SEC 有效性 ──
        for sec in card.get("cpm", {}).get("sec", []):
            if sec not in valid_secs:
                errors.append(f"{prefix}SEC '{sec}' 无效")

        # ── 前置模块不跳级 ──
        prereqs = card.get("cpm", {}).get("prerequisite_modules", [])
        current_idx = strict_chain.index(module) if module in strict_chain else -1
        for pr in prereqs:
            if pr not in valid_modules:
                errors.append(f"{prefix}前置模块 '{pr}' 无效")
            elif pr in strict_chain and current_idx >= 0:
                pr_idx = strict_chain.index(pr)
                if pr_idx > current_idx:
                    errors.append(f"{prefix}前置模块 '{pr}' 是严格链后续——跳过认知阶段")

        # ── 效果字段 ──
        eff = card.get("effect", {})
        if eff.get("type") not in valid_effect_types:
            errors.append(f"{prefix}效果类型 '{eff.get('type')}' 无效")

        # ── 文案非空 ──
        text_fields = [
            ("效果描述", card.get("effect_description", "")),
            ("基础效果", card.get("base_effect", "")),
            ("情绪扭曲", card.get("linkages", {}).get("emotion_distortion", "")),
            ("设计备忘", card.get("design_note", "")),
        ]
        for fname, val in text_fields:
            if not val or not str(val).strip():
                errors.append(f"{prefix}文案字段 '{fname}' 为空")

        # ── 唯一性 ──
        if cid in ids:
            errors.append(f"{prefix}ID '{cid}' 重复")
        if name in names:
            errors.append(f"{prefix}卡名 '{name}' 重复")
        ids.add(cid)
        names.add(name)

        # ── AP 消耗 ──
        if card.get("ap_cost", -1) != 0:
            errors.append(f"{prefix}AP 消耗应为 0，实际为 {card.get('ap_cost')}")

    # ── 每模块 5 张 ──
    module_counts = Counter(c["module"] for c in cards)
    for mod in valid_modules:
        if module_counts.get(mod, 0) != 5:
            errors.append(f"模块 '{mod}' 有 {module_counts.get(mod, 0)} 张 ≠ 5")

    # ── 唯物/唯心比例 ──
    for mod in valid_modules:
        mod_cards = [c for c in cards if c["module"] == mod]
        mat = sum(1 for c in mod_cards if c["tendency"] == "唯物")
        ide = sum(1 for c in mod_cards if c["tendency"] == "唯心")
        if mat not in (2, 3):
            errors.append(f"模块 '{mod}' 唯物={mat} 唯心={ide}（比例异常）")

    return errors


def main():
    root = Path(__file__).parent.parent.parent
    all_errors = []

    # ── 加载文件 ──
    for fname, validator in [
        ("emotion_cards.json", validate_emotion_cards),
        ("cognition_cards.json", validate_cognition_cards),
    ]:
        path = root / "data" / fname
        if not path.exists():
            all_errors.append(f"文件不存在: {path}")
            continue

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            all_errors.append(f"{fname} JSON 格式错误: {e}")
            continue

        file_errors = validator(data)
        all_errors.extend(file_errors)
        status = "✓" if not file_errors else f"✗ ({len(file_errors)} errors)"
        print(f"  {status} {fname}")

    print(f"\n{'='*60}")
    if all_errors:
        print(f"✗ 发现 {len(all_errors)} 个问题:")
        for e in all_errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print("✓ 全部验证通过！")
        print(f"  - 情绪卡 15 张: PAD 一致性 ✓, 数值范围 ✓, 文案完整 ✓")
        print(f"  - 认知卡 25 张: C⁵ 参数 ✓, CPM 一致性 ✓, 模块比例 ✓")


if __name__ == "__main__":
    main()
