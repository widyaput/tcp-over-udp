from Connection.Connection import Conn
from Segment.FlagEnums import FlagEnums
from Segment.Segment import Segment


class Client:
    def __init__(self):
        # anggap ada argument parser dan hasil parsing disimpan di args

        self.filePath = args.path
        self.isReceiveMetadata = True
        self.connection = Conn()
        pass

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


