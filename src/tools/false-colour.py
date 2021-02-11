"""
false-colour.py
https://github.com/sam210723/himawari-rx

Generates false colour images from multiple grayscale channels
"""

import argparse
import colorama
from colorama import Fore, Back, Style
import glob
from PIL import Image

argp = argparse.ArgumentParser(description="Generates false colour images from multiple grayscale channels")
argp.add_argument("INPUT", action="store", help="Path to folder containing images")
argp.add_argument("-r", action="store", help="Red channel (default: B05)", default="B05")
argp.add_argument("-g", action="store", help="Green channel (default: B04)", default="B04")
argp.add_argument("-b", action="store", help="Blue channel (default: VIS)", default="VIS")
argp.add_argument("-e", action="store", help="Image extension (default: PNG)", default="png")
args = argp.parse_args()

# Globals
files = {}
Image.MAX_IMAGE_PIXELS = None


def init():
    """
    Locate files and create image groups
    """
    global files

    # Initialise Colorama
    colorama.init(autoreset=True)
    
    # Search for channel files
    r = glob.glob(f"{args.INPUT}/IMG_DK01{args.r}_*.{args.e}")
    g = glob.glob(f"{args.INPUT}/IMG_DK01{args.g}_*.{args.e}")
    b = glob.glob(f"{args.INPUT}/IMG_DK01{args.b}_*.{args.e}")

    if len(r) == 0 or len(g) == 0 or len(b) == 0:
        if len(r) == 0: print(f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}MISSING RED CHANNEL")
        if len(g) == 0: print(f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}MISSING GREEN CHANNEL")
        if len(b) == 0: print(f"{Fore.WHITE}{Back.RED}{Style.BRIGHT}MISSING BLUE CHANNEL")

        print("\nExiting...")
        exit(1)
    else:
        print("Image channels:")
        print(f"  R: {Fore.WHITE}{Back.RED}{Style.BRIGHT}{args.r} \"{r[0]}\"")
        print(f"  G: {Fore.WHITE}{Back.GREEN}{Style.BRIGHT}{args.g} \"{g[0]}\"")
        print(f"  B: {Fore.WHITE}{Back.BLUE}{Style.BRIGHT}{args.b} \"{b[0]}\"")
        print()

        process(r[0], g[0], b[0])


def process(r, g, b):
    """
    Create false colour image from individual channels
    """
    
    print("Loading images...")
    
    images = {
        "R": Image.open(r),
        "G": Image.open(g),
        "B": Image.open(b)
    }

    # Print image details
    for i in images:
        print(f"  {i}: {images[i].size[0]}x{images[i].size[1]}")
    print()

    # Scale images to 2750px
    l = 2750
    for i in images:
        if images[i].size[0] != l:
            print(f"Scaling {i} channel...")
            images[i] = images[i].resize((l, l))
    print()
    
    # Combine channels into final image
    print("Combining channels...\n")
    out = Image.merge("RGB", (images["R"], images["G"], images["B"]))

    # Save image to disk
    fpath = f"{args.INPUT}/FC.png"
    out.save(fpath, format="PNG")
    print(f"Image saved to \"{fpath}\"")


try:
    init()
except KeyboardInterrupt:
    print("Exiting...")
    exit()
