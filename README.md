# Processor-Core-Design

Use verilog to design a single-cycle processor with Quartus II.
Download the program into the FPGA and we can see the results.
To run the program, make sure the .hex file are in the same directory. And change the file name in imem and dmem accordingly.

Before reset is asserted high, the state of the processor is undefined. After reset is asserted, the processor begins execution from instruction memory address zero with all zeros in the register file.

Instruction set:
|Instruction  |Opcode|Type  |Usage            |   Operation                                      |
| ------------|:----:|:-----:| :-------------:|:----------------------------------------------:|
|add          |00000 |R     |add $rd, $rs, $rt|   $rd = $rs + $rt                                |
|sub          |00001 |R     |sub $rd, $rs, $rt|   $rd = $rs – $rt                    |
|and          |00010 |R     |and $rd, $rs, $rt|   $rd = $rs AND $rt|
|or           |00011 |R     |or $rd, $rs, $rt |   $rd = $rs OR $rt|
|sll          |00100 |R     |sll $rd, $rs, $rt|   $rd = $rs shifted left by $rt[4:0], zero-fill  |
|srl          |00101 |R     |srl $rd, $rs, $rt|   $rd = $rs shifted right by $rt[4:0], zeroextend|
|addi         |00110 |I     |addi $rd, $rs, N |   $rd = $rs + N                    |
|lw           |00111 |I     |lw $rd, N($rs)   |   $rd = Mem[$rs+N] |
|sw           |01000 |I     |sw $rd, N($rs)   |   Mem[$rs+N] = $rd|
|beq          |01001 |I     |beq $rd, $rs, N  |   if ($rd==$rs) then PC=PC+1+N           |
|bgt          |01010 |I     |bgt $rd, $rs, N  |   if ($rd>$rs) then PC=PC+1+N           |
|jr           |01011 |I     |jr $rd           |   PC = $rd               |
|j            |01100 |J     |j N              |   PC = N               |
|jal          |01101 |J     |jal N            |   $r31=PC+1; PC = N          |
|input        |01110 |I     |input $rd        |   $rd = keyboard input          |
|output       |01111 |I     |output $rd       |   print character $rd[7:0] on LCD display       |

The formats of the R, I, and J type instructions are shown below.
|Type |Format|
|R    |Opcode [31:27]   Rd [26:22]   Rs [21:17]   Rt [16:12]       Zeroes [11:0]|
|I    |Opcode [31:27]   Rd [26:22]   Rs [21:17]   Immediate [16:0]|
|J    |Opcode [31:27]   Target [26:0]|
