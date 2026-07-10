#!/usr/bin/env python3
"""生成冲突战模拟器 HTML v2 — 从 data/*.json 卡池生成独立 HTML 文件.

用法: python3 tools/gen_battle_html.py > 冲突战模拟器_v2.html
      然后直接在浏览器中打开该文件.
"""

import json, sys
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def load(name):
    with open(DATA / name, encoding='utf-8') as f:
        return json.load(f)

def build_cards():
    """从 JSON 构建 HTML 所需的简化卡牌数据."""
    cards = []

    # ── 情绪卡 (15) ──
    emo_cards = load('emotion_cards.json')
    for c in emo_cards['cards']:
        po = c['play_effect']['pad_offset']
        cards.append({
            'id': 'e_' + c['id'],
            'n': c['name'],
            'cat': '情绪',
            'sub': c.get('valence_group', '?'),
            'pad': [round(po['dV'], 3), round(po['dA'], 3), round(po['dD'], 3)],
            'ap': 0,
            'desc': c['play_effect']['description'][:30],
            'link': ', '.join(c.get('linkages', {}).get('activates_drives', [])),
        })

    # ── 认知卡 (25) ──
    cog_cards = load('cognition_cards.json')
    for c in cog_cards['cards']:
        cq = c['cognitive_quality']
        # C⁵ → PAD 映射: d'→V(清晰即微悦), criterion→D(保守=低控), α→A(深度=唤醒)
        V = round(cq['d_prime'] * 0.6, 3)
        A = round(cq['depth_alpha'] * 0.8, 3)
        D = round(-cq['criterion'] * 0.5 + 0.25, 3)
        cards.append({
            'id': 'c_' + c['id'],
            'n': c['name'],
            'cat': '认知',
            'sub': c['module'],
            'pad': [V, A, D],
            'ap': 0,
            'desc': c['effect_description'][:30],
            'link': c.get('tendency', ''),
        })

    # ── 行为卡 (21) ──
    beh_cards = load('behavior_cards.json')
    drives = load('drives.json')
    dp_lookup = {d['id']: d['drive_pole'] for d in drives['drives']}

    for c in beh_cards['cards']:
        did = c.get('drive_id', '')
        pole = dp_lookup.get(did, {'valence': 0, 'intensity': 0, 'autonomy': 0})
        # drive_pole → PAD: valence→V, intensity→A, autonomy→D
        V = round(pole['valence'] * 0.7 + c.get('valence', 0) * 0.3, 3)
        A = round(pole['intensity'] * 0.7, 3)
        D = round(pole['autonomy'] * 0.7, 3)
        cards.append({
            'id': 'b_' + c['id'],
            'n': c['name'],
            'cat': '行为',
            'sub': c.get('drive', '?'),
            'pad': [V, A, D],
            'ap': c.get('base_ap', 1),
            'desc': c.get('effect_description', '')[:30],
            'link': c.get('drive_id', ''),
        })

    return cards


# ═══════════════════════════════════════════════
# HTML TEMPLATE
# ═══════════════════════════════════════════════

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>冲突战模拟器 v2 — 61张卡池</title>
<style>
:root{--bg:#0f1117;--s:#1a1d27;--s2:#22263a;--b:#2a2d38;--t:#e1e4ed;--t2:#b0b5c6;--m:#6b7094;--cog:#4fc3f7;--emo:#ef5350;--beh:#66bb6a;--san:#7e57c2;--hp:#ef5350;--pl:#42a5f5;--en:#ff7043;--wp:#ffd54f}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--t);font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',-apple-system,sans-serif;min-height:100vh;padding:8px;display:flex;flex-direction:column;gap:6px}
header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;padding:8px 14px;background:var(--s);border-radius:8px;border:1px solid var(--b)}
h1{font-size:0.95rem}.btn{padding:5px 12px;border-radius:5px;border:1px solid var(--b);background:var(--s2);color:var(--t);cursor:pointer;font-size:0.72rem;font-family:inherit}.btn:hover{background:#2e3350}.btn.primary{background:#3d5af1;border-color:#3d5af1;color:#fff}.btn.sm{padding:3px 7px;font-size:0.62rem}.btn.danger{background:#c62828;border-color:#c62828;color:#fff}
main{display:grid;grid-template-columns:1fr 1fr;gap:6px;flex:1}@media(max-width:960px){main{grid-template-columns:1fr}}
.panel{background:var(--s);border-radius:8px;border:1px solid var(--b);padding:8px;display:flex;flex-direction:column;gap:4px}
.panel.pl{border-top:3px solid var(--pl)}.panel.en{border-top:3px solid var(--en)}
h2{font-size:0.78rem}.row{display:flex;align-items:center;gap:6px;font-size:0.64rem;flex-wrap:wrap}
.bar{display:flex;align-items:center;gap:4px}.bar .lb{width:26px;font-weight:600;font-size:0.62rem}
.bar .bw{flex:1;height:9px;background:#11131c;border-radius:4px;overflow:hidden}
.bar .bf{height:100%;border-radius:4px;transition:width 0.4s}.bf.san{background:linear-gradient(90deg,#5c3d99,#7e57c2)}.bf.hp{background:linear-gradient(90deg,#c62828,#ef5350)}
.bar .val{width:50px;text-align:right;font-family:monospace;font-size:0.6rem}
.stat{font-size:0.6rem;font-family:monospace;color:var(--t2)}
.pad{display:flex;gap:3px;justify-content:center;font-size:0.62rem;font-family:monospace;padding:3px 6px;background:#11131c;border-radius:4px}
.pad .pi{flex:1;text-align:center;padding:2px 3px;border-radius:3px}.pad .pl{color:var(--m);font-size:0.54rem}.pad .pv{font-weight:700;font-size:0.7rem}
.slots{display:flex;gap:4px}
.slot{flex:1;min-width:85px;min-height:78px;background:var(--s2);border:2px dashed var(--b);border-radius:6px;padding:5px;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;transition:all 0.1s}
.slot:hover{border-color:var(--m)}.slot.set{border-style:solid}.slot.sc{border-color:rgba(79,195,247,0.3)}.slot.se{border-color:rgba(239,83,80,0.3)}.slot.sb{border-color:rgba(102,187,138,0.3)}
.slot.set.sc{background:rgba(79,195,247,0.06);border-color:var(--cog)}.slot.set.se{background:rgba(239,83,80,0.06);border-color:var(--emo)}.slot.set.sb{background:rgba(102,187,138,0.06);border-color:var(--beh)}
.slot .lb{font-size:0.56rem;color:var(--m)}.slot .mt{font-size:0.54rem;color:var(--m)}
.slot .cn{font-size:0.68rem;font-weight:600;text-align:center}.slot .cv{font-size:0.5rem;color:var(--t2);font-family:monospace}
.slot .apc{font-size:0.52rem;color:var(--wp)}
.bottom{background:var(--s);border-radius:8px;border:1px solid var(--b);padding:8px}
.tabs{display:flex;gap:2px;margin-bottom:5px}.tab{padding:3px 10px;border-radius:4px 4px 0 0;background:var(--s2);color:var(--m);cursor:pointer;font-size:0.64rem}.tab.on{background:var(--s);color:var(--t);border:1px solid var(--b);border-bottom:none}
.tc{display:none}.tc.on{display:block}
.grid{display:flex;flex-wrap:wrap;gap:4px;max-height:240px;overflow-y:auto}
.card{width:108px;padding:5px 7px;background:var(--s2);border:1px solid var(--b);border-radius:4px;cursor:pointer;font-size:0.62rem;transition:all 0.1s;display:flex;flex-direction:column;gap:1px}
.card:hover{border-color:var(--m)}.card.sel{border-color:var(--wp);box-shadow:0 0 6px rgba(255,213,79,0.25)}
.card .cn{font-weight:600}.card .ct{font-size:0.52rem;color:var(--m)}.card .cv{font-size:0.5rem;font-family:monospace;color:var(--t2)}.card .cd{font-size:0.48rem;color:var(--m);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card.cog{border-left:2px solid var(--cog)}.card.emo{border-left:2px solid var(--emo)}.card.beh{border-left:2px solid var(--beh)}
.log{max-height:150px;overflow-y:auto;font-size:0.6rem;font-family:monospace}
.log .l{padding:1px 4px;border-radius:2px}.log .lr{color:var(--wp);font-weight:600}.log .lp{background:rgba(66,165,245,0.05)}.log .le{background:rgba(255,112,67,0.05)}.log .lw{color:#66bb6a}.log .ll{color:var(--hp)}.log .li{color:var(--m);font-style:italic}
.filter{display:flex;gap:4px;align-items:center;flex-wrap:wrap;margin-bottom:4px;font-size:0.6rem}
.filter select,.filter input{padding:2px 6px;border-radius:3px;border:1px solid var(--b);background:var(--s2);color:var(--t);font-size:0.6rem;font-family:inherit}
@keyframes fw{50%{box-shadow:0 0 14px rgba(102,187,138,0.35)}}@keyframes fl{50%{box-shadow:0 0 14px rgba(239,83,80,0.35)}}.rw{animation:fw 0.5s}.rl{animation:fl 0.5s}
.combo-badge{font-size:0.54rem;padding:1px 5px;border-radius:3px;font-weight:600}
.combo-badge.cfull{background:rgba(255,213,79,0.15);color:var(--wp)}
.combo-badge.cnone{color:var(--m)}
</style>
</head>
<body>

<header>
  <div><h1>⚔️ 冲突战模拟器 v2</h1><div style="font-size:0.56rem;color:var(--m)">61张卡池 &nbsp;|&nbsp; D轴碰撞 &nbsp;|&nbsp; 空格=结算 &nbsp; 1-6=选槽 &nbsp; ESC=取消选中</div></div>
  <div style="display:flex;gap:4px;flex-wrap:wrap">
    <button class="btn primary" onclick="round()">⚡ 结算回合</button>
    <button class="btn" onclick="autoN(5)">×5</button>
    <button class="btn" onclick="autoN(10)">×10</button>
    <button class="btn" onclick="reset()">↺ 重置</button>
    <button class="btn sm" onclick="rnd()">🎲 随机配牌</button>
    <button class="btn sm" onclick="rndEmo()">🎭 随机情绪</button>
  </div>
</header>

<main>
  <div class="panel pl" id="pp">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>🧑 角色</h2>
      <span class="stat">AP:<span id="pap">6</span> &nbsp;WP:<span id="pwp" style="color:var(--wp)">5</span></span>
    </div>
    <div class="bar"><span class="lb" style="color:var(--san)">SAN</span><div class="bw"><div class="bf san" id="psb" style="width:100%"></div></div><span class="val" id="psv">100</span></div>
    <div class="bar"><span class="lb" style="color:var(--hp)">HP</span><div class="bw"><div class="bf hp" id="phb" style="width:100%"></div></div><span class="val" id="phv">100</span></div>
    <div class="pad" id="ppd"></div>
    <div class="slots" id="ps"></div>
    <div id="pcombo" style="text-align:center;min-height:14px"></div>
  </div>
  <div class="panel en" id="ep">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>👤 敌方</h2>
      <span class="stat">AP:<span id="eap">6</span> &nbsp;WP:<span id="ewp" style="color:var(--wp)">5</span></span>
    </div>
    <div class="bar"><span class="lb" style="color:var(--san)">SAN</span><div class="bw"><div class="bf san" id="esb" style="width:100%"></div></div><span class="val" id="esv">100</span></div>
    <div class="bar"><span class="lb" style="color:var(--hp)">HP</span><div class="bw"><div class="bf hp" id="ehb" style="width:100%"></div></div><span class="val" id="ehv">100</span></div>
    <div class="pad" id="epd"></div>
    <div class="slots" id="es"></div>
    <div id="ecombo" style="text-align:center;min-height:14px"></div>
  </div>
</main>

<div class="bottom">
  <div class="tabs">
    <div class="tab on" onclick="st('lib')">📚 卡牌库 (61张)</div>
    <div class="tab" onclick="st('log')">📜 战斗日志</div>
  </div>
  <div class="tc on" id="t-lib">
    <div class="filter">
      <select id="fcat" onchange="rc()"><option value="">全部类型</option><option>认知</option><option>情绪</option><option>行为</option></select>
      <select id="fsub" onchange="rc()"><option value="">全部子类</option></select>
      <input id="fq" placeholder="搜索卡名..." oninput="rc()" style="width:100px">
      <span style="color:var(--m)">点击选中 → 按 1-6 放入卡槽</span>
    </div>
    <div class="grid" id="cg"></div>
  </div>
  <div class="tc" id="t-log"><div class="log" id="bl"></div></div>
</div>

<script>
// ═══════════════════════════════════════════════════════
// CARD DATA (generated from JSON)
// ═══════════════════════════════════════════════════════
const CARDS = __CARDS_PLACEHOLDER__;

// ═══════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════
let S = {
  p: {san:100,ms:100,hp:100,mh:100,pad:[0,0,0],sl:[null,null,null],ap:6,wp:5},
  e: {san:100,ms:100,hp:100,mh:100,pad:[0,0,0],sl:[null,null,null],ap:6,wp:5},
  r: 0, sel: null, log: []
};

// ═══════════════════════════════════════════════════════
// RENDER
// ═══════════════════════════════════════════════════════
function rc(){
  let cat = document.getElementById('fcat').value;
  let sub = document.getElementById('fsub').value;
  let q = document.getElementById('fq').value.toLowerCase();
  let subs = new Set();
  CARDS.forEach(c => { if(c.sub) subs.add(c.sub); });

  // update sub filter
  let sel = document.getElementById('fsub');
  let csv = sel.value;
  sel.innerHTML = '<option value="">全部子类</option>' + [...subs].sort().map(s => `<option${s===csv?' selected':''}>${s}</option>`).join('');

  let filtered = CARDS.filter(c => {
    if(cat && c.cat !== cat) return false;
    if(sub && c.sub !== sub) return false;
    if(q && !c.n.toLowerCase().includes(q) && !c.sub.toLowerCase().includes(q)) return false;
    return true;
  });

  document.getElementById('cg').innerHTML = filtered.map(c => {
    let s = S.sel && S.sel.id === c.id ? 'sel' : '';
    let cls = c.cat === '认知' ? 'cog' : c.cat === '情绪' ? 'emo' : 'beh';
    let apStr = c.ap > 0 ? ` AP:${c.ap}` : '';
    return `<div class="card ${cls} ${s}" onclick="sel('${c.id}')" title="${c.desc||''}${apStr} | ${c.link||''}">
      <div class="cn">${c.n}</div><div class="ct">${c.cat}·${c.sub}</div>
      <div class="cv">V${c.pad[0].toFixed(1)} A${c.pad[1].toFixed(1)} D${c.pad[2].toFixed(1)}${apStr}</div>
      <div class="cd">${c.desc||''}</div>
    </div>`;
  }).join('');
}

function renderAll(){
  ['p','e'].forEach(s => { rs(s); rpd(s); rb(s); });
  rc();
}

function rs(s){
  let c = S[s], co = document.getElementById(s==='p'?'ps':'es');
  let cats = ['认知','情绪','行为'], cls = ['sc','se','sb'];
  co.innerHTML = cats.map((t,i) => {
    let x = c.sl[i];
    if(x) {
      let apStr = x.ap > 0 ? `<div class="apc">AP:${x.ap}</div>` : '';
      return `<div class="slot set ${cls[i]}" onclick="clr('${s}',${i})" title="点击清空">
        <div class="cn">${x.n}</div>
        <div class="cv">V${x.pad[0].toFixed(1)} A${x.pad[1].toFixed(1)} D${x.pad[2].toFixed(1)}</div>
        ${apStr}
      </div>`;
    }
    return `<div class="slot ${cls[i]}" onclick="asn('${s}',${i})"><span class="lb">${t}</span><span class="mt">点击选牌</span></div>`;
  }).join('');

  // Update AP / WP display
  document.getElementById(s==='p'?'pap':'eap').textContent = c.ap;
  document.getElementById(s==='p'?'pwp':'ewp').textContent = c.wp;

  // Combo badge
  updateCombo(s);
}

function updateCombo(s){
  let c = S[s];
  let hasCog = c.sl[0] !== null, hasEmo = c.sl[1] !== null, hasBeh = c.sl[2] !== null;
  let comboEl = document.getElementById(s==='p'?'pcombo':'ecombo');
  if(hasCog && hasEmo && hasBeh) comboEl.innerHTML = '<span class="combo-badge cfull">完整态度</span>';
  else if(hasCog && hasEmo) comboEl.innerHTML = '<span class="combo-badge" style="color:var(--cog)">酝酿</span>';
  else if(hasEmo && hasBeh) comboEl.innerHTML = '<span class="combo-badge" style="color:var(--emo)">冲动</span>';
  else if(hasCog && hasBeh) comboEl.innerHTML = '<span class="combo-badge" style="color:var(--beh)">执行</span>';
  else comboEl.innerHTML = '<span class="combo-badge cnone">-</span>';
}

function rpd(s){
  let c = S[s], el = document.getElementById(s==='p'?'ppd':'epd'), p = c.pad;
  el.innerHTML = 'VAD'.split('').map((l,i) => {
    let color = i===0 ? (p[0]>0.1?'#66bb6a':p[0]<-0.1?'#ef5350':'#b0b5c6')
             : i===2 ? (p[2]>0.1?'#66bb6a':p[2]<-0.1?'#ef5350':'#b0b5c6')
             : '#ffd54f';
    return `<div class="pi"><div class="pl">${l}</div><div class="pv" style="color:${color}">${p[i].toFixed(2)}</div></div>`;
  }).join('');
}

function rb(s){
  let c = S[s], pre = s==='p'?'p':'e';
  document.getElementById(pre+'sb').style.width = (c.san/c.ms*100)+'%';
  document.getElementById(pre+'sv').textContent = Math.round(c.san);
  document.getElementById(pre+'hb').style.width = (c.hp/c.mh*100)+'%';
  document.getElementById(pre+'hv').textContent = Math.round(c.hp);
}

// ═══════════════════════════════════════════════════════
// ACTIONS
// ═══════════════════════════════════════════════════════
function sel(id){ S.sel = CARDS.find(c => c.id === id); rc(); }
function asn(s, i){
  if(!S.sel) return log('⚠ 请先在卡牌库中点击选中一张卡牌', 'i');
  let cats = ['认知','情绪','行为'];
  if(S.sel.cat !== cats[i]) return log('⚠ 类别不匹配: 槽位需要【'+cats[i]+'】, 你选的是【'+S.sel.cat+'】', 'i');
  // Check AP for behavior cards
  if(S.sel.cat === '行为' && S.sel.ap > S[s].ap) return log('⚠ AP不足: 需要 '+S.sel.ap+' 当前仅有 '+S[s].ap, 'i');
  S[s].sl[i] = {...S.sel};
  S.sel = null;
  renderAll();
}
function clr(s,i){ S[s].sl[i] = null; renderAll(); }

// ═══════════════════════════════════════════════════════
// BATTLE ENGINE
// ═══════════════════════════════════════════════════════
function att(sl){
  let ps = sl.filter(x => x).map(x => x.pad);
  if(ps.length === 0) return [0,0,0];
  return [ps.reduce((s,v) => s+v[0], 0)/ps.length, ps.reduce((s,v) => s+v[1], 0)/ps.length, ps.reduce((s,v) => s+v[2], 0)/ps.length];
}
function mg(v){ return Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]); }

function detectCombo(sl){
  let hasCog = sl[0] !== null, hasEmo = sl[1] !== null, hasBeh = sl[2] !== null;
  if(hasCog && hasEmo && hasBeh) return {type:'完整态度', emoM:1.0, behM:1.0};
  if(hasCog && hasEmo) return {type:'酝酿', emoM:1.0, behM:1.0};
  if(hasEmo && hasBeh) return {type:'冲动', emoM:1.5, behM:1.2};
  if(hasCog && hasBeh) return {type:'执行', emoM:1.0, behM:1.0, wpB:1};
  return {type:null, emoM:1.0, behM:1.0};
}

function round(){
  S.r++;
  log('━━━ 第 '+S.r+' 回合 ━━━', 'lr');

  let results = [];
  ['p','e'].forEach(s => {
    let c = S[s];
    // Apply emotion card PAD offset
    if(c.sl[1]) {
      let emo = c.sl[1];
      let combo = detectCombo(c.sl);
      c.pad = [
        Math.max(-1, Math.min(1, c.pad[0] + emo.pad[0] * combo.emoM)),
        Math.max(-1, Math.min(1, c.pad[1] + emo.pad[1] * combo.emoM)),
        Math.max(-1, Math.min(1, c.pad[2] + emo.pad[2] * combo.emoM))
      ];
    }
    // Deduct AP for behavior card
    if(c.sl[2]) {
      let apCost = c.sl[2].ap || 0;
      c.ap = Math.max(0, c.ap - apCost);
    }
    // Willpower bonus for 执行
    let combo = detectCombo(c.sl);
    if(combo.wpB) c.wp = Math.min(5, c.wp + combo.wpB);

    results.push({s, pad:c.pad, combo, name:s==='p'?'角色':'敌方'});
  });

  let pa = S.p.pad, ea = S.e.pad;
  log('角色 PAD: V'+pa[0].toFixed(2)+' A'+pa[1].toFixed(2)+' D'+pa[2].toFixed(2) + ' '+detectCombo(S.p.sl).type, 'lp');
  log('敌方 PAD: V'+ea[0].toFixed(2)+' A'+ea[1].toFixed(2)+' D'+ea[2].toFixed(2) + ' '+detectCombo(S.e.sl).type, 'le');

  // ── D-axis collision (v4 formula) ──
  let dd = pa[2] - ea[2], pm = mg(pa), em = mg(ea);
  const SCALE = 5.0;
  let w = null, sd = 0;

  if(Math.abs(dd) > 0.2){
    w = dd > 0 ? 'p' : 'e';
    sd = Math.round((w==='p'?pm:em) * (1 + Math.abs(dd)) * SCALE);
    let wname = w==='p'?'角色':'敌方';
    let lname = w==='p'?'敌方':'角色';
    log(wname+' 主导碰撞 ΔD='+dd.toFixed(2)+' → '+lname+' SAN-'+sd, w==='p'?'lw':'ll');
  } else {
    sd = Math.round((pm+em)/4 * SCALE);
    log('势均力敌 → 双方各 SAN-'+sd, 'li');
  }

  if(w === 'p'){ S.e.san = Math.max(0, S.e.san - sd); fl('e','l'); fl('p','w'); }
  else if(w === 'e'){ S.p.san = Math.max(0, S.p.san - sd); fl('p','l'); fl('e','w'); }
  else { S.p.san = Math.max(0, S.p.san - sd); S.e.san = Math.max(0, S.e.san - sd); }

  // SAN overflow to HP
  ['p','e'].forEach(s => {
    let c = S[s];
    if(c.san <= 0){ c.hp = Math.max(0, c.hp - Math.abs(c.san)); c.san = 0; }
    if(c.san < 30 && c.hp > 0){ let b = Math.round((30-c.san)*0.15); c.hp = Math.max(0, c.hp-b); }
    // Reset AP, clear slots
    c.ap = 6;
    c.sl = [null, null, null];
    // PAD decay
    c.pad = [c.pad[0]*0.85, c.pad[1]*0.85, c.pad[2]*0.85];
  });

  if(S.p.hp <= 0) log('💀 角色崩溃 —— 敌方胜利', 'll');
  if(S.e.hp <= 0) log('🏆 敌方崩溃 —— 角色胜利', 'lw');

  renderAll();
}

function fl(s,r){
  let e = document.getElementById(s==='p'?'pp':'ep');
  e.classList.remove('rw','rl'); void e.offsetWidth;
  e.classList.add(r==='w'?'rw':'rl');
  setTimeout(() => e.classList.remove('rw','rl'), 500);
}

// ═══════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════
function log(m,c){
  S.log.push({m,c});
  let el = document.getElementById('bl');
  el.innerHTML += `<div class="l ${c||''}">[${S.r}] ${m}</div>`;
  el.scrollTop = el.scrollHeight;
}

function reset(){
  S = {
    p: {san:100,ms:100,hp:100,mh:100,pad:[0,0,0],sl:[null,null,null],ap:6,wp:5},
    e: {san:100,ms:100,hp:100,mh:100,pad:[0,0,0],sl:[null,null,null],ap:6,wp:5},
    r: 0, sel: null, log: []
  };
  document.getElementById('bl').innerHTML = '';
  renderAll();
  log('🔄 已重置', 'i');
}

function rnd(){
  ['p','e'].forEach(s => {
    S[s].sl = ['认知','情绪','行为'].map(cat => {
      let pool = CARDS.filter(x => x.cat === cat);
      return pool.length ? {...pool[Math.floor(Math.random()*pool.length)]} : null;
    });
  });
  log('🎲 随机配牌', 'i');
  renderAll();
}

function rndEmo(){
  ['p','e'].forEach(s => {
    let pool = CARDS.filter(x => x.cat === '情绪');
    S[s].sl[1] = pool.length ? {...pool[Math.floor(Math.random()*pool.length)]} : null;
    S[s].sl[0] = null; S[s].sl[2] = null;
  });
  log('🎭 随机情绪开局', 'i');
  renderAll();
}

function autoN(n){
  for(let i=0; i<n; i++){
    // Auto-fill empty slots
    ['p','e'].forEach(s => {
      S[s].sl = S[s].sl.map((x,j) => {
        if(x) return x;
        let pool = CARDS.filter(c => c.cat === ['认知','情绪','行为'][j]);
        if(j === 2) pool = pool.filter(c => (c.ap||0) <= S[s].ap); // only affordable behavior cards
        return pool.length ? {...pool[Math.floor(Math.random()*pool.length)]} : null;
      });
    });
    round();
    if(S.p.hp <= 0 || S.e.hp <= 0) break;
  }
  renderAll();
}

// Tabs
function st(n){
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
  document.querySelectorAll('.tc').forEach(t => t.classList.remove('on'));
  document.querySelector(`.tab[onclick="st('${n}')"]`).classList.add('on');
  document.getElementById('t-'+n).classList.add('on');
}

// Keyboard
document.addEventListener('keydown', e => {
  if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
  if(e.key === ' ' || e.key === 'Enter'){ e.preventDefault(); round(); }
  if(e.key === '1') asn('p', 0);
  if(e.key === '2') asn('p', 1);
  if(e.key === '3') asn('p', 2);
  if(e.key === '4') asn('e', 0);
  if(e.key === '5') asn('e', 1);
  if(e.key === '6') asn('e', 2);
  if(e.key === 'Escape'){ S.sel = null; rc(); }
});

reset();
</script>
</body>
</html>'''


if __name__ == '__main__':
    cards = build_cards()
    cards_json = json.dumps(cards, ensure_ascii=False, indent=2)
    html = HTML.replace('__CARDS_PLACEHOLDER__', cards_json)
    print(html)
