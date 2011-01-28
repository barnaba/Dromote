#encoding=utf8
import dbus
import re
from synchronous_recipe import synchronous

class DbusPlayerList(object):
  """Klasa wyszukująca dostępne odtwarzacze podłączone
  do szyny DBUS i wspierające protokół MPRIS."""
  def __init__(self, bus, lock):
    """Konstruktor, przyjmuje szynę do szukania i blokadę do tej szyny."""
    self.lock = lock
    self.bus = bus
    self.__initialize()

  @synchronous('lock')

  def __initialize(self):
    self.players = []
    m = re.compile("org\\.mpris\\.MediaPlayer2\\.(.+)")
    for name in self.bus.list_names():
      player = m.match(name)
      if player:
        self.players.append(player.group(1))

class MPRIS2Player(object):
  """Klasa reprezentująca połączenie z obiektem odtwarzacza spełniającego
  standard MPRIS2 za pomocą szyny DBUS. Wszystkie metody klasy są synchronizowane,
  ponieważ wszystkie operują na szynie DBus"""

  def __init__(self, bus, player_name, lock):
    """Konstruktor. bus to szyna za pomocą której ma zostać zrealizowane połączenie, lock
    to blokada do tej szyny, a player_name to nazwa odtwarzacza, który ma zostać połączony"""
    self.lock = lock
    self.name = player_name
    self.bus = bus
    self.__initialize()

  @synchronous('lock')
  def __initialize(self):
    player_object = self.bus.get_object('org.mpris.MediaPlayer2.'+self.name, '/org/mpris/MediaPlayer2')
    self.player = dbus.Interface(player_object, 'org.mpris.MediaPlayer2.Player')
    self.properties = dbus.Interface(self.player, 'org.freedesktop.DBus.Properties')

  def next(self):
    """Następny utwór"""
    self.player.Next()
	
  def prev(self):
    """Poprzedni utwór"""
    self.player.Previous()

  def play_pause(self):
    "Przełącz pomiędzy odtwarzaniem a pauzą"
    self.player.PlayPause()

  def seek(self, seconds):
    "Przewiń seconds sekund"
    t = int(seconds * 1000000)
    self.player.Seek(t)
	
  def __setitem__(self, key, value):
		self.properties.Set('org.mpris.MediaPlayer2.Player',key,value)
		return self[key]

  def __getitem__(self, key):
		return self.properties.Get('org.mpris.MediaPlayer2.Player',key)

  def song_position(self):
    """Pozycja w aktualnie odtwarzanym utworze"""
    return self["Position"]

  def song_length(self):
    """Długość aktualnie odtwarzanego utworu"""
    meta = self["Metadata"]
    return meta["mpris:length"]

  def song_title(self):
    """Tytuł aktualnie odtwarzanego utworu"""
    try:
      meta = self["Metadata"]
      return meta["xesam:title"].encode('utf-8')
    except KeyError:
      return None

  def song_artist(self):
    """Nazwa artysty powiązanego z aktualnie odtwarzanym utworem"""
    try:
      meta = self["Metadata"]
      return meta["xesam:artist"][0].encode('utf-8')
    except KeyError:
      return None

  def toggle_shuffle(self):
    """Przełączenie trybu losowego odtwarzania utworów"""
    self["Shuffle"] = not self["Shuffle"]

  def shuffle_status(self):
    """Stan trybu losowego odtwarzania utworów"""
    return self["Shuffle"]

  def toggle_repeat(self):
    """Przełączenie trybu powtarzania utworów""" 
    if self["LoopStatus"] == "Playlist":
			self["LoopStatus"] = "None" 
    else: 
      self["LoopStatus"] = "Playlist"

  def repeat_status(self):
    """Stan trybu powtarzania utworów""" 
    if self["LoopStatus"] == "Playlist": 
      return 1 
    else:
      return 0

  def volume(self, new_volume=None):
    """Ustawienie głośności i zwrócenie nowej głośności. Zakres głośności 0.0-1.0"""
    self["Volume"] = new_volume or self["Volume"]
    return self["Volume"]

  def louder(self):
    """Pogłośnienie o 10%"""
    self["Volume"] += 0.1

  def quieter(self):
    """Ściszenie o 10%"""
    self["Volume"] -= 0.1

  def __str__(self):
		title = self.song_title()
		progress = self.song_position() * 1.0 / self.song_length()
		progress_bar = "[" + "=" * int(progress * 70) + " " * (70 - int(progress * 70)) + "]"
		return str(int(progress*100)) + "%" + " " * 10 + title + "\n" + progress_bar

