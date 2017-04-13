from enum import Enum
import json
from tctrl.util import CleanDict, MergeDicts, GetByKey

class ParamType(Enum):
	"""The type of a parameter, which indicates what kind of value(s)
	it contains and how it is structured and handled."""
	
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
	"""A selectable option for a menu parameter or a string parameter that
	provides a set of suggested options."""
	
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def JsonDict(self):
		return {'key': self.key, 'label': self.label}

class OptionList(_BaseSchemaNode):
	"""A named list of ParamOptions include in an AppSchema which a ParamSpec
	can reference as an alternative to specifying options directly in the
	parameter schema."""
	
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
	"""A part of a multi-part ParamSpec (ivec or fvec)."""
	
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
	"""Defines a controllable parameter of a ModuleSpec. The parameter's
	ParamType defines which fields of the ParamSpec are used."""
	
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
		"""Minimum (inclusive) bound for a numeric parameter. If specified, the
		target application will not permit values below the specified value. If
		not specified, the parameter has no minimum value."""
		
		self.maxlimit = maxlimit
		"""Maximum (inclusive) bound for a numeric parameter. If specified, the
		target application will not permit values above the specified value. If
		not specified, the parameter has no maximum value."""
		
		self.minnorm = minnorm
		"""Minimum expected value for numeric parameter. The parameter may still
		permit values below this minimum. This is typically used for things like
		the range of a slider bound to this parameter. Control applications may
		require this field to be specififed for all numeric parameters."""
		
		self.maxnorm = maxnorm
		"""Maximum expected value for numeric parameter. The parameter may still
		permit values above this maximum. This is typically used for things like
		the range of a slider bound to this parameter. Control applications may
		require this field to be specififed for all numeric parameters."""
		
		self.defaultval = defaultval
		self.value = value
		self.valueindex = valueindex
		self.parts = parts
		self.style = style
		self.group = group
		
		self.options = options
		"""A list of ParamOptions that define the available options for a menu
		parameter, or an optional set of suggested values for a string
		parameter. Parameters that are not menus or strings do not use this
		field."""
		
		self.optionlist = optionlist
		"""The name of an OptionList defined in the AppSchema. This can be used
		as an alternative to specifying the options field directly. If the name
		does not correspond to an OptionList in the AppSchema, control
		applications may treat this as an error, or may just treat the parameter
		as having no available options."""
		
		self.tags = tags
		"""An optional set of string tags that indicate supplemental information
		about a parameter. For example, it could indicate that a parameter is
		an 'advanced' parameter, or that it should not support MIDI mapping."""
		
		self.help = help
		self.offhelp = offhelp
		self.buttontext = buttontext
		self.buttonofftext = buttonofftext
		
		self.properties = properties
		"""An optional dict of arbitrary additional attributes. This is
		typically used for unrecognized fields when parsing from JSON."""

	@property
	def JsonDict(self):
		return MergeDicts(
			CleanDict(self.properties),
			CleanDict({
				'key': self.key,
				'path': self.path,
				'label': self.label,
				'type': self.ptype.name if self.ptype else None,
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
				'tags': _TagsToJsList(self.tags),
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
	"""Defines a type of module which is included in an AppSchema and can be
	referenced by a ModuleSpec as an alternative to directly including full
	schema information about its parameters."""
	
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
	"""Defines a module in an AppSchema that handles some arbitrary behavior in
	the target app, and has a set of parameters which control that behvior. A
	module can either specify the full details of its parameters directly in the
	ModuleSpec or it can refer to a named ModuleTypeSpec defined elsewhere in
	the containing AppSchema."""
	
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
			'tags': _TagsToJsList(self.tags),
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
	"""Defines an available mode of communication with the target app, such as
	OSC input or output. Each type and direction of communication is defined by
	its own ConnectionInfo. So an OSC input port would be defined in a separate
	ConnectionInfo than an OSC output port."""
	
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
	"""Defines metadata about a grouping of elements. Groups can either apply
	to parameters of ModuleSpec or to child modules in a ModuleSpec or
	AppSchema."""
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
			'tags': _TagsToJsList(self.tags),
		})

class AppSchema(_BaseParentSchemaNode):
	"""Defines the schema of a full application. Functionality is grouped into a
	set of hierarchical modules. The AppSchema also contains general metadata
	about the application as a whole, such as how to communicate with it and how
	to represent it in a controller application."""
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
		"""A list of OptionLists which can be referenced by ParamSpecs within
		the AppSchema. Note that this is a list rather than a dict, but that the
		OptionLists in the list should have unique values in their key
		fields."""
		
		self.moduletypes = moduletypes or []
		"""A list of ModuleTypeSpecs which can be referenced by ModuleSpecs
		within the AppSchema. Note that this is a list rather than a dict, but
		that the ModuleTypeSpecs in the list should have unique values in their
		key fields."""

	@property
	def JsonDict(self):
		return CleanDict({
			'key': self.key,
			'path': self.path,
			'label': self.label,
			'tags': _TagsToJsList(self.tags),
			'description': self.description,
			'childGroups': _NodeListToJson(self.childgroups),
			'children': _NodeListToJson(self.children),
			'connections': _NodeListToJson(self.connections),
			'optionLists': _NodeListToJson(self.optionlists),
			'moduleTypes': _NodeListToJson(self.moduletypes),
		})

def _TagsToJsList(tags):
	if not tags:
		return None
	return sorted(tags)
