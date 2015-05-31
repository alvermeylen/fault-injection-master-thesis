# coding=utf-8
#from pycparser import c_ast

## statements are of type Node from c_ast

### Represents the classic basic bloc ###
class BasicBlock:
    
    def __init__(self, bid, coord, parents = [], condition = None):
        self.bid = bid
        self.coordBegin = coord
        self.coordEnd = coord
        self.parents = parents
        self.statements = []
        self.children = [] #we don't know the children yet.
        if len(parents) > 0:
            for p in parents:
                p.children.append(self)
        self.condition = condition
        
    def addStatement(self, stmt):
        self.statements.append(stmt)
        if stmt.coord.line > self.coordEnd.line :
            self.coordEnd = stmt.coord
        elif stmt.coord.line < self.coordBegin.line :
            self.coordBegin = stmt.coord
        
    def addChild(self, child):
        self.children.append(child)
        
    def setCondition(self, condition):
        self.condition = condition
        
    def getFirstStatement(self):
        return self.statements[0]
    
    def getLastStatement(self):
        return self.statements[len(self.statements)-1]
    
    def merge(self, bb):
        for stmt in bb.statements :
            self.addStatement(stmt)
        self.children += bb.children
        self.condition = bb.condition
        
    def __str__(self):
        ret =   "---------------" + '\n'
        ret +=  "| BB" + str(self.bid) + "         |" + '\n'
        ret +=  "|             |" + '\n'
        for stmt in self.statements :
            ret += "|   " + str(stmt.coord) + "|" + '\n'
            
        ret +=  "---------------" + '\n'
        return ret
    
    def __eq__(self, other) : 
        return self.bid == other.bid
    
    def __lt__(self, other) :
        return self.bid < other.bid
        
class CFG:
    
    def __init__(self):
        self.count = 0 #no child yet
        self.blocks = dict()
        
    def addBlock(self, bb):
        self.blocks[bb.coordBegin.line] = bb
    
    def addBlocks(self, bbList):
        for block in bbList :
            self.addBlock(block)
        
    ### Give the block containing the line at lineNbr ##
    def getBlock(self, lineNbr) :
        goodKey = max(key for key in self.blocks if key <= lineNbr)
        return self.blocks[goodKey]
    
    def getRoot(self) :
        key = min(self.blocks)
        return self.blocks[key]
        
        
    def __str__(self):
        ret = ""
        for key, bb in self.blocks.items() :
            ret += str(bb)
        return ret
    
    def count(self):
        return len(self.blocks)
    
    def createDotFile(self, name='cfg.dot') :
        dotFile = open(name, 'w')
        dotFile.write('digraph G {\n')
        
        for key, bb in self.blocks.items() :
            for child in bb.children :
                dotFile.write(str(bb.bid) + ' -> ' + str(child.bid) + '\n')
        
        dotFile.write('}\n')
            
    
        
