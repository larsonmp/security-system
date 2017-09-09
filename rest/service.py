#!/usr/bin/env python

from atexit import register
from flask import Flask, jsonify, request
from camera import Camera

app = Flask(__name__.split('.')[0])


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

@app.route('/camera')
def camera_list():
	return jsonify(resources.cameras.keys())

@app.route('/camera/<int:cid>/info')
def camera_info(cid):
	return jsonify(resources.cameras.get(cid).info())

@app.route('/camera/<int:cid>/snapshot', methods=['POST'])
def camera_capture(cid, count=1):
	req = request.get_json()
	#TODO: return snapshot-id (sid)
	return jsonify(resources.cameras.get(cid).capture(req.get('count', 1)))

@app.route('/camera/<int:cid>/snapshot/<int:sid>')
def camera_get_snapshot(cid, sid):
	pass #return image binary

@app.route('/camera/<int:cid>/snapshot/<int:sid>', methods=['DELETE'])
def camera_rm_snapshot(cid, sid):
	pass

@app.route('/camera/<int:cid>/snapshot/<int:sid>/info')
def camera_snapshot_info(cid, sid):
	pass #return snapshot resolution, encoding (dict)

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
