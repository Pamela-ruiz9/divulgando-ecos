# Estrategia de contenido — marca personal "Ecos"

> SECiD va por separado: solo comunicaciones institucionales (eventos, avisos), cuando haya algo que comunicar. No cuenta dentro de los 3 posts semanales.

## Pilares

| Pilar | Qué cubre | Peso |
|---|---|---|
| **Dinero con datos** | Finanzas personales, inflación, ahorro, crédito, economía de México | ~1/semana |
| **México en datos** | Demografía, sociedad, datos abiertos (INEGI, CONAPO, Banxico) | ~1/semana |
| **Ciencia curiosa** | Probabilidad, matemáticas, neurociencia, ciencia en general | ~1/semana |
| **Detrás de los datos** | Trabajo de actuaria/científica de datos, herramientas, aprendizajes, opinión | 1 cada 2 semanas (sustituye un slot) |

## Ritmo semanal

| Día | Formato | Rol |
|---|---|---|
| Lunes | Carrusel (5–8 slides) | Profundidad: se guarda y se comparte |
| Miércoles | Imagen con un dato | Rápido; ideal para actualidad |
| Viernes | Reel (15–30 s) | Alcance: gente nueva |

## Reglas de equilibrio

1. **2 atemporales + 1 de actualidad** por semana. Los atemporales se producen por adelantado (banco de reserva).
2. **80/20**: 80 % aporta conocimiento; 20 % tu voz (opinión, carrera, detrás de cámaras).
3. **Nunca dos posts seguidos del mismo pilar.**
4. **Toda cifra verificada** (ver sección siguiente); gráficas ilustrativas rotuladas como tales.
5. **Puente con SECiD**: cuando SECiD tenga evento, se comparte desde la cuenta personal con voz propia y marca "Ecos" (nunca la plantilla SECiD).

## Verificación de datos (no negociable)

No difundimos fake news. Ningún post sale con una cifra que no podamos sustentar.

1. **Fuente oficial o creíble**: INEGI, CONAPO, Banxico, CONEVAL, SHCP, Banco Mundial, ONU, OCDE, artículos revisados por pares. Nada de cifras de memoria, notas virales o fuentes sin autor.
2. **Código reproducible cuando hay cálculo o gráfica**: los datos se descargan con un script en `datos/scripts/` (vía API o archivo oficial) y las gráficas se generan desde esos datos, no a mano.
3. **Coherencia**: antes de marcar `listo`, se recalculan las cifras y se comparan con *todo* lo que las menciona (texto IG/LinkedIn, gráfica, guion, narración y subtítulos), incluidos los redondeos ("un tercio", "uno de cada cuatro").
4. **Citar en el post**: fuente, indicador o tabla, fecha de consulta y script en la sección `## Fuentes` del `post.md`; y fuente visible en la pieza.
5. **Distinguir**: dato observado vs. estimación vs. proyección; si hay fuentes que difieren (p. ej. CONAPO vs. ONU), anotarlo en `## Notas de verificación`.
6. **Si no se puede verificar, no se publica** (o se reformula sin la cifra).

## Propuesta semanal de temas (para la rutina automática)

Cada semana proponer **5–8 temas** para elegir 3, indicando: pilar, formato sugerido, gancho en una línea, fuente principal y si es actualidad o atemporal. Respetar las reglas de arriba considerando lo publicado las 2 semanas anteriores (`personal/publicados/`).

Fechas útiles (actualidad): publicación de inflación INEGI (quincenal), decisiones de tasa de Banxico, aguinaldo (dic), cuesta de enero, declaración anual (abr), Día de Muertos (esperanza de vida), regreso a clases, efemérides científicas.
