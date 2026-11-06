# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for engineering best practice rules."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class RuleInfo(BaseModel):
    """Metadata describing a best practice rule."""

    scope: str
    name: str
    title: str
    path: Path
    is_local: bool

    @property
    def identifier(self) -> str:
        """Return the fully qualified rule identifier (e.g. 'common/architecture')."""
        return f"{self.scope}/{self.name}"
