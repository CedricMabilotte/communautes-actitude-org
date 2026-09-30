# Déploiement

- Hébergement : GitHub Pages, dépôt `CedricMabilotte/communautes-actitude-org`, construction par GitHub Actions (`.github/workflows/publier.yml`) à chaque push sur `main`.
- Domaine : `communautes.actitude.org`, enregistrement `CNAME communautes → cedricmabilotte.github.io.` (TTL 1800) dans la zone Gandi LiveDNS `actitude.org`. Le domaine est déclaré côté GitHub par l'API (`gh api -X PUT repos/CedricMabilotte/communautes-actitude-org/pages -f cname=communautes.actitude.org`) : en mode workflow, un fichier CNAME est ignoré.
- HTTPS : certificat Let's Encrypt émis par GitHub, puis `https_enforced=true`.
- Pièges : le wildcard Gandi (`*` → webredir, TTL 10800) peut rester en cache 3 h ; le cache CDN de Pages dure ~10 min ; vérifier `gh api repos/…/deployments`, pas seulement `gh run list` ; vignettes en JPEG (limite 1 Go de l'artefact).
- Vignettes : `scripts/social_cards.py` tourne en local (Playwright + Chromium), les JPEG sont versionnés dans `assets/cards/`.
