from enum import Enum
import json
from tctrl.util import CleanDict, MergeDicts, GetByKey

class ParamType(Enum):
	other = 1
	bool = 3
	string = 4
	int = 5
	float = 6
	ivec = 7
	fvec = 8
	menu = 10
	trigger = 11

class _BaseSchemaNode:
	@property
	def JsonDict(self):
		raise NotImplementedError()

	def ToJson(self, **kwargs):
		return json.dumps(self.JsonDict, **kwargs)

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.JsonDict)

class ParamOption(_BaseSchemaNode):
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def JsonDict(self):
		return {'key': self.key, 'label': self.label}

class ParamPartSpec(_BaseSchemaNode):
	def __init__(self,
	             key,
	             path=None,
	             label=None,
	             minlimit=None,
	             maxlimit=None,
	             minnorm=None,
	             maxnorm=None,
	             defaultval=None,
	             value=None):
		self.key = key
		self.path = path
		self.label = label
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm
		self.defaultval = defaultval
		self.value = value

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'path': self.path,
			'label': self.label,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
			'default': self.defaultval,
			'value': self.value,
		})

class ParamSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			ptype=ParamType.other,
			path=None,
			othertype=None,
			minlimit=None,
			maxlimit=None,
			minnorm=None,
			maxnorm=None,
			defaultval=None,
			value=None,
			valueindex=None,
			parts=None,
			length=None,
			style=None,
			group=None,
			options=None,
			tags=None,
			help=None,
			offhelp=None,
			buttontext=None,
			buttonofftext=None,
			properties=None):
		self.key = key
		self.label = label
		self.ptype = ptype
		self.path = path
		self.othertype = othertype
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm
		self.defaultval = defaultval
		self.value = value
		self.valueindex = valueindex
		self.parts = parts
		self.length = length
		self.style = style
		self.group = group
		self.options = options
		self.tags = tags
		self.help = help
		self.offhelp = offhelp
		self.buttontext = buttontext
		self.buttonofftext = buttonofftext
		self.properties = properties

	@property
	def JsonDict(self):
		return MergeDicts(
			CleanDict(self.properties),
			CleanDict({
				'key': self.key,
				'path': self.path,
				'label': self.label,
				'type': self.ptype.name,
				'otherType': self.othertype,
				'minLimit': self.minlimit,
				'maxLimit': self.maxlimit,
				'minNorm': self.minnorm,
				'maxNorm': self.maxnorm,
				'default': self.defaultval,
				'value': self.value,
				'valueIndex': self.valueindex,
				'parts': [p.JsonDict for p in self.parts] if self.parts else None,
				'length': self.length,
				'style': self.style,
				'group': self.group,
				'options': [o.JsonDict for o in self.options] if self.options else None,
				'help': self.help,
				'offHelp': self.offhelp,
				'buttonText': self.buttontext,
				'buttonOffText': self.buttonofftext,
				'tags': self.tags,
			}))

class _BaseParentSchemaNode(_BaseSchemaNode):
	def __init__(self, children=None):
		self.children = children or []

	@property
	def JsonDict(self):
		raise NotImplementedError()

	def GetChild(self, key):
		return GetByKey(self.children, key)

	def EvaluatePath(self, path):
		if not path:
			return
		if '/' in path:
			firstpart, rest = path.split('/', maxsplit=1)
			m = self.GetChild(firstpart)
			if not m:
				return None
			return m.EvaluatePath(rest)
		else:
			return self.GetChild(path)

class ModuleSpec(_BaseParentSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			path=None,
			moduletype=None,
			group=None,
			tags=None,
			params=None,
			children=None):
		super().__init__(children=children)
		self.key = key
		self.label = label
		self.path = path
		self.moduletype = moduletype
		self.group = group
		self.tags = tags
		self.params = params or []
		self.children = children or []

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'label': self.label,
			'path': self.path,
			'tags': self.tags,
			'moduleType': self.moduletype,
			'group': self.group,
			'params': [c.JsonDict for c in self.params] if self.params else None,
			'children': [c.JsonDict for c in self.children] if self.children else None,
		})

	def GetParam(self, key):
		return GetByKey(self.params, key)

	def EvaluatePath(self, path):
		if path and path.startswith('@'):
			return self.GetParam(path[1:])
		return super().EvaluatePath(path)

class AppSchema(_BaseParentSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			tags=None,
			description=None,
			children=None):
		super().__init__(children=children)
		self.key = key
		self.path = '/' + key
		self.label = label
		self.tags = tags
		self.description = description

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'path': self.path,
			'label': self.label,
			'tags': self.tags,
			'description': self.description,
			'children': [c.JsonDict for c in self.children] if self.children else None,
		})

