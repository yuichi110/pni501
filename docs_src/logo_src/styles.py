# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Drawlib styles configuration for pni501 brand logos."""

from __future__ import annotations

import os

from drawlib.fonts import FontFile
from drawlib.preset_colors import DefaultColors
from drawlib.preset_styles import DefaultStyles
from drawlib.styles import Color

# Project Nemesis Index (pni501) - Brand Colors
# Primary monochrome: Pure Black for Light mode, Pure White for Dark mode
COLOR_BRAND_LIGHT = DefaultColors().Black
COLOR_BRAND_DARK = DefaultColors().White

# Alternative Cyber Teal (#05A8AB) from the theatrical title logo
COLOR_CYBER_TEAL = Color(r=5, g=168, b=171)

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_assets")


# Text font: Bodoni Moda Bold (SIL Open Font License 1.1 — flat hairline serifs for PROJECT, PNI, NI)
FONT_TEXT = FontFile(os.path.join(_ASSETS_DIR, "bodoni_moda_bold.ttf"))

# Number font: Bodoni Moda Regular (SIL Open Font License 1.1 — horizontal top bar on '5' & crisp Didone '501')
FONT_NUMBERS = FontFile(os.path.join(_ASSETS_DIR, "bodoni_moda_regular.ttf"))

Colors = DefaultColors()
Styles = DefaultStyles()
