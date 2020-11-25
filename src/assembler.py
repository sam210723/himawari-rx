"""
assembler.py
https://github.com/sam210723/himawari-rx
"""

from collections import deque, namedtuple
from colorama import Fore, Back, Style
from datetime import datetime
from enum import Enum
from threading import Thread
from time import time, sleep

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

        # Setup assembler thread
        assembler_thread = Thread(target=self.assembler_core)
        assembler_thread.name = "ASSEMBLER"
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
            
            # Dump packet to file if enabled
            if self.config.dump != None:
                self.config.dump.write(packet)
                self.config.dump.flush()
            
            # Parse packet header
            packet = self.parse_packet_header(packet)
            #print(".", end="", flush=True)

            # Parse packet data based on packet type
            if   packet.type == 1:   self.parse_file_contents(packet)   # File contents (payload)
            elif packet.type == 3:   self.parse_file_info(packet)       # File information
            elif packet.type == 255: self.parse_file_complete(packet)   # File complete marker
            else:
                if self.config.verbose: print(Fore.WHITE + Back.RED + Style.BRIGHT + f"UNKNOWN PACKET TYPE \"{packet.type}\"")


        # Gracefully exit core thread
        if self.stop: return


    def parse_packet_header(self, packet):
        """
        Get packet info from header
        """

        packet_tuple = namedtuple('packet_info', 'data type length uid')

        return packet_tuple(
            data   = packet,
            type   = packet[1],
            length = self.get_int(packet[2:4]),
            uid    = self.get_int(packet[4:8])
        )


    def parse_file_info(self, p):
        """
        Parse file info packet (type 3)
        """

        # Create file object if new UID
        if not self.file_exists(p):
            self.files[p.uid] = File()
        
        # Check for existing file info
        try:
            self.files[p.uid].name
            #if self.config.verbose: print(f"[INFO] {self.to_hex(p.uid, 4)}")
        except AttributeError:
            # Set file info properties
            self.files[p.uid].info(
                name   = self.get_string(p.data[84:]),
                path   = self.get_string(p.data[188:]),
                parts  = self.get_int(p.data[72:74]),
                length = self.get_int(p.data[172:176]),
                time_a = self.get_time(p.data[164:168]),
                time_b = self.get_time(p.data[60:64])
            )

            # Set ignored file flag
            self.files[p.uid].ignored = self.is_ignored(self.files[p.uid])

            # Print file info
            if self.config.verbose:
                print(f"\n[INFO] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" ", end='')
                print(f"{round(self.files[p.uid].length/1024, 1)} kB IN {self.files[p.uid].parts} PARTS")


    def parse_file_contents(self, p):
        """
        Parse file contents packet (type 1)
        """
        
        # Create file object if new UID
        if not self.file_exists(p):
            if self.config.verbose: print(Fore.WHITE + Back.RED + Style.BRIGHT + f"PART BEFORE INFO \"{self.to_hex(p.uid, 4)}\"")
            self.files[p.uid] = File()
        
        # Append data to file payload
        self.files[p.uid].add(p.data)

        # Print file part packet info
        if self.config.verbose and False:
            try:
                print(f"[PART] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" ", end='')
                print(f"#{str(self.get_int(p.data[8:10]) + 1).zfill(4)} ", end='')
                print(f"{str(len(self.files[p.uid].payload)).zfill(4)}/{str(self.files[p.uid].parts).zfill(4)}")
            except AttributeError:
                print(f"[PART] {self.to_hex(p.uid, 4)} ", end='')
                print(f"#{str(self.get_int(p.data[8:10]) + 1).zfill(4)}")
        
        # Check if last part has been received
        if self.files[p.uid].complete:
            # Delete ignored channels
            if self.files[p.uid].ignored:
                print(Fore.YELLOW + Back.BLACK + Style.BRIGHT + "       SKIPPING FILE IN IGNORED CHANNEL")
                del self.files[p.uid]
                return

            # Output format is uncompressed
            if self.config.format != "bz2":
                # Get decompression start time
                decomp_time = time()

                # Decompress file payload
                if not self.files[p.uid].decompress():
                    # Decompression failed
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[BZ2]  \"{self.files[p.uid].name}\"")
                    del self.files[p.uid]
                    return
                else:
                    if self.config.verbose: print(Fore.GREEN + Style.BRIGHT + f"[BZ2 ] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" OK ({round(time() - decomp_time, 3)}s)")

                # Save file to disk after decompression
                if self.config.format == "xrit":
                    ok = self.files[p.uid].save(self.config.path)
                
                # Generate image from decompressed payload
                elif any(fmt in self.config.format for fmt in ['png', 'jpg', 'bmp']):
                    pass
            else:
                # Save compressed payload to disk
                ok = self.files[p.uid].save(self.config.path)

            # Print save status message
            if ok:
                if self.config.verbose: print(Fore.GREEN + Style.BRIGHT + f"[SAVE] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" OK")
            else:
                if self.config.verbose: print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[SAVE] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" FAILED")

            # Remove file object from list
            del self.files[p.uid]


    def parse_file_complete(self, p):
        """
        Parse file complete packet (type 255)
        """
        
        # Ignore packet without associated file object
        if not self.file_exists(p): return

        # Check file info has been set
        try:
            self.files[p.uid].name
        except AttributeError:
            # Removed complete file with missing info
            del self.files[p.uid]
            return

        if self.config.verbose:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"[DONE] {self.to_hex(p.uid, 4)} \"{self.files[p.uid].name}\" COMPLETE ", end='')
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"{str(len(self.files[p.uid].payload)).zfill(4)}/{str(self.files[p.uid].parts).zfill(4)}")
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"MISSING {self.files[p.uid].parts - len(self.files[p.uid].payload)} PARTS")


    def is_ignored(self, f):
        """
        Check if file channel is ignored
        """

        return any(subs in f.name for subs in self.config.ignored)


    def file_exists(self, p):
        """
        Check if file object exists
        """

        return self.files.get(p.uid) != None



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
