from typing import Tuple
from Segment.Segment import Segment

class Conn:
    def __init__(self):
        pass
    
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