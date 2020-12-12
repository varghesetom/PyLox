#!/usr/bin/env python 

'''

We import the Token class, which we will use to bundle up our lexemes, and the TokenType which will be used as part of the Token class to identify one Token from another. 

The process boils down to going through our "source" and matching lexemes with Token cases. This is reflected in the method "_scan_tokens" where it logically sieves through the cases to find the appropriate Token match. More information on the cases is provided below for the method. 

These cases are (in order): 
    1. lexical chars -> characters that have an easy 1:1 correspondence in our Lox language. For instance, a left parentheses, '(', is the same in Python and Lox.
    2. comparisons -> cases where we have comparison operators such as '<!' or '==' 
    3. comment -> Okay, if it isn't in the predefined dictionary of chars, then is it a comment? If it's a comment we have to ignore all lexemes on the line. 
    4. newline -> check if we need to update our self.line 
    5. string -> check if we have a string in our ends. Similar to the comment case, we have to check if there is an opening string and we would have to ignore all the lexemes we find until the end 
    6. number -> if it's not in a comment or a string, then we can add a number literal 
    7. identifiers -> if not in a comment or a string and not a keyword, then we add whatever this may be as an identifier. 
'''

import sys 
sys.path.insert(0, "../")
import Token 
from TokenType import TokenType, RESERVED_KEYWORD_TOKENS
import Lox

class Scanner:

    def __init__(self, source: str):
        '''
        Initialize our scanner with a source input. This will be provided by "Lox.py" as either a REPL session
        or a program file. We store all tokens that we find into our array. The first scanner case ("lexical chars") 
        will be easier to use with a dictionary so that is also initialized here. 
        '''
        self.source = source 
        self.tokens = [] 
        self.start = 0    ## first char in the self.current lexeme we're currently considering 
        self.current = 0  ## where we are currently in lexeme 
        self.line = 1 

        self.lexChars = {
            '(' : TokenType.LEFT_PAREN,
            ')' : TokenType.RIGHT_PAREN,
            '{' : TokenType.LEFT_BRACE,
            '}' : TokenType.RIGHT_BRACE,
            ',' : TokenType.COMMA,
            '.' : TokenType.DOT,
            '-' : TokenType.MINUS, 
            '+' : TokenType.PLUS,
            ';' : TokenType.SEMICOLON,
            '*' : TokenType.STAR,
            ' ' : 0,
            '\r' : 0, 
            '\t' : 0,
            }

    def scan_tokens(self):
        '''
        While our self.current, the iterator, has not reached the end, keep scanning and adding tokens 
        At the end of our source input, we will add an EOF token 
        '''
        while not self.is_at_end():
            self.start = self.current 
            self._scan_token() 
        self.tokens.append(Token.Token(TokenType.EOF, "", self.line)) 
        return self.tokens 

    def is_at_end(self):
        '''
        Helper function to determine whether we reached end of input 
        '''
        return self.current >= len(self.source) 

    def _scan_token(self):
        '''
        Coordinator to match a character input from source to a lexical case 
        as mentioned in the header above 
        '''
        c = self.advance() 
        if c in self.lexChars:              
            if self.lexChars[c]:
                self.add_token(self.lexChars[c])
        elif c in ["!", "=", "<", ">"]:     
            self.comparison(c)
        elif c == '/':
            self.comment_case()            
        elif c == '\n':
            self.add_line()               
        elif c == '"':
            self.string()                
        elif self.is_digit(c):  
            self.number()               
        else:               
            self.identifier() 

    def advance(self):
        '''
        Helper function to advance our self.current iterator and returns
        the value one place BEFORE the new self.current index 
        '''
        self.current += 1 
        return self.source[self.current - 1]

    def add_token(self, token_type, literal = ""):
        '''
        What the other functions will call to add a token 
        '''
        self._add_token(token_type, literal)

    def _add_token(self, token_type, literal = ""): 
        '''
        The Token class takes 4 arguments in order to initialize: 
            i. type of token 
            ii. lexeme 
            iii. line number 
            iv. literal value 
        When we're adding a Token, we pass in our "token_type" and "literal"
        arguments. The "lexeme" argument is defined the area from where the 
        lexeme began (The function "scan_token" updates  "self.start" to where 
        the "self.current" lies after processing a lexical case from "_scan_token") 
        and where the "self.current" is.

        Should only be called the "add_token" method. 
        '''
        try:
            text = self.source[self.start:self.current]
            self.tokens.append(Token.Token(token_type, text, self.line, literal))
        except KeyError:
            Lox.Lox.error(self.line, "Unexpected character") 

    def match(self, expected: str):
        '''
        checks if there is a match at the "self.current" index when we encounter a char
        at "self.current - 1" that could match to make a token type 
        '''
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False 
        self.current += 1 
        return True 

    def add_line(self):
        '''
        Helper method to update whenever we encounter a newline lexical case 
        '''
        self.line += 1 

    def peek(self):
        '''
        Helper method to check the value where "self.current" is without advancing it
        '''
        if self.is_at_end(): return '\0' 
        return self.source[self.current] 

    def peekNext(self): 
        '''
        helper function for "number" function. Checks ahead 1 character to see 
        if reached end or space. 
        Used for the fractional number cases 
        '''
        if self.current + 1 >= len(self.source): 
            return '\0' 
        return self.source[self.current + 1] 

    def is_digit(self, c):
        '''
        Helper method to check if the char is an actual number or not 
        '''
        try:
            int(c)
            return True 
        except ValueError:
            return False 

    '''
    The rest of the lexical cases mentioned in header (2 through 7) 
    '''
    def comparison(self, c):
        ''' 
        comparison cases will need to be matched depending if there is a 
        second comparison operator or not.
        E.g. if we see a "!" that could mean the unary operator or the 
        "not equal to" sign
        '''
        if c == "!": 
            self.add_token(TokenType.BANG_EQUAL) if self.match("=") else self.add_token(TokenType.BANG)
        elif c == "=":
            self.add_token(TokenType.EQUAL_EQUAL) if self.match("=") else self.add_token(TokenType.EQUAL)
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL) if self.match("=") else self.add_token(TokenType.LESS) 
        else:
            self.add_token(TokenType.GREATER_EQUAL) if self.match("=") else self.add_token(TokenType.GREATER) 

    def comment_case(self):
        '''
        Basic comment case -- when we encounter a '/' we have to ignore everything until we reach a newline 
        '''
        if self.match('/'):
            while self.peek() != '\n' and not self.is_at_end():   # we don't care about lexeme matching what comes after   
                self.advance()
        else:
            self.add_token(TokenType.SLASH)

    def string(self):
        '''
        String case is similar to the comment case -- we don't care about lexeme matching anything
        that comes in between. Once
        '''
        while self.peek() != '"' and not self.is_at_end():  
            if self.peek() == '\n':                         ## handling multi-self.line strings 
                self.line += 1 
            self.advance() 
        if self.is_at_end():                                ## error -> unterminated string 
            print(f"self.source is {self.source}")
            Lox.Lox.error(self.line, "Unterminated string.") 
            return 
        self.advance()                                      ## the closing ' 
        value = self.source[self.start+1:self.current-1]    ## trim surrounding quotes (self.current was moved up a spot bc of advance and self.start[0] was the first ")  
        self.add_token(TokenType.STRING, value)  

    def number(self):
        '''
        Adding numbers as Tokens 
        '''
        while self.is_digit(self.peek()):                   ## keep iterating through all numerical input 
            self.advance() 
        if self.peek() == '.' and self.is_digit(self.peekNext()):          ## fractional case  
            self.advance() 
            while self.is_digit(self.peek()):
                self.advance() 
            self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current])) 
        else:
            self.add_token(TokenType.NUMBER, int(self.source[self.start:self.current])) 

    def identifier(self):
        '''
        The final lexical case. If none of the above cases were found, then our lexeme 
        must be either a reserved keyword or a user-defined identifier 
        '''
        while self.peek().isdigit() or self.peek().isalpha() or self.peek() == '_':
            self.advance() 
        text = self.source[self.start:self.current]
        token_type = RESERVED_KEYWORD_TOKENS.get(text, TokenType.IDENTIFIER)     ## if it isn't a reserved keyword, then we declare it as an identifier 
        self.add_token(token_type) 


    
