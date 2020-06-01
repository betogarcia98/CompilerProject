from globalTypes import *                       #Importar para el correcto funcionamiento del Parser
from semantica import *
f = ""
ifCounter = 0
whileCounter = 0
funName = ""

def getLoc(name,line):
    for scope in range(len(TablaDeSimbolos)):
        for nodo in TablaDeSimbolos[scope].nodos:
            if nodo.nombreCampo == name and line in  nodo.lineasDeAparicion:
                return nodo.memLoc, scope

def getNode(name,line):
    for scope in range(len(TablaDeSimbolos)):
        for nodo in TablaDeSimbolos[scope].nodos:
            if nodo.nombreCampo == name and line in  nodo.lineasDeAparicion:
                return nodo


def recursiveCGen(tree, imprime = True):
    global ifCounter
    global whileCounter
    global funName
    if tree == None:
        return
    checkChild = True 
    if tree.nType == TipoNodo.DEC:
        if tree.decType == DecTipo.FUNCION:
            if tree.child[0].str == "main":
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
                checkChild = False
                # f.write("START\n")
                f.write(tree.child[0].str+":\n")
                funName = tree.child[0].str
                f.write("sw $ra 0($sp)\n")
                f.write("addiu $sp $sp -4\n")
                # f.write("sw $fp 0($sp)\n")
                f.write("move $fp $sp\n")
                numeroHijos = -1
                nodo = tree.child[1]
                while 1:
                    if nodo == None:
                        break
                    numeroHijos+=1
                    nodo = nodo.sibling
                print("Size:",numeroHijos)
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
                    # numeroHijos-=1
                    nodo = nodo.sibling
                # f.write("addiu $sp $sp 4\n")
                print("N:",n)
                # f.write("move $sp $fp\n")
                spaceNeeded = 0
                for scope in TablaDeSimbolos:
                    if scope.funcionDueña == tree.child[0].str:
                        spaceNeeded+= scope.memLocScope
                        break
                
                f.write("addiu $sp $sp -4\n")
                f.write("addiu $sp $sp -"+str(spaceNeeded)+"\n")
                
                # f.write("END\n")
                recursiveCGen(tree.child[2])
                f.write("end_"+funName+":\n")
                f.write("lw $ra 4($fp)\n")
                z = 4*n + 8 + spaceNeeded
                f.write("addiu $sp $sp "+str(z)+"\n")
                f.write("lw $fp 0($sp)\n")
                f.write("jr $ra\n")
        else:
            checkChild = False
            pass
            
    elif tree.nType == TipoNodo.EXP:  
        isGlobal = False
        shouldStore = True
        if tree.expType == ExpTipo.ASSIGN:
            checkChild = False
            if tree.child[0].expType == ExpTipo.ARREGLO:
                node = getNode(tree.child[0].child[0].str,tree.lineno)
                isGlobal = True
                if tree.child[0].child[1].expType == ExpTipo.CONST:
                    ls = node.memLoc+(4*int(tree.child[0].child[1].val))
                    
                else:
                    f.write("move $t5 $a0\n")
                    recursiveCGen(tree.child[0].child[1])
                    ls = node.memLoc
                    f.write("mul $a0 $a0 4\n")
                    f.write("add $t3 $t3 $a0")
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
        elif tree.expType ==  ExpTipo.CONST:
            f.write("li $a0 "+tree.val+"\n")
        elif tree.expType == ExpTipo.IDENTIFIER:
            # print(tree.str,tree.lineno)
            ls, scope = getLoc(tree.str,tree.lineno)
            if scope == 0:
                isGlobal = True
            # f.write("here")
            if isGlobal:
                f.write("lw $a0 "+str(ls)+"($t3)\n")
            else:
                f.write("lw $a0 -"+str(ls)+"($fp)\n")
        elif tree.expType == ExpTipo.OPERATION:
            checkChild = False
            recursiveCGen(tree.child[0])
            f.write("sw $a0 0($sp)\n")
            f.write("addiu $sp $sp -4\n")
            recursiveCGen(tree.child[1])
            f.write("lw $t1 4($sp)\n")
            # print(tree.op)
            if tree.op == TokenType.PLUS:
                f.write("add $a0 $t1 $a0\n")
            elif tree.op == TokenType.LESS:
                f.write("sub $a0 $t1 $a0\n")
            elif tree.op == TokenType.MULT:
                f.write("mul $a0 $t1 $a0\n")
            elif tree.op == TokenType.DIV:
                f.write("div $a0 $t1 $a0\n")
            f.write("addiu $sp $sp 4\n")
        elif tree.expType == ExpTipo.ARREGLO:
            checkChild = False
            # f.write("#Aqui1\n")
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
                # f.write("sub $t3 $t3 "+str(ls)+"\n")
            # f.write("#Aqui2\n")
                
    elif tree.nType == TipoNodo.STMT:
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
                    # if aux_tree.type == OpTipo.ARRAY and aux_tree.child[0] != None:
                    #     aux_tree.type = OpTipo.INTEGER
                    #Buscar en la tabla de símbolos la definicion del parámetro del programa que está a punto
                    #de ser comprardo, ya que puede estar definida como arreglo aunque solo sea un identificador
                    
                    if param.arrayObj != None:          #Si el parametro debe ser un arreglo
                        this = SymTabObj("",0,"")
                        for scope in range(len(TablaDeSimbolos)):
                            for nodo in TablaDeSimbolos[scope].nodos:
                                if nodo.nombreCampo == aux_tree.str and aux_tree.lineno in  nodo.lineasDeAparicion:
                                    this = nodo
                                    break
                        param.memLoc = this.memLoc
                        # ImprimirTabla()
                        f.write("li $a0 0\n")
                        f.write("sw $a0 0($sp)\n")
                        f.write("addiu $sp $sp -4\n")
                        
                    else:                               #Si no se esperaba un arreglo
                        isGlobal = False
                        if aux_tree.expType ==  ExpTipo.CONST:
                            f.write("li $a0 "+aux_tree.val+"\n")
                        elif aux_tree.expType == ExpTipo.IDENTIFIER:
                            # print(tree.str,tree.lineno)
                            ls, scope = getLoc(aux_tree.str,aux_tree.lineno)
                            if scope == 0:
                                isGlobal = True
                            # f.write("here")
                            if isGlobal:
                                f.write("lw $a0 "+str(ls)+"($t3)\n")
                            else:
                                f.write("lw $a0 -"+str(ls)+"($fp)\n")
                        f.write("sw $a0 0($sp)\n")
                        f.write("addiu $sp $sp -4\n")
                    aux_tree = aux_tree.sibling         #Mover el nodo auxiliar al siguiente parámetro
                f.write("jal "+tree.child[0].str+"\n")
        elif tree.stmtType == StmtTipo.RETURN:
            checkChild = False
            recursiveCGen(tree.child[0])
            f.write("b end_"+funName+"\n")
            pass
            
            



            
    if checkChild:
        for child in tree.child:
            recursiveCGen(child)
    recursiveCGen(tree.sibling)


        

def codeGen(tree,file):
    global f
    print("Working...")
    # initializeFile(file)
    f = open (file,'w')
    f.write(".data\n")
    f.write("glob: .word 0\n")
    f.write(".text\n")
    f.write(".globl main\n")    
    recursiveCGen(tree)
    # f.write('aios mundo')
    f.close()
    pass

