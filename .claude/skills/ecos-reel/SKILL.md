---
name: ecos-reel
description: >-
  Escribe un reel de Ecos a partir de una idea: tres ganchos calificados, el guion
  hablado en reels/guiones/<Reel>.json, el texto en pantalla y la hoja de ritmo,
  con cifras verificadas. Úsalo cuando Pamela pida un reel, un guion, un gancho,
  una narración, "haz un reel de X" o vaya a preparar el video del viernes.
---

# ecos-reel

Adaptado de `ig-reel` (instagram-agent-skill, MIT). Convierte una idea en un reel
que la gente termina de ver, sin romper la regla de oro del repo: **toda cifra
verificada**.

```bash
python3 herramientas/gancho.py ganchos.txt                       # ordena tus opciones de gancho
python3 herramientas/ritmo.py reels/guiones/<Reel>.json --meta 20 # hoja de ritmo
python3 herramientas/humano.py guion.txt                          # que suene dicho, no escrito
```

## Antes de escribir

1. Lee `marca/personal.md` (voz, colores, reglas de la voz Piper) y
   `estrategia/pilares.md` (pilares y verificación de datos).
2. Lee `herramientas/ganchos.json`: 16 fórmulas con plantilla, versión en
   pantalla, para qué sirve y cómo se arruina.
3. **Consigue el dato antes que el gancho.** Si la idea lleva cifras, deben salir
   de un script en `datos/scripts/` con fuente oficial. Si todavía no existe, ese
   es el primer paso. Nunca inventes una cifra, ni de ejemplo: deja `{{cifra}}` y
   avisa.
4. Si la idea es vaga, haz una sola pregunta agrupada: qué dato, de qué fuente,
   qué cambia para quien lo ve.

## La forma (15–30 s de narración)

```
0–3 s     GANCHO    la cifra o el contraste. Frase hablada y texto en pantalla, por separado.
3–7 s     LO QUE ESTÁ EN JUEGO   por qué le importa a quien ve. Una frase.
7 s–…     CUERPO    una idea por frase; la escena cambia en cada frase.
últimos 3 s  CIERRE  cumple lo que prometió el gancho y UNA petición (pregunta o guardar).
última línea EL LOOP repite una palabra del gancho para que la repetición caiga natural.
```

## El ciclo

1. **Tres ganchos de fórmulas distintas** (no tres versiones de una). Para cada
   uno: frase hablada + texto en pantalla (≤ 6 palabras).
2. **Califícalos** con `gancho.py`. Muestra el ranking. Bajo 50: no hay gancho todavía.
3. **Escribe el guion** en `reels/guiones/<Reel>.json` con el formato de
   `render/voz.py`: `{"reel": "...", "frases": [{"id", "texto", "subtitulo"}]}`.
   - Números **con letra** en `texto` ("dos mil cincuenta"); con cifras en `subtitulo`.
   - `subtitulo: false` cuando lo dicho ya está escrito en pantalla.
   - Frases cortas, como habla Pamela: primera persona, cálida, sin rodeos.
4. **Ritmo**: `ritmo.py <guion> --meta <s>`. Corrige gancho > 3.5 s, frases > 4.5 s,
   tramos sin dato y cierre sin eco. Si ya hay narración, usa la duración real.
5. **Humaniza**: pasa el texto de las frases por `humano.py`.
6. **Coherencia** (no negociable): la cifra debe ser la misma en `datos/`, guion,
   subtítulos, texto en pantalla, `post.md` y gráfica, incluidos los redondeos.
7. Entrega:

```
REEL LISTO
gancho:     #2 Antes y después, 78 FUERTE
duración:   18.4 s en 7 frases (estimada / real)
pantalla:   5 tarjetas
humano:     84 PASA
datos:      datos/<archivo>.csv  ←  datos/scripts/<script>.py
siguiente:  python3 render/voz.py reels/guiones/<Reel>.json, luego la composición en reels/src/reels/
            y /ecos-texto para el post.md
```

Nunca publiques. Pamela revisa el `.mp4` en el PR y lo sube ella.

## Texto en pantalla

- 6 palabras o menos por tarjeta; la del gancho visible desde el frame 1.
- Zona segura en 1080×1920: nada arriba de y=230 ni debajo de y=1440; deja libres
  los 230 px de la derecha (ahí va la interfaz de Instagram).
- Fuente visible en pantalla (regla de pilares.md), en gris `#6B7A90`, pequeña.

## Reglas

- **Una idea por reel.** Si hay dos, son dos reels.
- **Cifras, no adjetivos**, y siempre con fuente.
- **Sin introducción**: nada de "hola", "en este video", nombre ni logo al inicio.
- **Distingue** dato observado, estimación y proyección también al hablar ("para 2050, según proyecciones…").
