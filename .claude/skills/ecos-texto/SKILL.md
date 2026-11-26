---
name: ecos-texto
description: >-
  Escribe y revisa los textos de un post de Ecos (secciones ## Instagram y
  ## LinkedIn del post.md): la primera línea que sobrevive al "… más", una sola
  petición, fuente, hashtags y términos de búsqueda. Úsalo cuando Pamela pida el
  caption, la descripción, el texto de LinkedIn o "revisa los textos".
---

# ecos-texto

Adaptado de `ig-caption` (instagram-agent-skill, MIT).

```bash
python3 herramientas/texto.py <voz>/borradores/<post>/post.md                     # Instagram
python3 herramientas/texto.py <post>/post.md --seccion LinkedIn
python3 herramientas/texto.py <post>/post.md --buscar "pensiones,demografía México"
python3 herramientas/humano.py <post>/post.md --seccion Instagram
```

`texto.py` muestra lo que se ve en el feed antes de "… más" (125 caracteres en
Instagram, ~210 en LinkedIn). Léelo antes que todo lo demás.

## Primero: ¿qué trabajo hace este texto?

- **A. El video ya enganchó (reel).** El texto no compite con el gancho: da el
  contexto, la fuente, los términos de búsqueda y la petición.
- **B. El texto es el gancho (imagen, carrusel).** La primera línea funciona
  como gancho: concreta, corta, y si se corta, que sea en suspenso, no a media idea.

Di cuál estás escribiendo.

## Forma

```
Línea 1   lo visible. Nunca saludo, hashtag ni emoji como primer carácter.
Cuerpo    párrafos cortos, uno de aire entre ellos. Aquí van las palabras que la gente busca.
Petición  UNA: pregunta concreta ("¿Tú cómo te imaginas el México de 2050?") o guardar.
Fuente    "Fuente: …" en el texto cuando hay cifras (regla de pilares.md).
Hashtags  hasta 5 en Instagram, específicos, al final. Nada de #viral, #parati.
```

LinkedIn: misma lógica, tono más profesional, el ángulo de actuaria/científica de
datos, sin emojis de lista, hashtags al final (≤ 5).

## Reglas

- **Sin links en Instagram**: no son clicables. Bio o primer comentario.
- **Una petición**: dos es igual a ninguna (`texto.py` las cuenta).
- **Términos de búsqueda como frases normales** ("pirámide poblacional de México"),
  no como hashtags.
- **Texto alternativo** para carruseles e imágenes: una o dos frases.
- **Las cifras del texto deben coincidir** con la pieza y con `datos/`.

## Ciclo

1. Decide A o B y dilo.
2. Escribe en el `post.md` (secciones `## Instagram`, `## LinkedIn`).
3. `humano.py` sobre cada sección; reescribe a mano las estructuras marcadas.
4. `texto.py` con los términos de búsqueda. Corrige cada FALLA; decide en voz alta cada AVISO.
5. `python3 herramientas/centro.py` para ver el veredicto del juez.
6. Entrega:

```
TEXTO LISTO
trabajo:   B, la primera línea es el gancho
visible:   118 de 125 caracteres antes del corte
petición:  una, pregunta
fuente:    en el texto y en ## Fuentes
hashtags:  4
humano:    86 PASA · texto.py: LISTO
```

Nada se publica: Pamela copia y pega.
