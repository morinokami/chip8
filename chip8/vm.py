#!/usr/bin/env python3

from enum import (
    Enum,
    auto,
)
import random
import time

import pygame

from config import (
    CLOCK_SPEED,
    TIMER_SPEED,
    MEMORY_SIZE,
    V_REGISTER_SIZE,
    PC_START,
    FONTSET_START,
    FONTSET_END,
    FONTSET,
)


class Instruction(Enum):
    SYS = auto()        # 0nnn
    CLS = auto()        # 00E0
    RET = auto()        # 00EE
    JPAddr = auto()     # 1nnn
    CALL = auto()       # 2nnn
    SEVxByte = auto()   # 3xkk
    SNEVxByte = auto()  # 4xkk
    SEVxVy = auto()     # 5xy0
    LDVxByte = auto()   # 6xkk
    ADDVxByte = auto()  # 7xkk
    LDVxVy = auto()     # 8xy0
    OR = auto()         # 8xy1
    AND = auto()        # 8xy2
    XOR = auto()        # 8xy3
    ADDVxVy = auto()    # 8xy4
    SUB = auto()        # 8xy5
    SHR = auto()        # 8xy6
    SUBN = auto()       # 8xy7
    SHL = auto()        # 8xyE
    SNEVxVy = auto()    # 9xy0
    LDIAddr = auto()    # Annn
    JPV0Addr = auto()   # Bnnn
    RND = auto()        # Cxkk
    DRW = auto()        # Dxyn
    SKP = auto()        # Ex9E
    SKNP = auto()       # ExA1
    LDVxDT = auto()     # Fx07
    LDVxK = auto()      # Fx0A
    LDDTVx = auto()     # Fx15
    LDSTVx = auto()     # Fx18
    ADDIVx = auto()     # Fx1E
    LDFVx = auto()      # Fx29
    LDBVx = auto()      # Fx33
    LDIVx = auto()      # Fx55
    LDVxI = auto()      # Fx65
    UNKNOWN = auto()


class Chip8:

    def __init__(self, display, keyboard):
        self.reset()
        self.display = display
        self.keyboard = keyboard

    def __str__(self):
        opcode = self.fetch()
        desc = 'PC: {}\n'.format(hex(self.pc))
        desc += 'OPCODE: {}\n'.format(hex(opcode))
        desc += 'V: [{}]\n'.format(', '.join('{}'.format(hex(v))
                                             for v in self.v))
        desc += 'I: {}\n'.format(hex(self.i))
        desc += 'STACK: [{}]'.format(', '.join('{}'.format(hex(v))
                                               for v in self.stack))
        return desc

    # Initialize

    def reset(self):
        self.memory = bytearray(MEMORY_SIZE)
        self.v = bytearray(V_REGISTER_SIZE)
        self.delay_timer = 0
        self.sound_timer = 0
        self.i = 0
        self.pc = PC_START
        self.stack = []

    def load(self, rom_data):
        self.init_memory()
        for i, val in enumerate(rom_data):
            self.memory[PC_START + i] = val

    def read_rom(self, rom):
        with open(rom, 'rb') as f:
            return f.read()

    def init_memory(self):
        self.clear_memory()

        for i in range(FONTSET_START, FONTSET_END):
            self.memory[i] = FONTSET[i - FONTSET_START]

    def clear_memory(self):
        for i in range(len(self.memory)):
            self.memory[i] = 0

    # Emulate

    def fetch(self):
        return self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    @staticmethod
    def decode(opcode):
        kk = opcode & 0x00FF
        n = opcode & 0x000F

        if opcode & 0xF000 == 0x0000:
            if opcode == 0x00E0:
                return Instruction.CLS
            elif opcode == 0x00EE:
                return Instruction.RET
            else:
                return Instruction.SYS
        elif opcode & 0xF000 == 0x1000:
            return Instruction.JPAddr
        elif opcode & 0xF000 == 0x2000:
            return Instruction.CALL
        elif opcode & 0xF000 == 0x3000:
            return Instruction.SEVxByte
        elif opcode & 0xF000 == 0x4000:
            return Instruction.SNEVxByte
        elif opcode & 0xF000 == 0x5000:
            return Instruction.SEVxVy
        elif opcode & 0xF000 == 0x6000:
            return Instruction.LDVxByte
        elif opcode & 0xF000 == 0x7000:
            return Instruction.ADDVxByte
        elif opcode & 0xF000 == 0x8000:
            if n == 0x0:
                return Instruction.LDVxVy
            elif n == 0x1:
                return Instruction.OR
            elif n == 0x2:
                return Instruction.AND
            elif n == 0x3:
                return Instruction.XOR
            elif n == 0x4:
                return Instruction.ADDVxVy
            elif n == 0x5:
                return Instruction.SUB
            elif n == 0x6:
                return Instruction.SHR
            elif n == 0x7:
                return Instruction.SUBN
            elif n == 0xE:
                return Instruction.SHL
        elif opcode & 0xF000 == 0x9000:
            return Instruction.SNEVxVy
        elif opcode & 0xF000 == 0xA000:
            return Instruction.LDIAddr
        elif opcode & 0xF000 == 0xB000:
            return Instruction.JPV0Addr
        elif opcode & 0xF000 == 0xC000:
            return Instruction.RND
        elif opcode & 0xF000 == 0xD000:
            return Instruction.DRW
        elif opcode & 0xF000 == 0xE000:
            if kk == 0x9E:
                return Instruction.SKP
            elif kk == 0xA1:
                return Instruction.SKNP
        elif opcode & 0xF000 == 0xF000:
            if kk == 0x07:
                return Instruction.LDVxDT
            elif kk == 0x0A:
                return Instruction.LDVxK
            elif kk == 0x15:
                return Instruction.LDDTVx
            elif kk == 0x18:
                return Instruction.LDSTVx
            elif kk == 0x1E:
                return Instruction.ADDIVx
            elif kk == 0x29:
                return Instruction.LDFVx
            elif kk == 0x33:
                return Instruction.LDBVx
            elif kk == 0x55:
                return Instruction.LDIVx
            elif kk == 0x65:
                return Instruction.LDVxI

        return Instruction.UNKNOWN

    def execute(self, opcode):
        print(self.opcode_desc(opcode))

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nnn = opcode & 0x0FFF
        kk = opcode & 0x00FF
        n = opcode & 0x000F
        inst = Chip8.decode(opcode)

        increment_pc = True

        key = self.keyboard.get_input()

        start = time.time()

        if inst == Instruction.SYS:
            # 0nnn - SYS addr
            # Jump to a machine code routine at nnn.
            #
            # This instruction is only used on the old computers on which
            # Chip-8 was originally implemented. It is ignored by modern
            # interpreters.
            raise NotImplementedError(inst)
        elif inst == Instruction.CLS:
            # 00E0 - CLS
            # Clear the display.
            self.display.clear()
        elif inst == Instruction.RET:
            # 00EE - RET
            # Return from a subroutine.
            #
            # The interpreter sets the program counter to the address at the
            # top of the stack, then subtracts 1 from the stack pointer.
            self.pc = self.stack.pop()
        elif inst == Instruction.JPAddr:
            # 1nnn - JP addr
            # Jump to location nnn.
            #
            # The interpreter sets the program counter to nnn.
            self.pc = nnn
            increment_pc = False
        elif inst == Instruction.CALL:
            # 2nnn - CALL addr
            # Call subroutine at nnn.
            #
            # The interpreter increments the stack pointer, then puts the
            # current PC on the top of the stack. The PC is then set to nnn.
            self.stack.append(self.pc)
            self.pc = nnn
            increment_pc = False
        elif inst == Instruction.SEVxByte:
            # 3xkk - SE Vx, byte
            # Skip next instruction if Vx = kk.
            #
            # The interpreter compares register Vx to kk, and if they are
            # equal, increments the program counter by 2.
            if self.v[x] == kk:
                self.pc += 2
        elif inst == Instruction.SNEVxByte:
            # 4xkk - SNE Vx, byte
            # Skip next instruction if Vx != kk.
            #
            # The interpreter compares register Vx to kk, and if they are not
            # equal, increments the program counter by 2.
            if self.v[x] != kk:
                self.pc += 2
        elif inst == Instruction.SEVxVy:
            # 5xy0 - SE Vx, Vy
            # Skip next instruction if Vx = Vy.
            #
            # The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
            if self.v[x] == self.v[y]:
                self.pc += 2
        elif inst == Instruction.LDVxByte:
            # 6xkk - LD Vx, byte
            # Set Vx = kk.
            #
            # The interpreter puts the value kk into register Vx.
            self.v[x] = kk
        elif inst == Instruction.ADDVxByte:
            # 7xkk - ADD Vx, byte
            # Set Vx = Vx + kk.
            #
            # Adds the value kk to the value of register Vx, then stores the
            # result in Vx.
            self.v[x] = (self.v[x] + kk) & 0xFF
        elif inst == Instruction.LDVxVy:
            # 8xy0 - LD Vx, Vy
            # Set Vx = Vy.
            #
            # Stores the value of register Vy in register Vx.
            self.v[x] = self.v[y]
        elif inst == Instruction.OR:
            # 8xy1 - OR Vx, Vy
            # Set Vx = Vx OR Vy.
            #
            # Performs a bitwise OR on the values of Vx and Vy, then stores the
            # result in Vx. A bitwise OR compares the corrseponding bits from
            # two values, and if either bit is 1, then the same bit in the
            # result is also 1. Otherwise, it is 0.
            self.v[x] |= self.v[y]
        elif inst == Instruction.AND:
            # 8xy2 - AND Vx, Vy
            # Set Vx = Vx AND Vy.
            #
            # Performs a bitwise AND on the values of Vx and Vy, then stores
            # the result in Vx. A bitwise AND compares the corrseponding bits
            # from two values, and if both bits are 1, then the same bit in
            # the result is also 1. Otherwise, it is 0.
            self.v[x] &= self.v[y]
        elif inst == Instruction.XOR:
            # 8xy3 - XOR Vx, Vy
            # Set Vx = Vx XOR Vy.
            #
            # Performs a bitwise exclusive OR on the values of Vx and Vy, then
            # stores the result in Vx. An exclusive OR compares the
            # corrseponding bits from two values, and if the bits are not both
            # the same, then the corresponding bit in the result is set to 1.
            # Otherwise, it is 0.
            self.v[x] ^= self.v[y]
        elif inst == Instruction.ADDVxVy:
            # 8xy4 - ADD Vx, Vy
            # Set Vx = Vx + Vy, set VF = carry.
            #
            # The values of Vx and Vy are added together. If the result is
            # greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0.
            # Only the lowest 8 bits of the result are kept, and stored in Vx.
            self.v[0xF] = self.v[x] + self.v[y] > 0xFF
            self.v[x] = (self.v[x] + self.v[y]) & 0xFF
        elif inst == Instruction.SUB:
            # 8xy5 - SUB Vx, Vy
            # Set Vx = Vx - Vy, set VF = NOT borrow.
            #
            # If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is
            # subtracted from Vx, and the results stored in Vx.
            self.v[0xF] = self.v[x] > self.v[y]
            self.v[x] = (self.v[x] - self.v[y]) & 0xFF
        elif inst == Instruction.SHR:
            # 8xy6 - SHR Vx {, Vy}
            # Set Vx = Vx SHR 1.
            #
            # If the least-significant bit of Vx is 1, then VF is set to 1,
            # otherwise 0. Then Vx is divided by 2.
            self.v[0xF] = self.v[x] & 0x01
            self.v[x] >>= 1
        elif inst == Instruction.SUBN:
            # 8xy7 - SUBN Vx, Vy
            # Set Vx = Vy - Vx, set VF = NOT borrow.
            #
            # If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is
            # subtracted from Vy, and the results stored in Vx.
            self.v[0xF] = self.v[y] > self.v[x]
            self.v[x] = (self.v[y] - self.v[x]) & 0xFF
        elif inst == Instruction.SHL:
            # 8xyE - SHL Vx {, Vy}
            # Set Vx = Vx SHL 1.
            #
            # If the most-significant bit of Vx is 1, then VF is set to 1,
            # otherwise to 0. Then Vx is multiplied by 2.
            self.v[0xF] = self.v[x] >> 7
            self.v[x] = (self.v[x] << 1) & 0xFF
        elif inst == Instruction.SNEVxVy:
            # 9xy0 - SNE Vx, Vy
            # Skip next instruction if Vx != Vy.
            #
            # The values of Vx and Vy are compared, and if they are not equal,
            # the program counter is increased by 2.
            if self.v[x] != self.v[y]:
                self.pc += 2
        elif inst == Instruction.LDIAddr:
            # Annn - LD I, addr
            # Set I = nnn.
            #
            # The value of register I is set to nnn.
            self.i = nnn
        elif inst == Instruction.JPV0Addr:
            # Bnnn - JP V0, addr
            # Jump to location nnn + V0.
            #
            # The program counter is set to nnn plus the value of V0.
            self.pc = self.v[0] + nnn
            increment_pc = False
        elif inst == Instruction.RND:
            # Cxkk - RND Vx, byte
            # Set Vx = random byte AND kk.
            #
            # The interpreter generates a random number from 0 to 255, which is
            # then ANDed with the value kk. The results are stored in Vx. See
            # instruction 8xy2 for more information on AND.
            self.v[x] = random.randint(0x0, 0xFF) & kk
        elif inst == Instruction.DRW:
            # Dxyn - DRW Vx, Vy, nibble
            # Display n-byte sprite starting at memory location I at (Vx, Vy),
            # set VF = collision.

            # The interpreter reads n bytes from memory, starting at the
            # address stored in I. These bytes are then displayed as sprites on
            # screen at coordinates (Vx, Vy). Sprites are XORed onto the
            # existing screen. If this causes any pixels to be erased, VF is
            # set to 1, otherwise it is set to 0. If the sprite is positioned
            # so part of it is outside the coordinates of the display, it wraps
            # around to the opposite side of the screen. See instruction 8xy3
            # for more information on XOR, and section 2.4, Display, for more
            # information on the Chip-8 screen and sprites.
            x, y, sprite = self.v[x], self.v[y], self.memory[self.i:self.i+n]
            erased = self.display.draw_sprite(x, y, sprite)
            self.v[0xF] = 1 if erased else 0
        elif inst == Instruction.SKP:
            # Ex9E - SKP Vx
            # Skip next instruction if key with the value of Vx is pressed.
            #
            # Checks the keyboard, and if the key corresponding to the value of
            # Vx is currently in the down position, PC is increased by 2.
            if key == self.v[x]:
                self.pc += 2
        elif inst == Instruction.SKNP:
            # ExA1 - SKNP Vx
            # Skip next instruction if key with the value of Vx is not pressed.
            #
            # Checks the keyboard, and if the key corresponding to the value of
            # Vx is currently in the up position, PC is increased by 2.
            if key != self.v[x]:
                self.pc += 2
        elif inst == Instruction.LDVxDT:
            # Fx07 - LD Vx, DT
            # Set Vx = delay timer value.
            #
            # The value of DT is placed into Vx.
            self.v[x] = self.delay_timer
        elif inst == Instruction.LDVxK:
            # Fx0A - LD Vx, K
            # Wait for a key press, store the value of the key in Vx.
            #
            # All execution stops until a key is pressed, then the value of
            # that key is stored in Vx.
            if key:
                self.v[x] = key
            else:
                increment_pc = False
        elif inst == Instruction.LDDTVx:
            # Fx15 - LD DT, Vx
            # Set delay timer = Vx.
            #
            # DT is set equal to the value of Vx.
            self.delay_timer = self.v[x]
        elif inst == Instruction.LDSTVx:
            # Fx18 - LD ST, Vx
            # Set sound timer = Vx.
            #
            # ST is set equal to the value of Vx.
            self.sound_timer = self.v[x]
        elif inst == Instruction.ADDIVx:
            # Fx1E - ADD I, Vx
            # Set I = I + Vx.
            #
            # The values of I and Vx are added, and the results are stored in I.
            self.i += self.v[x]
        elif inst == Instruction.LDFVx:
            # Fx29 - LD F, Vx
            # Set I = location of sprite for digit Vx.
            #
            # The value of I is set to the location for the hexadecimal sprite
            # corresponding to the value of Vx. See section 2.4, Display, for
            # more information on the Chip-8 hexadecimal font.
            self.i = FONTSET_START + self.v[x] * 5
        elif inst == Instruction.LDBVx:
            # Fx33 - LD B, Vx
            # Store BCD representation of Vx in memory locations I, I+1, and I+2.
            #
            # The interpreter takes the decimal value of Vx, and places the
            # hundreds digit in memory at location in I, the tens digit at
            # location I+1, and the ones digit at location I+2.
            hundrends = self.v[x] // 100
            tens = (self.v[x] // 10) % 10
            ones = self.v[x] % 10
            self.memory[self.i] = hundrends
            self.memory[self.i + 1] = tens
            self.memory[self.i + 2] = ones
        elif inst == Instruction.LDIVx:
            # Fx55 - LD [I], Vx
            # Store registers V0 through Vx in memory starting at location I.
            #
            # The interpreter copies the values of registers V0 through Vx into
            # memory, starting at the address in I.
            for i in range(x + 1):
                self.memory[self.i + i] = self.v[i]
        elif inst == Instruction.LDVxI:
            # Fx65 - LD Vx, [I]
            # Read registers V0 through Vx from memory starting at location I.
            #
            # The interpreter reads values from memory starting at location I
            # into registers V0 through Vx.
            for i in range(x + 1):
                self.v[i] = self.memory[self.i + i]
        elif inst == Instruction.UNKNOWN:
            raise Exception
        else:
            print(self)
            raise NotImplementedError(inst)

        if increment_pc:
            self.pc += 2

        end = time.time()
        elapsed = end - start
        if elapsed < CLOCK_SPEED:
            pygame.time.wait(int((CLOCK_SPEED - elapsed) * 1000))

    def run(self, rom):
        rom_data = self.read_rom(rom)
        self.load(rom_data)
        running = True
        counter = time.time()

        while running:
            # Fetch
            opcode = self.fetch()
            # Decode and execute
            self.execute(opcode)
            # Update timers
            if time.time() - counter > TIMER_SPEED:
                if self.delay_timer > 0:
                    self.delay_timer -= 1
                if self.sound_timer > 0:
                    if self.sound_timer == 1:
                        self.display.playBeep()
                    self.sound_timer -= 1
                counter = time.time()

                self.display.update()

            # Exit if the close buttun is pressed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

    def opcode_desc(self, opcode):
        desc = hex(opcode) + ' '
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nnn = opcode & 0x0FFF
        kk = opcode & 0x00FF
        n = opcode & 0x000F
        inst = Chip8.decode(opcode)

        if inst == Instruction.SYS:
            desc += 'SYS {}'.format(hex(nnn))
        elif inst == Instruction.CLS:
            desc += 'CLS'
        elif inst == Instruction.RET:
            desc += 'RET'
        elif inst == Instruction.JPAddr:
            desc += 'JP {}'.format(hex(nnn))
        elif inst == Instruction.CALL:
            desc += 'CALL {}'.format(hex(nnn))
        elif inst == Instruction.SEVxByte:
            desc += 'SE V{:x}, {}'.format(x, hex(kk))
        elif inst == Instruction.SNEVxByte:
            desc += 'SNE V{:x}, {}'.format(x, hex(kk))
        elif inst == Instruction.SEVxVy:
            desc += 'SE V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.LDVxByte:
            desc += 'LD V{:x}, {}'.format(x, hex(kk))
        elif inst == Instruction.ADDVxByte:
            desc += 'ADD V{:x}, {}'.format(x, hex(kk))
        elif inst == Instruction.LDVxVy:
            desc += 'LD V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.OR:
            desc += 'OR V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.AND:
            desc += 'AND V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.XOR:
            desc += 'XOR V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.ADDVxVy:
            desc += 'ADD V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.SUB:
            desc += 'SUB V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.SHR:
            desc += 'SHR V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.SUBN:
            desc += 'SUBN V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.SHL:
            desc += 'SHL V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.SNEVxVy:
            desc += 'SNE V{:x}, V{:x}'.format(x, y)
        elif inst == Instruction.LDIAddr:
            desc += 'LD I, {}'.format(hex(nnn))
        elif inst == Instruction.JPV0Addr:
            desc += 'JP V0, {}'.format(hex(nnn))
        elif inst == Instruction.RND:
            desc += 'RND V{:x}, byte'.format(x)
        elif inst == Instruction.DRW:
            desc += 'DRW V{:x}, V{:x}, {}'.format(x, y, hex(n))
        elif inst == Instruction.SKP:
            desc += 'SKP V{:x}'.format(x)
        elif inst == Instruction.SKNP:
            desc += 'SKNP V{:x}'.format(x)
        elif inst == Instruction.LDVxDT:
            desc += 'LD V{:x}, DT'.format(x)
        elif inst == Instruction.LDVxK:
            desc += 'LD V{:x}, K'.format(x)
        elif inst == Instruction.LDDTVx:
            desc += 'LD DT, V{:x}'.format(x)
        elif inst == Instruction.LDSTVx:
            desc += 'LD ST, V{:x}'.format(x)
        elif inst == Instruction.ADDIVx:
            desc += 'ADD I, V{:x}'.format(x)
        elif inst == Instruction.LDFVx:
            desc += 'LD F, V{:x}'.format(x)
        elif inst == Instruction.LDBVx:
            desc += 'LD B, V{:x}'.format(x)
        elif inst == Instruction.LDIVx:
            desc += 'LD [I], V{:x}'.format(x)
        elif inst == Instruction.LDVxI:
            desc += 'LD V{:x}, [I]'.format(x)

        return desc
