"""Build a self-contained index.html (page + data + small runtime) so the report works from GitHub Pages
or any static host.  usage: build_standalone.py report_page.html assets.json index.html"""
import sys, json

page, data, out = sys.argv[1:4]
frag = open(page, encoding='utf-8').read().replace('<meta name="dash-one-writer">', '')
rows = json.load(open(data, encoding='utf-8'))
payload = json.dumps(rows, separators=(',', ':')).replace('</', '<\\/')

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>McCoy's Fleet Asset Report</title>
<style>
:root { --color-bg:#f3f6f4; --color-panel:#ffffff; --color-fg:#14231d; --color-fg-muted:#55655d; --color-border-line:#d3dcd7; --color-warn:#9a6b00; --color-ok:#1f7a4d; --color-bad:#b3261e;
  --font-anthropic-sans: system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; --font-anthropic-serif: Georgia,"Times New Roman",serif;
  --cds-font-size-caption:.8rem; --cds-font-size-body:.9rem; --cds-font-size-heading:1.05rem; --cds-font-size-title:1.4rem; --cds-font-weight-medium:500;
  --cds-radius:8px; --cds-gap-sm:.5rem; --cds-gap-md:.85rem; --cds-gap-lg:1.25rem; --cds-pad-lg:1rem; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --color-bg:#0e1714; --color-panel:#15221d; --color-fg:#e8efeb; --color-fg-muted:#9fb1a8; --color-border-line:#2a3a33; --color-warn:#e0b030; color-scheme: dark; } }
html, body { margin: 0; } body { background: var(--color-bg); color: var(--color-fg); font: 14px/1.4 var(--font-anthropic-sans); padding: 16px max(16px, env(safe-area-inset-right, 0px)) 32px max(16px, env(safe-area-inset-left, 0px)); }
</style></head><body>
<div id="dash-root">
"""
SHIM = r"""
<script id="assets-data" type="application/json">__DATA__</script>
<script>
// Minimal runtime: the same page code the claude.ai report uses, backed by the embedded data.
const d3 = (() => {
  const nf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 6 });
  const M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const hexToHsl = (hex) => { const n = parseInt(hex.slice(1), 16), r = (n >> 16 & 255) / 255, g = (n >> 8 & 255) / 255, b = (n & 255) / 255;
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, dd = mx - mn; let h = 0, s = 0;
    if (dd) { s = dd / (1 - Math.abs(2 * l - 1)); h = mx === r ? ((g - b) / dd) % 6 : mx === g ? (b - r) / dd + 2 : (r - g) / dd + 4; h = (h * 60 + 360) % 360; }
    return { h, s, l }; };
  const hslHex = (h, s, l) => { const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = l - c / 2;
    const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
    return '#' + [r, g, b].map((v) => Math.round((v + m) * 255).toString(16).padStart(2, '0')).join(''); };
  return {
    format: (spec) => spec === '.0%' ? (n) => Math.round(n * 100) + '%' : (n) => nf.format(n),
    utcFormat: () => (d) => M[d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear(),
    max: (a, f) => { let m; for (const x of a) { const v = f ? f(x) : x; if (v != null && (m === undefined || v > m)) m = v; } return m; },
    mean: (a) => a.length ? a.reduce((s, v) => s + v, 0) / a.length : undefined,
    hsl: (a, s, l) => { const o = typeof a === 'string' ? hexToHsl(a) : { h: a, s, l }; o.formatHex = () => hslHex(o.h, o.s, o.l); return o; }
  };
})();
const dash = (() => {
  const store = { assets: { status: 'ok', data: JSON.parse(document.getElementById('assets-data').textContent) } };
  const draws = new Map();
  const run = (name) => { const fn = draws.get(name); if (fn) document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => fn(el)); };
  return {
    data: (id) => store[id] || { status: 'missing', data: [] },
    calc: (id, o) => { store[id] = { status: 'ok', data: o.fn(...o.inputs.map((i) => store[i].data)) }; },
    draw: (name, fn) => { if (fn) draws.set(name, fn); else run(name); },
    runAll: () => { for (const n of draws.keys()) run(n); }
  };
})();
</script>
"""
TAIL = "\n<script>dash.runAll();</script>\n</div>\n</body></html>\n"
open(out, 'w', encoding='utf-8').write(HEAD + SHIM.replace('__DATA__', payload) + "\n" + frag + TAIL)
