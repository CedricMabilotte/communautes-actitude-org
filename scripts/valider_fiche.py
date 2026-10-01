"""Valide une ou plusieurs fiches isolément : python3 scripts/valider_fiche.py <uid> [<uid>...]"""
import sys, shutil, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import generate_site as g

import re
PROSCRITS = ["résilience", "paradigme", "empowerment", "donner la parole", "emblématique", "fascinant", "crucial", "primitif", "préservé"]
A_SURVEILLER = [r"\bimpact", r"\brévolution", r"\balternative", r"\bunique\b", r"\briche\b", r"\bindigène", r"\btribu\b"]

def main():
    DATA0 = g.DATA
    for uid in sys.argv[1:]:
        g.DATA = DATA0
        src = DATA0 / f"{uid}.yml"
        with tempfile.TemporaryDirectory() as t:
            shutil.copy(src, t)
            g.DATA = pathlib.Path(t)
            f = g.charger()[0]
            txt = src.read_text(encoding="utf-8").lower()
            for m in g.MOTS_INTERDITS if hasattr(g, "MOTS_INTERDITS") else []:
                if m.lower() in txt:
                    g.fail(f"{uid} : mot interdit « {m} »")
            for m in PROSCRITS:
                if m in txt:
                    g.fail(f"{uid} : mot proscrit « {m} »")
            avert = [w for w in A_SURVEILLER if re.search(w, txt)]
            if avert:
                print(f"  attention {uid} : {', '.join(avert)} (autorisé seulement dans un nom officiel ou une citation)")
            print(f"ok {uid} : degré {f['degre']}, niveau {f['niveau_reconnaissance']}")

if __name__ == "__main__":
    main()
