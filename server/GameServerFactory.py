from twisted.internet.protocol import Factory

from server.GameServerProtocol import GameServerProtocol


class GameServerFactory(Factory):
    lookingForOpponent = []
    players = 0

    def __init__(self):
        print("Server is running...")

    def buildProtocol(self, addr):
        return GameServerProtocol(self)
