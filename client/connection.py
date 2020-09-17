import threading
import socket
from kivy.app import App

from client.function import change_to_game, change_button

HOST = 'localhost'
PORT = 8080


class ThreadedClient(threading.Thread):
    s = None

    def __init__(self):
        threading.Thread.__init__(self)

    def stop(self):
        # print("function stop")
        self.s.send("Close1".encode('ascii'))
        self.s.close()

    def reset(self):
        # print("function reset")
        self.s.send("reset".encode('ascii'))

    def send_answer_no(self, answer):
        self.s.send("no".encode('ascii'))

    def send_answer_yes(self, answer):
        # print("function yes")
        self.s.send("yes".encode('ascii'))

    def send_move(self, move):
        self.s.send(move)

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.s.send("C".encode('ascii'))
        data = self.s.recv(1024)
        data = data.decode('ascii')

        if data == "leave":
            self.s.close()
            return
        App.get_running_app().set_state("in_game")
        App.get_running_app().get_man().menu.leave_queue_on_join()
        change_to_game(int(data))

        while App.get_running_app().get_state() == "in_game":
            data = self.s.recv(1024)
            data = data.decode('ascii')

            if data == "leave" or data == "leaveleave":
                if App.get_running_app().state == "in_game":
                    App.get_running_app().man.menu.back_to_menu()
                self.s.close()
                return
            elif data == "reset":
                App.get_running_app().waiting_for_answer = 1
                App.get_running_app().man.ids.screen_game_online.ids.pasek.if_u_want_reset()
            elif data == "yes":
                # print("reset")
                App.get_running_app().waiting_for_answer = 0
                App.get_running_app().man.ids.screen_game_online.ids.pasek.reset(1)
                if App.get_running_app().man.who_am_I == 1:
                    print(App.get_running_app().man.who_am_I, "who am i ")
            elif data == "no":
                App.get_running_app().waiting_for_answer = 0
                try:
                    App.get_running_app().man.ids.screen_game_online.ids.pasek.want_reset.dismiss()
                except:
                    pass
            else:
                change_button(data)
