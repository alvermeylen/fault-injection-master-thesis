# coding=utf-8
from pycparser import c_parser, c_ast, parse_file
import argparse
import os

def transform_assert_equal(bop, hardFunDico) :
    #confidential code
    return ''
        
def generateHardenedCunitTests(dico, cunitFile, rootDirectory) :    
    with open(cunitFile, 'r') as f:
        lines = f.readlines()
    
    outputFile = open(os.path.join(rootDirectory,'cunit_tests.c'), 'w')
            
    ast = parse_file(cunitFile, use_cpp=True,
                    cpp_path='cpp', 
                    cpp_args=r'-I./utils/fake_libc_include')
    
                    
    for e in ast.ext :
        if e.coord.file == cunitFile :
            if type(e) is c_ast.FuncDef :
                #convention : all test function must begin with "test_"
                if "test_" in e.decl.name :
                    for stmt in e.body.block_items :
                        if type(stmt) is c_ast.Compound : 
                            for s in stmt.block_items :
                                if type(s) is c_ast.FuncCall :
                                    if "assert" in s.name.name :
                                        lines[s.coord.line-1] = transform_assert_equal(s.args.exprs[0], dico)
                elif e.decl.name == "main" :
                    lineCoord = e.body.block_items[0].coord.line - 1
                    tmp = lines[lineCoord]
                    lines[lineCoord]  = "\tsignal (SIGALRM, catch_alarm);\n"
                    lines[lineCoord] += "\tif(argc > 1) {\n"
                    lines[lineCoord] += "\t\tTIMEOUT = atoi(argv[1]);\n"
                    lines[lineCoord] += "\t} else {\n"
                    lines[lineCoord] += "\t\tTIMEOUT = 60;\n"
                    lines[lineCoord] += "\t}\n"
                    lines[lineCoord] += tmp 
                                
    
    for line in lines :
        outputFile.write(line)
