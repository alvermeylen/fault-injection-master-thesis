import sys
import random

sys.path.append('..')
from controlFlowHardening.tests_controlFlowHardening import generateCFE3TestScript    

def executeStrategy(stmtsDico, cfg, funDir, percBlocks, percLines) :
    blocks = list(cfg.blocks.values())
    sampleStart = random.sample(blocks, round(len(blocks)*percBlocks))
    sampleArrival = random.sample(blocks, round(len(blocks)*percBlocks))
    
    for bb0 in sampleStart :
        for bb1 in sampleArrival :
            generateCFE3TestScript(bb0, bb1, percLines, funDir)
