# Yacc example

import ply.yacc as yacc
from nodes import *
# Get the token map from the lexer.  This is required.
from real_lexer import tokens
import sys

def p_prog_with_externs(p):
    'prog : externs funcs'
    p[0] = Prog(p[2], p[1])

def p_prog_without_externs(p):
    'prog : funcs'
    p[0] = Prog(p[1])

def p_externs_single(p):
    'externs : extern'
    p[0] = Externs([p[1]])

def p_externs_more(p):
    'externs : externs externs'
    p[0] = Externs(p[1].externs + p[2].externs)

def p_extern_with_param(p):
    'extern : EXTERN type globid LPAREN tdecls RPAREN SEMICO'
    p[0] = Extern(p[2], p[3], p[5])

def p_extern_without_param(p):
    'extern : EXTERN type globid LPAREN RPAREN SEMICO'
    p[0] = Extern(p[2], p[3])

def p_funcs_single(p):
    'funcs : function'
    p[0] = Funcs([p[1]])

def p_funcs_more(p):
    'funcs : funcs funcs'
    p[0] = Funcs(p[1].funcs + p[2].funcs)

def p_func_blk(p):
    'function : DEF type globid LPAREN vdecls RPAREN blk'
    p[0] = Func(p[2], p[3], p[7], p[5])

def p_func_blk_noparam(p):
    'function : DEF type globid LPAREN RPAREN blk'
    p[0] = Func(p[2], p[3], p[6])

def p_blk_stmt(p):
    'blk : LBRACE stmts RBRACE'
    p[0] = Blk(p[2])

def p_blk_empty(p):
    'blk : LBRACE RBRACE'
    p[0] = Blk()

def p_stmts_stmt(p):
    'stmts : stmt'
    p[0] = Stmts([p[1]])

def p_stmts_more(p):
    'stmts : stmts stmts'
    p[0] = Stmts(p[1].stmts + p[2].stmts)

def p_stmt_blk(p):
    'stmt : blk'
    p[0] = p[1]

def p_stmt_expre(p):
    'stmt : expression SEMICO'
    p[0] = Expstmt(p[1])

def p_stmt_vdecl(p):
    'stmt : vdecl ASSIGN expression SEMICO'
    p[0] = Vardeclstmt(p[1], p[3])

def p_stmt_printslit(p):
    'stmt : PRINT slit SEMICO'
    p[0] = Printslit(p[2])

def p_stmt_print(p):
    'stmt : PRINT expression SEMICO'
    p[0] = SpecialFunc('print', p[2])

def p_stmt_ret(p):
    'stmt : RET expression SEMICO'
    p[0] = SpecialFunc('ret', p[2])

def p_stmt_ret_none(p):
    'stmt : RET SEMICO'
    p[0] = SpecialFunc('ret')

def p_stmt_if(p):
    'stmt : IF LPAREN expression RPAREN stmt '
    p[0] = IfElse(p[3], p[5])

def p_stmt_ifelse(p):
    'stmt : IF LPAREN expression RPAREN stmt ELSE stmt'
    p[0] = IfElse(p[3], p[5], p[7])

def p_stmt_while(p):
    'stmt : WHILE LPAREN expression RPAREN stmt'
    p[0] = While(p[3], p[5])

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

def p_expression_typecase(p):
    'expression : LBRACK type RBRACK expression'
    p[0] = Caststmt(p[2], p[4])

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


def p_type_basic(p):
    '''type : INT 
            | CINT 
            | FLOAT 
            | BOOL 
            | VOID'''
    p[0] = p[1]

def p_type_ref(p):
    'type : REF type'
    p[0] = p[1] + ' ' + p[2]

def p_type_ref_noalias(p):
    'type : NOALIAS REF type'
    p[0] = ' '.join(p[1:])

def p_tdecl_single(p):
    'tdecls : type'
    p[0] = Tdecls([p[1]])

def p_tdecl_more(p):
    'tdecls : tdecls COMMA tdecls'
    p[0] = Tdecls(p[1].types + p[3].types)

def p_vdecls_single(p):
    'vdecls : vdecl'
    p[0] = Vdecls([p[1]])

def p_vdecls_more(p):
    'vdecls : vdecls COMMA vdecls'
    p[0] = Vdecls(p[1].vars + p[3].vars)

def p_vdecl_var(p):
    'vdecl : type varid'
    p[0] = Vdecl(p[1], p[2])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser

parser = yacc.yacc()

data = sys.stdin.read()

result = parser.parse(data)

print(result)


