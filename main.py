"""Servidor FastAPI que genera un boceto tecnico de pernos de anclaje.

Se usa matplotlib para dibujar en 2D un perno tipo "L" o tipo "J" con sus
cotas de diametro, largo total, gancho y longitud de rosca. El resultado se
entrega como una imagen PNG descargable desde el navegador.
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path
import io
import math
import numpy as np

# Matplotlib se emplea en modo "Agg" para que funcione sin servidor de ventanas
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

app = FastAPI()

# Ruta al archivo HTML con el formulario
HTML_PATH = Path(__file__).parent / "static" / "index.html"


def draw_bolt_diagram(
    bolt_type: str,
    D: float,
    L: float,
    C: float,
    T: float,
    closing_angle: float = 180.0,
) -> bytes:
    """Genera un plano tecnico del perno usando matplotlib.

    Parameters
    ----------
    bolt_type : str
        "L" para perno en L o "J" para perno en J.
    D : float
        Diametro del perno.
    L : float
        Largo total del perno.
    C : float
        Largo del gancho.
    T : float
        Longitud de la rosca desde la parte superior.
    closing_angle : float, optional
        Angulo de cierre del gancho en grados (solo para tipo J).
    """

    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_aspect("equal")

    # Espaciado alrededor del perno para colocar las cotas
    offset = max(D * 2.0, 20.0)

    # --------- Dibujo del perno ---------
    ax.plot([0, 0], [0, L], color="black", linewidth=D, solid_capstyle="butt")

    lower_limit = -offset * 1.5
    if bolt_type.upper() == "L":
        ax.plot([0, -C], [0, 0], color="black", linewidth=D, solid_capstyle="butt")
        hook_left = -C
    else:  # tipo J con gancho curvo
        r = 4 * D
        angle_rad = math.radians(closing_angle)
        theta = np.linspace(0.0, angle_rad, 60)
        arc_x = -r * (1 - np.cos(theta))
        arc_y = -r * np.sin(theta)
        ax.plot(arc_x, arc_y, color="black", linewidth=D, solid_capstyle="butt")

        arc_length = r * angle_rad
        if C > arc_length:
            extra = C - arc_length
            dx = -r * np.sin(angle_rad)
            dy = -r * np.cos(angle_rad)
            norm = math.hypot(dx, dy)
            end_x = arc_x[-1]
            end_y = arc_y[-1]
            line_x = [end_x, end_x + dx / norm * extra]
            line_y = [end_y, end_y + dy / norm * extra]
            ax.plot(line_x, line_y, color="black", linewidth=D, solid_capstyle="butt")
            end_x = line_x[-1]
        else:
            end_x = arc_x[-1]
        hook_left = min(end_x, -D / 2)
        lower_limit = min(lower_limit, arc_y.min() - offset)

    # Zona roscada en gris con rayado
    if T > 0:
        thread = patches.Rectangle(
            (-D / 2, L - T),
            D,
            T,
            linewidth=1,
            edgecolor="gray",
            facecolor="none",
            hatch="////",
        )
        ax.add_patch(thread)

    # ----- Cotas -----
    right = D / 2 + offset
    left = hook_left - offset

    # Largo total
    ax.annotate(
        "",
        xy=(right, 0),
        xytext=(right, L),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(right + 2, L / 2, f"L: {L} mm", color="red", va="center")

    # Longitud de la rosca
    ax.annotate(
        "",
        xy=(left, L - T),
        xytext=(left, L),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(left - 2, L - T / 2, f"T: {T} mm", color="red", va="center", ha="right")

    # Gancho (parte inferior)
    ax.annotate(
        "",
        xy=(0, -offset / 2),
        xytext=(hook_left, -offset / 2),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(hook_left / 2, -offset / 2 - 2, f"C: {C} mm", color="red", ha="center", va="top")

    # Diametro (debajo del perno)
    y_d = L + offset * 0.2
    ax.annotate(
        "",
        xy=(-D / 2, y_d),
        xytext=(D / 2, y_d),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(0, y_d + 2, f"D: {D} mm", color="red", ha="center", va="bottom")

    # Ajustes finales del grafico
    ax.axis("off")
    ax.set_xlim(left, right + offset)
    ax.set_ylim(lower_limit, L + offset * 0.5)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Retorna el formulario principal."""
    return HTML_PATH.read_text(encoding="utf-8")


@app.get("/image")
async def image(
    bolt_type: str = Query("L", alias="type"),
    D: float = Query(20.0, alias="D"),
    L: float = Query(200.0, alias="L"),
    C: float = Query(50.0, alias="C"),
    T: float = Query(50.0, alias="T"),
    closing_angle: float = Query(180.0, alias="closing_angle"),
) -> StreamingResponse:
    """Devuelve la imagen PNG generada."""
    data = draw_bolt_diagram(bolt_type, D, L, C, T, closing_angle)
    return StreamingResponse(io.BytesIO(data), media_type="image/png")


@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("L", alias="type"),
    D: float = Query(20.0, alias="D"),
    L: float = Query(200.0, alias="L"),
    C: float = Query(50.0, alias="C"),
    T: float = Query(50.0, alias="T"),
    closing_angle: float = Query(180.0, alias="closing_angle"),
) -> str:
    """Muestra la imagen y ofrece la descarga."""
    query = (
        f"type={bolt_type}&D={D}&L={L}&C={C}&T={T}&closing_angle={closing_angle}"
    )
    img_tag = f'<img src="/image?{query}" alt="boceto">'
    download = f'<a href="/image?{query}" download="bolt.png">Descargar imagen</a>'
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"
