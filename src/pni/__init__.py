# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Project Nemesis Index (PNI) - Evaluate software development project health and generate reports."""

from __future__ import annotations

from typing import Final

LIB_NAME: Final[str] = "pni501"
LIB_VERSION: Final[str] = "0.1.3"

__version__: Final[str] = LIB_VERSION

__all__ = [
    "LIB_NAME",
    "LIB_VERSION",
    "__version__",
]
