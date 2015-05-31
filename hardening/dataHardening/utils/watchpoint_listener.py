# coding=utf-8
import gdb

def break_handler(breakpoint) :
    if breakpoint.breakpoint.type == gdb.BP_HARDWARE_WATCHPOINT :
        expr = breakpoint.breakpoint.expression
        gdb.execute("next")
        print("OLD VALUE :")
        gdb.execute("p " + expr)
        gdb.execute("set " + expr + " = $corrupt("+ expr + ")")
        print("NEW VALUE :")
        gdb.execute("p " + expr)
        gdb.execute("continue")
    '''
    else :
        print("ERROR : wrong watchpoint type")
        gdb.execute("continue")
    '''
        
gdb.events.stop.connect(break_handler)
