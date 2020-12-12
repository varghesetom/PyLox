
'''
Laying out the enumerations for every type of Token that we can encounter. During lexical analysis, the scanner will match some program input that fits a certain criteria with an associated TokenType. For example, if the program input had a "*", the scanner would match that with TokenType.STAR. 

The RESERVED_KEYWORD_TOKENS comes into play when we're discerning whether some program input value is an identifier or not. An identifier is a name used to identify whether it is a variable, function, class, module, etc. If the scanner input is not a RESERVED_KEYWORD_TOKEN, then it must be an identifier. 
'''

import enum 
from enum import auto 


class EnumName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name 

class TokenType(EnumName):
    ## single-char tokens 
    LEFT_PAREN, RIGHT_PAREN = auto(), auto() 
    LEFT_BRACE, RIGHT_BRACE = auto(), auto() 
    COMMA = auto()
    DOT = auto() 
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto() 
    SLASH = auto()
    STAR = auto() 

    ## one or 2 char tokens 
    BANG, BANG_EQUAL = auto(), auto() 
    EQUAL, EQUAL_EQUAL = auto(), auto() 
    GREATER, GREATER_EQUAL = auto(), auto() 
    LESS, LESS_EQUAL = auto(), auto() 

    ## Literals 
    IDENTIFIER, STRING, NUMBER = auto(), auto(), auto() 

    ## keywords 
    AND = auto() 
    CLASS = auto() 
    ELSE = auto() 
    FALSE = auto() 
    FOR = auto() 
    FUN = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto() 
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto() 
    EOF = auto() 


RESERVED_KEYWORD_TOKENS = { 
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "False": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "None": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "True": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE
        }

