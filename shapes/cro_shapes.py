# -*- coding: utf-8 -*-
"""
Builder for the Catastrophe Risk Ontology (CRO) SHACL shapes graph.

Produces `cat-risk-shapes.ttl` on a lifecycle SEPARATE from the ontology.
Every constraint is a NAMED node/property shape (no anonymous shape nodes),
each annotated with the competency question(s) it serves and an explicit
sh:severity. See cro_shapes.md for the design rationale.

@author: Sashi Kanth Tadinada, PhD
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
from rdflib.namespace import XSD, OWL
from rdflib.collection import Collection

SH = Namespace("http://www.w3.org/ns/shacl#")
CRO = Namespace("https://w3id.org/catrisk/ontology#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
SDO = Namespace("https://schema.org/")
SHP = Namespace("https://w3id.org/catrisk/shapes#")

g = Graph()
g.bind("sh", SH)
g.bind("cro", CRO)
g.bind("crosh", SHP)
g.bind("skos", SKOS)
g.bind("dcterms", DCTERMS)
g.bind("sdo", SDO)
g.bind("owl", OWL)
g.bind("xsd", XSD)

shapes_iri = URIRef("https://w3id.org/catrisk/shapes")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def node_shape(name, target_classes, cq, comment):
    """Create a named sh:NodeShape targeting one or more classes."""
    s = SHP[name]
    g.add((s, RDF.type, SH.NodeShape))
    for tc in (target_classes if isinstance(target_classes, (list, tuple)) else [target_classes]):
        g.add((s, SH.targetClass, tc))
    g.add((s, RDFS.comment, Literal(comment)))
    g.add((s, SKOS.note, Literal(f"Serves competency question(s): {cq}.")))
    return s


def prop(nodeshape, name, path, *, mn=None, mx=None, datatype=None, node_class=None,
         min_incl=None, max_incl=None, min_excl=None, severity="Violation",
         message=None, cq=None):
    """Create a NAMED sh:PropertyShape and attach it to `nodeshape` via sh:property."""
    p = SHP[name]
    g.add((p, RDF.type, SH.PropertyShape))
    g.add((p, SH.path, path))
    if mn is not None:
        g.add((p, SH.minCount, Literal(mn)))
    if mx is not None:
        g.add((p, SH.maxCount, Literal(mx)))
    if datatype is not None:
        g.add((p, SH.datatype, datatype))
    if node_class is not None:
        g.add((p, SH["class"], node_class))
    if min_incl is not None:
        g.add((p, SH.minInclusive, Literal(min_incl)))
    if max_incl is not None:
        g.add((p, SH.maxInclusive, Literal(max_incl)))
    if min_excl is not None:
        g.add((p, SH.minExclusive, Literal(min_excl)))
    g.add((p, SH.severity, SH[severity]))
    if message:
        g.add((p, SH.message, Literal(message)))
    if cq:
        g.add((p, SKOS.note, Literal(f"Serves competency question(s): {cq}.")))
    g.add((nodeshape, SH.property, p))
    return p


def sparql_constraint(nodeshape, name, select, message, severity="Warning"):
    """Attach a NAMED sh:SPARQLConstraint to a node shape."""
    c = SHP[name]
    g.add((c, RDF.type, SH.SPARQLConstraint))
    g.add((c, SH.message, Literal(message)))
    g.add((c, SH.severity, SH[severity]))
    g.add((c, SH.select, Literal(select)))
    g.add((nodeshape, SH.sparql, c))
    return c


# ------------------------------------------------------------------
# Shapes-graph header (separate lifecycle from the ontology)
# ------------------------------------------------------------------
g.add((shapes_iri, RDF.type, OWL.Ontology))
g.add((shapes_iri, RDFS.label, Literal("Catastrophe Risk Ontology - SHACL Shapes")))
g.add((shapes_iri, RDFS.comment, Literal(
    "Validation shapes for the Catastrophe Risk Ontology (CRO), derived from the "
    "ontology's competency questions. Maintained on a lifecycle separate from the ontology."
)))
_creator = URIRef("https://w3id.org/catrisk/shapes#author")
g.add((shapes_iri, DCTERMS.creator, _creator))
g.add((_creator, RDF.type, SDO.Person))
g.add((_creator, SDO.name, Literal("Sashi Kanth Tadinada, PhD")))
g.add((_creator, SDO.affiliation, Literal("NFP, Inc.")))
g.add((shapes_iri, DCTERMS.created, Literal("2026-09-26", datatype=XSD.date)))
g.add((shapes_iri, DCTERMS.source, URIRef("https://w3id.org/catrisk/ontology")))
g.add((shapes_iri, OWL.versionIRI, URIRef("https://w3id.org/catrisk/shapes/1.0.0")))

# ------------------------------------------------------------------
# 1. EventPerilMapShape  (CQ1, CQ4)
# ------------------------------------------------------------------
s = node_shape("EventPerilMapShape", CRO.EventPerilMap, "CQ1, CQ4",
               "An EventPerilMap decomposes one event's loss into a single peril contribution.")
prop(s, "EventPerilMap_hasEvent", CRO.hasEvent, mn=1, mx=1, node_class=CRO.Event,
     message="EventPerilMap must link to exactly one Event via hasEvent.", cq="CQ1, CQ4")
prop(s, "EventPerilMap_hasPeril", CRO.hasPeril, mn=1, mx=1,
     message="EventPerilMap must link to exactly one Peril via hasPeril.", cq="CQ1, CQ4")
prop(s, "EventPerilMap_hasFactorValue", CRO.hasFactorValue, mn=1, mx=1, datatype=XSD.float,
     min_incl=0.0, max_incl=1.0,
     message="hasFactorValue must be present and within [0,1].", cq="CQ1, CQ4")

# ------------------------------------------------------------------
# 2. EventPerilFactorSumShape  (CQ1, CQ4) - factors sum to unity per event
# ------------------------------------------------------------------
s = node_shape("EventPerilFactorSumShape", CRO.Event, "CQ1, CQ4",
               "The peril-contribution factors of an event's EventPerilMap records must sum to 1.0 (paper, section 3.2.2).")
sparql_constraint(
    s, "EventPerilFactorSum_Constraint",
    """SELECT $this (SUM(?f) AS ?total)
WHERE {
  $this <https://w3id.org/catrisk/ontology#hasEventPerilMap> ?m .
  ?m <https://w3id.org/catrisk/ontology#hasFactorValue> ?f .
}
GROUP BY $this
HAVING (ABS(SUM(?f) - 1.0) > 0.01)""",
    "The EventPerilMap factors for this Event do not sum to 1.0 (tolerance 0.01).",
    severity="Warning",
)

# ------------------------------------------------------------------
# 3. YlprKeyShape  (CQ1, CQ3) - composite key completeness
# ------------------------------------------------------------------
s = node_shape("YlprKeyShape", CRO.ylpr, "CQ1, CQ3",
               "ylpr is the composite key {Year, LOB, Peril, Region}; all four attributes must be present (paper, section 3.2.5).")
prop(s, "Ylpr_hasYearAttribute", CRO.hasYearAttribute, mn=1, mx=1, datatype=XSD.integer,
     message="ylpr must have exactly one hasYearAttribute.", cq="CQ1, CQ3")
prop(s, "Ylpr_hasLOBAttribute", CRO.hasLOBAttribute, mn=1, mx=1, node_class=CRO.LOB,
     message="ylpr must have exactly one hasLOBAttribute.", cq="CQ1, CQ3")
prop(s, "Ylpr_hasPerilAttribute", CRO.hasPerilAttribute, mn=1, mx=1,
     message="ylpr must have exactly one hasPerilAttribute.", cq="CQ1, CQ3")
prop(s, "Ylpr_hasRegionAttribute", CRO.hasRegionAttribute, mn=1, mx=1,
     message="ylpr must have exactly one hasRegionAttribute.", cq="CQ1, CQ3")

# ------------------------------------------------------------------
# 4. YlprUniqueShape  (CQ1, CQ3) - composite key uniqueness
# ------------------------------------------------------------------
s = node_shape("YlprUniqueShape", CRO.ylpr, "CQ1, CQ3",
               "The {Year, LOB, Peril, Region} 4-tuple should be unique across ylpr instances.")
sparql_constraint(
    s, "YlprUnique_Constraint",
    """SELECT $this ?other
WHERE {
  $this <https://w3id.org/catrisk/ontology#hasYearAttribute> ?y ;
        <https://w3id.org/catrisk/ontology#hasLOBAttribute> ?l ;
        <https://w3id.org/catrisk/ontology#hasPerilAttribute> ?p ;
        <https://w3id.org/catrisk/ontology#hasRegionAttribute> ?r .
  ?other a <https://w3id.org/catrisk/ontology#ylpr> ;
        <https://w3id.org/catrisk/ontology#hasYearAttribute> ?y ;
        <https://w3id.org/catrisk/ontology#hasLOBAttribute> ?l ;
        <https://w3id.org/catrisk/ontology#hasPerilAttribute> ?p ;
        <https://w3id.org/catrisk/ontology#hasRegionAttribute> ?r .
  FILTER (?other != $this)
}""",
    "Another ylpr shares this {Year, LOB, Peril, Region} composite key.",
    severity="Warning",
)

# ------------------------------------------------------------------
# 5. EventLossShape  (CQ1, CQ4)
# ------------------------------------------------------------------
s = node_shape("EventLossShape", CRO.EventLoss, "CQ1, CQ4",
               "EventLoss is the peril-attributed, aggregation-ready loss consumed by AAL comparison and non-modeled-loss summaries.")
prop(s, "EventLoss_eventLossOf", CRO.eventLossOf, mn=1, mx=1, node_class=CRO.Event,
     message="EventLoss must link to exactly one Event via eventLossOf.", cq="CQ1, CQ4")
prop(s, "EventLoss_hasPeril", CRO.hasPeril, mn=1, mx=1,
     message="EventLoss must have exactly one hasPeril.", cq="CQ1, CQ4")
prop(s, "EventLoss_hasLOB", CRO.hasLOB, mn=1, mx=1, node_class=CRO.LOB,
     message="EventLoss must have exactly one hasLOB.", cq="CQ1, CQ4")
prop(s, "EventLoss_hasLossCountry", CRO.hasLossCountry, mn=1, mx=1, node_class=CRO.Country,
     message="EventLoss must have exactly one hasLossCountry.", cq="CQ1, CQ4")
prop(s, "EventLoss_hasGrossIncurredLoss", CRO.hasGrossIncurredLoss, mn=1, mx=1,
     datatype=XSD.double, min_incl=0.0,
     message="EventLoss must have a non-negative hasGrossIncurredLoss.", cq="CQ1, CQ4")
prop(s, "EventLoss_isModeledLoss", CRO.isModeledLoss, mn=1, mx=1, datatype=XSD.boolean,
     message="EventLoss must state isModeledLoss (true/false).", cq="CQ4")
prop(s, "EventLoss_perilContributionFactor", CRO.perilContributionFactor, mn=1, mx=1,
     datatype=XSD.float, min_incl=0.0, max_incl=1.0,
     message="perilContributionFactor must be present and within [0,1].", cq="CQ1, CQ4")

# ------------------------------------------------------------------
# 6. EventClaimShape  (CQ1, CQ4, CQ5)
# ------------------------------------------------------------------
s = node_shape("EventClaimShape", CRO.EventClaim, "CQ1, CQ4, CQ5",
               "EventClaim is the as-reported record; a claim is described by Event, LOB, a loss location, and reported financials (paper, section 3.2.2).")
prop(s, "EventClaim_hasClaimEvent", CRO.hasClaimEvent, mn=1, mx=1, node_class=CRO.Event,
     message="EventClaim must link to exactly one Event via hasClaimEvent.", cq="CQ1, CQ4, CQ5")
prop(s, "EventClaim_hasClaimLOB", CRO.hasClaimLOB, mn=1, mx=1, node_class=CRO.LOB,
     message="EventClaim must have exactly one hasClaimLOB.", cq="CQ1, CQ4")
prop(s, "EventClaim_grossIncurred", CRO.grossIncurred, mn=1, mx=1, datatype=XSD.float,
     min_incl=0.0, message="EventClaim must have a non-negative grossIncurred.", cq="CQ1, CQ4")
# at least one loss location: hasClaimLossCountry OR hasClaimLossFeature (named sub-shapes)
_loc_country = SHP["EventClaim_lossLocationCountry"]
g.add((_loc_country, RDF.type, SH.PropertyShape))
g.add((_loc_country, SH.path, CRO.hasClaimLossCountry))
g.add((_loc_country, SH.minCount, Literal(1)))
_loc_feature = SHP["EventClaim_lossLocationFeature"]
g.add((_loc_feature, RDF.type, SH.PropertyShape))
g.add((_loc_feature, SH.path, CRO.hasClaimLossFeature))
g.add((_loc_feature, SH.minCount, Literal(1)))
_or_list = SHP["EventClaim_lossLocationList"]
Collection(g, _or_list, [_loc_country, _loc_feature])
g.add((s, SH["or"], _or_list))
g.add((s, SH.message, Literal("EventClaim must have at least one loss location (hasClaimLossCountry or hasClaimLossFeature).")))
# softer expectations -> Warning
prop(s, "EventClaim_IBNR", CRO.IBNR, mx=1, datatype=XSD.float, min_incl=0.0,
     severity="Warning", message="IBNR, if present, must be non-negative.", cq="CQ1")
prop(s, "EventClaim_completenessRatio", CRO.completenessRatio, mx=1, datatype=XSD.float,
     min_incl=1.0, severity="Warning",
     message="completenessRatio must be >= 1.0 (a loss-development factor: projected loss = incurred loss x completenessRatio).", cq="CQ5")
prop(s, "EventClaim_lastUpdated", CRO.lastUpdated, mx=1, datatype=XSD.date,
     severity="Warning", message="lastUpdated, if present, must be an xsd:date.", cq="CQ5")

# ------------------------------------------------------------------
# 7. AALShape  (CQ1)  - includes AAL subclasses
# ------------------------------------------------------------------
s = node_shape("AALShape",
               [CRO.AAL, CRO.PortfolioAAL, CRO.AccountAAL, CRO.LocationAAL], "CQ1",
               "An AAL record must carry a mean value to be comparable against observed losses.")
prop(s, "AAL_meanvalue", CRO.meanvalue, mn=1, mx=1, datatype=XSD.float, min_incl=0.0,
     message="AAL must have a non-negative meanvalue.", cq="CQ1")
prop(s, "AAL_sdvalue", CRO.sdvalue, mx=1, datatype=XSD.float, min_incl=0.0,
     severity="Warning", message="sdvalue, if present, must be non-negative.", cq="CQ1")

# ------------------------------------------------------------------
# 8. EPCurveShape  (CQ2, CQ3)  - includes OEP/AEP subclasses
# ------------------------------------------------------------------
s = node_shape("EPCurveShape", [CRO.EPCURVE, CRO.OEP, CRO.AEP], "CQ2, CQ3",
               "Each EP-curve point must be usable for return-period interpolation.")
prop(s, "EPCurve_returnperiod", CRO.returnperiod, mn=1, mx=1, datatype=XSD.float,
     min_excl=0.0, message="EP-curve point must have a positive returnperiod.", cq="CQ2, CQ3")
prop(s, "EPCurve_ep_loss", CRO.ep_loss, mn=1, mx=1, datatype=XSD.float, min_incl=0.0,
     message="EP-curve point must have a non-negative ep_loss.", cq="CQ2, CQ3")

# ------------------------------------------------------------------
g.serialize(destination="cat-risk-shapes.ttl", format="turtle")
print(f"Wrote cat-risk-shapes.ttl ({len(g)} triples).")
