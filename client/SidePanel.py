from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from client.board import BigBoard


class SidePanel(BoxLayout):
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
            self.parent.parent.ids.gra.status = [0] * 9
            BigBoard.current_player = -1
            BigBoard.status = [0] * 9
            try:
                App.get_running_app().clock_timer.cancel()
            except:
                pass
            BigBoard.MinTime = "00"
            self.parent.parent.ids.pasek.timeInGame = "00 : 00"
            BigBoard.where = -1
            BigBoard.are_we_playing = True
            for child in self.parent.parent.ids.gra.children:
                child.status = [0] * 9
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
        butt_yes.bind(on_release=lambda x: self.reset(1))

        box.add_widget(reset_text)
        box.add_widget(butt_no)
        box.add_widget(butt_yes)
        self.want_reset.add_widget(box)
        self.want_reset.open()

    def go_to(self, which_screen):
        self.parent.parent.manager.current = "screen" + str(which_screen)

    @staticmethod
    def disconnect():
        if App.get_running_app().man.if_online == 1:
            App.get_running_app().man.if_online = 0
            App.get_running_app().man.who_am_I = 0
            App.get_running_app().state = "in_menu"
            # print("disconnect")
            App.get_running_app().s.stop()
