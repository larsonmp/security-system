#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from logging import DEBUG, INFO, WARNING, basicConfig, getLogger
from mail import MailConfiguration, Mailer
from traceback import print_exc

from rest import Client
#from ux import TerminalInterface


if __name__=='__main__':
	parser = ArgumentParser(description='capture and email image')
	args = parser.parse_args()
	
	basicConfig(filename=datetime.now().strftime('demo_%Y-%m-%dT%H.%M.%S%z.log'), level=DEBUG, format='%(asctime)-15s %(message)s')
	logger = getLogger('demo')
	
	client = Client()
	cfg = MailConfiguration('mail.json', 'gmail')
	mailer = Mailer(cfg.address, cfg.username, cfg.password, cfg.host, cfg.port)

	filepaths = client.capture()
	mailer.send([cfg.address], 'camera activity', datetime.now().strftime('date: %FT%T'), filepaths)
	mailer.close()
