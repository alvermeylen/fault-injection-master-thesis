import sys
import random

sys.path.append('..')
from controlFlowHardening.tests_controlFlowHardening import generateCFE2TestScript    

def executeStrategy(stmtsDico, cfg, funDir, percBlocks) :
    tmpblocks = list(cfg.blocks.values())
    blocks = list(filter(lambda b : len(b.children) > 1, tmpblocks))
    sample = random.sample(blocks, round(len(blocks)*percBlocks))
    
    for bb in sample :
        generateCFE2TestScript(bb, funDir)
