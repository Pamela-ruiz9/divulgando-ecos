---
name: ecos-semana
description: >-
  Planea la semana de Ecos: propone 5–8 temas para los huecos del calendario
  (lunes carrusel, miércoles imagen, viernes reel), con pilar, gancho y fuente,
  respetando las reglas de equilibrio. Úsalo cuando Pamela diga "planea mi
  semana", "qué publico", "propuesta de temas" o "no sé de qué hablar".
---

# ecos-semana

Adaptado de `ig-plan` (instagram-agent-skill, MIT) a `estrategia/pilares.md`.

## Entrada

```bash
python3 herramientas/centro.py --brief
```

Da los huecos de las próximas 3 semanas, lo publicado/programado (−2 a +3
semanas) y el desempeño por pilar y formato (de las `metricas` de lo publicado).
Lee también `estrategia/pilares.md` (pilares, ritmo, reglas, fechas útiles).

Pregunta una sola vez, agrupado: ¿qué pasó esta semana (un dato que viste, una
pregunta que te hicieron, algo del trabajo)? Ahí están los mejores posts.

## Reglas (de pilares.md)

- 3 posts por semana: lunes carrusel, miércoles imagen, viernes reel.
- 2 atemporales + 1 de actualidad. Nunca dos seguidos del mismo pilar.
- 80 % conocimiento / 20 % voz propia.
- Revisa fechas de actualidad: inflación INEGI (quincenal), decisiones de
  Banxico, aguinaldo, cuesta de enero, declaración anual, etc.
- **Cada tema con fuente oficial identificada.** Si no hay fuente, no es tema.

## Para cada propuesta

Un ángulo, no un tema ("La inflación" no es plan; "Lo que de verdad subió en tu
súper este año, según el INPC" sí):

```
SEMANA DEL 30 NOV
LUN  CARRUSEL  Dinero con datos  · atemporal  · #4 El mito
     «¿Ahorrar en Cetes o en la cuenta del banco?» · Fuente: Banxico (tasas), CONDUSEF
MIE  IMAGEN    Ciencia curiosa   · atemporal  · #10 Probabilidad
     «23 personas, 50 % de cumpleaños compartido» · Fuente: cálculo propio (script)
VIE  REEL      México en datos   · actualidad · #11 Fecha límite
     «La inflación de noviembre: qué subió» · Fuente: INEGI INPC (fecha en el calendario de difusión de INEGI)
+ 2–5 alternativas para el banco de reserva
```

## Al aprobar

Por cada tema aprobado crea `personal/borradores/AAAA-MM-DD-slug/post.md` desde
`plantillas/post.md` con `estado: idea`, `pilar`, `formato`, `tipo` y
`publicar_el`. Corre `python3 herramientas/centro.py` para confirmar que el
calendario no rompe reglas. Nada se programa ni se publica.
