from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pathlib import Path
import base64

app = FastAPI()

HTML_PATH = Path(__file__).parent / "static" / "index.html"


def generate_svg(bolt_type: str, length: float, hook: float, thread: float) -> str:
    """Generate a simple SVG drawing of the bolt."""
    scale = 2.0
    body_length = max(length - hook, 0)
    width = (hook + 60) * scale
    height = (length + 60) * scale
    start_x = 30.0
    start_y = height - 30.0

    # Main path for the bolt body and hook
    path = f"M {start_x} {start_y} v {-body_length * scale}"
    if bolt_type == "L":
        path += f" h {hook * scale}"
    elif bolt_type == "J":
        radius = hook * scale / 2
        path += f" a {radius} {radius} 0 0 1 0 {-hook * scale}"

    svg_parts = [f'<svg width="{width}" height="{height}" '
                 'xmlns="http://www.w3.org/2000/svg">',
                 f'<path d="{path}" stroke="black" fill="none"/>']

    if thread > 0:
        y_thread = start_y - thread * scale
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{start_y}" '
            f'x2="{start_x + 5}" y2="{start_y}" stroke="blue"/>'
        )
        svg_parts.append(
            f'<line x1="{start_x - 5}" y1="{y_thread}" '
            f'x2="{start_x + 5}" y2="{y_thread}" stroke="blue"/>'
        )
        text_y = (start_y + y_thread) / 2
        svg_parts.append(
            f'<text x="{start_x + 10}" y="{text_y}" font-size="12">Rosca</text>'
        )

    svg_parts.append('</svg>')
    return ''.join(svg_parts)


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Serve the main page with the form."""
    return HTML_PATH.read_text(encoding="utf-8")


@app.get("/svg")
async def svg_image(
    bolt_type: str = Query("straight", alias="type"),
    length: float = 200.0,
    hook: float = 50.0,
    thread: float = 50.0,
) -> Response:
    svg = generate_svg(bolt_type, length, hook, thread)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("straight", alias="type"),
    length: float = 200.0,
    hook: float = 50.0,
    thread: float = 50.0,
) -> str:
    query = f"type={bolt_type}&length={length}&hook={hook}&thread={thread}"
    img_tag = f'<img src="/svg?{query}" alt="boceto">'
    download = (
        f'<a href="/svg?{query}" download="bolt.svg">Descargar SVG</a>'
    )
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"
