# -*- coding: utf-8 -*-
"""
chatWithGraph_anthropic.py

Direct Anthropic API version of the pipeline.  ***THIS MAKES A BILLABLE API CALL.***

    * Uses the official `anthropic` Python SDK (pip install anthropic).
    * Billed to your Anthropic API account / console credits -- NOT your Claude
      Code subscription. (For the no-extra-cost route use chatWithGraph_claude.py,
      which shells out to the `claude` CLI instead.)

Setup
-----
    pip install anthropic
    # then either paste your key into ANTHROPIC_API_KEY below,
    # or:  export ANTHROPIC_API_KEY=sk-ant-...

Run it from THIS directory (reads the prompt template + the .ttl by relative path):

    python chatWithGraph_anthropic.py
"""

import os
import re
import json  # noqa: F401  (kept for parity with the other scripts)
import textwrap

import pandas as pd
from rdflib import Graph
from tabulate import tabulate


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# Paste your key here, OR leave it blank ("") and set the ANTHROPIC_API_KEY
# environment variable instead (recommended -- keeps the key out of the file).
ANTHROPIC_API_KEY = ""

# Model. Override with:  export ANTHROPIC_MODEL=claude-sonnet-5
#   claude-opus-5     $5 / $25  per 1M tokens   (default, best SPARQL)
#   claude-sonnet-5   $2 / $10  per 1M tokens
#   claude-haiku-4-5  $1 / $5   per 1M tokens   (cheapest, weakest)
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
MAX_TOKENS = 8000

TTL_FILE = "cat-ontology example knowledge graph.ttl"
PROMPT_FILE = "Ontology aware prompting for SPARQL query generation.txt"


# list price ($ per 1M tokens) -- used only for the rough cost estimate printed
_PRICES = {
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}

_SYSTEM = (
    "You output only a single valid SPARQL query. "
    "No prose, no explanation, no markdown code fences."
)


# ---------------------------------------------------------------------------
# Output layout knobs -- tune these for the paper figure
# ---------------------------------------------------------------------------
WIDTH = 60            # width of banner / section rules + text wrap (characters)
MAX_COL_WIDTH = 12    # wrap any table cell / header wider than this
PAD = "  "            # left margin applied to every body line (2 spaces)

_ACRONYMS = {"lob", "aal", "id", "url", "us", "uk", "eu", "gwp", "aep", "oep"}


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
    u = meta.get("usage", {})
    rows = [
        ("model", meta.get("model_name", "?")),
        ("tokens", f"in {u.get('input_tokens', 0):,}  out {u.get('output_tokens', 0):,}"
                   f"  cache {u.get('cache_read_input_tokens', 0):,}"),
        ("stop", meta.get("stop_reason", "?")),
        ("cost", f"${meta.get('estimated_cost_usd', 0):.4f}  (list-price est.)"),
    ]
    if meta.get("request_id"):
        rows.append(("req id", meta["request_id"]))
    return "\n".join(f"{PAD}{k:<8}{v}" for k, v in rows)


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
    """Pull a bare SPARQL query out of the model response."""
    content = text.strip()

    m = re.search(r"```(?:sparql)?\s*(.*?)```", content, flags=re.DOTALL | re.IGNORECASE)
    if m:
        content = m.group(1).strip()

    m = re.search(r"(?is)\b(PREFIX|SELECT|ASK|CONSTRUCT|DESCRIBE)\b.*", content)
    if m:
        content = m.group(0).strip()

    return content


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
# the billable Anthropic API call
# ---------------------------------------------------------------------------
def call_anthropic(prompt_text, model=ANTHROPIC_MODEL, max_tokens=MAX_TOKENS):
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "\nThe 'anthropic' package is not installed in this environment.\n"
            "Install it first:\n\n    pip install anthropic\n"
        )

    api_key = ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "\nNo Anthropic API key found.\n"
            "Paste your key into ANTHROPIC_API_KEY at the top of this file, or run:\n\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
        )

    client = anthropic.Anthropic(api_key=api_key)

    try:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt_text}],
        )
    except anthropic.APIStatusError as e:
        raise SystemExit(f"\nAnthropic API error {e.status_code}: {e.message}")
    except anthropic.APIConnectionError as e:
        raise SystemExit(f"\nCould not reach the Anthropic API: {e}")

    if resp.stop_reason == "refusal":
        raise SystemExit("\nClaude declined this request (safety). No SPARQL generated.")

    text = "".join(b.text for b in resp.content if b.type == "text")

    u = resp.usage
    in_p, out_p = _PRICES.get(model, (0.0, 0.0))
    cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(u, "cache_creation_input_tokens", 0) or 0
    est_cost = (
        (u.input_tokens or 0) * in_p
        + (u.output_tokens or 0) * out_p
        + cache_read * in_p * 0.1
        + cache_write * in_p * 1.25
    ) / 1_000_000

    meta = {
        "model_name": resp.model,
        "stop_reason": resp.stop_reason,
        "usage": {
            "input_tokens": u.input_tokens,
            "output_tokens": u.output_tokens,
            "cache_read_input_tokens": cache_read,
            "cache_creation_input_tokens": cache_write,
        },
        "estimated_cost_usd": round(est_cost, 4),
        "request_id": getattr(resp, "_request_id", None),
    }
    return text, meta


# ---------------------------------------------------------------------------
# main pipeline
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(banner("chat with graph · Anthropic API (billable)"))

    g = load_ontology(TTL_FILE)

    user_question = input(f"\n{PAD}*ASK A QUESTION ABOUT YOUR DATA:\n{PAD}> ").strip()
    user_question = user_question.lstrip("#").strip()  # tolerate pasted comment lines

    prompt_text = build_prompt_text(user_question)

    print(f"\n{PAD}calling Anthropic API ({ANTHROPIC_MODEL}) -- BILLABLE ...")
    raw, meta = call_anthropic(prompt_text)

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
