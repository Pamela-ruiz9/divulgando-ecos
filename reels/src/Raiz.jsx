import {Composition, AbsoluteFill, interpolate, useCurrentFrame} from "remotion";

const Prueba = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: "linear-gradient(160deg,#0B1320,#023E8A)", justifyContent: "center", alignItems: "center"}}>
      <div style={{color: "#F5F8FC", fontSize: 90, fontFamily: "sans-serif", opacity: interpolate(f, [0, 20], [0, 1], {extrapolateRight: "clamp"})}}>
        Divulgando Ecos
      </div>
    </AbsoluteFill>
  );
};

export const Raiz = () => (
  <Composition id="Prueba" component={Prueba} durationInFrames={45} fps={30} width={1080} height={1920} />
);
