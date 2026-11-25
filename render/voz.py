"""Genera la narración de un reel con Piper (voz local, gratis).

Uso:
    .venv-voz/bin/python render/voz.py reels/guiones/<reel>.json [--voz voces/es_AR-daniela-high.onnx]

El guion es un JSON: {"reel": "MexicoEnvejece", "frases": [{"id": "gancho1", "texto": "..."}, ...]}
Escribe un WAV por frase en reels/public/voz/<reel>/ y un manifiesto voz.json con la duración
de cada frase (Remotion lo usa para sincronizar escenas y subtítulos).

Tip: escribe los números con letra ("dos mil cincuenta") para que la voz los lea bien.
"""
import argparse
import json
import wave
from pathlib import Path

from piper import PiperVoice

RAIZ = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion", type=Path)
    ap.add_argument("--voz", type=Path, default=RAIZ / "voces/es_AR-daniela-high.onnx")
    a = ap.parse_args()

    guion = json.loads(a.guion.read_text(encoding="utf-8"))
    salida = RAIZ / "reels/public/voz" / guion["reel"]
    salida.mkdir(parents=True, exist_ok=True)
    voz = PiperVoice.load(str(a.voz))

    manifiesto = []
    for frase in guion["frases"]:
        archivo = salida / f"{frase['id']}.wav"
        with wave.open(str(archivo), "wb") as w:
            voz.synthesize_wav(frase["texto"], w)
        with wave.open(str(archivo), "rb") as w:
            dur = w.getnframes() / w.getframerate()
        manifiesto.append({**frase, "archivo": f"voz/{guion['reel']}/{archivo.name}", "duracion": round(dur, 3)})
        print(f"{frase['id']:10s} {dur:5.2f}s  {frase['texto']}")

    (salida / "voz.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    print("total", round(sum(m["duracion"] for m in manifiesto), 2), "s")


if __name__ == "__main__":
    main()
