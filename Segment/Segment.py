import struct
from Segment.Flag import Flag
from Segment.FlagEnums import FlagEnums
from typing import Union

class Segment:
    """
    Segment class representation based on task specification
    """
    def __init__(self):
        self.__sequence = 0
        self.__ack = 0
        self.__flag = Flag(FlagEnums.DATA_ONLY)
        self.__checksum = 0
        self.__data = b""
    
    def __str__(self):
        """
        String representation of segment
        """
        return f"""
*** Segment Info ***
{'SEQ number':18} = {self.__sequence}
{'ACK number':18} = {self.__ack}
{'Flags':18} = [SYN {self.__flag.syn}] [ACK {self.__flag.ack}] [FIN {self.__flag.fin}]
{'Checksum':18} = {hex(self.__checksum)}
{'Valid checksum':18} = {self.is_valid_checksum()}
{'Length of data':18} = {len(self.__data)} bytes
        """
    
    def __sumSegment(self) -> int:
        """
        Get sum of all segment exclude checksum
        """
        sumSegment = 0x0000
        sumSegment = (sumSegment + self.__sequence) & 0xFFFF
        sumSegment = (sumSegment + self.__ack) & 0XFFFF
        sumSegment = (sumSegment + struct.unpack("B", self.__flag.bytes)[0]) & 0XFFFF
        i = 0
        while (i < len(self.__data)):
            chunk16bits = self.__data[i:i+2]
            if i == len(self.__data)-1:
                chunk16bits += struct.pack("x") #add padding to last byte from odd bytes data
            chunk16bits = struct.unpack("H", chunk16bits)[0]
            sumSegment = (sumSegment + chunk16bits) & 0xFFFF
            i += 2
        return sumSegment
    
    def set_sequence(self, sequence: int):
        """
        Setter for sequence number

        Receive int as argument
        """
        self.__sequence = sequence
    
    def set_ack(self, ack: int):
        """
        Setter for ack number

        Receive int as argument
        """
        self.__ack = ack
    
    def set_data(self, data: bytes):
        """
        Setter for data/payload

        Receive bytes as argument
        """
        self.__data = data
    
    def set_flag(self, flag: FlagEnums):
        self.__flag = Flag(flag)

    def set_all_from_bytes(self, source: bytes):
        """
        Create Segment from bytes that received from listening connection

        Receive bytes as argument
        """
        self.__data = source[12:]
        header = struct.unpack("IIBxH", source[0:12])
        self.__sequence = header[0]
        self.__ack = header[1]
        self.__flag = Flag(header[2])
        self.__checksum = header[3]
    
    def get_sequence(self) -> int:
        """
        Getter for sequence number
        """
        return self.__sequence
    
    def get_ack(self) -> int:
        """
        Getter for ack number
        """
        return self.__ack

    def get_data(self) -> bytes:
        """
        Getter for data/payload
        """
        return self.__data
    
    def get_flag(self) -> Union[FlagEnums, int]:
        """
        Getter for flag

        Will return int if segment is received from connection

        Will return FlagEnums if segment is created
        """
        return self.__flag
    
    def get_all_as_bytes(self) -> bytes:
        """
        Create Segment to bytes that will be sent through connection

        Only in this method, checksum will be calculated
        """
        byte: bytes = b""
        byte += struct.pack("I", self.__sequence)
        byte += struct.pack("I", self.__ack)
        byte += self.__flag.bytes + struct.pack("x")
        self.__checksum = 0xFFFF - self.__sumSegment()
        byte += struct.pack("H", self.__checksum)
        byte += self.__data
        return byte
    
    def is_valid_checksum(self) -> bool:
        """
        Check if checksum is one complement of sum segment
        """
        return self.__checksum == 0xFFFF - self.__sumSegment()


