import tkinter
from tkinter import filedialog
from lexical_analyzer import tokenize_lolcode 
from LOLCODE_Token import LOLToken  

class LOLCodeParser:
    def __init__(self, tokens):
        self.tokens = tokens  # Tokens from the lexer
        self.current_token_index = 0  # Pointer to the current token
        self.variables = {}  # Dictionary to store variable values


    def get_current_token(self):
        """Get the current token."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def consume(self):
        """Consume the current token and move to the next one."""
        if self.current_token_index < len(self.tokens):
            self.current_token_index += 1

    def skip_non_essential_tokens(self):
        """Skip over comments and irrelevant tokens."""
        while self.get_current_token() is not None and self.get_current_token()[0] in ['SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT']:
            self.consume()

    def parse(self):
        """Start parsing the program."""
        self.skip_non_essential_tokens()  # Skip comments and irrelevant tokens
        program = self.program()
        return program

    def program(self):
        """Parse a LOLCODE program."""
        self.skip_non_essential_tokens()
        if self.get_current_token() and self.get_current_token()[0] == 'HAI':
            self.consume()  # Consume HAI
            self.statements()  # Parse all statements, including WAZZUP
            self.skip_non_essential_tokens()
            if self.get_current_token() and self.get_current_token()[0] == 'KTHXBYE':
                self.consume()  # Consume KTHXBYE
                return 'Program successfully parsed!'
            else:
                raise SyntaxError('Expected KTHXBYE at the end of the program')
        else:
            raise SyntaxError('Expected HAI at the beginning of the program')


    def statements(self):
        """Parse a sequence of statements."""
        while self.get_current_token() is not None and self.get_current_token()[0] not in ['KTHXBYE']:
            token = self.get_current_token()
            
            if token[0] in ['SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT']:
                self.consume()  # Skip comments
            
            elif token[0] == 'WAZZUP':
                self.consume()  # Consume the WAZZUP token
                self.parse_wazzup()
            
            elif token[0] == 'VISIBLE':
                self.consume()  # Consume the Visible token
                self.visible_statement()
            
            elif token[0] == 'GIMMEH':
                self.consume()
                self.gimmeh_statement()
            
            else:
                raise SyntaxError(f"Unexpected token: {token[0]}")
            

    def parse_wazzup(self):
        """Parse the WAZZUP section for variable declarations."""
        self.skip_non_essential_tokens()

        while self.get_current_token() and self.get_current_token()[0] == 'I_HAS_A':
            self.consume()  # Consume I_HAS_A
            self.variable_declaration()  # Handle variable declaration
            self.skip_non_essential_tokens()

        if self.get_current_token() and self.get_current_token()[0] == 'BUHBYE':
            self.consume()  # Consume BUHBYE token
        else:
            raise SyntaxError('Expected BUHBYE to close the WAZZUP section')


    def variable_declaration(self):
        """Handle the declaration of variables with expressions."""
        if self.get_current_token()[0] == 'VAR_ID':
            var_name = self.get_current_token()[1]  # Get variable name
            self.consume()  # Consume the variable identifier
            if self.get_current_token()[0] == 'ITZ':
                self.consume()
                expr_result = self.expression()  # Handle expression for initialization
                self.variables[var_name] = expr_result  # Store the variable value
                print(f"Variable {var_name} initialized to {expr_result}")
            else:
                self.variables[var_name] = 'NOOB'  # Declare without initialization
                print(f"Variable {var_name} declared but not initialized.")
        else:
            raise SyntaxError('Expected variable identifier')


    def expression(self):
        """Parse expressions (handles operations, literals, and variables)."""
        current_token = self.get_current_token()
        
        if current_token[0] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            return self.consume_literal()
        
        # Handle variable references
        elif current_token[0] == 'VAR_ID':
            # Treat variable identifiers as part of expressions
            var_name = current_token[1]
            self.consume()  # Consume the variable identifier
            # Return the value of the variable 
            if var_name in self.variables:  # dictionary of variable values
                return self.variables[var_name]
            else:
                return None
                # raise SyntaxError(f"Undefined variable {var_name}")
        
        elif current_token[0] == 'SUM_OF':
            return self.binary_operation('SUM_OF', '+')
        
        elif current_token[0] == 'DIFF_OF':
            return self.binary_operation('DIFF_OF', '-')
        
        elif current_token[0] == 'PRODUKT_OF':
            return self.binary_operation('PRODUKT_OF', '*')
        
        elif current_token[0] == 'QUOSHUNT_OF':
            return self.binary_operation('QUOSHUNT_OF', '/')
        
        elif current_token[0] == 'MOD_OF':
            return self.binary_operation('MOD_OF', '%')
        
        elif current_token[0] == 'BIGGR_OF':
            return self.binary_operation('BIGGR_OF', 'max')
        
        elif current_token[0] == 'SMALLR_OF':
            return self.binary_operation('SMALLR_OF', 'min')
        
        elif current_token[0] == 'NOT':
            return self.unary_operation('NOT')
        
        elif current_token[0] == 'SMOOSH':
            return self.smush_operation()
        
        # elif current_token[0] == 'VISIBLE':
        #     return self.visible_statement()
        
        else:
            raise SyntaxError(f"Invalid expression: {current_token}")


    def consume_literal(self):
        """Consume and return a literal value."""
        current_token = self.get_current_token()
        if current_token[0] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            value = current_token[1]
            self.consume()
            return value
        else:
            raise SyntaxError('Expected a literal value')


    def binary_operation(self, operation, operator):
        """Handle binary operations like SUM_OF, DIFF_OF, etc."""
        self.consume()  # Consume the operation token
        self.skip_non_essential_tokens()
        left_operand = self.expression()  # Left operand
        self.skip_non_essential_tokens()
        if self.get_current_token()[0] != 'AN':
            raise SyntaxError(f"Expected 'AN' after {operation}")
        self.consume()  # Consume AN
        right_operand = self.expression()  # Right operand
        
        # Perform operation based on the operator
        result = self.perform_operation(left_operand, right_operand, operator)
        print(f"Operation result: {left_operand} {operator} {right_operand} = {result}")
        return result


    def unary_operation(self, operation):
        """Handle unary operations like NOT."""
        self.consume()  # Consume the NOT token
        operand = self.expression()  # Operand for NOT
        print(f"NOT {operand}")
        return not operand


    def smush_operation(self):
        """Handle SMOOSH operation with infinite operands."""
        self.consume()  # Consume the SMOOSH token
        operands = []
        while self.get_current_token() and self.get_current_token()[0] != 'VISIBLE':
            operands.append(self.expression())  # Consume operands
            self.skip_non_essential_tokens()
        result = ''.join(str(operand) for operand in operands)
        print(f"SMOOSH result: {result}")
        return result


    def perform_operation(self, left_operand, right_operand, operator):
        """Perform the operation with correct typecasting."""
        if isinstance(left_operand, str) or isinstance(right_operand, str):
            # Typecast to NUMBR or NUMBAR depending on operands
            left_operand = float(left_operand) if '.' in str(left_operand) else int(left_operand)
            right_operand = float(right_operand) if '.' in str(right_operand) else int(right_operand)
        
        if operator == '+':
            return left_operand + right_operand
        elif operator == '-':
            return left_operand - right_operand
        elif operator == '*':
            return left_operand * right_operand
        elif operator == '/':
            return left_operand / right_operand
        elif operator == '%':
            return left_operand % right_operand
        elif operator == 'max':
            return max(left_operand, right_operand)
        elif operator == 'min':
            return min(left_operand, right_operand)
        else:
            raise SyntaxError(f"Unknown operator {operator}")


    def visible_statement(self):
        """Handle the VISIBLE statement (output to console)."""
        operands = []
        while self.get_current_token() and self.get_current_token()[0] not in ['KTHXBYE', 'BTW']:
            if self.get_current_token()[0] == 'VISIBLE':
                self.consume()  # Consume additional VISIBLE if it appears redundantly
            expr_result = self.expression()
            if expr_result is None:
                expr_result = "NOOB"  # Default value for uninitialized variables
            operands.append(str(expr_result))  # Cast expressions to string
            self.skip_non_essential_tokens()
        print("\n".join(operands))



    def gimmeh_statement(self):
        """Handle the GIMMEH statement (accept input)."""
        token = self.get_current_token()

        if token and token[0] == 'VAR_ID':  # Ensure the next token is a variable
            var_name = token[1]
            if self.is_valid_variable_name(var_name):
                self.consume()  # Consume the variable name token
                user_input = input("Input for {}: ".format(var_name))  # Get input from the user
                self.variables[var_name] = str(user_input)  # Store input as a YARN (string)
            else:
                raise SyntaxError(f"Invalid variable name for GIMMEH: {var_name}")
        else:
            raise SyntaxError('Expected a variable after GIMMEH')



def syntax_analysis(source_code):
    # Tokenize the source code
    tokens = tokenize_lolcode(source_code)
    # for token in tokens:
    #     print(token)
    parser = LOLCodeParser(tokens)
    try:
        return parser.parse()
    except SyntaxError as e:
        return f"Syntax Error: {str(e)}"
    

def open_file():
    """Open a file dialog to select a LOLCODE file and process it."""
    # Set up Tkinter file dialog
    root = tkinter.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("LOLCode Files", "*.lol")])
    if file_path:
        with open(file_path, 'r') as file:
            source_code = file.read()
        return source_code
    return None

source_code = open_file()
if source_code:
    print(syntax_analysis(source_code))
