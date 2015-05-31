# coding=utf-8
from pycparser import c_ast , parse_file #parse_file is used for test purpose
from operator import attrgetter
import sys
from . import cfg


## ast is of type FileAST

### Creates the CFG from the AST ###
def buildCFG(ast):
    funCFGs = []
    for e in ast.ext :
        if type(e) is c_ast.FuncDef : #we check that we reached a function declaration
            funCFGs.append(buildFunctionCFG(e))
    return funCFGs
    
def buildFunctionCFG(fun):
    cfgraph = cfg.CFG()
    
    blocksList = buildBasicBlocs(fun.body.block_items)
        
    cfgraph.addBlocks(blocksList)
    return cfgraph

def buildBasicBlocs(statements, bid=0, parents=[]):
    if statements is None :
        return []
    
    bbid = bid
    blist = []
    inBB = False
    current = None
    
    statements = statements.block_items if type(statements) is c_ast.Compound else statements
    statements = [statements] if type(statements) is not list  else statements
    for stmt in statements :           
        if not inBB :
            current = cfg.BasicBlock(bbid, stmt.coord, parents)
            bbid += 1
            inBB = True
            parents = []
        
        ##########
        ### IF ###
        ########## 
        if type(stmt) is c_ast.If :
            current.setCondition(stmt.cond)
            current.addStatement(stmt)
            #This block becomes a conditional block
            #current = cfg.ConditionnalBasicBloc(current, stmt.cond)
            #We can be sure that the current bloc is finished
            blist.append(current)

            tmpList = buildBasicBlocs(stmt.iftrue, bbid, [current])
            bbid += len(tmpList)
            tmpList0 = buildBasicBlocs(stmt.iffalse, bbid, [current])
            bbid += len(tmpList0)
            tmpList += tmpList0
            #We need to make sure inBB is set to false because 'if' is a JUMP instruction
            inBB = False
            #There could be more than one parent for the next node. To find whose, we just have to find wich basic blocks does not have any child. Then, we know that these are the parents of the future node. One exception is the return statements that can never have children.
            for elem in tmpList :
                if type(elem.getLastStatement()) is not c_ast.Return and len(elem.children) == 0: 
                    parents.append(elem)
            
            if stmt.iffalse is None :
                parents.append(current)
            blist += tmpList
            
        elif type(stmt) is c_ast.Return :
            current.addStatement(stmt)
            #We need to make sure inBB is set to false because 'return' is a JUMP instruction
            inBB = False
            blist.append(current)
            parents = []
        
        ############
        ### LOOP ###
        ############       
        elif type(stmt) is c_ast.While or type(stmt) is c_ast.For:
            current.setCondition(stmt.cond)
            current.addStatement(stmt)
            blist.append(current)
            #Old see conditon with compound : tmpList = buildBasicBlocs(stmt.stmt.block_items, bbid, [current])
            tmpList = buildBasicBlocs(stmt.stmt, bbid, [current])
            bbid += len(tmpList)
            inBB = False
            tmpList = sorted(tmpList, key=attrgetter('coordBegin.line'))
            #There could be more than one parent for the next node. To find whose, we just have to find wich basic blocks does not have any child. Then, we know that these are the parents of the future node. One exception is the return statements that can never have children.
            for elem in tmpList :
                if type(elem.getLastStatement()) is not c_ast.Return and len(elem.children) == 0: 
                    if  type(elem.getLastStatement()) is not c_ast.Continue :
                        parents.append(elem)
                    if type(elem.getLastStatement()) is not c_ast.Break:
                        elem.addChild(tmpList[0]) #because we loop
            parents.append(current) #If loop condition is not satisfied, the loop body will never be entered
            blist += tmpList
        
        
        ########################
        ### BREAK & CONTINUE ###
        ########################   
        elif type(stmt) is c_ast.Break or type(stmt) is c_ast.Continue :
            current.addStatement(stmt)
            blist.append(current)

            inBB = False
            
        ##############
        ### SWITCH ###
        ##############
        elif type(stmt) is c_ast.Switch :
            current.addStatement(stmt)
            blist.append(current)

            inBB = False
            
            tmpList = buildBasicBlocs(stmt.stmt, bbid) #parenting handled in the for loop
            bbid += len(tmpList)
            
            defaultParents = []
            beforeDefault = True
            for elem in tmpList :
                if type(elem.getFirstStatement()) is c_ast.Default or type(elem.getFirstStatement()) is c_ast.Case :
                    current.addChild(elem)
                if type(elem.getFirstStatement()) is c_ast.Default :
                    beforeDefault = False
                    for parent in defaultParents :
                        parent.addChild(elem)
                if type(elem.getLastStatement()) is not c_ast.Return and len(elem.children) == 0:
                    if beforeDefault and type(elem.getLastStatement()) is not c_ast.Break :
                        defaultParents.append(elem)
                    else : 
                        #We suppose thant a case that does not end with a break is not linked with other 'case'. So we jump the switch !
                        parents.append(elem)
            if beforeDefault :
                parents.append(current) #If switch condition is not satisfied by any case and there is no 'default', the switch body will never be entered
            blist += tmpList
            
        ######################
        ### CASE & DEFAULT ###
        ######################
        #TODO whe should merge the case statement with the first of its statements !
        elif type(stmt) is c_ast.Case or type(stmt) is c_ast.Default: 
            #TODO condition ?
            '''
            current.addStatement(stmt)
            #We consider that the 'case' represents a whole bb different of its content
            blist.append(current)
            inBB = False

            tmpList = buildBasicBlocs(stmt.stmts, bbid, [current])
            bbid += len(tmpList)
            blist += tmpList;
            '''
            
            current.addStatement(stmt)
            inBB = False
            
            bbid -= 1

            tmpList = buildBasicBlocs(stmt.stmts, bbid) 
            bbid += len(tmpList)
            current.merge(tmpList[0])
            blist.append(current)
            for i in range(1,len(tmpList)) :
                blist.append(tmpList[i])
            
        elif type(stmt) is c_ast.DoWhile : #Nobody uses that...
            current.addStatement(stmt)
            blist.append(current)
            inBB = False
            
            tmpList = buildBasicBlocs(stmt.stmt, bbid, [current]) 
            bbid += len(tmpList)
            tmpList = sorted(tmpList, key=attrgetter('coordBegin.line'))    
            
            for elem in tmpList :
                if type(elem.getLastStatement()) is not c_ast.Return and len(elem.children) == 0: 
                    parents.append(elem)
                    elem.addChild(tmpList[0]) #because we loop
                    elem.setCondition(stmt.cond)
            
            blist += tmpList
            
            
        else :
            current.addStatement(stmt)
        #TODO 
        '''
        - goto        => Not handled by the hardener ?
        - TernaryOp ? => I think we don't care.
                         Just handle that as a assignement in the FI. 
        '''
        
    if inBB and current is not None:
        blist.append(current)
    return blist;
    

     
## TEST CODE ##
'''
filename = sys.argv[1]


ast = parse_file(filename, use_cpp=True,
            cpp_path='gcc',
            cpp_args=['-E', r'-I../utils/fake_libc_include'])

            
testList = buildCFG(ast)

print(testList[0])
testList[0].createDotFile()
'''

