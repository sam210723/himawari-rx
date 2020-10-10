"""
assembler.py
https://github.com/sam210723/himawari-rx
"""

from collections import deque
from colorama import Fore, Back, Style
from datetime import datetime
from enum import Enum
from threading import Thread
from time import sleep

from file import File

class Assembler:
    """
    Coordinates assembly of files (bz2 / images / text) from packets.
    """

    def __init__(self, config):
        """
        Initialises assembler class
        """

        self.ready = False      # Assembler ready flag
        self.stop = False       # Core thread stop flag
        self.rxq = deque()      # Data receive queue
        self.files = {}         # File object list
        self.config = config    # Assembler configuration

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
            
            # Get packet type
            try:
                packet_type = PacketType(packet[1]).name
            except ValueError:
                if self.config.verbose:
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[UNK]  TYPE: {packet[1]}   LEN: {len(packet)}")

            # Dump packet to file if enabled
            if self.config.dump != None:
                self.config.dump.write(packet)
                self.config.dump.flush()

            # Parse packet data based on packet type
            if   packet_type == "contents": self.parse_file_contents(packet)
            elif packet_type == "info":     self.parse_file_info(packet)
            elif packet_type == "complete": self.parse_file_complete(packet)
        
        # Gracefully exit core thread
        if self.stop:
            return


    def parse_file_contents(self, packet):
        """
        Parse file contents packet
        """

        # Get packet UID and length
        uid = self.get_int(packet[4:8])
        # length = self.get_int(packet[2:4])    # Always 1427 bytes
        
        # Ignore parts without associated file object
        if self.files.get(uid) == None:
            if self.config.verbose: print(Fore.WHITE + Back.RED + Style.BRIGHT + f"PART BEFORE INFO \"{self.to_hex(uid, 4)}\"")
            return
        
        # Append data to file payload
        self.files[uid].add(packet)

        # Print file part packet info
        #if self.config.verbose:
            #print(f"[PART] {self.to_hex(uid, 4)} \"{self.files[uid].name}\" ", end='')
            #print(f"#{str(self.get_int(packet[8:10]) + 1).zfill(4)} ", end='')
            #print(f"{str(len(self.files[uid].payload)).zfill(4)}/{str(self.files[uid].parts).zfill(4)}")
        
        # Check if last part has been received
        if self.files[uid].complete:

            # Output format is uncompressed
            if self.config.format != "bz2":
                # Decompress file payload
                if not self.files[uid].decompress():
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[BZ2]  \"{self.files[uid].name}\"")
                    del self.files[uid]
                    return

                # Save file to disk after decompression
                if self.config.format == "xrit":
                    ok = self.files[uid].save(self.config.path)
                
                # Generate image from decompressed payload
                elif any(fmt in self.config.format for fmt in ['png', 'jpg', 'bmp']):
                    pass
            else:
                # Save compressed payload to disk
                ok = self.files[uid].save(self.config.path)
            
            # Print save status message
            if ok:
                if self.config.verbose: print(Fore.GREEN + Style.BRIGHT + f"[SAVE] {self.to_hex(uid, 4)} \"{self.files[uid].name}\" OK")
            else:
                if self.config.verbose: print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[SAVE] {self.to_hex(uid, 4)} \"{self.files[uid].name}\" FAILED")
            
            # Remove file object from list
            del self.files[uid]


    def parse_file_info(self, packet):
        """
        Parse file info packet
        """

        # Get packet UID and length
        uid = self.get_int(packet[4:8])
        #length = self.get_int(packet[2:4])     # Always 242 bytes

        # Check if file ID already exists
        if self.files.get(uid) == None:
            # Check channel is not on the ignore list
            if any(subs in self.get_string(packet[84:]) for subs in self.config.ignored):
                return

            # Create new file object
            self.files[uid] = File(
                name   = self.get_string(packet[84:]),
                path   = self.get_string(packet[188:]),
                parts  = self.get_int(packet[72:74]),
                length = self.get_int(packet[172:176]),
                time_a = self.get_time(packet[164:168]),
                time_b = self.get_time(packet[60:64])
            )

            if self.config.verbose:
                print(f"\n[INFO] {self.to_hex(uid, 4)} \"{self.files[uid].name}\" ", end='')
                print(f"{round(self.files[uid].length/1024, 1)} kB IN {self.files[uid].parts} PARTS")


    def parse_file_complete(self, packet):
        """
        Parse file complete packet
        """

        # Get packet UID and length
        uid = self.get_int(packet[4:8])
        # length = self.get_int(packet[2:4])    # Always 8 bytes
        
        # Ignore packet without associated file object
        if self.files.get(uid) == None: return

        if self.config.verbose:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[DONE] {self.to_hex(uid, 4)} \"{self.files[uid].name}\" COMPLETE ", end='')
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"{str(len(self.files[uid].payload)).zfill(4)}/{str(self.files[uid].parts).zfill(4)}")
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"MISSING {self.files[uid].parts - len(self.files[uid].payload)} PARTS")


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


    def get_int(self, data):
        """
        Get integer from bytes
        """

        return int.from_bytes(data, 'little')


class PacketType(Enum):
    contents = 1        # File contents (payload)
    info     = 3        # File information
    complete = 255      # File complete marker
