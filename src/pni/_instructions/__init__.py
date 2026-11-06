# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""AI agent instructions package."""

from __future__ import annotations

from pni._instructions.base_model import InstructionInfo
from pni._instructions.manager import (
    copy_instruction_templates,
    get_instructions_content,
    get_instructions_info,
)

__all__ = [
    "InstructionInfo",
    "copy_instruction_templates",
    "get_instructions_content",
    "get_instructions_info",
]
