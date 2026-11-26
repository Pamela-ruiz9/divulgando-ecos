"""Revisa el texto (caption) de Instagram como lo muestra el feed.

Adaptado al español de `ig-caption/caption.py` de instagram-agent-skill,
de Jake Schincariol (MIT; ver herramientas/LICENCIAS.md).

Muestra los primeros ~125 caracteres (lo que se ve antes de "… más") y revisa:
primera línea, gancho concreto, hashtags, links muertos, una sola petición,
densidad de emojis y términos de búsqueda.

Uso:
    python3 herramientas/texto.py personal/borradores/<post>/post.md            # sección Instagram
    python3 herramientas/texto.py post.md --seccion LinkedIn --corte 210
    python3 herramientas/texto.py borrador.txt --buscar "pensiones,demografía México"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

LIMITE = 2200
CORTE = {"Instagram": 125, "LinkedIn": 210, "X": 280}
MAX_HASHTAGS_IG = 5   # Tope de Instagram desde dic-2025 según instagram-agent-skill. Verificar si cambia.

RE_HASHTAG = re.compile(r"(?<![\w&])#([^\W\d_]\w*)")
RE_LINK = re.compile(r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com|mx|org|net|io|gob\.mx|co)/\S*", re.I)
RE_EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿]")
RE_CONCRETO = re.compile(r"\d|(?<!^)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b", re.M)
RELLENO = {"viral", "fyp", "parati", "foryou", "explore", "explorepage", "trending", "reels",
           "instagood", "follow", "like4like", "instadaily", "viralreels"}
PETICIONES = [
    (re.compile(r"(?i)\bcomenta (?:la palabra )?[«\"]?[A-ZÁÉÍÓÚÑ0-9]{3,}\b"), "comentar una palabra"),
    (re.compile(r"(?i)\b(?:te leo|cuéntame|dime)\b|¿(?:tú|y tú|qu[ée] (?:opinas|piensas|crees)|cu[aá]l|qu[ée] \w+ crees)[^?]*\?"), "responder una pregunta"),
    (re.compile(r"(?i)\bgu[aá]rd(?:a|alo|ala|ar)\b"), "guardar"),
    (re.compile(r"(?i)\bcompárte(?:lo|la)\b|\bcomparte (?:esto|este)\b"), "compartir"),
    (re.compile(r"(?i)\bsígueme\b"), "seguir"),
    (re.compile(r"(?i)\blink en (?:la|mi) bio\b|\benlace en (?:la|mi) bio\b"), "link en bio"),
    (re.compile(r"(?i)\bescr[ií]beme\b|\bmánda(?:me)? (?:un )?(?:dm|mensaje)\b"), "mensaje directo"),
]


def hashtags(texto: str) -> list[str]:
    return [h for h in RE_HASHTAG.findall(texto) if not re.fullmatch(r"[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}", h)]


def revisar(texto: str, plataforma: str = "Instagram", buscar: list[str] | None = None) -> dict:
    texto = texto.strip()
    corte = CORTE.get(plataforma, 125)
    ventana = texto[:corte]
    primera = texto.split("\n", 1)[0].strip()
    tags = hashtags(texto)
    links = RE_LINK.findall(texto)
    emojis = RE_EMOJI.findall(texto)
    peticiones = sorted({n for p, n in PETICIONES if p.search(texto)})
    checks = []

    def add(estado, nombre, detalle):
        checks.append({"estado": estado, "check": nombre, "detalle": detalle})

    add("FALLA" if len(texto) > LIMITE else "OK", "LARGO", f"{len(texto)}/{LIMITE} caracteres")
    if not primera:
        add("FALLA", "PRIMERA LÍNEA", "empieza con una línea en blanco")
    elif primera[0] in "#@":
        add("FALLA", "PRIMERA LÍNEA", "empieza con hashtag o mención: es el lugar más valioso del texto")
    elif len(primera) > corte:
        add("AVISO", "PRIMERA LÍNEA", f"{len(primera)} caracteres: se corta a los {corte}. Bien si el corte deja intriga; mal si corta a media idea")
    else:
        add("OK", "PRIMERA LÍNEA", f"{len(primera)} caracteres, se ve completa")
    add("OK" if RE_CONCRETO.search(ventana) else "AVISO", "GANCHO CONCRETO",
        f"{len(RE_CONCRETO.findall(ventana))} cifra(s) o nombre(s) antes del corte"
        + ("" if RE_CONCRETO.search(ventana) else ": nada verificable antes de «más»"))

    relleno = [t for t in tags if t.lower() in RELLENO]
    if plataforma == "Instagram" and len(tags) > MAX_HASHTAGS_IG:
        add("AVISO", "HASHTAGS", f"{len(tags)} hashtags; Instagram solo cuenta {MAX_HASHTAGS_IG}. Deja los más específicos")
    elif relleno:
        add("AVISO", "HASHTAGS", f"genéricos que no describen nada: {', '.join('#' + t for t in relleno)}")
    else:
        add("OK", "HASHTAGS", f"{len(tags)}")
    if any(f"#{t}" in ventana for t in tags):
        add("AVISO", "LUGAR DE HASHTAGS", "hay hashtags antes del corte: gastan espacio visible")

    if plataforma == "Instagram" and links:
        add("AVISO", "LINKS", f"{len(links)} link(s): en Instagram no son clicables. Bio o primer comentario")
    if len(peticiones) == 1:
        add("OK", "UNA PETICIÓN", peticiones[0])
    elif not peticiones:
        add("AVISO", "UNA PETICIÓN", "no hay llamada a la acción: decide para qué es el post")
    else:
        add("AVISO", "UNA PETICIÓN", f"{len(peticiones)} peticiones ({', '.join(peticiones)}): dos es igual a ninguna")
    densidad = len(emojis) * 100 / max(len(texto), 1)
    add("AVISO" if densidad > 4 else "OK", "EMOJIS", f"{len(emojis)} ({densidad:.1f} por cada 100 caracteres)")
    if buscar:
        bajo = texto.lower()
        faltan = [k for k in buscar if k.lower() not in bajo]
        add("AVISO" if faltan else "OK", "BÚSQUEDA",
            f"{len(buscar) - len(faltan)}/{len(buscar)} términos" + (f"; faltan: {', '.join(faltan)}" if faltan else ""))

    fallas = sum(c["estado"] == "FALLA" for c in checks)
    avisos = sum(c["estado"] == "AVISO" for c in checks)
    return {"ventana": ventana, "cortado": len(texto) > corte, "checks": checks,
            "veredicto": "CORREGIR" if fallas else "REVISAR" if avisos else "LISTO"}


def mostrar(r: dict, plataforma: str) -> None:
    print(f"\nTEXTO {plataforma.upper()} · {r['veredicto']}")
    print("  LO QUE SE VE EN EL FEED")
    print("  +" + "-" * 54 + "+")
    for linea in sum((textwrap.wrap(l, 52) or [""] for l in r["ventana"].split("\n")), [])[:8]:
        print(f"  | {linea:<52} |")
    cola = "… más" if r["cortado"] else "(cabe completo)"
    print("  +" + "-" * (54 - len(cola) - 2) + f" {cola} +\n")
    for c in r["checks"]:
        print(f"  {c['estado']:<6} {c['check']:<18} {c['detalle']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Revisa un texto de Instagram/LinkedIn.")
    ap.add_argument("entrada", help="post.md, archivo de texto o - para stdin")
    ap.add_argument("--seccion", default="Instagram")
    ap.add_argument("--buscar", default="", help="términos separados por coma por los que quieres que te encuentren")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.entrada == "-":
        texto = sys.stdin.read()
    else:
        texto = Path(a.entrada).read_text(encoding="utf-8")
        if texto.startswith("---"):
            from humano import seccion_de_post
            texto = seccion_de_post(Path(a.entrada), a.seccion)
    r = revisar(texto, a.seccion, [k.strip() for k in a.buscar.split(",") if k.strip()])
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        mostrar(r, a.seccion)
    return 1 if r["veredicto"] == "CORREGIR" else 0


if __name__ == "__main__":
    sys.exit(main())
