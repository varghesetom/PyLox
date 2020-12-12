
'''
There is a separation of concerns by moving the function call into a separate file instead of 
having it with the rest of the front-end code with Interpreter.py. 

LoxCallable -> an interface making sure our native functions and function objects implement 
a call method and an arity method to check if # of parameters match # of arguments. 

NativeClock -> an example of a native, or built-in, function that the user can use in Lox. 
Native functions are written in the implementation language (Pyton) and are used in the target
language itself (Lox). This is a simple native function to calculate time elapsed. 

LoxFunction -> The real gist behind intepreting a Function AST class. In our Interpreter file,
we wrap the environment and overall stmt given in the Stmt.Function_Statement AST class into an
instance of LoxFunction within the "visit_Function_Statement" function. The same function also 
defines it in the current environment so when we see it later being called, we can use LoxFunction
class method "call()" to represent a function call. 

'''

from abc import ABC, abstractmethod 
import time 
from Environment import Environment 

class LoxCallable(ABC):
    
    @abstractmethod
    def call(self, interpreter, arguments):
        pass 

    @abstractmethod 
    def arity(self): 
        pass 

class NativeClock(LoxCallable):

    def arity(self):
        return 0 

    def call(self, interpreter, arguments):
        return time.perf_counter() / 1000 

    def __repr__(self):
        return "<native fn>"

class LoxFunction(LoxCallable): 

    def __init__(self, closure, declaration, is_initializer):
        '''
        Args 
            Closure -> is the enclosing environment.
            In most cases, this will be the self.globals
            from the Interpreter instance. But if we have
            nested functions, the enclosing environment will
            be the outer function's environment. 

            Declaration -> The Stmt.Function_Statement itself
            with its name, parameters, and body. 
        '''
        self.closure = closure    
        self.declaration = declaration 
        self.is_initializer = is_initializer 

    def call(self, interpreter, arguments):
        '''
        Each function call gets its own environment instance.
        This is how we can enable recursion with multiple call
        stacks. And no matter how deep we go into a recursion or
        a general nested function, we have to get out somehow so
        when we encounter a Return runtime exception we return that
        exception's return value 
        '''
        environment = Environment(self.closure)  ## self.closure is the enclosing environment for this new instance
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try: 
            interpreter.execute_block(self.declaration.body, environment) 
        except Return as r:
            if self.is_initializer: return self.closure.get_at(0, "this") 
            return r.value 
        if self.is_initializer: return self.closure.get_at(0, "this") 
    
    def bind(self, instance):
        env = Environment(self.closure) 
        env.define("this", instance) 
        return LoxFunction(env, self.declaration, self.is_initializer)  

    def arity(self):
        return len(self.declaration.params) 

    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>" 

    def __call__(self):
        '''
        Must be callable otherwise check for callability in Interpreter's
        "visit_Call" will fail. 
        '''
        pass 

class LoxClass(LoxCallable):

    def __init__(self, name: str, superclass, methods: dict):
        self.name = name 
        self.superclass = superclass 
        self.methods = methods 

    def find_method(self, name: str):
        '''
        We try to first find a class method within the class itself. 
        If it's not possible and we're a subclass, then we can try
        looking for it in the superclass as well (inheritance) 
        '''
        if name in self.methods:
            return self.methods.get(name) 
        if self.superclass:
            return self.superclass.find_method(name) 
        return 

    def call(self, interpreter, arguments: list):
        instance = LoxInstance(self) 
        initializer = self.find_method("init") 
        if initializer:
            initializer.bind(instance).call(interpreter, arguments) 
        return instance 

    def arity(self):
        initializer = self.find_method("init")
        if not initializer: return 0 
        return initializer.arity() 

    def __call__(self):
        pass 

    def __repr__(self):
        return self.name

class LoxInstance:
    '''
    Will store our Class's fields/attributes. We will 
    also call the LoxClass's methods here even though they're
    stored in the Class itself 
    '''
    def __init__(self, klass: LoxClass):
        self.klass = klass 
        self.fields = {} 

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme] 
        method = self.klass.find_method(name.lexeme) 
        if method:
            return method.bind(self) 
        message = "\"Undefined property '" + name.lexeme + "'.\"" 
        raise RuntimeError(name, message)

    def set(self, name, value):
        self.fields[name.lexeme] = value 

    def __repr__(self):
        return f"{self.klass.name} instance" 

class Return(RuntimeError):
    
    def __init__(self, value):
        self.value = value 

if __name__ == "__main__":
    d = {} 
    d[1] = NativeClock() 
    print(d[1].call("interp", [])) 
    n = NativeClock()
    print(n)
