#!/usr/bin/env python3
"""态度晶体可视化 — 同时生成 PNG 图片 + 交互式 HTML"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from mpl_toolkits.mplot3d import Axes3D

# ============================================================
# 数据准备
# ============================================================
values = [1, 0, -1]
value_labels = {1: '积极', 0: '中性', -1: '消极'}
points = list(product(values, repeat=3))

def get_attitude_name(cog, emo, beh):
    parts = []
    if cog == 1:    parts.append('积极认知')
    elif cog == -1: parts.append('消极认知')
    if emo == 1:    parts.append('积极情绪')
    elif emo == -1: parts.append('消极情绪')
    if beh == 1:    parts.append('积极行为')
    elif beh == -1: parts.append('消极行为')
    return '纯中性' if not parts else '+'.join(parts)

def get_color(cog, emo, beh):
    return ((cog + 1) / 2, (emo + 1) / 2, (beh + 1) / 2)

def get_category(cog, emo, beh):
    s = cog + emo + beh
    pc = sum(1 for v in (cog, emo, beh) if v == 1)
    nc = sum(1 for v in (cog, emo, beh) if v == -1)
    if pc == 3:       return '纯积极'
    elif nc == 3:     return '纯消极'
    elif pc == 0 and nc == 0: return '纯中性'
    elif s > 0:       return '偏积极'
    elif s < 0:       return '偏消极'
    elif pc and nc:   return '混合'
    return '含中性'

# 统计
positives = sum(1 for p in points if sum(p) > 0)
negatives = sum(1 for p in points if sum(p) < 0)
zero_sum  = sum(1 for p in points if sum(p) == 0)

# 按类别分组用于图例颜色
cat_colors = {
    '纯积极': '#ff4444',
    '纯消极': '#4444ff',
    '纯中性': '#888888',
    '偏积极': '#ff9944',
    '偏消极': '#4488cc',
}

# ============================================================
# PNG 静态图（matplotlib）
# ============================================================
print("🎨 生成静态 PNG...")
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Noto Serif CJK JP', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(18, 14))
ax = fig.add_subplot(111, projection='3d')

# 晶格连线
for i, p1 in enumerate(points):
    for j, p2 in enumerate(points):
        if i >= j: continue
        if sum(abs(a - b) for a, b in zip(p1, p2)) == 1:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                    color='gray', linewidth=0.6, alpha=0.25, zorder=0)

# 态度点
for cog, emo, beh in points:
    color = get_color(cog, emo, beh)
    name = get_attitude_name(cog, emo, beh)
    cat = get_category(cog, emo, beh)
    is_corner = (abs(cog) + abs(emo) + abs(beh)) == 3
    size = 160 if is_corner else 70

    ax.scatter(cog, emo, beh, c=[color], s=size, edgecolors='black',
               linewidth=0.4, alpha=0.9, zorder=5)

    # 只为关键点加标签
    if is_corner:
        ax.text(cog + 0.12, emo + 0.12, beh + 0.12, name,
                fontsize=8, alpha=0.9, fontfamily='sans-serif')

# 坐标轴
ax.set_xlabel('认知', fontsize=13, labelpad=10)
ax.set_ylabel('情绪', fontsize=13, labelpad=10)
ax.set_zlabel('行为', fontsize=13, labelpad=10)
ax.set_xticks([-1, 0, 1])
ax.set_yticks([-1, 0, 1])
ax.set_zticks([-1, 0, 1])
ax.set_xticklabels(['消极', '中性', '积极'], fontsize=10)
ax.set_yticklabels(['消极', '中性', '积极'], fontsize=10)
ax.set_zticklabels(['消极', '中性', '积极'], fontsize=10)
ax.set_box_aspect([1, 1, 1])

ax.set_title('态度晶体 — 认知 × 情绪 × 行为 = 27种态度\nAttitude Crystal',
             fontsize=18, fontweight='bold', pad=25)

# 图例
from matplotlib.patches import Patch
legend_handles = [
    Patch(color=get_color(1,1,1),   label='纯积极 (+++)'),
    Patch(color=get_color(-1,-1,-1), label='纯消极 (---)'),
    Patch(color=get_color(0,0,0),   label='纯中性 (000)'),
    Patch(color=get_color(1,0,-1),  label='混合态度'),
]
ax.legend(handles=legend_handles, loc='upper left', fontsize=10,
          title='图例', title_fontsize=11)

# 统计信息
info = f'27种态度 | 正面倾向 {positives} | 中性 {zero_sum} | 负面倾向 {negatives}'
fig.text(0.5, 0.01, info, ha='center', fontsize=12, style='italic', color='#555')

plt.tight_layout(rect=[0, 0.03, 1, 1])
png_path = '/home/dog/game/attitude_crystal.png'
plt.savefig(png_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   ✅ PNG 已保存: {png_path}")

# ============================================================
# 交互式 HTML（Plotly）
# ============================================================
print("🌐 生成交互式 HTML...")

scatter_data = []
for cog, emo, beh in points:
    name = get_attitude_name(cog, emo, beh)
    cat = get_category(cog, emo, beh)
    s = cog + emo + beh
    pc = sum(1 for v in (cog, emo, beh) if v == 1)
    nc = sum(1 for v in (cog, emo, beh) if v == -1)
    r, g, b = [int((v + 1) / 2 * 255) for v in (cog, emo, beh)]
    scatter_data.append({
        'x': cog, 'y': emo, 'z': beh,
        'name': name, 'category': cat, 'sum': s,
        'pos_count': pc, 'neg_count': nc,
        'color': f'rgb({r},{g},{b})',
        'label_cog': value_labels[cog],
        'label_emo': value_labels[emo],
        'label_beh': value_labels[beh],
    })

edges = []
for i, p1 in enumerate(points):
    for j, p2 in enumerate(points):
        if i >= j: continue
        if sum(abs(a - b) for a, b in zip(p1, p2)) == 1:
            edges.append({'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
                          'x2': p2[0], 'y2': p2[1], 'z2': p2[2]})

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>态度晶体 — 27种态度 3D 可视化</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #1a1a2e; color: #eee; font-family: 'Segoe UI','Noto Sans SC',sans-serif; overflow: hidden; height: 100vh; }}
  #plot {{ width: 100vw; height: 100vh; cursor: grab; }}
  #plot:active {{ cursor: grabbing; }}
  #info-panel {{
    position: absolute; top: 20px; left: 20px;
    background: rgba(0,0,0,0.75); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15); border-radius: 12px;
    padding: 18px 22px; pointer-events: none; max-width: 380px;
  }}
  #info-panel h1 {{
    font-size: 22px; margin-bottom: 4px;
    background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;
  }}
  #info-panel .subtitle {{ font-size: 12px; color: #999; margin-bottom: 12px; }}
  .stats {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; }}
  .stats span {{ opacity: 0.85; }}
  .axis-legend {{
    position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 24px;
    background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
    border-radius: 10px; padding: 10px 20px; font-size: 13px;
  }}
  .axis-legend .item {{ display: flex; align-items: center; gap: 6px; }}
  .axis-legend .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
</style>
</head>
<body>
<div id="plot"></div>

<div id="info-panel">
  <h1>态度晶体 · Attitude Crystal</h1>
  <div class="subtitle">认知 × 情绪 × 行为 = 27种态度</div>
  <div class="stats">
    <span>🟢 正面倾向: {positives}种</span>
    <span>⚪ 中性: {zero_sum}种</span>
    <span>🔴 负面倾向: {negatives}种</span>
  </div>
</div>

<div class="axis-legend">
  <div class="item"><div class="dot" style="background:#ff4444"></div> R = 认知轴</div>
  <div class="item"><div class="dot" style="background:#44ff44"></div> G = 情绪轴</div>
  <div class="item"><div class="dot" style="background:#4444ff"></div> B = 行为轴</div>
</div>

<script>
const scatterData = {json.dumps(scatter_data, ensure_ascii=False)};
const edges = {json.dumps(edges, ensure_ascii=False)};

const traces = [];
const ex = [], ey = [], ez = [];
edges.forEach(e => {{ ex.push(e.x1,e.x2,null); ey.push(e.y1,e.y2,null); ez.push(e.z1,e.z2,null); }});
traces.push({{ type:'scatter3d', mode:'lines', x:ex, y:ey, z:ez,
  line:{{ color:'rgba(255,255,255,0.15)', width:1 }}, hoverinfo:'skip', showlegend:false }});

scatterData.forEach(pt => {{
  traces.push({{
    type:'scatter3d', mode:'markers+text',
    x:[pt.x], y:[pt.y], z:[pt.z], text:[pt.name],
    textposition:'top center',
    textfont:{{ size:9, color:'#ccc', family:'Noto Sans SC, sans-serif' }},
    marker:{{ color:pt.color,
      size:(pt.pos_count===3||pt.neg_count===3||(pt.sum===0&&pt.pos_count===0))?14:8,
      symbol:'circle', line:{{ color:'rgba(255,255,255,0.4)', width:1 }} }},
    hovertemplate:('<b>%{{text}}</b><br>认知: '+pt.label_cog+' | 情绪: '+pt.label_emo+' | 行为: '+pt.label_beh+'<br>总和倾向: '+(pt.sum>0?'+':'')+pt.sum+'<br>类别: '+pt.category+'<extra></extra>'),
    showlegend:false,
  }});
}});

traces.push(
  {{ type:'scatter3d', mode:'markers', x:[null],y:[null],z:[null],
     marker:{{ color:'rgb(255,255,255)', size:12, symbol:'circle', line:{{ width:1, color:'#fff' }} }},
     name:'纯积极 (+++)' }},
  {{ type:'scatter3d', mode:'markers', x:[null],y:[null],z:[null],
     marker:{{ color:'rgb(0,0,0)', size:12, symbol:'circle', line:{{ width:1, color:'#fff' }} }},
     name:'纯消极 (---)' }},
  {{ type:'scatter3d', mode:'markers', x:[null],y:[null],z:[null],
     marker:{{ color:'rgb(128,128,128)', size:12, symbol:'circle', line:{{ width:1, color:'#fff' }} }},
     name:'纯中性 (000)' }}
);

Plotly.newPlot('plot', traces, {{
  scene: {{
    xaxis:{{ title:'认知', tickvals:[-1,0,1], ticktext:['消极(-1)','中性(0)','积极(+1)'],
      gridcolor:'rgba(255,255,255,0.08)', zerolinecolor:'rgba(255,255,255,0.2)', color:'#aaa' }},
    yaxis:{{ title:'情绪', tickvals:[-1,0,1], ticktext:['消极(-1)','中性(0)','积极(+1)'],
      gridcolor:'rgba(255,255,255,0.08)', zerolinecolor:'rgba(255,255,255,0.2)', color:'#aaa' }},
    zaxis:{{ title:'行为', tickvals:[-1,0,1], ticktext:['消极(-1)','中性(0)','积极(+1)'],
      gridcolor:'rgba(255,255,255,0.08)', zerolinecolor:'rgba(255,255,255,0.2)', color:'#aaa' }},
    aspectmode:'cube',
    camera:{{ eye:{{ x:1.6, y:1.6, z:1.6 }}, center:{{ x:0, y:0, z:0 }} }},
    bgcolor:'rgba(0,0,0,0)',
  }},
  paper_bgcolor:'rgba(0,0,0,0)', margin:{{ l:0, r:0, t:0, b:0 }},
  legend:{{ x:0.02, y:0.98, font:{{ color:'#ccc', size:11 }}, bgcolor:'rgba(0,0,0,0.5)' }},
  hovermode:'closest',
}}, {{ responsive:true, displayModeBar:true,
  modeBarButtonsToRemove:['lasso2d','select2d'], displaylogo:false,
  toImageButtonOptions:{{ format:'png', filename:'attitude_crystal' }} }});
</script>
</body>
</html>'''

html_path = '/home/dog/game/attitude_crystal.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"   ✅ HTML 已保存: {html_path}")

# ============================================================
# 打印态度列表
# ============================================================
print(f"\n{'='*60}")
print(f"  27种态度 = 3³ = 认知({'+/0/-'}) × 情绪({'+/0/-'}) × 行为({'+/0/-'})")
print(f"  正面倾向 {positives} | 中性 {zero_sum} | 负面倾向 {negatives}")
print(f"{'='*60}")
print(f"\n{'认知':^8} {'情绪':^8} {'行为':^8} {'态度名称':<32} {'类别'}")
print("-" * 72)
for cog, emo, beh in sorted(points, key=lambda p: (-sum(p), p[0], p[1], p[2])):
    name = get_attitude_name(cog, emo, beh)
    cat = get_category(cog, emo, beh)
    print(f"{value_labels[cog]:^8} {value_labels[emo]:^8} {value_labels[beh]:^8} {name:<32} {cat}")
