# -*- coding: utf-8 -*-
"""
Chemins des outils externes, pour Windows comme pour Linux (session cloud).

Chaque outil se cherche dans cet ordre : variable d'environnement, emplacement
habituel de l'installation Windows, puis le PATH. Aucun script ne doit plus
ecrire un chemin d'outil en dur : il importe ce module.

    BANC_FREECAD    freecadcmd (FreeCAD 1.0 en ligne de commande)
    BANC_CCX        ccx (CalculiX, livre avec FreeCAD)
    BANC_NAVIGATEUR navigateur Chromium sans interface (Edge, Chrome, Chromium)
"""

import os
import shutil

_WIN_FREECAD = r"C:/Program Files/FreeCAD 1.0/bin/freecadcmd.exe"
_WIN_CCX = r"C:/Program Files/FreeCAD 1.0/bin/ccx.exe"
_WIN_EDGE = r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"


def _cherche(var, chemins, noms):
    v = os.environ.get(var)
    if v:
        return v
    for c in chemins:
        if os.path.isfile(c):
            return c
    for n in noms:
        t = shutil.which(n)
        if t:
            return t
    return None


def freecad():
    return _cherche("BANC_FREECAD", [_WIN_FREECAD],
                    ["freecadcmd", "FreeCADCmd", "freecadcmd-daily"]) or _WIN_FREECAD


def ccx():
    return _cherche("BANC_CCX", [_WIN_CCX], ["ccx", "ccx_2.21", "ccx_2.20"]) or _WIN_CCX


def navigateur():
    """Navigateur Chromium sans interface, ou None."""
    return _cherche("BANC_NAVIGATEUR", [_WIN_EDGE],
                    ["msedge", "google-chrome", "google-chrome-stable", "chromium",
                     "chromium-browser", "chrome"])


def empreinte_modele():
    """Empreinte de params.py et parts.py (fins de ligne ramenees a LF). Un
    resultat engendre l'enregistre : il est perime si elle a change depuis.
    La date d'un fichier ne le dit pas : git ne la conserve pas, un depot tout
    juste extrait a tous ses fichiers du meme instant."""
    import hashlib
    h = hashlib.sha1()
    for nom in ("params.py", "parts.py"):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), nom), "rb") as f:
            h.update(f.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def aujourdhui():
    """Date du jour jj/mm/aaaa, a enregistrer DANS un resultat de calcul."""
    import time
    return time.strftime("%d/%m/%Y")


def options_navigateur():
    """Options communes du mode sans interface (Linux en conteneur : pas de bac a sable)."""
    o = ["--headless", "--disable-gpu", "--hide-scrollbars"]
    if os.name != "nt":
        o.append("--no-sandbox")
    return o


FREECAD = freecad()
CCX = ccx()
