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
        if not self.is_playing:
            if len(self.factory.lookingForOpponent) == 0:
                self.factory.lookingForOpponent.append(self)
                self.transport.write(("szukam").encode('ascii'))
            elif self not in self.factory.lookingForOpponent:
                self.opponent = self.factory.lookingForOpponent.pop()
                self.opponent.opponent = self
                self.transport.write("-1".encode('ascii'))
                self.opponent.transport.write("1".encode('ascii'))
                #self.GameOnline()
                #table.opponent.GameOnline()
                self.is_playing = True
                self.opponent.is_playing = True
        else:
            self.opponent.transport.write(data)
        #print("self: ",self)
        #print("opponent: ",self.opponent)

    def connectionLost(self, reason):
        try:
            print("cos")
            self.factory.lookingForOpponent.remove(self)
            self.factory.game = False
            self.opponent.transport.write("przeciwnik uciekl".encode('ascii'))
        except:
            pass

class GameServerFactory(Factory):
    lookingForOpponent = []
    ile = 0
    opponent = None
    alien = None
    game = False

    def __init__(self):
        print ("server is running...")
    
    def buildProtocol(self, addr):
        return GameServerProtocol(self)

reactor.listenTCP(8080, GameServerFactory())
reactor.run()