
'''
Token class that will hold each encountered lexeme, its associated token type (e.g. TokenType.PLUS), the line number in the file where it was found as well as the actual literal value.

Note that the "literal" argument in most cases when we're creating Tokens will be empty. The only times we will care about the "literal" argument is when we need to extract the actual numeric or string value of our lexeme 
'''

class Token:
    def __init__(self, token_type, lexeme: str, line : int, literal=""):
        self.token_type = token_type 
        self.lexeme = lexeme 
        self.line = line 
        self.literal = literal 

    def __str__(self):
        return str(self.token_type.name + " " + self.lexeme + " " + str(self.literal))

