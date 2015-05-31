# coding=utf-8
import gdb
from random import randint

class Corrupt(gdb.Function) :
    def __init__(self):
        super(Corrupt, self).__init__("corrupt")
        
    #convention : first bit = 1
    def invoke(self, var, bits="-1", nbrBits="1"):      
        print("fault injection")
        nbrBits = int(nbrBits)
        bitsList = str(bits).split(" ") 
        s = self.toBin(var)
        bits = str(bits)
        if bits == '-1' :
            bitsList = []
            for i in range(0, nbrBits) :
                b = randint(0, len(list(s))-1)
                while(b in bitsList) :
                    #TODO risque boucle infinie ?
                    b = randint(0, len(list(s))-1)
            
            if b > ((var.type.sizeof * 8) - 1) :
                b = (var.type.sizeof * 8) - 1
            elif b < 1 :
                b = randint(0, len(list(s))-1)
                
            bitsList.append(b)
        else :            
            bitsList = bitsList[0:int(nbrBits)]    
            
        s2 = self.bitFlip(s, list(set(bitsList))) #remove duplicates
        return long(s2, 2)
        
    
    def toBin(self, var) :    
        bitSize = var.type.sizeof * 8
        formatString = '{0:0'+str(bitSize)+'b}'
        #TODO : does it work if the value is coded on more bits than the long python type ?  
        return formatString.format(long(var))
        #return bin(var)
        
    
    def bitFlip(self, var, bits) :
        lvar = list(var)
        #bit = randint(0, len(lvar)-1)
        for bit in bits :
            bit = int(bit)
            if lvar[bit] is '1' :
                lvar[bit] = '0'
            else :
                lvar[bit] = '1'
        return "".join(lvar)
    
        
Corrupt()
