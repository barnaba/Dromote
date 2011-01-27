import dbus
import re
from synchronous_recipe import synchronous

class DbusPlayerList(object):
  def __init__(self, bus, lock):
    self.lock = lock
    self.bus = bus
    self.initialize()

  @synchronous('lock')

  def initialize(self):
    self.players = []
    m = re.compile("org\\.mpris\\.MediaPlayer2\\.(.+)")
    for name in self.bus.list_names():
      player = m.match(name)
      if player:
        self.players.append(player.group(1))

class MPRIS2Player(object):

  def __init__(self, bus, player_name, lock):
    self.lock = lock
    self.name = player_name
    self.bus = bus
    self.initialize()

  @synchronous('lock')
  def initialize(self):
    player_object = self.bus.get_object('org.mpris.MediaPlayer2.'+self.name, '/org/mpris/MediaPlayer2')
    self.player = dbus.Interface(player_object, 'org.mpris.MediaPlayer2.Player')
    self.properties = dbus.Interface(self.player, 'org.freedesktop.DBus.Properties')

  def next(self):
		self.player.Next()
	
  def play_pause(self):
		self.player.PlayPause()

  def prev(self):
		self.player.Previous()

  def seek(self, seconds):
		t = int(seconds * 1000000)
		self.player.Seek(t)
	
  def __setitem__(self, key, value):
		self.properties.Set('org.mpris.MediaPlayer2.Player',key,value)
		return self[key]

  def __getitem__(self, key):
		return self.properties.Get('org.mpris.MediaPlayer2.Player',key)

  def song_position(self):
		return self["Position"]

  def song_length(self):
		meta = self["Metadata"]
		return meta["mpris:length"]

  def song_title(self):
    try:
      meta = self["Metadata"]
      return meta["xesam:title"].encode('utf-8')
    except KeyError:
      return None

  def song_artist(self):
    try:
      meta = self["Metadata"]  
      return meta["xesam:artist"][0].encode('utf-8')
    except KeyError:
      return None

  def toggle_shuffle(self):
		self["Shuffle"] = not self["Shuffle"]

  def shuffle_status(self):
    return self["Shuffle"]

  def toggle_repeat(self):
		if self["LoopStatus"] == "Playlist":
			self["LoopStatus"] = "None"
		else:
			self["LoopStatus"] = "Playlist"

  def repeat_status(self):
    if self["LoopStatus"] == "Playlist":
      return 1 
    else:
      return 0

  def volume(self, new_volume=None):
		self["Volume"] = new_volume or self["Volume"]
		return self["Volume"]

  def louder(self):
    self["Volume"] += 0.1

  def quieter(self):
    self["Volume"] -= 0.1

  def __str__(self):
		title = self.song_title()
		progress = self.song_position() * 1.0 / self.song_length()
		progress_bar = "[" + "=" * int(progress * 70) + " " * (70 - int(progress * 70)) + "]"
		return str(int(progress*100)) + "%" + " " * 10 + title + "\n" + progress_bar

