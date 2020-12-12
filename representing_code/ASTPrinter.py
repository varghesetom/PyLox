#!/usr/bin/env python

import sys 
sys.path.insert(1, "tool/") 
sys.path.insert(1, "../scanner") 
import Expr 
from Token import Token 
from TokenType import TokenType 

'''

VISITOR PATTERN IMPLEMENTATION  

ASTPrinter is an example of a Visitor class that will be passed to the accept() methods of our concrete Expression classes. 
They will each then be passed back into the ASTPrinter to print out their parenthetical forms. 

'''

class ASTPrinter:

    def print_ast(self, expr):
        '''
        Expr argument is a syntax node in the file that we generated with "GenerateAST.py". 
        Based on the syntax node type, it'll call one of the following visitor methods below 
        '''
        return expr.accept(self) 

    def visit_Binary(self, expr):
        assert isinstance(expr, Expr.Binary), "Must be Binary Expression otherwise cannot print its AST" 
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right) 

    def visit_Grouping(self, expr):
        assert isinstance(expr, Expr.Grouping), "Must be Grouping Expression otherwise cannot print its AST" 
        return self.parenthesize("group", expr.expression) 

    def visit_Literal(self, expr):
        assert isinstance(expr, Expr.Literal), "Must be Literal Expression otherwise cannot print its AST" 
        return str(expr.value)

    def visit_Unary(self, expr):
        assert isinstance(expr, Expr.Unary), "Must be Unary Expression otherwise cannot print its AST"
        return self.parenthesize(expr.operator.lexeme, expr.right) 

    def parenthesize(self, name, *exprs):
        builder = ["(", name] 
        for expr in exprs:
            builder.append(expr.accept(self)) 
        builder.append(")") 
        return " ".join(builder) 

if __name__ == "__main__":
    ## Test Expression below 
    left_expression = Expr.Unary(Token(TokenType.MINUS, "-", 1, None), Expr.Literal(123)) 
    operator = Token(TokenType.STAR, "*", 1, None) 
    right_expression = Expr.Grouping(Expr.Literal(45.67)) 
    main_expression = Expr.Binary(left_expression, operator, right_expression) 
    print(ASTPrinter().print_ast(main_expression))


