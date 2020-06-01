from lexer import *
import sys

tokenType = None # holds current token
tokenString = None # holds the token string value 
Error = False
indentno = 0
lineno = 0
imprimeScanner = False

def globales(prog, pos, long):
    global programa
    global posicion
    global progLong
    programa = prog
    posicion = pos
    progLong = long

def parser(imprime = True):
    global tokenType, tokenString, lineno
    globalesLexer(programa, posicion, progLong)
    lineno, tokenType, tokenString = getToken(imprimeScanner)
    t=None 
    while tokenType == TokenType.COMMENT:
        lineno, tokenType, tokenString = getToken(imprimeScanner)
    
    t = program()

    if (tokenType != TokenType.ENDFILE):
        syntaxError("Code ends before file\n")
    if imprime:
        printTree(t)
    return t

def nuevoNodo(tipo):
    global lineno
    t = TreeNode()
    if (t == None):
        print('Se terminó la memoria')
    else:
        t.op = tipo
        t.lineno = lineno
    return t

def nuevoExpNodo(tipo):
    global lineno
    t = TreeNode()
    if (t == None):
        print('Se terminó la memoria')
    else:
        t.nType = TipoNodo.EXP
        t.expType = tipo
        t.lineno = lineno
    return t

def nuevoStmtNodo(tipo):
    global lineno
    t = TreeNode()
    if (t == None):
        print('Se terminó la memoria')
    else:
        t.nType = TipoNodo.STMT
        t.stmtType = tipo
        t.lineno = lineno
    return t

def nuevoDecNodo(tipo):
    global lineno
    t = TreeNode()
    if (t == None):
        print('Se terminó la memoria')
    else:
        t.nType = TipoNodo.DEC
        t.decType = tipo
        t.lineno = lineno
    return t

def match(expected, message=""):
    global tokenType, tokenString, lineno
    if (tokenType == expected):
        lineno, tokenType, tokenString = getToken(imprimeScanner)
        while(tokenType == TokenType.COMMENT):
            lineno, tokenType, tokenString = getToken(imprimeScanner)
    else:
        error("unexpected token -> "+message,True)

def syntaxError(message):
    global Error, lineno
    print(">>> Syntax error at line " + str(lineno-1)+ ": " + message, end='')
    Error = True

def error(message, move=True):
    global tokenType, tokenString, lineno
    Error = True
    syntaxError(message)
    debugPrint()
    lineno -= 1
    errorFunction(lineno,"", tokenString)
    if move:
        #lineno, tokenType, tokenString = getToken(imprimeScanner)
        # while tokenType == TokenType.COMMENT or tokenType!=TokenType.CLOSECURLYB:
        #     lineno, tokenType, tokenString = getToken(imprimeScanner)
        if tokenType == TokenType.IF:
            selection_stmt()
        elif tokenType == TokenType.ELSE:
            match(TokenType.ELSE)
            statement()
        elif tokenType == TokenType.INT:
            var()
        elif tokenType == TokenType.RETURN:
            return_stmt()
        elif tokenType == TokenType.VOID:
            declaration()
        elif tokenType == TokenType.WHILE:
            iteration_stmt()
        elif tokenType == TokenType.PLUS:
            match(TokenType.PLUS)
            term(None)
        elif tokenType == TokenType.LESS:
            match(TokenType.LESS)
            term(None)
        elif tokenType == TokenType.MULT:
            match(TokenType.MULT)
            factor(None)
        elif tokenType == TokenType.DIV:
            match(TokenType.DIV)
            factor(None)
        elif tokenType in booleanOperators:
            match(tokenType)
            additive_expression(None)
        elif tokenType == TokenType.ASSIGN:
            match(TokenType.ASSIGN)
            expression()
        elif tokenType == TokenType.SEMICOL:
            expression_stmt()
        elif tokenType == TokenType.COMMA:
            match(TokenType.COMMA)
            expression()
        elif tokenType == TokenType.OPENB:
            match(TokenType.OPENB)
            params()
        elif tokenType == TokenType.CLOSEB:
            match(TokenType.CLOSEB)
            compound_stmt()
        elif tokenType == TokenType.OPENSQUAREB:
            match(TokenType.OPENSQUAREB)
            expression()
        elif tokenType == TokenType.CLOSESQUAREB:
            match(TokenType.CLOSESQUAREB)
            match(TokenType.SEMICOL)
        elif tokenType == TokenType.OPENCURLYB:
            match(TokenType.OPENCURLYB)
            local_declarations()
        elif tokenType == TokenType.CLOSECURLYB:
            match(TokenType.CLOSECURLYB)
            debugPrint()
            declaration()
        elif tokenType == TokenType.ID:
            t = expression()
            return t
        elif tokenType == TokenType.NUM:
            expression()
        elif tokenType == TokenType.ENDFILE:
            sys.exit()

    print("      ")
    #declaration()
    return None

def debugPrint():
    print("Tokentype: ",tokenType," TokenString",tokenString, "Linea: ",lineno)

# printSpaces indents by printing spaces */
def printSpaces():
    print(" "*indentno, end = "")

# procedure printTree prints a syntax tree to the 
# listing file using indentation to indicate subtrees
def printTree(tree):
    global indentno
    indentno+=2 # INDENT
    while tree != None:
        printSpaces()
        if(tree.nType == TipoNodo.STMT):
            print("Stmt TokenType: ",tree.stmtType," Lineno: ",tree.lineno)
        elif (tree.nType == TipoNodo.EXP):
            print("Exp TokenType: ",tree.expType," Lineno: ",tree.lineno)
            printSpaces()
            if(tree.expType == ExpTipo.OPERATION):
                print("TokenType: ",tree.op," Str: ",tree.str)
            if(tree.expType == ExpTipo.IDENTIFIER):
                print("TokenType: IDENTIFIER, Str: ",tree.str)
            if(tree.expType == ExpTipo.CONST):
                print("TokenType: CONSTANT, Val: ",tree.val)
            if(tree.expType == ExpTipo.ASSIGN):
                print("TokenType: ASSIGN, Val: ",tree.str)
            if(tree.expType == ExpTipo.ARREGLO):
                print("TokenType: ARREGLO, Val: ",tree.str)
        elif (tree.nType == TipoNodo.DEC):
            print("Dec TokenType: ",tree.decType," Lineno: ",tree.lineno)
            printSpaces()
            if(tree.decType == DecTipo.FUNCION):
                print("TokenType: FUNCION","Tipo: ",tree.str)
            if(tree.decType == DecTipo.VARIABLE):
                print("TokenType: VARIABLE Tipo: ",tree.str)
            if(tree.decType == DecTipo.ARREGLO):
                print("TokenType: ARREGLO Tipo: ",tree.str)
        for child in tree.child:
            printTree(child)
        tree = tree.sibling
    indentno-=2 #UNINDENT

def program():
    global tokenType, tokenString, lineno
    t = declaration()
    q = t
    if(t!=None):
        while(tokenType!=TokenType.ENDFILE):
            p = q
            if(q != None and p !=None):
                q = declaration()
                p.sibling = q
    return t

def declaration():
    # print("declaration")
    global tokenType, tokenString, lineno
    t = None
    id = None
    tipo = None
    if tokenType == TokenType.ENDFILE:
        return t
    if(tokenType==TokenType.INT) or (tokenType==TokenType.VOID):
        t = nuevoDecNodo(DecTipo.VARIABLE)
        t.str = tipo = tokenString
        t.op = tokenType
        if(tokenType==TokenType.INT):
            match(TokenType.INT, "Se esperaba un token INT")
        elif(tokenType==TokenType.VOID):
            match(TokenType.VOID, "Se esperaba un token VOID")
        if(t!=None):
            if(tokenType == TokenType.ID): #si es un identificador
                t.child[0] = nuevoExpNodo(ExpTipo.IDENTIFIER) #agregar el nuevo nodo a donde corresponde
                t.child[0].str = id = tokenString #agregar el valor del identificador al nodo
                match(TokenType.ID, "Se esperaba un token ID")

                if(tokenType == TokenType.OPENB): #si hay un parentesis que abre
                    match(TokenType.OPENB, "Se esperaba un token (")
                    t = fun_declaration(tipo, id) #llamar la funcion correspondiente a una funcion

                elif(tokenType == TokenType.OPENSQUAREB): #si es un corchete que abre
                    match(TokenType.OPENSQUAREB, "Se esperaba un token [")
                    p = nuevoDecNodo(DecTipo.ARREGLO)
                    p.str = tipo
                    p.child[0] = t.child[0]
                    t = p
                    if(tokenType == TokenType.NUM): #si es un numero el que está dentro de los corchetes
                        t.child[1] = nuevoExpNodo(ExpTipo.CONST) #hacer el nuevo nodo para el numero, que es un constante
                        t.child[1].val = tokenString
                        match(TokenType.NUM, "Se esperaba un token numerico")

                    if(tokenType == TokenType.CLOSESQUAREB): #se cierran los corchetes
                        match(TokenType.CLOSESQUAREB, "Se esperaba un token ]")

                    if(tokenType == TokenType.SEMICOL): #se termina la linea con punto y coma
                        match(TokenType.SEMICOL, "Se esperaba que termine con punto y coma")

                    else: #si no se acabó con punto y coma
                        error("unexpected token -> tok - no termina con punto y coma \n")
                elif (tokenType == TokenType.SEMICOL): #si se acabó con punto y coma
                    match(TokenType.SEMICOL, "Se esperaba que termine con punto y coma")
                else: #si no se acabó con punto y coma
                    t = error("unexpected token -> tok - no termina con punto y coma o no continua con paréntesis\n")
            else: #si no es un identificador lo que sigue
                error("unexpected token -> tok - no es un id \n")
    else: #si no se empieza con el tipo de variable o funcion
        t = error("unexpected token -> tok - no es una variable o función \n")
    return t

def fun_declaration(tipo, id):
    # print("fun_declaration")
    global tokenType, tokenString, lineno
    t = params() #se llama a la funcion que obtiene los parametros
    if(tokenType == TokenType.CLOSEB): #se cierra el parentesis
        match(TokenType.CLOSEB, "Se esperaba un token )")
        p = nuevoDecNodo(DecTipo.FUNCION) #se crea el nuevo hijo para el cuerpo de la funcion
        if(p!=None):
            p.str = tipo
            p.child[0] = nuevoExpNodo(ExpTipo.IDENTIFIER)
            p.child[0].str = id
            p.child[1] = t
            t = p
            t.child[2] = compound_stmt() #se llama la funcion para el cuerpo de la funcion
    return t

def params():
    # print("params")
    global tokenType, tokenString, lineno
    t = None
    if(tokenType==TokenType.VOID):
        match(TokenType.VOID, "Se esperaba un token VOID")
        return t
    t = param() #llama a la funcion que acepta las declaraciones de los parametros
    q = t
    while(tokenType == TokenType.COMMA): #se pone la coma que los separa
        match(TokenType.COMMA, "Se esperaba un token COMMA")
        p = q #el nodo anterior va a ser el hermano mayor de los demás parametros
        if(q != None and p !=None):
            q = param() #llamar a la función que acepta los parametros
            p.sibling = q #hacer el anterior el hermano menor del parametro anterior
    return t

def param():
    # print("param")
    global tokenType, tokenString, lineno
    t = None
    if(tokenType==TokenType.INT): #es int o void el parametro 
        t = nuevoDecNodo(DecTipo.VARIABLE) #se crea el nodo con la información del parametro
        t.str = tipo = tokenString
        t.op = tokenType
        match(TokenType.INT, "Se esperaba un token INT")
        if(t!=None):
            if(tokenType == TokenType.ID):
                t.child[0] = nuevoExpNodo(ExpTipo.IDENTIFIER) #agregar el nuevo nodo a donde corresponde
                t.child[0].str = tokenString #agregar el valor del identificador al nodo
                match(TokenType.ID, "Se esperaba un identificador")
                if(tokenType == TokenType.OPENSQUAREB): #se abre el corchete
                    match(TokenType.OPENSQUAREB, "Se esperaba un token [")
                    p = nuevoDecNodo(DecTipo.ARREGLO)
                    p.str = tipo
                    p.child[0] = t.child[0]
                    t = p
                    if(tokenType == TokenType.NUM): #es un número dentro del corchete
                        t.child[1] = nuevoExpNodo(ExpTipo.CONST) #se crea el nodo que va a tener el número
                        t.child[1].val = tokenString
                        match(TokenType.NUM, "Se esperaba un número")
                    if(tokenType == TokenType.CLOSESQUAREB): #se cierra el corchete
                        match(TokenType.CLOSESQUAREB, "Se esperaba un token ]")
                    else: #si no se cerró el corchete
                        error("unexpected token -> no cierra con corchete \n")
            else: #si no viene un identificador
                error("unexpected token -> no es un id\n")
    else: #si no viene el tipo de la declaración
        error("unexpected token -> no tiene tipo \n")
    return t

def compound_stmt():
    # print("compound_stmt")
    global tokenType, tokenString, lineno
    t = None
    if(tokenType == TokenType.OPENCURLYB): #se empieza con una llave
        match(TokenType.OPENCURLYB, "Se esperaba una llave que abre")
        t = nuevoStmtNodo(StmtTipo.COMPOUND)
        t.child[0] = local_declarations()
        
        t.child[1] = nuevoStmtNodo(StmtTipo.COMPOUND)
        p = t.child[1]
        while tokenType!=TokenType.CLOSECURLYB:
            q = statement()
            if(q !=None):
                p.sibling = q #hacer el anterior el hermano menor del parametro anterior
                p = q
        match(TokenType.CLOSECURLYB, "Se esperaba una llave que cierra") #se cierran las llaves
    else: #si no se encontró la llave que abre
        t = error("unexpected token -> no se encontró la llave que abre \n")
    return t

def local_declarations():
    # print("local_declaration")
    global tokenType, tokenString, lineno
    t=nuevoStmtNodo(StmtTipo.COMPOUND)
    q = t
    while((tokenType==TokenType.INT) or (tokenType==TokenType.VOID)): #es int o void la variable
        p = nuevoDecNodo(DecTipo.VARIABLE) #se crea el nodo con la información de la variable
        p.str = tipo = tokenString
        p.op = tokenType
        if(tokenType==TokenType.INT):
            match(TokenType.INT, "Se esperaba un token INT")
        elif(tokenType==TokenType.VOID):
            match(TokenType.VOID, "Se esperaba un token VOID")
        if(p!=None):
            if(tokenType == TokenType.ID): #es el identificadot
                p.child[0] = nuevoExpNodo(ExpTipo.IDENTIFIER) #agregar el nuevo nodo a donde corresponde
                p.child[0].str = tokenString
                match(TokenType.ID, "Se esperaba un identificador")
                if(tokenType == TokenType.OPENSQUAREB):
                    nuevoN = nuevoDecNodo(DecTipo.ARREGLO)
                    nuevoN.str = tipo
                    nuevoN.child[0] = p.child[0]
                    p = nuevoN
                    match(TokenType.OPENSQUAREB, "Se esperaba un token [")
                    if(tokenType == TokenType.NUM):
                        p.child[1] = nuevoExpNodo(ExpTipo.CONST)
                        p.child[1].val = tokenString
                        match(TokenType.NUM, "Se esperaba un número")
                    if(tokenType == TokenType.CLOSESQUAREB):
                        match(TokenType.CLOSESQUAREB, "Se esperaba un token ]")
                    if(tokenType == TokenType.SEMICOL):
                        match(TokenType.SEMICOL, "No termina con punto y coma")
                        q.sibling = p
                        q = p
                    else:
                        t = error("unexpected token -> tok - No termina con punto y coma \n")
                elif (tokenType == TokenType.SEMICOL):
                    match(TokenType.SEMICOL, "No termina con punto y coma")
                    q.sibling = p
                    q = p
                else:
                    t = error("unexpected token -> tok - No termina con punto y coma \n")
            else:
                error("unexpected token -> tok - Se esperaba un identificador\n")
    return t

def statement(): #La lista de los estatutos posibles
    # print("statement")
    global tokenType, tokenString, lineno
    t = None
    if tokenType == TokenType.IF:
        t = selection_stmt()
    elif tokenType == TokenType.OPENCURLYB:
        t = compound_stmt()
    elif tokenType == TokenType.WHILE:
        t = iteration_stmt()
    elif tokenType == TokenType.RETURN:
        t = return_stmt()
    elif tokenType == TokenType.ID or tokenType == TokenType.SEMICOL or tokenType == TokenType.NUM or tokenType == TokenType.OPENB:
        t = expression_stmt()
    else:
        t = error("unexpected token -> es un estatuto no reconocido \n")
    return t

def expression_stmt():
    # print("expression_stmt")
    global tokenType, tokenString, lineno
    t = None
    if tokenType == TokenType.ID or tokenType == TokenType.NUM or tokenType == TokenType.OPENB:
        t = expression()
    if tokenType == TokenType.SEMICOL:
        match(TokenType.SEMICOL)
    else:
        error("unexpected token -> no termina con punto y coma\n",False)
    return t

def selection_stmt():
    # print("selection_stmt")
    global tokenType, tokenString, lineno
    t = nuevoStmtNodo(StmtTipo.IF)
    match(TokenType.IF)
    match(TokenType.OPENB)
    if (t!=None):
        t.child[0] = expression()
    match(TokenType.CLOSEB)
    if (t!=None):
        t.child[1] = statement()
    if (tokenType==TokenType.ELSE):
        match(TokenType.ELSE)
        if (t!=None):
            t.child[2] = statement()
    return t

def iteration_stmt():
    # print("iteration_stmt")
    global tokenType, tokenString, lineno
    t = nuevoStmtNodo(StmtTipo.WHILE)
    match(TokenType.WHILE)
    match(TokenType.OPENB)
    if (t!=None):
        t.child[0] = expression()
    match(TokenType.CLOSEB)
    if (t!=None):
        t.child[1] = statement()
    return t

def return_stmt():
    # print("return_stmt")
    global tokenType, tokenString, lineno
    t = nuevoStmtNodo(StmtTipo.RETURN)
    match(TokenType.RETURN)
    t.child[0] = expression_stmt()
    return t

def expression():
    # print("expression")
    global tokenType, tokenString, lineno
    t = None
    if(tokenType == TokenType.ID):
        t = var()
    if(t!=None and tokenType==TokenType.ASSIGN):
        p = nuevoExpNodo(ExpTipo.ASSIGN)
        p.str = tokenString
        match(TokenType.ASSIGN)
        if(t != None and p !=None):
            p.child[0] = t
            t = p
            t.child[1] = expression()
    else:
        t = simple_expression(t)
    
    if(t==None):
        error("unexpected token -> expresion incorrecta\n",False)
    return t

def var():
    # print("var")
    global tokenType, tokenString, lineno
    t = None
    if(tokenType == TokenType.ID):
        t = nuevoExpNodo(ExpTipo.IDENTIFIER)
        t.str = tokenString
        match(TokenType.ID)
        if(tokenType==TokenType.OPENB):
            match(TokenType.OPENB)
            p = nuevoStmtNodo(StmtTipo.CALL)
            if(t != None and p !=None):
                p.child[0] = t
                t = p
                t.child[1] = args()
            if(tokenType == TokenType.CLOSEB):
                match(TokenType.CLOSEB)
            else:
                t = error("unexpected token -> no cierra con parentesis \n")
        elif(tokenType==TokenType.OPENSQUAREB):
            match(TokenType.OPENSQUAREB)
            p = nuevoExpNodo(ExpTipo.ARREGLO)
            p.str = "var"
            if(t != None and p !=None):
                p.child[0] = t
                t = p
                t.child[1] = expression()
            if(tokenType == TokenType.CLOSESQUAREB):
                match(TokenType.CLOSESQUAREB)
            else:
                t = error("unexpected token -> no cierra con corchetes \n")
    return t

def simple_expression(idVar):
    #print("simple_expression")
    global tokenType, tokenString, lineno
    t = additive_expression(idVar)
    while(tokenType in booleanOperators):
        p = nuevoExpNodo(ExpTipo.OPERATION)
        p.op = tokenType
        p.str = tokenString
        match(tokenType)
        if(t != None and p !=None):
            p.child[0] = t
            t = p
            t.child[1] = additive_expression(None)
    return t

def additive_expression(idVar):
    #print("additive_expression")
    global tokenType, tokenString, lineno
    t = term(idVar)
    while (tokenType == TokenType.PLUS or tokenType == TokenType.LESS):
        p = nuevoExpNodo(ExpTipo.OPERATION)
        p.op = tokenType
        p.str = tokenString
        match(tokenType)
        if(t != None and p !=None):
            p.child[0] = t
            t = p
            t.child[1] = term(None)
    return t

def term(idVar):
    #print("term")
    global tokenType, tokenString, lineno
    t = factor(idVar)
    while (tokenType == TokenType.MULT or tokenType == TokenType.DIV):
        p = nuevoExpNodo(ExpTipo.OPERATION)
        p.op = tokenType
        p.str = tokenString
        match(tokenType)
        if(t != None and p !=None):
            p.child[0] = t
            t = p
            t.child[1] = factor(None)
    return t

def factor(idVar):
    #print("factor")
    global tokenType, tokenString, lineno
    t = None
    if(idVar != None):
        return idVar

    if(tokenType == TokenType.ID):
        t = var()
    elif(tokenType == TokenType.OPENB):
        match(TokenType.OPENB)
        t = expression()
        match(TokenType.CLOSEB)
    elif(tokenType == TokenType.NUM):
        t = nuevoExpNodo(ExpTipo.CONST)
        t.val = tokenString
        match(TokenType.NUM)
    else:
        error("unexpected token -> tok - no termina la expresion \n")
    return t
    
def args():
    # print("args")
    global tokenType, tokenString, lineno
    t=None
    if tokenType == TokenType.ID or tokenType == TokenType.NUM or tokenType == TokenType.OPENB:
        t = expression()
        q = t
        while(tokenType == TokenType.COMMA):
            match(TokenType.COMMA)
            p = q
            if(q != None and p !=None):
                q = expression()
                p.sibling = q
                p = q
    return t
    