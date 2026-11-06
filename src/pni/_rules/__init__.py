# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Engineering best practice rules package."""

from __future__ import annotations

from pni._rules.base_model import RuleInfo
from pni._rules.manager import (
    SUPPORTED_LANGUAGES,
    copy_rule_templates,
    detect_active_language,
    get_rule_content,
    list_rules,
)

__all__ = [
    "SUPPORTED_LANGUAGES",
    "RuleInfo",
    "copy_rule_templates",
    "detect_active_language",
    "get_rule_content",
    "list_rules",
]
