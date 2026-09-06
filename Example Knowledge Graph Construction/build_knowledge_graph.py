# -*- coding: utf-8 -*-
"""
build_knowledge_graph.py -- construct the example catastrophe-risk knowledge graph.

Starts from the CRO schema graph built in cro_schema.py, loads the instance data
from knowledge_graph_data.xlsx (countries, regions, perils, events, event/peril
factors, claims, portfolios, cat models, portfolio AAL and EP curves), derives
EventLoss, YLPR (year / LOB / peril / region) and modeled-loss-status triples via
SPARQL updates, and writes the populated graph to example_knowledge_graph.ttl.
A class/property summary of the built graph is written to ontology_summary.xlsx.

@author: Sashi Kanth Tadinada, PhD
"""

import pandas as pd
import numpy as np

from rdflib import Graph, Literal, Namespace, RDF, URIRef, OWL
from rdflib.namespace import RDFS, XSD

from cro_schema import *
from utils import *

import hashlib

# ---------------------------------------------
# LOAD FILES ----------------------------------

filename = "./knowledge_graph_data.xlsx"
country_df = pd.read_excel(filename,"country")
areas_df = pd.read_excel(filename,"areas")
peril_df = pd.read_excel(filename,"peril")

# selected events

selected_events = pd.read_excel(filename,"selected events")
selected_events_list = list(selected_events.eventcode)

lobs = pd.read_excel(filename,"lobs")

events = selected_events.copy() #pd.read_excel(filename,"events")
epfactors = pd.read_excel(filename,"epfactors") 
event_losses = pd.read_excel(filename,"event_losses")

events = events[events['eventcode'].isin(selected_events_list)]
epfactors = epfactors[epfactors['Cat Code'].isin(selected_events_list)]
event_losses = event_losses[event_losses['Cat Code'].isin(selected_events_list)]

portfolios = pd.read_excel(filename,"portfolios")
availablemodels = pd.read_excel(filename,"availablemodels")
portfolio_AAL = pd.read_excel(filename,"portfolio_AAL")
epcurves = pd.read_excel(filename,"epcurves")
catmodeldomains = pd.read_excel(filename,"catmodeldomains",usecols="A:C").dropna()
catmodeldomain_countries = pd.read_excel(filename,"catmodeldomains",usecols="H:I").dropna()

peril_map = dict(zip(peril_df['ShortName'],peril_df['Code']))

# # Load data into the graph
# # For countries
for _, row in country_df.iterrows():
    country_uri = URIRef(CRO[row['Oasis Code']])
    g.add((country_uri, RDF.type, Country))
    g.add((country_uri, CRO["adminBoundaryCategory"], Literal("country", datatype=XSD.string)))
    g.add((country_uri, CRO["adminBoundaryCode"], Literal(row['Oasis Code'], datatype=XSD.string)))
    g.add((country_uri, CRO["adminBoundaryName"], Literal(row['in OASIS'], datatype=XSD.string)))

# # For affected areas (areas_df)
for _, row in areas_df.iterrows():
    affected_area_uri = URIRef(CRO["lr_"+row['Region Code.1']])
    g.add((affected_area_uri, RDF.type, LossRegion))
    g.add((affected_area_uri, CRO["lossRegionCategory"], Literal("Loss Region", datatype=XSD.string)))
    g.add((affected_area_uri, CRO["lossRegionCode"], Literal(row['Region Code.1'], datatype=XSD.string)))
    g.add((affected_area_uri, CRO["lossRegionName"], Literal(row['RegionGroup'], datatype=XSD.string)))

for _, row in country_df.iterrows():
    subregion_uri = URIRef(CRO[row['Oasis Code']])
    affected_area_uri = URIRef(CRO["lr_"+row['Region Code']])
    g.add((affected_area_uri, containsAdminBoundary, subregion_uri))
    g.add((subregion_uri, isPartOf, affected_area_uri))

for _, row in peril_df.iterrows():
    peril_uri = URIRef(CRO[row['Code']])
    g.add((peril_uri, RDF.type, LossPeril))
    g.add((peril_uri, CRO["perilID"], Literal(row['PerilID'], datatype=XSD.string)))
    g.add((peril_uri, CRO["perilCode"], Literal(row['Code'], datatype=XSD.string)))
    g.add((peril_uri, CRO["perilName"], Literal(row['Peril Description'], datatype=XSD.string)))
    g.add((peril_uri, CRO["perilShortName"], Literal(row['ShortName'], datatype=XSD.string)))

# for events
# Properties for attributes

for _, row in events.iterrows():
    event_uri = URIRef(CRO[str(row['eventcode'])])
    g.add((event_uri, RDF.type, Event))
    g.add((event_uri, CRO["eventID"], Literal(str(row['eventcode']), datatype=XSD.string)))
    g.add((event_uri, CRO["eventName"], Literal(row['eventname'], datatype=XSD.string)))
    g.add((event_uri, CRO["catFamily"], Literal(row['Cat Family'], datatype=XSD.string)))
    g.add((event_uri, CRO["eventYear"], Literal(row['year'], datatype=XSD.int)))
    time_interval_uri = URIRef(TIME['DatesOfEvent'+str(row['eventcode'])])
    starttime = URIRef(TIME['StartEvent'+str(row['eventcode'])])
    endtime = URIRef(TIME['EndOfEvent'+str(row['eventcode'])])
 
    g.add((time_interval_uri, RDF.type, TIME.Interval))
    g.add((starttime, RDF.type, TIME.Instant))
    g.add((endtime, RDF.type, TIME.Instant))
    
    g.add((starttime, TIME.inXSDDate, Literal(row['startdate'], datatype=XSD.date)))
    g.add((endtime, TIME.inXSDDate, Literal(row['enddate'], datatype=XSD.date)))
    
    g.add((time_interval_uri,TIME.hasBeginning, starttime))
    g.add((time_interval_uri,TIME.hasEnd, endtime))
    
    g.add((event_uri, OccurenceTime, time_interval_uri))

for _, row in epfactors.iterrows():
    map_uri = URIRef(CRO['epf-'+str(row['index'])])
    g.add((map_uri, RDF.type, EventPerilMap))
    g.add((map_uri, CRO["eventinfo"], Literal(row['Cat Code'], datatype=XSD.string)))
    g.add((map_uri, CRO["epindex"], Literal(row['index'], datatype=XSD.int)))
    g.add((map_uri, CRO["perilinfo"], Literal(row['Code'], datatype=XSD.string)))
    g.add((map_uri, CRO["factor"], Literal(row['ContributionFactor'], datatype=XSD.float)))
    
    g.add((map_uri, hasEvent, URIRef(CRO[str(row['Cat Code'])])))
    g.add((map_uri, hasPeril, URIRef(CRO[row['Code']])))
    g.add((map_uri, hasFactorValue, Literal(row['ContributionFactor'], datatype=XSD.float)))
    
    g.add((URIRef(CRO[str(row['Cat Code'])]), hasEventPerilMap, map_uri))

for lob in list(lobs.LOB):
    lob_uri = CRO[lob.replace(" ","")]
    g.add((lob_uri, RDF.type, LOBClass))
    g.add((lob_uri, CRO["lobName"], Literal(lob.replace(" ",""), datatype=XSD.string)))
    g.add((lob_uri, CRO["lobDescription"], Literal(lob, datatype=XSD.string)))
    
# add ibnr etc
for index, row in event_losses.iterrows():
    claim_uri = URIRef(CRO['c-'+str(index)])
    g.add((claim_uri, RDF.type, EventClaim))
    g.add((claim_uri, CRO["grossIncurred"], Literal(row['GrossIncurred'], datatype=XSD.float)))
    g.add((claim_uri, CRO["lastUpdated"], Literal('2025-01-01', datatype=XSD.date)))
    g.add((claim_uri, CRO["IBNR"], Literal(row['IBNR'], datatype=XSD.float)))
    g.add((claim_uri, CRO["completenessRatio"], Literal(row['completeness_ratio'], datatype=XSD.float))) 
    g.add((claim_uri, CRO["recordID"], Literal(index, datatype=XSD.int)))
    
    g.add((claim_uri, hasClaimEvent, URIRef(CRO[str(row['Cat Code'])])))
    g.add((URIRef(CRO[str(row['Cat Code'])]), hasClaimRecord,claim_uri))
    
    g.add((claim_uri, hasClaimLOB, URIRef(CRO[row['LOB'].replace(" ","")])))
    g.add((claim_uri, hasClaimLossCountry, URIRef(CRO[row['CountryCode']])))

for _, row in portfolios.iterrows():
    port_uri = URIRef(CRO['port-'+str(row['index'])])
    g.add((port_uri, RDF.type, Portfolio))
    g.add((port_uri, CRO["portfolioDate"], Literal("{}-12-31".format(row['year']), datatype=XSD.date)))
    g.add((port_uri, CRO["portfolioID"], Literal(row['index'], datatype=XSD.int)))
    g.add((port_uri, CRO["portfolioName"], Literal(row['portname'], datatype=XSD.string)))
    g.add((port_uri, CRO["portfolioLOB"], Literal(row['LOB'], datatype=XSD.string)))
    g.add((port_uri, CRO["exposureDetailLevel"], Literal("portfolio", datatype=XSD.string)))
    
    port_time_uri = URIRef(TIME['portdate'+str(row['index'])])
    g.add((port_time_uri, RDF.type, TIME.Instant))
    g.add((port_time_uri, TIME.inXSDDate, Literal("{}-12-31".format(row['year']), datatype=XSD.date)))
    
    #set timestamp for portfolio
    g.add((port_uri,ptimestamp,port_time_uri))
    
    #partOfLOB
    g.add((port_uri, partOfLOB, URIRef(CRO[row['LOB'].replace(" ","")])))

# # For affected areas (areas_df)
for _, row in catmodeldomains.iterrows():
    catmodel_area_uri = URIRef(CRO["cr_"+row['CatModelDomainName']])
    g.add((catmodel_area_uri, RDF.type, CatModelDomainRegion))
    g.add((catmodel_area_uri, CRO["relatedLossRegionName"], Literal(row['RelatedLossRegion'], datatype=XSD.string)))
    g.add((catmodel_area_uri, CRO["catDomainDescription"], Literal(row['CatDomainDescription'], datatype=XSD.string)))
    lossregion_uri = URIRef(CRO["lr_"+row['RelatedLossRegion']])
    g.add((catmodel_area_uri,relatedLossRegion,lossregion_uri))

for _, row in catmodeldomain_countries.iterrows():
    subregion_uri = URIRef(CRO[row['Country']])
    catmodel_area_uri = URIRef(CRO["cr_"+row['CatModelDomainName.1']])
    g.add((catmodel_area_uri, containsAdminBoundary, subregion_uri))
    g.add((subregion_uri, inCatDomainOf, catmodel_area_uri))

for _, row in availablemodels.iterrows():
    model_uri = URIRef(CRO["model-"+row['model_name']])
    g.add((model_uri, RDF.type, CatModel))
    g.add((model_uri,CRO["catModelID"],Literal(row['index'],datatype=XSD.int)))
    g.add((model_uri,CRO["catModelRegion"],Literal(row['Region'],datatype=XSD.string)))
    g.add((model_uri,CRO["catModelPeril"],Literal(peril_map[row['Peril']],datatype=XSD.string)))
    g.add((model_uri,CRO["catModelAvailabilityStart"],Literal(row['StartAvailability'],datatype=XSD.int)))
    g.add((model_uri,CRO["catModelAvailabilityEnd"],Literal(row['EndAvailability'],datatype=XSD.int)))
    g.add((model_uri,CRO["catModelName"],Literal(row['modelname'],datatype=XSD.string)))
    
    model_start = URIRef(TIME['modelstartdate_'+row['model_name']])
    model_end = URIRef(TIME['modelenddate_'+row['model_name']])
    
    g.add((model_start, RDF.type, TIME.Instant))
    g.add((model_end, RDF.type, TIME.Instant))
    
    g.add((model_start, TIME.inXSDDate, Literal("{}-01-01".format(row['StartAvailability']), datatype=XSD.date)))
    g.add((model_end, TIME.inXSDDate, Literal("{}-01-01".format(row['EndAvailability']), datatype=XSD.date)))
    
    model_interval_uri = URIRef(TIME['ModelAvailability_'+row['model_name']])
    g.add((model_interval_uri, RDF.type, TIME.Interval))

    g.add((model_interval_uri,TIME.hasBeginning, model_start))
    g.add((model_interval_uri,TIME.hasEnd, model_end))
    
    g.add((model_uri,availability,model_interval_uri))

    g.add((model_uri,hasModelDomainRegion,URIRef(CRO["cr_"+row['CatModelDomainName']])))
    g.add((model_uri,includesPeril,URIRef(CRO[peril_map[row['Peril']]])))

for index, row in portfolio_AAL.iterrows():
    cat_uri = URIRef(CRO[row['analysisname'].replace(" ","")])
    g.add((cat_uri, RDF.type, CatastropheModelingResults))
    g.add((cat_uri,CRO["analysisName"],Literal(row['analysisname'],datatype=XSD.string)))
    g.add((cat_uri,CRO["analysisLevel"],Literal("portfolio",datatype=XSD.string)))
    
    analysis_date = URIRef(TIME['analysisdate_'+row['analysisname'].replace(" ","")])
    g.add((analysis_date, RDF.type, TIME.Instant))
    g.add((analysis_date, TIME.inXSDDate, Literal("{}-12-31".format(row['year']), datatype=XSD.date)))
    
    g.add((cat_uri,CRO["AnalysisDate"],analysis_date))
        
    g.add((cat_uri,hasCatModel,URIRef(CRO["model-"+row['model_name']])))
    g.add((cat_uri,hasPortfolio,URIRef(CRO['port-'+str(row['portid'])])))

    result_uri = URIRef(CRO["aal-"+str(index)])
    g.add((result_uri, RDF.type, PortfolioAAL))
    g.add((result_uri,mean_loss,Literal(row['AAL'],datatype=XSD.float)))
    
    g.add((cat_uri,has_AAL,result_uri)) 
    g.add((result_uri,part_of_cat_model_analysis,cat_uri))
    g.add((result_uri,relatedToExposure,URIRef(CRO['port-'+str(row['portid'])])))
    g.add((URIRef(CRO['port-'+str(row['portid'])]),exposureFor,result_uri))
    
    g.add((result_uri,detailLevel,Literal("portfolio",datatype=XSD.string)))

for index, row in epcurves.iterrows():
    cat_uri = URIRef(CRO[row['analysisname'].replace(" ","")])
    
    oep_uri = URIRef(CRO["oep-"+str(index)])
    g.add((oep_uri, RDF.type, OEP))
    g.add((oep_uri,meanloss,Literal(row['Gross Loss OEP'],datatype=XSD.float)))
    g.add((oep_uri,return_period,Literal(row['Return Period'],datatype=XSD.float)))

    aep_uri = URIRef(CRO["aep-"+str(index)])
    g.add((aep_uri, RDF.type, AEP))
    g.add((aep_uri,meanloss,Literal(row['Gross Loss AEP'],datatype=XSD.float)))
    g.add((aep_uri,return_period,Literal(row['Return Period'],datatype=XSD.float)))
    
    g.add((cat_uri,has_EP,oep_uri))
    g.add((cat_uri,has_EP,aep_uri))
    
    g.add((oep_uri,part_of_cat_model_analysis,cat_uri))
    g.add((aep_uri,part_of_cat_model_analysis,cat_uri))
    
    g.add((oep_uri,detailLevel,Literal("portfolio",datatype=XSD.string)))
    g.add((aep_uri,detailLevel,Literal("portfolio",datatype=XSD.string)))


def execute_sparql(g: Graph, qry: str) -> pd.DataFrame:
    """
    Executes a SPARQL query on the given knowledge graph and returns the results as a pandas DataFrame.

    Args:
        g (Graph): An RDFLib Graph object representing the knowledge graph.
        qry (str): A SPARQL query string.

    Returns:
        pd.DataFrame: A DataFrame containing the query results.
    """
    # Execute the SPARQL query
    results = g.query(qry)

    # Extract the variable names (columns)
    columns = results.vars

    # Transform results into a list of rows
    rows = [list(row) for row in results]

    # Convert to pandas DataFrame
    df = pd.DataFrame(rows, columns=[str(var) for var in columns])

    return df

populate_eventloss_table = """
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
prefix cro: <https://w3id.org/catrisk/ontology#>

INSERT {
  ?eventloss a cro:EventLoss ;
             cro:eventLossOf ?event ; 
             cro:hasPeril ?peril ;
             cro:perilContributionFactor ?perilfactor ;
             cro:hasGrossIncurredLoss ?calculatedLoss ;
             cro:hasLOB ?lob ;
             cro:hasLossCountry ?country .
             
             # Add the inverse triple directly:
             ?event cro:hasEventLossRecord ?eventloss .
}
WHERE {
  ?eventClaim cro:hasClaimEvent ?event ;
              cro:grossIncurred ?grossIncurred ;
              cro:IBNR ?ibnr ;
              cro:hasClaimLOB ?lob ;
              cro:hasClaimLossCountry ?country .
  ?event cro:hasEventPerilMap ?epmap .
  ?epmap cro:hasPeril ?peril ;
         cro:hasFactorValue ?perilfactor .

  # Calculate the loss value
  BIND((?grossIncurred + ?ibnr)*?perilfactor AS ?calculatedLoss)

  # Create a unique identifier for the eventloss instance within the EVENTLOSS namespace
  BIND(IRI(CONCAT("https://w3id.org/catrisk/ontology#", STRUUID())) AS ?eventloss)
}
"""

g.update(populate_eventloss_table)

populate_ylpr_eventloss = """
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
prefix cro: <https://w3id.org/catrisk/ontology#>

INSERT {
    ?eventloss cro:loss_ylpr ?ylpr_instance .
    ?eventloss cro:loss_ylpr_tag ?ylpr_tag .
    ?ylpr_instance a cro:ylpr ;
                 cro:ylpr_tag ?ylpr_tag ;
                 cro:hasLOBAttribute ?lob ;
                 cro:hasPerilAttribute ?peril ;
                 cro:hasRegionAttribute ?region ;
                 cro:hasYearAttribute ?ylpryear ;
                 cro:hasRelevantEventLoss ?eventloss .
    }
WHERE {
      ?eventloss a cro:EventLoss ;
                 cro:eventLossOf ?event ;
                 cro:hasPeril ?peril ;
                 cro:hasLOB ?lob ;
                 cro:hasLossCountry ?country .

        ?event cro:occurenceTime ?timeInterval .
        ?timeInterval time:hasEnd ?endTime .
        ?endTime time:inXSDDate ?eventdate .
        
        # Derive the region from the country (assuming a region-country mapping exists)
        ?country cro:isPartOf ?region .
        
        ?event cro:eventID ?eventid .
        ?peril cro:perilCode ?perilcode .
        ?region cro:lossRegionCode ?regioncode .
        ?lob cro:lobName ?lobcode .

  # Create the YLPR tag as a concatenated unique string
  BIND(CONCAT(STR(YEAR(?eventdate)), "-", STR(?lobcode), "-", STR(?perilcode), "-", STR(?regioncode)) AS ?ylpr_tag)

  # Extract year from timestamp
  BIND(YEAR(?eventdate) AS ?ylpryear)

  # Create the YLPR instance URI
  BIND(IRI(CONCAT("https://w3id.org/catrisk/ontology#", ENCODE_FOR_URI(?ylpr_tag))) AS ?ylpr_instance)
}

"""

g.update(populate_ylpr_eventloss)

populate_catmodeling_ylpr = """
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
prefix cro: <https://w3id.org/catrisk/ontology#>

INSERT {
  ?mloss cro:model_ylpr ?ylpr_instance .
  ?mloss cro:model_ylpr_tag ?ylpr_tag .
  ?ylpr_instance a cro:ylpr ;
                 cro:ylpr_tag ?ylpr_tag ;
                 cro:hasLOBAttribute ?lob ;
                 cro:hasPerilAttribute ?peril ;
                 cro:hasRegionAttribute ?lossregion ;
                 cro:hasYearAttribute ?ylpryear ;
                 cro:hasRelevantModeledLoss ?mloss .
}

WHERE {
        ?mloss rdf:type cro:CatastropheModelingAnalysis .
        ?mloss cro:hasPortfolio ?port .
        ?port cro:partOfLOB ?lob .
        
        ?port cro:portfoliotimestamp ?portdate .
        ?portdate time:inXSDDate ?porttimestamp .
        
        ?mloss cro:hasCatModel ?cat .
        ?cat cro:includesPeril ?peril .
        
        ?mloss cro:analysisLevel ?analysislevel .
        
        ?cat cro:hasModelDomainRegion ?catregion .
        ?catregion rdf:type cro:CatModelDomainRegion .
                
        ?catregion cro:relatedLossRegion ?lossregion .
        ?lossregion cro:lossRegionCode ?regioncode .
        
        ?peril cro:perilCode ?perilcode .
        ?lob cro:lobName ?LineOfBusiness .
        ?catregion cro:catDomainDescription ?catlossregion .
        
        FILTER(?analysislevel = "portfolio")
        
      # Create the YLPR tag as a concatenated unique string
          BIND(CONCAT(STR(YEAR(?porttimestamp)), "-", STR(?LineOfBusiness), "-", STR(?perilcode), "-", STR(?regioncode)) AS ?ylpr_tag)

          # Extract year from timestamp
          BIND(YEAR(?porttimestamp) AS ?ylpryear)
    
       # Create the YLPR instance URI
        BIND(IRI(CONCAT("https://w3id.org/catrisk/ontology#", ENCODE_FOR_URI(?ylpr_tag))) AS ?ylpr_instance)    
    }
"""
    
g.update(populate_catmodeling_ylpr)

setModeledLossStatus = """
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
prefix cro: <https://w3id.org/catrisk/ontology#>

INSERT {
        ?eventloss cro:isModeledLoss ?isModeledLoss .
    }

WHERE {       
       ?eventloss cro:loss_ylpr ?lossylpr .
       ?lossylpr cro:ylpr_tag ?tag .
          ?eventloss cro:eventLossOf ?event .
          ?event cro:eventName ?eventname .
          ?eventloss cro:hasLossCountry ?losscountry .
          ?losscountry cro:adminBoundaryCode ?countrycode .
          ?eventloss cro:hasGrossIncurredLoss ?grloss .

OPTIONAL {
  ?mloss cro:model_ylpr ?modelylpr .
  ?modelylpr cro:ylpr_tag ?tag .
  ?mloss cro:hasCatModel ?catmodel .
  ?catmodel cro:hasModelDomainRegion ?modeldomain .
    BIND("true"^^xsd:boolean AS ?modelingResultsExist)
}

OPTIONAL {
    ?losscountry cro:inCatDomainOf ?modeldomain .
    BIND("true"^^xsd:boolean AS ?losscountryInDomain)

}

BIND(
    IF(COALESCE(?modelingResultsExist, false) && COALESCE(?losscountryInDomain, false), true, false) AS ?isModeledLoss
  )

}
"""

g.update(setModeledLossStatus)
g.serialize(destination='example_knowledge_graph.ttl', format='turtle')


objectpropertylist = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cro: <https://w3id.org/catrisk/ontology#>

SELECT ?sourceclass ?property ?targetclass ?label ?description
WHERE {
  ?property a rdf:Property .
  ?property rdfs:domain ?sourceclass .
  ?property rdfs:range ?targetclass .
  
  FILTER(STRSTARTS(STR(?property), STR(cro:)))

  OPTIONAL { ?property rdfs:label ?label . }
  OPTIONAL { ?property rdfs:comment ?description . }
}
ORDER BY ?sourceclass
"""

objectproperty_df = execute_sparql(g,objectpropertylist)


objectproperty_df["Source"] = objectproperty_df['sourceclass'].apply(lambda x: x.split('#')[1])
objectproperty_df["Property"] = objectproperty_df['property'].apply(lambda x: x.split('#')[1])
objectproperty_df["Target"] = objectproperty_df['targetclass'].apply(lambda x: x.split('#')[1])

classlist = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX cro: <https://w3id.org/catrisk/ontology#>

SELECT DISTINCT ?class ?label ?description
WHERE {
  {
    ?class a owl:Class .
  }
  UNION
  {
    ?class a rdfs:Class .
  }
  UNION
  {
    ?class rdfs:subClassOf ?superclass .
  }
  
  FILTER(STRSTARTS(STR(?class), STR(cro:)))
  OPTIONAL { ?class rdfs:label ?label . }
  OPTIONAL { ?class rdfs:comment ?description . }
}
"""
classes_df = execute_sparql(g,classlist)
classes_df['DefinedClass'] = classes_df['class'].apply(lambda x: x.split('#')[1])

writer = pd.ExcelWriter("ontology_summary.xlsx",engine="openpyxl")
objectproperty_df.to_excel(writer, sheet_name="property", index=False)
classes_df.to_excel(writer, sheet_name="class", index=False)
writer.close()