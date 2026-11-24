"""Renderiza piezas HTML a PNG con Playwright (Chromium).

Uso:
    python3 render/render.py <archivo.html> [--datos datos.json] [--salida carpeta]
                             [--ancho 1080] [--alto 1350] [--nombre base]

- Cada <section class="slide"> se exporta como PNG (<nombre>-01.png, -02.png...).
- Si se pasa --datos, el JSON queda disponible en la página como window.DATOS
  (las plantillas lo usan para llenar textos).
- Por defecto, los PNG se guardan junto al HTML (o en --salida).
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def render(html: Path, ancho: int, alto: int, datos: dict | None = None,
           salida: Path | None = None, nombre: str | None = None) -> list[Path]:
    salida = salida or html.parent
    salida.mkdir(parents=True, exist_ok=True)
    nombre = nombre or html.stem
    rutas = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": ancho, "height": alto}, device_scale_factor=1)
        if datos is not None:
            pagina.add_init_script(f"window.DATOS = {json.dumps(datos, ensure_ascii=False)};")
        pagina.goto(html.resolve().as_uri())
        pagina.wait_for_load_state("networkidle")
        pagina.evaluate("document.fonts.ready")
        slides = pagina.query_selector_all("section.slide")
        objetivos = slides or [None]
        for i, slide in enumerate(objetivos, 1):
            destino = salida / f"{nombre}-{i:02d}.png"
            (slide or pagina).screenshot(path=str(destino))
            rutas.append(destino)
        navegador.close()
    return rutas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--datos", type=Path)
    ap.add_argument("--salida", type=Path)
    ap.add_argument("--nombre")
    ap.add_argument("--ancho", type=int, default=1080)
    ap.add_argument("--alto", type=int, default=1350)
    a = ap.parse_args()
    datos = json.loads(a.datos.read_text(encoding="utf-8")) if a.datos else None
    for r in render(a.html, a.ancho, a.alto, datos, a.salida, a.nombre):
        print(r)
