#!/usr/bin/env python3
"""
技能→脑区映射表生成器
=====================
从 大脑技能树3D.html 提取 74 技能节点数据,
将每个技能的 region 字段映射到 brain_regions.json 的脑区,
生成新坐标 (MNI解剖坐标替换PAD推导坐标),
对比新旧坐标差异。

用法:
  python tools/map_skills_to_regions.py
"""

import json
import re
import math
import os

# ═══════════════════════════════════════════════════════════
#  SECTION 1: 从 HTML 提取技能数据
# ═══════════════════════════════════════════════════════════

def extract_skills_from_html(html_path):
    """
    从 大脑技能树3D.html 解析 treeData, 提取所有技能节点.

    返回: dict with keys: cognition[], emotion[], behavior[], ultimate[]
    每个条目: {id, name, tier, mod/drive, type, ap, cd, x, y, z, light, desc, region}
    """
    import subprocess

    # 用 Python 正则从 HTML 提取 treeData
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 找到 treeData 定义 (var treeData={...};)
    match = re.search(r"var treeData=\{([^}]*\{[^}]*\}[^}]*\}[^}]*\}[^}]*\})", content, re.DOTALL)
    if not match:
        # 尝试更宽松的匹配
        match = re.search(r"var treeData=(\{.*?\}\s*;)", content, re.DOTALL)

    skills = {"cognition": [], "emotion": [], "behavior": [], "ultimate": []}

    # 认知节点: id:'cog_N',name:'...',tier:N,mod:'...',type:'...',ap:'...',cd:'...',x:...,y:...,z:...,desc:'...',region:'...'
    # 注意: desc 中可能包含转义单引号 \', 用 [^}]*? 匹配
    cog_pattern = r"\{id:'(cog_\d+)',name:'([^']+)',tier:(\d+),mod:'([^']+)',type:'([^']+)',ap:'([^']*)',cd:'([^']*)',x:([-\d.]+),y:([-\d.]+),z:([-\d.]+),desc:'(.*?)',region:'([^']+)'\}"
    cog_match = re.findall(cog_pattern, content)
    for m in cog_match:
        skills["cognition"].append({
            "id": m[0], "name": m[1], "tier": int(m[2]), "module": m[3],
            "type": m[4], "ap": m[5], "cd": m[6],
            "pad_x": float(m[7]), "pad_y": float(m[8]), "pad_z": float(m[9]),
            "desc": m[10], "region": m[11], "branch": "cognition"
        })

    # 情绪节点: id:'emo_N',name:'...',tier:N,x:...,y:...,z:...,light:...,desc:'...',region:'...'
    emo_pattern = r"\{id:'(emo_\d+)',name:'([^']+)',tier:(\d+),x:([-\d.]+),y:([-\d.]+),z:([-\d.]+),light:([-\d.]+),desc:'([^']*)',region:'([^']+)'\}"
    emo_match = re.findall(emo_pattern, content)
    for m in emo_match:
        skills["emotion"].append({
            "id": m[0], "name": m[1], "tier": int(m[2]),
            "pad_x": float(m[3]), "pad_y": float(m[4]), "pad_z": float(m[5]),
            "light": float(m[6]), "desc": m[7], "region": m[8],
            "branch": "emotion"
        })

    # 行为节点: id:'beh_N',name:'...',tier:N,drive:'...',x:...,y:...,z:...,ap:'...',cd:'...',desc:'...',region:'...'
    # 注意: x,y,z 在 drive 之后, ap/cd 之前
    beh_pattern = r"\{id:'(beh_\d+)',name:'([^']+)',tier:(\d+),drive:'([^']+)',x:([-\d.]+),y:([-\d.]+),z:([-\d.]+),ap:'([^']*)',cd:'([^']*)',desc:'(.*?)',region:'([^']+)'\}"
    beh_match = re.findall(beh_pattern, content)
    for m in beh_match:
        skills["behavior"].append({
            "id": m[0], "name": m[1], "tier": int(m[2]), "drive": m[3],
            "pad_x": float(m[4]), "pad_y": float(m[5]), "pad_z": float(m[6]),
            "ap": m[7], "cd": m[8], "desc": m[9], "region": m[10],
            "branch": "behavior"
        })

    # 终极技能: id:'ult_N',name:'...',combo:'...',x:...,y:...,z:...,ap:'...',cd:'...',cost:N,desc:'...',region:'...'
    # 注意: z 可能带显式 + 号 (如 z:+0.576), 没有 tier 字段
    ult_pattern = r"\{id:'(ult_\d+)',name:'([^']+)',combo:'([^']*)',x:([-\d.]+),y:([-\d.]+),z:\+?([-\d.]+),ap:'([^']*)',cd:'([^']*)',cost:(\d+),desc:'(.*?)',region:'([^']+)'\}"
    ult_match = re.findall(ult_pattern, content)
    for m in ult_match:
        skills["ultimate"].append({
            "id": m[0], "name": m[1], "combo": m[2], "tier": "U",
            "pad_x": float(m[3]), "pad_y": float(m[4]), "pad_z": float(m[5]),
            "ap": m[6], "cd": m[7], "cost": int(m[8]),
            "desc": m[9], "region": m[10], "branch": "ultimate"
        })

    total = sum(len(v) for v in skills.values())
    print(f"📋 从 HTML 提取 {total} 技能:")
    for branch, lst in skills.items():
        print(f"   {branch}: {len(lst)} 个")

    return skills


# ═══════════════════════════════════════════════════════════
#  SECTION 2: 技能脑区 → 图谱脑区 映射逻辑
# ═══════════════════════════════════════════════════════════

def normalize_region_name(region_str):
    """
    将技能树 region 字段标准化为 brain_regions.json 的键名.
    处理复合名称 (如 '杏仁核+下丘脑+PAG') 和子区域名 (如 '海马体 CA1').
    """
    # 去除网络/通路前缀
    network_prefixes = [
        "反射环路·", "前额叶极·",
    ]
    for prefix in network_prefixes:
        if region_str.startswith(prefix):
            region_str = region_str[len(prefix):]

    # 直接匹配 (最高优先级)
    DIRECT_MAP = {
        "杏仁核+下丘脑+PAG": "杏仁核",  # 取主成分
        "腹侧纹状体/NAcc+BNST": "腹侧纹状体",
        "前脑岛+ACC": "前脑岛",
        "OFC+mPFC+颞极": "OFC",
        "PAG+上丘+脑干": "杏仁核-PAG",
        "基底节+杏仁核": "基底节间接通路",
        "NAcc+VTA/多巴胺": "NAcc核",
        "vmPFC+TPJ+楔前叶": "vmPFC",
        "mPFC+颞极+后扣带": "mPFC",
        "ACC+额顶控制网络": "ACC背侧",
        "前脑岛+ACC+VTA": "岛叶-ACC-VTA",
    }

    if region_str in DIRECT_MAP:
        return DIRECT_MAP[region_str]

    # 子区域去除 (取主结构)
    SUBREGION_STRIP = [
        " CA1", " CA3", "壳", "核", "吻侧", "背侧",
    ]
    stripped = region_str
    for s in SUBREGION_STRIP:
        stripped = stripped.replace(s, "")

    # 特殊映射
    SPECIAL = {
        "枕叶 V1": "枕叶 V1",
        "伏隔核/NAcc": "伏隔核/NAcc",
        "VTA-NAcc": "VTA-NAcc",
        "Broca区": "Broca区",
        "Wernicke区": "Wernicke区",
        "DMN+OFC": "DMN+OFC",
        "dlPFC": "dlPFC",
        "vmPFC": "vmPFC",
        "mPFC": "mPFC",
        "mPFC-杏仁核": "mPFC-杏仁核",
        "vmPFC-TPJ": "vmPFC-TPJ",
        "TPJ": "TPJ",
        "OFC": "OFC",
        "ACC": "ACC",
        "ACC背侧": "ACC背侧",
        "ACC吻侧": "ACC吻侧",
        "BNST": "BNST",
        "前脑岛": "前脑岛",
        "全脑整合": "全脑整合",
        "杏仁核-PAG": "杏仁核-PAG",
        "岛叶-ACC": "岛叶-ACC",
        "岛叶-vmPFC": "岛叶-vmPFC",
        "岛叶-PFC-杏仁核": "岛叶-PFC-杏仁核",
        "岛叶-ACC-VTA": "岛叶-ACC-VTA",
    }

    if stripped in SPECIAL:
        return SPECIAL[stripped]

    return region_str  # 保留原文


def match_skill_to_region(skill, brain_regions):
    """
    将技能匹配到 brain_regions.json 中的脑区.
    返回匹配到的脑区键名, 若无匹配则返回 None.
    """
    raw_region = skill.get("region", "")
    normalized = normalize_region_name(raw_region)

    # 精确匹配
    if normalized in brain_regions:
        return normalized

    # 模糊匹配: 检查 brain_regions 的键是否包含在 normalized 中 (反之亦然)
    for key in brain_regions:
        if key in normalized or normalized in key:
            return key

    return None


# ═══════════════════════════════════════════════════════════
#  SECTION 3: 半球镜像
# ═══════════════════════════════════════════════════════════

def apply_hemisphere(mni_coords, pad_x):
    """
    根据技能在PAD空间中的 X 位置决定半球:
      pad_x < 0 → 左半球 (MNI X < 0, 保持)
      pad_x > 0 → 右半球 (MNI X > 0, 镜像)
      pad_x ≈ 0 → 中线 (MNI X = 0)
    """
    x, y, z = mni_coords
    if pad_x > 0.05:
        # 右半球: 取 X 绝对值
        return (abs(x), y, z)
    elif pad_x < -0.05:
        # 左半球: 保持负 X
        return (-abs(x), y, z)
    else:
        # 中线
        return (0, y, z)


# ═══════════════════════════════════════════════════════════
#  SECTION 4: 主程序
# ═══════════════════════════════════════════════════════════

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "技能树系统", "大脑技能树3D.html")
    regions_path = os.path.join(base_dir, "data", "brain_regions.json")
    output_path = os.path.join(base_dir, "data", "skill_coords.json")

    # 加载脑区数据
    with open(regions_path, "r", encoding="utf-8") as f:
        regions_data = json.load(f)
    brain_regions = regions_data["regions"]

    # 提取技能
    skills = extract_skills_from_html(html_path)

    # 映射 + 计算新坐标
    def game_from_mni(mni):
        """MNI → 游戏空间"""
        return (
            round(mni[0] / 90.0 * 1.0, 4),
            round(mni[2] / 90.0 * 1.0 + 0.55, 4),
            round(mni[1] / 126.0 * 0.85, 4),
        )

    matched = 0
    unmatched = []
    output_skills = []

    for branch, skill_list in skills.items():
        for skill in skill_list:
            region_key = match_skill_to_region(skill, brain_regions)

            if region_key:
                region_info = brain_regions[region_key]
                mni = region_info["mni_xyz"]
                # 应用半球
                mni_hemi = apply_hemisphere(mni, skill["pad_x"])
                game_new = game_from_mni(mni_hemi)
                matched += 1
            else:
                # 无匹配: 保留旧PAD坐标, 但标记
                region_info = None
                mni_hemi = None
                game_new = (skill["pad_x"], skill["pad_y"], skill["pad_z"])

            entry = {
                "id": skill["id"],
                "name": skill["name"],
                "branch": branch,
                "tier": skill["tier"],
                "region": skill.get("region", ""),
                "region_matched": region_key,
                # 旧坐标 (PAD推导)
                "pad_xyz": [skill["pad_x"], skill["pad_y"], skill["pad_z"]],
                # 新坐标 (MNI解剖)
                "mni_xyz": list(mni_hemi) if mni_hemi else None,
                "game_xyz_new": list(game_new),
            }

            # 添加额外元信息
            if "module" in skill:
                entry["module"] = skill["module"]
            if "drive" in skill:
                entry["drive"] = skill["drive"]
            if "type" in skill:
                entry["type"] = skill["type"]

            if not region_key:
                unmatched.append(skill["name"])

            output_skills.append(entry)

    # 输出
    output = {
        "_description": "74技能节点坐标映射: PAD推导(旧) → MNI解剖(新)",
        "_source": "Phase 2: tools/map_skills_to_regions.py",
        "_created": "2026-07-11",
        "_stats": {
            "total_skills": len(output_skills),
            "matched": matched,
            "unmatched": len(unmatched),
            "unmatched_list": unmatched,
        },
        "skills": output_skills,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已生成 {output_path}")
    print(f"   匹配: {matched}/{len(output_skills)}")
    if unmatched:
        print(f"   ⚠ 未匹配 ({len(unmatched)}): {unmatched}")

    # 对比分析
    print("\n" + "=" * 60)
    print("📊 新旧坐标对比 (前10个技能)")
    print("=" * 60)
    print(f"{'技能':<8} {'region':<18} {'旧PAD_xyz':<28} {'新MNI_xyz':<28} {'Δ距离':>6}")
    print("-" * 90)

    for s in output_skills[:10]:
        old = s["pad_xyz"]
        new = s["game_xyz_new"]
        dist = math.sqrt(sum((o - n) ** 2 for o, n in zip(old, new)))
        old_str = f"({old[0]:.2f},{old[1]:.2f},{old[2]:.2f})"
        new_str = f"({new[0]:.2f},{new[1]:.2f},{new[2]:.2f})"
        rgn = (s.get("region") or "")[:16]
        print(f"{s['name']:<8} {rgn:<18} {old_str:<28} {new_str:<28} {dist:>6.3f}")

    # 计算平均偏移
    all_dists = []
    for s in output_skills:
        old = s["pad_xyz"]
        new = s["game_xyz_new"]
        all_dists.append(math.sqrt(sum((o - n) ** 2 for o, n in zip(old, new))))

    print(f"\n📏 平均坐标偏移: {sum(all_dists)/len(all_dists):.3f}")
    print(f"   最大偏移: {max(all_dists):.3f}")
    print(f"   最小偏移: {min(all_dists):.3f}")
    print(f"\n💡 大偏移是预期行为——MNI解剖坐标替换了PAD心理学公式推导值")


if __name__ == "__main__":
    main()
