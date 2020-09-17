from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager


class GameOffline(Screen, BoxLayout):
    pass


class GameOnline(Screen):
    pass


class Manager(ScreenManager):
    gameOffline = ObjectProperty(None)
    gameOnline = ObjectProperty(None)
    menu = ObjectProperty(None)

    if_online = 0
    who_am_I = 0
