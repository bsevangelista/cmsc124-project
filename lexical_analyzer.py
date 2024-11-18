import re
from LOLCODE_Token import LOLToken 

# Compile patterns into a single regex
token_patterns = []
for name, pattern in LOLToken: 
    token_patterns.append(f'(?P<{name}>{pattern})')
token_regex = '|'.join(token_patterns)

def tokenize_lolcode(source_code):
    tokens = []
    line_number = 1

    for match in re.finditer(token_regex, source_code):
        # print(match)
        kind = match.lastgroup # Type of token
        # print(line_number,kind)
        value = match.group(kind) # Token
        # print(line_number,value)
        if kind == 'WHITESPACE' or kind == 'NEWLINE':
            if kind == 'NEWLINE':
                line_number += 1  # Track line numbers
            continue  # Skip whitespace and newlines
        elif kind == 'MISMATCH':
            print(f"Unexpected character {value} at line {line_number}")
        tokens.append((kind, value, line_number))
    return tokens

lolcode_program = """
HAI
I HAS A VAR ITZ 10
VISIBLE "HELLO WORLD"
KTHXBYE
"""

tokens = tokenize_lolcode(lolcode_program)
for token in tokens:
    print(token)
