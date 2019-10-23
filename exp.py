# this file contains all class for node
class ExpBase:
    name = None
    depth = 0
    def __init__(self, name: str):
        self.name = name

class Vdecl:
    depth = 0
    def __init__(self, node, typ, var):
        self.node = 'vdecl'
        self.type = typ
        self.var = var

class Tdecls(ExpBase):
    def __init__(self, types: list):
        self.name = 'tdecls'
        self.types = types

class Varval(ExpBase):
    def __init__(self, var: str):
        self.name = 'varval'
        self.var = var

class Lit(ExpBase):
    def __init__(self, value):
        self.name = 'lit'
        self.value = value

class Uop(ExpBase):
    def __init__(self, op, exp):
        self.name = 'uop'
        self.op = op
        self.exp = exp

class Binop(ExpBase):
    def __init__(self, op, lhs, rhs):
        self.name = 'binop'
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

class Assign(ExpBase):
    def __init__(self, var, exp):
        self.name = 'assign'
        self.exp = exp

class Expstmt(ExpBase):
    def __init__(self, exp):
        self.name = 'expstmt'
        self.exp = exp

    
class Vdecls(ExpBase):
    def __init__(self, vars: list):
        self.name = 'vdecls'
        self.vars = vars

class Extern(ExpBase):
    def __init__(self, ret_type, globid, tdecls):
        self.name = 'extern'
        self.ret_type = ret_type
        self.globid = globid
        self.tdecls = tdecls

class Externs(ExpBase):
    def __init__(self, externs: list):
        self.name = 'externs'
        self.externs = externs

