from globalTypes import *

def globalesLexer(prog, pos, long):
    global programa
    global posicion
    global progLong
    global contador
    global numLinea
    programa = prog
    posicion = pos
    progLong = long
    numLinea = 1
    #se inicializa el contador que controlará la lectura de la string del archivo
    contador = pos

    #para poder leer el último token
    programa = programa.replace('$','\n$')
    pass

with open('matriz.txt') as f:
    fil, col = [int(x) for x in next(f).split()]
    simbolos = next(f).split('.')
    M = [[int(x) for x in line.split()] for line in f]
    simbolos2 = []
    for simbolo in simbolos:
        if len(simbolo) >1:
            simbolos2.extend(list(simbolo))
        # elif simbolo == '!':
        #     pass
        else:
            simbolos2.append(simbolo)

mapa = {}
for i in range(len(simbolos)):
    for c in simbolos[i]:
        mapa[c]=i

'''
Funcion que regresa el tipo de token y el token que corresponde, de igual forma
informa si tiene un error en el lexico y el tipo de error, en caso de caracteres no validos y 
construcciones de identificadores y numeros incorrectas
'''
def getToken(imprime = True):
    global programa
    global posicion
    global progLong
    global contador
    global numLinea
    global imprimeG
    imprimeG = imprime
    token = ''

    archivo = programa
    
    estado = 0
    
    #mientras el archivo no termine
    c=''
    while (c != '$'):
        #obtiene el caracter correspondiente a la posición del archivo
        c = archivo[contador]
        if ( c=='\n' and estado != 30): #contar el numero de linea en el que se encuentra y si no se encuentra en el estado de signo de admiración
            numLinea += 1
        
        #agregar todo lo que venga después de un comentario
        while c not in simbolos and (estado ==24 or estado==26):
            token +=c
            contador += 1
            c = archivo[contador]
        #en caso de encontrar un caracter invalido mandar el error correspondiente
        if c not in simbolos2 and estado !=24 and estado!=26:
            token +=c
            contador += 1
            errorFunction(numLinea+1, "Caracter invalido ", token)
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.ERROR,"\t \t",auxToken)
            return numLinea, TokenType.ERROR, auxToken
        #obtener el estado correspondiente si pertenece a los simbolos
        if c in simbolos2:
            estado = M[estado][mapa[c]]
        #terminar el ciclo en caso de haber terminado de leer el archivo
        if c=='$':
            return numLinea, TokenType.ENDFILE, token
        if estado == 2:  #token de numero
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.NUM,"\t \t",auxToken)
            return numLinea, TokenType.NUM, auxToken
        elif estado == 12: # token de identificador
            auxToken = token
            token = ''
            estado = 0
            #checar si no pertenece a las palabras reservadas del lenguaje
            if auxToken in reservedKeyWords:
                if auxToken == "else":
                    printea(TokenType.ELSE,"\t \t",auxToken)
                    return numLinea, TokenType.ELSE, auxToken
                elif auxToken == "if":
                    printea(TokenType.IF,"\t \t",auxToken)
                    return numLinea, TokenType.IF, auxToken
                elif auxToken == "int":
                    printea(TokenType.INT,"\t \t",auxToken)
                    return numLinea, TokenType.INT, auxToken
                elif auxToken == "return":
                    printea(TokenType.RETURN,"\t \t",auxToken)
                    return numLinea, TokenType.RETURN, auxToken
                elif auxToken == "void":
                    printea(TokenType.VOID,"\t \t",auxToken)
                    return numLinea, TokenType.VOID, auxToken
                elif auxToken == "while":
                    printea(TokenType.WHILE,"\t \t",auxToken)
                    return numLinea, TokenType.WHILE, auxToken
                else:
                    printea(TokenType.ERROR,"\t \t",auxToken)
                    return numLinea, TokenType.ERROR, auxToken
            else:
                printea(TokenType.ID,"\t \t",auxToken)
                return numLinea, TokenType.ID, auxToken
        elif estado == 34: #error de numero en id
            auxToken = token
            errorFunction(numLinea, "Error en la formación de un identificador ", token)
            token = ''
            estado = 0
            printea(TokenType.ERROR,"\t \t",auxToken)
            return numLinea, TokenType.ERROR, auxToken
        elif estado == 33: #error de letra en digitos
            auxToken = token
            errorFunction(numLinea, "Error en la formación de un numero ", token)
            token = ''
            estado = 0
            printea(TokenType.ERROR,"\t \t",auxToken)
            return numLinea, TokenType.ERROR, auxToken
        elif estado == 35: #error de signo de admiracion
            auxToken = token
            errorFunction(numLinea, "Error en la formación de un diferenciador ", token)
            token = ''
            estado = 0
            printea(TokenType.ERROR,"\t \t",auxToken)
            return numLinea, TokenType.ERROR, auxToken
        elif estado == 18: #paretesis que abre
            token += c #se agrega el ultimo caracter al token para que lo reconozca sin saber qué sigue y esto se repite para varios caracteres
            auxToken = token
            token = ''
            estado = 0
            contador += 1 #se mueve el contador al siguiente caracter y esto también se repite en los tokens de caracteres únicos
            printea(TokenType.OPENB,"\t \t",auxToken)
            return numLinea, TokenType.OPENB, auxToken
        elif estado == 19: #paretesis que cierra
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.CLOSEB,"\t \t",auxToken)
            return numLinea, TokenType.CLOSEB, auxToken
        elif estado == 20: #paretesis cuadrado que abre
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.OPENSQUAREB,"\t \t",auxToken)
            return numLinea, TokenType.OPENSQUAREB, auxToken
        elif estado == 21: #paretesis cuadrado que cierra
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.CLOSESQUAREB,"\t \t",auxToken)
            return numLinea, TokenType.CLOSESQUAREB, auxToken
        elif estado == 22:  #paretesis curly que abre
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.OPENCURLYB,"\t \t",auxToken)
            return numLinea, TokenType.OPENCURLYB, auxToken
        elif estado == 23: #paretesis curly que cierra
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.CLOSECURLYB,"\t \t",auxToken)
            return numLinea, TokenType.CLOSECURLYB, auxToken
        elif estado == 3: #signo más
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.PLUS,"\t \t",auxToken)
            return numLinea, TokenType.PLUS, auxToken
        elif estado == 4: #signo menos
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.LESS,"\t \t",auxToken)
            return numLinea, TokenType.LESS, auxToken
        elif estado == 5: #signo de multiplicacion
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.MULT,"\t \t",auxToken)
            return numLinea, TokenType.MULT, auxToken
        elif estado == 25: # signo de division
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.DIV,"\t \t",auxToken)
            return numLinea, TokenType.DIV, auxToken
        elif estado == 14: # signos de comparacion
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.EQUAL,"\t \t",auxToken)
            return numLinea, TokenType.EQUAL, auxToken
        elif estado == 15: #signo de asignacion o igual
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.ASSIGN,"\t \t",auxToken)
            return numLinea, TokenType.ASSIGN, auxToken
        elif estado == 29: #signo de menor que
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.LOWERTHAN,"\t \t",auxToken)
            return numLinea, TokenType.LOWERTHAN, auxToken
        elif estado == 28: #signo de mayor que
            auxToken = token
            token = ''
            estado = 0
            printea(TokenType.GREATERT,"\t \t",auxToken)
            return numLinea, TokenType.GREATERT, auxToken
        elif estado == 16: #signo de punto y coma
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.SEMICOL,"\t \t",auxToken)
            return numLinea, TokenType.SEMICOL, auxToken
        elif estado == 17: # signo de coma
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.COMMA,"\t \t",auxToken)
            return numLinea, TokenType.COMMA, auxToken
        elif estado == 9: # signo de menor o igual que
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.LTEQUAL,"\t \t",auxToken)
            return numLinea, TokenType.LTEQUAL, auxToken
        elif estado == 10: #signo de mayor o igual que
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.GTEQUAL,"\t \t",auxToken)
            return numLinea, TokenType.GTEQUAL, auxToken
        elif estado == 31: #signo de exclamación con un signo de igual, signo de diferencia
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.DIFF,"\t \t",auxToken)
            return numLinea, TokenType.DIFF, auxToken
        elif estado == 27: #estado de fin de comentario
            token += c
            auxToken = token
            token = ''
            estado = 0
            contador += 1
            printea(TokenType.COMMENT,"\t \t",auxToken)
            return numLinea, TokenType.COMMENT, auxToken
        elif estado == 0: #cuando el estado es 0 solamente sumar a la  posición
            contador += 1
        elif estado != 0:
            token +=c
            contador += 1
    pass
#función para imprimir solamente cuando sea requerido
def printea(tipotoken, cadena, token):
    if imprimeG:
        print(tipotoken, cadena, token)
    pass

'''
    Función para hacer visibles los errores en la consola
    numeroLinea = número de linea donde se encontró el error
    mensaje = el mensaje de error correspondiente
    y a su vez poner un acento circunflejo que indique el lugar del error
'''
def errorFunction(numeroLinea, mensaje, token):
    auxArchivo = programa.split('\n')
    #numeroLinea += -1
    print("Linea ", numeroLinea," : ", mensaje)
    lineaError = auxArchivo[numeroLinea-1].replace('\n',' ')
    print(lineaError)
    espacios = ''
    for x in range(lineaError.find(token)):
        espacios+=" "
    print(espacios+"^")
    pass