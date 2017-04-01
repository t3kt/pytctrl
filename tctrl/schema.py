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

def _NodeListToJson(nodes):
	if not nodes:
		return None
	return [n.JsonDict for n in nodes]

class _BaseSchemaNode:
	@property
	def JsonDict(self):
		raise NotImplementedError()

	def ToJson(self, **kwargs):
		dumpargs = {'sort_keys': True}
		dumpargs.update(kwargs)
		return json.dumps(self.JsonDict, **dumpargs)

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.JsonDict)

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return self.__dict__ == other.__dict__

class ParamOption(_BaseSchemaNode):
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def JsonDict(self):
		return {'key': self.key, 'label': self.label}

class OptionList(_BaseSchemaNode):
	def __init__(self,
							 key,
							 label=None,
							 options=None):
		self.key = key
		self.label = label
		self.options = options or []

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'label': self.label,
			'options': _NodeListToJson(self.options),
		})

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
			style=None,
			group=None,
			options=None,
			optionlist=None,
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
		self.style = style
		self.group = group
		self.options = options
		self.optionlist = optionlist
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
				'parts': _NodeListToJson(self.parts),
				'style': self.style,
				'group': self.group,
				'options': _NodeListToJson(self.options),
				'optionList': self.optionlist,
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

class ModuleTypeSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			params=None,
			paramgroups=None):
		self.key = key
		self.label = label
		self.params = params or []
		self.paramgroups = paramgroups or []

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'label': self.label,
			'paramGroups': _NodeListToJson(self.paramgroups),
			'params': _NodeListToJson(self.params),
		})

	def GetParam(self, key):
		return GetByKey(self.params, key)

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
			children=None,
			paramgroups=None,
			childgroups=None):
		super().__init__(children=children)
		self.key = key
		self.label = label
		self.path = path
		self.moduletype = moduletype
		self.group = group
		self.tags = tags
		self.params = params or []
		self.children = children or []
		self.paramgroups = paramgroups or []
		self.childgroups = childgroups or []

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'label': self.label,
			'path': self.path,
			'tags': self.tags,
			'moduleType': self.moduletype,
			'group': self.group,
			'paramGroups': _NodeListToJson(self.paramgroups),
			'childGroups': _NodeListToJson(self.childgroups),
			'params': _NodeListToJson(self.params),
			'children': _NodeListToJson(self.children),
		})

	def GetParam(self, key):
		return GetByKey(self.params, key)

class ConnectionInfo(_BaseSchemaNode):
	def __init__(self,
	             conntype=None,
	             host=None,
	             port=None):
		self.conntype = conntype
		self.host = host
		self.port = port

	@property
	def JsonDict(self):
		return CleanDict({
			'type': self.conntype,
			'host': self.host,
			'port': self.port,
		})

class GroupInfo(_BaseSchemaNode):
	def __init__(
		self,
		key,
		label=None,
		tags=None):
		self.key = key
		self.label = label
		self.tags = tags

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'label': self.label,
			'tags': self.tags,
		})

class AppSchema(_BaseParentSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			tags=None,
			description=None,
			children=None,
			childgroups=None,
			optionlists=None,
			connections=None,
			moduletypes=None):
		super().__init__(children=children)
		self.key = key
		self.path = '/' + key
		self.label = label
		self.tags = tags
		self.description = description
		self.connections = connections
		self.childgroups = childgroups or []
		self.optionlists = optionlists or []
		self.moduletypes = moduletypes or []

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'path': self.path,
			'label': self.label,
			'tags': self.tags,
			'description': self.description,
			'childGroups': _NodeListToJson(self.childgroups),
			'children': _NodeListToJson(self.children),
			'connections': _NodeListToJson(self.connections),
			'optionLists': _NodeListToJson(self.optionlists),
		})
