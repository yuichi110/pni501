# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Built-in verification harness Dockerfiles and target-scoped .pni/dockerfiles/ materialization."""

from __future__ import annotations

from pni._dockerfiles.manager import (
    BUILTIN_DOCKERFILES_DIR,
    DOCKERFILES_REL_DIR,
    ensure_target_dockerfile,
    list_builtin_dockerfiles,
    resolve_template_dockerfile,
)

__all__ = [
    "BUILTIN_DOCKERFILES_DIR",
    "DOCKERFILES_REL_DIR",
    "ensure_target_dockerfile",
    "list_builtin_dockerfiles",
    "resolve_template_dockerfile",
]
