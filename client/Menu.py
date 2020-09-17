from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen

from client.board import BigBoard
from client.function import go_to_screen, plus_sec
from client.mainApp import TicTacToeApp


class Menu(Screen):
    que = None
    leave = None

    def connect_to_server(self):
        BigBoard.are_we_playing = True
        App.get_running_app().set_state("in_queue")
        self.que = ModalView(size_hint=(.75, .5))
        time_text = Label(text="00 : 00", font_size=50, id="time_text")
        App.get_running_app().clock_timer = Clock.schedule_interval(self.timer_for_que, 1.000)
        self.que.bind(on_dismiss=self.leave_queue_on_dismiss)
        self.que.add_widget(time_text)
        self.que.open()
        TicTacToeApp.que_for_game(App.get_running_app())

    @staticmethod
    def cancel_timer_and_set_menu():
        App.get_running_app().clock_timer.cancel()
        App.get_running_app().set_state("in_menu")

    def leave_queue_on_dismiss(self, dt):
        if App.get_running_app().state == "in_queue":
            self.cancel_timer_and_set_menu()
            App.get_running_app().s.stop()

    def leave_queue_on_join(self):
        self.cancel_timer_and_set_menu()
        self.que.dismiss()

    def timer_for_que(self, dt):
        self.que.children[0].text = plus_sec(self.que.children[0].text)

    def back_to_menu(self):
        self.leave = ModalView(size_hint=(.75, .5))
        text = Label(text="Your opponent leave", font_size=50)
        self.leave.bind(on_dismiss=lambda x: go_to_screen(1))
        self.leave.add_widget(text)
        self.leave.open()
        App.get_running_app().man.if_online = 0
        App.get_running_app().man.who_am_I = 0
        App.get_running_app().state = "in_menu"
        App.get_running_app().man.ids.screen_game_online.ids.pasek.reset()
