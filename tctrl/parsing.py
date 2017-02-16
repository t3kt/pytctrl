# tctrl.parser

from tctrl.schema import ParamType, ParamOption, ParamPartSpec, ParamSpec, ModuleSpec, AppSchema

class ParseException(Exception):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


def ParseParamType(s):
	if not s:
		return None
	s = s.lower()
	for t in ParamType:
		if t.name == s:
			return t
	return None

def OptionFromObj(obj):
	if not obj:
		raise ParseException('Invalid ParamOption: %r' % obj)
	if isinstance(obj, str):
		return ParamOption(obj, obj)
	if isinstance(obj, dict):
		return ParamOption(key=obj['key'], label=obj.get('label'))
	raise ParseException('Invalid ParamOption: %r' % obj)


def OptionsFromObj(obj):
	return [OptionFromObj(o) for o in obj] if obj else None

def ReadParamPartFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Param part is missing key')
	return ParamPartSpec(
		obj['key'],
		label=obj.get('label'),
		defaultval=obj.get('default'),
		minlimit=obj.get('minLimit'),
		maxlimit=obj.get('maxLimit'),
		minnorm=obj.get('minNorm'),
		maxnorm=obj.get('maxNorm'),
	)

def ReadParamFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Param is missing key')
	if 'type' not in obj:
		raise ParseException('Param is missing type')
	typestr = obj['type']
	ptype = ParseParamType(typestr) or ParamType.other
	partobjs = obj.get('parts')
	length = obj.get('length') or (len(partobjs) if partobjs else None) or 1
	param = ParamSpec(obj['key'], ptype, length=length)
	param.othertype = obj.get('otherType') or obj.get('type')
	param.label = obj.get('label')
	param.style = obj.get('style')
	param.group = obj.get('group')
	param.tags = obj.get('tags')
	param.defaultval = obj.get('default')
	param.minlimit = obj.get('minLimit')
	param.maxlimit = obj.get('maxLimit')
	param.minnorm = obj.get('minNorm')
	param.maxnorm = obj.get('maxNorm')
	param.parts = [ReadParamPartFromObj(p) for p in partobjs] if partobjs else None
	param.options = OptionsFromObj(obj.get('options'))
	param.properties = {}
	for key, val in obj.items():
		if key not in _KnownKeys:
			param.properties[key] = val
	return param

_KnownKeys = [
	'key',
	'label',
	'type',
	'length',
	'otherType',
	'minLimit',
	'maxLimit',
	'minNorm',
	'maxNorm',
	'default',
	'parts',
	'length',
	'style',
	'group',
	'options',
	'tags',
]

def ReadModuleFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Module is missing key')
	module = ModuleSpec(obj['key'])
	module.moduletype = obj.get('moduleType')
	module.label = obj.get('label')
	module.group = obj.get('group')
	module.tags = obj.get('tags')
	paramobjs = obj.get('params')
	module.params = [ReadParamFromObj(o) for o in paramobjs] if paramobjs else None
	childobjs = obj.get('children')
	module.children = [ReadModuleFromObj(o) for o in childobjs] if childobjs else None
	return module

def ReadAppFromObj(obj):
	if 'key' not in obj:
		raise ParseException('App is missing key')
	app = AppSchema(obj['key'])
	app.label = obj.get('label')
	app.tags = obj.get('tags')
	app.description = obj.get('description')
	childobjs = obj.get('children')
	app.children = [ReadModuleFromObj(o) for o in childobjs] if childobjs else None
	return app
