"""
file.py
https://github.com/sam210723/himawari-rx
"""

import bz2
import pathlib

class File:
    """
    Incoming file object containing file properties and payload
    """

    def __init__(self):
        self.buffer = None
        self.part_counter = 0
        self.ignored = False
        self.complete = False
        self.compressed = True


    def info(self, name, path, parts, length, time_a, time_b):
        """
        Set properties for incoming file
        """

        self.name      = name.split('.')[0]
        self.ext       = f".{name.split('.')[1]}"
        self.path      = path
        self.parts     = parts
        self.length    = length
        self.time_a    = time_a
        self.time_b    = time_b
        self.time_diff = time_b[0] - time_a[0]

        # Allocate byte array for file payload
        self.buffer = bytearray(length)


    def add(self, data):
        """
        Add data to file payload
        """

        #TODO: Handle part arriving before info (put in temp dict until info ready)

        # Get file part number and byte offset
        part = self.get_int(data[8:10])
        offset = part * 1411

        # Add data to file payload
        self.buffer[offset : offset + 1411] = data[16:]
        self.part_counter += 1

        # Check all parts have been received
        try:
            self.complete = self.part_counter == self.parts
        except AttributeError:
            # Handle complete check before file info has been set
            self.complete = False

        return self.part_counter


    def save(self, path):
        """
        Save file payload to disk

        Args:
            path (str): Path to output directory

        Returns:
            bool: Save success flag
        """

        f = open(self.get_save_path(path), 'wb')
        f.write(self.buffer[:self.length])
        f.close()

        return True


    def decompress(self):
        """
        Decompress bz2 file payload
        """

        # Decompress bz2 payload
        try:
            decomp = bz2.decompress(self.buffer[:self.length])
        except Exception:
            return False
        
        self.buffer = decomp
        self.length = len(self.buffer)
        self.compressed = False

        return True


    def get_save_path(self, path):
        """
        Get save path for file based on name and extension
        """

        if self.name[:3] == "IMG":
            name_split = self.name.split("_")
            date = name_split[2][:8]
            time = name_split[2][8:]

            if self.compressed:
                self.ext = ".bz2"
            else:
                self.ext = ""
            
            pathlib.Path(f"{path}\\{date}\\{time}").mkdir(parents=True, exist_ok=True)
            return f"{path}\\{date}\\{time}\\{self.name}{self.ext}"

        elif self.ext == ".tar":
            return f"{path}\\{self.name}{self.ext}"


    def get_int(self, data):
        """
        Get integer from bytes
        """

        return int.from_bytes(data, 'little')
