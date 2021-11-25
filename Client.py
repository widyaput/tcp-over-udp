from typing import Tuple
from Segment.FlagEnums import FlagEnums
import argparse
import binascii
import Connection.Connection
from Segment.Segment import Segment


class Client:
    def __init__(self, broad_server: str, port_server: int):
        args = {
            "port": (int, "Client port"),
            "path": (str, "Destination path"),
            "-s": (None, "Send metadata"),
        }
        parser = argparse.ArgumentParser()
        for argument in args.keys():
            input_type, help_desc = args[argument]
            if input_type is None:
                parser.add_argument(
                    argument,
                    help=help_desc,
                    action="store_const",
                    const=True,
                    default=False,
                )
            else:
                parser.add_argument(argument, help=help_desc, type=input_type)

        args = parser.parse_args()
        print(args.port, args.path , args.s)
        self.ip = "localhost"
        self.port = args.port
        self.path = args.path
        self.get_metadata = args.s
        self.conn = Connection.Connection.Conn(
            self.ip,
            self.port,
            send_broadcast=True
            )
        self.server_broadcast_addr = (broad_server, port_server)

    def handshake_3way(self, addr: Tuple[str, int]) -> bool:
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


if __name__ == "__main__":
    client = Client("", 5005)
