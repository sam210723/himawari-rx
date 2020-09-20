"""
assembler.py
https://github.com/sam210723/himawari-rx
"""

from collections import deque
from datetime import datetime
from enum import Enum
from threading import Thread
from time import sleep

class Assembler:
    """
    Coordinates assembly of bz2 files from UDP frames.
    """

    def __init__(self, dump):
        """
        Initialises assembler class
        """

        self.ready = False      # Assembler ready flag
        self.stop = False       # Core thread stop flag
        self.rxq = deque()      # Data receive queue
        self.dump = dump        # Packet dump file

        # Setup core assembler thread
        assembler_thread = Thread()
        assembler_thread.name = "ASSEMBLER CORE"
        assembler_thread.run = self.assembler_core
        assembler_thread.start()


    def assembler_core(self):
        """
        Distributes packets to parsers
        """

        # Indicate core thread has initialised
        self.ready = True

        while not self.stop:
            # Pull next packet from queue
            packet = self.pull()

            # If queue is empty
            if packet == None:
                sleep(10 / 1000)
                continue
            
            # Parse primary packet header
            packet_type = self.parse_primary(packet)

            # Parse packet data
            if   packet_type == "contents": self.parse_file_contents(packet)
            elif packet_type == "info":     self.parse_file_info(packet)
        
        # Gracefully exit core thread
        if self.stop:
            return


    def parse_primary(self, packet):
        """
        Parse primary packet header
        """

        packet_header = packet[:10]
        packet_type = PacketType(packet_header[1])
        packet_length = int.from_bytes(packet_header[2:4], 'little')

        return packet_type.name


    def parse_file_contents(self, packet):
        """
        Parse file contents packet
        """

        file_id = int.from_bytes(packet[4:8], 'little')
        file_part = int.from_bytes(packet[8:10], 'little')


    def parse_file_info(self, packet):
        """
        Parse file info packet
        """

        file_id = int.from_bytes(packet[4:8], 'little')
        file_name = self.get_string(packet[84:])
        file_path = self.get_string(packet[188:])
        packet_data_length = packet[8]
        file_tx_time = self.get_time(packet[60:64])
        file_creation_time = self.get_time(packet[164:168])

        print( "[FILE INFO]")
        print(f"  ID:          {self.to_hex(file_id, 4)}")
        print(f"  NAME:        {file_name}")
        print(f"  CREATED:     {file_creation_time[1]}")
        print(f"  TRANSMITTED: {file_tx_time[1]}")
        print()


    def push(self, packet):
        """
        Push data to receive queue
        """

        self.rxq.append(packet)


    def pull(self):
        """
        Pull data from receive queue
        """

        try:
            # Return top item
            return self.rxq.popleft()
        except IndexError:
            # Queue empty
            return None


    def complete(self):
        """
        Checks if receive queue is empty
        """

        return len(self.rxq) == 0


    def to_hex(self, data, l):
        if type(data) == bytes: data = int.from_bytes(data, byteorder='big')
        
        return f"0x{data:0{l*2}X}"


    def get_string(self, data):
        """
        Gets null-terminated string from bytes
        """
        
        end = data.index(b'\x00')
        return data[:end].decode('utf-8')


    def get_time(self, data):
        """
        Get datetime object and human readable string from UNIX timestamp
        """

        ts = int.from_bytes(data, 'little')
        dt = datetime.utcfromtimestamp(ts)
        s = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

        return dt, s


class PacketType(Enum):
    unknown  = 0
    contents = 1
    info     = 3
    unknown1 = 255
