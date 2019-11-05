# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex
import sys
# List of token names.   This is always required
tokens = [
'PLUS',
'MINUS',
'TIMES',
'DIVIDE',
'BTH', # bigger than
'LTH', # less than
'AND', # and
'OR', # or
'LPAREN',
'RPAREN',
'LBRACE',
'RBRACE',
'LBRACK',
'RBRACK',
'COMMA',
'SEMICO',
'EQU',
'ASSIGN',
'NEG',
'flit',
'lit',
'slit',
'type_base',
'ident',
'varid',
]


# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_BTH     = r'\>'
t_LTH     = r'\<'
t_AND    = r'\&\&'
t_OR     = r'\|\|'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_LBRACK  = r'\['
t_RBRACK  = r'\]'
t_COMMA   = r','
t_SEMICO  = r';'
t_EQU     = r'=='
t_ASSIGN  = r'='
t_NEG     = r'!'

# some keywords
reserved = {
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'int' : 'INT',
    'cint' : 'CINT',
    'float' : 'FLOAT',
    'bool' : 'BOOL',
    'void' : 'VOID',
    'ref' : 'REF',
    'noalias' : 'NOALIAS',
    'def' : 'DEF',
    'print' : 'PRINT',
    'extern' : 'EXTERN',
    'return': 'RET'
 }


def t_flit(t):
    r'[0-9]+\.[0-9]+'
    t.value = float(t.value)
    return t

def t_lit(t):
    r'true|false|[0-9]+'
    if t.value == 'true':
        t.value = True
        return t
    elif t.value == 'false':
        t.value = false
        return t
    else:
        t.value = int(t.value)
        return t


def t_slit(t):
    r'"[^"\n\r]*"'
    # t.value = t.value[1:-1]
    return t

def t_ident(t):
    r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ident')    # Check for reserved words
    return t

def t_varid(t):
    r'\$[a-zA-Z_]+[a-zA-Z0-9_]*'
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'
t_ignore_COMMENT = r'\#.*'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    sys.exit(1)
    t.lexer.skip(1)

tokens = list(reserved.values()) + tokens
# Build the lexer
lexer = lex.lex()

# if __name__ == '__main__':
#     # Test it out
#     data = ''
#     with open(sys.argv[1], 'r') as my_file:
#         data += (my_file.read())
#     # Give the lexer some input
#     lexer.input(data)

#     # Tokenize
#     while True:
#         tok = lexer.token()
#         if not tok: 
#             break      # No more input
#         print(tok)
