#!/usr/bin/env python
from twisted.internet import reactor, protocol
import json
from pynput.mouse import Controller as Controller_1
from pynput.keyboard import Controller as Controller_2
from pynput.mouse import Button
from pynput.keyboard import Key
from display import *
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
try:
    SERVER = (s.getsockname()[0], 6666)
except:
    warning_print("please connect to a wifi")
    SERVER = ("127.0.0.1", 6666)

Keyboard = Controller_2()
Mouse = Controller_1()

transports = {}
FORMAT = "utf-8"

server_name = quest_input("Enter Your server name: ")
passwd = quest_input("Enter your password: ")
normal_print(("Your Local host:", SERVER[0]))


class Remote(protocol.Protocol):
    def __init__(self):
        self.previous = ""
        self.access = False
        self.caps_lock = False

    def dataReceived(self, data):
        data = data.decode(FORMAT)
        try:
            data = json.loads(data)
            self.analyze_data(data)
        except:
            data_list = ["{" + x for x in data.split("{")[1:]]
            for i in data_list:
                data = json.loads(i)
                if not (data["TYPE"] == "type_keyboard" and data == self.previous):
                    self.analyze_data(data)
                    self.previous = data
            self.previous = ""

    def analyze_data(self, data):
        if data["ORDER"] == "ask access":
            if data["DATA"] == passwd and transports[self.transport] <= 7:
                self.send_msg("ask access", "access granted")
                self.access = True
                transports[self.transport] = 0

            elif transports[self.transport] > 7:
                self.send_msg("ask access", "Baned")
                warning_print(f"{self.transport} tried more than 7 times to connect to server!!")
            else:
                transports[self.transport] += 1
                fail_print(("Failed connection request:", self.transport))
                self.send_msg("ask access", "Failed")

        elif self.access and data["ORDER"] == "action":
            self.give_control(data)

    def send_msg(self, order, data):
        msg = {"ORDER": order, "DATA": data}
        msg = json.dumps(msg)
        msg = msg.encode(FORMAT)
        self.transport.write(msg)

    def connectionMade(self):
        normal_print(f"Connected to {self.transport.getHost()}.")
        if self.transport not in transports.keys():
            transports[self.transport] = 0
            self.send_msg("GREETING", server_name)

    def give_control(self, data):
        if data["TYPE"] == "mouse":
            if data["DATA"] == "left click":
                Mouse.click(Button.left)
            elif data["DATA"] == "right click":
                Mouse.click(Button.right)
            elif data["DATA"] == "middle click":
                Mouse.click(Button.middle)
            elif data["DATA"][-5:] == "press":
                if data["DATA"].split(" ")[0] == "left":
                    Mouse.press(Button.left)
                elif data["DATA"].split(" ")[0] == "right":
                    Mouse.press(Button.right)
                else:
                    Mouse.press(Button.middle)
            elif data["DATA"][-7:] == "release":
                if data["DATA"].split(" ")[1] == "left":
                    Mouse.release(Button.left)
                elif data["DATA"].split(" ")[0] == "right":
                    Mouse.release(Button.right)
                else:
                    Mouse.release(Button.middle)
            elif data["DATA"] == "move":
                Mouse.move(data["VALUE"][0], data["VALUE"][1])
            elif data["DATA"] == "scroll":
                Mouse.scroll(data["VALUE"][0]/2, data["VALUE"][1]/2)

        elif data["TYPE"] == "type_keyboard":
            if data["DATA"] == "release":
                if data["VALUE"] in ["space", "tab", "print_screen", "esc", "shift", "enter", "caps_lock",
                                     "print_screen", "backspace"]:
                    Keyboard.tap(getattr(Key, data["VALUE"]))
                else:
                    Keyboard.tap(data["VALUE"])

        elif data["TYPE"] == "video_player":
            if data["VALUE"] == "press":
                Keyboard.press(getattr(Key, data["DATA"]))
            else:
                Keyboard.release(getattr(Key, data["DATA"]))


class RemoteFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Remote()


if __name__ == '__main__':
    reactor.listenTCP(6666, RemoteFactory())

    reactor.run()

# alt = <Key.alt: <65513>>
#  |
#  |  alt_gr = <Key.alt_gr: <65406>>
#  |
#  |  alt_r = <Key.alt_r: <65514>>
#  |
#  |  backspace = <Key.backspace: <65288>>
#  |
#  |  caps_lock = <Key.caps_lock: <65509>>
#  |
#  |  cmd = <Key.cmd: <65515>>
#  |
#  |  cmd_r = <Key.cmd_r: <65516>>

#  |  ctrl = <Key.ctrl: <65507>>
#  |
#  |  ctrl_r = <Key.ctrl_r: <65508>>
#  |
#  |  delete = <Key.delete: <65535>>
#  |
#  |  down = <Key.down: <65364>>
#  |
#  |  end = <Key.end: <65367>>
#  |
#  |  enter = <Key.enter: <65293>>
#  |
#  |  esc = <Key.esc: <65307>>
#  |
#  |  f1 = <Key.f1: <65470>>
#  |
#  |  f10 = <Key.f10: <65479>>
#  |
#  |  f11 = <Key.f11: <65480>>
#  |
#  |  f12 = <Key.f12: <65481>>
#  |
#  |  f13 = <Key.f13: <65482>>

#  |  f14 = <Key.f14: <65483>>
#  |
#  |  f15 = <Key.f15: <65484>>
#  |
#  |  f16 = <Key.f16: <65485>>
#  |
#  |  f17 = <Key.f17: <65486>>
#  |
#  |  f18 = <Key.f18: <65487>>
#  |
#  |  f19 = <Key.f19: <65488>>
#  |
#  |  f2 = <Key.f2: <65471>>
#  |
#  |  f20 = <Key.f20: <65489>>
#  |
#  |  f3 = <Key.f3: <65472>>
#  |
#  |  f4 = <Key.f4: <65473>>
#  |
#  |  f5 = <Key.f5: <65474>>
#  |
#  |  f6 = <Key.f6: <65475>>
# f6 = <Key.f6: <65475>>
#  |
#  |  f7 = <Key.f7: <65476>>
#  |
#  |  f8 = <Key.f8: <65477>>
#  |
#  |  f9 = <Key.f9: <65478>>
#  |
#  |  home = <Key.home: <65360>>
#  |
#  |  insert = <Key.insert: <65379>>
#  |
#  |  left = <Key.left: <65361>>
#  |
#  |  media_next = <Key.media_next: <269025047>>
#  |
#  |  media_play_pause = <Key.media_play_pause: <269025044>>
#  |
#  |  media_previous = <Key.media_previous: <269025046>>
#  |
#  |  media_volume_down = <Key.media_volume_down: <269025041>>

# media_volume_mute = <Key.media_volume_mute: <269025042>>
# |
# |  media_volume_up = <Key.media_volume_up: <269025043>>
# |
# |  menu = <Key.menu: <65383>>
# |
# |  num_lock = <Key.num_lock: <65407>>
# |
# |  page_down = <Key.page_down: <65366>>
# |
# |  page_up = <Key.page_up: <65365>>
# |
# |  pause = <Key.pause: <65299>>
# |
# |  print_screen = <Key.print_screen: <65377>>
# |
# |  right = <Key.right: <65363>>
# |
# |  scroll_lock = <Key.scroll_lock: <65300>>
# |
# |  shift = <Key.shift: <65505>>

# shift_r = <Key.shift_r: <65506>>
#  |
#  |  space = <Key.space: ' '>
#  |
#  |  tab = <Key.tab: <65289>>
#  |
#  |  up = <Key.up: <65362>>
