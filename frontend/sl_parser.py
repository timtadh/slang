#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from ply import yacc
from sl_lexer import tokens, Lexer
from ast import Node

## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    tokens = tokens
    precedence = (
    )

    def __new__(cls, **kwargs):
        ## Does magic to allow PLY to do its thing.
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.table = dict()
        self.loc = list()
        self.yacc = yacc.yacc(module=self,  tabmodule="sl_parser_tab", debug=0, **kwargs)
        return self.yacc

    def get_table(self):
        c = self.table
        for s in self.loc:
            c = self.table[c]
        return c

    def p_Start(self, t):
        'Start : Stmts'
        t[0] = t[1]

    def p_Stmts1(self, t):
        'Stmts : Stmts Stmt'
        for stmt in t[2]:
            t[1].addkid(stmt)
        t[0] = t[1]

    def p_Stmts2(self, t):
        'Stmts : Stmt'
        stmts = Node('Stmts')
        for stmt in t[1]:
            stmts.addkid(stmt)
        t[0] = stmts

    # If you want to add this back you have to add SEMI colons or line
    # terminators to the language, yuck.
    #def p_Stmt1(self, t):
        #'Stmt : Expr SEMI'
        #t[0] = t[1]

    def p_Stmt0(self, t):
        'Stmt : PRINT Expr'
        t[0] = [ Node('Print').addkid(t[2]) ]

    def p_Stmt1(self, t):
        'Stmt : Call'
        t[0] = [ t[1] ]

    def p_Stmt2(self, t):
        'Stmt : AssignExpr'
        t[0] = [ t[1] ]

    def p_Stmt3(self, t):
        'Stmt : NAME EQUAL FuncDecl'
        t[0] = [ Node('Assign').addkid(t[1]).addkid(t[3]) ]

    def p_Stmt4(self, t):
        'Stmt : IF BooleanExpr Block'
        t[0] = [ Node('If').addkid(t[2]).addkid(t[3]) ]

    def p_Stmt5(self, t):
        'Stmt : IF BooleanExpr Block ELSE Block'
        t[0] = [ Node('If').addkid(t[2]).addkid(t[3]).addkid(t[5]) ]

    def p_Stmt6(self, t):
        'Stmt : VAR NAME'
        t[0] = [ Node('Var').addkid(t[2]) ]

    def p_Stmt7(self, t):
        'Stmt : VAR NAME EQUAL Expr'
        t[0] = [ Node('Var').addkid(t[2]).addkid(t[4]) ]

    def p_Stmt8(self, t):
        'Stmt : VAR NAME EQUAL FuncDecl'
        t[0] = [ Node('Var').addkid(t[2]).addkid(t[4]) ]

    def p_Stmt9(self, t):
        'Stmt : WHILE BooleanExpr Block'
        t[0] = [ Node('While').addkid(t[2]).addkid(t[3]) ]

    def p_Stmt10(self, t):
        'Stmt : FOR DeclAssignExpr SEMI BooleanExpr SEMI AssignExpr Block'
        stmts = t[7]
        stmts.addkid(t[6])
        t[0] = [t[2], Node('While').addkid(t[4]).addkid(stmts)]

    def p_AssignExpr(self, t):
        'AssignExpr : NAME EQUAL Expr'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_DeclAssignExpr(self, t):
        'DeclAssignExpr : VAR NAME EQUAL Expr'
        t[0] = Node('Var').addkid(t[2]).addkid(t[4])

    def p_Block(self, t):
        'Block : LCURLY BlockStmts RCURLY'
        t[0] = t[2]

    def p_LoopStmts1(self, t):
        'BlockStmts : BlockStmts Stmt'
        for stmt in t[2]:
            t[1].addkid(stmt)
        t[0] = t[1]

    def p_LoopStmts2(self, t):
        'BlockStmts : BlockStmts LoopControlStmt'
        for stmt in t[2]:
            t[1].addkid(stmt)
        t[0] = t[1]

    def p_LoopStmts3(self, t):
        'BlockStmts : Stmt'
        stmts = Node('Stmts')
        for stmt in t[1]:
            stmts.addkid(stmt)
        t[0] = stmts

    def p_LoopStmts4(self, t):
        'BlockStmts : LoopControlStmt'
        stmts = Node('Stmts')
        for stmt in t[1]:
            stmts.addkid(stmt)
        t[0] = stmts

    def p_LoopControlStmt1(self, t):
        'LoopControlStmt : BREAK'
        t[0] = [ Node('Break').addkid(t[1]) ]

    def p_LoopControlStmt2(self, t):
        'LoopControlStmt : CONTINUE'
        t[0] = [ Node('Continue').addkid(t[1]) ]

    def p_FuncDecl1(self, t):
        'FuncDecl : FUNC LPAREN RPAREN LCURLY Return RCURLY'
        t[0] = Node('Func').addkid(t[5])

    def p_FuncDecl2(self, t):
        'FuncDecl : FUNC LPAREN RPAREN LCURLY Stmts Return RCURLY'
        t[0] = (
            Node('Func')
                .addkid(t[5])
                .addkid(t[6])
        )

    def p_FuncDecl3(self, t):
        'FuncDecl : FUNC LPAREN DParams RPAREN LCURLY Return RCURLY'
        t[0] = (
            Node('Func')
                .addkid(t[3])
                .addkid(t[6])
        )
    def p_FuncDecl4(self, t):
        'FuncDecl : FUNC LPAREN DParams RPAREN LCURLY Stmts Return RCURLY'
        t[0] = (
            Node('Func')
                .addkid(t[3])
                .addkid(t[6])
                .addkid(t[7])
        )

    def p_Return1(self, t):
        'Return : RETURN'
        t[0] = Node('Return')

    def p_Return2(self, t):
        'Return : RETURN Expr'
        t[0] = Node('Return').addkid(t[2])

    def p_Expr(self, t):
        'Expr : AddSub'
        t[0] = Node('Expr').addkid(t[1])

    def p_AddSub1(self, t):
        'AddSub : AddSub PLUS MulDiv'
        t[0] = Node('+').addkid(t[1]).addkid(t[3])

    def p_AddSub2(self, t):
        'AddSub : AddSub DASH MulDiv'
        t[0] = Node('-').addkid(t[1]).addkid(t[3])

    def p_AddSub3(self, t):
        'AddSub : MulDiv'
        t[0] = t[1]

    def p_MulDiv1(self, t):
        'MulDiv : MulDiv STAR Atomic'
        t[0] = Node('*').addkid(t[1]).addkid(t[3])

    def p_MulDiv2(self, t):
        'MulDiv : MulDiv SLASH Atomic'
        t[0] = Node('/').addkid(t[1]).addkid(t[3])

    def p_MulDiv3(self, t):
        'MulDiv : Atomic'
        t[0] = t[1]

    def p_Atomic1(self, t):
        'Atomic : Value'
        t[0] = t[1]

    def p_Atomic2(self, t):
        'Atomic : LPAREN Expr RPAREN'
        t[0] = t[2]

    def p_Value1(self, t):
        'Value : INT_VAL'
        t[0] = Node('INT').addkid(t[1])

    def p_Value2(self, t):
        'Value : NAME'
        t[0] = Node('NAME').addkid(t[1])

    def p_Value3(self, t):
        'Value : Call'
        t[0] = t[1]

    def p_Call1(self, t):
        'Call : NAME LPAREN Params RPAREN'
        t[0] = Node('Call').addkid(t[1]).addkid(t[3])

    def p_Call2(self, t):
        'Call : NAME LPAREN RPAREN'
        t[0] = Node('Call').addkid(t[1])

    def p_Params1(self, t):
        'Params : Params COMMA Expr'
        t[0] = t[1].addkid(t[3])

    def p_Params2(self, t):
        'Params : Expr'
        t[0] = Node('Params').addkid(t[1])

    def p_DParams1(self, t):
        'DParams : DParams COMMA NAME'
        t[0] = t[1].addkid(t[3])

    def p_DParams2(self, t):
        'DParams : NAME'
        t[0] = Node('DParams').addkid(t[1])

    def p_BooleanExpr(self, t):
        'BooleanExpr : OrExpr'
        t[0] = Node('BooleanExpr').addkid(t[1])

    def p_OrExpr1(self, t):
        'OrExpr : OrExpr OR AndExpr'
        t[0] = Node('Or').addkid(t[1]).addkid(t[3])

    def p_OrExpr2(self, t):
        'OrExpr : AndExpr'
        t[0] = t[1]

    def p_AndExpr1(self, t):
        'AndExpr : AndExpr AND NotExpr'
        t[0] = Node('And').addkid(t[1]).addkid(t[3])

    def p_AndExpr2(self, t):
        'AndExpr : NotExpr'
        t[0] = t[1]

    def p_NotExpr1(self, t):
        'NotExpr : NOT BooleanTerm'
        t[0] = Node('Not').addkid(t[2])

    def p_NotExpr2(self, t):
        'NotExpr : BooleanTerm'
        t[0] = t[1]

    def p_BooleanTerm1(self, t):
        'BooleanTerm : CmpExpr'
        t[0] = t[1]

    def p_BooleanTerm5(self, t):
        'BooleanTerm : LPAREN BooleanExpr RPAREN'
        t[0] = t[2]

    def p_CmpExpr(self, t):
        'CmpExpr : Expr CmpOp Expr'
        t[0] = t[2].addkid(t[1]).addkid(t[3])

    def p_CmpOp(self, t):
        '''CmpOp : EQEQ
                | NQ
                | LT
                | LE
                | GT
                | GE'''
        t[0] = Node(t[1])

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        f = func(x) {
            if (x > 0) {
                if (x/2 + x/2 == x) { // then it is even
                    c = f(x+1)
                } else {
                    c = f(x-3)
                }
            } else {
                if (x < 5) {
                    if (x != 0) {
                        x = x - 1
                    }
                    c = x
                } else {
                    c = 10
                }
            }
            return c
        }
        print f(10)
    ''', lexer=Lexer()).dotty()
