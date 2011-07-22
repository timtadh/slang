Lexical and Syntax Analysis
===========================

Lexically and syntactically analyzes the language of Slang and produces an abstract syntax tree
[AST].

---

Lexical analysis is the process of breaking up the raw text of the input program in to `tokens` and
`attributes`. This is implemented in `sl_lexer` using the `PLY` lexing and parsing library. A token
is a lexical attribute of the language (think noun or verb). Something that can be identified by a
"word" in the language without any context. For instance the "+" operator is always a "+". An
attribute is attached to a token. It provides a additional contextual information. For instance
all numbers are given the same token, INT_VAL, in order to discern which the value of the number one
must examine the attached attribute.

Syntactic analysis works on the stream of (token, attribute) pairs. In slang it produces an
abstract syntax tree of the input program. To view an example abstract syntax tree please see the
top level examples directory. The parser is implemented in `sl_parser` and once again makes use of
`PLY`.
