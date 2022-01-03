import vlc, time, datetime, sys, colorama
from colorama import Fore
from . import main as M

#notes to self
#we need a way to go BACK in time for the video, so I'll do a thing where I've got a second audio player for each player that plays what happened 30 seconds ago.

class Player: #media player
	def __init__(self, url:str, main:M.Main, name, index):
		self.muted = False
		self.name = name
		self.index = index
		self.active = False
		self.url = url
		self.main = main
		self.vlc:vlc.Instance = main.vlc
		self.time_start:int = 0
		self.date_start:datetime.datetime = None
		self.start()
	
	def log(self, *args, t="normal"):
		colors = {"normal": Fore.BLUE,  "good":Fore.GREEN, "warn": Fore.YELLOW, "bad": Fore.RED, "important": Fore.MAGENTA}
		if t not in colors: t == "warn"
		p = f"{colors[t]}{colorama.Style.BRIGHT}"
		b = f"{colorama.Style.BRIGHT}"
		b1 = colorama.Style.NORMAL
		print(f"{b}{Fore.WHITE}[{b1}{Fore.GREEN}{self.name}{b}{Fore.WHITE}]", p, "\t", *args)
	
	def start(self):
		self.log("Starting...")
		self.media = self.vlc.media_new(self.url)
		self.player:vlc.MediaPlayer = self.vlc.media_player_new()

		#self.media.add_option(f"sout=#transcode{{vcodec=none,acodec=mp3,ab=320,channels=2,samplerate=44100}}:file{{dst={ self.name }.mp3}}")
		#self.media.add_option(f"sout=#transcode{{vcodec=none,acodec=mp3,ab=320,channels=2,samplerate=44100}}:file{{dst='{ self.name }.mp3'}}")
		#self.media.add_option("sout=#duplicate{dst=display,dst=\"transcode{vcodec=none,acodec=mp3,ab=320,channels=2,samplerate=44100}:file{dst=\""+ self.name +".mp3\"}\"")

		self.player.set_media(self.media)

		self.player.play()
		self.time_start = time.time()
		self.date_start = datetime.datetime.now()
		self.log("Started!")
		self.set_volume(0)
	
	def update(self):
		v = 1
		if self.muted:
			v = 0
		if self.main.solo == True or self.main.focus:
			if self.main.selected != self.index:
				if self.main.focus: v = .5
				else: v = 0
			else:
				v = 1 #this will remain 1 while all others turn to 0
		if self.main.full_muted: v = 0
		self.set_volume(v)
		


	def activate(self):
		self.update()
		self.active = True

	def set_volume(self, value:float):
		self.player.audio_set_volume(int(value * 100))
		self.log("Set volume to", f"{value*100}%")

