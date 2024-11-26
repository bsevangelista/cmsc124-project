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
    
    def peek_next_token(self):
        """Returns the next token without consuming it, or None if at the end."""
        if self.current_token_index + 1 < len(self.tokens):
            return self.tokens[self.current_token_index + 1]
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
            # print('entered statements')
            
            if token[0] in ['SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT']:
                self.consume()  # Skip comments         
            elif token[0] == 'WAZZUP':
                # print('entered wazzup')
                self.consume()
                self.parse_wazzup()   
            elif token[0] == 'VISIBLE':
                self.visible_statement()      
            elif token[0] == 'GIMMEH':
                # print('entered gimmeh')
                self.consume()
                self.gimmeh_statement()       
            elif token[0] == 'VAR_ID':
                self.assignment_statement()       
            else:
                raise SyntaxError(f"Unexpected token: {token}")
            
            self.skip_non_essential_tokens()


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
    
    def assignment_statement(self):
        """Handle variable assignments."""
        if self.get_current_token()[0] == 'VAR_ID':
            var_name = self.get_current_token()[1]
            self.consume()  # Consume the variable identifier
            # print(self.get_current_token())

            if self.get_current_token()[0] == 'R':
                # print('matched R')
                self.consume()  # Consume the R token
                value = self.expression()  # Parse the expression
                self.variables[var_name] = value  # Assign value to variable
                # print(f"Assigned {value} to {var_name}")

            elif self.get_current_token()[0] == 'IS_NOW_A':
                # print('matched IS_NOW_A')
                self.consume()  # Consume 'IS_NOW_A'
                target_type = self.get_current_token()
                if target_type[0] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'TYPE']:
                    self.consume()  # Consume the type
                    if var_name in self.variables:
                        self.variables[var_name] = self.cast_value(self.variables[var_name], target_type[1])
                        # print(f"Variable {var_name} recast to {target_type[1]}")
                    else:
                        raise SyntaxError(f"Undefined variable: {var_name}")
                else:
                    raise SyntaxError(f"Invalid type: {target_type}")
            else:
                raise SyntaxError("Expected 'R' in assignment statement")
        else:
            raise SyntaxError("Expected a variable identifier in assignment")
        
            
    def cast_value(self, value, target_type):
        """Helper function to cast a value to a target type."""
        try:
            if target_type == 'NUMBR':
                return int(value)
            elif target_type == 'NUMBAR':
                return float(value)
            elif target_type == 'YARN':
                return str(value)
            elif target_type == 'TROOF':
                return bool(value) if value not in ['NOOB', None, '', 0, 0.0] else False
        except ValueError:
            raise SyntaxError(f"Cannot cast {value} to {target_type}")


    def expression(self):
        """Parse expressions (handles operations, literals, and variables)."""
        current_token = self.get_current_token()
        # print('entered expressions')

        if current_token is None:
            raise SyntaxError("Unexpected end of input in expression")
        
        # Handle literals
        if current_token[0] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            return self.consume_literal()
        
        # Handle variable references
        elif current_token[0] == 'VAR_ID':
            var_name = current_token[1]
            self.consume()  # Consume the variable identifier
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                raise SyntaxError(f"Undefined variable: {var_name}")
        
        # Handle arithmetic and logical operations
        elif current_token[0] in ['SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF',
                                'MOD_OF', 'BIGGR_OF', 'SMALLR_OF']:
            return self.binary_operation(current_token[0], self.operator_map(current_token[0]))
        
        # Handle unary operations
        elif current_token[0] == 'NOT':
            return self.unary_operation('NOT')
        
        # Handle SMOOSH
        elif current_token[0] == 'SMOOSH':
            return self.smush_operation()
        
        # Handle MAEK
        elif current_token[0] == 'MAEK':
            return self.maek_expression()
        
        elif current_token[0] == 'BOTH_SAEM':
            return self.comparison_operation('BOTH_SAEM')
        
        elif current_token[0] == 'DIFFRINT':
            return self.comparison_operation('DIFFRINT')
        
        # Return None for non-expression tokens
        return SyntaxError(f"Invalid expression: {current_token}")
    
    def comparison_operation(self, operation):
        """Handle comparison operations."""
        self.consume()  # Consume the comparison token (e.g., BOTH_SAEM or DIFFRINT)
        self.skip_non_essential_tokens()
        
        # Parse the first operand
        left_operand = self.expression()
        self.skip_non_essential_tokens()
        
        # Expect and consume 'AN'
        if self.get_current_token()[0] != 'AN':
            raise SyntaxError(f"Expected 'AN' after {operation}")
        self.consume()  # Consume AN
        
        # Parse the second operand
        right_operand = self.expression()
        
        # Perform the comparison
        if operation == 'BOTH_SAEM':
            return left_operand == right_operand
        elif operation == 'DIFFRINT':
            return left_operand != right_operand
        else:
            raise SyntaxError(f"Unknown comparison operation: {operation}")
    
    def maek_expression(self):
        """Handle MAEK typecasting for expressions."""
        self.consume()  # Consume the 'MAEK' token
        expr_result = self.expression()  # Parse the expression
        
        if self.get_current_token() and self.get_current_token()[0] == 'A':
            self.consume()  # Consume the 'A' token

        if self.get_current_token() and self.get_current_token()[0] in ['TROOF', 'NUMBR', 'NUMBAR', 'YARN', 'TYPE']:
            target_type = self.get_current_token()[1]
            self.consume()  # Consume the type token
            
            # Typecast and return result to IT (not modifying the variable itself)
            return self.cast_value(expr_result, target_type)

    def operator_map(self, operation):
        """Map LOLCODE operations to Python operators."""
        return {
            'SUM_OF': '+',
            'DIFF_OF': '-',
            'PRODUKT_OF': '*',
            'QUOSHUNT_OF': '/',
            'MOD_OF': '%',
            'BIGGR_OF': 'max',
            'SMALLR_OF': 'min',
        }.get(operation, None)


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
        # print(f"Operation result: {left_operand} {operator} {right_operand} = {result}")
        return result

    def unary_operation(self, operation):
        """Handle unary operations like NOT."""
        self.consume()  # Consume the NOT token
        operand = self.expression()  # Operand for NOT
        # print(f"NOT {operand}")
        return not operand

    def smush_operation(self):
        """Handle SMOOSH operation with infinite operands."""
        if self.get_current_token() and self.get_current_token()[0] == 'SMOOSH':
            # print("matched smoosh")
            self.consume()  # Consume the 'SMOOSH' token

        operands = []

        while self.get_current_token():
            # print('entered smoosh')
            current_token = self.get_current_token()
            # print(f"Processing token: {current_token}")

            # Break the loop if the next token is not 'AN'
            next_token = self.peek_next_token()
            if current_token[0] == 'AN':
                self.consume()
            
            # Skip 'AN' tokens
            elif next_token is None or next_token[0] != 'AN':
                result = ''.join(str(operand) for operand in operands)
                # print(f"SMOOSH result: {result}")
                return result
            
            # Parse the operand
            operand = self.expression() 
            if operand is not None:
                operands.append(operand)
            else:
                raise SyntaxError("Invalid operand in SMOOSH operation")

            self.skip_non_essential_tokens()

        # Concatenate operands into a single string
        result = ''.join(str(operand) for operand in operands)
        # print(f"SMOOSH result: {result}")
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
        # print('entered visible statement')
        """Handle the VISIBLE statement with infinite arity or a single expression."""
        if self.get_current_token() and self.get_current_token()[0] == 'VISIBLE':
            self.consume()  # Consume the 'VISIBLE' token

        result = []  # Store the results of all operands

        # Continue parsing additional operands
        while self.get_current_token():
            expr_result = self.expression()
            # Handle invalid expressions
            if expr_result is None:
                result.append("NOOB")  # Default to "NOOB" for uninitialized variables
            else:
                # Remove quotation marks if the result is a string (YARN)
                if isinstance(expr_result, str) and (expr_result.startswith('"') and expr_result.endswith('"')):
                    result.append(expr_result[1:-1])  # Strip the quotes
                else:
                    result.append(str(expr_result))  # Convert to string for other types

            # print('entered visible')
            token = self.get_current_token()
            # print(f"Processing token: {token}")

            # Handle 'AN'
            if token[0] in ['AN', '+']:
                # print('matched AN')
                self.consume()  # Consume the 'AN' token
                self.skip_non_essential_tokens()  # Skip any non-essential tokens like whitespace

                # Look ahead to check if there is a valid expression or operator
                next_token = self.peek_next_token()
                if next_token is None or next_token[0] in ['SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF', 'MOD_OF', 'BIGGR_OF', 'SMALLR_OF']:
                    continue  # If the next token is an operator, continue without breaking
            else:
                break

        # Concatenate all results with a '+' separator for the final output
        final_result = '+'.join(result)
        print(final_result) 

    def gimmeh_statement(self):
        """Handle the GIMMEH statement (accept input)."""
        token = self.get_current_token()

        if token and token[0] == 'VAR_ID':  # Ensure the next token is a variable
            var_name = token[1]
            self.consume()  # Consume the variable name token
            user_input = input("Input for {}: ".format(var_name))  # Get input from the user
            self.variables[var_name] = str(user_input)  # Store input as a YARN (string)
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
