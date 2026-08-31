"""Offline HTML viewer for JuniorRegionSphere — 2D panorama strip + AR heading overlay."""
from __future__ import annotations

import json
from html import escape


def render_viewer(data: dict) -> str:
    payload = json.dumps(data, default=str)
    name = escape(data.get("name") or "sphere")
    arena = escape((data.get("arena") or {}).get("name") or "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no"/>
<title>JuniorRegionSphere — {name}</title>
<style>
:root {{ color-scheme: dark; }}
body {{ margin:0; font-family: ui-sans-serif, system-ui; background:#0b0f14; color:#e8eef6; }}
header {{ padding:12px 16px; display:flex; gap:12px; align-items:center; background:#121820; }}
h1 {{ font-size:16px; margin:0; }}
button {{ background:#1d2a38; color:#e8eef6; border:1px solid #31465c; border-radius:8px; padding:8px 12px; }}
#stage {{ position:relative; height:58vh; overflow:hidden; background:#07090c; }}
#pano {{
  position:absolute; inset:0;
  background: radial-gradient(circle at 50% 55%, #1a2734 0%, #0b0f14 70%);
}}
.hotspot {{
  position:absolute; transform:translate(-50%,-50%);
  min-width:28px; height:28px; border-radius:999px;
  background:#3dd68c; color:#062013; font-size:11px; font-weight:700;
  display:flex; align-items:center; justify-content:center; padding:0 8px;
  cursor:pointer; box-shadow:0 0 0 4px rgba(61,214,140,.25);
}}
.hotspot.locked {{ background:#ffd166; box-shadow:0 0 0 6px rgba(255,209,102,.35); }}
#hud {{ padding:12px 16px; display:grid; gap:8px; }}
#meta {{ font-size:13px; opacity:.85; }}
#info {{ background:#121820; border-radius:12px; padding:12px; min-height:88px; }}
#compass {{ font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
<header>
  <h1>JuniorRegionSphere · {name}</h1>
  <span>{arena}</span>
  <button id="mode">2D</button>
  <button id="left">◀</button>
  <button id="right">▶</button>
</header>
<div id="stage"><div id="pano"></div></div>
<div id="hud">
  <div id="compass">heading —</div>
  <div id="meta">Drag or use compass. Select a wall.</div>
  <div id="info">No hotspot locked.</div>
</div>
<script>
const DATA = {payload};
let heading = 0;
let ar = false;
const pano = document.getElementById('pano');
const info = document.getElementById('info');
const compass = document.getElementById('compass');
const modeBtn = document.getElementById('mode');

function wrap(d){{ d = d % 360; return d < 0 ? d + 360 : d; }}
function compass8(d){{
  const dirs = ['N','NE','E','SE','S','SW','W','NW'];
  return dirs[Math.round(d/45)%8];
}}
function place(){{
  pano.innerHTML = '';
  const w = pano.clientWidth || window.innerWidth;
  const h = pano.clientHeight || 300;
  (DATA.hotspots||[]).forEach(hs => {{
    const delta = ((hs.yaw_deg - heading + 540) % 360) - 180;
    if (Math.abs(delta) > 90) return;
    const el = document.createElement('div');
    el.className = 'hotspot';
    el.textContent = hs.name;
    el.style.left = (50 + delta / 90 * 50) + '%';
    el.style.top = (52 - (hs.pitch_deg||0)) + '%';
    el.onclick = () => select(hs);
    pano.appendChild(el);
  }});
  compass.textContent = 'heading ' + heading.toFixed(0) + '° ' + compass8(heading);
}}
function select(hs){{
  document.querySelectorAll('.hotspot').forEach(e => e.classList.remove('locked'));
  const nav = hs.from_arena || {{}};
  info.innerHTML = '<strong>' + hs.name + '</strong><br/>'
    + 'bearing ' + (hs.yaw_deg||0).toFixed(0) + '° '
    + (hs.compass_from_arena||'') + '<br/>'
    + (nav.distance_mi != null ? (nav.distance_mi + ' mi · ' + nav.compass) : '') + '<br/>'
    + (hs.notes || '');
}}
async function pollLook(){{
  try {{
    const r = await fetch('/sphere/' + DATA.id + '/look?heading=' + heading);
    const j = await r.json();
    if (j.locked) {{
      const hs = (DATA.hotspots||[]).find(h => h.id === j.locked.id) || j.locked;
      select(hs);
    }}
  }} catch (e) {{}}
}}
modeBtn.onclick = () => {{
  ar = !ar;
  modeBtn.textContent = ar ? 'AR' : '2D';
  if (ar && window.DeviceOrientationEvent && DeviceOrientationEvent.requestPermission) {{
    DeviceOrientationEvent.requestPermission().catch(()=>{{}});
  }}
}};
document.getElementById('left').onclick = () => {{ heading = wrap(heading - 15); place(); pollLook(); }};
document.getElementById('right').onclick = () => {{ heading = wrap(heading + 15); place(); pollLook(); }};
let drag = null;
pano.addEventListener('pointerdown', e => drag = e.clientX);
window.addEventListener('pointerup', () => drag = null);
window.addEventListener('pointermove', e => {{
  if (drag == null) return;
  heading = wrap(heading - (e.clientX - drag) * 0.35);
  drag = e.clientX; place();
}});
window.addEventListener('deviceorientation', e => {{
  if (!ar) return;
  const a = e.webkitCompassHeading != null ? e.webkitCompassHeading : (e.alpha != null ? (360 - e.alpha) : null);
  if (a == null) return;
  heading = wrap(a); place(); pollLook();
}});
place();
</script>
</body></html>"""
