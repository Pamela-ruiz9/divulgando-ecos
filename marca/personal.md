# Marca personal — "Ecos"

> Voz personal de Pamela Ruiz. **Nunca mezclar con SECiD** (ver `secid.md`):
> sin naranja, sin dorado, sin hexágonos, sin Poppins.

## Quién habla
Pamela Ruiz — actuaria y científica de datos (CDMX).
Intereses: ciencia, matemáticas, finanzas, demografía, neurociencia, tecnología, arte y diseño.

## Tono
Primera persona ("yo", "te cuento"). Cálido, curioso, claro.
Explica lo complejo con ejemplos cotidianos. Rigor: toda cifra con fuente.

## Colores
| Rol | Hex | Uso |
|---|---|---|
| Fondo oscuro | `#0B1320` | Fondo principal (posts, reels) |
| Primario | `#023E8A` | Bloques, barras, títulos sobre claro |
| Acento | `#06DBD1` | Resaltados, cifra clave, línea de datos principal |
| Claro | `#CDE1F8` | Texto secundario sobre oscuro, fondos claros |
| Texto | `#F5F8FC` | Texto principal sobre oscuro |
| Gris | `#6B7A90` | Notas, fuentes, ejes de gráficas |

| Azul cielo | `#7EC8F2` | Paso intermedio en degradados |
| Rosa | `#F48FB1` | Acento cálido, segunda serie en gráficas |
| Rosa intenso | `#D9488F` | Énfasis puntual (una palabra, un dato) |
| Rosa pálido | `#FCE4EF` | Fondos claros, tarjetas |

Variante clara (LinkedIn/documentos): fondo `#F5F8FC`, texto `#0B1320`, primario `#023E8A`, acento `#06A8A0` (cian más oscuro para contraste).

> Los rosas deben ser rosa/fucsia frío, **nunca coral, salmón ni naranja** (eso es de SECiD).

## Degradados (sello de la marca)
Los degradados son el recurso visual principal. Usarlos en fondos, títulos grandes y formas; **nunca** detrás de texto pequeño ni dentro de gráficas de datos (ahí, colores planos).

| Nombre | CSS | Uso |
|---|---|---|
| **Profundo** | `linear-gradient(160deg, #0B1320 0%, #023E8A 100%)` | Fondo base de posts y reels |
| **Océano** | `linear-gradient(135deg, #023E8A 0%, #7EC8F2 55%, #06DBD1 100%)` | Portadas, bloques destacados |
| **Amanecer** | `linear-gradient(135deg, #023E8A 0%, #7EC8F2 50%, #F48FB1 100%)` | Portadas, títulos, cierre de carrusel |
| **Aurora** | `linear-gradient(120deg, #06DBD1 0%, #7EC8F2 40%, #F48FB1 75%, #D9488F 100%)` | Texto grande en degradado, líneas, ondas |
| **Bruma** | `linear-gradient(180deg, #F5F8FC 0%, #CDE1F8 60%, #FCE4EF 100%)` | Fondo de la variante clara |

Reglas:
- Un degradado protagonista por pieza; el resto, colores planos.
- Texto sobre degradado: blanco `#F5F8FC` con peso ≥ 600, o sobre una tarjeta semitransparente `rgba(11,19,32,.55)`.
- Gráficas con **una sola serie**: línea/barras en cian `#06DBD1`, anotaciones en rosa `#F48FB1`.
- Gráficas con **varias series** (fondo oscuro), en este orden fijo — validado para daltonismo con el validador de `dataviz`:
  1. `#0FA8A2` cian  2. `#6A6FF0` azul-violeta  3. `#E05A9E` rosa  · contexto: gris `#6B7A90`.
  El cian y el rosa **nunca van juntos sin el azul en medio** (se confunden con deuteranopía).

## Tipografía (Google Fonts)
- Títulos: **Quicksand** (600–700)
- Texto: **Nunito Sans**
- Cifras/código: **JetBrains Mono**

## Motivo gráfico
**Ondas concéntricas / ecos** con trazo en degradado (Aurora) que se expanden desde un punto, sobre el fondo Profundo; partículas sutiles.
Avatar: `assets/personal/avatar.png` (ilustración, fondo negro).

Variación del motivo (para que no se vea repetido):
- Posición: esquina superior derecha, esquina inferior izquierda, o **naciendo de un elemento con significado** (la cifra clave, un punto de la gráfica).
- Tamaño e intensidad: grande y tenue como fondo, o pequeño y nítido como acento.
- En reels: las ondas se animan (se expanden) en las transiciones.
- Regla: el motivo aparece en toda pieza, pero no siempre igual; alternar posiciones entre posts consecutivos.

Firma: **no** poner el usuario de Instagram en las imágenes.

## Voz (reels)
- Narración: Piper, voz **es_AR-daniela-high** (local, gratis). Generar con `render/voz.py` a partir de `reels/guiones/<Reel>.json`.
- Escribir números con letra en el guion ("dos mil cincuenta"); en subtítulos, con cifras.
- Subtítulos solo cuando la voz dice algo que no está ya escrito en pantalla.

## Redes
- Instagram: (usuario fuera del repo a propósito)
- LinkedIn: /in/pamela-ruíz-512834231
- Web: https://pamela-ruiz9.github.io
