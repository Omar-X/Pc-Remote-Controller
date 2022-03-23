import socket
import webbrowser
from sys import platform
import urllib.request
# from twisted.internet import protocol, reactor
# import json
FORMAT = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
try:
    SERVER = (s.getsockname()[0], 6666)
except:
    print("please connect to a wifi")
    SERVER = ("127.0.0.1", 6666)


def _subnet_reader():
    # data_line = None
    # try:
    #     if platform == "linux":
    #         data = os.popen("ifconfig").readlines()
    #     else:
    #         data = os.popen("ifconfig").readlines()
    #     for i in data:
    #         if i.find("netmask") != -1 or i.find("Subnet Mask") != -1:
    #             data_line = i
    #             break
    #     if not data_line:
    #         return 24
    #
    # except:
    #     return 24
    return 24


def _get_available_hosts(server=SERVER[0], subnet=24):
    hosts = []
    binary_length = "".join(["1" for i in range(32 - subnet)])
    length = int(binary_length, 2)
    network = _ip_converter(server)[:subnet]
    for i in range(1, length):
        sub_ip = ("".join(["0" for n in range(32 - subnet)]) + bin(i)[2:])[-(32 - subnet):]
        binary_host = network + sub_ip
        host = _ip_reader(binary_host)
        hosts.append(host)
    return hosts


def _ip_reader(text):
    return str(int(text[:8], 2)) + "." + str(int(text[8:16], 2)) + "." + str(int(text[16:24], 2)) + "." + str(
        int(text[24:32], 2))


def _ip_converter(text):
    dic = text.split(".")
    serial = ""
    for i in dic:
        part = bin(int(i))[2:]
        while len(part) < 8:
            part = "0" + part
        serial += part
    return serial


# very slow method
def check_location(host="127.0.0.1", port=80):
    if len(host.split(".")) == 4:
        for i in host.split("."):
            if not i.isdigit():
                return False
    else:
        return False
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sk.connect_ex((host, port))
    sk.close()
    if not result:
        return True
    else:
        return False

def get_server():
    results = []
    hosts = _get_available_hosts(SERVER[0], _subnet_reader())
    for i in hosts:
        if check_location(i, 6666):
            results.append(i)
    return results


def open_website(protocol="https", host="www.google.com",
                 new_url=False, new_url_tab=False, read_url=False):
    if not new_url and not new_url_tab:
        webbrowser.open("{protocol}://{URL}".format(protocol=protocol, URL=host))
        print("{protocol}://{URL}".format(protocol=protocol, URL=host))
    elif new_url and not new_url_tab:
        webbrowser.open_new("{protocol}://{URL}".format(protocol=protocol, URL=host))
        print("{protocol}://{URL}".format(protocol=protocol, URL=host))
    else:
        webbrowser.open_new_tab("{protocol}://{URL}".format(protocol=protocol, URL=host))
        print("{protocol}://{URL}".format(protocol=protocol, URL=host))
    if read_url:
        for i in str(urllib.request.urlopen("{protocol}://{URL}".format(protocol=protocol, URL=host)).read()).split(
                ","):
            print(i)

# class RemoteClient(protocol.DatagramProtocol):
#     def __init__(self, host, port = 6666):
#         self.host = host
#         self.port = port
#         self.server = ""
#
#     def startProtocol(self):
#         options = _get_available_hosts()
#         for i in options:
#             self.send_msg("CHECK", "open")
#
#     def datagramReceived(self, datagram, addr):
#         data = json.loads(datagram.decode(FORMAT))
#         if data["ORDER"] == "CHECK" and data["DATA"] == "yes":
#             self.server = addr
#             print("SERVER FOUND: ", self.server)
#
#     def send_msg(self, order, data, action_type="", value=None):
#         if value and type(value) == tuple:
#             value = [round(value[0], 0), round(value[1], 0)]
#         msg = {"ORDER": order, "DATA": data, "TYPE": action_type, "VALUE": value}
#         msg = json.dumps(msg)
#         msg = msg.encode(FORMAT)
#         print("msg:", msg)
#         print(data.split(" "))
#         self.transport.write(msg)


