#!/usr/bin/env python3
"""Génère communautes.actitude.org depuis data/communautes/*.yml vers site/.

Seule dépendance : pyyaml. Les garde-fous font échouer la génération.
"""
import csv, datetime as dt, html, io, json, math, os, re, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import quote
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import visuel as V

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "communautes"
PAGES = ROOT / "pages"
ASSETS = ROOT / "assets"
OUT = ROOT / "site"
BASE = "https://communautes.actitude.org"
REPO = "https://github.com/CedricMabilotte/communautes-actitude-org"
CONTACT = "contact@actitude.org"
LICENCE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr"
TODAY = dt.date.today().isoformat()

# ---------------------------------------------------------------- référentiels
DROITS = [
    ("autogouvernement", "Institutions propres", "Une assemblée ou un gouvernement propre, reconnu par l'État."),
    ("pouvoir_normatif", "Faire ses propres règles", "Des normes obligatoires : lois de pays, droit coutumier reconnu."),
    ("justice_propre", "Justice propre", "Une juridiction propre ou la reconnaissance de la justice coutumière."),
    ("terres", "Terres et territoire", "Propriété ou maîtrise collective des terres."),
    ("ressources", "Ressources naturelles", "Contrôle ou partage du sous-sol, de l'eau, des forêts, de la pêche."),
    ("consentement", "Consultation, consentement", "Obligation de consulter, ou d'obtenir l'accord, avant un projet."),
    ("langue", "Langue officielle", "La langue est officielle ou co-officielle."),
    ("education", "Éducation", "Un enseignement propre, ou maîtrisé par la communauté."),
    ("fiscalite", "Impôt et budget", "Un pouvoir fiscal ou un budget propre garanti."),
    ("representation", "Sièges garantis", "Une représentation garantie dans les institutions de l'État."),
    ("statut_personnel", "Statut ou citoyenneté propre", "Citoyenneté locale, droit de domicile, statut civil coutumier."),
    ("autodetermination_externe", "Choisir son statut", "Un référendum d'indépendance ou un droit de sécession prévu par un texte."),
]
DKEYS = [d[0] for d in DROITS]
VALEURS = {
    "reconnu": "Inscrit dans un texte",
    "partiel": "Partiel",
    "conteste": "Remis en cause",
    "non_etabli": "Aucune source trouvée",
    "non_applicable": "Sans objet",
}
VRANK = {"reconnu": 4, "partiel": 3, "conteste": 2, "non_etabli": 1, "non_applicable": 0}
EFFECT = {"effective": "Appliqué", "partielle": "Appliqué en partie", "contestee": "Contesté dans les faits", "non_etablie": "Inconnue"}
TYPES = {
    "peuple_autochtone": "Peuple autochtone",
    "peuple_tribal": "Peuple tribal",
    "minorite_nationale": "Minorité nationale, ethnique ou linguistique",
    "communaute_afrodescendante": "Communauté afrodescendante",
    "peuple_territoire_non_autonome": "Territoire non autonome",
    "peuple_libre_association": "État en libre association",
    "collectivite_insulaire_ou_regionale": "Région autonome à statut international",
}
REGIONS = {"afrique": "Afrique", "ameriques": "Amériques", "asie": "Asie", "europe": "Europe", "oceanie": "Océanie"}
BASES = {"territoriale": "Territoriale", "personnelle": "Personnelle (sans territoire)", "mixte": "Mixte"}
DEGRES = [
    (0, "Aucun droit établi", "Aucune source n'établit un droit de la grille."),
    (1, "Participation", "Consultation, langue, éducation, sièges ou statut : la communauté participe, sans institution propre ni terres."),
    (2, "Gestion propre", "Des institutions propres ou des terres collectives, sans pouvoir normatif ni justice propre."),
    (3, "Autogouvernement", "Des institutions propres qui font des règles ou rendent la justice, au moins en partie."),
    (4, "Autonomie législative", "Des institutions propres qui légifèrent pleinement dans leurs domaines."),
    (5, "Autodétermination ouverte", "Un texte prévoit que la population choisisse son statut, jusqu'à l'indépendance."),
]
COURT = ["aucun", "particip.", "gestion", "autogouv.", "législatif", "autodéterm."]
MECA = {
    "liste_tna": ("Liste des territoires non autonomes", "contraignant"),
    "dnudpa": ("Déclaration sur les droits des peuples autochtones", "déclaratif"),
    "oit_169": ("Convention 169 de l'OIT", "contraignant"),
    "rapporteur_special": ("Rapporteur spécial", "mention"),
    "organe_traite": ("Organe de traité", "mention"),
    "instance_permanente": ("Instance permanente / MEDPA", "mention"),
    "forum_minorites": ("Forum sur les minorités", "déclaratif"),
    "accord_sous_egide": ("Accord sous égide ONU ou SDN", "contraignant"),
    "mission_onu": ("Mission des Nations unies", "contraignant"),
}
FORCE_TXT = {"contraignant": "Engagement contraignant", "déclaratif": "Texte déclaratif", "mention": "Mention par un organe"}
NATURES = {"constitution": "Constitution", "loi_organique": "Loi organique", "statut_autonomie": "Statut d'autonomie", "loi": "Loi ou décret",
           "traite": "Traité", "accord_revendication": "Accord de revendication", "accord_paix": "Accord de paix",
           "jurisprudence": "Jurisprudence", "coutume_reconnue": "Coutume reconnue"}
PUBLIC_KEYS = ["uid", "nom", "endonyme", "territoire", "etats", "region", "coord", "type", "types_secondaires", "base", "population", "lieux", "surface_km2", "reconnaissance_regionale",
               "resume", "reconnaissance_onu", "base_nationale", "droits", "effectivite", "chronologie", "fiabilite", "sources"]

NNBSP = "\u202f"

def typo(t):
    t = re.sub(r"[ \u00a0]([:;?!»])", NNBSP + r"\1", t)
    return re.sub(r"«[ \u00a0]", "«" + NNBSP, t)

def e(s):
    return html.escape(typo(str(s if s is not None else "")), quote=True)

def fail(msg):
    print("ÉCHEC :", msg, file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------- données
def ge_p(v):
    return v in ("reconnu", "partiel")

def degre(d):
    v = {k: d["droits"][k]["valeur"] for k in DKEYS}
    if ge_p(v["autodetermination_externe"]):
        return 5
    if v["autogouvernement"] == "reconnu" and v["pouvoir_normatif"] == "reconnu":
        return 4
    if ge_p(v["autogouvernement"]) and (ge_p(v["pouvoir_normatif"]) or ge_p(v["justice_propre"])):
        return 3
    if ge_p(v["autogouvernement"]) or ge_p(v["terres"]):
        return 2
    if any(ge_p(x) for x in v.values()):
        return 1
    return 0

MECA_REG = {
    "commission_africaine": "Commission africaine des droits de l'homme et des peuples",
    "cour_africaine": "Cour africaine des droits de l'homme et des peuples",
    "cour_interamericaine": "Cour interaméricaine des droits de l'homme",
    "commission_interamericaine": "Commission interaméricaine des droits de l'homme",
    "conseil_europe_fcnm": "Convention-cadre pour la protection des minorités nationales",
    "charte_langues_regionales": "Charte européenne des langues régionales ou minoritaires",
    "union_europeenne": "Union européenne",
}
NIVEAUX = {"onu": "Nations unies", "regional": "Système régional", "national": "État seulement"}

def niveau(d):
    if d.get("reconnaissance_onu"):
        return "onu"
    if d.get("reconnaissance_regionale"):
        return "regional"
    return "national"

def force(d):
    order = ["contraignant", "déclaratif", "mention"]
    fs = [MECA[r["mecanisme"]][1] for r in d.get("reconnaissance_onu", []) if r.get("mecanisme") in MECA]
    for o in order:
        if o in fs:
            return o
    return None

def date_maj(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return dt.date.fromtimestamp(path.stat().st_mtime).isoformat()

def charger():
    fiches, uids = [], set()
    for p in sorted(DATA.glob("*.yml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        uid = d.get("uid")
        if uid != p.stem:
            fail(f"{p.name} : uid « {uid} » différent du nom de fichier")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", uid):
            fail(f"{p.name} : uid non ASCII ou mal formé")
        if uid in uids:
            fail(f"uid en double : {uid}")
        uids.add(uid)
        for k in ["nom", "etats", "region", "coord", "type", "resume", "droits", "effectivite", "sources"]:
            if not d.get(k):
                fail(f"{uid} : champ {k} manquant")
        if d["type"] not in TYPES: fail(f"{uid} : type inconnu {d['type']}")
        if d["region"] not in REGIONS: fail(f"{uid} : région inconnue")
        if d.get("base", "territoriale") not in BASES: fail(f"{uid} : base inconnue")
        for k in DKEYS:
            r = d["droits"].get(k)
            if not r or r.get("valeur") not in VALEURS:
                fail(f"{uid} : droit {k} absent ou valeur invalide")
            if r["valeur"] in ("reconnu", "partiel", "conteste") and not (r.get("note") and str(r.get("source", "")).startswith("http")):
                fail(f"{uid} : droit {k} = {r['valeur']} sans note ni source")
        if d["effectivite"].get("valeur") not in EFFECT: fail(f"{uid} : effectivité invalide")
        for r in d.get("reconnaissance_onu", []):
            if r.get("mecanisme") not in MECA: fail(f"{uid} : mécanisme ONU inconnu {r.get('mecanisme')}")
        for s in d["sources"]:
            if not str(s.get("url", "")).startswith("http"): fail(f"{uid} : source sans URL")
        pub = {k: d.get(k) for k in PUBLIC_KEYS}       # liste blanche (biblio L63)
        pub.setdefault("base", "territoriale")
        if pub["base"] is None: pub["base"] = "territoriale"
        pub["degre"] = degre(d)
        pub["force_onu"] = force(d)
        pub["niveau_reconnaissance"] = niveau(d)
        for r in d.get("reconnaissance_regionale") or []:
            if r.get("mecanisme") not in MECA_REG:
                fail(f"{uid} : mécanisme régional inconnu {r.get('mecanisme')}")
        pub["date_maj"] = date_maj(p)
        pub["titre"] = d.get("endonyme") or d["nom"]
        fiches.append(pub)
    if not fiches:
        fail("aucune fiche")
    import unicodedata
    fiches.sort(key=lambda f: unicodedata.normalize("NFD", f["titre"]).encode("ascii", "ignore").decode().lower())
    return fiches

# ---------------------------------------------------------------- carte
MAP = json.loads((ASSETS / "map.json").read_text())

def project(lat, lon):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    M = math.sqrt(3) / 2
    lam, phi = math.radians(lon), math.radians(lat)
    l = math.asin(M * math.sin(phi)); l2 = l * l; l6 = l2 ** 3
    x = lam * math.cos(l) / (M * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)))
    y = l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2))
    k = MAP["scale"]; tx, ty = MAP["translate"]
    return tx + k * x, ty - k * y

def land_svg_file():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MAP["W"]} {MAP["H"]}">'
            f'<path d="{MAP["sphere"]}" fill="none" stroke="#D3D6D0" stroke-width="1"/>'
            f'<path d="{MAP["land"]}" fill="#C4C8C1" fill-opacity=".6"/></svg>')

# ---------------------------------------------------------------- gabarits
LBLS = {k: l for k, l, _ in DROITS}
COURTS = {"autogouvernement": "Institutions", "pouvoir_normatif": "Règles", "justice_propre": "Justice", "terres": "Terres",
          "ressources": "Ressources", "consentement": "Consentement", "langue": "Langue", "education": "Éducation",
          "fiscalite": "Impôt", "representation": "Sièges", "statut_personnel": "Statut", "autodetermination_externe": "Choisir son statut"}

def vals_of(d):
    return {k: d["droits"][k]["valeur"] for k in DKEYS}

def fp(d, lg=False):
    v = vals_of(d)
    n = list(v.values()).count("reconnu"); p = list(v.values()).count("partiel")
    labels = {k: f"{LBLS[k]} : {VALEURS[v[k]]}" for k in DKEYS}
    aria = f"Empreinte des 12 droits : {n} inscrits dans un texte, {p} partiels"
    if lg:
        return (f'<div class="bigfp" role="img" aria-label="{aria}"><span class="only-light">{V.matrix(v, labels, 40)}</span>'
                f'<span class="only-dark">{V.fiche_dial(v, COURTS)}</span></div>')
    return (f'<span class="fp" role="img" aria-label="{aria}"><span class="only-light">{V.matrix(v, labels, 15)}</span>'
            f'<span class="only-dark">{V.dial(v, 40)}</span></span>')

def legende_etats():
    ex = [("reconnu", "Inscrit dans un texte"), ("partiel", "Partiel"), ("conteste", "Remis en cause"), ("non_etabli", "Aucune source trouvée")]
    li = "".join(f'<span>{V.pic("terres", v, 16)}{e(t)}</span>' for v, t in ex)
    return f'<div class="keyv" aria-hidden="true">{li}</div>'

def dg(n, label=True):
    t = f'<span class="dg dg-{n}" aria-hidden="true">{n}</span>'
    return f'<span class="pill">{t}{e(DEGRES[n][1]) if label else ""}<span class="visually-hidden">Degré {n}</span></span>'

NAV = [("/", "Atlas"), ("/dossiers/", "Dossiers"), ("/comparer/", "Comparer"), ("/cadre/", "Le cadre"), ("/methode/", "Méthode"), ("/a-propos/", "À propos")]

def page(path, title, desc, body, *, og_img="/assets/cards/_accueil.jpg", og_type="website", jsonld=None, extra_head="", scripts=()):
    canon = BASE + path
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == path else ""}>{e(t)}</a>' for h, t in NAV)
    full_title = title if path == "/" else f"{title} — Communautés reconnues"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    js = "".join(f'<script src="{s}" defer></script>' for s in scripts)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="author" content="Cedric Mabilotte">
<meta name="copyright" content="Cedric Mabilotte">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0D1321" media="(prefers-color-scheme: dark)">
<meta property="og:site_name" content="Communautés reconnues">
<meta property="og:locale" content="fr_FR">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(title)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/atom+xml" title="Communautés reconnues — mises à jour" href="/flux.xml">
<link rel="preload" href="/assets/fonts/jost-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<script>try{{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
{extra_head}{ld}
</head>
<body>
{V.sprite()}
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top"><div class="wrap">
<a class="brand" href="/"><span class="mark" aria-hidden="true">{"<i></i>" * 12}</span><span>Communautés reconnues<small>Atlas des autonomies</small></span></a>
<nav class="nav" aria-label="Principale">{nav}</nav>
<button class="theme" type="button" data-theme-toggle aria-label="Changer de thème clair ou sombre">Clair / sombre</button>
</div></header>
<main id="contenu">
{body}
</main>
<footer><div class="wrap">
<div class="h-card"><p><strong>Communautés reconnues</strong> — un atlas des droits d'autonomie inscrits dans le droit des États, pour les peuples et communautés reconnus dans le système des Nations unies.</p>
<p>Créé par <a class="p-name u-url" rel="me" href="{BASE}/">Cedric Mabilotte</a>. Contenus sous licence <a rel="license" href="{LICENCE_URL}">CC BY-NC-SA 4.0</a>.</p></div>
<ul><li><a href="/droit-de-reponse/">Droit de réponse</a></li><li><a href="/ce-que-le-cadre-ne-dit-pas/">Ce que le cadre ne dit pas</a></li><li><a href="/donnees/">Données ouvertes</a></li><li><a href="/flux.xml">Flux des mises à jour</a></li></ul>
<ul><li><a href="{REPO}">Code source</a></li><li><a href="/mentions-legales/">Mentions légales</a></li><li><a href="mailto:{CONTACT}">{CONTACT}</a></li></ul>
</div></footer>
<script src="/assets/theme.js" defer></script>{js}
</body></html>"""

def facts_row(dt_, dd):
    return f"<dt>{e(dt_)}</dt><dd>{dd}</dd>" if dd else ""

def fmt_pop(p):
    if not p or not p.get("valeur"):
        return ""
    v = f'{int(p["valeur"]):,}'.replace(",", " ")
    y = f' ({p["annee"]})' if p.get("annee") else ""
    return f"{v}{y}"

def fmt_num(x):
    if x is None:
        return ""
    if isinstance(x, float) and not x.is_integer():
        return f"{x:,.1f}".replace(",", "\u202f").replace(".", ",")
    return f"{int(x):,}".replace(",", "\u202f")

def chiffres_html(d):
    items = []
    for key, label, unit in (("population", "personnes", None), ("lieux", None, "unite"), ("surface_km2", "km²", None)):
        c = d.get(key) or {}
        if c.get("valeur") is None:
            items.append(f'<div class="ch ch-na"><b>—</b><span>{e(dict(population="population", lieux="lieux", surface_km2="surface")[key])} : aucune source trouvée</span></div>')
            continue
        lab = c.get("unite") if unit else label
        per = c.get("perimetre") or ""
        yr = f" · {c['annee']}" if c.get("annee") else ""
        src = f' · {link(c["source"], "source")}' if c.get("source") else ""
        items.append(f'<div class="ch"><b>{fmt_num(c["valeur"])}</b><span>{e(lab)}{yr}{src}</span>{("<small>" + e(per) + "</small>") if per else ""}</div>')
    return '<div class="chiffres">' + "".join(items) + "</div>"

def link(url, text):
    return f'<a href="{e(url)}" rel="noopener">{e(text)}</a>'

def domain(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)", url or "")
    return m.group(1) if m else ""

DOSSIERS = []
CAS_PAR_UID = {}

def charger_dossiers(uids):
    out = []
    for p in sorted((ROOT / "data" / "dossiers").glob("*.yml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        if d.get("slug") != p.stem:
            fail(f"dossier {p.name} : slug différent du nom de fichier")
        cles = {m["cle"] for m in d.get("mecanismes") or []}
        ids = set()
        for c in d.get("cas") or []:
            if c.get("mecanisme") not in cles:
                fail(f"dossier {p.stem} / {c.get('id')} : mécanisme {c.get('mecanisme')} non déclaré")
            if c.get("atlas_uid") and c["atlas_uid"] not in uids:
                fail(f"dossier {p.stem} / {c.get('id')} : atlas_uid {c['atlas_uid']} inconnu")
            if c.get("id") in ids:
                fail(f"dossier {p.stem} : id de cas en double {c.get('id')}")
            ids.add(c.get("id"))
            if c.get("atlas_uid"):
                CAS_PAR_UID.setdefault(c["atlas_uid"], []).append((d, c))
        out.append(d)
    return out

def dossiers_liens(d):
    cas = CAS_PAR_UID.get(d["uid"])
    if not cas:
        return ""
    li = "".join(f'<li><a href="/dossiers/{dos["slug"]}/#{c["id"]}"><strong>{e(c.get("entite") or c.get("communaute"))}</strong></a> — <span class="muted">{e(dos["titre"])}</span></li>' for dos, c in cas)
    return f'<h2 id="dossiers">Dans les dossiers thématiques</h2><ul class="un">{li}</ul>'

def paras(txt):
    return "".join(f"<p>{e(x.strip())}</p>" for x in re.split(r"\n\s*\n", str(txt or "")) if x.strip())

def dossiers_index_html(dossiers):
    cards = []
    for i, d in enumerate(dossiers, 1):
        meca = " · ".join(e(m["libelle"]) for m in d.get("mecanismes") or [])
        cards.append(f'<li class="dcard"><span class="dnum mono">D{i}</span><div><h2 class="dt"><a href="/dossiers/{d["slug"]}/">{e(d["titre"])}</a></h2>'
                     f'<p>{e(d.get("chapeau", ""))}</p><p class="meta sans">{len(d.get("cas") or [])} cas · {meca}</p></div></li>')
    body = f"""<div class="wrap"><header style="padding:44px 0 8px"><p class="kicker">Dossiers thématiques</p><h1>Des questions précises, communauté par communauté</h1>
<p class="lede prose">Chaque dossier suit une question à travers les communautés de l'atlas et au-delà : les notions qu'elles emploient, les textes qui les fondent, ce qui s'applique réellement.</p></header>
<ol class="dlist">{''.join(cards)}</ol></div>"""
    return page("/dossiers/", "Dossiers thématiques", "Études thématiques : personnalité juridique des entités naturelles, habiter sans posséder.", body)

def dossier_html(d, fiches_par_uid):
    mecas = d.get("mecanismes") or []
    cas = d.get("cas") or []
    counts = {m["cle"]: sum(1 for c in cas if c["mecanisme"] == m["cle"]) for m in mecas}
    legend = "".join(f'<li><a href="#m-{m["cle"]}"><b class="mono">{counts[m["cle"]]}</b> {e(m["libelle"])}</a><p>{e(m.get("definition", ""))}</p></li>' for m in mecas)
    idx = "".join(
        f'<tr><td><a href="#{c["id"]}">{e(c.get("entite") or c["communaute"])}</a></td><td>{e(c["communaute"])}</td><td>{e(", ".join(c.get("etats") or []))}</td>'
        f'<td class="mono">{e(c.get("annee") or "")}</td><td>{e(next(m["libelle"] for m in mecas if m["cle"] == c["mecanisme"]))}</td></tr>' for c in cas)
    concepts = "".join(
        f'<div class="cpt"><dt>{e(k["terme"])} <span class="muted sans">({e(k.get("langue", ""))})</span></dt><dd>{e(k.get("sens", ""))}'
        f'{" " + link(k["source"], "source") if k.get("source") else ""}</dd></div>' for k in d.get("concepts") or [])
    blocs = []
    for m in mecas:
        items = []
        for c in [c for c in cas if c["mecanisme"] == m["cle"]]:
            f = fiches_par_uid.get(c.get("atlas_uid"))
            atl = f'<p class="sans atl">Fiche de l\'atlas : <a href="/c/{f["uid"]}/">{e(f["titre"])}</a></p>' if f else ""
            textes = "".join(f'<li><span class="tag">{e(t.get("nature", ""))}</span>{link(t["source"], t["titre"]) if t.get("source") else e(t.get("titre"))}{" · " + str(t["annee"]) if t.get("annee") else ""}</li>' for t in c.get("textes") or [])
            srcs = "".join(f'<li>{link(x["url"], x.get("titre") or x["url"])}</li>' for x in c.get("sources") or [])
            items.append(f"""<article class="cas" id="{e(c['id'])}"><header><p class="kicker">{e(", ".join(c.get("etats") or []))}{" · " + str(c["annee"]) if c.get("annee") else ""}</p>
<h3>{e(c.get("entite") or c["communaute"])}</h3><p class="sub">{e(c["communaute"])}{(" — <em>" + e(c["concept_local"]) + "</em>") if c.get("concept_local") else ""}</p></header>
{paras(c.get("resume"))}
<dl class="facts">{facts_row("Qui agit", e(c.get("gouvernance", "")))}{facts_row("Application", e(c.get("effectivite", "")))}</dl>
{('<h4>Textes de référence</h4><ul class="un">' + textes + '</ul>') if textes else ''}
{('<details><summary class="sans">Sources</summary><ol class="srcs">' + srcs + '</ol></details>') if srcs else ''}{atl}</article>""")
        blocs.append(f'<section id="m-{m["cle"]}"><h2>{e(m["libelle"])}</h2><p class="prose muted">{e(m.get("definition", ""))}</p>{"".join(items)}</section>')
    lim = "".join(f"<li>{e(x)}</li>" for x in d.get("limites") or [])
    body = f"""<div class="wrap dossier"><header style="padding:44px 0 8px"><p class="kicker">Dossier thématique · {len(cas)} cas</p><h1>{e(d["titre"])}</h1>
<p class="lede prose">{e(d.get("chapeau", ""))}</p></header>
<div class="prose">{paras(d.get("introduction"))}</div>
<h2 id="mecanismes">Les mécanismes</h2><ul class="mlist">{legend}</ul>
<h2 id="index">Les cas</h2><div class="cmpwrap"><table class="plain"><thead><tr><th>Entité ou terre</th><th>Communauté</th><th>État</th><th>Année</th><th>Mécanisme</th></tr></thead><tbody>{idx}</tbody></table></div>
{('<h2 id="concepts">Les notions des communautés</h2><dl class="cpts">' + concepts + '</dl>') if concepts else ''}
{''.join(blocs)}
<h2 id="synthese">Ce que les cas ont en commun</h2><div class="prose">{paras(d.get("synthese"))}</div>
{('<h2 id="limites">Limites du dossier</h2><ul class="prose">' + lim + '</ul>') if lim else ''}
<p class="warn">Information juridique générale, à la date de mise à jour. Une erreur ? <a href="/droit-de-reponse/">Droit de réponse</a>.</p></div>"""
    jl = {"@context": "https://schema.org", "@type": "Article", "headline": d["titre"], "description": d.get("chapeau", ""), "inLanguage": "fr",
          "author": {"@type": "Person", "name": "Cedric Mabilotte"}, "license": LICENCE_URL, "url": f"{BASE}/dossiers/{d['slug']}/"}
    return page(f"/dossiers/{d['slug']}/", d["titre"], d.get("chapeau", ""), body, og_img=f"/assets/cards/_dossier-{d['slug']}.jpg", og_type="article", jsonld=jl)

def fiche_html(d):
    x, y = project(*d["coord"])
    px, py = 100 * x / MAP["W"], 100 * y / MAP["H"]
    kicker = f'{REGIONS[d["region"]]} · {TYPES[d["type"]]}'
    sub = d["nom"] if d["titre"] != d["nom"] else (d.get("territoire") or "")
    ladder = "".join(f'<span class="dg-{i}{" on" if i == d["degre"] else ""}"{" aria-hidden=true" if i != d["degre"] else ""}>{i}</span>' for i in range(6))
    types2 = ", ".join(TYPES.get(t, t) for t in (d.get("types_secondaires") or []))
    facts = "".join([
        facts_row("Territoire", e(d.get("territoire") or "")),
        facts_row("État" + ("s" if len(d["etats"]) > 1 else ""), e(", ".join(d["etats"]))),
        facts_row("Base", e(BASES[d["base"]])),
        facts_row("Aussi", e(types2)),
        facts_row("Reconnaissance", e(NIVEAUX[d["niveau_reconnaissance"]])),
        facts_row("Application", e(EFFECT[d["effectivite"]["valeur"]])),
        facts_row("Mise à jour", f'<time class="dt-updated" datetime="{d["date_maj"]}">{d["date_maj"]}</time>'),
    ])
    items = []
    for k, lbl, q in DROITS:
        r = d["droits"][k]
        src = f'<p class="src">{link(r["source"], "Source : " + domain(r["source"]))}</p>' if r.get("source") else ""
        note = f"<p>{e(r['note'])}</p>" if r.get("note") else f'<p class="muted">{e(q)}</p>'
        items.append(f'<li id="d-{k}"><span class="ico"><span class="only-light">{V.pic(k, r["valeur"], 32)}</span><span class="only-dark">{V.dial(vals_of(d), 36, only=DKEYS.index(k))}</span></span><div><h3>{e(lbl)}</h3><p class="val">{e(VALEURS[r["valeur"]])}</p>{note}{src}</div></li>')
    reg = "".join(
        f'<li><span class="tag">Système régional</span><strong>{e(MECA_REG[r["mecanisme"]])}</strong>{" · " + str(r["annee"]) if r.get("annee") else ""}<br>{e(r.get("detail", ""))}'
        f'{" — " + link(r["source"], domain(r["source"])) if r.get("source") else ""}</li>'
        for r in d.get("reconnaissance_regionale") or [])
    rec_vide = "" if (d.get("reconnaissance_onu") or d.get("reconnaissance_regionale")) else '<li class="muted">Reconnaissance par l\'État seulement : voir les textes nationaux.</li>'
    un = "".join(
        f'<li><span class="tag{" t-contraignant" if MECA[r["mecanisme"]][1] == "contraignant" else ""}">{e(FORCE_TXT[MECA[r["mecanisme"]][1]])}</span>'
        f'<strong>{e(MECA[r["mecanisme"]][0])}</strong>{" · " + str(r["annee"]) if r.get("annee") else ""}<br>{e(r.get("detail", ""))}'
        f'{" — " + link(r["source"], domain(r["source"])) if r.get("source") else ""}</li>'
        for r in d.get("reconnaissance_onu") or [])
    nat = "".join(
        f'<li><span class="tag">{e(NATURES.get(b.get("nature"), b.get("nature", "")))}</span><strong>{e(b.get("instrument", ""))}</strong>'
        f'{" · " + str(b["annee"]) if b.get("annee") else ""}{" — " + link(b["source"], domain(b["source"])) if b.get("source") else ""}</li>'
        for b in d.get("base_nationale") or [])
    chrono = "".join(f'<li><b>{e(c.get("annee"))}</b><span>{e(c.get("evenement"))}</span></li>' for c in sorted(d.get("chronologie") or [], key=lambda c: str(c.get("annee"))))
    fia = d.get("fiabilite") or {}
    ver = "".join(f"<li>{e(s)}</li>" for s in fia.get("verifie") or [])
    nc = "".join(f"<li>{e(s)}</li>" for s in fia.get("non_confirme") or [])
    srcs = "".join(f'<li>{link(s["url"], s.get("titre") or s["url"])}</li>' for s in d["sources"])
    eff = d["effectivite"]
    url = f'{BASE}/c/{d["uid"]}/'
    txt = f'{d["titre"]} — {DEGRES[d["degre"]][1].lower()} (degré {d["degre"]}/5)'
    share = f"""<div class="share" data-share data-url="{e(url)}" data-text="{e(txt)}"><span class="lbl">Partager</span>
<button type="button" data-native hidden>Partager…</button>
<button type="button" data-copy>Copier le lien</button>
<a href="https://bsky.app/intent/compose?text={quote(txt + ' ' + url)}" rel="noopener">Bluesky</a>
<a href="#" data-mastodon>Mastodon</a>
<a href="https://t.me/share/url?url={quote(url)}&amp;text={quote(txt)}" rel="noopener">Telegram</a>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}" rel="noopener">LinkedIn</a>
<a href="/assets/cards/{d['uid']}-portrait.jpg" download>Image portrait</a>
<span class="visually-hidden" aria-live="polite" data-status></span></div>"""
    body = f"""<article class="h-entry">
<div class="wrap"><header class="fhead">
<div><p class="kicker">{e(kicker)}</p>
<h1 class="p-name">{e(d['titre'])}</h1>
<p class="sub">{e(sub)}</p>
<p class="lede p-summary e-content">{e(d['resume'])}</p>
{chiffres_html(d)}
{share}</div>
<div><figure class="locator"><img src="/assets/land.svg" alt="" width="1000" height="487"><span class="dot" style="left:{px:.2f}%;top:{py:.2f}%"></span><figcaption class="visually-hidden">Localisation approximative : {e(d.get('territoire') or d['nom'])}</figcaption></figure>
<p class="kicker" style="margin-top:18px">Degré d'autonomie calculé</p>
<div class="ladder" role="img" aria-label="Degré {d['degre']} sur 5 : {e(DEGRES[d['degre']][1])}">{ladder}</div>
<p style="margin:4px 0 0"><strong>{e(DEGRES[d['degre']][1])}</strong> — <span class="muted">{e(DEGRES[d['degre']][2])}</span> <a href="/cadre/#degre">Règle de calcul</a></p>
<dl class="facts">{facts}</dl></div>
</header>

<h2 id="droits">Les douze droits</h2>
{legende_etats()}
{fp(d, lg=True)}
<ul class="grid12" style="margin-top:20px">{''.join(items)}</ul>

<div class="two">
<section><h2 id="onu">Reconnaissance officielle</h2><ul class="un">{un}{reg}{rec_vide}</ul></section>
<section><h2 id="textes">Textes nationaux</h2><ul class="un">{nat or '<li class="muted">Aucune entrée.</li>'}</ul></section>
</div>

{dossiers_liens(d)}
<h2 id="application">Ce qui s'applique réellement</h2>
<div class="box prose"><p class="kicker" style="margin:0 0 6px">{e(EFFECT[eff['valeur']])}</p><p style="margin:0">{e(eff.get('note', ''))}</p>{('<p class="src sans" style="font-size:.78rem;margin:8px 0 0">' + link(eff['source'], 'Source : ' + domain(eff['source'])) + '</p>') if eff.get('source') else ''}</div>

{('<h2 id="chronologie">Chronologie</h2><ol class="tl">' + chrono + '</ol>') if chrono else ''}

<div class="two">
<section><h2 id="fiabilite">Fiabilité</h2>
{('<h3>Vérifié sur la source</h3><ul>' + ver + '</ul>') if ver else ''}
{('<h3>Non confirmé</h3><ul>' + nc + '</ul>') if nc else ''}</section>
<section><h2 id="sources">Sources</h2><ol class="srcs">{srcs}</ol></section>
</div>
<p class="warn">Information juridique générale, à la date indiquée. Ce n'est pas un conseil et cela ne qualifie ni un peuple ni une personne. Une erreur ? <a href="/droit-de-reponse/">Droit de réponse</a>.</p>
</div></article>"""
    jl = {"@context": "https://schema.org", "@type": "Article", "headline": d["titre"], "alternativeHeadline": d["nom"],
          "description": d["resume"], "inLanguage": "fr", "dateModified": d["date_maj"], "url": url,
          "image": f"{BASE}/assets/cards/{d['uid']}.jpg",
          "author": {"@type": "Person", "name": "Cedric Mabilotte"},
          "copyrightHolder": {"@type": "Person", "name": "Cedric Mabilotte"}, "license": LICENCE_URL,
          "isPartOf": {"@type": "WebSite", "name": "Communautés reconnues", "url": BASE + "/"},
          "about": {"@type": "Place", "name": d.get("territoire") or d["nom"], "geo": {"@type": "GeoCoordinates", "latitude": d["coord"][0], "longitude": d["coord"][1]}}}
    desc = f'{d["nom"]} ({", ".join(d["etats"])}) : {DEGRES[d["degre"]][1].lower()}. Les douze droits, les textes, la reconnaissance à l\'ONU et ce qui s\'applique réellement.'
    return page(f'/c/{d["uid"]}/', d["titre"], desc, body, og_img=f'/assets/cards/{d["uid"]}.jpg', og_type="article", jsonld=jl, scripts=("/assets/share.js",))

def howto(fiches):
    n = len(fiches)
    counts = {k: tuple(sum(1 for f in fiches if f["droits"][k]["valeur"] == v) for v in ("reconnu", "partiel", "conteste")) for k in DKEYS}
    fams = []
    for fk, nom, ks in V.FAM:
        li = "".join(f'<li>{V.pic(k, "reconnu", 28)}<span>{e(COURTS[k])}<small>{counts[k][0]} inscrits · {counts[k][1]} partiels</small></span></li>' for k in ks)
        fams.append(f'<div class="fam" style="--c:var(--f-{fk})"><h3>{e(nom)}</h3><ul>{li}</ul></div>')
    light = f'<div class="howto only-light"><h2>Comment lire : chaque droit a son signe</h2><div class="fams">{"".join(fams)}</div></div>'
    dark = f'<div class="only-dark">{V.big_dial(counts, n, COURTS)}</div>'
    return light + dark

def index_html(fiches):
    etats = sorted({s for f in fiches for s in f["etats"]})
    counts = [sum(1 for f in fiches if f["degre"] == i) for i in range(6)]
    degbar = "".join(
        f'<div class="seg" style="--n:{max(c, 2)}"><button type="button" style="--b:var(--d{i});--c:var(--t{i})" data-deg="{i}" aria-pressed="false" '
        f'aria-label="Degré {i}, {e(DEGRES[i][1])} : {c} fiche{"s" if c > 1 else ""}. Filtrer.">{c}</button><span aria-hidden="true" title="{e(DEGRES[i][1])}">{i} · {COURT[i]}</span></div>' for i, c in enumerate(counts))
    legend = "".join(f"<span>{i} · {e(t)}</span>" for i, t, _ in DEGRES)
    pts = []
    ordre = sorted(fiches, key=lambda f: -f["coord"][0])
    pos = V.dorling([project(*f["coord"]) for f in ordre], 7.2, gap=1.0, iters=300, pull=.03)
    for f, (x, y) in zip(ordre, pos):
        dd = f["degre"]
        pts.append(f'<a class="pt" href="/c/{f["uid"]}/" data-uid="{f["uid"]}" aria-label="{e(f["titre"])}, degré {dd}">'
                   f'<circle class="halo" cx="{x:.1f}" cy="{y:.1f}" r="10.5"/><circle class="c" cx="{x:.1f}" cy="{y:.1f}" r="7.2" style="fill:var(--d{dd})"/>'
                   f'<text x="{x:.1f}" y="{y + .4:.1f}" style="fill:var(--t{dd})">{dd}</text></a>')
    svg = (f'<svg viewBox="0 0 {MAP["W"]} {MAP["H"]}" role="group" aria-label="Carte du monde : un cercle par communauté, placé près de son territoire, avec son degré d\'autonomie">'
           f'<path class="grat" d="{MAP["grat30"]}"/><path class="land" d="{MAP["land"]}"/><path class="borders" d="{MAP["borders"]}"/>'
           f'<path class="sphere" d="{MAP["sphere"]}"/>{"".join(pts)}</svg>')
    rows = []
    for f in fiches:
        vals = " ".join(f'{k}:{f["droits"][k]["valeur"]}' for k in DKEYS)
        search = " ".join([f["nom"], f.get("endonyme") or "", f.get("territoire") or "", " ".join(f["etats"])]).lower()
        sub = f' <small>{e(f["nom"])}</small>' if f["titre"] != f["nom"] else ""
        rows.append(
            f'<li class="row" data-uid="{f["uid"]}" data-region="{f["region"]}" data-type="{f["type"]}" data-deg="{f["degre"]}" '
            f'data-eff="{f["effectivite"]["valeur"]}" data-niv="{f["niveau_reconnaissance"]}" data-base="{f["base"]}" data-d="{e(vals)}" data-q="{e(search)}">'
            f'<div><a class="n" href="/c/{f["uid"]}/">{e(f["titre"])}{sub}</a>'
            f'<div class="meta">{e(", ".join(f["etats"]))} · {e(TYPES[f["type"]])} · {e(EFFECT[f["effectivite"]["valeur"]])}</div></div>'
            f'<div class="right">{fp(f)}{dg(f["degre"], label=False)}</div></li>')
    opt = lambda dct: "".join(f'<option value="{k}">{e(v)}</option>' for k, v in dct.items())
    body = f"""<div class="wrap">
<section class="hero">
<div><p class="kicker">Atlas · {len(fiches)} communautés · mis à jour le {max(f['date_maj'] for f in fiches)}</p>
<h1>Qui décide ici&#8239;?</h1>
<p class="lede">Certains peuples et communautés ont obtenu, dans le droit de l'État où ils vivent, le droit de décider eux-mêmes d'une part de leurs affaires&#8239;: leurs terres, leur langue, leur justice, parfois leur avenir politique. Cet atlas les recense texte par texte, à partir de sources publiques.</p>
<ul class="figures"><li><b>{len(fiches)}</b><span>communautés</span></li><li><b>{len(etats)}</b><span>États</span></li><li><b>12</b><span>droits examinés</span></li><li><b>{len(DOSSIERS)}</b><span><a href="/dossiers/">dossiers thématiques</a></span></li></ul></div>
<div>{howto(fiches)}
<p class="kicker" style="margin-top:28px">Répartition par degré d'autonomie — cliquer pour filtrer</p>
<div class="degbar" data-degbar>{degbar}</div></div>
</section>
<figure class="map" data-map>{svg}<div class="tip" data-tip></div>
<figcaption class="maplegend"><span class="only-light">Un cercle par communauté, déplacé au plus près de son territoire pour rester lisible ; le chiffre est le degré d'autonomie. Sans frontières d'États.</span><span class="only-dark">Un point par communauté ; plus le point est clair, plus le degré d'autonomie calculé est élevé. Fond : côtes Natural Earth 1:110 m, frontières d'États volontairement omises.</span><span>Projection Equal Earth</span></figcaption></figure>

<form class="filters" role="search" aria-label="Filtrer l'atlas" onsubmit="return false">
<label>Rechercher<input type="search" name="q" placeholder="Nom, territoire, État…" autocomplete="off"></label>
<label>Région<select name="region"><option value="">Toutes</option>{opt(REGIONS)}</select></label>
<label>Type<select name="type"><option value="">Tous</option>{opt(TYPES)}</select></label>
<label>Droit inscrit<select name="droit"><option value="">Aucun filtre</option>{''.join(f'<option value="{k}">{e(l)}</option>' for k, l, _ in DROITS)}</select></label>
<label>Reconnaissance<select name="niv"><option value="">Tous niveaux</option>{opt(NIVEAUX)}</select></label>
<label>Application<select name="eff"><option value="">Toutes</option>{opt(EFFECT)}</select></label>
</form>
<div class="fbar"><span aria-live="polite" data-count>{len(fiches)} fiches</span><span><button type="button" data-reset>Tout afficher</button> · <a href="/comparer/">Tableau comparatif</a></span></div>
{legende_etats()}
<ul class="rows" data-rows>{''.join(rows)}</ul>
<p class="empty" data-empty hidden>Aucune fiche ne correspond. <button type="button" data-reset class="sans">Tout afficher</button></p>
<p class="warn">Le degré décrit ce que disent des textes à une date donnée. Il ne classe pas les peuples. <a href="/ce-que-le-cadre-ne-dit-pas/">Ce que le cadre ne dit pas</a>.</p>
</div>"""
    jl = {"@context": "https://schema.org", "@type": "WebSite", "name": "Communautés reconnues", "url": BASE + "/", "inLanguage": "fr",
          "description": "Atlas des droits d'autonomie inscrits dans le droit national pour les peuples et communautés officiellement reconnus.",
          "author": {"@type": "Person", "name": "Cedric Mabilotte"}, "copyrightHolder": {"@type": "Person", "name": "Cedric Mabilotte"}, "license": LICENCE_URL}
    return page("/", "Communautés reconnues — qui décide ici ?", "Atlas public des peuples et communautés officiellement reconnus qui disposent de droits d'autonomie dans le droit de leur État : douze droits examinés, textes et sources.",
                body, jsonld=jl, scripts=("/assets/app.js",))

def comparer_html(fiches):
    head = "".join(f'<th scope="col"><button type="button" data-col="{i}">{e(l)}</button></th>' for i, (k, l, _) in enumerate(DROITS))
    rows = []
    for f in fiches:
        cells = "".join(f'<td class="c" data-v="{VRANK[f["droits"][k]["valeur"]]}"><a href="/c/{f["uid"]}/#d-{k}" title="{e(l)} : {e(VALEURS[f["droits"][k]["valeur"]])}">{V.pic(k, f["droits"][k]["valeur"], 20)}<span class="visually-hidden">{e(VALEURS[f["droits"][k]["valeur"]])}</span></a></td>' for k, l, _ in DROITS)
        rows.append(f'<tr data-region="{f["region"]}"><th scope="row" class="nm"><a href="/c/{f["uid"]}/">{e(f["titre"])}</a></th>{cells}<td class="d" data-v="{f["degre"]}">{dg(f["degre"], label=False)}</td></tr>')
    body = f"""<div class="wrap">
<header style="padding:44px 0 8px"><p class="kicker">Tableau comparatif</p><h1>Douze droits, {len(fiches)} communautés</h1>
<p class="lede prose">Chaque ligne est une fiche, chaque colonne un droit. Cliquer sur l'intitulé d'une colonne trie les communautés selon ce droit ; cliquer sur une case ouvre le droit dans la fiche.</p></header>
{legende_etats()}
<div class="cmpwrap"><table class="cmp" data-cmp><caption class="visually-hidden">Valeur de chacun des douze droits, par communauté</caption>
<thead><tr><th scope="col" class="nm"><button type="button" data-col="name" style="writing-mode:horizontal-tb;transform:none">Communauté</button></th>{head}<th scope="col"><button type="button" data-col="12">Degré</button></th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
</div>"""
    return page("/comparer/", "Tableau comparatif des douze droits", "Les douze droits d'autonomie, côte à côte, pour toutes les communautés de l'atlas.", body, og_img="/assets/cards/_comparer.jpg", scripts=("/assets/compare.js",))

def cadre_html(fiches):
    cnt = lambda key, val: sum(1 for f in fiches if f[key] == val)
    types = "".join(f"<tr><td>{e(v)}</td><td class='mono'>{cnt('type', k)}</td></tr>" for k, v in TYPES.items())
    droits = "".join(f"<tr><td><strong>{e(l)}</strong></td><td>{e(q)}</td></tr>" for k, l, q in DROITS)
    vals = "".join(f"<tr><td><i class='v-{k}' style='display:inline-block;width:14px;height:14px;border:1px solid var(--s-ne);vertical-align:-2px;margin-right:8px'></i>{e(v)}</td><td>{e(VD[k])}</td></tr>" for k, v in VALEURS.items())
    degres = "".join(f"<tr><td>{dg(i, label=False)}</td><td><strong>{e(t)}</strong></td><td>{e(x)}</td><td class='mono'>{cnt('degre', i)}</td></tr>" for i, t, x in DEGRES)
    meca = "".join(f"<tr><td>{e(v[0])}</td><td>{e(FORCE_TXT[v[1]])}</td></tr>" for k, v in MECA.items())
    body = f"""<div class="wrap"><header style="padding:44px 0 8px"><p class="kicker">Le cadre</p><h1>Comment une communauté est décrite</h1>
<p class="lede prose">Chaque fiche répond aux mêmes questions, dans le même ordre. Le cadre est publié pour qu'on puisse le discuter.</p></header>
<div class="prose">
<h2 id="entree">Deux conditions pour entrer</h2>
<p>La communauté est officiellement reconnue, à au moins un de ces niveaux&#8239;: par les Nations unies (liste des territoires non autonomes, mention nommée par un organe de l'ONU, accord conclu sous son égide, Convention 169 de l'OIT, Déclaration de 2007 appliquée par l'État)&#8239;; par un système régional (Cour ou Commission africaine, Cour ou Commission interaméricaine, Conseil de l'Europe)&#8239;; ou par son État seul, qui la nomme dans une constitution, une loi, une liste officielle, ou lui délimite un territoire ou une institution.</p>
<p>Et au moins un texte de cet État lui accorde, en tant que groupe, un droit de la grille ci-dessous. Une autonomie administrative sans groupe désigné n'entre pas. Un État souverain n'entre pas. Un groupe reconnu sans aucun droit collectif n'entre pas&#8239;: c'est le cas des Aïnous du Japon.</p>
<p>Chaque fiche indique le niveau de reconnaissance le plus élevé&#8239;: {cnt('niveau_reconnaissance','onu')} communautés par les Nations unies, {cnt('niveau_reconnaissance','regional')} par un système régional, {cnt('niveau_reconnaissance','national')} par leur État seulement.</p>
</div>
<h2 id="chiffres">Trois chiffres, avec leur périmètre</h2>
<p class="prose">Chaque fiche donne la population, le nombre de lieux concernés (communes, réserves, villages, terres titrées, conseils…) et la surface du territoire. Chaque chiffre porte son année, sa source et son périmètre&#8239;: qui ou quoi est compté. Un chiffre sans source n'est pas affiché. Deux chiffres ne se comparent qu'après lecture de leurs périmètres&#8239;: la population d'une région autonome n'est pas celle d'un peuple.</p>
<h2 id="types">Sept types de communautés</h2>
<p class="prose">Un type principal par fiche, d'autres possibles. Le type reprend le vocabulaire de l'instrument qui fonde la reconnaissance&#8239;: un même peuple peut relever de plusieurs.</p>
<table class="plain"><thead><tr><th>Type</th><th>Fiches</th></tr></thead><tbody>{types}</tbody></table>
<h2 id="onu">La reconnaissance aux Nations unies n'a pas toujours la même force</h2>
<table class="plain"><thead><tr><th>Mécanisme</th><th>Force</th></tr></thead><tbody>{meca}</tbody></table>
<h2 id="grille">Douze droits</h2>
<table class="plain"><thead><tr><th>Droit</th><th>Question posée</th></tr></thead><tbody>{droits}</tbody></table>
<h3>Cinq valeurs</h3>
<table class="plain"><tbody>{vals}</tbody></table>
<h2 id="degre">Le degré d'autonomie se calcule</h2>
<p class="prose">Personne ne fixe le degré à la main. Le programme de génération du site l'établit à partir des douze valeurs, selon la règle suivante, lue de haut en bas&#8239;: la première condition remplie donne le degré. Seules les valeurs «&#8239;inscrit dans un texte&#8239;» et «&#8239;partiel&#8239;» comptent.</p>
<table class="plain"><thead><tr><th></th><th>Degré</th><th>Condition</th><th>Fiches</th></tr></thead><tbody>{degres}</tbody></table>
<p class="prose muted">Le degré mesure ce que disent les textes. Ce qui se passe réellement est noté à part, dans la rubrique «&#8239;Ce qui s'applique réellement&#8239;» de chaque fiche, avec sa source.</p>
<h2 id="base">Territoire ou personnes</h2>
<p class="prose">Certaines autonomies s'attachent à un territoire, d'autres aux personnes, où qu'elles vivent&#8239;: les parlements sámi sont élus sur une liste électorale propre, les communautés nationales italienne et hongroise de Slovénie se gouvernent elles-mêmes sur une zone de peuplement. La fiche l'indique sous «&#8239;Base&#8239;», indépendamment du degré.</p>
</div>"""
    return page("/cadre/", "Le cadre de description", "Les deux conditions d'entrée, les sept types de communautés, les douze droits et la règle de calcul du degré d'autonomie.", body)

VD = {"reconnu": "Le droit figure dans un texte en vigueur (constitution, loi, statut, accord) et il est appliqué par l'État.",
      "partiel": "Le droit figure dans un texte, avec des limites fortes : domaines restreints, tutelle de l'État, portée réduite.",
      "conteste": "Le texte existe mais il est suspendu, abrogé en partie, attaqué en justice ou pas mis en œuvre.",
      "non_etabli": "Aucune source trouvée. Cela ne veut pas dire que le droit n'existe pas.",
      "non_applicable": "La question ne se pose pas pour cette communauté."}

def md_page(slug, fiches):
    raw = (PAGES / f"{slug}.md").read_text(encoding="utf-8")
    fm, _, txt = raw.partition("\n---\n")
    meta = yaml.safe_load(fm.replace("---\n", "", 1))
    body = md(txt.replace("{{N}}", str(len(fiches))).replace("{{CONTACT}}", CONTACT).replace("{{REPO}}", REPO))
    content = f"""<div class="wrap"><header style="padding:44px 0 8px"><p class="kicker">{e(meta['kicker'])}</p><h1>{e(meta['titre'])}</h1></header>
<div class="prose">{body}</div></div>"""
    return page(f"/{slug}/", meta["titre"], meta["description"], content)

def inline(t):
    t = e(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    return t

def md(src):
    out, para, lst = [], [], None
    def flush():
        nonlocal para, lst
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>"); lst = None
    for line in src.splitlines():
        s = line.strip()
        if not s:
            flush(); continue
        m = re.match(r"^(#{2,3})\s+(.*?)(?:\s+\{#([\w-]+)\})?$", s)
        if m:
            flush(); lvl = len(m.group(1)); ida = f' id="{m.group(3)}"' if m.group(3) else ""
            out.append(f"<h{lvl}{ida}>{inline(m.group(2))}</h{lvl}>"); continue
        if s.startswith("- "):
            if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
            lst = (lst or []) + [s[2:]]; continue
        if s.startswith("> "):
            flush(); out.append(f'<p class="warn">{inline(s[2:])}</p>'); continue
        if lst is not None:
            lst[-1] += " " + s; continue
        para.append(s)
    flush()
    return "\n".join(out)

# ---------------------------------------------------------------- sorties annexes
def feed(fiches):
    items = sorted(fiches, key=lambda f: (f["date_maj"], f["uid"]), reverse=True)
    ent = "".join(f"""<entry><title>{e(f['titre'])} — {e(f['nom'])}</title><link href="{BASE}/c/{f['uid']}/"/><id>{BASE}/c/{f['uid']}/</id><updated>{f['date_maj']}T00:00:00Z</updated><summary>{e(f['resume'])}</summary></entry>""" for f in items)
    upd = items[0]["date_maj"]
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="fr"><title>Communautés reconnues</title><link href="{BASE}/"/><link rel="self" href="{BASE}/flux.xml"/><id>{BASE}/</id><updated>{upd}T00:00:00Z</updated><author><name>Cedric Mabilotte</name></author><rights>CC BY-NC-SA 4.0 — Cedric Mabilotte</rights>{ent}</feed>"""

def sitemap(fiches, pages):
    last = max(f["date_maj"] for f in fiches)
    urls = [(p, last) for p in pages] + [(f"/c/{f['uid']}/", f["date_maj"]) for f in fiches]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls) + "</urlset>"

def v(f, k):
    x = f.get(k) or {}
    return "" if x.get("valeur") is None else x["valeur"]

def export_csv(fiches):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["uid", "nom", "endonyme", "territoire", "etats", "region", "type", "base", "latitude", "longitude", "population", "population_perimetre", "lieux", "lieux_unite", "surface_km2", "degre", "effectivite", "niveau_reconnaissance", "force_onu", "date_maj"] + DKEYS)
    for f in fiches:
        w.writerow([f["uid"], f["nom"], f.get("endonyme") or "", f.get("territoire") or "", "; ".join(f["etats"]), f["region"], f["type"], f["base"],
                    f["coord"][0], f["coord"][1], v(f, "population"), (f.get("population") or {}).get("perimetre", ""), v(f, "lieux"), (f.get("lieux") or {}).get("unite", ""), v(f, "surface_km2"),
                    f["degre"], f["effectivite"]["valeur"], f["niveau_reconnaissance"], f["force_onu"] or "", f["date_maj"]] + [f["droits"][k]["valeur"] for k in DKEYS])
    return buf.getvalue()

def page404():
    return page("/404.html", "Page introuvable", "Cette adresse ne correspond à aucune page.",
                '<div class="wrap" style="padding:64px 0"><p class="kicker">Erreur 404</p><h1>Cette page n\'existe pas</h1><p class="prose">L\'adresse a pu changer. <a href="/">Retour à l’atlas</a>.</p></div>')

# ---------------------------------------------------------------- garde-fous
def verifier_liens(out):
    bad = []
    ids = {}
    for p in out.rglob("*.html"):
        t = p.read_text(encoding="utf-8")
        ids[p] = set(re.findall(r'id="([^"]+)"', t))
    for p in out.rglob("*.html"):
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="(/[^"#?]*)(#[^"]*)?"', t):
            u, anc = m.group(1), m.group(2)
            tgt = out / u.lstrip("/")
            if u.endswith("/"):
                tgt = tgt / "index.html"
            if not tgt.exists():
                bad.append(f"{p.relative_to(out)} → {u}")
            elif anc and tgt.suffix == ".html" and anc[1:] not in ids.get(tgt, set()):
                bad.append(f"{p.relative_to(out)} → {u}{anc} (ancre)")
    if bad:
        fail("liens internes cassés :\n  " + "\n  ".join(sorted(set(bad))[:40]))

MOTS_INTERDITS = ["généré par", "genere par", "intelligence artificielle", "chatgpt", "openai", "enriched_by", "raw_response"]
_extra = ROOT / "_interne" / "mots-interdits.txt"   # liste locale complémentaire, non versionnée
if _extra.exists():
    MOTS_INTERDITS += [w.strip().lower() for w in _extra.read_text(encoding="utf-8").splitlines() if w.strip()]

def verifier_provenance(out):
    for p in list(out.rglob("*.html")) + list(out.rglob("*.json")) + list(out.rglob("*.csv")):
        t = p.read_text(encoding="utf-8").lower()
        for w in MOTS_INTERDITS:
            if w in t:
                fail(f"{p.relative_to(out)} contient « {w} »")

# ---------------------------------------------------------------- build
def main():
    fiches = charger()
    DOSSIERS[:] = charger_dossiers({f["uid"] for f in fiches})
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets", ignore=shutil.ignore_patterns("map.json", "cards-src"))
    (OUT / "assets" / "land.svg").write_text(land_svg_file(), encoding="utf-8")
    def w(rel, txt):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
    w("index.html", index_html(fiches))
    w("comparer/index.html", comparer_html(fiches))
    w("cadre/index.html", cadre_html(fiches))
    pages = ["/", "/comparer/", "/cadre/", "/dossiers/"]
    w("dossiers/index.html", dossiers_index_html(DOSSIERS))
    fpu = {f["uid"]: f for f in fiches}
    for d in DOSSIERS:
        w(f"dossiers/{d['slug']}/index.html", dossier_html(d, fpu)); pages.append(f"/dossiers/{d['slug']}/")
    for p in sorted(PAGES.glob("*.md")):
        w(f"{p.stem}/index.html", md_page(p.stem, fiches)); pages.append(f"/{p.stem}/")
    for f in fiches:
        w(f"c/{f['uid']}/index.html", fiche_html(f))
    w("404.html", page404())
    pub = [{k: f.get(k) for k in PUBLIC_KEYS + ["degre", "force_onu", "niveau_reconnaissance", "date_maj"]} for f in fiches]
    w("donnees/communautes.json", json.dumps({"licence": "CC BY-NC-SA 4.0", "auteur": "Cedric Mabilotte",
                                              "genere_le": TODAY, "cadre": BASE + "/cadre/", "fiches": pub}, ensure_ascii=False, indent=1))
    w("donnees/communautes.csv", export_csv(fiches))
    w("flux.xml", feed(fiches))
    w("sitemap.xml", sitemap(fiches, pages))
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    w(".nojekyll", "")
    verifier_liens(OUT)
    verifier_provenance(OUT)
    missing = [f["uid"] for f in fiches if not (OUT / "assets" / "cards" / f"{f['uid']}.jpg").exists()]
    if missing:
        print(f"attention : {len(missing)} vignette(s) de partage manquante(s) — lancer scripts/social_cards.py", file=sys.stderr)
    print(f"ok : {len(fiches)} fiches, {len(pages)} pages → {OUT}")

if __name__ == "__main__":
    main()
