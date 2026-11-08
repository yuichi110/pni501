# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test pcli discovery and version logic."""

import pytest

from tools.pcli.common import discover_toolsets
from tools.pcli.pypi.client import (
    check_new_version_ok,
    check_version_syntax,
    get_new_version,
)


def test_discover_toolsets() -> None:
    """Test that all expected toolsets are discovered."""
    toolsets = discover_toolsets()
    assert "code-check" in toolsets
    assert "pypi" in toolsets
    assert "test" in toolsets


def test_version_syntax_valid() -> None:
    """Test valid version syntax."""
    check_version_syntax("0.1.0")
    check_version_syntax("0.1.0.dev1")
    check_version_syntax("1.2.3.rc1")


def test_version_syntax_invalid() -> None:
    """Test invalid version syntax."""
    with pytest.raises(ValueError):
        check_version_syntax("0.1")
    with pytest.raises(ValueError):
        check_version_syntax("invalid")


def test_check_new_version_initial() -> None:
    """Test initial version validation when latest_version is None."""
    check_new_version_ok(None, "0.1.0")


def test_get_new_version() -> None:
    """Test extracting new version from pyproject.toml."""
    ver = get_new_version()
    assert ver == "0.1.2"
