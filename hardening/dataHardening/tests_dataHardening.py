import os
from pycparser import c_ast
import json


def getStatementsDictionnary(funBody, currentCFG, rec=False, params=[]) :
    global retainLeftStmts
    global retainRightStmts
    global retainOpStmts
    
    if not rec :
        initRetainStmts()
        for p in params :
            p.coord.line = currentCFG.getRoot().coordBegin.line
            retainLeftStmts["variablesNames"].append(p.name)
            retainLeftStmts[p.name] = [p]
            
    if funBody is None :
        return

    funBody = funBody.block_items if type(funBody) is c_ast.Compound else funBody
    funBody = [funBody] if type(funBody) is not list else funBody
    
    for stmt in funBody :
        
        if type(stmt) is c_ast.Decl :
            
            if type(stmt.type.type) is not c_ast.Struct :
    
                if type(stmt.init) is c_ast.Cast :
                    stmt.init = stmt.init.expr
                
                if type(stmt.type) is not c_ast.Struct :
                    retainLeftStmts["variablesNames"].append(stmt.name)
                               
                retainLeftStmts[stmt.name] = [stmt]
                
                if stmt.init is not None :
                    if type(stmt.init) is c_ast.InitList :
                        #a priori : les éléments dans la liste != constante
                        #a posteriori : chaque cellule du tableau
                        length = getArraySize(stmt.init.exprs)
                        for elem in getInitListID(stmt.init.exprs) :
                            try :
                                retainRightStmts[elem.name].append(elem)
                            except KeyError :
                                retainRightStmts[elem.name] = [elem]
                                retainRightStmts["variablesNames"].append(elem.name)
                        #TODO array a posteriori
                        #generateTransientDataStorageTestScriptForArray(stmt, length, True) #a posteriori
                    else :
                        if type(stmt.init) is c_ast.Cast : 
                            stmt.init = stmt.init.expr
                            
                        if type(stmt.init) is c_ast.UnaryOp :                            
                            if '++' in stmt.init.op :
                                retainOpStmts['+'].append(stmt)
                            elif '--' in stmt.init.op :
                                retainOpStmts['-'].append(stmt)
                            else :
                                retainOpStmts[op].append(stmt)
                                
                            try :
                                retainRightStmts[stmt.name].append(stmt)
                            except KeyError :
                                retainRightStmts[stmt.name] = [stmt]
                                retainRightStmts["variablesNames"].append(stmt.name)
 
                            stmt.init = stmt.init.expr
                                
                        elif type(stmt.init) is c_ast.BinaryOp :
                            #Permanent storage error only on left val because of propagation
                            dico = getOperatorsAndExprFromBinaryOp(stmt.init)
                            for elem in dico['expr'] :
                                try :
                                    retainRightStmts[elem.name].append(elem)
                                except KeyError :
                                    retainRightStmts[elem.name] = [elem]
                                    retainRightStmts["variablesNames"].append(elem.name)
                                
                            for op in dico['op'] :
                                #Note : corrupt the left value and 
                                # not the values on wich the op has actual effect
                                # OK ?
                                retainOpStmts[op].append(stmt)
                            
                        elif type(stmt.init) is c_ast.ID :
                            try :
                                retainRightStmts[stmt.init.name].append(stmt.init)
                            except KeyError :
                                retainRightStmts[stmt.init.name] = [stmt.init]
                                retainRightStmts["variablesNames"].append(stmt.init.name)

        ### Assignment ###
        elif type(stmt) is c_ast.Assignment :

            if type(stmt.rvalue) is c_ast.Cast :
                stmt.rvalue = stmt.rvalue.expr
            
            if type(stmt.lvalue) is c_ast.Cast or type(stmt.lvalue) is c_ast.UnaryOp :
                stmt.lvalue = stmt.lvalue.expr
                
            if type(stmt.lvalue) is c_ast.ArrayRef :
                stmt.lvalue.name = getArrayCellName(stmt.lvalue)
                
            if type(stmt.lvalue) is c_ast.StructRef :
                stmt.lvalue.name = getStructFieldName(stmt.lvalue)
                
            stmtLVal = stmt.lvalue
            
            if type(stmt.rvalue) is c_ast.InitList :
                #a priori : list elements != constant ; a posteriori, each cell                
                length = getArraySize(stmt.rvalue.exprs)
                for elem in getInitListID(stmt.rvalue.exprs) :
                    try :
                        retainRightStmts[elem.name].append(elem)
                    except KeyError :
                        retainRightStmts["variablesNames"].append(elem.name)
                        retainRightStmts[elem.name] = [elem]
                #TODO tableau a posteriori !
                #generateTransientDataStorageTestScriptForArray(stmt, length, True) #a posteriori
                   
            else :
                #In case where lvalue is an ArrayRef, we do the same.
                #The difference is that we had lvalue instead of the list to retainLeftStmts
                try :
                    retainLeftStmts[stmt.lvalue.name].append(stmtLVal)
                except KeyError :
                    retainLeftStmts[stmt.lvalue.name] = [stmtLVal]
                    retainLeftStmts["variablesNames"].append(stmt.lvalue.name)
                
                if type(stmt.rvalue) is c_ast.BinaryOp :
                    dico = getOperatorsAndExprFromBinaryOp(stmt.rvalue)
                    for elem in dico['expr'] :
                        try :
                            retainRightStmts[elem.name].append(elem)
                        except KeyError :
                            retainRightStmts[elem.name] = [elem]
                            retainRightStmts["variablesNames"].append(elem.name)
                    for op in dico['op'] :
                        #Note : corrupt the left value and not the values on wich the op has actual effect
                        retainOpStmts[op].append(stmtLVal)
                            
                elif type(stmt.rvalue) is c_ast.ID :
                    try :
                        retainRightStmts[stmt.rvalue.name].append(stmt.rvalue)
                    except KeyError :
                        retainRightStmts[stmt.rvalue.name] = [stmt.rvalue]
                        retainRightStmts["variablesNames"].append(stmt.rvalue.name)                
                
                elif type(stmt.rvalue) is c_ast.UnaryOp : 
                    if '++' in stmt.rvalue.op :
                        retainOpStmts['+'].append(stmtLVal)
                    elif '--' in stmt.rvalue.op :
                        retainOpStmts['-'].append(stmtLVal)
                    else :
                        retainOpStmts[stmt.rvalue.op].append(stmtLVal)
                    
                    if type(stmt.rvalue.expr) is c_ast.BinaryOp :
                        dico = getOperatorsAndExprFromBinaryOp(stmt.rvalue.expr)
                        for elem in dico['expr'] :
                            try :
                                retainRightStmts[elem.name].append(elem)
                            except KeyError :
                                retainRightStmts[elem.name] = [elem]
                                retainRightStmts["variablesNames"].append(elem.name)
                        for op in dico['op'] :
                            #Note : corrupt the left value and not the values on wich the op has actual effect
                            retainOpStmts[op].append(stmtLVal)
                        
                    elif type(stmt.rvalue.expr) is not c_ast.Constant :    
                    
                        try :
                            retainRightStmts[stmt.rvalue.expr.name].append(stmt.rvalue.expr)
                        except KeyError :
                            retainRightStmts[stmt.rvalue.expr.name] = [stmt.rvalue.expr]
                            retainRightStmts["variablesNames"].append(stmt.rvalue.expr.name)
                  
                         
                elif type(stmt.rvalue) is c_ast.ArrayRef :                        
                    try :
                        retainRightStmts[getArrayCellName(stmt.rvalue)].append(stmt.rvalue)
                    except KeyError :
                        retainRightStmts[getArrayCellName(stmt.rvalue)] = [stmt.rvalue]
                        retainRightStmts["variablesNames"].append(getArrayCellName(stmt.rvalue))

                
                if '+=' in stmt.op :
                    retainOpStmts['+'].append(stmtLVal)
                elif '-=' in stmt.op :
                    retainOpStmts['-'].append(stmtLVal)
                elif '*=' in stmt.op :
                    retainOpStmts['*'].append(stmtLVal)
                elif '/=' in stmt.op :
                    retainOpStmts['/'].append(stmtLVal)
                elif '%=' in stmt.op :
                    retainOpStmts['%'].append(stmtLVal)
                elif '&=' in stmt.op :
                    retainOpStmts['&'].append(stmtLVal)
                elif '|=' in stmt.op :
                    retainOpStmts['|'].append(stmtLVal)
                elif '^=' in stmt.op :
                    retainOpStmts['^'].append(stmtLVal)
                elif '<<=' in stmt.op :
                    retainOpStmts['<<'].append(stmtLVal)
                elif '>>' in stmt.op :
                    retainOpStmts['>>'].append(stmtLVal)

    
        ### Unary Op ###
        elif type(stmt) is c_ast.UnaryOp :
            if type(stmt.expr) is c_ast.ArrayRef :
                stmt.expr.name = getArrayCellName(stmt.expr)
            
            elif type(stmt.expr) is c_ast.StructRef :
                stmt.expr.name = getStructFieldName(stmt.expr)
                
            stmtExpr = stmt.expr
                
            try :
                retainLeftStmts[stmt.expr.name].append(stmtExpr)
            except KeyError :
                retainLeftStmts[stmt.expr.name] = [stmtExpr]
                retainLeftStmts["variablesNames"].append(stmt.expr.name)
                
            if '++' in stmt.op :
                retainOpStmts['+'].append(stmtExpr)
            elif '--' in stmt.op :
                retainOpStmts['-'].append(stmtExpr)
            else :
                retainOpStmts[stmt.op].append(stmtExpr)
       
       ### Cast ###        
        elif type(stmt) is c_ast.Cast :
             getStatementsDictionnary(stmt.expr, currentCFG, rec=True)
             
        ### Typedef ###
        elif type(stmt) is c_ast.Typedef :
            getStatementsDictionnary(stmt.type.type, currentCFG, rec=True)            
             
        ### Function Call ###
        elif type(stmt) is c_ast.FuncCall :
            for arg in getAllArgs(stmt.args.exprs) :
                if type(arg) is c_ast.UnaryOp :
                    
                    pStmt = arg.expr
                    
                    ## LEFT
                    try :    
                        retainLeftStmts[arg.expr.name].append(pStmt)
                    except KeyError :
                        retainLeftStmts[arg.expr.name] = [pStmt]
                        retainLeftStmts["variablesNames"].append(arg.expr.name)
                        
                    ## RIGHT
                    try :    
                        retainRightStmts[arg.expr.name].append(pStmt)
                    except KeyError :
                        retainRightStmts[arg.expr.name] = [pStmt]
                        retainRightStmts["variablesNames"].append(arg.expr.name)
                    
                    if '++' in arg.op :
                        retainOpStmts['+'].append(pStmt)
                    elif '--' in arg.op :
                        retainOpStmts['-'].append(pStmt)
                    else :
                        retainOpStmts[arg.op].append(pStmt)
                        
                elif type(arg) is c_ast.BinaryOp :
                    dico = getOperatorsAndExprFromBinaryOp(arg)
                    for e in dico['expr'] :
                        if arg.coord.line == 7 :
                            print(type(e))
                        ## LEFT
                        try :    
                            retainLeftStmts[e.name].append(e)
                        except KeyError :
                            retainLeftStmts[e.name] = [e]
                            retainLeftStmts["variablesNames"].append(e.name)
                        
                        ## RIGHT
                        try :    
                            retainRightStmts[e.name].append(e)
                        except KeyError :
                            retainRightStmts[e.name] = [e]
                            retainRightStmts["variablesNames"].append(e.name)
                        
                        for op in dico['op'] :
                            #Note : corrupt the left value and not the values on wich the op has actual effect
                            retainOpStmts[op].append(e)
                        
                elif type(arg) is c_ast.ID :
                    try :
                        retainLeftStmts[arg.name].append(arg)
                    except KeyError :
                        retainLeftStmts[arg.name] = [arg]
                        retainLeftStmts["variablesNames"].append(arg.name)
                        
                    try :
                        retainRightStmts[arg.name].append(arg)
                    except KeyError :
                        retainRightStmts[arg.name] = [arg]
                        retainRightStmts["variablesNames"].append(arg.name)
                            
        ### Decl List ###   
        elif type(stmt) is c_ast.DeclList :
            getStatementsDictionnary(stmt.decls, currentCFG, rec=True)
            
        ### While, DoWhile and Switch ###
        elif type(stmt) is c_ast.While or type(stmt) is c_ast.DoWhile or type(stmt) is c_ast.Switch:
            if type(stmt.cond) is c_ast.Cast or type(stmt.cond) is c_ast.UnaryOp :
                stmt.cond = stmt.cond.expr
            #if and NOT elif because of the cast or unaryop condition
            if type(stmt.cond) is c_ast.BinaryOp :
                dico = getOperatorsAndExprFromBinaryOp(stmt.cond)
                for elem in dico['expr'] :
                    try :
                        retainRightStmts[elem.name].append(elem)
                    except KeyError :
                        retainRightStmts[elem.name] = [elem]
                        retainRightStmts["variablesNames"].append(elem.name)
                #NO need for operators. CFEs simulate that.
            elif type(stmt.cond) is c_ast.ID :
                try :
                    retainRightStmts[stmt.cond.name].append(stmt.cond)
                except KeyError :
                    retainRightStmts[stmt.cond.name] = [stmt.cond]
                    retainRightStmts["variablesNames"].append(stmt.cond.name)
                    
            getStatementsDictionnary(stmt.stmt, currentCFG, rec=True) #a posteriori
    
        ### FOR ###    
        elif type(stmt) is c_ast.For :
            #TODO : a priori : init, next ?
            if type(stmt.cond) is c_ast.BinaryOp :
                dico = getOperatorsAndExprFromBinaryOp(stmt.cond)
                for elem in dico['expr'] :
                    try :
                        retainRightStmts[elem.name].append(elem)
                    except KeyError :
                        retainRightStmts[elem.name] = [elem]
                        retainRightStmts["variablesNames"].append(elem.name)
                #NO need for operators. CFEs simulate that.
        
            # a posteriori
            if stmt.init is not None :
                #init + body
                getStatementsDictionnary([stmt.init] + stmt.stmt.block_items, currentCFG, rec=True)
            else :
                # body only
                getStatementsDictionnary(stmt.stmt.block_items, currentCFG, rec=True)
            #next
            getStatementsDictionnary([stmt.next], currentCFG, rec=True)
        
        ### IF ###
        elif type(stmt) is c_ast.If :
            if type(stmt.cond) is c_ast.BinaryOp :
                dico = getOperatorsAndExprFromBinaryOp(stmt.cond)
                for elem in dico['expr'] :
                    try :
                        retainRightStmts[elem.name].append(elem)
                    except KeyError :
                        retainRightStmts[elem.name] = [elem]
                        retainRightStmts["variablesNames"].append(elem.name)

            #NO need for operators. CFEs simulate that.
            getStatementsDictionnary(stmt.iftrue, currentCFG, rec=True) #a posteriori
            getStatementsDictionnary(stmt.iffalse, currentCFG, rec=True) #a posteriori
        
        ### CASE and DEFAULT ###
        elif type(stmt) is c_ast.Case or type(stmt) is c_ast.Default : 
            getStatementsDictionnary(stmt.stmts, currentCFG, rec=True)  
    
    if not rec :    
        retDico = {}
        retDico['left'] = retainLeftStmts
        retDico['right'] = retainRightStmts
        retDico['op'] = retainOpStmts
        return retDico
    

#####################
#### CORRUPTION #####
#####################


def corruptVar(stmt, line, bits, next=False, temp=False) :
    stringBits = ""
    for bit in bits :
        stringBits += str(bit)
        stringBits += " "
        
    string = "break "
    string += str(stmt.coord.file)+":"+str(line) + "\n"
    string += "\t" + "commands"
    string += "\n"
    # ATTENTION : Could provoke an error because of "ambiguous set operation" if the variable name is small.
    #If this happens, you can change the 'set' by 'print'. The effects will be the same, but the value will be printed.
    
    if next :
        string += "\t" + "\t" + "corrupt " + stmt.name + " " + str(len(bits)) + " " + stringBits + "next"
    else :
        string += "\t" + "\t" + "corrupt " + stmt.name + " " + str(len(bits)) + " " + stringBits
    
    if temp :
        string += " disable\n"
    else :
        string += "\n"
        
    string += "\t" + "end"
    string += "\n"
    string += "\n"
    
    return string

###############
#### UTILS ####
###############
        
def initRetainStmts() :
    global retainLeftStmts
    global retainRightStmts
    global retainOpStmts
    
    retainLeftStmts = {}
    retainRightStmts = {}
    retainOpStmts = {}
    #operators
    retainOpStmts['+'] = []
    retainOpStmts['-'] = []
    retainOpStmts['*'] = []
    retainOpStmts['/'] = []
    retainOpStmts['%'] = []
    retainOpStmts['&'] = [] 
    retainOpStmts['&&'] = []
    retainOpStmts['|'] = [] 
    retainOpStmts['||'] = []
    retainOpStmts['!'] = [] 
    retainOpStmts['~'] = []
    retainOpStmts['^'] = [] 
    retainOpStmts['<<'] = [] 
    retainOpStmts['>>'] = [] 
    retainOpStmts['>'] = []
    retainOpStmts['<'] = []
    retainOpStmts['<='] = []
    retainOpStmts['>='] = []
    retainOpStmts['=='] = []
    retainOpStmts['!='] = []
    retainOpStmts['operators'] = [  '+','-','*','/','%','&','&&','|','||','!', '~', 
                                    '^', '<<', '>>', '<', '>', '<=', '>=', '==', '!=' ]
    #variables
    retainLeftStmts["variablesNames"] = []
    retainRightStmts["variablesNames"] = []
    
    retainLeftStmts["variablesArray"] = []
    retainRightStmts["variablesArray"] = []
    
def initretainRightStmts() :
    global retainRightStmts
    
    retainRightStmts = {}
    #operators
    retainRightStmts['+'] = []
    retainRightStmts['-'] = []
    retainRightStmts['*'] = []
    retainRightStmts['/'] = []
    retainRightStmts['%'] = []
    retainRightStmts['&'] = [] 
    retainRightStmts['&&'] = []
    retainRightStmts['|'] = [] 
    retainRightStmts['||'] = []
    retainRightStmts['!'] = [] 
    retainRightStmts['~'] = []
    retainRightStmts['^'] = [] 
    retainRightStmts['<<'] = [] 
    retainRightStmts['>>'] = [] 
    retainRightStmts['>'] = []
    retainRightStmts['<'] = []
    retainRightStmts['<='] = []
    retainRightStmts['>='] = []
    retainRightStmts['=='] = []
    retainRightStmts['!='] = []
    #variables
    retainRightStmts["variablesNames"] = []
    retainRightStmts["variablesArray"] = []
    
def initScript(script, scriptName, funName, cunit=False) :
    script.write("source " + os.path.join(os.getcwd(),"dataHardening", "utils", "corrupt_command.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"dataHardening", "utils", "corrupt_function.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"utils", "xml_init.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"utils", "signal_listener.py") + "\n")
    if not cunit :
        script.write("source " + os.path.join(os.getcwd(),"utils", "exit_listener.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"utils", "bp_listener.py") + "\n")
    script.write("source " + os.path.join(os.getcwd(),"utils", "write_result.py") + "\n\n")
    
    script.write("set detach-on-fork off\n")
    script.write("set follow-fork-mode child\n\n")
    
    script.write("set $xml = \"" + scriptName + ".xml\"\n")
    script.write("set $fun = \"" + funName + "\"\n")
    script.write("set $bphit = 0 \n")
    script.write("set $testresult = 0 \n\n")
    
    '''
    if args.watch :
        #include the watchpoint listener
        script.write("source " + os.path.join(os.getcwd(),"dataHardening", "utils/watch_variable.py")+"\n"+"\n")
        #Break when the main start to set the watchpoint on the variable
        script.write("rbreak main \n")
        script.write("\t" + "commands \n")
        script.write("\t" + "\t" + "watch " + args.watch + "\n")
        script.write("\t" + "\t" + "continue \n")
        script.write("\t" + "end \n \n")
    else :
        script.write("\n")
    '''
    
    script.write("\n")
    
        
def closeScript(script, cunit=False) :
    if cunit :
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
        script.write("\t" + "\t" + "\t" + "\t" + "WriteResult \"Failedi\"\n")
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
                     
def getArraySize(array, count=0) : 
    for elem in array :
        if type(elem) is c_ast.InitList :
            count = getArraySize(elem.exprs, count)
        else :
            count += 1
    return count

def getInitListID(array, rlist=[]) :
    for elem in array :
        if type(elem) is c_ast.InitList :
            rlist = getInitListID(elem, rlist)
        elif type(elem) is c_ast.ID : #could be ID, Cast, UnaryOP. Something else ?
            rlist.append(elem)
        elif type(elem) is c_ast.Cast or  type(elem) is c_ast.UnaryOp :
            rlist.append(elem.expr)
    return rlist
    

def getArrayCellName(arrayRef, name="") :
    if type(arrayRef.name) is c_ast.ArrayRef :
        if type(arrayRef.subscript) is c_ast.ID :
            name = '[' + arrayRef.subscript.name + ']' + name
        else :
            name = '[' + arrayRef.subscript.value + ']' + name
        return getArrayCellName(arrayRef.name, name)
    else :
        if type(arrayRef.subscript) is c_ast.ID :
            if type(arrayRef.name) is str :
                name = arrayRef.name + '[' + arrayRef.subscript.name + ']' + name
            else :
                name = arrayRef.name.name + '[' + arrayRef.subscript.name + ']' + name
        else :
            if type(arrayRef.name) is str :
                name = arrayRef.name.name + '[' + arrayRef.subscript.value + ']' + name
            else :
                name = arrayRef.name.name + '[' + arrayRef.subscript.value + ']' + name
        return name
    
def getArrayCellNameForScript(arrayRef, name="") :
    if type(arrayRef.name) is c_ast.ArrayRef :
        if type(arrayRef.subscript) is c_ast.ID :
            name += arrayRef.subscript.name + name
        else :
            name += arrayRef.subscript.value + name
        return getArrayCellNameForScript(arrayRef.name, name)
    else :
        if type(arrayRef.subscript) is c_ast.ID :
            if type(arrayRef.name) is str :
                name = arrayRef.name + arrayRef.subscript.name + name
            else :
                name = arrayRef.name.name + arrayRef.subscript.name + name
        else :
            if type(arrayRef.name) is str :
                name = arrayRef.name + arrayRef.subscript.value + name
            else :
                name = arrayRef.name.name + arrayRef.subscript.value + name
        return name
    
def getStructFieldName(struct, name = "") :
    if type(struct.name) is c_ast.StructRef :
        name = struct.field.name + '.' + name
        return getStructFieldName(struct.name, name)
    else :
        if not name :
            return struct.name.name + "." + struct.field.name
        else :
            return struct.name.name + "." + struct.field.name + "." + name
    
def getOperatorsAndExprFromBinaryOp(bop) :
    dico={'op' : [], 'expr' : []}
    
    while(type(bop) is c_ast.BinaryOp) :    
        if type(bop.right) is c_ast.ID :
            dico['expr'].append(bop.right)
        elif type(bop.right) is c_ast.Cast or type(bop.right) is c_ast.UnaryOp : 
            if type(bop.right.expr) is c_ast.BinaryOp :
                tmpDico = getOperatorsAndExprFromBinaryOp(bop.right.expr)
                dico['op'] += tmpDico['op']
                dico['expr'] += tmpDico['expr'] 
            else :
                tmpExpr = getExpr(bop.right.expr)
                if type(tmpExpr) is not c_ast.Constant :  
                    dico['expr'].append(tmpExpr)
            
        dico['op'].append(bop.op)
        bop = bop.left
    
    if type(bop) is c_ast.ID :
        dico['expr'].append(bop)
    elif type(bop) is c_ast.Cast or type(bop) is c_ast.UnaryOp : 
        if type(bop.expr) is not c_ast.Constant : 
            dico['expr'].append(bop.expr)
    
    #remove duplicates
    dico['expr'] = list(set(dico['expr']))
    dico['op'] = list(set(dico['op']))
    
    return dico

def getExpr(elem) :
    if type(elem) is c_ast.Cast or type(elem) is c_ast.UnaryOp :
        return getExpr(elem.expr)    
    else :
        return elem    

def getAllArgs(args) :
    ret = []
    for arg in args :
        if type(arg) is c_ast.FuncCall :
            ret += getAllArgs(arg.args.exprs)
        else :
            ret.append(arg)
    return ret


'''''''''''''''''''''''''''''''''
    FAULT SCRIPTS GENERATION
'''''''''''''''''''''''''''''''''


####################
#### TRANSIENT #####
####################     
       
def generateTransientDataStorageTestScript(stmt, funDir, bits, next=True) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    transientDataStorage = os.path.join(funDir, 'transientFIScripts', 'dataStorage')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    if bits == -1 :
        bits = [-1]
    
    bitsListString = ""
    for bit in bits :
        bitsListString += str(bit)
        bitsListString += "_"
    bitsListString = bitsListString[:-1]
    
    if type(stmt) is c_ast.ArrayRef :    
        scriptName = os.path.join(transientDataStorage, "transientDataStorage_" + 
        str(stmt.coord.line) + '_' + getArrayCellNameForScript(stmt) + '_bits-' + bitsListString)
        stmt.name = getArrayCellName(stmt)
    else :
        scriptName = os.path.join(transientDataStorage, "transientDataStorage_" + 
        str(stmt.coord.line) + '_' + stmt.name + '_bits-' + bitsListString)

    i = 0
    while(os.path.exists(scriptName + "_" + str(i))) :
        i += 1
    scriptName += '_' + str(i) 
    script = open(scriptName, 'w')
    initScript(script, scriptName, funName, cunit)
    script.write("XMLInit Transient Data Storage Error\n\n")
    script.write(corruptVar(stmt, stmt.coord.line, bits, next, True)) 
    closeScript(script, cunit)
    
    runScript = open(os.path.join(transientDataStorage, "run_transient_data_storage_tests.py"), 'a')
    runScript.write(   "os.system(\"gdb --batch -x " + scriptName + " --args program \" + str(timeout))\n")
    runScript.close()
    
def generateTransientDataProcessingTestScript(stmt, funDir, bits) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    transientDataProcessing = os.path.join(funDir, 'transientFIScripts', 'dataProcessing')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    if bits == -1 :
        bits = [-1]
        
    bitsListString = ""
    for bit in bits :
        bitsListString += str(bit)
        bitsListString += "_"
    bitsListString = bitsListString[:-1]
    
    if type(stmt) is c_ast.ArrayRef :    
        scriptName = os.path.join(transientDataProcessing, "transientDataProcessing_" + 
        str(stmt.coord.line) + '_' + getArrayCellNameForScript(stmt) + '_bits-' + bitsListString)
        stmt.name = getArrayCellNameForScript(stmt)
    else :
        scriptName = os.path.join(transientDataProcessing, "transientDataProcessing_" + 
        str(stmt.coord.line) + '_' + stmt.name + '_bits-' + bitsListString)
    
    if type(stmt) is c_ast.ArrayRef :    
        stmt.name = getArrayCellName(stmt)
    
    i = 0
    while(os.path.exists(scriptName + "_" + str(i))) :
        i += 1
    scriptName += '_' + str(i)
    script = open(scriptName, 'w')
    initScript(script, scriptName, funName, cunit)
    script.write("XMLInit Transient Data Processing Error\n\n")
    script.write(corruptVar(stmt, stmt.coord.line, bits, True, True)) 
    closeScript(script, cunit)
    
    runScript = open(os.path.join(transientDataProcessing, "run_transient_data_processing_tests.py"), 'a')
    runScript.write("os.system(\"gdb --batch -x " + scriptName + " --args program \" + str(timeout))\n")
    runScript.close()
    
####################
#### PERMANENT #####
####################

def generatePermanentDataStorageTestScript(stmts, funDir, bits, var, next=True) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    if type(var) is c_ast.ArrayRef :
        var = getArrayCellNameForScript(var)
    
    permanentDataStorage = os.path.join(funDir, 'permanentFIScripts', 'dataStorage')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    if bits == -1 :
        bits = [-1]
    
    bitsListString = ""
    for bit in bits :
        bitsListString += str(bit)
        bitsListString += "_"
    bitsListString = bitsListString[:-1]
    
    scriptName =    os.path.join(permanentDataStorage, 'permanentDataStorage_' + var 
                                     + '_bits-' + bitsListString)
    script = open(scriptName, 'w')
    initScript(script, scriptName, funName, cunit)
    script.write("XMLInit Permanent Data Storage Error\n\n")
    writePermanentCorruptions(stmts, script, bits, next)
    closeScript(script, cunit)
        
    runScript = open(os.path.join(permanentDataStorage, "run_permanent_data_storage_tests.py"), 'a')
    runScript.write("os.system(\"gdb --batch -x " + scriptName + " --args program \" + str(timeout))\n")
    runScript.close()
        
def generatePermanentDataProcessingTestScript(stmts, funDir, bits, op, next=True) :
    with open('injection-strategies.properties', 'r') as jsonfile :
        properties = json.load(jsonfile) 
    cunit = properties['cunit'] != ""
    
    permanentDataProcessing = os.path.join(funDir, 'permanentFIScripts', 'dataProcessing')
    funName = funDir.split(os.path.sep)
    funName = funName[len(funName)-1]
    
    if bits == -1 :
        bits = [-1]
    
    bitsListString = ""
    for bit in bits :
        bitsListString += str(bit)
        bitsListString += "_"
    bitsListString = bitsListString[:-1]
    
    scriptName = os.path.join(permanentDataProcessing, 'permanentDataStorage_' + op  + '_bits-' + bitsListString)
    script = open(scriptName, 'w')
    initScript(script, scriptName, funName, cunit)
    script.write("XMLInit Permanent Data Storage Error\n\n")
    writePermanentCorruptions(stmts, script, bits, next)
    closeScript(script, cunit)
        
    runScript = open(os.path.join(permanentDataProcessing, "run_permanent_data_processing_tests.py"), 'a')
    runScript.write("os.system(\"gdb --batch -x " + scriptName + " --args program \" + str(timeout))\n")
    runScript.close()


def writePermanentCorruptions(stmts, script, bits, next=True) :
    for stmt in stmts : 
        if type(stmt) is c_ast.ArrayRef :    
            stmt.name = getArrayCellName(stmt)
        script.write(corruptVar(stmt, stmt.coord.line, bits, True, False))
        script.write("\n")





























