"""Centro de difusión: cola, revisión automática ("juez") y calendario de posts.

Inspirado en el Social Command Center de watchboard, adaptado a este repo:
aquí no hay LLM ni API de redes; el juez son reglas deterministas sacadas de
`estrategia/pilares.md`, `marca/*.md` y `difusion.json`.

Uso:
    python3 herramientas/centro.py                 # resumen en consola
    python3 herramientas/centro.py --html centro.html --md centro.md
    python3 herramientas/centro.py --brief         # contexto para la propuesta semanal de temas
    python3 herramientas/centro.py --ci            # sale con error si un post `listo` tiene bloqueos

Veredictos (equivalentes a PUBLISH / REVIEW / HOLD / KILL de watchboard):
    PUBLICAR    listo y sin observaciones
    REVISAR     listo o en revisión, con avisos que alguien debe mirar
    BLOQUEADO   tiene al menos un bloqueo (no debe salir así)
    EN PROCESO  idea o borrador (se muestran sus pendientes, no bloquea CI)
    PUBLICADO / DESCARTADO
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = json.loads((RAIZ / "difusion.json").read_text(encoding="utf-8"))
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

RE_HASHTAG = re.compile(r"(?<![\w&])#([^\W\d_]\w*)")
RE_HEX = re.compile(r"^(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
RE_CIFRA = re.compile(r"\d+(?:[.,]\d+)?\s*%|\b\d{2,}(?:[.,]\d+)*\b")
RE_COMENTARIO = re.compile(r"<!--.*?-->", re.S)
# @usuario de redes, sin confundir con reglas de CSS (@media, @import…) ni correos.
RE_USUARIO = re.compile(
    r"(?<![\w.])@(?!(?:media|import|font-face|keyframes|supports|page|charset|layer|container|property|namespace)\b)"
    r"([A-Za-z0-9_](?:[A-Za-z0-9_.]{1,28}[A-Za-z0-9_]))")


@dataclass
class Post:
    ruta: Path
    meta: dict
    secciones: dict[str, str]
    obs: list[tuple[str, str]] = field(default_factory=list)  # (nivel, mensaje)

    @property
    def carpeta(self) -> Path:
        return self.ruta.parent if self.ruta.name == "post.md" else self.ruta.parent

    @property
    def rel(self) -> str:
        return str(self.ruta.relative_to(RAIZ))

    @property
    def estado(self) -> str:
        return str(self.meta.get("estado") or "borrador")

    @property
    def fecha(self) -> dt.date | None:
        return a_fecha(self.meta.get("publicar_el") or self.meta.get("fecha_publicacion"))

    @property
    def bloqueos(self) -> list[str]:
        return [m for n, m in self.obs if n == "bloqueo"]

    @property
    def avisos(self) -> list[str]:
        return [m for n, m in self.obs if n == "aviso"]

    @property
    def veredicto(self) -> str:
        if self.estado == "publicado":
            return "PUBLICADO"
        if self.estado == "descartado":
            return "DESCARTADO"
        if self.estado in ("idea", "borrador"):
            return "EN PROCESO"
        if self.bloqueos:
            return "BLOQUEADO"
        if self.avisos or self.estado == "en-revision":
            return "REVISAR"
        return "PUBLICAR"


def a_fecha(v) -> dt.date | None:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str) and v.strip():
        try:
            return dt.date.fromisoformat(v.strip()[:10])
        except ValueError:
            return None
    return None


def limpiar(texto: str) -> str:
    return RE_COMENTARIO.sub("", texto).strip()


def leer_post(ruta: Path) -> Post | None:
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        return None
    _, fm, cuerpo = texto.split("---", 2)
    meta = yaml.safe_load(fm) or {}
    secciones: dict[str, str] = {}
    actual = None
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            actual = linea[3:].strip()
            secciones[actual] = ""
        elif actual is not None:
            secciones[actual] += linea + "\n"
    return Post(ruta, meta, {k: limpiar(v) for k, v in secciones.items()})


def encontrar_posts() -> list[Post]:
    posts = []
    for voz in CONFIG["voces"]:
        for sub in ("borradores", "publicados"):
            base = RAIZ / voz / sub
            if not base.exists():
                continue
            for ruta in sorted(list(base.glob("*/post.md")) + list(base.glob("*.md"))):
                p = leer_post(ruta)
                if p:
                    posts.append(p)
    return posts


def hashtags(texto: str) -> list[str]:
    return [h for h in RE_HASHTAG.findall(texto) if not RE_HEX.match(h)]


# ── Juez: reglas por post ──

def revisar_post(p: Post, hoy: dt.date) -> None:
    m, add = p.meta, p.obs.append
    voz = m.get("voz")
    avanzado = p.estado in ("en-revision", "listo", "publicado")

    for campo in ("titulo", "voz", "plataformas", "estado"):
        if not m.get(campo):
            add(("bloqueo", f"Falta `{campo}` en el front matter"))
    if p.estado not in CONFIG["estados"]:
        add(("aviso", f"Estado desconocido `{p.estado}` (válidos: {', '.join(CONFIG['estados'])})"))
    if voz and voz not in CONFIG["voces"]:
        add(("bloqueo", f"Voz desconocida `{voz}`"))
    if voz == CONFIG["ritmo"]["voz"]:
        if not m.get("pilar"):
            add(("aviso", "Sin `pilar` (necesario para equilibrar el calendario)"))
        elif m["pilar"] not in CONFIG["pilares"]:
            add(("aviso", f"Pilar `{m['pilar']}` no está en estrategia/pilares.md"))
        if m.get("formato") and m["formato"] not in CONFIG["formatos"]:
            add(("aviso", f"Formato `{m['formato']}` desconocido"))
    if avanzado and not p.fecha:
        add(("bloqueo", "Sin `publicar_el`"))

    # Textos por plataforma: existencia, longitud, hashtags, fuente visible.
    hay_cifras = False
    for plat in m.get("plataformas") or []:
        cfg = CONFIG["plataformas"].get(str(plat).lower())
        if not cfg:
            add(("aviso", f"Plataforma `{plat}` sin reglas en difusion.json"))
            continue
        texto = p.secciones.get(cfg["seccion"], "")
        if not texto:
            add(("bloqueo" if avanzado else "aviso", f"Falta la sección `## {cfg['seccion']}`"))
            continue
        n = len(texto)
        if n > cfg["max_caracteres"]:
            add(("bloqueo", f"{cfg['seccion']}: {n}/{cfg['max_caracteres']} caracteres"))
        tags = hashtags(texto)
        if len(tags) > cfg["max_hashtags"]:
            add(("bloqueo", f"{cfg['seccion']}: {len(tags)} hashtags (máx. {cfg['max_hashtags']})"))
        elif len(tags) > cfg["hashtags_recomendados"]:
            add(("aviso", f"{cfg['seccion']}: {len(tags)} hashtags (recomendado ≤ {cfg['hashtags_recomendados']})"))
        if RE_CIFRA.search(re.sub(r"#\w+", "", texto)):
            hay_cifras = True
            if "fuente" not in texto.lower():
                add(("aviso", f"{cfg['seccion']}: tiene cifras y no nombra la fuente (¿está visible en la pieza?)"))

    # Verificación de datos (no negociable).
    fuentes = p.secciones.get("Fuentes", "")
    if hay_cifras and not fuentes:
        add(("bloqueo", "Hay cifras y `## Fuentes` está vacía"))
    if fuentes and re.search(r"datos/scripts/|https?://", fuentes) is None:
        add(("aviso", "Fuentes sin enlace ni script reproducible"))
    notas = p.secciones.get("Notas de verificación", "")
    pendientes = re.findall(r"- \[ \] (.+)", notas)
    if pendientes and p.estado in ("listo", "publicado"):
        for item in pendientes:
            add(("bloqueo", f"Checklist sin marcar: {item.strip()}"))
    if hay_cifras and avanzado and not notas:
        add(("aviso", "Sin `## Notas de verificación`"))

    # Archivos y marca.
    for nombre in m.get("archivos") or []:
        if not (p.carpeta / nombre).exists():
            if Path(nombre).suffix in (".mp4", ".mov", ".webm"):
                if not m.get("fuente_reel"):
                    add(("aviso", f"`{nombre}` no está y no hay `fuente_reel` para regenerarlo"))
            else:
                add(("bloqueo" if avanzado else "aviso", f"Falta el archivo `{nombre}`"))
    for clave in ("fuente_reel", "datos"):
        if m.get(clave) and not (RAIZ / m[clave]).exists():
            add(("bloqueo", f"`{clave}` apunta a `{m[clave]}`, que no existe"))
    revisar_marca(p, voz)

    # Ciclo de vida.
    if p.fecha and p.fecha < hoy and p.estado not in ("publicado", "descartado"):
        add(("aviso", f"Vencido: debía salir el {p.fecha}"))
    if p.estado == "publicado":
        if not m.get("link"):
            add(("aviso", "Publicado sin `link`"))
        if "/borradores/" in p.rel:
            add(("aviso", "Publicado pero sigue en `borradores/`"))
        if not m.get("metricas"):
            add(("aviso", "Sin `metricas` (alcance, guardados…): alimentan la propuesta semanal"))


def revisar_marca(p: Post, voz: str | None) -> None:
    reglas = CONFIG["prohibido"].get(voz or "", {})
    if not reglas:
        return
    archivos = [f for f in p.carpeta.iterdir() if f.suffix in (".html", ".css", ".jsx", ".js")]
    if p.meta.get("fuente_reel"):
        archivos.append(RAIZ / p.meta["fuente_reel"])
    for f in archivos:
        if not f.exists():
            continue
        contenido = f.read_text(encoding="utf-8", errors="ignore")
        if reglas.get("sin_usuarios_en_piezas"):
            for usuario in sorted(set(RE_USUARIO.findall(contenido))):
                p.obs.append(("bloqueo", f"`@{usuario}` aparece en {f.name} (la firma no va en las piezas)"))
        for s in reglas.get("marca_ajena", []):
            if s.lower() in contenido.lower():
                p.obs.append(("bloqueo", f"{f.name} usa `{s}`, que es de la otra marca"))


# ── Juez: reglas de calendario (entre posts) ──

def lunes_de(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def revisar_calendario(posts: list[Post]) -> list[str]:
    ritmo = CONFIG["ritmo"]
    activos = sorted(
        (p for p in posts if p.meta.get("voz") == ritmo["voz"] and p.fecha and p.estado != "descartado"),
        key=lambda p: p.fecha,
    )
    globales = []
    for a, b in zip(activos, activos[1:]):
        if a.meta.get("pilar") and a.meta.get("pilar") == b.meta.get("pilar"):
            b.obs.append(("aviso", f"Mismo pilar que el post anterior ({a.meta['titulo']})"))
    por_semana: dict[dt.date, list[Post]] = {}
    for p in activos:
        por_semana.setdefault(lunes_de(p.fecha), []).append(p)
    for semana, ps in sorted(por_semana.items()):
        if len(ps) > ritmo["posts_por_semana"]:
            globales.append(f"Semana del {semana}: {len(ps)} posts (ritmo: {ritmo['posts_por_semana']})")
        actualidad = sum(1 for p in ps if p.meta.get("tipo") == "actualidad")
        if actualidad > ritmo["actualidad_por_semana"]:
            globales.append(f"Semana del {semana}: {actualidad} de actualidad (regla: 2 atemporales + 1 de actualidad)")
    for p in activos:
        dia = DIAS[p.fecha.weekday()]
        esperado = ritmo["dias"].get(dia)
        if esperado is None:
            p.obs.append(("aviso", f"Sale en {dia}; los días del ritmo son {', '.join(ritmo['dias'])}"))
        elif p.meta.get("formato") and p.meta["formato"] != esperado:
            p.obs.append(("aviso", f"El {dia} toca {esperado}, este es {p.meta['formato']}"))
    return globales


def calendario(posts: list[Post], hoy: dt.date, semanas: int = 3) -> list[dict]:
    """Huecos y posts asignados para las próximas semanas (voz con ritmo)."""
    ritmo = CONFIG["ritmo"]
    por_fecha = {}
    for p in posts:
        if p.meta.get("voz") == ritmo["voz"] and p.fecha and p.estado != "descartado":
            por_fecha.setdefault(p.fecha, []).append(p)
    filas = []
    inicio = lunes_de(hoy)
    for s in range(semanas):
        for dia, formato in ritmo["dias"].items():
            fecha = inicio + dt.timedelta(weeks=s, days=DIAS.index(dia))
            filas.append({"fecha": fecha, "dia": dia, "formato": formato, "posts": por_fecha.get(fecha, [])})
    return filas


# ── Desempeño (equivalente a HISTORIC PERFORMANCE de watchboard) ──

def desempeno(posts: list[Post]) -> dict[str, dict[str, dict]]:
    tablas: dict[str, dict[str, dict]] = {"pilar": {}, "formato": {}}
    for p in posts:
        met = p.meta.get("metricas") or {}
        if p.estado != "publicado" or not met:
            continue
        for eje in tablas:
            clave = p.meta.get(eje) or "—"
            fila = tablas[eje].setdefault(clave, {"n": 0})
            fila["n"] += 1
            for k, v in met.items():
                if isinstance(v, (int, float)):
                    fila[k] = fila.get(k, 0) + v
    return tablas


# ── Salidas ──

ICONO = {"PUBLICAR": "🟢", "REVISAR": "🟡", "BLOQUEADO": "🔴", "EN PROCESO": "⚪", "PUBLICADO": "✅", "DESCARTADO": "⚫"}


def salida_md(posts: list[Post], globales: list[str], hoy: dt.date) -> str:
    out = [f"# Centro de difusión — {hoy}", "", "## Cola", "",
           "| | Fecha | Voz | Post | Estado | Bloqueos | Avisos |", "|---|---|---|---|---|---|---|"]
    for p in sorted(posts, key=lambda p: (p.fecha or dt.date.max)):
        out.append(f"| {ICONO[p.veredicto]} {p.veredicto} | {p.fecha or '—'} | {p.meta.get('voz', '—')} | "
                   f"[{p.meta.get('titulo', p.rel)}]({p.rel}) | {p.estado} | {len(p.bloqueos)} | {len(p.avisos)} |")
    out += ["", "## Calendario (próximas 3 semanas)", "", "| Fecha | Día | Formato | Post |", "|---|---|---|---|"]
    for f in calendario(posts, hoy):
        nombres = ", ".join(f"{ICONO[p.veredicto]} {p.meta.get('titulo')}" for p in f["posts"]) or "**hueco**"
        out.append(f"| {f['fecha']} | {f['dia']} | {f['formato']} | {nombres} |")
    if globales:
        out += ["", "## Reglas de calendario", ""] + [f"- ⚠️ {g}" for g in globales]
    out += ["", "## Detalle", ""]
    for p in posts:
        if not p.obs:
            continue
        out.append(f"### {ICONO[p.veredicto]} {p.meta.get('titulo', p.rel)}")
        out += [f"- {'🔴' if n == 'bloqueo' else '🟡'} {msg}" for n, msg in p.obs]
        out.append("")
    return "\n".join(out) + "\n"


def salida_brief(posts: list[Post], hoy: dt.date) -> str:
    """Contexto para la rutina de propuesta semanal (como el prompt de generate-social-queue)."""
    recientes = [p for p in posts if p.fecha and hoy - dt.timedelta(days=14) <= p.fecha <= hoy + dt.timedelta(days=21)
                 and p.estado != "descartado" and p.meta.get("voz") == CONFIG["ritmo"]["voz"]]
    out = [f"# Brief para la propuesta semanal — {hoy}", "",
           "Reglas: ver estrategia/pilares.md. Proponer 5–8 temas para llenar los huecos.", "",
           "## Publicado o programado (−2 a +3 semanas)", ""]
    for p in sorted(recientes, key=lambda p: p.fecha):
        out.append(f"- {p.fecha} · {p.meta.get('pilar', 'sin pilar')} · {p.meta.get('formato', '?')} · "
                   f"{p.meta.get('tipo', '?')} · {p.meta.get('titulo')} ({p.estado})")
    out += ["", "## Huecos", ""]
    out += [f"- {f['fecha']} ({f['dia']}): {f['formato']}" for f in calendario(posts, hoy) if not f["posts"]]
    tablas = desempeno(posts)
    out += ["", "## Desempeño histórico", ""]
    if not any(tablas.values()):
        out.append("Aún no hay `metricas` en posts publicados. Priorizar variedad.")
    for eje, filas in tablas.items():
        for clave, fila in sorted(filas.items()):
            extras = ", ".join(f"{k}: {v / fila['n']:.0f}" for k, v in fila.items() if k != "n")
            out.append(f"- {eje} **{clave}** ({fila['n']} posts) — promedio {extras}")
    return "\n".join(out) + "\n"


def salida_html(posts: list[Post], globales: list[str], hoy: dt.date) -> str:
    e = html.escape
    color = {"PUBLICAR": "#06DBD1", "REVISAR": "#F48FB1", "BLOQUEADO": "#D9488F",
             "EN PROCESO": "#6B7A90", "PUBLICADO": "#7EC8F2", "DESCARTADO": "#6B7A90"}
    tarjetas = []
    for p in sorted(posts, key=lambda p: (p.fecha or dt.date.max)):
        textos = "".join(
            f"<details><summary>{e(s)} · {len(p.secciones.get(s, ''))} car.</summary><pre>{e(p.secciones.get(s, ''))}</pre></details>"
            for s in (CONFIG["plataformas"][k]["seccion"] for k in CONFIG["plataformas"]) if s in p.secciones)
        obs = "".join(f"<li class='{n}'>{e(m)}</li>" for n, m in p.obs) or "<li class='ok'>Sin observaciones</li>"
        tarjetas.append(f"""<article style="--c:{color[p.veredicto]}">
<header><span class="v">{p.veredicto}</span><span>{p.fecha or 'sin fecha'} · {e(str(p.meta.get('voz', '')))} · {e(str(p.meta.get('formato', '')))}</span></header>
<h2>{e(str(p.meta.get('titulo', p.rel)))}</h2><p class="m">{e(str(p.meta.get('pilar', '')))} · estado: {e(p.estado)} · <code>{e(p.rel)}</code></p>
<ul>{obs}</ul>{textos}</article>""")
    cal = "".join(
        f"<tr><td>{f['fecha']}</td><td>{f['dia']}</td><td>{f['formato']}</td><td>"
        + (", ".join(e(str(p.meta.get('titulo'))) for p in f['posts']) or "<b class='hueco'>hueco</b>") + "</td></tr>"
        for f in calendario(posts, hoy))
    glob = "".join(f"<li class='aviso'>{e(g)}</li>" for g in globales)
    return f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Centro de difusión</title>
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@600;700&family=Nunito+Sans:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#0B1320;color:#F5F8FC;font:15px/1.5 'Nunito Sans',sans-serif;padding:24px 16px}}
main{{max-width:980px;margin:auto}} h1,h2{{font-family:Quicksand,sans-serif}}
h1{{background:linear-gradient(120deg,#06DBD1,#7EC8F2 40%,#F48FB1 75%,#D9488F);-webkit-background-clip:text;color:transparent}}
article{{border:1px solid #1d2a40;border-left:4px solid var(--c);border-radius:10px;padding:14px 16px;margin:12px 0;background:#0f1a2c}}
article header{{display:flex;gap:12px;flex-wrap:wrap;color:#CDE1F8;font-size:13px}} .v{{color:var(--c);font-weight:700}}
article h2{{margin:6px 0 2px;font-size:18px}} .m{{color:#6B7A90;margin:0 0 8px;font-size:13px}}
li.bloqueo::marker{{content:'● ';color:#D9488F}} li.aviso::marker{{content:'● ';color:#F48FB1}} li.ok::marker{{content:'● ';color:#06DBD1}}
pre{{white-space:pre-wrap;font:13px/1.5 'Nunito Sans';background:#0B1320;padding:10px;border-radius:8px}}
table{{border-collapse:collapse;width:100%}} td,th{{padding:6px 8px;border-bottom:1px solid #1d2a40;text-align:left}}
.hueco{{color:#F48FB1}} code{{font-family:'JetBrains Mono';font-size:12px}}
</style><main><h1>Centro de difusión</h1><p class="m">Generado el {hoy} con herramientas/centro.py</p>
<h2>Calendario</h2><table><tr><th>Fecha</th><th>Día</th><th>Formato</th><th>Post</th></tr>{cal}</table>
{f'<h2>Reglas de calendario</h2><ul>{glob}</ul>' if glob else ''}
<h2>Cola</h2>{''.join(tarjetas)}</main></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hoy", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--md", type=Path, help="Escribe el reporte en Markdown")
    ap.add_argument("--html", type=Path, help="Escribe el tablero en HTML")
    ap.add_argument("--brief", action="store_true", help="Imprime el contexto para la propuesta semanal")
    ap.add_argument("--ci", action="store_true", help="Error si algún post listo/publicado tiene bloqueos")
    a = ap.parse_args()

    posts = encontrar_posts()
    for p in posts:
        revisar_post(p, a.hoy)
    globales = revisar_calendario(posts)

    if a.brief:
        print(salida_brief(posts, a.hoy))
        return 0
    if a.md:
        a.md.write_text(salida_md(posts, globales, a.hoy), encoding="utf-8")
    if a.html:
        a.html.write_text(salida_html(posts, globales, a.hoy), encoding="utf-8")

    for p in sorted(posts, key=lambda p: (p.fecha or dt.date.max)):
        print(f"{ICONO[p.veredicto]} {p.veredicto:<11} {str(p.fecha or '—'):<10}  {p.meta.get('titulo', p.rel)}")
        for n, msg in p.obs:
            print(f"     {'✖' if n == 'bloqueo' else '·'} {msg}")
    for g in globales:
        print(f"⚠️  {g}")

    if a.ci:
        malos = [p for p in posts if p.estado in ("listo", "publicado") and p.bloqueos]
        if malos:
            print(f"\n{len(malos)} post(s) listos con bloqueos.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
