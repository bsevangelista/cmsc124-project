import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import sys
from io import StringIO

# Import the existing syntax analyzer components
from test import LOLCODESyntaxAnalyzer, NodeType, ASTNode, SymbolTable
from lexical_analyzer import tokenize_lolcode

class ASTInterpreter:
    def __init__(self, ast: ASTNode, symbol_table: SymbolTable):
        self.ast = ast
        self.symbol_table = symbol_table

    def evaluate_node(self, node: ASTNode):
        """Recursively evaluate an AST node."""
        if node.node_type == NodeType.LITERAL:
            return node.value
        elif node.node_type == NodeType.EXPRESSION:
            if node.children:
                return self.evaluate_node(node.children[0])  # Evaluate the child node
            else:
                return node.value
        elif node.node_type == NodeType.OPERATION:
            if len(node.children) < 2:
                raise IndexError(f"Operation node '{node.value}' requires at least 2 operands.")
            
            if node.value == "SUM":
                return sum(self.evaluate_node(child) for child in node.children)
            elif node.value == "DIFF":
                return self.evaluate_node(node.children[0]) - self.evaluate_node(node.children[1])
            elif node.value == "PRODUKT":
                result = 1
                for child in node.children:
                    print(child, 'here')
                    value = self.evaluate_node(child)
                    if isinstance(value, (int, float)):  # Ensure it's numeric
                        result *= value
                    else:
                        raise TypeError(f"Cannot multiply non-numeric type: {type(value)}")
                return result
            elif node.value == "QUOSHUNT":
                if len(node.children) < 2:
                    raise IndexError(f"QUOSHUNT operation requires 2 operands.")
                return self.evaluate_node(node.children[0]) // self.evaluate_node(node.children[1])
            elif node.value == "BIGGR":
                return max(self.evaluate_node(child) for child in node.children)
            elif node.value == "SMALLR":
                return min(self.evaluate_node(child) for child in node.children)
        elif node.node_type == NodeType.VARIABLE:
            var_details = self.symbol_table.variables.get(node.value)
            if var_details:
                return var_details['value']
            else:
                raise ValueError(f"Variable '{node.value}' not defined.")
        else:
            raise ValueError(f"Unknown node type: {node.node_type}")


    def interpret(self, node: ASTNode):
        """Interpret the AST, focusing on program logic."""
        if node.node_type in [NodeType.PROGRAM, NodeType.STATEMENT_LIST]:
            for child in node.children:
                self.interpret(child)
        elif node.node_type == NodeType.PRINT:
            value = self.evaluate_node(node.children[0])
            print(value)
        elif node.node_type == NodeType.ASSIGNMENT:
            var_name = node.value
            value = self.evaluate_node(node.children[0])
            self.symbol_table.add_variable(var_name, "DYNAMIC", value)
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
        # elif node.node_type == NodeType.DECLARATION:
        #     self.check_declaration(node)
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

    def check_declaration(self, node: ASTNode):
        var_name = node.value
        if var_name in self.symbol_table:
            self.errors.append(f"Variable '{var_name}' already declared.")
        else:
            # Default type and value
            var_type = 'NOOB'
            var_value = None

            # If initialized, evaluate the initializer
            if node.children:
                var_type, var_value = self.evaluate_expression(node.children[0])

            # Add to the symbol table
            self.symbol_table[var_name] = {'type': var_type, 'value': var_value}

    def evaluate_expression(self, node: ASTNode):
        if node.node_type == NodeType.LITERAL:
            return node.token_type, node.value  # Type and value of the literal
        elif node.node_type == NodeType.OPERATION:
            return self.evaluate_operation(node)
        elif node.node_type == NodeType.EXPRESSION:
            var_name = node.value
            if var_name in self.symbol_table:
                return self.symbol_table[var_name]['type'], self.symbol_table[var_name]['value']
            else:
                return(f"Variable '{var_name}' not declared.")
        # Add more cases as needed...

    def evaluate_operation(self, node: ASTNode):
        operation = node.value
        left_type, left_value = self.evaluate_expression(node.children[0])
        right_type, right_value = self.evaluate_expression(node.children[1])
        if left_type not in {'NUMBR', 'NUMBAR'} or right_type not in {'NUMBR', 'NUMBAR'}:
            return(f"Invalid operand types for operation '{operation}'.")

        result_type = 'NUMBAR' if 'NUMBAR' in (left_type, right_type) else 'NUMBR'
        result_value = self.perform_operation(operation, left_value, right_value)
        return result_type, result_value
    
    def perform_operation(self, operation: str, left_value, right_value):
        """
        Perform an arithmetic operation and return the result.
        """
        if operation == 'SUM_OF':
            return left_value + right_value
        elif operation == 'DIFF_OF':
            return left_value - right_value
        elif operation == 'PRODUKT_OF':
            return left_value * right_value
        elif operation == 'QUOSHUNT_OF':
            if right_value == 0:
                print("Division by zero.")
            return left_value / right_value
        elif operation == 'MOD_OF':
            if right_value == 0:
                print("Division by zero.")
            return left_value % right_value
        elif operation == 'BIGGR_OF':
            return max(left_value, right_value)
        elif operation == 'SMALLR_OF':
            return min(left_value, right_value)
        else:
            print(f"Unknown operation: {operation}")
    
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
    
    def infer_type(self, node: ASTNode):
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
        master.geometry("1200x800")
        
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
        self.text_editor.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def setup_tokens_list(self):
        tokens_frame = ttk.LabelFrame(self.main_frame, text="Tokens")
        tokens_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        self.tokens_tree = ttk.Treeview(tokens_frame, columns=('Lexeme', 'Token'), show='headings')
        self.tokens_tree.heading('Lexeme', text='Lexeme')
        self.tokens_tree.heading('Token', text='Token')
        self.tokens_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def setup_symbol_table(self):
        symbol_frame = ttk.LabelFrame(self.main_frame, text="Symbol Table")
        symbol_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        self.symbol_tree = ttk.Treeview(symbol_frame, columns=('Variable', 'Type', 'Value'), show='headings')
        self.symbol_tree.heading('Variable', text='Variable')
        self.symbol_tree.heading('Type', text='Type')
        self.symbol_tree.heading('Value', text='Value')
        self.symbol_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def setup_execute_button(self):
        execute_frame = ttk.Frame(self.main_frame)
        execute_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        self.execute_button = ttk.Button(execute_frame, text="Execute", command=self.execute_code)
        self.execute_button.pack(pady=5)
    
    def setup_console(self):
        console_frame = ttk.LabelFrame(self.main_frame, text="Console")
        console_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        self.console = tk.Text(console_frame, wrap=tk.WORD, height=10, state='disabled')
        self.console.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    
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

            # Populate tokens list
            for token in tokens:
                self.tokens_tree.insert('', 'end', values=(token[1], token[0]))

            # Syntax Analysis
            syntax_analyzer = LOLCODESyntaxAnalyzer(tokens)
            ast = syntax_analyzer.parse_program()
            print(ast)

            # Semantic Analysis
            semantic_analyzer = SemanticAnalyzer(ast, syntax_analyzer.symbol_table)
            semantic_result = semantic_analyzer.analyze()

            if semantic_result:
                # Populate Symbol Table
                for var_name, details in semantic_analyzer.symbol_table.get_variables().items():
                    var_type = details['type']
                    var_value = details['value']
                    self.symbol_tree.insert('', 'end', values=(var_name, var_type, var_value))

                # Interpret and Execute Code
                interpreter = ASTInterpreter(ast, syntax_analyzer.symbol_table)

                # Redirect stdout to capture console output
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()

                try:
                    interpreter.interpret(ast)  # Interpret the AST
                    output = redirected_output.getvalue()
                    self.console.insert(tk.END, output)
                except Exception as e:
                    self.console.insert(tk.END, f"Runtime Error: {e}\n")
                finally:
                    # Restore stdout
                    sys.stdout = old_stdout

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