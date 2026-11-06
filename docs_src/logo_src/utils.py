# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Reusable drawing utilities for the pni501 brand logo and icon mark."""

from __future__ import annotations

import os

import numpy as np
from drawlib.canvas import clear, get_dimage, setup
from drawlib.fonts import FontFile
from drawlib.images import image
from drawlib.shapes import triangle
from drawlib.styles import Color, Colors, Styles
from drawlib.text import text
from PIL import Image

# Primary brand colors: Pure Black (Light) / Pure White (Dark)
# Alternative Cyber Teal sampled from theatrical Ghost in the Shell logo (#05A8AB)
COLOR_CYBER_TEAL = Color(r=5, g=168, b=171)

# Single-family SIL Open Font License 1.1 Didone typography (Bodoni Moda):
# - FONT_TEXT (Bodoni Moda Bold): Flat unbracketed hairline serifs for PROJECT, PNI, NI
# - FONT_NUMBERS (Bodoni Moda Regular): Crisp Didone numerals for '501'
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_assets")
FONT_TEXT = FontFile(os.path.join(_ASSETS_DIR, "bodoni_moda_bold.ttf"))
FONT_NUMBERS = FontFile(os.path.join(_ASSETS_DIR, "bodoni_moda_regular.ttf"))


def draw_logo_icon(
    *,
    canvas_width: float = 100.0,
    is_dark: bool = False,
    is_stencil: bool = False,
) -> None:
    """Draw the standalone pni501 minimal icon mark in a 100x100 coordinate space.

    The icon mark is an equilateral-proportioned solid triangle containing
    'PNI' (Bodoni Moda Bold) and '501' (Bodoni Moda Regular with calibrated optical scale).
    Pure Black on light backgrounds; Pure White on dark backgrounds.

    If is_stencil=True, the letters 'PNI' and '501' are cut out transparently
    from the solid triangle, allowing the background behind the logo to show through.

    Args:
        canvas_width: Virtual width of the active canvas (defaults to 100.0).
        is_dark: Whether to use dark mode styling.
        is_stencil: Whether to cut out inscribed letters transparently.
    """
    scale = canvas_width / 100.0
    tri_color = Colors.White if is_dark else Colors.Black
    txt_color = Colors.Black if is_dark else Colors.White

    tri_w, tri_h = 92.0 * scale, 80.0 * scale
    tri_cx, tri_cy = 50.0 * scale, 50.0 * scale
    pni_size = 142.84 * scale
    num_size = 178.81 * scale
    pni_y = 48.5 * scale
    num_y = 26.5 * scale

    if not is_stencil:
        style_tri = Styles.PrimaryFlat.patch(
            shape_fill_color=tri_color,
            shape_line_color=tri_color,
            shape_line_width=0.0,
        )
        triangle((tri_cx, tri_cy), width=tri_w, height=tri_h, style=style_tri)

        style_pni = Styles.DarkBold.patch(
            text_color=txt_color,
            text_size=pni_size,
            text_font=FONT_TEXT,
            halign="center",
            valign="center",
        )
        text((50.0 * scale, pni_y), "PNI", style=style_pni)

        style_501 = Styles.DarkBold.patch(
            text_color=txt_color,
            text_size=num_size,
            text_font=FONT_NUMBERS,
            halign="center",
            valign="center",
        )
        text((50.0 * scale, num_y), "501", style=style_501)
        return

    # Stencil rendering (cutout transparent letters)
    icon_dim = round(canvas_width)
    setup(width=icon_dim, height=icon_dim, dpi=200, color=Colors.White, alpha=0.0)
    style_tri = Styles.PrimaryFlat.patch(
        shape_fill_color=tri_color,
        shape_line_color=tri_color,
        shape_line_width=0.0,
    )
    triangle((tri_cx, tri_cy), width=tri_w, height=tri_h, style=style_tri)
    tri_arr = np.array(get_dimage().get_pil_image())
    clear()

    setup(width=icon_dim, height=icon_dim, dpi=200, color=Colors.Black)
    style_pni = Styles.DarkBold.patch(
        text_color=Colors.White,
        text_size=pni_size,
        text_font=FONT_TEXT,
        halign="center",
        valign="center",
    )
    text((50.0 * scale, pni_y), "PNI", style=style_pni)

    style_501 = Styles.DarkBold.patch(
        text_color=Colors.White,
        text_size=num_size,
        text_font=FONT_NUMBERS,
        halign="center",
        valign="center",
    )
    text((50.0 * scale, num_y), "501", style=style_501)
    txt_arr = np.array(get_dimage().get_pil_image())
    clear()

    tri_alpha = tri_arr[:, :, 3].astype(float)
    mask_norm = txt_arr[:, :, 0].astype(float) / 255.0
    cutout_alpha = np.clip(tri_alpha * (1.0 - mask_norm), 0, 255).astype(np.uint8)

    stencil_arr = np.zeros_like(tri_arr)
    stencil_arr[:, :, :3] = 255 if is_dark else 0
    stencil_arr[:, :, 3] = cutout_alpha
    stencil_pil = Image.fromarray(stencil_arr, mode="RGBA")

    setup(width=icon_dim, height=icon_dim, dpi=200, color=Colors.White, alpha=0.0)
    image((50.0 * scale, 50.0 * scale), width=canvas_width, image=stencil_pil)


def draw_logo(
    *,
    canvas_width: float = 540.0,
    is_dark: bool = False,
    is_stencil: bool = False,
) -> None:
    """Draw the official horizontal pni501 brand logo: PROJECT [△ NI] 501.

    Flanked by 'PROJECT' on the left and '501' on the right, with an elevated
    solid triangle containing 'NI' in the center (homage to 'GHOST [△ IN THE] SHELL'
    and Project 2501 where 'ni' represents '2').
    Pure Black on light backgrounds; Pure White on dark backgrounds.

    If is_stencil=True, the letter 'NI' is cut out transparently from the central
    triangle, allowing the background behind the logo to show through.

    Designed for a 540x100 coordinate space with balanced margins.

    Args:
        canvas_width: Virtual width of the active canvas (defaults to 540.0).
        is_dark: Whether to use dark mode styling.
        is_stencil: Whether to cut out inscribed letters transparently.
    """
    scale = canvas_width / 540.0
    brand_color = Colors.White if is_dark else Colors.Black
    inscribed_color = Colors.Black if is_dark else Colors.White

    # Calibrated Bodoni Moda geometry: symmetric outer margins & matching baseline
    project_bottom_y = 6.77 * scale
    num_bottom_y = 5.15 * scale
    project_x = 307.47 * scale
    tri_base_y = 16.0 * scale
    tri_h = 68.0 * scale
    tri_w = 74.0 * scale
    tri_cx = 358.96 * scale
    tri_cy = tri_base_y + tri_h / 2.0
    num_x = 410.42 * scale
    ni_y = 35.27 * scale

    project_size = 74.52 * scale
    ni_size = 38.55 * scale
    num_size = 80.47 * scale

    if not is_stencil:
        style_project = Styles.DarkBold.patch(
            text_color=brand_color,
            text_size=project_size,
            text_font=FONT_TEXT,
            halign="right",
            valign="bottom",
        )
        text((project_x, project_bottom_y), "PROJECT", style=style_project)

        style_tri = Styles.PrimaryFlat.patch(
            shape_fill_color=brand_color,
            shape_line_color=brand_color,
            shape_line_width=0.0,
        )
        triangle((tri_cx, tri_cy), width=tri_w, height=tri_h, style=style_tri)

        style_ni = Styles.DarkBold.patch(
            text_color=inscribed_color,
            text_size=ni_size,
            text_font=FONT_TEXT,
            halign="center",
            valign="center",
        )
        text((tri_cx, ni_y), "NI", style=style_ni)

        style_501 = Styles.DarkBold.patch(
            text_color=brand_color,
            text_size=num_size,
            text_font=FONT_NUMBERS,
            halign="left",
            valign="bottom",
        )
        text((num_x, num_bottom_y), "501", style=style_501)
        return

    # Stencil rendering (cutout transparent 'NI' inside central triangle)
    canvas_w = round(canvas_width)
    canvas_h = round(100.0 * scale)
    setup(width=canvas_w, height=canvas_h, dpi=200, color=Colors.White, alpha=0.0)
    style_project = Styles.DarkBold.patch(
        text_color=brand_color,
        text_size=project_size,
        text_font=FONT_TEXT,
        halign="right",
        valign="bottom",
    )
    text((project_x, project_bottom_y), "PROJECT", style=style_project)

    style_tri = Styles.PrimaryFlat.patch(
        shape_fill_color=brand_color,
        shape_line_color=brand_color,
        shape_line_width=0.0,
    )
    triangle((tri_cx, tri_cy), width=tri_w, height=tri_h, style=style_tri)

    style_501 = Styles.DarkBold.patch(
        text_color=brand_color,
        text_size=num_size,
        text_font=FONT_NUMBERS,
        halign="left",
        valign="bottom",
    )
    text((num_x, num_bottom_y), "501", style=style_501)
    base_arr = np.array(get_dimage().get_pil_image())
    clear()

    setup(width=canvas_w, height=canvas_h, dpi=200, color=Colors.Black)
    style_ni = Styles.DarkBold.patch(
        text_color=Colors.White,
        text_size=ni_size,
        text_font=FONT_TEXT,
        halign="center",
        valign="center",
    )
    text((tri_cx, ni_y), "NI", style=style_ni)
    ni_arr = np.array(get_dimage().get_pil_image())
    clear()

    base_alpha = base_arr[:, :, 3].astype(float)
    mask_norm = ni_arr[:, :, 0].astype(float) / 255.0
    cutout_alpha = np.clip(base_alpha * (1.0 - mask_norm), 0, 255).astype(np.uint8)

    stencil_arr = base_arr.copy()
    stencil_arr[:, :, 3] = cutout_alpha
    stencil_pil = Image.fromarray(stencil_arr, mode="RGBA")

    setup(width=canvas_w, height=canvas_h, dpi=200, color=Colors.White, alpha=0.0)
    image((canvas_width / 2.0, 50.0 * scale), width=canvas_width, image=stencil_pil)
