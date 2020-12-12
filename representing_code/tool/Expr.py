#!/usr/bin/env python

import sys
sys.path.insert(1, '../../scanner')
from abc import ABC, abstractmethod
from Token import Token

class Expr(ABC):

	@abstractmethod
	def __init__(self, left, operator, right):
		pass

class Assign(Expr):

	def __init__(self, name, value):
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Assign(self)

class Binary(Expr):

	def __init__(self, left, operator, right):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Binary(self)

class Call(Expr):

	def __init__(self, callee, paren, arguments):
		self.callee = callee
		self.paren = paren
		self.arguments = arguments

	def accept(self, visitor):
		return visitor.visit_Call(self)

class Get(Expr):

	def __init__(self, object, name):
		self.object = object
		self.name = name

	def accept(self, visitor):
		return visitor.visit_Get(self)

class Set(Expr):

	def __init__(self, object, name, value):
		self.object = object
		self.name = name
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Set(self)

class Super(Expr):

	def __init__(self, keyword, method):
		self.keyword = keyword
		self.method = method

	def accept(self, visitor):
		return visitor.visit_Super(self)

class This(Expr):

	def __init__(self, keyword):
		self.keyword = keyword

	def accept(self, visitor):
		return visitor.visit_This(self)

class Grouping(Expr):

	def __init__(self, expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visit_Grouping(self)

class Literal(Expr):

	def __init__(self, value):
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Literal(self)

class Logical(Expr):

	def __init__(self, left, operator, right):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Logical(self)

class Unary(Expr):

	def __init__(self, operator, right):
		self.operator = operator
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Unary(self)

class Variable(Expr):

	def __init__(self, name):
		self.name = name

	def accept(self, visitor):
		return visitor.visit_Variable(self)
