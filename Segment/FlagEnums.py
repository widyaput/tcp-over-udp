import enum
from typing import Optional

class FlagEnums(enum.Enum):
    """
        Class enum for all flags.
        
        SYN_ONLY needed when first three way handshake by client.
        
        
        SYN_AND_ACK needed when server responding first three way handshake by client.
        
        
        ACK_ONLY mostly needed when client responding from file transfer by server
        
        
        FIN_ONLY needed when tearing down connection (end of file) send by server to client
        
        
        DATA_ONLY needed when segment only bring data from server to client (default for Segment class)
    """
    SYN_ONLY    = 0b00000010
    ACK_ONLY    = 0b00010000
    FIN_ONLY    = 0b00000001
    SYN_AND_ACK = 0b00010010
    DATA_ONLY   = 0b00000000

