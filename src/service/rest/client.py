from io import BytesIO
from json import dumps
from mimetypes import guess_all_extensions
from os.path import join
from requests import delete, get, post
from tempfile import gettempdir

def guess_extension(mimetype):
	#there's an oddity on raspbian wherein guess_extension is non-deterministic
	return sorted(guess_all_extensions(mimetype))[-1]

class Client(object):
	def __init__(self, protocol='http', host='localhost', port=80):
		super().__init__()
		self._base_url = '{}://{}:{}'.format(protocol, host, port)
	
	def capture_snapshot(self, cid=0, count=1):
		url = '{base_url}/camera/{cid:d}/snapshot'.format(base_url=self._base_url, cid=cid)
		body = {
			'count': count
		}
		headers = {
			'Content-Type': 'application/json'
		}
		return post(url, headers=headers, data=dumps(body)).json()
	
	def delete_snapshot(self, sid, cid=0):
		url = '{base_url}/camera/{cid:d}/snapshot/{sid}'.format(base_url=self._base_url, cid=cid, sid=sid)
		return delete(url)
	
	def get_snapshot(self, sid, cid=0):
		url = '{base_url}/camera/{cid:d}/snapshot/{sid}'.format(base_url=self._base_url, cid=cid, sid=sid)
		response = get(url)
		extension = guess_extension(response.headers['content-type'])
		filepath = join(gettempdir(), sid + extension)
		with open(filepath, 'wb') as fp:
			fp.write(BytesIO(response.content).read())
		return filepath
	
	def get_all_snapshot_ids(self, cid=0):
		url = '{base_url}/camera/{cid:d}/snapshot'.format(base_url=self._base_url, cid=cid)
		response = get(url)
		return response.json()
