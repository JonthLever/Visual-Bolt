"""Servidor que genera bocetos de pernos de anclaje en SVG."""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pathlib import Path

# Instancia principal de FastAPI
app = FastAPI()

# Ruta al archivo HTML con el formulario
HTML_PATH = Path(__file__).parent / "static" / "index.html"


def generate_svg(
    bolt_type: str,
    length: float,
    hook: float,
    thread: float,
    diameter: float,
) -> str:
    """Genera un SVG con medidas del perno de anclaje."""

    # Escala para que el dibujo sea visible en pantalla
    scale = 2.0

    # Longitud del cuerpo sin contar el gancho
    body_length = max(length - hook, 0)

    # Margen alrededor del dibujo
    margin = 40

    # Grosor del perno escalado para el trazo
    line_thickness = max(diameter * scale, 1)

    # Calculamos el tamaño total del lienzo
    width = max(hook * scale + margin * 2 + line_thickness, 200)
    height = length * scale + margin * 2 + line_thickness

    # Coordenadas de inicio (centro de la línea)
    start_x = margin + line_thickness / 2
    start_y = height - margin - line_thickness / 2

    # Trazo principal del perno
    path = f"M {start_x} {start_y} v {-body_length * scale}"
    if bolt_type == "L":
        # Para un perno en forma de L dibujamos la patita
        path += f" h {hook * scale}"
    elif bolt_type == "J":
        # Para un perno en J usamos un arco
        radius = hook * scale / 2
        path += f" a {radius} {radius} 0 0 1 0 {-hook * scale}"

    # Componentes base del SVG
    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<defs>'
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">'
        '<path d="M0 0 L10 5 L0 10 z" fill="black"/></marker>'
        '</defs>',
        f'<path d="{path}" stroke="black" stroke-width="{line_thickness}" '
        'fill="none"/>'
    ]

    if thread > 0:
        # Longitud de la rosca indicada con líneas azules
        y_thread = start_y - thread * scale
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{start_y}" x2="{start_x + 5}" y2="{start_y}" stroke="blue"/>'
        )
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{y_thread}" x2="{start_x + 5}" y2="{y_thread}" stroke="blue"/>'
        )
        text_y = (start_y + y_thread) / 2
        svg_parts.append(
            f'<text x="{start_x + 10}" y="{text_y}" font-size="12">Rosca</text>'
        )

        # Cota de la rosca (flechas rojas)
        thread_line_x = start_x - 20
        svg_parts.append(
            f'<line x1="{thread_line_x}" y1="{start_y}" x2="{thread_line_x}" y2="{y_thread}" '
            f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
        )
        svg_parts.append(
            f'<text x="{thread_line_x - 5}" y="{(start_y + y_thread) / 2}" '
            f'font-size="12" fill="red" text-anchor="end">{thread} mm</text>'
        )

    # Cota total del perno
    length_line_x = start_x + 40
    svg_parts.append(
        f'<line x1="{length_line_x}" y1="{start_y}" x2="{length_line_x}" y2="{start_y - length * scale}" '
        f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
    )
    svg_parts.append(
        f'<text x="{length_line_x + 5}" y="{start_y - (length * scale) / 2}" '
        f'font-size="12" fill="red">{length} mm</text>'
    )

    if hook > 0:
        # Cota del gancho en la parte inferior
        hook_line_y = start_y + 20
        svg_parts.append(
            f'<line x1="{start_x}" y1="{hook_line_y}" x2="{start_x + hook * scale}" y2="{hook_line_y}" '
            f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
        )
        svg_parts.append(
            f'<text x="{start_x + (hook * scale) / 2}" y="{hook_line_y - 5}" '
            f'font-size="12" fill="red" text-anchor="middle">{hook} mm</text>'
        )

    # Cota del diámetro del perno
    diameter_line_y = start_y + 40
    svg_parts.append(
        f'<line x1="{start_x - line_thickness / 2}" y1="{diameter_line_y}" '
        f'x2="{start_x + line_thickness / 2}" y2="{diameter_line_y}" '
        f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
    )
    svg_parts.append(
        f'<text x="{start_x}" y="{diameter_line_y - 5}" font-size="12" '
        f'fill="red" text-anchor="middle">{diameter} mm</text>'
    )

    svg_parts.append('</svg>')
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
    diameter: float = 20.0,
) -> Response:
    # Generamos el dibujo con los parámetros recibidos
    svg = generate_svg(bolt_type, length, hook, thread, diameter)
    return Response(content=svg, media_type="image/svg+xml")


# Pagina auxiliar que muestra el boceto y enlace de descarga
@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("straight", alias="type"),
    length: float = 200.0,
    hook: float = 50.0,
    thread: float = 50.0,
    diameter: float = 20.0,
) -> str:
    # Armamos la consulta para reutilizarla tanto en la imagen como en el enlace
    query = (
        f"type={bolt_type}&length={length}&hook={hook}&thread={thread}"
        f"&diameter={diameter}"
    )
    img_tag = f'<img src="/svg?{query}" alt="boceto">'
    download = (
        f'<a href="/svg?{query}" download="bolt.svg">Descargar SVG</a>'
    )
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"