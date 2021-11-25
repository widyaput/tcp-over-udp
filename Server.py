from typing import Tuple
from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
from Segment.Segment import Segment
from math import ceil
import socket, os
import argparse

class Server:
    def __init__(self, window_size: int):
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
        self.filePath = args.path
        self.is_send_metadata = args.s
        fObj = open(self.filePath, "rb")
        fObj.seek(0, 2)
        self.fileSize = fObj.tell()
        self.windowSize = window_size
        self.segmentCnt = ceil(self.fileSize/Segment.get_max_data_size())

        if self.is_send_metadata:
            base = os.path.basename(self.filePath)
            self.fileName = os.path.splitext(base)[0]
            self.fileExt = os.path.splitext(base)[1]

        fObj.close()
        self.connection = Conn(
            self.ip,
            self.port,
            listen_broadcast=True
        )

    def find_clients(self):
        print("### Listening for clients ###")
        self.clientConnection = []
        listening = "y"

        while listening == "y":
            addr, resp = self.connection.listen_for_data()
            if resp.get_flag().syn and resp.is_valid_checksum() and addr not in self.clientConnection:
                self.clientConnection.append(addr)
                listening = input("Listen more? (y/n) ")
        

    def handshake_3way(self, addr: Tuple[str, int]) -> bool:
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

    def fileTransfer(self):
        print("\n### Initiating three way handshake with the clients ###")
        failedHandshakeClient = []
        
        # Anggap lah list of client sudah terinisialisasi
        for clientAddress in self.clientConnection:
            # Lakukan handshake ke client
            handshakeStatus = self.handshake_3way(clientAddress)
            
            # Buang client dari list jika handshake gagal
            if not handshakeStatus:
                failedHandshakeClient.append(clientAddress)
        
        for clientAddress in failedHandshakeClient:
            self.clientConnection.remove(clientAddress)
        
        print("\n### Commencing file transfer ###")

        for clientAddress in self.clientConnection:
            self.goBackNARQServer(clientAddress)
            

    def sendMetadata(self, clientAddress):
        segmentMetadata = Segment()
        separator = b"\x00"
        byteFilename = bytes(self.fileName, 'ascii')
        byteExtension = bytes(self.fileExt, 'ascii')

        metadata = byteFilename + separator + byteExtension

        segmentMetadata.set_data(metadata)
        self.connection.send_data(segmentMetadata, clientAddress)

    def goBackNARQServer(self, clientAddress: Tuple):
        if self.is_send_metadata:
            self.sendMetadata()
        
        windowSize = self.windowSize
        segmentCnt = self.segmentCnt

        # windowStart = sequenceBase
        windowStart = 0
        windowEnd = min(windowStart+windowSize, segmentCnt)
        
        fObj = open(self.filePath, "rb")

        while windowStart < segmentCnt:
            cntSegment = windowEnd-windowStart

            ithSegment = 0
            while ithSegment < cntSegment:
                seekOffset = Segment.get_max_data_size()*(windowStart+ithSegment)
                fObj.seek(seekOffset)
                readData = fObj.read(Segment.get_max_data_size())

                sendSegment = Segment()
                sendSegment.set_data(readData)
                nextSequence = windowStart+ithSegment
                sendSegment.set_sequence(nextSequence)
                self.connection.send_data(sendSegment, clientAddress)
                print(f"[Segment SEQ={nextSequence}] Sent")
                
                ithSegment += 1
            

            for _ in range(0, cntSegment):
                try:
                    recvAddr, recvSegment = self.connection.listen_for_data()
                    isValidChecksum = recvSegment.is_valid_checksum()
                    ackNumber = recvSegment.get_ack()

                    if isValidChecksum:
                        if recvAddr == clientAddress:
                            if ackNumber == windowStart:
                                windowStart += 1
                                endOffset = windowStart+windowSize
                                windowEnd = min(endOffset, segmentCnt)
                                print(f"[Segment SEQ={ackNumber}] Acked")
                            else:
                                print(f"[Segment SEQ={ackNumber}] NOT ACKED. ACK number mismatch!")
                                break
                        else:
                            print(f"[Segment SEQ={ackNumber}] NOT ACKED. Received address not match!")
                            break
                    else:
                        print(f"[Segment SEQ={ackNumber}] NOT ACKED. Checksum failed!")
                        print(recvSegment)
                        break
                except socket.timeout:
                    print(f"[Segment SEQ={ackNumber}] NOT ACKED. Socket timeout!")
                    break
            
        print(f"\n### Sending FIN to client ### \n\n### File transfer has been completed ###")
        sendSegment = Segment()
        sendSegment.set_flag(FlagEnums.FIN_ONLY)
        self.connection.send_data(sendSegment, clientAddress)

        _, recvSegment = self.connection.listen_for_data()
        ackNumber = recvSegment.get_ack()

        if not recvSegment.get_flag().ack:
            print(f"\n[Segment SEQ={ackNumber}] Invalid ACK segment\n")
            print(recvSegment)
        else:
            print(f"\n### Connection closed ###")
        fObj.close()


            
if __name__ == "__main__":
    server = Server(4)
    server.find_clients()
    server.fileTransfer()