import time, vlc, os, colorama, sys, console
from colorama import Fore
from console.utils import wait_key
import console.utils
from .. import utils
from ..prodict import Prodict

class ConfigTrack(Prodict):
	url:	str
	name:	str
	muted:	bool
	def init(self):
		self.url = ""
		self.name = "Untitled Track"
		self.muted = False
	

class Config(Prodict):
	tracks:		list[ConfigTrack]

	def init(self):
		self.tracks = []


