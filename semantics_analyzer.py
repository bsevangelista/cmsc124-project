import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import re
import sys
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
        elif node.node_type == NodeType.BOOLEAN_OPERATION:
            if not node.children:
                raise ValueError("BOOLEAN_OPERATION must have at least one child.")

            operation = node.value  # This would hold AND, OR, XOR, NOT, ALL, or ANY

            if operation == "AND":
                # Evaluate both expressions and compute AND logic
                if len(node.children) != 2:
                    raise ValueError("AND operation must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if bool(left) and bool(right) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "OR":
                # Evaluate both expressions and compute OR logic
                if len(node.children) != 2:
                    raise ValueError("OR operation must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if bool(left) or bool(right) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "XOR":
                # XOR: True if one is True and the other is False
                if len(node.children) != 2:
                    raise ValueError("XOR operation must have exactly two operands.")
                left = self.evaluate_node(node.children[0])
                right = self.evaluate_node(node.children[1])
                if bool(left) != bool(right) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "NOT":
                # Unary NOT operation
                if len(node.children) != 1:
                    raise ValueError("NOT operation must have exactly one operand.")
                operand = self.evaluate_node(node.children[0])
                if not bool(operand) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "ALL":
                # Handle ALL with infinite arity
                # Ensure no nesting of ALL or ANY within each other
                if all(self.evaluate_node(child) for child in node.children) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            elif operation == "ANY":
                # Handle ANY with infinite arity
                if any(self.evaluate_node(child) for child in node.children) == True:
                    return 'WIN'
                else:
                    return 'FAIL'

            else:
                raise ValueError(f"Unknown boolean operation: {operation}")

        elif node.node_type == NodeType.OPERATION:
            if len(node.children) < 2:
                raise IndexError(f"Operation node '{node.value}' requires at least 2 operands.")
        
            # Handle specific operations
            values = [self.evaluate_node(child) for child in node.children]
            # print(values)
            if None in values:
                raise ValueError(f"Operation '{node.value}' has NoneType operand(s): {values}")
            elif any(isinstance(value, str) and (value == 'WIN' or value == 'FAIL') for value in values):
                for i in range(len(values)):
                    if values[i] == 'WIN':
                        values[i] = 1
                    elif values[i] == 'FAIL':
                        values[i] = 0
            elif any(isinstance(value, str) for value in values):
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
            elif node.value == "SMOOSH":
                # Evaluate each child and convert their value to string, then concatenate
                concatenated_string = "".join([str(self.evaluate_node(child)) for child in node.children])
                return concatenated_string
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
        elif node.node_type == NodeType.FUNCTION_CALL:
            self.check_function_call(node)
        
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
    
    def check_function_call(self, node: ASTNode):
        """Check semantic rules for function calls"""
        func_name = node.value
        
        # Check if function exists
        if func_name not in self.symbol_table.functions:
            self.errors.append(f"Function '{func_name}' not defined")
        else:
            # Check argument count
            expected_params = len(self.symbol_table.functions[func_name])
            actual_args = len(node.children)
            
            if expected_params != actual_args:
                self.errors.append(f"Function '{func_name}' expects {expected_params} arguments, got {actual_args}")
    
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
        master.geometry("1200x900")

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
        file_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        self.file_button = ttk.Button(file_frame, text="Open File", command=self.open_file)
        self.file_button.pack(padx=5, pady=5)
    
    def setup_text_editor(self):
        editor_frame = ttk.LabelFrame(self.main_frame, text="Text Editor")
        editor_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        self.text_editor = tk.Text(editor_frame, wrap=tk.WORD, height=20)
        self.text_editor.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.config(yscrollcommand=text_scroll.set)
        
    def setup_tokens_list(self):
        tokens_frame = ttk.LabelFrame(self.main_frame, text="Tokens")
        tokens_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=('Lexeme', 'Token', 'Classification'), show='headings')
        self.tokens_tree.heading('Lexeme', text='Lexeme')
        self.tokens_tree.heading('Token', text='Token')
        self.tokens_tree.heading('Classification', text='Classification')
        self.tokens_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Populate the Treeview with lexemes and classifications
        if len(self.lexemes) > 0:
            for lexeme, token in self.lexemes.items():
                classification = LEXEME_CLASSIFICATIONS.get(lexeme, 'Unknown')
                self.tokens_tree.insert('', 'end', values=(lexeme, token, classification))
        
    def setup_symbol_table(self):
        symbol_frame = ttk.LabelFrame(self.main_frame, text="Symbol Table")
        symbol_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=('Variable', 'Type', 'Value'), show='headings')
        self.symbol_tree.heading('Variable', text='Variable')
        self.symbol_tree.heading('Type', text='Type')
        self.symbol_tree.heading('Value', text='Value')
        self.symbol_tree.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        symbol_scroll = ttk.Scrollbar(symbol_frame, orient=tk.VERTICAL, command=self.symbol_tree.yview)
        symbol_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.symbol_tree.config(yscrollcommand=symbol_scroll.set)
        
    def setup_execute_button(self):
        execute_frame = ttk.Frame(self.main_frame)
        execute_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        self.execute_button = ttk.Button(execute_frame, text="Execute", command=self.execute_code)
        self.execute_button.pack(pady=5)
    
    def setup_console(self):
        console_frame = ttk.LabelFrame(self.main_frame, text="Console")
        console_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        self.console = tk.Text(console_frame, wrap=tk.WORD, height=10, state='disabled')
        self.console.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        console_scroll = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.console.yview)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=console_scroll.set)
        
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
                # Populate Symbol Table
                # for var_name, details in semantic_analyzer.symbol_table.get_variables().items():
                #     var_type = details['type']
                #     var_value = details['value']
                #     self.symbol_tree.insert('', 'end', values=(var_name, var_type, var_value))
                    # print(var_name,details)

                # Interpret and Execute Code
                interpreter = ASTInterpreter(ast, syntax_analyzer.symbol_table, master=self.master)

                # Redirect stdout to capture console output
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()

                try:
                    interpreter.interpret(ast)  # Interpret the AST
                    # print(ast)
                    # for var_name, details in semantic_analyzer.symbol_table.get_variables().items():
                    #     print(var_name,details)
                    output = redirected_output.getvalue()
                    self.console.insert(tk.END, output)
                except Exception as e:
                    self.console.insert(tk.END, f"Runtime Error: {e}\n")
                finally:
                    # Restore stdout
                    sys.stdout = old_stdout

                # Populate Symbol Table after interpretation
                for var_name, details in semantic_analyzer.symbol_table.get_variables().items():
                    var_type = details['type']
                    var_value = details['value']
                    self.symbol_tree.insert('', 'end', values=(var_name, var_type, var_value))

                self.console.config(state='disabled')
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