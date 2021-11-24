from Segment.FlagEnums import FlagEnums
import argparse
import binascii
import Connection.Connection
from Segment.Segment import Segment
class Client:
    def __init__(self):
        args = {
            "port" : (int, "Client port"),
            "path" : (str, "Destination path")
        }
        parser = argparse.ArgumentParser
        for argument in args.keys():
            input_type, help_desc = args[argument]
            if input_type is None:
                parser.add_argument(argument,help=help_desc,action="store_const",const=True,default=False)
            else:
                parser.add_argument(argument,help=help_desc,type=input_type)
                
        args = parser.argsParse()

        self.ip = "localhost"
        self.port = args.port
        self.path = args.path
        self.verbose_segment_print = args.f
        self.show_payload = args.d
        self.get_metadata = True
        self.conn = Connection.Connection.Conn(
            self.ip,
            self.port,
            auto_ifname= b"eth2",
            send_broadcast=True
            )
        self.ip = self.conn.get_ipv4()
        self.server_broadcast_addr = (self.conn.get_broadcast_addr(), 5005)
        
    def handshake_3way(self, addr: Tuple(str, int)) -> bool:
        syn_ack_resp = Segment()
        syn_ack_resp.set_flag(FlagEnums.SYN_ONLY)
        self.conn.send_data(syn_ack_resp, addr)
        
        server_addr, resp, checksum_success = self.conn.listen_for_data()
        resp_flag = resp.get_flag()
        if resp_flag.syn and resp_flag.ack:
            ack_req = Segment()
            ack_req.set_flag(FlagEnums.ACK_ONLY)
            self.conn.send_data(ack_req, server_addr)
            self.server_addr = server_addr
        else:
            exit(1)
            
    def argsParse(self,) -> argparse.Namespace:
        return self.parser.parse_args()
