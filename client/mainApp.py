from kivy.app import App

from client import connection
from client import Menu
from client import SidePanel
from client.Manager import Manager


class TicTacToeApp(App):
    state = "in_menu"
    man = None
    s = None
    clock_timer = None
    waiting_for_answer = 0

    def build(self):
        self.man = Manager()
        return self.man

    def get_man(self):
        return self.man

    def get_state(self):
        return self.state

    def set_state(self, val):
        self.state = val

    def que_for_game(self):
        self.s = connection.ThreadedClient()
        self.s.start()


if __name__ == '__main__':
    TTApp = TicTacToeApp()
    TTApp.run()
