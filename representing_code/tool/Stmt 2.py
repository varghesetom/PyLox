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
		assert isinstance(statements, list), 'statements needs to match list type'
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
		assert isinstance(expression, Expr), 'expression needs to match Expr type'
		self.expression = expression

	def accept(self, visitor):
		return visitor.visit_Expression_Statement(self)

class Function_Statement(Stmt):

	def __init__(self, name, params, body):
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name
		assert isinstance(params, list), 'params needs to match list type'
		self.params = params
		assert isinstance(body, list), 'body needs to match list type'
		self.body = body

	def accept(self, visitor):
		return visitor.visit_Function_Statement(self)

class If_Statement(Stmt):

	def __init__(self, condition, then_branch, else_branch):
		assert isinstance(condition, Expr), 'condition needs to match Expr type'
		self.condition = condition
		assert isinstance(then_branch, Stmt), 'then_branch needs to match Stmt type'
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor):
		return visitor.visit_If_Statement(self)

class Print_Statement(Stmt):

	def __init__(self, expression):
		assert isinstance(expression, Expr), 'expression needs to match Expr type'
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
		assert isinstance(name, Token), 'name needs to match Token type'
		self.name = name
		assert isinstance(initializer, Expr), 'initializer needs to match Expr type'
		self.initializer = initializer

	def accept(self, visitor):
		return visitor.visit_Var_Statement(self)

class While_Statement(Stmt):

	def __init__(self, condition, body):
		assert isinstance(condition, Expr), 'condition needs to match Expr type'
		self.condition = condition
		assert isinstance(body, Stmt), 'body needs to match Stmt type'
		self.body = body

	def accept(self, visitor):
		return visitor.visit_While_Statement(self)
