"""Descarga la pirámide poblacional de México (Banco Mundial, fuente 40:
Population estimates and projections, basada en UN WPP).

Uso: python3 datos/scripts/piramide_mx.py [años...]   (default: 1970 2000 2025 2050)
Salida: datos/piramide_mx.csv  (anio, grupo, sexo, poblacion)
"""
import csv, json, sys, urllib.request
from pathlib import Path

GRUPOS = ["0004","0509","1014","1519","2024","2529","3034","3539","4044","4549",
          "5054","5559","6064","6569","7074","7579","80UP"]
ANIOS = sys.argv[1:] or ["1970", "2000", "2025", "2050"]
URL = "https://api.worldbank.org/v2/country/MEX/indicator/SP.POP.{g}.{s}?format=json&source=40&date={a1}:{a2}&per_page=200"

filas = []
for g in GRUPOS:
    for s, sexo in (("FE", "mujeres"), ("MA", "hombres")):
        url = URL.format(g=g, s=s, a1=min(ANIOS), a2=max(ANIOS))
        with urllib.request.urlopen(url, timeout=30) as r:
            meta, datos = json.load(r)
        for d in datos or []:
            if d["date"] in ANIOS and d["value"] is not None:
                etiqueta = "80+" if g == "80UP" else f"{int(g[:2])}-{int(g[2:])}"
                filas.append({"anio": d["date"], "orden": GRUPOS.index(g), "grupo": etiqueta, "sexo": sexo, "poblacion": d["value"]})

salida = Path(__file__).resolve().parents[1] / "piramide_mx.csv"
with salida.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["anio", "grupo", "sexo", "poblacion"], extrasaction="ignore")
    w.writeheader(); w.writerows(sorted(filas, key=lambda x: (x["anio"], x["orden"], x["sexo"])))
print(salida, len(filas), "filas")
