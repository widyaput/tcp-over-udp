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
        print(f"\n[v] Fetching the metadata...")

        recvAddr, recvSegment = self.connection.listen_for_data(serverAddress)
        recvData = recvSegment.get_data()
        isValidChecksum = recvSegment.is_valid_checksum()

        if isValidChecksum:
            if serverAddress == recvAddr:
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
    
    def goBackNARQClient(self, serverAddress: Tuple):
        print("[v] Starting file transfer...")

        if self.isReceiveMetadata:
            self.receiveMetadata(serverAddress)

        fObj = open(self.filePath, "wb")
        reqNumber = 0
        isEOF = False

        while not(isEOF):
            _, recvSegment = self.connection.listen_for_data(serverAddress)
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

                    self.connection.send_data(ackSegment, serverAddress)
                    reqNumber += 1
                elif segFlag == FlagEnums.FIN_ONLY:
                    print(f"[v] FIN flag has found, stopping transfer...")
                    print(f"[v] Sending ACK and tearing down the connection...")
                    
                    ackSegment = Segment()
                    ackSegment.set_flag(FlagEnums.FIN_ONLY)

                    self.connection.send_data(ackSegment, serverAddress)

                    isEOF = True
                else:
                     print(f"[!] Sequence number not equal with the Request Number, ignoring the segment...") 
            else:
                print(f"[!] Checksum has failed, sending the previous sequence number")
                ackSegment = Segment()
                ackSegment.set_ack(reqNumber-1)

                self.connection.send_data(ackSegment, serverAddress)
                print(recvSegment)

        self.connection.close_socket()
        fObj.close()


