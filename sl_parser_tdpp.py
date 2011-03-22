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
    Start       : Stmts;

    Stmts       : Stmt Stmts';
    Stmts'      : Stmt Stmts';
    Stmts'      : e;

    Stmt        : PRINT Expr;
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

    Expr        : AddSub;

    AddSub      : MulDiv AddSub';
    AddSub'     : PLUS MulDiv AddSub';
    AddSub'     : DASH MulDiv AddSub';
    AddSub'     : e;


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
    ''')
    def FullGrammar(self, nt, *production):
        print nt, production


    @BaseParser.productions('''
        MulDiv' : e;''')
    def Pass(self, nt, *prod):
        print nt, prod

    @BaseParser.production("MulDiv : Atomic MulDiv'")
    def MulDiv(self, nt, b, extra):
        print nt, b, extra

    @BaseParser.productions('''
    MulDiv' : STAR Atomic MulDiv';
    MulDiv' : SLASH Atomic MulDiv';''')
    def MulDiv_(self, nt, op, b, extra):
        print nt, op, b, extra

    @BaseParser.production('Atomic : Value')
    def Atomic1(self, nt, val):
        print nt, val
        return val


    @BaseParser.production('Atomic : LPAREN Expr RPAREN')
    def Atomic2(self, nt, lparen, expr, rparen):
        print nt, expr
        return expr

    @BaseParser.production('Value : INT_VAL')
    def Value1(self, nt, val):
        print nt, val.value
        return val.value

    @BaseParser.production('Value : NameOrCall')
    def Value2(self, nt, val):
        print nt, val
        return val


if __name__ == '__main__':

    parser = Parser(Lex, debug=True)
    parser.parse('''
        print 2
    ''')