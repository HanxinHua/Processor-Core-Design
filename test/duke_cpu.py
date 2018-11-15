#!/usr/bin/python

# Base library and ISA description code for the Duke 250/550 tool suite
# By Tyler Bletsch, Fall 2016

import os,sys,re

# vvvvvv ISA specification vvvvvv
INSTR_BITS = 32 # bit width of instructions (this is probably just the word size of the system)
REG_BITS = 32   # bit width of registers (this is probably just the word size of the system)

# Define the fields of the R-, I-, and J-type instructions here
type_formats = {  
    'R': (
        ('opcode',5),
        ('rd',5),
        ('rs',5),
        ('rt',5),
        ('zeroes',12),
    ),
    'I': (
        ('opcode',5),
        ('rd',5),
        ('rs',5),
        ('imm',17),
    ),
    'J': (
        ('opcode',5),
        ('imm',27),
    ),
}
# ^^^^^^ ISA specification ^^^^^^

OPCODE_BITS = type_formats.values()[0][0][1] # the FIRST format; the FIRST field of that format (which is opcode), the SECOND value (the number of bits)

def iff(c,a,b):
    if c: return a
    else: return b
def ones(n):
    return ((1<<n)-1)
def get_bits(val,hi,lo):
    return (val>>lo) & ones(hi-lo+1)
def sign_extend(n,hi_bit):
    if n & (1<<hi_bit): # if negative, extend with 1s
        n |= ~ones(hi_bit)
    return n
def unsigned_hex(val,nbits):
    return "%*x" % (nbits/4, val & ones(nbits))
def signed_hex(val):
    if val<0:
        return "-0x%x" % -val
    else:
        return "0x%x" % val
        
# abstract base class for instructions
# never instantiate directly, intead use the Instruction.from_instr_val() and Instruction.assemble() constructors, which create appropriately subclassed instructions
class Instruction(object):
    #defaults for argument fields:
    rs=0
    rt=0
    rd=0
    imm=0
    zeroes=0 # for unused fields of instructions
    
    @staticmethod
    # create an appropriately subclassed instruction object based on a binary value (for decoding/disassembling machine code)
    def from_instr_val(instr_val):
        opcode = get_bits(instr_val,INSTR_BITS-1,INSTR_BITS-1-OPCODE_BITS+1)
        if opcode not in opcode2class:
            raise ValueError("No such opcode as '0x%02x' for instruction 0x%08x." % (opcode,instr_val))
        cls = opcode2class[opcode]
        self = cls()
        self.instr_val = instr_val
        self.decode()
        return self
        
    @staticmethod
    # create an appropriately subclassed instruction object based on an opname and arguments (for assembling from human-written code)
    def assemble(opname, args):
        if opname not in opname2class:
            raise ValueError("No such instruction as '%s' in the OPS table." % opname)
        cls = opname2class[opname]
        self = cls()
        self.asm_args_parse(args)
        self.encode()
        return self
        
    # parse human-written arguments according to the subclass's args_usage and set object attributes accordingly
    def asm_args_parse(self, args, allow_labels=False):
        # convert a usage string like "$rs, $rt, $rd" into a regex that captures arguments in the given format
        usage_regex = self.args_usage
        usage_regex = re.sub(r'([\(\)])',r'\s*\\\1\s*',usage_regex)         # escape literal parens, allow spaces around them
        usage_regex = re.sub(r'\s*,\s*',r'\\s*,\\s*',usage_regex)           # allow spaces around commas
        usage_regex = re.sub(r'\$r([std])',r'\\$r(?P<r\1>\d+)',usage_regex) # capture $rd as field 'rd', $rt as 'rt', $rs as 'rs'
        usage_regex = re.sub(r'N',r'(?:(?P<imm>-?\d+)|\w+)',usage_regex)              # capture literal N as field 'imm' 
        # ^ (note: we allow this to parse a label instead, in which case the immediate is 0 and should be patched in by the assembler later)
        usage_regex = "^\s*%s\s*$" % usage_regex                            # anchored regex on both sides, allow space padding
        
        #print usage_regex
        #print args
        # then apply that regex to the given args, parsing them out by the names given in the args_usage (exception: 'N' is stored as 'imm')
        m = re.match(usage_regex,args) # apply regex
        if not m: # fail to match?
            raise ValueError("Arguments given to instruction '%s' don't match usage ('%s') (given arguments: '%s')." % (self.opname,self.args_usage,args))
        for k,v in m.groupdict().items():
            #print k,v
            if k=="imm" and v==None: 
                if allow_labels:
                    # in this case we parsed a label instead of a numeric immediate, so we set value to 0 in the expectation that the assembler will patch later
                    v = 0
                else:
                    raise ValueError("Provided instruction contains a label reference, which is not supported.")
            setattr(self, k, int(v))
        
    # produce human-readable assembly instruction using the subclass's args_usage and this object's attributes
    def disasm(self,hex_immediates=True,show_hex_value_comment=False,show_binary_value_comment=False): 
        r = self.args_usage
        if '$rs' in self.args_usage: r = re.sub(r'\$rs', "$r%d"%self.rs, r)
        if '$rt' in self.args_usage: r = re.sub(r'\$rt', "$r%d"%self.rt, r)
        if '$rd' in self.args_usage: r = re.sub(r'\$rd', "$r%d"%self.rd, r)
        if 'N' in self.args_usage: 
            if hex_immediates:
                r = re.sub(r'N', signed_hex(self.imm), r)
            else:
                r = re.sub(r'N', "%d"%self.imm, r)
        r = "%s %s" % (self.opname,r)
        if show_hex_value_comment or show_binary_value_comment:
            r = "%-25s # " % r
        if show_hex_value_comment:
            r += "[%0*x]" % (INSTR_BITS/4,self.instr_val)
        if show_binary_value_comment:
            r += "[%s]" % self.instr_val_binary()
        return r
        
    def instr_val_binary(self):
        return format(self.instr_val,"0%db"%INSTR_BITS)
        
    # make object printable
    def __repr__(self):
        return "<%s: %s (%08x)>" % (type(self).__name__, self.disasm(), self.instr_val)
        
    # use instr_val to decode opname, type, and the component fields based on type_formats (R/I/J-type fields)
    def decode(self):
        format = type_formats[self.type]
        bit=INSTR_BITS-1
        for field_name,field_bits in format:
            setattr(self,field_name,get_bits(self.instr_val,bit,bit-field_bits+1))
            # special handling to sign extend immediate: imm_raw = plain bits copied; imm = sign extended
            if field_name=="imm":
                self.imm_raw = self.imm
                self.imm = sign_extend(self.imm_raw, field_bits-1)
            bit -= field_bits
        
    
    # use opname and component fields to encode instr_val based on type_formats (R/I/J-type fields)
    def encode(self):
        format = type_formats[self.type]
        self.instr_val = 0 # will fill in with bitwise ops
        bit=INSTR_BITS-1
        for field_name,field_bits in format:
            self.instr_val |= (getattr(self,field_name) & ones(field_bits))  << (bit-field_bits+1)
            bit -= field_bits

# vvvvvv ISA specification vvvvvv

# specify instructions as subclasses of Instruction.
# you can specify more instructions than you actually use in this particular ISA; what matters is which classes appear in the OPS table below.
# this makes it easy to swap instructions in and out year-to-year

class Op_add(Instruction):
    opname = "add"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] + simulator.reg[self.rt]

class Op_sub(Instruction):
    opname = "sub"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] - simulator.reg[self.rt]

class Op_and(Instruction):
    opname = "and"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] & simulator.reg[self.rt]

class Op_or(Instruction):
    opname = "or"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] | simulator.reg[self.rt]

class Op_not(Instruction):
    opname = "not"
    type = "R"
    args_usage = "$rd, $rs"
    def sim(self, simulator):
        simulator.reg[self.rd] = ~simulator.reg[self.rs]

class Op_sll(Instruction):
    opname = "sll"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] << get_bits(simulator.reg[self.rt],4,0)

class Op_srl(Instruction):
    opname = "srl"
    type = "R"
    args_usage = "$rd, $rs, $rt"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] >> get_bits(simulator.reg[self.rt],4,0)

class Op_addi(Instruction):
    opname = "addi"
    type = "I"
    args_usage = "$rd, $rs, N"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.reg[self.rs] + self.imm

class Op_lw(Instruction):
    opname = "lw"
    type = "I"
    args_usage = "$rd, N($rs)"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.memory[ simulator.reg[self.rs] + self.imm ]

class Op_sw(Instruction):
    opname = "sw"
    type = "I"
    args_usage = "$rd, N($rs)"
    def sim(self, simulator):
        simulator.memory[ simulator.reg[self.rs] + self.imm ] = simulator.reg[self.rd]

class Op_beq(Instruction):
    opname = "beq"
    type = "I"
    args_usage = "$rd, $rs, N"
    def sim(self, simulator):
        if simulator.reg[self.rd] == simulator.reg[self.rs]:
            simulator.pc += 1+self.imm

class Op_bgt(Instruction):
    opname = "bgt"
    type = "I"
    args_usage = "$rd, $rs, N"
    def sim(self, simulator):
        if simulator.reg[self.rd] > simulator.reg[self.rs]:
            simulator.pc += 1+self.imm

class Op_jr(Instruction):
    opname = "jr"
    type = "I"
    args_usage = "$rd"
    def sim(self, simulator):
        simulator.pc += simulator.reg[self.rd]

class Op_j(Instruction):
    opname = "j"
    type = "J"
    args_usage = "N"
    def sim(self, simulator):
        simulator.pc = self.imm

class Op_jal(Instruction):
    opname = "jal"
    type = "J"
    args_usage = "N"
    def sim(self, simulator):
        simulator.reg[31] = simulator.pc+1
        simulator.pc = self.imm

class Op_input(Instruction):
    opname = "input"
    type = "I"
    args_usage = "$rd"
    def sim(self, simulator):
        simulator.reg[self.rd] = simulator.input()

class Op_output(Instruction):
    opname = "output"
    type = "I"
    args_usage = "$rd"
    def sim(self, simulator):
        simulator.output(simulator.reg[self.rd])

# ops table -- this defines which ops specified above are in your ISA, and what their opcode is
OPS = (   # << ISA specification
    #opname  opcode
    (Op_add,   0x00),
    (Op_sub,   0x01),
    (Op_and,   0x02),
    (Op_or,    0x03),
    (Op_sll,   0x04),
    (Op_srl,   0x05),
    (Op_addi,  0x06),
    (Op_lw,    0x07),
    (Op_sw,    0x08),
    (Op_beq,   0x09),
    (Op_bgt,   0x0a),
    (Op_jr,    0x0b),
    (Op_j,     0x0c),
    (Op_jal,   0x0d),
    (Op_input, 0x0e),
    (Op_output,0x0f),
)
# ^^^^^^ ISA specification ^^^^^^

#opname2class  = {r[0].opname:r[0] for r in OPS} # lookup table 
#opcode2class  = {r[1]       :r[0] for r in OPS} # lookup table
# (sweet dict comprehension syntax needs python 2.7, which teer machines dont have, so here's an ugly tuple thing)
opname2class  = dict((r[0].opname,r[0]) for r in OPS) # lookup table
opcode2class  = dict((r[1]       ,r[0]) for r in OPS) # lookup table
for r in OPS: r[0].opcode = r[1] # make each Op class know its own opcode



if 0:
    print Instruction.assemble("j","50")
    print Instruction.assemble("j","lbl")
    print Instruction.assemble("j","100000")
    print Instruction.from_instr_val(0x6626ddcb)
    #sys.exit(0)
    import random
    i=0
    while i<0x7fffffffff:
        print Instruction.from_instr_val(random.randint(0,0x7fffffff))
        i+=7077
    print Instruction.assemble("add", "$r5, $r9, $r4")
    print Instruction.assemble("or", "$r10, $r7, $r2")
    print Instruction.from_instr_val(0x4aaaaaaa)
