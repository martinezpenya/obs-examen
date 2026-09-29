# OBS para grabar exámenes

Plantilla de [OBS Studio](https://obsproject.com) y manual para el alumnado. Sirve para que cada estudiante grabe su pantalla durante un examen práctico, con **la hora del sistema (con segundos) y su nombre** siempre visibles en el vídeo. Así el profesorado puede comprobar después quién ha hecho el examen, cuándo y cómo.

El alumnado solo tiene que importar la plantilla, escribir su nombre y elegir dónde se guarda el vídeo. Todo lo demás ya viene configurado.

![Vista previa de OBS con el reloj y el nombre](assets/cap2.png)

## Qué se reparte al alumnado

| Archivo | Qué es |
|---|---|
| [`manual.pdf`](manual.pdf) | El manual paso a paso (también en [`manual.md`](manual.md)) |
| [`EXAMEN_OBS.zip`](EXAMEN_OBS.zip) | La colección de escenas y el perfil, listos para importar en OBS |

## Contenido del repositorio

| Archivo | Para qué |
|---|---|
| `Escen_EXAMEN_EPM.json` | Colección de escenas: fuentes **Nombre** (texto FreeType 2), **Reloj** (navegador) y **Pantalla** (captura de pantalla) |
| `Perf_EXAMEN_EPM/` | Perfil de OBS con los ajustes de vídeo y de grabación |
| `reloj_marca_agua.html` | Código original del reloj. Ya va incrustado en la escena, así que el alumnado no lo necesita |
| `manual.md` y `assets/` | El manual y sus capturas |
| `generar_pdf.py` | Genera `manual.pdf` a partir de `manual.md` |

## Ajustes de la plantilla

| Ajuste | Valor | Por qué |
|---|---|---|
| Fotogramas | 1 FPS | Para vigilar un examen basta con una imagen por segundo, y así el vídeo pesa muy poco |
| Resolución | Lienzo 1920×1080, salida 1280×720 | Se lee el texto de la pantalla sin disparar el tamaño del archivo |
| Formato | MP4 híbrido | Si OBS se cierra de golpe, el vídeo se sigue pudiendo abrir, y se reproduce en cualquier sitio (necesita OBS 30.2 o posterior) |
| Bitrate de vídeo | 150 kbps (x264, CBR) | Unos 65 MB por hora de examen |
| División de archivos | Cada 250 MB (más de 3 horas) | En la práctica sale un solo archivo por examen; el manual avisa de que, si salen varios, se suban todos |
| Audio | Sin fuentes de audio | No se graba sonido; el MP4 lleva una pista en silencio (FFmpeg AAC) |
| Reloj | HTML incrustado como URL `data:` | No depende de rutas de archivo ni de conexión a internet |
| Ruta de grabación | Sin fijar | Cada estudiante elige su carpeta (paso 4 del manual) |

La fuente **Pantalla** es de PipeWire (Linux con Wayland). En Windows, macOS o Linux con X11 hay que sustituirla por la captura de pantalla de ese sistema; el paso 1 del manual explica cómo.

## Mantenimiento

**Regenerar el PDF** después de cambiar `manual.md` o una captura. Hace falta Chromium y conexión a internet, porque las tipografías se cargan desde Google Fonts:

```bash
pip install markdown
python generar_pdf.py
```

El PDF sigue el estilo del sistema de diseño *Material FP*: tipografías Archivo, Source Sans 3 y JetBrains Mono, fondo crema y avisos con su rótulo escrito.

**Regenerar el zip** después de cambiar la escena o el perfil:

```bash
rm -f EXAMEN_OBS.zip && zip -r -X EXAMEN_OBS.zip Escen_EXAMEN_EPM.json Perf_EXAMEN_EPM
```

**Cambiar el reloj:** edita `reloj_marca_agua.html` y vuelve a incrustarlo en la escena:

```bash
python3 - <<'EOF'
import base64, json
d = json.load(open("Escen_EXAMEN_EPM.json"))
url = "data:text/html;charset=utf-8;base64," + base64.b64encode(open("reloj_marca_agua.html", "rb").read()).decode()
for s in d["sources"]:
    if s["name"] == "Reloj":
        s["settings"]["url"] = url
json.dump(d, open("Escen_EXAMEN_EPM.json", "w"), indent=4, ensure_ascii=False)
EOF
```

Después regenera el zip.
