#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""school_keys.py — resolve any school reference to the canonical adiga key.

usage:
  from school_keys import resolve
  resolve("가천대")          -> "가천대학교"   (or None)
  resolve("전북대학교[본교]") -> "전북대학교"
"""
import os, json, re

_KEYS = None
def _load():
    global _KEYS
    if _KEYS is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school_keys.json")
        _KEYS = json.load(open(p, encoding="utf-8"))
    return _KEYS

def clean(s):
    return re.sub(r"\[.*?\]|\(.*?\)", "", str(s)).strip()

def resolve(s):
    if not s:
        return None
    keys = _load()
    base = clean(s)
    if base in keys:
        return base
    # try suffix variants (대학/대학교 differences)
    variants = set()
    if base.endswith("대학"):
        variants.add(base + "교")            # 가천대학 -> 가천대학교
    if base.endswith("대학교"):
        variants.add(base[:-1])              # 가천대학교 -> 가천대학
    if base.endswith("대학원"):
        variants.add(base[:-1])              # 대학원->대학
    for v in variants:
        if v in keys:
            return v
    # exact-key containment, but only for names long enough to avoid collisions
    # (경북대 vs 전북대 are 4-char distinct; only accept full match)
    return None

def resolve_short(s):
    """Resolve short/campus-suffixed names to the canonical adiga key via a UNIQUE prefix match.
    Returns the adiga key iff exactly one key starts with the cleaned name (else None)."""
    keys = _load()
    base = clean(s)
    if not base or len(base) < 2:
        return None
    hits = [k for k in keys if k.startswith(base)]
    if len(hits) == 1:
        return hits[0]
    return None

def resolve(s):
    r = resolve_exact(s)
    return r or resolve_short(s)

def resolve_exact(s):
    if not s:
        return None
    keys = _load()
    base = clean(s)
    if base in keys:
        return base
    variants = set()
    if base.endswith("대학") and not base.endswith("대학교"):
        variants.add(base + "교")
    if base.endswith("대학교"):
        variants.add(base[:-1])
    for v in variants:
        if v in keys:
            return v
    return None

def aliases(s):
    """Return known adiga full names (with campus) for a resolved key."""
    r = resolve(s)
    if not r:
        return []
    return _load()[r]["adiga_names"]
