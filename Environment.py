#!/usr/bin/env python

'''
The Environment is necessary for lexical scoping. The book touches upon the difference between lexical and dynamic scoping with the latter being extremely rare in practice because of its need to be executed at runtime to pinpoint exactly what each variable will be. Lexical scoping is preferred because you can see from the written code what each variable will be in different scopes. 
To introduce that with Lox, we will have an overall global environment. But if we introduce Statement blocks, we are now creating a sub-area where the variables defined here (even possibly defined with the same name as the enclosing environment) will have their values exist only here. 

We implement that notion with an instance of Environment() representing an overall environment with a "values" dictionary which will track our variables and their associated values. If the user tries accessing an identifier that doesn't exist in the current Environment, we can look at its "enclosing" environment--and so on and so forth. 
'''
import sys 
sys.path.insert(0, "scanner/")
from Token import Token 
import Lox 

class Environment:

    def __init__(self, enclosing=None):
        '''
        Create a new instance of an Environemnt. If we pass in an argument, then
        it would be the enclosing environment. 

        E.g. we could have an overall global environment with 
        "global = Environment()" and then a for-loop would have a new environment
        called "for_loop = Environment(global)" so it can still access variables 
        defined in the "global" environment 
        '''
        self.values = {} 
        assert (type(enclosing) == Environment or enclosing == None), "enclosing init arg must be of type Environment or NoneType" 
        self.enclosing = enclosing 

    def define(self, name, value):
        '''
        Args: name -> can be either a Token (lexeme) or a String. 
        Most of the time it'll be a token that will need 
        to be defined in the environment. But one string
        argument could be the "clock" native function 
        '''
        self.values[name] = value   

    def get(self, name):  
        '''
        Arg -> Name is of Token Type. 
        If token's lexeme exists in environment, retrieve associated value 
        otherwise look into its enclosing environments 
        '''
        if name.lexeme in self.values:
            return self.values[name.lexeme] 
        if self.enclosing:
            return self.enclosing.get(name) 
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.") 

    def assign(self, name, value):
        '''
        Similar to above except this time we are reassigning a new
        value to a previously defined variable 
        '''
        if name.lexeme in self.values:
            self.values[name.lexeme] = value 
            return 
        if self.enclosing:   ## if we can't find the variable to assign to, we try going to the enclosing one
            self.enclosing.assign(name, value) 
            return
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.") 

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values[name]

    def ancestor(self, distance):
        '''
        Returns an ancestral environment where our variable
        was defined. 
        '''
        environment = self 
        for i in range(distance):
            environment = environment.enclosing 
        return environment 

    def assign_at(self, distance: int, name: Token, value):
        self.ancestor(distance).values[name.lexeme] = value 
