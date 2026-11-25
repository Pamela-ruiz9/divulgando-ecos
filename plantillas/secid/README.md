# Plantillas SECiD (solo comunicación institucional)

Uso exclusivo para comunicaciones de SECiD: eventos, convocatorias, avisos, logros de la comunidad.
La divulgación personal usa la marca "Ecos" (ver `marca/personal.md`).

| Plantilla | Para qué | Campos (JSON) |
|---|---|---|
| `evento.html` | Journal Club, seminarios, talleres, hackathons, meetups | `tipo, titulo, descripcion, ponente{iniciales,nombre,cargo}, fecha, hora, lugar, lugar_detalle, cta, url` |
| `aviso.html` | Convocatorias, avisos, bolsa de trabajo, anuncios | `tipo, titulo, cuerpo, cta, url` |

- Usa `<em>palabra</em>` en el título para resaltarla en naranja; `<b>` en el cuerpo la resalta en dorado.
- `"ejemplo": true` agrega una banda "EJEMPLO" (solo para pruebas).

```bash
python3 render/render.py plantillas/secid/evento.html \
  --datos secid/borradores/AAAA-MM-DD-tema/datos.json \
  --salida secid/borradores/AAAA-MM-DD-tema --nombre imagen
```
