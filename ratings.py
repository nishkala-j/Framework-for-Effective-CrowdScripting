from bs4 import BeautifulSoup
import urllib2
import re
import nltk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from SPARQLWrapper import SPARQLWrapper, JSON


def removeNonAscii(s): 
	return "".join(i for i in s if ord(i)<128)

def getKeyWords(mystr):
	sparql= SPARQLWrapper("http://dbpedia.org/sparql")
	mystr=re.sub("[^a-zA-Z0-9 ]",'',mystr)
	words= nltk.word_tokenize(mystr)
	tagged= nltk.pos_tag(words)
	keys = [word for (word, tag) in tagged if (tag=='NN' or tag=='NNS' or tag=='NNP')]
	newkeys=[]
	for key in keys:
		if key=='apple':
			key='Apple Inc.'
		mykeys=[]
		query = u"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT * WHERE {?x rdfs:label '"+key+"' @en. ?x dbpedia-owl:abstract ?abstract.  FILTER (LANG(?abstract) = 'en')}"
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
				cont = abst[0]['abstract']['value']
				#cont=re.sub("[^a-zA-Z0-9 ]",'',cont)
				words= nltk.word_tokenize(cont)
				tagged= nltk.pos_tag(words)
				print 'for key: ',key
				mykeys = [word for (word, tag) in tagged if (tag=='NN' or tag=='NNS' or tag=='NNP')]
				print mykeys
				newkeys.extend(mykeys)
	keys.extend(newkeys)
	return keys


def rateBlog(myurl):
	try:
		url=urllib2.urlopen('https://'+myurl)
	except urllib2.URLError:
		print 'cannot open'
	else:
		content=url.read()
		soup= BeautifulSoup(content)
		#posts= soup.findAll("h3","post-title entry-title")
		posts=soup.findAll("div","post-outer")
		print 'No of posts: ',len(posts)
		for post in posts:
			try:
				c=post.find("h3","post-title entry-title").find("a").string
			except AttributeError:
				print 'One post has no title'
			else:
				c= removeNonAscii(c)
				print 'title',c
				cont = post.find(attrs={'itemprop':'description articleBody'})
				cont= str(cont)
				cont = re.sub("<!--.*?-->",'',cont)
				cont = re.sub("<.*?>",'',cont)
				cont = re.sub("&nbsp;",'',cont)
				'''
				#cont = re.sub(" \d+|\.|\!|\;|\(|\)|\:|\*|\,|\-|\_",'',cont)
				cont = re.sub("[^a-zA-Z0-9 ]",'',cont)
				#cont = removeNonAscii(cont)
				words= nltk.word_tokenize(cont)
				tagged= nltk.pos_tag(words)
				keys = [word for (word, tag) in tagged if (tag=='NN' or tag=='NNS' or tag=='NNP')]
				#print re.split("\W+", cont)
				'''
				getKeyWords(cont)
				
				

s='ilovenewsforapple.blogspot.in'
s='crazylibidolittlegirl.blogspot.in/'
rateBlog(s)