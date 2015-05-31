import sys
import random

sys.path.append('..')
from controlFlowHardening.tests_controlFlowHardening import generateCFE1TestScript    

def executeStrategy(stmtsDico, cfg, funDir, percBlocks) :
    blocks = list(cfg.blocks.values())
    sampleStart = random.sample(blocks, round(len(blocks)*percBlocks))
    sampleArrival = random.sample(blocks, round(len(blocks)*percBlocks))
    
    for bb0 in sampleStart :
        for bb1 in sampleArrival :
            generateCFE1TestScript(bb0, bb1, funDir)
