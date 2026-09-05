# -*- coding: utf-8 -*-
"""
chatWithGraph_OpenAI.py


Setup
-----
    pip install langchain-openai
    # then either paste your key into OPENAI_API_KEY below,
    # or:  export OPENAI_API_KEY=sk-...

Run it from THIS directory (reads the prompt template + the .ttl by relative path):

    python chatWithGraph_OpenAI.py
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
# Paste your key here, OR leave it blank ("") and set the OPENAI_API_KEY
# environment variable instead (recommended -- keeps the key out of the file).
OPENAI_API_KEY = ""

# Model. Override with:  export OPENAI_MODEL=gpt-4o
#   gpt-4         $30 / $60  per 1M tokens   (default -- matches original script)
#   gpt-4-turbo   $10 / $30  per 1M tokens
#   gpt-4o        $2.50 / $10 per 1M tokens
#   gpt-4o-mini   $0.15 / $0.60 per 1M tokens
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4")
TEMPERATURE = 0.0
MAX_TOKENS = 8000

TTL_FILE = "cat-ontology example knowledge graph.ttl"
PROMPT_FILE = "Ontology aware prompting for SPARQL query generation.txt"

# list price ($ per 1M tokens) -- used only for the rough cost estimate printed
_PRICES = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.0),
    "gpt-4.1": (2.0, 8.0),
    "gpt-4-turbo": (10.0, 30.0),
    "gpt-4": (30.0, 60.0),
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
                   f"  total {u.get('total_tokens', 0):,}"),
        ("finish", meta.get("finish_reason", "?")),
        ("cost", f"${meta.get('estimated_cost_usd', 0):.4f}  (list-price est.)"),
    ]
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
# the billable OpenAI call  (LangChain ChatOpenAI, same as the original script)
# ---------------------------------------------------------------------------
def _price_for(model_name):
    for key in sorted(_PRICES, key=len, reverse=True):
        if model_name.startswith(key):
            return _PRICES[key]
    return _PRICES["gpt-4"]


def call_openai(prompt_text, model=OPENAI_MODEL, temperature=TEMPERATURE):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise SystemExit(
            "\n'langchain-openai' is not installed in this environment.\n"
            "Install it first:\n\n    pip install langchain-openai\n"
        )

    api_key = OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "\nNo OpenAI API key found.\n"
            "Paste your key into OPENAI_API_KEY at the top of this file, or run:\n\n"
            "    export OPENAI_API_KEY=sk-...\n"
        )

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=MAX_TOKENS,
    )

    try:
        resp = llm.invoke(
            [("system", _SYSTEM), ("human", prompt_text)]
        )
    except Exception as e:  # openai.RateLimitError, AuthenticationError, ...
        raise SystemExit(f"\nOpenAI call failed:\n{e}")

    content = resp.content
    text = content if isinstance(content, str) else "".join(str(x) for x in content)

    rm = getattr(resp, "response_metadata", {}) or {}
    tu = rm.get("token_usage", {}) or {}
    um = getattr(resp, "usage_metadata", None) or {}
    in_tok = um.get("input_tokens") or tu.get("prompt_tokens") or 0
    out_tok = um.get("output_tokens") or tu.get("completion_tokens") or 0
    total_tok = um.get("total_tokens") or tu.get("total_tokens") or (in_tok + out_tok)

    model_name = rm.get("model_name") or model
    in_p, out_p = _price_for(model_name)
    est_cost = (in_tok * in_p + out_tok * out_p) / 1_000_000

    meta = {
        "model_name": model_name,
        "finish_reason": rm.get("finish_reason", "?"),
        "usage": {
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": total_tok,
        },
        "estimated_cost_usd": round(est_cost, 4),
    }
    return text, meta


# ---------------------------------------------------------------------------
# main pipeline
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(banner("chat with graph · OpenAI (billable)"))

    g = load_ontology(TTL_FILE)

    user_question = input(f"\n{PAD}*ASK A QUESTION ABOUT YOUR DATA:\n{PAD}> ").strip()
    user_question = user_question.lstrip("#").strip()  # tolerate pasted comment lines

    prompt_text = build_prompt_text(user_question)

    print(f"\n{PAD}calling OpenAI ({OPENAI_MODEL}) -- BILLABLE ...")
    raw, meta = call_openai(prompt_text)

    print(section("OpenAI response"))
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
