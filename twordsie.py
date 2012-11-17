import os
from flask import render_template
from flask import Flask
from flask import url_for
from flask import request
from os import environ
import urllib2
import urllib
import json
from bs4 import BeautifulSoup
import time
import datetime
from datetime import timedelta
from datetime import date
import simplejson
import gviz_api


from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


app = Flask(__name__)

@app.route('/')
def main():
	
	
	return render_template("index.html")


@app.route('/results',methods=['POST', 'GET'])
def gettweets():	
	
	username = request.args.get('username')
	
	data = cache.get(username)
	if data is not None:
		return render_template("results.html",data=json.dumps(data))
		
	url = 'http://api.twitter.com/1/statuses/user_timeline.json?screen_name='+username+'&count=200'
	content = urllib2.urlopen(url)
	tweets = json.loads(content.read())
	
	data = {'cols': [{'type': 'string', 'label': 'Tweets'}],
			'rows': [{'c': [{'v': tweet["text"]}]} for tweet in tweets]}


	cache.set(username, data, timeout=20 * 60)

	return render_template("results.html",data=json.dumps(data))
	

	
if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)

