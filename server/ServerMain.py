from twisted.internet import reactor


from server.GameServerFactory import GameServerFactory

if __name__ == '__main__':
    reactor.listenTCP(8080, GameServerFactory())
    reactor.run()
