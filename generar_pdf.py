"""Genera manual.pdf a partir de manual.md con el estilo del design system «Material FP».

Uso: python generar_pdf.py   (necesita el paquete `markdown` y Chromium)
"""
import html
import re
import subprocess
import tempfile
from pathlib import Path

import markdown

AQUI = Path(__file__).resolve().parent
MD = AQUI / "manual.md"
PDF = AQUI / "manual.pdf"
CHROMIUM = "chromium"

CSS = """
@import url("https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap");

:root {
  --surface: #faf5ea; --surface-raised: #fffdf7; --surface-sunken: #efe7d6;
  --ink: #241d16; --ink-muted: #6b5f51;
  --hairline: #8d8271; --hairline-soft: #d8cdb8;
  --accent: #1f5a52; --on-accent: #fdfaf3; --accent-soft: #dde9e4;
  --info: #1f4f7a; --info-soft: #dde8f2;
  --warn: #7d5310; --warn-soft: #f6e8c9;
  --code-surface: #211a13; --code-ink: #f7f2e6;
  --font-display: Archivo, "Helvetica Neue", Arial, sans-serif;
  --font-sans: "Source Sans 3", "Source Sans Pro", Calibri, sans-serif;
  --font-mono: "JetBrains Mono", "DejaVu Sans Mono", monospace;
}

@page {
  size: A4;
  margin: 20mm 20mm 22mm 20mm;
  background: var(--surface);
  @bottom-left {
    content: "Grabar el examen con OBS";
    font: 8.5pt "Source Sans 3", sans-serif; color: #6b5f51;
  }
  @bottom-right {
    content: counter(page);
    font: 8.5pt "Source Sans 3", sans-serif; color: #6b5f51;
  }
}
@page portada {
  margin: 0;
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

* { box-sizing: border-box; }
html, body { margin: 0; background: var(--surface); }
body {
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 11pt;
  line-height: 1.45;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* Portada: banda de accent a sangre, como la portada de unidad */
.portada {
  page: portada;
  display: flex;
  height: 297mm;
  break-after: page;
}
.portada__banda { width: 26mm; flex: none; background: var(--accent); }
.portada__txt {
  flex: 1;
  padding: 0 22mm 0 18mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 7mm;
}
.portada__ud { font: 700 20pt/1.1 var(--font-display); color: var(--accent); margin: 0; }
.portada h1 {
  font: 800 34pt/1.02 var(--font-display);
  letter-spacing: -0.02em;
  margin: 0;
}
.portada__intro { font-size: 13pt; line-height: 1.4; margin: 0; max-width: 140mm; }
.portada hr { height: 1px; background: var(--hairline); border: 0; margin: 0; }
.portada__meta { color: var(--ink-muted); font-size: 9.5pt; display: flex; flex-wrap: wrap; gap: 2mm 6mm; margin: 0; }

/* Secciones */
.seccion { margin: 0 0 8mm; }
.seccion + .seccion { border-top: 1px solid var(--hairline); padding-top: 7mm; }
.etiqueta, h2 { break-after: avoid; }
.etiqueta {
  font: 700 8pt/1.2 var(--font-sans);
  letter-spacing: 0.08em;
  color: var(--accent);
  margin: 0 0 1.5mm;
}
h2 {
  font: 700 20pt/1.1 var(--font-display);
  letter-spacing: -0.01em;
  margin: 0 0 4mm;
  break-after: avoid;
}
h2 + * { break-before: avoid; }
p { margin: 0 0 3mm; }
strong { font-weight: 700; }
a { color: var(--accent); }
code {
  font-family: var(--font-mono);
  font-size: 9pt;
  background: var(--surface-sunken);
  padding: 0.3mm 1.2mm;
  border-radius: 1px;
}

/* Listas del sistema: cuadrado de accent en las no ordenadas, número en accent en las ordenadas */
ul, ol { margin: 0 0 4mm; padding: 0; list-style: none; }
li { position: relative; padding-left: 7mm; margin-bottom: 1.8mm; }
ul > li::before {
  content: ""; position: absolute; left: 0.5mm; top: 0.52em;
  width: 2.2mm; height: 2.2mm; background: var(--accent);
}
ol { counter-reset: n; }
ol > li { counter-increment: n; }
ol > li::before {
  content: counter(n);
  position: absolute; left: 0; top: 0.1em;
  width: 5mm; height: 5mm;
  display: grid; place-items: center;
  border-radius: 999px;
  background: var(--accent); color: var(--on-accent);
  font: 700 8pt/1 var(--font-display);
}

/* Capturas: con filete, nunca de fondo bajo el texto */
figure { margin: 2mm 0 5mm; break-inside: avoid; }
figure img {
  display: block;
  max-width: 100%;
  max-height: 82mm;
  margin: 0 auto;
  border: 1px solid var(--hairline);
  border-radius: 4px;
  background: var(--surface-raised);
}
figcaption { color: var(--ink-muted); font-size: 8.5pt; text-align: center; margin-top: 1.5mm; }

/* Avisos: siempre con su palabra escrita */
.aviso {
  border-radius: 4px;
  border-left: 4px solid var(--info);
  background: var(--info-soft);
  padding: 4mm 5mm;
  margin: 3mm 0 5mm;
  break-inside: avoid;
}
.aviso p { margin: 0; }
.aviso__titulo { font: 700 8pt/1.2 var(--font-sans); letter-spacing: 0.08em; color: var(--info); margin-bottom: 1.5mm !important; }
.aviso--atencion { border-left-color: var(--warn); background: var(--warn-soft); }
.aviso--atencion .aviso__titulo { color: var(--warn); }
"""


def convertir(md_text: str) -> str:
    lineas = md_text.splitlines()
    titulo = lineas[0].lstrip("# ").strip()
    titulo = re.sub(r"^Manual:\s*", "", titulo)
    titulo = titulo[:1].upper() + titulo[1:]
    resto = "\n".join(lineas[1:]).strip()

    # La primera línea de texto es la entradilla de la portada
    intro, _, cuerpo = resto.partition("\n\n")

    # Los separadores --- sobran: cada sección ya tiene su propio corte
    cuerpo = re.sub(r"^---\s*$", "", cuerpo, flags=re.M)

    # Trocear por secciones de nivel 2
    secciones = re.split(r"^## ", cuerpo, flags=re.M)
    partes = []
    for sec in secciones:
        sec = sec.strip()
        if not sec:
            continue
        cab, _, contenido = sec.partition("\n")
        m = re.match(r"Paso (\d+)\s*[—-]\s*(.+)", cab)
        if m:
            etiqueta, h2, clase = f"PASO {m.group(1)}", m.group(2), "seccion paso"
        else:
            etiqueta, h2, clase = "ANTES DE EMPEZAR" if "empezar" in cab.lower() else "", cab, "seccion"
        cuerpo_html = markdown.markdown(contenido, extensions=["sane_lists"])
        partes.append(
            f'<section class="{clase}">'
            + (f'<p class="etiqueta">{etiqueta}</p>' if etiqueta else "")
            + f"<h2>{html.escape(h2)}</h2>{cuerpo_html}</section>"
        )
    cuerpo_html = "\n".join(partes)

    # Imágenes sueltas → figura con pie
    cuerpo_html = re.sub(
        r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>',
        lambda m: f'<figure><img alt="{m.group(1)}" src="{AQUI / m.group(2)}"><figcaption>{m.group(1)}</figcaption></figure>',
        cuerpo_html,
    )

    # Párrafos con ⚠️ → aviso de atención (el sistema no usa emoji: la palabra hace de señal)
    def aviso(m):
        texto = re.sub(r"^\s*(Importante:|IMPORTANTE:)\s*", "", m.group(1))
        texto = texto[:1].upper() + texto[1:]
        return (
            '<div class="aviso aviso--atencion"><p class="aviso__titulo">ATENCIÓN</p>'
            f"<p>{texto}</p></div>"
        )

    # Las listas que siguen una numeración (4., 5.…) arrancan el contador donde toca
    cuerpo_html = re.sub(
        r'<ol start="(\d+)">',
        lambda m: f'<ol style="counter-reset: n {int(m.group(1)) - 1}">',
        cuerpo_html,
    )

    cuerpo_html = re.sub(r"<p>⚠️\s*(.+?)</p>", aviso, cuerpo_html, flags=re.S)

    intro_html = markdown.markdown(intro).removeprefix("<p>").removesuffix("</p>")
    portada = f"""
<section class="portada">
  <div class="portada__banda"></div>
  <div class="portada__txt">
    <p class="portada__ud">GUÍA DEL ALUMNADO</p>
    <h1>{html.escape(titulo)}</h1>
    <p class="portada__intro">{intro_html}</p>
    <hr>
    <p class="portada__meta"><span>OBS Studio</span><span>Windows · macOS · Linux</span><span>Cinco pasos</span></p>
  </div>
</section>"""

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>{html.escape(titulo)}</title>
<style>{CSS}</style></head>
<body>{portada}
<main>{cuerpo_html}</main>
</body></html>"""


def main():
    doc = convertir(MD.read_text(encoding="utf-8"))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8", dir=AQUI) as f:
        f.write(doc)
        tmp = Path(f.name)
    try:
        subprocess.run(
            [CHROMIUM, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             "--virtual-time-budget=15000", f"--print-to-pdf={PDF}", tmp.as_uri()],
            check=True, capture_output=True,
        )
    finally:
        tmp.unlink()
    print(f"Generado {PDF}")


if __name__ == "__main__":
    main()
