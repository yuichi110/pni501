# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Standalone pni501 icon mark for dark backgrounds with transparent canvas."""

from drawlib.canvas import save, setup
from drawlib.styles import Colors
from drawlib.utils import draw_logo_icon

setup(width=100, height=100, dpi=200, color=Colors.Black, alpha=0.0)

draw_logo_icon(canvas_width=100.0, is_dark=True, is_stencil=True)

save()
