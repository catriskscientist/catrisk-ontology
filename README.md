# Catastrophe Risk Ontology (CRO)

Data and code companion to the paper:

> **Ontologies for Catastrophe Risk Management and Analytics**
> Sashi Kanth Tadinada, Ph.D. — *manuscript under review*

This repository bundles the **Catastrophe Risk Ontology (CRO)**, a populated example
knowledge graph, worked SPARQL queries, a natural-language "chat with your graph"
pipeline (NL → SPARQL via an LLM), and the hurricane **claims-normalization** and
**loss-normalization / model-validation** datasets and analysis used in the paper.
Everything needed to inspect the ontology, run the example queries, reproduce the
loss-normalization figures, and try the LLM query-generation workflow is included here.

---

## Overview

The **Catastrophe Risk Ontology (CRO)** is a formal knowledge representation designed to
**unify and contextualize catastrophe-related data** across perils, regions, lines of
business, and accident years within the (re)insurance sector. It addresses the challenges
posed by fragmented and siloed datasets — often stored in disparate formats and lacking
semantic alignment — that lead to valuable information being underutilized. CRO transforms
disparate data sources into **coherent, enterprise-wide data assets** that support advanced
catastrophe analytics, portfolio risk monitoring, and loss benchmarking.

## Why CRO? Addressing key challenges

Catastrophe risk management demands the integration of diverse datasets — claims, exposure,
and catastrophe modeling outputs. In practice this is non-trivial:

- **Data fragmentation and silos**: Claims and modeling data are siloed and embedded in
  enterprise data models, making them hard to collect, integrate, and reconcile across
  market geographies and regulatory regimes.
- **Semantic heterogeneity**: Without a well-defined taxonomy, terms in claims and modeling
  feeds carry differing meanings, obstructing unification and advanced analytics.
- **Nontrivial data comparison**: Comparing claims to catastrophe modeling results is
  complicated by evolving portfolios, inflation, and **Non-Modeled Risks (NMR)** — losses
  from hazards, subperils, regions, exposure, or coverage classes the models omit.
- **Integration with emerging technologies**: Structured domain knowledge is needed to
  ground generative-AI systems and reduce hallucinations in LLM outputs.

## Key features and capabilities

- **Enterprise-wide data integration**: Harmonizes claims, exposure, and catastrophe-model
  outputs into a consistent long-term dataset across years, lines of business, perils, and
  regions.
- **Enhanced knowledge management**: A **structured knowledge layer** supporting semantic
  interoperability across stakeholders (insurers, reinsurers, brokers, model vendors) and
  reducing reliance on intensive ETL.
- **Advanced catastrophe analytics**:
  - **Multi-dimensional loss analysis** — breakdowns by event, line of business, peril,
    region, paid losses, reserves, and loss components.
  - **Evaluation of Non-Modeled Risks (NMR)** — pattern identification and risk-load
    computation for losses not covered by models.
  - **Portfolio performance monitoring** — risk metrics tracked over time by peril,
    geography, and line of business.
  - **Model validation** — granular vulnerability analysis across building characteristics
    (construction, occupancy, floor area) and robust model evaluation.
  - **Normalizing historical losses** — adjusting past claims for changes in exposure, cost
    inflation, and other factors to enable meaningful comparison.
- **LLM integration and generative-AI applications**:
  - **Grounding generative AI** — validated domain expertise for LLMs, improving natural
    language querying and reducing hallucinations.
  - **Semantic search and natural-language querying** — free-text interaction with the
    knowledge base.
  - **Retrieval-Augmented Generation (RAG)** — "chat-with-data" applications that translate
    natural-language questions into SPARQL, execute them on the CRO knowledge graph, and
    summarize the results.
- **Flexibility and extensibility**: A dynamic schema allows rapid incorporation of new
  risks, perils, or regulatory requirements without major redesign.

## Core components of CRO

Formally, an ontology like CRO is a tuple **O = (C, R, P, I)**:

- **C (Concepts)** — fundamental categories of entities, e.g. `Disaster Event`, `Peril`,
  `Geographic Region`, `Catastrophe Model`, `Accident Year`, `Incurred Loss`,
  `Modeled Result`.
- **R (Relationships)** — links between concepts (a `Disaster Event` occurs in a `Region`;
  a `Claim` is associated with an `Exposure Asset`).
- **P (Properties)** — attributes and constraints on each concept (a `Disaster Event` has a
  unique ID, start date, and end date).
- **I (Instances)** — the real-world data points populating the framework, expressed as a
  knowledge graph.

CRO organizes the core concepts of catastrophe risk — `peril`, `region`, `event`, `hazard`,
`claim`, `policy`, `account`, `portfolio`, `catastrophe model`, and result metrics such as
`AAL` and `PML`. It builds on the **TIME** and **GeoSPARQL** vocabularies and includes
modules for **Region, Peril, Incurred Loss (Claims Data), Exposure Data, Catastrophe
Modeling**, and **Aggregation Vectors**.

## Ontology-driven knowledge management system

CRO is the conceptual layer for an ontology-driven knowledge management system (KMS) that
integrates and normalizes data from claims, model outputs, and metadata, maps it into a
unified knowledge graph, and provides user-interaction tools. It uses the **Semantic Web
Rule Language (SWRL)** for logical reasoning — automatic inference of new knowledge (e.g.
identifying Non-Modeled Risks) and continuous consistency monitoring — and **SPARQL** for
complex, inference-driven queries over the graph.

## Case study and demonstrations

A case study for a hypothetical property insurer, built on the example knowledge graph
(`LLM integration (chat with data)/cat-ontology example knowledge graph.ttl`), shows how
CRO-powered knowledge graphs can:

- **reconcile modeled and incurred losses**,
- **track patterns in non-modeled risks**,
- support **Retrieval-Augmented Generation (RAG)** systems for catastrophe-risk analytics,
- answer **competency questions** — comparing incurred loss to modeled Average Annual Loss
  (AAL) for specific perils and regions, determining observed loss return periods, and
  summarizing non-modeled losses.

The LLM integration translates natural-language questions into SPARQL queries, executes
them on the CRO knowledge graph, and summarizes the results.

## Accessing the ontology

- **Ontology (Turtle / TTL):** <https://w3id.org/catrisk/ontology/>
  (prefix `cro: https://w3id.org/catrisk/ontology#`)
- **Source, documentation, and examples:** <https://github.com/catriskscientist/catrisk-ontology>

The `ontology.ttl` file in this repository is the version accompanying the paper.

---

## File manifest

| File | Path | Description |
|------|------|-------------|
| `ontology.ttl` | `./ontology.ttl` | The **Catastrophe Risk Ontology (CRO)** in Turtle/RDF — the full class hierarchy, object and data properties, and axioms (namespace `cro:`). Authoritative machine-readable schema. Imports GeoSPARQL, OWL-Time, SKOS, and Dublin Core vocabularies. |
| `Catastrophe Risk Ontology - Classes, Properties.xlsx` | `./Catastrophe Risk Ontology - Classes, Properties.xlsx` | Human-readable companion to `ontology.ttl`. **`class`** sheet: 52 classes with labels and descriptions. **`property`** sheet: 125 object/data properties as *source → property → target*, with labels, descriptions, and OWL characteristics (functional, inverse-functional, symmetric, transitive, reflexive, cardinality bounds). |
| `Sample SPARQL Queries.txt` | `./Sample SPARQL Queries.txt` | Six worked SPARQL queries (`q0`–`q5`) against the example graph: cat-model/peril inventory, events and peril factors, event losses by peril/region/country, portfolio AAL rollups, incurred-vs-modeled AAL comparison, and event-specific loss lookup. |
| `cat-ontology example knowledge graph.ttl` | `./LLM integration (chat with data)/cat-ontology example knowledge graph.ttl` | A populated **example knowledge graph** (instance data) conforming to the ontology — synthetic events, losses, portfolios, cat-model results, and reference dimensions (peril, region, LOB, year). Query target for the SPARQL examples and the LLM chat pipeline. No proprietary data. |
| `Ontology aware prompting for SPARQL query generation.txt` | `./LLM integration (chat with data)/Ontology aware prompting for SPARQL query generation.txt` | The **ontology-aware prompt template** that turns a natural-language question into a SPARQL query. Embeds the class/property schema, the `cro:` namespace, controlled peril/region/LOB codes, and query-construction guidance; `{question}` is substituted at run time. |
| `chatWithGraph_OpenAI.py` | `./LLM integration (chat with data)/chatWithGraph_OpenAI.py` | "Chat with your graph" pipeline (NL → SPARQL → results), **OpenAI API** backend. Loads the example graph, builds the prompt, calls the LLM, extracts the SPARQL, runs it against the graph, and pretty-prints the result table. |
| `chatWithGraph_anthropic.py` | `./LLM integration (chat with data)/chatWithGraph_anthropic.py` | Same pipeline, **Anthropic API** backend (official `anthropic` SDK). Makes a billable API call against an Anthropic API key. |
| `chatWithGraph_claude.py` | `./LLM integration (chat with data)/chatWithGraph_claude.py` | Same pipeline, **Claude Code CLI** backend — shells out to the local `claude` command, so it uses an existing Claude Code subscription and needs no API key. |
| `Hurricane Claims Normalization Data.xlsx` | `./Hurricane Claims Normalization Data.xlsx` | Historical hurricane **claims-normalization** dataset: 536 rows of claims by county across 18 named U.S. hurricanes (Frances 2004 → Dorian 2019). Total claims, county identifiers, historical and current TIV, and the normalization factors (`alpha_c`, `beta`, `gamma`) used to restate historical claims onto a common current-exposure basis. |
| `ylt.csv` | `./Hurricane Loss Normalization with MCMC/ylt.csv` | A **100,000-year Year Loss Table (YLT)**: one row per simulated year with the annual-maximum event loss, normalized to 2025 dollars/exposure. Input to the empirical OEP curve, AAL, and Bayesian calibration in the notebook. |
| `hurricane_loss_analysis_forPaper.ipynb` | `./Hurricane Loss Normalization with MCMC/hurricane_loss_analysis_forPaper.ipynb` | Jupyter notebook reproducing the **loss-normalization and model-validation** analysis (personal lines, 2004–2024, normalized to 2025): event return periods from the empirical YLT OEP curve, empirical-vs-model AAL with bootstrap, likelihood of the observed history under the model, and **Bayesian/MCMC calibration** of the scaling factor κ (with KDE tail-fidelity checks). |

Supporting files: `file_manifest.csv` (this table as CSV), `requirements.txt`, `CITATION.cff`,
`LICENSE`.

---

## Detailed contents

### 1. The ontology (schema)

- **`ontology.ttl`** is the source of truth: a Turtle serialization of the Catastrophe Risk
  Ontology. Open it with any RDF tool (Protégé, `rdflib`, GraphDB, Apache Jena).
- **`Catastrophe Risk Ontology - Classes, Properties.xlsx`** is the same content in a
  reviewer-friendly spreadsheet, split into a `class` sheet and a `property` sheet — browse
  the model without an RDF toolchain.

### 2. Example knowledge graph & queries

- **`cat-ontology example knowledge graph.ttl`** instantiates the ontology with a
  self-contained synthetic dataset (events, losses, portfolios, modeled results, and
  reference dimensions). It exercises every relationship used in the paper's examples and
  contains no proprietary data.
- **`Sample SPARQL Queries.txt`** contains ready-to-run queries against that graph, e.g.
  with `rdflib`:

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
| `chatWithGraph_OpenAI.py` | OpenAI API | `langchain-openai` + `OPENAI_API_KEY` |
| `chatWithGraph_anthropic.py` | Anthropic API | `anthropic` + `ANTHROPIC_API_KEY` (billable) |
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
  uncertainty, quantifies how likely the observed 2004–2024 history is under the model, and
  runs a Bayesian/MCMC calibration of the scaling factor **κ** that reconciles the model
  distribution with the observed record (including KDE tail-fidelity validation).

  Requirements: Python 3, Jupyter, and `numpy`, `pandas`, `matplotlib`, `scipy`. The
  Metropolis-Hastings sampler is hand-rolled with NumPy — no PyMC or other MCMC package is
  needed. Run from inside the `Hurricane Loss Normalization with MCMC/` directory so
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

`requirements.txt` covers the ontology tools, the SPARQL/chat pipeline, and the notebook.
`chatWithGraph_claude.py` needs the local `claude` CLI on `PATH` and no Python package.

---

## How to cite

The paper is under review; the final citation and DOI will be added on publication. In the
meantime:

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

See `CITATION.cff` for the machine-readable version.

## License

Released under **[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**
(full text in `LICENSE`). You are free to share and adapt the material for any purpose,
including commercially, provided you give appropriate credit to the paper above. No
proprietary or personally identifiable data are included; the example knowledge graph and
the Year Loss Table are synthetic.

---

*README last updated: 2026-09-05.*
