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

    for match in re.finditer(token_regex, source_code):
        # print(match)
        kind = match.lastgroup # Type of token
        # print(line_number,kind)
        value = match.group(kind) # Token
        # print(line_number,value)
        if kind == 'WHITESPACE' or kind == 'NEWLINE':
            if kind == 'NEWLINE':
                line_number += 1  # Track line numbers
                tokens.append((kind, '\\n', line_number))
            continue  # Skip whitespace and newlines
        elif kind in {'SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT'}:
            # Extract and process the comment text
            if kind == 'SINGLE_LINE_COMMENT':
                comment_text = value[4:]  # Skip "BTW"
            elif kind == 'MULTI_LINE_COMMENT':
                comment_text = value[4:-4]  # Skip "OBTW" and "TLDR"
                # Count the number of newline characters in the multi-line comment
                num_newlines = comment_text.count('\n')
                line_number += num_newlines  # Increment line_number by the number of newlines
        elif kind == 'MISMATCH':
            print(f"Unexpected character {value} at line {line_number}")

        else:
            tokens.append((kind, value, line_number))
    return tokens