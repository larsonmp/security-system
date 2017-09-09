#!/usr/bin/env python

import curses


class Interface(object):
	pass


class TerminalInterface(Interface):
	def __init__(self):
		super(TerminalInterface, self).__init__()
		self._stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		
		self._stdscr.keypad(1)
		
	def display(self, queue):
		self._stdscr.clear()
		self._stdscr.border(0)
		self._stdscr.addstr(2, 2, "Please enter a number...", curses.A_UNDERLINE)
		self._stdscr.addstr(5, 4, "1 - Capture single image")
		self._stdscr.addstr(6, 4, "2 - Show statistics")
		self._stdscr.addstr(7, 4, "3 - Exit")
		self._stdscr.refresh()

		while True:
			x = self._stdscr.getch()

			if x == ord('1'):
				queue.put('capture')
			if x == ord('2'):
				curses.beep()
			if x == ord('3'):
				queue.put('quit')
				break
		curses.endwin()
	
	def close(self):
		self.cleanup()
	
	def cleanup(self):
		self._stdscr.keypad(0)
		curses.echo()
		curses.nocbreak()
		curses.endwin()


class GraphicalInterface(Interface):
	pass


