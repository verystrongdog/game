#!/usr/bin/env python3
"""脑壳烘焙 — all_obj 的受控 OBJ → 一份可进 Unity 的减面 mesh

把 `data/brain_regions.json` 里带 `obj_file` 的解剖载体（按文件去重，多个
functional_id 共享同一载体）导入、减面、挂**共享材质**，导出 FBX。

设计依据（引用即读取）：
  - 材质分组复用 `build_brain_skill_tree_windows.py` 的 LOBE 配色表（18 键 → 13 种去重颜色），
    不另发明一套：那是 v2 世代的脑叶着色口径，改色是美术决策，不在本工具职责内
  - 减面目标 200,000 三角面：来源 design/presentation/visualization-3d/Unity接入设计.md §五
  - 资产形态：脑壳是**唯一进 Unity 工程的建模产物**（同上 §四）；.blend / 742 MB 中间件都不进
  - 不保留全半球外壳：见 脑模型资产登记.md 与 Unity接入设计.md §八-4

用法:
  blender.exe --background --factory-startup --python code/tools/bake_brain_shell.py \
      -- --out <输出目录> [--tris 200000]

输出（默认 build/ 子目录，**绝不默认写资产目录**）:
  - brain_shell.fbx（Unity 用：Y-up、无动画、共享材质）
  - bake_report.json（产出核对：面数、材质数、区域对象数、缺失文件）
"""

import bpy
import json
import os
import sys
import math
from pathlib import Path

# 复用 v2 生成器的脑叶配色表（来源：code/tools/build_brain_skill_tree_windows.py §LOBE）
LOBE = {
    "frontal":           (0.48, 0.56, 1.0, 1.0),
    "temporal":          (0.31, 0.76, 0.97, 1.0),
    "parietal":          (0.42, 0.53, 0.95, 1.0),
    "occipital":         (0.38, 0.50, 0.90, 1.0),
    "parieto-occipital": (0.40, 0.52, 0.92, 1.0),
    "temporo-parietal":  (0.36, 0.64, 0.96, 1.0),
    "cingulate":         (0.94, 0.63, 0.38, 1.0),
    "cingulate-insula":  (0.94, 0.63, 0.38, 1.0),
    "insula":            (0.94, 0.63, 0.38, 1.0),
    "limbic":            (0.94, 0.63, 0.38, 1.0),
    "basal_ganglia":     (0.91, 0.65, 0.25, 1.0),
    "diencephalon":      (0.75, 0.35, 0.30, 1.0),
    "brainstem":         (0.75, 0.30, 0.25, 1.0),
    "midbrain":          (0.75, 0.33, 0.28, 1.0),
    "midbrain-temporal": (0.75, 0.40, 0.30, 1.0),
    "frontal-temporal":  (0.55, 0.55, 0.65, 1.0),
    "frontal-parietal":  (0.55, 0.55, 0.65, 1.0),
    "frontal-insula":    (0.55, 0.55, 0.65, 1.0),
}
ALPHA = {"cortical": 0.10, "subcortical": 0.20}   # 来源：同上 §ALPHA


def argv_opt(flag, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else default


PROJECT = os.environ.get("YANTF_BRAIN_PROJECT") or str(Path(__file__).resolve().parents[2])
ASSET_DIR = os.path.join(PROJECT, "design", "presentation", "visualization-3d", "blender_assets")
OUT_DIR = argv_opt("--out") or os.path.join(ASSET_DIR, "build")
TRI_BUDGET = int(argv_opt("--tris", "200000"))


def log(m):
    print(f"[BakeShell] {m}")


def obj_lobe(name):
    """OBJ 文件名 → 脑叶分组。**逐字复用** v2 生成器的解析表
    （来源：code/tools/build_brain_skill_tree_windows.py §obj_lobe）。"""
    n = name.lower()
    m = {"amygdala": "temporal", "hippocampus": "temporal", "caudate": "basal_ganglia",
         "putamen": "basal_ganglia", "pallidum": "basal_ganglia", "accumbens": "basal_ganglia",
         "thalamus": "diencephalon", "ventraldc": "diencephalon",
         "brain-stem": "brainstem", "cerebellum": "brainstem",
         "ventricle": "frontal-temporal", "cc_": "frontal-temporal"}
    for k, v in m.items():
        if k in n:
            return v
    if ".dk." in n:
        r = n.split(".dk.")[-1].replace(".obj", "").strip()
        d = {"superiorfrontal": "frontal", "rostralmiddlefrontal": "frontal",
             "caudalmiddlefrontal": "frontal", "parsopercularis": "frontal",
             "parstriangularis": "frontal", "parsorbitalis": "frontal",
             "lateralorbitofrontal": "frontal", "medialorbitofrontal": "frontal",
             "precentral": "frontal", "paracentral": "frontal", "frontalpole": "frontal",
             "superiortemporal": "temporal", "middletemporal": "temporal",
             "inferiortemporal": "temporal", "transversetemporal": "temporal",
             "temporalpole": "temporal", "fusiform": "temporal", "entorhinal": "temporal",
             "parahippocampal": "temporal", "bankssts": "temporal",
             "superiorparietal": "parietal", "inferiorparietal": "parietal",
             "supramarginal": "parietal", "precuneus": "parietal", "postcentral": "parietal",
             "lateraloccipital": "occipital", "lingual": "occipital",
             "pericalcarine": "occipital", "cuneus": "occipital",
             "rostralanteriorcingulate": "cingulate", "caudalanteriorcingulate": "cingulate",
             "posteriorcingulate": "cingulate", "isthmuscingulate": "cingulate",
             "insula": "insula"}
        return d.get(r, "frontal")
    return "frontal"


def tissue_material(color, name):
    """共享材质：同一颜色只建一个（v2 世代那 238 个逐对象材质是反面教材）。"""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.3
    alpha = ALPHA["cortical"]
    try:
        m.blend_method = 'BLEND'
    except Exception:
        pass
    if hasattr(m, 'use_transparent_shadow'):
        m.use_transparent_shadow = False
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'BLENDED'
    if 'Alpha' in bsdf.inputs:
        bsdf.inputs['Alpha'].default_value = alpha
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m


def import_obj(filepath):
    if hasattr(bpy.ops.wm, 'obj_import'):
        bpy.ops.wm.obj_import(filepath=filepath)
    else:
        bpy.ops.import_scene.obj(filepath=filepath)


def tris_of(obj):
    return sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)


def main():
    log("=" * 56)
    log("脑壳烘焙 — all_obj → 减面 + 共享材质的 Unity mesh")
    log("=" * 56)
    log(f"项目: {PROJECT}")
    log(f"输出: {OUT_DIR}")
    log(f"减面目标: {TRI_BUDGET:,} 三角面")
    if os.path.abspath(OUT_DIR) == os.path.abspath(ASSET_DIR):
        log("⚠⚠ 输出目录 == 资产目录——那里是正典源与冻结快照，确认你要这么做")

    with open(os.path.join(PROJECT, "data", "brain_regions.json"), encoding="utf-8") as f:
        regions = json.load(f)["regions"]

    # 按 obj_file 去重（正典：多个 functional_id 共享同一解剖载体）
    by_file = {}
    for key, v in regions.items():
        p = v.get("obj_file")
        if not p:
            continue
        by_file.setdefault(p, []).append(key)
    log(f"解剖载体 {len(by_file)} 个文件 · functional_id {sum(len(v) for v in by_file.values())} 个")

    # 清场景
    for o in [o for o in list(bpy.data.objects)]:
        bpy.data.objects.remove(o, do_unlink=True)

    root = bpy.data.collections.new("BrainShell")
    bpy.context.scene.collection.children.link(root)

    missing, imported = [], []
    mats = {}
    for rel, fids in sorted(by_file.items()):
        path = os.path.join(PROJECT, rel)
        if not os.path.exists(path):
            missing.append(rel)
            continue
        before = set(bpy.data.objects)
        import_obj(path)
        new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
        lobe = obj_lobe(os.path.basename(rel))
        color = LOBE.get(lobe, LOBE["frontal"])
        mat = mats.setdefault(tuple(color), tissue_material(color, f"tissue_{lobe}"))
        for o in new:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            root.objects.link(o)
            o.name = fids[0] if len(new) == 1 else f"{fids[0]}_{o.name}"
            o.data.materials.clear()
            o.data.materials.append(mat)
            for fid in fids[1:]:
                o[f"functional_id_{fid}"] = True
            o["functional_ids"] = ",".join(fids)
            o["lobe"] = lobe
            imported.append(o)

    pre_tris = sum(tris_of(o) for o in imported)
    log(f"导入 {len(imported)} 个 mesh · 原始 {pre_tris:,} 三角面 · 材质 {len(mats)} 个")
    if missing:
        log(f"⚠ 缺失 {len(missing)} 个 OBJ（前 3：{missing[:3]}）——all_obj 需按登记重下")

    # 按原始面数比例分配预算 → Decimate COLLAPSE
    for o in imported:
        t = tris_of(o)
        if t == 0:
            continue
        share = TRI_BUDGET * (t / pre_tris) if pre_tris else 0
        ratio = min(1.0, share / t)
        if ratio < 1.0:
            mod = o.modifiers.new(name="Decimate", type='DECIMATE')
            mod.decimate_type = 'COLLAPSE'
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = o
            for x in bpy.context.selected_objects:
                x.select_set(False)
            o.select_set(True)
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception as e:
                log(f"⚠ {o.name} 减面失败：{e}")

    post_tris = sum(tris_of(o) for o in imported)
    log(f"减面后 {post_tris:,} 三角面（预算 {TRI_BUDGET:,} · 达成率 {100*post_tris/max(1,TRI_BUDGET):.0f}%）")

    os.makedirs(OUT_DIR, exist_ok=True)
    fbx = os.path.join(OUT_DIR, "brain_shell.fbx")
    props = bpy.ops.export_scene.fbx.get_rna_type().properties.keys()
    kw = {"filepath": fbx, "use_selection": False}
    for k, v in [("object_types", {'MESH'}), ("use_mesh_modifiers", True),
                 ("mesh_smooth_type", 'FACE'), ("axis_forward", '-Z'), ("axis_up", 'Y'),
                 ("apply_unit_scale", True), ("global_scale", 1.0), ("embed_textures", False)]:
        if k in props:
            kw[k] = v
    bpy.ops.object.select_all(action='DESELECT')
    for o in imported:
        o.select_set(True)
    try:
        bpy.ops.export_scene.fbx(**kw)
    except TypeError as e:
        log(f"⚠ 部分导出参数不被支持，改用最小参数重试：{e}")
        bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'MESH'})

    report = {
        "_description": "脑壳烘焙产出核对（工具：code/tools/bake_brain_shell.py）",
        "carrier_files": len(by_file),
        "functional_ids": sum(len(v) for v in by_file.values()),
        "imported_meshes": len(imported),
        "missing_files": missing,
        "tris_source": pre_tris,
        "tris_baked": post_tris,
        "tri_budget": TRI_BUDGET,
        "materials": sorted({m.name for m in mats.values()}),
        "material_count": len(mats),
        "fbx_bytes": os.path.getsize(fbx) if os.path.exists(fbx) else 0,
    }
    with open(os.path.join(OUT_DIR, "bake_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    log(f"FBX → {fbx}  ({report['fbx_bytes']/1e6:.1f} MB)")
    log(f"核对报告 → {os.path.join(OUT_DIR, 'bake_report.json')}")
    ok = (not missing) and post_tris <= TRI_BUDGET * 1.05
    log("✅ 达成" if ok else "⚠ 未达成（见报告）")


if __name__ == "__main__":
    main()
