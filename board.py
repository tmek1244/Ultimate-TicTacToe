from functools import partial

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.uix.modalview import ModalView

import function

class BigBoard(GridLayout, Screen):
    status = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    current_player = -1
    where =  -1
    SecTime = "00"
    MinTime = "00"
    clockTimer = False
    are_we_playing = False

    time = MinTime + ' : ' + SecTime		

    def on_status(self, coords, whoWin):
        BigBoard.status[coords] = whoWin    

        win = function.ifSbWin(BigBoard.status)
        winner = ''
        if win == 1:
            winner = "X win!"
        elif win == -1:
            winner = "O win!"
        elif win == 6:
            winner = "Draw!"

        if winner:
            popup = ModalView(size_hint = (0.75 , 0.5))
            victory_label = Label(text = winner, font_size = 50)
            popup.add_widget(victory_label)
            self.clockTimer = False
            popup.open()
            self.parent.parent.parent.ids.pasek.reset(1)
            BigBoard.are_we_playing = False

class TicTacToeGrid(GridLayout):

    status = ListProperty([0, 0, 0,
                           0, 0, 0,
                           0, 0, 0])

    still_playing = NumericProperty(1)
    r = NumericProperty(.5)
    g = NumericProperty(.5)
    b = NumericProperty(.5)
    background_image = StringProperty('')

    colors = {1: 'assets/X.png', -1: 'assets/O.png'}
    colorsGrey = {1: 'assets/XGrey.png', -1: 'assets/OGrey.png', 6: 'assets/drawGrey.png'}

    def button_pressed(self, button):
        BigBoard.are_we_playing = True
        if ((self.coords == BigBoard.where or BigBoard.where == -1) and
            not self.status[button.coords] and self.still_playing
            and (int(App.get_running_app().getMan().who_am_I) == int(BigBoard.current_player)
            or not App.get_running_app().getMan().if_online)):

            if BigBoard.where == -1 and App.get_running_app().getMan().if_online == False:
                BigBoard.clockTimer = True
                App.get_running_app().clock_timer = Clock.schedule_interval(partial(function.timer, "offline"), 1.000)

            BigBoard.current_player *= -1
            button.background_color = (1, 1, 1, 1)
            button.background_normal = self.colors[BigBoard.current_player]
            self.status[button.coords] = BigBoard.current_player
            BigBoard.where = button.coords
            
            if App.get_running_app().getMan().if_online:
                data = str(self.coords) + str(button.coords)
                App.get_running_app().s.send_move(data.encode('ascii'))
            else:
                App.get_running_app().man.ids.screen_game_offline.ids.pasek.ids.whos_playing.background_normal = self.colors[-BigBoard.current_player]

            i = 1
            while BigBoard.status[BigBoard.where] and i < 12:
                BigBoard.where = (BigBoard.where + 1)%9
                i += 1

            self.r = .5
            self.g = .5
            self.b = .5

            if BigBoard.are_we_playing:
                function.changeColor(BigBoard.where, self.parent, 'red')
            else:
                BigBoard.where = -1

    def on_status(self, instance, new_value):
        status = new_value

        winner = function.ifSbWin(status)

        if winner:
            for child in self.children:
                child.background_color = (1, 1, 1, 0)
                child.background_normal = ""
            self.background_image = self.colorsGrey[winner]

            BigBoard.on_status(self, self.coords, winner)
