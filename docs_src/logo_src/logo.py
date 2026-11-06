# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Official horizontal pni501 brand logo (PROJECT [△ NI] 501)."""

from drawlib.canvas import save, setup
from drawlib.styles import Colors
from drawlib.utils import draw_logo

setup(width=540, height=100, dpi=200, color=Colors.White)

draw_logo(canvas_width=540.0)

save()
