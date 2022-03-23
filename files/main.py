# ! /usr/bin/env python3
# "https://icons8.com/icon/6rhrZdzVI9KS/smart-tv">Smart Tv</a> icon by <a target="_blank" href="https://icons8.com">
# https://pixabay.com/users/maxxgirr-3565425/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=4532320
# https://mixkit.co/free-sound-effects/keyboard/
# https://www.freeimages.com/photo/blue-and-black-1170949
# https://www.freeimages.com/photo/blue-1184674

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.dropdown import DropDown
from kivy.support import install_twisted_reactor
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
import json
from time import time
from open_host import check_location, open_website
from kivy.utils import get_color_from_hex as C
# to use android functions like notifications, flash, battery and sensors >> use plyer module
from plyer import orientation as screen_orientation

# from plyer import notification

install_twisted_reactor()
from twisted.internet import reactor, protocol

FORMAT = "utf-8"
platform_name = "android"

if platform_name == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET, Permission.ACCESS_WIFI_STATE,
                         Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE,
                         Permission.CAPTURE_AUDIO_OUTPUT, Permission.WAKE_LOCK])


class Audio:
    def __init__(self):
        if platform_name == "android":
            from jnius import autoclass
            self.MediaPlayer = autoclass('android.media.MediaPlayer')
            self.audio = self.MediaPlayer()
            self.audio.setDataSource("Musics/mixkit-single-key-press-in-a-laptop-2541.mp3")
        else:
            self.audio = SoundLoader.load("Musics/mixkit-single-key-press-in-a-laptop-2541.wav")

    def play_audio(self):
        if platform_name == "android":
            try:
                self.audio.prepare()
                self.audio.start()
                Clock.schedule_once(self.close_audio, 0.22)
            except:
                self.audio = self.MediaPlayer()
                self.audio.setDataSource("Musics/mixkit-single-key-press-in-a-laptop-2541.mp3")
        else:
            self.audio = SoundLoader.load("Musics/mixkit-single-key-press-in-a-laptop-2541.wav")
            self.audio.play()

    def close_audio(self, *args):
        if platform_name == "android":
            try:
                self.audio.stop()
            except:
                pass


class RemoteClient(protocol.Protocol):
    def __init__(self):
        self.access = False
        self.connection_failure = False

    def connectionMade(self):
        print(f"Connected to {self.transport.getHost()}.")
        self.factory.app.connector(self.transport)
        self.factory.app.channel_opened = True
        if not self.access:
            self.factory.app.ask_connection()
        else:
            if self.connection_failure:
                self.factory.app.stop_waiting_popup()
                self.connection_failure = False

    def dataReceived(self, data):
        data = json.loads(data.decode(FORMAT))
        print("data received:", data)
        if data["ORDER"] == "ask access":
            if data["DATA"] == "access granted":
                self.factory.app.start_project()
                self.access = True
            elif data["DATA"] == "Baned":
                self.factory.app.stop_waiting_screen()
                self.factory.app.warning_popup("Your device has been baned !!")
            else:
                self.factory.app.stop_waiting_popup()
                self.factory.app.warning_popup("Wrong Password !!!")

        elif data["ORDER"] == "GREETING":
            servername = data["DATA"]
            self.factory.app.warning_popup(f"Connected to {servername}", "", (0, 0, 0, 0))
            self.factory.app.ids.label_1.text = servername.title()


class RemoteClientFactor(protocol.ReconnectingClientFactory):
    protocol = RemoteClient

    def __init__(self, app):
        self.app = app

    def startedConnecting(self, connector):
        print("trying to connect to localhost on port 6666 ...")

    def clientConnectionLost(self, connector, reason):
        print("connection lost: " + str(reason))
        self.protocol.connection_failure = True
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        self.app.start_waiting_popup(title="Connection Lost", separator_color=(0, 0, 1, 1))

    def clientConnectionFailed(self, connector, reason):
        print("connection failed: " + str(reason))
        self.protocol.connection_failure = True
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        self.app.start_waiting_popup(title="Connection Failed", separator_color=(0, 0, 1, 1))


class MY_Keyboard(VKeyboard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Main_widget(ScreenManager):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        # to access REMOTE_CONTROLLERApp class
        self.app = app
        self.audio = Audio()
        self.press_position = None
        self.open_popup = False
        self.open_popup_warning = False
        self.channel_opened = False
        # back button in android
        Window.bind(on_keyboard=self.Android_back_click)
        self.scroll_slower = 3
        self.move_slower = 1
        self.t1 = 0
        self.double_touch = False
        self.mouse_speed = 5
        self.open_website = open_website

    def set_other_screens(self):
        def open_screen(screen, *args):
            self.transition.direction = "right"
            if screen == "Settings":
                self.current = "settings_screen"
            else:
                self.current = "details_screen"

        dropdown = DropDown()
        target_button = self.ids.details_settings_selector
        for i in ["Settings", "Details"]:
            button = Button(text=str(i), size_hint_y=None, height="40sp", font_size="20sp",
                            background_color=(0, 0, 0, 0))
            button.bind(on_release=lambda button: dropdown.select(button.text))
            dropdown.add_widget(button)
        target_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, screen: open_screen(screen))

    def Android_back_click(self, window, key, *largs):
        def change_dir(*args):
            self.transition.direction = "left"

        if key == 27:
            if self.current == "screen_2":
                self.transition.direction = "right"
                self.set_other_screens()
                self.current = "screen_1"
                Clock.schedule_once(change_dir, 1)
            elif self.current in ["mouse_screen", "keyboard_screen", "video_control_screen"]:
                self.transition.direction = "right"
                self.current = "screen_2"
                Clock.schedule_once(change_dir, 1)
                try:
                    if platform_name == "android":
                        screen_orientation.set_portrait()
                except Exception as e:
                    print("Error:", e)
            elif self.current in ["settings_screen", "details_screen"]:
                self.transition.direction = "left"
                self.current = "screen_1"
            else:
                App.get_running_app().stop()
            return True

    # ============== Warning pop up.
    def warning_popup(self, text, title="Warning", separator_color=(0, 0, 1, 1)):
        self.displayed_warning_popup = False

        def checker(first, *args):
            if not self.open_popup_warning and not self.displayed_warning_popup:
                self.displayed_warning_popup = True
                if first:
                    clock.cancel()
                self.open_popup_warning = True
                box = BoxLayout(orientation="vertical", spacing=10, padding=10)
                button = Button(text="okay", size_hint_y=0.3,
                                font_size="20sp", background_color=(0, 0, 0, 0))
                box.add_widget(Label(text="", size_hint_y=0.1))
                box.add_widget(
                    Label(text=text,
                          size_hint_y=0.3,
                          font_size="20sp"))
                box.add_widget(button)
                popup = Popup(title=title, content=box,
                              size_hint=(0.75, 0.35), title_align="center", title_size="18sp",
                              separator_color=separator_color)
                popup.background_color = C("#3B5BFD")
                popup.open()

                def dismiss_popup(*args):
                    self.open_popup_warning = False
                    popup.dismiss()

                button.bind(on_release=dismiss_popup)
                return True
            else:
                return False

        checker_value = checker(0)
        if not checker_value:
            clock = Clock.schedule_interval(checker, 5)

    # ========== waiting popup.
    def start_waiting_popup(self, *args, title=" ", separator_color=(0, 0, 0, 0)):
        if not self.open_popup:
            self.waiting_popup(title, separator_color)
            self.wait_schedule = Clock.schedule_interval(self.wait_clock, 1)
            self.open_popup = True

    def wait_clock(self, *args):
        widget = self.wait_text
        if widget.text == ". . . ":
            widget.text = ""
        else:
            widget.text += ". "

    def waiting_popup(self, title, separator_color):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.wait_text = Label(text=". ", color=(0, 0, 1), font_size="34sp")
        box.add_widget(Label(text="",size_hint_y=0.1))
        box.add_widget(Label(text="Please Wait", size_hint_y=0.1, font_size="30sp"))
        box.add_widget(self.wait_text)
        self.popup_wait = Popup(content=box, size_hint=(0.75, 0.3), auto_dismiss=False, title=title,
                                separator_color=separator_color, title_align="center")
        self.popup_wait.background_color = (0, 0, 0.1)
        self.popup_wait.open()

    def stop_waiting_popup(self, *args):
        if self.open_popup:
            self.wait_schedule.cancel()
            self.popup_wait.dismiss()
            self.open_popup = False

    # =========

    def ask_connection(self):
        self.connection_request = False

        def check_channel_local(*args):
            if not self.channel_opened:
                if not self.connection_request:
                    value = self.check_channel(self.ids.local_host.text)
                    self.connection_request = True
                    if not value:
                        clock.cancel()


            else:
                clock.cancel()
                Clock.schedule_once(self.stop_waiting_popup)
                self.send_msg("ask access", self.ids.passwd.text)

        Clock.schedule_once(self.start_waiting_popup)
        clock = Clock.schedule_interval(check_channel_local, 5)

    def start_project(self):
        self.stop_waiting_popup()
        self.current = "screen_2"

    def on_touch_down(self, touch):
        if ScreenManager.on_touch_up(self, touch):
            return
        if self.current == "mouse_screen":
            self.press_position = (touch.x, touch.y)
            if (time() - self.t1) <= 0.5 and self.t1:
                self.send_msg("action", "left press", "mouse")
                self.double_touch = True
            self.t1 = time()
        elif self.current == "keyboard_screen":
            pass
        elif self.current == "video_control_screen":
            pass

    def on_touch_move(self, touch):
        if ScreenManager.on_touch_move(self, touch):
            return
        if self.current == "mouse_screen":
            t2 = time() - self.t1
            speed = ((touch.x - self.press_position[0]) / self.mouse_speed,
                     -(touch.y - self.press_position[1]) / self.mouse_speed)
            if (self.press_position[0] / self.width) < 0.8:
                if self.move_slower == 1:
                    self.send_msg("action", "move", "mouse", speed)
                    self.move_slower = 0
                else:
                    self.move_slower += 1
            else:
                if self.scroll_slower == 3:
                    self.send_msg("action", "scroll", "mouse", speed)
                    self.scroll_slower = 0
                else:
                    self.scroll_slower += 1

        elif self.current == "keyboard_screen":
            pass
        elif self.current == "video_control_screen":
            pass

    def on_touch_up(self, touch):
        if ScreenManager.on_touch_down(self, touch):
            return
        if self.current == "mouse_screen":
            t2 = time() - self.t1
            if t2 <= 0.8 and abs(touch.x - self.press_position[0]) <= 20 and abs(
                    touch.y - self.press_position[1]) <= 20:
                self.send_msg("action", "left click", "mouse")
            elif self.double_touch:
                self.send_msg("action", "left release", "mouse")
        elif self.current == "keyboard_screen":
            pass
        elif self.current == "video_control_screen":
            pass

    def connector(self, transport):
        self.transport = transport

    def check_channel(self, host):
        print("host:", host)
        if check_location(host, 6666):
            self.open_channel(host)
            return True
        else:
            self.warning_popup("Host isn't opened.")
            self.stop_waiting_popup()
            return False

    def open_channel(self, host):
        reactor.connectTCP(host, 6666, RemoteClientFactor(self))

    def send_msg(self, order, data, action_type="", value=None):
        if value and type(value) == tuple:
            value = [round(value[0], 0), round(value[1], 0)]

        msg = {"ORDER": order, "DATA": data, "TYPE": action_type, "VALUE": value}
        msg = json.dumps(msg)
        msg = msg.encode(FORMAT)
        self.transport.write(msg)

    def set_orientation(self, *args):
        try:
            if platform_name == "android":
                screen_orientation.set_landscape()
        except Exception as e:
            print("Error:", e)

    def add_keyboard(self):
        def get_keyboard_screen(*args):
            keyboard = MY_Keyboard(pos_hint={"x": 0, "y": 0}, size_hint=(1, 1),
                                   background_color=C("#26005400"), key_background_color=C("#617AF6"),
                                   font_size="15sp")
            keyboard.bind(on_key_down=self.key_down)
            keyboard.bind(on_key_up=self.key_up)
            self.ids.keyboard_id.add_widget(keyboard)
            self.current = "keyboard_screen"
            self.keyboard = keyboard

        self.set_orientation()

        Clock.schedule_once(get_keyboard_screen, 1)

    def key_up(self, keyboard, keycode, internal, modifiers, *args):
        self.audio.play_audio()
        if isinstance(keycode, tuple):
            keycode = keycode[1]
        if keycode == "escape":
            keycode = "esc"
        elif keycode == "capslock":
            keycode = "caps_lock"
        elif keycode == "layout":
            keycode = "print_screen"
        elif keycode == "spacebar":
            keycode = "space"
        print("internal:", internal, "keycode:", keycode)
        if internal is None or internal in [" ", "\t"]:
            self.send_msg("action", "release", "type_keyboard", keycode)
        else:
            self.send_msg("action", "release", "type_keyboard", internal)

    def key_down(self, keyboard, keycode, internal, *args):
        if isinstance(keycode, tuple):
            keycode = keycode[1]
        if keycode == "escape":
            keycode = "esc"
        elif keycode == "capslock":
            keycode = "caps_lock"
        elif keycode == "layout":
            keycode = "print_screen"
        elif keycode == "spacebar":
            keycode = "space"
        if internal is None or internal in [" ", "\t"]:
            self.send_msg("action", "release", "type_keyboard", keycode)
        else:
            self.send_msg("action", "release", "type_keyboard", internal)


class REMOTE_CONTROLLERApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        widget = Main_widget(self)
        widget.set_other_screens()
        return widget


if __name__ == "__main__":
    # adding fonts, you can call them using font_name property.
    LabelBase.register('fonts', 'Fonts/ArialUnicodeMS.ttf')
    LabelBase.register("shapes", "Fonts/Font_90_Icons.ttf")
    LabelBase.register("shapes2", "Fonts/modernpics.otf")

    # to adjust the app when the keyboard rises
    from kivy.core.window import Window

    Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
    Window.softinput_mode = "below_target"
    # to add a color in the background of the app.
    Window.clearcolor = (169.0 / 255, 172.0 / 255, 175.0 / 255, 0)
    REMOTE_CONTROLLERApp().run()

# def notifier(title="Notification", message="notification message", timeout=5):
#     # notification.notify(title = title, message=message,timeout=timeout,app_icon="Images/icon.png",
#     # app_name="NOTIFICATION",ticker = "1") use notification with audio.start()  #only for android
#     print(title)
