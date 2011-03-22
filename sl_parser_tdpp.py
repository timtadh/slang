#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from tdpp.parser import BaseParser
from sl_lexer import tokens, Lexer
from ast import Node

def Lex(inpt):
    lexer = Lexer()
    lexer.input(inpt)
    for t in lexer:
        yield t

class Parser(BaseParser):

    tokens = tokens

    @BaseParser.productions('''

    Stmt        : NameStmt;

    NameStmt    : NAME NameStmt';
    NameStmt'   : Call';
    NameStmt'   : AssignStmt;

    AssignStmt  : EQUAL Assignable;
    Assignable  : Expr;
    Assignable  : Function;

    Function    : FUNC LPAREN ParamDecl LCURLY FuncBody RCURLY;
    ParamDecl   : RPAREN;
    ParamDecl   : DParams RPAREN;
    FuncBody    : Return;
    FuncBody    : Stmts Return;

    Return      : RETURN RetExpr;
    RetExpr     : Expr;
    RetExpr     : e;


    NameOrCall  : NAME NameOrCall';
    NameOrCall' : Call';
    NameOrCall' : e;

    Call'       : LPAREN Call'';
    Call''      : RPAREN;
    Call''      : Params RPAREN;

    Params      : Expr Params';
    Params'     : COMMA Expr Params';
    Params'     : e;

    DParams     : NAME DParams';
    DParams'    : COMMA NAME DParams';
    DParams'    : e;
    ''')
    def FullGrammar(self, nt, *production):
        print nt, production

    @BaseParser.production(" Start : Stmts;")
    def Start(self, nt, stmts):
        return stmts

    @BaseParser.production("Stmts : Stmt Stmts';")
    @BaseParser.production("Stmts' : Stmt Stmts';")
    def Stmts(self, nt, stmt, stmts):
        return stmts.addkid(stmt, True)

    @BaseParser.production("Stmts' : e;")
    def Stmts_2(self, nt, e):
        return Node('Stmts')

    @BaseParser.production("Stmt : PRINT Expr;")
    def PrintStmt(self, nt, prin, expr):
        return Node('Print').addkid(expr)

    @BaseParser.production("Expr : AddSub;")
    def Expr(self, nt, expr):
        return Node('Expr').addkid(expr)

    @BaseParser.productions('''
    MulDiv' : e;
    AddSub' : e;''')
    def Pass(self, nt, *prod): pass

    @BaseParser.productions('''
    MulDiv : Atomic MulDiv';
    AddSub : MulDiv AddSub';''')
    def OpCollapse(self, nt, b, extra):
        if extra is not None:
            b = Node(extra[0]).addkid(b).addkid(extra[1])
            #print
            #print b
            if len(extra) == 3:
                #print ' '*4, extra[2]
                ret = self.OpCollapse(None, b, extra[2])
                #print
                #print ret
                return ret
        return b

    @BaseParser.productions('''
    AddSub' : PLUS MulDiv AddSub';
    AddSub' : DASH MulDiv AddSub';
    MulDiv' : STAR Atomic MulDiv';
    MulDiv' : SLASH Atomic MulDiv';''')
    def Op(self, nt, op, b, extra):
        if extra is not None:
            if len(extra) == 2:
                return op.value, b, (extra[0], extra[1])
            return op.value, b, (extra[0], extra[1], extra[2])
        return op.value, b

    @BaseParser.production('Atomic : Value')
    def Atomic1(self, nt, val):
        return val


    @BaseParser.production('Atomic : LPAREN Expr RPAREN')
    def Atomic2(self, nt, lparen, expr, rparen):
        return expr

    @BaseParser.production('Value : INT_VAL')
    def Value1(self, nt, val):
        return Node('INT').addkid(val.value)

    @BaseParser.production('Value : NameOrCall')
    def Value2(self, nt, val):
        print nt, val
        return val


if __name__ == '__main__':
    import il, il_gen
    parser = Parser(Lex, debug=False)
    ast = parser.parse('''
        print 1
        print 2
        print 3+3*5+5
    ''')

    print
    print ast

    il.run(*il_gen.generate(ast))