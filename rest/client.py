#!/usr/bin/env python

from json import dumps
from requests import get, post

class Client(object):
	def __init__(self):
		super(Client, self).__init__()
		self._url = 'http://localhost:10082/camera/{cid:d}/snapshot'
	
	def capture(self, cid=0, count=1):
		body = {
			'count': count
		}
		headers = {
			'Content-Type': 'application/json'
		}
		return post(self._url.format(cid=cid), headers=headers, data=dumps(body)).json()

