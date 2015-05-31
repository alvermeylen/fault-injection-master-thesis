# coding=utf-8
import gdb
import xml.etree.ElementTree as ET

class MakeJump (gdb.Command):
     
    def __init__ (self):
        super (MakeJump, self).__init__ ("MakeJump", gdb.COMMAND_USER)
     
    def invoke (self, arg, from_tty):
        # arg should be the error type (string)
        args = arg.split(" ")
        arrival = args[0]
        if(len(args) > 1) :
            gdb.execute('next')
        gdb.execute('set $bphit = $bphit + 1')
        gdb.execute('jump ' + arrival )        
        
        gdb.execute('disable $bpnum')
        gdb.execute('continue')        
     
MakeJump()
