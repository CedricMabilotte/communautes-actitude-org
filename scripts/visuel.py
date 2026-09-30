"""Éléments graphiques de l'atlas.

Thème clair (atlas Isotype) : matrice 4 × 3 de pictogrammes d'objets du droit, aucune figure humaine.
Thème sombre (encre de nuit) : cadran de 12 secteurs, le premier à midi, dans l'ordre du cadre.
Les deux sont rendus dans la page ; la feuille de style montre celui du thème actif.
"""
import html, math

DKEYS = ["autogouvernement", "pouvoir_normatif", "justice_propre", "terres", "ressources", "consentement",
         "langue", "education", "fiscalite", "representation", "statut_personnel", "autodetermination_externe"]
FAM = [("inst", "Institutions", DKEYS[0:3]), ("terr", "Territoire", DKEYS[3:6]),
       ("comp", "Compétences", DKEYS[6:9]), ("etat", "Rapport à l'État", DKEYS[9:12])]
FAM_OF = {k: f for f, _, ks in FAM for k in ks}

def e(s):
    return html.escape(str(s), quote=True)

P = {
    # hémicycle : deux gradins en demi-couronne, tribune, socle
    "autogouvernement": "M1.5,18.5A10.5,10.5 0 0 1 22.5,18.5H19.2A7.2,7.2 0 0 0 4.8,18.5Z"
                        "M6.3,18.5A5.7,5.7 0 0 1 17.7,18.5H14.6A2.6,2.6 0 0 0 9.4,18.5Z"
                        "M10.6,14.6H13.4V18.5H10.6Z"
                        "M1.5,19.8H22.5V22H1.5Z",
    # table de loi : stèle à fronton cintré, lignes gravées en réserve, plinthe
    "pouvoir_normatif": "M5,20V8.5A7,7 0 0 1 19,8.5V20Z"
                        "M8.2,8.6V10.1H15.8V8.6Z M8.2,11.9V13.4H15.8V11.9Z M8.2,15.2V16.7H13.4V15.2Z"
                        "M3,20.6H21V22.8H3Z",
    # balance : fléau, colonne, deux plateaux suspendus
    "justice_propre": "M10.9,4.6H13.1V19.6H10.9Z M12,1.6A1.7,1.7 0 1 1 11.99,1.6Z"
                      "M2.5,5.2H21.5V7H2.5Z M7,20.2H17V22.4H7Z"
                      "M5,7L1.9,13.4H3L5.6,8.1 8.2,13.4H9.3L6.2,7Z"
                      "M17.8,7L14.7,13.4H15.8L18.4,8.1 21,13.4H22.1L19,7Z"
                      "M1.4,13.6H9.8A4.2,4.2 0 0 1 1.4,13.6Z M14.2,13.6H22.6A4.2,4.2 0 0 1 14.2,13.6Z",
    # parcelle : champ en perspective, trois bandes labourées, borne
    "terres": "M1.5,20L3.1,16.8H18.6L17,20Z M3.7,15.6L5.3,12.4H20.8L19.2,15.6Z M5.9,11.2L7.5,8H23L21.4,11.2Z"
              "M3,3.5H5.2V9.2H3Z M5.2,3.5L9.6,5 5.2,6.5Z",
    # goutte : ressource, avec ligne de niveau en réserve
    "ressources": "M12,1.5C12,1.5 4.6,10.4 4.6,15.2A7.4,7.4 0 0 0 19.4,15.2C19.4,10.4 12,1.5 12,1.5Z"
                  "M7.9,16.9C9.6,16.2 10.6,17.8 12,17.8S14.4,16.2 16.1,16.9L15.6,18.1C14.4,17.6 13.4,19.1 12,19.1S9.6,17.6 8.4,18.1Z",
    # main levée : paume ouverte, doigts en barres, manchette (aucun visage, aucun corps)
    "consentement": "M6.4,6.2A1.3,1.3 0 0 1 9,6.2V12H6.4Z M9.6,3.8A1.3,1.3 0 0 1 12.2,3.8V12H9.6Z"
                    "M12.8,4.4A1.3,1.3 0 0 1 15.4,4.4V12H12.8Z M16,7A1.3,1.3 0 0 1 18.6,7V14H16Z"
                    "M6.4,12.6H18.6V16.4L16.4,19.4H8.8L6.4,16.4Z"
                    "M6.4,15.6L2.9,11.4A1.3,1.3 0 0 1 4.9,9.8L7.6,12.9Z"
                    "M8.6,20.2H16.4V22.6H8.6Z",
    # bulle : parole, deux lignes en réserve
    "langue": "M2,3.5H22V16.5H11.5L6,21.5V16.5H2Z M5.5,7.4V9H18.5V7.4Z M5.5,11V12.6H14V11Z",
    # livre : ouvert, pages en biais, tranche
    "education": "M1.5,5.5Q6.5,5 11.2,7.4V20.4Q6.5,18 1.5,18.5Z M12.8,7.4Q17.5,5 22.5,5.5V18.5Q17.5,18 12.8,20.4Z"
                 "M1.5,19.7Q6.5,19.2 11.2,21.6H12.8Q17.5,19.2 22.5,19.7V21.6Q17.5,21.2 12.8,23H11.2Q6.5,21.2 1.5,21.6Z",
    # pièce : monnaie à trou carré, listel en réserve
    "fiscalite": "M12,2.5A9.5,9.5 0 1 1 11.99,2.5Z M12,4.6A7.4,7.4 0 1 0 12.01,4.6Z"
                 "M12,5.7A6.3,6.3 0 1 1 11.99,5.7Z M9.8,9.8V14.2H14.2V9.8Z",
    # siège : fauteuil de parlement, dossier, assise, pieds
    "representation": "M5.2,2.5H18.8V11.6H5.2Z M3.2,12.6H20.8V16H3.2Z M4.6,16H7.2V22.5H4.6Z M16.8,16H19.4V22.5H16.8Z"
                      "M3.2,8.8H5.2V12.6H3.2Z M18.8,8.8H20.8V12.6H18.8Z",
    # carte d'identité : cadre vide (aucun portrait), lignes, puce
    "statut_personnel": "M1.5,5H22.5V19H1.5Z M4,8V16H10V8Z M12,8.2V9.8H20V8.2Z M12,11.2V12.8H20V11.2Z M12,14.2V15.8H17V14.2Z",
    # urne : bulletin plié engagé dans la fente
    "autodetermination_externe": "M8.4,1.8H15.6V12.8H8.4Z M8.4,6.4L15.6,5.2V6.6L8.4,7.8Z"
                                 "M2.5,12H7.4V14.2H16.6V12H21.5V22.5H2.5Z M9,17V18.6H15V17Z",
}


def sprite():
    """Symboles et motifs partagés, à placer une fois par page."""
    sy = "".join(f'<symbol id="p-{k}" viewBox="0 0 24 24"><path fill-rule="evenodd" d="{d}"/></symbol>' for k, d in P.items())
    pats = "".join(
        f'<pattern id="h-{fk}" width="3.2" height="3.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="1.3" height="3.2" class="hf hf-{fk}"/></pattern>' for fk, _, _ in FAM)
    hc = ('<pattern id="hc" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(40)">'
          '<rect width="1.5" height="4" class="hacc"/></pattern>')
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            f'<clipPath id="cut" clipPathUnits="userSpaceOnUse"><rect x="0" y="0" width="12" height="24"/></clipPath>'
            f'{pats}{hc}</defs>{sy}</svg>')


def pic(k, v, size=24, label=None):
    fk = FAM_OF[k]
    u = f"#p-{k}"
    if v == "reconnu":
        inner = f'<use href="{u}" class="pf pf-{fk}"/>'
    elif v == "partiel":
        inner = f'<use href="{u}" class="pg"/><use href="{u}" class="pf pf-{fk}" clip-path="url(#cut)"/>'
    elif v == "conteste":
        inner = f'<use href="{u}" fill="url(#h-{fk})"/>'
    elif v == "non_etabli":
        inner = (f'<use href="{u}" class="pg"/><rect x=".75" y=".75" width="22.5" height="22.5" fill="none" class="pdash" '
                 f'stroke-width=".9" stroke-dasharray=".1 2.2" stroke-linecap="round"/>')
    else:
        inner = '<rect x="7" y="11.2" width="10" height="1.6" class="pm"/>'
    t = f"<title>{e(label)}</title>" if label else ""
    return f'<svg class="pc" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true">{t}{inner}</svg>'


def matrix(vals, labels, size=16):
    cols = []
    for fk, _, ks in FAM:
        cols.append('<span class="mc">' + "".join(pic(k, vals[k], size, labels.get(k)) for k in ks) + "</span>")
    return f'<span class="mx" style="--s:{size}px">{"".join(cols)}</span>'


# ------------------------------------------------------------------ cadran
def _pt(cx, cy, r, a):
    t = math.radians(a)
    return cx + r * math.sin(t), cy - r * math.cos(t)


def sector(cx, cy, r0, r1, a0, a1):
    x0, y0 = _pt(cx, cy, r1, a0); x1, y1 = _pt(cx, cy, r1, a1)
    x2, y2 = _pt(cx, cy, r0, a1); x3, y3 = _pt(cx, cy, r0, a0)
    lg = 1 if a1 - a0 > 180 else 0
    return (f"M{x0:.2f},{y0:.2f}A{r1},{r1} 0 {lg} 1 {x1:.2f},{y1:.2f}L{x2:.2f},{y2:.2f}"
            f"A{r0},{r0} 0 {lg} 0 {x3:.2f},{y3:.2f}Z")


def seg_angles(i, small=1.4, big=4.5):
    a0 = i * 30 + (big if i % 3 == 0 else small)
    a1 = (i + 1) * 30 - (big if i % 3 == 2 else small)
    return a0, a1


def seg(v, cx, cy, r0, r1, i, sw=1):
    a0, a1 = seg_angles(i)
    if v == "reconnu":
        return f'<path d="{sector(cx, cy, r0, r1, a0, a1)}" class="dlit"/>'
    if v == "partiel":
        mid = r0 + (r1 - r0) / 2
        return (f'<path d="{sector(cx, cy, r0, r1, a0, a1)}" class="doff dstroke" stroke-width="{sw * .6}"/>'
                f'<path d="{sector(cx, cy, r0, mid, a0, a1)}" class="dlit"/>')
    if v == "conteste":
        return f'<path d="{sector(cx, cy, r0, r1, a0, a1)}" fill="url(#hc)" class="dacc" stroke-width="{sw * .8}"/>'
    if v == "non_etabli":
        return (f'<path d="{sector(cx, cy, r0 + sw / 2, r1 - sw / 2, a0 + .4, a1 - .4)}" fill="none" class="dstroke" '
                f'stroke-width="{sw}" stroke-dasharray="{sw * .1} {sw * 3}" stroke-linecap="round"/>')
    am = (a0 + a1) / 2
    x0, y0 = _pt(cx, cy, r0 + (r1 - r0) * .38, am); x1, y1 = _pt(cx, cy, r0 + (r1 - r0) * .62, am)
    return f'<path d="M{x0:.2f},{y0:.2f}L{x1:.2f},{y1:.2f}" class="dmut" stroke-width="{sw * 1.2}"/>'


def dial(vals, size=44, only=None):
    c = 50
    parts = ['<circle cx="50" cy="50" r="15" fill="none" class="dfaint" stroke-width="1"/>']
    for i, k in enumerate(DKEYS):
        if only is not None and i != only:
            a0, a1 = seg_angles(i)
            parts.append(f'<path d="{sector(c, c, 20, 48, a0, a1)}" class="doff"/>')
            continue
        parts.append(seg(vals[k], c, c, 20, 48, i, sw=2.2))
    return f'<svg class="dial" viewBox="0 0 100 100" width="{size}" height="{size}" aria-hidden="true">{"".join(parts)}</svg>'


def fiche_dial(vals, short):
    W = 560
    c = W / 2
    r0, r1 = 92, 214
    parts = [f'<circle cx="{c}" cy="{c}" r="{r0 - 16}" fill="none" class="dfaint"/>']
    for i, k in enumerate(DKEYS):
        parts.append(seg(vals[k], c, c, r0, r1, i, sw=3))
        a0, a1 = seg_angles(i)
        am = (a0 + a1) / 2
        lx, ly = _pt(c, c, r1 + 18, am)
        anchor = "start" if 8 < am < 172 else ("end" if 188 < am < 352 else "middle")
        parts.append(f'<text class="dlab" x="{lx:.1f}" y="{ly + 5:.1f}" text-anchor="{anchor}"><tspan class="dnum">{i + 1:02d} </tspan>{e(short[k])}</text>')
    v = list(vals.values())
    parts.append(f'<text class="dtot" x="{c}" y="{c + 6}" text-anchor="middle">{v.count("reconnu")} + {v.count("partiel")}</text>'
                 f'<text class="dlab" x="{c}" y="{c + 28}" text-anchor="middle">inscrits + partiels</text>')
    return f'<svg class="fdial" viewBox="-110 -10 {W + 220} {W + 20}" aria-hidden="true">{"".join(parts)}</svg>'


def big_dial(counts, n, short):
    """counts[k] = (inscrits, partiels, remis en cause) ; longueur des secteurs = part des fiches."""
    W, H = 860, 700
    cx, cy = W / 2, H / 2
    r0, rmax = 70, 262
    parts = []
    for i, k in enumerate(DKEYS):
        a0, a1 = seg_angles(i, 1.2, 3.5)
        rec, par, con = counts[k]
        r1 = r0 + (rmax - r0) * rec / n
        r2 = r1 + (rmax - r0) * par / n
        r3 = r2 + (rmax - r0) * con / n
        parts.append(f'<path d="{sector(cx, cy, r0, rmax, a0, a1)}" class="doff"/>')
        parts.append(f'<path d="{sector(cx, cy, r0, r1, a0, a1)}" class="dlit"/>')
        parts.append(f'<path d="{sector(cx, cy, r1, r2, a0, a1)}" class="dhalf"/>')
        if con:
            parts.append(f'<path d="{sector(cx, cy, r2, r3, a0, a1)}" fill="url(#hc)"/>')
        am = (a0 + a1) / 2
        lx, ly = _pt(cx, cy, rmax + 22, am)
        anchor = "start" if 6 < am < 174 else ("end" if 186 < am < 354 else "middle")
        dy = -10 if (am < 30 or am > 330) else (14 if 150 < am < 210 else 0)
        x0, y0 = _pt(cx, cy, rmax + 4, am); x1, y1 = _pt(cx, cy, rmax + 15, am)
        parts.append(f'<path d="M{x0:.1f},{y0:.1f}L{x1:.1f},{y1:.1f}" class="dstroke" stroke-width="1"/>')
        parts.append(f'<text class="dlab" x="{lx:.1f}" y="{ly + dy:.1f}" text-anchor="{anchor}"><tspan class="dnum">{i + 1:02d} </tspan>{e(short[k])}</text>'
                     f'<text class="dlab dsm" x="{lx:.1f}" y="{ly + dy + 15:.1f}" text-anchor="{anchor}">{rec} + {par} partiels</text>')
    for q in (.25, .5, .75):
        r = r0 + (rmax - r0) * q
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" class="dring" stroke-width="1.6"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{rmax + .5}" fill="none" class="dstroke" stroke-width="1"/>')
    parts.append(f'<text class="dtot" x="{cx}" y="{cy - 4}" text-anchor="middle">{n} fiches</text>'
                 f'<text class="dlab" x="{cx}" y="{cy + 18}" text-anchor="middle">12 droits</text>')
    for fi in range(4):
        a0 = fi * 90 + 3.5; a1 = fi * 90 + 90 - 3.5
        x0, y0 = _pt(cx, cy, r0 - 10, a0); x1, y1 = _pt(cx, cy, r0 - 10, a1)
        parts.append(f'<path d="M{x0:.1f},{y0:.1f}A{r0 - 10},{r0 - 10} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" class="dacc" stroke-width="1.2"/>')
    return (f'<svg class="bdial" viewBox="-40 0 {W + 80} {H}" role="img" aria-label="Cadran : pour chacun des douze droits, '
            f'la part des {n} fiches où il est inscrit dans un texte, puis partiel, puis remis en cause">{"".join(parts)}</svg>')


def dorling(pts, r, gap=1.0, iters=400, pull=0.03):
    import random
    pts = [list(p) for p in pts]
    org = [p[:] for p in pts]
    rnd = random.Random(7)
    n = len(pts)
    m = 2 * r + gap
    for _ in range(iters):
        for i in range(n):
            for j in range(i + 1, n):
                dx = pts[j][0] - pts[i][0]; dy = pts[j][1] - pts[i][1]
                d = math.hypot(dx, dy)
                if d < m:
                    if d < 1e-6:
                        a = rnd.random() * 6.283
                        dx, dy, d = math.cos(a), math.sin(a), 1
                    push = (m - d) / 2
                    ux, uy = dx / d, dy / d
                    pts[i][0] -= ux * push; pts[i][1] -= uy * push
                    pts[j][0] += ux * push; pts[j][1] += uy * push
        for i in range(n):
            pts[i][0] += (org[i][0] - pts[i][0]) * pull
            pts[i][1] += (org[i][1] - pts[i][1]) * pull
    return pts
