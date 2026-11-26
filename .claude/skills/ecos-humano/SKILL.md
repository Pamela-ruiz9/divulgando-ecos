---
name: ecos-humano
description: >-
  Quita la huella de texto generado (caracteres invisibles, muletillas de IA,
  estructuras de plantilla) y califica qué tan humano suena un texto en español.
  Úsalo antes de entregar cualquier texto o guion, o cuando Pamela diga
  "humanízalo", "suena a IA" o "suena a ChatGPT".
---

# ecos-humano

Adaptado de `ig-human` (instagram-agent-skill, MIT) al español.

```bash
python3 herramientas/humano.py borrador.txt                          # diagnóstico
python3 herramientas/humano.py borrador.txt --corregir -o limpio.txt # aplica cambios
python3 herramientas/humano.py <post>/post.md --seccion Instagram
```

Usa `herramientas/muletillas.json`, editable: si Pamela usa una palabra a
propósito, se quita de la lista.

## Qué hace sola
Borra caracteres invisibles (espacios de ancho cero, marcas de dirección, etc.),
respetando los que unen emojis compuestos.

## Qué sugiere (se aplica con `--corregir`)
Muletillas: "cabe destacar que", "en el mundo actual", "sumergirnos en",
"fascinante", "crucial", "un viaje", "sígueme para más"…

## Qué tienes que reescribir a mano
- "No es solo X, es Y" / "No solo X, sino también Y"
- Preguntas retóricas de una línea ("¿El resultado?")
- Tríadas perfectas, listas con emoji en cada línea, emojis de plantilla (🚀🔥💡✨🎯)
- Exceso de rayas (—). Ojo: en español la raya es correcta; solo se marca si abunda.
- Frases todas del mismo largo

## Señales (0–100, más alto = más humano)
VARIEDAD (largo de frases), CONCRECIÓN (cifras y nombres), MULETILLAS, HUELLA
(invisibles, rayas), VOZ (primera y segunda persona, sin estructuras de plantilla).
PASA con 70+ y ninguna señal bajo 55.

## Honestidad
Son heurísticas locales; no es un detector de IA, no llama a ninguno y no promete
pasar uno. Nunca digas que un texto es "indetectable".

## Orden
1. `humano.py` → 2. reescribe lo marcado → 3. vuelve a correrlo (dos rondas es
normal; cinco significa que el borrador hay que rehacerlo) → 4. muestra el texto
limpio junto con el puntaje, nunca solo el puntaje.
