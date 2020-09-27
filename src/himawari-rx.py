"""
himawari-rx.py
https://github.com/sam210723/himawari-rx

Frontend for HimawariCast file assembler and image generator
"""

from argparse import ArgumentParser
import colorama
from colorama import Fore, Back, Style
from configparser import ConfigParser
from pathlib import Path
import socket
import struct

from assembler import Assembler

class HimawariRX:
    def __init__(self):
        print("┌──────────────────────────────────────────────┐")
        print("│                 himawari-rx                  │")
        print("│       HimawariCast Downlink Processor        │")
        print("├──────────────────────────────────────────────┤")
        print("│    @sam210723       vksdr.com/himawari-rx    │")
        print("└──────────────────────────────────────────────┘\n")

        # Initialise Colorama
        colorama.init(autoreset=True)

        self.args = self.parse_args()
        self.config = self.parse_config()
        self.print_config()
        self.config_dirs()
        self.config_input()

        if self.args.dump != None:
            self.dumpf = open(self.args.dump, "wb")
            print(Fore.GREEN + Style.BRIGHT + f"Opened packet output file: {self.args.dump}")
        else:
            self.dumpf = None

        self.assembler = Assembler(
            self.dumpf,
            self.config['rx']['path'],
            self.config['rx']['format']
        )

        # Check assembler thread is ready
        if not self.assembler.ready:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + "ASSEMBLER CORE THREAD FAILED TO START")
            self.safe_stop()

        print("──────────────────────────────────────────────────────────────────────────────────")

        self.stop = False
        self.loop()


    def loop(self):
        """
        Handle data from UDP socket
        """

        while not self.stop:
            try:
                data, addr = self.sck.recvfrom(1427)
                
                # Push to assembler
                self.assembler.push(data)
            except Exception as e:
                print(e)
                self.safe_stop()


    def config_input(self):
        """
        Configure UDP socket
        """

        self.sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = self.config['udp']['ip']
        port = self.config['udp']['port']

        print(f"Binding UDP socket ({ip}:{port})...", end='')

        try:
            # Bind socket
            self.sck.bind(('', port))

            # Setup multicast
            mreq = struct.pack("=4sl", socket.inet_aton(ip), socket.INADDR_ANY)
            self.sck.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            print(Fore.GREEN + Style.BRIGHT + "SUCCESS")
        except socket.error as e:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + "FAILED")
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
        argp.add_argument("-v", action="store_true", help="Enable verbose console output (only useful for debugging)", default=False)
        argp.add_argument("--dump", action="store", help="Path to packet output file")
        
        return argp.parse_args()
    

    def parse_config(self):
        """
        Parse configuration file
        """

        cfgp = ConfigParser()
        cfgp.read(self.args.config)

        opts = {
            "rx": {
                "path": Path(cfgp.get('rx', 'path')),
                "format": cfgp.get('rx', 'format')
            },
            "udp": {
                "ip":   cfgp.get('udp', 'ip'),
                "port": cfgp.getint('udp', 'port')
            }
        }

        # Check output format is valid
        if opts['rx']['format'] not in ['bz2', 'hrit', 'png', 'jpg', 'bmp']:
            print(Fore.WHITE + Back.RED + Style.BRIGHT + f"INVALID OUTPUT FORMAT \"{opts['rx']['format']}\"")
            self.safe_stop()

        return opts


    def print_config(self):
        """
        Print configuration information
        """

        print(f"CONFIG FILE:    {self.args.config}")
        print(f"UDP INPUT:      {self.config['udp']['ip']}:{self.config['udp']['port']}")
        print(f"OUTPUT PATH:    {self.config['rx']['path'].absolute()}")
        print(f"OUTPUT FORMAT:  {self.config['rx']['format']}\n")


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
    try:
        HimawariRX()
    except KeyboardInterrupt:
        print("Exiting...")
        exit()
