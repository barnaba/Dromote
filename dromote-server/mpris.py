import dbus
import re

class DbusPlayerList:
  def __init__(self, bus):
    bus = dbus.SessionBus()
    self.players = []
    m = re.compile("org\\.mpris\\.MediaPlayer2\\.(.+)")
    for name in bus.list_names():
      player = m.match(name)
      if player:
        self.players.append(player.group(1))


class MPRIS2Player():

  def __init__(self, bus, player_name):
		player_object = bus.get_object('org.mpris.MediaPlayer2.'+player_name, '/org/mpris/MediaPlayer2')
		self.player = dbus.Interface(player_object, 'org.mpris.MediaPlayer2.Player')
		self.properties = dbus.Interface(self.player, 'org.freedesktop.DBus.Properties')

  def next(self):
		self.player.Next()
	
  def play_pause(self):
		self.player.PlayPause()

  def prev(self):
		self.player.Previous()

  def __rshift__(self, seconds):
		t = int(seconds * 1000000)
		self.player.Seek(t)
	
  def __lshift__(self, seconds):
		self.__add__(-seconds)

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
		meta = self["Metadata"]
		return meta["xesam:title"]

  def toggle_shuffle(self):
		self["Shuffle"] = not self["Shuffle"]

  def toggle_loop(self):
		if self["LoopStatus"] == "Playlist":
			self["LoopStatus"] = "None"
		else:
			self["LoopStatus"] = "Playlist"

  def volume(self, new_volume=None):
		self["Volume"] = new_volume or self["Volume"]
		return self["Volume"]

  def __str__(self):
		title = self.song_title()
		progress = self.song_position() * 1.0 / self.song_length()
		progress_bar = "[" + "=" * int(progress * 70) + " " * (70 - int(progress * 70)) + "]"
		return str(int(progress*100)) + "%" + " " * 10 + title + "\n" + progress_bar

