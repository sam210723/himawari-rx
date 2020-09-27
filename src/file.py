"""
file.py
https://github.com/sam210723/himawari-rx
"""

class File:
    """
    Incoming file object containing file properties and payload
    """

    def __init__(self, name, path, parts, time_a, time_b):
        self.name      = name.split('.')[0]
        self.ext       = name.split('.')[1]
        self.path      = path
        self.parts     = parts
        self.time_a    = time_a
        self.time_b    = time_b
        self.time_diff = time_b[0] - time_a[0]

        self.payload = b''


    def print_info(self):
        """
        Print info about incoming file
        """
        
        print(f"\n[NEW FILE] \"{self.name}\"\n")
