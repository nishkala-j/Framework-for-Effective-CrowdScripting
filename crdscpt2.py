from bs4 import BeautifulSoup
import urllib2
import re
import gdata
from pymongo import MongoClient
from sentiwordnet import SentiWordNetCorpusReader, SentiSynset
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn 
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
import chardet

def detect_lang(text):
    try: 
        text=unicode(text)
        encoding = chardet.detect(text)
    except UnicodeDecodeError:
        print 'unicode error'
        return 'not ascii'
    except IndexError:
    	return "index error" #special chars
    else: 
        if encoding['encoding'] == 'ascii':
            languages_ratios={}
            tokens=wordpunct_tokenize(text)
            words = [word.lower() for word in tokens]

            for language in stopwords.fileids():
                stopwords_set = set(stopwords.words(language))
                words_set = set(words)
                common_elements = words_set.intersection(stopwords_set)
                languages_ratios[language]= len(common_elements)

            #print languages_ratios
            most_rated_language = max(languages_ratios, key=languages_ratios.get)
            if languages_ratios[most_rated_language] == languages_ratios["english"]:
                return 'english'
            else:
                return most_rated_language
        else:
            return "Not ascii"

def pos_or_neg(myword):
	global swn
	if(detect_lang(myword)=="english"):
		try:
			tagger=pos_tag(word_tokenize(myword))
		except TypeError:
			print 'typeError'
			return False
		else:
			doc_pos_score=0
			doc_neg_score=0
			for key,value in tagger:
				# Check for adjectives, nouns from adjectives and adverbs
				#print key,value
				if (value == 'NNS'): #plural nouns
					if ( wn.synsets(key)== []):
						return False
				if (value=='JJ' or value=='RB'): #adjectives and adverbs
					word=key
					try:
						syn = swn.senti_synsets(word,"a")
						if syn != []:
							syn=syn[0]
						else:
							syn= swn.senti_synsets(word,"r")
							if syn!=[]:
								syn=syn[0]
							else:
								syn=swn.senti_synsets(word,"n")[0]
					except IndexError:
						print 'IndexError for word'
						return False
					else:
						doc_pos_score=doc_pos_score+syn.pos_score
						doc_neg_score=doc_neg_score+syn.neg_score
			if (doc_pos_score >= doc_neg_score):
				return True
			else:
				return False
	else:
		return False


def getScripters():
	global user_url
	global count
	url= urllib2.urlopen(user_url)
	content= url.read()
	soup= BeautifulSoup(content)
	links= soup.findAll("a",href=True)
	for a in links:
		link=a['href']
		if re.findall('blogger.com/profile/',link):
			print "Found the URL: ", link
			uid=re.search('blogger\.com/profile/(\d+)',link).group(1)
			entry= db.scripters.find_one({"profile":link})
			if entry==None:
				user={"profile":link, "scripter_id":uid, "valid":"true"}
				coll.insert(user)
				count= count+1
				print 'insertion complete record no: ',count
		if re.findall('blogger.com/profile-find',link) and a.string=='Next':
			print 'Next Url: ',link
			user_url=link
	if count<100:
		getScripters()


def getBlogsnPosts():
	global db
	users=db.scripters.find({"username":{"$exists":False}})
	for user in users:
		if user["valid"]=="true":
			myurl= user['profile']
			print myurl
			try:
				url= urllib2.urlopen(myurl)
			except urllib2.URLError:
				print 'cannot open'
				db.scripters.update({"_id":user["_id"]},{'$set':{"valid":"false"}})
			else:
				content= url.read()
				soup= BeautifulSoup(content)
				username= soup.find("div","vcard").find("h1").string
				email=''
				userblogs=[]
				print username
				links= soup.findAll("li","sidebar-item")	
				for at in links:
					if at.string:
						b=unicode(at.string)
						if re.findall('printEmail',b):
							email=re.search('printEmail\(\"blog(.*?)\.biz', b).group(1)
							print email
							if email=="":
								print "no email hence break- must not check for blogs and posts"
								break
						else:
							ps= at.find_parent("ul").find_previous_sibling("h2")
							if ps:
								if ps.string == 'My blogs':
									print b," : ",at.a['href']
									blog=at.a['href']
									if(pos_or_neg(b)):
										#userblogs.append(b)
										if re.findall('blogspot',blog):
											g= re.search('http\://(.*?)/',blog).group(1)
											print g
											blog='https://pes-spartans.appspot.com/'+g
											#blog='https://'+g
											userblogs.append(g)
				if(userblogs!= [] and email!=""):
					db.scripters.update({"_id":user["_id"]},{'$set':{"username":username,"email":email,"blogs":userblogs}})
					print 'updated user '
				else:
					print 'Not used since not in english or no email provided'
					db.scripters.update({"_id":user["_id"]},{'$set':{"valid":"false"}})


client= MongoClient()
db= client.crowdscripting2
coll = db.scripters
swn_filename= 'SentiWordNet_3.0.0_20130122.txt'
swn= SentiWordNetCorpusReader(swn_filename)
#user_url='http://www.blogger.com/profile-find.g?t=l&loc0=US&loc1=california'
user_url='https://www.blogger.com/profile-find.g?t=i&q=google'
count=0
getScripters()
#getBlogsnPosts()

