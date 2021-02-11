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
        self.buffer = None          # Byte array for file payload
        self.part_counter = 0       # Number of parts received
        self.temp_parts = []        # List of parts which arrived before info
        self.ignored = False        # File is associated with ignored channel
        self.complete = False       # All file parts have been received
        self.compressed = True      # File compression state flag


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

        # Process parts received before info
        if len(self.temp_parts) > 0:
            for part in self.temp_parts:
                self.add(part)
            self.temp_parts = []


    def add(self, data):
        """
        Add data to file payload
        """

        # Get file part number and byte offset
        part = self.get_int(data[8:10])

        try:
            self.name
        except AttributeError:
            self.temp_parts.append(data)
            return len(self.temp_parts)

        # Add data to file payload
        offset = part * 1411
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
            
            pathlib.Path(f"{path}/{date}/{time}").mkdir(parents=True, exist_ok=True)
            return f"{path}/{date}/{time}/{self.name}{self.ext}"

        elif self.ext == ".tar":
            return f"{path}/{self.name}{self.ext}"
        else:
            return f"{path}/{self.name}"


    def get_int(self, data):
        """
        Get integer from bytes
        """

        return int.from_bytes(data, 'little')
