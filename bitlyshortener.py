##bit.ly link shortener

import urllib
import requests
import os
from os.path import expanduser
import json
HOME = expanduser("~")

def load_api_key():
	global api_key
	global username
	f = open(os.getenv("HOME")+'/.boxlinux', 'r')
	settings = json.loads(f.read())
	api_key = settings['bitly']
	username = settings['username']
	return [api_key, username]

def shorten_url(longUrl):
	longUrl = urllib.quote_plus(longUrl)
	load_api_key()
	url = "https://api-ssl.bitly.com/v3/shorten?longUrl="+longUrl+"&login="+username+"&apiKey="+api_key
	r = requests.get(url)
	rtrnval = json.loads(r.content)
	#this is quick and dirty, it will break if any changes are made to the bitly API
	rtrnval = json.loads(json.dumps(rtrnval['data']))
	return rtrnval['url']