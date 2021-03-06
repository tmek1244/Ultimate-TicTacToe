from functools import partial

from kivy.app import App
from kivy.clock import Clock

from client.board import BigBoard


def go_to_screen(where):
    App.get_running_app().man.current = "screen" + str(where)


def plus_sec(time):
    time = time.split(' : ')
    if time[1] == '59':
        time[1] = '00'
        time[0] = str(int(time[0]) + 1)
    else:
        time[1] = str(int(time[1]) + 1)
        if int(time[1]) < 10:
            time[1] = '0' + time[1]
    return time[0] + ' : ' + time[1]


def timer(mode, dt):
    side_panel = App.get_running_app().get_man().ids
    if mode == "offline":
        side_panel = side_panel.screen_game_offline.ids.pasek
    elif mode == "online":
        side_panel = side_panel.screen_game_online.ids.pasek
    side_panel.timeInGame = plus_sec(side_panel.timeInGame)


def change_color(where, root, color):
    for child in root.children:
        if child.coords == where:
            if not App.get_running_app().get_man().if_online and BigBoard.current_player == 1:
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


def if_sb_win(tab):
    sums = [  # rows
        sum(tab[0:3]),
        # columns
        sum(tab[3:6]),
        sum(tab[6:9]),
        sum(tab[0::3]),
        # diagonals
        sum(tab[1::3]),
        sum(tab[2::3]),
        sum(tab[::4]),
        sum(tab[2:-2:2])]

    if 3 in sums:
        return 1
    if -3 in sums:
        return -1
    if 0 not in tab:
        return 6


def change_to_game(who_am_i):
    who = {1: 'assets/O.png', -1: 'assets/X.png'}
    App.get_running_app().man.ids.screen_game_online.ids.pasek.background_image = who[who_am_i]
    App.get_running_app().get_man().if_online = 1
    App.get_running_app().get_man().who_am_I = who_am_i
    App.get_running_app().get_man().current = "screen3"
    App.get_running_app().set_state("in_game")
    BigBoard.clockTimer = True
    App.get_running_app().clock_timer = Clock.schedule_interval(partial(timer, "online"), 1.000)


def change_button(data):
    colors = {1: 'assets/X.png', -1: 'assets/O.png', 6: 'assets/draw.png'}
    x = (child for child in App.get_running_app().get_man().gameOnline.ids.gra.children if
         child.coords == int(data[0]))
    for child in x:
        for butt in child.children:
            if butt.coords == int(data[1]):
                # print(data)
                # changeButton(butt, child)
                BigBoard.are_we_playing = True
                BigBoard.current_player *= -1
                butt.background_color = (1, 1, 1, 1)
                butt.background_normal = colors[BigBoard.current_player]
                child.status[butt.coords] = BigBoard.current_player
                BigBoard.where = butt.coords
                i = 1
                while BigBoard.status[BigBoard.where] and i < 12:
                    BigBoard.where = (BigBoard.where + 1) % 9
                    i += 1
                child.r = .5
                child.g = .5
                child.b = .5
                if BigBoard.are_we_playing:
                    change_color(BigBoard.where, child.parent, '')
                else:
                    BigBoard.where = -1
                change_color(BigBoard.where, child.parent, '')
