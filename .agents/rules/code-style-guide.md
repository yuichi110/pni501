---
trigger: model_decision
description: Coding Guidelines for pni501
---

# Code Style Guide for pni501

This document defines the coding standards and style guidelines for the `pni501` project.

## 1. General Principles
- **Target Python Version**: Python 3.11 or higher.
- **Standard Compliance**: Follow PEP 8.
- **Formatting & Linting**:
  - Use `ruff` for both linting and formatting.
  - Max line length is **120** characters.
  - Use `ty` for static type checking (`./pcli code-check type` or `uv run ty check`).

## 2. Naming Conventions
- **Modules and Packages**: `snake_case`. Keep names short and descriptive.
- **Classes**: `PascalCase`.
- **Functions and Methods**: `snake_case`.
- **Constants**: `UPPER_SNAKE_CASE` or `Final[T]`.

## 3. Type Hinting
- All public functions and methods must have complete type hints for arguments and return values.
- Use `from __future__ import annotations`.

## 4. Documentation (Docstrings)
- Follow the Google Python Style Guide for docstrings.
- All public modules, classes, and functions must have docstrings.

## 5. File Header
All Python source files must start with the following copyright and license header:

```python
# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
```
