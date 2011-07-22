Control Flow Analyzer
=====================

This package does control flow analysis on the output of the intermediate code generator (found in
the `il` package).

The purpose of the control flow analysis is to build a representation on which to efficiently
compute dataflow analysis. There are several types of control flow representation which might be
computed in a compiler, Slang uses `structural` analysis. Structural analysis identifies functional
groups of basic blocks, eg. if-then groups, it-then-else groups, while groups, etc... It then builds
a `control flow tree` from the analysis. An example of such a tree can be found in the top level
examples directory.

Ullman et all. in the "Dragon Book" give an algorithm for spliting intermediate code into basic
blocks and building a control flow graph. Slang skips this step. The intermediate code generator
generates the control flow graph of basic blocks directly. Therefore, the analysis of the control
flow is in some sense split between the il code generator and this analysis package.
