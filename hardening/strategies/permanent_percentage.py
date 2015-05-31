import sys
import random

sys.path.append('..')
from dataHardening.tests_dataHardening import generatePermanentDataStorageTestScript    
from dataHardening.tests_dataHardening import generatePermanentDataProcessingTestScript    

def executeStrategy(stmtsDico, cfg, funDir, percVar) :
    names = stmtsDico['left']["variablesNames"]
    leftVars = random.sample(names, round(percVar*len(names)))
    names = stmtsDico['op']["operators"]
    opVars = random.sample(names, round(percVar*len(names)))
    
    opDico = generateOpDico()
    
    for var in leftVars :
        stmts = stmtsDico['left'][var]
        generatePermanentDataStorageTestScript(stmts, funDir, -1, var, True)
        
    for op in opVars :
        stmts = stmtsDico['op'][op]
        if stmts != [] :
            generatePermanentDataProcessingTestScript(stmts, funDir, -1, opDico[op], True)
        

def generateOpDico() :
    opDico = {}
    opDico['+'] = 'plus'
    opDico['-'] = 'minus'
    opDico['*'] = 'times'
    opDico['/'] = 'divide'
    opDico['%'] = 'modulo'
    opDico['&'] = 'bitwiseAND'
    opDico['&&'] = 'logicalAND'
    opDico['|'] = 'bitwiseOR'
    opDico['||'] = 'logicalOR'
    opDico['!'] = 'logicalNOT'
    opDico['~'] = 'bitwiseNOT'
    opDico['^'] = 'XOR'
    opDico['<<'] = 'leftShift'
    opDico['>>'] = 'rightShift'
    opDico['>'] = 'lt'
    opDico['<'] = 'gt'
    opDico['<='] = 'le'
    opDico['>='] = 'ge'
    opDico['=='] = 'equal'
    opDico['!='] = 'different'
    return opDico
