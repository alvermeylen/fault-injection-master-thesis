import argparse
import strategies
import json
import sys
import os
import shutil
from pycparser import c_ast , parse_file
import time

sys.path.append('..')
from controlFlowGraph.ControlFlow import buildFunctionCFG
from dataHardening.tests_dataHardening import getStatementsDictionnary  
from cunit.transform_cunit import generateHardenedCunitTests
       
    
#################
## Directories ##            
#################

def createFunDirsAndScripts(funName) :
    funDir = os.path.join(rootDirectory, funName)
    transientDataStorageDir = os.path.join(funDir, 'transientFIScripts', 'dataStorage')
    transientDataProcessingDir = os.path.join(funDir, 'transientFIScripts', 'dataProcessing')
    permanentDataStorageDir = os.path.join(funDir, 'permanentFIScripts', 'dataStorage')
    permanentDataProcessingDir = os.path.join(funDir, 'permanentFIScripts', 'dataProcessing')
    CFE1Dir = os.path.join(funDir, 'CFE', 'CFE1')
    CFE2Dir = os.path.join(funDir, 'CFE', 'CFE2')
    CFE3Dir = os.path.join(funDir, 'CFE', 'CFE3')
    CFE4Dir = os.path.join(funDir, 'CFE', 'CFE4')
    CFE5Dir = os.path.join(funDir, 'CFE', 'CFE5')
     
    ### function directory ###
    if not os.path.exists(funDir) :
        os.makedirs(funDir)
        
    scriptName = os.path.join(funDir, "run_tests.py")
    mainScript = open(scriptName, "a")
    mainScript.write("import os\n")
    mainScript.write("import sys\n\n")
    mainScript.write("if len(sys.argv) > 1 :\n")
    mainScript.write("\t" + "timeout = sys.argv[1]\n")
    mainScript.write("else :\n")
    mainScript.write("\t" + "timeout = 3\n\n")
    mainScript.write("xmlFile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results.xml'), 'w')\n")
    mainScript.write("xmlFile.write('<" + funName + ">\\n</" + funName + ">')\n")
    mainScript.write("xmlFile.close()\n\n")        
    mainScript.write("print(\"Tests on data flow\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(transientDataStorageDir, 
                     "run_transient_data_storage_tests.py") + " \" + str(timeout)) \n")
    mainScript.write("os.system(\"python "+ os.path.join(transientDataProcessingDir, 
                     "run_transient_data_processing_tests.py") + " \" + str(timeout)) \n")
    mainScript.write("os.system(\"python "+ os.path.join(permanentDataStorageDir, 
                     "run_permanent_data_storage_tests.py") + " \" + str(timeout)) \n")
    mainScript.write("os.system(\"python "+ os.path.join(permanentDataProcessingDir, 
                     "run_permanent_data_processing_tests.py") + " \" + str(timeout)) \n")
                     
    mainScript.write("print(\"Tests on control flow\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(CFE1Dir, 
                     "run_CFE1_tests.py") + "\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(CFE2Dir, 
                     "run_CFE2_tests.py") + "\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(CFE3Dir, 
                     "run_CFE3_tests.py") + "\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(CFE4Dir, 
                     "run_CFE4_tests.py") + "\") \n")
    mainScript.write("os.system(\"python "+ os.path.join(CFE5Dir, 
                     "run_CFE5_tests.py") + "\") \n")
    mainScript.close()
        
    
    ### Transient data storage ###
    
    if not os.path.exists(transientDataStorageDir) :
        os.makedirs(transientDataStorageDir)
    
    scriptName = os.path.join(transientDataStorageDir,  "run_transient_data_storage_tests.py")
    transientDataStorageScript = open(scriptName, 'w')
    transientDataStorageScript.write("import os\n")
    transientDataStorageScript.write("import sys\n\n")
    transientDataStorageScript.write("if len(sys.argv) > 1 :\n")
    transientDataStorageScript.write("\t" + "timeout = sys.argv[1]\n")
    transientDataStorageScript.write("else :\n")
    transientDataStorageScript.write("\t" + "timeout = 3\n\n")
    transientDataStorageScript.write("print(\"transient data storage -- tests\") \n")
    transientDataStorageScript.close()
    
    ### Transient data processing ###    
        
    if not os.path.exists(transientDataProcessingDir) :
        os.makedirs(transientDataProcessingDir)
        
    scriptName = os.path.join(transientDataProcessingDir, "run_transient_data_processing_tests.py")
    transientDataProcessingScript = open(scriptName, 'w')
    transientDataProcessingScript.write("import os\n")
    transientDataProcessingScript.write("import sys\n\n")
    transientDataProcessingScript.write("if len(sys.argv) > 1 :\n")
    transientDataProcessingScript.write("\t" + "timeout = sys.argv[1]\n")
    transientDataProcessingScript.write("else :\n")
    transientDataProcessingScript.write("\t" + "timeout = 3\n\n")
    transientDataProcessingScript.write("print(\"transient data processing -- tests\") \n")
    transientDataProcessingScript.close()
        
    ### Permanent data storage ###    
    
    if not os.path.exists(permanentDataStorageDir) :
        os.makedirs(permanentDataStorageDir)
        
    scriptName = os.path.join(permanentDataStorageDir, "run_permanent_data_storage_tests.py")
    permanentDataStorageScript = open(scriptName, 'w')
    permanentDataStorageScript.write("import os\n")
    permanentDataStorageScript.write("import sys\n\n")
    permanentDataStorageScript.write("if len(sys.argv) > 1 :\n")
    permanentDataStorageScript.write("\t" + "timeout = sys.argv[1]\n")
    permanentDataStorageScript.write("else :\n")
    permanentDataStorageScript.write("\t" + "timeout = 3\n\n")
    permanentDataStorageScript.write("print(\"permanent data storage -- tests\") \n")    
    permanentDataStorageScript.close()
    
    ### Permanent data processing ###
        
    if not os.path.exists(permanentDataProcessingDir) :
        os.makedirs(permanentDataProcessingDir)
        
    scriptName = os.path.join(permanentDataProcessingDir, "run_permanent_data_processing_tests.py")
    permanentDataProcessingScript = open(scriptName, 'w')
    permanentDataProcessingScript.write("import os\n")
    permanentDataProcessingScript.write("import sys\n\n")
    permanentDataProcessingScript.write("if len(sys.argv) > 1 :\n")
    permanentDataProcessingScript.write("\t" + "timeout = sys.argv[1]\n")
    permanentDataProcessingScript.write("else :\n")
    permanentDataProcessingScript.write("\t" + "timeout = 3\n\n")
    permanentDataProcessingScript.write("print(\"permanent data processing -- tests\") \n")
    permanentDataProcessingScript.close()
    
    ### CFE 1 ###
        
    if not os.path.exists(CFE1Dir) :
        os.makedirs(CFE1Dir)
        
    CFE1Script = open(os.path.join(CFE1Dir, "run_CFE1_tests.py"), 'w')
    CFE1Script.write("import os \n \n")
    CFE1Script.write("print(\"CFE1 -- tests\") \n")        
    CFE1Script.close()
    
    ### CFE 2 ###    
        
    if not os.path.exists(CFE2Dir) :
        os.makedirs(CFE2Dir)

    CFE2Script = open(os.path.join(CFE2Dir, "run_CFE2_tests.py"), 'w')
    CFE2Script.write("import os \n \n")
    CFE2Script.write("print(\"CFE2 -- tests\")  \n")
    CFE2Script.close()
    
    ### CFE 3 ###
    
    if not os.path.exists(CFE3Dir) :
        os.makedirs(CFE3Dir)
        
    CFE3Script = open(os.path.join(CFE3Dir, "run_CFE3_tests.py"), 'w')
    CFE3Script.write("import os \n \n")
    CFE3Script.write("print(\"CFE3 -- tests\")  \n")    
    CFE3Script.close()
    
    ### CFE 4 ###    
        
    if not os.path.exists(CFE4Dir) :
        os.makedirs(CFE4Dir)
        
    CFE4Script = open(os.path.join(CFE4Dir, "run_CFE4_tests.py"), 'w')
    CFE4Script.write("import os \n \n")
    CFE4Script.write("print(\"CFE1 -- tests\")  \n")
    CFE4Script.close()
    
    ### CFE 5 ###
        
    if not os.path.exists(CFE5Dir) :
        os.makedirs(CFE5Dir)
        
    CFE5Script = open(os.path.join(CFE5Dir, "run_CFE5_tests.py"), 'w')
    CFE5Script.write("import os \n \n")
    CFE5Script.write("print(\"CFE5 -- tests\") \n")
    CFE5Script.close()

#################
#### Scripts ####
#################
    
            
def writeRunScript() :
    script = open(os.path.join(rootDirectory, "run_all_tests.py"), 'w')
    script.write("from pathlib import Path \n")
    script.write("import lxml.etree as ET\n")
    script.write("import os\n")
    script.write("import sys\n\n")
    
    script.write("if len(sys.argv) > 1 :\n")
    script.write("\t" + "timeout = sys.argv[1]\n")
    script.write("else :\n")
    script.write("\t" + "timeout = 3\n\n")
    
    script.write("directory = os.path.dirname(os.path.realpath(__file__))\n")
    script.write("os.system(\"scons -Q\") \n \n")
    
    script.write("result = open(os.path.join(directory, 'results.xml'), 'w')\n")
    script.write("result.write('<results>\\n')\n")
    
    script.write("p = Path(directory) \n")
    script.write("for folder in p.iterdir() : \n")
    script.write("\t" + "if folder.is_dir() : \n")
    script.write("\t" + "\t" + "absPath = os.path.join(directory,str(folder),\"run_tests.py\") \n")    
    script.write("\t" + "\t" + "os.system(\"python \" + absPath + \" \" + str(timeout))\n")
    
    script.write("\t" + "\t" + "with open(os.path.join(directory,str(folder), 'results.xml'), 'r') as funxml :\n")
    script.write("\t" + "\t" + "\t" + "result.write(funxml.read())\n")
    script.write("\t" + "\t" + "\t" + "result.write('\\n')\n")
    
    script.write("result.write('</results>\\n')\n")
    script.write("result.close()\n\n")
    
    xsl_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "utils", "results.xsl")
    
    script.write("resultXML = ET.parse(os.path.join(directory, 'results.xml'))\n")
    script.write("xslt = ET.parse(\"" + xsl_file + "\")\n")
    script.write("transform = ET.XSLT(xslt)\n")
    script.write("resultHTML = transform(resultXML)\n")
    script.write("with open(os.path.join(directory, 'results.html'), 'w') as html :\n")
    script.write("\t" + "html.write(str(resultHTML))\n")
    script.write("\t" + "html.close()\n")
    
    script.close() 

def writeSconsScript(files, cunit=False) :                
    cu = []
    if cunit :
        cu.append(os.path.join(rootDirectory, "cunit_tests.c"))
        cu.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "tests", "utils", "yacca", "yacca.c"))
        cu.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "tests", "utils", "dual", "dual.so"))
        cu.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "tests", "utils", "FI", "FI.c"))
    files = list(set(files)|set(cu)) #remove duplicates
    script =  open(os.path.join(rootDirectory, "SConstruct"), 'w')
    script.write("Program(\"program\", [")
    fileList = ""
    for f in files :
        if f :
            fileList += "\"" + f + "\", "
    script.write(fileList[:-2])
    if cunit :
        script.write("], CCFLAGS=\"-O0 -ggdb\", LIBS=\"cunit\" )")
    else :
        script.write("], CCFLAGS=\"-O0 -ggdb\" )")
    script.close()    
    
##########    
## MAIN ##
##########

parser = argparse.ArgumentParser(description='Generate fault injections scripts')
parser.add_argument("--strategies", "-str", type=str, nargs='+', help="strategies that will be used")
args = parser.parse_args()

if not args.strategies :
    raise Exception("No strategy given !")
    
with open('injection-strategies.properties', 'r') as jsonfile :
    properties = json.load(jsonfile)    

### FOLDER ###
if properties['folder'] != "" :
    rootDirectory  = properties['folder']
else:
    rootDirectory = os.path.join(os.environ['HOME'], "FaultInjectionTests")
    
if os.path.exists(rootDirectory) :
    shutil.rmtree(rootDirectory)
os.makedirs(rootDirectory)

## Write run script and scons ##
writeRunScript()
cfiles = properties['testsFiles'] if properties['compileFiles'][0] == "" else properties['testsFiles']+properties['compileFiles']
writeSconsScript(cfiles, properties['cunit'] != "")


funDico = {}
for f in properties['testsFiles'] :
    ast = parse_file(f, use_cpp=True, cpp_path='cpp', cpp_args=r'-I./utils/fake_libc_include')
    for element in ast.ext :
        if type(element) is c_ast.FuncDef :
            createFunDirsAndScripts(element.decl.name)
            cfg = buildFunctionCFG(element)
            params = [] if not element.decl.type.args else element.decl.type.args.params
            statementsDico = getStatementsDictionnary(element.body.block_items, cfg, False, params)
            
            if element.decl.type.args :
                funDico[element.decl.name] = element.decl.type.args.params
            else :
                funDico[element.decl.name] = []
            
            t0 = time.time()     
            for strategy in args.strategies :
                ts0 = time.time()
                argsDico = properties['strategies'][strategy]
                argsDico['stmtsDico'] = statementsDico
                argsDico['cfg'] = cfg
                argsDico['funDir'] = os.path.join(rootDirectory,element.decl.name)
                __import__('strategies.'+strategy)
                getattr(strategies, strategy).executeStrategy(**argsDico)
                ts1 = time.time()
                print("time for strategy " + strategy + " = " + str(ts1-ts0))
            t1 = time.time()
            print("total time = " + str(t1-t0))

if properties['cunit'] != "" :
    generateHardenedCunitTests(funDico, properties['cunit'], rootDirectory)
