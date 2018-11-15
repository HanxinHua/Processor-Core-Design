#!/usr/bin/python

# Hex file disassembler for the Duke 250/550 tool suite
# By Tyler Bletsch, Fall 2016
VERSION="2016fa.0"

import sys,os,re

from duke_cpu import Instruction,iff,INSTR_BITS,REG_BITS

from optparse import OptionParser

parser = OptionParser("Usage: %prog [options] <file.hex>", description="Assembler for the Duke 250/550 tool suite", version=VERSION)
 
#parser.add_option("-n", "--number", dest="number", help="Quantity of things", metavar="NUM", type="int")
#parser.add_option("-h", "--host", dest="hostname", help="Hostname. Default: %default", metavar="HOST", default="localhost")
#parser.add_option("-s", "--sort", dest="sort", help="Sort by the given key.  One of: length,name.", metavar="KEY", type="choice", choices=['length','name'])
parser.add_option("-v", "--verbose", dest="verbose", help="Print the assembly result to the console.", action="store_true")
 
(options, args) = parser.parse_args()
 
if (len(args)<=0):
        parser.print_help()
        sys.exit(0)

# hacked together quick intel hex writer; only supports fixed record size
class HexWriter(object):
    def __init__(self, filename, record_size):
        self.filename = filename
        self.fp = open(filename,"w")
        self.record_size = record_size
        self.addr = 0
        
    def write_record(self, v):
        record_type = 0x00 # data record
        checksum = self.record_size + (self.addr>>8) + (self.addr & 0xff)
        for i in range(self.record_size):
            checksum += (v>>(8*i)) & 0xff
        checksum = (-checksum) & 0xff
        self.fp.write(":%02x%04x%02x%0*x%02x\n" % (self.record_size, self.addr, record_type, self.record_size*2, v, checksum))
        self.addr += 1
        
    def close(self):
        self.fp.write(":00000001FF\n")
        self.fp.close()

if 0:
    hp = HexWriter("q",4)
    hp.write_record(0x31408000)
    hp.write_record(0x30400000)
    hp.write_record(0x6800002A)
    hp.write_record(0)
    hp.write_record(0)
    hp.close()
        
def assemble(file_in):
    fp = open(file_in,"r")
    labels = {}
    imem=[]
    dmem=[]
    section_text=True
    def cur_counter(): return iff(section_text,len(imem),len(dmem))
    for n,line in enumerate(fp):
        def die(msg):
            print "%s:%d: %s" % (file_in,n,line)
            print "%s:%d: %s" % (file_in,n,msg)
            sys.exit(1)
        line = re.sub(r'^\s*','',line) # eat leading whitespace
        line = re.sub(r'\s*([;#].*)?$','',line) # eat trailing comment and whitespace
        m = re.match(r'^(\w+):',line)
        if m:
            line = re.sub(r'^\w+:\s*','',line) # eat label
            label = m.group(1)
            loc = cur_counter()
            labels[label] = loc
        if line == '': # if nothing left, skip this otherwise blank linke
            continue
        # must be an instr here
        m = re.match('^(\.?\w+)\s*(.*?)\s*$',line)
        if not m:
            die("Unable to parse line '%s'" % (line))
            return False
        opname = m.group(1)
        args = m.group(2)
        if opname==".text":
            section_text=True
        elif opname==".data":
            section_text=False
        elif opname==".word":
            if section_text:
                die("No .word declaration allowed in text section")
            else:
                v = int(args)
                dmem.append(v)
        elif opname==".ascii" or opname==".asciiz":
            if section_text:
                die("No .ascii/.asciiz declaration allowed in text section")
            else:
                m = re.match(r'^\"([^"]+)\"$',args)
                if not m:
                    die("Bad string given to .ascii/.asciiz")
                for ch in m.group(1):
                    dmem.append(ord(ch))
                if opname==".asciiz":
                    dmem.append(0)
        else: # this is an instruction
            if not section_text:
                die("Instruction encountered in data section")
            else: 
                try:
                    instr = Instruction.assemble(opname,args)
                    imem.append(instr)
                except ValueError,e:
                    die(str(e))
    print "Assembled %d data words and %d instruction words." % (len(dmem),len(imem))
    if options.verbose:
        print ""
        print "== dmem =="
        for addr,d in enumerate(dmem):
            print "%08x : %08x" % (addr,d)
        print "== imem =="
        for addr,instr in enumerate(imem):
            print "%08x : %s" % (addr,instr.disasm(show_hex_value_comment=True,show_binary_value_comment=True))
        print "== labels =="
        for label,loc in labels.items():
            print "%-10s : %08x" % (label,loc)
        print ""
    base_filename = re.sub(r'\.\w+$','',file_in)
    imem_filename = "%s-imem.hex" % base_filename
    dmem_filename = "%s-dmem.hex" % base_filename
    
    print "Writing %s..." % dmem_filename
    hp_dmem = HexWriter(dmem_filename,REG_BITS/8)
    for addr,d in enumerate(dmem):
        hp_dmem.write_record(d)
    if len(dmem)==0: 
        # quartus complains about otherwise empty hex files, so we throw them a word
        hp_dmem.write_record(0)
    hp_dmem.close()
            
    print "Writing %s..." % imem_filename
    hp_imem = HexWriter(imem_filename,INSTR_BITS/8)
    for addr,instr in enumerate(imem):
        hp_imem.write_record(instr.instr_val)
    hp_imem.close()
        
            

assemble(args[0])