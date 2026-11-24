import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from "remotion";
import {C, Fondo, Entra, Degradado, Fuente, ease, FUENTE_TITULO, FUENTE_TEXTO, FUENTE_MONO} from "../marca/ecos";
import datos from "../datos/piramide_mx.json";

// Línea de tiempo (30 fps)
const T = {gancho: [0, 105], piramide: [105, 480], comparacion: [480, 615], cierre: [615, 720]};
export const DURACION = 720;

// Tramos de la pirámide: [inicio transición, fin transición] hacia cada año (frames relativos a la escena)
const PASOS = [
  {anio: "1970", llega: 0},
  {anio: "2000", llega: 110},
  {anio: "2025", llega: 200},
  {anio: "2050", llega: 290},
];
const TRANSICION = 35;

const suma = (anio, grupos) =>
  grupos.reduce((s, g) => s + datos.pct[anio][g].mujeres + datos.pct[anio][g].hombres, 0);
const NINOS = ["0-4", "5-9", "10-14"];
const MAYORES = ["65-69", "70-74", "75-79", "80+"];

// Valor interpolado de cualquier función del año en el frame f
function enFrame(f, fn) {
  let v = fn(PASOS[0].anio);
  for (let i = 1; i < PASOS.length; i++) {
    const p = interpolate(f, [PASOS[i].llega - TRANSICION, PASOS[i].llega], [0, 1],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease});
    v = v + (fn(PASOS[i].anio) - fn(PASOS[i - 1].anio)) * p;
  }
  return v;
}
const anioActual = (f) => [...PASOS].reverse().find((p) => f >= p.llega - TRANSICION / 2)?.anio ?? "1970";

const Gancho = () => (
  <AbsoluteFill style={{padding: "0 80px", justifyContent: "center"}}>
    <Entra desde={0} style={{fontFamily: FUENTE_MONO, fontWeight: 700, fontSize: 34, letterSpacing: ".16em", color: C.cian}}>
      MÉXICO EN DATOS
    </Entra>
    <Entra desde={10} style={{fontFamily: FUENTE_TITULO, fontWeight: 700, fontSize: 104, lineHeight: 1.05, color: C.texto, marginTop: 30}}>
      En 1970, casi <Degradado>la mitad</Degradado> de México eran niños.
    </Entra>
    <Entra desde={45} style={{fontFamily: FUENTE_TEXTO, fontSize: 46, color: C.hielo, marginTop: 40}}>
      Mira cómo cambia hasta 2050 👇
    </Entra>
  </AbsoluteFill>
);

const ANCHO_POR_PCT = 40; // px por punto porcentual
const ALTO_FILA = 50;

const Piramide = () => {
  const f = useCurrentFrame();
  const grupos = [...datos.grupos].reverse(); // 80+ arriba
  const anio = anioActual(f);
  const ninos = enFrame(f, (a) => suma(a, NINOS));
  const mayores = enFrame(f, (a) => suma(a, MAYORES));
  const total = enFrame(f, (a) => datos.total_millones[a]);
  const centro = 540;
  const top = 720;
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", top: 230, left: 80, right: 80, display: "flex", justifyContent: "space-between", alignItems: "flex-end"}}>
        <div>
          <div style={{fontFamily: FUENTE_TITULO, fontWeight: 700, fontSize: 150, lineHeight: 1, color: C.texto}}>
            <Degradado>{anio}</Degradado>
          </div>
          <div style={{fontFamily: FUENTE_TEXTO, fontSize: 34, color: C.hielo, marginTop: 6}}>
            {total.toFixed(0)} millones de personas{anio === "2050" ? " (proyección)" : ""}
          </div>
        </div>
      </div>
      {/* indicadores */}
      <div style={{position: "absolute", top: 470, left: 80, right: 80, display: "flex", gap: 24}}>
        {[["Niños (0–14)", ninos], ["Adultos mayores (65+)", mayores]].map(([t, v]) => (
          <div key={t} style={{flex: 1, background: "rgba(11,19,32,.55)", border: "1px solid rgba(205,225,248,.15)", borderRadius: 22, padding: "16px 24px"}}>
            <div style={{fontFamily: FUENTE_TEXTO, fontSize: 28, color: C.hielo}}>{t}</div>
            <div style={{fontFamily: FUENTE_MONO, fontWeight: 700, fontSize: 58, color: C.texto}}>{v.toFixed(1)}%</div>
          </div>
        ))}
      </div>
      {/* pirámide */}
      <svg width="1080" height="1920" style={{position: "absolute", inset: 0}}>
        <text x={centro - 20} y={top - 22} textAnchor="end" fill={C.texto} fontFamily={FUENTE_TEXTO} fontWeight="700" fontSize="30">Hombres</text>
        <text x={centro + 20} y={top - 22} fill={C.texto} fontFamily={FUENTE_TEXTO} fontWeight="700" fontSize="30">Mujeres</text>
        {grupos.map((g, i) => {
          const y = top + i * ALTO_FILA;
          const h = enFrame(f, (a) => datos.pct[a][g].hombres) * ANCHO_POR_PCT;
          const m = enFrame(f, (a) => datos.pct[a][g].mujeres) * ANCHO_POR_PCT;
          const enfasis = NINOS.includes(g) || MAYORES.includes(g);
          return (
            <g key={g}>
              <rect x={centro - 34 - h} y={y} width={h} height={ALTO_FILA - 6} rx="4" fill={C.serie2} opacity={enfasis ? 1 : 0.55} />
              <rect x={centro + 34} y={y} width={m} height={ALTO_FILA - 6} rx="4" fill={C.serie3} opacity={enfasis ? 1 : 0.55} />
              <text x={centro} y={y + 31} textAnchor="middle" fill={C.hielo} fontFamily={FUENTE_MONO} fontSize="21">{g}</text>
            </g>
          );
        })}
      </svg>
      <Fuente>Porcentaje de la población por edad y sexo. Fuente: Banco Mundial, estimaciones y proyecciones de población (con base en ONU, World Population Prospects).</Fuente>
    </AbsoluteFill>
  );
};

const Comparacion = () => {
  const n = suma("2050", NINOS), m = suma("2050", MAYORES);
  return (
    <AbsoluteFill style={{padding: "0 80px", justifyContent: "center"}}>
      <Entra desde={0} style={{fontFamily: FUENTE_TITULO, fontWeight: 700, fontSize: 88, lineHeight: 1.08, color: C.texto}}>
        En 2050 habrá casi <Degradado>tantos adultos mayores</Degradado> como niños.
      </Entra>
      <div style={{display: "flex", gap: 30, marginTop: 70}}>
        {[["Niños (0–14)", n, C.serie2], ["65 años o más", m, C.serie3]].map(([t, v, col], i) => (
          <Entra key={t} desde={20 + i * 12} style={{flex: 1, borderTop: `8px solid ${col}`, background: "rgba(11,19,32,.55)", borderRadius: 22, padding: "30px 30px"}}>
            <div style={{fontFamily: FUENTE_MONO, fontWeight: 700, fontSize: 96, color: C.texto}}>{v.toFixed(1)}%</div>
            <div style={{fontFamily: FUENTE_TEXTO, fontSize: 34, color: C.hielo}}>{t}</div>
          </Entra>
        ))}
      </div>
      <Entra desde={50} style={{fontFamily: FUENTE_TEXTO, fontSize: 40, color: C.hielo, marginTop: 60}}>
        En 1970 eran {suma("1970", NINOS).toFixed(0)}% contra {suma("1970", MAYORES).toFixed(1)}%.
      </Entra>
    </AbsoluteFill>
  );
};

const Cierre = () => (
  <AbsoluteFill style={{padding: "0 80px", justifyContent: "center"}}>
    <Entra desde={0} style={{fontFamily: FUENTE_TITULO, fontWeight: 700, fontSize: 84, lineHeight: 1.1, color: C.texto}}>
      ¿Qué significa esto para las <Degradado>pensiones</Degradado>, la salud y el trabajo?
    </Entra>
    <Entra desde={25} style={{fontFamily: FUENTE_TEXTO, fontSize: 44, color: C.hielo, marginTop: 50}}>
      Te leo en comentarios 💬
    </Entra>
  </AbsoluteFill>
);

export const MexicoEnvejece = () => {
  const f = useCurrentFrame();
  // las ondas cambian de origen según la escena
  const origen = f < T.piramide[0] ? {x: 880, y: 360} : f < T.comparacion[0] ? {x: 540, y: 1100} : {x: 180, y: 1600};
  return (
    <AbsoluteFill style={{background: C.fondo}}>
      <Fondo {...origen} intensidad={f >= T.piramide[0] && f < T.comparacion[0] ? 0.2 : 0.5} />
      <Sequence from={T.gancho[0]} durationInFrames={T.gancho[1] - T.gancho[0]}><Gancho /></Sequence>
      <Sequence from={T.piramide[0]} durationInFrames={T.piramide[1] - T.piramide[0]}><Piramide /></Sequence>
      <Sequence from={T.comparacion[0]} durationInFrames={T.comparacion[1] - T.comparacion[0]}><Comparacion /></Sequence>
      <Sequence from={T.cierre[0]} durationInFrames={T.cierre[1] - T.cierre[0]}><Cierre /></Sequence>
    </AbsoluteFill>
  );
};
