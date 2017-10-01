#!/usr/bin/env python

from smtplib import SMTP_SSL, SMTPServerDisconnected

from argparse import ArgumentParser
from datetime import datetime
from getpass import getpass
from os.path import basename
from platform import node
from threading import Lock
from traceback import print_exc
from yaml import safe_load

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailConfiguration(object):
	def __init__(self, filepath, name):
		with open(filepath) as fp:
			config = safe_load(fp)[name]
			self._username = config['username']
			self._password = config['password'].decode(config['password.encoding'])
			self._address = config['address']
			self._host = config['outgoing']['host']
			self._port = config['outgoing']['port']
	
	@property
	def username(self):
		return self._username
	
	@property
	def password(self):
		return self._password
	
	@property
	def address(self):
		return self._address
	
	@property
	def host(self):
		return self._host
	
	@property
	def port(self):
		return self._port


class Mailer(object):
	def __init__(self, sender, username, password, mailhost, mailport):
		self._sender = sender
		self._username = username
		self._password = password
		
		self._host = mailhost
		self._port = mailport
		
		self._session = SMTP_SSL(self._host, self._port)
		
		self._lock = Lock()
	
	def send(self, recipients, subject, body, images=None):
		with self._lock:
			try:
				self._login()
				self._send(recipients, subject, body, images or [])
			except Exception:
				print_exc()
			finally:
				self.close()
	
	def _send(self, recipients, subject, body, images):
		self._recipients = recipients
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg['From'] = self._sender
		msg['To'] = ', '.join(self._recipients)
		for image in images:
			with open(image, 'rb') as fp:
				msg.attach(MIMEImage(fp.read(), name=basename(image)))
		msg.attach(MIMEText(body, 'plain'))
		
		self._session.sendmail(self._sender, self._recipients, msg.as_string())
	
	def _login(self):
		self._session.connect(self._host, self._port)
		self._session.ehlo(self._host)
		self._session.login(self._username, self._password or getpass())
	
	def close(self):
		try:
			self._session.quit()
		except SMTPServerDisconnected:
			pass


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('configpath', nargs='?', default='config/mail.yaml', help='mail configuration')
	parser.add_argument('imagepath', nargs='?', default='sample.png', help='PNG image to attach')
	args = parser.parse_args()
	cfg = MailConfiguration(args.configpath, 'gmail')
	mailer = Mailer(cfg.address, cfg.username, cfg.password, cfg.host, cfg.port)
	mailer.send([cfg.address], 'subject', 'body', args.imagepath)

