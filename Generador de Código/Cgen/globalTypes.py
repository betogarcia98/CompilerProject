from enum import Enum
#arreglo de strings con las palabras reservadas del lenguaje
reservedKeyWords = ['if','else','int','return','void','while']
#calse de enums para identificar los tokens del lenguaje
class TokenType(Enum):
    ENDFILE = 0
    ERROR = 1
    #palabras reservadas
    IF = 'if'
    ELSE = 'else'
    INT = 'int'
    RETURN = 'return'
    VOID = 'void'
    WHILE = 'while'
    #simbolos especiales
    PLUS = '+'
    LESS = '-'
    MULT = '*'
    DIV = '/'
    LOWERTHAN = '<'
    GREATERT = '>'
    LTEQUAL = '<='
    GTEQUAL = '>='
    EQUAL = "=="
    DIFF = '!='
    ASSIGN = '='
    SEMICOL = ';'
    COMMA = ','
    OPENB = '('
    CLOSEB = ')'
    OPENSQUAREB = '['
    CLOSESQUAREB = ']'
    OPENCURLYB = '{'
    CLOSECURLYB = '}'
    #simbolos de varios caracteres
    ID = 2
    NUM = 3
    COMMENT = 4
    pass

booleanOperators = [TokenType.LOWERTHAN, TokenType.GREATERT, TokenType.LTEQUAL, TokenType.GTEQUAL, TokenType.EQUAL, TokenType.DIFF]

class TipoNodo(Enum):
    STMT = 0
    EXP = 1
    DEC = 2
    pass

class StmtTipo(Enum):
    IF = 0
    WHILE = 1
    RETURN = 2
    CALL = 3
    COMPOUND = 4
    pass

class ExpTipo(Enum):
    OPERATION = 0
    IDENTIFIER = 1
    CONST = 2
    ASSIGN = 3
    ARREGLO = 4
    pass

class OpTipo(Enum):
    BOOLEAN = 0
    INTEGER = 1
    ARRAY = 2
    VOID = 3
    pass

class DecTipo(Enum):
    FUNCION = 0
    VARIABLE = 1
    ARREGLO = 2
    pass

class TreeNode:
    def __init__(self):
        self.child = [None]*5               # tipo treeNode
        self.lineno = 0                     # tipo int
        self.sibling = None                 # tipo treeNode
        self.op = None                      # tipo TokenType
        self.val = None                     # tipo int
        self.str = None                     # tipo String
        self.nType = None                   # tipo TipoNodo
        self.stmtType = None                # tipo StmtTipo
        self.expType = None                 # tipo ExpTipo
        self.decType = None                 # tipo DecTipo
        self.type = None                    # tipo OpTipo
