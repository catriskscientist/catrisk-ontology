# -*- coding: utf-8 -*-
"""
cro_schema.py -- build the Catastrophe Risk Ontology (CRO) schema graph.

Loads the W3C OWL-Time (time.ttl) and OGC GeoSPARQL (geo.ttl) vocabularies,
declares the CRO classes and object/data properties, applies the labels,
comments, and OWL characteristics from ontology_definitions.xlsx, and writes the
result to cro_schema.ttl.

Imported by build_knowledge_graph.py, which reuses the populated ``g`` graph and
the class/property names defined here.

@author: Sashi Kanth Tadinada, PhD
"""

import pandas as pd
import numpy as np
from rdflib import Graph, Literal, Namespace, RDF, URIRef, BNode
from rdflib.namespace import RDFS, XSD, RDF, OWL
import networkx as nx

# Load the existing GeoSPARQL ontology into the graph
g = Graph()

ontology_iri = URIRef("https://w3id.org/catrisk/ontology")
version_iri = URIRef("https://w3id.org/catrisk/ontology/1.0.0")

CRO = Namespace("https://w3id.org/catrisk/ontology#")
g.bind("cro",CRO)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", Namespace("http://www.w3.org/2001/XMLSchema#"))

# Namespaces used for authorship / attribution metadata
DCTERMS = Namespace("http://purl.org/dc/terms/")
SDO = Namespace("https://schema.org/")
VANN = Namespace("http://purl.org/vocab/vann/")
g.bind("dcterms", DCTERMS)
g.bind("sdo", SDO)
g.bind("vann", VANN)


# Define the ontology declaration
g.add((ontology_iri, RDF.type, OWL.Ontology))
g.add((ontology_iri, RDFS.label, Literal("Catastrophe Risk Ontology")))
g.add((ontology_iri, RDFS.comment, Literal(
    "An ontology to describe key concepts and relationships in catastrophe property insurance modeling, including exposure, events, losses, perils, and portfolios."
)))
g.add((ontology_iri, OWL.versionIRI, version_iri))

# --- Authorship / attribution ---
creator = BNode()
g.add((creator, RDF.type, SDO.Person))
g.add((creator, SDO.name, Literal("Sashi Kanth Tadinada, PhD")))
g.add((creator, SDO.affiliation, Literal("NFP, Inc.")))
g.add((creator, SDO.email, Literal("tadinadasashi@gmail.com", datatype=XSD.string)))
g.add((ontology_iri, DCTERMS.creator, creator))
g.add((ontology_iri, DCTERMS.created, Literal("2026-09-03", datatype=XSD.date)))
g.add((ontology_iri, VANN.author, Literal("Sashi Kanth Tadinada", datatype=XSD.string)))
g.add((ontology_iri, VANN.preferredNamespacePrefix, Literal("cro", datatype=XSD.string)))
g.add((ontology_iri, VANN.preferredNamespaceUri, Literal("https://w3id.org/catrisk/ontology#", datatype=XSD.anyURI)))

# Define the new class AdminBoundary as a subclass of geo:Feature
AdminBoundary = URIRef(CRO.AdminBoundary)
# Define the new class AdminBoundary as a subclass of geo:Feature
Grid = URIRef(CRO.Grid)

g.parse("time.ttl", format="turtle")
g.parse("geo.ttl", format="turtle")

# Define the GEO namespace
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
g.bind("geo", GEO)

TIME = Namespace("http://www.w3.org/2006/time#")
g.bind("time",TIME)

Feature = GEO.Feature
FeatureCollection = GEO.FeatureCollection
GeometryCollection = GEO.GeometryCollection

hasGeometry = GEO.hasGeometry

# Add the AdminBoundary class to the graph
g.add((AdminBoundary, RDF.type, RDFS.Class))
g.add((AdminBoundary, RDFS.subClassOf, Feature))

# Add the AdminBoundary class to the graph
g.add((Grid, RDF.type, RDFS.Class))
g.add((Grid, RDFS.subClassOf, Feature))

# Define the data property "level"
level = URIRef(CRO.adminBoundarylevel)

g.add((level, RDF.type, RDF.Property))
g.add((level, RDFS.domain, AdminBoundary))
g.add((level, RDFS.range, XSD.integer))
g.add((level, RDFS.label, Literal("Level property for administrative boundaries")))

# Define the containment property "contains"
contains = URIRef(CRO.adminBoundaryContains)
g.add((contains, RDF.type, RDF.Property))
g.add((contains, RDFS.domain, AdminBoundary))
g.add((contains, RDFS.range, AdminBoundary))
g.add((contains, RDFS.label, Literal("Represents the containment relationship between administrative boundaries")))

Region = URIRef(CRO.Region)

# Add the Region class to the graph
g.add((Region, RDF.type, RDFS.Class))
g.add((Region, RDFS.subClassOf, FeatureCollection))


# Classes
Country = URIRef(CRO.Country)
AreaCode = URIRef(CRO.AreaCode)
County = URIRef(CRO.County)
ZipCode = URIRef(CRO.ZipCode)

LossRegion = URIRef(CRO.LossRegion)
CatModelDomainRegion = URIRef(CRO.CatModelDomainRegion)

# Define class hierarchy
g.add((Country, RDFS.subClassOf, AdminBoundary))
g.add((AreaCode, RDFS.subClassOf, AdminBoundary))
g.add((County, RDFS.subClassOf, AdminBoundary))
g.add((ZipCode, RDFS.subClassOf, AdminBoundary))

g.add((LossRegion, RDFS.subClassOf, Region))
g.add((CatModelDomainRegion, RDFS.subClassOf, Region))

# Property to link affected areas to their subregions (either Country or AreaCode)
containsAdminBoundary = URIRef(CRO.hasAdminBoundary)
isPartOf = URIRef(CRO.isPartOf)

g.add((containsAdminBoundary, RDF.type, RDF.Property))
g.add((containsAdminBoundary, RDFS.domain, LossRegion))
g.add((containsAdminBoundary, RDFS.range, Country))

g.add((containsAdminBoundary, RDF.type, RDF.Property))
g.add((containsAdminBoundary, RDFS.domain, CatModelDomainRegion))
g.add((containsAdminBoundary, RDFS.range, Country))

inCatDomainOf = URIRef(CRO.inCatDomainOf)

g.add((inCatDomainOf, RDF.type, RDF.Property))
g.add((inCatDomainOf, RDFS.domain, Country))
g.add((inCatDomainOf, RDFS.range, CatModelDomainRegion))

g.add((isPartOf, RDF.type, RDF.Property))
g.add((isPartOf, RDFS.domain,Country))
g.add((isPartOf, RDFS.range, LossRegion))

relatedLossRegion = URIRef(CRO.relatedLossRegion)

g.add((relatedLossRegion, RDF.type, RDF.Property))
g.add((relatedLossRegion, RDFS.domain, CatModelDomainRegion))
g.add((relatedLossRegion, RDFS.range, LossRegion))

#------------------------------------------------------------
# -------------- PERIL ----------------------------

# Classes
Peril = URIRef(CRO.Peril)
LossPeril = URIRef(CRO.LossPeril)
PerilGroup = URIRef(CRO.PerilGroup)
PerilChain = URIRef(CRO.PerilChain)

# Define class hierarchy
g.add((PerilGroup, RDFS.subClassOf, Peril))
g.add((LossPeril, RDFS.subClassOf, Peril))
g.add((PerilChain, RDFS.subClassOf, Peril))

hasMember = URIRef(CRO.hasMember)
hasSubPeril = URIRef(CRO.hasSubPeril)
hasNextPeril = URIRef(CRO.hasNextPeril)
hasPreviousPeril = URIRef(CRO.hasPreviousPeril)

g.add((hasMember, RDF.type, RDF.Property))

g.add((hasNextPeril, RDF.type, RDF.Property))
g.add((hasPreviousPeril, RDF.type, RDF.Property))

g.add((hasMember, RDFS.domain, PerilChain))
g.add((hasMember, RDFS.range, LossPeril))

g.add((hasNextPeril, RDFS.domain, LossPeril))
g.add((hasNextPeril, RDFS.range, LossPeril))

g.add((hasPreviousPeril, RDFS.domain, LossPeril))
g.add((hasPreviousPeril, RDFS.range, LossPeril))

g.add((hasSubPeril, RDFS.domain, LossPeril))
g.add((hasSubPeril, RDFS.range, LossPeril))



# Event ---------------------------------------

# Define the Event class    
Event = URIRef(CRO.Event)
g.add((Event, RDF.type, RDFS.Class))

OccurenceTime = URIRef(CRO.occurenceTime)

g.add((OccurenceTime, RDF.type, RDF.Property))
g.add((OccurenceTime, RDFS.domain, Event))
g.add((OccurenceTime, RDFS.range, TIME.Interval))

# Define the EventPerilMap class (intermediary class)
EventPerilMap = URIRef(CRO.EventPerilMap)
g.add((EventPerilMap, RDF.type, RDFS.Class))

# Define properties for EventPerilMap
hasEvent = URIRef(CRO.hasEvent)
hasPeril = URIRef(CRO.hasPeril)
hasFactorValue = URIRef(CRO.hasFactorValue)

g.add((hasEvent, RDF.type, RDF.Property))
g.add((hasEvent, RDFS.domain, EventPerilMap))
g.add((hasEvent, RDFS.range, Event))

g.add((hasPeril, RDF.type, RDF.Property))
g.add((hasPeril, RDFS.domain, EventPerilMap))
g.add((hasPeril, RDFS.range, Peril))

g.add((hasFactorValue, RDF.type, RDF.Property))
g.add((hasFactorValue, RDFS.domain, EventPerilMap))
g.add((hasFactorValue, RDFS.range, XSD.float))

hasEventPerilMap = URIRef(CRO.hasEventPerilMap)
g.add((hasEventPerilMap, RDF.type, RDF.Property))
g.add((hasEventPerilMap, RDFS.domain, Event))
g.add((hasEventPerilMap, RDFS.range, EventPerilMap))

## ------------------------------------------
### CLAIM RECORD AND LOB
# Define the namespaces

# Add EVENTCLAIM and LOB classes
EventClaim = URIRef(CRO.EventClaim)
PolicyClaim = URIRef(CRO.PolicyClaim)
LOBClass = URIRef(CRO.LOB)

g.add((PolicyClaim, RDF.type, RDFS.Class))
g.add((EventClaim, RDF.type, RDFS.Class))
g.add((LOBClass, RDF.type, RDFS.Class))

# Define relationships
claimPartOf = URIRef(CRO.claimPartOf)
g.add((claimPartOf, RDF.type, RDF.Property))
g.add((claimPartOf, RDFS.domain, PolicyClaim))
g.add((claimPartOf, RDFS.range, EventClaim))

# EVENTCLAIM connected to LOB via hasLOB
hasClaimLOB = URIRef(CRO.hasClaimLOB)
g.add((hasClaimLOB, RDF.type, RDF.Property))
g.add((hasClaimLOB, RDFS.domain, EventClaim))
g.add((hasClaimLOB, RDFS.range, LOBClass))

# EVENTCLAIM connected to EventPerilMap (EPR) via hasEPR
hasClaimEvent = URIRef(CRO.hasClaimEvent)
g.add((hasClaimEvent, RDF.type, RDF.Property))
g.add((hasClaimEvent, RDFS.domain, EventClaim))
g.add((hasClaimEvent, RDFS.range, Event))

# EVENTCLAIM connected to EventPerilMap (EPR) via hasEPR
# Claim-loss location hierarchy. hasClaimLossFeature (EventClaim -> AdminBoundary)
# is the umbrella; the level-specific children below are its sub-properties, so a
# query on hasClaimLossFeature catches country/county/ZIP claim locations.
# Labels/comments set explicitly for the new ones (not in ontology_definitions.xlsx);
# hasClaimLossCountry keeps its label/comment from the Excel property sheet.
hasClaimLossFeature = URIRef(CRO.hasClaimLossFeature)
g.add((hasClaimLossFeature, RDF.type, RDF.Property))
g.add((hasClaimLossFeature, RDFS.domain, EventClaim))
g.add((hasClaimLossFeature, RDFS.range, AdminBoundary))
g.add((hasClaimLossFeature, RDFS.label, Literal("Has Claim Loss Feature")))
g.add((hasClaimLossFeature, RDFS.comment, Literal("Administrative boundary (feature) where the event claim loss occurred.")))

hasClaimLossCountry = URIRef(CRO.hasClaimLossCountry)
g.add((hasClaimLossCountry, RDF.type, RDF.Property))
g.add((hasClaimLossCountry, RDFS.subPropertyOf, hasClaimLossFeature))
g.add((hasClaimLossCountry, RDFS.domain, EventClaim))
g.add((hasClaimLossCountry, RDFS.range, Country))

hasClaimLossCounty = URIRef(CRO.hasClaimLossCounty)
g.add((hasClaimLossCounty, RDF.type, RDF.Property))
g.add((hasClaimLossCounty, RDFS.subPropertyOf, hasClaimLossFeature))
g.add((hasClaimLossCounty, RDFS.domain, EventClaim))
g.add((hasClaimLossCounty, RDFS.range, County))
g.add((hasClaimLossCounty, RDFS.label, Literal("Has Claim Loss County")))
g.add((hasClaimLossCounty, RDFS.comment, Literal("County where the event claim loss occurred.")))

hasClaimLossZip = URIRef(CRO.hasClaimLossZip)
g.add((hasClaimLossZip, RDF.type, RDF.Property))
g.add((hasClaimLossZip, RDFS.subPropertyOf, hasClaimLossFeature))
g.add((hasClaimLossZip, RDFS.domain, EventClaim))
g.add((hasClaimLossZip, RDFS.range, ZipCode))
g.add((hasClaimLossZip, RDFS.label, Literal("Has Claim Loss Zip")))
g.add((hasClaimLossZip, RDFS.comment, Literal("ZIP code area where the event claim loss occurred.")))


hasClaimRecord = URIRef(CRO.hasClaimRecord)
g.add((hasClaimRecord, RDF.type, RDF.Property))
g.add((hasClaimRecord, RDFS.domain, Event))
g.add((hasClaimRecord, RDFS.range, EventClaim))

g.add((hasClaimRecord,OWL.inverseOf,hasClaimEvent))

EventFootprint = URIRef(CRO.EventFootprint)
EventFootprintGeometry = URIRef(CRO.EventFootprintGeometry)

g.add((EventFootprint, RDF.type, RDFS.Class))
g.add((EventFootprint, RDFS.subClassOf, FeatureCollection))

g.add((EventFootprintGeometry, RDF.type, RDFS.Class))
g.add((EventFootprintGeometry, RDFS.subClassOf, GeometryCollection))

g.add((EventFootprint, RDF.type, RDFS.Class))
g.add((EventFootprint, RDFS.subClassOf, FeatureCollection))

g.add((hasGeometry, RDFS.domain, EventFootprint))
g.add((hasGeometry, RDFS.range, EventFootprintGeometry))

hasFootprint = CRO.hasEventFootprint
eventFootprintOf = CRO.eventFootprintOf

g.add((hasFootprint, RDF.type, RDF.Property))
g.add((hasFootprint, RDFS.domain, Event))
g.add((hasFootprint, RDFS.range, EventFootprint))

g.add((eventFootprintOf, RDF.type, RDF.Property))
g.add((eventFootprintOf, RDFS.domain, EventFootprint))
g.add((eventFootprintOf, RDFS.range, Event))

g.add((hasFootprint, OWL.inverseOf, eventFootprintOf))

## ------------------------------------------
### EXPOSURE CLASS

Exposure = URIRef(CRO.Exposure)
g.add((Exposure, RDF.type, RDFS.Class))

## ------------------------------------------
### PORTFOLIO CLASS

# Define the Portfolio namespace

# Define the Portfolio class
Portfolio = URIRef(CRO.Portfolio)
g.add((Portfolio, RDF.type, RDFS.Class))

# Define Portfolio properties
ptimestamp = URIRef(CRO.portfoliotimestamp)

g.add((ptimestamp, RDF.type, RDF.Property))
g.add((ptimestamp, RDFS.domain, Portfolio))
g.add((ptimestamp, RDFS.range, TIME.Instant))


# Define relationship: Portfolio connected to LOB via hasLOB
partOfLOB = URIRef(CRO.partOfLOB) 
g.add((partOfLOB, RDF.type, RDF.Property))
g.add((partOfLOB, RDFS.domain, Portfolio))
g.add((partOfLOB, RDFS.range, CRO.LOB))  # Links to the LOB class


# Define the Portfolio class
Account = URIRef(CRO.Account)
g.add((Account, RDF.type, RDFS.Class))

# Define the Portfolio class
Policy = URIRef(CRO.Policy)
g.add((Policy, RDF.type, RDFS.Class))

# Define the Portfolio class
Location = URIRef(CRO.Location)
g.add((Location, RDF.type, RDFS.Class))

g.add((Location, RDFS.subClassOf, Exposure))
g.add((Account, RDFS.subClassOf, Exposure))
g.add((Portfolio, RDFS.subClassOf, Exposure))
g.add((LOBClass, RDFS.subClassOf, Exposure))


# Define relationship: Portfolio connected to LOB via hasLOB
partOfPortfolio = URIRef(CRO.partOfPortfolio)
g.add((partOfPortfolio, RDF.type, RDF.Property))
g.add((partOfPortfolio, RDFS.domain, Account))
g.add((partOfPortfolio, RDFS.range, Portfolio))  # Links to the LOB class

hasPolicyClaim = URIRef(CRO.hasPolicyClaim)
g.add((hasPolicyClaim, RDF.type, RDF.Property))
g.add((hasPolicyClaim, RDFS.domain, Policy))
g.add((hasPolicyClaim, RDFS.range, PolicyClaim))  # Links to the LOB class

# Define relationship: Portfolio connected to LOB via hasLOB
partOfAccount = URIRef(CRO.partOfAccount)
g.add((partOfAccount, RDF.type, RDF.Property))
g.add((partOfAccount, RDFS.domain, Location))
g.add((partOfAccount, RDFS.range, Account))  # Links to the LOB class

coveredBy = URIRef(CRO.coveredBy)
g.add((coveredBy, RDF.type, RDF.Property))
g.add((coveredBy, RDFS.domain, Account))
g.add((coveredBy, RDFS.range, Policy))  # Links to the LOB class

locatedIn = URIRef(CRO.locatedIn)
g.add((locatedIn, RDF.type, RDF.Property))
g.add((locatedIn, RDFS.domain, Location))
g.add((locatedIn, RDFS.range, Feature))  # Links to the LOB class

policyIncludesPeril = URIRef(CRO.policyIncludesPeril)
g.add((policyIncludesPeril, RDF.type, RDF.Property))
g.add((policyIncludesPeril, RDFS.domain, Policy))
g.add((policyIncludesPeril, RDFS.range, Peril))  


## Exposure Accumulation Class
##3 ------------------------------------------------------------------
# --------------------------------------------------------

# Define the CatModel class and its properties
CatModel = URIRef(CRO.CatastropheModel)
g.add((CatModel, RDF.type, RDFS.Class))

Vendor = URIRef(CRO.vendor)

g.add((Vendor, RDF.type, RDF.Property))
g.add((Vendor, RDFS.domain, CatModel))
g.add((Vendor, RDFS.range, XSD.string))

availability = URIRef(CRO.availabilityInterval)
g.add((availability, RDF.type, RDF.Property))
g.add((availability, RDFS.domain, CatModel))
g.add((availability, RDFS.range, TIME.Interval))

# Define relationships for CatModel
includesPeril = URIRef(CRO.includesPeril)
hasModelDomainRegion = URIRef(CRO.hasModelDomainRegion)

g.add((includesPeril, RDF.type, RDF.Property))
g.add((includesPeril, RDFS.domain, CatModel))
g.add((includesPeril, RDFS.range, Peril))

g.add((hasModelDomainRegion, RDF.type, RDF.Property))
g.add((hasModelDomainRegion, RDFS.domain, CatModel))
g.add((hasModelDomainRegion, RDFS.range, CatModelDomainRegion))

# Define LossModeling class and its properties
LossModeling = URIRef(CRO.LossModelAnalysis)
g.add((LossModeling, RDF.type, RDFS.Class))

ltimestamp = URIRef(CRO.analysisDate)
analysisID = URIRef(CRO.analysisID)
analysisName = URIRef(CRO.analysisName)

g.add((ltimestamp, RDF.type, RDF.Property))
g.add((ltimestamp, RDFS.domain, LossModeling))
g.add((ltimestamp, RDFS.range, TIME.Instant))

g.add((analysisID, RDF.type, RDF.Property))
g.add((analysisID, RDFS.domain, LossModeling))
g.add((analysisID, RDFS.range, XSD.string))

g.add((analysisName, RDF.type, RDF.Property))
g.add((analysisName, RDFS.domain, LossModeling))
g.add((analysisName, RDFS.range, XSD.string))

hasExposure = URIRef(CRO.hasExposure)
g.add((hasExposure, RDF.type, RDF.Property))
g.add((hasExposure, RDFS.domain, LossModeling))
g.add((hasExposure, RDFS.range, Exposure))

# Define sub-properties
hasPortfolio = URIRef(CRO.hasPortfolio)
g.add((hasPortfolio, RDF.type, RDF.Property))
g.add((hasPortfolio, RDFS.subPropertyOf, hasExposure))
g.add((hasPortfolio, RDFS.domain, LossModeling))
g.add((hasPortfolio, RDFS.range, Portfolio))

hasAccount = URIRef(CRO.hasAccount)
g.add((hasAccount, RDF.type, RDF.Property))
g.add((hasAccount, RDFS.subPropertyOf, hasExposure))
g.add((hasAccount, RDFS.domain, LossModeling))
g.add((hasAccount, RDFS.range, Account))

hasLocation = URIRef(CRO.hasLocation)
g.add((hasLocation, RDF.type, RDF.Property))
g.add((hasLocation, RDFS.subPropertyOf, hasExposure))
g.add((hasLocation, RDFS.domain, LossModeling))
g.add((hasLocation, RDFS.range, Location))

RiskScenario = URIRef(CRO.RiskScenario)
g.add((RiskScenario, RDF.type, RDFS.Class))

DisasterScenario = URIRef(CRO.DisasterScenario)
CharacteristicEvent = URIRef(CRO.CharacteristicEvent)

g.add((DisasterScenario, RDF.type, RDFS.Class))
g.add((CharacteristicEvent, RDF.type, RDFS.Class))

g.add((DisasterScenario, RDFS.subClassOf, RiskScenario))
g.add((CharacteristicEvent, RDFS.subClassOf, RiskScenario))

# Define LossModeling sub-classes: CatastropheModelingResults and AccumulationResults
CatastropheModelingResults = URIRef(CRO.CatastropheModelingAnalysis)

g.add((CatastropheModelingResults, RDF.type, RDFS.Class))
g.add((CatastropheModelingResults, RDFS.subClassOf, LossModeling))

ExposureAccumulationResults = URIRef(CRO.ExposureAccumulationAnalysis)
g.add((ExposureAccumulationResults, RDF.type, RDFS.Class))
g.add((ExposureAccumulationResults, RDFS.subClassOf, LossModeling))

ScenarioModelingAnalysis = URIRef(CRO.ScenarioModelingAnalysis)
g.add((ScenarioModelingAnalysis, RDF.type, RDFS.Class))
g.add((ScenarioModelingAnalysis, RDFS.subClassOf, LossModeling))


# Define relationship for CatastropheModelingResults to CatModel
hasCatModel = URIRef(CRO.hasCatModel)
g.add((hasCatModel, RDF.type, RDF.Property))
g.add((hasCatModel, RDFS.domain, CatastropheModelingResults))
g.add((hasCatModel, RDFS.range, CatModel))

AnalysisOutput = URIRef(CRO.AnalysisOutput)
g.add((AnalysisOutput, RDF.type, RDFS.Class))

# Define ResultRecord class and its subclasses AAL and EPCURVE
ResultRecord = URIRef(CRO.CatModelResultRecord)

g.add((ResultRecord, RDF.type, RDFS.Class))
g.add((ResultRecord, RDFS.subClassOf, AnalysisOutput))

AAL = URIRef(CRO.AAL)

PortfolioAAL = URIRef(CRO.PortfolioAAL)
AccountAAL = URIRef(CRO.AccountAAL)
LocationAAL = URIRef(CRO.LocationAAL)

EPCURVE = URIRef(CRO.EPCURVE)
OEP = URIRef(CRO.OEP)
AEP = URIRef(CRO.AEP)

YLT = URIRef(CRO.YLT)
ELT = URIRef(CRO.ELT)
YELT = URIRef(CRO.YELT)
TVAR = URIRef(CRO.TVAR)

g.add((AAL, RDF.type, RDFS.Class))
g.add((EPCURVE, RDF.type, RDFS.Class))
g.add((OEP, RDF.type, RDFS.Class))
g.add((AEP, RDF.type, RDFS.Class))

g.add((YLT, RDF.type, RDFS.Class))
g.add((ELT, RDF.type, RDFS.Class))
g.add((YELT, RDF.type, RDFS.Class))
g.add((TVAR, RDF.type, RDFS.Class))

# Specify ResultRecord as the superclass of AAL and EPCURVE
g.add((AAL, RDFS.subClassOf, ResultRecord))
g.add((EPCURVE, RDFS.subClassOf, ResultRecord))
g.add((OEP, RDFS.subClassOf, EPCURVE))
g.add((AEP, RDFS.subClassOf, EPCURVE))

g.add((YLT, RDFS.subClassOf, ResultRecord))
g.add((ELT, RDFS.subClassOf, ResultRecord))
g.add((YELT, RDFS.subClassOf, ResultRecord))
g.add((TVAR, RDFS.subClassOf, ResultRecord))


g.add((PortfolioAAL, RDFS.subClassOf, AAL))
g.add((AccountAAL, RDFS.subClassOf, AAL))
g.add((LocationAAL, RDFS.subClassOf, AAL))

# Define properties for ResultRecord
detailLevel  = URIRef(CRO.detailLevel)

# Declare the data property
g.add((detailLevel, RDF.type, RDF.Property))
g.add((detailLevel, RDFS.domain, ResultRecord))
g.add((detailLevel, RDFS.range, XSD.string))

# Define properties for AAL
mean_loss = URIRef(CRO.meanvalue)
sd_loss = URIRef(CRO.sdvalue)

g.add((mean_loss, RDF.type, RDF.Property))
g.add((mean_loss, RDFS.domain, AAL))
g.add((mean_loss, RDFS.range, XSD.float))

g.add((sd_loss, RDF.type, RDF.Property))
g.add((sd_loss, RDFS.domain, AAL))
g.add((sd_loss, RDFS.range, XSD.float))

# Define properties for EPCURVE (including shared properties with AAL)
return_period = URIRef(CRO.returnperiod)

g.add((return_period, RDF.type, RDF.Property))
g.add((return_period, RDFS.domain, EPCURVE))
g.add((return_period, RDFS.range, XSD.float))

meanloss = URIRef(CRO.ep_loss)

# Associate mean_loss and sd_loss with EPCURVE as well
g.add((meanloss, RDF.type, RDF.Property))
g.add((meanloss, RDFS.domain, EPCURVE))
g.add((meanloss, RDFS.range, XSD.float))

sdloss = URIRef(CRO.ep_loss_sd)

g.add((sdloss, RDF.type, RDF.Property))
g.add((sdloss, RDFS.domain, EPCURVE))
g.add((sdloss, RDFS.range, XSD.float))

# Define properties for linking CatastropheModelingResults and ResultRecord
has_AAL = URIRef(CRO.hasAAL)
has_EP = URIRef(CRO.hasEPCurve)

relatedToExposure  = URIRef(CRO.underlyingExposure)
exposureFor = URIRef(CRO.exposureFor)

g.add((relatedToExposure , RDF.type, RDF.Property))
g.add((relatedToExposure , RDFS.domain, ResultRecord))
g.add((relatedToExposure , RDFS.range, Exposure))

g.add((exposureFor, RDF.type, RDF.Property))
g.add((exposureFor, RDFS.domain, Exposure))
g.add((exposureFor, RDFS.range, ResultRecord))

part_of_cat_model_analysis = URIRef(CRO.partOfCatModelAnalysis)

# Set hasResultRecord as an ObjectProperty from CatastropheModelingResults to ResultRecord
g.add((has_AAL, RDF.type, RDF.Property))
g.add((has_AAL, RDFS.domain, CatastropheModelingResults))
g.add((has_AAL, RDFS.range, AAL))

# Set hasResultRecord as an ObjectProperty from CatastropheModelingResults to ResultRecord
g.add((has_EP, RDF.type, RDF.Property))
g.add((has_EP, RDFS.domain, CatastropheModelingResults))
g.add((has_EP, RDFS.range, EPCURVE))

# Set partOfCatModelAnalysis as an inverse property to hasResultRecord
g.add((part_of_cat_model_analysis, RDF.type, RDF.Property))
g.add((part_of_cat_model_analysis, RDFS.domain, ResultRecord))
g.add((part_of_cat_model_analysis, RDFS.range, CatastropheModelingResults))

# -------------------------- exposure accumulation -------------------------------------

ExposureAccumulationRecord = URIRef(CRO.ExposureAccumulationRecord)
g.add((ExposureAccumulationRecord, RDFS.subClassOf, AnalysisOutput))


# Define relationship between Exposure and Portfolio
forPortfolio = URIRef(CRO.forPortfolio)
g.add((forPortfolio, RDF.type, RDF.Property))
g.add((forPortfolio, RDFS.domain, ExposureAccumulationResults))
g.add((forPortfolio, RDFS.range, Portfolio))

# Define relationship between Exposure and Peril
forPeril = URIRef(CRO.forPeril)
g.add((forPeril, RDF.type, RDF.Property))
g.add((forPeril, RDFS.domain, ExposureAccumulationResults))
g.add((forPeril, RDFS.range, Peril))

# Define relationship between Exposure and Peril
forFeature = URIRef(CRO.forFeature)
g.add((forFeature, RDF.type, RDF.Property))
g.add((forFeature, RDFS.domain, ExposureAccumulationRecord))
g.add((forFeature, RDFS.range, Feature))

part_of_exp_analysis = URIRef(CRO.partOfExposureAccumulatonAnalysis)
g.add((part_of_exp_analysis, RDF.type, RDF.Property))
g.add((part_of_exp_analysis, RDFS.domain, ExposureAccumulationRecord))
g.add((part_of_exp_analysis, RDFS.range, ExposureAccumulationResults))

# --------------------------------------------------------------

hasRiskScenario = URIRef(CRO.hasRiskScenario)
g.add((hasRiskScenario, RDF.type, RDF.Property))
g.add((hasRiskScenario, RDFS.domain, ScenarioModelingAnalysis))
g.add((hasRiskScenario, RDFS.range, RiskScenario))

ScenarioModelingRecord = URIRef(CRO.ScenarioModelingRecord)
g.add((ScenarioModelingRecord, RDFS.subClassOf, AnalysisOutput))

#---------------------------------------------------------------

AggregationVector = URIRef(CRO.AggregationVector)
ylpr = URIRef(CRO.ylpr)
PerilRegion = URIRef(CRO.PerilRegion)

g.add((AggregationVector, RDF.type, RDFS.Class))
g.add((ylpr, RDFS.subClassOf, AggregationVector))
g.add((PerilRegion, RDFS.subClassOf, AggregationVector))

ylpr_y = URIRef(CRO.hasYearAttribute)
ylpr_l = URIRef(CRO.hasLOBAttribute)
ylpr_p = URIRef(CRO.hasPerilAttribute)
ylpr_r = URIRef(CRO.hasRegionAttribute)

ylpr_description = URIRef(CRO.desc)

g.add((ylpr_y, RDF.type, RDF.Property))
g.add((ylpr_y, RDFS.domain, ylpr))
g.add((ylpr_y, RDFS.range, XSD.int))

g.add((ylpr_l, RDF.type, RDF.Property))
g.add((ylpr_l, RDFS.domain, ylpr))
g.add((ylpr_l, RDFS.range, LOBClass))

g.add((ylpr_p, RDF.type, RDF.Property))
g.add((ylpr_p, RDFS.domain, ylpr))
g.add((ylpr_p, RDFS.range, Peril))

g.add((ylpr_r, RDF.type, RDF.Property))
g.add((ylpr_r, RDFS.domain, ylpr))
g.add((ylpr_r, RDFS.range, Region))

pr_p = URIRef(CRO.hasPerilAttribute)
pr_r = URIRef(CRO.hasRegionAttribute)

g.add((pr_p, RDF.type, RDF.Property))
g.add((pr_p, RDFS.domain, PerilRegion))
g.add((pr_p, RDFS.range, Peril))

g.add((pr_r, RDF.type, RDF.Property))
g.add((pr_r, RDFS.domain, PerilRegion))
g.add((pr_r, RDFS.range, Region))


# ------------------------

EventLoss = URIRef(CRO.EventLoss)
g.add((EventLoss, RDF.type, RDFS.Class))

ev_ylpr = URIRef(CRO.loss_ylpr)

g.add((ev_ylpr, RDF.type, RDF.Property))
g.add((ev_ylpr, RDFS.domain, EventLoss))
g.add((ev_ylpr, RDFS.range, ylpr))

g.add((CRO.eventLossOf, RDF.type, RDF.Property))
g.add((CRO.eventLossOf, RDFS.domain, CRO.EventLoss))
g.add((CRO.eventLossOf, RDFS.range, Event))

g.add((CRO.hasEventLossRecord, RDF.type, RDF.Property))
g.add((CRO.hasEventLossRecord, RDFS.domain, Event))
g.add((CRO.hasEventLossRecord, RDFS.range, EventLoss))

g.add((CRO.hasEventLossRecord, OWL.inverseOf, CRO.eventLossOf))

g.add((CRO.hasPeril, RDF.type, RDF.Property))
g.add((CRO.hasPeril, RDFS.domain, CRO.EventLoss))
g.add((CRO.hasPeril, RDFS.range, Peril))

g.add((CRO.hasLOB, RDF.type, RDF.Property))
g.add((CRO.hasLOB, RDFS.domain, CRO.EventLoss))
g.add((CRO.hasLOB, RDFS.range, LOBClass))

g.add((CRO.hasLossCountry, RDF.type, RDF.Property))
g.add((CRO.hasLossCountry, RDFS.domain, CRO.EventLoss))
g.add((CRO.hasLossCountry, RDFS.range, Country))

cat_ylpr = URIRef(CRO.model_ylpr)

g.add((cat_ylpr, RDF.type, RDF.Property))
g.add((cat_ylpr, RDFS.domain, CatastropheModelingResults))
g.add((cat_ylpr, RDFS.range, ylpr))

# ---------------------------

hasRelevantModeledLoss = URIRef(CRO.hasRelevantModeledLoss)
hasRelevantEventLoss = URIRef(CRO.hasRelevantEventLoss)

g.add((hasRelevantModeledLoss, RDF.type, RDF.Property))
g.add((hasRelevantModeledLoss, RDFS.domain, ylpr))
g.add((hasRelevantModeledLoss, RDFS.range, CatastropheModelingResults))

g.add((hasRelevantEventLoss, RDF.type, RDF.Property))
g.add((hasRelevantEventLoss, RDFS.domain, ylpr))
g.add((hasRelevantEventLoss, RDFS.range, EventLoss))

# ---------------------------
# Feature collection membership (FeatureCollection <-> Feature), inverse pair.
# Label/comment set explicitly (not in Excel).
containsFeature = URIRef(CRO.containsFeature)
memberOf = URIRef(CRO.memberOf)

g.add((containsFeature, RDF.type, RDF.Property))
g.add((containsFeature, RDFS.domain, FeatureCollection))
g.add((containsFeature, RDFS.range, Feature))
g.add((containsFeature, RDFS.label, Literal("Contains Feature")))
g.add((containsFeature, RDFS.comment, Literal("Relates a feature collection to a feature it contains.")))

g.add((memberOf, RDF.type, RDF.Property))
g.add((memberOf, RDFS.domain, Feature))
g.add((memberOf, RDFS.range, FeatureCollection))
g.add((memberOf, RDFS.label, Literal("Member Of")))
g.add((memberOf, RDFS.comment, Literal("Relates a feature to the feature collection of which it is a member.")))

g.add((containsFeature, OWL.inverseOf, memberOf))

# NOTE: hasAdminBoundary / isPartOf / inCatDomainOf are deliberately NOT made
# children of containsFeature. They encode analytical membership (loss-region
# aggregation and cat-model-domain coverage), which is distinct from the purely
# spatial containment modeled here.

# Level-specific children of containsFeature (state intentionally skipped).
containsCountry = URIRef(CRO.containsCountry)
containsCounty = URIRef(CRO.containsCounty)
containsZip = URIRef(CRO.containsZip)

g.add((containsCountry, RDF.type, RDF.Property))
g.add((containsCountry, RDFS.subPropertyOf, containsFeature))
g.add((containsCountry, RDFS.domain, FeatureCollection))
g.add((containsCountry, RDFS.range, Country))
g.add((containsCountry, RDFS.label, Literal("Contains Country")))
g.add((containsCountry, RDFS.comment, Literal("Relates a feature collection to a country it contains.")))

g.add((containsCounty, RDF.type, RDF.Property))
g.add((containsCounty, RDFS.subPropertyOf, containsFeature))
g.add((containsCounty, RDFS.domain, FeatureCollection))
g.add((containsCounty, RDFS.range, County))
g.add((containsCounty, RDFS.label, Literal("Contains County")))
g.add((containsCounty, RDFS.comment, Literal("Relates a feature collection to a county it contains.")))

g.add((containsZip, RDF.type, RDF.Property))
g.add((containsZip, RDFS.subPropertyOf, containsFeature))
g.add((containsZip, RDFS.domain, FeatureCollection))
g.add((containsZip, RDFS.range, ZipCode))
g.add((containsZip, RDFS.label, Literal("Contains Zip")))
g.add((containsZip, RDFS.comment, Literal("Relates a feature collection to a ZIP code area it contains.")))

# ---------------------------

####### DATA PROPERTY ******

datatypes = {'bool':XSD.boolean, 'str':XSD.string,'datetime':XSD.date,'float':XSD.float,'int':XSD.int,"double":XSD.double}


def add_data_properties(classURI,dataproperties):
    for propname,dtype in dataproperties.items():
        uri = CRO[propname]
        g.add((uri, RDF.type, RDF.Property))
        g.add((uri, RDFS.domain, classURI))
        g.add((uri, RDFS.range, datatypes[dtype]))


country_dataproperties = {"adminBoundaryCategory":"str",
                          "adminBoundaryCode":"str",
                          "adminBoundaryName":"str"}

lossregion_dataproperties = {"lossRegionCategory":"str",
                             "lossRegionCode":"str",
                             "lossRegionName":"str"}

peril_dataproperties = {"perilID":"str",
                        "perilName":"str",
                        "perilCode":"str",
                        "perilShortName":"str"}

event_dataproperties = {"eventID":"str",
                        "eventName":"str",
                        "eventYear":"str",
                        "eventQuarter":"str",
                        "catFamily":"str"}

eventperilmap_dataproperties = {"epindex":"str",
                                "eventinfo":"str",
                                "perilinfo":"str",
                                "factor":"float"
                                }

lob_dataproperties = { "lobName":"str",
                        "lobDescription":"str"                                                
                        }

eventclaim_dataproperties = { "grossIncurred": "float",
                            "lastUpdated" : "datetime",
                            "IBNR" : "float",
                            "completenessRatio":"float",
                            "recordID":"int"    
                        }

portfolio_dataproperties = {"portfolioDate":"datetime",
                            "portfolioYear":"int",
                            "portfolioID":"str",
                            "portfolioName":"str",
                            "portfolioLOB" : "str",
                            "exposureDetailLevel":"str"
                            }

catdomain_dataproperties = {
                            "catDomainDescription":"str",
                            "relatedLossRegionName": "str"
                            }

catmodel_dataproperties = {
                            "catModelID":"str",
                            "catModelRegion":"str",
                            "catModelPeril":"str",
                            "catModelAvailabilityStart":"int",
                            "catModelAvailabilityEnd":"int",
                            "catModelName":"str",
                            "catModelDescription":"str",
                            "catModelEvaluationNotes":"str"
                            }

ylpr_dataproperties = {"ylpr_tag":"str"}


eventloss_dataproperties = {
                                "perilContributionFactor":"float",
                                "hasGrossIncurredLoss":"float",
                                "loss_ylpr_tag":"str",
                                "isModeledLoss":"bool"   
                            }

lossmodeling_dataproperties = {   "analysisName":"str",
                                    "analysisDescription":"str",
                                    "analysisLevel":"str",
                                    "analysisType":"str"}

expAccumulation_dataproperties = {
                                        "totalnsuredValue": "double",
                                        "grossLimit":"double"
                            }


add_data_properties(Country,country_dataproperties)
add_data_properties(LossRegion,lossregion_dataproperties)
add_data_properties(LossPeril,peril_dataproperties)
add_data_properties(Event,event_dataproperties)
add_data_properties(EventPerilMap,eventperilmap_dataproperties)
add_data_properties(LOBClass,lob_dataproperties)
add_data_properties(EventClaim,eventclaim_dataproperties)
add_data_properties(Portfolio,portfolio_dataproperties)
add_data_properties(CatModelDomainRegion,catdomain_dataproperties)
add_data_properties(CatModel,catmodel_dataproperties)
add_data_properties(ylpr,ylpr_dataproperties)
add_data_properties(EventLoss,eventloss_dataproperties)
add_data_properties(LossModeling,lossmodeling_dataproperties)
add_data_properties(ExposureAccumulationRecord,expAccumulation_dataproperties)

excel_file = "ontology_definitions.xlsx"
class_df = pd.read_excel(excel_file, sheet_name="class")

for index, row in class_df.iterrows():
    class_name = row['DefinedClass']  # Adjust column name if different
    label = row['label']
    description = row['description']

    class_uri = CRO[class_name]

    # Add or update label and comment
    g.set((class_uri, RDFS.label, Literal(label)))
    g.set((class_uri, RDFS.comment, Literal(description)))

# Process property definitions
prop_df = pd.read_excel(excel_file, sheet_name="property")

for index, row in prop_df.iterrows():
    prop_name = row['Property']  # Adjust column name if different
    label = row['label']
    description = row['description']

    prop_uri = CRO[prop_name]

    g.set((prop_uri, RDFS.label, Literal(label)))
    g.set((prop_uri, RDFS.comment, Literal(description)))
    
    # Add functional/inverse functional
    if row.get("functional", "") == 1:
        g.add((prop_uri, RDF.type, OWL.FunctionalProperty))
    if row.get("inversefunctional", "") == 1:
        g.add((prop_uri, RDF.type, OWL.InverseFunctionalProperty))

    # source_class = CRO[row["Source"]]
    
    # min_card = row.get("minCardinality")
    # max_card = row.get("maxCardinality")
    
    # restriction = BNode()

    # if pd.notna(min_card) or pd.notna(max_card):
    #     g.add((source_class, RDFS.subClassOf, restriction))
    #     g.add((restriction, RDF.type, OWL.Restriction))
    #     g.add((restriction, OWL.onProperty, prop_uri))

    #     if pd.notna(min_card):
    #         g.add((restriction, OWL.minCardinality, Literal(int(min_card), datatype=XSD.nonNegativeInteger)))

    #     if pd.notna(max_card):
    #         g.add((restriction, OWL.maxCardinality, Literal(int(max_card), datatype=XSD.nonNegativeInteger)))    
    
# save
g.serialize(destination='cro_schema.ttl', format='turtle')