#!/usr/bin/env python3

import pytest

from chip8.config import (
    PC_START,
    FONTSET_START,
    FONTSET_END,
    FONTSET,
)
from chip8.peripherals import (
    Display,
    Keyboard,
)
from chip8.vm import (
    Chip8,
    Instruction,
)

display = Display()
keyboard = Keyboard()
chip8 = Chip8(display, keyboard)


def setup_module(module):
    chip8.reset()

def test_fontset():
    chip8.init_memory()
    assert chip8.memory[FONTSET_START:FONTSET_END] == bytearray(FONTSET)


def test_load():
    rom_data = bytearray([0x01, 0x23, 0x45, 0x67, 0x89])
    chip8.load(rom_data)
    assert chip8.memory[PC_START:PC_START+len(rom_data)] == rom_data


def test_fetch():
    rom_data = bytearray([0x01, 0x23, 0x45, 0x67, 0x89])
    chip8.load(rom_data)
    opcode0 = chip8.fetch()
    assert opcode0 == 0x0123
    chip8.pc += 2
    opcode1 = chip8.fetch()
    assert opcode1 == 0x4567


@pytest.mark.parametrize('arg, expected', [
    (0x0000, Instruction.SYS),
    (0x00E0, Instruction.CLS),
    (0x00EE, Instruction.RET),
    (0x1000, Instruction.JPAddr),
    (0x2000, Instruction.CALL),
    (0x3000, Instruction.SEVxByte),
    (0x4000, Instruction.SNEVxByte),
    (0x5000, Instruction.SEVxVy),
    (0x6000, Instruction.LDVxByte),
    (0x7000, Instruction.ADDVxByte),
    (0x8000, Instruction.LDVxVy),
    (0x8001, Instruction.OR),
    (0x8002, Instruction.AND),
    (0x8003, Instruction.XOR),
    (0x8004, Instruction.ADDVxVy),
    (0x8005, Instruction.SUB),
    (0x8006, Instruction.SHR),
    (0x8007, Instruction.SUBN),
    (0x800E, Instruction.SHL),
    (0x9000, Instruction.SNEVxVy),
    (0xA000, Instruction.LDIAddr),
    (0xB000, Instruction.JPV0Addr),
    (0xC000, Instruction.RND),
    (0xD000, Instruction.DRW),
    (0xE09E, Instruction.SKP),
    (0xE0A1, Instruction.SKNP),
    (0xF007, Instruction.LDVxDT),
    (0xF00A, Instruction.LDVxK),
    (0xF015, Instruction.LDDTVx),
    (0xF018, Instruction.LDSTVx),
    (0xF01E, Instruction.ADDIVx),
    (0xF029, Instruction.LDFVx),
    (0xF033, Instruction.LDBVx),
    (0xF055, Instruction.LDIVx),
    (0xF065, Instruction.LDVxI),
    (0xFFFF, Instruction.UNKNOWN),
])
def test_decode(arg, expected):
    inst = Chip8.decode(arg)
    assert inst == expected


# TODO
def test_00E0():
    pass


def test_1nnn():
    chip8.execute(0x1234)
    assert chip8.pc == 0x234


def test_2nnn():
    pc_prev = chip8.pc
    chip8.execute(0x2123)
    assert chip8.stack[-1] == pc_prev
    assert chip8.pc == 0x123


def test_3xkk():
    chip8.execute(0x6123)
    pc_prev = chip8.pc
    chip8.execute(0x3122)
    assert chip8.pc == pc_prev + 2
    chip8.execute(0x6123)
    pc_prev = chip8.pc
    chip8.execute(0x3123)
    assert chip8.pc == pc_prev + 4

def test_4xkk():
    chip8.execute(0x6011)
    pc_prev = chip8.pc
    chip8.execute(0x4011)
    assert chip8.pc == pc_prev + 2
    chip8.execute(0x6011)
    pc_prev = chip8.pc
    chip8.execute(0x4012)
    assert chip8.pc == pc_prev + 4

def test_5xy0():
    chip8.execute(0x6011)
    chip8.execute(0x6112)
    pc_prev = chip8.pc
    chip8.execute(0x5010)
    assert chip8.pc == pc_prev + 2
    chip8.execute(0x6111)
    pc_prev = chip8.pc
    chip8.execute(0x5010)
    assert chip8.pc == pc_prev + 4

def test_6xkk():
    chip8.execute(0x6012)
    assert chip8.v[0x0] == 0x12
    chip8.execute(0x6FFF)
    assert chip8.v[0xF] == 0xFF


def test_7xkk():
    chip8.execute(0x6012)
    chip8.execute(0x7001)
    assert chip8.v[0x0] == 0x13


def test_8xy0():
    chip8.execute(0x61AB)
    chip8.execute(0x8010)
    assert chip8.v[0x0] == 0xAB

def test_8xy1():
    chip8.execute(0x60A2)
    chip8.execute(0x612F)
    chip8.execute(0x8011)
    assert chip8.v[0x0] == 0xA2 | 0x2F

def test_8xy2():
    chip8.execute(0x6012)
    chip8.execute(0x6123)
    chip8.execute(0x8012)
    assert chip8.v[0x0] == 0x12 & 0x23

def test_8xy3():
    chip8.execute(0x60A2)
    chip8.execute(0x612F)
    chip8.execute(0x8013)
    assert chip8.v[0x0] == 0xA2 ^ 0x2F

def test_8xy4():
    chip8.execute(0x6001)
    chip8.execute(0x6123)
    chip8.execute(0x8014)
    assert chip8.v[0x0] == 0x01 + 0x23
    assert chip8.v[0xF] == 0
    chip8.execute(0x60FF)
    chip8.execute(0x6101)
    chip8.execute(0x8014)
    assert chip8.v[0x0] == 0x00
    assert chip8.v[0xF] == 1

def test_8xy5():
    chip8.execute(0x60AB)
    chip8.execute(0x6189)
    chip8.execute(0x8015)
    assert chip8.v[0x0] == 0xAB - 0x89
    assert chip8.v[0xF] == 1
    chip8.execute(0x6000)
    chip8.execute(0x6101)
    chip8.execute(0x8015)
    assert chip8.v[0x0] == 0xFF
    assert chip8.v[0xF] == 0

def test_8xy6():
    chip8.execute(0x6001)
    chip8.execute(0x8006)
    assert chip8.v[0xf] == 0x1
    assert chip8.v[0x0] == 0x1 >> 1
    chip8.execute(0x6002)
    chip8.execute(0x8006)
    assert chip8.v[0xf] == 0x0
    assert chip8.v[0x0] == 0x2 >> 1

def test_8xy7():
    chip8.execute(0x6089)
    chip8.execute(0x61AB)
    chip8.execute(0x8017)
    assert chip8.v[0x0] == 0xAB - 0x89
    assert chip8.v[0xF] == 1
    chip8.execute(0x6001)
    chip8.execute(0x6100)
    chip8.execute(0x8017)
    assert chip8.v[0x0] == 0xFF
    assert chip8.v[0xF] == 0

def test_8xyE():
    chip8.execute(0x6001)
    chip8.execute(0x800E)
    assert chip8.v[0xf] == 0x0
    assert chip8.v[0x0] == 0x1 << 1
    chip8.execute(0x60FF)
    chip8.execute(0x800E)
    assert chip8.v[0xf] == 0x1
    assert chip8.v[0x0] == (0xFF << 1) & 0xFF

def test_9xy0():
    chip8.execute(0x6011)
    chip8.execute(0x6112)
    pc_prev = chip8.pc
    chip8.execute(0x9010)
    assert chip8.pc == pc_prev + 4
    chip8.execute(0x6111)
    pc_prev = chip8.pc
    chip8.execute(0x9010)
    assert chip8.pc == pc_prev + 2

def test_Annn():
    chip8.execute(0xA123)
    assert chip8.i == 0x123

def test_Bnnn():
    chip8.execute(0x6077)
    chip8.execute(0xB123)
    assert chip8.pc == 0x77 + 0x123

def test_Cxkk():
    chip8.execute(0xC0FF)
    assert 0x0 <= chip8.v[0x0] <= 0xFF

# TODO
def test_Dxyn():
    chip8.i = FONTSET_START
    chip8.execute(0xD115)
    assert chip8.v[0xF] == 0
    chip8.execute(0xD115)
    assert chip8.v[0xF] == 1
def test_Ex9E():
    pass
def test_ExA1():
    pass

def test_Fx07():
    chip8.delay_timer = 0x12
    chip8.execute(0xF307)
    assert chip8.v[3] == 0x12

# TODO
def test_Fx0A():
    pass

def test_Fx15():
    chip8.execute(0x6012)
    chip8.execute(0xF015)
    assert chip8.delay_timer == 0x12

def test_Fx18():
    chip8.execute(0x601A)
    chip8.execute(0xF018)
    assert chip8.sound_timer == 0x1A

def test_Fx1E():
    chip8.execute(0xA123)
    chip8.execute(0x6123)
    chip8.execute(0xF11E)
    assert chip8.i == 0x146

@pytest.mark.parametrize('arg, expected', [
    (0x0, FONTSET_START + 5 * 0x0),
    (0x1, FONTSET_START + 5 * 0x1),
    (0x2, FONTSET_START + 5 * 0x2),
    (0x3, FONTSET_START + 5 * 0x3),
    (0x4, FONTSET_START + 5 * 0x4),
    (0x5, FONTSET_START + 5 * 0x5),
    (0x6, FONTSET_START + 5 * 0x6),
    (0x7, FONTSET_START + 5 * 0x7),
    (0x8, FONTSET_START + 5 * 0x8),
    (0x9, FONTSET_START + 5 * 0x9),
    (0xA, FONTSET_START + 5 * 0xA),
    (0xB, FONTSET_START + 5 * 0xB),
    (0xC, FONTSET_START + 5 * 0xC),
    (0xD, FONTSET_START + 5 * 0xD),
    (0xE, FONTSET_START + 5 * 0xE),
    (0xF, FONTSET_START + 5 * 0xF),
])
def test_Fx29(arg, expected):
    chip8.v[0] = arg
    chip8.execute(0xF029)
    assert chip8.i == expected

def test_Fx33():
    chip8.execute(0x607B)
    chip8.execute(0xA000)
    chip8.execute(0xF033)
    assert chip8.memory[0x0] == 0x1
    assert chip8.memory[0x1] == 0x2
    assert chip8.memory[0x2] == 0x3

def test_Fx55():
    chip8.execute(0x6001)
    chip8.execute(0x6123)
    chip8.execute(0x6245)
    chip8.execute(0x6367)
    chip8.execute(0x6489)
    chip8.execute(0xA111)
    chip8.execute(0xF455)
    assert chip8.memory[0x111:0x116] == bytearray([0x01, 0x23, 0x45, 0x67, 0x89])

def test_Fx65():
    rom_data = bytearray([0x01, 0x23, 0x45, 0x67, 0x89])
    chip8.load(rom_data)
    chip8.execute(0xA201)
    chip8.execute(0xF265)
    assert chip8.v[0x0] == 0x23
    assert chip8.v[0x1] == 0x45
    assert chip8.v[0x2] == 0x67
