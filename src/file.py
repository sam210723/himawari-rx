"""
file.py
https://github.com/sam210723/himawari-rx
"""

class File:
    """
    Incoming file object containing file properties and payload
    """

    def __init__(self, name, path, parts, length, time_a, time_b):
        self.name      = name.split('.')[0]
        self.ext       = name.split('.')[1]
        self.path      = path
        self.parts     = parts
        self.length    = length
        self.time_a    = time_a
        self.time_b    = time_b
        self.time_diff = time_b[0] - time_a[0]

        self.payload = b''
        self.complete = False

        if self.ext == "bz2": self.ext = "hrit.bz2"
        if self.ext == "tar": self.ext = "txt.tar"


    def add(self, data):
        """
        Add data to file payload
        """

        # Append data to payload
        self.payload += data[16:]

        # Check if last part has been received
        part = self.get_int(data[8:10])
        self.complete = part == (self.parts - 1)

        return len(self.payload)


    def save(self, path):
        """
        Save file payload to disk

        Args:
            path (str): Path to output directory

        Returns:
            bool: Save success flag
        """

        # Check payload length is correct (file content without FEC)
        if len(self.payload) < self.length:
            return False
        
        with open(f"{path}\\{self.name}.{self.ext}", 'wb') as f:
            f.write(self.payload[:self.length])
            f.close()

        return True


    def print_info(self):
        """
        Print info about incoming file
        """

        print(f"\n[FILE] \"{self.name}\"")


    def get_int(self, data):
        """
        Get integer from bytes
        """

        return int.from_bytes(data, 'little')
