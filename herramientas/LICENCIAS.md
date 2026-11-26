# Licencias de terceros

Las herramientas `humano.py`, `muletillas.json`, `texto.py`, `gancho.py`,
`ganchos.json`, `ritmo.py` y los comandos en `.claude/skills/ecos-*` están
adaptados (traducidos y reescritos para el español y para este repo) de
**instagram-agent-skill** de Jake Schincariol:
https://github.com/Jakeschincariol/instagram-agent-skill (revisado el 2026-11-26).

Revisión de seguridad hecha antes de adaptarlo: los scripts originales solo usan
la librería estándar de Python, no hacen llamadas de red ni ejecutan comandos, y
solo escriben en el archivo de salida que se les indica. Las instrucciones de
los comandos no piden credenciales ni publican nada.

Licencia original:

```
MIT License

Copyright (c) 2026 Jake Schincariol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
