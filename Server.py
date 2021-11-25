from typing import Tuple
from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
from Segment.Segment import Segment
import socket, os

class Server:
    def __init__(self):
        # Anggap sudah ada parser dengan variable args

        # File transfer
        self.filePath = args.path
        SEEK_OFFSET = 0
        SEEK_FROM_END = 2
        WINDOW_SIZE = 4
        self.MAX_DATA_SEGMENT_SIZE = 32768
        
        fObj = open(self.filePath, "rb")
        fObj.seek(SEEK_OFFSET, SEEK_FROM_END)
        self.fileSize = fObj.tell()
        self.windowSize = WINDOW_SIZE
        self.segmentCnt = self.fileSize/self.MAX_DATA_SEGMENT_SIZE
        self.isSendMetadata = True

        if self.isSendMetadata:
            base = os.path.basename(self.filePath)
            self.fileName = os.path.splitext(base)[0]
            self.fileExt = os.path.splitext(base)[1]

        fObj.close()
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
        print("\n[v] Initiating three way handshake with the clients...")
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
        
        print("\n[v] Commencing file transfer...")

        for clientAddress in self.clientConnection:
            self.goBackNARQServer(clientAddress)
            

    def sendMetadata(self, clientAddress):
        segmentMetadata = Segment()
        separator = b"\x00"
        byteFilename = bytes(self.fileName, 'ascii')
        byteExtension = bytes(self.fileExt, 'ascii')

        metadata = byteFilename + separator + byteExtension

        segmentMetadata.set_data(metadata)
        self.connection.send_data(segmentMetadata)

    def goBackNARQServer(self, clientAddress: Tuple):
        if self.isSendMetadata:
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
                seekOffset = self.MAX_DATA_SEGMENT_SIZE*(windowStart+ithSegment)
                fObj.seek(seekOffset)
                readData = fObj.read(self.MAX_DATA_SEGMENT_SIZE)

                sendSegment = Segment()
                sendSegment.set_data(readData)
                nextSequence = windowStart+ithSegment
                sendSegment.set_sequence(nextSequence)
                sendSegment.set_ack(ithSegment)
                self.connection.send_data(sendSegment, clientAddress)
                print(f"[v] Sending segment with sequence number {nextSequence}")
                
                ithSegment += 1
            

            for _ in range(0, cntSegment):
                try:
                    recvAddr, recvSegment = self.connection.listen_for_data(clientAddress)
                    isValidChecksum = recvSegment.is_valid_checksum()
                    ackNumber = recvSegment.get_ack()

                    if isValidChecksum:
                        if recvAddr == clientAddress:
                            if ackNumber == windowStart:
                                windowStart += 1
                                endOffset = windowStart+windowSize
                                windowEnd = min(endOffset, segmentCnt)
                                print(f"[v] New sequence base = {windowStart}, ACK number {ackNumber}")
                            else:
                                print(f"[!] Ignoring the segment, ACK number not match, ")
                                break
                        else:
                            print(f"[!] Ignoring the segment, received address not match")
                            break
                    else:
                        print(f"[!] Checksum failed!")
                        print(recvSegment)
                        break
                except socket.timeout:
                    print(f"[!] Socket timeout!")
                    break
            
        print(f"\n[v] Sending FIN to client... File transfer has been completed \n")
        sendSegment = Segment()
        sendSegment.set_flag(FlagEnums.FIN_ONLY)
        self.connection.send_data(sendSegment, clientAddress)

        _, recvSegment = self.connection.listen_for_data(clientAddress)
        isNotValidACK = not(recvSegment.get_ack())

        if isNotValidACK:
            print(f"\n[!] Invalid ACK segment\n")
            print(recvSegment)
        else:
            print(f"\n[!] Connection closed\n")
        fObj.close()

            
