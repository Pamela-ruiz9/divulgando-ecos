"""Hoja de ritmo de un reel: cuánto dura cada frase del guion y qué falla.

Adaptado al español de `ig-reel/beats.py` de instagram-agent-skill,
de Jake Schincariol (MIT; ver herramientas/LICENCIAS.md).

Diferencia clave: aquí el guion es `reels/guiones/<Reel>.json` (el mismo que
lee render/voz.py). Si ya existe `reels/public/voz/<Reel>/voz.json`, usa las
duraciones REALES de la narración; si no, las estima por número de palabras
con la velocidad medida de la voz Piper.

Marca: gancho largo, frases largas, tramos sin nada concreto, duración fuera
de meta y cierre que no hace eco del gancho (el loop).

Uso:
    python3 herramientas/ritmo.py reels/guiones/MexicoEnvejece.json --meta 20
    python3 herramientas/ritmo.py guion.txt --meta 30          # una frase por línea
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GANCHO_MAX = 3.5       # segundos; en español se permite un poco más que en inglés
FRASE_MAX = 4.5
RE_PALABRA = re.compile(r"[\wáéíóúñü]+", re.I)
RE_CONCRETO = re.compile(r"\d|(?i:\b(?:mil|millón|millones|mitad|tercio|cuarto|uno de cada|dos|tres|cuatro|cinco|"
                         r"diez|veinte|cien|por ciento)\b)|(?<!^)(?<![¿¡])\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b")
VACIAS = {"de", "la", "el", "los", "las", "y", "en", "que", "a", "un", "una", "es", "para", "por", "con",
          "se", "su", "al", "del", "lo", "como", "más", "ya", "eran", "son", "habrá", "esto"}


def palabras_por_seg() -> float:
    """Mide la velocidad real de la voz con los manifiestos voz.json existentes."""
    total_p = total_s = 0.0
    for m in (RAIZ / "reels/public/voz").glob("*/voz.json"):
        for f in json.loads(m.read_text(encoding="utf-8")):
            total_p += len(RE_PALABRA.findall(f["texto"]))
            total_s += f["duracion"]
    return total_p / total_s if total_s else 2.9


def cargar(ruta: Path) -> tuple[list[dict], str]:
    if ruta.suffix == ".json":
        guion = json.loads(ruta.read_text(encoding="utf-8"))
        frases = [{"id": f["id"], "texto": f["texto"]} for f in guion["frases"]]
        manifiesto = RAIZ / "reels/public/voz" / guion["reel"] / "voz.json"
        if manifiesto.exists():
            reales = {f["id"]: f for f in json.loads(manifiesto.read_text(encoding="utf-8"))}
            if all(f["id"] in reales and reales[f["id"]]["texto"] == f["texto"] for f in frases):
                for f in frases:
                    f["dur"] = reales[f["id"]]["duracion"]
                return frases, "duración real (voz.json)"
            return frases, "estimada: el guion cambió desde la última narración; vuelve a correr render/voz.py"
        return frases, "estimada (aún no hay narración)"
    lineas = [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [{"id": str(i + 1), "texto": l} for i, l in enumerate(lineas)], "estimada"


def analizar(frases: list[dict], meta: float | None) -> dict:
    pps = palabras_por_seg()
    reloj, notas = 0.0, []
    for f in frases:
        f.setdefault("dur", len(RE_PALABRA.findall(f["texto"])) / pps)
        f["inicio"], f["avisos"] = reloj, []
        f["concreto"] = bool(RE_CONCRETO.search(f["texto"]))
        reloj += f["dur"]
    if frases[0]["dur"] > GANCHO_MAX:
        frases[0]["avisos"].append(f"gancho de {frases[0]['dur']:.1f} s (máx. {GANCHO_MAX})")
        notas.append(f"El gancho tarda {frases[0]['dur']:.1f} s. Déjalo en ~{int(GANCHO_MAX * pps)} palabras "
                     "o parte la frase: la decisión de quedarse se toma antes.")
    if not frases[0]["concreto"]:
        notas.append("El gancho no tiene cifra, año ni nombre.")
    for f in frases[1:]:
        if f["dur"] > FRASE_MAX:
            f["avisos"].append(f"{f['dur']:.1f} s en una sola frase: cambia de escena a la mitad")
    racha = 0
    for f in frases:
        racha = 0 if f["concreto"] else racha + 1
        if racha == 3:
            f["avisos"].append("tres frases seguidas sin nada concreto")
    ultima = {w.lower() for w in RE_PALABRA.findall(frases[-1]["texto"])} - VACIAS
    primera = {w.lower() for w in RE_PALABRA.findall(frases[0]["texto"])} - VACIAS
    if len(frases) > 1 and not (ultima & primera):
        notas.append("El cierre no repite ninguna palabra del gancho: el loop (volver a verlo) se siente menos natural.")
    if meta:
        if reloj > meta * 1.15:
            notas.append(f"Dura {reloj:.1f} s y la meta es {meta:.0f} s: recorta {reloj - meta:.1f} s.")
        elif reloj < meta * 0.7:
            notas.append(f"Dura {reloj:.1f} s, bastante menos que la meta de {meta:.0f} s (puede estar bien).")
    return {"frases": frases, "total": reloj, "pps": pps, "notas": notas}


def tc(s: float) -> str:
    return f"{int(s // 60)}:{s % 60:04.1f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Hoja de ritmo de un guion de reel.")
    ap.add_argument("guion", type=Path)
    ap.add_argument("--meta", type=float, help="duración objetivo en segundos (narración)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    frases, fuente = cargar(a.guion)
    r = analizar(frases, a.meta)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print(f"\nRITMO · {len(frases)} frases · {r['total']:.1f} s de narración · {fuente} · {r['pps']:.1f} palabras/s")
    print("=" * 72)
    for i, f in enumerate(frases):
        etiqueta = "GANCHO" if i == 0 else "CIERRE" if i == len(frases) - 1 else ""
        print(f"  {tc(f['inicio'])}  {f['dur']:4.1f}s  {etiqueta:<7}{'·' if f['concreto'] else ' '} {f['texto'][:52]}")
        for av in f["avisos"]:
            print(f"  {'':<20}⚠ {av}")
    if r["notas"]:
        print("-" * 72)
        for n in r["notas"]:
            print(f"  • {n}")
    print("\n  (· = frase con dato concreto. La narración no incluye pausas ni animaciones de la composición.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
