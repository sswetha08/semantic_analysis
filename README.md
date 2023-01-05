## Semantic Analysis - Gee language

The purpose of this project is to implement a dynamically typed version of a subset of Gee language and output a 'state'.
The state will include all the variables and their values in the program.

This is evaluated by the compiler using two passes - In the first pass, the program is parsed and an Abstract Syntax Tree is created. This is implemented as a Recursive Descent Parser (Top-Down).

In the second pass, the 'state' (modeled by a dictionary) is constructed. This is achieved by implementing a 'meaning' function each for the following Abstract Syntax statements:
* Assign.
* IfStmt (if-then-else)
* WhileStmt.
* Block.
* StmtList
