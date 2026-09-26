# SHACL Shapes for the Catastrophe Risk Ontology (CRO)

**Author:** Sashi Kanth Tadinada, PhD (NFP, Inc.)
**Status:** Design specification — documentation only. The shapes described here are *proposed*; the enforceable `cat-risk-shapes.ttl` graph is to be generated subsequently.
**Scope of this pass:** the incurred-loss and modeling-comparison core of the CRO — `EventClaim`, `EventLoss`, `EventPerilMap`, `ylpr`, `AAL`, and `EPCURVE`.

---

## 1. Purpose and Methodology

The Catastrophe Risk Ontology (CRO) provides the terminological (T-box) layer that unifies claims, exposure, and catastrophe-model data into a single knowledge graph. Terminology alone, however, does not guarantee that the *instance* data (A-box) is complete or internally consistent enough to answer the analyses the ontology was designed for. The Shapes Constraint Language (SHACL) supplies that missing layer: a set of validatable integrity constraints over the instance data.

Consistent with the competency-question-driven methodology adopted for the CRO (following Noy and McGuinness, 2001, and Grüninger and Fox, 1995), the shapes in this document are derived **from the competency questions (CQs), not from the class list**. Each shape is justified by the data it must guarantee so that a given CQ is answerable, and is annotated with the CQ(s) it serves. This ensures that validation effort is directed at the constraints that materially affect the ontology's information needs rather than at incidental structure.

The design observes four conventions drawn from established SHACL practice:

1. **Named node and property shapes** are used throughout; anonymous (blank-node) shapes are avoided so that every constraint is individually addressable and maintainable.
2. **Severity levels** distinguish hard invariants (`sh:Violation`) from softer expectations and cross-record advisories (`sh:Warning`). Loosening a constraint is backward-compatible; tightening is not, so the first pass favours the weaker severity where a rule is not yet certain.
3. The **shapes graph is maintained on a separate lifecycle** from the ontology graph, permitting the constraints to evolve independently of the vocabulary.
4. Each shape carries an `rdfs:comment` and a `skos:note` recording the competency question it addresses, preserving an audit trail from requirement to constraint.

---

## 2. Competency Questions

The shapes are motivated by the five competency questions that guided the CRO's design (paper, Table 1):

| ID | Competency Question |
|----|---------------------|
| **CQ1** | Compare Commercial Lines' Incurred Loss to modeled AAL (Average Annual Loss) between 2017 and 2023 for U.S. Windstorm. |
| **CQ2** | What is the observed loss return period in the 2021 Dixie Wildfire for U.S. Consumer lines? |
| **CQ3** | List peril-region(s) in 2022 incurred losses that correspond to more than a 100-year return period. |
| **CQ4** | Summarize non-modeled losses in 2020 by Peril, Loss Country, and Line of Business. |
| **CQ5** | Based on the consumer lines' historical losses, what would be the normalized loss in 2025 dollars for Hurricane Katrina? |

CQ2, CQ3, and CQ5 are answered by *analytical computation* — return-period estimation by interpolation against the modeled Exceedance-Probability (EP) curve, and loss normalization via county-level damage ratios and Total Insured Value (TIV) trending (paper, §4.3, Eqs. 2–3). They therefore require no additional ontology terms; the role of SHACL for these questions is to guarantee that the computational *inputs* — EP-curve points, and county-resolved claims and exposure — are present and well-formed.

---

## 3. Proposed Shapes

| Shape (named) | Target class | Serves | Key constraints | Severity |
|---------------|--------------|--------|-----------------|----------|
| `EventPerilMapShape` | `cro:EventPerilMap` | CQ1, CQ4 | exactly one `cro:hasEvent`, one `cro:hasPeril`, one `cro:hasFactorValue`; factor in `[0,1]` | Violation |
| `EventPerilFactorSumShape` | `cro:Event` | CQ1, CQ4 | Σ of `cro:hasFactorValue` over an event's `EventPerilMap` records = 1.0 (`sh:sparql`) | Warning |
| `YlprKeyShape` | `cro:ylpr` | CQ1, CQ3 | exactly one each of `hasYearAttribute`, `hasLOBAttribute`, `hasPerilAttribute`, `hasRegionAttribute` | Violation |
| `YlprUniqueShape` | `cro:ylpr` | CQ1, CQ3 | the {Year, LOB, Peril, Region} 4-tuple is unique across instances (`sh:sparql`) | Warning |
| `EventLossShape` | `cro:EventLoss` | CQ1, CQ4 | required (min 1): `eventLossOf`, `hasPeril`, `hasLOB`, `hasLossCountry`, `hasGrossIncurredLoss` (≥ 0), `isModeledLoss`; `perilContributionFactor` in `[0,1]` | Violation |
| `EventClaimShape` | `cro:EventClaim` | CQ1, CQ4, CQ5 | required: `hasClaimEvent`, `hasClaimLOB`, ≥ 1 loss location (`hasClaimLossCountry` or `hasClaimLossFeature`), `grossIncurred` (≥ 0); `IBNR` (≥ 0), `lastUpdated`, `completenessRatio` (≥ 1.0) | Violation / Warning |
| `AALShape` | `cro:AAL` | CQ1 | `meanvalue` exactly 1 (≥ 0); `sdvalue` ≥ 0 if present | Violation |
| `EPCurveShape` | `cro:EPCURVE` | CQ2, CQ3 | `returnperiod` exactly 1 (> 0); `ep_loss` exactly 1 (≥ 0) | Violation |

---

## 4. Shape Descriptions

**`EventPerilMapShape`** — Each `EventPerilMap` record decomposes an event's loss into a single peril contribution; the shape therefore requires exactly one linked event, one peril, and one factor value bounded to the unit interval. This underpins the like-to-like comparison of observed and modeled losses by ensuring that only modeled perils can be isolated (CQ1, CQ4).

**`EventPerilFactorSumShape`** — The paper stipulates that the peril-contribution factors "sum to unity across all records for a given event" (§3.2.2). This event-scoped constraint verifies that the decomposition is exhaustive and non-duplicative; it is expressed as a `sh:sparql` constraint at `sh:Warning` severity to accommodate rounding tolerance in reported factors.

**`YlprKeyShape`** — The aggregation vector `ylpr` acts as the composite key {Year, LOB, Peril, Region} that "make[s] each model analysis run unique" (§3.2.5). The shape enforces the presence of all four attributes, since a partially-specified vector cannot participate in the actual-versus-modeled join on which CQ1 and CQ3 depend.

**`YlprUniqueShape`** — Complementing the key-completeness rule, this constraint checks that no two `ylpr` instances share the same 4-tuple, preserving the composite key's uniqueness. It is issued as a `sh:Warning` because legitimate duplicates may arise transiently during data loading before de-duplication.

**`EventLossShape`** — `EventLoss` is the peril-attributed, aggregation-ready view of loss that both non-modeled-loss summarization (CQ4) and the AAL comparison (CQ1) consume. The shape requires the dimensions those questions group and filter on — peril, line of business, loss country, the loss amount, and the `isModeledLoss` flag — and bounds the peril-contribution factor to `[0,1]`.

**`EventClaimShape`** — `EventClaim` is the as-reported record from which `EventLoss` is derived and from which Hurricane-Katrina-style normalization draws county-level claims (CQ5). Following the paper's characterization of a claim by *Policy/LOB, Event, Date of loss, and Country of loss* (§3.2.2), the shape requires the event, the line of business, at least one loss location, and a non-negative `grossIncurred`; `IBNR`, `lastUpdated`, and `completenessRatio` are checked at `sh:Warning`. The `completenessRatio` is a loss-development factor — projected (ultimate) loss = incurred loss × completenessRatio — and is therefore constrained to be `≥ 1.0`. Validation against the case-study data (see §6), where the ratio ranges 1.0–4.5, confirmed that a naïve "fraction" reading bounded to `[0,1]` would be incorrect.

**`AALShape`** — The Average Annual Loss record must carry a mean value to be comparable against observed losses; the shape requires a single non-negative `meanvalue` and, where reported, a non-negative standard deviation, so that CQ1's AAL side is well-formed.

**`EPCurveShape`** — Return-period estimation for an observed loss (CQ2, CQ3) interpolates against the modeled EP curve. The shape guarantees that each `EPCURVE` point carries a strictly-positive return period and a non-negative loss value, ensuring the curve is usable for interpolation. The constraint applies transitively to the `OEP` and `AEP` subclasses.

---

## 5. Controlled Vocabularies (Illustrative — Not Enforced)

The case-study data uses fixed codes for peril, line of business, and loss region. These are documented here as candidate `sh:in` enumerations to illustrate how value-set validation *could* be expressed. **They are not enforced in the current pass**, since the value sets may be extended as the knowledge graph grows; they are recorded for future consideration at `sh:Warning` severity.

| Attribute | Property | Candidate value set |
|-----------|----------|---------------------|
| Peril code | `cro:perilCode` | `WW1` (windstorm), `OO1` (flood), `QQ1` (earthquake), `BB1` (wildfire) |
| Line of business | `cro:lobName` | `COMMERCIAL`, `CONSUMER` |
| Loss-region code | `cro:lossRegionCode` | `US`, `CB` (Caribbean), `EU` (Europe), `CA` (Canada) |

Illustrative Turtle (for reference only; not part of the active shapes graph):

```turtle
cro-sh:PerilCodeShape a sh:NodeShape ;
    sh:targetClass cro:LossPeril ;
    rdfs:comment "Illustrative controlled vocabulary for peril codes — not enforced." ;
    sh:property [
        sh:path cro:perilCode ;
        sh:in ( "WW1" "OO1" "QQ1" "BB1" ) ;
        sh:severity sh:Warning ;
    ] .
```

---

## 6. Validation Against the Case-Study Knowledge Graph

The shapes graph (`cat-risk-shapes.ttl`, generated by `cro_shapes.py`) was validated against the case-study knowledge graph using `pyshacl`. The initial run surfaced exactly the kind of assumption errors the methodology is designed to catch, all of which were corrected in the shapes rather than the data:

- **`completenessRatio`** was initially bounded to `[0,1]`. The data revealed a range of 1.0–4.5, and the domain semantics confirm it is a loss-development factor (ultimate = incurred × ratio), i.e. `≥ 1.0`. The constraint was corrected accordingly — an instance of the article's caution against tightening a constraint past its true domain rule.
- **`hasGrossIncurredLoss`** is serialized as `xsd:double` (the result of SPARQL arithmetic), not `xsd:float`; the datatype constraint was aligned.
- **`hasYearAttribute`** is `xsd:integer` (from the `YEAR()` function), not `xsd:int`; the datatype constraint was aligned.

After these corrections the knowledge graph **conforms** to all eight shapes with zero violations and zero warnings. This closes the loop required by the methodology: sample data is validated against the shapes before the constraints are declared stable.

## 7. Next Steps

1. Generate `cat-risk-shapes.ttl` from a dedicated builder (`cro_shapes.py`), on a lifecycle separate from the ontology.
2. Validate the case-study knowledge graph against the shapes and review the report before promoting any `sh:Warning` to `sh:Violation`.
3. Revisit the controlled vocabularies (§5) and the composite-key uniqueness rule once the instance data has been validated.

---

### References
- Noy, N. F., & McGuinness, D. L. (2001). *Ontology Development 101: A Guide to Creating Your First Ontology.*
- Grüninger, M., & Fox, M. S. (1995). *Methodology for the Design and Evaluation of Ontologies.*
- Tadinada, S. K. *Ontologies for Catastrophe Risk Management and Analytics* (CAS Publications, CASPub-2025-Var-0018.R2) — §3.2.2, §3.2.5, §4.3.
- W3C (2017). *Shapes Constraint Language (SHACL).*
