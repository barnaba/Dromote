import socket
import signal
import sys
import threading
import gobject
import time
from mpris import *
from dbus.mainloop.glib import DBusGMainLoop


def signal_handler(signal, frame):
  print 'Server terminating'
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def handle_signal(interface_name, changed_properties, invalidated):
  update_now_playing()

def update_now_playing():
  player = update_now_playing.player
  client = update_now_playing.client
  if not (client is None):
    if player.song_title() is None:
      client.send("-")
    else:
      client.send('"' + player.song_title() + '" by ' + player.song_artist() + "\n")

def main():  

  gobject.threads_init()
  DBusGMainLoop(set_as_default=True)
  context = gobject.MainLoop().get_context()

  d = dbus.SessionBus()
  d.add_signal_receiver(handle_signal, "PropertiesChanged", path="/org/mpris/MediaPlayer2")

  lock = threading.Lock()
  updater = threading.Thread(target=loopContext,args=(context,lock))
  updater.daemon = True
  updater.start()

  serversocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
  hostname = len(sys.argv) > 1 and sys.argv[1] or ''
  serversocket.bind((hostname, 9006))
  print "server started..."
  serversocket.listen(5)
  try:
    while 1:
      i = 0
      (clientsocket, address) = serversocket.accept()
      update_now_playing.client = clientsocket
      print "client connected: " , address
      l = DbusPlayerList(d)
      if len(l.players) < 1:
        print repr(l.players)
        print "no mpris compliant players found :<"
        print "dropping client!"
        clientsocket.sendall("bye\n")
        update_now_playing.client = None
        time.sleep(1)
        continue
      player = MPRIS2Player(d, l.players[i])
      update_now_playing.player = player
      update_now_playing()

      clientsocket.sendall("PLAYERS\n" + " ".join(l.players) + "\n")
      print "available players: " + " ".join(l.players)
      print "connected player : " + str(l.players[i])

      lock.acquire()
      while clientsocket: 
          lock.release() 
          msg = clientsocket.recv(128).rstrip()
          lock.acquire()
          m = re.search("cycle (\d)",msg) 
          if m:
            i = int(m.group(1))
            player = MPRIS2Player(d, l.players[i])
            update_now_playing.player = player
            update_now_playing()
            print "connected player: " + str(l.players[i])
          elif re.search("bye",msg):
            clientsocket.sendall("bye\n")
            update_now_playing.client = None
            break
          elif msg and hasattr(player, msg):
              fun = getattr(player, msg)
              fun()
              print "command: " + msg
      print "client disconnected"
      lock.release()
  except KeyboardInterrupt:
    clientsocket.close()
    serversocket.close()

def loopContext(context, lock):
  while 1:
    with lock:
      context.iteration(False)
    time.sleep(0.001)


if __name__ == "__main__":
      main()

