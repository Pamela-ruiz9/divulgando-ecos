"""Renderiza piezas HTML a PNG con Playwright (Chromium).

Uso:
    python3 render/render.py <archivo.html> [--ancho 1080] [--alto 1350]

Cada <section class="slide"> del HTML se exporta como un PNG
(<nombre>-01.png, <nombre>-02.png...). Si no hay slides, se exporta la página
completa como <nombre>.png. Los PNG se guardan junto al HTML.
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def render(html: Path, ancho: int, alto: int) -> list[Path]:
    salidas = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(viewport={"width": ancho, "height": alto}, device_scale_factor=1)
        pagina.goto(html.resolve().as_uri())
        pagina.wait_for_load_state("networkidle")
        pagina.evaluate("document.fonts.ready")
        slides = pagina.query_selector_all("section.slide")
        if slides:
            for i, slide in enumerate(slides, 1):
                destino = html.with_name(f"{html.stem}-{i:02d}.png")
                slide.screenshot(path=str(destino))
                salidas.append(destino)
        else:
            destino = html.with_suffix(".png")
            pagina.screenshot(path=str(destino))
            salidas.append(destino)
        navegador.close()
    return salidas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--ancho", type=int, default=1080)
    ap.add_argument("--alto", type=int, default=1350)
    args = ap.parse_args()
    for s in render(args.html, args.ancho, args.alto):
        print(s)
