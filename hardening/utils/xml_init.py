# coding=utf-8
import gdb

class XMLInit (gdb.Command):
     
    def __init__ (self):
        super (XMLInit, self).__init__ ("XMLInit", gdb.COMMAND_USER)
     
    def invoke (self, arg, from_tty):
        # arg should be the error type (string)
        filename = gdb.parse_and_eval("$xml").string()
        xmlfile = open(filename, 'w')
        
        xmlfile.write('<test>\n')
        
        xmlfile.write('\t<errorType>')
        xmlfile.write(arg)
        xmlfile.write('</errorType>\n')
        
        xmlfile.write('\t<breakpointHit>0</breakpointHit>\n')
        
        xmlfile.write('\t<returnCode></returnCode>\n')
        
        xmlfile.write('\t<FIResult></FIResult>\n')
        
        xmlfile.write('</test>\n')
    
        
     
XMLInit()
