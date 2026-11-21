# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative Tree-sitter analyzer suites covering all 49 extended Tier A/B/C languages."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.declarative.checkers import build_declarative_suite
from pni._actions.ast_analyze.declarative.profile import (
    BugIdiomRule,
    CustomAuditHook,
    CustomHookResult,
    CweSinkRule,
    LanguageGrammarProfile,
)
from pni._actions.ast_analyze.declarative.profiles_tier_a import TIER_A_PROFILES
from pni._actions.ast_analyze.declarative.profiles_tier_b import TIER_B_PROFILES
from pni._actions.ast_analyze.declarative.profiles_tier_c import TIER_C_PROFILES
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

ALL_DECLARATIVE_PROFILES: Final[dict[str, LanguageGrammarProfile]] = {
    profile.language_id: profile
    for profile in (*TIER_A_PROFILES, *TIER_B_PROFILES, *TIER_C_PROFILES)
}

DECLARATIVE_SUITES: Final[dict[str, LanguageAnalyzerSuite]] = {
    lang_id: build_declarative_suite(profile)
    for lang_id, profile in ALL_DECLARATIVE_PROFILES.items()
}

__all__ = [
    "ALL_DECLARATIVE_PROFILES",
    "DECLARATIVE_SUITES",
    "BugIdiomRule",
    "CustomAuditHook",
    "CustomHookResult",
    "CweSinkRule",
    "LanguageGrammarProfile",
    "build_declarative_suite",
]
