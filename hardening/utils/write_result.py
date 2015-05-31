# coding=utf-8
import gdb

class WriteResult (gdb.Command):
     
    def __init__ (self):
        super (WriteResult, self).__init__ ("WriteResult", gdb.COMMAND_USER)
     
    def invoke (self, arg, from_tty):
        #arg should be the test result
        fun = gdb.parse_and_eval("$fun").string()
        xmlResultFile = os.path.abspath(os.path.join(os.getcwd(), fun, 'results.xml'))
        tree = ET.parse(xmlResultFile)
        root = tree.getroot()
        xml = gdb.parse_and_eval("$xml").string()[:-4]
        split = xml.split(os.sep)
        parent = root.find(split[len(split)-1])
        if parent is None :
            parent = ET.Element(split[len(split)-1])
            root.append(parent)
        
        test_elem = ET.Element("test")
        bphit_elem = ET.Element("breakpointHit")
        bphit_elem.text =  str(int(gdb.parse_and_eval("$bphit")))
        returnCode_elem = ET.Element("returnCode")
        returnCode_elem.text = str(int(gdb.parse_and_eval("$testresult")))
        FIResult_elem = ET.Element("FIResult")
        FIResult_elem.text = arg[1:-1]
        
        test_elem.append(bphit_elem)
        test_elem.append(returnCode_elem)
        test_elem.append(FIResult_elem)
        parent.append(test_elem)
        
        with open(xmlResultFile, "w") as treeFile:
            tree.write(treeFile)
            
        #write in the xml file coresponding to the test
        xmlFile = gdb.parse_and_eval("$xml").string() 
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        retCode = root.find('returnCode') 
        retCode.text = str(int(gdb.parse_and_eval("$testresult")))
        fiRes = root.find('FIResult')
        fiRes.text = arg[1:-1]
        with open(xmlFile, "w") as treeFile:
            tree.write(treeFile)
        
     
WriteResult()
