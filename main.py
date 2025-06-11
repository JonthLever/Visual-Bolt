"""Servidor FastAPI que genera bocetos en SVG de pernos de anclaje.
El estilo del dibujo imita un plano técnico 2D.
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from pathlib import Path

app = FastAPI()

# Archivo HTML que contiene el formulario
HTML_PATH = Path(__file__).parent / "static" / "index.html"


def generate_svg(bolt_type: str, diameter: float, length: float, hook: float, thread: float) -> str:
    """Devuelve un string SVG representando un perno de tipo L.

    El orden de parámetros corresponde a:
    D = diámetro, L = largo total, C = gancho, T = rosca.
    """

    # Escala para que los valores ingresados se aprecien mejor
    scale = 2.0
    margin = 40

    # Grosor del trazo equivalente al diámetro
    line_thickness = max(diameter * scale, 1)

    # Tamaño total del lienzo
    width = margin * 2 + hook * scale + line_thickness
    height = margin * 2 + length * scale + line_thickness

    # Coordenadas base
    start_x = margin + hook * scale + line_thickness / 2
    start_y = height - margin - line_thickness / 2
    top_y = start_y - length * scale

    svg_parts = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto">',
        '<path d="M0 0 L10 5 L0 10 z" fill="black"/></marker>',
        '</defs>',
        # Cuerpo del perno
        f'<line x1="{start_x}" y1="{start_y}" x2="{start_x}" y2="{top_y}" '
        f'stroke="black" stroke-width="{line_thickness}" />',
        f'<line x1="{start_x}" y1="{start_y}" x2="{start_x - hook * scale}" y2="{start_y}" '
        f'stroke="black" stroke-width="{line_thickness}" />',
    ]

    # Sección de rosca si aplica
    if thread > 0:
        thread_y = top_y + thread * scale
        # Líneas de referencia para la rosca
        svg_parts.append(
            f'<line x1="{start_x - diameter * scale / 2}" y1="{top_y}" '
            f'x2="{start_x + diameter * scale / 2}" y2="{top_y}" stroke="blue" />'
        )
        svg_parts.append(
            f'<line x1="{start_x - diameter * scale / 2}" y1="{thread_y}" '
            f'x2="{start_x + diameter * scale / 2}" y2="{thread_y}" stroke="blue" />'
        )
        # Cota de rosca
        svg_parts.append(
            f'<line x1="{start_x + 30}" y1="{top_y}" x2="{start_x + 30}" y2="{thread_y}" '
            f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)" />'
        )
        svg_parts.append(
            f'<text x="{start_x + 35}" y="{(top_y + thread_y) / 2}" font-size="12" fill="red">T: {thread} mm</text>'
        )

    # Cota de largo total
    svg_parts.append(
        f'<line x1="{start_x + 50}" y1="{start_y}" x2="{start_x + 50}" y2="{top_y}" '
        f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)" />'
    )
    svg_parts.append(
        f'<text x="{start_x + 55}" y="{(start_y + top_y) / 2}" font-size="12" fill="red">L: {length} mm</text>'
    )

    # Cota del gancho
    if hook > 0:
        svg_parts.append(
            f'<line x1="{start_x}" y1="{start_y + 20}" x2="{start_x - hook * scale}" y2="{start_y + 20}" '
            f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)" />'
        )
        svg_parts.append(
            f'<text x="{start_x - (hook * scale) / 2}" y="{start_y + 35}" font-size="12" fill="red" text-anchor="middle">C: {hook} mm</text>'
        )

    # Cota de diámetro
    svg_parts.append(
        f'<line x1="{start_x - line_thickness / 2}" y1="{start_y + 40}" '
        f'x2="{start_x + line_thickness / 2}" y2="{start_y + 40}" '
        f'stroke="red" marker-start="url(#arrow)" marker-end="url(#arrow)" />'
    )
    svg_parts.append(
        f'<text x="{start_x}" y="{start_y + 55}" font-size="12" fill="red" text-anchor="middle">D: {diameter} mm</text>'
    )

    svg_parts.append('</svg>')
    return ''.join(svg_parts)


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Muestra el formulario principal."""
    return HTML_PATH.read_text(encoding="utf-8")


@app.get("/svg")
async def svg_image(
    bolt_type: str = Query("L", alias="type"),
    diameter: float = Query(20.0, alias="D"),
    length: float = Query(200.0, alias="L"),
    hook: float = Query(50.0, alias="C"),
    thread: float = Query(50.0, alias="T"),
) -> Response:
    svg = generate_svg(bolt_type, diameter, length, hook, thread)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("L", alias="type"),
    diameter: float = Query(20.0, alias="D"),
    length: float = Query(200.0, alias="L"),
    hook: float = Query(50.0, alias="C"),
    thread: float = Query(50.0, alias="T"),
) -> str:
    query = f"type={bolt_type}&D={diameter}&L={length}&C={hook}&T={thread}"
    img_tag = f'<img src="/svg?{query}" alt="boceto">'
    download = f'<a href="/svg?{query}" download="bolt.svg">Descargar SVG</a>'
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"
