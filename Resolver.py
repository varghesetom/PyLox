
import sys 
sys.path.insert(0, "representing_code/tool/") 
sys.path.insert(0, "scanner/") 
import enum
from enum import auto 
from Expr import Expr 
from Stmt import Stmt 
from Token import Token
import TokenType 
import Lox 

class FunctionType(TokenType.EnumName):
    NONE, FUNCTION, METHOD, INITIALIZER = auto(), auto(), auto(), auto() 

class ClassType(TokenType.EnumName):
    '''
    will be used to know if we are trying to use "this" outside of a class.
    Will also be used for inheritance 
    '''
    NONE, CLASS, SUBCLASS = auto(), auto(), auto() 

class Resolver:

    def __init__(self, interpreter):
        self.interpreter = interpreter 
        self.scopes = [] 
        self.current_function = FunctionType.NONE 
        self.current_class = ClassType.NONE # start off knowing that we aren't in a class just yet 

    def resolve(self, expr_or_stmts):
        if isinstance(expr_or_stmts, Expr):
            self._resolve(expr_or_stmts)  
        elif isinstance(expr_or_stmts, Stmt):
            self._resolve(expr_or_stmts)
        elif isinstance(expr_or_stmts, list):
            for statement in expr_or_stmts:
                self._resolve(statement) 

    def _resolve(self, obj):
        '''
        Passing the Resolver Visitor to either a statement
        or an expression. Based on its specific Stmt or Expr
        subclass type, the "accept()" method will call one of 
        the "visit_" visitor methods here. 
        '''
        obj.accept(self)   ## passing either a statement or an expression 

    def resolve_local(self, expr, name: Token):
        for hop in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[hop]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - hop) 
                return 
        # not found -- assume it's global 

    def resolve_function(self, function: Stmt, function_type: FunctionType):
        enclosing_function = self.current_function 
        self.current_function = function_type 
        self.begin_scope() 
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope() 
        self.current_function = enclosing_function 

    def begin_scope(self):
        self.scopes.append({}) 

    def end_scope(self):
        self.scopes.pop() 

    def declare(self, name: Token):
        if not self.scopes: 
            return 
        else: 
            innermost_scope = self.scopes[-1] 
            if name.lexeme in innermost_scope:
                Lox.Lox.error(name, "Already variable with this name in this scope") 
            innermost_scope[name.lexeme] = False 

    def define(self, name: Token):
        if not self.scopes: 
            return
        else:
            innermost_scope = self.scopes[-1] 
            innermost_scope[name.lexeme] = True 


    # VISITOR METHODS 

    def visit_Block(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements) 
        self.end_scope()

    def visit_Class_Statement(self, stmt):
        '''
        Not common for a class to be a local 
        variable but we allow it here with Lox 
        '''
        enclosing_class = self.current_class  ## store in case we have nested classes so we need to store the outer class
        self.current_class = ClassType.CLASS 
        self.declare(stmt.name)
        self.define(stmt.name) 
        if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme: 
            Lox.Lox.error("A class can't inherit from itself.") 
        if stmt.superclass: 
            self.current_class = ClassType.SUBCLASS 
            self.resolve(stmt.superclass)
        if stmt.superclass:
            self.begin_scope() 
            self.scopes[-1]["super"] = True 
        self.begin_scope()
        self.scopes[-1]["this"] = True 
        for method in stmt.methods:
            declaration = FunctionType.METHOD 
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER 
            self.resolve_function(method, declaration) 
        self.end_scope() 
        if stmt.superclass:
            self.end_scope() 
        self.current_class = enclosing_class 

    def visit_Var_Statement(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer) 
        self.define(stmt.name)

    def visit_Variable(self, expr):
        if self.scopes and expr.name.lexeme in self.scopes[-1] and self.scopes[-1][expr.name.lexeme] == False: 
            Lox.Lox.error(expr.name, "Can't read local variable in its own initializer")
        self.resolve_local(expr, expr.name) 

    def visit_Assign(self, expr):
        self.resolve(expr.value) 
        self.resolve_local(expr, expr.name) 

    def visit_Function_Statement(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION) 

    ## OTHER AST CLASSES 

    def visit_Expression_Statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_If_Statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_Print_Statement(self, stmt):
        self.resolve(stmt.expression)

    def visit_Return_Statement(self, stmt):
        if self.current_function == FunctionType.NONE:
            Lox.Lox.error(stmt.keyword, "Can't return from top-level code") 
        if stmt.value:
            if self.current_function == FunctionType.INITIALIZER:
                Lox.Lox.error(stmt.keyword, "Can't return a value from an initializer") 
            self.resolve(stmt.value)

    def visit_While_Statement(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_Binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_Call(self, expr):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)

    def visit_Get(self, expr):
        self.resolve(expr.object)

    def visit_Grouping(self, expr):
        self.resolve(expr.expression)

    def visit_Literal(self, expr):
        return 

    def visit_Logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_Unary(self, expr):
        self.resolve(expr.right)

    def visit_Set(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object) 

    def visit_This(self, expr):
        if self.current_class == ClassType.NONE:
            Lox.Lox.error(expr.keyword, "Can't use 'this' outside of a class") 
            return 
        self.resolve_local(expr, expr.keyword)

    def visit_Super(self, expr):
        if self.current_class == ClassType.NONE:
            Lox.Lox.error(expr.keyword, "Can't use 'super' outside of a class") 
        elif self.current_class != ClassType.SUBCLASS:
            Lox.Lox.error(expr.keyword, "Can't use 'super' in a class with no superclass") 
        self.resolve_local(expr, expr.keyword) 


