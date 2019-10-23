# this file contains all class for node
class ExpBase:
    name = None
    depth = 0
    def __init__(self, name: str):
        self.name = name
    def incDepth(self):
        self.depth += 1
    def set_depth(self, depth):
        self.depth = depth
    
class Vdecl:
    depth = 0
    def __init__(self, typ: str, var: str):
        self.node = 'vdecl'
        self.type = typ
        self.var = var
    def incDepth(self):
        self.depth += 1
    def __str__(self):
        s = '  ' * self.depth + 'node: ' + self.node + '\n'
        s += '  ' * self.depth + 'type: ' + self.type + '\n'
        s += '  ' * self.depth + 'var: ' + self.var + '\n' 
        return s
    def depth(self, depth):
        self.depth = depth
        

class Tdecls(ExpBase):
    def __init__(self, types: list):
        self.name = 'tdecls'
        self.types = types
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'types: ' + '\n'
        for t in self.types:
            s += '  ' * (self.depth + 1) + '- ' + t + '\n'
        return s

class Varval(ExpBase):
    def __init__(self, var: str):
        self.name = 'varval'
        self.var = var
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'var: ' + self.var + '\n'
        return s

class Lit(ExpBase):
    def __init__(self, value):
        self.name = 'lit'
        self.value = value
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'value: ' + str(self.value) + '\n'
        return s

class Uop(ExpBase):
    def __init__(self, op, exp):
        self.name = 'uop'
        self.op = op
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'op: ' + self.op + '\n'
        s += '  ' * self.depth + 'exp: ' + '\n'
        self.exp.set_depth(self.depth + 1)
        s += str(self.exp)
        return s


class Binop(ExpBase):
    def __init__(self, op, lhs, rhs):
        self.name = 'binop'
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'op: ' + self.op + '\n'
        s += '  ' * self.depth + 'lhs: ' + '\n'
        self.lhs.set_depth(self.depth + 1)
        s += str(self.lhs)
        s += '  ' * self.depth + 'rhs: ' + '\n'
        self.rhs.set_depth(self.depth + 1)
        s += str(self.rhs)
        return s

class Assign(ExpBase):
    def __init__(self, var, exp):
        self.name = 'assign'
        self.exp = exp

class Expstmt(ExpBase):
    def __init__(self, exp):
        self.name = 'expstmt'
        self.exp = exp

class Stmts(ExpBase):
    def __init__(self, stmts: list):
        self.name = 'stmts'
        self.stmts = stmts

class IfElse(ExpBase):
    def __init__(self, cond, stmt, else_stmt):
        self.name = 'if'
        self.cond = cond
        self.stmt = stmt
        self.else_stmt = else_stmt

class Blk(ExpBase):
    def __init(self, stmts):
        self.name = 'blk'
        self.contents = stmts
    
class Func(ExpBase):
    def __init__(self, ret_type, globid, blk):
        self.name = 'func'
        self.ret_type = ret_type
        self.globid = globid
        self.blk = blk

class Funcs(ExpBase):
    def __init__(self, funcs):
        self.name = 'funcs'
        self.funcs = funcs
    
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

class Prog(ExpBase):
    def __init__(self, funcs):
        self.name = 'prog'
        self.funcs = funcs

