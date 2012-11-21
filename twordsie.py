from __future__ import with_statement
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask import render_template
from flask import Flask
from flask import url_for
from flask import request
from os import environ
import urllib2
import json
import simplejson
import re
from collections import deque, defaultdict
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from mongoengine import *
from mongoengine import connect


from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


app = Flask(__name__)
connect('twordsie', host='mongodb://heroku:windows@alex.mongohq.com:10078/app9292233')

class User(Document):
	wordcount = ListField(ListField())
	mentions = ListField(ListField())
	username = StringField(max_length=50)

@app.route('/')
def main():
	

	return render_template("index.html")


@app.route('/results',methods=['POST', 'GET'])
def gettweets():	
	
	username = request.args.get('username')
	
	username_mentions = username+'_mentions'
	username_wordcount = username+'_wordcount'
	
#	things = cache.get_many(username, username_mentions, username_wordcount)
#	if things[0] is not None:
#		return render_template("results.html",data=json.dumps(things[0]), mentions=things[1], wordcount=things[2])
		
	url = 'http://api.twitter.com/1/statuses/user_timeline.json?screen_name='+username+'&count=200'
	content = urllib2.urlopen(url)
	tweets = json.loads(content.read())
	
	data = {'cols': [{'type': 'string', 'label': 'Tweets'}],
			'rows': [{'c': [{'v': tweet["text"]}]} for tweet in tweets]}
	
	wordcount = getwordcount(tweets)
	mentions = getmentions(tweets)
	
	
	user = User(username=username, wordcount=wordcount, mentions=mentions)
	user.save()
	
	for user in User.objects:
		theemail = str(user.username)
		
	return theemail

#	cache.set_many({username:data,username_mentions:mentions,username_wordcount:wordcount}, timeout=20 * 60)
		
#	return render_template("results.html",data=json.dumps(data), wordcount=wordcount, mentions=mentions)
	

def getmentions(tweets):

	mentions = defaultdict(int)
	
	for tweet in tweets:
		text = tweet["text"].lower()
		match = re.search(r'@\w+', text)
		if match:
			mentions[match.group()] +=1
							
	return sorted(mentions.iteritems(), key=lambda x:x[1], reverse=True)[0:10]

def getwordcount(tweets):
		
	tweetlist = []
	for tweet in tweets:
	      tweetlist.append(tweet["text"])

	tweetstr = ''.join(tweetlist)
	tweetstr = tweetstr.lower()

	fullWords = re.split('\W+',tweetstr)
	stopWords = set(['twitpic','youtu','www','instagr','gt','4sq','RT','doesn','Your','com','The','http','ly','instagr','www.','gt','bit','a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'just', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also','although','always','am','among', 'amongst', 'amoungst', 'amount',  'an', 'and', 'another', 'any','anyhow','anyone','anything','anyway', 'anywhere', 'are', 'around', 'as',  'at', 'back','be','became', 'because','become','becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom','but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven','else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'own','part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'the'])
	
	mentions = getmentions(tweets)
	mentionlist=[]	
	for item in mentions:
		mentionlist.append(str(item[0])[1:])
	mentionset = set(mentionlist)
	
	stopWords.update(mentionset)
	
	d = defaultdict(int)
	for word in fullWords:
		if word not in stopWords and len(word)>2:
			d[word] += 1

	wordcount = sorted(d.iteritems(), key = lambda t: t[1], reverse = True)[0:10]
	
	return wordcount
	
	
if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)

