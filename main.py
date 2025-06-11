"""Servidor que genera bocetos de pernos de anclaje en SVG."""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pathlib import Path
import base64

# Instancia principal de FastAPI
app = FastAPI()

# Ruta al archivo HTML con el formulario
HTML_PATH = Path(__file__).parent / "static" / "index.html"


def generate_svg(bolt_type: str, length: float, hook: float, thread: float) -> str:
    """Genera un SVG sencillo representando el perno."""

    # Escala para que el dibujo sea visible en pantalla
    scale = 2.0

    # Calculamos la longitud del cuerpo restando la parte del gancho si existe
    body_length = max(length - hook, 0)

    # Dimensiones generales del dibujo con un margen adicional
    width = (hook + 60) * scale
    height = (length + 60) * scale

    # Coordenadas de inicio (abajo a la izquierda del dibujo)
    start_x = 30.0
    start_y = height - 30.0

    # Trazo principal que une el cuerpo con el gancho
    path = f"M {start_x} {start_y} v {-body_length * scale}"
    if bolt_type == "L":
        # Para un perno en forma de L simplemente dibujamos la "patita"
        path += f" h {hook * scale}"
    elif bolt_type == "J":
        # Para un perno en J usamos un arco con radio la mitad del gancho
        radius = hook * scale / 2
        path += f" a {radius} {radius} 0 0 1 0 {-hook * scale}"

    # Piezas que compondrán el SVG final
    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        f'<path d="{path}" stroke="black" fill="none"/>'
    ]

    if thread > 0:
        # Indicamos la longitud de la rosca con dos líneas azules
        y_thread = start_y - thread * scale
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{start_y}" '
            f'x2="{start_x + 5}" y2="{start_y}" stroke="blue"/>'
        )
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{y_thread}" '
            f'x2="{start_x + 5}" y2="{y_thread}" stroke="blue"/>'
        )

        # Texto que explica la sección roscada
        text_y = (start_y + y_thread) / 2
        svg_parts.append(
            f'<text x="{start_x + 10}" y="{text_y}" font-size="12">Rosca</text>'
        )

    svg_parts.append('</svg>')
    # Unimos todas las partes para obtener el SVG completo
    return ''.join(svg_parts)


# Pagina principal con el formulario
@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Devuelve el formulario HTML que solicita las medidas."""
    return HTML_PATH.read_text(encoding="utf-8")


# Ruta que devuelve únicamente la imagen en SVG
@app.get("/svg")
async def svg_image(
    bolt_type: str = Query("straight", alias="type"),
    length: float = 200.0,
    hook: float = 50.0,
    thread: float = 50.0,
) -> Response:
    # Generamos el dibujo con los parámetros recibidos
    svg = generate_svg(bolt_type, length, hook, thread)
    return Response(content=svg, media_type="image/svg+xml")


# Pagina auxiliar que muestra el boceto y enlace de descarga
@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("straight", alias="type"),
    length: float = 200.0,
    hook: float = 50.0,
    thread: float = 50.0,
) -> str:
    # Armamos la consulta para reutilizarla tanto en la imagen como en el enlace
    query = f"type={bolt_type}&length={length}&hook={hook}&thread={thread}"
    img_tag = f'<img src="/svg?{query}" alt="boceto">'
    download = (
        f'<a href="/svg?{query}" download="bolt.svg">Descargar SVG</a>'
    )
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"