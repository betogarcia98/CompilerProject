from globalTypes import *               #Importar los Enum, para la definición de los tokens

def globales(prog, pos, long):          #Función para definir los valores iniciales de las variables globales
    global programa                     #Variable que contiene un string con todo el programa para revisar
    global posicion                     #Variable para controlar la posición del programa que se esta revisando
    global progLong                     #Variable que contiene la longitud de la cadena del programa (Sin contar el token de )
    global charCounter                  #Variable para contar el número de caracteres (manejo de errores) 
    global lineCumulative               #Variable para guardar toda la cadena de la línea actual (manejo de errore)
    global lineCounter                  #Variable para contar el número de líneas que se han procesado (manejo de errores)
    #Asignaciones de los valores#
    programa = prog                     
    posicion = pos
    progLong = long
    charCounter = 0
    lineCumulative = ""
    lineCounter = 0
'''
Función para asignar el TokenType de las palabras reservadas,
recibe como parámetro el string que representa una palabra reservada
y regresa el valor de tipo TokenType.
'''
def getTokenType(palabra):          
    if(palabra=="else"):
        return TokenType.ELSE
    elif(palabra=="if"):
        return TokenType.IF
    elif(palabra=="int"):
        return TokenType.INT
    elif(palabra=="return"):
        return TokenType.RETURN
    elif(palabra=="void"):
        return TokenType.VOID
    elif(palabra=="while"):
        return TokenType.WHILE

#Arreglo que contiene las cadenas de palabras reservadas permitidas en el lenguaje
PalabrasReservadas = ["else","if","int","return","void","while"]    
#Arreglos para el control de la lógica del flujo entre los estados
#Conjuto de estados terminales
EstadosTerminal = [1,2,3,6,8,10,12,13,14,15,16,17,18,19,20,25,26,27,28,29,30,32,33,34]     
#Conjunto de estados finales que solo procesan un cáracter
EstadosTokenUnico = [1,2,3,6,8,10,12,13,14,15,16,17,18,19,20,25]    
'''
Función para imprimir errores del parser
Recibe el valor del token que causó error y el tipo de expresió que no pudo formar
'''
def markActualError(tokenValue, failedExpression):
    #Se definen las variables que se van a utilizar como globales (para que no tengan valor local)
    global lineCounter
    global lineCumulative
    print("Error creating "+failedExpression+":")
    print("Unexpected Token: '"+tokenValue+"' at line "+str(lineCounter+1)+":")    #Imprimir detalles de error
    print(lineCumulative+"")                                            #Imprimir la línea que contiene el error y el acento circunflejo
    indicator = ""
    for i in range(len(lineCumulative)-2):
        indicator+=" "
    indicator+="^"
    print(indicator)

'''
Función de control
Recibe un parámetro booleano para indicar si se desea que se impriman los tokens
'''
def getToken(imprimir = True):
    #Se definen las variables que se van a utilizar como globales (para que no tengan valor local)
    global programa                                     
    global posicion
    global progLong
    global charCounter
    global lineCumulative
    global lineCounter
    #Generar la matriz desde el archivo de texto, además generar una lista con todos los caracteres válidos del lenguaje
    with open('matriz.txt') as f:
        fil, col = [int(x) for x in next(f).split()]
        simbolos = next(f).split('.')
        simbol = []
        for s in simbolos:
            if len(s) == 1:
                simbol.append(s)
            else:
                simbol.extend(list(s))
        M = [[int(x) for x in line.split()] for line in f]

    estado = 0                      #Estado para el control con la matriz de estados
    token = ''                      #Variable para almacenar el token a desplegar
    unexpectedTkn =""               #Variable para capturar caracteres inesperados durante la revisión del programa (Manejo de errores)
    findPosition = 0                #Variable para guardar la posición en la que se encontró el caracter inesperado (Manejo de errores)
    #Mapa de caracteres para los conjuntos de símbolos que representan las columnas de la matriz de cambios de estado
    mapa = {}                       
    for i in range(len(simbolos)):
            for c in simbolos[i]:
                mapa[c]=i

    p=posicion                      #La p se define como la posición a revisar del programa, es la variable con la que se recorre el archivo durante el ciclo
    while(p<=progLong):             #Prácticamente un ciclo ilimitado porque el manejo del final de ejecución es con el Token de ENDFILE
        tType = TokenType.DEFAULT   #Definir el tipo default de TokenType
        c = programa[p]             #El caracter a revisar es el que está en la posición actual
        if c not in simbol and estado !=23 and estado!=24:  #Si el caracter no está en los símbolos permitidos y no se está leyendo un comentario
            p+=1                                                #Incrementar  la posición en la que se està revisando
            posicion = p                                        #Asignarlo a la variable global
            lineCumulative+=c                                   #Añadir el cáracter al valor actual de la línea completa
            print("Unexpected Token: '"+c+"' at line "+str(lineCounter)+":")    #Imprimir detalles de error
            print(lineCumulative+"")                                            #Imprimir la línea que contiene el error y el acento circunflejo
            indicator = ""
            for i in range(len(lineCumulative)-2):
                indicator+=" "
            indicator+="^"
            print(indicator)
            token+=c                                                            #Añadir el caracter que causo error al Token de error
            return TokenType.ERROR,token                                        #Regresa el error
        elif(c=='\n'):                                      #Si el token que llegó es un salto de línea
            lineCounter+=1                                      #Aumentar en uno el contador de líneas
            charCounter=0                                       #Establecer en 0 el número de caracteres en la línea nueva
            lineCumulative =""                                  #Vaciar el contenido de la línea actual
            if(estado==23 or estado==24):                       #Si se esta recibiendo un comentario
                token+=c                                            #Añadir el salto de línea al token
        elif c == '$':                                      #Si el caracter recibido es el fin de archivo
            tType = TokenType.ENDFILE                           #Devolver el TokenType correspondiente y regresar los valores
            token = "$ "
            break
        else:                                               #Si no hay ninguna consideración de cáracter especial
            if c in simbol:                                     #Si el caracter está en los símbolos permitidos
                estado = M[estado][mapa[c]]                         #Calcular el estado nuevo con la matriz de estados
        if estado != 0:                                     #Si el estado es diferente al inicial (Donde se recibe cualquier caracter de separación)
            token += c                                          #Añadir el caracter al token actual

        #Eleccion del TokenType basado en cada uno de los estados terminales
        if estado==1:
            tType = TokenType.MAS
        elif estado==2:
            tType = TokenType.MENOS
        elif estado==3 :
            tType = TokenType.MULT
        elif estado==6:
            tType = TokenType.MENORIGUAL
        elif estado==8:
            tType = TokenType.MAYORIGUAL
        elif estado==10:
            tType = TokenType.IGUALIGUAL
        elif estado==12:
            tType = TokenType.NOT
        elif estado==13:
            tType = TokenType.PUNTOYCOMA
        elif estado==14:
            tType = TokenType.COMA
        elif estado==15:
            tType = TokenType.PARENTESISABRIR
        elif estado==16:
            tType = TokenType.PARENTESISCERRAR
        elif estado==17:
            tType = TokenType.CORCHETEABRIR
        elif estado==18:
            tType = TokenType.CORCHETECERRAR
        elif estado==19:
            tType = TokenType.LLAVEABRIR
        elif estado==20:
            tType = TokenType.LLAVEACERRAR
        elif estado==25:
            tType =  TokenType.COMENTARIO
        elif estado==26:
            tType = TokenType.MENOR
        elif estado==27:
            tType = TokenType.MAYOR
        elif estado==28:
            tType = TokenType.IGUAL
        elif estado==29:
            tType = TokenType.DIV
        elif estado==30:
            tType = TokenType.DIFERENTE
        elif estado==31:                            #Estado especial, aquí es cuando se detecta un carácter 
            if(unexpectedTkn==""):                  #Asegurar que se guarde solamente el primer caracter equivocado
                unexpectedTkn=c                         #Guardar el caracter
                findPosition = charCounter              #Y su posición
        elif estado==32:                            #Estado en el que se despliega el error en identificador o número. un mecanismo muy similar al de caracter inesperado
            print("Unexpected Token: '"+unexpectedTkn+"' at line "+str(lineCounter)+":")
            print(lineCumulative)
            indicator = ""
            for i in range(len(lineCumulative)):
                if i==findPosition-1:
                    indicator+="^"
                else:
                    indicator+=" "
            print(indicator)
            tType = TokenType.ERROR
        elif estado==33:                            #Estado para guardar identificadores
            pr = token[:-1]                         #Eliminar la última posición del token (Otro caracter que debe ser analizado después)
            if pr in PalabrasReservadas:            #Si el token esta en las palabras reservadas
                tType = getTokenType(pr)                #Obtener su TokenType
            else:                                   #Si no. se trata de cualquier otro identificador
                tType = TokenType.ID                    
        elif estado==34:
            tType = TokenType.NUM
        p+=1                                        #Al final de cada revisión de caracter, aumentar la posición sobre el programa
        charCounter+=1                              #Aumentar el contador de caracteres en la línea
        lineCumulative+=c                           #Añadir el caracter al control de la línea
        if(estado in EstadosTerminal):              #Si el estado en el que estaba es terminal, romper el ciclo
            break
    if(estado not in EstadosTokenUnico):            #Si el Token es uno compuesto por un solo caracter, quitar el último caracter de todos lados
         p-=1
         token = token[:-1]
         lineCumulative = lineCumulative[:-1]
         charCounter-=1
    posicion = p
    if(imprimir):                                   #Revisar si el programa debe imprimir
        print("Token: "+tType.name+" TokenString: "+token)
    return tType, token                             #Regresar el TokenType encontrado y su valor