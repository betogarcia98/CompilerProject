from enum import Enum

class TipoExpresion(Enum):
    Op = 0
    Const = 1

class NodoArbol:
    def __init__(self):
        self.hijoIzq = None
        self.hijoDer = None
        self.exp = None # tipo de expresion
        self.op = None  # char (TokenType) {'+', '-', '*'}
        self.val = None # tipo int [0-9]

def nuevoNodo(tipo):
    t = NodoArbol()
    if (t == None):
        print('Se terminó la memoria')
    else:
        t.exp = tipo
    return t

def errorSintaxis(mensaje):
    print(">>> Error de sintaxis: " + mensaje)

def imprimeEspacios():
    print(" "*endentacion, end="")

def imprimeAST(arbol):
    global endentacion
    endentacion+=2 # ENDENTA
    if arbol != None:
        imprimeEspacios();
        if arbol.exp == TipoExpresion.Op:
            print("Op: ", arbol.op)
        elif arbol.exp == TipoExpresion.Const:
            print("Const: ",arbol.val," ")
        else:
            print("ExpNode de tipo desconocido")
        imprimeAST(arbol.hijoIzq)
        imprimeAST(arbol.hijoDer)
    endentacion-=2 # DESENDENTA

def match(c):
    global token, pos
    if token == c:
        pos+=1
        if pos == len(cadena):
            token = '$'
        else:
            token = cadena[pos]
    else:
        errorSintaxis("Token no esperado")

def exp():
    t = term()
    while token in '+-':
        p = nuevoNodo(TipoExpresion.Op)
        p.hijoIzq = t
        p.op = token
        t = p
        match(token)
        t.hijoDer = term()
    return t

def term():
    t = factor()
    while token == '*':
        p = nuevoNodo(TipoExpresion.Op)
        p.hijoIzq = t
        p.op = token
        t = p
        match(token)
        t.hijoDer = factor()
    return t

def factor():
    if token in '0123456789':
        t = nuevoNodo(TipoExpresion.Const)
        t.val = token
        match(token)
    elif token == '(':
        match('(')
        t = exp()
        match(')')
    else:
        errorSintaxis("Token no esperado")
    return t

cadena = input("Escribe la cadena:")
pos = 0
token = cadena[pos]
AST = exp()
endentacion = 0
if token != '$':
    errorSintaxis("El código termina antes que el archivo")
else:
    imprimeAST(AST)









