#!/usr/bin/env python3

import argparse
import glob

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from vm import Chip8
from peripherals import (
    Display,
    Keyboard,
)

roms = []
for rom in sorted(glob.glob('../roms/*')):
    roms.append(rom)
rom_options = ', '.join('{}. {}'.format(n, path.split('/')[-1]) for n, path in enumerate(roms))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='make ROM=[rom]')
    parser.add_argument('rom', type=int, help=rom_options)
    args = parser.parse_args()
    rom = roms[args.rom]

    display = Display()
    keyboard = Keyboard()
    chip8 = Chip8(display, keyboard)
    chip8.run(rom)
