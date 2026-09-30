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
from playwright.sync_api import sync_playwright

ROOT = g.ROOT
CARDS = ROOT / "assets" / "cards"
FONTS = (ROOT / "assets" / "fonts").as_uri()

CSS = f"""
@font-face{{font-family:S;font-weight:200 900;src:url({FONTS}/source-serif-4-latin-opsz-normal.woff2)}}
@font-face{{font-family:S;font-weight:200 900;src:url({FONTS}/source-serif-4-latin-ext-opsz-normal.woff2);unicode-range:U+0100-02FF,U+1E00-1EFF}}
@font-face{{font-family:P;font-weight:500;src:url({FONTS}/ibm-plex-sans-latin-500-normal.woff2)}}
@font-face{{font-family:P;font-weight:500;src:url({FONTS}/ibm-plex-sans-latin-ext-500-normal.woff2);unicode-range:U+0100-02FF,U+1E00-1EFF}}
@font-face{{font-family:P;font-weight:600;src:url({FONTS}/ibm-plex-sans-latin-600-normal.woff2)}}
@font-face{{font-family:M;src:url({FONTS}/ibm-plex-mono-latin-400-normal.woff2)}}
*{{box-sizing:border-box;margin:0}}
body{{background:#F5F2E9;color:#1E231F;font-family:S;width:var(--w);height:var(--h);position:relative;overflow:hidden}}
.band{{position:absolute;left:0;right:0;top:0;height:12px;background:#1E231F}}
.k{{font:600 24px/1.2 P;letter-spacing:.08em;text-transform:uppercase;color:#A8451A}}
h1{{font-weight:600;letter-spacing:-.02em;line-height:1.02}}
.ex{{color:#595F52}}
.fp{{display:grid;grid-template-columns:repeat(12,44px);gap:8px}}
.fp i{{display:block;width:44px;height:44px;border:2px solid #8C8676}}
.v-reconnu{{background:#1C4A32;border-color:#1C4A32!important}}
.v-partiel{{background:linear-gradient(to top,#C9A13B 50%,transparent 50%);border-color:#C9A13B!important}}
.v-conteste{{background:repeating-linear-gradient(45deg,#B5471C 0 4px,transparent 4px 10px);border-color:#B5471C!important}}
.loc{{position:relative}}
.loc img{{display:block;width:100%}}
.dot{{position:absolute;width:20px;height:20px;border-radius:50%;background:#E2622E;border:3px solid #F5F2E9;transform:translate(-50%,-50%)}}
.dot::after{{content:"";position:absolute;inset:-12px;border:2px solid #E2622E;border-radius:50%}}
.lad{{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;align-items:end}}
.lad span{{height:18px;border:1.5px solid #595F52}}
.lad span.on{{height:48px}}
.d0{{background:#EAE3D0}}.d1{{background:#D9C487}}.d2{{background:#AFA656}}.d3{{background:#6F914F}}.d4{{background:#3D7049}}.d5{{background:#1C4A32}}
.dl{{font:500 22px/1.25 P;color:#1E231F;margin-top:12px}}
.dl b{{font:400 40px/1 M;margin-right:10px;vertical-align:-4px}}
.foot{{position:absolute;display:flex;justify-content:space-between;align-items:baseline;font:500 22px/1 P;color:#595F52}}
.foot b{{font:600 30px/1 S;color:#1E231F}}
.foot b em{{font-style:normal;color:#A8451A}}
"""

def fit(title, base, maxlen):
    n = len(title)
    return base if n <= maxlen else max(int(base * maxlen / n), int(base * .55))

def doc(w, h, inner):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="--w:{w}px;--h:{h}px"><div class="band"></div>{inner}</body></html>'

def cells(d):
    return "".join(f'<i class="v-{d["droits"][k]["valeur"]}"></i>' for k in g.DKEYS)

def legend(fs=20):
    it=[("reconnu","Inscrit dans un texte"),("partiel","Partiel"),("conteste","Remis en cause"),("non_etabli","Aucune source")]
    return "".join(f'<span style="display:inline-flex;align-items:center;gap:8px;margin-right:22px"><i class="v-{k}" style="display:inline-block;width:{fs}px;height:{fs}px;border:2px solid #8C8676"></i>{l}</span>' for k,l in it)

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
<div class="fp" style="position:absolute;left:64px;top:442px">{cells(d)}</div>
<div style="position:absolute;left:64px;top:502px;font:500 19px/1 P;color:#595F52">{legend(18)}</div>
<div style="position:absolute;left:800px;top:64px;width:336px">
 <div class="loc"><img src="{landuri}"><span class="dot" style="left:{px:.2f}%;top:{py:.2f}%"></span></div>
 <div class="lad" style="margin-top:44px">{ladder(d['degre'])}</div>
 <p class="dl"><b>{d['degre']}/5</b>{e(lbl)}</p>
</div>
<div class="foot" style="left:64px;right:64px;top:568px"><span>{foot_txt} · 12 droits examinés</span><b>Communautés <em>reconnues</em></b></div>"""
        return doc(1200, 630, inner)
    fs = fit(t, 104, 14)
    big = "".join(f'<div style="display:flex;flex-direction:column;gap:6px;align-items:center"><i class="v-{d["droits"][k]["valeur"]}" style="width:120px;height:56px"></i><span style="font:500 17px/1.1 P;color:#595F52;text-align:center;height:38px">{e(l)}</span></div>' for k, l, _ in g.DROITS)
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
<div class="fp" style="position:absolute;left:72px;right:72px;top:800px;grid-template-columns:repeat(6,1fr);gap:18px 16px">{big}</div>
<div style="position:absolute;left:72px;right:72px;top:1150px;font:500 22px/1 P;color:#595F52">{legend(22)}</div>
<div class="foot" style="left:72px;right:72px;top:1262px"><span>{foot_txt}</span><b>Communautés <em>reconnues</em></b></div>"""
    return doc(1080, 1350, inner)

def card_generic(title, sub, fiches, landuri):
    pts = []
    for f in fiches:
        x, y = g.project(*f["coord"])
        c = ["#EAE3D0", "#D9C487", "#AFA656", "#6F914F", "#3D7049", "#1C4A32"][f["degre"]]
        pts.append(f'<span style="position:absolute;left:{100*x/g.MAP["W"]:.2f}%;top:{100*y/g.MAP["H"]:.2f}%;width:14px;height:14px;border-radius:50%;background:{c};border:2px solid #F5F2E9;outline:1px solid #595F52;transform:translate(-50%,-50%)"></span>')
    inner = f"""
<div style="position:absolute;left:64px;top:64px;width:540px">
 <p class="k">Atlas des autonomies · {len(fiches)} communautés</p>
 <h1 style="font-size:78px;margin-top:22px">{html.escape(title)}</h1>
 <p class="ex" style="font-size:30px;margin-top:18px;line-height:1.3">{html.escape(sub)}</p>
</div>
<div class="loc" style="position:absolute;left:600px;top:110px;width:560px"><img src="{landuri}">{''.join(pts)}</div>
<div class="lad" style="position:absolute;left:600px;top:420px;width:560px">{ladder(-1)}</div>
<div class="foot" style="left:64px;right:64px;top:568px"><span>communautes.actitude.org</span><b>Communautés <em>reconnues</em></b></div>"""
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
