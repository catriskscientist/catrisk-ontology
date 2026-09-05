# -*- coding: utf-8 -*-
"""
chatWithGraph_claude.py

    * No OpenAI key, no Anthropic API key.
    * Uses your existing Claude Code subscription via `claude -p`.
    * Override the model with:  export CLAUDE_MODEL=opus   (default: "sonnet")

Run it from THIS directory (it reads the prompt template and the .ttl by
relative path):

    python chatWithGraph_claude.py
"""

import os
import re
import json
import shutil
import textwrap
import subprocess

import pandas as pd
from rdflib import Graph

from tabulate import tabulate

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")
TTL_FILE = "cat-ontology example knowledge graph.ttl"
PROMPT_FILE = "Ontology aware prompting for SPARQL query generation.txt"

# ---------------------------------------------------------------------------
# Output layout knobs -- tune these for the paper figure
# ---------------------------------------------------------------------------
WIDTH = 60            # width of banner / section rules + text wrap (characters)
MAX_COL_WIDTH = 12    # wrap any table cell / header wider than this
PAD = "  "            # left margin applied to every body line (2 spaces)

_ACRONYMS = {"lob", "aal", "id", "url", "us", "uk", "eu", "gwp", "aep", "oep"}


# ---------------------------------------------------------------------------
# display helpers
# ---------------------------------------------------------------------------
def banner(text):
    bar = "═" * WIDTH
    return f"\n{bar}\n{text.upper()}\n{bar}"


def section(title):
    tail = "─" * max(0, WIDTH - len(title) - 2)
    return f"\n{title}  {tail}\n"


def indent(text, pad=PAD):
    return "\n".join(pad + ln for ln in str(text).splitlines())


def wrap_block(text, width=WIDTH):
    """Left-pad every line and soft-wrap long ones, keeping leading indentation.

    SPARQL is whitespace-insensitive, so wrapping is safe; long tokens such as
    URIs are never split.
    """
    limit = width - len(PAD)
    out = []
    for ln in str(text).splitlines():
        lead = " " * (len(ln) - len(ln.lstrip(" ")))
        body = ln.strip()
        if not body:
            out.append("")
            continue
        pieces = textwrap.wrap(
            body,
            width=max(12, limit - len(lead)),
            break_long_words=False,
            break_on_hyphens=False,
        ) or [body]
        out.append(PAD + lead + pieces[0])
        for p in pieces[1:]:
            out.append(PAD + lead + "  " + p)
    return "\n".join(out)


def _pretty_headers(cols, wrap=True):
    """camelCase / snake_case column names -> 'Title Case' words for the figure."""
    out = []
    for c in cols:
        words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(c)).replace("_", " ").split()
        words = [w.upper() if w.lower() in _ACRONYMS else w.capitalize() for w in words]
        label = " ".join(words) or str(c)
        if wrap:
            label = "\n".join(textwrap.wrap(label, width=MAX_COL_WIDTH)) or label
        out.append(label)
    return out


def format_meta(meta):
    """Compact one-block summary of a Claude CLI response instead of raw JSON."""
    u = meta.get("usage", {}) or {}
    dur = (meta.get("duration_ms") or 0) / 1000
    cost = meta.get("total_cost_usd")
    rows = [
        ("model", meta.get("model_name", "?")),
        ("tokens", f"in {u.get('input_tokens', 0):,}  out {u.get('output_tokens', 0):,}"
                   f"  cache {u.get('cache_creation_input_tokens', 0):,}"),
        ("time", f"{dur:.1f} s"),
    ]
    if cost is not None:
        rows.append(("cost", f"${cost:.4f}"))
    if meta.get("session_id"):
        rows.append(("session", meta["session_id"]))
    return "\n".join(f"{PAD}{k:<8}{v}" for k, v in rows)


def coerce_numeric(df, threshold=0.9):
    """Turn columns that are 'mostly numbers' into real numeric dtype."""
    df = df.copy()
    for col in df.columns:
        conv = pd.to_numeric(df[col], errors="coerce")
        if len(conv) and conv.notnull().mean() >= threshold:
            df[col] = conv
    return df


def render_table(df, max_rows=60):
    shown = df.head(max_rows).copy()
    shown.columns = _pretty_headers(shown.columns)
    table = tabulate(
        shown,
        headers="keys",
        tablefmt="fancy_grid",
        floatfmt=",.2f",
        showindex=False,
        numalign="right",
        stralign="left",
        maxcolwidths=MAX_COL_WIDTH,
    )
    out = indent(table)
    if len(df) > max_rows:
        out += f"\n{PAD}... {len(df) - max_rows:,} more rows not shown"
    return out


def totals_line(df):
    num = df.select_dtypes("number").columns
    if not len(num):
        return ""
    names = _pretty_headers(num, wrap=False)
    bits = [f"{n} = {df[c].sum():,.2f}" for n, c in zip(names, num)]
    return f"{PAD}sum   " + "    ".join(bits)


# ---------------------------------------------------------------------------
# pipeline helpers
# ---------------------------------------------------------------------------
def load_ontology(ttl_file):
    print("\nStep 1  loading ontology ...", end="", flush=True)
    g = Graph()
    g.parse(ttl_file, format="turtle")
    print(f" ok  ({len(g):,} triples)")
    return g


def build_prompt_text(user_question):
    print("Step 2  preparing prompt ...", end="", flush=True)
    with open(PROMPT_FILE, "r", encoding="utf-8") as fh:
        template_text = fh.read()
    prompt = template_text.replace("{question}", user_question)
    print(" ok")
    return prompt


def execute_sparql(g: Graph, qry: str) -> pd.DataFrame:
    """Run a SPARQL query on the graph and return the rows as a DataFrame."""
    results = g.query(qry)
    columns = [str(v) for v in results.vars]
    rows = [list(row) for row in results]
    return pd.DataFrame(rows, columns=columns)


def extract_pretty_sparql(text: str) -> str:
    """Pull a bare SPARQL query out of the model response.

    Handles ```sparql fences, plain ``` fences, and a stray sentence of prose
    before the query.
    """
    content = text.strip()

    m = re.search(r"```(?:sparql)?\s*(.*?)```", content, flags=re.DOTALL | re.IGNORECASE)
    if m:
        content = m.group(1).strip()

    m = re.search(r"(?is)\b(PREFIX|SELECT|ASK|CONSTRUCT|DESCRIBE)\b.*", content)
    if m:
        content = m.group(0).strip()

    return content


# ---------------------------------------------------------------------------
# Claude via the local CLI (no API key)
# ---------------------------------------------------------------------------
_SYSTEM = (
    "You output only a single valid SPARQL query. "
    "No prose, no explanation, no markdown code fences."
)


def call_claude(prompt_text, model=CLAUDE_MODEL, timeout=300):
    """Send `prompt_text` to Claude through the `claude` CLI, return (text, meta)."""
    cli = shutil.which("claude")
    if not cli:
        raise RuntimeError("`claude` CLI not found on PATH. Install Claude Code first.")

    cmd = [
        cli,
        "-p", prompt_text,
        "--output-format", "json",
        "--model", model,
        "--append-system-prompt", _SYSTEM,
    ]

    # If this script is itself launched from within a Claude Code session, the
    # CLI refuses to start ("cannot be launched inside another Claude Code
    # session"). Drop the marker vars so the child runs as a fresh session.
    child_env = os.environ.copy()
    for var in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SSE_PORT"):
        child_env.pop(var, None)

    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=child_env
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited {proc.returncode}:\n{proc.stderr.strip()[:800]}"
        )

    payload = json.loads(proc.stdout)
    if payload.get("is_error"):
        raise RuntimeError(f"claude returned an error: {payload.get('result', payload)}")

    text = payload.get("result", "")
    meta = {
        "model_name": payload.get("model", model),
        "usage": payload.get("usage", {}),
        "total_cost_usd": payload.get("total_cost_usd"),
        "duration_ms": payload.get("duration_ms"),
        "num_turns": payload.get("num_turns"),
        "session_id": payload.get("session_id"),
    }
    return text, meta


# ---------------------------------------------------------------------------
# main pipeline
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(banner("chat with graph · Claude"))

    g = load_ontology(TTL_FILE)

    user_question = input(f"\n{PAD}*ASK A QUESTION ABOUT YOUR DATA:\n{PAD}> ").strip()
    user_question = user_question.lstrip("#").strip()  # tolerate pasted comment lines

    prompt_text = build_prompt_text(user_question)

    print(f"\n{PAD}calling Claude ({CLAUDE_MODEL}) ...")
    raw, meta = call_claude(prompt_text)

    print(section("Claude response"))
    print(format_meta(meta))

    sparql_query = extract_pretty_sparql(raw)
    print(section("Generated SPARQL"))
    print(wrap_block(sparql_query))

    input(f"\n{PAD}proceed ? [Enter] ")

    results = coerce_numeric(execute_sparql(g, sparql_query))

    print(section(f"Results · {len(results):,} rows"))
    print(render_table(results))
    tot = totals_line(results)
    if tot:
        print("\n" + tot)

    print(f"\n{PAD}done.\n")

# summarize non-modeled incurred losses in 2020 by peril code, loss country name and lob name
# compare total incurred losses and total modeled AAL for US COMMERCIAL hurricane by year
