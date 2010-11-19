import socket
import signal
import sys
from mpris import *

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

