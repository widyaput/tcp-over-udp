import struct
from typing import Union
from Segment.FlagEnums import FlagEnums

class Flag:
    """
    Flag for segment.

    Can get bytes from flag, checking if flag contain SYN, ACK, or FIN.
    
    """
    def __init__(self, flag: Union[FlagEnums, int]):
        self.syn = bool((flag.value if type(flag) == FlagEnums else flag ) & FlagEnums.SYN_ONLY.value)
        self.ack = bool((flag.value if type(flag) == FlagEnums else flag ) & FlagEnums.ACK_ONLY.value)
        self.fin = bool((flag.value if type(flag) == FlagEnums else flag ) & FlagEnums.FIN_ONLY.value)
        self.bytes = struct.pack("B", (flag.value if type(flag) == FlagEnums else flag ))
        
        # Readable version of above.
        # !DO NOT REMOVE THESE LINES. REMOVE THESE AFTER THIS PROJECT DONE
        # if type(flag) == FlagEnums:
        #     self.syn = bool(flag.value & FlagEnums.SYN_ONLY.value)
        #     self.ack = bool(flag.value & FlagEnums.ACK_ONLY.value)
        #     self.fin = bool(flag.value & FlagEnums.FIN_ONLY.value)
        #     self.bytes = struct.pack("B", flag.value)
        # if type(flag) == int:
        #     self.syn = bool(flag & (FlagEnums.SYN_ONLY.value))
        #     self.ack = bool(flag & (FlagEnums.ACK_ONLY.value))
        #     self.fin = bool(flag & (FlagEnums.FIN_ONLY.value))
        #     self.bytes = struct.pack("B", flag)