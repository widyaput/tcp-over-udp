from typing import Tuple
from Segment.Segment import Segment
import socket

class Conn:
    def __init__(self, ip : str, port : int, auto_ifname : str = None, send_broadcast : bool = False, listen_broadcast : bool = False):
        self.ip   = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        if send_broadcast:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if listen_broadcast:
            self.sock.bind(("", port))
        else:
            self.sock.bind((self.ip, port))
        
    
    def send_data(self, seg: Segment, dest: Tuple(str, int)):
        """
        seg = Segment that will be send
        dest = (ip, port)
        """
        pass

    def listen_for_data(self) -> Tuple(Tuple(str, int), Segment):
        """
        Return (_RetAddress, data as Segment)
        """
        pass