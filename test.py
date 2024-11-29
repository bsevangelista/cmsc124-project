import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from enum import Enum, auto
from typing import List, Tuple, Optional, Union
from lexical_analyzer import tokenize_lolcode 

# TODO:
#     linebreaks - need den icheck pero tinanggal ko muna sila sa lexical analyzer
#     check for valid tokens - correct spellings
#     check for required token at start of statements (eg, VISIBLE, GIMMEH, WAZZUP) - parse statements
#     check for expected var_id operands in comparison [test case 6]
#     if token is var_id in parse_statements - parse assignment | parse recasting
#     parse recasting (IS NOW A) [test case 4]
#     infinite arity for smoosh and visible [test case 4]
#     parse boolean operation [test case 5]
#     other parsers
#     Reusing the NodeType and ASTNode from the previous syntax analyzer
class NodeType(Enum):
    PROGRAM = auto()
    STATEMENT_LIST = auto()
    PRINT = auto()
    DECLARATION = auto()
    ASSIGNMENT = auto()
    INPUT = auto()
    OPERATION = auto()
    BOOLEAN_OPERATION = auto()
    COMPARISON = auto()
    IF_STATEMENT = auto()
    SWITCH_CASE = auto()
    LOOP = auto()
    FUNCTION_DEFINITION = auto()
    FUNCTION_CALL = auto()
    LITERAL = auto()
    EXPRESSION = auto()
    TYPECASTING = auto()
    RECASTING = auto()
    FUNCTION_RETURN = auto()
    COMMENT = auto()

class ASTNode:
    def __init__(self, node_type: NodeType, value: Optional[str] = None, children: Optional[List['ASTNode']] = None):
        self.node_type = node_type
        self.value = value
        self.children = children or []
        
    def __repr__(self, level=0):
        ret = "  " * level + f"{self.node_type.name}"
        if self.value:
            ret += f": {self.value}"
        ret += "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

class SymbolTable:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.loops = {}
    
    def add_variable(self, name: str, type: str):
        self.variables[name] = type
    
    def add_function(self, name: str, params: List[str]):
        self.functions[name] = params
    
    def add_loop(self, name: str):
        self.loops[name] = True

class LOLCODESyntaxAnalyzer:
    def __init__(self, tokens: List[Tuple[str, str, int]]):
        self.tokens = tokens
        self.current_token_index = 0
        self.symbol_table = SymbolTable()

    
    def peek(self) -> Optional[Tuple[str, str, int]]:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None
    
    def consume(self, expected_type: str = None) -> Tuple[str, str, int]:
        while self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            if token[0] == 'NEWLINE' and expected_type != 'NEWLINE':
                self.current_token_index += 1
                continue  # Skip newlines until it see the expected type
            if expected_type and token[0] != expected_type:
                raise SyntaxError(f"Expected {expected_type}, found {token[0]} at line {token[2]}")
            self.current_token_index += 1
            # print(token)
            return token
        raise SyntaxError("Unexpected end of input")
    
    def parse_linebreak(self):
        """Parse <linebreak> ::= \n | \n <linebreak>."""
        if self.peek() and self.peek()[0] == 'NEWLINE':
            self.consume('NEWLINE')
            while self.peek() and self.peek()[0] == 'NEWLINE':
                self.consume('NEWLINE')  # Consume additional linebreaks
            return True
        return False
    
    def parse_program(self) -> ASTNode:
        # self.consume('NEWLINE')
        self.consume('HAI')
        # self.consume('NEWLINE')
        while self.peek() and self.peek()[0] != 'KTHXBYE':
            statement_list = self.parse_statement_list()
        
        self.consume('KTHXBYE')
        return ASTNode(NodeType.PROGRAM, children=[statement_list])
    
    def parse_statement_list(self) -> ASTNode:
        statements = []
        while self.peek() and self.peek()[0] != 'KTHXBYE':
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            
            # Automatically skip newlines
            while self.peek() and self.peek()[0] == 'NEWLINE':
                self.consume('NEWLINE')
        
        return ASTNode(NodeType.STATEMENT_LIST, children=statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        token = self.peek()
        if not token:
            return None
        
        statement_parsers = {
            'VISIBLE': self.parse_print,
            'WAZZUP': self.parse_declaration,
            'R': self.parse_assignment,
            'GIMMEH': self.parse_input,
            'SUM_OF': self.parse_operation,
            'BOTH_SAEM': self.parse_comparison,
            'O_RLY': self.parse_if_statement,
            'WTF?': self.parse_switch_case,
            'IM_IN_YR': self.parse_loop,
            'HOW_IZ_I': self.parse_function_definition,
            'I_IZ': self.parse_function_call,
            'BTW': self.parse_comment,
            'OBTW': self.parse_multi_line_comment,
            'MAEK': self.parse_typecasting,
            'IS_NOW_A': self.parse_recasting,
            'FOUND_YR': self.parse_function_return,
            'VAR_ID': self.parse_assignment
        }
        
        parser = statement_parsers.get(token[0])
        return parser() if parser else None
    
    def parse_print(self) -> ASTNode:
        self.consume('VISIBLE')
        expr = self.parse_expression()
        return ASTNode(NodeType.PRINT, children=[expr])
    
    def parse_declaration(self) -> ASTNode:
        self.consume('WAZZUP')
        # self.consume('NEWLINE')
        
        declarations = []
        while self.peek() and self.peek()[0] != 'BUHBYE':
            self.consume('I_HAS_A')
            var_token = self.consume('VAR_ID')
            
            if self.peek() and self.peek()[0] == 'ITZ':
                self.consume('ITZ')
                value = self.parse_expression()
                declarations.append(ASTNode(NodeType.DECLARATION, value=var_token[1], children=[value]))
                self.symbol_table.add_variable(var_token[1], 'NOOB')
            else:
                declarations.append(ASTNode(NodeType.DECLARATION, value=var_token[1]))
                self.symbol_table.add_variable(var_token[1], 'NOOB')
            
            while self.peek() and self.peek()[0] == 'NEWLINE':
                self.consume('NEWLINE')
        
        self.consume('BUHBYE')
        
        return ASTNode(NodeType.STATEMENT_LIST, children=declarations)
    
    def parse_assignment(self) -> ASTNode:
        var_token = self.consume('VAR_ID')
        self.consume('R')
        value = self.parse_expression()
        return ASTNode(NodeType.ASSIGNMENT, value=var_token[1], children=[value])
    
    def parse_input(self) -> ASTNode:
        self.consume('GIMMEH')
        var_token = self.consume('VAR_ID')
        return ASTNode(NodeType.INPUT, value=var_token[1])
    
    def parse_operation(self) -> ASTNode:
        operations = {
            'SUM_OF': 'SUM',
            'DIFF_OF': 'DIFF',
            'PRODUKT_OF': 'PRODUKT',
            'QUOSHUNT_OF': 'QUOSHUNT',
            'MOD_OF': 'MOD',
            'BIGGR_OF': 'BIGGR',
            'SMALLR_OF': 'SMALLR',
            'SMOOSH': 'SMOOSH'
        }
        
        op_type = self.consume()[0]
        left = self.parse_expression()
        self.consume('AN')
        right = self.parse_expression()
        
        return ASTNode(NodeType.OPERATION, value=operations[op_type], children=[left, right])
    
    def parse_comparison(self) -> ASTNode:
        comparisons = {
            'BOTH_SAEM': 'EQ',
            'DIFFRINT': 'NEQ'
        }
        
        op_type = self.consume()[0]
        left = self.parse_expression()
        self.consume('AN')
        right = self.parse_expression()
        
        return ASTNode(NodeType.COMPARISON, value=comparisons[op_type], children=[left, right])
    
    def parse_expression(self) -> ASTNode:
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected end of input")
        
        if token[0] == 'VAR_ID':
            return ASTNode(NodeType.EXPRESSION, value=self.consume('VAR_ID')[1])
        elif token[0] in {'NUMBR', 'NUMBAR', 'YARN', 'TROOF'}:
            return ASTNode(NodeType.LITERAL, value=self.consume()[1])
        elif token[0] in {'SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF', 'MOD_OF', 'BIGGR_OF', 'SMALLR_OF', 'SMOOSH'}:
            return self.parse_operation()
        elif token[0] in {'BOTH_SAEM', 'DIFFRINT'}:
            return self.parse_comparison()
        elif token[0] == 'MAEK':
            return self.parse_typecasting()
        
        raise SyntaxError(f"Unexpected token in expression: {token}")
    
    def parse_if_statement(self) -> ASTNode:
        condition = self.parse_expression()
        self.consume('O_RLY')
        # self.consume('NEWLINE')
        
        self.consume('YA_RLY')
        # self.consume('NEWLINE')
        true_block = self.parse_statement_list()
        
        alternative_blocks = []
        while self.peek() and self.peek()[0] == 'MEBBE':
            self.consume('MEBBE')
            alt_condition = self.parse_expression()
            # self.consume('NEWLINE')
            alt_block = self.parse_statement_list()
            alternative_blocks.append((alt_condition, alt_block))
        
        false_block = None
        if self.peek() and self.peek()[0] == 'NO_WAI':
            self.consume('NO_WAI')
            # self.consume('NEWLINE')
            false_block = self.parse_statement_list()
        
        self.consume('OIC')
        
        children = [condition, true_block]
        if alternative_blocks:
            children.extend([ASTNode(NodeType.STATEMENT_LIST, children=[cond, block]) for cond, block in alternative_blocks])
        if false_block:
            children.append(false_block)
        
        return ASTNode(NodeType.IF_STATEMENT, children=children)
    
    # Placeholder methods for advanced parsing
    def parse_switch_case(self) -> ASTNode:
        raise NotImplementedError("Switch case parsing not implemented")
    
    def parse_loop(self) -> ASTNode:
        raise NotImplementedError("Loop parsing not implemented")
    
    def parse_function_definition(self) -> ASTNode:
        raise NotImplementedError("Function definition parsing not implemented")
    
    def parse_function_call(self) -> ASTNode:
        raise NotImplementedError("Function call parsing not implemented")
    
    def parse_typecasting(self) -> ASTNode:
        raise NotImplementedError("Typecasting parsing not implemented")
    
    def parse_recasting(self) -> ASTNode:
        raise NotImplementedError("Recasting parsing not implemented")
    
    def parse_function_return(self) -> ASTNode:
        raise NotImplementedError("Function return parsing not implemented")
    
    def parse_comment(self) -> ASTNode:
        self.consume('BTW')
        return ASTNode(NodeType.COMMENT, value=self.consume('MISMATCH')[1])
    
    def parse_multi_line_comment(self) -> ASTNode:
        self.consume('OBTW')
        # Consume until TLDR is found
        comment_parts = []
        while self.peek() and self.peek()[0] != 'TLDR':
            comment_parts.append(self.consume()[1])
        self.consume('TLDR')
        return ASTNode(NodeType.COMMENT, value=' '.join(comment_parts))

class LOLCODEParserGUI:
    def __init__(self, master):
        self.master = master
        master.title("LOLCODE Parser")
        master.geometry("600x500")

        # File selection frame
        self.file_frame = tk.Frame(master)
        self.file_frame.pack(pady=10, padx=10, fill=tk.X)

        self.file_label = tk.Label(self.file_frame, text="Selected File:")
        self.file_label.pack(side=tk.LEFT)

        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(self.file_frame, textvariable=self.file_path, width=40)
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

        # Parse button
        self.parse_button = tk.Button(master, text="Parse LOLCODE", command=self.parse_lolcode)
        self.parse_button.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select LOLCODE File", 
            filetypes=[("LOLCODE Files", "*.lol")]
        )
        if filename:
            self.file_path.set(filename)

    def parse_lolcode(self):
        # Clear previous results
        for text_widget in [self.tokens_text, self.ast_text, self.symbol_text]:
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
            analyzer = LOLCODESyntaxAnalyzer(tokens)
            ast = analyzer.parse_program()

            # Display AST
            self.ast_text.insert(tk.END, "ABSTRACT SYNTAX TREE:\n")
            self.ast_text.insert(tk.END, str(ast))

            # Display Symbol Tables
            self.symbol_text.insert(tk.END, "SYMBOL TABLES:\n")
            self.symbol_text.insert(tk.END, "Variables:\n")
            for var, type in analyzer.symbol_table.variables.items():
                self.symbol_text.insert(tk.END, f"{var}: {type}\n")
            
            self.symbol_text.insert(tk.END, "\nFunctions:\n")
            for func, params in analyzer.symbol_table.functions.items():
                self.symbol_text.insert(tk.END, f"{func}: {params}\n")
            
            self.symbol_text.insert(tk.END, "\nLoops:\n")
            for loop in analyzer.symbol_table.loops:
                self.symbol_text.insert(tk.END, f"{loop}\n")

            print('program parsed successfully!')
        except Exception as e:
            messagebox.showerror("Parsing Error", str(e))

def main():
    root = tk.Tk()
    LOLCODEParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()