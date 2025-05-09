#!/usr/bin/env python3
"""
Hack Assembler – Nand2Tetris, Lecture 6
---------------------------------------
Translates Hack assembly (.asm) to 16‑bit machine code (.hack).

Usage:
    python hack_assembler.py Foo.asm   ->  Foo.hack
"""

import argparse
import pathlib
import re
import sys

# ───────────────────────────────────────── PARSER ──────────────────────────────────────────
COMMENT_RE = re.compile(r'//.*')

class Parser:
    """Reads, cleans, and yields assembly commands one by one."""
    def __init__(self, file_path: str):
        with open(file_path, 'r', encoding='utf‑8') as f:
            self.lines = [self._clean(l) for l in f]
        # Drop Nones / blanks
        self.lines = [l for l in self.lines if l]

    @staticmethod
    def _clean(line: str) -> str | None:
        line = re.sub(COMMENT_RE, '', line).strip()
        return line or None    # None signals “skip”

    def __iter__(self):
        return iter(self.lines)

# ───────────────────────────────────── SYMBOL TABLE ────────────────────────────────────────
class SymbolTable:
    """Maintains (symbol, address) pairs."""
    _PREDEFINED = {
        'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,
        **{f'R{i}':i for i in range(16)},
        'SCREEN':16384,'KBD':24576
    }

    def __init__(self):
        self.table: dict[str,int] = dict(self._PREDEFINED)
        self._next_var_addr = 16

    def add_label(self, symbol: str, address: int) -> None:
        self.table[symbol] = address

    def resolve(self, symbol: str) -> int:
        """Return numeric value (constant, label, or new variable)."""
        if symbol.isdigit():
            return int(symbol)

        if symbol not in self.table:            # new variable
            self.table[symbol] = self._next_var_addr
            self._next_var_addr += 1
        return self.table[symbol]

# ───────────────────────────────────────── CODE MAP ─────────────────────────────────────────
class Code:
    """Static helpers translating mnemonics  bit‑strings."""
    _DEST = {
        None:   '000',
        'M':    '001', 'D':    '010',  'MD':  '011',
        'A':    '100', 'AM':   '101',  'AD':  '110',
        'AMD':  '111'
    }

    _JUMP = {
        None:   '000',
        'JGT':  '001', 'JEQ':  '010',  'JGE':  '011',
        'JLT':  '100', 'JNE':  '101',  'JLE':  '110',
        'JMP':  '111'
    }

    # 7‑bit comp codes (a c1‑c6).  Complete per Hack spec.
    _COMP = {
        '0'  : '0101010',  '1'  : '0111111',  '-1' : '0111010',
        'D'  : '0001100',  'A'  : '0110000',  'M'  : '1110000',
        '!D' : '0001101',  '!A' : '0110001',  '!M' : '1110001',
        '-D' : '0001111',  '-A' : '0110011',  '-M' : '1110011',
        'D+1': '0011111',  'A+1': '0110111',  'M+1': '1110111',
        'D-1': '0001110',  'A-1': '0110010',  'M-1': '1110010',
        'D+A': '0000010',  'D+M': '1000010',
        'D-A': '0010011',  'D-M': '1010011',
        'A-D': '0000111',  'M-D': '1000111',
        'D&A': '0000000',  'D&M': '1000000',
        'D|A': '0010101',  'D|M': '1010101'
    }

    @classmethod
    def dest(cls, mnem: str | None) -> str:
        return cls._DEST.get(mnem, '000')

    @classmethod
    def comp(cls, mnem: str) -> str:
        try:
            return cls._COMP[mnem]
        except KeyError:
            raise ValueError(f'Unknown comp mnemonic: {mnem!r}') from None

    @classmethod
    def jump(cls, mnem: str | None) -> str:
        return cls._JUMP.get(mnem, '000')

# ───────────────────────────────────────── ASSEMBLER ────────────────────────────────────────
class Assembler:
    def __init__(self, asm_path: str):
        self.parser  = Parser(asm_path)
        self.symtab  = SymbolTable()
        self._first_pass()

    # ───────────── Pass 1:  record label → address ─────────────
    def _first_pass(self) -> None:
        rom_addr = 0
        for line in self.parser:
            if line.startswith('(') and line.endswith(')'):
                label = line[1:-1]
                self.symtab.add_label(label, rom_addr)
            else:
                rom_addr += 1

    # ───────────── Pass 2:  generate machine code ─────────────
    def assemble(self) -> list[str]:
        binary: list[str] = []
        for line in self.parser:
            if line.startswith('('):                        # label – skip
                continue
            if line.startswith('@'):                        # A‑instruction
                symbol = line[1:]
                value  = self.symtab.resolve(symbol)
                binary.append(f'{value:016b}')
            else:                                           # C‑instruction
                binary.append(self._encode_c(line))
        return binary

    @staticmethod
    def _split_c(line: str) -> tuple[str|None,str,str|None]:
        """Return (dest, comp, jump) with dest/jump possibly None."""
        dest, comp, jump = None, line, None
        if '=' in line:
            dest, comp = line.split('=', 1)
        if ';' in comp:
            comp, jump = comp.split(';', 1)
        return dest, comp, jump

    def _encode_c(self, line: str) -> str:
        dest, comp, jump = self._split_c(line)
        return '111' + Code.comp(comp) + Code.dest(dest) + Code.jump(jump)

# ────────────────────────────────────────── CLI ────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description='Hack Assembler (Nand2Tetris)')
    ap.add_argument('asm', type=pathlib.Path, help='Input .asm file')
    args = ap.parse_args()

    if args.asm.suffix.lower() != '.asm':
        sys.exit('Input file must have .asm extension')

    out_path = args.asm.with_suffix('.hack')

    assembler = Assembler(str(args.asm))
    machine   = assembler.assemble()

    out_path.write_text('\n'.join(machine), encoding='utf‑8')
    print(f'Wrote {out_path} ({len(machine)} instructions)')

if __name__ == '__main__':
    main()
