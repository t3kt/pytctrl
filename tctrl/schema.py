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

class ParamOption:
	def __init__(self, key, label):
		self.key = key
		self.label = label

	@property
	def _JsonDict(self):
		return {'key': self.key, 'label': self.label}

	def ToJson(self):
		return json.dumps(self._JsonDict)

	@staticmethod
	def FromObj(obj):
		if not obj:
			raise ParseException('Invalid ParamOption: %r' % obj)
		if isinstance(obj, str):
			return ParamOption(obj, obj)
		if isinstance(obj, dict):
			return ParamOption(key=obj['key'], label=obj.get('label'))
		raise ParseException('Invalid ParamOption: %r' % obj)

class ParamSpec:
	def __init__(
			self,
			key,
			label=None,
			ptype=ParamType.other,
			othertype=None,
			minlimit=None,
			maxlimit=None,
			minnorm=None,
			maxnorm=None,
			defaultval=None,
			length=None,
			style=None,
			group=None,
			options=None,
			tags=None):
		self.key = key
		self.label = label
		self.ptype = ptype
		self.othertype = othertype
		self.minlimit = minlimit
		self.maxlimit = maxlimit
		self.minnorm = minnorm
		self.maxnorm = maxnorm
		self.defaultval = defaultval
		self.length = length
		self.style = style
		self.group = group
		self.options = options
		self.tags = tags

	@property
	def _JsonDict(self):
		return _CleanDict({
			'key': self.key,
			'label': self.label,
			'type': self.ptype.name,
			'othertype': self.othertype,
			'minLimit': self.minlimit,
			'maxLimit': self.maxlimit,
			'minNorm': self.minnorm,
			'maxNorm': self.maxnorm,
			'default': self.defaultval,
			'length': self.length,
			'style': self.style,
			'group': self.group,
			'options': [o._JsonDict for o in self.options] if self.options else None,
			'tags': self.tags,
		})

	def __repr__(self):
		return 'ParamSpec(%r)' % self._JsonDict

	def ToJson(self):
		return json.dumps(self._JsonDict)

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
