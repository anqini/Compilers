from ekcc import *
from nodes import *
from llvmlite import ir
import sys

data = sys.stdin.read()
parser = yacc.yacc()
result = parser.parse(data)
result.eval()

print(module)