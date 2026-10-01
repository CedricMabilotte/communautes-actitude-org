# Cadre de catégorisation — communautes.actitude.org

Version 2 — 2026-10-01 : le critère d'entrée s'ouvre aux reconnaissances nationales et régionales ; ajout des chiffres (lieux, villages, surface, population). Version 1.1 — 2026-09-30 (libellés affichés, base territoriale/personnelle, force de la reconnaissance ONU, règle du degré). Ce cadre fixe ce qu'on range, comment on le range, et ce qu'on refuse de conclure.

## 0. Critère d'entrée (périmètre) — v2

Une communauté entre dans l'atlas si les DEUX conditions sont remplies :

1. **Reconnaissance officielle**, à au moins un de ces niveaux :
   - **ONU** : un mécanisme de la liste §2 la vise nommément, ou vise la catégorie à laquelle son État l'a rattachée ;
   - **régional** : Commission ou Cour africaine, Cour ou Commission interaméricaine, Conseil de l'Europe (Convention-cadre pour la protection des minorités nationales, Charte des langues), Union européenne ;
   - **national** : l'État la reconnaît nommément (constitution, loi, décret, liste officielle comme les « Scheduled Tribes » en Inde, registre des peuples autochtones) ou lui délimite un territoire, une institution ou un statut.
2. **Droits spécifiques d'autogestion ou d'autodétermination** attribués à la communauté en tant que collectif par un instrument juridique national ou infranational en vigueur : au moins un droit de la grille §3 au niveau « reconnu » ou « partiel ».

Le niveau de reconnaissance le plus haut est calculé et affiché (`niveau_reconnaissance` : onu / regional / national). Les États non membres de l'ONU (Taïwan) entrent par le niveau national.

Exclus : autonomies purement administratives sans sujet collectif, mouvements sans instrument juridique, États souverains, groupes reconnus sans aucun droit collectif (ex. Aïnous du Japon, loi de 2019).

Cas limites assumés : un territoire non autonome inscrit à la liste de l'ONU entre même si le droit de la puissance administrante est pauvre ; l'effectivité est alors notée à part.

## 0 bis. Chiffres

`population` (avec `perimetre` : qui est compté), `lieux` (nombre et unité : communes, réserves, resguardos, terres indigènes, conseils…), `villages` (nombre de villages ou de localités habitées dans la zone concernée, avec `perimetre`), `surface_km2` (avec `perimetre`). Chaque chiffre porte son année et sa source ; sans source, `valeur: null`. Les chiffres ne se comparent pas entre fiches sans lire le périmètre.

## 1. Types de communautés (`type`) — un seul type principal, `types_secondaires` possibles

| clé | libellé | fondement |
|---|---|---|
| `peuple_autochtone` | Peuple autochtone | DNUDPA 2007, Convention OIT 169 |
| `peuple_tribal` | Peuple tribal ou coutumier | Convention OIT 169 art. 1(a) |
| `minorite_nationale` | Minorité nationale, ethnique, linguistique ou religieuse | Pacte DCP art. 27, Déclaration ONU 1992 |
| `communaute_afrodescendante` | Communauté afrodescendante traditionnelle | Décennie internationale des personnes d'ascendance africaine, OIT 169 (peuple tribal) |
| `peuple_territoire_non_autonome` | Peuple d'un territoire non autonome | Charte art. 73, résolution 1514 (XV), liste du Comité spécial de la décolonisation |
| `peuple_libre_association` | Peuple d'un État en libre association | Résolution 1541 (XV) principe VII |
| `collectivite_insulaire_ou_regionale` | Population d'une région autonome à statut international | règlement international (SDN, traité) ou suivi onusien |

## 2. Reconnaissance dans le système ONU (`reconnaissance_onu[].mecanisme`)

| clé | libellé |
|---|---|
| `liste_tna` | Inscrit sur la liste des territoires non autonomes (C-24) |
| `dnudpa` | État ayant voté/rallié la DNUDPA et reconnaissant ce peuple comme autochtone |
| `oit_169` | Convention OIT 169 ratifiée par l'État |
| `rapporteur_special` | Rapport ou communication du Rapporteur spécial sur les droits des peuples autochtones |
| `organe_traite` | Observations d'un organe de traité (CERD, CDH, CDESC) nommant la communauté |
| `instance_permanente` | Instance permanente / MEDPA (EMRIP) : participation ou étude nommant la communauté |
| `forum_minorites` | Forum sur les questions relatives aux minorités / Déclaration 1992 |
| `accord_sous_egide` | Accord de paix ou règlement conclu sous égide ou suivi de l'ONU (ou SDN) |
| `mission_onu` | Mission ou opération de l'ONU liée au statut (ex. MINURSO, MONUB) |

Chaque entrée : `{mecanisme, detail, annee, source}` — `source` est une URL onusienne (un.org, ohchr.org, ilo.org, undocs.org) chaque fois que possible.

## 3. Grille des droits (`droits`) — 12 droits, valeur parmi `reconnu` / `partiel` / `conteste` / `non_etabli` / `non_applicable`

`reconnu` = inscrit dans un instrument juridique national en vigueur et appliqué ; `partiel` = inscrit avec limites fortes (portée, tutelle, domaines restreints) ; `conteste` = inscrit mais suspendu, révoqué, non appliqué ou attaqué en justice ; `non_etabli` = on n'a pas trouvé de source qui l'établisse (état honnête, pas un « non ») ; `non_applicable` = sans objet.

| clé | droit | question posée |
|---|---|---|
| `autogouvernement` | Institutions propres | Existe-t-il une assemblée ou un gouvernement élu ou coutumier propre, reconnu par l'État ? |
| `pouvoir_normatif` | Pouvoir normatif | Ces institutions édictent-elles des normes obligatoires (lois de pays, droit coutumier reconnu) ? |
| `justice_propre` | Justice propre | Existe-t-il une juridiction propre ou une reconnaissance de la justice coutumière ? |
| `terres` | Terres et territoire | Propriété ou maîtrise collective des terres, inaliénabilité ? |
| `ressources` | Ressources naturelles | Contrôle ou partage des ressources (sous-sol, eau, forêts, pêche) ? |
| `consentement` | Consultation et consentement | Obligation de consulter / consentement libre, préalable et éclairé ? |
| `langue` | Langue | Langue officielle ou co-officielle sur le territoire ? |
| `education` | Éducation | Système éducatif propre ou maîtrisé ? |
| `fiscalite` | Fiscalité et budget | Pouvoir fiscal ou budget propre garanti ? |
| `representation` | Représentation garantie | Sièges réservés ou représentation garantie au niveau de l'État ? |
| `statut_personnel` | Citoyenneté ou statut propre | Citoyenneté locale, droit de domicile, statut civil coutumier ? |
| `autodetermination_externe` | Autodétermination externe | Référendum d'indépendance ou droit de sécession prévu par un texte ? |

Chaque droit : `{valeur, note, source}`. `note` = une phrase factuelle qui cite l'instrument (article, année).

## 4. Degré d'autonomie — CALCULÉ, jamais saisi

Calculé par `scripts/generate_site.py` (fonction `degre`). Seules les valeurs `reconnu` et `partiel` comptent. Première condition remplie, de haut en bas :

- **5 — Autodétermination ouverte** : `autodetermination_externe` reconnu ou partiel.
- **4 — Autonomie législative** : `autogouvernement` reconnu ET `pouvoir_normatif` reconnu.
- **3 — Autogouvernement** : `autogouvernement` ≥ partiel ET (`pouvoir_normatif` ≥ partiel OU `justice_propre` ≥ partiel).
- **2 — Gestion propre** : `autogouvernement` ≥ partiel OU `terres` ≥ partiel.
- **1 — Participation** : au moins un autre droit ≥ partiel.
- **0 — Aucun droit établi**.

Le degré mesure ce que dit le droit, pas ce qui se passe. L'écart se lit dans `effectivite`.

## 4 bis. Libellés publics

`reconnu` → « Inscrit dans un texte » ; `partiel` → « Partiel » ; `conteste` → « Remis en cause » ; `non_etabli` → « Aucune source trouvée » ; effectivité `non_etablie` → « Inconnue ». « Autogestion » évité (sens historique) → « gestion propre ».

## 4 ter. Base (`base`)

`territoriale` / `personnelle` / `mixte` — indépendante du degré (autonomies non territoriales : parlements sámi, communautés nationales de Slovénie).

## 4 quater. Force de la reconnaissance ONU — calculée depuis `mecanisme`

contraignant : `liste_tna`, `oit_169`, `accord_sous_egide`, `mission_onu` ; déclaratif : `dnudpa`, `forum_minorites` ; mention : `rapporteur_special`, `organe_traite`, `instance_permanente`.

## 5. Effectivité (`effectivite`) — saisie, sourcée

`effective` / `partielle` / `contestee` / `non_etablie` + `note` (qui cite un rapport ONU, une décision de justice ou une source indépendante).

## 6. Bases nationales (`base_nationale[].nature`)

`constitution`, `loi_organique`, `statut_autonomie`, `loi`, `traite`, `accord_revendication`, `accord_paix`, `jurisprudence`, `coutume_reconnue`.

## 7. Régions (`region`) — géoschéma M49 de l'ONU, niveau 1 en français

`afrique`, `ameriques`, `asie`, `europe`, `oceanie`.

## 8. Ce que le cadre ne dit pas

- Le degré ne classe pas des peuples : il décrit des textes.
- « Non établi » veut dire « pas de source trouvée », jamais « n'existe pas ».
- Un peuple réparti sur plusieurs États a une fiche par régime juridique quand les régimes diffèrent (ex. Sámi de Norvège, de Finlande).
- Le nom de la fiche suit l'usage de la communauté (endonyme) quand il est attesté, le nom administratif vient ensuite.
