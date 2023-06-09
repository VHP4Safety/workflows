
###############################################################################
### Imporing necessary modules.

import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from pyvis.network import Network
from IPython.display import display, HTML, IFrame
import urllib
import simplejson as json
import pandas as pd
import re
import requests
import warnings
import statistics
from edelweiss_data import API, QueryExpression as Q


###############################################################################
## Define the AOP of Interest

AOPid = "37"

## Set Service URLs

# SPARQL endpoint URLs
aopwikisparql=SPARQLWrapper("http://aopwiki.cloud.vhp4safety.nl/sparql/")
aopdbsparql=SPARQLWrapper("http://aopdb.rdf.bigcat-bioinformatics.org/sparql/")
wikipathwayssparql = SPARQLWrapper("http://sparql.wikipathways.org/sparql/")

# ChemIdConvert URL
chemidconvert = 'https://chemidconvert.cloud.douglasconnect.com/v1/'

# BridgeDB base URL
bridgedb = "http://bridgedb.cloud.vhp4safety.nl/"
# bridgedb = "http://81.169.225.178:8084/"
# bridgedb = "http://81.169.225.178:8086/"
# bridgedb = "http://81.169.225.178:8088/"

# EdelweissData API URL
edelweiss_api_url = 'https://api.staging.kit.cloud.douglasconnect.com'


## AOP-Wiki RDF

# Define all variables as ontology terms present in AOP-Wiki RDF
title = 'dc:title'
webpage = 'foaf:page'
creator = 'dc:creator'
abstract = 'dcterms:abstract'
key_event = 'aopo:has_key_event'
molecular_initiating_event = 'aopo:has_molecular_initiating_event'
adverse_outcome = 'aopo:has_adverse_outcome'
key_event_relationship = 'aopo:has_key_event_relationship'
stressor = 'ncit:C54571'

# Create the list of all terms of interest
listofterms = [title,webpage,creator,abstract,key_event,molecular_initiating_event,adverse_outcome,key_event_relationship,stressor]

#Initiate the DataFrame
AOPinfo = pd.DataFrame(columns=['Properties'], index = [list(listofterms)])

#Query all terms of interest in the selected AOP
for term in listofterms:
    sparqlquery = '''
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    SELECT (group_concat(distinct ?item;separator=";") as ?items)
    WHERE{
    ?AOP_URI a aopo:AdverseOutcomePathway;'''+term+''' ?item.
    FILTER (?AOP_URI = aop:'''+AOPid +''')}
    '''
    aopwikisparql.setQuery(sparqlquery)
    aopwikisparql.setReturnFormat(JSON)  
    results = aopwikisparql.query().convert()
    for result in results["results"]["bindings"]:
        if 'identifiers.org' in result["items"]["value"]:
            AOPinfo.at[term,'Properties'] = ', '.join(result["items"]["value"].split(';'))
        else:
            AOPinfo.at[term,'Properties'] = result["items"]["value"]

display(AOPinfo)


## Generating AOP Network

Key_Events = str(AOPinfo.iat[4,0]).split(', ')

# A network of pathways can be built by searching other pathways where the key 
# events in our AOP exist. Here, we are searching for other AOPs that include 
# the KEs in our pathway.
for Key_Event in Key_Events:
    sparqlquery = '''
    SELECT ?MIE_ID ?KE_ID ?AO_ID ?KER_ID ?KE_Title
    WHERE{
    ?KE_URI a aopo:KeyEvent; dcterms:isPartOf ?AOP_URI.
    ?AOP_URI aopo:has_key_event ?KE_URI2; aopo:has_molecular_initiating_event ?MIE_URI; aopo:has_adverse_outcome ?AO_URI; aopo:has_key_event_relationship ?KER_URI.
    ?KE_URI2 rdfs:label ?KE_ID; dc:title ?KE_Title. 
    ?MIE_URI rdfs:label ?MIE_ID.
    ?AO_URI rdfs:label ?AO_ID.
    ?KER_URI rdfs:label ?KER_ID.    
    FILTER (?KE_URI = <'''+Key_Event+'''>)}
    '''
    aopwikisparql.setQuery(sparqlquery)
    aopwikisparql.setReturnFormat(JSON)  
    results = aopwikisparql.query().convert()

    MIEs = set([])
    KEs = set([])
    KEtitle = {}
    AOs = set([])
    KERs = set([])
    for result in results["results"]["bindings"]:
        MIEs.add(result["MIE_ID"]["value"])
        AOs.add(result["AO_ID"]["value"])
        KEs.add(result["KE_ID"]["value"])
        KERs.add(result["KER_ID"]["value"])
        KEtitle[result["KE_ID"]["value"]]=result["KE_Title"]["value"]

# Listing all intermediate KEs that are not MIEs or AOs. 
KEsIntermediate = []
for item in KEs:
    if item not in MIEs and item not in AOs:
        KEsIntermediate.append(item) 

# Initiating the network figure
net = Network(height="100%", width="100%")

# Adding nodes for Molecular Initiating Events, Key Events, and Adverse 
# Outcomes to the network figure
for MIE in MIEs:
    net.add_node(MIE, color = 'lightgreen', size = 50, shape = 'circle', font = '20px arial black', title = KEtitle[MIE])
for KE in KEsIntermediate:
    net.add_node(KE, color = 'khaki', size = 50, shape = 'circle', font = '20px arial black', title = KEtitle[KE])
for AO in AOs:
    net.add_node(AO, color = 'salmon', size = 50, shape = 'circle', font = '20px arial black', title = KEtitle[AO])

# Adding all Key Event Relationships to the network figure after querying all 
# KERs for all KEs in AOP-Wiki RDF
for KER in KERs:
    sparqlquery = '''
    SELECT ?KE_UP_ID ?KE_DOWN_ID 
    WHERE{
    ?KER_URI a aopo:KeyEventRelationship; rdfs:label ?KER_ID; aopo:has_upstream_key_event ?KE_UP_URI; aopo:has_downstream_key_event ?KE_DOWN_URI.
    ?KE_UP_URI rdfs:label ?KE_UP_ID.
    ?KE_DOWN_URI rdfs:label ?KE_DOWN_ID.
    FILTER (?KER_ID = "'''+KER+'''")}
    '''
    aopwikisparql.setQuery(sparqlquery)
    aopwikisparql.setReturnFormat(JSON)  
    results = aopwikisparql.query().convert()
    for result in results["results"]["bindings"]:
        net.add_edge(result["KE_UP_ID"]["value"],result["KE_DOWN_ID"]["value"],width = 2, color = 'black',label = KER, arrows = 'to')

net.show('mygraph.html')

IFrame(src='./mygraph.html', width=700, height=600)


# Querying all chemicals that are part of the selected AOP
sparqlquery = '''
SELECT ?CAS_ID (fn:substring(?CompTox,33) as ?CompTox_ID) ?Chemical_name
WHERE{
?AOP_URI a aopo:AdverseOutcomePathway; nci:C54571 ?Stressor.
?Stressor aopo:has_chemical_entity ?Chemical.
?Chemical cheminf:000446 ?CAS_ID; dc:title ?Chemical_name.
OPTIONAL {?Chemical cheminf:000568 ?CompTox.}
FILTER (?AOP_URI = aop:'''+AOPid +''')}
'''
aopwikisparql.setQuery(sparqlquery)
aopwikisparql.setReturnFormat(JSON)  
results = aopwikisparql.query().convert()

Chemical_names = {}
CompTox = {}

for result in results["results"]["bindings"]:
    try: CompTox[result["CAS_ID"]["value"]] =result["CompTox_ID"]["value"]
    except: pass
for result in results["results"]["bindings"]:
    try: Chemical_names[result["CAS_ID"]["value"]] =result["Chemical_name"]["value"]
    except: pass

Chemdata = pd.DataFrame(columns=['Chemical_name','CAS_ID','CompTox_ID'])
for CAS_ID in Chemical_names:
    Chemdata = Chemdata.append({
        'Chemical_name' : Chemical_names[CAS_ID],
        'CAS_ID'        : CAS_ID,
        'CompTox_ID'    : CompTox[CAS_ID],
        }, ignore_index=True)

display(Chemdata)   # These are all the chemicals included

compounds = []
for index, row in Chemdata.iterrows():
    compounds.append(row['CAS_ID'])

compounds


## ChemIdConvert

compoundstable = pd.DataFrame(columns=['CAS_ID', 'Image', 'Smiles', 'InChIKey'])

# Fill "compounds" with the "smiles" by the compound name.
for compound in compounds:
    smiles = requests.get(chemidconvert + 'cas/to/smiles', params={'cas': compound}).json()['smiles']
    inchikey = requests.get(chemidconvert + 'smiles/to/inchikey', params={'smiles': smiles}).json()['inchikey']
    compoundstable = compoundstable.append({'CAS_ID': compound, 'Image': smiles, 'Smiles': smiles, 'InChIKey' : inchikey}, ignore_index=True)

def smiles_to_image_html(smiles):  # "smiles" shadows "smiles" from outer scope, use this function only in "to_html().
    """Gets for each smile the image, in HTML.
    :param smiles: Takes the “smiles” form “compounds”.
    :return: The HTML code for the image of the given smiles.
    """
    return '<img style="width:150px" src="' + chemidconvert+'asSvg?smiles='+urllib.parse.quote(smiles)+'"/>'


# Return a HTML table of "compounds", after "compounds" is fill by "smiles_to_image_html".
HTML(compoundstable.to_html(escape=False, formatters=dict(Image=smiles_to_image_html)))


## AOP-DB RDF

Key_Events = str(AOPinfo.iat[4,0]).split(', ')
Genes = []

# Getting AOPs from the KEs.
for Key_Event in Key_Events:
    sparqlquery = '''
    SELECT DISTINCT ?KE_ID ?Entrez_ID WHERE{
    ?KE_URI edam:data_1027 ?Entrez_URI. ?Entrez_URI edam:data_1027 ?Entrez_ID.
    FILTER (?KE_URI = <'''+Key_Event +'''>)}
    '''
    aopdbsparql.setQuery(sparqlquery)
    aopdbsparql.setReturnFormat(JSON)  
    results = aopdbsparql.query().convert()
    for result in results["results"]["bindings"]:
        Genes.append(result["Entrez_ID"]["value"])

print(Genes)


## BridgeDb to Map Identifiers

inputdatasource = 'L'
outputdatasource = ['H','En']
Species = ['Human','Mouse','Rat']

Mappings = {}
HGNC = []

for source in outputdatasource:
    Mappings[source] = []
    for Entrez in Genes:
        for species in Species:
            allmappings = re.split('\t|\n', requests.get(bridgedb + species + '/xrefs/' + inputdatasource + '/' + Entrez + '?dataSource='+source).text)
            if allmappings[0] != '':
                break
        Mappings[source].append(allmappings[0])

ids = {}
for source in Mappings:
    ids[source]=[]
    for identifier in Mappings[source]:
        ids[source].append(identifier)

GenesTable = pd.DataFrame(columns=['Entrez','HGNC','Ensembl'])
GenesTable['Entrez'] = Genes
GenesTable['HGNC'] = ids['H']
GenesTable['Ensembl'] = ids['En']

display(GenesTable)

