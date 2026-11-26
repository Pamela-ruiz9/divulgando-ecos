"""Quita la huella de "texto hecho por máquina" y califica qué tan humano suena.

Adaptado al español de `ig-human` (humanize.py + detect.py) de
instagram-agent-skill, de Jake Schincariol (MIT; ver herramientas/LICENCIAS.md).

Diferencias con el original:
- Las rayas (—) NO se convierten en comas: en español son puntuación correcta
  para incisos. Solo se avisa si hay demasiadas (es una huella de IA).
- Comillas y puntos suspensivos tipográficos se respetan.
- El léxico (`muletillas.json`) es en español y propio de la divulgación.

Qué hace sola:  borra caracteres invisibles (siempre).
Qué sugiere:    muletillas con su cambio (se aplican solo con --corregir).
Qué marca:      estructuras que hay que reescribir a mano.

Uso:
    python3 herramientas/humano.py borrador.txt
    python3 herramientas/humano.py borrador.txt --corregir -o limpio.txt
    python3 herramientas/humano.py personal/borradores/<post>/post.md --seccion Instagram
    echo "texto" | python3 herramientas/humano.py -

Esto son heurísticas locales; no es un detector de IA ni promete pasar uno.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LEXICO = json.loads((AQUI / "muletillas.json").read_text(encoding="utf-8"))
RE_URL = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
RE_FRASE = re.compile(r"[^.!?¿¡\n]+[.!?]*")
RE_PERSONA = re.compile(
    r"(?i)\b(?:yo|me|mi|mis|te|ti|tu|tus|tú|contigo|nos|nuestro|nuestra|nuestros|nuestras|\w{3,}mos|"
    r"crees|sabes|imaginas|piensas|revisas|tienes|puedes|quieres|haces|compras|ahorras|ganas|gastas|pagas|"
    r"mira|guarda|revisa|imagina|calcula|compara|dime|cuéntame)\b")
RE_CONCRETO = re.compile(r"\d|(?<![.!?]\s)(?<!^)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b", re.M)


def _cp(spec: str):
    if "-" in spec:
        a, b = spec.split("-")
        return int(a[2:], 16), int(b[2:], 16)
    return int(spec[2:], 16)


def es_emoji(c: str) -> bool:
    return unicodedata.category(c) == "So" or 0x1F000 <= ord(c) <= 0x1FAFF


def limpiar_invisibles(texto: str) -> tuple[str, list[str]]:
    hallados = []
    for e in LEXICO["invisibles"]:
        cp = _cp(e["cp"])
        rango = cp if isinstance(cp, tuple) else (cp, cp)
        nuevo, n = [], 0
        for i, c in enumerate(texto):
            if rango[0] <= ord(c) <= rango[1]:
                # El ZWJ une emojis compuestos (👩‍💻): ahí no es huella.
                if c == "‍" and 0 < i < len(texto) - 1 and es_emoji(texto[i - 1]) and es_emoji(texto[i + 1]):
                    nuevo.append(c)
                    continue
                n += 1
                nuevo.append(" " if e["accion"] == "espacio" else "")
            else:
                nuevo.append(c)
        if n:
            hallados.append(f"{n}× {e['nombre']}")
            texto = "".join(nuevo)
    return texto, hallados


def buscar_muletillas(texto: str, corregir: bool) -> tuple[str, list[dict]]:
    hallados = []
    urls = RE_URL.findall(texto)
    for i, u in enumerate(urls):
        texto = texto.replace(u, f"\x00{i}\x00", 1)
    for e in sorted(LEXICO["palabras"], key=lambda e: -len(e["buscar"])):
        patron = re.compile(r"(?<!\w)" + re.escape(e["buscar"]).replace(r"\ ", r"\s+") + r"(?!\w)", re.I)
        n = len(patron.findall(texto))
        if not n:
            continue
        hallados.append({**e, "veces": n})
        if corregir:
            def cambio(m, r=e["cambiar"]):
                if not r:
                    return ""
                return r[0].upper() + r[1:] if m.group(0)[0].isupper() else r
            texto = patron.sub(cambio, texto)
    if corregir:
        texto = re.sub(r"[ \t]{2,}", " ", texto)
        texto = re.sub(r"(?m)^[ \t]*[,;:]\s*", "", texto)
        texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)
        texto = re.sub(r",\s*([,.;:!?])", r"\1", texto)
        # Tras borrar una apertura, la frase debe empezar con mayúscula.
        texto = re.sub(r"(^|[.!?]\s+|\n)([a-záéíóúñ])", lambda m: m.group(1) + m.group(2).upper(), texto)
    for i, u in enumerate(urls):
        texto = texto.replace(f"\x00{i}\x00", u)
    return texto, hallados


def buscar_estructuras(texto: str) -> list[dict]:
    marcas = []
    for s in LEXICO["estructuras"]:
        try:
            n = len(re.findall(s["regex"], texto))
        except re.error:
            continue
        if n:
            marcas.append({"nombre": s["nombre"], "veces": n, "arreglo": s["arreglo"]})
    rayas = texto.count("—")
    mil = max(len(texto), 1) / 1000
    if rayas / mil > 4:
        marcas.append({"nombre": f"Muchas rayas (—): {rayas}", "veces": rayas,
                       "arreglo": "En español son correctas, pero en exceso delatan a la IA. Deja una o dos."})
    largos = [len(f.split()) for f in RE_FRASE.findall(texto) if len(f.split()) > 2]
    if len(largos) >= 4:
        cv = statistics.pstdev(largos) / statistics.mean(largos)
        if cv < 0.35:
            marcas.append({"nombre": f"Frases del mismo largo (variación {cv:.2f})", "veces": len(largos),
                           "arreglo": "Parte una frase en dos y deja otra larga. Las máquinas escriben parejo."})
    return marcas


def calificar(texto: str) -> dict[str, float]:
    """Cinco señales de 0 a 100 (más alto = más humano), como detect.py."""
    palabras = re.findall(r"\w+", texto)
    n = max(len(palabras), 1)
    largos = [len(f.split()) for f in RE_FRASE.findall(texto) if f.split()]
    variacion = statistics.pstdev(largos) / statistics.mean(largos) if len(largos) >= 3 else 0.6
    concretos = len(RE_CONCRETO.findall(texto)) * 100 / n
    _, mul = buscar_muletillas(texto, False)
    densidad = sum(m["veces"] for m in mul) * 100 / n
    invisibles = sum(1 for c in texto if unicodedata.category(c) == "Cf" and c != "‍")
    rayas = texto.count("—") * 1000 / max(len(texto), 1)
    estructuras = len(buscar_estructuras(texto))
    # En español el sujeto se omite: además de pronombres, cuenta verbos en
    # primera del plural (-mos) y segundas personas frecuentes (crees, sabes…).
    primera = len(RE_PERSONA.findall(texto)) * 100 / n
    return {
        "VARIEDAD": max(0, min(100, variacion / 0.6 * 100)),
        "CONCRECIÓN": max(15, min(100, concretos * 12)),
        "MULETILLAS": max(0, 100 - densidad * 25),
        "HUELLA": max(0, 100 - invisibles * 30 - max(0, rayas - 4) * 10),
        "VOZ": max(0, min(100, 50 + primera * 6) - estructuras * 15),
    }


def veredicto(senales: dict[str, float]) -> tuple[float, str]:
    total = statistics.mean(senales.values()) * 0.6 + min(senales.values()) * 0.4
    return total, ("PASA" if total >= 70 and min(senales.values()) >= 55 else "REVISAR" if total >= 50 else "REESCRIBIR")


def revisar(texto: str, corregir: bool = False) -> dict:
    sin_invisibles, invisibles = limpiar_invisibles(texto)
    antes, _ = veredicto(calificar(texto))
    limpio, muletillas = buscar_muletillas(sin_invisibles, corregir)
    senales = calificar(limpio)
    total, v = veredicto(senales)
    return {"texto": limpio, "invisibles": invisibles, "muletillas": muletillas,
            "estructuras": buscar_estructuras(limpio), "senales": senales, "puntaje": total,
            "puntaje_original": antes, "veredicto": v}


def seccion_de_post(ruta: Path, seccion: str) -> str:
    cuerpo = ruta.read_text(encoding="utf-8").split("---", 2)[-1]
    m = re.search(rf"(?ms)^## {re.escape(seccion)}\s*\n(.*?)(?=^## |\Z)", cuerpo)
    if not m:
        sys.exit(f"No hay sección `## {seccion}` en {ruta}")
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Humaniza y califica un texto en español.")
    ap.add_argument("entrada", help="archivo de texto, post.md (con --seccion) o - para stdin")
    ap.add_argument("--seccion", help="sección de un post.md, p. ej. Instagram")
    ap.add_argument("--corregir", action="store_true", help="aplica los cambios de muletillas")
    ap.add_argument("-o", "--salida", type=Path, help="escribe el texto limpio aquí")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.entrada == "-":
        texto = sys.stdin.read()
    elif a.seccion:
        texto = seccion_de_post(Path(a.entrada), a.seccion)
    else:
        texto = Path(a.entrada).read_text(encoding="utf-8")
    r = revisar(texto, a.corregir)

    if a.salida:
        a.salida.write_text(r["texto"], encoding="utf-8")
    if a.json:
        print(json.dumps({k: v for k, v in r.items() if k != "texto"}, ensure_ascii=False, indent=2))
        return 0

    cambio = f" (antes {r['puntaje_original']:.0f})" if round(r["puntaje_original"]) != round(r["puntaje"]) else ""
    print(f"\nHUMANO · {r['puntaje']:.0f}/100{cambio} · {r['veredicto']}")
    print("=" * 60)
    for k, v in r["senales"].items():
        print(f"  {k:<11} {'#' * round(v / 100 * 24):<24} {v:5.1f}")
    if r["invisibles"]:
        print("\n1. Invisibles borrados: " + ", ".join(r["invisibles"]))
    if r["muletillas"]:
        print(f"\n2. Muletillas{' (corregidas)' if a.corregir else ''}:")
        for m in r["muletillas"]:
            print(f"   «{m['buscar']}» ×{m['veces']} → {('«' + m['cambiar'] + '»') if m['cambiar'] else '(borrar)'}")
    if r["estructuras"]:
        print("\n3. Reescribe a mano:")
        for s in r["estructuras"]:
            print(f"   {s['nombre']} ×{s['veces']}: {s['arreglo']}")
    if r["veredicto"] != "PASA":
        peor = min(r["senales"], key=r["senales"].get)
        print(f"\nLa señal más débil es {peor}: arregla esa y vuelve a correrlo.")
    if not a.salida and (a.corregir or r["invisibles"]):
        print("\n--- texto limpio ---\n" + r["texto"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
