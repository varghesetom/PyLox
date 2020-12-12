## Pylox

A Python-based interpreter for the Lox language as devised by Bob Nystrom, a compiler engineer at Google, who wrote a book on language implementations: https://craftinginterpreters.com/. The first half of the book revolved around writing a tree-based interpreter in Java. The objective was to port this into Python from lexical analysis to implementing OOP concepts like classes and inheritance. For more background information, please see below. 

## Testing 

I used the same test suite he wrote for his Java-based interpreter, "jlox", and modified it for Python. To run the test suite located in "test", run the "test_runner.py". An output file, "out", will be generated as well to highlight the test results. Pylox currently passes 235 tests. 

## Usage 

Written in Python 3.8 for MacOS. The best way to use the program is to write a Lox program and call ```python Lox.py [LOX_PROGRAM]```. If you want to run some sample Lox programs and see how they're written, substitue [LOX_PROGRAM] with any of the tests located in "test/". For more details on Lox, please consult his book "Crafting Interpreters".

## Background 

### ***SCANNER*** 
The responsibility for the Scanner is to perform accurate lexical analysis. The end goal is to scan through our program input, whether it be from REPL or a file,and translate the encountered lexemes into tokens. Lexemes are grouping of characters that together reflect some meaning in a language.

E.g. A common lexeme in many programming languages is "<" which means 'less than'. Lexical analysis detects this character and recognizes this actually can translate to a "<" token which will hold that character info as well as what kind of token (LESS).

Another example of a lexeme would be "for" which means the start of a loop in many languages. This would be wrapped up in a Token class and its type would be a keyword token. A keyword token is when certain words, or "lexemes", hold special meaning and can only mean one meaning in the programming language. Unlike, say, a "Bob" lexeme that can represent a variable that holds an assignment, "for" can never be used for variable assignment. But before we get to that step of figuring out how tokens all work together, lexical analysis first categorizes each lexeme into a token.

### ***PARSER*** 

The job of a parser is to translate tokens -> syntax classs. To do this, we need
1. Grammar - a set of grammar rules to follow--more specifically, a Context-Free grammar. Most popular is
some flavor Backus-Naur Form representation of Context-Free Grammar where we follow "name ::= expansion"
where "::=" means 'can be substituted for'.

E.g if we have a grammar rule such as "lunch ::= sandwich | pizza | salad", we can substitute the expression "lunch" with either "sandwich", "pizza", or "salad" and it would be considered valid. A Context-Free Grammar will have many of these rules which can be recursively broken down further until we reach an end expression (aka "terminal"). Going with the same example as above, we could have a rule called 'sandwich ::= "pastrami" | "turkey"'

2. Methodology - In the book, we use a Recursive Descent Parser to rip through our code from the top-down. Defining
what "top-down" is somewhat subtle. It means we go down in terms of precedence.

E.g We can recursively solve for an addition problem. We have "+" operator along with 2 operands and an "addition" production rule that needs two operands for addition to take place. Both operands themselves call the "multiplication" production rule. So each operand must continue and call the "unary" production rule to find out if there is a "!=" unary operator or calls the "primary" production rule. This is our final expression rule to check if our operand is a boolean, number, string, parentheses, etc. The reason we went from addition -> multiplication -> unary (really just "!=") -> primary is because in our basic mathematics we generally follow PEMDAS (Parentheses -> Exponents -> Mult/Div -> Add/Sub) so we have to find out if our operands are really themselves multiplication operands (e.g. (2 * 3) + (4 * 6) means both operands are binary multiplication expressions that boil down to 4 number primitives BEFORE we add the products together)

### ***INTERPRETER***

To tackle the actual interpretation of our ASTs we use a combination of metaprogramming and the Visitor pattern to go through each expression and statement in order to evaluate their true meaning. We pass in the entire Parser-constructed AST, represented by an array of statements, to the Interpreter which will visit each AST subclass (each "array statement" is a mini syntax tree where the nodes are the various tokens) and utilize "Expr.py" and "Stmt.py" to figure out which visitor method to implement. These two Python files are generated metaprogrammatically from "GenerateAST.py" to save time explicitly writing out each type of Expression and Statement node. For more details on the Visitor implementation, pelase see below. 

#### Start-to-End Example 
Let's go through a complete example from start to finish. If we have a simple 1-line program like "print 1+3;", lexical analysis will translate each lexeme into a token. The tokens would be PRINT,  NUMBER (1),  PLUS,  NUMBER (3), SEMICOLON, EOF. Next, during the Parser phase, the Parser will see a PRINT token and determine that it needs to start wrapping up the successive tokens into a meaningful AST. But before it starts to wrap up everything into a Print Statement (Stmt.Print), it first tries to evaluate the expression, 1 + 3. 

This is where we can see how Recursive Descent Parsing shines. It "descends" downwards from the lowest-level precedence expression, an "assignment" expression, past "or" expression, "and" expression, and so on until it reaches the terminating expression, "primary". Here it tries to match the first token, a NUMBER (1), and returns this Expression Literal successfully ("Expr.Literal"). It returns back to the previous function call, which was a "call" expression, but can't match the next token, a PLUS, and so returns the Expression Literal back to the next function call...until finally it reaches the "addition" expression and can match the PLUS token with the conditional. The recursive descent begins again from there to match the next token, NUMBER, and finally wraps it all up in a Binary Expression (Expr.Binary). Note, this Binary Expression itself has subexpressions (an Expr.Literal = 1, Expr.Literal = 3). 

Now, we can continue checking if we have a correct print statement. In Lox, every statement needs to terminate with a semicolon. Until then, it'll consume all the tokens, ignoring whatever they may be. Finally, as mentioned earlier, it wraps up all this work into a Print Stmt. We can see how involved Recursive Descent can get even with a simple 1-line of code, but we finally have a correct AST for the Interpreter! 

This AST is passed along to the Interpreter, a Visitor class that first sees a Stmt.Print, which tells it indirectly to call "visit_Print_Statment()" and so evaluate the expression it's currently holding, the Binary Expression we wrapped it with. This Binary expression indirectly tells the Interpreter to call "visit_Binary()". This tells the Intepreter to evaluate the left and right subexpressions, through "visit_Literal()" and end up with two directly evaluated values, 1 and 3. Returning to the "visit_Binary()" function, it evaluates that the wrapped operator is a PLUS and can now evaluate 1 + 3 = 4. We can finally return this value to "visit_Print_Statement()" which prints it to stdout. And we're done! 

For more details, please see the code files especially for the Parser. The functions are written top-down making it easier to see the "descent". 

#### Visitor Pattern
Every concrete class of Expr and Stmt will have an "accept" method that will take a Visitor (could be either Interpreter.py or ASTPrinter.py. The latter is only used to print out the expressions correctly.). The Visitor will need to have all the "visit" methods to match up with each concrete class (e.g. if Literal calls its accept method, it'll call the passed in visitor as such, "visitor.visit_Literal(self") where the Literal Expr class is again passed as an argument to the visitor as well!). As the visitor calls its specially-designed visit method, it'll call the fields of the concrete Expr class (e.g. keeping with the same Literal example, the ASTPrinter will return
"str(expr.value)" where "expr" is the Literal).
