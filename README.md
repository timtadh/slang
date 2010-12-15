slang : Simple Language
=======================

Slang is going to be a very simple functional language to be used to teach the
basics of interpretation and complilation.

### Current status:

1. Intermediate Language [DONE]
1. Lexer [DONE]
1. Grammar [DONE]
1. Parser [DONE]
1. AST Definition [DONE]
1. Symbol Table
1. IL Generation (subtasks need to be defined here...)
1. ...

Table of Contents
-----------------

1. Quick Example Program
1. Intermediate Language
2. Slang Langauge Spec


Quick Example Program
---------------------

Here is the type of language I am aiming for, note you will be able to define
functions on the stack.

    f = func(a, b) {
        c = add(a,b)
        return c
    }
    r = f(2,3)
    print(r)
    exit()


Intermediate Language
----------------------
The "Intermediate Language" will be used to test the compiler before conversion
to x86. Technically this isn't in anyway nessary. However, I have not done much
x86 assembly programming, so this is an easier way for me to just get started.
I made it as simple as possible. It doesn't even currently have a branch
instruction. However, based on my understanding of lambda calculus (which is
very vague actually) I shouldn't need a branch instruction. If it turns out I do
I can always add it in later. This instruction set is viable for doing basic
operations.

Here is the langauge spec, note all operands go CMD to <- from

    LOAD  to_reg  MEM[from_reg]     # load address in from_reg into to_reg
    SAVE  MEM[to_reg]  from_reg     # save reg into address in to_reg
    IMM   to_reg  CONST[32 bits]    # load constant into the reg
    J     reg                       # jump to address stored in the reg
    PC    reg                       # load pc+2 into the reg
    ADD   a, b                      # regs[a] = regs[a] + regs[b]
    SUB   a, b                      # regs[a] = regs[a] - regs[b]
    MUL   a, b                      # regs[a] = regs[a] * regs[b]
    DIV   a, b                      # regs[a] = regs[a] / regs[b]
    EXIT                            # exit program
    PRIN  reg                       # print register a

There are 5 registers for the VM:

    $0 = bp = base pointer
    $1 = fp = frame pointer
    $2 = ra = return address
    $3 = t1 = temp 1
    $4 = t2 = temp 2


Slang Langauge Spec
-------------------

Tokens:

    NAME   : '([a-zA-Z_])(([a-zA-Z_])|([0-9]))*'
    INT    : '(-?0[xX]([a-fA-F0-9])+)|(-?([0-9])+)'
    COMMA  : ','
    LPAREN : '('
    RPAREN : ')'
    LCURLY : '{'
    RCURLY : '}'
    EQUAL  : '='

Productions:

    Start : Block
    Block : Block Stmt
    Block : Stmt
    Stmt : NAME EQUAL FUNC LPAREN Dparams RPAREN LCURLY Block Return RCURLY
    Stmt : NAME EQUAL FUNC LPAREN RPAREN LCURLY Block Return RCURLY
    Stmt : NAME EQUAL Call
    Stmt : Call
    Return : RETURN Params
    Return : CONTINUE Call
    Call : NAME LPAREN Params RPAREN
    Call : NAME LPAREN RPAREN
    Dparams : Dparams COMMA NAME
    Dparams : NAME
    Params : Params COMMA Value
    Params : Value
    Value : NAME
    Value : INT
