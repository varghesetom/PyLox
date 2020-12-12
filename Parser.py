#!/usr/bin/env python

'''
WHERE WE ARE

We can now encapsulate our logic into units that can be re-used: functions. The chapter goes in the unusual way of 
defining a Function Call first and then explaining what a Function Declaration/Object is. In this file, we can organize
the new additions with respect to Function Call and Function Declaration. 

Function Declaration --> Before a function can be called, it must be defined. To reflect this, we add or revamp the functions 
functions "declaration()" and "function()" Declaration()" mainly identifies whether we encounter a FUN token and if so, calls  
"function" while passing in the word 'function' as an argument. This is because later when we add classes, we will use the same FUN token
to mark down class methods so we need a way of differentiating methods and functions with the "function()" call. The "function()"
call is a straightforward implementation of what a typical function looks like: identifier as the name of function, the parameters 
grouped together in parentheses, and a function body. We bundle this in a Function Statement and call it a day. 

Function Call --> Only after a function is defined, which also means the Interpreter later will store this function object in its environment,
can we actually call it. Surprisingly, a function call is extremely high precedence. The function "operator" is in fact the highest precedence
out of all operators. When we look at Python too we can see that operators like "!" or "<" are only evaluated after a function call (e.g. 
if we have a function called "is_true()" then we can write "if (!is_true()))...". If the "!" was higher precedence, we would 
get an error because "is_true()" isn't evaluated to anything as of yet.) As a result, we have the actual call parsing within the "unary()" 
parsing call. We only call "finish_call()" if we evaluate to a primary expression and there's a LEFT_PAREN. 

'''

import sys 
sys.path.insert(0, "scanner") 
sys.path.insert(0, "representing_code/tool")
from TokenType import TokenType 
import Expr
import Stmt 
import Lox 

class Parser:
    
    def __init__(self, tokens):
        '''
        Initialize our tokens which are produced by our Scanner 
        '''
        self.tokens = tokens 
        self.current = 0 

    def parse(self):
        '''
        Our program can now "remember" by storing all statements into an 
        array for the Interpreter.py later. In terms of precedence, the 
        "declaration()" is now the highest precedence, supplanting "expression()"
        from before 
        '''
        try:
            statements = [] 
            while not self.is_at_end():
                valid_statement = self.declaration()   
                if valid_statement:            ## in case there is a ParseError we don't want to add a NoneType 
                    statements.append(valid_statement) 
            return statements 
        except ParseError:  ## we return a ParseError in the error() function 
            return 

    def declaration(self):
        '''
        check if there is a Class or Function token 
        Otherwise, we go and proceed onto a Variable token 
        to try and see if we can bundle up a Variable statement syntax class. Otherwise 
        continue on with "statement()"  
        '''
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration() 
            if self.match(TokenType.FUN):
                return self.function("function") 
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement() 
        except ParseError as p:
            self.synchronize()  
            return 

    def class_declaration(self):
        '''
        We arrange our tokens in the correct order to be packaged as a 
        LoxClass AST class: have the class name, methods, and any superclass
        that the class inherits from. 
        In Lox, the syntax is "SUBCLASS_NAME < SUPERCLASS_NAME"  
        '''
        name = self.consume(TokenType.IDENTIFIER, "Expect class name") 
        superclass = None 
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name") 
            superclass = Expr.Variable(self.previous()) 
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body") 
        methods = [] 
        while not self.is_at_end() and not self.check(TokenType.RIGHT_BRACE):
            methods.append(self.function("method")) 
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body") 
        return Stmt.Class_Statement(name, superclass, methods) 

    def function(self, kind):
        '''
        Function Declaration -> a function must have 
            1. Name
            2. Parameters
            3. Body 
        '''
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name") 
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.") 
        parameters = [] 
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name")) 
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255: 
                    self.error(self.peek(), "Can't have more than 255 parameters") 
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name"))
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters") 
        err_message = "Expect '{' before " + str(kind) + " body" 
        self.consume(TokenType.LEFT_BRACE, err_message)  
        body = self.block_statement() 
        return Stmt.Function_Statement(name, parameters, body) 

    def var_declaration(self):
        '''
        create a Variable Statement as long as our tokens are correct and in
        the right order. 
        ''' 
        name = self.consume(TokenType.IDENTIFIER, "Expect a variable name.") 
        initializer = None 
        if self.match(TokenType.EQUAL):
            initializer = self.expression() 
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.") 
        return Stmt.Var_Statement(name, initializer) 

    def statement(self):
        '''
        If we aren't creating a Variable Statement, then it could be either:
            1. Return statement 
            2. Block statement 
            3. While statement 
            4. For statement 
            5. If statement 
            6. Print statement
            7. Expression statement 
        '''
        if self.match(TokenType.RETURN): 
            return self.return_statement() 
        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block_statement()) 
        if self.match(TokenType.IF):
            return self.if_statement() 
        if self.match(TokenType.PRINT): 
            return self.print_statement() 
        if self.match(TokenType.WHILE):         ## new 'While' statement case for this chapter 
            return self.while_statement() 
        if self.match(TokenType.FOR):
            return self.for_statement()
        return self.expression_statement() 

    def return_statement(self):
        keyword = self.previous()
        value = None 
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value") 
        return Stmt.Return_Statement(keyword, value) 

    def block_statement(self):
        '''
        If we have a Block setup with a "{" then we create a new subsection of 
        valid statements and return them provided that we have a closing brace 
        '''
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            valid_statement = self.declaration() 
            if valid_statement: 
                statements.append(valid_statement) 
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.") 
        return statements 

    def if_statement(self):
        '''
        Evaluating an IF conditional is straightforward. Match the 
        enclosing parentheses and make sure there is an expression in between. 
        Execute the branches and bundle into a If Statement AST class 
        '''
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.") 
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if-condition.") 
        then_branch = self.statement()
        else_branch = None 
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return Stmt.If_Statement(condition, then_branch, else_branch) 

    def print_statement(self):
        '''
        Bundle up a Print statement syntax class. Note that here we are calling 
        "expression()" which means we're first getting the Expression syntax 
        node whatever it may be before bundling that up in a Statement syntax 
        tree 
        '''
        value = self.expression() 
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.") 
        return Stmt.Print_Statement(value)

    def while_statement(self):
        '''
        Straightforward implementation of the While Statement AST class 
        '''
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.") 
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition") 
        body = self.statement() 
        return Stmt.While_Statement(condition, body) 

    def for_statement(self):
        '''
        A for statement is made up of 4 parts, the first 3 of which are
        in a parenthetical group. 
            1. Initializer -> optional; conventionally a variable 
            2. Condition -> optional; an expression AST class. If not set,
            loop will run forever 
            3. Increment -> optional; 
            4. Body -> after parsing the above 3, we then parse the rest 
            as the body statement. But after doing so, we need to bundle 
            up the entire for-loop in the correct order. Depending on 
            whether each of the above 3 parts exists, we return a Statement
            block in the appropriate order (e.g. we execute a statement body
            and only then do we execute the increment like in a regular for
            loop) 
        '''
        # initializer 
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.") 
        initializer = None 
        if self.match(TokenType.SEMICOLON):
            pass 
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement() 
        ## condition 
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition") 
        ## increment 
        increment = None 
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.") 
        # body 
        body = self.statement() 
        if increment:
            body = Stmt.Block([body, Stmt.Expression_Statement(increment)])
        if not condition:
            condition = Expr.Literal(True) 
        body = Stmt.While_Statement(condition, body) 
        if initializer:
            body = Stmt.Block([initializer, body]) 
        return body 

    def expression_statement(self):
        '''
        similar to print statement above. In Lox's case, expression statements 
        are just expressions that terminate with a semicolon. 
        '''
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.") 
        return Stmt.Expression_Statement(expr) 


    ## PARSING EXPRESSIONS 

    def expression(self):
        '''
        This top-line production rule really calls the next rule in the precedence chain 
        '''
        return self.assignment() 

    def assignment(self):
        '''
        slight difference from other recursions because we don't want to have a chain 
        of "=" operator/operands in the left-hand side. E.g. Can't have expressions 
        like "a = b + c = d" 

        The "Control Flow" chapter also includes the starting point for Logical Operators 
        with "or_op()"

        The "Classes" chapter introduces setters which only activate when the Left-Hand 
        side is a getter that we want to update 
        '''
        expr = self.or_op() 
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Expr.Variable): # aka non-reserved IDENTIFIERS 
                name = expr.name 
                return Expr.Assign(name, value) 
            elif isinstance(expr, Expr.Get): 
                get = expr 
                return Expr.Set(get.object, get.name, value) 
            Lox.Lox.error(equals, "Invalid assignment target.") 
        return expr 

    def or_op(self):
        '''
        As is the pattern, we keep introducing lower-precedence expressions such 
        as "or" or "and" which will recursively descend into the expressions previously
        explained. 

        Here we descend our left-hand side with the "and_op()" and if there is an OR token,
        we can repeat ourselves with the right-hand side and bundle it up in a Logical Expression
        AST class 
        '''
        expr = self.and_op() 
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_op() 
            expr = Expr.Logical(expr, operator, right) 
        return expr 

    def and_op(self):
        '''
        We can continue descending into the full expression with "equality()" 
        for our left-hand operand and then repeat if there is an AND Token 
        '''
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right) 
        return expr 

    def equality(self):
        '''
        We call the comparison() rule first to define our left operand. After that's done, 
        which means it ended up in some type of "primitive" terminal, we can then check 
        if our tokens are "!=" or "==". We store that in our "operator" and, like the left
        operand, do the same recursion for the right operand. 
        We bundle these operands and the operator into an Expression syntax class and return
        '''
        expr = self.comparison()  
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous() 
            right = self.comparison() 
            expr = Expr.Binary(expr, operator, right) 
        return expr 
   
    def comparison(self):
        '''
        Similar process to "equality" with the left and right operands recursively descending 
        from "addition". 
        We bundle again into an Expression syntax class and return 
        '''
        expr = self.addition()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expr = Expr.Binary(expr, operator, right) 
        return expr 

    def addition(self):
        '''
        Similar process to "equality" with the left and right operands recursively descending
        from "addition".
        We bundle again into an Expression syntax class and return   
        '''
        expr = self.multiplication()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.multiplication()
            expr = Expr.Binary(expr, operator, right)
        return expr 

    def multiplication(self):
        '''
        Similar process to "equality" with the left and right operands recursively descending
        from "unary".
        We bundle again into an Expression syntax class and return   
        '''
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right) 
        return expr 

    def unary(self):
        ''' 
        Bit different from the above. Only acceptable unary expressions are "!" or "-".
        What's also interesting is that we can keep recursively exploring "unary" ad infinitum 
        so we could have expressions like "!!!!!!!!!True" 
        '''
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        return self.call() 

    def call(self):
        '''
        Function call -> when we see an identifier matching to a function 
        name as returned by "primary()" and match with an immediate "(" 
        then we know we're entering a function call.  

        Object getter -> if we see a "." followed by a property identifier
        then we're trying to access that property just like in Python. 
        '''
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.") 
                expr = Expr.Get(expr, name) 
            else:
                break 
        return expr 

    def finish_call(self, callee):
        '''
        Will create a Call Expression that will bundle up a 
        function/method callee with a ')' paren and token 
        arguments to be interpreted by the visit_Call method
        later 
        '''
        arguments = [] 
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments") 
                arguments.append(self.expression()) 
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.") 
        return Expr.Call(callee, paren, arguments) 

    def primary(self):
        '''
        We've reached the end with terminal conditions. This is how we stop the recursive descent
        Terminals include -> Bools, Null, Numbers, Strings, Parenthetical groups (which as expected
        have their nested expression start the whole process back up from the top. 
        '''
        if self.match(TokenType.THIS): return Expr.This(self.previous()) 
        if self.match(TokenType.FALSE): return Expr.Literal(False)
        if self.match(TokenType.TRUE): return Expr.Literal(True)
        if self.match(TokenType.NIL): return Expr.Literal(None) 
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal) 

        if self.match(TokenType.SUPER): 
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.") 
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name") 
            return Expr.Super(keyword, method) 

        if self.match(TokenType.IDENTIFIER): 
            return Expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")  ## need to find a match otherwise must record as error 
            return Expr.Grouping(expr) 
        self.error(self.peek(), "Expect expression")   ## indicates we reached a token that can't start an expr 

    # HELPER AND ERROR-RECOVERY FUNCTIONS  

    def advance(self):
        '''
        We usually advance in our token array when there are sucessful matches 
        in our production rules. 

        Note: This is used in "match()" and "consume()" so anytime we see those
        two including "advance()", we have to remember that we are progressing 
        forward in our tokens array 
        '''
        if not self.is_at_end():
            self.current += 1 
        return self.previous() 

    def match(self, *types):
        '''
        checks if there is a match between a stated Token type in a set of token
        types and where the "self.current" iterator is in our token array 
        '''
        for token_type in types:
            if self.check(token_type):
                self.advance() 
                return True 
        return False 

    def consume(self, token_type, message: str):
        '''
        Similar to "match()" as it checks for the one token to 
        see if we have a match and then advanced to the next one.
        A custom message is given here however
        '''
        if self.check(token_type): 
            return self.advance() 
        raise self.error(self.peek(), message)

    def check(self, token_type):
        '''
        returns boolean indicating that token type arg did match where we are
        in array 
        '''
        if self.is_at_end(): return False 
        return self.peek().token_type == token_type 

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current] 

    def previous(self):
        return self.tokens[self.current - 1] 

    def error(self, token, message):
        Lox.Lox.error(token, message)  
        raise ParseError

    def synchronize(self):
        ''' 
        After encountering an error, we discard the remaining tokens from the errorneous
        statement "area". We continue onwards until we find a new statement as indicated
        by keywords such as PRINT or FOR or until we reach a SEMICOLON which usually means 
        we finished our erroneous statement "area". We do this so we don't keep recording 
        more errors that all result from the original error--this info wouldn't be helpful
        for users and would make them panic
        ''' 
        self.advance()
        new_statement_beginnings = [
                TokenType.CLASS, 
                TokenType.FUN, 
                TokenType.VAR, 
                TokenType.FOR, 
                TokenType.IF, 
                TokenType.WHILE, 
                TokenType.PRINT, 
                TokenType.RETURN
        ]       
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON: 
                return 
            if self.peek().token_type in new_statement_beginnings:
                return 
            self.advance() 

class ParseError(Exception):
    pass 



