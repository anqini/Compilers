from llvmlite import ir
import llvmlite.binding as llvm
from symTable import *
import sys
import clang

#defines the types for llvmlite
integerType = ir.IntType(32)
booleanType = ir.IntType(1)
floatType = ir.FloatType()
voidType = ir.VoidType()

typeMap = {
    'int': integerType,
    'cint': integerType,
    'float': floatType,
    'void': voidType,
    'bool': booleanType,
    'ref int': ir.PointerType(integerType),
    'ref float': ir.PointerType(floatType),
    'ref bool': ir.PointerType(booleanType),
    'ref cint': ir.PointerType(integerType),
    'noalias ref int': ir.PointerType(integerType),
    'noalias ref float': ir.PointerType(floatType),
    'noalias ref bool': ir.PointerType(booleanType),
    'noalias ref cint': ir.PointerType(integerType)
}

module = ir.Module( name='module')
funcTable = SymTable()
symtable = SymTable()

voidptr_ty = ir.IntType(8).as_pointer()
printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
printf = ir.Function(module, printf_ty, name="printf")


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
    def eval(self, builder):
        try:
            # print(self.var)
            # symtable.print()
            value = builder.load(symtable[self.var], name=self.var)
        except:
            print("Error: Variable not Defined!")
            sys.exit(1)
        return value


# literal
class Lit(ExpBase):
    def __init__(self, value):
        self.name = 'lit'
        self.value = value
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'value: ' + str(self.value) + '\n'
        return s
    def eval(self, builder):
        if(self.value == 'true' or self.value == 'false'):
            return ir.Constant(ir.IntType(1), self.value)
        else:
            return ir.Constant(ir.IntType(32), self.value)

class Flit(Lit):
    def __init__(self, value):
        self.name = 'flit'
        self.value = value
    def eval(self, builder):
        return ir.Constant(floatType,self.value)


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
    def eval(self, builder):
        value = self.exp.eval(builder)
        if self.op == 'minus':
            if hasattr(value, 'name') and symtable[value.name.split('.')[0]].name[-2:] == '.c':
                cond = builder.icmp_signed('==', value, ir.Constant(integerType, -2147483648), name=".check_neg")
                with builder.if_then(cond):
                    error_terminate(builder)
            return builder.neg(value, name=".uop_neg")
        elif self.op == 'not':
            if str(value.type) == 'i32':
                value = builder.icmp_signed('!=', value, ir.Constant(integerType, 0), name=".convert")
            return builder.not_(value, name=".uop_not")


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

    def eval(self, builder):
        # try:
        if self.op == 'or':
            return builder.or_(self.lhs.eval(builder), \
                self.rhs.eval(builder), name = ".binop_or")
        elif self.op == 'and':
            return builder.and_(self.lhs.eval(builder), \
                self.rhs.eval(builder), name = ".binop_and")
        lhs = self.lhs.eval(builder)
        rhs = self.rhs.eval(builder)
        if hasattr(lhs, 'name') and hasattr(rhs, 'name') and \
            lhs.name in symtable and rhs.name in symtable and \
            symtable[lhs.name].name[-2:] == '.c' and symtable[rhs.name].name[-2:] == '.c':
            # print('we are doing checked integer calculation!')
            if self.op == 'add':
                res = builder.sadd_with_overflow(lhs, rhs, name = ".binop_add_checked")
                isOverflow = builder.extract_value(res, 1)
                with builder.if_then(isOverflow):
                    error_terminate(builder)
                return res
            elif self.op == "sub":
                res = builder.ssub_with_overflow(lhs, rhs, name = ".binop_sub_checked")
                isOverflow = builder.extract_value(res, 1)
                with builder.if_then(isOverflow):
                    error_terminate(builder)
                return res
            elif self.op == "mul":
                res = builder.smul_with_overflow(lhs, rhs, name = ".binop_mul_checked")
                isOverflow = builder.extract_value(res, 1)
                with builder.if_then(isOverflow):
                    error_terminate(builder)
                return res
            elif self.op == "div":
                with builder.if_then(builder.icmp_signed('==', \
                     ir.Constant(integerType, 0), rhs, name = ".check_zero_div")):
                    error_terminate(builder)
                # left part is int_min
                cond1 = builder.icmp_signed('==', \
                     ir.Constant(integerType, -2147483648), lhs, name = ".check_min_int")
                # right part is -1
                cond2 = builder.icmp_signed('==', \
                     ir.Constant(integerType, -1), rhs, name = ".check_-1_div")
                with builder.if_then(builder.and_(cond1, cond2)):
                    error_terminate(builder)
                return builder.sdiv(lhs, rhs, name = ".binop_sdiv_checked")
            elif self.op == 'eq':
                return builder.icmp_signed('==', lhs, rhs, name = ".binop_eq_checked")
            elif self.op == 'gt':
                return builder.icmp_signed('>', lhs, rhs, name = ".binop_gt_checked")
            elif self.op == 'lt':
                return builder.icmp_signed('<', lhs, rhs, name = ".binop_lt_checked")
        elif str(rhs.type) == 'float':
            if self.op == 'add':
                return builder.fadd(lhs, rhs, name = ".binop_fadd")
            elif self.op == "sub":
                return builder.fsub(lhs, rhs, name = ".binop_fsub")
            elif self.op == "mul":
                return builder.fmul(lhs, rhs, name = ".binop_fmul")
            elif self.op == "div":
                return builder.fdiv(lhs, rhs, name = ".binop_fdiv")
            elif self.op == 'eq':
                return builder.fcmp_ordered('==', lhs, rhs, name = ".binop_eq")
            elif self.op == 'gt':
                return builder.fcmp_ordered('>', lhs, rhs, name = ".binop_gt")
            elif self.op == 'lt':
                return builder.fcmp_ordered('<', lhs, rhs, name = ".binop_lt")
        else:
            if self.op == 'add':
                return builder.add(lhs, rhs, name = ".binop_add")
            elif self.op == "sub":
                return builder.sub(lhs, rhs, name = ".binop_sub")
            elif self.op == "mul":
                return builder.mul(lhs, rhs, name = ".binop_mul")
            elif self.op == "div":
                return builder.sdiv(lhs, rhs, name = ".binop_sdiv")
            elif self.op == 'eq':
                return builder.icmp_signed('==', lhs, rhs, name = ".binop_eq")
            elif self.op == 'gt':
                return builder.icmp_signed('>', lhs, rhs, name = ".binop_gt")
            elif self.op == 'lt':
                return builder.icmp_signed('<', lhs, rhs, name = ".binop_lt")
        # except:
        #     print("Error: Type Conflict!")
        #     sys.exit(1)



# assignment
class Assign(ExpBase):
    # a = 1;
    # int a = 1;  -> vdecl
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
    def eval(self, builder):
        value = self.exp.eval(builder)
        if str(value.type) == 'i32' and str(symtable[self.var].type) == 'float*':
            builder.store(builder.sitofp(value, floatType, name='int2float'), symtable[self.var])
        elif str(value.type) == 'float' and str(symtable[self.var].type) == 'i32*':
            builder.store(builder.fptosi(value, integerType, name='float2int'), symtable[self.var])
        else:
            builder.store(value, symtable[self.var])



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
    def eval(self, builder):
        self.exp.eval(builder)

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
    def eval(self, builder):
        pred = self.cond.eval(builder)
        if str(pred.type) != 'i1': 
            print('Error: Condition Type Error!')
            sys.exit()
        with builder.if_else(pred) as (then, otherwise):
            with then:
                if self.stmt.name == 'blk':
                    self.stmt.eval(None, None, True, builder)
                else: 
                    symtable.grow()
                    self.stmt.eval(builder)
                    symtable.pop()
            with otherwise:
                if self.else_stmt:
                    if self.else_stmt.name == 'blk':
                        self.else_stmt.eval(None, None, True, builder)
                    else: 
                        symtable.grow()
                        self.else_stmt.eval(builder)  
                        symtable.pop()                  

# while class
class While(IfElse):
    def __init__(self, cond, stmt):
        super(While, self).__init__(cond, stmt)
        self.name = 'while'
    def eval(self, builder):
        w_body_block = builder.append_basic_block(".while.body")
        w_after_block = builder.append_basic_block(".while.after")

        # head
        cond_head = self.cond.eval(builder)
        builder.cbranch(cond_head, w_body_block, w_after_block)
        # body
        builder.position_at_start(w_body_block)
        
        if self.stmt.name == 'blk':
            self.stmt.eval(None, None, True, builder)
        else:
            symtable.grow()
            self.stmt.eval(builder)  
            symtable.pop()
        # duplicate condition in body
        cond_body = self.cond.eval(builder)
        builder.cbranch(cond_body, w_body_block, w_after_block)
        # after
        builder.position_at_start(w_after_block)

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

    def eval(self, fn, args, ifelse = False, builder=None): # args are vdecls
        symtable.grow()
        if not ifelse:
            fn_block = fn.append_basic_block(name="entry")
            builder = ir.IRBuilder(fn_block)
            fn_args = fn.args 
            for idx, arg in enumerate(args):
                if 'ref' not in arg.type: # not a reference type
                    alloca = builder.alloca(typeMap[arg.type], name=arg.var)
                    builder.store(fn_args[idx], alloca)
                    symtable[arg.var] = alloca
                else: # reference type
                    symtable[arg.var] = fn_args[idx]
        for stmt in self.contents.stmts:
            stmt.eval(builder)
        if fn and str(fn.type).split(' ')[0] == 'void':
            builder.ret_void()
        # symtable.print()
        symtable.pop()


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
    def eval(self):
        if self.vdecls:
            fn_type = ir.FunctionType(typeMap[self.ret_type], [typeMap[vdecl.type] for vdecl in self.vdecls.vars])
        else:
            fn_type = ir.FunctionType(typeMap[self.ret_type], [])
        fn = ir.Function( module, fn_type, name=self.globid)
        funcTable[self.globid] = fn
        self.blk.eval(fn, self.vdecls.vars if self.vdecls else [])
        



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
    def eval(self):
        fn_type = ir.FunctionType(typeMap[self.ret_type], [typeMap[typ] for typ in self.tdecls.types])  # func = ir.Function(module, functionType, name = i["globid"] )
        fn = ir.Function(module, fn_type, name=self.globid)
        if str(fn.name) == 'getarg':
            fn_block = fn.append_basic_block(name="entry")
            builder = ir.IRBuilder(fn_block)
            arg, = fn.args 
            builder.ret(arg)
        elif str(fn.name) == 'getargf':
            fn_block = fn.append_basic_block(name="entry")
            builder = ir.IRBuilder(fn_block)
            arg, = fn.args 
            builder.ret(builder.sitofp(arg, floatType, name="int2fp"))
        funcTable[self.globid] = fn

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
    def eval(self):
        # externs eval
        if self.externs:
            for extern in self.externs.externs:
                extern.eval()
        # functions eval
        for func in self.funcs.funcs:
            func.eval()
        # funcTable.print()


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
    def eval(self, builder):
        value = self.exp.eval(builder)
        if self.type == 'int' and str(value.type) == 'float':
            return builder.fptosi(value, integerType, name="fp2int")
        elif self.type == 'float' and str(value.type) == 'i32':
            return builder.sitofp(value, floatType, name="int2fp")
        else:
            return value

# special function including print and ret
class SpecialFunc(Expstmt):
    '''
    Special functions includes 'print', 'ret'
    '''
    def __init__(self, name, exp = None):
        self.name = name
        self.exp = exp
    def eval(self, builder):
        if self.name == 'print':
            value = self.exp.eval(builder)    
            # else:
            #     raise TypeError('Must be Interger, Boolean or Float!')
        
            # llvm_ptr = ir.Constant(ir.PointerType(ir.IntType(8)), llvm_arr)

            # Declare argument list
            voidptr_ty = ir.IntType(8).as_pointer()
            fmt = "%d\n\0"
            if str(value.type) == 'float':
                value = builder.fpext(value, ir.DoubleType())
                fmt = "%f\n\0"
            c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                                bytearray(fmt.encode("utf8")))
            global_fmt = ir.GlobalVariable(module, c_fmt.type, name="fstr" + str(value))
            global_fmt.linkage = 'internal'
            global_fmt.global_constant = True
            global_fmt.initializer = c_fmt
            fmt_arg = builder.bitcast(global_fmt, voidptr_ty)

            # Call Print Function
            builder.call(printf, [fmt_arg, value])
        elif self.name == 'ret':
            builder.ret(self.exp.eval(builder))


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
    def eval(self, builder):
        fn = funcTable[self.globid]
        # print(fn.args[0].type)
        args = [] # arguments
        for idx, exp in enumerate(self.params.exps):
            if isinstance(fn.args[idx].type, ir.types.PointerType):
                args.append(symtable[exp.eval(builder).name.split('.')[0]])
            else:
                args.append(exp.eval(builder))
        try:
            ret_value =  builder.call(funcTable[self.globid], args)
        except TypeError as e:
            print(e, "Error: Type Doesn't Match!", file=sys.stderr)
            sys.exit(1)
        return ret_value

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
    def eval(self, builder):
        # int $c = 1;
        if 'ref' in self.vdecl.type:
            alloca = symtable[self.exp.eval(builder).name.split('.')[0]]
        else:
            alloca = None
            if self.vdecl.type == 'cint':
                alloca = builder.alloca(typeMap[self.vdecl.type], name=self.vdecl.var + '.c')
            else:
                alloca = builder.alloca(typeMap[self.vdecl.type], name=self.vdecl.var)
            builder.store(self.exp.eval(builder), alloca)
        symtable[self.vdecl.var] = alloca

# print string lit function
class Printslit(ExpBase):
    def __init__(self, string: str):
        self.name = 'printslit'
        self.string = string
    
    def __str__(self):
        s = '  ' * self.depth + 'name: ' + self.name + '\n'
        s += '  ' * self.depth + 'string: ' + self.string + '\n'
        return s
    def eval(self, builder):
        py_string = self.string
        py_byte_string = bytearray(py_string.encode())[1:-1]
        length = len(py_byte_string)
        arr_type = ir.ArrayType(ir.IntType(8), length)
        llvm_arr = ir.Constant(arr_type, py_byte_string)
        llvm_ptr = ir.Constant(ir.PointerType(ir.IntType(8)), llvm_arr)

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%c \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode()))
        global_fmt = ir.GlobalVariable(module, c_fmt.type, name="fstr" + self.string + str(random.random()))
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = builder.bitcast(global_fmt, voidptr_ty)

        # Call Print Function
        builder.call(printf, [fmt_arg, llvm_arr])
        # builder.ret(ir.Constant(integerType, 0))




import random
def error_terminate(builder):
    printNode = Printslit('eee' + str(random.random()))
    printNode.eval(builder)
    builder.ret(ir.Constant(integerType, 1))



