"""Califica ganchos (primera frase de un reel o portada de carrusel) y los ordena.

Adaptado al español de `ig-reel/hookscore.py` de instagram-agent-skill,
de Jake Schincariol (MIT; ver herramientas/LICENCIAS.md).

Cinco propiedades, de 0 a 100: LARGO (se dice en ~3 s), CONCRECIÓN (cifra,
año, nombre), TENSIÓN (algo en juego o un contraste), AL FRENTE (lo
interesante en las primeras palabras) y A QUIÉN (le habla a alguien).
También dice qué fórmula de `ganchos.json` usa cada uno.

Qué NO es: un predictor de vistas. Según su autor, el original separa bien un
gancho real de uno malo, pero casi no distingue entre dos ganchos decentes.
Úsalo para cazar saludos, rodeos y ganchos sin nada concreto.

Uso:
    python3 herramientas/gancho.py ganchos.txt          # uno por línea, ordenados
    python3 herramientas/gancho.py --gancho "En 1970, casi la mitad de México eran niños."
    python3 herramientas/gancho.py reels/guiones/MexicoEnvejece.json   # califica la primera frase
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FORMULAS = json.loads((AQUI / "ganchos.json").read_text(encoding="utf-8"))["ganchos"]
PALABRAS_POR_SEG = 3.2   # medido con la voz Piper de reels/public/voz/*/voz.json

RE_PALABRA = re.compile(r"[\wáéíóúñü$%]+(?:[.,]\d+)?", re.I)
RE_CIFRA = re.compile(r"\$\s?\d|\b\d[\d.,]*\s*%?|\b(?:19|20)\d\d\b")
RE_PROPIO = re.compile(r"(?<!^)(?<![.!?¿¡]\s)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b")
RE_EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

NUMEROS = {"dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce",
           "quince", "veinte", "treinta", "cuarenta", "cincuenta", "cien", "ciento", "mil", "millón",
           "millones", "mitad", "tercio", "cuarto", "doble", "triple", "cero", "porciento",
           "pesos", "dólares", "sueldo", "salario", "aguinaldo", "inflación", "pensión", "deuda"}
TENSION = {"no", "nunca", "nadie", "nada", "sin", "pero", "mito", "error", "equivoqué", "mal", "falso",
           "mentira", "miente", "truco", "pierdes", "pierde", "perdí", "cuesta", "costó", "caro", "gratis",
           "deja", "dejes", "evita", "cuidado", "riesgo", "peligro", "ya", "todavía", "aún", "solo",
           "sólo", "realmente", "verdad", "secreto", "esconde", "contra", "vs", "antes", "después",
           "cambia", "cambió", "cruzó", "nadie", "casi", "más", "menos", "mitad", "doble", "tanto", "tantos"}
APERTURAS_FLOJAS = ["hola", "bueno", "bien", "ok", "oye", "chicos", "hoy", "en este video", "en el video",
                    "les quiero", "te quiero", "quiero", "vamos a", "les voy", "te voy a", "hablemos",
                    "sabías que", "¿sabías que", "este es", "esto es", "hay", "existe", "como sabes",
                    "seguramente", "básicamente", "la verdad", "el día de hoy"]
IMPERATIVOS = {"mira", "imagina", "guarda", "revisa", "calcula", "compara", "deja", "evita", "piensa",
               "adivina", "haz", "toma", "fíjate", "olvida", "nunca"}
DESCALIFICA = [
    (re.compile(r"(?i)^\s*(?:¡?hola|¿?qué tal|bienvenid)"), "Saludo: nadie entró al feed a que lo saludaran."),
    (re.compile(r"(?i)\ben (?:este|el) (?:video|reel|post)\b|\bte voy a (?:enseñar|mostrar|explicar)\b"),
     "Preámbulo de video: bórralo y abre con lo que ibas a enseñar."),
    (re.compile(r"(?i)^\s*(?:deja de hacer scroll|no hagas scroll|espera)\b"), "Pedir atención demuestra que no la ganaste."),
    (re.compile(r"#\w+"), "Hashtag en el gancho."),
    (RE_EMOJI, "Emoji en el gancho: en pantalla no cabe palabra y emoji a la vez."),
]


def palabras(t: str) -> list[str]:
    return RE_PALABRA.findall(t)


def tope(n: float) -> float:
    return max(0.0, min(100.0, n))


def largo(t):
    n = len(palabras(t))
    seg = n / PALABRAS_POR_SEG
    p = 100.0 if 5 <= n <= 14 else tope(100 - (5 - n) * 20) if n < 5 else tope(100 - (n - 14) * 10)
    if len(t.strip()) > 80:
        p -= 10
    return tope(p), f"{n} palabras, ~{seg:.1f} s dicho (ideal 5–14 palabras, ≤ 3–4 s)"


def concrecion(t):
    bajo = [w.lower() for w in palabras(t)]
    hallados = RE_CIFRA.findall(t) + RE_PROPIO.findall(t) + [w for w in bajo if w in NUMEROS]
    hallados = [h.strip() for h in hallados if h.strip()]
    p = 15.0 if not hallados else tope(45 + 30 * len(hallados))
    return p, (f"{len(hallados)} marca(s) concreta(s): {', '.join(hallados[:4])}" if hallados
               else "sin cifra, año ni nombre: nada verificable")


def tension(t):
    hits = sorted({w.lower() for w in palabras(t) if w.lower() in TENSION})
    if re.search(r"(?:19|20)\d\d\b.*(?:19|20)\d\d\b", t):
        hits.append("contraste de años")
    p = {0: 20.0, 1: 70.0}.get(len(hits), 100.0)
    return p, (f"{len(hits)} marca(s): {', '.join(hits[:4])}" if hits else "nada en juego, ningún contraste")


def al_frente(t):
    ws = palabras(t)
    if not ws:
        return 0.0, "vacío"
    bajo = [w.lower() for w in ws]
    inicio = t.strip().lower().lstrip("¿¡…. ")
    floja = next((a for a in APERTURAS_FLOJAS if inicio.startswith(a.lstrip("¿"))), None)
    pos = next((i for i, w in enumerate(ws) if RE_CIFRA.match(w) or bajo[i] in NUMEROS or bajo[i] in TENSION
                or (i and RE_PROPIO.match(w))), None)
    if pos is None:
        base, donde = 30.0, "lo interesante no aparece"
    elif pos <= 3:
        base, donde = 100.0, f"lo interesante en la palabra {pos + 1}"
    elif pos <= 6:
        base, donde = 70.0, f"lo interesante en la palabra {pos + 1}; podría ir antes"
    else:
        base, donde = 40.0, f"lo interesante hasta la palabra {pos + 1}: tarde"
    return tope(base - (30 if floja else 0)), donde + (f"; apertura floja «{floja}»" if floja else "")


def a_quien(t):
    bajo = t.lower()
    ws = [w.lower() for w in palabras(t)]
    if re.search(r"\b(?:tú|te|tu|tus|ti|contigo|usted|ustedes)\b", bajo) or re.search(r"\b\w+(?:as|es)\b\?", bajo):
        return 100.0, "le habla a quien mira"
    if ws and ws[0] in IMPERATIVOS:
        return 90.0, f"abre con imperativo («{ws[0]}»)"
    if re.search(r"\b(?:yo|me|mi|mis|nos|nuestro|nuestra|\w{3,}mos)\b", bajo):
        return 70.0, "primera persona, sin nombrar a quien mira"
    return 55.0, "tercera persona (en datos puede funcionar si la cifra es fuerte)"


PROPIEDADES = {"LARGO": largo, "CONCRECIÓN": concrecion, "TENSIÓN": tension, "AL FRENTE": al_frente, "A QUIÉN": a_quien}


def formula(t: str) -> str | None:
    # Las más específicas primero; «La cifra que sorprende» (cualquier %) al final.
    for f in sorted(FORMULAS, key=lambda f: f["id"] == 1):
        if re.search(f["match"], t.strip(), re.I):
            return f"#{f['id']} {f['nombre']}"
    return None


def calificar(t: str) -> dict:
    res = {k: fn(t) for k, fn in PROPIEDADES.items()}
    puntos = [v[0] for v in res.values()]
    marcas = [m for p, m in DESCALIFICA if p.search(t)]
    total = tope(statistics.mean(puntos) * 0.6 + min(puntos) * 0.4 - 15 * len(marcas))
    veredicto = "FUERTE" if total >= 70 and min(puntos) >= 55 and not marcas else "OK" if total >= 50 else "DÉBIL"
    return {"gancho": t.strip(), "propiedades": res, "descalifica": marcas, "puntaje": round(total, 1),
            "veredicto": veredicto, "formula": formula(t), "mas_debil": min(res, key=lambda k: res[k][0])}


def leer(entrada: str) -> list[str]:
    if entrada == "-":
        return [l.strip() for l in sys.stdin.read().splitlines() if l.strip()]
    ruta = Path(entrada)
    if ruta.suffix == ".json":
        guion = json.loads(ruta.read_text(encoding="utf-8"))
        return [guion["frases"][0]["texto"]]
    return [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description="Califica ganchos de reels en español.")
    ap.add_argument("entrada", nargs="?", default="-", help="archivo (uno por línea), guion .json o -")
    ap.add_argument("--gancho", help="califica un solo gancho")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    lineas = [a.gancho] if a.gancho else leer(a.entrada)
    res = sorted((calificar(l) for l in lineas), key=lambda r: -r["puntaje"])
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    if len(res) == 1:
        r = res[0]
        print(f"\nGANCHO  «{r['gancho']}»")
        print("=" * 64)
        for k, (p, det) in r["propiedades"].items():
            print(f"  {k:<11} {'#' * round(p / 100 * 24):<24} {p:5.1f}  {det}")
        print("-" * 64)
        print(f"  PUNTAJE     {r['puntaje']:.0f}  {r['veredicto']}" + (f"   fórmula {r['formula']}" if r["formula"] else ""))
        for m in r["descalifica"]:
            print(f"  ✖ {m}")
        if r["veredicto"] != "FUERTE":
            print(f"  Lo más débil: {r['mas_debil']}. Arregla eso y vuelve a calificar.")
    else:
        print("\nGANCHOS ORDENADOS\n" + "=" * 72)
        for i, r in enumerate(res):
            print(f"{'→' if i == 0 else ' '} {r['puntaje']:5.1f} {r['veredicto']:<7} {r['gancho'][:58]}")
            print(f"        {r['formula'] or 'sin fórmula reconocida'} · más débil: {r['mas_debil']}")
            for m in r["descalifica"]:
                print(f"        ✖ {m}")
        print("\nGraba el primero. Si el primero está bajo 50, ninguno es el gancho todavía.")
    return 0 if res[0]["puntaje"] >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())
