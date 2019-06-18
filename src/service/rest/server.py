from atexit import register
from flask import Flask, jsonify, request, send_file
from io import BytesIO
from os import remove
from os.path import basename
from sys import stdout, stderr
from tinydb import Query, TinyDB
from uuid import uuid4 as random_uuid

from .camera import Camera
from service.i2c import Thermometer, initialize

app = Flask(__name__.split('.')[0])
initialize()

class ImageRepository(object):
	def __init__(self, filepath='db.json'):
		super().__init__()
		self._db = TinyDB(filepath)
		self._table = self._db.table('snapshot', cache_size=32)
	
	def persist(self, filepaths):
		for filepath in filepaths:
			sid = str(random_uuid())
			self._table.insert({'id': sid, 'filepath': filepath})
			yield sid
	
	def retrieve(self, cid, sid):
		filepath = self._table.get(Query().id == str(sid)).get('filepath')
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
		super().__init__()
		self._cameras = {
			0: Camera(0)
		}
		self._sensors = {
			0: Thermometer.new()
		}
		register(self.close)
	
	@property
	def cameras(self):
		return self._cameras
	
	@property
	def sensors(self):
		return self._sensors

	def close(self):
		for camera in self._cameras.values():
			camera.close()
		for sensor in self._sensors.values():
			sensor.close()

resources = Resources()
img_repo = ImageRepository()

stderr.write('resources.cameras: {}\n'.format(resources.cameras))

@app.route('/camera')
def camera_list():
	return jsonify(list(resources.cameras.keys()))

@app.route('/camera/<int:cid>/info')
def camera_info(cid):
	return jsonify(resources.cameras.get(cid).info)

@app.route('/camera/<int:cid>/snapshot', methods=['GET', 'POST'])
def camera_capture(cid, count=1):
	stderr.write('request: {}\n'.format(request))
	if request.method == 'POST':
		req = request.get_json() or {}
		stderr.write('cam: {}\n'.format(resources.cameras))
		stderr.write('json: {}\n'.format(req))
		paths = resources.cameras.get(cid).capture(req.get('count', 1))
		return jsonify(list(img_repo.persist(paths)))
	else:
		results = img_repo.get_all_ids()
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

@app.route('/system/python')
def python():
	import platform
	return jsonify({'version': platform.python_version()})

@app.route('/sensor')
def sensor_list():
	return jsonify(list(resources.sensors.keys()))

@app.route('/sensor/<int:sid>', methods=['GET'])
def sensor(sid):
	unit = request.args.get('unit')
	sensor = resources.sensors.get(sid)
	reading = sensor.read(unit)
	return jsonify({
		'value': reading.value,
		'unit': reading.unit
	})

@app.route('/sensor/<int:sid>/info', methods=['GET'])
def sensor_info(sid):
	sensor = resources.sensors.get(sid)
	return jsonify({
		'type': sensor.type
	})

@app.route('/sensor/<int:sid>/history', methods=['GET'])
def sensor_history(sid):
	year = request.args.get('year')
	pass #return list of measurements (weekly averages for year, daily averages for month, hourly readings for day?)

@app.route('/sensor/<int:id>/history', methods=['DELETE'])
def sensor_history_rm(sid):
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

