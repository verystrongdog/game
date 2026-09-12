#!/usr/bin/env python3
"""
精神专科医院建筑设计方案参考图集 — 图像处理脚本
====================================================
功能：
  1. 从 PDF 提取所有页面为高分辨率 PNG（300 DPI，适合蓝图细节）
  2. 按医院规模（150床/300床/500床/大样图）分目录组织
  3. 图像增强：自适应对比度 + 锐化（让蓝图线条更清晰）
  4. 生成缩略图（快速浏览用）
  5. 生成 HTML 浏览页面（可交互的图集浏览器）
  6. 输出 JSON 清单（方便程序化引用）

用法：
  python3 code/tools/process_hospital_atlas.py [--pdf PATH] [--out PATH] [--dpi N]

依赖：
  - poppler-utils (pdftoppm)
  - Python 3 + Pillow
  sudo apt install poppler-utils python3-pillow
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ============================================================
# 配置
# ============================================================

# PDF 页面 → 章节映射（依据目录页和编制说明）
PAGE_SECTIONS = {
    # 文字部分（不渲染）
    **{p: "文字部分" for p in range(1, 6)},

    # 150床 方案一 (p6-10)
    **{p: "150床_方案一" for p in range(6, 11)},

    # 150床 方案二 (p11-14)
    **{p: "150床_方案二" for p in range(11, 15)},

    # 300床 方案一 (p15-18)
    **{p: "300床_方案一" for p in range(15, 19)},

    # 300床 方案二 (p19-23)
    **{p: "300床_方案二" for p in range(19, 24)},

    # 500床 方案一 (p24-28)
    **{p: "500床_方案一" for p in range(24, 29)},

    # 500床 方案二 (p29-32)
    **{p: "500床_方案二" for p in range(29, 33)},

    # 大样示意图 (p33-34)
    **{p: "大样示意图" for p in range(33, 35)},
}

# 楼层标注（根据建筑制图惯例推断，部分需人工确认）
PAGE_FLOOR_LABELS = {
    6:  "一层平面图",  7:  "二层平面图",  8:  "三层平面图",
    9:  "四层平面图", 10:  "五层平面图",
    11: "一层平面图", 12:  "二层平面图", 13:  "三层平面图", 14: "四层平面图",
    15: "一层平面图", 16:  "二层平面图", 17:  "三层平面图", 18: "四层平面图",
    19: "总平面图",   20:  "一层平面图", 21:  "二层平面图",
    22: "三层平面图", 23:  "四层平面图",
    24: "总平面图",   25:  "一层平面图", 26:  "二层平面图",
    27: "三层平面图", 28:  "四层平面图",
    29: "总平面图",   30:  "一层平面图", 31:  "二层平面图", 32: "三层平面图",
    33: "门窗大样",   34:  "细部大样",
}


def run_pdftoppm(pdf_path, out_dir, dpi=300, first_page=1, last_page=None):
    """调用 pdftoppm 提取页面为 PNG。返回输出文件路径列表。"""
    if last_page is None:
        # 获取总页数
        info = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
        for line in info.stdout.splitlines():
            if line.startswith("Pages:"):
                last_page = int(line.split(":")[1].strip())
                break

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pdftoppm", "-png",
        "-r", str(dpi),
        "-f", str(first_page),
        "-l", str(last_page),
        pdf_path,
        str(out_dir / "page"),
    ]
    print(f"[提取] {first_page}-{last_page} 页 → {out_dir} @ {dpi} DPI")
    subprocess.run(cmd, check=True, capture_output=True)

    # pdftoppm 输出的文件名格式: page-01.png, page-02.png, ...
    files = sorted(out_dir.glob("page-*.png"))
    return files


def enhance_blueprint(img_path, out_path, contrast=1.3, sharpen_radius=1.2, sharpen_amount=1.5):
    """
    蓝图增强：提高对比度 + 锐化线条。
    适用于 CAD 导出的黑白线稿图。
    """
    from PIL import Image, ImageEnhance, ImageFilter

    img = Image.open(img_path)

    # 转灰度（如果不是的话）
    if img.mode not in ("L", "1"):
        img = img.convert("L")

    # 自适应对比度拉伸（用 percentile 裁剪极值避免噪声放大）
    import numpy as np
    arr = np.asarray(img, dtype=np.float32)
    lo, hi = np.percentile(arr, [2, 98])
    if hi - lo > 10:
        arr = np.clip((arr - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # 对比度增强
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    # Unsharp mask 锐化
    if sharpen_amount > 0:
        img = img.filter(ImageFilter.UnsharpMask(radius=sharpen_radius, percent=int(sharpen_amount * 100)))

    img.save(out_path, "PNG", optimize=True)
    print(f"[增强] {img_path.name} → {Path(out_path).name}")


def create_thumbnail(img_path, out_path, size=(600, 400)):
    """生成缩略图。"""
    from PIL import Image

    img = Image.open(img_path)
    img.thumbnail(size, Image.LANCZOS)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def generate_html_gallery(base_dir, manifest):
    """生成 HTML 图集浏览器。"""
    base = Path(base_dir)
    html_path = base / "index.html"

    # 按章节分组
    sections = {}
    for entry in manifest["pages"]:
        sec = entry["section"]
        sections.setdefault(sec, []).append(entry)

    section_cards = []
    for sec_name, pages in sections.items():
        if sec_name == "文字部分":
            continue
        thumb_rows = []
        for p in pages:
            thumb_src = p["thumbnail"].replace(str(base) + "/", "")
            full_src = p["full_res"].replace(str(base) + "/", "")
            label = p.get("floor_label", "")
            thumb_rows.append(
                f'        <div class="page-card" onclick="openLightbox(\'{full_src}\')">'
                f'<img src="{thumb_src}" loading="lazy" alt="第{p["page"]}页">'
                f'<div class="label">p{p["page"]} — {label}</div></div>'
            )
        section_cards.append(
            f'    <section><h2>{sec_name}</h2><div class="grid">\n' +
            '\n'.join(thumb_rows) +
            '\n    </div></section>'
        )

    scale_labels = [s for s in sections if s != "文字部分"]
    nav_items = '\n'.join(f'      <li><a href="#{s}">{s}</a></li>' for s in scale_labels)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>精神专科医院建筑设计方案参考图集</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #1a1a2e; color: #e0e0e0; }}
  header {{ background: #16213e; padding: 24px 32px; border-bottom: 2px solid #0f3460; }}
  header h1 {{ font-size: 20px; font-weight: 500; }}
  header p {{ font-size: 13px; color: #8899aa; margin-top: 6px; }}
  nav {{ background: #0f3460; padding: 10px 32px; position: sticky; top: 0; z-index: 10; }}
  nav ul {{ list-style: none; display: flex; gap: 20px; flex-wrap: wrap; }}
  nav a {{ color: #c0d0e0; text-decoration: none; font-size: 13px; }}
  nav a:hover {{ color: #fff; }}
  main {{ padding: 24px 32px; }}
  section {{ margin-bottom: 40px; }}
  section h2 {{ font-size: 16px; font-weight: 500; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #333; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
  .page-card {{ background: #222244; border-radius: 6px; overflow: hidden; cursor: pointer; transition: transform .15s; }}
  .page-card:hover {{ transform: scale(1.02); }}
  .page-card img {{ width: 100%; height: 220px; object-fit: cover; display: block; }}
  .page-card .label {{ padding: 8px 12px; font-size: 12px; color: #aab; }}
  /* Lightbox */
  #lightbox {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,.92); z-index: 100; cursor: zoom-out; }}
  #lightbox img {{ max-width: 96vw; max-height: 96vh; position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); }}
  #lightbox .close {{ position: absolute; top: 16px; right: 24px; font-size: 28px; color: #aaa; cursor: pointer; }}
  .footer {{ text-align: center; padding: 32px; font-size: 11px; color: #556; }}
</style>
</head>
<body>
<header>
  <h1>精神专科医院建筑设计方案参考图集</h1>
  <p>卫生部编制 · 2009年12月 · 共34页 · 150床/300床/500床 + 大样图</p>
</header>
<nav><ul>
{nav_items}
</ul></nav>
<main>
{chr(10).join(section_cards)}
</main>
<div id="lightbox" onclick="this.style.display='none'">
  <span class="close">&times;</span>
  <img id="lightbox-img" src="">
</div>
<div class="footer">生成于 manifest.output_time · 来源: {manifest["source_pdf"]}</div>
<script>
function openLightbox(src) {{
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox').style.display = 'block';
}}
document.addEventListener('keydown', e => {{ if (e.key==='Escape') document.getElementById('lightbox').style.display='none'; }});
</script>
</body>
</html>'''

    html_path.write_text(html, encoding="utf-8")
    print(f"[HTML] 图集浏览器 → {html_path}")


def main():
    parser = argparse.ArgumentParser(description="精神专科医院参考图集处理脚本")
    parser.add_argument("--pdf", required=True,
                        help="输入 PDF 路径（2026-09-12：去掉开发机默认值——原值只在作者机器上存在，属掩盖）")
    parser.add_argument("--out", default="data/hospital_ref",
                        help="输出目录（相对于项目根目录）")
    parser.add_argument("--dpi", type=int, default=300,
                        help="渲染 DPI（默认 300，建筑图纸建议 ≥300）")
    parser.add_argument("--no-enhance", action="store_true",
                        help="跳过图像增强")
    parser.add_argument("--thumb-only", action="store_true",
                        help="只生成缩略图（已有全分辨率图的情况下）")
    parser.add_argument("--pages", type=str, default=None,
                        help="只处理指定页面，如 '6-10,15-18'")
    args = parser.parse_args()

    pdf_path = args.pdf
    if not os.path.exists(pdf_path):
        print(f"[错误] PDF 文件不存在: {pdf_path}")
        sys.exit(1)

    # 输出目录结构
    base = Path(args.out)
    full_dir = base / "full"       # 全分辨率 + 增强
    thumb_dir = base / "thumb"     # 缩略图

    print(f"{'='*60}")
    print(f"精神专科医院建筑设计方案参考图集 — 图像处理")
    print(f"  源文件: {pdf_path}")
    print(f"  输出基目录: {base}")
    print(f"  渲染 DPI: {args.dpi}")
    print(f"{'='*60}")

    # Step 1: 渲染页面
    if not args.thumb_only:
        raw_dir = base / "raw"
        raw_files = run_pdftoppm(pdf_path, raw_dir, dpi=args.dpi, first_page=6, last_page=34)
    else:
        raw_files = sorted(full_dir.glob("page-*.png"))
        if not raw_files:
            print("[错误] 没有找到全分辨率图片，请先不带 --thumb-only 运行一次")
            sys.exit(1)

    # Step 2: 图像增强 + 复制到 full 目录
    full_dir.mkdir(parents=True, exist_ok=True)
    enhanced_files = []
    for raw_file in raw_files:
        out_name = raw_file.name
        out_path = full_dir / out_name
        if not args.no_enhance:
            enhance_blueprint(raw_file, out_path)
        else:
            from PIL import Image
            Image.open(raw_file).save(out_path, "PNG", optimize=True)
        enhanced_files.append(out_path)

    # Step 3: 生成缩略图
    thumb_dir.mkdir(parents=True, exist_ok=True)
    for f in enhanced_files:
        thumb_path = thumb_dir / f.name
        create_thumbnail(f, thumb_path, size=(600, 420))

    # Step 4: 构建 manifest
    from datetime import datetime
    manifest = {
        "source_pdf": pdf_path,
        "total_pages": 34,
        "extracted_pages": len(enhanced_files),
        "dpi": args.dpi,
        "output_time": datetime.now().isoformat(),
        "directories": {
            "full_res": str(full_dir),
            "thumbnails": str(thumb_dir),
        },
        "pages": [],
    }

    for f in enhanced_files:
        # page-NN.png → 页码
        page_num = int(f.stem.split("-")[1])
        section = PAGE_SECTIONS.get(page_num, "未知")
        floor_label = PAGE_FLOOR_LABELS.get(page_num, "")
        manifest["pages"].append({
            "page": page_num,
            "section": section,
            "floor_label": floor_label,
            "full_res": str(f),
            "thumbnail": str(thumb_dir / f.name),
        })

    # 写 manifest
    manifest_path = base / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[清单] → {manifest_path}")

    # Step 5: 生成 HTML 浏览器
    generate_html_gallery(base, manifest)

    print(f"\n{'='*60}")
    print(f"完成！输出文件:")
    print(f"  全分辨率图: {full_dir}/  ({len(enhanced_files)} 张)")
    print(f"  缩略图:     {thumb_dir}/  ({len(enhanced_files)} 张)")
    print(f"  清单:       {manifest_path}")
    print(f"  HTML 浏览器: {base}/index.html")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
