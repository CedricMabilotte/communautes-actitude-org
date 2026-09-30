#!/usr/bin/env python3
"""Vignettes de partage (JPEG) : 1200×630 (og:image) et 1080×1350 (portrait) pour chaque fiche.

À lancer en local quand une fiche change (nécessite playwright + chromium) :
    python3 scripts/social_cards.py [uid ...]
Les JPEG vont dans assets/cards/ et sont versionnés.
"""
import html, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import generate_site as g
import visuel as V
from playwright.sync_api import sync_playwright

ROOT = g.ROOT
CARDS = ROOT / "assets" / "cards"
FONTS = (ROOT / "assets" / "fonts").as_uri()

CSS = f"""
@font-face{{font-family:J;font-weight:100 900;src:url({FONTS}/jost-latin-wght-normal.woff2)}}
@font-face{{font-family:J;font-weight:100 900;src:url({FONTS}/jost-latin-ext-wght-normal.woff2);unicode-range:U+0102-0111,U+0114-0129,U+012C-014B,U+014E-0169,U+016C-02BA,U+1E00-1EFF}}
@font-face{{font-family:F;font-weight:100 900;src:url({FONTS}/libre-franklin-latin-wght-normal.woff2)}}
@font-face{{font-family:F;font-weight:100 900;src:url({FONTS}/libre-franklin-latin-ext-wght-normal.woff2);unicode-range:U+0100-02FF,U+0300-036F,U+1E00-1EFF}}
:root{{--f-inst:#2656A6;--f-terr:#8F5E12;--f-comp:#B03A26;--f-etat:#1B1D1F;--ghost:#E1E3DF;--muted:#50555A;--accent:#2656A6}}
*{{box-sizing:border-box;margin:0}}
body{{background:#FFFFFF;color:#1B1D1F;font-family:J;width:var(--w);height:var(--h);position:relative;overflow:hidden}}
.band{{position:absolute;left:0;right:0;top:0;height:12px;display:flex}}.band i{{flex:1}}
.k{{font:500 24px/1.2 J;letter-spacing:.06em;text-transform:uppercase;color:#50555A}}
h1{{font-weight:500;letter-spacing:-.015em;line-height:1.02}}
.ex{{color:#50555A;font-family:F}}
.pf-inst{{fill:var(--f-inst)}}.pf-terr{{fill:var(--f-terr)}}.pf-comp{{fill:var(--f-comp)}}.pf-etat{{fill:var(--f-etat)}}
.pg{{fill:var(--ghost)}}.pdash{{stroke:var(--muted)}}.pm{{fill:var(--muted)}}
.hf-inst{{fill:var(--f-inst)}}.hf-terr{{fill:var(--f-terr)}}.hf-comp{{fill:var(--f-comp)}}.hf-etat{{fill:var(--f-etat)}}.hacc{{fill:var(--accent)}}
.mx{{display:inline-flex;gap:calc(var(--s) * .45)}}.mc{{display:flex;gap:calc(var(--s) * .12)}}.pc{{display:block}}
.loc{{position:relative}}
.loc img{{display:block;width:100%}}
.dot{{position:absolute;width:20px;height:20px;border-radius:50%;background:#2656A6;border:3px solid #fff;transform:translate(-50%,-50%)}}
.dot::after{{content:"";position:absolute;inset:-12px;border:2px solid #2656A6;border-radius:50%}}
.lad{{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;align-items:end}}
.lad span{{height:18px;border:1.5px solid #B8BCB5}}
.lad span.on{{height:48px}}
.d0{{background:#F1F2EE}}.d1{{background:#D3DBE7}}.d2{{background:#A4B5D0}}.d3{{background:#6F89B4}}.d4{{background:#3F6098}}.d5{{background:#1C3766}}
.dl{{font:500 22px/1.25 J;color:#1B1D1F;margin-top:12px}}
.dl b{{font:500 40px/1 J;margin-right:10px;vertical-align:-4px}}
.foot{{position:absolute;display:flex;justify-content:space-between;align-items:center;font:500 22px/1 J;color:#50555A}}
.foot b{{font:500 28px/1 J;color:#1B1D1F;display:flex;align-items:center;gap:12px}}
.mark{{display:grid;grid-template-columns:repeat(4,8px);gap:3px}}.mark i{{width:8px;height:8px}}
.mark i:nth-child(4n+1){{background:var(--f-inst)}}.mark i:nth-child(4n+2){{background:var(--f-terr)}}.mark i:nth-child(4n+3){{background:var(--f-comp)}}.mark i:nth-child(4n+4){{background:var(--f-etat)}}
"""

def fit(title, base, maxlen):
    n = len(title)
    return base if n <= maxlen else max(int(base * maxlen / n), int(base * .55))

def doc(w, h, inner):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="--w:{w}px;--h:{h}px">{V.sprite()}<div class="band"><i style="background:#2656A6"></i><i style="background:#8F5E12"></i><i style="background:#B03A26"></i><i style="background:#1B1D1F"></i></div>{inner}</body></html>'

def cells(d, size=44):
    return V.matrix(g.vals_of(d), {}, size)

def legend(fs=20):
    it=[("reconnu","Inscrit dans un texte"),("partiel","Partiel"),("conteste","Remis en cause"),("non_etabli","Aucune source")]
    return "".join(f'<span style="display:inline-flex;align-items:center;gap:8px;margin-right:22px">{V.pic("terres", k, fs)}{l}</span>' for k,l in it)

def ladder(n):
    return "".join(f'<span class="d{i}{" on" if i == n else ""}"></span>' for i in range(6))

def land():
    return (ROOT / "site" / "assets" / "land.svg").as_uri() if (ROOT / "site" / "assets" / "land.svg").exists() else ""

def card_land(d, landuri, portrait=False):
    x, y = g.project(*d["coord"])
    px, py = 100 * x / g.MAP["W"], 100 * y / g.MAP["H"]
    e = html.escape
    t = d["titre"]; ex = d["nom"] if d["titre"] != d["nom"] else (d.get("territoire") or "")
    kick = f'{g.REGIONS[d["region"]]} · {g.TYPES[d["type"]]}'
    lbl = g.DEGRES[d["degre"]][1]
    foot_txt = 'communautes.actitude.org'
    if not portrait:
        fs = fit(t, 88, 16)
        inner = f"""
<div style="position:absolute;left:64px;top:64px;width:680px">
 <p class="k">{e(kick)}</p>
 <h1 style="font-size:{fs}px;margin-top:22px">{e(t)}</h1>
 <p class="ex" style="font-size:30px;margin-top:14px">{e(ex)}</p>
</div>
<p class="k" style="position:absolute;left:64px;top:408px;color:#595F52;font-size:20px">Les 12 droits</p>
<div style="position:absolute;left:64px;top:436px">{cells(d)}</div>
<div style="position:absolute;left:64px;top:502px;font:500 19px/1 J;color:#595F52">{legend(18)}</div>
<div style="position:absolute;left:800px;top:64px;width:336px">
 <div class="loc"><img src="{landuri}"><span class="dot" style="left:{px:.2f}%;top:{py:.2f}%"></span></div>
 <div class="lad" style="margin-top:44px">{ladder(d['degre'])}</div>
 <p class="dl"><b>{d['degre']}/5</b>{e(lbl)}</p>
</div>
<div class="foot" style="left:64px;right:64px;top:568px"><span>{foot_txt} · 12 droits examinés</span><b><span class="mark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>Communautés reconnues</b></div>"""
        return doc(1200, 630, inner)
    fs = fit(t, 104, 14)
    big = "".join(f'<div style="display:flex;flex-direction:column;gap:8px;align-items:center">{V.pic(k, d["droits"][k]["valeur"], 84)}<span style="font:500 17px/1.1 J;color:#50555A;text-align:center;height:38px">{e(l)}</span></div>' for k, l, _ in g.DROITS)
    inner = f"""
<div style="position:absolute;left:72px;right:72px;top:96px">
 <p class="k" style="font-size:26px">{e(kick)}</p>
 <h1 style="font-size:{fs}px;margin-top:22px">{e(t)}</h1>
 <p class="ex" style="font-size:36px;margin-top:14px">{e(ex)}</p>
</div>
<div style="position:absolute;left:72px;right:72px;top:470px;display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:end">
 <div class="loc"><img src="{landuri}"><span class="dot" style="left:{px:.2f}%;top:{py:.2f}%"></span></div>
 <div><div class="lad">{ladder(d['degre'])}</div><p class="dl" style="font-size:26px"><b>{d['degre']}/5</b>{e(lbl)}</p></div>
</div>
<div style="position:absolute;left:72px;right:72px;top:790px;display:grid;grid-template-columns:repeat(6,1fr);gap:16px 16px">{big}</div>
<div style="position:absolute;left:72px;right:72px;top:1150px;font:500 22px/1 J;color:#595F52">{legend(22)}</div>
<div class="foot" style="left:72px;right:72px;top:1262px"><span>{foot_txt}</span><b><span class="mark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>Communautés reconnues</b></div>"""
    return doc(1080, 1350, inner)

def card_generic(title, sub, fiches, landuri):
    pts = []
    for f in fiches:
        x, y = g.project(*f["coord"])
        c = ["#F1F2EE", "#D3DBE7", "#A4B5D0", "#6F89B4", "#3F6098", "#1C3766"][f["degre"]]
        pts.append(f'<span style="position:absolute;left:{100*x/g.MAP["W"]:.2f}%;top:{100*y/g.MAP["H"]:.2f}%;width:14px;height:14px;border-radius:50%;background:{c};border:2px solid #F5F2E9;outline:1px solid #8A8F94;transform:translate(-50%,-50%)"></span>')
    inner = f"""
<div style="position:absolute;left:64px;top:64px;width:540px">
 <p class="k" style="font-size:21px">Atlas des autonomies · {len(fiches)} communautés</p>
 <h1 style="font-size:78px;margin-top:22px">{html.escape(title)}</h1>
 <p class="ex" style="font-size:30px;margin-top:18px;line-height:1.3">{html.escape(sub)}</p>
</div>
<div class="loc" style="position:absolute;left:600px;top:110px;width:560px"><img src="{landuri}">{''.join(pts)}</div>
<div class="lad" style="position:absolute;left:600px;top:420px;width:560px">{ladder(-1)}</div>
<div class="foot" style="left:64px;right:64px;top:568px"><span>communautes.actitude.org</span><b><span class="mark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>Communautés reconnues</b></div>"""
    return doc(1200, 630, inner)

def main():
    fiches = g.charger()
    only = set(sys.argv[1:])
    CARDS.mkdir(parents=True, exist_ok=True)
    landfile = ROOT / "assets" / "cards-src" / "land.svg"
    landfile.parent.mkdir(exist_ok=True)
    landfile.write_text(g.land_svg_file(), encoding="utf-8")
    landuri = landfile.as_uri()
    tmp = ROOT / "assets" / "cards-src" / "tmp.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        def shot(htmltxt, w, h, out):
            tmp.write_text(htmltxt, encoding="utf-8")
            pg.set_viewport_size({"width": w, "height": h})
            pg.goto(tmp.as_uri()); pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(out), type="jpeg", quality=86)
        if not only:
            shot(card_generic("Qui décide ici ?", "Les droits d'autonomie inscrits dans le droit des États, communauté par communauté.", fiches, landuri), 1200, 630, CARDS / "_accueil.jpg")
            for dos in g.charger_dossiers({f["uid"] for f in fiches}):
                sub = [x for x in fiches if x["uid"] in {c.get("atlas_uid") for c in dos.get("cas") or []}] or fiches
                shot(card_generic(dos["titre"] if len(dos["titre"]) < 60 else dos["titre"].split(":")[0], f'Dossier thématique · {len(dos.get("cas") or [])} cas', sub, landuri), 1200, 630, CARDS / f"_dossier-{dos['slug']}.jpg")
            shot(card_generic("Douze droits, côte à côte", "Tableau comparatif des droits d'autonomie de chaque communauté de l’atlas.", fiches, landuri), 1200, 630, CARDS / "_comparer.jpg")
        for d in fiches:
            if only and d["uid"] not in only:
                continue
            shot(card_land(d, landuri), 1200, 630, CARDS / f"{d['uid']}.jpg")
            shot(card_land(d, landuri, portrait=True), 1080, 1350, CARDS / f"{d['uid']}-portrait.jpg")
        b.close()
    tmp.unlink(missing_ok=True)
    print("vignettes :", len(list(CARDS.glob("*.jpg"))))

if __name__ == "__main__":
    main()
