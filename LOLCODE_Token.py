LOLToken = [
    # Comments
    ('SINGLE_LINE_COMMENT', r'BTW[^\n]*'),  # Single-line comments
    
    # Keywords (Program start/end)
    ('HAI', r'\bHAI\b'),
    ('KTHXBYE', r'\bKTHXBYE\b'),
    ('WAZZUP', r'\bWAZZUP\b'),
    ('BUHBYE', r'\bBUHBYE\b'),

    # Keywords (Comments)
    ('BTW', r'\bBTW\b'),
    ('OBTW', r'\bOBTW\b'),
    ('TLDR', r'\bTLDR\b'),

    # Keywords (Variables)
    ('I_HAS_A', r'\bI HAS A\b'),
    ('ITZ', r'\bITZ\b'),
    ('R', r'\bR\b'),

    # Keywords (Operators)
    ('SUM_OF', r'\bSUM OF\b'),
    ('DIFF_OF', r'\bDIFF OF\b'),
    ('PRODUKT_OF', r'\bPRODUKT OF\b'),
    ('QUOSHUNT_OF', r'\bQUOSHUNT OF\b'),
    ('MOD_OF', r'\bMOD OF\b'),
    ('BIGGR_OF', r'\bBIGGR OF\b'),
    ('SMALLR_OF', r'\bSMALLR OF\b'),
    ('BOTH_OF', r'\bBOTH OF\b'),
    ('EITHER_OF', r'\bEITHER OF\b'),
    ('WON_OF', r'\bWON OF\b'),
    ('NOT', r'\bNOT\b'),
    ('ANY_OF', r'\bANY OF\b'),
    ('ALL_OF', r'\bALL OF\b'),
    ('BOTH_SAEM', r'\bBOTH SAEM\b'),
    ('DIFFRINT', r'\bDIFFRINT\b'),

    # Keywords (Miscellaneous)
    ('SMOOSH', r'\bSMOOSH\b'),
    ('MAEK', r'\bMAEK\b'),
    ('A', r'\bA\b'),
    ('AN', r'\bAN\b'),
    ('IS_NOW_A', r'\bIS NOW A\b'),
    ('VISIBLE', r'\bVISIBLE\b'),
    ('GIMMEH', r'\bGIMMEH\b'),

    # Keywords (Conditionals)
    ('O_RLY', r'\bO RLY\?'),
    ('YA_RLY', r'\bYA RLY\b'),
    ('MEBBE', r'\bMEBBE\b'),
    ('NO_WAI', r'\bNO WAI\b'),
    ('WTF', r'\bWTF\?'),
    ('OMGWTF', r'\bOMGWTF\b'),
    ('OMG', r'\bOMG\b'),
    ('OIC', r'\bOIC\b'),

    # Keywords (Loops)
    ('IM_IN_YR', r'\bIM IN YR\b'),
    ('UPPIN', r'\bUPPIN\b'),
    ('NERFIN', r'\bNERFIN\b'),
    ('YR', r'\bYR\b'),
    ('TIL', r'\bTIL\b'),
    ('WILE', r'\bWILE\b'),
    ('IM_OUTTA_YR', r'\bIM OUTTA YR\b'),

    # Keywords (Functions)
    ('HOW_IZ_I', r'\bHOW IZ I\b'),
    ('IF_U_SAY_SO', r'\bIF U SAY SO\b'),
    ('GTFO', r'\bGTFO\b'),
    ('FOUND_YR', r'\bFOUND YR\b'),
    ('I_IZ', r'\bI IZ\b'),
    ('MKAY', r'\bMKAY\b'),

    # Literals
    ('NUMBAR', r'\b-?[0-9]+\.[0-9]+\b'),  # Float literal
    ('NUMBR', r'\b-?[0-9]+\b'),  # Integer literal
    ('YARN', r'"[^"]*"'),  # String literal
    ('TROOF', r'\b(WIN|FAIL)\b'),  # Boolean literal
    ('TYPE', r'\b(NOOB|NUMBR|NUMBAR|YARN|TROOF)\b'),  # Data types

    # Identifiers
    ('VAR_ID', r'\b[a-zA-Z][a-zA-Z0-9_]*\b'),  # Variable identifier
    ('FUNC_ID', r'\b[a-zA-Z][a-zA-Z0-9_]*\b'),  # Function identifier
    ('LOOP_ID', r'\b[a-zA-Z][a-zA-Z0-9_]*\b'),  # Loop identifier

    # Whitespace and others
    ('CONCAT', r'\+'),  
    ('WHITESPACE', r'[ \t]+'),  # Spaces and tabs
    ('NEWLINE', r'\n'),  #  Newlines
    ('MISMATCH', r'.'),  # Any character  
]