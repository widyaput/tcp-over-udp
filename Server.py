from typing import Tuple
from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
from Segment.Segment import Segment
import socket

class Server:
    def __init__(self):
        # Anggap sudah ada parser dengan variable args

        # File transfer
        self.filePath = args.path
        SEEK_OFFSET = 0
        SEEK_FROM_END = 2
        WINDOW_SIZE = 4
        self.MAX_DATA_SEGMENT_SIZE = 32768
        with open(self.path, "rb") as fObj:
            fObj.seek(SEEK_OFFSET, SEEK_FROM_END)
            self.fileSize = fObj.tell()
        self.windowSize = WINDOW_SIZE
        self.segmentCnt = self.fileSize/self.MAX_DATA_SEGMENT_SIZE
        self.isSendMetadata = True
        if self.isSendMetadata:
            self.fileName = self.filePath[self.filePath.rfind("/") + 1:self.filePath.rfind(".")]
            self.fileExt = self.filePath[self.filePath.rfind("."):]

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

    def fileTransfer(self):
        print("\n[!] Initiating three way handshake with clients...")
        failedHandshakeClient = []
        
        # Anggap lah list of client sudah terinisialisasi
        for clientAddress in self.clientConnection:
            # Lakukan handshake ke client
            HANDSHAKE_FAILED = False
            handshakeStatus = self.handshake_3way(clientAddress)
            
            # Buang client dari list jika handshake gagal
            if handshakeStatus == HANDSHAKE_FAILED:
                failedHandshakeClient.append(clientAddress)
        
        for clientAddress in failedHandshakeClient:
            self.clientConnection.remove(clientAddress)
        
        print("\n[!] Commencing file transfer...")

        for clientAddress in self.clientConnection:
            self.goBackNARQServer()
            

    def sendMetadata(self, clientAddress):
        segmentMetadata = Segment()
        metadata = bytes(self.fileName, 'ascii') + b"\x00" + bytes(self.fileExt, 'ascii')
        segmentMetadata.set_data(metadata)
        self.connection.send_data(segmentMetadata)

    def goBackNARQServer(self, clientAddress: Tuple):
        if self.isSendMetadata:
            self.sendMetadata()
        
        windowSize = self.windowSize
        segmentCnt = self.segmentCnt

        windowStart = 0
        windowEnd = min(windowStart+windowSize, segmentCnt)
        
        with open(self.filePath, "rb") as fObj:
            cntIteration = 0

            while windowStart < segmentCnt:
                print(f"\n[!] [{clientAddress[0]}:{clientAddress[1]}] Transfer iteration = {cntIteration}")

                cntSegment = windowEnd-windowStart
                
                for i in range(0, cntSegment):
                    segment = Segment()
                    seekOffset = self.MAX_DATA_SEGMENT_SIZE*(windowStart+1)

                    fObj.seek(seekOffset)
                    # Maybe provide better Segment constructor
                    segment.set_data(fObj.read(self.MAX_DATA_SEGMENT_SIZE))
                    segment.set_sequence(windowStart+i)
                    segment.set_ack(0)

                    self.connection.send_data(segment, clientAddress)
                    print(f"[!] [{clientAddress[0]}:{clientAddress[1]}] Sending segment with sequence number {windowStart + i}")

                
                for _ in range(0, cntSegment):
                    recvAddr, recvSegment = self.connection.listen_for_data(clientAddress)
                    ackNumber = recvSegment.get_ack()
                    isValidChecksum = recvSegment.is_valid_checksum()
                    if isValidChecksum and recvAddr == clientAddress:
                        if ackNumber == windowStart:
                            windowStart += 1
                            windowEnd = min(windowStart+windowSize, segmentCnt)
                            print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] ACK number {ackNumber}, new sequence base = {windowStart}")
                        else:
                            print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] ACK number not match, ignoring segment")
                    elif not isValidChecksum:
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Checksum failed {recvAddr[0]}:{recvAddr[0]}")
                    elif recvAddr != clientAddress:
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Source address not match, ignoring segment")
                    else:
                        print(f"[!] [{recvAddr[0]}:{recvAddr[0]}] Unknown error")
                        print(recvSegment)
            cntIteration += 1

        # File transfer completed, tearing down the connection
        print(f"\n[!] [{clientAddress[0]}:{clientAddress[1]}] File transfer completed, sending FIN to client...\n")
        sendSegment = Segment()
        sendSegment.set_flag(FlagEnums.FIN_ONLY)
        self.connection.send_data(sendSegment, clientAddress)

        # Waiting for ACK
        _, recvSegment = self.connection.listen_for_data(clientAddress)
        if recvSegment.get_ack():
            print(f"\n[!] [{clientAddress[0]}:{clientAddress[1]}] Connection closed\n")
        else:
            print(f"\n[!] [{clientAddress[0]}:{clientAddress[1]}] Invalid ACK segment\n")
            print(recvSegment)

            