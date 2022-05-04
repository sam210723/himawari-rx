"""
himawari-rx.py
https://github.com/sam210723/himawari-rx

Frontend for HimawariCast file assembler and image generator
"""

import ast
from argparse import ArgumentParser
from collections import namedtuple
import colorama
from colorama import Fore, Back, Style
from configparser import ConfigParser
import os
from pathlib import Path
import socket
import struct
from time import time, sleep

from assembler import Assembler

class HimawariRX:
    def __init__(self):
        self.version = "0.1.4"

        try:
            print("┌──────────────────────────────────────────────┐")
            print("│                 himawari-rx                  │")
            print("│       HimawariCast Downlink Processor        │")
            print("├──────────────────────────────────────────────┤")
            print("│    @sam210723       vksdr.com/himawari-rx    │")
            print("└──────────────────────────────────────────────┘\n")
        except UnicodeEncodeError:
            print(f"himawari-rx v{self.version}\n")

        # Initialise Colorama
        colorama.init(autoreset=True)

        # Parse command line arguments
        self.args = self.parse_args()

        # Change working directory to script location
        os.chdir(Path(__file__).parent.absolute())

        # Configure himawari-rx
        self.config = self.parse_config()
        self.print_config()
        self.config_dirs()
        self.config_input()

        # Open packet dump file
        if self.args.dump != None:
            self.dumpf = open(self.args.dump, "wb")
            print(Fore.GREEN + Style.BRIGHT + f"Writing packets to: \"{self.args.dump}\"")
        else:
            self.dumpf = None

        # Create file assembler instance
        assembler_config = namedtuple('assembler_config', 'verbose dump path combine format ignored')
        self.assembler = Assembler(
            assembler_config(
                self.args.v,
                self.dumpf,
                self.config['rx']['path'],
                self.config['rx']['combine'],
                self.config['rx']['format'],
                self.config['rx']['ignored']
            )
        )

        # Check assembler thread is ready
        if not self.assembler.ready:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + "ASSEMBLER THREAD FAILED TO START")
            self.safe_stop()

        try:
            print("──────────────────────────────────────────────────────────────────────────────────")
        except UnicodeEncodeError:
            pass

        # Reset stop flag
        self.stop = False

        # Get processing start time
        self.stime = time()

        # Enter main loop
        try:
            self.loop()
        except KeyboardInterrupt:
            self.safe_stop()


    def loop(self):
        """
        Handle data from UDP socket
        """

        # Maximum packet length
        buflen = 1427

        while not self.stop:
            if self.config['rx']['input'] == "nng":
                try:
                    # Read packet from socket
                    data, addr = self.sck.recv(buflen + 8)
                except Exception as e:
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + "LOST CONNECTION TO NANOMSG SOURCE")
                    print(e)
                    self.safe_stop()
                
                # Push to assembler
                self.assembler.push(data[8:])

            elif self.config['rx']['input'] == "tcp":
                try:
                    # Read packet from socket
                    data, addr = self.sck.recv(buflen)
                except Exception as e:
                    print(Fore.WHITE + Back.RED + Style.BRIGHT + "LOST CONNECTION TO TCP SOURCE")
                    print(e)
                    self.safe_stop()
                
                # Push to assembler
                self.assembler.push(data)

            elif self.config['rx']['input'] == "udp":
                try:
                    # Read packet from socket
                    data, addr = self.sck.recvfrom(buflen)
                except Exception as e:
                    print(e)
                    self.safe_stop()
                
                # Push to assembler
                self.assembler.push(data)

            elif self.config['rx']['input'] == "file":
                if not self.packetf.closed:
                    # Read packet header from file
                    header = self.packetf.read(6)

                    # No more data to read from file
                    if header == b'':
                        self.packetf.close()
                        continue

                    # Get length of packet
                    length = int.from_bytes(header[2:4], 'little') - 6

                    # Read remaining bytes of packet from file and combine with header bytes
                    packet = header + self.packetf.read(length)

                    # Push to assembler
                    self.assembler.push(packet)
                else:
                    # Assembler has all packets from file, wait for processing
                    if self.assembler.complete():
                        run_time = round(time() - self.stime, 3)
                        print(f"\nFINISHED PROCESSING FILE ({run_time}s)")

                        self.safe_stop()
                    else:
                        # Limit loop speed when waiting for assembler to finish processing
                        sleep(0.5)


    def config_input(self):
        """
        Configure UDP socket or file input
        """

        if self.config['rx']['input'] == "nng":
            # Create socket and address
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = (self.config['nng']['ip'], int(self.config['nng']['port']))

            # Connect socket
            print(f"Connecting to {addr[0]}:{addr[1]}...", end='', flush=True)
            self.connect_socket(self.sck, addr)

            # Setup nanomsg publisher in goesrecv
            self.sck.send(b'\x00\x53\x50\x00\x00\x21\x00\x00')
            if self.sck.recv(8) != b'\x00\x53\x50\x00\x00\x20\x00\x00':
                print(Fore.WHITE + Back.RED + Style.BRIGHT + "ERROR CONFIGURING NANOMSG")
                self.safe_stop()

        elif self.config['rx']['input'] == "tcp":
            # Create socket and address
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = (self.config['tcp']['ip'], int(self.config['tcp']['port']))

            # Connect socket
            print(f"Connecting to {addr[0]}:{addr[1]}...", end='', flush=True)
            self.connect_socket(self.sck, addr)

        elif self.config['rx']['input'] == "udp":
            # Create socket and address
            self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (self.config['udp']['ip'], int(self.config['udp']['port']))

            # Bind socket
            print(f"Binding UDP socket {addr[0]}:{addr[1]}...", end='', flush=True)
            try:
                # Bind socket
                self.sck.bind(('', addr[1]))

                # Setup multicast
                mreq = struct.pack("=4sl", socket.inet_aton(addr[0]), socket.INADDR_ANY)
                self.sck.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

                print(Fore.GREEN + Style.BRIGHT + "SUCCESS")
            except socket.error as e:
                print(Fore.WHITE + Back.RED + Style.BRIGHT + "FAILED")
                print(e)
                self.safe_stop()

        elif self.config['rx']['input'] == "file":
            print(f"Opening packet file...", end='')

            if Path(self.args.file).exists():
                self.packetf = open(self.args.file, 'rb')
                print(Fore.GREEN + Style.BRIGHT + "SUCCESS")
            else:
                print(Fore.WHITE + Back.RED + Style.BRIGHT + "FILE DOES NOT EXIST")
                self.safe_stop()


    def connect_socket(self, s, addr):
        """
        Connect a socket and handle exceptions
        """

        try:
            s.connect(addr)
            print(Fore.GREEN + Style.BRIGHT + "CONNECTED")
        except socket.error as e:
            if e.errno == 10061: print(Fore.WHITE + Back.RED + Style.BRIGHT + "CONNECTION REFUSED")
            print(e)
            self.safe_stop()


    def config_dirs(self):
        """
        Configure output directory structure
        """

        # Create output root directory
        if not self.config['rx']['path'].exists():
            self.config['rx']['path'].mkdir()


    def parse_args(self):
        """
        Parse command line arguments
        """

        argp = ArgumentParser()
        argp.description = "Receive weather images from geostationary satellite Himawari-8 (140.7˚E) via the HimawariCast service."
        argp.add_argument("--config", action="store", help="Configuration file path (.ini)", default="himawari-rx.ini")
        argp.add_argument("--file", action="store", help="Path to packet file", default=None)
        argp.add_argument("-v", action="store_true", help="Enable verbose console output (only useful for debugging)", default=True)
        argp.add_argument("--dump", action="store", help="Path to packet output file")

        args = argp.parse_args()

        # Get absolute path of input file
        if args.file: args.file = str(Path(args.file).absolute())

        return args
    

    def parse_config(self):
        """
        Parse configuration file
        """

        cfgp = ConfigParser()
        cfgp.read(self.args.config)

        opts = {
            "rx": {
                "input": cfgp.get('rx', 'input'),
                "path": Path(cfgp.get('rx', 'path')),
                "combine": cfgp.getboolean('rx', 'combine'),
                "format": cfgp.get('rx', 'format'),
                "ignored": cfgp.get('rx', 'ignored')
            },
            "nng": {
                "ip":   cfgp.get('nng', 'ip'),
                "port": cfgp.getint('nng', 'port')
            },
            "tcp": {
                "ip":   cfgp.get('tcp', 'ip'),
                "port": cfgp.getint('tcp', 'port')
            },
            "udp": {
                "ip":   cfgp.get('udp', 'ip'),
                "port": cfgp.getint('udp', 'port')
            }
        }

        # Check input type is valid
        if opts['rx']['input'] not in ['nng', 'tcp', 'udp']:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"INVALID INPUT TYPE \"{opts['rx']['input']}\"")
            self.safe_stop()

        # Check output format is valid
        if opts['rx']['format'] not in ['bz2', 'xrit', 'png', 'jpg', 'bmp']:    #TODO: Handle image formats
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"INVALID OUTPUT FORMAT \"{opts['rx']['format']}\"")
            self.safe_stop()
        
        # If band blacklist is not empty
        if opts['rx']['ignored'] != "":
            # Parse blacklist string into int or list
            ignored = ast.literal_eval(opts['rx']['ignored'])

            # If parsed into int, wrap int in list
            if type(ignored) == str: ignored = [ignored]
            opts['rx']['ignored'] = ignored

        return opts


    def print_config(self):
        """
        Print configuration information
        """

        print(f"CONFIG FILE:      {self.args.config}")
        
        if not self.args.file:
            input_path =  f"{self.config['rx']['input'].upper()}"
            input_path += f" ({self.config[self.config['rx']['input']]['ip']}:{self.config[self.config['rx']['input']]['port']})"
        else:
            input_path = Path(self.args.file).name
            self.config['rx']['input'] = "file"


        print(f"INPUT:            {input_path}")
        print(f"OUTPUT PATH:      {self.config['rx']['path'].absolute()}")
        print(f"OUTPUT FORMAT:    {self.config['rx']['format']}")
        print(f"COMBINED OUTPUT:  {'YES' if self.config['rx']['combine'] else 'NO'}")

        if (len(self.config['rx']['ignored']) == 0):
            print("IGNORED CHANNELS: None")
        else:
            ignored = ""
            for i, c in enumerate(self.config['rx']['ignored']):
                if i > 0: ignored += ", "
                ignored += c
        
            print(f"IGNORED CHANNELS: {ignored}")
        
        print(f"VERSION:          {self.version}\n")


    def safe_stop(self, message=True):
        """
        Safely kill threads and exit
        """

        self.stop = True

        try:
            self.assembler.stop = True
        except AttributeError:
            pass
        
        if self.args.dump != None:
            self.dumpf.close()

        if message: print("\nExiting...")
        exit()


if __name__ == "__main__":
    HimawariRX()
