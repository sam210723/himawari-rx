"""
xrit-img.py
https://github.com/sam210723/himawari-rx

Generates images from LRIT/HRIT files
"""

import argparse
from collections import namedtuple
import colorama
from colorama import Fore, Back, Style
import glob
import numpy as np
import os
from PIL import Image

argp = argparse.ArgumentParser(description="Generates images from LRIT/HRIT files")
argp.add_argument("INPUT", action="store", help="xRIT file (or folder) to process")
argp.add_argument("-s", action="store_true", help="Process incomplete images as individual segments")
argp.add_argument("-o", action="store_true", help="Overwrite existing images")
args = argp.parse_args()

# Globals
files = []
groups = {}
total_segments = 10

# Named tuples
FileName = namedtuple('FileName' , 'channel date time segment full')

def init():
    """
    Locate files and create image groups
    """
    global files
    global groups

    # Initialise Colorama
    colorama.init(autoreset=True)

    # Input is directory
    if os.path.isdir(args.INPUT):
        for f in glob.glob(f"{args.INPUT}\\IMG_*[!.png]"):
            files.append(f)
        files.sort()
    
        # Check at least one file was found
        if len(files) < 1:
            print(f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}NO xRIT IMG FILES FOUND")
            print("Exiting...")
            exit(1)
        
        # Print file list
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"  - {f}")
        
        # Group segments
        for f in files:
            name = parse_name(f)
            
            # Create new group
            if name.full not in groups:
                groups[name.full] = {}

            # Add image to group
            groups[name.full][name.segment] = f
        
        # Print image list
        print(f"\nFound {len(groups)} images:")
        for i in list(groups):
            print(f"  {i}")

            # Check for missing segments
            located_segments = len(groups[i])

            if located_segments == total_segments:
                print(f"    {Fore.GREEN}{Style.BRIGHT}Found all segments")
            else:
                print(f"    {Fore.WHITE}{Back.RED}{Style.BRIGHT}MISSING {total_segments - located_segments} SEGMENTS")

                if args.s:
                    print("    PROCESSING WITH MISSING SEGMENTS")
                else:
                    print("    IMAGE WILL BE SKIPPED")
                    groups.pop(i, None)
            
            # Check image has not already been generated
            if os.path.isfile(f"{args.INPUT}\\{name.full}.png") and not args.o:
                print("    IMAGE ALREADY GENERATED...SKIPPING (use -o to overwrite existing images)")
                groups.pop(i, None)
            print()
        
        print("-----------------------------------------\n")

        # Process each image group
        for i in groups:
            process_group(i, groups[i])
            print()
    
    # Input is a file
    else:
        process_single(args.INPUT)


def process_group(name, group):
    """
    Process group of segments
    """
    
    print(f"{name}:")

    images = {}

    # Create image from each file in group
    for seg in group:
        img = process_single(group[seg], False)
        images[seg] = img

    # Create output image
    i = next(iter(images))
    h = images[i].height * total_segments
    v = images[i].width
    out_i = Image.new("L", (h, v))

    # Add segments to output image
    for i in images:
        img = images[i]
        offset = img.height * (i - 1)
        out_i.paste(img, (0, offset))
    
    out_i.save(f"{args.INPUT}\\{name}.png", format="PNG")
    print(f"  {Fore.GREEN}{Style.BRIGHT}SAVED \"{args.INPUT}\\{name}.png\"\n")

def process_single(path, save=True):
    """
    Process single image segment
    """
    
    # Parse file name
    name = parse_name(path)
    if save: print(f"{name.full}:")

    # Get file fields
    header, data = load_hrit(path)

    # Get image properties from HRIT header
    h, v, bpp = get_image_properties(header)
    print(f"  {h}x{v} @ {bpp} bpp")

    # Create numpy array from data field
    z = np.frombuffer(data, dtype=f">u{int(bpp / 8)}", count=h*v).reshape(v, h)

    #TODO: Save native 16-bit images
    #TEMP: 16-bit to 8-bit depth conversion
    if bpp == 16: z = z / 4
    
    #i = Image.frombuffer("I;16", [h, v], z.astype('uint16'), 'raw', 'I;16', 0, 1)
    i = Image.frombuffer("L", [h, v], z.astype('uint8'), 'raw', 'L', 0, 1)
    
    # Save image or return object
    if save:
        i.save(f"{args.INPUT}.png")
    else:
        return i


def load_hrit(path):
    """
    Load HRIT file from disk
    """

    payload = b''
    
    # Read file contents
    with open(path, 'rb') as f:
        payload = f.read()
        f.close()
    
    # Get HRIT field lengths
    header_len, data_len = parse_primary(payload)

    # Separate header and data fields
    header = payload[:header_len]
    data = payload[header_len:]

    return header, data


def parse_name(path):
    """
    Parse HRIT file name into tuple
    """

    basename = os.path.basename(path)
    split = basename.split("_")

    return FileName(
        split[1],
        split[2][:8],
        split[2][8:],
        int(split[3][:3]),
        basename[:-9]
    )


def parse_primary(data):
    """
    Parse HRIT primary header
    """

    primary_header = data[:16]
    header_len = int.from_bytes(primary_header[4:8], 'big')
    data_len = int.from_bytes(primary_header[8:16], 'big')

    return header_len, data_len


def get_image_properties(header):
    """
    Get image resolution and bit depth from HRIT header
    """

    header = header[16:25]
    h = int.from_bytes(header[4:6], 'big')
    v = int.from_bytes(header[6:8], 'big')
    bpp = header[3]

    return h, v, bpp


try:
    init()
except KeyboardInterrupt:
    print("Exiting...")
    exit()
