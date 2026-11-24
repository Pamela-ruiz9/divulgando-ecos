// Marca personal "Ecos" para reels — ver marca/personal.md
import {AbsoluteFill, interpolate, useCurrentFrame, Easing} from "remotion";
import {loadFont as loadQuicksand} from "@remotion/google-fonts/Quicksand";
import {loadFont as loadNunito} from "@remotion/google-fonts/NunitoSans";
import {loadFont as loadMono} from "@remotion/google-fonts/JetBrainsMono";

export const FUENTE_TITULO = loadQuicksand("normal", {weights: ["600", "700"]}).fontFamily;
export const FUENTE_TEXTO = loadNunito("normal", {weights: ["400", "600", "700"]}).fontFamily;
export const FUENTE_MONO = loadMono("normal", {weights: ["500", "700"]}).fontFamily;

export const C = {
  fondo: "#0B1320", primario: "#023E8A", cian: "#06DBD1", cielo: "#7EC8F2",
  rosa: "#F48FB1", rosaInt: "#D9488F", hielo: "#CDE1F8", texto: "#F5F8FC", gris: "#8A98AE",
  // series validadas (daltonismo) — orden fijo
  serie1: "#0FA8A2", serie2: "#6A6FF0", serie3: "#E05A9E",
};
export const AURORA = "linear-gradient(120deg, #06DBD1 0%, #7EC8F2 40%, #F48FB1 75%, #D9488F 100%)";
export const PROFUNDO = "linear-gradient(160deg, #0B1320 0%, #0A1D3F 55%, #023E8A 100%)";

export const ease = Easing.bezier(0.65, 0, 0.35, 1);

// Fondo con degradado Profundo + ondas que se expanden desde (x, y)
export const Fondo = ({x = 900, y = 260, intensidad = 0.5}) => {
  const f = useCurrentFrame();
  const anillos = [0, 1, 2, 3, 4];
  return (
    <AbsoluteFill style={{background: PROFUNDO}}>
      <svg width="1080" height="1920" style={{position: "absolute", inset: 0}}>
        <defs>
          <linearGradient id="aurora" x1="0" y1="1" x2="1" y2="0">
            <stop offset="0" stopColor="#06DBD1" /><stop offset=".4" stopColor="#7EC8F2" />
            <stop offset=".75" stopColor="#F48FB1" /><stop offset="1" stopColor="#D9488F" />
          </linearGradient>
        </defs>
        {anillos.map((i) => {
          const ciclo = ((f + i * 36) % 180) / 180; // cada onda tarda 6 s en expandirse
          return (
            <circle key={i} cx={x} cy={y} r={40 + ciclo * 520} fill="none" stroke="url(#aurora)"
              strokeWidth={5 - ciclo * 3.5} opacity={(1 - ciclo) * intensidad} />
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// Texto que entra deslizándose y aparece
export const Entra = ({desde = 0, children, style}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [desde, desde + 18], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease});
  return <div style={{opacity: p, transform: `translateY(${(1 - p) * 40}px)`, ...style}}>{children}</div>;
};

export const Degradado = ({children, style}) => (
  <span style={{background: AURORA, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", ...style}}>{children}</span>
);

export const Fuente = ({children}) => (
  <div style={{position: "absolute", top: 1590, left: 80, right: 150, fontFamily: FUENTE_TEXTO, fontSize: 26, color: C.gris, lineHeight: 1.4}}>
    {children}
  </div>
);
