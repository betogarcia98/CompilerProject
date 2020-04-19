from enum import Enum
import Lexer as Lex
from globalTypes import *

def globales(prog, pos, long):
    global programa
    global posicion
    global progLong
    programa = prog
    posicion = pos
    progLong = long

def globales2(tok, v, e):
    global token
    global val
    global endentacion
    token = tok
    val = v
    endentacion = e

class NodoArbol:
    def __init__(self, tipo, val):
        self.hijos = []
        self.type = tipo
        self.value = val
    
def nuevoNodo(tipo,val=None):
    t = NodoArbol(tipo,val)
    if (t == None):
        print('Se terminó la memoria')
    return t


def errorSintaxis(mensaje):
    print(">>> Error de sintaxis: " + mensaje)

def imprimeEspacios():
    print(" "*endentacion, end="")

def imprimeAST(arbol):
    global endentacion
    endentacion+=2 # ENDENTA
    if arbol != None:
        imprimeEspacios()
        print(arbol.type)
        for hijo in arbol.hijos:
            imprimeAST(hijo)
    endentacion-=2 # DESENDENTA

def leaf_maker(tipo):
    global val
    t = nuevoNodo(tipo,val)
    match(tipo)
    return t

def match(c):
    global token
    #print("token: "+str(token)+" c: "+str(c))
    if token == c:
        if token == TokenType.ENDFILE:
            token = '$'
        else:
            token, val = Lex.getToken(False)
            while token == TokenType.COMENTARIO:
                token, val = Lex.getToken()
    else:
        errorSintaxis("Token no esperado")
    #print(token)

def program():
    newNode = nuevoNodo("Program")
    newNode.hijos.append(declaration_list())
    print("Got a program")
    return newNode

def declaration_list():
    newNode = nuevoNodo("Declaration List")
    newNode.hijos.append(declaration())
    t = declaration()
    while t.type!="Error":
        newNode.hijos.append(t)
        t = declaration()
    return newNode

def declaration():
    newNode = nuevoNodo("Declaration")
    p1 = type_specifier()
    if p1.type == "Error":
        return nuevoNodo("Error")
    p2 = leaf_maker(TokenType.ID)
    if token == TokenType.PARENTESISABRIR:
        t = fun_declaration(p1,p2)
    elif token == TokenType.CORCHETEABRIR or token == TokenType.PUNTOYCOMA:
        t = var_declaration(p1,p2)  
    else:
        return nuevoNodo("Error") 
    newNode.hijos.append(t)
    return newNode

def var_declaration(uno, dos):
    global token
    newNode = nuevoNodo("Var-declaration")
    newNode.hijos.append(uno)
    newNode.hijos.append(dos)
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        newNode.hijos.append(leaf_maker(TokenType.NUM))
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode

def type_specifier():
    global token
    newNode = nuevoNodo("Type-specifier")
    if token == TokenType.INT:
        newNode.hijos.append(leaf_maker(TokenType.INT))
    elif(token == TokenType.VOID):
        newNode.hijos.append(leaf_maker(TokenType.VOID))
    else:
        return nuevoNodo("Error")
    return newNode

def fun_declaration(uno, dos):
    newNode = nuevoNodo("Fun-declaration")
    newNode.hijos.append(uno)
    newNode.hijos.append(dos)
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(params())
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    newNode.hijos.append(compound_stmt())
    return newNode

def params():
    newNode = nuevoNodo("Params")
    if token == TokenType.VOID:
        newNode.hijos.append(leaf_maker(TokenType.VOID))
    else:
        newNode.hijos.append(param_list())
    return newNode

def param_list():
    newNode = nuevoNodo("Param-list")
    newNode.hijos.append(param())
    while token == TokenType.COMA:
        newNode.hijos.append(leaf_maker(TokenType.COMA))
        newNode.hijos.append(param())
    return newNode

def param():
    newNode = nuevoNodo("Param")
    newNode.hijos.append(type_specifier())
    newNode.hijos.append(leaf_maker(TokenType.ID))
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    return newNode

def compound_stmt():
    newNode = nuevoNodo("Compound-stmt")
    if token != TokenType.LLAVEABRIR:
        return nuevoNodo("Error")
    newNode.hijos.append(leaf_maker(TokenType.LLAVEABRIR))
    t = local_declaration()
    if t.type == "Local-declaration":
        newNode.hijos.append(t)
    t = statement_list()
    if t.type == "Statement-list":
        newNode.hijos.append(t)
    newNode.hijos.append(leaf_maker(TokenType.LLAVEACERRAR))
    return newNode

def local_declaration():
    p1 = type_specifier()
    if p1.type == "Error":
        return nuevoNodo("Error")
    p2 = leaf_maker(TokenType.ID)
    t = var_declaration(p1,p2)
    newNode = nuevoNodo("Local-declaration")
    newNode.hijos.append(t)    
    while p1.type != "Error":
        p1 = type_specifier()
        if p1.type == "Error":
            break
        p2 = leaf_maker(TokenType.ID)
        t = var_declaration(p1,p2)
        newNode.hijos.append(t)
    return newNode

def statement_list():
    t = statement()
    if t.type != "Statement":
        return t
    newNode = nuevoNodo("Statement-list")
    newNode.hijos.append(t)
    while t.type=="Statement":
        t = statement()
        if t.type != "Statement":
            break
        newNode.hijos.append(t)
    return newNode

def statement():
    newNode  = nuevoNodo("Statement")
    print("E s")
    t = expression_stmt()
    if t.type == "Expression-stmt":
        newNode.hijos.append(t)
        return newNode
    print("C s")        
    t = compound_stmt()
    if t.type == "Compound-stmt":
        newNode.hijos.append(t)
        return newNode
    print("S s")
    t = selection_stmt()
    if t.type == "Selection-stmt":
        newNode.hijos.append(t)
        return newNode
    print("I s")
    t = iteration_stmt()
    if t.type == "Iteration-stmt":
        newNode.hijos.append(t)
        return newNode
    print("R s")
    t = return_stmt()
    if t.type == "Return-stmt":
        newNode.hijos.append(t)
        return newNode
    return nuevoNodo("Error")

def expression_stmt():
    newNode = nuevoNodo("Expression-stmt")
    t = expression()
    if t.type == "Expression":
        newNode.hijos.append(t)
    if token != TokenType.PUNTOYCOMA:
        return nuevoNodo("Error")
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode
    
def selection_stmt():
    if token != TokenType.IF:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Selection-stmt")
    newNode.hijos.append(leaf_maker(TokenType.IF))
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(expression())
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    t = statement()
    if t.type == "Error":
        return t
    newNode.hijos.append(t)
    if token == TokenType.ELSE:
        newNode.hijos.append(TokenType.ELSE)
        t = statement()
        if t.type != "Statement":
            return nuevoNodo("Error")
        newNode.hijos.append(t)
    return newNode

def iteration_stmt():
    if token != TokenType.WHILE:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Iteration-stmt")
    newNode.hijos.append(leaf_maker(TokenType.WHILE))
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(expression())
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    t = statement()
    if t.type != "Statement":
        return nuevoNodo("Error")
    newNode.hijos.append(t)
    return newNode

def return_stmt():
    if token != TokenType.RETURN:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Return-stmt")
    newNode.hijos.append(leaf_maker(TokenType.RETURN))
    t = expression()
    if t.type == "Expression":
        newNode.hijos.append(t)
    if token != TokenType.PUNTOYCOMA:
        return nuevoNodo("Error")
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode

def expression():
    newNode = nuevoNodo("Expression")
    #print("Var")
    t = var()
    if t.type == "Var":
        if token == TokenType.IGUAL:
            while t.type == "Var":
                #print("W V in")
                if token == TokenType.IGUAL:
                    #print("W V in I")
                    newNode.hijos.append(t)
                    newNode.hijos.append(leaf_maker(TokenType.IGUAL))
                else:
                    #print("W V in E")
                    newNode.hijos.append(simple_expression(t))
                    return newNode
                #print("Var")
                t = var()
            #print("W V out")
            newNode.hijos.append(simple_expression())
        else:
            #print("V in = out")
            newNode.hijos.append(simple_expression(t))
    else:
        #print("V out")
        newNode.hijos.append(simple_expression())
    return newNode

def var():
    newNode = nuevoNodo("Var")
    if token != TokenType.ID:
        return nuevoNodo("Error")
    newNode.hijos.append(leaf_maker(TokenType.ID))
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        newNode.hijos.append(expression())
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    return newNode

def simple_expression(variable = None):
    newNode = nuevoNodo("Simple-expression")
    t = additive_expression(variable)
    if t.type != "Additive-expression":
        return t
    newNode.hijos.append(t)
    t = relop()
    if t.type == "Relop":
        newNode.hijos.append(t)
        newNode.hijos.append(additive_expression())
    return newNode

def relop():
    newNode = nuevoNodo("Relop")
    if token == TokenType.MENORIGUAL:
        newNode.hijos.append(leaf_maker(TokenType.MENORIGUAL))
    elif token == TokenType.MENOR:
        newNode.hijos.append(leaf_maker(TokenType.MENOR))
    elif token == TokenType.MAYOR:
        newNode.hijos.append(leaf_maker(TokenType.MAYOR))
    elif token == TokenType.MAYORIGUAL:
        newNode.hijos.append(leaf_maker(TokenType.MAYORIGUAL))
    elif token == TokenType.IGUALIGUAL:
        newNode.hijos.append(leaf_maker(TokenType.IGUALIGUAL))
    elif token == TokenType.NOT:
        newNode.hijos.append(leaf_maker(TokenType.NOT))
    else:
        return nuevoNodo("Error")
    return newNode

def additive_expression(variable = None):
    newNode = nuevoNodo("Additive-expression")
    t = term(variable)
    if t.type != "Term":
        return t
    newNode.hijos.append(t)
    t = addop()
    while t.type == "Addop":
        newNode.hijos.append(t)
        newNode.hijos.append(term())
        t = addop()
    return newNode

def addop():
    newNode = nuevoNodo("Addop")
    if token == TokenType.MAS:
        newNode.hijos.append(leaf_maker(TokenType.MAS))
    elif token == TokenType.MENOS:
        newNode.hijos.append(leaf_maker(TokenType.MENOS))
    else:
        return nuevoNodo("Error")
    return newNode

def term(variable = None):
    newNode = nuevoNodo("Term")
    t = factor(variable)
    if t.type != "Factor":
        return t
    newNode.hijos.append(t)
    t = mulop()
    while t.type == "Mulop":
        newNode.hijos.append(t)
        newNode.hijos.append(factor())
        t = mulop()
    return newNode

def mulop():
    newNode = nuevoNodo("Mulop")
    if token == TokenType.MULT:
        newNode.hijos.append(leaf_maker(TokenType.MULT))
    elif token == TokenType.DIV:
        newNode.hijos.append(leaf_maker(TokenType.DIV))
    else:
        return nuevoNodo("Error")
    return newNode

def factor(variable = None):
    newNode = nuevoNodo("Factor")
    if variable != None:
        if token == TokenType.PARENTESISABRIR:
            nuevo = call(variable)
            newNode.hijos.append(nuevo)
        else:
            newNode.hijos.append(variable)
    else:
        if token == TokenType.PARENTESISABRIR:
            newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
            newNode.hijos.append(expression())
            newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
        elif token == TokenType.NUM:
            newNode.hijos.append(leaf_maker(TokenType.NUM))
        else:
            t = var()
            if t.type == "Var":
                newNode.hijos.append(t)
            else:
                return nuevoNodo("Error")
    return newNode

def call(variable):
    print("##########Will check a call")
    newNode = nuevoNodo("Call")
    newNode.hijos.append(variable)
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    t = args()
    if t.type == "Args":
        newNode.hijos.append(t)
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    return newNode

def args():
    newNode = nuevoNodo("Args")
    t = arg_list()
    if t.type != "Arg-list":
        return nuevoNodo("Error")
    newNode.hijos.append(t)
    return newNode

def arg_list():
    newNode = nuevoNodo("Arg-list")
    t = expression()
    if t.type != "Expression":
        return nuevoNodo("Error")
    newNode.hijos.append(t)
    while token == TokenType.COMA:        
        newNode.hijos.append(leaf_maker(TokenType.COMA))
        newNode.hijos.append(expression())
    return newNode



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


def parser(imprimir = True):
    Lex.globales(programa,posicion,progLong)
    toke, valor = Lex.getToken()
    while toke == TokenType.COMENTARIO:
        toke, valor = Lex.getToken(False)
    endent = 0
    globales2(toke,valor,endent)
    
    AST = program()
    # if token != '$':
    #     errorSintaxis("El código termina antes que el archivo")
    # else:
    print("Got here!")
    imprimeAST(AST)