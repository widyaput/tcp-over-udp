from typing import Tuple
from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
from Segment.Segment import Segment


class Server:
    def __init__(self):
        self.connection = Conn()
        pass

    # TODO: IMPLEMENT GO BACK N

    def handshake_3way(self, addr: Tuple(str, int)) -> bool:
        """
        Method for server after client send a first handshake SYN request

        Returning status of the handshake (success or not)

        Receive address (ip, port) as argument
        """
        syn_ack_resp = Segment()
        syn_ack_resp.set_flag(FlagEnums.SYN_AND_ACK)
        self.connection.send_data(syn_ack_resp, addr)

        recvaddr, resp = self.connection.listen_for_data()
        if recvaddr == addr and resp.get_flag().ack and resp.is_valid_checksum():
            return True
        return False
