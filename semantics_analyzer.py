import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import sys
from io import StringIO

# Import the existing syntax analyzer components
from test import LOLCODESyntaxAnalyzer, NodeType, ASTNode, SymbolTable
from lexical_analyzer import tokenize_lolcode

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
            
            # Semantic Analysis
            semantic_analyzer = SemanticAnalyzer(ast, syntax_analyzer.symbol_table)
            semantic_result = semantic_analyzer.analyze()
            
            # If no semantic errors, display symbol table
            if semantic_result:
                for var, type_val in syntax_analyzer.symbol_table.variables.items():
                    self.symbol_tree.insert('', 'end', values=(var, type_val, ''))
                
                # Capture console output
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                
                try:
                    # Here you would add code interpretation/execution
                    # This is a placeholder - you'd need to implement an actual interpreter
                    self.console.config(state='normal')
                    self.console.insert(tk.END, "Code executed successfully!\n")
                    self.console.config(state='disabled')
                except Exception as e:
                    self.console.config(state='normal')
                    self.console.insert(tk.END, f"Runtime Error: {str(e)}\n")
                    self.console.config(state='disabled')
                
                # Restore stdout
                sys.stdout = old_stdout
            else:
                # Display semantic errors
                self.console.config(state='normal')
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