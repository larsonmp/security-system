#!/usr/bin/env python

from atexit import register
from flask import Flask, jsonify, request, send_file
from io import BytesIO
from os import remove
from os.path import basename
from tinydb import Query, TinyDB
from uuid import uuid4 as random_uuid

from camera import Camera

app = Flask(__name__.split('.')[0])


class ImageRepository(object):
	def __init__(self, filepath='db.json'):
		super(ImageRepository, self).__init__()
		self._db = TinyDB(filepath)
		self._table = self._db.table('snapshot', cache_size=32)
	
	def persist(self, filepaths):
		for filepath in filepaths:
			sid = str(random_uuid())
			self._table.insert({'id': sid, 'filepath': filepath})
			yield sid
	
	def retrieve(self, cid, sid):
		filepath = self._table.get(Query().id == str(sid)).get('filepath')
		print filepath
		data = None
		with open(filepath, 'rb') as fp:
			data = BytesIO(fp.read())
		return basename(filepath), data
	
	def delete(self, cid, sid):
		record = self._table.get(Query().id == str(sid))
		self._table.remove(eid=record.eid)
		remove(record.get('filepath'))
	
	def get_all_ids(self):
		return [record.get('id') for record in self._table.all()]


class Resources(object):
	def __init__(self):
		super(Resources, self).__init__()
		self._cameras = {
			0: Camera(0)
		}
		register(self.close)
	
	@property
	def cameras(self):
		return self._cameras

	def close(self):
		for camera in self._cameras.values():
			camera.close()

resources = Resources()
img_repo = ImageRepository()

@app.route('/camera')
def camera_list():
	return jsonify(resources.cameras.keys())

@app.route('/camera/<int:cid>/info')
def camera_info(cid):
	return jsonify(resources.cameras.get(cid).info())

@app.route('/camera/<int:cid>/snapshot', methods=['GET', 'POST'])
def camera_capture(cid, count=1):
	if request.method == 'POST':
		req = request.get_json()
		paths = resources.cameras.get(cid).capture(req.get('count', 1))
		return jsonify(list(img_repo.persist(paths)))
	else:
		results = img_repo.get_all_ids()
		print results
		return jsonify(results)

@app.route('/camera/<int:cid>/snapshot/<uuid:sid>')
def camera_get_snapshot(cid, sid):
	filename, data = img_repo.retrieve(cid, sid)
	return send_file(data, attachment_filename=filename, mimetype='image/jpeg', as_attachment=True)

@app.route('/camera/<int:cid>/snapshot/<uuid:sid>', methods=['DELETE'])
def camera_rm_snapshot(cid, sid):
	img_repo.delete(cid, sid)
	return jsonify({'success': True})

@app.route('/camera/<int:cid>/snapshot/<uuid:sid>/info')
def camera_snapshot_info(cid, sid):
	#TODO: EXIF
	return jsonify({'this route not yet implemented': 'sorry for the inconvenience'}), 501

@app.route('/camera/<int:cid>/stream')
def camera_stream(cid):
	pass #possible?

@app.route('/thermometer')
def thermometers():
	pass

@app.route('/thermometer/<int:id>')
def thermometer(id):
	pass #return temperature

@app.route('/thermometer/<int:id>/info')
def thermometer_info(id):
	pass #return units, accuracy? (dict)

@app.route('/thermometer/<int:id>/history')
def thermometer_history(id):
	year = request.args.get('year')
	pass #return list of measurements (weekly averages for year, daily averages for month, hourly readings for day?)

@app.route('/thermometer/<int:id>/history')
def thermometer_history_rm(id):
	pass #delete cache

@app.route('/motion/event')
def motion_events():
	pass #return dict<id, events>

@app.route('/motion/event/<int:id>')
def motion_event(id):
	pass #return event (timestamp, related sid?)

@app.route('/led')
def led():
	pass #return list of LEDs

@app.route('/led/<int:id>/status', methods=['GET', 'POST'])
def led_status(id):
	pass #get -> return on/off; post -> set on/off

@app.route('/status')
def status():
	return 'status: up'

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port='10082', threaded=True)
