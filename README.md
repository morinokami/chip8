# CHIP-8 emulator written in Python

## Usage

```sh
$ python3 -m venv venv
$ pip -r requirements.txt
$ make help
usage: make ROM=[rom]

positional arguments:
  rom         0. 15PUZZLE, 1. BLINKY, 2. BLITZ, 3. BRIX, 4. CONNECT4, 5.
              GUESS, 6. HIDDEN, 7. INVADERS, 8. KALEID, 9. MAZE, 10. MERLIN,
              11. MISSILE, 12. PONG, 13. PONG2, 14. PUZZLE, 15. SYZYGY, 16.
              TANK, 17. TETRIS, 18. TICTAC, 19. UFO, 20. VBRIX, 21. VERS, 22.
              WIPEOFF

optional arguments:
  -h, --help  show this help message and exit
$ make ROM=7
```

## Key Mapping
```
Keypad                   Keyboard
+-+-+-+-+                +-+-+-+-+
|1|2|3|C|                |1|2|3|4|
+-+-+-+-+                +-+-+-+-+
|4|5|6|D|                |Q|W|E|R|
+-+-+-+-+       =>       +-+-+-+-+
|7|8|9|E|                |A|S|D|F|
+-+-+-+-+                +-+-+-+-+
|A|0|B|F|                |Z|X|C|V|
+-+-+-+-+                +-+-+-+-+
```

## Useful References
* [Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)
* [How to write an emulator (CHIP-8 interpreter) — Multigesture.net](http://www.multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/)
* [CHIP-8 - Wikipedia](https://en.wikipedia.org/wiki/CHIP-8)
* [(Super)CHIP 8 Secrets](https://github.com/AfBu/haxe-chip-8-emulator/wiki/(Super)CHIP-8-Secrets)
