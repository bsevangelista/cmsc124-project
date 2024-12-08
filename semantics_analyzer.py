import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import re
import sys
import copy
from io import StringIO

# Import the existing syntax analyzer components
from test import LOLCODESyntaxAnalyzer, NodeType, ASTNode, SymbolTable
from lexical_analyzer import tokenize_lolcode
from token_classification import LEXEME_CLASSIFICATIONS

class ASTInterpreter:
    def __init__(self, ast: ASTNode, symbol_table: SymbolTable, master = None):
        self.ast = ast
        self.symbol_table = symbol_table
        self.master = master

    def evaluate_node(self, node: ASTNode):
        """Recursively evaluate an AST node."""
        if node.node_type == NodeType.LITERAL:
            if isinstance(node.value, str):
                node.value = node.value.replace('"', '')
                try:
                    if '.' in node.value:
                        return float(node.value)
                    else:
                        return int(node.value)
                except:
                    return node.value  # Return as string if conversion fails
        elif node.node_type == NodeType.EXPRESSION:
            if node.children:
                return self.evaluate_node(node.children[0])  # Evaluate the child node
            elif node.children == []: # Handle explicit variable
                var_details = self.symbol_table.variables.get(node.value)
                if var_details:
                    return var_details['value']
                else:
                    raise ValueError(f"Variable '{node.value}' not defined.")
            else:
                raise IndexError(f"Expression {node} {node.children} has no children.")
        elif node.node_type == NodeType.COMPARISON:
            if len(node.children) < 2:
                raise IndexError(f"Operation node '{node.value}' requires at least 2 operands.")
            # Handle specific operations
            values = [self.evaluate_node(child) for child in node.children]

            if None in values:
                raise ValueError(f"Operation '{node.value}' has NoneType operand(s): {values}")
            
            if any(isinstance(value, str) and (value == 'WIN' or value == 'FAIL') for value in values):
                for i in range(len(values)):
                    if values[i] == 'WIN':
                        values[i] = 1
                    elif values[i] == 'FAIL':
                        values[i] = 0
            
            operation = node.value

            if operation == "EQ":
                if len(node.children) != 2:
                    raise ValueError("EQ operation must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if left == right:
                    return 'WIN'
                else:
                    return 'FAIL'
                
            if operation == "NEQ":
                if len(node.children) != 2:
                    raise ValueError("NEQ operation must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if left != right:
                    return 'WIN'
                else:
                    return 'FAIL'

        elif node.node_type == NodeType.BOOLEAN_OPERATION:
            if not node.children:
                raise ValueError("BOOLEAN_OPERATION must have at least one child.")

            operation = node.value  # Extract boolean operation type

            if operation == "AND":
                if len(node.children) != 2:
                    raise ValueError("AND must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if left == 'WIN' and right == 'WIN':
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "OR":
                if len(node.children) != 2:
                    raise ValueError("OR must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if left == 'WIN' or right == 'WIN':
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "XOR":
                if len(node.children) != 2:
                    raise ValueError("XOR must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if left != right:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "NOT":
                if len(node.children) != 1:
                    raise ValueError("NOT must have exactly one operand.")
                operand = self.evaluate_node(node.children[0])
                if operand == 'WIN':
                    return 'FAIL'
                else:
                    return 'WIN'

            elif operation == "ALL":
                if all(self.evaluate_node(child) == 'WIN' for child in node.children):
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "ANY":
                if any(self.evaluate_node(child) == 'WIN' for child in node.children):
                    return 'WIN'
                else:
                    return 'FAIL'

            else:
                raise ValueError(f"Unknown boolean operation: {operation}")

            
        elif node.node_type == NodeType.UNARY_OP:
            if not node.children or len(node.children) != 1:
                raise ValueError("Unary operation must have exactly one child node.")

            operand_node = node.children[0]
            
            if node.value == "NOT":
                operand_result = self.evaluate_node(operand_node)
                if operand_result == "FAIL":
                    return "WIN" 
                else:
                    return "FAIL"

            else:
                raise ValueError(f"Unknown unary operation: {node.value}")

        elif node.node_type == NodeType.OPERATION:
            if len(node.children) < 2:
                raise IndexError(f"Operation node '{node.value}' requires at least 2 operands.")
        
            # Handle specific operations
            values = [self.evaluate_node(child) for child in node.children]
            # print(values)
            if None in values:
                raise ValueError(f"Operation '{node.value}' has NoneType operand(s): {values}")
            
            if node.value == "SMOOSH":
                # Evaluate each child and convert their value to string, then concatenate
                concatenated_string = "".join([str(self.evaluate_node(child)) for child in node.children])
                return concatenated_string
            
            # no string value at this point
            if any(isinstance(value, str) and (value == 'WIN' or value == 'FAIL') for value in values):
                for i in range(len(values)):
                    if values[i] == 'WIN':
                        values[i] = 1
                    elif values[i] == 'FAIL':
                        values[i] = 0
            if any(isinstance(value, str) for value in values):
                raise TypeError(f"Cannot perform operation '{node.value}' with string operands: {values}")
            
            if node.value == "SUM":
                return sum(values)
            elif node.value == "DIFF":
                return values[0] - values[1]
            elif node.value == "PRODUKT":
                result = 1
                for value in values:
                    if isinstance(value, (int, float)):
                        result *= value
                    else:
                        raise TypeError(f"Cannot multiply non-numeric type: {type(value)}")
                return result
            elif node.value == "QUOSHUNT":
                if values[1] == 0:
                    raise ZeroDivisionError("Division by zero in QUOSHUNT operation.")
                if any(isinstance(value, float) for value in values):
                    return values[0] / values[1]
                else:
                    return values[0] // values[1]
            elif node.value == "BIGGR":
                return max(values)
            elif node.value == "SMALLR":
                return min(values)
            elif node.value == "MOD":
                return values[0] % values[1]
        elif node.node_type == NodeType.TYPECASTING:
            # Ensure there is a child to evaluate
            if not node.children or len(node.children) < 1:
                raise ValueError("TYPECASTING node requires at least one child to evaluate.")

            # Evaluate the child node
            value = self.evaluate_node(node.children[0])

            # Perform typecasting based on the target type defined in node.value
            if node.value == "NUMBR":  # Convert to integer
                try:
                    return int(value)
                except ValueError:
                    raise ValueError(f"Cannot convert value '{value}' to integer.")
            
            elif node.value == "NUMBAR":  # Convert to float
                try:
                    return float(value)
                except ValueError:
                    raise ValueError(f"Cannot convert value '{value}' to float.")

            elif node.value == "YARN":  # Convert to string
                return str(value)
            
            elif node.value == "TROOF":
                if value == '' or value == 0:
                    value = 'FAIL'
                    return str(value)
                else:
                    value = 'WIN'
                    return str(value)
            else:
                raise ValueError(f"Unknown typecasting target '{node.value}'.")
        else:
            raise ValueError(f"Unknown node type: {node.node_type}")

    def update_to_symbol_table(self, name, value):
        if isinstance(value, float):
            value = round(value, 2)
            self.symbol_table.update_variable(name, 'NUMBAR', value)
        elif isinstance(value, int):
            self.symbol_table.update_variable(name, 'NUMBR', value)
        elif isinstance(value, str):
            if value == 'WIN' or value == 'FAIL':
                self.symbol_table.update_variable(name, 'TROOF', value)
            else:
                self.symbol_table.update_variable(name, 'YARN', value)
        else:
            self.symbol_table.update_variable(name, 'NOOB', value)

    def add_to_symbol_table(self, name, value):
        if isinstance(value, float):
            value = round(value, 2)
            self.symbol_table.add_variable(name, 'NUMBAR', value)
        elif isinstance(value, int):
            self.symbol_table.add_variable(name, 'NUMBR', value)
        elif isinstance(value, str):
            if value == 'WIN' or value == 'FAIL':
                self.symbol_table.add_variable(name, 'TROOF', value)
            else:
                self.symbol_table.add_variable(name, 'YARN', value)
        else:
            self.symbol_table.add_variable(name, 'NOOB', value)

    def interpret(self, node: ASTNode):
        """Interpret the AST, focusing on program logic."""
        if not node:
            raise ValueError("Node is None during interpretation.")
        
        if node.node_type in [NodeType.PROGRAM, NodeType.STATEMENT_LIST]:
            for child in node.children:
                self.interpret(child)
        
        elif node.node_type == NodeType.PRINT:
            if not node.children:
                raise ValueError("PRINT node must have a child to print.")
            # Evaluate all children and join their values into a single line
            values_to_print = [str(self.evaluate_node(child)) for child in node.children]
            concatenated_output = " ".join(values_to_print)  # Join with a space
            
            self.update_to_symbol_table('IT', concatenated_output)
            print(concatenated_output)

        elif node.node_type == NodeType.INPUT:
            if not node.children or len(node.children) < 1:
                pass
            var_name = node.value
            # Prompt user for input using a Tkinter popup
            user_input = simpledialog.askstring("Input", f"Enter value for {var_name}:", parent = self.master)
            if user_input is None:
                raise ValueError("No input provided by the user.")
            # Try to convert the input to an appropriate type
            try:
                if '.' in user_input:
                    value = float(user_input)
                else:
                    value = int(user_input)
            except ValueError:
                value = user_input  # Treat as string if conversion fails
            print(user_input)
            self.update_to_symbol_table(var_name, value)

        elif node.node_type == NodeType.DECLARATION:
            if not node.children or len(node.children) < 1:
                pass
            else:
                var_name = node.value
                value = self.evaluate_node(node.children[0])
                self.add_to_symbol_table(var_name, value)
        
        elif node.node_type == NodeType.ASSIGNMENT:
            if not node.children or len(node.children) < 1:
                raise ValueError("ASSIGNMENT node requires at least one child.")
            var_name = node.value
            value = self.evaluate_node(node.children[0])
            self.update_to_symbol_table(var_name, value)  # Update symbol table for assignments
        
        elif node.node_type == NodeType.RECASTING:
            # Ensure there is at least one child node
            if not node.children or len(node.children) < 1:
                raise ValueError("RECASTING requires at least one exression to process.")

            # Determine the target type from node.value
            target_type = node.value  # Example values: 'NUMBAR', 'NUMBR', 'TROOF', 'YARN', 'NOOB'

            # Evaluate the child node's value
            value = self.evaluate_node(node.children[0])

            # Handle typecasting logic
            if target_type == "NUMBR":  # Convert to integer
                try:
                    recast_value = int(float(value))  # Attempt numeric conversion
                except ValueError:
                    recast_value = 0  # Default value on failed conversion
            elif target_type == "NUMBAR":  # Convert to float
                try:
                    recast_value = float(value)
                except ValueError:
                    recast_value = 0.0  # Default value on failed conversion
            elif target_type == "TROOF":  # Convert to boolean (0/1)
                if value == '' or value == 0:
                    recast_value = str('FAIL')
                else:
                    recast_value = str('WIN')
            elif target_type == "YARN":  # Convert to string
                recast_value = str(value)
            elif target_type == "NOOB":  # Handle unsupported types
                recast_value = str('NOOB')  
            else:
                raise ValueError(f"Unknown typecasting target: {target_type}")
            # Update the symbol table with the recast value and its type
            self.symbol_table.update_variable(node.children[0].value, target_type, recast_value)
        
        elif node.node_type == NodeType.IF_ELSE:
            if not node.children or len(node.children) < 1:
                raise ValueError("IF_ELSE node must have at least one child.")

            # Iterate through the children to evaluate conditions and execute blocks
            for child in node.children:
                if child.node_type == NodeType.IF_STATEMENT:
                    # Handle the primary IF statement
                    condition_node = child.children[0]
                    statement_list_node = child.children[1]
                    condition_result = self.evaluate_node(condition_node)
                    
                    if condition_result == 'WIN':  # True condition
                        self.interpret(statement_list_node)
                        return  # Exit after a block is executed
                    
                elif child.node_type == NodeType.ELSEIF_STATEMENT:
                    # Handle ELSEIF statements
                    condition_node = child.children[0]
                    statement_list_node = child.children[1]
                    condition_result = self.evaluate_node(condition_node)

                    if condition_result == 'WIN':  # True condition
                        self.interpret(statement_list_node)
                        return  # Exit after a block is executed
                    
                elif child.node_type == NodeType.ELSE_STATEMENT:
                    # Handle the ELSE statement (no condition, just execute block)
                    statement_list_node = child.children[0]
                    self.interpret(statement_list_node)
                    return  # Exit after ELSE block is executed
                
        elif node.node_type == NodeType.TYPECASTING:
            if not node.children or len(node.children) < 1:
                raise ValueError("TYPECASTING node must have at least one child.")

            # Determine the target type for casting
            target_type = node.value  # The target type (e.g., NUMBAR, NUMBR, TROOF, YARN, NOOB)
            child_value = self.evaluate_node(node.children[0])  # Evaluate the child node

            # Perform typecasting based on the target type
            if target_type == "NUMBAR":  # Convert to float
                try:
                    casted_value = float(child_value)
                except ValueError:
                    raise TypeError(f"Cannot cast value '{child_value}' to NUMBAR.")
            elif target_type == "NUMBR":  # Convert to int
                try:
                    casted_value = int(float(child_value))  # Handle numeric strings with decimals
                except ValueError:
                    raise TypeError(f"Cannot cast value '{child_value}' to NUMBR.")
            elif target_type == "TROOF":  # Convert to boolean-like value
                casted_value = 'WIN' if child_value else 'FAIL'
            elif target_type == "YARN":  # Convert to string
                casted_value = str(child_value)
            elif target_type == "NOOB":  # Convert to null-like value
                casted_value = "NOOB"
            else:
                raise ValueError(f"Unknown target type for typecasting: {target_type}")
            self.symbol_table.update_variable("IT", target_type, casted_value)

        elif node.node_type == NodeType.SWITCH_CASE:
            if not node.children or len(node.children) < 2:
                raise ValueError("SWITCH_CASE must have an expression and at least one CASE_LIST.")

            # Evaluate the switch expression
            switch_value = self.evaluate_node(node.children[0])  # The first child is the expression (e.g., choice)

            # Traverse through CASE_LIST nodes
            case_matched = False
            for case_node in node.children[1:]:
                if case_node.node_type == NodeType.CASE_LIST:
                    # The first child of CASE_LIST is the case literal
                    case_value = self.evaluate_node(case_node.children[0])

                    # Check if the switch value matches the case value
                    if switch_value == case_value:
                        case_matched = True
                        self.interpret(case_node.children[1])  # Execute the STATEMENT_LIST
                        # Check for a BREAK statement
                        if len(case_node.children) > 2 and case_node.children[2].node_type == NodeType.BREAK:
                            return  # Exit the SWITCH_CASE
                elif case_node.node_type == NodeType.DEFAULT_CASE:
                    # Execute the DEFAULT_CASE if no match was found
                    if not case_matched:
                        self.interpret(case_node.children[0])  # Execute the STATEMENT_LIST
                        return
            # If no match and no DEFAULT_CASE, do nothing

        elif node.node_type == NodeType.LOOP:
            # if len(node.children) < 4:
            #     raise ValueError("LOOP node must have a direction, loop variable, condition, and statement list.")

            direction = node.children[0].value  # "UPPIN" or "NERFIN"
            loop_variable_node = node.children[1]  # Loop variable
            condition_node = node.children[2]  # Loop condition
            statement_list_node = node.children[3]  # Statements to execute in the loop

            # Get the initial value of the loop variable
            loop_variable = loop_variable_node.value
            var_details = self.symbol_table.variables.get(loop_variable)
            loop_variable_value = var_details["value"]

            while True:
                # Evaluate the loop condition
                condition_result = self.evaluate_node(condition_node)

                # Break the loop if the condition is not met
                if condition_result != "WIN":
                    break

                # Execute the loop body
                self.interpret(statement_list_node)

                # Update the loop variable
                if direction == "UPPIN":
                    loop_variable_value += 1
                elif direction == "NERFIN":
                    loop_variable_value -= 1
                else:
                    raise ValueError(f"Unknown loop direction: {direction}")

                # Update the symbol table with the new value of the loop variable
                self.update_to_symbol_table(loop_variable, loop_variable_value)
                # self.symbol_table[loop_variable]["value"] = loop_variable_value

        elif node.node_type == NodeType.FUNCTION_DEFINITION:
            # Handle Function Definition
            function_name = node.value
            params = [param.value for param in node.children[0].children]
            body = node.children[1]
            
            # Save the function definition into the symbol table
            self.symbol_table.add_function(function_name, params, body)


        elif node.node_type == NodeType.FUNCTION_CALL:
            function_name = node.value  # Name of the function being called
            arguments = [self.evaluate_node(arg) for arg in node.children]

            # Retrieve the function definition
            function = self.symbol_table.get_function(function_name)
            if not function:
                raise ValueError(f"Undefined function: {function_name}")

            # Check argument count
            if len(arguments) != len(function["params"]):
                raise ValueError(f"Function {function_name} expects {len(function['params'])} arguments, got {len(arguments)}")

            # Manage local function scope
            local_scope = self.symbol_table.copy()  # Clone the current symbol table for local scope isolation
            for param, arg in zip(function["params"], arguments):
                if isinstance(arg, float):
                    arg = round(arg, 2)
                    local_scope.add_variable(param, 'NUMBAR', arg)
                elif isinstance(arg, int):
                    local_scope.add_variable(param, 'NUMBR', arg)
                elif isinstance(arg, str):
                    if arg == 'WIN' or arg == 'FAIL':
                        local_scope.add_variable(param, 'TROOF', arg)
                    else:
                        local_scope.add_variable(param, 'YARN', arg)
                else:
                    local_scope.add_variable(param, 'NOOB', arg)
                # local_scope.add_variable(param, "ANY", arg)  # Update local scope with arguments

            # Temporarily switch scopes for execution
            self.symbol_table = local_scope
            try:
                self.interpret(function["body"])  # Interpret the function body within this isolated scope
            finally:
                # Restore the original symbol table
                self.symbol_table = local_scope  # Restore back to the parent symbol table
                
        elif node.node_type == NodeType.FUNCTION_RETURN:
            # Handle function return logic
            return_value = self.evaluate_node(node.children[0])  # Evaluate the return expression
            self.update_to_symbol_table("IT", return_value)  # Store return value in the special variable `IT`
            # Signal that the function has returned
        else:
            print(f"Unhandled node type: {node.node_type}")

class SemanticAnalyzer:
    def __init__(self, ast: ASTNode, symbol_table: SymbolTable):
        self.ast = ast
        self.symbol_table = symbol_table
        self.errors = []
        
    def analyze(self):
        """Perform semantic analysis on the AST"""
        self.traverse_ast(self.ast)
        return len(self.errors) == 0
    
    def traverse_ast(self, node: ASTNode):
        """Recursively traverse the AST and perform semantic checks"""
        if not node:
            return
        
        # Type checking and semantic rules for different node types
        if node.node_type == NodeType.ASSIGNMENT:
            self.check_assignment(node)
        elif node.node_type == NodeType.OPERATION:
            self.check_operation(node)
        elif node.node_type == NodeType.COMPARISON:
            self.check_comparison(node)
        # elif node.node_type == NodeType.FUNCTION_CALL:
        #     self.check_function_call(node)
        
        # Recursively check children
        for child in node.children:
            if isinstance(child, ASTNode):
                self.traverse_ast(child)
    
    def check_assignment(self, node: ASTNode):
        """Check semantic rules for variable assignment"""
        var_name = node.value
        
        # Check if variable exists in symbol table
        if var_name not in self.symbol_table.variables:
            self.errors.append(f"Variable '{var_name}' used before declaration")
        
        # Type compatibility check (basic)
        if len(node.children) > 0:
            value_type = self.infer_type(node.children[0])
            current_type = self.symbol_table.variables.get(var_name, 'NOOB')
            
            if current_type == 'NOOB':
                # Update type if not previously defined
                self.symbol_table.variables[var_name] = value_type
    
    def check_operation(self, node: ASTNode):
        """Check semantic rules for arithmetic operations"""
        if len(node.children) < 2:
            self.errors.append(f"Insufficient operands for operation: {node.value}")
    
    def check_comparison(self, node: ASTNode):
        """Check semantic rules for comparisons"""
        if len(node.children) != 2:
            self.errors.append(f"Invalid comparison: {node.value}")
    
    # def check_function_call(self, node: ASTNode):
    #     """Check semantic rules for function calls"""
    #     func_name = node.value
        
    #     # Check if function exists
    #     if func_name not in self.symbol_table.functions:
    #         self.errors.append(f"Function '{func_name}' not defined")
    #     else:
    #         # Check argument count
    #         expected_params = len(self.symbol_table.functions[func_name])
    #         actual_args = len(node.children)
            
    #         if expected_params != actual_args:
    #             self.errors.append(f"Function '{func_name}' expects {expected_params} arguments, got {actual_args}")
    
    def infer_type(self, node: ASTNode) -> str:
        """Infer the type of an AST node"""
        if node.node_type == NodeType.LITERAL:
            if isinstance(node.value, int):
                return 'NUMBR'
            elif isinstance(node.value, float):
                return 'NUMBAR'
            elif isinstance(node.value, str):
                return 'YARN'
            elif isinstance(node.value, bool):
                return 'TROOF'
        
        # Fallback type
        return 'NOOB'

class LOLCODECompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("LOLCODE Compiler")
        master.geometry("1200x1000")

        # Initialize lexemes as an empty dictionary first
        self.lexemes = {}
        
        # Create main frame
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Layout with grid
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)
        
        # File Explorer (1)
        self.setup_file_explorer()
        
        # Text Editor (2)
        self.setup_text_editor()
        
        # Tokens List (3)
        self.setup_tokens_list()
        
        # Symbol Table (4)
        self.setup_symbol_table()
        
        # Execute Button (5)
        self.setup_execute_button()
        
        # Console (6)
        self.setup_console()
    
    def setup_file_explorer(self):
        file_frame = ttk.LabelFrame(self.main_frame, text="File Explorer")
        file_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=0, pady=0)

        # Create the button with increased width and internal padding for size
        self.file_button = ttk.Button(file_frame, text="Open File", command=self.open_file)

        # Pack the button aligned to the left with extra padding for size
        self.file_button.pack(anchor='w', padx=10, pady=5, ipadx=10, ipady=5, fill='x')  # 'anchor=w' aligns it to the left, 'fill=x' makes it stretch
    
    def setup_text_editor(self):
        editor_frame = ttk.LabelFrame(self.main_frame, text="Text Editor")
        editor_frame.grid(row=1, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)
        
        self.text_editor = tk.Text(editor_frame, wrap=tk.WORD, height=20)
        self.text_editor.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.config(yscrollcommand=text_scroll.set)
        
    def setup_tokens_list(self):
        tokens_frame = ttk.LabelFrame(self.main_frame, text="Tokens")
        tokens_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=('Lexeme', 'Token', 'Classification'), show='headings')
        self.tokens_tree.heading('Lexeme', text='Lexeme')
        self.tokens_tree.heading('Token', text='Token')
        self.tokens_tree.heading('Classification', text='Classification')
        self.tokens_tree.column('Lexeme', width=150)
        self.tokens_tree.column('Token', width=100)
        self.tokens_tree.column('Classification', width=150)
        self.tokens_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Populate the Treeview with lexemes and classifications
        if len(self.lexemes) > 0:
            for lexeme, token in self.lexemes.items():
                classification = LEXEME_CLASSIFICATIONS.get(lexeme, 'Unknown')
                self.tokens_tree.insert('', 'end', values=(lexeme, token, classification))
        
    def setup_symbol_table(self):
        symbol_frame = ttk.LabelFrame(self.main_frame, text="Symbol Table")
        symbol_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)
        
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=('Variable', 'Type', 'Value'), show='headings')
        self.symbol_tree.heading('Variable', text='Variable')
        self.symbol_tree.heading('Type', text='Type')
        self.symbol_tree.heading('Value', text='Value')
        self.symbol_tree.column('Variable', width=150)
        self.symbol_tree.column('Type', width=100)
        self.symbol_tree.column('Value', width=150)
        self.symbol_tree.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        symbol_scroll = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, command=self.symbol_tree.yview)
        symbol_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.symbol_tree.config(yscrollcommand=symbol_scroll.set)
        
    def setup_execute_button(self):
        execute_frame = ttk.Frame(self.main_frame)
        execute_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Create the Execute button with a custom width and increased padding for size
        self.execute_button = ttk.Button(execute_frame, text="Execute", command=self.execute_code, width=50)

        # Pack the button aligned to the left with additional internal padding
        self.execute_button.pack(anchor='w', padx=10, pady=5, ipadx=10, ipady=5, fill='x')  # 'anchor=w' aligns it to the left, 'fill=x' stretches it
    
    def setup_console(self):
        console_frame = ttk.LabelFrame(self.main_frame, text="Console")
        console_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        # Create a console Text widget and configure it to fill space
        self.console = tk.Text(console_frame, wrap=tk.WORD, state='disabled')
        self.console.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Add a vertical scrollbar
        console_scroll = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console.yview)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=console_scroll.set)
        
        # Adjust row weights in the grid to make the console fill the remaining space
        self.main_frame.rowconfigure(4, weight=1)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("LOLCODE Files", "*.lol")])
        if file_path:
            with open(file_path, 'r') as file:
                code = file.read()
                self.text_editor.delete('1.0', tk.END)
                self.text_editor.insert(tk.END, code)
    
    def execute_code(self):
        # Clear previous results
        self.tokens_tree.delete(*self.tokens_tree.get_children())
        self.symbol_tree.delete(*self.symbol_tree.get_children())
        self.console.config(state='normal')
        self.console.delete('1.0', tk.END)

        # Get code from text editor
        code = self.text_editor.get('1.0', tk.END).strip()

        try:
            # Tokenization
            tokens = tokenize_lolcode(code)
            self.lexemes = {token[1]: token[0] for token in tokens}

            # Populate tokens list
            for lexeme, token in self.lexemes.items():
                classification = LEXEME_CLASSIFICATIONS.get(token, 'Unknown')
                self.tokens_tree.insert('', 'end', values=(lexeme, token, classification))

            # Syntax Analysis
            syntax_analyzer = LOLCODESyntaxAnalyzer(tokens)
            ast = syntax_analyzer.parse_program()
            print(ast)

            # Semantic Analysis
            semantic_analyzer = SemanticAnalyzer(ast, syntax_analyzer.symbol_table)
            semantic_result = semantic_analyzer.analyze()

            if semantic_result:
                # Interpret and Execute Code One Node at a Time
                interpreter = ASTInterpreter(ast, syntax_analyzer.symbol_table, master=self.master)

                # Redirect stdout to capture console output
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()

                try:
                    for node in ast.children:  # Process each child node individually
                        try:
                            interpreter.interpret(node)  # Interpret the current AST node
                            output = redirected_output.getvalue()
                            if output:
                                self.console.insert(tk.END, output)  # Display the output
                        except Exception as e:
                            # Handle and display runtime error for the specific node
                            self.console.insert(tk.END, f"Runtime Error: {e}\n")
                            break  # Stop execution after the first error
                        finally:
                            # Clear the redirected output buffer
                            redirected_output.seek(0)
                            redirected_output.truncate(0)

                        # Update Symbol Table dynamically after each node
                        self.symbol_tree.delete(*self.symbol_tree.get_children())
                        for var_name, details in semantic_analyzer.symbol_table.get_variables().items():
                            var_type = details['type']
                            var_value = details['value']
                            self.symbol_tree.insert('', 'end', values=(var_name, var_type, var_value))

                    self.console.config(state='disabled')

                finally:
                    # Restore stdout
                    sys.stdout = old_stdout
            else:
                # Display semantic errors
                for error in semantic_analyzer.errors:
                    self.console.insert(tk.END, f"Semantic Error: {error}\n")
                self.console.config(state='disabled')

        except Exception as e:
            self.console.config(state='normal')
            self.console.insert(tk.END, f"Error: {str(e)}\n")
            self.console.config(state='disabled')



def main():
    root = tk.Tk()
    app = LOLCODECompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()