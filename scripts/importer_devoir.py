"""Crée le notebook d'un devoir du ML Zoomcamp à partir de son énoncé.

Usage, depuis la racine du repo ml-zoomcamp :
    python scripts/importer_devoir.py 01-intro

Le script lit l'énoncé dans le repo du cours, le découpe par section,
et crée <module>/homework.ipynb avec une cellule de texte par section
suivie d'une cellule de code vide. Il ne remplace jamais un notebook existant.
"""

import json
import sys
import uuid
from pathlib import Path

COURS = Path.home() / "Development/IA/machine-learning-zoomcamp"
SESSION = "2026"
FIN = ("Learning in Public", "Submit the results")


def decouper_sections(texte):
    sections = []
    courante = []
    dans_code = False
    for ligne in texte.splitlines():
        if ligne.strip().startswith("```"):
            dans_code = not dans_code
        est_titre = not dans_code and ligne.startswith("#") and " " in ligne[:5]
        if est_titre:
            if any(mot in ligne for mot in FIN):
                break
            if courante:
                sections.append("\n".join(courante).strip())
            courante = [ligne]
        else:
            courante.append(ligne)
    if courante:
        sections.append("\n".join(courante).strip())
    return [s for s in sections if s]


def cellule(type_cellule, texte=""):
    contenu = {
        "id": uuid.uuid4().hex[:8],
        "cell_type": type_cellule,
        "metadata": {},
        "source": texte.splitlines(keepends=True),
    }
    if type_cellule == "code":
        contenu["execution_count"] = None
        contenu["outputs"] = []
    return contenu


def creer_notebook(module):
    enonce = COURS / "cohorts" / SESSION / "homework" / module / "homework.md"
    if not enonce.exists():
        sys.exit(f"Énoncé introuvable : {enonce}")

    destination = Path(module) / "homework.ipynb"
    if destination.exists():
        sys.exit(f"{destination} existe déjà, je ne le remplace pas.")

    sections = decouper_sections(enonce.read_text(encoding="utf-8"))
    lien = (
        "https://github.com/DataTalksClub/machine-learning-zoomcamp/blob/main/"
        f"cohorts/{SESSION}/homework/{module}/homework.md"
    )

    cellules = [cellule("markdown", f"{sections[0]}\n\nÉnoncé : {lien}")]
    for section in sections[1:]:
        cellules.append(cellule("markdown", section))
        cellules.append(cellule("code"))

    notebook = {
        "cells": cellules,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    destination.parent.mkdir(exist_ok=True)
    destination.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"Créé : {destination} ({len(sections) - 1} sections)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage : python scripts/importer_devoir.py 01-intro")
    creer_notebook(sys.argv[1])
