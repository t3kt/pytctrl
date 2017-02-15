from enum import Enum
import json
from tctrl.util import FillToLength

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


class ParseException(Exception):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


def _ParseParamType(str):
	if not str:
		return None
	str = str.lower()
	for t in ParamType:
		if t.name == str:
			return t
	return None


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

def _OptionFromObj(obj):
	if not obj:
		raise ParseException('Invalid ParamOption: %r' % obj)
	if isinstance(obj, str):
		return ParamOption(obj, obj)
	if isinstance(obj, dict):
		return ParamOption(key=obj['key'], label=obj.get('label'))
	raise ParseException('Invalid ParamOption: %r' % obj)


def _OptionsFromObj(obj):
	if isinstance(obj, list):
		return [_OptionFromObj(o) for o in obj]
	return None


class ParamSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			ptype,
			label=None,
			tags=None,
			style=None,
			group=None):
		self.key = key
		self.label = label
		self.ptype = ptype
		self.style = style
		self.group = group
		self.tags = tags

	def _ReadProperties(self, obj):
		self.label = obj.get('label')
		self.style = obj.get('style')
		self.group = obj.get('group')
		self.tags = obj.get('tags')

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'tags': self.tags,
			'type': self.ptype.name,
			'style': self.style,
			'group': self.group,
		})

def ParamWithType(
		key,
		ptype,
		length=1):
	if ptype == ParamType.bool:
		return BoolParamSpec(key)
	elif ptype in [ParamType.string, ParamType.menu]:
		return MenuOrStringParamSpec(key, ptype)
	elif ptype in [ParamType.int, ParamType.float]:
		if length is None or length == 1:
			return NumberParamSpec(key, ptype)
		return VectorParamSpec(key, ptype, length=length)
	elif ptype in [ParamType.ivec, ParamType.fvec]:
		return VectorParamSpec(key, ptype, length=length)
	elif ptype == ParamType.trigger:
		return ParamSpec(key, ptype)
	elif ptype == ParamType.other:
		return OtherParamSpec(key)
	else:
		return None

def ParamFromObj(obj):
	key = obj['key']
	typestr = obj['type']
	ptype = _ParseParamType(typestr)
	if ptype is None:
		param = OtherParamSpec(key, othertype=typestr)
	else:
		param = ParamWithType(key, ptype, length=obj.get('length'))
	param._ReadProperties(obj)
	return param

class OtherParamSpec(ParamSpec):
	def __init__(
			self,
			key,
			label=None,
			tags=None,
			style=None,
			group=None,
			othertype=None,
			properties=None):
		super().__init__(
			key,
			ParamType.other,
			label=label,
			tags=tags,
			style=style,
			group=group)
		self.othertype = othertype
		self.properties = properties

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		if 'otherType' in obj:
			self.othertype = obj['otherType']
		self.properties = {}
		for key, val in obj:
			if key not in ['key', 'type', 'otherType', 'style', 'group', '']:
				self.properties[key] = val

	@property
	def JsonDict(self):
		return _MergeDicts(
			super().JsonDict,
			_CleanDict({
				'otherType': self.othertype,
			}),
			_CleanDict(self.properties))


class MenuOrStringParamSpec(ParamSpec):
	def __init__(
			self,
			key,
			ptype,
			label=None,
			tags=None,
			style=None,
			group=None,
			defaultval=None,
			options=None):
		super().__init__(
			key,
			ptype,
			label=label,
			tags=tags,
			style=style,
			group=group)
		self.defaultval = defaultval
		self.options = options

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		self.defaultval = obj.get('default')
		self.options = _OptionsFromObj(obj.get('options'))

	@property
	def JsonDict(self):
		return _MergeDicts(
			super().JsonDict,
			_CleanDict({
				'default': self.defaultval,
				'options': [o.JsonDict for o in self.options] if self.options else None,
			}))


class BoolParamSpec(ParamSpec):
	def __init__(
			self,
			key,
			label=None,
			tags=None,
			style=None,
			group=None,
			defaultval=None):
		super().__init__(
			key,
			ParamType.bool,
			label=label,
			tags=tags,
			style=style,
			group=group)
		self.defaultval = defaultval

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		self.defaultval = obj.get('default')

	@property
	def JsonDict(self):
		return _MergeDicts(
			super().JsonDict,
			_CleanDict({
				'default': self.defaultval,
			}))


class NumberParamSpec(ParamSpec):
	def __init__(
			self,
			key,
			ptype,
			label=None,
			tags=None,
			style=None,
			group=None,
			defaultval=None,
			minlimit=None,
			maxlimit=None,
			minnorm=None,
			maxnorm=None):
		super().__init__(
			key,
			ptype,
			label=label,
			tags=tags,
			style=style,
			group=group)
		self.defaultval = defaultval
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		self.defaultval = obj.get('default')
		self.minlimit = obj.get('minLimit')
		self.maxlimit = obj.get('maxLimit')
		self.minnorm = obj.get('minNorm')
		self.maxnorm = obj.get('maxNorm')

	@property
	def JsonDict(self):
		return _MergeDicts(
			super().JsonDict,
			_CleanDict({
				'default': self.defaultval,
				'minLimit': self.minlimit,
				'maxLimit': self.maxlimit,
				'minNorm': self.minnorm,
				'maxNorm': self.maxnorm,
			}))

class VectorParamSpec(ParamSpec):
	def __init__(
			self,
			key,
			ptype,
			length=1,
			label=None,
			tags=None,
			style=None,
			group=None,
			defaultval=None,
			minlimit=None,
			maxlimit=None,
			minnorm=None,
			maxnorm=None):
		super().__init__(
			key,
			ptype,
			label=label,
			tags=tags,
			style=style,
			group=group)
		self.length = length
		self.defaultval = defaultval
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		self.length = obj['length']
		self.defaultval = FillToLength(obj.get('default'), self.length)
		self.minlimit = FillToLength(obj.get('minLimit'), self.length)
		self.maxlimit = FillToLength(obj.get('maxLimit'), self.length)
		self.minnorm = FillToLength(obj.get('minNorm'), self.length)
		self.maxnorm = FillToLength(obj.get('maxNorm'), self.length)

	@property
	def JsonDict(self):
		return _MergeDicts(
			super().JsonDict,
			_CleanDict({
				'default': self.defaultval,
				'minLimit': self.minlimit,
				'maxLimit': self.maxlimit,
				'minNorm': self.minnorm,
				'maxNorm': self.maxnorm,
			}))


class ModuleSpec(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			moduletype=None,
			group=None,
			tags=None,
			params=None,
			children=None):
		self.key = key
		self.label = label
		self.moduletype = moduletype
		self.group = group
		self.tags = tags
		self.params = params
		self.children = children

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'tags': self.tags,
			'moduleType': self.moduletype,
			'group': self.group,
			'params': [c.JsonDict for c in self.params] if self.params else None,
			'children': [c.JsonDict for c in self.children] if self.children else None,
		})

	def _ReadProperties(self, obj):
		self.label = obj.get('label')
		self.moduletype = obj.get('moduleType')
		self.group = obj.get('group')
		self.tags = obj.get('tags')
		paramobjs = obj.get('params')
		childobjs = obj.get('children')
		self.params = [ParamFromObj(o) for o in paramobjs] if paramobjs else None
		self.children = [ModuleFromObj(o) for o in childobjs] if childobjs else None

def ModuleFromObj(obj):
	key = obj['key']
	module = ModuleSpec(key)
	module._ReadProperties(obj)
	return module

class AppSchema(_BaseSchemaNode):
	def __init__(
			self,
			key,
			label=None,
			tags=None,
			description=None,
			children=None):
		self.key = key
		self.label = label
		self.tags = tags
		self.description = description
		self.children = children or []

	@property
	def JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'tags': self.tags,
			'description': self.description,
			'children': [c.JsonDict for c in self.children] if self.children else None,
		})

	def _ReadProperties(self, obj):
		self.label = obj.get('label')
		self.tags = obj.get('tags')
		self.description = obj.get('description')
		childobjs = obj.get('children')
		self.children = [ModuleFromObj(o) for o in childobjs] if childobjs else None

def AppFromObj(obj):
	app = AppSchema(obj['key'])
	app._ReadProperties(obj)
	return app

def _CleanDict(d):
	for k in list(d.keys()):
		if d[k] is None or d[k] == '':
			del d[k]
	return d

def _MergeDicts(*parts):
	d = dict()
	if parts:
		for part in parts:
			d.update(part)
	return d
