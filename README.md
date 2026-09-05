# Data & Code Availability — Catastrophe Risk Ontology and Hurricane Loss Normalization

This repository is the data and code companion to the paper:

> **Ontologies for Catastrophe Risk Management and Analytics**
> Sashi Kanth Tadinada, Ph.D
> *(Under review)*

**Project home:** the Catastrophe Risk Ontology (CRO) is maintained at
<https://github.com/catriskscientist/catrisk-ontology> and published under the persistent
identifier <https://w3id.org/catrisk/ontology/>.

It bundles the **Catastrophe Risk Ontology (CRO)**, a populated example knowledge graph,
worked SPARQL queries, a natural-language "chat with your graph" pipeline (NL → SPARQL via an LLM),
and the hurricane **claims-normalization** and **loss-normalization / model-validation** datasets and
analysis used in the paper.

Everything needed to inspect the ontology, run the example queries, reproduce the
loss-normalization figures, and try the LLM query-generation workflow is included here.

---

## How to cite

The paper is currently under review; the final citation and DOI will be added on
publication. In the meantime, please cite:

```bibtex
@unpublished{tadinada_catrisk_ontologies,
  title  = {Ontologies for Catastrophe Risk Management and Analytics},
  author = {Tadinada, Sashi Kanth},
  note   = {Manuscript under review},
  year   = {2026}
}

@misc{catrisk_ontology,
  title        = {Catastrophe Risk Ontology (CRO)},
  author       = {Tadinada, Sashi Kanth},
  howpublished = {\url{https://w3id.org/catrisk/ontology/}},
  note         = {Source and documentation: \url{https://github.com/catriskscientist/catrisk-ontology}}
}
```

## License

Released under **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**.
You are free to share and adapt the material for any purpose, including commercially,
provided you give appropriate credit to the paper above.

## Ontology namespace

The ontology is published under the persistent identifier
**`https://w3id.org/catrisk/ontology/`** (prefix `cro: https://w3id.org/catrisk/ontology#`),
which resolves to the canonical ontology; source and documentation live at
<https://github.com/catriskscientist/catrisk-ontology>. The `ontology.ttl` file in this
bundle is the version accompanying the paper.

---

## File manifest

| File | Path | Description |
|------|------|-------------|
| `ontology.ttl` | `./ontology.ttl` | The **Catastrophe Risk Ontology (CRO)** in Turtle/RDF — the full class hierarchy, object and data properties, and axioms (namespace `cro:`). This is the authoritative machine-readable schema for the framework. Imports GeoSPARQL, OWL-Time, SKOS, and Dublin Core vocabularies. |
| `Catastrophe Risk Ontology - Classes, Properties.xlsx` | `./Catastrophe Risk Ontology - Classes, Properties.xlsx` | Human-readable companion to `ontology.ttl`. **`class`** sheet: 52 classes with labels and descriptions. **`property`** sheet: 125 object/data properties as *source → property → target*, with labels, descriptions, and OWL characteristics (functional, inverse-functional, symmetric, transitive, reflexive, cardinality bounds). |
| `Sample SPARQL Queries.txt` | `./Sample SPARQL Queries.txt` | Six worked SPARQL queries (`q0`–`q5`) demonstrating retrieval against the ontology: cat-model/peril inventory, events and peril factors, event losses by peril/region/country, portfolio AAL rollups, incurred-vs-modeled AAL comparison, and event-specific loss lookup. |
| `cat-ontology example knowledge graph.ttl` | `./LLM integration (chat with data)/cat-ontology example knowledge graph.ttl` | A populated **example knowledge graph** (instance data) conforming to the ontology — synthetic events, losses, portfolios, cat-model results, and reference dimensions (peril, region, LOB, year). Used as the queryable graph for the SPARQL examples and the LLM chat pipeline. |
| `Ontology aware prompting for SPARQL query generation.txt` | `./LLM integration (chat with data)/Ontology aware prompting for SPARQL query generation.txt` | The **ontology-aware prompt template** that turns a natural-language question into a SPARQL query. Embeds the class/property schema, the `cro:` namespace, controlled peril/region/LOB codes, and query-construction guidance; `{question}` is substituted at run time. |
| `chatWithGraph_OpenAI.py` | `./LLM integration (chat with data)/chatWithGraph_OpenAI.py` | "Chat with your graph" pipeline (NL → SPARQL → results), **OpenAI API** backend. Loads the example graph, builds the prompt, calls the LLM, extracts the SPARQL, runs it against the graph, and pretty-prints the result table. |
| `chatWithGraph_anthropic.py` | `./LLM integration (chat with data)/chatWithGraph_anthropic.py` | Same pipeline, **Anthropic API** backend (official `anthropic` SDK). Note: makes a billable API call against an Anthropic API key. |
| `chatWithGraph_claude.py` | `./LLM integration (chat with data)/chatWithGraph_claude.py` | Same pipeline, **Claude Code CLI** backend — shells out to the local `claude` command, so it uses an existing Claude Code subscription and needs no API key. |
| `Hurricane Claims Normalization Data.xlsx` | `./Hurricane Claims Normalization Data.xlsx` | Historical hurricane **claims normalization** dataset: 536 rows of claims by county across 18 named U.S. hurricanes (Frances 2004 → Dorian 2019). Columns include total claims, county identifiers, historical and current TIV, and the normalization factors (`alpha_c`, `beta`, `gamma`) used to restate historical claims onto a common current-exposure basis. |
| `ylt.csv` | `./Hurricane Loss Normalization with MCMC/ylt.csv` | A **100,000-year Year Loss Table (YLT)**: one row per simulated year with the annual-maximum event loss, normalized to 2025 dollars/exposure. Input to the empirical OEP curve, AAL, and Bayesian calibration in the notebook. |
| `hurricane_loss_analysis_forPaper.ipynb` | `./Hurricane Loss Normalization with MCMC/hurricane_loss_analysis_forPaper.ipynb` | Jupyter notebook reproducing the **loss-normalization and model-validation** analysis (personal lines, 2004–2024, normalized to 2025): event return periods from the empirical YLT OEP curve, empirical-vs-model AAL with bootstrap, likelihood of the observed history under the model, and **Bayesian/MCMC calibration** of the scaling factor κ (with KDE tail-fidelity checks). |

---

## Detailed contents

### 1. The ontology (schema)

- **`ontology.ttl`** is the source of truth: a Turtle serialization of the Catastrophe
  Risk Ontology. Open it with any RDF tool (Protégé, `rdflib`, GraphDB, Apache Jena).
- **`Catastrophe Risk Ontology - Classes, Properties.xlsx`** is the same content in a
  reviewer-friendly spreadsheet, split into a `class` sheet and a `property` sheet. Use
  it to browse the model without an RDF toolchain.

### 2. Example knowledge graph & queries

- **`cat-ontology example knowledge graph.ttl`** instantiates the ontology with a
  self-contained synthetic dataset (events, losses, portfolios, modeled results, and
  reference dimensions). It is large enough to exercise every relationship in the paper's
  examples but contains no proprietary data.
- **`Sample SPARQL Queries.txt`** contains ready-to-run queries against that graph. Load
  the graph and run any query, e.g. with `rdflib`:

  ```python
  from rdflib import Graph
  g = Graph()
  g.parse("LLM integration (chat with data)/cat-ontology example knowledge graph.ttl",
          format="turtle")
  for row in g.query(open("Sample SPARQL Queries.txt").read().split('q0 = """')[1].split('"""')[0]):
      print(row)
  ```

### 3. LLM integration — "chat with your graph"

The three `chatWithGraph_*.py` scripts implement the **same** natural-language-to-SPARQL
pipeline and differ only in the LLM backend. Each one:

1. loads the example knowledge graph,
2. injects your question into `Ontology aware prompting for SPARQL query generation.txt`,
3. asks the LLM to emit a SPARQL query,
4. executes that query on the graph, and
5. renders the results as a formatted table.

| Script | Backend | Requirements |
|--------|---------|--------------|
| `chatWithGraph_OpenAI.py` | OpenAI API | `openai` package + `OPENAI_API_KEY` |
| `chatWithGraph_anthropic.py` | Anthropic API | `anthropic` package + `ANTHROPIC_API_KEY` (billable) |
| `chatWithGraph_claude.py` | Claude Code CLI | local `claude` CLI on `PATH` (no API key) |

Run any of them from inside the `LLM integration (chat with data)/` directory (they read
the `.ttl` and prompt file by relative path):

```bash
cd "LLM integration (chat with data)"
python chatWithGraph_claude.py
```

Shared Python dependencies: `rdflib`, `pandas`, `tabulate` (plus the backend's SDK).

### 4. Hurricane claims normalization

**`Hurricane Claims Normalization Data.xlsx`** provides the county-level historical claim
counts and the normalization factors (`alpha_c`, `beta`, `gamma`) and TIV values used to
restate historical hurricane claims onto a common 2025 exposure basis — the empirical
foundation for the normalization method in the paper.

### 5. Hurricane loss normalization & model validation (MCMC)

- **`ylt.csv`** — the 100,000-year simulated Year Loss Table (annual maximum event loss),
  normalized to 2025 dollars.
- **`hurricane_loss_analysis_forPaper.ipynb`** — the analysis notebook. It computes
  empirical event return periods, compares empirical and modeled AAL with bootstrap
  uncertainty, quantifies how likely the observed 2004–2024 history is under the model,
  and runs a Bayesian/MCMC calibration of the scaling factor **κ** that reconciles the
  model distribution with the observed record (including KDE tail-fidelity validation).

  Requirements: Python 3, Jupyter, and `numpy`, `pandas`, `matplotlib`, `scipy`. The
  Metropolis-Hastings sampler is hand-rolled with NumPy — no PyMC or other MCMC package
  is needed. Run from inside the `Hurricane Loss Normalization with MCMC/` directory so
  `ylt.csv` is found by relative path.

---

## Suggested environment

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# LLM backend SDKs, only if you use those scripts:
pip install langchain-openai      # chatWithGraph_OpenAI.py
pip install anthropic             # chatWithGraph_anthropic.py
```

`requirements.txt` covers the ontology tools, the SPARQL/chat pipeline, and the
notebook. `chatWithGraph_claude.py` needs the local `claude` CLI on `PATH` and no
Python package.

---

## Repository contents at a glance

- `ontology.ttl`, `Catastrophe Risk Ontology - Classes, Properties.xlsx` — the schema
- `Sample SPARQL Queries.txt` — worked queries
- `LLM integration (chat with data)/` — example knowledge graph, prompt template, and the
  three `chatWithGraph_*.py` pipelines
- `Hurricane Claims Normalization Data.xlsx` — claims-normalization dataset
- `Hurricane Loss Normalization with MCMC/` — `ylt.csv` and the analysis notebook
- `file_manifest.csv`, `Data and Code Availability.docx` — the manifest in two formats
- `LICENSE` (CC BY 4.0), `CITATION.cff`, `requirements.txt`

---

*README last updated: 2026-09-05.*
