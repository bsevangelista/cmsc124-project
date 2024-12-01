import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from enum import Enum, auto
from typing import List, Tuple, Optional, Union
from lexical_analyzer import tokenize_lolcode 

# TODO:
#     check for valid tokens - correct spellings
#     check for required token at start of statements (eg, VISIBLE, GIMMEH, WAZZUP) - parse statements
#     check for expected var_id operands in comparison [test case 6]
#     if token is var_id in parse_statements - parse assignment | parse recasting
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
    
    def peek_next(self):
        """
        Peek at the token after the current token without consuming it.
        """
        next_index = self.current_token_index + 1
        if next_index < len(self.tokens):
            return self.tokens[next_index]
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
    
    def expect_newline(self):
        """Ensure that the next token is a NEWLINE and consume it."""
        if self.peek() and self.peek()[0] == 'NEWLINE':
            self.consume('NEWLINE')
        else:
            raise SyntaxError(f"Expected NEWLINE, found {self.peek()[0]} at line {self.peek()[2] if self.peek() else 'EOF'}")

    
    # def parse_linebreak(self):
    #     """Parse <linebreak> ::= \n | \n <linebreak>."""
    #     if self.peek() and self.peek()[0] == 'NEWLINE':
    #         self.consume('NEWLINE')
    #         while self.peek() and self.peek()[0] == 'NEWLINE':
    #             self.consume('NEWLINE')  # Consume additional linebreaks
    #         return True
    #     return False
    
    def parse_program(self) -> ASTNode:
        # self.consume('NEWLINE')
        self.consume('HAI')
        # Enforce a newline after HAI
        if self.peek() and self.peek()[0] == 'NEWLINE':
            self.consume('NEWLINE')
        else:
            raise SyntaxError(f"Expected NEWLINE, found {self.peek()[0]} at line {self.peek()[2]}")

        while self.peek() and self.peek()[0] != 'KTHXBYE':
            statement_list = self.parse_statement_list()
        
        self.consume('KTHXBYE')
        return ASTNode(NodeType.PROGRAM, children=[statement_list])
    
    def parse_statement_list(self, allow_gtfo: bool = False) -> ASTNode:
        """Parse a list of statements with optional GTFO support
        :param allow_gtfo: Whether to allow GTFO (break) statement """
        statements = []
        while self.peek() and self.peek()[0] not in {'KTHXBYE', 'OIC', 'OMGWTF', 'OMG'}:
            
            # Check for GTFO if allowed
            if allow_gtfo and self.peek() and self.peek()[0] == 'GTFO':
                self.consume('GTFO')
                statements.append(ASTNode(NodeType.STATEMENT_LIST, value='BREAK'))
                break
            
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            
            while self.peek() and self.peek()[0] == 'NEWLINE':
                self.expect_newline()
        
        return ASTNode(NodeType.STATEMENT_LIST, children=statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        token = self.peek()
        if not token:
            return None
        if token[0] in {'BOTH_SAEM', 'DIFFRINT'}:  # Check for potential condition
            condition = self.parse_comparison()  # Parse the condition first
            # Expect a NEWLINE after the condition before `O_RLY`
            self.expect_newline()
            if self.peek() and self.peek()[0] == 'O_RLY':  # Verify O_RLY follows the condition
                return self.parse_if_statement(condition)  # Pass condition to parse_if_statement
        
        statement_parsers = {
            'VISIBLE': self.parse_print,
            'WAZZUP': self.parse_declaration,
            'R': self.parse_assignment,
            'GIMMEH': self.parse_input,
            'SUM_OF': self.parse_operation,
            'BOTH_SAEM': self.parse_comparison,
            'DIFFRINT': self.parse_comparison,
            # 'O_RLY': self.parse_if_statement,
            'WTF?': self.parse_switch_case,
            'IM_IN_YR': self.parse_loop,
            'HOW_IZ_I': self.parse_function_definition,
            'I_IZ': self.parse_function_call,
            # 'BTW': self.parse_comment,
            # 'OBTW': self.parse_multi_line_comment,
            'MAEK': self.parse_typecasting,
            'IS_NOW_A': self.parse_recasting,
            'FOUND_YR': self.parse_function_return,
            'VAR_ID': self.handle_var_id,
            'GTFO': lambda: ASTNode(NodeType.STATEMENT_LIST, value='BREAK')  # Break statement
        }
        
        # Get the parser function for the current token
        parser = statement_parsers.get(token[0])
        if parser:
            return parser()  # Call the parser function

        # Handle unrecognized tokens
        raise SyntaxError(f"Unexpected token: {token[0]} at line {token[2]}")
    
    def handle_var_id(self):      
        # next_token = self.peek_next()  # Peek at the next token to decide what to do
        # if next_token and next_token[0] == 'R':
        #     return self.parse_assignment()
        # elif next_token and next_token[0] == 'IS_NOW_A':
        #     return self.parse_recasting()
        # else:
        #     raise SyntaxError(f"Unexpected token after variable: {next_token}")

        var_token = self.consume('VAR_ID')
    
        # Peek next token to determine the type of statement
        next_token = self.peek()
        
        if not next_token:
            # Simple variable reference
            return ASTNode(NodeType.EXPRESSION, value=var_token[1])
        
        if next_token[0] == 'R':
            # Assignment
            self.consume('R')
            value = self.parse_expression()
            return ASTNode(NodeType.ASSIGNMENT, value=var_token[1], children=[value])
        
        if next_token[0] == 'IS_NOW_A':
            # Recasting
            return self.parse_recasting(var_token[1])
        
        # if self.peek() and self.peek()[0] == 'NEWLINE':
        #     self.consume('NEWLINE')
        # else:
        #     raise SyntaxError("FUCKs")
        # If no special handling, treat as simple expression
        return ASTNode(NodeType.EXPRESSION, value=var_token[1])

        
    def parse_print(self) -> ASTNode:
        self.consume('VISIBLE')
        # expr = self.parse_expression()
        # return ASTNode(NodeType.PRINT, children=[expr])
    
        # Support for infinite arity print
        expressions = []
        while True:
            expr = self.parse_expression()
            expressions.append(expr)
            
            # Check if there are more expressions to print
            if self.peek() and self.peek()[0] == 'AN':
                self.consume('AN')
            elif self.peek() and self.peek()[0] == 'CONCAT':
                self.consume('CONCAT')
            elif self.peek() and self.peek()[0] in {
                                                        'SUM_OF': 'SUM',
                                                        'DIFF_OF': 'DIFF',
                                                        'PRODUKT_OF': 'PRODUKT',
                                                        'QUOSHUNT_OF': 'QUOSHUNT',
                                                        'MOD_OF': 'MOD',
                                                        'BIGGR_OF': 'BIGGR',
                                                        'SMALLR_OF': 'SMALLR',
                                                        'SMOOSH': 'SMOOSH'
                                                    }:
                continue
            else:
                break
        
        return ASTNode(NodeType.PRINT, children=expressions)
    
    def parse_declaration(self) -> ASTNode:
        """Parse variable declarations enclosed in WAZZUP and BUHBYE."""
        self.consume('WAZZUP')  # Consume the declaration start token
        
        declarations = []
        
        while self.peek() and self.peek()[0] != 'BUHBYE':
            self.consume('I_HAS_A')
            var_token = self.consume('VAR_ID')
            # Parse optional initialization with ITZ
            if self.peek() and self.peek()[0] == 'ITZ':
                self.consume('ITZ')
                value = self.parse_expression()
                inferred_type = self.infer_type(value)  # Infer the type from the expression
                declarations.append(ASTNode(NodeType.DECLARATION, value=var_token[1], children=[value]))
                self.symbol_table.add_variable(var_token[1], inferred_type)
            else:
                declarations.append(ASTNode(NodeType.DECLARATION, value=var_token[1], children=[]))
                self.symbol_table.add_variable(var_token[1], 'NOOB')  # Default type if no value
            
            # Ensure NEWLINE after each declaration
            self.expect_newline()
        
        # Consume the end token
        self.consume('BUHBYE')
        
        return ASTNode(NodeType.STATEMENT_LIST, children=declarations)
    
    def infer_type(self, value: ASTNode) -> str:
        """Infer the type of a variable based on its initial value."""
        if value.node_type == NodeType.LITERAL:
            if isinstance(value.value, int):
                return 'NUMBR'
            elif isinstance(value.value, float):
                return 'NUMBAR'
            elif isinstance(value.value, str):
                return  
            elif isinstance(value.value, bool):
                return 'TROOF'
        return 'NOOB'  # Default type
    
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

        # Special handling for SMOOSH with infinite arity
        if op_type == 'SMOOSH':
            expressions = []
            while True:
                expr = self.parse_expression()
                expressions.append(expr)
                
                # Check if there are more expressions
                if self.peek() and self.peek()[0] == 'AN':
                    self.consume('AN')
                else:
                    break
            
            return ASTNode(NodeType.OPERATION, value=operations[op_type], children=expressions)
    
        # Existing binary operation parsing
        left = self.parse_expression()
        self.consume('AN')
        right = self.parse_expression()

        # Support for additional expressions in some operations (like MOD_OF)
        # additional_expressions = []
        # while self.peek() and self.peek()[0] == 'AN':
        #     self.consume('AN')
        #     additional_expr = self.parse_expression()
        #     additional_expressions.append(additional_expr)
        
        # # Combine expressions
        # children = [left, right] + additional_expressions
        
        # return ASTNode(NodeType.OPERATION, value=operations[op_type], children=children)
        
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
        
        # Add boolean expression handling
        boolean_ops = {
            'NOT', 'BOTH_OF', 'EITHER_OF', 'WON_OF', 
            'ALL_OF', 'ANY_OF'
        }
        
        if token[0] == 'VAR_ID':
            return ASTNode(NodeType.EXPRESSION, value=self.consume(token[0])[1])
        elif token[0] in {'NUMBR', 'NUMBAR', 'YARN', 'TROOF'}:
            return ASTNode(NodeType.LITERAL, value=self.consume(token[0])[1])
        elif token[0] in boolean_ops:
            return self.parse_boolean_expr()
        elif token[0] in {'SUM_OF', 'DIFF_OF', 'PRODUKT_OF', 'QUOSHUNT_OF', 'MOD_OF', 'BIGGR_OF', 'SMALLR_OF', 'SMOOSH'}:
            return self.parse_operation()
        elif token[0] in {'BOTH_SAEM', 'DIFFRINT'}:
            return self.parse_comparison()
        elif token[0] == 'MAEK':
            return self.parse_typecasting()
        
        raise SyntaxError(f"Unexpected token in expression: {token}")
    
    def parse_boolean_expr(self) -> ASTNode:
        """ Parse complex boolean expressions in LOLCODE """
        token = self.peek()
        
        # Handle basic boolean literals
        if token[0] in {'TROOF'}:
            return ASTNode(NodeType.LITERAL, value=self.consume()[1])
        
        # Handle NOT operation
        if token[0] == 'NOT':
            self.consume('NOT')
            expr = self.parse_boolean_expr()
            return ASTNode(NodeType.BOOLEAN_OPERATION, value='NOT', children=[expr])
        
        # Handle binary boolean operations
        binary_ops = {
            'BOTH_OF': 'AND',
            'EITHER_OF': 'OR',
            'WON_OF': 'XOR'
        }
        
        if token[0] in binary_ops:
            op = self.consume()[0]
            left = self.parse_boolean_expr()
            self.consume('AN')
            right = self.parse_boolean_expr()
            return ASTNode(NodeType.BOOLEAN_OPERATION, 
                        value=binary_ops[op], 
                        children=[left, right])
        
        # Handle multi-arity operations: ALL OF and ANY OF
        if token[0] in {'ALL_OF', 'ANY_OF'}:
            op = self.consume()[0]
            expressions = []
            
            # Collect expressions until MKAY
            while self.peek() and self.peek()[0] != 'MKAY':
                expr = self.parse_boolean_expr()
                expressions.append(expr)
                
                # Consume AN if present
                if self.peek() and self.peek()[0] == 'AN':
                    self.consume('AN')
            
            # Consume MKAY
            self.consume('MKAY')
            
            return ASTNode(NodeType.BOOLEAN_OPERATION, 
                        value='ALL' if op == 'ALL_OF' else 'ANY', 
                        children=expressions)
        
        # Recursive handling of nested boolean expressions
        if token[0] == 'BOTH_OF':
            self.consume('BOTH_OF')
            left = self.parse_boolean_expr()
            self.consume('AN')
            right = self.parse_boolean_expr()
            return ASTNode(NodeType.BOOLEAN_OPERATION, value='AND', children=[left, right])
        
        if token[0] == 'EITHER_OF':
            self.consume('EITHER_OF')
            left = self.parse_boolean_expr()
            self.consume('AN')
            right = self.parse_boolean_expr()
            return ASTNode(NodeType.BOOLEAN_OPERATION, value='OR', children=[left, right])
        
        # Fallback to regular expression parsing
        return self.parse_expression()
    
    def parse_if_statement(self, condition: ASTNode) -> ASTNode:
        """Parse an if-then statement, starting after the condition."""
        self.consume('O_RLY')  # Consume O_RLY
        self.expect_newline()

        # Parse YA_RLY and the true block
        self.consume('YA_RLY')
        self.expect_newline()
        true_block = []
        while self.peek() and self.peek()[0] not in {'MEBBE', 'NO_WAI', 'OIC'}:
            data = self.parse_statement()
            print(data)
            true_block.append(data)
            self.expect_newline()
        
        # Parse MEBBE blocks (optional)
        alternative_blocks = []
        while self.peek() and self.peek()[0] == 'MEBBE':
            self.consume('MEBBE')
            alt_condition = self.parse_expression()
            alt_block = []  # Initialize alt_block inside the loop
            self.expect_newline()
            while self.peek() and self.peek()[0] not in {'MEBBE', 'NO_WAI', 'OIC'}:
                alt_block.append(self.parse_statement())
                self.expect_newline()
            alternative_blocks.append((alt_condition, alt_block))

        # Parse NO_WAI block (optional)
        false_block = []
        if self.peek() and self.peek()[0] == 'NO_WAI':
            self.consume('NO_WAI')
            self.expect_newline()
            while self.peek() and self.peek()[0] != 'OIC':
                false_block.append(self.parse_statement())
                self.expect_newline()

        # Consume OIC to close the if-then statement
        if self.peek() and self.peek()[0] == 'OIC':
            self.consume('OIC')
            self.expect_newline()
        else:
            raise SyntaxError("Expected OIC to close the if-then statement")

        # Construct AST node
        children = [condition, ASTNode(NodeType.STATEMENT_LIST, children=true_block)]
        if alternative_blocks:
            for cond, block in alternative_blocks:
                assert isinstance(cond, ASTNode), f"Invalid condition: {cond}"
                assert all(isinstance(stmt, ASTNode) for stmt in block), f"Invalid block: {block}"
                
                alternative_node = ASTNode(NodeType.STATEMENT_LIST, children=[cond, ASTNode(NodeType.STATEMENT_LIST, children=block)])
                children.append(alternative_node)
        if false_block:
            children.append(ASTNode(NodeType.STATEMENT_LIST, children=false_block))

        return ASTNode(NodeType.IF_STATEMENT, children=children)


    
    # Placeholder methods for advanced parsing
    def parse_switch_case(self) -> ASTNode:
        """Parse switch-case (WTF?) statement with enhanced support for VAR_ID condition"""
        self.consume('WTF?')
        
        # Support VAR_ID as a direct condition
        expr = self.parse_expression()
        
        cases = []
        default_case = None

        while self.peek() and self.peek()[0] == 'OMG':
            self.consume('OMG')
            case_value = self.parse_expression()  # Use parse_expression instead of consume
            case_block = self.parse_statement_list(allow_gtfo=True)  # Allow GTFO in case blocks
            cases.append((case_value, case_block))
        
        if self.peek() and self.peek()[0] == 'OMGWTF':
            self.consume('OMGWTF')
            default_case = self.parse_statement_list(allow_gtfo=True)
        
        self.consume('OIC')
        
        children = [expr]
        children.extend([
            ASTNode(NodeType.STATEMENT_LIST, children=[case_value, case_block]) 
            for case_value, case_block in cases
        ])
        
        if default_case:
            children.append(default_case)
        
        return ASTNode(NodeType.SWITCH_CASE, children=children)
    
    def parse_loop(self) -> ASTNode:
        """Parse loop (IM IN YR) statement"""
        self.consume('IM_IN_YR')
        loop_name = self.consume('VAR_ID')[1]
        
        # Optional loop condition mode
        mode = None
        if self.peek() and self.peek()[0] in {'UPPIN', 'NERFIN'}:
            mode = self.consume()[0]
            self.consume('YR')
            var_token = self.consume('VAR_ID')
        
        # Optional condition
        condition = None
        if self.peek() and self.peek()[0] == 'WILE':
            self.consume('WILE')
            condition = self.parse_expression()
        
        # Loop body
        body = self.parse_statement_list()
        
        # Closing loop
        self.consume('IM_OUTTA_YR')
        self.consume('VAR_ID')  # Match loop name
        
        # Add loop to symbol table
        self.symbol_table.add_loop(loop_name)
        
        return ASTNode(NodeType.LOOP, value=loop_name, children=[
            ASTNode(NodeType.LITERAL, value=mode) if mode else None,
            condition,
            body
        ])
    
    def parse_function_definition(self) -> ASTNode:
        """Parse function definition (HOW IZ I)"""
        self.consume('HOW_IZ_I')
        func_name = self.consume('VAR_ID')[1]
        
        # Parameters
        params = []
        if self.peek() and self.peek()[0] == 'YR':
            while self.peek() and self.peek()[0] == 'YR':
                self.consume('YR')
                param = self.consume('VAR_ID')[1]
                params.append(param)
        
        # Function body
        body = self.parse_statement_list()
        
        # Closing
        self.consume('IF_U_SAY_SO')
        
        # Add to symbol table
        self.symbol_table.add_function(func_name, params)
        
        return ASTNode(NodeType.FUNCTION_DEFINITION, 
                       value=func_name, 
                       children=[
                           ASTNode(NodeType.STATEMENT_LIST, children=[
                               ASTNode(NodeType.LITERAL, value=param) for param in params
                           ]),
                           body
                       ])
    
    def parse_function_call(self) -> ASTNode:
        """Parse function call (I IZ)"""
        self.consume('I_IZ')
        func_name = self.consume('VAR_ID')[1]
        
        # Arguments
        args = []
        if self.peek() and self.peek()[0] == 'YR':
            while self.peek() and self.peek()[0] == 'YR':
                self.consume('YR')
                arg = self.parse_expression()
                args.append(arg)
        
        return ASTNode(NodeType.FUNCTION_CALL, 
                       value=func_name, 
                       children=args)
    
    def parse_typecasting(self) -> ASTNode:
        """Parse typecasting (MAEK) operation"""
        self.consume('MAEK')
        self.consume('A')
        expr = self.parse_expression()
        type_token = self.consume()
        
        # Validate type
        valid_types = {'NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'TYPE'}
        if type_token[0] not in valid_types:
            raise SyntaxError(f"Invalid type for typecasting: {type_token[0]}")
        
        return ASTNode(NodeType.TYPECASTING, value=type_token[1], children=[expr])

    
    def parse_recasting(self, var_name: str) -> ASTNode:
        """Parse recasting (IS NOW A) operation""" 
        self.consume('IS_NOW_A')
        type_token = self.consume()
        
        # Validate type
        valid_types = {'NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'TYPE'}
        if type_token[0] not in valid_types:
            raise SyntaxError(f"Invalid type for recasting: {type_token[0]}")
        
        # Update symbol table
        self.symbol_table.add_variable(var_name, type_token[1])
        
        return ASTNode(NodeType.RECASTING, value=type_token[1], children=[
            ASTNode(NodeType.EXPRESSION, value=var_name)
        ])
    
    def parse_function_return(self) -> ASTNode:
        """Parse function return (FOUND YR)"""
        self.consume('FOUND_YR')
        return_value = self.parse_expression()
        
        return ASTNode(NodeType.FUNCTION_RETURN, children=[return_value])
    
    # def parse_comment(self) -> ASTNode:
    #     self.consume('BTW')
    #     return ASTNode(NodeType.COMMENT, value=self.consume('MISMATCH')[1])
    
    # def parse_multi_line_comment(self) -> ASTNode:
    #     self.consume('OBTW')
    #     # Consume until TLDR is found
    #     comment_parts = []
    #     while self.peek() and self.peek()[0] != 'TLDR':
    #         comment_parts.append(self.consume()[1])
    #     self.consume('TLDR')
    #     return ASTNode(NodeType.COMMENT, value=' '.join(comment_parts))

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