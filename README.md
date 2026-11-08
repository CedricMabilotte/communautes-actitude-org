# Communautés reconnues

Atlas des peuples et communautés officiellement reconnus (Nations unies, systèmes régionaux ou État) qui disposent, dans le droit de leur État, de droits d'autonomie : institutions propres, terres, justice, langue, jusqu'au choix de leur statut.

Site : **https://communautes.actitude.org**

Créé par Cedric Mabilotte. Licence : CC BY-NC-SA 4.0 (voir `LICENCE`).

## Structure

| Chemin | Contenu |
|---|---|
| `data/communautes/*.yml` | une fiche par communauté (format : `docs/exemple-fiche.yml`) |
| `docs/cadre.md` | le cadre de description : critère d'entrée, types, 12 droits, règle du degré |
| `pages/*.md` | pages éditoriales (méthode, droit de réponse, biais…) |
| `data/dossiers/*.yml` | dossiers thématiques (format : `docs/format-dossier.yml`) |
| `assets/` | CSS, JS, polices auto-hébergées, fond de carte, vignettes de partage |
| `scripts/generate_site.py` | génère `site/` (seule dépendance : `pyyaml`), calcule les degrés, vérifie les liens |
| `scripts/social_cards.py` | fabrique les vignettes JPEG 1200×630 et 1080×1350 (Playwright, en local) |

## Utilisation

```
pip install pyyaml
python3 scripts/generate_site.py          # → site/
python3 -m http.server -d site 8000       # aperçu sur http://localhost:8000
```

Ajouter une communauté : créer `data/communautes/<uid>.yml` sur le modèle de `docs/exemple-fiche.yml`, puis `python3 scripts/social_cards.py <uid>` pour ses vignettes. Le générateur refuse une fiche dont un droit « inscrit », « partiel » ou « remis en cause » n'a pas de note et de source.

## Corrections

Voir la page [Droit de réponse](https://communautes.actitude.org/droit-de-reponse/) ou ouvrir un ticket.

## Réutiliser

- **Fiches** : `data/communautes/<slug>.yml` (une fiche par communauté), tables dans `data/tables/`, dossiers dans `data/dossiers/`. Adresse stable sur le site : https://communautes.actitude.org/c/<slug>/ (site hors ligne au 08/11 : certificat, ticket Support en cours).
- **Téléchargement** : https://communautes.actitude.org/donnees/communautes.json et communautes.csv (régénérés au build).
- **Licences** (`LICENSE`) : textes CC BY-NC-SA 4.0 ; données ODbL 1.0 ; code AGPL-3.0-or-later ; sources tierces à leur licence.
- **Citer** : `CITATION.cff` (GitHub : « Cite this repository »). Archive pérenne : Software Heritage,
  https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/CedricMabilotte/communautes-actitude-org
- **Corriger** : `CONTRIBUTING.md` — une issue ou une PR par fiche, source citée, réponse sous un mois.
