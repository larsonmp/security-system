#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from logging import DEBUG, INFO, WARNING, basicConfig, getLogger
from logging.config import dictConfig
from threading import Lock, Thread, Timer
from time import sleep
from traceback import print_exc
from yaml import safe_load

import service.gpio as gpio
from service.mail import MailConfiguration, Mailer
from service.rest import Client


class Controller(object):
	def __init__(self):
		super().__init__()
		self._client = Client(port=10082)
		cfg = MailConfiguration('config/mail.yaml', 'gmail')
		self._mailer = Mailer(cfg.address, cfg.username, cfg.password, cfg.host, cfg.port)
		self._recipients = [cfg.address]
		self._threads = []
	
	def capture_image(self):
		sids = self._client.capture_snapshot(count=2)
		filepaths = [self._client.get_snapshot(sid) for sid in sids]
		thread = Thread(target=self._mailer.send, args=(self._recipients, 'camera activity', datetime.now().strftime('date: %FT%T'), filepaths))
		thread.start()
		self._threads.append(thread)
	
	def get_image_ids(self):
		return self._client.get_all_snapshot_ids()
	
	def close(self):
		for thread in self._threads:
			thread.join()
		self._mailer.close()


class CameraAdapter(gpio.Output):
	def __init__(self, controller):
		super().__init__()
		self._controller = controller
		self._timer = None
		self._lock = Lock()
		self._logger = getLogger('camera')
	
	def start(self):
		if self.lock():
			self._timer = Timer(0.5, self.unlock)
			self._timer.start()
			self._controller.capture_image()
		else:
			self._logger.warning('couldn\'t acquire lock, skipping photo')
	
	def lock(self):
		return self._lock.acquire(False)
	
	def unlock(self):
		self._lock.release()


if __name__=='__main__':
	parser = ArgumentParser(description='detect motion, capture image, transmit image')
	parser.add_argument('-l', '--logging-config', metavar="PATH", default='config/logging.yaml', help='path to logging configuration file')
	args = parser.parse_args()
	
	try:
		with open(args.logging_config) as fp:
			config = safe_load(fp.read())
			dictConfig(config)
	except RuntimeError as e:
		print_exc()
		basicConfig(filename=datetime.now().strftime('driver_%Y-%m-%dT%H.%M.%S%z.log'), level=DEBUG, format='%(asctime)-15s %(message)s')
	logger = getLogger('driver')
	
	controller = Controller()
	
	try:
		gpio.initialize()
		detector = gpio.MotionDetector(37)
		detector.add_output(gpio.Buzzer(7))
		detector.add_output(gpio.LED(35))
		detector.add_output(gpio.Logger())
		detector.add_output(CameraAdapter(controller))
		while True:
			sleep(5)
	except KeyboardInterrupt:
		pass
	finally:
		gpio.cleanup()
	
	controller.close()

