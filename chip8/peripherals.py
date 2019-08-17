#!/usr/bin/env python3

import pygame

from config import (
    TITLE,
    DISPLAY_WIDTH,
    DISPLAY_HEIGHT,
    SCALE_FACTOR,
    COLORS,
)


class Display:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        size = (DISPLAY_WIDTH * SCALE_FACTOR, DISPLAY_HEIGHT * SCALE_FACTOR)
        self.surface = pygame.display.set_mode(size)
        self.frameBuffer = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT)

    def __str__(self):
        res = ''
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                res += str(self.frameBuffer[x + y * DISPLAY_WIDTH])
            res += '\n'
        return res

    def draw_sprite(self, x, y, data):
        erased = False
        for yy, byte in enumerate(data):
            for xx, bit in enumerate(bits(byte)):
                erased = self.write_to_buffer(x + xx, y + yy, bit) or erased
        return erased

    def write_to_buffer(self, x, y, color_code):
        if x >= DISPLAY_WIDTH or y >= DISPLAY_HEIGHT:
            return
        # x, y = x % DISPLAY_WIDTH, y % DISPLAY_HEIGHT
        prev_filled = self.filled(x, y)
        cur_filled = color_code ^ prev_filled
        self.frameBuffer[x + y * DISPLAY_WIDTH] = cur_filled

        return prev_filled and not cur_filled

    def filled(self, x, y):
        return self.frameBuffer[x + y * DISPLAY_WIDTH] == 1

    def clear(self):
        self.frameBuffer = bytearray(DISPLAY_WIDTH * DISPLAY_HEIGHT)
        self.surface.fill(COLORS[0])

    def update(self):
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                x_scaled = x * SCALE_FACTOR + 1
                y_scaled = y * SCALE_FACTOR + 1
                rect = (x_scaled, y_scaled, SCALE_FACTOR - 2, SCALE_FACTOR - 2)
                color = self.frameBuffer[x + y * DISPLAY_WIDTH]
                pygame.draw.rect(self.surface, COLORS[color], rect)
        pygame.display.update()

    def playBeep(self):
        #TODO
        print('beep')


class Keyboard():

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_4]:
            return 0x1
        elif keys[pygame.K_5]:
            return 0x2
        elif keys[pygame.K_6]:
            return 0x3
        elif keys[pygame.K_7]:
            return 0xC
        elif keys[pygame.K_r]:
            return 0x4
        elif keys[pygame.K_t]:
            return 0x5
        elif keys[pygame.K_y]:
            return 0x6
        elif keys[pygame.K_u]:
            return 0xD
        elif keys[pygame.K_f]:
            return 0x7
        elif keys[pygame.K_g]:
            return 0x8
        elif keys[pygame.K_h]:
            return 0x9
        elif keys[pygame.K_j]:
            return 0xE
        elif keys[pygame.K_v]:
            return 0xA
        elif keys[pygame.K_b]:
            return 0x0
        elif keys[pygame.K_n]:
            return 0xB
        elif keys[pygame.K_m]:
            return 0xF
        else:
            return None


def bits(n):
    return (int(i) for i in '{:08b}'.format(n))
