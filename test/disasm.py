#!/usr/bin/python

# Hex file disassembler for the Duke 250/550 tool suite
# By Tyler Bletsch, Fall 2016
VERSION="2016fa.0"

import sys,os,re

from duke_cpu import Instruction,iff,INSTR_BITS

from optparse import OptionParser

parser = OptionParser("Usage: %prog [options] <file-imem.hex>", description="Hex file disassembler for the Duke 250/550 tool suite", version=VERSION)
 
parser.add_option("-x", "--no-hex-values", dest="no_hex_values", help="Don't include hex instruction values as comments.", action="store_true")
parser.add_option("-b", "--binary-values", dest="binary_values", help="Include binary instruction values as comments.", action="store_true")
parser.add_option("-l", "--no-labels", dest="no_labels", help="Don't include offset labels.", action="store_true")
parser.add_option("-d", "--decimal-immediates", dest="decimal_immediates", help="Show immediate values as decimal rather than hex.", action="store_true")

parser.add_option("-D", "--dmem-file", dest="dmem_file", help="Include content of dmem in the disassembly as .data section. ", metavar="DMEM.HEX", default=None)

#parser.add_option("-f", "--format", dest="format", help="Set the input file format.", metavar="FMT", type="choice", choices=['hex','raw','mif'])
#parser.add_option("-n", "--number", dest="number", help="Quantity of things", metavar="NUM", type="int")
#parser.add_option("-h", "--host", dest="hostname", help="Hostname. Default: %default", metavar="HOST", default="localhost")
#parser.add_option("-s", "--sort", dest="sort", help="Sort by the given key.  One of: length,name.", metavar="KEY", type="choice", choices=['length','name'])
#parser.add_option("-v", "--verbose", dest="verbose", help="Print extra info.", action="store_true")
 
(options, args) = parser.parse_args()
 
if (len(args)<=0):
        parser.print_help()
        sys.exit(0)

f = open(args[0],"r")
addr = 0
last_data = -1
ignoring_zeroes=False
print ".text"
for line in f:
    line=line.strip()
    #v = int(line,16)
    m = re.match(r':([0-9a-f]{2})([0-9a-f]{4})([0-9a-f]{2})([0-9a-f]*)([0-9a-f]{2})$',line,flags=re.IGNORECASE)
    if not m:
        print "Unable to parse '%s', ignoring." % line.strip()
        continue
    (length,addr,rectype,data,checksum) = (int('0'+x,16) for x in m.groups())
    if rectype==0: # data
        if length != INSTR_BITS/8:
            raise ValueError("This disassembler requires the HEX file to have one record per %d-bit instruction; can't parse line '%s'." % (INSTR_BITS,line))
        if addr != addr:
            raise ValueError("This HEX file appears to have out-of-order records, which is legal, but not supported by this program. Expected address 0x%x, got 0x%x with line '%s'." % (addr,addr,line))
        if data==last_data and data==0:
            if not ignoring_zeroes:
                print "# More instructions with value %08x omitted..." % (0)
                ignoring_zeroes = True
        else:
            instr = Instruction.from_instr_val(data)
            r = ""
            if not options.no_labels: r += "L%0*x: " % (INSTR_BITS/4, addr)
            r += instr.disasm(
                hex_immediates=not options.decimal_immediates,
                show_hex_value_comment=not options.no_hex_values, 
                show_binary_value_comment=options.binary_values
            )
            print r
    elif rectype==1: # eof
        break
    else: # segment/linear address
        raise ValueError("This disassembler only allows basic HEX records; can't parse line '%s' with record type %d" % (line,rectype))
    addr += 1
    last_data = data

#yeah im a bad person for copy pasting this instead of factoring it into a function, but w/e
if options.dmem_file:
    f = open(options.dmem_file,"r")
    addr = 0
    last_data = -1
    ignoring_zeroes=False
    print ".data"
    for line in f:
        line=line.strip()
        #v = int(line,16)
        m = re.match(r':([0-9a-f]{2})([0-9a-f]{4})([0-9a-f]{2})([0-9a-f]*)([0-9a-f]{2})$',line,flags=re.IGNORECASE)
        if not m:
            print "Unable to parse '%s', ignoring." % line.strip()
            continue
        (length,addr,rectype,data,checksum) = (int('0'+x,16) for x in m.groups())
        if rectype==0: # data
            if length != INSTR_BITS/8:
                raise ValueError("This disassembler requires the HEX file to have one record per %d-bit instruction; can't parse line '%s'." % (INSTR_BITS,line))
            if addr != addr:
                raise ValueError("This HEX file appears to have out-of-order records, which is legal, but not supported by this program. Expected address 0x%x, got 0x%x with line '%s'." % (addr,addr,line))
            if data==last_data and data==0:
                if not ignoring_zeroes:
                    print "# More words with value %08x omitted..." % (0)
                    ignoring_zeroes = True
            else:
                r = ""
                if not options.no_labels: r += "D%0*x: " % (INSTR_BITS/4, addr)
                r += ".word %d" % data
                print r
        elif rectype==1: # eof
            break
        else: # segment/linear address
            raise ValueError("This disassembler only allows basic HEX records; can't parse line '%s' with record type %d" % (line,rectype))
        addr += 1
        last_data = data
