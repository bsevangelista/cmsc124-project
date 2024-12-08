import re
from LOLCODE_Token import LOLToken 

# Compile patterns into a single regex
token_patterns = []
for name, pattern in LOLToken: 
    token_patterns.append(f'(?P<{name}>{pattern})')
token_regex = re.compile('|'.join(token_patterns), re.S)

def tokenize_lolcode(source_code):
    tokens = []
    line_number = 1
    comment = False
    start_line = 0
    end_line = 0
    
    for match in re.finditer(token_regex, source_code):
        kind = match.lastgroup # Type of token
        value = match.group(kind) # Token

        if kind == 'WHITESPACE' or kind == 'NEWLINE':
            if kind == 'NEWLINE':
                line_number += 1  # Track line numbers
                tokens.append((kind, '\\n', line_number))
            continue  # Skip whitespace and newlines
        elif kind == 'SINGLE_LINE_COMMENT':
            comment_text = value[4:]  # Skip "BTW"
        elif kind == 'OBTW':
            comment = True
            start_line = line_number
        elif kind == 'TLDR':
            comment = False
            end_line = line_number
        elif kind == 'MISMATCH':
            if comment == False:
                raise SyntaxError(f"Unexpected character {value} at line {line_number}")

        else:
            if comment == False:
                tokens.append((kind, value, line_number))

    for token in tokens:
        # Check if a token is aligned with a multiline comment
        if (start_line <= token[2] <= end_line) and token[0] != 'NEWLINE':
            raise SyntaxError("Error: multiline comments should have its own line")
    return tokens