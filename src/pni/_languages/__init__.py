# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Central language metadata and Tree-sitter grammar provider registry."""

from __future__ import annotations

from pni._languages.registry import (
    GRAMMAR_PROVIDERS,
    LANGUAGE_REGISTRY,
    GrammarProviderSpec,
    GrammarSource,
    LanguageCategory,
    LanguageSpec,
    LanguageTier,
    get_grammar_provider,
    get_language_by_path,
    get_language_spec,
    iter_language_specs,
    list_supported_languages,
    register_grammar_provider,
    register_language_spec,
    resolve_grammar_for_path,
    resolve_language_id,
)

__all__ = [
    "GRAMMAR_PROVIDERS",
    "LANGUAGE_REGISTRY",
    "GrammarProviderSpec",
    "GrammarSource",
    "LanguageCategory",
    "LanguageSpec",
    "LanguageTier",
    "get_grammar_provider",
    "get_language_by_path",
    "get_language_spec",
    "iter_language_specs",
    "list_supported_languages",
    "register_grammar_provider",
    "register_language_spec",
    "resolve_grammar_for_path",
    "resolve_language_id",
]
