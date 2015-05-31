import sys
import random

sys.path.append('..')
from controlFlowHardening.tests_controlFlowHardening import generateCFE5TestScript    

def executeStrategy(stmtsDico, cfg, funDir, percBlocks, percLines) :
    blocks = list(cfg.blocks.values())
    sample = random.sample(blocks, round(len(blocks)*percBlocks))
    
    for bb0 in sample :
        generateCFE5TestScript(bb0, percLines, funDir)
