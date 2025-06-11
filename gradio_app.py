"""Gradio interface to generate technical drawings of anchor bolts."""

import io
from math import radians

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import gradio as gr


def draw_bolt_diagram(bolt_type: str, D: float, L: float, C: float, T: float, closing_angle: float = 180.0) -> bytes:
    """Return PNG image bytes with a technical drawing of an anchor bolt."""
    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_aspect("equal")

    offset = max(D * 1.5, 20)

    # vertical shaft
    ax.plot([0, 0], [0, L], color="black", linewidth=D, solid_capstyle="butt")

    if bolt_type.upper() == "L":
        ax.plot([0, -C], [0, 0], color="black", linewidth=D, solid_capstyle="butt")
        arc_length = C
        end_x = -C
        end_y = 0
        bottom_y = 0
    else:
        r = 4 * D
        angle_rad = radians(closing_angle)
        theta = np.linspace(0, angle_rad, 60)
        arc_x = -r * (1 - np.cos(theta))
        arc_y = -r * np.sin(theta)
        ax.plot(arc_x, arc_y, color="black", linewidth=D, solid_capstyle="butt")
        arc_length = r * angle_rad
        end_x = arc_x[-1]
        end_y = arc_y[-1]
        if C > arc_length:
            extra = C - arc_length
            dx = -np.sin(angle_rad)
            dy = -np.cos(angle_rad)
            ax.plot([end_x, end_x + dx * extra], [end_y, end_y + dy * extra],
                    color="black", linewidth=D, solid_capstyle="butt")
            end_x += dx * extra
            end_y += dy * extra
        bottom_y = arc_y.min()

    L_total = L + arc_length

    # threaded region
    if T > 0:
        thread = patches.Rectangle((-D / 2, L - T), D, T,
                                   facecolor="white", edgecolor="gray", hatch="////")
        ax.add_patch(thread)

    right = D / 2 + offset
    left = end_x - offset

    # Total length dimension
    ax.annotate("", xy=(right, bottom_y), xytext=(right, L),
                arrowprops=dict(arrowstyle="<->", color="red"))
    ax.text(right + 2, (L + bottom_y) / 2, f"L_total: {L_total:.1f} mm", color="red", va="center")

    # Thread dimension
    ax.annotate("", xy=(left, L - T), xytext=(left, L),
                arrowprops=dict(arrowstyle="<->", color="red"))
    ax.text(left - 2, L - T / 2, f"T: {T} mm", color="red", ha="right", va="center")

    # Hook dimension
    hook_y = bottom_y - offset * 0.3
    ax.annotate("", xy=(0, hook_y), xytext=(end_x, hook_y),
                arrowprops=dict(arrowstyle="<->", color="red"))
    ax.text(end_x / 2, hook_y - 2, f"C: {C} mm", color="red", ha="center", va="top")

    # Diameter dimension
    diam_y = L + offset * 0.3
    ax.annotate("", xy=(-D / 2, diam_y), xytext=(D / 2, diam_y),
                arrowprops=dict(arrowstyle="<->", color="red"))
    ax.text(0, diam_y + 2, f"D: {D} mm", color="red", ha="center", va="bottom")

    # labels for arc length and total length
    ax.text(left, L + offset * 0.1, f"Arc Length: {arc_length:.1f} mm", color="blue")
    ax.text(left, L + offset * 0.1 - 10, f"Total Length: {L_total:.1f} mm", color="blue")

    ax.axis("off")
    ax.set_xlim(left - offset * 0.2, right + offset)
    ax.set_ylim(bottom_y - offset * 0.5, L + offset * 0.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate(bolt_type, D, L, C, T, closing_angle):
    return draw_bolt_diagram(bolt_type, D, L, C, T, closing_angle)


def main():
    interface = gr.Interface(
        fn=generate,
        inputs=[
            gr.Radio(["L", "J"], label="Bolt Type", value="L"),
            gr.Number(label="Diameter D (mm)", value=20),
            gr.Number(label="Straight Length L (mm)", value=200),
            gr.Number(label="Hook Length C (mm)", value=50),
            gr.Number(label="Thread Length T (mm)", value=50),
            gr.Number(label="Closing Angle (°)", value=180),
        ],
        outputs=gr.Image(type="pil", label="Diagram"),
        live=True,
        title="Anchor Bolt Diagram",
        description="Interactive drawing of L or J anchor bolts. Closing angle only applies to J-type bolts.",
    )
    interface.launch()


if __name__ == "__main__":
    main()
