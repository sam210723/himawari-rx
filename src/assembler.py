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
            
            self.parse(packet)
        
        # Gracefully exit core thread
        if self.stop:
            return


    def parse(self, packet):
        """
        Parse packet header
        """

        # [00][TYPE][LEN:1][LEN:0][][][][][COUNTER:1][COUNTER:0]
        header = packet[:10]

        packet_type = PacketType(packet[1])
        packet_length = int.from_bytes(header[2:4], 'little')

        if packet_type.name == "contents":
            file_id = packet[4:8]
            print(f"  ID:          {self.to_hex(file_id, 4)}")

            file_part = int.from_bytes(header[8:10], 'little')

            if self.dump:
                self.dump.write(packet)
                self.dump.flush()
        
        elif packet_type.name == "info":
            file_id = packet[4:8]

            file_name = packet[84:]
            file_name = file_name[:file_name.index(b'\x00')]
            file_name = file_name.decode('utf-8')

            file_path = packet[188:]
            file_path = file_path[:file_path.index(b'\x00')]
            file_path = file_path.decode('utf-8')

            data_length = packet[8]

            transmit_time = datetime.utcfromtimestamp(
                int.from_bytes(packet[60:64], 'little')
            )
            creation_time = datetime.utcfromtimestamp(
                int.from_bytes(packet[164:168], 'little')
            )


            print( "[FILE INFO]")
            print(f"  NAME:        {file_name}")
            print(f"  PATH:        {file_path}")
            print(f"  ID:          {self.to_hex(file_id, 4)}")
            print(f"  CREATED:     {creation_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"  TRANSMITTED: {transmit_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
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


class PacketType(Enum):
    unknown  = 0
    contents = 1
    info     = 3
    unknown1 = 255
