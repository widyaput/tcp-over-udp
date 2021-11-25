from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
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

    def receiveMetadata(self, serverAddress):
        print(f"\n[Bonus] [{serverAddress[0]}:{serverAddress[1]}] Fetching metadata...")

        recvAddr, recvSegment = self.connection.listen_for_data(serverAddress)

        if recvAddr == serverAddress and recvSegment.is_valid_checksum():
            recvData = recvSegment.get_data()

            fileName = ""
            fileExt = ""
            isFileName = True

            for currByte in recvData:
                if currByte == 0x0:
                    isFileName = False
                elif isFileName:
                    fileName += chr(currByte)
                else:
                    fileExt += chr(currByte)
                
            print(f"[Bonus] [{serverAddress[0]}:{serverAddress[1]}] Metadata information :")
            print(f"[Bonus] [{serverAddress[0]}:{serverAddress[1]}] Source filename : {fileName}")
            print(f"[Bonus] [{serverAddress[0]}:{serverAddress[1]}] File extension  : {fileExt}\n")
        elif recvAddr != serverAddress:
            print(f"[Bonus] [{serverAddress[0]}:{serverAddress[1]}] Source address not match, ignoring segment")
        else:
            print(f"[Bonus] [{serverAddress[0]}:{serverAddress[1]}] Checksum failed, ignoring segment")

        print(recvSegment)
    
    def goBackNARQClient(self, serverAddress: Tuple):
        print("[!] Starting file transfer...")

        if self.isReceiveMetadata:
            self.receiveMetadata(serverAddress)

        with open(self.filePath, "wb") as fObj:
            reqNumber = 0
            isEOF = False

            while not isEOF:
                recvAddr, recvSegment = self.connection.listen_for_data(serverAddress)

                if recvAddr == serverAddress and recvSegment.is_valid_checksum():
                    seqNumber = recvSegment.get_sequence()

                    if reqNumber == seqNumber:
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Sequence number match with Rn, sending Ack number {reqNumber}...")
                        fObj.write(recvSegment.get_data())

                        ackSegment = Segment()
                        ackSegment.set_ack(reqNumber)
                        ackSegment.set_sequence(seqNumber)

                        self.connection.send_data(ackSegment, serverAddress)
                        reqNumber += 1
                    elif recvAddr.get_flag(FlagEnums.FIN_ONLY):
                        isEOF = True
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] FIN flag, stopping transfer...")
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Sending ACK tearing down connection...")

                        ackSegment = Segment()
                        ackSegment.set_flag(FlagEnums.FIN_ONLY)

                        self.connection.send_data(ackSegment, serverAddress)
                    else:
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Sequence number not equal with Rn ({seqNumber} =/= {reqNumber}), ignoring...")
                elif not recvSegment.is_valid_checksum():
                    print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Checksum failed, ignoring segment")

                print(recvSegment)
        self.connection.close_socket()


    

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
    client.three_way_handshake()
    client.listen_file_transfer()
