# coding=utf-8
import gdb

def break_handler(breakpoint) :
    try :
        bpnum = breakpoint.breakpoint.number
        gdb.execute("set $bpnum = " + str(bpnum))
    except AttributeError :
        pass
        
gdb.events.stop.connect(break_handler)
