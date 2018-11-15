ECE 550 ASSEMBLER/DISASSEMBLER
------------------------------
(Last revised 2016-10-24 by Tyler Bletsch for ECE 550, Fall 2016)

We have provided a simple assembler and disassembler for the Duke 550 CPU.
Currently, these tools have only been tested on Linux x86 systems, e.g.
login.oit.duke.edu.

== UPDATES ==
  - rev1, 2016-10-16. Initial release.
  - rev2, 2016-10-24. Fix bug in test-simple.s.
  - rev3, 2016-10-25. Fix another bug in test-simple.s.

== THE ASSEMBLER ==

The assembler takes one argument, which is the filename of an assembly-language 
program.  It writes two memory initialization files:
  - one for the instruction memory (-imem.hex) 
  - one for the data memory (-dmem.hex)

To assemble the test program that is included, type './asm.py example.s'.
For help, run the program without arguments, e.g. './asm.py'.

KNOWN LIMITATIONS: The assembler does not support referencing labels in instructions
(e.g. "j endloop"), but it does support specifying labels ("endloop:"). If run
with the "-v" option, it will report all label offsets, allowing you manually patch
in labels. Additionally, only decimal integers are supported for immediates in 
instructions.

The output format is the Intel HEX format, which specifies words using a special
notiation, see: https://en.wikipedia.org/wiki/Intel_HEX

You can also add the -v flag to the assembler to output debug information,
including the symbol table.

Please note that the program needs to have a ".text" header marking the beginning 
of the instructions. A ".data" header is also necessary to mark the beginning of 
the static data section. In case of doubt, look at the organization of the 
included example program. 

== THE DISASSEMBLER ==

Disassembly is the process of converting binary files back into human-readable 
assembly. Naturally, some information is not recoverable, such as original comments
and labels.

It is provided in order to verify constructed binaries, to test the assembler, and
to reverse engineer two HEX files for which the source was not available.

To disassemble an imem.hex file:
  ./disasm.py <imem.hex>

It supports a variety of options to tune the output; run the tool without
arguments for a help message, e.g. './disasm.py'.

If you'd like to disassemble a hex file in such a way that the assembler could 
re-assemble it, use:
  ./disasm.py -xd <imem.hex> -D <dmem.hex>

