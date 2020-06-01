import Lexer as Lex                 #Importar el lexer, se hace en una variable para poder definir las variables globales que necesita para funcionar
from globalTypes import *           #Importar los tipos de Token para checarlos directamente
'''
Función para definir las variables globales que vienen del script de prueba
'''
def globales(prog, pos, long):
    global programa
    global posicion
    global progLong
    programa = prog
    posicion = pos
    progLong = long

'''
Función para definir las variables globales que se usan adicionalmente (y que no vienen en el script de prueba)
'''
def globales2(tok, v, e):
    global token
    global val
    global endentacion
    token = tok
    val = v
    endentacion = e

'''
Clase que define los nodos del árbol, cada uno tiene un tipo, un valor del token y una lista donde tiene a sus hijos
'''
class NodoArbol:
    def __init__(self, tipo, val):
        self.hijos = []
        self.type = tipo
        self.value = val
    
'''
Funcion para inicializar los nodos, el valor del nodo es None por defecto porque esto es para las ramas del árbol
'''
def nuevoNodo(tipo,val=None):
    t = NodoArbol(tipo,val)
    if (t == None):
        print('Se terminó la memoria')
    return t

'''
Función auxiliar para la impresión del árbol
'''
def imprimeEspacios():
    print(" "*endentacion, end="")

'''
Función para imprimir el árbol
'''
def imprimeAST(arbol):
    global endentacion          #Usando la variable de edentación
    endentacion+=2              #Cada nodo padre se aumenta la edentación
    if arbol != None:           #Si el árbol no es nulo
        imprimeEspacios()       #Imprimir los espacios correspondientes y después el tipo
        print(arbol.type)
        for hijo in arbol.hijos:    #Si tiene hijos el nodo, imprimir recursivamente a sus hijos
            imprimeAST(hijo)
    endentacion-=2              #Al terminar de imprimir el nodo padre reduce la edentación

'''
Función para crear los nodos hoja (Con un token adentro)
'''
def leaf_maker(tipo):
    global val
    t = nuevoNodo(tipo,val)
    match(tipo)
    return t

'''
Función para mandar llamar el error en el lexer, recibe el nombre de la estructura que no se pudo formar
'''
def genericError(structure):
    global val
    Lex.markActualError(val,structure)
    match("Error")

'''
Función para verificar que el token actual corresponde al que estaos buscando
'''
def match(c):
    global token            #Variables globales que se usan (Para que no tengan valor local)
    global val
    if c == "Error":        #Si se va a procesar un token de error
       c = token            #Obliga a que sean iguales
    if token == c:          #Si el token esperado coincide con el que se esta buscando
        token, val = Lex.getToken(False)        #Obtener el token siguiente
        while token == TokenType.COMENTARIO:    #Si el token es un comentario, buscar el siguiente que no lo sea
            token, val = Lex.getToken()

'''
Funciones que describen la gramatica del lenguaje, en todas (si no hay error) se genera un nodo del tipo que se esta revisando 
y se llenan sus hijos con los valores apropiados, si al esperar un token según la gramatica se obtiene uno distinto, se manda 
llamar la función 'genericError' que imprime el error y obtiene el token siguiente

Sobre cada función se encuentra la regla de la gramática que representa
'''
# Program -> Declaration-list
def program():
    newNode = nuevoNodo("Program")
    newNode.hijos.append(declaration_list())
    return newNode
#Declaration-list -> Declaration{Declaration}
def declaration_list():
    newNode = nuevoNodo("Declaration List")
    t = declaration()
    while t.type != "Declaration":
        genericError("Declaration-list")
        t = declaration()
    while t.type!="Error":
        newNode.hijos.append(t)
        t = declaration()
    return newNode
#Declaration -> Var-declaration|Fun-declaration
def declaration():
    newNode = nuevoNodo("Declaration")
    p1 = type_specifier()
    while p1.type != "Type-specifier":
        if token == TokenType.ENDFILE:
            return nuevoNodo("Error")
        genericError("Declaration")
        p1 = type_specifier()
    while token != TokenType.ID:
        genericError("Declaration")
    p2 = leaf_maker(TokenType.ID)
    if token == TokenType.PARENTESISABRIR:
        t = fun_declaration(p1,p2)
    elif token == TokenType.CORCHETEABRIR or token == TokenType.PUNTOYCOMA:
        t = var_declaration(p1,p2)  
    else:
        return nuevoNodo("Error") 
    newNode.hijos.append(t)
    return newNode
#Var-declaration -> Type-specifier ID ["["NUM"]"]";"
def var_declaration(uno, dos):
    global token
    newNode = nuevoNodo("Var-declaration")
    newNode.hijos.append(uno)
    newNode.hijos.append(dos)
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        while token != TokenType.NUM:
            genericError("Var-declaration")
        newNode.hijos.append(leaf_maker(TokenType.NUM))
        while token != TokenType.CORCHETECERRAR:
            genericError("Var-declaration")
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    while token != TokenType.PUNTOYCOMA:
            genericError("Var-declaration")
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode
#Type-specifier -> INT|VOID
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
#Fun-declaration -> Type-specifier ID "("Params")"Compound-stmt
def fun_declaration(uno, dos):
    newNode = nuevoNodo("Fun-declaration")
    newNode.hijos.append(uno)
    newNode.hijos.append(dos)
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(params())
    while token != TokenType.PARENTESISCERRAR:
        genericError("Fun-declaration")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    newNode.hijos.append(compound_stmt())
    return newNode
#Params -> Param-list|VOID
def params():
    newNode = nuevoNodo("Params")
    if token == TokenType.VOID:
        newNode.hijos.append(leaf_maker(TokenType.VOID))
    else:
        newNode.hijos.append(param_list())
    return newNode
#Param-list -> Param{","Param}
def param_list():
    newNode = nuevoNodo("Param-list")
    t = param()
    while t.type != "Param":
        genericError("Param-list")
        t = param()
    newNode.hijos.append(t)
    while token == TokenType.COMA:
        newNode.hijos.append(leaf_maker(TokenType.COMA))
        t = param()
        while t.type != "Param":
            genericError("Param-list")
            t = param()
        newNode.hijos.append(t)
    return newNode
#Param -> Type-specifier ID ["[""]"]
def param():
    newNode = nuevoNodo("Param")
    t = type_specifier()
    if t.type == "Error":
        return t
    newNode.hijos.append(t)
    while token != TokenType.ID:
        genericError("Param")
    newNode.hijos.append(leaf_maker(TokenType.ID))
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        while token != TokenType.CORCHETECERRAR:
            genericError("Param")
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    return newNode
#Compound-stmt -> "{"Local-declaration Statement-list "}"
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
    while token != TokenType.LLAVEACERRAR:
        genericError("Compound-stmt")
    newNode.hijos.append(leaf_maker(TokenType.LLAVEACERRAR))
    return newNode
#Local-declaration -> {Var-declaration}
def local_declaration():
    p1 = type_specifier()
    if p1.type == "Error":
        return p1
    while token != TokenType.ID:
        genericError("Local-declaration")
    p2 = leaf_maker(TokenType.ID)
    passF = token == TokenType.CORCHETEABRIR
    if not passF:
        passF = token == TokenType.PUNTOYCOMA    
    while not passF:
        genericError("Local-declaration")
        passF = token == TokenType.CORCHETEABRIR
        if not passF:
            passF = token == TokenType.PUNTOYCOMA
    t = var_declaration(p1,p2)
    newNode = nuevoNodo("Local-declaration")
    newNode.hijos.append(t)    
    while p1.type != "Error":
        p1 = type_specifier()
        if p1.type == "Error":
            break
        while token != TokenType.ID:
            genericError("Local-declaration")
        p2 = leaf_maker(TokenType.ID)
        passF = token == TokenType.CORCHETEABRIR
        if not passF:
            passF = token == TokenType.PUNTOYCOMA    
        while not passF:
            genericError("Local-declaration")
            passF = token == TokenType.CORCHETEABRIR
            if not passF:
                passF = token == TokenType.PUNTOYCOMA
        t = var_declaration(p1,p2)
        newNode.hijos.append(t)
    return newNode
#Statement-list -> {Statement}
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
#Statement -> Expression-stmt|Compound-stmt|Selection-stmt|Iteration-stmt|Return-stmt
def statement():
    newNode  = nuevoNodo("Statement")
    t = expression_stmt()
    if t.type == "Expression-stmt":
        newNode.hijos.append(t)
        return newNode
    t = compound_stmt()
    if t.type == "Compound-stmt":
        newNode.hijos.append(t)
        return newNode
    t = selection_stmt()
    if t.type == "Selection-stmt":
        newNode.hijos.append(t)
        return newNode
    t = iteration_stmt()
    if t.type == "Iteration-stmt":
        newNode.hijos.append(t)
        return newNode
    t = return_stmt()
    if t.type == "Return-stmt":
        newNode.hijos.append(t)
        return newNode
    return nuevoNodo("Error")
#Expression-stmt -> [Expression]";"
def expression_stmt():
    newNode = nuevoNodo("Expression-stmt")
    t = expression()
    if t.type != "Expression":
        return t
    newNode.hijos.append(t)
    while token != TokenType.PUNTOYCOMA:
        genericError("Expression-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode
#Selection-stmt -> IF "("Expression")" Statement [ELSE Statement]
def selection_stmt():
    if token != TokenType.IF:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Selection-stmt")
    newNode.hijos.append(leaf_maker(TokenType.IF))
    while token != TokenType.PARENTESISABRIR:
        genericError("Selection-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(expression())
    while token != TokenType.PARENTESISCERRAR:
        genericError("Selection-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    t = statement()
    while t.type == "Error":
        genericError("Selection_stmt")
        t = statement()
    newNode.hijos.append(t)
    if token == TokenType.ELSE:
        newNode.hijos.append(TokenType.ELSE)
        t = statement()
        while t.type != "Statement":
            genericError("Selection_stmt")
            t = statement()
        newNode.hijos.append(t)
    return newNode
#Iteration-stmt -> WHILE "("Expression")" Statement
def iteration_stmt():
    if token != TokenType.WHILE:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Iteration-stmt")
    newNode.hijos.append(leaf_maker(TokenType.WHILE))
    while token != TokenType.PARENTESISABRIR:
        genericError("Iteration-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    newNode.hijos.append(expression())
    while token != TokenType.PARENTESISCERRAR:
        genericError("Iteration-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    t = statement()
    while t.type != "Statement":
        genericError("Iteration-stmt")
        t = statement()
    newNode.hijos.append(t)
    return newNode
#Return-stmt -> RETURN [Expression]";"
def return_stmt():
    if token != TokenType.RETURN:
        return nuevoNodo("Error")
    newNode = nuevoNodo("Return-stmt")
    newNode.hijos.append(leaf_maker(TokenType.RETURN))
    t = expression()
    if t.type == "Expression":
        newNode.hijos.append(t)
    while token != TokenType.PUNTOYCOMA:
        genericError("Return-stmt")
    newNode.hijos.append(leaf_maker(TokenType.PUNTOYCOMA))
    return newNode
#Expression -> {Var"="}Simple-expression
def expression():
    newNode = nuevoNodo("Expression")
    t = var()
    if t.type == "Var":
        if token == TokenType.IGUAL:
            while t.type == "Var":
                if token == TokenType.IGUAL:
                    newNode.hijos.append(t)
                    newNode.hijos.append(leaf_maker(TokenType.IGUAL))
                else:
                    newNode.hijos.append(simple_expression(t))
                    return newNode
                t = var()
            t = simple_expression()
            while t.type != "Simple-expression":
                genericError("Expression")
                t = simple_expression()
            newNode.hijos.append(t)
        else:
            newNode.hijos.append(simple_expression(t))
    else:
        t = simple_expression()
        if t.type != "Simple-expression":
            return t
        newNode.hijos.append(t)
    return newNode
#Var -> ID ["["Expression"]"]
def var():
    newNode = nuevoNodo("Var")
    if token != TokenType.ID:
        return nuevoNodo("Error")
    newNode.hijos.append(leaf_maker(TokenType.ID))
    if token == TokenType.CORCHETEABRIR:
        newNode.hijos.append(leaf_maker(TokenType.CORCHETEABRIR))
        newNode.hijos.append(expression())
        while token != TokenType.CORCHETECERRAR:
            genericError("Var")
        newNode.hijos.append(leaf_maker(TokenType.CORCHETECERRAR))
    return newNode
#Simple-expression -> Additive-expression [Relop Additive-expression]
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
#Relop -> "<""="|"<"|">"|">""="|"=""="|"!""="
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
#Aditive-expression -> Term {Addop Term}
def additive_expression(variable = None):
    newNode = nuevoNodo("Additive-expression")
    t = term(variable)
    if t.type != "Term":
        return t
    newNode.hijos.append(t)
    t = addop()
    while t.type == "Addop":
        newNode.hijos.append(t)
        t = term()
        while t.type != "Term":
            genericError("Additive_expression")
            t = term()
        newNode.hijos.append(t)
        t = addop()
    return newNode
#Addop -> "+"|"-"
def addop():
    newNode = nuevoNodo("Addop")
    if token == TokenType.MAS:
        newNode.hijos.append(leaf_maker(TokenType.MAS))
    elif token == TokenType.MENOS:
        newNode.hijos.append(leaf_maker(TokenType.MENOS))
    else:
        return nuevoNodo("Error")
    return newNode
#Term -> Factor{Mulop Factor}
def term(variable = None):
    newNode = nuevoNodo("Term")
    t = factor(variable)
    if t.type != "Factor":
        return t
    newNode.hijos.append(t)
    t = mulop()
    while t.type == "Mulop":
        newNode.hijos.append(t)
        t = factor()
        while t.type != "Factor":
            genericError("Term")
            t = factor()
        newNode.hijos.append(t)
        t = mulop()
    return newNode
#Mulop -> "*"|"/"
def mulop():
    newNode = nuevoNodo("Mulop")
    if token == TokenType.MULT:
        newNode.hijos.append(leaf_maker(TokenType.MULT))
    elif token == TokenType.DIV:
        newNode.hijos.append(leaf_maker(TokenType.DIV))
    else:
        return nuevoNodo("Error")
    return newNode
#Factor -> "("Expression")"|Var|Call|NUM
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
            while token != TokenType.PARENTESISCERRAR:
                genericError("Factor")
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
#Call -> ID "("Args")"
def call(variable):
    newNode = nuevoNodo("Call")
    newNode.hijos.append(variable)
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISABRIR))
    t = args()
    if t.type == "Args":
        newNode.hijos.append(t)
    while token != TokenType.PARENTESISCERRAR:
        genericError("Call")
    newNode.hijos.append(leaf_maker(TokenType.PARENTESISCERRAR))
    return newNode
#Args -> [Arg-list]
def args():
    newNode = nuevoNodo("Args")
    t = arg_list()
    if t.type != "Arg-list":
        return nuevoNodo("Error")
    newNode.hijos.append(t)
    return newNode
#Arg-list -> Expression{","Expression}
def arg_list():
    newNode = nuevoNodo("Arg-list")
    t = expression()
    if t.type != "Expression":
        return nuevoNodo("Error")
    newNode.hijos.append(t)
    while token == TokenType.COMA:        
        newNode.hijos.append(leaf_maker(TokenType.COMA))
        t = expression()
        while t.type != "Expression":
            genericError("Arg-list")
            t = expression()
        newNode.hijos.append(t)
    return newNode

'''
Función de control de todo el Parser
'''
def parser(imprimir = True):
    global token                            #Variable global para saber el fin de archivo
    Lex.globales(programa,posicion,progLong)    #Declarar las variables globales en el Lexer
    toke, valor = Lex.getToken(False)       #Obtener el primer token (Que no sea un comentario)
    while toke == TokenType.COMENTARIO:
        toke, valor = Lex.getToken(False)
    endent = 0                              #Definir el valor de edentación como 0
    globales2(toke,valor,endent)            #Definir el resto de las variables globales
    AST = program()                         #Generar el Abstract Syntax Tree
    if token != TokenType.ENDFILE:          #Verificar si hay un error en el código
         errorSintaxis("El código termina antes que el archivo")
    else:
        if imprimir:                        #Imprimir si se recibió en verdadero la variable correspondiente
            imprimeAST(AST)