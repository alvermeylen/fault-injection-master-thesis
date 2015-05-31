import os
from pycparser import c_ast
import random
import json

###############
#### UTILS ####
###############

def makeJump(start, arrival, fileName) :
    string = "break " + str(fileName) + ':' + str(start) + "\n"
    string += "\t" + "commands \n"
    string += "\t" + "\t" + "MakeJump " + str(fileName) + ':' + str(arrival) + " next" "\n"
    string += "\t" + "end"
    
    return string


def conditionToString(condition) :
    if type(condition) is c_ast.BinaryOp :
        string = ""
        
        if type(condition.left) is c_ast.ID : 
            string += condition.left.name
        elif type(condition.left) is c_ast.Constant :
            string += condition.left.value
        else :
            return "error"
    
        string += condition.op
        
        if type(condition.right) is c_ast.ID : 
            string += condition.right.name
        elif type(condition.right) is c_ast.Constant :
            string += condition.right.value
        else :
            return "error"
    
        return string
        
    elif type(condition) is c_ast.Constant : #if(true) or if(false)
        return condition.left.value
    
    else :
        return "error"


def initScript(script, scriptName, fun, cunit=False) :
    script.write("source " + os.path.join(os.getcwd(), "controlFlowHardening", "utils", "MakeJump.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(), "utils", "xml_init.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(), "utils", "signal_listener.py") + "\n")
    if not cunit :
        script.write("source " + os.path.join(os.getcwd(), "utils", "exit_listener.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(), "utils", "bp_listener.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"utils", "write_result.py") + "\n\n")
    
    script.write("set detach-on-fork off\n")
    script.write("set follow-fork-mode child\n\n")
    
    script.write("set $xml = \"" + scriptName + ".xml\"\n")
    script.write("set $fun = \"" + fun + "\"\n")
    script.write("set $bphit = 0 \n")
    script.write("set $testresult = 0 \n\n")
    
    '''
    if args.watch :
        script.write("source " + os.path.join(os.getcwd(),"dataHardening","utils","watch_variable.py")+"\n\n")
        script.write("rbreak main \n")
        script.write("\t" + "commands \n")
        script.write("\t" + "\t" + "watch " + args.watch + "\n")
        script.write("\t" + "\t" + "continue \n")
        script.write("\t" + "end \n")
    else :
        script.write("\n")
    '''
    script.write("\n")
        
        
        
def closeScript(script, cunit=False) :
    
    if cunit :
        script.write("\n")
        script.write("rbreak fi_init\n")
        script.write("\t" + "commands\n")
        script.write("\t" + "\t" + "enable\n")
        script.write("\t" + "\t" + "set $testresult = test_result\n")
        script.write("\t" + "\t" + "if ($testresult != 0 && $bphit > 0) \n")
        script.write("\t" + "\t" + "\t" + "WriteResult \"FI detected\"\n")
        script.write("\t" + "\t" + "else\n")
        script.write("\t" + "\t" + "\t" + "if ($bphit == 0)\n")
        script.write("\t" + "\t" + "\t" + "\t" + "WriteResult \"No injection\"\n")
        script.write("\t" + "\t" + "\t" + "else\n")
        script.write("\t" + "\t" + "\t" + "\t" + "WriteResult \"Failed\"\n")
        script.write("\t" + "\t" + "\t" + "end\n")
        script.write("\t" + "\t" + "end\n")
        script.write("\t" + "\t" + "set $bphit = 0\n")
        script.write("\t" + "\t" + "continue\n")
        script.write("\t" + "end\n\n")
        script.write("rbreak catch_alarm\n")
        script.write("\t" + "commands\n")
        script.write("\t" + "\t" + "WriteResult \"TIMEOUT (killed)\"\n")
        script.write("\t" + "\t" + "set $bphit = 0\n")
        script.write("\t" + "\t" + "set variable yacca_error = 0\n")
        script.write("\t" + "\t" + "continue\n")
        script.write("\t" + "end\n")
    
    script.write("\n")
    script.write("run")
    script.close()



#############################
#### Control Flow Errors ####
#############################
        

#CFE type 1 -- Illegal branches
def generateCFE1TestScript(bb0, bb1, funDir) :
    if  bb0 == bb1 or bb1 in bb0.children :
        return
    
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    CFE1Directory = os.path.join(funDir, 'CFE', 'CFE1')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    scriptName = os.path.join(CFE1Directory, "CFE1_"+str(bb0.bid)+"-to-"+str(bb1.bid))
    script = open(scriptName, 'w')
    initScript(script, scriptName, funName, cunit)
    script.write("XMLInit Control FLow Error -- type 1\n\n")
    #Jump from the end of bb0 to the first statement of bb1
    script.write(makeJump(bb0.coordEnd.line, bb1.coordBegin.line, bb0.coordEnd.file))
    closeScript(script, cunit)
    
    CFE1Script = open(os.path.join(CFE1Directory, 'run_CFE1_tests.py'), 'a')
    CFE1Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
    CFE1Script.close()
    
#CFE type 2 -- Wrong branches
def generateCFE2TestScript(bb, funDir) :
    if len(bb.children) < 2 :
        return
    
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    CFE2Directory = os.path.join(funDir, 'CFE', 'CFE2')
    CFE2Script = open(os.path.join(CFE2Directory, 'run_CFE2_tests.py'), 'a')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    #extract the condtion so it can be written into the script in order to make a conditionnal breakpoint
    # return "error" id no condition could have been extracted
    conditionString = conditionToString(bb.condition)
    #Improvement : loops -- break after a random number of iterations
    #Imrpovement : better way to handle the switch
    if conditionString is not "error" and len(bb.children) == 2 :
        scriptName = os.path.join(CFE2Directory, "CFE2_"+str(bb.bid))
        script = open(scriptName, 'w')
        initScript(script, scriptName, funName, cunit)
        script.write("XMLInit Control FLow Error -- type 2\n\n")
        script.write("break " + str(bb.coordEnd.file) + ':' + str(bb.coordEnd.line) + "\n")
        script.write("\t" + "commands \n")
        #conditional breakpoint
        script.write("\t" + "\t" + "if("+conditionString+") \n")
        script.write("\t" + "\t" + "\t"  + "MakeJump " + str(bb.coordEnd.file) + ':' +
                    str(max(bb.children).coordBegin.line) + " next \n")
        script.write("\t" + "\t" + "else \n")
        script.write("\t" + "\t" + "\t"  + "MakeJump " + str(bb.coordEnd.file) + ':' +  
                    str(min(bb.children).coordBegin.line) + " next \n")
        script.write("\t" + "\t" + "end \n")
        script.write("\t" + "\t" + "disable $bpnum\n")
        script.write("\t" + "end \n")
        closeScript(script, cunit)
        
        CFE2Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
        
    else :
        #in the case no condition could have been "extracted"
        #we jump to every children, even the "legal" one
        #The tester need to analyze the results to discard the false negative
        for child in bb.children :
            scriptName = os.path.join(CFE2Directory, "CFE2_"+str(bb.bid)+"-to-"+str(child.bid))
            script = open(scriptName, 'w')
            initScript(script, scriptName, funName, cunit)
            script.write("XMLInit Control FLow Error -- type 2\n\n")
            script.write(makeJump(bb.coordEnd.line, child.coordBegin.line, child.coordEnd.file))
            closeScript(script, cunit)
            
            CFE2Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
    
    CFE2Script.close()
    
#CFE type 3 -- from end of bb0 to body of bb1 
def generateCFE3TestScript(bb0, bb1, percLines, funDir) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    CFE3Directory = os.path.join(funDir, 'CFE', 'CFE3')
    CFE3Script = open(os.path.join(CFE3Directory, 'run_CFE3_tests.py'), 'a')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    l = range(bb1.coordBegin.line, bb1.coordEnd.line+1)
    r = random.sample(l, round(len(l)*percLines))
    for i in r :
        scriptName = os.path.join(CFE3Directory, "CFE3_"+str(bb0.bid)+"-to-"+str(bb1.bid)+'_'+str(i))
        script = open(scriptName, 'w')
        initScript(script, scriptName, funName, cunit)
        script.write("XMLInit Control FLow Error -- type 3\n\n")
        script.write(makeJump(bb0.coordEnd.line, i, bb0.coordEnd.file))
        closeScript(script, cunit)
    
        CFE3Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
    
    CFE3Script.close()
    
#CFE type 4 -- from body of bb0 to body of bb1 
def generateCFE4TestScript(bb0, bb1, percLines, funDir) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    CFE4Directory = os.path.join(funDir, 'CFE', 'CFE4')
    CFE4Script = open(os.path.join(CFE4Directory, 'run_CFE4_tests.py'), 'a')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    l0 = range(bb0.coordBegin.line, bb0.coordEnd.line+1)
    l1 = range(bb1.coordBegin.line, bb1.coordEnd.line+1)
    r0 = random.sample(l0, round(len(l0)*percLines))
    r1 = random.sample(l1, round(len(l1)*percLines))
    
    for i in  r0 :
      for j in r1 :
        if bb1 in bb0.children and i == bb0.coordEnd.line and j == bb1.coordBegin.line :
            break
        scriptName = os.path.join(CFE4Directory, "CFE4_"+str(bb0.bid)+'_'+str(i)+"-to-"+str(bb1.bid)+'_'+str(j))
        script = open(scriptName, 'w')
        initScript(script, scriptName, funName, cunit)
        script.write("XMLInit Control FLow Error -- type 4\n\n")
        script.write(makeJump(i, j, bb1.coordEnd.file))
        closeScript(script, cunit)
    
        CFE4Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
    
    CFE4Script.close()
    
    
#CFE type 5 -- from body of bb0 to body of bb0 
def generateCFE5TestScript(bb0, percLines, funDir) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    CFE5Directory = os.path.join(funDir, 'CFE', 'CFE5')
    CFE5Script = open(os.path.join(CFE5Directory, 'run_CFE5_tests.py'), 'a')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    l = range(bb0.coordBegin.line, bb0.coordEnd.line+1)
    r0 = random.sample(l, round(len(l)*percLines))
    r1 = random.sample(l, round(len(l)*percLines))
    
    for i in r0 :
      for j in r1 :
        if j == i+1 :
            break
        scriptName = os.path.join(CFE5Directory, "CFE5_"+str(bb0.bid)+'_'+str(i)+"-to-"+str(bb0.bid)+'_'+str(j))
        script = open(scriptName, 'w')
        initScript(script, scriptName, funName, cunit)
        script.write("XMLInit Control FLow Error -- type 5\n\n")
        script.write(makeJump(i, j, bb0.coordEnd.file))
        closeScript(script, cunit)
    
        CFE5Script.write("os.system(\"gdb program --batch -x " + scriptName + "\") \n")
    
    CFE5Script.close()
