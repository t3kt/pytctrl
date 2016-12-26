from enum import Enum
import json


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


class ParamOption:
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def _JsonDict(self):
		return {'key': self.key, 'label': self.label}

	def ToJson(self):
		return json.dumps(self._JsonDict)

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


class SpecNode:
	def __init__(self,
							 key,
							 label=None,
							 tags=None):
		self.key = key
		self.label = label
		self.tags = tags

	def _ReadProperties(self, obj):
		self.label = obj.get('label')
		self.tags = obj.get('tags')

	@property
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'tags': self.tags})

	def ToJson(self):
		return json.dumps(self._JsonDict)


class ParamSpec(SpecNode):
	def __init__(
			self,
			key,
			ptype,
			label=None,
			tags=None,
			style=None,
			group=None):
		super().__init__(
			key,
			label=label,
			tags=tags)
		self.ptype = ptype
		self.style = style
		self.group = group

	def _ReadProperties(self, obj):
		super()._ReadProperties(obj)
		self.style = obj.get('style')
		self.group = obj.get('group')

	@property
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'type': self.ptype.name,
			'style': self.style,
			'group': self.group,
		}))
		return obj

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
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'otherType': self.othertype,
		}))
		obj.update(_CleanDict(self.properties))
		return obj


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
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'default': self.defaultval,
			'options': [o._JsonDict for o in self.options] if self.options else None,
		}))
		return obj


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
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'default': self.defaultval,
		}))
		return obj


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
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'default': self.defaultval,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
		}))
		return obj

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
		self.defaultval = _FillToLength(obj.get('default'), self.length)
		self.minlimit = _FillToLength(obj.get('minLimit'), self.length)
		self.maxlimit = _FillToLength(obj.get('maxLimit'), self.length)
		self.minnorm = _FillToLength(obj.get('minNorm'), self.length)
		self.maxnorm = _FillToLength(obj.get('maxNorm'), self.length)

	@property
	def _JsonDict(self):
		obj = super()._JsonDict
		obj.update(_CleanDict({
			'default': self.defaultval,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
		}))
		return obj

def _FillToLength(vals, length=None):
	length = length or 1
	if vals is None or len(vals) == 0:
		return [None] * length
	if not isinstance(vals, list):
		return [vals] * length
	if len(vals) >= length:
		return vals[:length]
	return [
		vals[i if i < len(vals) else -1]
		for i in range(length)
	]


class ModuleSpec:
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
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'moduleType': self.moduletype,
			'group': self.group,
			'tags': self.tags,
			'params': [c._JsonDict for c in self.params] if self.params else None,
			'children': [c._JsonDict for c in self.children] if self.children else None,
		})

	def __repr__(self):
		return 'ModuleSpec(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)


class AppSchema:
	def __init__(self, key, label=None, description=None, children=None):
		self.key = key
		self.label = label
		self.description = description
		self.children = children or []

	@property
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'description': self.description,
			'children': [c._JsonDict for c in self.children],
		})

	def __repr__(self):
		return 'AppSchema(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)


def _CleanDict(d):
	for k in list(d.keys()):
		if d[k] is None or d[k] == '':
			del d[k]
	return d
