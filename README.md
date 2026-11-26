# Divulgando Ecos

Repositorio de difusión: borradores, publicaciones y recursos para redes. Una voz, muchos ecos.

Dos voces, un mismo flujo:

| Carpeta     | Para qué                                              |
|-------------|-------------------------------------------------------|
| `personal/` | Contenido propio (LinkedIn, X, blog, etc.)            |
| `secid/`    | Contenido para publicar como parte de SECID           |
| `plantillas/` | Formatos reutilizables de post                      |
| `assets/`   | Imágenes, gráficos y material visual por voz          |

## Flujo

1. Escribe en `<voz>/borradores/` con nombre `AAAA-MM-DD-tema.md`.
2. Usa una plantilla de `plantillas/` como base.
3. Revisa con el juez (`python3 herramientas/centro.py`) y abre PR; el job **Revisar posts** corre lo mismo.
4. Al publicar, muévelo a `<voz>/publicados/`, agrega el `link` y, a los 7 días, las `metricas`.

Un mismo tema puede tener versión personal y versión SECID: crea ambos archivos con el mismo slug.

## Videos (reels)

Los `.mp4` no se versionan (están en `.gitignore`): se regeneran desde el código.

```bash
cd reels
npx remotion render src/index.jsx <IdComposicion> ../<voz>/borradores/<post>/<archivo>.mp4
```

Para revisarlos, arrastra el `.mp4` a un comentario del PR: GitHub lo reproduce ahí mismo.

## Centro de difusión (cola, juez y calendario)

`herramientas/centro.py` lee todos los `post.md`, los revisa con reglas de `estrategia/pilares.md`,
`marca/*.md` y `difusion.json`, y da un veredicto por post:

| Veredicto | Significa |
|---|---|
| 🟢 PUBLICAR | `listo` y sin observaciones |
| 🟡 REVISAR | tiene avisos que alguien debe mirar (o está `en-revision`) |
| 🔴 BLOQUEADO | no debe salir: cifras sin fuente, checklist sin marcar, marca mezclada, texto demasiado largo, archivo faltante… |
| ⚪ EN PROCESO | idea o borrador |

También revisa el calendario: ritmo lunes/miércoles/viernes, nunca dos posts seguidos del mismo pilar,
máximo 3 por semana y 1 de actualidad, y posts vencidos.

```bash
python3 herramientas/centro.py                          # resumen en consola
python3 herramientas/centro.py --html centro.html       # tablero visual (abrir en el navegador)
python3 herramientas/centro.py --brief                  # huecos + lo reciente + desempeño, para proponer temas
```

En cada PR, `.github/workflows/revisar-posts.yml` corre el juez, deja el reporte en el resumen del job
y falla si un post `listo` tiene bloqueos.

## Herramientas de escritura y comandos de Claude

Adaptadas al español de [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
(MIT, ver `herramientas/LICENCIAS.md`). Todo corre local, sin red.

| Herramienta | Para qué |
|---|---|
| `herramientas/gancho.py` | Califica y ordena ganchos (16 fórmulas de divulgación en `ganchos.json`) |
| `herramientas/ritmo.py` | Hoja de ritmo de `reels/guiones/<Reel>.json` (usa la duración real de `voz.json` si existe) |
| `herramientas/texto.py` | Revisa el texto de Instagram/LinkedIn como se ve en el feed antes de "… más" |
| `herramientas/humano.py` | Quita invisibles y muletillas de IA; califica qué tan humano suena |

`centro.py` ya corre `texto.py` y `humano.py` sobre cada post.

Comandos para Claude Code (en `.claude/skills/`): `/ecos-semana` (plan y temas),
`/ecos-reel` (guion), `/ecos-carrusel`, `/ecos-texto` (captions) y `/ecos-humano`.
Ninguno publica: escriben, y tú publicas.
