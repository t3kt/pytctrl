from tctrl.schema import *

class ModelNode:
	def __init__(self, key, path):
		self.key = key
		self.path = path

class ParamModel(ModelNode):
	def __init__(
			self,
			spec: ParamSpec,
			parent: ModelNode):
		super().__init__(
			spec.key,
			path='%s/%s' % (parent.path, spec.key))
		self.spec = spec
		self.parent = parent

	@property
	def label(self):
		return self.spec.label

def _MapByKey(nodes):
	return { n.key: n for n in nodes } if nodes else {}

class ModuleModel(ModelNode):
	def __init__(
			self,
			spec: ParamSpec,
			parent: ModelNode):
		super().__init__(
			spec.key,
			path='%s/%s' % (parent.path, spec.key))
		self.spec = spec
		self.parent = parent

	@property
	def label(self):
		return self.spec.label
