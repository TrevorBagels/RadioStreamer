import time, vlc, os, colorama, sys
from colorama import Fore
from . import utils
from console.utils import wait_key
import console.utils
import console
class Main:
	def __init__(self):
		from . import player
		self.full_muted = False #true if we don't want any sound
		self.solo = False #set TRUE if we only want to hear the selected source
		self.focus = False #set to TRUE if you want all tracks other than this one to drop their volume to 20% or less
		self.selected = 0
		self.vlc:vlc.Instance = vlc.Instance("--input-repeat=1", "--fullscreen")
		#urls = ["https://us4.internet-radio.com/proxy/wsjf?mp=/stream;", "http://airspectrum.cdnstream1.com:8018/1606_192"]
		urls = ["https://broadcastify.cdnstream1.com/32048", "https://broadcastify.cdnstream1.com/20766", "https://broadcastify.cdnstream1.com/20613", "https://broadcastify.cdnstream1.com/35614"]
		names = ["Portland State", "Portland F&R", "Multnomah Sheriff & Gresham Police Dispatch", "Oregon State Police"]
		default_muted = [False, False, False, True]
		self._name_filler = utils.longest_string_filler(names)
		self.players:list[player.Player] = []
		for x, i in zip(urls, range(len(urls))):
			self.players.append(player.Player(x, self, names[i], i))
			self.players[i].muted = default_muted[i]
		def stepback(v):
			def sb():
				self.step_back(seconds=v)
			return sb
		self.actions = {
			"mute all": self.mute_all,
			"mute source": self.mute_source,
			"solo source": self.solo_player,
			#"cycle source": self.switch_station,
			"<< 10s": stepback(10),
			"<< 30s": stepback(30),
			"to LIVE >>": self.step_live,
			"exit": self.ext
			}

		self.update_players()
		
		self.running = True
		while self.running:
			self.update_players() #update media players
			self.action_menu() #update the display
			self.action_menu_execute() #get any input from the user and then repeat

	

	def input_num(self, mx=9, allowed=[], oopsie=int):
		'''
		mx - max value
		allowed - list of strings that are accepted as input
		'''
		#print("\n > ", end='')
		#with self.lock:
		i = wait_key()
		if i in allowed:
			return i
		try:
			if int(i) <= mx:
				#console.utils.clear_line() 
				#print("\n >", i)
				return int(i)
			else: 
				#console.utils.clear_line()
				oopsie()
				return self.input_num(mx=mx, allowed=allowed, oopsie=oopsie)
		except:
			#console.utils.clear_line()
			oopsie()
			return self.input_num(mx=mx, allowed=allowed, oopsie=oopsie)


		
	def action_menu(self):
		_w, _b, _r, _g, _y = Fore.WHITE, Fore.BLUE, Fore.RED, Fore.GREEN, Fore.YELLOW

		display = "\n" + colorama.Style.DIM + Fore.MAGENTA + utils.terminal_size()[0] * "-" + "\n"
		display += colorama.Style.NORMAL

		for x, i in zip(self.players, range(len(self.players))):
			if self.selected == x.index: display += f"{_w}[{_g}x{_w}]"
			else: display += f"{_w}[ ]"
			display += "\t" + _b + x.name + (self._name_filler - len(x.name))*" "  + _w
			status_muted, status_solo, status_volume = "\t\t", "\t\t", f"{x.player.audio_get_volume()}%"
			if x.muted: status_muted = f"{_r}MUTED{_w}\t\t"
			if self.solo and self.selected == x.index: status_solo = f"{_b}SOLO{_w}\t\t"
			if self.focus and self.selected == x.index: status_solo = f"{_y}FOCUS{_w}\t\t"
			tl = (time.time() - x.time_start) #total length (seconds)
			lp = x.player.get_time()/1000 / tl #length perecentage (0-1)
			ls = "-" * 14 #length string
			ls = ls[:int(lp*14)] + colorama.Style.DIM + ls[int(lp*14):] + colorama.Style.NORMAL
			np = f"{_g}{utils.hms(x.player.get_time()/1000)}\t{_r}" + ls + f"\t{_g}{utils.hms( tl  )}"
			display += "\t\t" + status_muted + "\t" + status_solo + "\t" + status_volume + "\t" + np + "\n\n"
		
		#now playing (np)
		display += "\n\n"
		
		i = 0
		for k, v in self.actions.items():
			i += 1
			display += f"{Fore.RED}{i}.){Fore.BLUE} {k}\n"
		
		console.utils.clear()
		print(display)
		print("\n")
		


	def action_menu_execute(self):
		#time.sleep(.05)
		#self.action_menu_execute()
		actions_list = [k for k, v in self.actions.items()]
		def station_down():
			self.switch_station(direction=-1)
		def focus():
			if self.solo:
				self.solo = False
			self.focus = not self.focus
		hidden_actions = {
			"A": station_down, "B": self.switch_station, 
			"m": self.mute_source, "M": self.mute_all, 
			"q": self.ext, "s": self.solo_player, 
			"f": focus, ",": self.step_back, "l": self.step_live}
		def reupdate_display():
			self.update_players()
			self.action_menu()

		action = self.input_num(mx=len(actions_list), allowed=hidden_actions, oopsie=reupdate_display)
		if type(action) == int:
			a = self.actions[actions_list[action - 1]]
		else:
			a = hidden_actions[action]
		a()
	
	def get_selected(self):
		return self.players[self.selected]


	def mute_source(self):
		self.get_selected().muted = not self.get_selected().muted
	def mute_all(self):
		print("all muted/unmuted")
		self.full_muted = not self.full_muted
	def solo_player(self):
		if self.focus:
			self.focus = False
		self.solo = not self.solo
	def switch_station(self, direction=1):
		self.selected += direction
		if self.selected > len(self.players)-1:
			self.selected = 0
		if self.selected < 0:
			self.selected = len(self.players) - 1
	def step_back(self, seconds=3):
		print("<-",seconds)
		self.get_selected().player.set_time(self.get_selected().player.get_time() - seconds*1000)
	def step_live(self):
		l = (time.time() - self.get_selected().time_start) * 1000 - 500 #offset by half a second to account for any uncertainty/error
		l = int(l)
		print("Setting time to", utils.hms(l/1000))
		self.get_selected().player.set_time(l)
		#self.get_selected().player.set_time(self.get_selected().player.get_length())
	def update_players(self):
		for p in self.players: p.update()
	
	def ext(self):
		self.running = False
		sys.exit()
	

	