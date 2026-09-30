# -*- coding: utf-8 -*-
"""Shared, safe reader/writer for data.js.

data.js carries THREE globals that the CRM app reads at runtime:
    window.UNIV_KNOWLEDGE = [ ... ];   (array of university records)
    window.UNIV_GUIDES    = { ... };   (school -> {ba,ma,lang} guide URLs)
    window.UNIV_SPECIAL   = { ... };   (visa-restricted / free-major / medical sections)

Historical incident: a one-off rewrite of data.js dropped the whole
`window.UNIV_GUIDES = {...};` block and left a stray `]}}};` behind, so the file
stopped parsing (SyntaxError) and EVERY global after it failed to load.
The previous writers split the file with a naive `[`/`]` counter (not
string-aware) and never validated the result before writing.

This module makes that impossible:
  * parse: string-aware brace/bracket matching; ALL THREE globals must be found
    or it raises (a missing global ABORTS instead of being silently dropped)
  * counts: record counts may never shrink (caller passes the previous minimums)
  * syntax: the rendered text must pass `node --check` (real JS parse)
  * atomicity: write to a temp file then os.replace; a timestamped backup is kept
"""
import json
import os
import shutil
import subprocess
import sys
import datetime

GLOBALS = ("UNIV_KNOWLEDGE", "UNIV_GUIDES", "UNIV_SPECIAL")


def _match(text, start, open_ch, close_ch):
    """Index of the bracket that closes text[start], ignoring brackets inside strings."""
    depth = 0
    instr = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced %s%s starting at %d" % (open_ch, close_ch, start))


def _slice(text, marker, open_ch, close_ch):
    at = text.find("window." + marker)
    if at < 0:
        raise ValueError("window.%s not found in data.js" % marker)
    b = text.find(open_ch, at)
    if b < 0:
        raise ValueError("window.%s: no '%s' after marker" % (marker, open_ch))
    e = _match(text, b, open_ch, close_ch)
    return at, text[b:e + 1]


def parse_globals_from_text(text):
    """Return {prefix, knowledge, guides, special} or raise if any global is missing."""
    k_at, k_txt = _slice(text, "UNIV_KNOWLEDGE", "[", "]")
    g_at, g_txt = _slice(text, "UNIV_GUIDES", "{", "}")
    s_at, s_txt = _slice(text, "UNIV_SPECIAL", "{", "}")
    if not (k_at < g_at < s_at):
        raise ValueError("data.js globals are out of order: KNOWLEDGE@%d GUIDES@%d SPECIAL@%d"
                         % (k_at, g_at, s_at))
    return {
        "prefix": text[:k_at],
        "knowledge": json.loads(k_txt),
        "guides": json.loads(g_txt),
        "special": json.loads(s_txt),
    }


def parse_globals(path):
    return parse_globals_from_text(open(path, encoding="utf-8").read())


def render(prefix, knowledge, guides, special, knowledge_indent=1):
    """Rebuild the whole file text (\n newlines). All three globals always emitted."""
    return (prefix
            + "window.UNIV_KNOWLEDGE = "
            + json.dumps(knowledge, ensure_ascii=False, indent=knowledge_indent)
            + ";\n\n"
            + "window.UNIV_GUIDES = " + json.dumps(guides, ensure_ascii=False) + ";\n\n"
            + "window.UNIV_SPECIAL = " + json.dumps(special, ensure_ascii=False) + ";\n")


def counts(text):
    g = parse_globals_from_text(text)
    return {"UNIV_KNOWLEDGE": len(g["knowledge"]),
            "UNIV_GUIDES": len(g["guides"]),
            "UNIV_SPECIAL": len(g["special"])}


def node_check(text):
    """Raise unless the text is a syntactically valid JS file (node --check)."""
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_datajs_check_tmp.js")
    try:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError("node --check FAILED:\n" + (r.stderr or r.stdout))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def write_safe(path, text, expect=None, backup=True):
    """Validate then atomically replace data.js. Never leaves a partial file.

    expect: dict with minimum counts, e.g. {"UNIV_KNOWLEDGE": 322, "UNIV_GUIDES": 174,
    "UNIV_SPECIAL": 5}. A shrink ABORTS the write.
    """
    body = text.replace("\r\n", "\n")
    have = counts(body)
    if expect:
        for name, minimum in expect.items():
            if minimum is not None and have.get(name, 0) < minimum:
                raise ValueError("ABORT: %s count %d < required %d (refusing to shrink KB)"
                                 % (name, have.get(name, 0), minimum))
    node_check(body)
    if backup and os.path.exists(path):
        bak = path.replace(".js", "_bak_%s.js" % datetime.date.today().isoformat())
        if not os.path.exists(bak):
            shutil.copy(path, bak)
            print("backup:", bak)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(body)          # newline='\r\n' -> LF in body becomes CRLF on disk
    os.replace(tmp, path)
    return have


def load_and_guard(path):
    """Convenience: parse + return globals, raising a clear error if any is missing."""
    try:
        return parse_globals(path)
    except ValueError as ex:
        print("data.js integrity check failed:", ex, file=sys.stderr)
        raise