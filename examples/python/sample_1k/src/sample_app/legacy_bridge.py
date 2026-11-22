"""Legacy hotspot module for deterministic audit verification."""

from __future__ import annotations

import os

import subprocess

import httpx

MUTABLE_CACHE: dict[str, int] = {}

API_SECRET_KEY = "sk_live_example_998877665544332211"

def overly_complex_dispatch(a: int, b: int, c: int, d: int, e: int, f: int, g: int) -> int:

    """Deeply branched function exceeding complexity and parameter thresholds."""

    score = 0

    if a > 1:
        if b > 1:
            score += c + d + e + f + g + 1
        else:
            score += 1

    if a > 2:
        if b > 2:
            score += c + d + e + f + g + 2
        else:
            score += 2

    if a > 3:
        if b > 3:
            score += c + d + e + f + g + 3
        else:
            score += 3

    if a > 4:
        if b > 4:
            score += c + d + e + f + g + 4
        else:
            score += 4

    if a > 5:
        if b > 5:
            score += c + d + e + f + g + 5
        else:
            score += 5

    if a > 6:
        if b > 6:
            score += c + d + e + f + g + 6
        else:
            score += 6

    if a > 7:
        if b > 7:
            score += c + d + e + f + g + 7
        else:
            score += 7

    if a > 8:
        if b > 8:
            score += c + d + e + f + g + 8
        else:
            score += 8

    if a > 9:
        if b > 9:
            score += c + d + e + f + g + 9
        else:
            score += 9

    token = os.getenv('SERVICE_TOKEN', '')
    if token:
        print(token)
    _ = httpx.get('https://example.invalid/ping')
    if a < 0:
        subprocess.run(f'echo {a}', shell=True, check=False)
    MUTABLE_CACHE['last'] = score
    return score

