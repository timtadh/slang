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

    @BaseParser.production(" Start : Stmts;")
    def Start(self, nt, stmts):
        return stmts

    @BaseParser.production("Stmts : Stmt Stmts';")
    @BaseParser.production("Stmts' : Stmt Stmts';")
    def Stmts(self, nt, stmt, stmts):
        return stmts.addkid(stmt, before=True)

    @BaseParser.production("Stmts' : e;")
    def Stmts_2(self, nt, e):
        return Node('Stmts')

    @BaseParser.production("Stmt : PRINT Expr;")
    def Stmt1(self, nt, prin, expr):
        return Node('Print').addkid(expr)

    @BaseParser.production("Stmt : NameStmt;")
    def Stmt2(self, nt, stmt):
        return stmt

    @BaseParser.production("NameStmt : NAME NameStmt';")
    def NameStmt(self, nt, name, stmt):
        name = name.value
        stmt.addkid(name, before=True)
        #print 'NAME STATEMENT', nt, name, stmt
        return stmt

    @BaseParser.production("NameStmt'   : Call';")
    def NameStmt_1(self, nt, call):
        #print nt, call
        return call

    @BaseParser.production("NameStmt'   : AssignStmt;")
    def NameStmt_2(self, nt, assign):
        #print nt, assign
        return Node('Assign').addkid(assign)

    @BaseParser.production("AssignStmt  : EQUAL Assignable;")
    def AssignStmt(self, nt, equal, assignable):
        return assignable

    @BaseParser.production("Assignable  : Expr;")
    @BaseParser.production("Assignable  : Function;")
    def Assignable1(self, nt, expr):
        return expr


    @BaseParser.production("Function    : FUNC LPAREN ParamDecl LCURLY FuncBody RCURLY;")
    def Function(self, nt, func, lparen, dparams, lcurly, body, rcurly):
        n = Node('Func')
        stmts, ret = body
        if dparams: n.addkid(dparams)
        if stmts: n.addkid(stmts)
        n.addkid(ret)
        #print 'function', n
        return n

    @BaseParser.production("ParamDecl   : RPAREN;")
    def ParamDecl1(self, nt, rparen):
        pass
    @BaseParser.production("ParamDecl   : DParams RPAREN;")
    def ParamDecl2(self, nt, dparams, rparen):
        return dparams
    @BaseParser.production("FuncBody    : Return;")
    def FuncBody1(self, nt, ret):
        return None, ret
    @BaseParser.production("FuncBody    : Stmts Return;")
    def FuncBody2(self, nt, stmts, ret):
        return stmts, ret


    @BaseParser.production("Return : RETURN RetExpr;")
    def Return(self, nt, ret, expr):
        return expr
    @BaseParser.production("RetExpr : Expr;")
    def RetExpr_1(self, nt, expr):
        return Node('Return').addkid(expr)
    @BaseParser.production("RetExpr     : e;")
    def RetExpr_2(self, nt, e):
        return Node('Return')


    @BaseParser.production("Call'       : LPAREN Call'';")
    def Call_(self, nt, lparen, call):
        return call
    @BaseParser.production("Call''      : RPAREN;")
    def Call__1(self, nt, rparen):
        return Node('Call')
    @BaseParser.production("Call''      : Params RPAREN;")
    def Call__2(self, nt, params, rparen):
        return Node('Call').addkid(params)


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
        #print nt, val
        return val

    @BaseParser.production("NameOrCall : NAME NameOrCall';")
    def NameOrCall(self, nt, name, val):
        if val is None: return Node('NAME').addkid(name.value)
        return val.addkid(name.value, before=True)

    @BaseParser.production("NameOrCall' : Call'")
    def NameOrCall_1(self, nt, call):
        return call

    @BaseParser.production("NameOrCall' : e")
    def NameOrCall_2(self, nt, e): pass

    @BaseParser.production("Params : Expr Params';")
    def Params(self, nt, expr, params):
        return params.addkid(expr, before=True)

    @BaseParser.production("Params' : COMMA Expr Params';")
    def Params_1(self, nt, comma, expr, params):
        return params.addkid(expr, before=True)

    @BaseParser.production("Params' : e;")
    def Params_2(self, nt, e):
        return Node('Params')

    @BaseParser.production("DParams : NAME DParams';")
    def DParams(self, nt, name, dparams):
        return dparams.addkid(name.value, before=True)

    @BaseParser.production("DParams' : COMMA NAME DParams';")
    def DParams_1(self, nt, comma, name, dparams):
        return dparams.addkid(name.value, before=True)

    @BaseParser.production("DParams' : e;")
    def DParams_2(self, nt, e):
        return Node('DParams')


if __name__ == '__main__':
    import il, il_gen
    parser = Parser(Lex, debug=False)
    ast = parser.parse('''
        f = func(a, b) { return a + b }
        print f(5, 10)
    ''')

    print
    print ast

    il.run(*il_gen.generate(ast))