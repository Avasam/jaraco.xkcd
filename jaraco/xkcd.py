import urllib.parse
import random
import importlib
import contextlib

import jaraco.text
import requests

session = requests.session()


class Comic:
	root = 'https://xkcd.com/'

	__cache = {}

	def __new__(cls, number):
		return cls.__cache.setdefault(number, super().__new__(cls))

	def __init__(self, number):
		if vars(self):
			return
		path = '{number}/info.0.json'.format(**locals())
		url = urllib.parse.urljoin(self.root, path)
		resp = session.get(url)
		resp.raise_for_status()
		vars(self).update(resp.json())

	@classmethod
	def latest(cls):
		url = urllib.parse.urljoin(cls.root, 'info.0.json')
		resp = session.get(url)
		resp.raise_for_status()
		return cls(resp.json()['num'])

	@classmethod
	def all(cls):
		latest = cls.latest()
		return map(cls, range(latest.number, 0, -1))

	@classmethod
	def random(cls):
		"""
		Return a randomly-selected comic
		"""
		latest = cls.latest()
		return cls(random.randint(1, latest.number))

	@classmethod
	def search(cls, text):
		"""
		Find a comic with the matching text
		"""
		title_matches = (
			comic
			for comic in cls.all()
			if text in jaraco.text.FoldedCase(comic.title)
		)
		return next(title_matches, None)

	@property
	def number(self):
		return self.num

	def __repr__(self):
		return '{self.__class__.__name__}({self.number})'.format(**locals())

	def __str__(self):
		return 'xkcd:{self.title} ({self.img})'.format(**locals())


with contextlib.suppress(ImportError):
	core = importlib.import_module('pmxbot.core')

	@core.command()
	def xkcd(rest):
		return Comic.search(rest) if rest else Comic.random()
