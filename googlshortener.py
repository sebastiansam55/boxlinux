#!/usr/bin/env python

import requests
import json


def shorten_url(longURL):
	url = "https://www.googleapis.com/urlshortener/v1/url"
	headers = {'Content-type': 'application/json'}
	data = {'longUrl': longURL}
	r = requests.post(url=url, headers=headers, data=json.dumps(data))
	return json.loads(r.content)['id']