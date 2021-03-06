#!/usr/bin/python
#-*- coding: utf-8 -*-

# Parser module generated by unicc from logics.par.
# DO NOT EDIT THIS FILE MANUALLY, IT WILL GO AWAY!


class Node(object):
	"""
	This is an AST node.
	"""

	def __init__(self, emit = None, match = None, children = None):
		self.emit = emit
		self.match = match
		self.children = children or []

	def dump(self, level=0):
		if self.emit:
			txt = "%s%s" % (level * " ", self.emit)
			if self.match and self.match != self.emit:
				txt += " (%s)" % self.match

			print(txt)
			level += 1

		for child in self.children:
			child.dump(level)


class ParseException(Exception):
	"""
	Exception to be raised on a parse error.
	"""

	def __init__(self, row, col, txt = None):
		if isinstance(txt, list):
			expecting = txt
			txt = ("Line %d, column %d: Parse error, expecting %s" %
					(row, col, ", ".join([("%r" % symbol[0])
						for symbol in txt])))
		else:
			expecting = None

		super(ParseException, self).__init__(txt)

		self.row = row
		self.col = col
		self.expecting = expecting


class ParserToken(object):
	state = 0
	line = 0
	column = 0

	node = None

	value = None


class ParserControlBlock(object):

	# Stack
	stack = None
	tos = None

	# Values
	ret = None

	# State
	act = None
	idx = None
	lhs = None

	# Lookahead
	sym = -1
	old_sym = -1
	len = 0

	# Lexical analysis
	lexem = None
	next = None
	eof = None
	is_eof = None

	# Input buffering
	input = None
	buf = ""

	# Error handling
	error_delay = 3
	error_count = 0

	line = 1
	column = 1

	


class Parser(object):

	# Actions
	_ERROR = 0
	_REDUCE = 1
	_SHIFT = 2

	# Parse tables
	_symbols = (
		("&eof", "", 3, 0, 0, 1),
		("False", "False", 2, 0, 0, 1),
		("True", "True", 2, 0, 0, 1),
		("**", "**", 2, 0, 0, 1),
		("!=", "!=", 2, 0, 0, 1),
		("<>", "<>", 2, 0, 0, 1),
		(">", ">", 2, 0, 0, 1),
		("<", "<", 2, 0, 0, 1),
		("<=", "<=", 2, 0, 0, 1),
		(">=", ">=", 2, 0, 0, 1),
		("==", "==", 2, 0, 0, 1),
		("IN", "", 2, 0, 0, 1),
		("NOT", "", 2, 0, 0, 1),
		("AND", "", 2, 0, 0, 1),
		("OR", "", 2, 0, 0, 1),
		("ELSE", "", 2, 0, 0, 1),
		("IF", "", 2, 0, 0, 1),
		("FOR", "", 2, 0, 0, 1),
		("NUMBER", "NUMBER", 2, 0, 0, 1),
		("STRING", "STRING", 2, 0, 0, 0),
		("IDENT", "IDENT", 2, 0, 0, 1),
		("whitespace", "", 2, 0, 1, 1),
		(",", "", 1, 0, 0, 1),
		(".", "", 1, 0, 0, 1),
		("]", "", 1, 0, 0, 1),
		("[", "", 1, 0, 0, 1),
		(")", "", 1, 0, 0, 1),
		("(", "", 1, 0, 0, 1),
		("~", "", 1, 0, 0, 1),
		("%", "", 1, 0, 0, 1),
		("/", "", 1, 0, 0, 1),
		("*", "", 1, 0, 0, 1),
		("-", "", 1, 0, 0, 1),
		("+", "", 1, 0, 0, 1),
		("&embedded_7*", "", 0, 0, 0, 1),
		("&embedded_7+", "", 0, 0, 0, 1),
		("&embedded_7", "", 0, 0, 0, 1),
		("&embedded_6?", "", 0, 0, 0, 1),
		("&embedded_6", "", 0, 0, 0, 1),
		("comprehension", "", 0, 0, 0, 1),
		("STRING+", "", 0, 0, 0, 1),
		("&embedded_5", "", 0, 0, 0, 1),
		("list", "", 0, 0, 0, 1),
		("trailer+", "", 0, 0, 0, 1),
		("trailer", "", 0, 0, 0, 1),
		("atom", "", 0, 0, 0, 1),
		("entity", "", 0, 0, 0, 1),
		("power", "", 0, 0, 0, 1),
		("&embedded_4", "", 0, 0, 0, 1),
		("factor", "", 0, 0, 0, 1),
		("term", "", 0, 0, 0, 1),
		("&embedded_3+", "", 0, 0, 0, 1),
		("&embedded_3", "", 0, 0, 0, 1),
		("&embedded_2", "", 0, 0, 0, 1),
		("expr", "", 0, 0, 0, 1),
		("not_in", "", 0, 0, 0, 1),
		("in", "", 0, 0, 0, 1),
		("comparison", "", 0, 0, 0, 1),
		("&embedded_1+", "", 0, 0, 0, 1),
		("&embedded_1", "", 0, 0, 0, 1),
		("not_test", "", 0, 0, 0, 1),
		("&embedded_0+", "", 0, 0, 0, 1),
		("&embedded_0", "", 0, 0, 0, 1),
		("and_test", "", 0, 0, 0, 1),
		("or_test", "", 0, 0, 0, 1),
		("if_else", "", 0, 0, 0, 1),
		("test", "", 0, 0, 0, 1),
		("expression", "", 0, 0, 0, 1),
		("logic", "", 0, 0, 0, 1)
	)
	_productions = (
		("logic -> expression ~&eof", "", 2, 68),
		("expression -> test", "", 1, 67),
		("test -> if_else", "", 1, 66),
		("test -> or_test", "", 1, 66),
		("if_else -> or_test @IF or_test @ELSE test", "if_else", 5, 65),
		("or_test -> and_test &embedded_0+", "or_test", 2, 64),
		("&embedded_0 -> @OR and_test", "", 2, 62),
		("&embedded_0+ -> &embedded_0+ &embedded_0", "", 2, 61),
		("&embedded_0+ -> &embedded_0", "", 1, 61),
		("or_test -> and_test", "", 1, 64),
		("and_test -> not_test &embedded_1+", "and_test", 2, 63),
		("&embedded_1 -> @AND not_test", "", 2, 59),
		("&embedded_1+ -> &embedded_1+ &embedded_1", "", 2, 58),
		("&embedded_1+ -> &embedded_1", "", 1, 58),
		("and_test -> not_test", "", 1, 63),
		("not_test -> @NOT not_test", "not_test", 2, 60),
		("not_test -> comparison", "", 1, 60),
		("in -> @IN", "in", 1, 56),
		("not_in -> @NOT @IN", "not_in", 2, 55),
		("comparison -> expr &embedded_3+", "comparison", 2, 57),
		("&embedded_2 -> \"==\"", "", 1, 53),
		("&embedded_2 -> \">=\"", "", 1, 53),
		("&embedded_2 -> \"<=\"", "", 1, 53),
		("&embedded_2 -> \"<\"", "", 1, 53),
		("&embedded_2 -> \">\"", "", 1, 53),
		("&embedded_2 -> \"<>\"", "", 1, 53),
		("&embedded_2 -> \"!=\"", "", 1, 53),
		("&embedded_2 -> in", "", 1, 53),
		("&embedded_2 -> not_in", "", 1, 53),
		("&embedded_3 -> &embedded_2 expr", "", 2, 52),
		("&embedded_3+ -> &embedded_3+ &embedded_3", "", 2, 51),
		("&embedded_3+ -> &embedded_3", "", 1, 51),
		("comparison -> expr", "", 1, 57),
		("expr -> expr '+' term", "add", 3, 54),
		("expr -> expr '-' term", "sub", 3, 54),
		("expr -> term", "", 1, 54),
		("term -> term '*' factor", "mul", 3, 50),
		("term -> term '/' factor", "div", 3, 50),
		("term -> term '%' factor", "mod", 3, 50),
		("term -> factor", "", 1, 50),
		("&embedded_4 -> '+'", "", 1, 48),
		("&embedded_4 -> '-'", "", 1, 48),
		("&embedded_4 -> '~'", "", 1, 48),
		("factor -> &embedded_4 factor", "factor", 2, 49),
		("factor -> power", "", 1, 49),
		("power -> entity \"**\" factor", "power", 3, 47),
		("power -> entity", "", 1, 47),
		("entity -> atom trailer+", "entity", 2, 46),
		("trailer+ -> trailer+ trailer", "", 2, 43),
		("trailer+ -> trailer", "", 1, 43),
		("entity -> atom", "", 1, 46),
		("trailer -> '(' list ')'", "", 3, 44),
		("trailer -> '[' expression ']'", "", 3, 44),
		("trailer -> '.' @IDENT", "", 2, 44),
		("&embedded_5 -> \"True\"", "", 1, 41),
		("&embedded_5 -> \"False\"", "", 1, 41),
		("atom -> &embedded_5", "", 1, 45),
		("atom -> @NUMBER", "", 1, 45),
		("atom -> @IDENT", "", 1, 45),
		("STRING+ -> STRING+ @STRING", "", 2, 40),
		("STRING+ -> @STRING", "", 1, 40),
		("atom -> STRING+", "strings", 1, 45),
		("atom -> comprehension", "", 1, 45),
		("atom -> '[' list ']'", "", 3, 45),
		("atom -> '(' expression ')'", "atom", 3, 45),
		("comprehension -> '[' expression @FOR @IDENT @IN or_test &embedded_6? ']'", "comprehension", 8, 39),
		("&embedded_6 -> @IF expression", "", 2, 38),
		("&embedded_6? -> &embedded_6", "", 1, 37),
		("&embedded_6? -> ", "", 0, 37),
		("list -> expression &embedded_7*", "list", 2, 42),
		("&embedded_7 -> ',' expression", "", 2, 36),
		("&embedded_7+ -> &embedded_7+ &embedded_7", "", 2, 35),
		("&embedded_7+ -> &embedded_7", "", 1, 35),
		("&embedded_7* -> &embedded_7+", "", 1, 34),
		("&embedded_7* -> ", "", 0, 34),
		("list -> ", "list", 0, 42)
	)
	_act = (
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((0, 3, 0), ),
		((16, 2, 14), ),
		((14, 2, 15), ),
		((13, 2, 17), ),
		((12, 2, 19), (11, 3, 17), (10, 3, 20), (9, 3, 21), (8, 3, 22), (7, 3, 23), (6, 3, 24), (5, 3, 25), (4, 3, 26), (33, 2, 22), (32, 2, 23), ),
		((31, 2, 24), (30, 2, 25), (29, 2, 26), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((3, 2, 27), ),
		((27, 2, 29), (25, 2, 30), (23, 2, 31), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((19, 3, 59), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((14, 2, 15), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((13, 2, 17), ),
		((11, 3, 18), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((12, 2, 19), (11, 3, 17), (10, 3, 20), (9, 3, 21), (8, 3, 22), (7, 3, 23), (6, 3, 24), (5, 3, 25), (4, 3, 26), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((27, 2, 29), (25, 2, 30), (23, 2, 31), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((20, 3, 53), ),
		((26, 3, 64), ),
		((17, 2, 42), (22, 2, 43), ),
		((24, 3, 63), ),
		((15, 2, 45), ),
		((33, 2, 22), (32, 2, 23), ),
		((31, 2, 24), (30, 2, 25), (29, 2, 26), ),
		((31, 2, 24), (30, 2, 25), (29, 2, 26), ),
		((22, 2, 43), ),
		((26, 3, 51), ),
		((24, 3, 52), ),
		((20, 2, 46), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((22, 2, 43), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((11, 2, 47), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((16, 2, 49), ),
		((20, 3, 58), (19, 3, 60), (18, 3, 57), (12, 2, 1), (33, 3, 40), (32, 3, 41), (28, 3, 42), (27, 2, 11), (25, 2, 12), (2, 3, 54), (1, 3, 55), ),
		((24, 3, 65), )
	)
	_go = (
		((67, 2, 2), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((60, 3, 15), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		(),
		(),
		((62, 3, 8), (61, 2, 16), ),
		((59, 3, 13), (58, 2, 18), ),
		((56, 3, 27), (55, 3, 28), (53, 2, 20), (52, 3, 31), (51, 2, 21), ),
		(),
		((49, 3, 43), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		(),
		((44, 3, 49), (43, 2, 28), ),
		((67, 2, 32), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((67, 2, 33), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (42, 2, 34), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		(),
		((64, 2, 35), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((63, 3, 6), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((62, 3, 7), ),
		((60, 3, 11), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((59, 3, 12), ),
		(),
		((54, 2, 36), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((56, 3, 27), (55, 3, 28), (53, 2, 20), (52, 3, 30), ),
		((50, 2, 37), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((50, 2, 38), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((49, 3, 36), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((49, 3, 37), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((49, 3, 38), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((49, 3, 45), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((44, 3, 48), ),
		((67, 2, 39), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (42, 2, 40), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((67, 2, 41), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		(),
		(),
		((36, 3, 72), (35, 2, 44), (34, 3, 69), ),
		(),
		(),
		(),
		(),
		(),
		((36, 3, 72), (35, 2, 44), (34, 3, 69), ),
		(),
		(),
		(),
		((67, 3, 70), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((36, 3, 71), ),
		((66, 3, 4), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		(),
		((64, 2, 48), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		((38, 3, 67), (37, 2, 50), ),
		((67, 3, 66), (66, 3, 1), (65, 3, 2), (64, 2, 3), (63, 2, 4), (60, 2, 5), (57, 3, 16), (54, 2, 6), (50, 2, 7), (49, 3, 39), (48, 2, 8), (47, 3, 44), (46, 2, 9), (45, 2, 10), (41, 3, 56), (40, 2, 13), (39, 3, 62), ),
		()
	)

	_def_prod = (-1, -1, -1, 3, 9, 14, 32, 35, -1, 46, 50, -1, 75, 61, -1, -1, 5, -1, 10, -1, -1, 19, -1, -1, -1, -1, -1, -1, 47, 75, -1, -1, -1, 74, -1, -1, 29, 33, 34, 74, -1, -1, -1, -1, 73, -1, -1, -1, 68, -1, -1)

	# Lexical analysis
	_dfa_select = ()
	_dfa_index = (
		(0, 40, 41, 42, 43, 45, 46, 47, 48, 50, 51, 54, 57, 59, 65, 66, 67, 68, 72, 73, 74, 75, 76, 77, 78, 79, 84, 89, 94, 99, 104, 109, 114, 119, 124, 126, 128, 135, 136, 142, 148, 155, 161, 165, 172, 178, 185, 187, 196, 202, 209, 215, 222, 227, 234, 241, 248, 255, 262, 269, 276, 283, 290),
	)
	_dfa_chars = ((33, 33), (34, 34), (35, 35), (37, 37), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 57), (60, 60), (61, 61), (62, 62), (70, 70), (84, 84), (91, 91), (93, 93), (97, 97), (101, 101), (102, 102), (105, 105), (110, 110), (111, 111), (126, 126), (9, 10), (13, 13), (32, 32), (65, 69), (71, 83), (85, 90), (95, 95), (98, 100), (103, 104), (106, 109), (112, 122), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (42, 42), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (48, 57), (-1, -1), (-1, -1), (46, 46), (48, 57), (-1, -1), (61, 61), (62, 62), (-1, -1), (61, 61), (-1, -1), (97, 97), (48, 57), (65, 90), (95, 95), (98, 122), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (9, 10), (13, 13), (32, 32), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (61, 61), (-1, -1), (48, 57), (-1, -1), (114, 114), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (-1, -1), (-1, -1), (34, 34), (92, 92), (0, 33), (35, 91), (93, 65535), (-1, -1), (34, 34), (92, 92), (0, 33), (35, 91), (93, 65535), (-1, -1), (110, 110), (48, 57), (65, 90), (95, 95), (97, 109), (111, 122), (-1, -1), (39, 39), (92, 92), (0, 38), (40, 91), (93, 65535), (-1, -1), (10, 10), (0, 9), (11, 65535), (-1, -1), (108, 108), (48, 57), (65, 90), (95, 95), (97, 107), (109, 122), (-1, -1), (39, 39), (92, 92), (0, 38), (40, 91), (93, 65535), (-1, -1), (111, 111), (48, 57), (65, 90), (95, 95), (97, 110), (112, 122), (-1, -1), (61, 61), (-1, -1), (102, 102), (110, 110), (48, 57), (65, 90), (95, 95), (97, 101), (103, 109), (111, 122), (-1, -1), (34, 34), (92, 92), (0, 33), (35, 91), (93, 65535), (-1, -1), (111, 111), (48, 57), (65, 90), (95, 95), (97, 110), (112, 122), (-1, -1), (39, 39), (92, 92), (0, 38), (40, 91), (93, 65535), (-1, -1), (114, 114), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (-1, -1), (48, 57), (65, 90), (95, 95), (97, 122), (-1, -1), (117, 117), (48, 57), (65, 90), (95, 95), (97, 116), (118, 122), (-1, -1), (100, 100), (48, 57), (65, 90), (95, 95), (97, 99), (101, 122), (-1, -1), (115, 115), (48, 57), (65, 90), (95, 95), (97, 114), (116, 122), (-1, -1), (116, 116), (48, 57), (65, 90), (95, 95), (97, 115), (117, 122), (-1, -1), (101, 101), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (-1, -1), (101, 101), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (-1, -1), (101, 101), (48, 57), (65, 90), (95, 95), (97, 100), (102, 122), (-1, -1), (114, 114), (48, 57), (65, 90), (95, 95), (97, 113), (115, 122), (-1, -1), (115, 115), (48, 57), (65, 90), (95, 95), (97, 114), (116, 122), (-1, -1), (108, 108), (48, 57), (65, 90), (95, 95), (97, 107), (109, 122), (-1, -1))
	_dfa_trans = (34, 39, 42, 1, 44, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 46, 12, 13, 36, 14, 15, 40, 43, 45, 47, 49, 51, 16, 17, 17, 17, 52, 52, 52, 52, 52, 52, 52, 52, -1, -1, -1, -1, 20, -1, -1, -1, -1, 35, -1, -1, 35, 10, -1, 21, 22, -1, 24, -1, 62, 52, 52, 52, 52, -1, -1, -1, -1, 17, 17, 17, -1, -1, -1, -1, -1, -1, -1, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 18, -1, 35, -1, 53, 52, 52, 52, 52, 52, -1, -1, 19, 48, 39, 39, 39, -1, 19, 48, 39, 39, 39, -1, 54, 52, 52, 52, 52, 52, -1, 19, 50, 44, 44, 44, -1, 37, 42, 42, -1, 55, 52, 52, 52, 52, 52, -1, 19, 50, 44, 44, 44, -1, 60, 52, 52, 52, 52, 52, -1, 23, -1, 25, 26, 52, 52, 52, 52, 52, 52, -1, 38, 48, 39, 39, 39, -1, 56, 52, 52, 52, 52, 52, -1, 41, 50, 44, 44, 44, -1, 27, 52, 52, 52, 52, 52, -1, 52, 52, 52, 52, -1, 57, 52, 52, 52, 52, 52, -1, 28, 52, 52, 52, 52, 52, -1, 58, 52, 52, 52, 52, 52, -1, 30, 52, 52, 52, 52, 52, -1, 31, 52, 52, 52, 52, 52, -1, 32, 52, 52, 52, 52, 52, -1, 33, 52, 52, 52, 52, 52, -1, 29, 52, 52, 52, 52, 52, -1, 59, 52, 52, 52, 52, 52, -1, 61, 52, 52, 52, 52, 52, -1)
	_dfa_accept = (
		(0, 30, 28, 27, 32, 34, 23, 33, 24, 31, 19, 8, 7, 21, 26, 25, 29, 22, 5, 20, 4, 9, 6, 11, 10, 17, 12, 15, 14, 18, 13, 3, 16, 2, 0, 19, 21, 22, 20, 0, 21, 20, 0, 21, 0, 21, 0, 21, 0, 21, 0, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21),
	)

	# Parsing actions



	# Parsing algorithm

	def _get_act(self, pcb):
		# Get action table entry

		# Check action table first
		for (sym, pcb.act, pcb.idx) in self._act[pcb.tos.state]:
			if sym == pcb.sym:
				return True if pcb.act else False #enforced parse error

		# Otherwise, apply default production
		pcb.idx = self._def_prod[pcb.tos.state]
		if pcb.idx > -1:
			pcb.act = self._REDUCE
			return True

		return False

	def _get_go(self, pcb):
		# Get goto table entry

		for (sym, pcb.act, pcb.idx) in self._go[pcb.tos.state]:
			if sym == pcb.lhs:
				return True

		return False

	def _get_char(self, pcb):
		# Get next character from input stream

		if callable(pcb.input):
			return pcb.input()

		if pcb.input:
			ch = pcb.input[0]
			pcb.input = pcb.input[1:]
		else:
			ch = pcb.eof

		return ch

	def _get_input(self, pcb, offset):
		# Performs input buffering

		while offset >= len(pcb.buf):
			if pcb.is_eof:
				return pcb.eof

			ch = self._get_char(pcb)
			if ch == pcb.eof:
				pcb.is_eof = True
				return pcb.eof

			pcb.buf += ch

		#print("_get_input", pcb.buf, offset, pcb.buf[offset], ord(pcb.buf[offset]))

		return ord(pcb.buf[offset])

	def _clear_input(self, pcb):
		# Purge input from buffer that is not necessary anymore

		if pcb.buf:

			# Perform position counting.
			for pos in range(0, pcb.len):
				ch = pcb.buf[pos]
				if ch == '\n':
					pcb.line += 1
					pcb.column = 0
				else:
					pcb.column += 1

			pcb.buf = pcb.buf[pcb.len:]

		pcb.len = 0
		pcb.sym = -1

	def _lex(self, pcb):
		# Lexical analysis

		state = length = 0
		machine = self._dfa_select[pcb.tos.state] if not 1 else 0
		next = self._get_input(pcb, length)

		if next == pcb.eof:
			pcb.sym = 0
			return

		while state > -1 and next != pcb.eof:
			idx = self._dfa_index[machine][state]
			state = -1

			while self._dfa_chars[idx][0] > -1:
				if (next >= self._dfa_chars[idx][0]
					and next <= self._dfa_chars[idx][1]):

					length += 1
					state = self._dfa_trans[idx]

					if self._dfa_accept[machine][state] > 0:
						pcb.sym = self._dfa_accept[machine][state] - 1
						pcb.len = length

						# Test! (??)
						if pcb.sym == 0:
							state = -1
							break

						# Stop if matched symbol should be parsed nongreedy
						if not self._symbols[pcb.sym][5]:
							state = -1
							break

					next = self._get_input(pcb, length)
					break

				idx += 1

			# TODO: Semantic Terminal Selection?

		#print("_lex", pcb.sym, pcb.len)

	def _get_sym(self, pcb):
		# Get lookahead symbol

		pcb.sym = -1
		pcb.len = 0

		# insensitive mode
		if 1:
			while True:
				self._lex(pcb)

				# check for whitespace
				if pcb.sym > -1 and self._symbols[pcb.sym][4]:
					self._clear_input(pcb)
					continue

				break

		# sensitive mode
		else:
			if self._dfa_select[pcb.tos.state] > -1:
				self._lex(pcb)

			# If there is no matching DFA state machine, try to identify the
			# end-of-file symbol. If this also fails, a parse error will raise.
			elif self._get_input(pcb, 0) == pcb.eof:
				pcb.sym = 0

		return pcb.sym > -1

	def parse(self, s = None):
		if s is None:
			try:
				s = raw_input(">")
			except NameError:
				s = input(">")

		pcb = ParserControlBlock()
		pcb.stack = []
		pcb.input = s

		pcb.tos = ParserToken()
		pcb.stack.append(pcb.tos)

		while True:
			#print("state = %d" % pcb.tos.state)

			# TODO: Error Recovery
			self._get_sym(pcb)

			#print("pcb.sym = %d (%s)" % (pcb.sym, self._symbols[pcb.sym][0]))
			#print("pcb.len = %d" % pcb.len)

			# Get action table entry
			if not self._get_act(pcb):
				raise ParseException(pcb.line, pcb.column,
					[self._symbols[sym]
						for (sym, pcb.act, pcb.idx)
							in self._act[pcb.tos.state]])

			#print("pcb.act = %d" % pcb.act)

			# Shift
			if pcb.act & self._SHIFT:
				#print("SHIFT", pcb.sym, self._symbols[pcb.sym])

				pcb.tos = ParserToken()
				pcb.stack.append(pcb.tos)

				# Execute scanner actions, if existing.
				scan_fn = getattr(self, "_scan_action_%d" % pcb.sym, None)
				if scan_fn:
					scan_fn(pcb)

				pcb.tos.state = -1 if pcb.act & self._REDUCE else pcb.idx
				pcb.tos.symbol = self._symbols[pcb.sym]

				pcb.tos.line = pcb.line
				pcb.tos.column = pcb.column
				pcb.stack[-1 - 0].value = pcb.buf[:pcb.len]

				if pcb.tos.symbol[1]:
					pcb.tos.node = Node(pcb.tos.symbol[1], pcb.stack[-1 - 0].value)

				if pcb.sym != 0 and pcb.sym != -1:
					self._clear_input(pcb)
					pcb.old_sym = -1

			# Reduce
			while pcb.act & self._REDUCE:

				# Set default left-hand side
				pcb.lhs = self._productions[pcb.idx][3]

				#print("REDUCE", pcb.idx, self._productions[pcb.idx][0])
				#print("state", pcb.tos.state)

				# Call reduce function
				#print("CALL", "_reduce_action_%d" % pcb.idx)
				reduce_fn = getattr(self, "_reduce_action_%d" % pcb.idx, None)
				if reduce_fn:
					reduce_fn(pcb)

				# Drop right-hand side
				cnodes = None
				for _ in range(0, self._productions[pcb.idx][2]):
					item = pcb.stack.pop()

					if item.node:
						if cnodes is None:
							cnodes = []

						if isinstance(item.node, list):
							cnodes = item.node + cnodes
						else:
							cnodes.insert(0, item.node)

				pcb.tos = pcb.stack[-1]

				# Handle AST nodes
				if self._productions[pcb.idx][1]:
					#print("%s = %s" % (self._productions[pcb.idx][0], self._productions[pcb.idx][1]))
					node = Node(self._productions[pcb.idx][1],
											children=cnodes)

				else:
					node = None

				# Goal symbol reduced, and stack is empty?
				if pcb.lhs == 68 and len(pcb.stack) == 1:
					pcb.tos.node = node or cnodes
					self._clear_input(pcb)
					break

				self._get_go(pcb)

				pcb.tos = ParserToken()
				pcb.stack.append(pcb.tos)

				pcb.tos.symbol = self._symbols[pcb.lhs]
				pcb.tos.state = -1 if pcb.act & self._REDUCE else pcb.idx
				pcb.tos.value = pcb.ret
				pcb.tos.node = node or cnodes
				pcb.tos.line = pcb.line
				pcb.tos.column = pcb.column

			if pcb.act & self._REDUCE and pcb.idx == 0:
				break

		if pcb.ret is None and pcb.tos.node:
			if isinstance(pcb.tos.node, list):
				if len(pcb.tos.node) > 1:
					node = Node(children=pcb.tos.node)
				else:
					node = pcb.tos.node[0]
			else:
				node = pcb.tos.node
		else:
			node = None

		return pcb.ret or node



if __name__ == "__main__":
	import sys

	p = Parser()
	ret = p.parse(sys.argv[1] if len(sys.argv) > 1 else None)

	if isinstance(ret, Node):
		ret.dump()

