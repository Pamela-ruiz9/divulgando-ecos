// Motivo SECiD: cubos isométricos dentro de hexágonos (como el logo).
// cubos(svg, lista) — cada item: {x, y, r, color, marco?}
const SECID_TONOS = {
  naranja: ["#F65425", "#C8401A", "#FF7B52"],
  dorado:  ["#FDB157", "#D98E35", "#FFCA7A"],
  pizarra: ["#4A6A8A", "#34506B", "#6D8BA8"],
  crema:   ["#E4DFD0", "#B9B4A6", "#F4EFE0"],
};

function hexPts(cx, cy, r) {
  const p = [];
  for (let i = 0; i < 6; i++) {
    const a = Math.PI / 180 * (60 * i);
    p.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
  }
  return p;
}

function cubos(svg, lista) {
  const NS = "http://www.w3.org/2000/svg";
  const poly = (pts, fill) => {
    const e = document.createElementNS(NS, "polygon");
    e.setAttribute("points", pts.map(p => p.join(",")).join(" "));
    e.setAttribute("fill", fill);
    svg.appendChild(e);
  };
  for (const c of lista) {
    if (c.marco) {
      poly(hexPts(c.x, c.y, c.r * 1.28), SECID_TONOS[c.marco][0]);
      poly(hexPts(c.x, c.y, c.r * 1.12), "#0F0F0F");
    }
    const [base, sombra, luz] = SECID_TONOS[c.color];
    const h = hexPts(c.x, c.y, c.r);           // 0=der,1=abajo-der,2=abajo-izq,3=izq,4=arriba-izq,5=arriba-der
    const ctr = [c.x, c.y];
    poly([ctr, h[5], h[0], h[1]], base);        // cara derecha
    poly([ctr, h[1], h[2], h[3]], luz);         // cara inferior
    poly([ctr, h[3], h[4], h[5]], sombra);      // cara superior
  }
}

// Llena elementos con data-campo="ruta.del.json" desde window.DATOS.
function llenar() {
  const d = window.DATOS || {};
  const get = (o, ruta) => ruta.split(".").reduce((a, k) => (a == null ? a : a[k]), o);
  document.querySelectorAll("[data-campo]").forEach(el => {
    const v = get(d, el.dataset.campo);
    if (v == null || v === "") { if (el.dataset.opcional !== undefined) el.closest("[data-bloque]")?.remove(); return; }
    el.innerHTML = v;
  });
  if (d.ejemplo) document.querySelectorAll(".slide").forEach(s => {
    const b = document.createElement("div"); b.className = "ejemplo"; b.textContent = "EJEMPLO"; s.appendChild(b);
  });
}
