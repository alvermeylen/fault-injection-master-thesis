# coding=utf-8
import gdb

def break_handler(breakpoint) :
    
    if breakpoint.breakpoint.type == gdb.BP_HARDWARE_WATCHPOINT :
        expr = breakpoint.breakpoint.expression
        print("The watched variable's value has been modified !")
        gdb.execute("continue")
    
    else :
        print(str(breakpoint.breakpoint.type))
        print("Not a watchpoint")
        gdb.execute("continue")
    
        
gdb.events.stop.connect(break_handler)
