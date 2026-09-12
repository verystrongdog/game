"""
玻璃大脑技能树 — Windows Blender 构建脚本
==========================================
在 Windows 版 Blender 中运行此脚本。

用法:
  方式1 (推荐): blender --background --python 此文件.py
  方式2 (GUI):   Blender → Scripting 工作区 → Open → 此文件 → Run Script

前置条件:
  - WSL 中已生成 data/brain_regions.json + data/skill_coords.json
  - WSL 中已解压 blender_assets/all_obj/ (brain-for-blender OBJ)
  - Windows 版 Blender >= 3.0

输出:
  - 技能树系统/blender_assets/brain_skill_tree.blend
  - 技能树系统/blender_assets/brain_skill_tree.glb
"""

import bpy
import json
import os
import math

# ═══════════════════════════════════════════════════════════
#  配置 — 按需修改
# ═══════════════════════════════════════════════════════════

# WSL 项目路径 (从 Windows 访问 WSL 文件)
# 格式: \\wsl$\<发行版名>\home\<用户名>\game
PROJECT = r"\\wsl$\Ubuntu\home\dog\game"

# 如果 WSL 路径不可用, 把 data/ 和 blender_assets/ 复制到 Windows 某目录, 然后改下面路径
# PROJECT = r"D:\game"

EXPORT_GLB = True     # 导出 GLB (给 Unity / 3D Viewer)
EXPORT_BLEND = True   # 保存 .blend (给 Blender)

OUTPUT_DIR = os.path.join(PROJECT, "技能树系统", "blender_assets")
DATA_DIR   = os.path.join(PROJECT, "data")
OBJ_DIR    = os.path.join(PROJECT, "技能树系统", "blender_assets", "all_obj")

# ═══════════════════════════════════════════════════════════
#  视觉配置
# ═══════════════════════════════════════════════════════════

NODE = {
    "cognition": {"radius": 1.5, "color": (0.48,0.56,1.0,1.0), "emit": (0.48,0.56,1.0)},
    "emotion":   {"radius": 1.7, "color": (0.94,0.63,0.38,1.0), "emit": (0.94,0.63,0.38)},
    "behavior":  {"radius": 1.5, "color": (0.31,0.76,0.97,1.0), "emit": (0.31,0.76,0.97)},
    "ultimate":  {"radius": 2.2, "color": (0.91,0.82,0.44,1.0), "emit": (0.91,0.82,0.44)},
}

# 脑叶颜色 (7色体系)
LOBE = {
    "frontal":           (0.48,0.56,1.0,1.0),
    "temporal":          (0.31,0.76,0.97,1.0),
    "parietal":          (0.42,0.53,0.95,1.0),
    "occipital":         (0.38,0.50,0.90,1.0),
    "parieto-occipital": (0.40,0.52,0.92,1.0),
    "temporo-parietal":  (0.36,0.64,0.96,1.0),
    "cingulate":         (0.94,0.63,0.38,1.0),
    "cingulate-insula":  (0.94,0.63,0.38,1.0),
    "insula":            (0.94,0.63,0.38,1.0),
    "limbic":            (0.94,0.63,0.38,1.0),
    "basal_ganglia":     (0.91,0.65,0.25,1.0),
    "diencephalon":      (0.75,0.35,0.30,1.0),
    "brainstem":         (0.75,0.30,0.25,1.0),
    "midbrain":          (0.75,0.33,0.28,1.0),
    "midbrain-temporal": (0.75,0.40,0.30,1.0),
    "frontal-temporal":  (0.55,0.55,0.65,1.0),
    "frontal-parietal":  (0.55,0.55,0.65,1.0),
    "frontal-insula":    (0.55,0.55,0.65,1.0),
}

# 深度透明度 (外层透→内层实)
ALPHA = {"cortical": 0.10, "subcortical": 0.20}

# ═══════════════════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════════════════

def log(msg):
    print(f"[BrainSkillTree] {msg}")

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def mat(name, base, emission=None, alpha=1.0, roughness=0.3):
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Roughness'].default_value = roughness
    if alpha < 1.0:
        m.blend_method = 'BLEND'
        m.shadow_method = 'NONE'
        bsdf.inputs['Alpha'].default_value = alpha
    if emission:
        bsdf.inputs['Emission'].default_value = (*emission, 0.3)
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# ═══════════════════════════════════════════════════════════
#  OBJ 文件名 → 脑叶 解析
# ═══════════════════════════════════════════════════════════

def obj_lobe(name):
    n = name.lower()
    m = {"amygdala":"temporal","hippocampus":"temporal","caudate":"basal_ganglia",
         "putamen":"basal_ganglia","pallidum":"basal_ganglia","accumbens":"basal_ganglia",
         "thalamus":"diencephalon","ventraldc":"diencephalon",
         "brain-stem":"brainstem","cerebellum":"brainstem",
         "ventricle":"frontal-temporal","cc_":"frontal-temporal"}
    for k, v in m.items():
        if k in n: return v
    if ".dk." in n:
        r = n.split(".dk.")[-1].replace(".obj","").strip()
        d = {"superiorfrontal":"frontal","rostralmiddlefrontal":"frontal","caudalmiddlefrontal":"frontal",
             "parsopercularis":"frontal","parstriangularis":"frontal","parsorbitalis":"frontal",
             "lateralorbitofrontal":"frontal","medialorbitofrontal":"frontal",
             "precentral":"frontal","paracentral":"frontal","frontalpole":"frontal",
             "superiortemporal":"temporal","middletemporal":"temporal","inferiortemporal":"temporal",
             "transversetemporal":"temporal","temporalpole":"temporal","fusiform":"temporal",
             "entorhinal":"temporal","parahippocampal":"temporal","bankssts":"temporal",
             "superiorparietal":"parietal","inferiorparietal":"parietal",
             "supramarginal":"parietal","precuneus":"parietal","postcentral":"parietal",
             "lateraloccipital":"occipital","lingual":"occipital",
             "pericalcarine":"occipital","cuneus":"occipital",
             "rostralanteriorcingulate":"cingulate","caudalanteriorcingulate":"cingulate",
             "posteriorcingulate":"cingulate","isthmuscingulate":"cingulate",
             "insula":"insula"}
        return d.get(r, "frontal")
    return "frontal"

# ═══════════════════════════════════════════════════════════
#  Section 1: 导入脑 OBJ
# ═══════════════════════════════════════════════════════════

def step1_import():
    log("="*50)
    log("1/6 导入脑 OBJ 文件")
    log("="*50)
    brain = coll("BrainMesh")
    ctx = coll("Cortex", brain)
    sub = coll("Subcortical", brain)
    n = 0

    dk = os.path.join(OBJ_DIR, "pial_DK")
    if os.path.isdir(dk):
        files = sorted([f for f in os.listdir(dk) if f.endswith('.obj')])
        log(f"DK 皮层: {len(files)} files")
        for i, f in enumerate(files):
            try:
                bpy.ops.import_scene.obj(filepath=os.path.join(dk, f))
                for o in bpy.context.selected_objects:
                    for c in o.users_collection: c.objects.unlink(o)
                    ctx.objects.link(o)
                n += 1
            except: pass
            if (i+1) % 20 == 0: log(f"  {i+1}/{len(files)}")

    sc = os.path.join(OBJ_DIR, "subcortical")
    if os.path.isdir(sc):
        files = sorted([f for f in os.listdir(sc) if f.endswith('.obj')])
        log(f"皮层下: {len(files)} files")
        for i, f in enumerate(files):
            try:
                bpy.ops.import_scene.obj(filepath=os.path.join(sc, f))
                for o in bpy.context.selected_objects:
                    for c in o.users_collection: c.objects.unlink(o)
                    sub.objects.link(o)
                n += 1
            except: pass
            if (i+1) % 20 == 0: log(f"  {i+1}/{len(files)}")
    log(f"导入完成: {n} OBJ")
    return ctx, sub

# ═══════════════════════════════════════════════════════════
#  Section 2: 玻璃材质
# ═══════════════════════════════════════════════════════════

def step2_materials(ctx, sub):
    log("="*50)
    log("2/6 玻璃材质 (脑叶颜色 + 分层透明度)")
    log("="*50)
    cmat, smat = {}, {}
    for lobe, clr in LOBE.items():
        cmat[lobe] = mat(f"ctx_{lobe}", clr, (clr[0]*0.2,clr[1]*0.2,clr[2]*0.2), alpha=ALPHA["cortical"])
        smat[lobe] = mat(f"sub_{lobe}", clr, (clr[0]*0.3,clr[1]*0.3,clr[2]*0.3), alpha=ALPHA["subcortical"])

    cc, sc = 0, 0
    if ctx:
        for o in ctx.all_objects:
            if o.type == 'MESH':
                o.data.materials.clear()
                o.data.materials.append(cmat.get(obj_lobe(o.name), cmat["frontal"]))
                cc += 1
    if sub:
        for o in sub.all_objects:
            if o.type == 'MESH':
                o.data.materials.clear()
                o.data.materials.append(smat.get(obj_lobe(o.name), smat["basal_ganglia"]))
                sc += 1
    log(f"皮层: {cc} (α=0.10) | 皮层下: {sc} (α=0.20)")
    log("蓝紫=额叶  青蓝=颞叶  靛蓝=顶叶/枕叶  暖橙=边缘  琥珀=基底节  红褐=脑干")

# ═══════════════════════════════════════════════════════════
#  Section 3: 技能节点
# ═══════════════════════════════════════════════════════════

def step3_nodes():
    log("="*50)
    log("3/6 放置 74 技能节点")
    log("="*50)

    sp = os.path.join(DATA_DIR, "skill_coords.json")
    rp = os.path.join(DATA_DIR, "brain_regions.json")
    with open(sp, "r", encoding="utf-8") as f: skills = json.load(f)
    with open(rp, "r", encoding="utf-8") as f: regions = json.load(f)

    root = coll("SkillNodes")
    bc = {b: coll(b.capitalize(), root) for b in ["cognition","emotion","behavior","ultimate"]}
    nodes = {}

    for s in skills["skills"]:
        sid, name, branch = s["id"], s["name"], s["branch"]
        rk = s.get("region_matched")
        xyz = None

        if rk and rk in regions["regions"]:
            r = regions["regions"][rk]
            fs = r.get("fs_xyz")
            if fs:
                px = s["pad_xyz"][0]
                xyz = ((abs(fs[0]) if px>0.05 else -abs(fs[0]) if px<-0.05 else 0), fs[1], fs[2])

        if not xyz:
            gx, gy, gz = s["game_xyz_new"]
            xyz = (gx*70, gz*120/0.85, (gy-0.55)*75)

        cfg = NODE.get(branch, NODE["cognition"])
        x, y, z = xyz
        r = cfg["radius"]

        if cfg == NODE["cognition"]:   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(x,y,z))
        elif cfg == NODE["emotion"]:   bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x,y,z))
        elif cfg == NODE["behavior"]:  bpy.ops.mesh.primitive_cube_add(size=r*2.5, location=(x,y,z))
        else:                          bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(x,y,z))

        obj = bpy.context.active_object
        obj.name = f"{sid}_{name}"
        for k, v in [("skill_id",sid),("skill_name",name),("branch",branch),("tier",str(s.get("tier","")))]:
            obj[k] = v

        nm = mat(f"n_{branch}", cfg["color"], cfg["emit"], alpha=0.9, roughness=0.2)
        obj.data.materials.append(nm)
        for c in obj.users_collection: c.objects.unlink(obj)
        bc[branch].objects.link(obj)
        nodes[sid] = obj

    log(f"放置: {len(nodes)} 节点")
    return nodes

# ═══════════════════════════════════════════════════════════
#  Section 4: 连线
# ═══════════════════════════════════════════════════════════

def step4_tracts(nodes):
    log("="*50)
    log("4/6 创建连线 (功能前置 + 层级升级)")
    log("="*50)

    tc = coll("Tracts")
    fc = coll("Functional", tc)
    lc = coll("Tier", tc)

    sp = os.path.join(DATA_DIR, "skill_coords.json")
    with open(sp, "r", encoding="utf-8") as f: data = json.load(f)

    # 功能前置
    fn = 0
    for p in data.get("prereqs", []):
        if len(p) >= 2 and p[0] in nodes and p[1] in nodes:
            bez(nodes[p[0]], nodes[p[1]], fc, tier=False)
            fn += 1

    # 层级升级
    tn = tier_lines(nodes, lc)
    log(f"功能: {fn} | 层级: {tn} | 合计: {fn+tn}")


def tier_lines(nodes, collection):
    br = {"cognition":{}, "emotion":{}, "behavior":{}}
    for sid, o in nodes.items():
        b, t = o.get("branch",""), o.get("tier","")
        if b in br and t.isdigit(): br[b].setdefault(int(t),[]).append(o)

    clr = {"cognition":(0.4,0.5,0.9,0.7),"emotion":(0.9,0.5,0.3,0.7),"behavior":(0.3,0.7,0.9,0.7)}
    count = 0
    for b, tiers in br.items():
        st = sorted(tiers.keys())
        c = clr.get(b, (0.5,)*4)
        for i in range(len(st)-1):
            for fo in tiers[st[i]]:
                near = min(tiers[st[i+1]], key=lambda o: (fo.location-o.location).length)
                bez(fo, near, collection, tier=True, color=c)
                count += 1

    # L5 → 终极
    ult = [o for sid,o in nodes.items() if o.get("branch")=="ultimate"]
    if ult:
        uc = (0.9,0.8,0.4,0.8)
        for b, tiers in br.items():
            mx = max(tiers.keys())
            for fo in tiers[mx][:3]:
                for uo in ult[:2]:
                    bez(fo, uo, collection, tier=True, color=uc)
                    count += 1
    return count


def bez(fr, to, collection, tier=False, color=None):
    fp, tp = fr.location, to.location
    mx, my, mz = (fp.x+tp.x)/2, (fp.y+tp.y)/2, (fp.z+tp.z)/2
    mid = (mx, my, mz+(5.0 if tier else 3.0))

    cd = bpy.data.curves.new(f"{'t' if tier else 'f'}_{fr.name}_{to.name}", 'CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = 0.25 if tier else 0.15
    sp = cd.splines.new('BEZIER')
    sp.bezier_points.add(2)
    for i, pt in enumerate([fp, mid, tp]):
        sp.bezier_points[i].co = pt
        sp.bezier_points[i].handle_left_type = 'AUTO'
        sp.bezier_points[i].handle_right_type = 'AUTO'

    co = bpy.data.objects.new(cd.name, cd)
    collection.objects.link(co)
    c = color or (0.4,0.5,0.7,0.5)
    m = mat(f"tr_{'t' if tier else 'f'}", c, (c[0]*0.5,c[1]*0.5,c[2]*0.5), alpha=c[3])
    co.data.materials.append(m)
    return co

# ═══════════════════════════════════════════════════════════
#  Section 5: 灯光与渲染
# ═══════════════════════════════════════════════════════════

def step5_lighting():
    log("="*50)
    log("5/6 灯光与渲染设置")
    log("="*50)

    for o in list(bpy.data.objects):
        if o.type == 'LIGHT': bpy.data.objects.remove(o, do_unlink=True)

    for name, loc, en, clr in [
        ("Key", (80,-40,80), 300, (1.0,0.95,0.85)),
        ("Fill", (-60,30,-40), 150, (0.5,0.6,0.8)),
        ("Rim", (0,0,-80), 80, (0.2,0.25,0.35)),
    ]:
        bpy.ops.object.light_add(type='AREA', location=loc)
        l = bpy.context.active_object
        l.name = name; l.data.energy = en; l.data.color = clr

    w = bpy.context.scene.world
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04,0.04,0.08,1.0)
        bg.inputs["Strength"].default_value = 0.3

    cam = bpy.data.objects.get("Camera")
    if cam:
        cam.location = (0,-200,40)
        cam.rotation_euler = (math.radians(80),0,0)
        cam.data.lens = 50

    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    try: s.eevee.use_bloom = True; s.eevee.bloom_intensity = 0.3
    except: pass
    s.render.resolution_x = 1920
    s.render.resolution_y = 1080
    log("EEVEE + Bloom + 3-point light")

# ═══════════════════════════════════════════════════════════
#  Section 6: 导出
# ═══════════════════════════════════════════════════════════

def step6_export():
    log("="*50)
    log("6/6 导出")
    log("="*50)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if EXPORT_BLEND:
        fp = os.path.join(OUTPUT_DIR, "brain_skill_tree.blend")
        bpy.ops.wm.save_as_mainfile(filepath=fp)
        log(f".blend → {fp}")

    if EXPORT_GLB:
        fp = os.path.join(OUTPUT_DIR, "brain_skill_tree.glb")
        log(f"Exporting .glb ...")
        bpy.ops.object.select_all(action='DESELECT')
        for cn in ["BrainMesh","SkillNodes","Tracts"]:
            c = bpy.data.collections.get(cn)
            if c:
                for o in c.all_objects: o.select_set(True)
        try:
            bpy.ops.export_scene.gltf(filepath=fp, use_selection=True, export_format='GLB')
            log(f".glb → {fp}")
        except Exception as e:
            log(f"GLB export failed: {e}")
            try:
                bpy.ops.export_scene.gltf(filepath=fp, export_format='GLB')
                log(f".glb → {fp} (all objects)")
            except Exception as e2:
                log(f"GLB retry also failed: {e2}")

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main():
    log("")
    log("╔══════════════════════════════════════════╗")
    log("║  🧠 玻璃大脑技能树 v2                     ║")
    log("║  脑叶着色 · 分层透明 · 升级连线            ║")
    log("╚══════════════════════════════════════════╝")
    log(f"项目路径: {PROJECT}")

    if not os.path.isdir(PROJECT):
        log(f"\n!!! 错误: 找不到项目路径")
        log(f"!!! {PROJECT}")
        log(f"!!! 请修改脚本顶部的 PROJECT 变量\n")
        return
    if not os.path.isdir(OBJ_DIR):
        log(f"\n!!! 错误: 找不到 OBJ 目录")
        log(f"!!! {OBJ_DIR}")
        log(f"!!! 确保 WSL 中已解压 brain-for-blender 数据\n")
        return

    # 清场景
    for o in [o for o in list(bpy.data.objects) if o.type in ('MESH','EMPTY','CURVE')]:
        bpy.data.objects.remove(o, do_unlink=True)

    ctx, sub = step1_import()
    step2_materials(ctx, sub)
    nodes = step3_nodes()
    step4_tracts(nodes)
    step5_lighting()
    step6_export()

    log("\n╔══════════════════════════════════════════╗")
    log("║  ✅ 构建完成!                             ║")
    log(f"║  .blend: brain_skill_tree.blend          ║")
    if EXPORT_GLB:
        log(f"║  .glb:   brain_skill_tree.glb            ║")
    log("╚══════════════════════════════════════════╝\n")

if __name__ == "__main__":
    main()
