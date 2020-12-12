#!/usr/bin/env python 

'''
WHERE WE ARE NOW 

The Interpreter can now interpret basic OOP 

'''

import sys 
sys.path.insert(0, "scanner") 
sys.path.insert(0, "representing_code/tool") 
import operator 
import Lox 
from Token import Token 
from TokenType import TokenType 
import Expr 
import Stmt
from Environment import Environment 
from Callable import NativeClock, LoxFunction, Return, LoxClass, LoxInstance 
from collections import defaultdict 

class Interpreter(): 


    def __init__(self):
        '''
        Environment is created for scope purposes 
        '''
        self.globals = Environment() 
        self.globals.define("clock", NativeClock())
        self.environment = self.globals 
        self.local_scopes = defaultdict(str)
        self.operators = {"-": operator.sub, "+": operator.add, "/": operator.floordiv,"*": operator.mul}  

    def interpret(self, statements):
        '''
        We take our array of statement ASTs from the 
        Parser and start executing them 
        '''
        try:
            for statement in statements:
                self.execute(statement) 
        except RuntimeError as e:
            Lox.Lox.runtime_error(e.args) 

    def execute(self, stmt):
        '''
        Execution really means having the statement accept 
        the Interpreter visitor. Depending on the specific AST contained 
        in either Stmt.py or Expr.py, it'll then call one of 
        the Interpreter's methods below for evaluation. 
        '''
        return stmt.accept(self) 

    def resolve(self, expr, depth):
        '''
        Will be called within the Resolver class to find out how many
        environment "hops" it will take to get to a local variable 
        '''
        self.local_scopes[expr] = depth 

    def visit_Class_Statement(self, stmt):
        '''
        When we come across a Stmt.Class, we make sure our current environment
        has a label for this syntax node BEFORE wrapping it in a runtime LoxClass.
        We then reassign the syntax node class to this runtime klass. We break this
        into two pieces so the LoxClass can still access the class name in its methods.
        '''
        superclass = None 
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass) 
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.") 
        self.environment.define(stmt.name.lexeme, None) 
        if stmt.superclass:
            self.environment = Environment(self.environment) # we create a new env for the super class 
            self.environment.define("super", superclass) 
        methods = {}
        for method in stmt.methods:
            function = LoxFunction(self.environment, method, method.name.lexeme == 'init')
            methods[method.name.lexeme] = function 
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if superclass:
            self.environment = self.environment.enclosing  # go back to original 
        #klass = LoxClass(stmt.name, None, methods) 
        self.environment.assign(stmt.name, klass) 

    def visit_Function_Statement(self, stmt):
        '''
        If we encounter a Stmt.Function_Statement in our array of statements,
        we wrap it in a LoxFunction instance along with the current environment
        we are in (e.g. we could be in a block_statement body with a new inner
        environment which we're passing into LoxFunction) 
        '''
        function = LoxFunction(self.environment, stmt, False) 
        self.environment.define(stmt.name.lexeme, function) ## now our function call can retrieve the function name to get the object 

    def visit_Return_Statement(self, stmt):
        '''
        When we encounter a return statement class we can evaluate its value and raise 
        a custom Runtime Exception to get all the way back to our original Call expression 
        '''
        value = None 
        if stmt.value:
            value = self.evaluate(stmt.value)
        raise Return(value) 

    def visit_Block(self, stmt):
        '''
        Each block AST will get it's own Environment for its set of statements. 
        We pass in the current self.environment as the enclosing environment for 
        our new environment dedicated for this block. 
        '''
        assert isinstance(stmt, Stmt.Block), "must be of type Block Statement" 
        self.execute_block(stmt.statements, Environment(self.environment)) 

    def execute_block(self, statements, env):
        '''
        We make sure to keep track of our overall environment so that when 
        we are evaluating the statements with respect to a new environment for 
        our statement block, we can go back to our previous self.environment. 
        This is how we implement scoping concepts such as nesting and shadowing.
        '''
        prev_env = self.environment 
        try:
            self.environment = env     
            for statement in statements:
                self.execute(statement) 
        finally:
            self.environment = prev_env 

    def visit_If_Statement(self, stmt):
        assert isinstance(stmt, Stmt.If_Statement), "must be of type If Statement" 
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)
        return 

    def visit_While_Statement(self, stmt):
        assert isinstance(stmt, Stmt.While_Statement), "must of type While Statement"
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body) 
        return 
    
    def visit_Expression_Statement(self, stmt):
        assert isinstance(stmt, Stmt.Expression_Statement), "must be of type Expression Statement" 
        self.evaluate(stmt.expression)
        return 

    def visit_Print_Statement(self, stmt):
        '''
        All we need to do is evaluate the expression AST and print it out 
        '''
        assert isinstance(stmt, Stmt.Print_Statement), "must be of type Print Statement" 
        value = self.evaluate(stmt.expression)
        print(str(value)) 
        return 

    def visit_Var_Statement(self, stmt):
        '''
        The point of variables is to "remember" so here we initialize it with an expression 
        and define it in our local environment 
        '''
        assert isinstance(stmt, Stmt.Var_Statement), "must be of type Variable Statement" 
        value = None 
        if stmt.initializer:
            value = self.evaluate(stmt.initializer) 
        self.environment.define(stmt.name.lexeme, value) 
        return 

    # EXPRESSION VISITOR METHODS BELOW

    def evaluate(self, expr):
        '''
        expr is a type of AST defined in "Expr.py" and will
        call one of the visitor methods below depending on its type 
        '''
        return expr.accept(self) 

    def visit_Logical(self, expr):
        '''
        The short-circuiting is why we didn't package Logical Operator expressions 
        with the rest of the Binary operations. If we detect an OR token and we 
        know the left-hand operand is 'truthy', then we can return it and short-circuit.
        If it is an AND and the left-hand side is 'falsy' then we return it and short-circuit.
        Only if the above two cases don't short-circuit, do we bother evaluating 
        the right operand
        '''
        assert isinstance(expr, Expr.Logical), "Expression must be of type If otherwise cannot evaluate" 
        left = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left): 
                return left 
        else:
            if not self.is_truthy(left): return left 
        return self.evaluate(expr.right) 

    def visit_Assign(self, expr):
        '''
        In our env, create an assignment for our variable to a value evaluation. 
        With the Resolver, we can also assign a variable in a local scope different
        values.
        '''
        assert isinstance(expr, Expr.Assign), "Expression must be of type Assignment otherwise cannot evaluate" 
        value = self.evaluate(expr.value)
        if expr in self.local_scopes: 
            distance = self.local_scopes[expr] 
            self.environment.assign_at(distance, expr.name, value) 
        else: 
            self.environment.assign(expr.name, value)  
        return value 

    def visit_Literal(self, expr):
        assert isinstance(expr, Expr.Literal), "Expression must be of type Literal otherwise cannot evaluate" 
        return expr.value

    def visit_Grouping(self, expr):
        assert isinstance(expr, Expr.Grouping), "Expression must be of type Grouping otherwise cannot evaluate"
        return self.evaluate(expr.expression) 

    def visit_Unary(self, expr):
        assert isinstance(expr, Expr.Unary), "Expression must be of type Unary otherwise cannot evaluate"
        right = self.evaluate(expr.right) 
        if expr.operator.token_type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right) 
            if self.is_int(right):
                return -(int(right))
            return -(float(right))
        elif expr.operator.token_type == TokenType.BANG:
            return not self.is_truthy(right) 
        return

    def visit_Variable(self, expr):
        return self.look_up_var(expr.name, expr) 

    def visit_Binary(self, expr):
        '''
        Many kinds of binary operations exist such as 
        addition, subtraction, >=, etc. For binary expressions 
        that need numbers, we first check the operands before 
        committing to the evaluation (e.g. can't try to convert
        a string to a float) 
        '''
        assert isinstance(expr, Expr.Binary), "Expression must be of type Binary otherwise cannot evaluate" 
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.token_type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right) 
            return self.perform_operation("-", left, right) 
        elif expr.operator.token_type == TokenType.SLASH:
            try: 
                self.check_number_operands(expr.operator, left, right) 
                return self.perform_operation("/", left, right) 
            except ZeroDivisionError:
                raise RuntimeError(expr.operator, "Cannot divide by 0") 
        elif expr.operator.token_type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right) 
            return self.perform_operation("*", left, right) 
        elif expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return left + right         # basic (+) operator overloading for strings 
            res = self.perform_operation("+", left, right) 
            if res:
                return res 
            raise RuntimeError(expr.operator,"Operands must be two numbers or two strings.") 
        elif expr.operator.token_type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right) 
            return float(left) > float(right) 
        elif expr.operator.token_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right) 
            return float(left) >= float(right) 
        elif expr.operator.token_type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right) 
            return float(left) < float(right)
        elif expr.operator.token_type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right) 
            return float(left) <= float(right) 
        elif expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right) 
        elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right) 
        return None 

    def visit_Call(self, expr):
        '''
        Our callee's identifier must exist in our environment and then we can 
        evaluate all its arguments (because some of them may have side-effects). 
        We do two checks to make sure our callee is even callable and the number
        of arguments match the function object's # of parameters 
        '''
        callee = self.evaluate(expr.callee)    ## if successful, expr.callee will return its corresponding Lox Function object 
        arguments = [self.evaluate(argument) for argument in expr.arguments] 
        if not callable(callee):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")  
        function = callee 
        if len(arguments) != function.arity():
            raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")  

        return function.call(self, arguments)   ## will get return value 

    def visit_Get(self, expr):
        '''
        A Get Expression consists of the LoxInstance of a class and the 
        property identifier that we are trying to access with dot notation. 
        (e.g. LoxInstanceOfClass.someProperty). The actual getting is done 
        in the LoxInstance class 
        '''
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name) 
        raise RuntimeError(expr.name, "Only instances have properties.") 

    def visit_Set(self, expr):
        obj = self.evaluate(expr.object) 
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.") 
        value = self.evaluate(expr.value)
        obj.set(expr.name, value) 
        return value 

    def visit_Super(self, expr):
        distance = self.local_scopes[expr] 
        superclass = self.environment.get_at(distance, "super") 
        obj = self.environment.get_at(distance - 1, "this") 
        method = superclass.find_method(expr.method.lexeme) 
        if not method:
            message = "Undefined property '" + expr.method.lexeme + "'."
            raise RuntimeError(expr.method, message) 
        return method.bind(obj) 

    def visit_This(self, expr):
        return self.look_up_var(expr.keyword, expr) 

    def check_number_operand(self, operator, operand):
        try:
            float(operand)
        except (TypeError, ValueError):
            raise RuntimeError(operator, "Operand must be a number.") 

    def check_number_operands(self, operator, *operands):
        left, right = operands[0], operands[1] 
        if type(left) not in [int, float] or type(right) not in [int, float]:
            raise RuntimeError(operator, "Operands must be numbers.") 
        try:
            float(left)
            float(right)
        except (TypeError, ValueError): 
            raise RuntimeError(operator, "Operands must be numbers.") 

    def is_int(self, x):
        '''
        Helper function to make sure we perform binary operations 
        without a trailing 0 if both operands are ints 
        '''
        try:
            a = float(x)
            b = int(a) 
        except (TypeError, ValueError):
            return False 
        else:
            return a == b

    def perform_operation(self, operator, *operands):
        left, right = operands[0], operands[1] 
        if type(left) not in [int, float] or type(right) not in [int, float]:
            return False 
        operator = self.operators[operator] 
        int_res = operator(int(left), int(right)) 
        if self.is_int(left) and self.is_int(right):
            return int_res 
        float_res = operator(float(left), float(right))  
        return float_res if float_res != int_res else int_res

    def is_equal(self, a, b):
        if a is None and b is None: return True 
        elif a is None: return False 
        return operator.eq(a, b) and type(a) == type(b)   ## Python doesn't have strict equality

    def is_truthy(self, obj):
        '''
        If the given object is None or False it'll return False 
        otherwise will return true 
        '''
        if obj is None: return False 
        if type(obj) == bool: return obj 
        return True 

    def look_up_var(self, name: Token, expr):
        '''
        we get the resolved # of "environment hops" with distance.
        If it's in a local scope we can find how many hops it takes.
        Otherwise we assume it must be a global variable 
        '''
        distance = self.local_scopes[expr] 
        if distance or distance == 0:
            return self.environment.get_at(distance, name.lexeme)
        elif name.lexeme in self.environment.values:
            return self.environment.get(name) 
        else:
            return self.globals.get(name) 

