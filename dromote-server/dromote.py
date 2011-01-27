import socket
import signal
import sys
import threading
import gobject
import time
from mpris import *
from dbus.mainloop.glib import DBusGMainLoop
from synchronous_recipe import synchronous


def signal_handler(signal, frame):
  print 'Server terminating'
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def handle_signal(interface_name, changed_properties, invalidated):
  main.something_changed = True

def update_now_playing():
  if not (update_now_playing.player is None or update_now_playing.client is None):
    player = update_now_playing.player
    client = update_now_playing.client
    msg = " ".join(('STATUS', str(int(player.volume()*100)), str(player.repeat_status()), str(player.shuffle_status())))
    client.send(msg + "\n")
    if player.song_title() is None:
      client.send("-\n")
    else:
      msg = '"' + player.song_title() + '" by ' + player.song_artist() + "\n"
      client.send(msg)

def main():  
  main.something_changed = False
  update_now_playing
  #gobject.threads_init()
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
      l = DbusPlayerList(d, lock)
      if len(l.players) < 1:
        print repr(l.players)
        print "no mpris compliant players found :<"
        print "dropping client!"
        clientsocket.sendall("bye\n")
        update_now_playing.client = None
        time.sleep(1)
        continue
      player = MPRIS2Player(d, l.players[i], lock)
      update_now_playing.player = player
      update_now_playing()

      clientsocket.sendall("PLAYERS\n" + " ".join(l.players) + "\n")
      print "available players: " + " ".join(l.players)
      print "connected player : " + str(l.players[i])

      while clientsocket: 
          msg = clientsocket.recv(128).rstrip()
          m = re.search("cycle (\d)",msg) 
          if m:
            i = int(m.group(1))
            player = MPRIS2Player(d, l.players[i], lock)
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
  except KeyboardInterrupt:
    clientsocket.close()
    serversocket.close()

def loopContext(context, lock):
  while 1:
    with lock:
      context.iteration(False)
    if main.something_changed:
      update_now_playing()
      main.something_changed = False
    time.sleep(0.1)


if __name__ == "__main__":
      main()

