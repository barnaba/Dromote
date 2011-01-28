#encoding=utf8
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
  """Klasa wysyła aktualne dane o odtwarzaczu do klienta"""

  def __init__(self, bus, lock):
    """Konstruktor, przyjmuje obiekt szyny D-Bus i locka,
    blokującego dostęp do tej szyny"""
    self.lock = lock
    self.bus = bus

    self.change = False
    self.players = None
    self.player = None
    self.client = None

  def update(self):
    """Metoda wysyłająca aktualny stan odtwarzacza i
    informacje o odtwarzanym utworze"""  
    if not (self.client is None or self.player is None):
      if (self.change):
        status = self.__get_status_msg()
        np = self.__get_now_playing_msg()
        self.send(status, np)
    self.change = False

  def send(self, *args):
    """Metoda wysyłająca. *args są wysyłane do pilota,
    każdy w oddzielnej linii"""
    if not self.client is None:
      for msg in args:
        self.client.send(str(msg) + "\n")

  def update_players(self):
    """Metoda wysyłająca informacje o dostępnych
    odtwarzaczach"""  
    msg = self.__get_players_msg()
    self.send(msg)

  def __get_status_msg(self):
    """Metoda budująca wiadomość stanu: "STATUS a b c",
    gdzie a to głośność (1-100), b stan zapętlenia (0/1), c
    stan losowego odtwarzania (0/1)"""
    player = self.player
    return " ".join(('STATUS', str(int(self.player.volume()*100)), \
        str(self.player.repeat_status()), str(self.player.shuffle_status()))) 

  def __get_now_playing_msg(self):
    """metoda budująca wiadomość o aktualnie odtwarzanym utworze:
    '"<nazwa utworu>" by <nazwa artysty>'"""
    player = self.player
    if player.song_title() is None:
      return "-"
    else:
      return '"' + self.player.song_title() + '" by ' + self.player.song_artist()

  def __get_players_msg(self):
    """metoda budująca wiadomość o dostępnych odtwarzaczach: 'PLAYERS\na, b… x', gdzie a i b… x to nazwy odtwarzaczy""" 
    if not self.players is None:
      return "PLAYERS\n" + " ".join(self.players)

  def set_player(self, i=0):
    """metoda zmiany odtwarzacza, i to kolejność odtwarzacza
    na liście self.players - równowazna kolejności w spinnerze"""
    if not self.players is None:
      self.player = MPRIS2Player(self.bus, self.players[i], self.lock)

class DBusListener(object):
  """Klasa nasłuchuje na powiadomienia o zmianie właściwości odtwarzacza.
  Nasłuchiwanie odbywa się w wątku, który trzeba zacząć metodą start()"""

  def __init__(self, lock):
    """Konstruktor. Musi być uruchomiony przed innymi klasami korzystającymi
    z DBusa. lock - blokada dotycząca DBusa"""
    self.lock = lock

    gobject.threads_init()
    DBusGMainLoop(set_as_default=True)

    self.context = gobject.MainLoop().get_context()
    self.bus = dbus.SessionBus()

    def handle_signal(interface_name, changed_properties, invalidated):
      self.updater.change = True

    self.bus.add_signal_receiver(handle_signal, "PropertiesChanged", path="/org/mpris/MediaPlayer2")

  def start(self):
    """metoda startująca wątek nasłuchujący zmian w D-Busie"""
    updater = threading.Thread(target=self.__runLoop)
    updater.daemon = True
    updater.start()

  def __runLoop(self):
    while True:
      with self.lock:
        self.context.iteration(False)
      self.updater.update()
      time.sleep(0.1)

class DromoteServer(object):
  """Klasa obsługuje połączenie z klientem"""
  
  def __init__(self, updater, hostname='', port=9006):
    self.clientsocket = None
    self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serversocket.bind((hostname, port))
    self.serversocket.listen(5)
    self.updater = updater

  def accept(self):
      """Metoda czeka na połączenie od klienta i je zwraca"""
      (self.clientsocket, address) = self.serversocket.accept()
      return self.clientsocket

  def get_command(self):
    """Metoda czeka na komendę wysłaną przez klienta i ją zwraca"""
    return self.clientsocket.recv(128).rstrip()

  def close(self):
    """metoda zamyka połączenie z klientem, a następnie kończy nasłuchiwanie
    na porcie serwera"""  
    if not self.clientsocket is None:
      self.clientsocket.close()
    self.serversocket.close()

class CmdProcessor(object):
  """Klasa przetwarzająca otrzymane komendy"""

  def __init__(self, updater):
    self.updater = updater

  def process_commands(self, msg):
    """metoda przetwarza komendę i wysyła odpowiednie informacje zwrotne
    do klienta. Dostępne komendy: 'cycle n', 'bye', '*'. Metoda spróbuje
    wywołać gwiazdkę na obiekcie MPRISPlayer2"""
    match = re.search("cycle (\d)", msg) 
    if match:
      self.updater.set_player(int(match.group(1)))
      self.updater.change = True
      self.updater.update
    elif re.search("bye", msg):
      self.updater.send("bye")
      self.updater.client = None
      return False 
    elif msg and hasattr(self.updater.player, msg):
      fun = getattr(self.updater.player, msg)
      fun()
    return True 

def main():  
  """Główna funkcja"""
  try:
    lock = threading.Lock()
    listener = DBusListener(lock)
    updater = RemoteUpdater(listener.bus, lock)
    listener.updater = updater
    server = DromoteServer(updater)
    listener.start()
    processor = CmdProcessor(updater)
    while True:
      client = server.accept()
      updater.client = client
      updater.players = DbusPlayerList(listener.bus, lock).players
      updater.update_players()
      updater.set_player()
      while updater.client:
        msg = server.get_command()
        print msg
        if not processor.process_commands(msg):
          break
  except KeyboardInterrupt:
    server.close()




if __name__ == "__main__":
  main()
