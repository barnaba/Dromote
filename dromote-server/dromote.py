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
  hostname = len(sys.argv) > 1 and sys.argv[1] or socket.gethostname()
  serversocket.bind((hostname, 9006))
  print "connecting to " + hostname
  serversocket.listen(5)
  while 1:
    i = 0
    (clientsocket, address) = serversocket.accept()
    print "client connected"
    d = dbus.SessionBus()
    l = DbusPlayerList(d)
    player = MPRIS2Player(d, l.players[i])
    while 1: 
      try:
        msg = clientsocket.recv(128).rstrip()
        if msg == "cycle":
          i+=1 
          i%=len(l.players)
          player = MPRIS2Player(d, l.players[i])
        elif msg:
            fun = getattr(player, msg)
            fun()
      except KeyboardInterrupt:
        clientsocket.close()
        serversocket.close()
        del clientsocket
        del serversocket


if __name__ == "__main__":
      main()

