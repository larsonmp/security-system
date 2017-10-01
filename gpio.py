#!/usr/bin/env python

import RPi.GPIO as gpio
from collections import deque
from datetime import datetime
from logging import getLogger
from threading import Timer
from time import sleep

class Output(object):
	def __init__(self):
		super(Output, self).__init__()
	
	def start(self):
		pass
	
	def stop(self):
		pass


class GpioOutput(object):
	def __init__(self, channel, device_type):
		super(GpioOutput, self).__init__()
		self._channel = channel
		self._device_type = device_type
		gpio.setup(channel, gpio.OUT)
		gpio.output(channel, False)
		getLogger(__name__).info('channel %2d is %s', channel, device_type)


class Logger(Output):
	def __init__(self):
		super(Logger, self).__init__()
		self._id = 0
	
	def start(self):
		print '[{}]: event {}: motion detected'.format(datetime.now(), self._id)
		self._id += 1


class Buzzer(GpioOutput):
	def __init__(self, channel):
		super(Buzzer, self).__init__(channel, 'buzzer')
		self._timer = None
	
	def start(self):
		gpio.output(self._channel, True)
		if self._timer:
			self._timer.cancel()
		self._timer = Timer(3.0, self.stop)
		self._timer.start()
	
	def stop(self):
		gpio.output(self._channel, False)
	

class LED(GpioOutput):
	def __init__(self, channel):
		super(LED, self).__init__(channel, 'LED')
		self._timer = None
	
	def start(self):
		gpio.output(self._channel, True)
		if self._timer:
			self._timer.cancel()
		self._timer = Timer(2.0, self.stop)
		self._timer.start()
	
	def stop(self):
		gpio.output(self._channel, False)


class MotionDetector(object):
	def __init__(self, channel):
		super(MotionDetector, self).__init__()
		self._logger = getLogger(__name__)
		self._channel = channel
		self.configure(self._channel)
		self._output = []
	
	def configure(self, channel):
		gpio.setup(channel, gpio.IN, pull_up_down = gpio.PUD_UP)
		self._logger.info('channel %d is motion sensor (pull up, attach to ground to trigger)', channel)
		gpio.add_event_detect(channel, gpio.RISING, callback=self.rising, bouncetime=500)
		#gpio.add_event_detect(channel, gpio.BOTH, callback=self.both, bouncetime=100)
	
	def add_output(self, output):
		self._output.append(output)
	
	def both(self, channel):
		if channel is not self._channel:
			self._logger.warning('triggered on unexpected channel')
		if gpio.input(channel):
			self.rising(channel)
		else:
			self.falling(channel)
	
	def rising(self, channel):
		for output in self._output:
			output.start()
	
	def falling(self, channel):
		for output in self._output:
			output.stop()

def initialize():
	gpio.setmode(gpio.BOARD)

def cleanup():
	gpio.cleanup()

