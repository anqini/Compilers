# this file contains all class for node
class ExpBase:
    ''' 
    this is the base class of all classes except vdecl
    it contains 'name' and 'depth'
    name is the name of the instance
    depth is the level of node in the tree, which helps to produce indentation
    '''
    name = None
    depth = 0
    # init name
    def __init__(self, name: str):
        self.name = name
    # increment depth
    def incDepth(self):
        self.depth += 1
    # setter
    def set_depth(self, depth):
        self.depth = depth
    
# the classs is for variable declear
class Vdecl(ExpBase):
    def __init__(self, typ: str, var: str):
        self.node = 'vdecl'
        self.type = typ
        self.var = var
    def __str__(self):
        s = '  ' * self.depth + 'node: ' + self.node + '\n'
        s += '  ' * self.depth + 'type: ' + self.type + '\n'
        s += '  ' * self.depth + 'var: ' + self.var + '\n' 
        return s

# a group of variable declearation       
class Vdecls(ExpBase):
    def __init__(self, vars: list):
        self.name = 'vdecls'
        self.vars = vars
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'vars:' + '\n'
        for var in self.vars:
            s += '  ' * (self.depth + 1) + '-\n'
            var.set_depth(self.depth + 2)
            s += str(var)
        return s

# type declearation
class Tdecls(ExpBase):
    def __init__(self, types: list):
        self.name = 'tdecls'
        self.types = types
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'types:' + '\n'
        for t in self.types:
            s += '  ' * (self.depth + 1) + '- ' + t + '\n'
        return s

# variable var
class Varval(ExpBase):
    def __init__(self, var: str):
        self.name = 'varval'
        self.var = var
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'var: ' + self.var + '\n'
        return s

# literal
class Lit(ExpBase):
    def __init__(self, value):
        self.name = 'lit'
        self.value = value
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'value: ' + str(self.value) + '\n'
        return s

class Flit(Lit):
    def __init__(self, value):
        self.name = 'flit'
        self.value = value

# unary operator
class Uop(ExpBase):
    def __init__(self, op, exp):
        self.name = 'uop'
        self.op = op
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'op: ' + self.op + '\n'
        s += '  ' * self.depth + 'exp:' + '\n'
        self.exp.set_depth(self.depth + 1)
        s += str(self.exp)
        return s

# binary operator
class Binop(ExpBase):
    def __init__(self, op, lhs, rhs):
        self.name = 'binop'
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'op: ' + self.op + '\n'
        s += '  ' * self.depth + 'lhs:' + '\n'
        self.lhs.set_depth(self.depth + 1)
        s += str(self.lhs)
        s += '  ' * self.depth + 'rhs:' + '\n'
        self.rhs.set_depth(self.depth + 1)
        s += str(self.rhs)
        return s

# assignment
class Assign(ExpBase):
    def __init__(self, var, exp):
        self.name = 'assign'
        self.var = var
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'var: ' + self.var + '\n'
        s += '  ' * self.depth + 'exp:' + '\n'
        self.exp.set_depth(self.depth + 1)
        s += str(self.exp)
        return s

# expression statement
class Expstmt(ExpBase):
    def __init__(self, exp = None):
        self.name = 'expstmt'
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        if self.exp:
            s += '  ' * self.depth + 'exp:' + '\n'
            self.exp.set_depth(self.depth + 1)
            s += str(self.exp)
        return s

# statements
class Stmts(ExpBase):
    def __init__(self, stmts: list):
        self.name = 'stmts'
        self.stmts = stmts
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'stmts:' + '\n'
        for stmt in self.stmts:
            s += '  ' * (self.depth + 1) + '-\n'
            stmt.set_depth(self.depth + 2)
            s += str(stmt)
        return s

# expressions
class Exps(ExpBase):
    def __init__(self, exps: list):
        self.name = 'exps'
        self.exps = exps
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'exps:' + '\n'
        for exp in self.exps:
            s += '  ' * (self.depth + 1) + '-\n'
            exp.set_depth(self.depth + 2)
            s += str(exp)
        return s

# if else statement
class IfElse(ExpBase):
    def __init__(self, cond, stmt, else_stmt = None):
        self.name = 'if'
        self.cond = cond
        self.stmt = stmt
        self.else_stmt = else_stmt
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'cond:' + '\n'
        self.cond.set_depth(self.depth + 1)
        s += str(self.cond)
        s += '  ' * self.depth + 'stmt:' + '\n'
        self.stmt.set_depth(self.depth + 1)
        s += str(self.stmt)
        if self.else_stmt: 
            s += '  ' * self.depth + 'else_stmt:' + '\n'
            self.else_stmt.set_depth(self.depth + 1)
            s += str(self.else_stmt)
        return s

# while class
class While(IfElse):
    def __init__(self, cond, stmt):
        super(While, self).__init__(cond, stmt)
        self.name = 'while'

# block
class Blk(ExpBase):
    def __init__(self, stmts = None):
        self.name = 'blk'
        self.contents = stmts
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        if self.contents:
            s += '  ' * self.depth + 'contents:' + '\n'
            self.contents.set_depth(self.depth + 1)
            s += str(self.contents)
        return s

# function 
class Func(ExpBase):
    def __init__(self, ret_type, globid, blk, vdecls = None):
        self.name = 'func'
        self.ret_type = ret_type
        self.globid = globid
        self.blk = blk
        self.vdecls = vdecls
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'ret_type: ' + self.ret_type + '\n'
        s += '  ' * self.depth + 'globid: ' + self.globid + '\n'
        s += '  ' * self.depth + 'blk:' + '\n'
        self.blk.set_depth(self.depth + 1)
        s += str(self.blk)
        if self.vdecls:
            s += '  ' * self.depth + 'vdecls:' + '\n'
            self.vdecls.set_depth(self.depth + 1)
            s += str(self.vdecls)
        return s

# functions
class Funcs(ExpBase):
    def __init__(self, funcs):
        self.name = 'funcs'
        self.funcs = funcs
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'funcs:' + '\n'
        for func in self.funcs:
            s += '  ' * (self.depth + 1) + '-\n'
            func.set_depth(self.depth + 2)
            s += str(func)
        return s
    
# external
class Extern(ExpBase):
    def __init__(self, ret_type, globid, tdecls = None):
        self.name = 'extern'
        self.ret_type = ret_type
        self.globid = globid
        self.tdecls = tdecls
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'ret_type: ' + self.ret_type + '\n'
        s += '  ' * self.depth + 'globid: ' + self.globid + '\n'
        if self.tdecls:
            s += '  ' * self.depth + 'tdecls:' + '\n'
            self.tdecls.set_depth(self.depth + 1)
            s += str(self.tdecls)
        return s

# externals
class Externs(ExpBase):
    def __init__(self, externs: list):
        self.name = 'externs'
        self.externs = externs
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'externs:' + '\n'
        for extern in self.externs:
            s += '  ' * (self.depth + 1) + '-\n'
            extern.set_depth(self.depth + 2)
            s += str(extern)
        return s

class Prog(ExpBase):
    def __init__(self, funcs, externs = None):
        self.name = 'prog'
        self.funcs = funcs
        self.externs = externs
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'funcs:' + '\n'
        self.funcs.set_depth(self.depth + 1)
        s += str(self.funcs)
        if self.externs:
            s += '  ' * self.depth + 'externs:' + '\n'
            self.externs.set_depth(self.depth + 1)
            s += str(self.externs)
        return s


class Caststmt(ExpBase):
    def __init__(self, typ, exp):
        self.name = 'caststmt'
        self.type = typ
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'type: '+ self.type + '\n'
        s += '  ' * self.depth + 'exp:' + '\n'
        self.exp.set_depth(self.depth + 1)
        s += str(self.exp)
        return s

# special function including print and ret
class SpecialFunc(Expstmt):
    '''
    Special functions includes 'print', 'ret'
    '''
    def __init__(self, name, exp = None):
        self.name = name
        self.exp = exp

# function calls
class Funccall(ExpBase):
    def __init__(self, globid, params = None):
        self.name = 'funccall'
        self.globid = globid
        self.params = params
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'globid: '+ self.globid + '\n'
        if self.params:
            s += '  ' * self.depth + 'params:' + '\n'
            self.params.set_depth(self.depth + 1)
            s += str(self.params)
        return s

# variable declaration statement
class Vardeclstmt(ExpBase):
    def __init__(self, vdecl, exp):
        self.name = 'vardeclstmt'
        self.vdecl = vdecl
        self.exp = exp
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'vdecl:' + '\n'
        self.vdecl.set_depth(self.depth + 1)
        s += str(self.vdecl)        
        s += '  ' * self.depth + 'exp:' + '\n'
        self.exp.set_depth(self.depth + 1)
        s += str(self.exp)
        return s

# print string lit function
class Printslit(ExpBase):
    def __init__(self, string: str):
        self.name = 'printslit'
        self.string = string
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'string: ' + self.string + '\n'
        return s