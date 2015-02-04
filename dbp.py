from SPARQLWrapper import SPARQLWrapper, JSON

sparql= SPARQLWrapper("http://dbpedia.org/sparql")
query = u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * 
WHERE {?x rdfs:label 'New York' @en. ?x dbpedia-owl:abstract ?abstract. OPTIONAL { ?x dbpedia-owl:areaTotal ?areaTotal. } OPTIONAL { ?x dbpprop:governor ?governor. } OPTIONAL { ?x dbpprop:birthPlace ?birthPlace. } FILTER (LANG(?abstract) = 'en')}"""

query = u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * 
WHERE {?x rdfs:label 'Apple' @en. ?x dbpedia-owl:abstract ?abstract.  FILTER (LANG(?abstract) = 'en')}"""

query =u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?syn
WHERE { 
  {
   ?disPage dbpedia-owl:wikiPageDisambiguates <http://dbpedia.org/resource/iphone> .
   ?disPage dbpedia-owl:wikiPageDisambiguates ?syn . 
  } 
  UNION
  {
   <http://dbpedia.org/resource/Less> dbpedia-owl:wikiPageDisambiguates ?syn .
  }
}
"""
query = u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * 
WHERE {?x rdfs:label 'Apple Inc.' @en. ?x dbpedia-owl:abstract ?abstract.  FILTER (LANG(?abstract) = 'en')}"""
sparql.setQuery(query)

sparql.setReturnFormat(JSON)
try:
	results = sparql.query().convert()
except urllib2.HTTPError:
	print 'Cannot open'
else:
	#print results
	abst=results['results']['bindings']
	if abst!=[]:
		print abst[0]['abstract']['value']