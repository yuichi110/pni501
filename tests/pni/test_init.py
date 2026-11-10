# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test pni module attributes."""

import pni


def test_package_metadata() -> None:
    """Test that pni package exports version and library name."""
    assert pni.LIB_NAME == "pni501"
    assert pni.LIB_VERSION == "0.1.4"
    assert pni.__version__ == "0.1.4"
