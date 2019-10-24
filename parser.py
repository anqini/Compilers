# Yacc example

import ply.yacc as yacc
from nodes import *
# Get the token map from the lexer.  This is required.
from real_lexer import tokens


def p_stmts_stmt(p):
    'stmts : stmt'
    p[0] = Stmts([p[1]])

def p_stmts_more(p):
    'stmts : stmts stmts'
    p[0] = Stmts(p[1].stmts + p[2].stmts)


def p_stmt_expre(p):
    'stmt : expression SEMICO'
    p[0] = Expstmt(p[1])

def p_exps_exp(p):
    'exps : expression'
    p[0] = Exps([p[1]])

def p_exps_comb(p):
    'exps : exps COMMA exps'
    p[0] = Exps(p[1].exps + p[3].exps)

def p_expression_term(p):
    'expression : lit'
    p[0] = Lit(p[1])

def p_expression_binop(p):
    'expression : binop'
    p[0] = p[1]

def p_expression_nop(p):
    'expression : uop'
    p[0] = p[1]

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_var(p):
    'expression : varid'
    p[0] = Varval(p[1])

def p_expression_func_without_param(p):
    'expression : globid LPAREN RPAREN'
    p[0] = Funccall(p[1])

def p_expression_func(p):
    'expression : globid LPAREN exps RPAREN'
    p[0] = Funccall(p[1], p[3])

def p_binop_ops(p):
    '''binop : arith-ops
            | logic-ops'''
    p[0] = p[1]

def p_binop_assign(p):
    'binop : varid ASSIGN expression'
    p[0] = Assign(p[1], p[3])

def p_arithops_exp(p):
    '''arith-ops : expression PLUS expression
       | expression MINUS expression
       | expression TIMES expression
       | expression DIVIDE expression'''
    if p[2] == '+':
        binop = 'add'
    elif p[2] == '-':
        binop = 'sub'
    elif p[2] == '*':
        binop = 'mul'
    elif p[2] == '/':
        binop = 'div'
    else: raise Exception('arith-ops mismatch...')
    p[0] = Binop(binop, p[1], p[3])

def p_logicops_exp(p):
    '''logic-ops : expression EQU expression
       | expression LTH expression
       | expression BTH expression
       | expression AND expression
       | expression OR expression'''
    if p[2] == '==':
        op = 'eq'
    elif p[2] == '>':
        op = 'gt'
    elif p[2] == '<':
        op = 'lt'
    elif p[2] == '||':
        op = 'or'
    elif p[2] == '&&':
        op = 'and'
    else: raise Exception('logic-ops mismatch...')
    p[0] = Binop(op, p[1], p[3])

def p_uop_exp(p):
    '''uop : NEG expression
        | MINUS expression'''
    p[0] = Uop('not', p[2])


def p_globid_ident(p):
    'globid : ident'
    p[0] = p[1]

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser

parser = yacc.yacc()

result = parser.parse("fib(1 + $w, 2);")

print(result)


