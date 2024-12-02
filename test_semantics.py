import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from enum import Enum, auto
from typing import List, Tuple, Optional, Union, Dict, Any
import ast

# Import the existing lexical analyzer and syntax analyzer
from lexical_analyzer import tokenize_lolcode
from test import LOLCODESyntaxAnalyzer, NodeType, ASTNode, SymbolTable

class SemanticError(Exception):
    """Custom exception for semantic analysis errors."""
    pass

class SemanticAnalyzer:
    def __init__(self, ast_root: ASTNode, symbol_table: SymbolTable):
        """
        Initialize the semantic analyzer with the AST and symbol table.
        
        :param ast_root: Root node of the Abstract Syntax Tree
        :param symbol_table: Symbol table from syntax analysis
        """
        self.ast_root = ast_root
        self.symbol_table = symbol_table
        self.errors: List[str] = []
        
    def analyze(self):
        """
        Perform comprehensive semantic analysis on the AST.
        """
        self.errors = []  # Reset errors
        self._analyze_node(self.ast_root)
        return len(self.errors) == 0
    
    def _analyze_node(self, node: ASTNode):
        """
        Recursively analyze each node in the AST for semantic correctness.
        
        :param node: Current AST node to analyze
        """
        if not node:
            return
        
        # Dispatch to specific analysis methods based on node type
        analysis_methods = {
            NodeType.ASSIGNMENT: self._analyze_assignment,
            NodeType.DECLARATION: self._analyze_declaration,
            NodeType.OPERATION: self._analyze_operation,
            NodeType.COMPARISON: self._analyze_comparison,
            NodeType.BOOLEAN_OPERATION: self._analyze_boolean_operation,
            NodeType.FUNCTION_CALL: self._analyze_function_call,
            NodeType.FUNCTION_DEFINITION: self._analyze_function_definition,
            NodeType.FUNCTION_RETURN: self._analyze_function_return,
            NodeType.TYPECASTING: self._analyze_typecasting,
            NodeType.RECASTING: self._analyze_recasting,
            NodeType.IF_STATEMENT: self._analyze_if_statement,
            NodeType.SWITCH_CASE: self._analyze_switch_case,
            NodeType.LOOP: self._analyze_loop
        }
        
        # Call specific analysis method if exists
        if node.node_type in analysis_methods:
            analysis_methods[node.node_type](node)
        
        # Recursively analyze children
        for child in node.children:
            if isinstance(child, ASTNode):
                self._analyze_node(child)
    
    def _analyze_assignment(self, node: ASTNode):
        """
        Analyze variable assignment for type consistency and variable existence.
        
        :param node: Assignment node to analyze
        """
        var_name = node.value
        
        # Check if variable is declared
        if var_name not in self.symbol_table.variables:
            self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration")
        
        # Type checking would typically happen here
        # In a more advanced implementation, you'd verify type compatibility
    
    def _analyze_declaration(self, node: ASTNode):
        """
        Analyze variable declaration.
        
        :param node: Declaration node to analyze
        """
        var_name = node.value
        
        # Check for duplicate declarations
        if var_name in self.symbol_table.variables:
            self.errors.append(f"Semantic Error: Variable '{var_name}' already declared")
    
    def _analyze_operation(self, node: ASTNode):
        """
        Analyze arithmetic and concatenation operations.
        
        :param node: Operation node to analyze
        """
        # Validate operand count
        if len(node.children) < 2:
            self.errors.append(f"Semantic Error: Insufficient operands for operation {node.value}")
    
    def _analyze_comparison(self, node: ASTNode):
        """
        Analyze comparison operations.
        
        :param node: Comparison node to analyze
        """
        # Validate operand count
        if len(node.children) != 2:
            self.errors.append(f"Semantic Error: Invalid number of operands for comparison {node.value}")
    
    def _analyze_boolean_operation(self, node: ASTNode):
        """
        Analyze boolean operations.
        
        :param node: Boolean operation node to analyze
        """
        # Validate operand count based on operation type
        if node.value in {'AND', 'OR', 'XOR'} and len(node.children) != 2:
            self.errors.append(f"Semantic Error: Binary boolean operation {node.value} requires 2 operands")
        elif node.value == 'NOT' and len(node.children) != 1:
            self.errors.append(f"Semantic Error: Unary NOT operation requires 1 operand")
    
    def _analyze_function_call(self, node: ASTNode):
        """
        Analyze function calls for parameter count and existence.
        
        :param node: Function call node to analyze
        """
        func_name = node.value
        
        # Check if function exists
        if func_name not in self.symbol_table.functions:
            self.errors.append(f"Semantic Error: Undefined function '{func_name}'")
        else:
            # Check parameter count
            expected_params = len(self.symbol_table.functions[func_name])
            actual_params = len(node.children)
            
            if expected_params != actual_params:
                self.errors.append(
                    f"Semantic Error: Function '{func_name}' called with {actual_params} "
                    f"arguments, but expects {expected_params}"
                )
    
    def _analyze_function_definition(self, node: ASTNode):
        """
        Analyze function definition.
        
        :param node: Function definition node to analyze
        """
        # Check for duplicate function definitions
        func_name = node.value
        if func_name in self.symbol_table.functions:
            self.errors.append(f"Semantic Error: Function '{func_name}' already defined")
    
    def _analyze_function_return(self, node: ASTNode):
        """
        Analyze function returns.
        
        :param node: Function return node to analyze
        """
        # Additional return-related checks could be added here
        pass
    
    def _analyze_typecasting(self, node: ASTNode):
        """
        Analyze type casting operations.
        
        :param node: Typecasting node to analyze
        """
        valid_types = {'NUMBR', 'NUMBAR', 'YARN', 'TROOF'}
        
        if node.value not in valid_types:
            self.errors.append(f"Semantic Error: Invalid type casting to {node.value}")
    
    def _analyze_recasting(self, node: ASTNode):
        """
        Analyze type recasting operations.
        
        :param node: Recasting node to analyze
        """
        valid_types = {'NUMBR', 'NUMBAR', 'YARN', 'TROOF'}
        
        if node.value not in valid_types:
            self.errors.append(f"Semantic Error: Invalid type recasting to {node.value}")
    
    def _analyze_if_statement(self, node: ASTNode):
        """
        Analyze if-statement structure.
        
        :param node: If-statement node to analyze
        """
        # Validate condition exists
        if not node.children or len(node.children) < 2:
            self.errors.append("Semantic Error: If statement requires a condition and a true block")
    
    def _analyze_switch_case(self, node: ASTNode):
        """
        Analyze switch-case structure.
        
        :param node: Switch-case node to analyze
        """
        # Validate condition exists
        if not node.children or len(node.children) < 1:
            self.errors.append("Semantic Error: Switch-case requires a condition")
    
    def _analyze_loop(self, node: ASTNode):
        """
        Analyze loop structure.
        
        :param node: Loop node to analyze
        """
        # Check loop name
        if not node.value:
            self.errors.append("Semantic Error: Loop requires a name")
    
    def get_semantic_errors(self) -> List[str]:
        """
        Retrieve all semantic errors found during analysis.
        
        :return: List of semantic error messages
        """
        return self.errors

class LOLCODESemanticParserGUI:
    def __init__(self, master):
        self.master = master
        master.title("LOLCODE Semantic Analyzer")
        master.geometry("800x600")

        # File selection frame
        self.file_frame = tk.Frame(master)
        self.file_frame.pack(pady=10, padx=10, fill=tk.X)

        self.file_label = tk.Label(self.file_frame, text="Selected File:")
        self.file_label.pack(side=tk.LEFT)

        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5)

        self.browse_button = tk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT)

        # Notebook for different views
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Tokens view
        self.tokens_frame = tk.Frame(self.notebook)
        self.tokens_text = tk.Text(self.tokens_frame, wrap=tk.WORD, height=20)
        self.tokens_text.pack(expand=True, fill=tk.BOTH)
        self.notebook.add(self.tokens_frame, text="Tokens")

        # AST view
        self.ast_frame = tk.Frame(self.notebook)
        self.ast_text = tk.Text(self.ast_frame, wrap=tk.WORD, height=20)
        self.ast_text.pack(expand=True, fill=tk.BOTH)
        self.notebook.add(self.ast_frame, text="Abstract Syntax Tree")

        # Symbol Table view
        self.symbol_frame = tk.Frame(self.notebook)
        self.symbol_text = tk.Text(self.symbol_frame, wrap=tk.WORD, height=20)
        self.symbol_text.pack(expand=True, fill=tk.BOTH)
        self.notebook.add(self.symbol_frame, text="Symbol Tables")

        # Semantic Errors view
        self.semantic_frame = tk.Frame(self.notebook)
        self.semantic_text = tk.Text(self.semantic_frame, wrap=tk.WORD, height=20)
        self.semantic_text.pack(expand=True, fill=tk.BOTH)
        self.notebook.add(self.semantic_frame, text="Semantic Errors")

        # Parse button
        self.parse_button = tk.Button(master, text="Analyze LOLCODE", command=self.analyze_lolcode)
        self.parse_button.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select LOLCODE File", 
            filetypes=[("LOLCODE Files", "*.lol")]
        )
        if filename:
            self.file_path.set(filename)

    def analyze_lolcode(self):
        # Clear previous results
        for text_widget in [self.tokens_text, self.ast_text, self.symbol_text, self.semantic_text]:
            text_widget.delete('1.0', tk.END)

        # Get the file path
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a LOLCODE file")
            return

        try:
            # Read the file
            with open(file_path, 'r') as file:
                source_code = file.read()

            # Tokenize
            tokens = tokenize_lolcode(source_code)
            
            # Display tokens
            self.tokens_text.insert(tk.END, "TOKENS:\n")
            for token in tokens:
                self.tokens_text.insert(tk.END, f"{token}\n")

            # Parse
            syntax_analyzer = LOLCODESyntaxAnalyzer(tokens)
            ast = syntax_analyzer.parse_program()

            # Display AST
            self.ast_text.insert(tk.END, "ABSTRACT SYNTAX TREE:\n")
            self.ast_text.insert(tk.END, str(ast))

            # Display Symbol Tables
            self.symbol_text.insert(tk.END, "SYMBOL TABLES:\n")
            self.symbol_text.insert(tk.END, "Variables:\n")
            for var, type in syntax_analyzer.symbol_table.variables.items():
                self.symbol_text.insert(tk.END, f"{var}: {type}\n")
            
            self.symbol_text.insert(tk.END, "\nFunctions:\n")
            for func, params in syntax_analyzer.symbol_table.functions.items():
                self.symbol_text.insert(tk.END, f"{func}: {params}\n")
            
            self.symbol_text.insert(tk.END, "\nLoops:\n")
            for loop in syntax_analyzer.symbol_table.loops:
                self.symbol_text.insert(tk.END, f"{loop}\n")

            # Perform Semantic Analysis
            semantic_analyzer = SemanticAnalyzer(ast, syntax_analyzer.symbol_table)
            is_semantically_valid = semantic_analyzer.analyze()

            # Display Semantic Errors
            semantic_errors = semantic_analyzer.get_semantic_errors()
            self.semantic_text.insert(tk.END, "SEMANTIC ANALYSIS:\n")
            if is_semantically_valid:
                self.semantic_text.insert(tk.END, "No semantic errors found!\n")
            else:
                for error in semantic_errors:
                    self.semantic_text.insert(tk.END, f"• {error}\n")

            print('Program analyzed successfully!')

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))

def main():
    root = tk.Tk()
    LOLCODESemanticParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()