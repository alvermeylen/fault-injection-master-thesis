import sys
import random

sys.path.append('..')
from dataHardening.tests_dataHardening import generateTransientDataStorageTestScript    
from dataHardening.tests_dataHardening import generateTransientDataProcessingTestScript    


def executeStrategy(stmtsDico, cfg, funDir, percVar, percStmts) :
    #Statements
    names = stmtsDico['right']["variablesNames"]    
    rightVars = random.sample(names, round(percVar*len(names)))
    names = stmtsDico['left']["variablesNames"]
    leftVars = random.sample(names, round(percVar*len(names)))
    names = stmtsDico['op']["operators"]
    opVars = random.sample(names, round(percVar*len(names)))
    
    #a priori
    for var in rightVars :
        stmts = stmtsDico['right'][var]
        sample = random.sample(stmts, round(len(stmts)*percStmts))
        for stmt in sample :
            generateTransientDataStorageTestScript(stmt, funDir, -1, False)
            
    #op - a priori
    for op in opVars :
        stmts = stmtsDico['op'][op]
        sample = random.sample(stmts, round(len(stmts)*percStmts))
        for stmt in sample :
            generateTransientDataProcessingTestScript(stmt, funDir, -1)
            
    #a posteriori
    for var in leftVars :
        stmts = stmtsDico['left'][var]
        sample = random.sample(stmts, round(len(stmts)*percStmts))
        for stmt in sample :
            generateTransientDataStorageTestScript(stmt, funDir, -1, False)
    
