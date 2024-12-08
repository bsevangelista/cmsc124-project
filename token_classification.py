LEXEME_CLASSIFICATIONS = {
    # Program Structure Keywords
    'HAI': 'Program Start',
    'KTHXBYE': 'Program End',
    'WAZZUP': 'Global Scope Start',
    'BUHBYE': 'Global Scope End',

    # Comment Keywords
    'BTW': 'Single-line Comment Marker',
    'OBTW': 'Multi-line Comment Start',
    'TLDR': 'Multi-line Comment End',

    # Variable Declaration and Assignment
    'I_HAS_A': 'Variable Declaration',
    'ITZ': 'Variable Initialization',
    'R': 'Assignment Operator',

    # Arithmetic Operators
    'SUM_OF': 'Addition Operator',
    'DIFF_OF': 'Subtraction Operator', 
    'PRODUKT_OF': 'Multiplication Operator',
    'QUOSHUNT_OF': 'Division Operator',
    'MOD_OF': 'Modulo Operator',
    'BIGGR_OF': 'Maximum Operator',
    'SMALLR_OF': 'Minimum Operator',

    # Logical Operators
    'BOTH_OF': 'Logical AND',
    'EITHER_OF': 'Logical OR',
    'WON_OF': 'Logical XOR',
    'NOT': 'Logical NOT',
    'ANY_OF': 'Logical Reduction OR',
    'ALL_OF': 'Logical Reduction AND',
    'BOTH_SAEM': 'Equality Comparison',
    'DIFFRINT': 'Inequality Comparison',

    # Miscellaneous Keywords
    'SMOOSH': 'String Concatenation',
    'MAEK': 'Type Casting',
    'A': 'Type Indicator',
    'AN': 'Argument Separator',
    'IS_NOW_A': 'Type Conversion',
    'VISIBLE': 'Print Statement',
    'GIMMEH': 'Input Statement',

    # Conditional Keywords
    'O_RLY': 'Conditional Start',
    'YA_RLY': 'If Condition',
    'MEBBE': 'Else If Condition',
    'NO_WAI': 'Else Condition',
    'WTF': 'Switch Statement Start',
    'OMG': 'Case Matching',
    'OMGWTF': 'Default Case',
    'OIC': 'Conditional/Switch End',

    # Loop Keywords
    'IM_IN_YR': 'Loop Start',
    'UPPIN': 'Loop Increment',
    'NERFIN': 'Loop Decrement',
    'YR': 'Loop Variable',
    'TIL': 'Loop Until Condition',
    'WILE': 'Loop While Condition',
    'IM_OUTTA_YR': 'Loop End',

    # Function Keywords
    'HOW_IZ_I': 'Function Definition Start',
    'IF_U_SAY_SO': 'Function Definition End',
    'GTFO': 'Early Return/Exit',
    'FOUND_YR': 'Return Statement',
    'I_IZ': 'Function Call',
    'MKAY': 'Function/Argument List Terminator',

    # Literals and Types
    'NUMBAR': 'Float Literal',
    'NUMBR': 'Integer Literal',
    'YARN': 'String Literal',
    'TROOF': 'Boolean Literal',
    'TYPE': 'Data Type Keyword',
    'NOOB': 'Uninitialized Type',

    # Identifiers
    'VAR_ID': 'Variable Identifier',
    'FUNC_ID': 'Function Identifier',
    'LOOP_ID': 'Loop Identifier',

    # Miscellaneous Symbols
    'CONCAT': 'Concatenation Symbol',
    'WHITESPACE': 'Whitespace',
    'NEWLINE': 'Line Break',
    'MISMATCH': 'Unrecognized Token',

    # Supplementary Keywords
    'A': 'Auxiliary Keyword',
    'AN': 'Auxiliary Keyword'
}
