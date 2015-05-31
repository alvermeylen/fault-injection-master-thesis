# coding=utf-8
import gdb
import os
import xml.etree.ElementTree as ET

def break_handler(stop_event) :
    if type(stop_event) is gdb.SignalEvent :
        if str(stop_event.stop_signal) == "SIGSEGV" : #Segmentation fault 
            gdb.execute("WriteResult SIGSEGV")
        elif str(stop_event.stop_signal) == "SIGKILL" : #timeout
            gdb.execute("WriteResult TIMEOUT")
                
gdb.events.stop.connect(break_handler)


#TODO still used ?
def writeTestResultSignal() :
    fun = gdb.parse_and_eval("$fun").string()
    xmlResultFile = os.path.abspath(os.path.join(os.getcwd(), fun, 'results.xml'))
    tree = ET.parse(xmlResultFile)
    root = tree.getroot()
    xml = gdb.parse_and_eval("$xml").string()[:-4]
    split = xml.split(os.sep)
    newElem = ET.Element(split[len(split)-1])
    newElem.text = "Interrupted (SIGSEGV)"
    root.append(newElem) 
    with open(xmlResultFile, "w") as treeFile:
        tree.write(treeFile)
