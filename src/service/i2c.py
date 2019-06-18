#!/usr/bin/env python

from smbus import SMBus
from struct import pack, unpack
from time import sleep

_bus = None

#https://github.com/sparkfun/Serial7SegmentDisplay/wiki/Special-Commands
_cmd = {
  'clear_display': 0x76,
  'decimal_ctrl': 0x77,
  'cursor_ctrl': 0x79,
  'brightness_ctrl': 0x7A,
  'digit_1_ctrl': 0x7B,
  'digit_2_ctrl': 0x7C,
  'digit_3_ctrl': 0x7D,
  'digit_4_ctrl': 0x7E,
  'baud_rate_cfg': 0x7F,
  'i2c_address_cfg': 0x80,
  'factory_reset': 0x81
}

def initialize():
	global _bus
	if not _bus:
		_bus = SMBus(1)

class Sensor(object):
	def __init__(self):
		super().__init__()
	
	@property
	def type(self):
		return self._type()
	
	def read(self):
		pass
	
	def close(self):
		pass
	
	def _type(self):
		pass


class Reading(object):
	def __init__(self, value, unit):
		self._unit = unit
		self._value = value
	
	@property
	def unit(self):
		return self._unit
	
	@property
	def value(self):
		return self._value
	
	def __str__(self):
		return str({'unit': self.unit, 'value': self.value})
	
	def __repr__(self):
		return str({'unit': self.unit, 'value': self.value})


class Thermometer(Sensor):
	def __init__(self, bus, address=None):
		super().__init__()
		self._address = address or 0x48 #default: tmp102 sensor
		self._bus = bus
	
	def read(self, unit='celcius'):
		celcius = self._read()
		if not unit or unit in ['C', 'c', 'celcius']:
			return Reading(celcius, 'celcius')
		elif unit in ['F', 'f', 'fahrenheit']:
			return Reading(9 * celcius / 5 + 32, 'fahrenheit')
		else:
			raise RuntimeError('unsupported unit: {}'.format(unit))
	
	def _read(self):
		raw = self._bus.read_word_data(self._address, 0x00)
		return (unpack("<H", pack(">H", raw))[0] >> 4) * 0.0625
	
	def _type(self):
		return 'thermometer'
	
	@classmethod
	def new(cls):
		global _bus
		return cls(_bus)


def write_float(address, value):
	global _bus, _cmd
	_bus.write_byte(address, _cmd['clear_display'])
	_bus.write_byte_data(address, _cmd['decimal_ctrl'], 0b00000100)
	for digit in '{0:4d}'.format(int(10 * value)):
		_bus.write_byte(address, ord(digit))

def write_integer(address, value):
	_bus.write_byte(address, 0x76)
	for digit in '{0:4d}'.format(value):
		_bus.write_byte(address, ord(digit))

def read_celcius(address):
	raw = _bus.read_word_data(address, 0x00)
	return (unpack("<H", pack(">H", raw))[0] >> 4) * 0.0625


if __name__ == '__main__':
	_bus = SMBus(1)
	display_address = 0x71
	tmp102_address = 0x48
	
	try:
		while True:
			celcius = read_celcius(tmp102_address)
			print('C: {0:0.2f}'.format(celcius))
			write_float(display_address, celcius)
			sleep(3)
	except KeyboardInterrupt:
		pass
	except:
		raise

