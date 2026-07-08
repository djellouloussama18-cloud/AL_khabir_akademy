#!/usr/bin/env python3
import re
import sys
from pathlib import Path

# Read the HTML file
html_path = Path('C:/Users/pC/Al khabir Academy/index.html')
content = html_path.read_text(encoding='utf-8', errors='replace')

# Extract script
script_start = content.find('<script>')
script_end = content.find('</script>')
if script_start == -1 or script_end == -1:
    print("Script tags not found")
    sys.exit(1)

script = content[script_start:script_end + 9]
lines = script.split('\n')

print('=' * 80)
print('ALL CONST and LET DECLARATIONS (with line numbers)')
print('=' * 80)

const_declarations = []
let_declarations = []

# Find const declarations
for i, line in enumerate(lines):
    # Match const var = ... (in case we have property access)
    matches = re.finditer(r'\b(const)\s+(\w+)\s*=', line)
    for match in matches:
        line_num = i + 1940
        var_name = match.group(2)
        print(f'Line {line_num}: {match.group(1)} {var_name}')
        const_declarations.append((line_num, var_name))

# Find let declarations
for i, line in enumerate(lines):
    matches = re.finditer(r'\b(let)\s+(\w+)\s*=', line)
    for match in matches:
        line_num = i + 1940
        var_name = match.group(2)
        print(f'Line {line_num}: {match.group(1)} {var_name}')
        let_declarations.append((line_num, var_name))

print()
print('=' * 80)
print('CHECKING FOR DUPLICATES (same scope)')
print('=' * 80)

# Combine all declarations
all_decls = const_declarations + let_declarations
name_to_line = {}

for line_num, name in all_decls:
    if name in name_to_line:
        print(f'DUPLICATE: {name} found at lines {name_to_line[name]} and {line_num}')
    else:
        name_to_line[name] = line_num

# Check specific variables mentioned in the requirements
print('\nChecking variables mentioned in requirements:')
required_vars = ['wilayaEl', 'submitBtn', 'BASE_PRICE', 'DELIVERY_PRICES', 
                 'REMOTE_WILAYAS', 'WILAYAS', 'COMMUNES']

for var in required_vars:
    if var in name_to_line:
        print(f'  ✓ {var}: found at line {name_to_line[var]}')
    else:
        print(f'  ✗ {var}: NOT FOUND!')

print()
print('=' * 80)
print('CHECKING BRACE/PARENTHESIS/BRACKET BALANCE')
print('=' * 80)

braces = 0
parens = 0
brackets = 0
errors = []

for i, line in enumerate(lines):
    line_num = i + 1940
    for j, char in enumerate(line):
        if char == '{':
            braces += 1
        elif char == '}':
            braces -= 1
            if braces < 0:
                errors.append(f'Line {line_num}: Too many }}')
        elif char == '(':
            parens += 1
            # Check for ASI misparse potential - look for consecutive expressions
            if j > 0:
                prev_char = line[j-1]
                # Check for patterns that could cause ASI issues
                if prev_char not in [' ', '\t', ';', '+', '-', '*', '/', ',', '=', '!', '?', ':']:
                    errors.append(f'Line {line_num}: Position {j}: Possible ASI misparse - "{line[max(0,j-5):j+5]}"')
        elif char == ')':
            parens -= 1
            if parens < 0:
                errors.append(f'Line {line_num}: Too many )')
        elif char == '[':
            brackets += 1
        elif char == ']':
            brackets -= 1
            if brackets < 0:
                errors.append(f'Line {line_num}: Too many ]')

if braces == 0 and parens == 0 and brackets == 0:
    print('✓ All braces, parens, and brackets are balanced')
else:
    print(f'✗ Braces: {braces}, Parens: {parens}, Brackets: {brackets}')
    if errors:
        print('✗ Balance errors:')
        for err in errors:
            print(f'  {err}')

print()
print('=' * 80)
print('CHECKING FOR SEMICOLON/COMMA ISSUES (ASI problems)')
print('=' * 80)

# Look for possible ASI issues around const declarations
for i, line in enumerate(lines):
    line_num = i + 1940
    
    # Check if we're in the middle of an expression when a const starts
    prev_has_reachable_code = False
    if i > 0:
        for j in range(len(lines[i-1]) - 1, -1, -1):
            ch = lines[i-1][j]
            if ch in ['}', ')', ']', ';', '+', '-', '*', '/', ',', '=', '!', '?', ':']:
                prev_has_reachable_code = True
                break
            elif ch.isalnum() or ch == '_':
                prev_has_reachable_code = False
                break
    
    # Look for const at start of line (ignoring whitespace)
    trimmed = line.strip()
    if trimmed.startswith('const '):
        if not prev_has_reachable_code and i > 0:
            # Could be ASI issue if the previous line wasn't properly terminated
            # Show context
            print(f'Line {line_num}: const declaration - check previous line for ASI issues')
            print(f'  Context: ...{lines[i-1][-50:]}"')