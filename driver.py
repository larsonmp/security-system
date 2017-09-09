#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from logging import DEBUG, INFO, WARNING, basicConfig, getLogger
from mail import MailConfiguration, Mailer
from multiprocessing import Process, Queue
from requests import post
from threading import Lock, Thread, Timer
from time import sleep
from traceback import print_exc

import gpio
from rest import Client
from ux import TerminalInterface


class Controller(object):
	def __init__(self):
		super(Controller, self).__init__()
		self._client = Client()
		cfg = MailConfiguration('mail.json', 'gmail')
		self._mailer = Mailer(cfg.address, cfg.username, cfg.password, cfg.host, cfg.port)
		self._recipients = [cfg.address]
		self._threads = []
	
	def capture(self):
		filepaths = self._client.capture(count=2)
		thread = Thread(target=self._mailer.send, args=(self._recipients, 'camera activity', datetime.now().strftime('date: %FT%T'), filepaths))
		thread.start()
		self._threads.append(thread)
	
	def close(self):
		for thread in self._threads:
			thread.join()
		self._mailer.close()


class CameraAdapter(gpio.Output):
	def __init__(self, controller):
		super(CameraAdapter, self).__init__()
		self._controller = controller
		self._timer = None
		self._lock = Lock()
	
	def start(self):
		if self.lock():
			self._timer = Timer(0.5, self.unlock)
			self._timer.start()
			self._controller.capture()
		else:
			print 'couldn\'t acquire lock, skipping photo'
	
	def lock(self):
		return self._lock.acquire(False)
	
	def unlock(self):
		self._lock.release()


if __name__=='__main__':
	parser = ArgumentParser(description='detect motion, capture image, transmit image')
	parser.add_argument('-i', '--interactive', action='store_true', help='control sentry interactively')
	args = parser.parse_args()
	
	basicConfig(filename=datetime.now().strftime('driver_%Y-%m-%dT%H.%M.%S%z.log'), level=DEBUG, format='%(asctime)-15s %(message)s')
	logger = getLogger('driver')
	controller = Controller()
	
	if args.interactive:
		queue = Queue()
		ui = TerminalInterface()
		process = Process(target=ui.display, args=(queue,))
		try:
			process.start()
			while True:
				command = queue.get()
				if 'capture' == command:
					logger.debug('capture')
					controller.capture()
				elif 'quit' == command:
					break
			logger.debug('closing queue...')
			queue.close()
			logger.debug('joining queue...')
			queue.join_thread()
			logger.debug('joining process...')
			process.join()
		except Exception:
			logger.exception('whoops')
		finally:
			ui.close()
	else:
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

