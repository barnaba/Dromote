import dbus
import re
import socket
import signal
import sys

class DbusPlayerList:
  def __init__(self, bus):
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
		meta = self["Metadata"]
		return meta["xesam:title"]

  def toggle_shuffle(self):
		self["Shuffle"] = not self["Shuffle"]

  def toggle_repeat(self):
		if self["LoopStatus"] == "Playlist":
			self["LoopStatus"] = "None"
		else:
			self["LoopStatus"] = "Playlist"

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


def signal_handler(signal, frame):
  print 'Server terminating'
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main():  
  serversocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
  hostname = len(sys.argv) > 1 and sys.argv[1] or ''
  serversocket.bind((hostname, 9006))
  print "server started..."
  serversocket.listen(5)
  try:
    while 1:
      i = 0
      (clientsocket, address) = serversocket.accept()
      print "client connected: " , address
      d = dbus.SessionBus()
      l = DbusPlayerList(d)
      if not len(l.players):
        print "no mpris compliant players found :<"
        print "dropping client!"
        clientsocket.close()
      player = MPRIS2Player(d, l.players[i])
      print "available players: " + " ".join(l.players)
      print "connected player : " + str(l.players[i])
      while clientsocket: 
          msg = clientsocket.recv(128).rstrip()
          if msg == "cycle":
            i+=1 
            i%=len(l.players)
            player = MPRIS2Player(d, l.players[i])
            print "connected player: " + str(l.players[i])
          elif msg == "bye":
            clientsocket.close()
            break
          elif msg and hasattr(player, msg):
              fun = getattr(player, msg)
              fun()
              print "command: " + msg
      print "client disconnected"
  except KeyboardInterrupt:
    clientsocket.close()
    serversocket.close()
    del clientsocket
    del serversocket


if __name__ == "__main__":
      main()

