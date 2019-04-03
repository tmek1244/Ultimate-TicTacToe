import threading
import queue
import socket
import sys
import asyncore
import logging

from functools import partial

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('log.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

HOST = '168.63.65.239'
PORT = 8080

def timer(self, dt):
    if int(BigBoard.SecTime) == 59:
        BigBoard.MinTime = str(int(BigBoard.MinTime) + 1)
        BigBoard.SecTime = "00"
    else:
        BigBoard.SecTime = str(int(BigBoard.SecTime) + 1)
    if 0 < int(BigBoard.SecTime) < 10:
        BigBoard.SecTime = '0'+BigBoard.SecTime
    elif BigBoard.SecTime == "0":
        BigBoard.SecTime = "00"
    self.ids.pasek.timeInGame = BigBoard.MinTime + ' : ' + BigBoard.SecTime
    #print(self.parent.parent.ids.pasek.timeInGame)
    return BigBoard.clockTimer

def changeColor(where, root, color):
    for child in root.children:
        if child.coords == where:
            #print(rootA.size)
            if not App.get_running_app().getMan().if_online and BigBoard.current_player == 1:
                child.r = .5
                child.g = .5
                child.b = 1
            elif color != 'red':
                child.r = .1
                child.g = 1
                child.b = .1
            else:
                child.r = .7
                child.g = .2
                child.b = .1

def ifSbWin(tab):
    sums = [	#rows
                sum(tab[0:3]),
                #columns
                sum(tab[3:6]),
                sum(tab[6:9]),
                sum(tab[0::3]),
                #diagonals
                sum(tab[1::3]),
                sum(tab[2::3]),
                sum(tab[::4]),
                sum(tab[2:-2:2])]

    if 3 in sums:
        return 1
    if -3 in sums:
        return -1
    if 0 not in tab:
        return 5

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

        win = ifSbWin(BigBoard.status)
        winner = ''
        if win == 1:
            winner = "Wygral 1 gracz!"
        elif win == -1:
            winner = "Wygral 2 gracz!"
        elif win == 5:
            winner = "Remis!"

        if winner:
            popup = ModalView(size_hint = (0.75 , 0.5))
            victory_label = Label(text = winner, font_size = 50)
            print("winner")
            popup.add_widget(victory_label)
            self.clockTimer = False
            #popup.bind(on_dismiss = self.parent.parent.parent.ids.pasek.reset())
            popup.open()
            self.parent.parent.parent.ids.pasek.reset()

class TicTacToeGrid(GridLayout):

    status = ListProperty([0, 0, 0,
                           0, 0, 0,
                           0, 0, 0])

    still_playing = NumericProperty(1)
    r = NumericProperty(.5)
    g = NumericProperty(.5)
    b = NumericProperty(.5)


    colors = {1: 'assets/X.png', -1: 'assets/O.png', 5: 'assets/draft.png'}

    def button_pressed(self, button):
        BigBoard.are_we_playing = True
        if ((self.coords == BigBoard.where or BigBoard.where == -1) and
            not self.status[button.coords] and self.still_playing
            and (int(App.get_running_app().getMan().who_am_I) == int(BigBoard.current_player)
            or not App.get_running_app().getMan().if_online)):
            if BigBoard.where == -1 and App.get_running_app().getMan().if_online == False:
                BigBoard.clockTimer = True
                Clock.schedule_interval(partial(timer, self.parent.parent.parent), 1.000)

            BigBoard.current_player *= -1
            button.background_color = (1, 1, 1, 1)
            button.background_normal = self.colors[BigBoard.current_player]
            self.status[button.coords] = BigBoard.current_player
            BigBoard.where = button.coords
            if App.get_running_app().getMan().if_online:
                print("jestem")
                data = str(self.coords) + str(button.coords)
                App.get_running_app().getQ().put(data.encode('ascii'))
                #App.get_running_app().getQ().task_done()

            i = 1
            while BigBoard.status[BigBoard.where] and i < 12:
                BigBoard.where = (BigBoard.where + 1)%9
                i += 1
            self.r = .5
            self.g = .5
            self.b = .5
            if BigBoard.are_we_playing:
                changeColor(BigBoard.where, self.parent, 'red')
            else:
                BigBoard.where = -1

    def on_status(self, instance, new_value):
        #print("tutaj2")
        status = new_value

        winner = ifSbWin(status)

        if winner:
            self.still_playing = 0
            for child in self.children:
                child.background_color = (0, 0, 0, 0)
            self.canvas.add(Rectangle(group="additional", pos=self.pos, size=self.size, source=self.colors[winner]))
            BigBoard.on_status(self, self.coords, winner)

class GameOffline(Screen, BoxLayout):
    pass

class GameOnline(Screen):
    pass

class PasekBoczny(BoxLayout):
    timeInGame = StringProperty("00 : 00")
    
    def reset(self):
        print(self)
        self.parent.parent.ids.gra.status = [0]*9
        BigBoard.current_player = -1
        BigBoard.status = [0]*9
        BigBoard.clockTimer = False
        BigBoard.SecTime = "-1"
        BigBoard.MinTime = "00"
        BigBoard.are_we_playing = False
        self.parent.parent.ids.pasek.timeInGame = "00 : 00"
        BigBoard.where = -1
        for child in self.parent.parent.ids.gra.children:
            child.status = [0]*9
            child.still_playing = 1
            for button in child.children:
                button.background_normal = ""
                button.background_color = (.32, .32, .32, 1)
            child.r = .5
            child.g = .5
            child.b = .5
            if child.canvas.get_group("additional") != {}:
                for additional in child.canvas.get_group("additional"):
                    #print(additional)
                    try:
                        child.canvas.remove(additional)
                    except:
                        pass
    
    def goTo(self, whichScreen):
        #print(whichScreen)

        self.parent.parent.manager.current = "screen" + str(whichScreen)

class Menu(Screen):
    def connectToServer(self):
        TicTacToeApp.que_for_game(App.get_running_app())
    
    def killThread(self):
        TicTacToeApp.kill(App.get_running_app())

class Manager(ScreenManager):
    gameOffline = ObjectProperty(None)
    gameOnline = ObjectProperty(None)
    menu = ObjectProperty(None)

    if_online = 0
    who_am_I = 0
    
class ThreadedClient(threading.Thread):
    s = None
    if_run = True
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        #print(dir(App.get_running_app().getMan().gameonline))
        #print(App.get_running_app().getMan().menu)

    def change_if_run(self):
        self.if_run = False

    def run(self):
        #print(self.if_run)
        if not self.if_run:
            return
        App.get_running_app().getMan().if_online = True
        if(not App.get_running_app().getState() == "in_queue"):
            App.get_running_app().setState("in_queue")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((HOST, PORT))
            self.s.send("C".encode('ascii'))
            while self.if_run:
                #print(self.if_run)
                data = self.s.recv(1024)
                data = data.decode('ascii')
                if data == "1" and not App.get_running_app().getState() == "in_game": 
                    App.get_running_app().getMan().ids.screen_game_online.ids.pasek.ids.whosplaying.text="O"
                    App.get_running_app().getMan().if_online = 1
                    App.get_running_app().getMan().who_am_I = data
                    App.get_running_app().getMan().current="screen3"
                    App.get_running_app().setState("in_game")
                    BigBoard.clockTimer = True
                    Clock.schedule_interval(partial(timer, App.get_running_app().getMan().ids.screen_game_online), 1.000)
                elif data == "-1" and not App.get_running_app().getState() == "in_game": 
                    App.get_running_app().getMan().ids.screen_game_online.ids.pasek.ids.whosplaying.text="X"
                    App.get_running_app().getMan().if_online = 1
                    App.get_running_app().getMan().who_am_I = data
                    App.get_running_app().getMan().current="screen3"
                    App.get_running_app().setState("in_game")
                    BigBoard.clockTimer = True
                    Clock.schedule_interval(partial(timer, App.get_running_app().getMan().ids.screen_game_online), 1.000)
                    self.w8_for_move()
                elif App.get_running_app().getState() == "in_game":
                    #print(dir(App.get_running_app().getMan().gameOnline.ids.gra))
                    print(data)
                    for child in App.get_running_app().getMan().gameOnline.ids.gra.children:
                        if child.coords == (int)(data[0]):
                            for butt in child.children:
                                if butt.coords == (int)(data[1]):
                                    print(data)
                                    BigBoard.current_player *= -1
                                    butt.background_color = (1, 1, 1, 1)
                                    butt.background_normal = TicTacToeGrid.colors[BigBoard.current_player]
                                    child.status[butt.coords] = BigBoard.current_player
                                    BigBoard.where = butt.coords
                                    i = 1
                                    while BigBoard.status[BigBoard.where] and i < 12:
                                        BigBoard.where = (BigBoard.where + 1)%9
                                        i += 1
                                    child.r = .5
                                    child.g = .5
                                    child.b = .5
                                    changeColor(BigBoard.where, child.parent, '')
                    self.w8_for_move()

    def w8_for_move(self):
        que = App.get_running_app().getQ()
        #print(self)
        while self.if_run:
            #print(self.if_run)
            if not que.empty():
                data = que.get()
                que.task_done()
                self.s.send(data)
                #print(data.decode('ascii'))
                return

    def join(self, timeout=None):
        self._stop_event.set()
        threading.Thread.join(self, timeout)

    def stopped(self):
        return self._stop_event.is_set()

class AsyncClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((HOST, PORT))
        self.send("C".encode('ascii'))
    def handle_connect(self):
        print("cossd")
    def handle_close(self):
        self.close()        


class TicTacToeApp(App):
    state = "in_menu"
    man = None
    s = None
    q = queue.Queue()

    def build(self):
        self.man = Manager()
        logger.error("cos tam wiadomosc2")
        return self.man
    
    def getMan(self):
        return self.man
    
    def getState(self):
        return self.state
    
    def setState(self, val):
        self.state = val
    
    def getQ(self):
        return self.q

    def que_for_game(self):
        self.connect()

    def connect(self):
        #self.s = ThreadedClient()
        #self.s.start()
        self.s = AsyncClient()
        asyncore.loop()

    def kill(self):
        #self.s.join()
        sys.exit()


if __name__ == '__main__': 
    logger.error("cos tam wiadomosc1")
    TTApp = TicTacToeApp()
    TTApp.run()