import json, re, html, pathlib
D=str(pathlib.Path(__file__).resolve().parents[1]/'icons')
meta=json.load(open(f'{D}/glyphs.json'))
def svg(n,size,title=False):
    s=open(f'{D}/svg/glyph-{n:02d}.svg').read().strip()
    s=s.replace('width="24" height="24"',f'width="{size}" height="{size}" aria-hidden="true" focusable="false"')
    s=s.replace(' xmlns="http://www.w3.org/2000/svg"','')
    return re.sub(r'\n\s*','',s)
def std_svg(name,size):
    s=open(f'{D}/standard/{name}.svg').read().strip()
    s=s.replace('width="24" height="24"',f'width="{size}" height="{size}" aria-hidden="true" focusable="false"')
    s=s.replace(' xmlns="http://www.w3.org/2000/svg"','')
    return re.sub(r'\n\s*','',s)
std=json.load(open(f'{D}/standard.json'))
cards=[]
for g in meta:
    n=int(g['id'][-2:])
    cards.append(f'''<article class="card">
  <div class="tiles"><div class="tile light">{svg(n,96)}</div><div class="tile dark">{svg(n,96)}</div></div>
  <div class="meta"><div class="id">{g['id']} <span class="pos">r{g['row']} c{g['col']}</span></div>
  <p class="desc">{html.escape(g['description'])}</p>
  <p class="role"><span class="label">Role</span> {html.escape(g['suggestedRole'])} <span class="conf {g['confidence'].split()[0]}">{g['confidence']}</span></p></div>
</article>''')
def strip(size,theme):
    items=''.join(f'<span class="s" title="glyph-{n:02d}">{svg(n,size)}</span>' for n in range(1,42))
    return f'<div class="strip {theme}"><span class="sz">{size}px<br>{theme}</span><div class="row">{items}</div></div>'
strips=''.join(strip(s,t) for t in ('light','dark') for s in (16,24,32))
std_cards=[]
for g in std:
    std_cards.append(f'''<article class="card">
  <div class="tiles"><div class="tile light">{std_svg(g['id'],96)}</div><div class="tile dark">{std_svg(g['id'],96)}</div></div>
  <div class="meta"><div class="id">{g['id']} <span class="pos">{g['category']}</span></div>
  <p class="desc">{html.escape(g['description'])}</p></div>
</article>''')
def std_strip(size,theme):
    items=''.join(f'<span class="s" title="{g["id"]}">{std_svg(g["id"],size)}</span>' for g in std)
    return f'<div class="strip {theme}"><span class="sz">{size}px<br>{theme}</span><div class="row">{items}</div></div>'
std_strips=''.join(std_strip(s,t) for t in ('light','dark') for s in (16,24,32))
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Glyph Contact Sheet</title>
<style>
:root{{--bg:#f4f4f2;--fg:#1b1b1b;--muted:#666;--card:#fff;--line:#ddd;--lt:#fff;--dk:#16181c;--dkfg:#ececec}}
@media (prefers-color-scheme:dark){{:root{{--bg:#101114;--fg:#e8e8e8;--muted:#9a9a9a;--card:#191b1f;--line:#2c2f35}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,Roboto,Helvetica,Arial,sans-serif}}
header,main,section{{max-width:1280px;margin:0 auto;padding:0 16px}}
header{{padding-top:28px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:32px 0 12px}}
.note{{color:var(--muted);margin:0 0 4px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden}}
.tiles{{display:grid;grid-template-columns:1fr 1fr}}
.tile{{display:flex;align-items:center;justify-content:center;padding:14px 0}}
.tile svg{{outline:1px dashed rgba(127,127,127,.25)}}
.light{{background:var(--lt);color:#111}} .dark{{background:var(--dk);color:var(--dkfg)}}
.meta{{padding:10px 12px 12px;border-top:1px solid var(--line)}}
.id{{font-weight:600;font-variant-numeric:tabular-nums}} .pos{{color:var(--muted);font-weight:400;font-size:12px;margin-left:6px}}
.desc{{margin:4px 0 6px}} .role{{margin:0}} .label{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em;margin-right:4px}}
.conf{{font-size:11px;border-radius:9px;padding:1px 7px;margin-left:4px;border:1px solid currentColor}}
.conf.high{{color:#2f8a3e}} .conf.medium{{color:#b07a12}} .conf.low{{color:#999}}
.strip{{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:6px;margin-bottom:6px;overflow-x:auto}}
.strip .row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center}}
.sz{{font-size:12px;opacity:.7;min-width:36px;font-variant-numeric:tabular-nums}}
.s{{display:inline-flex}}
footer{{max-width:1280px;margin:32px auto;padding:0 16px;color:var(--muted);font-size:12px}}
</style></head><body>
<header><h1>Glyph contact sheet</h1>
<p class="note">41 monoline glyphs &middot; 24&times;24 viewBox &middot; stroke-width 1.2 &middot; butt caps, miter joins &middot; drawn in currentColor.</p>
<p class="note">Glyph artwork &copy; the owner. All rights reserved. Not covered by any open-source licence of the apps that use it.</p>
<p class="note">The standard icons further down are a separate, MIT-licensed set (icons/standard/).</p></header>
<main>
<h2>Glyphs (96&nbsp;px, light and dark)</h2>
<div class="grid">
{''.join(cards)}
</div>
<h2>Small-size legibility (16 / 24 / 32&nbsp;px)</h2>
{strips}
</main>
<section id="standard">
<h2>Standard icons (MIT)</h2>
<p class="note">{len(std)} conventional symbols drawn in the house style &middot; MIT, see LICENSE &middot; the glyphs above remain all rights reserved.</p>
<h2>Standard icons (96&nbsp;px, light and dark)</h2>
<div class="grid">
{''.join(std_cards)}
</div>
<h2>Standard icons, small-size legibility (16 / 24 / 32&nbsp;px)</h2>
{std_strips}
</section>
<footer>Suggested roles are guesses from the shapes alone, not decisions. Glyph numbers follow the source sheet row by row, left to right.</footer>
</body></html>
'''
open(f'{D}/contact-sheet.html','w').write(page)
print(len(page))
