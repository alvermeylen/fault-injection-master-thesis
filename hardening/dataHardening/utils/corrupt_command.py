# coding=utf-8
import gdb
import xml.etree.ElementTree as ET

class Corrupt (gdb.Command):
     
    def __init__ (self):
        super (Corrupt, self).__init__ ("corrupt", gdb.COMMAND_USER)
     
    def invoke (self, arg, from_tty):
        args = arg.split(" ")
        var = args[0]
        nbrBits = args[1]
        bits = ""
        for i in range(2, 2+int(nbrBits)) :
            bits += args[i]
            bits += " "
            
        disable = False
        if(len(args) > 3 + int(nbrBits)) :
            gdb.execute('next')
            disable = True
        elif(len(args) > 2 + int(nbrBits)) :
            if args[len(args)-1] == "next" :
                gdb.execute('next')
            elif args[len(args)-1] == "disable" :
                disable = True
                
        gdb.execute('set variable ' + var + ' = $corrupt(' + var + ', ' + bits[:-1] + ',' + nbrBits + ')' )
        
        gdb.execute('set $bphit = $bphit + 1')
        
        if disable :
            gdb.execute('disable $bpnum')
        
        gdb.execute('continue')
        
     
Corrupt()
