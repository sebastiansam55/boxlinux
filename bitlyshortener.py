##bit.ly link shortener

import requests

global apikey
apikey = <>

global auth_token

def get_auth_token():
	global auth_token
	r = requests.request(url, 