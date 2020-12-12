#!/usr/bin/env python 

'''
Instead of directly writing out each Statement and Expression Syntax node, this file will be used to generate the "Expr.py" and
"Stmt.py" files that will have various expressions to be used as part of our grammar for Lox. Honestly, there's not much of a  
need to have this Expr.py file be placed in tool/ but the original version had it as such so I'll keep it the same way as well. 
'''

import sys 
from typing import List

class GenerateAST:
    def __init__(self):
        try:
            if len(sys.argv) != 2:
                print("Usage: ./GenerateAST.py <output_directory>") 
                sys.exit(1) 
            self.output_dir = sys.argv[1] 
        except IOError:
            print("ruh-oh can't find directory") 

    def defineAST(self, base_name : str, types : List):
        path = self.output_dir + "/" + base_name + ".py" 
        with open (path, "w") as f:
            f.write("#!/usr/bin/env python\n\n") 
            f.write("import sys\n") 
            f.write("sys.path.insert(1, '../../scanner')\n")
            f.write("from abc import ABC, abstractmethod\n") 
            if base_name == "Stmt":         ## Statements will need to import created Exprs
                f.write("from Expr import Expr\n") 
            f.write("from Token import Token\n\n") 
            f.write(f"class {base_name}(ABC):\n\n") 
            f.write("\t@abstractmethod\n") 
            f.write(f"\tdef __init__(self, left, operator, right):\n\t\tpass\n")
            for line in types:
                assert len(line.split(":")) == 2, "The line is not properly formatted. Can't have spaces in between ':' character. Must only be 2 items total"
                class_name = line.split(":")[0]
                fields = line.split(":")[1]   ## each field will have the "static type" along with its identifier 
                fields = fields if len(fields) == 1 else fields.split(",")  ## depends what expression passes in. Binary has multiple fields while Literal only has 1 (value) 
                arg_fields = [field.split()[1] for field in fields] 
                arg_fields = ", ".join(arg_fields) 
                f.write(f"\nclass {class_name}({base_name}):\n\n")
                f.write(f"\tdef __init__(self, {arg_fields}):\n")
                for field in fields:
                    static_type, identifier = field.split() 
                    #if identifier != "else_branch" and class_name not in ["Return_Statement", "Class_Statement"]: 
                        #f.write(f"\t\tassert isinstance({identifier}, {static_type}), '{identifier} needs to match {static_type} type'\n") 
                    f.write(f"\t\tself.{identifier} = {identifier}\n")
                f.write("\n\tdef accept(self, visitor):\n")
                f.write(f"\t\treturn visitor.visit_{class_name}(self)\n") 


if __name__ == "__main__":
    t = GenerateAST() 
    t.defineAST("Expr", [ 
        "Assign:Token name, Expr value", 
        "Binary:Expr left, Token operator, Expr right",
        "Call:Expr callee, Token paren, list arguments", 
        "Get:Expr object, Token name", 
        "Set:Expr object, Token name, Expr value", 
        "Super:Token keyword, Token method", 
        "This:Token keyword", 
        "Grouping:Expr expression",
        "Literal:object value",
        "Logical:Expr left, Token operator, Expr right",  
        "Unary:Token operator, Expr right",
        "Variable:Token name" 
    ])
    t.defineAST("Stmt", [
        "Block:list statements", 
        "Class_Statement:Token name, Expr superclass, list methods", 
        "Expression_Statement:Expr expression",
        "Function_Statement:Token name, list params, list body", 
        "If_Statement:Expr condition, Stmt then_branch, Stmt else_branch",  
        "Print_Statement:Expr expression",
        "Return_Statement:Token keyword, Expr value", 
        "Var_Statement:Token name, Expr initializer",
        "While_Statement:Expr condition, Stmt body" 
    ])
