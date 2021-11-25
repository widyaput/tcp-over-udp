from Connection.Connection import Conn
from typing import Tuple
from Segment.FlagEnums import FlagEnums
import argparse
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
        self.ip = "localhost"
        self.port = args.port
        self.path = args.path
        self.is_receive_metadata = args.s
        self.connection = Conn(
            self.ip,
            self.port,
            send_broadcast=True
        )
        self.server_broadcast_addr = (broad_server, port_server)

    def receiveMetadata(self):
        print(f"\n[v] Fetching the metadata...")

        recvAddr, recvSegment = self.connection.listen_for_data()
        recvData = recvSegment.get_data()
        isValidChecksum = recvSegment.is_valid_checksum()

        if isValidChecksum:
            if self.server_broadcast_addr == recvAddr:
                byteSeparator = b"\x00"
                fileName, fileExt = recvData.split(byteSeparator)
                fileName = fileName.decode("utf-8")
                fileExt = fileExt.decode("utf-8")

                print(f"[v] Metadata Info :")
                print(f"[v] File Name : {fileName}")
                print(f"[v] File Extension : {fileExt}\n")
            else:
                print(f"[!] Ignoring segment, Server address not match")
        else:
            print(f"[!] Checksum has failed, ignoring the segment")

        print(recvSegment)
    
    def goBackNARQClient(self):
        print("[v] Starting file transfer...")

        if self.is_receive_metadata:
            self.receiveMetadata()

        fObj = open(self.path, "wb")
        reqNumber = 0
        isEOF = False

        while not(isEOF):
            _, recvSegment = self.connection.listen_for_data()
            isValidChecksum = recvSegment.is_valid_checksum()
            seqNumber = recvSegment.get_sequence()
            segData = recvSegment.get_data()
            segFlag = recvSegment.get_flag()

            if isValidChecksum:
                if reqNumber == seqNumber:
                    print(f"[v] Sending ACK number {reqNumber}... Sequence number match with Request Number")
                    fObj.write(segData)
                    
                    ackSegment = Segment()
                    ackSegment.set_ack(reqNumber)
                    ackSegment.set_flag(FlagEnums.ACK_ONLY)

                    self.connection.send_data(ackSegment, self.server_broadcast_addr)
                    reqNumber += 1
                elif segFlag.fin:
                    print(f"[v] FIN flag has found, stopping transfer...")
                    print(f"[v] Sending ACK and tearing down the connection...")
                    
                    ackSegment = Segment()
                    ackSegment.set_flag(FlagEnums.FIN_ONLY)

                    self.connection.send_data(ackSegment, self.server_broadcast_addr)

                    isEOF = True
                else:
                    print(f"[!] Sequence number not equal with the Request Number, ignoring the segment...") 
                    ackSegment = Segment()
                    ackSegment.set_ack(reqNumber-1)

                    self.connection.send_data(ackSegment, self.server_broadcast_addr)
                    print(recvSegment)
            else:
                print(f"[!] Checksum has failed, sending the previous sequence number")
                ackSegment = Segment()
                ackSegment.set_ack(reqNumber-1)

                self.connection.send_data(ackSegment, self.server_broadcast_addr)
                print(recvSegment)

        self.connection.close_socket()
        fObj.close()

    def handshake_3way(self) -> bool:
        syn_ack_resp = Segment()
        syn_ack_resp.set_flag(FlagEnums.SYN_ONLY)
        self.connection.send_data(syn_ack_resp, self.server_broadcast_addr)

        server_addr, resp = self.connection.listen_for_data()
        if not resp.is_valid_checksum:
            exit(1)
        resp_flag = resp.get_flag()
        if resp_flag.syn and resp_flag.ack:
            ack_req = Segment()
            ack_req.set_flag(FlagEnums.ACK_ONLY)
            self.connection.send_data(ack_req, server_addr)
            self.server_addr = server_addr
        else:
            exit(1)


if __name__ == "__main__":
    client = Client("", 5005)
    client.handshake_3way()
    client.goBackNARQClient()
