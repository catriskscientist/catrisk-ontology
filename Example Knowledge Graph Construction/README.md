# Example Knowledge Graph Construction

Scripts and inputs that build the example catastrophe-risk knowledge graph used in
the paper. The pipeline has two stages:

1. **Schema** — `cro_schema.py` assembles the Catastrophe Risk Ontology (CRO): it
   loads the W3C OWL-Time and OGC GeoSPARQL vocabularies, declares the CRO classes
   and object/data properties, applies labels, comments, and OWL characteristics
   from `ontology_definitions.xlsx`, and serialises the result to `cro_schema.ttl`.
2. **Instances** — `build_knowledge_graph.py` imports that schema graph, loads the
   instance data from `knowledge_graph_data.xlsx` (countries, regions, perils,
   events, event/peril factors, claims, portfolios, cat models, portfolio AAL and
   EP curves), then runs a series of SPARQL `INSERT` updates to derive `EventLoss`,
   `YLPR` (year / LOB / peril / region) and modeled-loss-status triples. The
   populated graph is written to `example_knowledge_graph.ttl`.

## Files

| File | Role |
|------|------|
| `cro_schema.py` | Builds the CRO schema graph; imported by `build_knowledge_graph.py`. |
| `build_knowledge_graph.py` | Populates the schema with instance data and derived triples; produces the example knowledge graph. |
| `utils.py` | Date-parsing helper used by the build. |
| `ontology_definitions.xlsx` | `class` and `property` sheets: labels, comments, and OWL characteristics (functional / inverse-functional) applied to the schema. |
| `knowledge_graph_data.xlsx` | Instance data — one sheet per entity type (`country`, `areas`, `peril`, `selected events`, `epfactors`, `event_losses`, `portfolios`, `availablemodels`, `portfolio_AAL`, `epcurves`, `catmodeldomains`, `lobs`). |
| `time.ttl` | W3C OWL-Time vocabulary (dependency, parsed as-is). |
| `geo.ttl` | OGC GeoSPARQL vocabulary (dependency, parsed as-is). |
| `cro_schema.ttl` | Generated CRO schema (output of stage 1, included for reference). |
| `example_knowledge_graph.ttl` | Generated example knowledge graph (output of stage 2). |

## Run

```bash
pip install -r requirements.txt

# from inside this directory (paths are relative)
python build_knowledge_graph.py
```

`build_knowledge_graph.py` imports `cro_schema.py`, so a single run rebuilds both
`cro_schema.ttl` and `example_knowledge_graph.ttl`. It also writes
`ontology_summary.xlsx` — a class/property listing queried back out of the built
graph (regenerated each run; not tracked here).

The ontology namespace is `cro: https://w3id.org/catrisk/ontology#`.
