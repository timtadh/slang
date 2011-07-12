slang : Simple Language
=======================

Slang is going to be a very simple functional language to be used to teach the
basics of interpretation and compilation.

### Current status:

1. Documentation [In Progress]
1. Lexer [Done]
1. Simple Grammar [Done]
1. Parser [Done]
1. AST Definition [Done]
1. Symbol Table [Functional]
1. IR Generation [Functional]
1. Simple Code Generation for the SRVM* [Functional]
1. Complex Code Generation for the SRVM [Not Started]
1. Simple Code Generation for x86 [Not Started]
1. Complex Code Generation for x86 [Not Started]

[*] SRVM : Simple Register based Virtual Machine <br/>
a virtual machine of my own devising to demonstrate the basics of a VM.

Table of Contents
-----------------

1. Quick Example Program
1. The SRVM
2. Slang Language Spec


Quick Example Program
---------------------

Here is the language as it currently stands. It has more syntax than this, but
this syntax is pretty stable. It does not currently support closures.

    g = func() {
        g1 = func() { return g2() }
        g2 = func() { return g3() }
        g3 = func() { return h() }
        return g1()
    }
    h = func() { return f() }
    f = func() { return 5 / 4 * 2 + 10 - 5 * 2 / 3 }
    print g()


Intermediate Representations
----------------------------

There are two intermediate representations used in slang. The first
representation, an AST, is closely tied to the grammar of slang. The AST is
directly generated by the various parser front ends. The second representation,
quads, is independent of the grammar and may eventually be the target of more
than one language. 

The AST representation is a redundant representation, however it is useful for
two purposes. First, it allows for the demonstration of multiple parsing
algorithms without an exorbitant amount of work on any particular parser. The
"smarts" are put in the generation of the quads based off of the AST. 

### AST

The AST is currently undocumented. This is intentional as the language itself
has not been standardized. Once the language stabilizes the AST will be
documented to allow easy interoperability. Until then, if you "want to know"
the best approach is too generate the graphviz from a code fragment you are
interested in. eg.

    --- make_viz.py

    from sl_parser import Parser
    from sl_lexer import Lexer

    print Parser().parse('''
        if (1 > 2) {
        print 1
        } else {
        print 2
        }
        ''', lexer=Lexer()).dotty()

    --------

    python make_viz.py | dot -Tpng -o test.png

### Quads

coming soon! :-p

The SRVM Language
-----------------
The SRVM (Simple Register based Viritual Machine) is a simple virtual machine
built for 2 purposes. 1) I want to demonstrate code generation without having
to explain x86. 2) I want to demonstrate what a VM could look like and how to
implement one. I made it as simple as possible. It doesn't even currently have a
branch instruction. If it turns out I need it I can always add it in later. This
instruction set is viable for doing basic operations.

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

There is currently no assembler for the language. I generate the instructions
as Python tuples.

#### Example
This gets 2 variables from the stack and adds them together

    code = [
        (IMM, 3, 0), # load args
        (ADD, 3, 0),
        (IMM, 4, 1),
        (ADD, 4, 0),
        (LOAD, 3, 3),
        (LOAD, 4, 4),
        (ADD, 4, 3), # do addition
    ]


Slang Langauge Spec
-------------------

Tokens:

    NAME     : '([a-zA-Z_])(([a-zA-Z_])|([0-9]))*'
    INT      : '(-?0[xX]([a-fA-F0-9])+)|(-?([0-9])+)'
    RETURN   : 'return'
    FUNC     : 'func'
    PRINT    : 'print'
    IF       : 'if'
    else     : 'else'
    COMMA    : ','
    LPAREN   : '('
    RPAREN   : ')'
    LCURLY   : '{'
    RCURLY   : '}'
    EQUAL    : '='
    EQEQ     : '=='
    NQ       : '!='
    LT       : '<'
    LE       : '<='
    GT       : '>'
    SLASH    : '\/'
    STAR     : '\*'
    DASH     : '\-'
    PLUS     : '\+'

Productions:


    Start       : Stmts
    Stmts       : Stmts Stmt
    Stmts       : Stmt
    Stmt        : PRINT Expr
    Stmt        : Call
    Stmt        : NAME EQUAL Expr
    Stmt        : NAME EQUAL FUNC LPAREN RPAREN LCURLY Return RCURLY
    Stmt        : NAME EQUAL FUNC LPAREN RPAREN LCURLY Stmts Return RCURLY
    Stmt        : NAME EQUAL FUNC LPAREN DParams RPAREN LCURLY Return RCURLY
    Stmt        : NAME EQUAL FUNC LPAREN DParams RPAREN LCURLY Stmts Return RCURLY
    Stmt        : IF LPAREN BooleanExpr RPAREN LCURLY Stmts RCURLY
    Stmt        : IF LPAREN BooleanExpr RPAREN LCURLY Stmts RCURLY ELSE LCURLY Stmts RCURLY
    Return      : RETURN
    Return      : RETURN Expr
    Expr        : AddSub
    AddSub      : AddSub PLUS MulDiv
    AddSub      : AddSub DASH MulDiv
    AddSub      : MulDiv
    MulDiv      : MulDiv STAR Atomic
    MulDiv      : MulDiv SLASH Atomic
    MulDiv      : Atomic
    Atomic      : Value
    Atomic      : LPAREN Expr RPAREN
    Value       : INT_VAL
    Value       : NAME
    Value       : Call
    Call        : NAME LPAREN Params RPAREN
    Call        : NAME LPAREN RPAREN
    Params      : Params COMMA Expr
    Params      : Expr
    DParams     : DParams COMMA NAME
    DParams     : NAME
    BooleanExpr : OrExpr
    OrExpr      : OrExpr OR AndExpr
    OrExpr      : AndExpr
    AndExpr     : AndExpr AND NotExpr
    AndExpr     : NotExpr
    NotExpr     : NOT BooleanTerm
    NotExpr     : BooleanTerm
    BooleanTerm : CmpExpr
    BooleanTerm : LPAREN BooleanExpr RPAREN
    CmpExpr     : Expr CmpOp Expr
    CmpOp       : EQEQ
    CmpOp       : NQ
    CmpOp       : LT
    CmpOp       : LE
    CmpOp       : GT
    CmpOp       : GE

