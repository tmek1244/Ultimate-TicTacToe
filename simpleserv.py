import random

from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory

class GameServerProtocol(protocol.Protocol):
    def __init__(self,factory):
        self.factory = factory
        self.is_playing = False
        self.opponent = None
 
    def connectionMade(self):
        self.factory.ile += 1

    def dataReceived(self, data):
        data = data.decode('ascii')

        if data == "Close1":
            self.transport.write("leave".encode('ascii'))
            return
        if data == "reset" or data == "yes" or data == "no":
            data = data.encode('ascii')
            self.opponent.transport.write(data)
        else:
            if not self.is_playing:
                if len(self.factory.lookingForOpponent) == 0 and data == "C":
                    self.factory.lookingForOpponent.append(self)
                elif self not in self.factory.lookingForOpponent:
                    self.opponent = self.factory.lookingForOpponent.pop()
                    self.opponent.opponent = self
                    if random.randint(0, 1) == 1:
                        self.transport.write("-1".encode('ascii'))
                        self.opponent.transport.write("1".encode('ascii'))
                    else:
                        self.transport.write("1".encode('ascii'))
                        self.opponent.transport.write("-1".encode('ascii'))
                        
                    self.is_playing = True
                    self.opponent.is_playing = True
            else:
                if self.opponent == "left":
                    self.transport.write("leave".encode('ascii'))
                else:
                    self.opponent.transport.write(data.encode('ascii'))       

    def connectionLost(self, reason):
        try:
            self.factory.lookingForOpponent.remove(self)
        except:
            try:
                self.opponent.transport.write("leave".encode('ascii'))
                self.opponent.opponent = "left"
            except:
                pass

class GameServerFactory(Factory):
    lookingForOpponent = []
    ile = 0

    def __init__(self):
        print ("server is running...")
    
    def buildProtocol(self, addr):
        return GameServerProtocol(self)

reactor.listenTCP(8080, GameServerFactory())
reactor.run()