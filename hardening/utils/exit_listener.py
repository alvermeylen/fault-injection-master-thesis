# coding=utf-8
import gdb
import os
import xml.etree.ElementTree as ET


def exit_handler(exit_event) :
    if hasattr(exit_event, 'exit_code'):
        bphit = int(gdb.parse_and_eval("$bphit"))
        returnCode = int(exit_event.exit_code)
        gdb.execute("set $testresult = " + str(returnCode))
        
        if bphit > 0 and returnCode != 0 :
            gdb.execute("WriteResult \"FI detected\"")
        elif bphit == 0 :
            gdb.execute("WriteResult \"No injection\"")
        else :
            gdb.execute("WriteResult \"Failed\"")
        
        
gdb.events.exited.connect(exit_handler)
