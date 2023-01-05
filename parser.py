import re, sys, string

debug = False
dict = { }
tokens = [ ]

def error( msg ):
	#print msg
	sys.exit(msg)

#  Expression class and its subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)
	
	def value(self, state):
		left = self.left.value(state)
		right = self.right.value(state)

		if self.op == "+":
			return left + right
		if self.op == "-":
			return left - right
		if self.op == "*":
			return left * right
		if self.op == "/":
			return left - right

	def tipe(self, typeMap):
		left = self.left.tipe(typeMap)
		right = self.right.tipe(typeMap)
		if left != right:
			printType(typeMap)
			error("Type Error: " + str(left) + str(right))
		return left

class RelationalExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)
	
	def value(self, state):
		left = self.left.value(state)
		right = self.right.value(state)

		if self.op == ">":
			return left > right
		if self.op == ">=":
			return left >= right
		if self.op == "<":
			return left < right
		if self.op == "<=":
			return left <= right
		if self.op == "!=":
			return left != right
		if self.op == "==":
			return left == right
	
	def tipe(self, typeMap):
		left = self.left.tipe(typeMap)
		right = self.right.tipe(typeMap)
		if left != right:
			error("Type mismatch")
		return "boolean"


class AndExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)
	
	def value(self, state):
		left = self.left.value(state)
		right = self.right.value(state)
		return left and right

	def tipe(self, typeMap):
		left = self.left.tipe(typeMap)
		right = self.right.tipe(typeMap)
		if left != right:
			error("Type mismatch")
		return left

class Assign( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right) + "\n"

	def meaning(self, state, typeMap):
		# check type
		if self.left.name in typeMap:
			if self.right.tipe(typeMap) != typeMap[self.left.name]:
				printType(typeMap)
				error("Type Error")
		else:
			typeMap[self.left.name] = self.right.tipe(typeMap)
		# check value
		state[self.left.name] = self.right.value(state)
		
		return state, typeMap
		
class Number( Expression ):
	def __init__(self, val):
		self.val = val
		
	def __str__(self):
		return str(self.val)
	
	def value(self, state):
		return int(self.val)

	def tipe(self, state):
		return "number"

class Identifier( Expression ):
	def __init__(self, name):
		self.name = name 
		
	def __str__(self):
		return str(self.name)
	
	def value(self, state):
		if self.name in state:
			return state[self.name]
		else:
			error(str(self.name) +" is referenced before being defined!")
	
	def tipe(self, typeMap):
		if self.name in typeMap:
			return typeMap[self.name]
		else:
			printType(typeMap)
			error(str(self.name) +" is referenced before being defined!")

class Block():
	def __init__(self, stmtList):
		self.stmtList = stmtList
		
	def __str__(self):
		return "\n" + str(self.stmtList)

	def meaning(self, state, typeMap):
		state, typeMap = self.stmtList.meaning(state, typeMap)
		return state,typeMap
	

class IfStatement( Expression ):
	def __init__(self, expr, block, elseblk = None):
		self.expr = expr
		self.block = block
		self.elseblk = elseblk
		
	def __str__(self):
		if self.elseblk == None:
			return "if " + str(self.expr) + str(self.block)  + "endif" + "\n"
		else:
			return "if " + str(self.expr) + str(self.block) + "else" + str(self.elseblk) + "endif" + "\n" 

	def meaning(self, state, typeMap):
		self.expr.tipe(typeMap)
		if self.expr.value(state):
			state, typeMap = self.block.meaning(state, typeMap)
		elif self.elseblk:
			state, typeMap = self.elseblk.meaning(state, typeMap)
		return state, typeMap
			
class WhileStatement( Expression ):
	def __init__(self, expr, block):
		self.expr = expr
		self.block = block
		
	def __str__(self):
		return "while " + str(self.expr) + str(self.block) + "endwhile" + "\n"

	def meaning(self, state, typeMap):
		self.expr.tipe(typeMap)
		while self.expr.value(state):
			state, typeMap = self.block.meaning(state, typeMap)
		return state, typeMap
			

class StatementList( Expression ):
	def __init__(self, statements):
		self.statements = statements
		
	def __str__(self):
		res = ""
		for st in self.statements:
			res += str(st)
		return res
	
	def meaning(self, state, typeMap):
		for st in self.statements:
			state, typeMap = st.meaning(state, typeMap)
		return state, typeMap


# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.

def match(matchtok):
	tok = tokens.peek( )
	if (tok != matchtok): error("Expecting "+ matchtok)
	tokens.next( )
	return tok
	
def factor( ):
	# factor = number | string | ident |  "(" expression ")" 

	tok = tokens.peek( )
	if debug: print ("Factor: ", tok)
	if re.match(Lexer. number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr
	if re.match(Lexer.string, tok):
		expt = str(tok)
		tokens.next( )
		return expr
	if re.match(Lexer.identifier, tok):
		#expr = str(tok)
		expr = Identifier(tok)
		tokens.next( )
		return expr	
	if tok == "(":
		tokens.next( )  # or match( tok )
		expr = expression( )
		tokens.peek( )
		tok = match(")")
		return expr
	error("Invalid operand")
	return


def term( ):
	""" term    = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def addExpr( ):
	""" addExpr    = term { ('+' | '-') term } """

	tok = tokens.peek( )
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def relationalExpr():
	# addExpr [ relation addExpr ]
	left = addExpr()
	tok = tokens.peek()
	if re.match(Lexer.relational, tok):
		tokens.next( )  # or match( tok )
		right = addExpr()
		left = RelationalExpr(tok, left, right)		
	return left
	
def andExpr():
	# andExpr    = relationalExpr { "and" relationalExpr }
	left = relationalExpr()
	tok = tokens.peek()
	while tok == "and":
		tokens.next()
		right = relationalExpr()
		left = AndExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def expression():
	# expression = andExpr { "or" andExpr }
	left = andExpr()
	tok = tokens.peek()
	while tok == "or":
		tokens.next()
		right = andExpr()
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def block():
	# block = ":" eoln indent stmtList undent
	tok = tokens.peek()
	if tok == ':':
		tokens.next()
		tok = tokens.peek()
		if tok == ';':
			tokens.next()
			tok = tokens.peek()
			if tok == '@':
				tokens.next()
				astS = parseStmtList()
				tok = tokens.peek()
				if tok == '~':
					tokens.next()
					return Block(astS)
	error("no match if")

def ifStmt():
	""" ifStatement = "if" expression block   [ "else" block ] """
	tokens.next()
	tok = tokens.peek( )
	expr = expression()
	blkIf = block()
	tok = tokens.peek()
	if tok == "else":
		tokens.next( )  # or match( tok )
		blkElse = block()
		return IfStatement(expr, blkIf, blkElse)
	return IfStatement(expr, blkIf)

def whileStmt():
	# whileStatement = "while"  expression  block
	tokens.next()
	expr = expression()
	blk = block()
	return WhileStatement(expr,blk)

def assign():
	# assign = ident "=" expression  eoln
	ident = Identifier(tokens.peek())
	tokens.next()
	tok = tokens.peek( )
	if tok == "=":
		tokens.next()
		expr = expression()
		tok = tokens.peek()
		if tok == ";":
			tokens.next()
			return Assign("=", ident, expr)
		else:
			error("match expected ;")
	

def parseStmt():
	# statement = ifStatement |  whileStatement  |  assign
	tok = tokens.peek( )
	if tok == "if":
		expr = ifStmt()
		return expr
	elif tok == "while":
		expr = whileStmt()
		return expr
	if re.match(Lexer.identifier, tok):
		expr = assign()
		return expr
	else:
		error("error condition stmt")

def parseStmtList(  ):
	""" gee = { Statement } """
	tok = tokens.peek( )
	statementList = []
	while tok is not None and tok != '~':
		ast = parseStmt()
		statementList.append(ast)
		tok = tokens.peek()
	return StatementList(statementList)

def parse(text) :
	global tokens
	tokens = Lexer(text)
	stmtlist = parseStmtList() 
	print (str(stmtlist))
	# now traverse stmtList
	semanticAnalysis(stmtlist)
	return

def semanticAnalysis(stmtlist):
	state = {}
	typeMap = {}
	state, typeMap = stmtlist.meaning(state, typeMap)
	printState(state)
	printType(typeMap)
	return

def printState(state):
	eleList = []
	for ele, val in state.items():
		eleList.append("<" + str(ele) + "," + str(val) + ">")
	concat = ', '.join(eleList)
	print("{" + concat + "}")

def printType(typeMap):
	for ele, type in typeMap.items():
		print(ele + " " + type)

# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	
	
	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct
		

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line

def mklines(filename):
	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	for line in inn:
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
		elif indent < pos[-1]:
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		print (ct, "\t", line)
		lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	# print undent
	return lines



def main():
	"""main program for testing"""
	global debug
	ct = 0
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
	if len(sys.argv) < 2+ct:
		print ("Usage:  %s filename" % sys.argv[0])
		return
	parse("".join(mklines(sys.argv[1+ct])))
	return


main()
