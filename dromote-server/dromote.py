import socket
import signal
import sys
import threading
import gobject
import time
from mpris import *
from dbus.mainloop.glib import DBusGMainLoop
from synchronous_recipe import synchronous

class RemoteUpdater(object):

  def __init__(self, bus, lock):
    self.lock = lock
    self.bus = bus

    self.change = False
    self.players = None
    self.player = None
    self.client = None

  def update(self):
    if not (self.client is None or self.player is None):
      if (self.change):
        status = self.__get_status_msg()
        np = self.__get_now_playing_msg()
        self.send(status, np)
    self.change = False

  def send(self, *args):
    if not self.client is None:
      for msg in args:
        self.client.send(str(msg) + "\n")

  def update_players(self):
    msg = self.__get_players_msg()
    self.send(msg)

  def __get_status_msg(self):
    player = self.player
    return " ".join(('STATUS', str(int(self.player.volume()*100)), \
        str(self.player.repeat_status()), str(self.player.shuffle_status()))) 

  def __get_now_playing_msg(self):
    player = self.player
    if player.song_title() is None:
      return "-"
    else:
      return '"' + self.player.song_title() + '" by ' + self.player.song_artist()

  def __get_players_msg(self):
    if not self.players is None:
      return "PLAYERS\n" + " ".join(self.players)

  def set_player(self, i=0):
    if not self.players is None:
      self.player = MPRIS2Player(self.bus, self.players[i], self.lock)

class DBusListener(object):

  def __init__(self, lock):
    self.lock = lock

    gobject.threads_init()
    DBusGMainLoop(set_as_default=True)

    self.context = gobject.MainLoop().get_context()
    self.bus = dbus.SessionBus()

    def handle_signal(interface_name, changed_properties, invalidated):
      self.updater.change = True

    self.bus.add_signal_receiver(handle_signal, "PropertiesChanged", path="/org/mpris/MediaPlayer2")

  def start(self):
    updater = threading.Thread(target=self.runLoop)
    updater.daemon = True
    updater.start()

  def runLoop(self):
    while True:
      with self.lock:
        self.context.iteration(False)
      self.updater.update()
      time.sleep(0.1)

class DromoteServer(object):
  
  def __init__(self, updater, hostname='', port=9006):
    self.serversocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
    self.serversocket.bind((hostname, port))
    self.serversocket.listen(5)
    self.updater = updater

  def accept(self):
      (self.clientsocket, address) = self.serversocket.accept()
      return self.clientsocket

  def process_commands(self):
      msg = self.clientsocket.recv(128).rstrip()
      match = re.search("cycle (\d)",msg) 
      if match:
        self.updater.set_player(int(match.group(1)))
        self.updater.change = True
        self.updater.update
      elif re.search("bye",msg):
        self.clientsocket.sendall("bye\n")
        self.updater.client = None
        return False 
      elif msg and hasattr(self.updater.player, msg):
        fun = getattr(self.updater.player, msg)
        fun()
      return True 

def main():  
  try:
    lock = threading.Lock()
    listener = DBusListener(lock)
    updater = RemoteUpdater(listener.bus, lock)
    listener.updater = updater
    server = DromoteServer(updater)
    listener.start()
    while True:
      client = server.accept()
      updater.client = client
      updater.players = DbusPlayerList(listener.bus, lock).players
      updater.update_players()
      updater.set_player()
      while updater.client:
        if not server.process_commands():
          break
  except KeyboardInterrupt:
    #close sockets
    pass




if __name__ == "__main__":
      main()
