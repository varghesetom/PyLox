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
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name
		assert isinstance(value, Expr), 'value needs to match Expr type'
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Assign(self)

class Binary(Expr):

	def __init__(self, left, operator, right):
		assert isinstance(left, Expr), 'left needs to match Expr type'
		self.left = left
		assert isinstance(operator, Token), 'operator needs to match Token type'
		self.operator = operator
		assert isinstance(right, Expr), 'right needs to match Expr type'
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Binary(self)

class Call(Expr):

	def __init__(self, callee, paren, arguments):
		assert isinstance(callee, Expr), 'callee needs to match Expr type'
		self.callee = callee
		assert isinstance(paren, Token), 'paren needs to match Token type'
		self.paren = paren
		assert isinstance(arguments, list), 'arguments needs to match list type'
		self.arguments = arguments

	def accept(self, visitor):
		return visitor.visit_Call(self)

class Get(Expr):

	def __init__(self, object, name):
		assert isinstance(object, Expr), 'object needs to match Expr type'
		self.object = object
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name

	def accept(self, visitor):
		return visitor.visit_Get(self)

class Set(Expr):

	def __init__(self, object, name, value):
		assert isinstance(object, Expr), 'object needs to match Expr type'
		self.object = object
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name
		assert isinstance(value, Expr), 'value needs to match Expr type'
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Set(self)

class Super(Expr):

	def __init__(self, keyword, method):
		assert isinstance(keyword, Token), 'keyword needs to match Token type'
		self.keyword = keyword
		assert isinstance(method, Token), 'method needs to match Token type'
		self.method = method

	def accept(self, visitor):
		return visitor.visit_Super(self)

class This(Expr):

	def __init__(self, keyword):
		assert isinstance(keyword, Token), 'keyword needs to match Token type'
		self.keyword = keyword

	def accept(self, visitor):
		return visitor.visit_This(self)

class Grouping(Expr):

	def __init__(self, expression):
		assert isinstance(expression, Expr), 'expression needs to match Expr type'
		self.expression = expression

	def accept(self, visitor):
		return visitor.visit_Grouping(self)

class Literal(Expr):

	def __init__(self, value):
		assert isinstance(value, object), 'value needs to match object type'
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Literal(self)

class Logical(Expr):

	def __init__(self, left, operator, right):
		assert isinstance(left, Expr), 'left needs to match Expr type'
		self.left = left
		assert isinstance(operator, Token), 'operator needs to match Token type'
		self.operator = operator
		assert isinstance(right, Expr), 'right needs to match Expr type'
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Logical(self)

class Unary(Expr):

	def __init__(self, operator, right):
		assert isinstance(operator, Token), 'operator needs to match Token type'
		self.operator = operator
		assert isinstance(right, Expr), 'right needs to match Expr type'
		self.right = right

	def accept(self, visitor):
		return visitor.visit_Unary(self)

class Variable(Expr):

	def __init__(self, name):
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name

	def accept(self, visitor):
		return visitor.visit_Variable(self)
