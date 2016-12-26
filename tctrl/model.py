from tctrl.schema import *

class Accessor:
	def __init__(self):
		self.paramVals = {}

	def SetParam(self, param, value):
		self.paramVals[param.path] = value

	def GetParam(self, param):
		return self.paramVals.get(param.path)

class ModelNode:
	def __init__(self, key, path):
		self.key = key
		self.path = path


class ParamModel(ModelNode):
	def __init__(
			self,
			spec: ParamSpec,
			parent: 'ModuleModel'):
		super().__init__(
			spec.key,
			path='%s/%s' % (parent.path, spec.key))
		self.app = parent.app
		self.spec = spec
		self.parent = parent

	@property
	def label(self):
		return self.spec.label

	@property
	def value(self):
		return self.app.accessor.GetParam(self)

	@value.setter
	def value(self, val):
		self.app.accessor.SetParam(self, val)


def _MapByKey(nodes):
	return {n.key: n for n in nodes} if nodes else {}


class ModuleModel(ModelNode):
	def __init__(
			self,
			app: 'AppModel',
			spec: ModuleSpec,
			parent: 'ModuleModel'):
		super().__init__(
			spec.key,
			path='%s/%s' % (parent.path if parent else app.path, spec.key))
		self.app = app
		self.spec = spec
		self.parent = parent
		self.children = _MapByKey([ModuleModel(app=app, spec=spec, parent=self) for spec in spec.children] if spec.children else None)
		self.params = _MapByKey([ParamModel(spec=spec, parent=self) for spec in spec.params] if spec.params else None)

	@property
	def label(self):
		return self.spec.label


class AppModel(ModelNode):
	def __init__(self, spec, accessor=None):
		super().__init__(spec.key, '/%s' % spec.key)
		self.app = self
		self.accessor = accessor or Accessor()
		self.children = _MapByKey([ModuleModel(app=self, spec=spec) for spec in spec.children] if spec.children else [])
