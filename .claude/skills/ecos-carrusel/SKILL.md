---
name: ecos-carrusel
description: >-
  Arma un carrusel de Ecos (el post de los lunes): portada que gana el deslizar,
  texto por slide, slide de resumen y los PNG de 1080×1350 con la marca. Úsalo
  cuando Pamela pida un carrusel, slides, "conviértelo en carrusel" o tenga una
  idea con pasos o lista.
---

# ecos-carrusel

Adaptado de `ig-carousel` (instagram-agent-skill, MIT).

## ¿Carrusel o reel?

Carrusel cuando la idea tiene **secuencia y se relee**: pasos, una explicación
por partes, antes/después, una lista que vale la pena guardar. Reel cuando tiene
movimiento o un desenlace que hay que ver. Una sola afirmación no es ninguno de
los dos: pásala a `/ecos-reel`.

## Estructura (6–10 slides)

```
1        PORTADA   el gancho, ≤ 6 palabras, legible en miniatura. Una línea de promesa debajo.
2        LO QUE ESTÁ EN JUEGO   una frase. Instagram puede mostrar el carrusel empezando aquí: debe sostenerse solo.
3 a N    UNA IDEA POR SLIDE: título de 3–7 palabras y máximo 25 palabras debajo.
N+1      RESUMEN   todo en una lista: es la slide que se captura y se comparte.
ÚLTIMA   CIERRE    una petición + fuente(s).
```

## Reglas de la marca Ecos (marca/personal.md)

- Fondo degradado **Profundo**; un solo degradado protagonista por pieza.
- Títulos Quicksand 600–700, texto Nunito Sans, cifras JetBrains Mono. Texto ≥ 32 px.
- Motivo de ondas en todas las slides, **variando posición** entre slides.
- Gráficas con colores planos (serie única en cian `#06DBD1`; varias series en el orden fijo validado).
- Gráficas ilustrativas rotuladas como tales; **fuente visible** en la slide del dato.
- Numera las slides (3/8). **Sin** usuario de Instagram en las piezas (el juez lo bloquea).
- Deja libres 120 px en cada borde de la portada (recorte de la cuadrícula).

## Construcción

1. Primero el texto slide por slide como lista numerada, para que Pamela lo
   apruebe antes de diseñar. Gancho de portada calificado con `herramientas/gancho.py`.
2. Luego `<voz>/borradores/<post>/carrusel.html` con una `<section class="slide">`
   por slide (1080×1350). Toma como base los estilos de
   `personal/borradores/2026-11-25-black-friday/imagen.html`.
3. Exporta: `python3 render/render.py <post>/carrusel.html --nombre slide`
   (un PNG por slide: `slide-01.png`, `slide-02.png`…) y lista los archivos en
   `archivos:` del `post.md`.
4. Texto del post con `/ecos-texto` (trabajo B) y alt text de la portada.
5. `python3 herramientas/centro.py` para el veredicto.

```
CARRUSEL · 8 slides
1 PORTADA  ¿DESCUENTO REAL?
           Lo que dicen los datos del Black Friday.
2          175 productos "en oferta". Ninguno en su precio más bajo del año.
…
7 RESUMEN  3 hábitos antes de comprar
8 CIERRE   ¿Tú revisas el historial de precios? · Fuente: Which? (2025)
```

Nada se sube: Pamela publica.
