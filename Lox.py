#!/usr/bin/env python

'''
Our main interpreter program that when run as an executable will either start a REPL session 
or evaluate a program file. 
'''

import sys 
sys.path.insert(0, "scanner")
sys.path.insert(0, "representing_code/") 
sys.path.insert(0, "representing_code/tool/") 
import enum 
from enum import auto 
from Token import Token 
from TokenType import TokenType
import Scanner
from ASTPrinter import ASTPrinter
from Parser import Parser 
from Interpreter import Interpreter 
from Resolver import Resolver 

class Lox: 
    had_error = False 
    had_runtime_error = False 

    def __init__(self):
        self._validate_inputs() 

    def _validate_inputs(self):
        '''
        Determine whether to open a REPL session 
        or evaluate a program file 
        '''
        if len(sys.argv) > 2:
            print("Usage: plox [script]:") 
            exit(1) 
        elif len(sys.argv) == 2:
            self.run_file(sys.argv[1]) 
        else:
            self.run_prompt() 

    def run_file(self, path: str): 
        try:
            with open(path, "r") as f:
                content = f.read() 
            self.run(content) 
            if self.had_error:
                sys.exit(1)  
            if self.had_runtime_error:
                sys.exit(2)
        except IOError:
            print("file can't be found") 

    def run_prompt(self):
        try:
            for line in sys.stdin:
                if not line: 
                    sys.exit()
                print(f"{self.run(line)}")
        except KeyboardInterrupt:
            sys.exit(1)

    def run(self, source: str):
        '''
        Driver -> calls in the Scanner class that does the heavy lifting generating tokens from lexemes. 
        Afterwards our Parser generates an unambiguous AST which is passed to our ASTPrinter Visitor 
        to print out for our eyes. It's also passed to our Interpreter, a Visitor itself and which 
        at this point can only evaluate basic expressions like a calculator 
        '''
        scanner = Scanner.Scanner(source) 
        tokens = scanner.scan_tokens() 
        #for token in tokens:
        #    print(token)
        parser = Parser(tokens) 
        statements = parser.parse()
        if self.had_error: return 
        interpreter = Interpreter() 
        resolver = Resolver(interpreter) 
        resolver.resolve(statements) 
        if self.had_error: return       ## if there is an error in parsing/resolving, we don't bother to interpret 
        interpreter.interpret(statements) 

    ## because we're calling "Lox.error" in the Scanner, we'll need to call the Lox class itself 
    ## and staticmethods can't access class attributes
    @classmethod                    
    def error(self, *args):
        if isinstance(args[0], int) and isinstance(args[1], str):
            line, message = args[0], args[1] 
            Lox.report(line, "", message) 
        else:                               ## second case for Parsing 
            token, message = args[0], args[1] 
            if token.token_type == TokenType.EOF:
                Lox.report(token.line, " at end", message) 
            else:
                Lox.report(token.line, " at '" + token.lexeme + "'", message) 

    @classmethod 
    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error {where}: {message}") 
        had_error = True

    @classmethod 
    def runtime_error(self, args):
        token, message = args
        print(f"{message}\n[line {token.line}]") 
        had_runtime_error = True 

if __name__ == "__main__":
    l = Lox()
