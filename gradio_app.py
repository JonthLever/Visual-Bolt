"""Interactive Gradio app that renders anchor bolts with Matplotlib."""

import io
from math import radians

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import gradio as gr

# Conversion factors from different units to millimeters
UNIT_TO_MM = {
    "mm": 1.0,
    "cm": 10.0,
    "inches": 25.4,
    "meters": 1000.0,
    "feet": 304.8,
}


def validate_inputs(bolt_type: str, D: float, S: float, C: float, T: float) -> str:
    """Return an error message if the parameters are invalid."""
    if any(val <= 0 for val in (D, S, C, T)):
        return "All dimensions must be positive values."
    if T > S:
        return "Thread length T cannot exceed shaft length."
    if bolt_type.upper() == "L" and C + T > S + C:
        return "For L bolts, C + T must not exceed total length."
    return ""


def draw_bolt_diagram(
    bolt_type: str,
    D: float,
    S: float,
    C: float,
    T: float,
    closing_angle: float = 180.0,
    *,
    units: str = "mm",
) -> bytes:
    """Return PNG bytes with a 2D technical diagram of an anchor bolt."""

    factor = UNIT_TO_MM.get(units, 1.0)
    D_mm = D * factor
    S_mm = S * factor
    C_mm = C * factor
    T_mm = T * factor

    fig, ax = plt.subplots(figsize=(5, 6))
    ax.set_aspect("equal")

    offset = max(D_mm * 1.5, 20)

    # vertical shaft
    ax.plot([0, 0], [0, S_mm], color="black", linewidth=D_mm, solid_capstyle="butt")

    if bolt_type.upper() == "L":
        # simple 90° hook
        ax.plot([0, -C_mm], [0, 0], color="black", linewidth=D_mm, solid_capstyle="butt")
        arc_length = C_mm
        end_x = -C_mm
        bottom_y = 0
    else:
        # curved J hook
        r = 4 * D_mm
        angle_rad = radians(closing_angle)
        theta = np.linspace(0.0, angle_rad, 60)
        arc_x = -r * (1 - np.cos(theta))
        arc_y = -r * np.sin(theta)
        ax.plot(arc_x, arc_y, color="black", linewidth=D_mm, solid_capstyle="butt")
        arc_length = r * angle_rad
        end_x = arc_x[-1]
        end_y = arc_y[-1]
        if C_mm > arc_length:
            extra = C_mm - arc_length
            dx = -np.sin(angle_rad)
            dy = -np.cos(angle_rad)
            ax.plot(
                [end_x, end_x + dx * extra],
                [end_y, end_y + dy * extra],
                color="black",
                linewidth=D_mm,
                solid_capstyle="butt",
            )
            end_x += dx * extra
            end_y += dy * extra
        bottom_y = arc_y.min()

    L_total = S_mm + arc_length

    # threaded region aligned with shaft width
    if T_mm > 0:
        thread = patches.Rectangle(
            (-D_mm / 2, S_mm - T_mm),
            D_mm,
            T_mm,
            facecolor="white",
            edgecolor="gray",
            hatch="////",
        )
        ax.add_patch(thread)

    right = D_mm / 2 + offset
    left = end_x - offset

    # total length
    ax.annotate(
        "",
        xy=(right, bottom_y),
        xytext=(right, S_mm),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(
        right + 2,
        (S_mm + bottom_y) / 2,
        f"L_total: {L_total:.1f} mm",
        color="red",
        va="center",
    )

    # thread length
    ax.annotate(
        "",
        xy=(left, S_mm - T_mm),
        xytext=(left, S_mm),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(
        left - 2,
        S_mm - T_mm / 2,
        f"T: {T} {units}",
        color="red",
        ha="right",
        va="center",
    )

    # hook length
    hook_y = bottom_y - offset * 0.3
    ax.annotate(
        "",
        xy=(0, hook_y),
        xytext=(end_x, hook_y),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(end_x / 2, hook_y - 2, f"C: {C} {units}", color="red", ha="center", va="top")

    # diameter
    diam_y = S_mm + offset * 0.3
    ax.annotate(
        "",
        xy=(-D_mm / 2, diam_y),
        xytext=(D_mm / 2, diam_y),
        arrowprops=dict(arrowstyle="<->", color="red"),
    )
    ax.text(0, diam_y + 2, f"D: {D} {units}", color="red", ha="center", va="bottom")

    if bolt_type.upper() == "J":
        ax.text(left, S_mm + offset * 0.1, f"Arc Length: {arc_length:.1f} mm", color="blue")
    ax.text(left, S_mm + offset * 0.1 - 10, f"Total Length: {L_total:.1f} mm", color="blue")

    ax.axis("off")
    ax.set_xlim(left - offset * 0.2, right + offset)
    ax.set_ylim(bottom_y - offset * 0.5, S_mm + offset * 0.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def main() -> None:
    """Launch the interactive Gradio interface."""

    with gr.Blocks() as demo:
        gr.Markdown("# Anchor Bolt Designer")

        with gr.Row():
            with gr.Column():
                bolt_type = gr.Radio(["L", "J"], label="Bolt Type", value="L")
                units = gr.Dropdown(
                    ["mm", "cm", "inches", "meters", "feet"],
                    value="mm",
                    label="Units",
                )
                D = gr.Number(value=20, label="Diameter D")
                S_val = gr.Number(value=200, label="Shaft Length S")
                C = gr.Number(value=50, label="Hook Length C")
                T = gr.Number(value=50, label="Thread Length T")
                closing_angle = gr.Number(value=180, label="Closing Angle (°)")

            with gr.Column():
                warning = gr.Markdown(visible=False)
                output_img = gr.Image(label="Diagram")
                download = gr.DownloadButton(label="Download PNG", filename="bolt.png")

        def refresh(bt, d, s, c, t, angle, unit):
            err = validate_inputs(bt, d, s, c, t)
            if err:
                return gr.update(value=f"**Error:** {err}", visible=True), None, None
            png = draw_bolt_diagram(bt, d, s, c, t, angle, units=unit)
            return gr.update(visible=False), png, png

        inputs = [bolt_type, D, S_val, C, T, closing_angle, units]

        for comp in inputs:
            comp.change(
                refresh,
                inputs=inputs,
                outputs=[warning, output_img, download],
            )

        bolt_type.change(
            lambda b: gr.update(visible=b == "J"),
            inputs=bolt_type,
            outputs=closing_angle,
        )

    demo.launch()


if __name__ == "__main__":
    main()
