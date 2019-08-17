#!/usr/bin/env python3

import pytest

from chip8.config import (
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    SCALE_FACTOR,
    COLORS,
)
from chip8.peripherals import Display

display = Display()

def setup_module(module):
    display.clear()

def test_write_to_buffer():
    args = (0, 0, 1)
    assert not display.write_to_buffer(*args)
    assert display.filled(0, 0)
    assert display.write_to_buffer(*args)
    assert not display.filled(0, 0)

def test_draw_sprite():
    sprite = [0xFF, 0xFF]
    assert not display.draw_sprite(0, 0, sprite)
    assert display.draw_sprite(0, 1, sprite)
