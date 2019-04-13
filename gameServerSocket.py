from functools import partial

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from function import goToScreen, plusSec, timer, changeButton, changeColor, ifSbWin
from board import BigBoard
import connection

class GameOffline(Screen, BoxLayout):
    pass

class GameOnline(Screen):
    pass

class PasekBoczny(BoxLayout):
    timeInGame = StringProperty("00 : 00")
    want_reset = None
    background_image = StringProperty("assets/X.png")

    def reset(self, yes=0):
        if App.get_running_app().man.if_online == 0 or yes == 1: 
            App.get_running_app().waiting_for_answer = 0
            try:
                self.want_reset.dismiss()
            except:
                pass
            self.parent.parent.ids.gra.status = [0]*9
            BigBoard.current_player = -1
            BigBoard.status = [0]*9
            try:
                App.get_running_app().clock_timer.cancel()
            except:
                pass
            BigBoard.MinTime = "00"
            self.parent.parent.ids.pasek.timeInGame = "00 : 00"
            BigBoard.where = -1
            BigBoard.are_we_playing = True
            for child in self.parent.parent.ids.gra.children:
                child.status = [0]*9
                child.still_playing = 1
                child.background_image = ''
                for button in child.children:
                    button.background_normal = ""
                    button.background_color = (.32, .32, .32, 1)
                child.r = .5
                child.g = .5
                child.b = .5

        elif App.get_running_app().man.if_online == 1:
            self.want_reset = ModalView(size_hint=(.75, .5))
            reset_text = Label(text="waiting for opponent", font_size=50)
            App.get_running_app().waiting_for_answer = 1
            self.want_reset.add_widget(reset_text)
            App.get_running_app().s.reset()
            self.want_reset.open()
        
    def if_u_want_reset(self):
        self.want_reset = Popup(size_hint=(.75, .5), auto_dismiss=False, title='')
        reset_text = Label(text="Do you want to reset?", font_size=50)

        box = BoxLayout(orientation='vertical')
        butt_no = Button(text="No")
        butt_no.bind(on_release=App.get_running_app().s.send_answer_no)
        butt_no.bind(on_release=self.want_reset.dismiss)
        butt_yes = Button(text="Yes")
        butt_yes.bind(on_release=App.get_running_app().s.send_answer_yes)
        butt_yes.bind(on_release=self.want_reset.dismiss)
        butt_yes.bind(on_release=lambda x:self.reset(1))

        box.add_widget(reset_text)
        box.add_widget(butt_no)
        box.add_widget(butt_yes)
        self.want_reset.add_widget(box)
        self.want_reset.open()

    def goTo(self, whichScreen):
        self.parent.parent.manager.current = "screen" + str(whichScreen)
    
    def disconnect(self):
        if App.get_running_app().man.if_online == 1:
            App.get_running_app().man.if_online = 0
            App.get_running_app().man.who_am_I = 0
            App.get_running_app().state = "in_menu"
            # print("disconnect")
            App.get_running_app().s.stop()

class Menu(Screen):
    que = None
    leave = None

    def connectToServer(self):
        BigBoard.are_we_playing = True
        App.get_running_app().setState("in_queue")
        self.que = ModalView(size_hint=(.75, .5))
        time_text = Label(text="00 : 00", font_size=50, id="time_text")
        App.get_running_app().clock_timer = Clock.schedule_interval(self.timer_for_que, 1.000)
        self.que.bind(on_dismiss=self.leave_queue_on_dismiss)
        self.que.add_widget(time_text)
        self.que.open()
        TicTacToeApp.que_for_game(App.get_running_app())
    
    def cancel_timer_and_set_menu(self):
        App.get_running_app().clock_timer.cancel()
        App.get_running_app().setState("in_menu")

    def leave_queue_on_dismiss(self, dt):
        if App.get_running_app().state == "in_queue":
            self.cancel_timer_and_set_menu()
            App.get_running_app().s.stop()

    def leave_queue_on_join(self):
        self.cancel_timer_and_set_menu()
        self.que.dismiss()

    def timer_for_que(self, dt):
        self.que.children[0].text = plusSec(self.que.children[0].text)

    def back_to_menu(self):
        self.leave = ModalView(size_hint=(.75, .5))
        text = Label(text="Your opponent leave", font_size=50)
        self.leave.bind(on_dismiss=lambda x:goToScreen(1))
        self.leave.add_widget(text)
        self.leave.open()
        App.get_running_app().man.if_online = 0
        App.get_running_app().man.who_am_I = 0
        App.get_running_app().state = "in_menu"
        App.get_running_app().man.ids.screen_game_online.ids.pasek.reset()

class Manager(ScreenManager):
    gameOffline = ObjectProperty(None)
    gameOnline = ObjectProperty(None)
    menu = ObjectProperty(None)

    if_online = 0
    who_am_I = 0
    
class TicTacToeApp(App):
    state = "in_menu"
    man = None
    s = None
    clock_timer = None
    waiting_for_answer = 0

    def build(self):
        self.man = Manager()
        return self.man
    
    def getMan(self):
        return self.man
    
    def getState(self):
        return self.state
    
    def setState(self, val):
        self.state = val

    def que_for_game(self):
        self.s = connection.ThreadedClient()
        self.s.start()

if __name__ == '__main__': 
    TTApp = TicTacToeApp()
    TTApp.run()