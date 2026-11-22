# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Centralized environment settings for on-demand Tree-sitter grammar asset resolution."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GrammarAssetSettings:
    """Resolved environment overrides for PNI extra Tree-sitter grammar caching."""

    base_url: str
    release_tag: str
    cache_dir: str
    local_app_data: str
    xdg_cache_home: str


def load_grammar_asset_settings() -> GrammarAssetSettings:
    """Read all grammar-asset environment variables from a single centralized config module."""
    return GrammarAssetSettings(
        base_url=os.environ.get("PNI_GRAMMAR_BASE_URL", "").strip().rstrip("/"),
        release_tag=os.environ.get("PNI_GRAMMAR_RELEASE_TAG", "").strip(),
        cache_dir=os.environ.get("PNI_GRAMMAR_CACHE_DIR", "").strip(),
        local_app_data=os.environ.get("LOCALAPPDATA", "").strip(),
        xdg_cache_home=os.environ.get("XDG_CACHE_HOME", "").strip(),
    )


__all__ = ["GrammarAssetSettings", "load_grammar_asset_settings"]
