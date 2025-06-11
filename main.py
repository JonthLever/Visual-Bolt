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

# Matplotlib se emplea en modo "Agg" para que funcione sin servidor de ventanas
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

app = FastAPI()

# Ruta al archivo HTML con el formulario
HTML_PATH = Path(__file__).parent / "static" / "index.html"


def draw_bolt_diagram(bolt_type: str, D: float, L: float, C: float, T: float) -> bytes:
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
    """

    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_aspect("equal")

    # Espaciado alrededor del perno para colocar las cotas
    offset = max(D * 2.0, 20.0)

    # --------- Dibujo del perno ---------
    ax.plot([0, 0], [0, L], color="black", linewidth=D, solid_capstyle="butt")

    if bolt_type.upper() == "L":
        ax.plot([0, -C], [0, 0], color="black", linewidth=D, solid_capstyle="butt")
        hook_left = -C
    else:  # tipo J
        r = 4 * D
        steps = 40
        arc_x = []
        arc_y = []
        for i in range(steps + 1):
            theta = -math.pi * i / steps
            arc_x.append(-r + r * math.cos(theta))
            arc_y.append(r * math.sin(theta))
        ax.plot(arc_x, arc_y, color="black", linewidth=D, solid_capstyle="butt")
        if C > 2 * r:
            ax.plot([-C, -2 * r], [0, 0], color="black", linewidth=D, solid_capstyle="butt")
        hook_left = -max(C, 2 * r)

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
        xytext=(-C, -offset / 2),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(-C / 2, -offset / 2 - 2, f"C: {C} mm", color="red", ha="center", va="top")

    # Diametro (debajo del perno)
    ax.annotate(
        "",
        xy=(-D / 2, -offset),
        xytext=(D / 2, -offset),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(0, -offset - 2, f"D: {D} mm", color="red", ha="center", va="top")

    # Ajustes finales del grafico
    ax.axis("off")
    ax.set_xlim(left, right + offset)
    ax.set_ylim(-offset * 1.5, L + offset * 0.5)

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
) -> StreamingResponse:
    """Devuelve la imagen PNG generada."""
    data = draw_bolt_diagram(bolt_type, D, L, C, T)
    return StreamingResponse(io.BytesIO(data), media_type="image/png")


@app.get("/draw", response_class=HTMLResponse)
async def draw_page(
    bolt_type: str = Query("L", alias="type"),
    D: float = Query(20.0, alias="D"),
    L: float = Query(200.0, alias="L"),
    C: float = Query(50.0, alias="C"),
    T: float = Query(50.0, alias="T"),
) -> str:
    """Muestra la imagen y ofrece la descarga."""
    query = f"type={bolt_type}&D={D}&L={L}&C={C}&T={T}"
    img_tag = f'<img src="/image?{query}" alt="boceto">'
    download = f'<a href="/image?{query}" download="bolt.png">Descargar imagen</a>'
    back = '<p><a href="/">Volver</a></p>'
    return f"<h1>Boceto generado</h1>{img_tag}<br>{download}{back}"