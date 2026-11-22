"""Lazy loaders for bundled COBOL, R, Vue, Protobuf, and Dockerfile Tree-sitter grammars."""

from __future__ import annotations

import importlib
from typing import Final

_LANGUAGES: Final[tuple[str, ...]] = ("cobol", "r", "vue", "proto", "dockerfile")


def _load(lang_id: str) -> object:
    """Lazily import a single compiled grammar extension and return its PyCapsule."""
    mod = importlib.import_module(f"pni501_extra_grammars._{lang_id}")
    return mod.language()


def available_languages() -> tuple[str, ...]:
    """Return the tuple of bundled grammar identifiers."""
    return _LANGUAGES


def language_cobol() -> object:
    """Return the Tree-sitter Language PyCapsule for COBOL."""
    return _load("cobol")


def language_r() -> object:
    """Return the Tree-sitter Language PyCapsule for R."""
    return _load("r")


def language_vue() -> object:
    """Return the Tree-sitter Language PyCapsule for Vue SFC."""
    return _load("vue")


def language_proto() -> object:
    """Return the Tree-sitter Language PyCapsule for Protocol Buffers."""
    return _load("proto")


def language_dockerfile() -> object:
    """Return the Tree-sitter Language PyCapsule for Dockerfile."""
    return _load("dockerfile")


__all__ = [
    "available_languages",
    "language_cobol",
    "language_dockerfile",
    "language_proto",
    "language_r",
    "language_vue",
]
