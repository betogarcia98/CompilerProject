import enum
class TokenType(enum.Enum):
    DEFAULT =""
    MAS = 1
    MENOS = 2
    MULT = 3
    DIV = 4
    MENORIGUAL = 5
    MAYORIGUAL = 6
    IGUALIGUAL = 7
    NOT = 8
    PUNTOYCOMA = 9
    COMA = 10
    PARENTESISABRIR = 11
    PARENTESISCERRAR = 12
    CORCHETEABRIR = 13
    CORCHETECERRAR = 14
    LLAVEABRIR = 15
    LLAVEACERRAR = 16
    COMENTARIO = 18
    MENOR = 19
    MAYOR = 20
    IGUAL = 21
    DIFERENTE = 22
    ERROR = 23
    ID = 24
    NUM = 25
    ENDFILE = 34
    ELSE = 26
    IF = 27
    INT = 28
    RETURN = 29
    VOID = 30
    WHILE = 31
    pass

