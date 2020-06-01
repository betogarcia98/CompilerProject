'''
Alberto García Caballero A01364120
Es importante mencionar que el parser que utilicé es de Iván Bruno Muñóz Yhmoff,
ya que la manera de generación del AST me pareció mucho más acertada que la mía
y más implementable, por lo que los archivos lexer.py, parser.py, matriz.txt
y globalTypes.py que se utilizan para el correcto funcionamiento del proyecto no son
de mi autoría.
'''
from globalTypes import *                       #Importar para el correcto funcionamiento del Parser
from Parser import *
'''
Clase para guardar los datos de un arreglo (En caso de que ese sea el tipo de nodo)
Se guarda el tipo del arreglo (VOID en caso de estar vacío, que es cuando se recibe de una lista de parámetros, e INT si es un entero)
Se guarda el tamaño del arreglo, para poder guardarlo en la tabla
'''
class Arr():
    def __init__(self, tipo, tamaño):
        self.tipo = tipo
        self.tamaño = tamaño
'''
Clase para guardar los datos de una función (En caso de que el nodo lo sea)
Se guarda el número de parametros que debe recibir la función
Se guarda el tipo de retorno la función (INT o VOID)
'''
class Fun():
    def __init__(self, tipo, numParam):
        self.numParam = numParam
        self.tipo = tipo
        self.paramList = []
'''
Clase para guardar los datos de cada registro que se va a guardar en la tabla de símbolos
Se guarda el nombre del campo, este es el campo más importante porque es el que no debe de repetirse en el mismo scope
Una lista que contiene los números de línea en los que está presente la variable o una llamada a la función
El tipo del objeto (Este sólo se usa al nivel de variables y es INT o VOID)
Además dos objetos, uno de arreglo y uno de función que solo se llenan en caso de que el objeto sea uno de estos dos tipos,
estos tienen un valor por defecto de None, lo que significa que es una variable
'''
class SymTabObj():    
    def __init__(self, nombreCampo, primeraAparicion, tipo, arrayObj = None, funObj = None):
        self.nombreCampo = nombreCampo
        self.lineasDeAparicion = []
        self.lineasDeAparicion.append(primeraAparicion)
        self.tipo = tipo
        self.arrayObj = arrayObj
        self.funObj = funObj
'''
Clase para guardar los objetos que se guardarán en cada nivel (scope) que se encuentra en la tabla de símbolos
Se guarda una lista que contiene los nodos de cada nivel y
Una variable que guarda el nombre del bloque al que le pertenece el scope, este puede ser tal cual la función o
el tipo de statement que lo generó
'''
class Scope():
    def __init__(self):
        self.nodos = []
        self.funcionDueña = ""
'''
Variable para guardar el flujo del stack mientras se llena la tabla de símbolos, en la primera posición
se guarda el scope 0 y después se va añadiendo el que está en uso, una vez que salga de el scope en el que se 
esta guardando se hace pop de la lista y se mete el nuevo, es sólo un registro de con que scopes se está trabajando
ya que la información como tal se va guaradando en la tabla de símbolos.
'''
stackControl = []                   
'''
Lista de scopes, que sirve para separar todos los nodos por nivel
'''
TablaDeSimbolos = []
'''
Inicialización del scope 0 (que contiene la información base de las funciones input y output y se agregan estos nodos a la tabla de símbolos)
'''
scopeActual = 0                                     #Varible global para el llenado de la tabla
stackControl.append(scopeActual)                    #Se añade el scope 0 al stack
scope0 = Scope()                                    #Se crea el objeto Scope para la tabla de símbolos
scope0.funcionDueña = "Global"
nodo = SymTabObj("outBase",0,TokenType.INT)         #Se agrega el primer nodo del scope, que contiene el tipo de parámetro que tiene la función output
scope0.nodos.append(nodo)
fun = Fun(TokenType.INT,1)
fun.paramList.append(nodo.nombreCampo)
nodo = SymTabObj("output",0,TokenType.VOID, None, fun)  #Se agrega el nodo de la función de output a la tabla
scope0.nodos.append(nodo)
nodo = SymTabObj("input",0,TokenType.INT,None,Fun(TokenType.INT,0)) #Se agrega el nodo de la función input
scope0.nodos.append(nodo)
TablaDeSimbolos.append(scope0)                      #Se agrega el scope a la tabla de símbolos
'''
Función para insertar la información de un nodo en la tabla de símbolos (En el scope correspondiente)
'''
def InsertTabla(nombreNodo, aparicion, tipo, arr = None, func = None):
    global scopeActual                                              #Se define que se va a usar el scope actual como variable global
    for nodo in TablaDeSimbolos[scopeActual].nodos:                 #Recorrer todos los nodos que hay en el scope actual
        if nombreNodo == nodo.nombreCampo:                          #Si se encuentra un nodo que tenga el nombre mandado como parámetro
            if not aparicion in nodo.lineasDeAparicion:             #Evitar entradas de número de línea duplicadas
                nodo.lineasDeAparicion.append(aparicion)            #Se añade el número de línea a la lista de apariciones del nodo encontrado
            return
    nodo = SymTabObj(nombreNodo,aparicion,tipo,arr,func)            #Términa el recorrido de los ciclos, lo que significa que no se encontró
    TablaDeSimbolos[scopeActual].nodos.append(nodo)                 #Agregar el nodo en el scope actual
'''
Función que busca el un nodo en la Tabla de símbolos (Pero solo en los scopes que haya en el stack en el momento) 
y regresa el número de scope en dónde lo encontró
'''
def BuscarScopeEnStack(nombre):
    yaExiste = False
    for nodo in TablaDeSimbolos[scopeActual].nodos:
            if nodo.nombreCampo == nombre:         
                yaExiste = True
                break
    for i in range(len(stackControl)):                              #De 0 al número de scopes que haya en el stack
        for nodo in TablaDeSimbolos[stackControl[-i-1]].nodos:      #Por cada nodo que haya en el scope (Se recorren de atrás hacia adelante)
            if nodo.nombreCampo == nombre:                          #Revisar si el nombre coincide
                return stackControl[-i-1], yaExiste                 #Y regresar el número de scope que se encontró
    return stackControl[-1], yaExiste                               #En caso de no haberlo encontrado, regresa el último scope del stack
'''
Función para imprimir los errores
'''
def errorGenerico(mensaje, string, line):
    print(mensaje,string,line)
'''
Función para generar la tabla de símbolos, recíbe el AST
'''
def table(tree, imprime = True):
    global scopeActual                      #Variables globales
    global stackControl
    if tree != None:                        #Mientras el árbol no esté vacío
        scopesDeDiferencia = 0              #Define que el número de scopes creados en el scope actual son 0 (En caso de que se creen más)
        controlArbol = False                #Para saber si se deber recorrer los nodos hijos o no (De acuerdo a la estructura del AST)
        if tree.nType == TipoNodo.EXP:      #Si el nodo es una expresión
            controlArbol = True             #Hay que recorrer a sus hijos
            if(tree.expType == ExpTipo.IDENTIFIER): #Si la expresión es de tipo identifier
                '''
                Definir el numero de scope a insertar e insertar el nodo, se manda con tipo 'DC' 
                porque no debería de ser su declaración, solo añadir una aprición
                '''
                auxScope = scopeActual                          
                scopeActual,_ = BuscarScopeEnStack(tree.str)    
                InsertTabla(tree.str,tree.lineno,"DC")
                scopeActual = auxScope
                '''
                Hacer un recorrido para encontrar el nodo recien insertado y si su tipo es DC
                significa que se uso el indentificador sin estar declarado
                '''
                for nodo in TablaDeSimbolos[scopeActual].nodos: 
                    if nodo.nombreCampo == tree.str and "DC" == nodo.tipo:
                        errorGenerico("Variable no definida ",tree.str,tree.lineno)
            '''
            Si la expresión es de tipo arreglo, hacer un prosedimiento similar al de identificador, 
            pero obteniendo el nombre del primer hijo
            '''
            if(tree.expType == ExpTipo.ARREGLO):
                auxScope = scopeActual
                scopeActual,_ = BuscarScopeEnStack(tree.child[0].str)
                arreglo = Arr(TokenType.VOID,0)
                InsertTabla(tree.child[0].str,tree.lineno,"DC",arreglo)
                table(tree.child[1])
                scopeActual = auxScope
                for nodo in TablaDeSimbolos[scopeActual].nodos: 
                    if nodo.nombreCampo == tree.child[0].str and "DC" == nodo.tipo:
                        errorGenerico("Arreglo no definido ",tree.child[0].str,tree.lineno)
                controlArbol = False                #Sus hijos no deben de recorrerse
        #Si el nodo es un statement
        elif(tree.nType == TipoNodo.STMT):
            '''
            Si es un if o un else añadir su scope al stack
            '''
            if(tree.stmtType == StmtTipo.IF or tree.stmtType == StmtTipo.WHILE):
                scopeActual+=1
                scopesDeDiferencia+=1
                stackControl.append(scopeActual)
                newScope = Scope()
                newScope.funcionDueña = tree.stmtType
                TablaDeSimbolos.append(newScope)
            controlArbol = True             #Sin importar que tipo de statement sea, recorrer sus hijos
        #Si el nodo es na declaración
        elif(tree.nType == TipoNodo.DEC):
            _,existe = BuscarScopeEnStack(tree.child[0].str)    #Revisar si no existe en el scope actual
            '''
            Si la declaración es de una función
            '''
            if(tree.decType == DecTipo.FUNCION):
                if(len(stackControl) != 1):                      #Revisar que siempre se inserten en el scope 0
                    stackControl = stackControl[:-1]
                aux_tree = tree.child[1]
                funcion = Fun(tree.str,0)
                '''
                Llenado de sus parámetros, incluyendo los nombre y el número para usarlo como referencia en el análisis semántico
                '''
                while(aux_tree != None and aux_tree.stmtType != StmtTipo.COMPOUND):
                    funcion.numParam+=1
                    funcion.paramList.append(aux_tree.child[0].str)
                    aux_tree = aux_tree.sibling
                auxScope = scopeActual
                scopeActual = 0
                #Definir que tipo regresa la función
                if tree.str == "int":
                    tipoFun = TokenType.INT
                else:
                    tipoFun = TokenType.VOID
                if existe:                              #Si ya existe en este scope, desplegar error
                    errorGenerico("La función ya está declarada:",tree.child[0].str,tree.lineno)
                else:                                   #Si no existe, insrtar el nodo en la tabla
                    InsertTabla(tree.child[0].str,tree.lineno,tipoFun,None,funcion)
                scopeActual = auxScope
                '''
                Añadir el scope de la función al stack
                '''
                scopeActual+=1
                stackControl.append(scopeActual)
                scopesDeDiferencia+=1
                newScope = Scope()
                newScope.funcionDueña = tree.child[0].str
                TablaDeSimbolos.append(newScope)
                controlArbol = True                 #Sí recorrer sus hijos
                '''
                Si el tipo de declaración es una variable, verificar que sea int y que no exista en el scope actual
                '''
            elif(tree.decType == DecTipo.VARIABLE):
                if tree.str != 'int':
                    errorGenerico("Se esperaba int", tree.child[0].str, tree.lineno)
                else:
                    if existe:
                        errorGenerico("La variable ya está declarada en este scope",tree.child[0].str,tree.lineno)
                    else:
                        InsertTabla(tree.child[0].str,tree.lineno,tree.str)
                '''
                Si el tipo de declaración es un arreglo, verificar el tipo, que no se haya declarado en el scope actual
                e insertar el nodo en la tabla de símbolos
                '''
            elif(tree.decType == DecTipo.ARREGLO):
                if tree.str != 'int':
                    errorGenerico("Se esperaba un int", tree.child[0].str, tree.lineno)
                else:
                    if existe:
                        errorGenerico("El arreglo ya está declarada en este scope",tree.child[0].str,tree.lineno)
                    else:
                        if tree.child[1] == None:
                            arreglo = Arr(TokenType.VOID,0)
                            InsertTabla(tree.child[0].str,tree.lineno,TokenType.INT,arreglo)
                        else:
                            arreglo = Arr(tree.str, tree.child[1].val)
                            InsertTabla(tree.child[0].str,tree.lineno,TokenType.INT,arreglo)                        
        #Si se deben recorrer los hijos, hacerlo
        if controlArbol:
            for child in tree.child:
                table(child)
        #Si se crearon scopes en esta llamada, sacarlos del stack
        if scopesDeDiferencia > 0:
            if len(stackControl)!=1:
                stackControl.pop()
        tree = table(tree.sibling)          #Llamar a la función con el hermano del nodo
'''
Función para imprimir la tabla de símbolos completa
'''
def ImprimirTabla():
    for scope in range(len(TablaDeSimbolos)):
        giones = "".ljust(100,"*")
        print(giones)
        print("Número de scope:",scope)
        print("Funcion o bloque:",TablaDeSimbolos[scope].funcionDueña)
        nombre  = "Nombre".ljust(19)
        tipo    = "Tipo:".ljust(19)
        tipoObj = "Tipo de objeto:".ljust(29)
        apar    = "Lineas de aparción:".ljust(30)
        if TablaDeSimbolos[scope].nodos != []:
            print(nombre,tipo,tipoObj,apar,sep=" ")
        else:
            print(">>>>>Scope vacío")
        for nodo in TablaDeSimbolos[scope].nodos:
            ImprimirNodo(nodo)
        print()
'''
Función para imprimir los datos que contiene un nodo
'''
def ImprimirNodo(n):
    print("".ljust(100,"-"))
    nombre = n.nombreCampo.ljust(19)
    tipo = str(n.tipo).ljust(19)
    apar = n.lineasDeAparicion
    if n.arrayObj == None and n.funObj == None:
        obj = "Variable".ljust(29)
        print(nombre,tipo,obj,apar,sep=" ")
    else:
        if(n.arrayObj != None):
            obj = "Arreglo".ljust(29)
            print(nombre,tipo,obj,apar,sep=" ")
            print("".ljust(19),"".ljust(19),"Tipo:",n.arrayObj.tipo,sep=" ")
            print("".ljust(19),"".ljust(19),"Tamaño:",n.arrayObj.tamaño,sep=" ")
        elif(n.funObj != None):
            obj = "Funcion".ljust(29)
            print(nombre,tipo,obj,apar,sep=" ")
            print("".ljust(19),"".ljust(19),"Tipo:",n.funObj.tipo,sep=" ")
            print("".ljust(19),"".ljust(19),"Número de parámetros:",n.funObj.numParam,sep=" ")
            print("".ljust(19),"".ljust(19),"Parámetros:",n.funObj.paramList,sep=" ")
'''
Función para realizar el análisis semántico, recibiendo el AST
'''
def checkNode(tree):
    #Mientras no esté vacío el nodo
    if tree != None:
        #Mandar llamar al función para cada hijo                 
        for child in tree.child:
            checkNode(child)
        #Y para cada hermano
        checkNode(tree.sibling)
        if tree.nType == TipoNodo.EXP:                              #Si el nodo es una expresión
            if tree.expType in [ExpTipo.IDENTIFIER, ExpTipo.CONST]: #Si es un identificador o una constante estableces que es de tipo entero
                tree.type = OpTipo.INTEGER
            elif tree.expType == ExpTipo.ARREGLO:                   #Si es de tipo arreglo 
                if tree.child[0].type != OpTipo.INTEGER:                #Y su hijo no es de tipo entero significa que lo que hay entre los corchetes no es entero
                    #Imprimir el error
                    errorGenerico("Error en el tipo en la declaración del arreglo",tree.child[0].str,tree.lineno)
                else:
                    tree.type = OpTipo.ARRAY                            #Si no, lo que hay en los corchetes es válido, el tipo del nodo es arreglo
            #Si es una operación o un assign
            elif tree.expType == ExpTipo.OPERATION or tree.expType == ExpTipo.ASSIGN:
                #Verificar que el tipo de los hijos sea entero o arreglo
                child1 = tree.child[0]
                child2 = tree.child[1]
                if child1.type not in [OpTipo.INTEGER, OpTipo.ARRAY]:
                    errorGenerico("Operando no es entero",child1.type,child1.lineno)
                if child2.type not in [OpTipo.INTEGER, OpTipo.ARRAY]:
                    errorGenerico("Operando no es entero",child2.type,child2.lineno)
                if (tree.op in booleanOperators):   #Si el operador es de tipo booleano
                    tree.type = OpTipo.BOOLEAN          #Definir que ese es el tipo
                else:           
                    tree.type = OpTipo.INTEGER      #Si no definir el tipo como entero
        if tree.nType == TipoNodo.STMT:                         #Si el tipo de nodo es un statement
            if tree.stmtType == StmtTipo.RETURN:                    #Si es un return
                if tree.child[0] != None:                       #Verificar que el tipo de retorno sea un entero
                    if tree.child[0].type != OpTipo.INTEGER:
                        errorGenerico("Return no regresa una variable de tipo entero",tree.str,tree.lineno)
            #Revisar si la expresión es booleana dentro del while
            elif tree.stmtType == StmtTipo.WHILE and tree.child[0].type != OpTipo.BOOLEAN:
                errorGenerico("El statement While esperaba una expresión boolenana","while",tree.lineno)
            #Revisar si la expresión es booleana dentro del if
            elif tree.stmtType == StmtTipo.IF and tree.child[0].type != OpTipo.BOOLEAN:  
                errorGenerico("El statement If esperaba una expresión boolenana","if",tree.lineno)
            #Si el statement es de tipo call
            elif tree.stmtType == StmtTipo.CALL:
                paramToCompare = []
                '''
                Obtener los objetos de la lista de parámetros (Ubicada en su declaración en la tabla de símbolos)
                con base en el nombre de función que tiene la llamada
                '''
                for scope in range(len(TablaDeSimbolos)):
                    if TablaDeSimbolos[scope].funcionDueña == tree.child[0].str:
                        paramToCompare = TablaDeSimbolos[scope].nodos
                for nodo in TablaDeSimbolos[0].nodos:
                    if nodo.nombreCampo == tree.child[0].str:
                        paramToCompare = paramToCompare[:nodo.funObj.numParam]
                aux_tree = tree.child[1]        #Obtener el primer parámetro de la llamada
                if(aux_tree != None and len(paramToCompare)>0): #Si hay parámetros para comparar en el programa y en la definición de la función
                    #Recorriendo todos los parámetros esperados se va revisando si los del programa son del mismo tipo
                    for param in paramToCompare:
                        if aux_tree==None:      #Si no hay parámetros en el programa, significa que no se mandaron completos
                            errorGenerico("Parametros enviados menores a los esperados",tree.child[0].str,tree.lineno)
                            break
                        #Definir como entero el arreglo si tiene un índice entero 
                        if aux_tree.type == OpTipo.ARRAY and aux_tree.child[0] != None:
                            aux_tree.type = OpTipo.INTEGER
                        #Buscar en la tabla de símbolos la definicion del parámetro del programa que está a punto
                        #de ser comprardo, ya que puede estar definida como arreglo aunque solo sea un identificador
                        this = SymTabObj("",0,"")
                        for scope in range(len(TablaDeSimbolos)):
                            for nodo in TablaDeSimbolos[scope].nodos:
                                if nodo.nombreCampo == aux_tree.str and aux_tree.lineno in  nodo.lineasDeAparicion:
                                    this = nodo
                                    break
                        if param.arrayObj != None:          #Si el parametro debe ser un arreglo
                            if this.arrayObj == None:       #Y no lo es, mandar mensaje de error
                                errorGenerico("Se esperaba arreglo",aux_tree.str,aux_tree.lineno)
                        else:                               #Si no se esperaba un arreglo
                            if this.arrayObj != None:       #Y si es, mandar mensaje de error
                                errorGenerico("No se esperaba arreglo",aux_tree.str,aux_tree.lineno)
                            else:
                                if aux_tree.type != OpTipo.INTEGER: #Verificar que se un entero, si no mandar error
                                    errorGenerico("Se esperaba un int",aux_tree.str,aux_tree.lineno)
                        aux_tree = aux_tree.sibling         #Mover el nodo auxiliar al siguiente parámetro
                    if aux_tree != None:                #Si aún quedaban parámetros por revisar, es un error
                        errorGenerico("Parametros enviados mayores a los esperados",aux_tree.str,tree.lineno)
                else:                                   #Si no hay parámetros en el código, pero si se esperaban por la declaración, mandar error
                    if len(paramToCompare)>=1:
                        errorGenerico("Parametros enviados menores a los esperados",tree.child[0].str,tree.lineno)
                '''
                Definir si la llamada es de tipo INT o tipo VOID
                '''
                for nodo in TablaDeSimbolos[0].nodos:
                    if tree.child[0].str == nodo.nombreCampo:
                        if nodo.tipo == TokenType.INT:
                            tree.type = OpTipo.INTEGER
                            tree.child[0].type = OpTipo.INTEGER
                        else:
                            tree.type = OpTipo.VOID
                            tree.child[0].type = OpTipo.VOID            
'''
Función base, se manda llamar a generación de la tabla de símbolos, si se debe imprimir aparece, y después
ejecuta la llamada a la función chackNode, que realiza el análisis semántico completo
'''
def semantica(tree, imprime = True):
    table(tree,imprime)
    if(imprime):
        ImprimirTabla()
    checkNode(tree)
    pass