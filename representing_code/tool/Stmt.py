#!/usr/bin/env python

import sys
sys.path.insert(1, '../../scanner')
from abc import ABC, abstractmethod
from Expr import Expr
from Token import Token

class Stmt(ABC):

	@abstractmethod
	def __init__(self, left, operator, right):
		pass

class Block(Stmt):

	def __init__(self, statements):
		self.statements = statements

	def accept(self, visitor):
		return visitor.visit_Block(self)

class Class_Statement(Stmt):

	def __init__(self, name, superclass, methods):
		self.name = name
		self.superclass = superclass
		self.methods = methods

	def accept(self, visitor):
		return visitor.visit_Class_Statement(self)

class Expression_Statement(Stmt):

	def __init__(self, expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visit_Expression_Statement(self)

class Function_Statement(Stmt):

	def __init__(self, name, params, body):
		self.name = name
		self.params = params
		self.body = body

	def accept(self, visitor):
		return visitor.visit_Function_Statement(self)

class If_Statement(Stmt):

	def __init__(self, condition, then_branch, else_branch):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor):
		return visitor.visit_If_Statement(self)

class Print_Statement(Stmt):

	def __init__(self, expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visit_Print_Statement(self)

class Return_Statement(Stmt):

	def __init__(self, keyword, value):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor):
		return visitor.visit_Return_Statement(self)

class Var_Statement(Stmt):

	def __init__(self, name, initializer):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor):
		return visitor.visit_Var_Statement(self)

class While_Statement(Stmt):

	def __init__(self, condition, body):
		self.condition = condition
		self.body = body

	def accept(self, visitor):
		return visitor.visit_While_Statement(self)
