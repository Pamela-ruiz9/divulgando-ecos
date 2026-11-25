import {Composition} from "remotion";
import {MexicoEnvejece, DURACION as DUR_MX} from "./reels/MexicoEnvejece";

// Reels verticales 1080×1920 a 30 fps. Agrega aquí cada reel nuevo.
export const Raiz = () => (
  <>
    <Composition id="MexicoEnvejece" component={MexicoEnvejece} durationInFrames={DUR_MX} fps={30} width={1080} height={1920} />
  </>
);
