'''
Alberto García Caballero
A01364120
'''
from globalTypes import *                       
from semantica import *
f = ""                  #Variable para escribir en el archivo
ifCounter = 0           #Variable para el control en la creación de Ifs
whileCounter = 0        #Variable para el control en la creación de Whiles
funName = ""            #Variable para el control en el término de Funciones
'''
Funcion para obtener la localización en memoria que le corresponde a un nodo de la tabla de símbolos,
recibe como parámetros el nombre del campo a buscar y el número de línea
'''
def getLoc(name,line):
    for scope in range(len(TablaDeSimbolos)):
        for nodo in TablaDeSimbolos[scope].nodos:
            if nodo.nombreCampo == name and line in  nodo.lineasDeAparicion:
                return nodo.memLoc, scope
'''
Funcion para obtener el objeto completo de la tabla de símbolos,recibe como parámetros el nombre 
del campo a buscar y el número de línea
'''
def getNode(name,line):
    for scope in range(len(TablaDeSimbolos)):
        for nodo in TablaDeSimbolos[scope].nodos:
            if nodo.nombreCampo == name and line in  nodo.lineasDeAparicion:
                return nodo

'''
Función para la generación de código, recibe de forma recursiva el AST, (el nodo inicial o sus hijos 
o hermanos de un determinado nodo), y con base en el tipo de nodo, genera el código necesario.
Recibe como parámetros el nodo del que se debe generar código y un parámetro opcional que indica si 
el nodo debe realizar generación de código en sus hermanos, o no.
'''
def recursiveCGen(tree, checkSibling = True):
    global ifCounter                        #Variable para el flujo de Ifs
    global whileCounter                     #Variable para el flujo de Whiles
    global funName                          #Variable para el control de la etiqueta en los return
    if tree == None:                        #Si el nodo es nulo, detener la ejecución, (hijo o hermano de hoja)
        return
    checkChild = True                       #Por defecto, generar el código de los hijos
    if tree.nType == TipoNodo.DEC:          #Si es una declaración
        if tree.decType == DecTipo.FUNCION:     #Si es una función
            if tree.child[0].str == "main":     #Código para la función main
                f.write("main:\n")
                f.write("la $t3 glob\n")
                f.write("move $fp $sp\n")
                spaceNeeded = 0
                for scope in TablaDeSimbolos:
                    if scope.funcionDueña == tree.child[0].str:
                        spaceNeeded+= scope.memLocScope
                        break
                print("SN:",spaceNeeded)
                f.write("addiu $sp $sp -"+str(spaceNeeded)+"\n")
            else:
                '''
                Código para cualquier otra función, guarda la return address, el control link y asigna los valores
                de los parámetros a su lugar correspondiente en las variables locales, después se genera el código
                de lo que contiene la función, y después se devuelve el $fp y el $sp al lugar en el que estaban 
                antes de llamara la función.
                '''
                checkChild = False
                f.write(tree.child[0].str+":\n")
                funName = tree.child[0].str
                f.write("sw $ra 0($sp)\n")
                f.write("addiu $sp $sp -4\n")
                f.write("move $fp $sp\n")
                numeroHijos = -1
                nodo = tree.child[1]
                while 1:
                    if nodo == None:
                        break
                    numeroHijos+=1
                    nodo = nodo.sibling
                nodo = tree.child[1]
                move = 4*(numeroHijos+1)+4
                f.write("addiu $sp $sp "+str(move)+"\n")
                n = 0
                while nodo != None:
                    if nodo.decType == DecTipo.VARIABLE:
                        n += 1
                        ls,_ = getLoc(nodo.child[0].str,nodo.child[0].lineno)
                        f.write("lw $a0 0($sp)\n")
                        f.write("sw $a0 -"+str(ls)+"($fp)\n")
                        f.write("addiu $sp $sp -4\n")
                    else:
                        f.write("addiu $sp $sp -4\n")
                        n += 1
                    nodo = nodo.sibling
                spaceNeeded = 0
                for scope in TablaDeSimbolos:
                    if scope.funcionDueña == tree.child[0].str:
                        spaceNeeded+= scope.memLocScope
                        break
                f.write("addiu $sp $sp -4\n")
                f.write("addiu $sp $sp -"+str(spaceNeeded)+"\n")
                recursiveCGen(tree.child[2])
                f.write("end_"+funName+":\n")
                f.write("lw $ra 4($fp)\n")
                z = 4*n + 8 + spaceNeeded
                f.write("addiu $sp $sp "+str(z)+"\n")
                f.write("lw $fp 0($sp)\n")
                f.write("jr $ra\n")
        else:                                   #Si no es una función, no recorrer a sus hijos
            checkChild = False
            pass
    elif tree.nType == TipoNodo.EXP:                        #Si el nodo es de tipo expresión 
        isGlobal = False                                    #Por defecto asumir que las variables son locales
        shouldStore = True 
        '''
        Si el nodo es un assign
        Establecer que no se deben de revisar los hijos del nodo
        Después generar el código del lado derecho del assign
        Ubicar la localización de la variable del lado izquierdo, ya sea arreglo o no
        Generar el código para asignar lo que se generó del lado derecho
        '''
        if tree.expType == ExpTipo.ASSIGN:      
            checkChild = False
            if tree.child[0].expType == ExpTipo.ARREGLO:
                node = getNode(tree.child[0].child[0].str,tree.lineno)
                isGlobal = True
                recursiveCGen(tree.child[1])
                if tree.child[0].child[1].expType == ExpTipo.CONST:
                    ls = node.memLoc+(4*int(tree.child[0].child[1].val))
                    
                else:
                    f.write("move $t5 $a0\n")
                    recursiveCGen(tree.child[0].child[1])
                    ls = node.memLoc
                    f.write("mul $a0 $a0 4\n")
                    f.write("add $t3 $t3 $a0\n")
                    f.write("sw $t5 "+str(ls)+"($t3)\n")
                    f.write("sub $t3 $t3 $a0\n")
                    shouldStore = False
            else:
                ls, scope = getLoc(tree.child[0].str,tree.child[0].lineno)
                if scope == 0:
                    isGlobal = True
                recursiveCGen(tree.child[1])
            if shouldStore:
                if isGlobal:
                    f.write("sw $a0 "+str(ls)+"($t3)\n")
                else:
                    f.write("sw $a0 -"+str(ls)+"($fp)\n")
            '''
            Si el nodo es una constante, cargar el contenido del nodo al acumulador
            '''
        elif tree.expType ==  ExpTipo.CONST:
            f.write("li $a0 "+tree.val+"\n")
            '''
            Si el nodo es un identificador, ubicar el lugar de la memoria donde se tien que guardar
            Y guardarlo dependiendo si es global o local
            '''
        elif tree.expType == ExpTipo.IDENTIFIER:
            ls, scope = getLoc(tree.str,tree.lineno)
            if scope == 0:
                isGlobal = True
            if isGlobal:
                f.write("lw $a0 "+str(ls)+"($t3)\n")
            else:
                f.write("lw $a0 -"+str(ls)+"($fp)\n")
            '''
            Si el nodo es una operación, generar el contenido de un lado de la operación,
            Después mover el resultado al stack, generar el código para el otro lado de la
            operación y finalmente evaluar la operación usando el stack y un regustro temporal.
            '''
        elif tree.expType == ExpTipo.OPERATION:
            checkChild = False
            recursiveCGen(tree.child[0])
            f.write("sw $a0 0($sp)\n")
            f.write("addiu $sp $sp -4\n")
            recursiveCGen(tree.child[1])
            f.write("lw $t1 4($sp)\n")
            if tree.op == TokenType.PLUS:
                f.write("add $a0 $t1 $a0\n")
            elif tree.op == TokenType.LESS:
                f.write("sub $a0 $t1 $a0\n")
            elif tree.op == TokenType.MULT:
                f.write("mul $a0 $t1 $a0\n")
            elif tree.op == TokenType.DIV:
                f.write("div $a0 $t1 $a0\n")
            f.write("addiu $sp $sp 4\n")
            '''
            Si el nodo es un arreglo
            Calcular el offset con base en el indice del arreglo
            Dependiendo de si lo que tiene dentro es una constante o no

            '''
        elif tree.expType == ExpTipo.ARREGLO:
            checkChild = False
            node = getNode(tree.child[0].str,tree.lineno)
            if tree.child[1].expType == ExpTipo.CONST:
                index = tree.child[1].val    
                ls = node.memLoc+(4*int(index))
                f.write("lw $a0 "+str(ls)+"($t3)\n")
            else:
                recursiveCGen(tree.child[1])
                f.write("mul $a0 $a0 4\n")
                f.write("add $t3 $t3 $a0\n")
                f.write("move $t1 $a0\n")
                ls,_ = getLoc(tree.child[0].str,tree.lineno)
                f.write("lw $a0 "+str(ls)+"($t3)\n")
                f.write("sub $t3 $t3 $t1\n")
    
    elif tree.nType == TipoNodo.STMT:                       #si el nodo es un statement
        '''
        Si el nodo es un if o un while
        Primero generar el nombre del las etiquetas que se usarán en caso de que sea necesario hacer branch
        Después generar el código de la condición, establecer a dónde tiene que hacer branc en caso de ser verdadera
        Generar después la parte que se ejecuta en caso de que la condición no se cumpla
        Generar las instrucciónes del final del if o while, si es while especificar que regrese al inicio
        '''
        if tree.stmtType == StmtTipo.IF or tree.stmtType == StmtTipo.WHILE:
            checkChild = False
            if tree.stmtType == StmtTipo.IF:
                localCounter = ifCounter
                ifCounter+=1
                label = "true_branch_"+str(localCounter)+"\n"
            else:
                localCounter = whileCounter
                whileCounter+=1
                f.write("start_while_"+str(localCounter)+":\n")
                label = "while_"+str(localCounter)+"\n"
            recursiveCGen(tree.child[0].child[0])
            f.write("sw $a0 0($sp)\n")
            f.write("addiu $sp $sp -4\n")
            recursiveCGen(tree.child[0].child[1])
            f.write("lw $t1 4($sp)\n")
            f.write("addiu $sp $sp 4\n")            
            if tree.child[0].op == TokenType.EQUAL:
                print("igualigual :o")
                f.write("beq $a0 $t1 "+label)
            if tree.child[0].op == TokenType.DIFF:
                print("!igual :o")
                f.write("bne $a0 $t1 "+label)
            if tree.child[0].op == TokenType.LOWERTHAN:
                print("< :o")
                f.write("slt $t2 $t1 $a0\n")
                f.write("bne $t2 $0 "+label)
            if tree.child[0].op == TokenType.GTEQUAL:
                print(">= :o")
                f.write("slt $t2 $t1 $a0\n")
                f.write("beq $t2 $0 "+label)
            if tree.child[0].op == TokenType.GREATERT:
                print("> :o")
                f.write("slt $t2 $a0 $t1\n")
                f.write("bne $t2 $0 "+label)
            if tree.child[0].op == TokenType.LTEQUAL:
                print("<= :o")
                f.write("slt $t2 $a0 $t1\n")
                f.write("beq $t2 $0 "+label)

            if tree.stmtType == StmtTipo.IF:
                f.write("false_branch_"+str(localCounter)+":\n")
                if tree.child[2] != None:
                    recursiveCGen(tree.child[2])
                f.write("b end_if_"+str(localCounter)+"\n")
                f.write("true_branch_"+str(localCounter)+":\n")
                recursiveCGen(tree.child[1])
                f.write("end_if_"+str(localCounter)+":\n")
            else:
                f.write("b end_while_"+str(localCounter)+"\n")
                f.write("while_"+str(localCounter)+":\n")
                recursiveCGen(tree.child[1])
                f.write("b start_while_"+str(localCounter)+"\n")
                f.write("end_while_"+str(localCounter)+":\n")
            '''
            Si el nodo es una llamada
            Establecer que no se genere código para los hijos
            Después verificar los casos especiales (input y output) donde se hacen syscall
            Si no fue un caso especial, traer de la tabla de símbolos el número de parámetros esperados
            Guardar la posición actal del $fp en el stack
            Generar el código para guardar el valor de cada parámetro en el stack
            Después hacer un jal hacia la etiqueta de la función
            '''
        elif tree.stmtType == StmtTipo.CALL:
            checkChild = False
            if tree.child[0].str == "output":    
                recursiveCGen(tree.child[1])
                f.write("li $v0 1\n")
                f.write("syscall\n")
            elif tree.child[0].str == "input":
                f.write("li $v0 5\n")
                f.write("syscall\n")
                f.write("move $a0 $v0\n")
            else:
                f.write("sw $fp 0($sp)\n")
                f.write("addiu $sp $sp -4\n")
                paramToCompare = []
                for scope in range(len(TablaDeSimbolos)):
                    if TablaDeSimbolos[scope].funcionDueña == tree.child[0].str:
                        paramToCompare = TablaDeSimbolos[scope].nodos
                        break
                for nodo in TablaDeSimbolos[0].nodos:
                    if nodo.nombreCampo == tree.child[0].str:
                        paramToCompare = paramToCompare[:nodo.funObj.numParam]
                aux_tree = tree.child[1]        
                for param in paramToCompare:                                                     
                    recursiveCGen(aux_tree,False)
                    f.write("sw $a0 0($sp)\n")
                    f.write("addiu $sp $sp -4\n")
                    aux_tree = aux_tree.sibling         
                f.write("jal "+tree.child[0].str+"\n")
            '''
            Si el nodo es un return, evaluar loq ue tenga del lado derecho para cargarlo al acumulador
            Y hacer un branch incindicional a la etiqueta que indica el final de la función 
            '''
        elif tree.stmtType == StmtTipo.RETURN:
            checkChild = False
            for child in tree.child:
                recursiveCGen(child)
            f.write("b end_"+funName+"\n")
        '''
        Recorrer de forma recursiva a los hijos y los hermanos del nodo, solo en caso de que se deba hacer
        '''
    if checkChild:
        for child in tree.child:
            recursiveCGen(child)
    if checkSibling:
        recursiveCGen(tree.sibling)

'''
Función inicial para la generación de código
Recibe el AST y el nombre del archivo al que se va a escribir
Abre el archivo en formato de escritura, escribe las instrucciones de Spim iniciales
Genera el código del AST
Escribe las instrucciones finales de Spim

'''
def codeGen(tree,file):
    global f
    f = open (file,'w')
    f.write(".data\n")
    f.write("glob: .word 0\n")
    f.write(".text\n")
    f.write(".globl main\n")    
    recursiveCGen(tree)
    f.write("li $v0 10\n")
    f.write("syscall\n")
    f.close()
    ImprimirTabla()