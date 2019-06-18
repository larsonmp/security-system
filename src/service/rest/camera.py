from datetime import datetime
from picamera import PiCamera

class Camera(object):
	def __init__(self, id=0):
		super().__init__()
		self._id = id
		self._camera = PiCamera(resolution=(2592, 1944))

	@property
	def id(self):
		return self._id
	
	@property
	def info(self):
		return {
			'id': self._id,
			'resolution': self._camera.resolution,
			'frame-rate': str(self._camera.framerate)
		}
	
	def capture(self, count=1):
		return self._capture_to_file(count)

	def _capture_to_file(self, count):
		filepaths = []
		for iteration in range(count):
			filepaths.append(datetime.now().strftime('/tmp/image_%FT%H.%M.%S.jpg'))
			self._camera.capture(filepaths[iteration])
		return filepaths
	
	def close(self):
		self._camera.close()
	
	def __str__(self):
		return str({'id': self.id, 'info': self.info})
	
	def __repr__(self):
		return str({'id': self.id, 'info': self.info})


