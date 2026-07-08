#!/usr/bin/env python3
"""
态度空间模型 (Attitude Space Model) 可视化
===========================================
基于"态度空间模型.docx"中的完整定义：
  - 27种态度，每种有专属四字成语名称
  - 5种分类：一致型 / 行为冲突型 / 情绪冲突型 / 认知冲突型 / 三维冲突型
  - 态度强度 I = C²+E²+B²
  - 态度冲突度 K = 3 - 一致性分数
  - 态度稳定度 S = 3 - K

输出：
  - attitude_space.png   : matplotlib 静态高清图
  - attitude_space.html  : Plotly 交互式 3D 网页
"""

import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from mpl_toolkits.mplot3d import Axes3D

# ============================================================
# 0. 基础数据 — 严格来自文档
# ============================================================
values = [1, 0, -1]
val_label = {1: '积极', 0: '中性', -1: '消极'}
val_char  = {1: '+', 0: '0', -1: '-'}

points = list(product(values, repeat=3))  # 27 个点

# 文档 第3节：每个坐标的专属四字成语名称
ATTITUDE_NAMES = {
    (+1, +1, +1): '心悦诚服',
    (+1, +1,  0): '跃跃欲试',
    (+1, +1, -1): '有心无力',
    (+1,  0, +1): '知行合一',
    (+1,  0,  0): '静观其变',
    (+1,  0, -1): '望而生畏',
    (+1, -1, +1): '忍辱负重',
    (+1, -1,  0): '貌合神离',
    (+1, -1, -1): '知难而退',
    ( 0, +1, +1): '感情用事',
    ( 0, +1,  0): '拭目以待',
    ( 0, +1, -1): '望而却步',
    ( 0,  0, +1): '顺势而为',
    ( 0,  0,  0): '随遇而安',
    ( 0,  0, -1): '置身事外',
    ( 0, -1, +1): '勉为其难',
    ( 0, -1,  0): '冷眼旁观',
    ( 0, -1, -1): '避而远之',
    (-1, +1, +1): '自欺欺人',
    (-1, +1,  0): '将信将疑',
    (-1, +1, -1): '进退两难',
    (-1,  0, +1): '迫不得已',
    (-1,  0,  0): '不以为然',
    (-1,  0, -1): '敬而远之',
    (-1, -1, +1): '逆流而上',
    (-1, -1,  0): '黯然神伤',
    (-1, -1, -1): '深恶痛绝',
}

# 文档 第4节：5类结构划分
def get_category(c, e, b):
    """
    一致型 (Consistent)       : 三维同号 → (+++) (000) (---)
    行为冲突型 (Behavior conflict): 行为与认知情绪异号
    情绪冲突型 (Emotion conflict) : 情绪与认知行为异号
    认知冲突型 (Cognition conflict): 认知与情绪行为异号
    三维冲突型 (Full conflict)    : 三维两正一负或两负一正且三者无一致
    """
    if c == e == b:
        return '一致型'
    # 行为冲突：行为方向与(认知,情绪)不同，且认知==情绪
    if c == e and c != b and c != 0 and b != 0:
        return '行为冲突型'
    # 情绪冲突：情绪与(认知,行为)不同，且认知==行为
    if c == b and c != e and c != 0 and e != 0:
        return '情绪冲突型'
    # 认知冲突：认知与(情绪,行为)不同，且情绪==行为
    if e == b and e != c and e != 0 and c != 0:
        return '认知冲突型'
    # 其余为三维冲突（含中性维度的混合情况）
    return '三维冲突型'


# 文档 第6节：态度强度 I = C² + E² + B²
def get_strength(c, e, b):
    return c*c + e*e + b*b

# 文档 第7节：态度冲突度 K = max - min (三维极差)
def get_conflict(c, e, b):
    return max(c, e, b) - min(c, e, b)

# 文档 第8节：态度稳定度 S = 3 - K
def get_stability(c, e, b):
    return 3 - get_conflict(c, e, b)

# 欧氏距离
def euclidean(p1, p2):
    return math.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))

# ============================================================
# 颜色映射
# ============================================================
def rgb_color(c, e, b):
    """将 [-1,0,1] 映射到 RGB 通道: -1→0, 0→127, 1→255"""
    return tuple(int((v + 1) / 2 * 255) for v in (c, e, b))

def hex_color(c, e, b):
    r, g, b = rgb_color(c, e, b)
    return f'#{r:02x}{g:02x}{b:02x}'

def rgb_str(c, e, b):
    r, g, b = rgb_color(c, e, b)
    return f'rgb({r},{g},{b})'

CATEGORY_COLORS = {
    '一致型':      '#e74c3c',  # 红
    '行为冲突型':  '#f39c12',  # 橙
    '情绪冲突型':  '#2ecc71',  # 绿
    '认知冲突型':  '#3498db',  # 蓝
    '三维冲突型':  '#9b59b6',  # 紫
}

# ============================================================
# 统计信息
# ============================================================
stats_by_cat = {}
for p in points:
    cat = get_category(*p)
    stats_by_cat.setdefault(cat, []).append(p)

pos_count = sum(1 for p in points if sum(p) > 0)
neu_count = sum(1 for p in points if sum(p) == 0)
neg_count = sum(1 for p in points if sum(p) < 0)

print(f"态度空间模型: 27种态度")
print(f"  正面倾向: {pos_count}  中性: {neu_count}  负面倾向: {neg_count}")
for cat, pts in sorted(stats_by_cat.items()):
    print(f"  {cat}: {len(pts)}种 — {', '.join(ATTITUDE_NAMES[p] for p in pts)}")

# ============================================================
# 1. Matplotlib 静态图
# ============================================================
print("\n🎨 生成静态 PNG...")
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(22, 17))
ax = fig.add_subplot(111, projection='3d')

# -- 晶格连线 --
for i, p1 in enumerate(points):
    for j, p2 in enumerate(points):
        if i >= j:
            continue
        if sum(abs(a - b) for a, b in zip(p1, p2)) == 1:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                    color='gray', linewidth=0.5, alpha=0.2, zorder=0)

# -- 态度点 --
for c, e, b in points:
    name = ATTITUDE_NAMES[(c, e, b)]
    cat  = get_category(c, e, b)
    color = tuple(v / 255 for v in rgb_color(c, e, b))
    strength = get_strength(c, e, b)
    size = 50 + strength * 60  # 强度越大点越大

    ax.scatter(c, e, b, c=[color], s=size, edgecolors='black',
               linewidth=0.3, alpha=0.92, zorder=5)

    # 所有点都标上成语名
    offset = 0.18
    ax.text(c + offset, e + offset, b + offset, name,
            fontsize=7, alpha=0.85, ha='center',
            fontfamily='sans-serif')

# -- 坐标轴 --
ax.set_xlabel('认知 Cognition', fontsize=13, labelpad=12)
ax.set_ylabel('情绪 Emotion',   fontsize=13, labelpad=12)
ax.set_zlabel('行为 Behavior',  fontsize=13, labelpad=12)
ax.set_xticks([-1, 0, 1])
ax.set_yticks([-1, 0, 1])
ax.set_zticks([-1, 0, 1])
ax.set_xticklabels(['消极 −', '中性 0', '积极 +'], fontsize=10)
ax.set_yticklabels(['消极 −', '中性 0', '积极 +'], fontsize=10)
ax.set_zticklabels(['消极 −', '中性 0', '积极 +'], fontsize=10)
ax.set_box_aspect([1, 1, 1])

ax.set_title('态度空间模型 · Attitude Space Model\n'
             '认知 × 情绪 × 行为 = 3³ = 27种态度',
             fontsize=20, fontweight='bold', pad=30)

# -- 分类图例 --
from matplotlib.patches import Patch
legend_handles = []
for cat, color in CATEGORY_COLORS.items():
    count = len(stats_by_cat[cat])
    legend_handles.append(Patch(color=color, label=f'{cat} ({count}种)'))
# 额外：颜色=RGB含义
legend_handles.append(Patch(color='#aaaaaa', label='点颜色=RGB(认知情,情绪情,行为情)'))

ax.legend(handles=legend_handles, loc='upper left', fontsize=9,
          title='分类 (边框颜色)', title_fontsize=10)

# -- 底部统计 --
info_lines = [
    f'正面倾向 {pos_count} · 中性 {neu_count} · 负面倾向 {neg_count}',
    '强度 I=C²+E²+B²  ·  冲突度 K=极差  ·  稳定度 S=3−K  ·  距离 d=欧氏距离'
]
fig.text(0.5, 0.015, '\n'.join(info_lines), ha='center', fontsize=11,
         style='italic', color='#555')

plt.tight_layout(rect=[0, 0.06, 1, 1])
png_path = '/home/dog/game/attitude_space.png'
plt.savefig(png_path, dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   ✅ PNG 已保存: {png_path}")


# ============================================================
# 2. Plotly 交互式 HTML
# ============================================================
print("🌐 生成交互式 HTML...")

# 准备连线数据
edges = []
for i, p1 in enumerate(points):
    for j, p2 in enumerate(points):
        if i >= j:
            continue
        if sum(abs(a - b) for a, b in zip(p1, p2)) == 1:
            edges.append({'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
                          'x2': p2[0], 'y2': p2[1], 'z2': p2[2]})

# 准备点数据
scatter_data = []
for c, e, b in points:
    name = ATTITUDE_NAMES[(c, e, b)]
    cat  = get_category(c, e, b)
    s    = c + e + b
    I    = get_strength(c, e, b)
    K    = get_conflict(c, e, b)
    S    = get_stability(c, e, b)
    scatter_data.append({
        'x': c, 'y': e, 'z': b,
        'name': name, 'category': cat, 'sum': s,
        'strength': I, 'conflict': K, 'stability': S,
        'color': rgb_str(c, e, b),
        'label_c': val_label[c],
        'label_e': val_label[e],
        'label_b': val_label[b],
    })

# 强度层级（用于筛选器）
strength_groups = {0: [], 1: [], 2: [], 3: []}
for d in scatter_data:
    strength_groups[d['strength']].append(d['name'])

# 生成 HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>态度空间模型 · Attitude Space Model</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0d1117; color: #c9d1d9;
    font-family: 'Segoe UI', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
    overflow: hidden; height: 100vh; display: flex;
  }}
  #sidebar {{
    width: 320px; min-width: 320px;
    background: #161b22; border-right: 1px solid #30363d;
    display: flex; flex-direction: column; overflow-y: auto;
    padding: 20px;
  }}
  #sidebar h1 {{
    font-size: 20px; font-weight: 800; margin-bottom: 4px;
    background: linear-gradient(135deg, #ff6b6b, #feca57, #48dbfb, #a29bfe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  #sidebar .subtitle {{ font-size: 12px; color: #8b949e; margin-bottom: 16px; }}
  #sidebar h2 {{ font-size: 14px; color: #e6edf3; margin: 16px 0 8px; border-bottom: 1px solid #30363d; padding-bottom: 4px; }}
  #plot {{ flex: 1; cursor: grab; }}
  #plot:active {{ cursor: grabbing; }}
  .stat-row {{ display: flex; justify-content: space-between; font-size: 12px; padding: 3px 0; }}
  .stat-row .val {{ color: #58a6ff; font-weight: 600; }}
  .category-list {{ font-size: 11px; }}
  .category-list .cat-item {{
    display: flex; align-items: center; gap: 6px; padding: 3px 0;
  }}
  .cat-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  #selected-info {{
    margin-top: 12px; padding: 10px; background: #1c2128;
    border-radius: 8px; font-size: 11px; line-height: 1.6;
    border: 1px solid #30363d; min-height: 60px;
  }}
  #selected-info .sel-name {{ font-size: 18px; font-weight: 700; }}
  #selected-info .sel-cat  {{ color: #8b949e; }}
  .legend-row {{ display: flex; align-items: center; gap: 6px; font-size: 11px; margin: 2px 0; }}
  .legend-swatch {{ width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }}
  .axis-legend {{ margin-top: 12px; font-size: 10px; color: #8b949e; }}
  .btn-group {{ display: flex; gap: 6px; margin-top: 10px; flex-wrap: wrap; }}
  .btn-group button {{
    background: #21262d; border: 1px solid #30363d; color: #c9d1d9;
    padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 11px;
  }}
  .btn-group button:hover {{ background: #30363d; }}
  .btn-group button.active {{ background: #1f6feb; border-color: #1f6feb; color: #fff; }}
</style>
</head>
<body>

<div id="sidebar">
  <h1>态度空间模型</h1>
  <div class="subtitle">Attitude Space Model<br>认知 × 情绪 × 行为 = 3³ = 27种态度</div>

  <h2>📊 统计概览</h2>
  <div class="stat-row"><span>正面倾向 (Σ&gt;0)</span><span class="val">{pos_count} 种</span></div>
  <div class="stat-row"><span>中性 (Σ=0)</span><span class="val">{neu_count} 种</span></div>
  <div class="stat-row"><span>负面倾向 (Σ&lt;0)</span><span class="val">{neg_count} 种</span></div>

  <h2>🏷️ 按分类</h2>
  <div class="category-list">
'''

for cat, color in CATEGORY_COLORS.items():
    count = len(stats_by_cat[cat])
    names = '、'.join(ATTITUDE_NAMES[p] for p in stats_by_cat[cat])
    html += f'''    <div class="cat-item">
      <span class="cat-dot" style="background:{color}"></span>
      <span>{cat}</span><span style="color:#58a6ff;margin-left:auto">{count}种</span>
    </div>
    <div style="font-size:10px;color:#8b949e;margin-left:16px;margin-bottom:4px">{names}</div>
'''

html += '''
  </div>

  <h2>🔍 强度筛选</h2>
  <div class="btn-group" id="strength-btns">
    <button class="active" data-strength="all">全部</button>
    <button data-strength="0">I=0 (中性)</button>
    <button data-strength="1">I=1 (单维)</button>
    <button data-strength="2">I=2 (双维)</button>
    <button data-strength="3">I=3 (三维)</button>
  </div>

  <div id="selected-info">
    <span style="color:#8b949e">🖱️ 点击图中的点查看详情</span>
  </div>

  <div class="axis-legend">
    <b>轴颜色编码：</b> R=认知轴 · G=情绪轴 · B=行为轴<br>
    <b>距离公式：</b> d = √[(C₁−C₂)²+(E₁−E₂)²+(B₁−B₂)²]<br>
    <b>强度 I</b>=C²+E²+B² &nbsp;
    <b>冲突度 K</b>=max−min &nbsp;
    <b>稳定度 S</b>=3−K
  </div>
</div>

<div id="plot"></div>

<script>
const scatterData = ''' + json.dumps(scatter_data, ensure_ascii=False) + ''';
const edges = ''' + json.dumps(edges, ensure_ascii=False) + ''';

// 构建 traces
const traces = [];

// 晶格连线
const ex = [], ey = [], ez = [];
edges.forEach(e => { ex.push(e.x1, e.x2, null); ey.push(e.y1, e.y2, null); ez.push(e.z1, e.z2, null); });
traces.push({
  type: 'scatter3d', mode: 'lines', x: ex, y: ey, z: ez,
  line: { color: 'rgba(255,255,255,0.12)', width: 1 },
  hoverinfo: 'skip', showlegend: false, name: 'lattice'
});

// 态度点 - 每个强度一组
[0, 1, 2, 3].forEach(strength => {
  const pts = scatterData.filter(d => d.strength === strength);
  if (!pts.length) return;
  const sizes = {0: 6, 1: 8, 2: 10, 3: 13};
  traces.push({
    type: 'scatter3d', mode: 'markers+text',
    x: pts.map(p => p.x), y: pts.map(p => p.y), z: pts.map(p => p.z),
    text: pts.map(p => p.name),
    textposition: 'top center',
    textfont: { size: strength >= 2 ? 10 : 8, color: '#e6edf3', family: 'Noto Sans SC, Microsoft YaHei, sans-serif' },
    marker: {
      color: pts.map(p => p.color),
      size: sizes[strength],
      symbol: 'circle',
      line: { color: 'rgba(255,255,255,0.3)', width: 0.8 }
    },
    hovertemplate: (
      '<b>%{text}</b><br>'
      + '认知: %{customdata[0]} | 情绪: %{customdata[1]} | 行为: %{customdata[2]}<br>'
      + '总和倾向: %{customdata[3]}<br>'
      + '分类: %{customdata[4]}<br>'
      + '强度 I=%{customdata[5]} · 冲突度 K=%{customdata[6]} · 稳定度 S=%{customdata[7]}'
      + '<extra></extra>'
    ),
    customdata: pts.map(p => [
      p.label_c, p.label_e, p.label_b,
      (p.sum > 0 ? '+' : '') + p.sum,
      p.category, p.strength, p.conflict, p.stability
    ]),
    showlegend: false,
    name: 'strength-' + strength,
  });
});

// 分类图例
const catColors = ''' + json.dumps(CATEGORY_COLORS) + ''';
const catEntries = Object.entries(catColors);
catEntries.forEach(([cat, color]) => {
  traces.push({
    type: 'scatter3d', mode: 'markers',
    x: [null], y: [null], z: [null],
    marker: { color: color, size: 10, symbol: 'circle', line: { width: 1, color: '#fff' } },
    name: cat,
  });
});

// Plotly 配置
const layout = {
  scene: {
    xaxis: {
      title: { text: '认知 Cognition', font: { color: '#ff6b6b', size: 13 } },
      tickvals: [-1, 0, 1],
      ticktext: ['消极 (−1)', '中性 (0)', '积极 (+1)'],
      gridcolor: 'rgba(255,107,107,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)',
      color: '#aaa',
      range: [-1.5, 1.5]
    },
    yaxis: {
      title: { text: '情绪 Emotion', font: { color: '#feca57', size: 13 } },
      tickvals: [-1, 0, 1],
      ticktext: ['消极 (−1)', '中性 (0)', '积极 (+1)'],
      gridcolor: 'rgba(254,202,87,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)',
      color: '#aaa',
      range: [-1.5, 1.5]
    },
    zaxis: {
      title: { text: '行为 Behavior', font: { color: '#48dbfb', size: 13 } },
      tickvals: [-1, 0, 1],
      ticktext: ['消极 (−1)', '中性 (0)', '积极 (+1)'],
      gridcolor: 'rgba(72,219,251,0.1)',
      zerolinecolor: 'rgba(255,255,255,0.2)',
      color: '#aaa',
      range: [-1.5, 1.5]
    },
    aspectmode: 'cube',
    camera: { eye: { x: 1.5, y: 1.5, z: 1.5 }, center: { x: 0, y: 0, z: 0 } },
    bgcolor: 'rgba(0,0,0,0)',
  },
  paper_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 0, r: 0, t: 0, b: 0 },
  legend: {
    x: 0.01, y: 0.99,
    font: { color: '#c9d1d9', size: 11 },
    bgcolor: 'rgba(22,27,34,0.85)',
    bordercolor: '#30363d',
    borderwidth: 1,
  },
  hovermode: 'closest',
};

const config = {
  responsive: true,
  displayModeBar: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
  displaylogo: false,
  toImageButtonOptions: { format: 'png', filename: 'attitude_space' },
};

Plotly.newPlot('plot', traces, layout, config).then(() => {
  const plotEl = document.getElementById('plot');

  // 点击点事件
  plotEl.on('plotly_click', data => {
    if (!data.points.length) return;
    const pt = data.points[0];
    const cd = pt.customdata;
    if (!cd) return;
    document.getElementById('selected-info').innerHTML = `
      <div class="sel-name">${pt.text || '—'}</div>
      <div class="sel-cat">${cd[4]}</div>
      <div>认知: ${cd[0]} · 情绪: ${cd[1]} · 行为: ${cd[2]}</div>
      <div>总和倾向: ${cd[3]} &nbsp;|&nbsp; 强度 I=${cd[5]} &nbsp; 冲突度 K=${cd[6]} &nbsp; 稳定度 S=${cd[7]}</div>
    `;
  });

  // 强度筛选按钮
  document.querySelectorAll('#strength-btns button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#strength-btns button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const strength = btn.dataset.strength;
      const update = {};
      for (let i = 1; i <= 4; i++) {
        const traceIdx = i;  // traces[1..4] = strength 0..3
        update[traceIdx] = { visible: strength === 'all' || (traceIdx - 1) == parseInt(strength) };
      }
      Plotly.restyle('plot', update);
    });
  });

  // 响应式
  window.addEventListener('resize', () => Plotly.Plots.resize(plotEl));
});
</script>

</body>
</html>'''

html_path = '/home/dog/game/attitude_space.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"   ✅ HTML 已保存: {html_path}")


# ============================================================
# 3. 终端文本摘要
# ============================================================
print(f"\n{'='*72}")
print(f"  态度空间模型 — 完整列表")
print(f"  C认知 × E情绪 × B行为 = 27种态度")
print(f"{'='*72}")
print(f"\n{'坐标(C,E,B)':<16} {'成语名称':<12} {'分类':<10} {'和':>4} {'强度I':>5} {'冲突K':>5} {'稳定S':>5}")
print("-" * 72)
for c, e, b in sorted(points, key=lambda p: (-sum(p), -get_strength(*p), p[0], p[1], p[2])):
    name = ATTITUDE_NAMES[(c, e, b)]
    cat  = get_category(c, e, b)
    s    = c + e + b
    I    = get_strength(c, e, b)
    K    = get_conflict(c, e, b)
    S    = get_stability(c, e, b)
    coord_str = f"({val_char[c]},{val_char[e]},{val_char[b]})"
    print(f"  {coord_str:<16} {name:<12} {cat:<10} {s:>+4} {I:>5} {K:>5} {S:>5}")

print(f"\n✅ 全部完成: {png_path} + {html_path}")
