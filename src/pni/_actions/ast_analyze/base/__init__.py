# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base classes for multi-language AST and framework checkers."""

from __future__ import annotations

from pni._actions.ast_analyze.base.dependencies import BaseDependencyChecker
from pni._actions.ast_analyze.base.docs import BaseDocChecker
from pni._actions.ast_analyze.base.framework import BaseFrameworkChecker
from pni._actions.ast_analyze.base.imports import BaseImportChecker
from pni._actions.ast_analyze.base.operational import BaseOperationalChecker
from pni._actions.ast_analyze.base.quality import BaseQualityChecker
from pni._actions.ast_analyze.base.security import BaseSecurityChecker
from pni._actions.ast_analyze.base.testing import BaseTestChecker
from pni._actions.ast_analyze.base.typing import BaseTypingChecker

__all__ = [
    "BaseDependencyChecker",
    "BaseDocChecker",
    "BaseFrameworkChecker",
    "BaseImportChecker",
    "BaseOperationalChecker",
    "BaseQualityChecker",
    "BaseSecurityChecker",
    "BaseTestChecker",
    "BaseTypingChecker",
]
