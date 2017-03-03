# tctrl.parser

from tctrl.schema import ParamType, ParamOption, ParamPartSpec, ParamSpec, ModuleSpec, ConnectionInfo, AppSchema

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

def ReadParamPartFromObj(obj, pathprefix=None):
	if 'key' not in obj:
		raise ParseException('Param part is missing key')
	return ParamPartSpec(
		obj['key'],
		label=obj.get('label'),
		defaultval=obj.get('default'),
		value=obj.get('value'),
		minlimit=obj.get('minLimit'),
		maxlimit=obj.get('maxLimit'),
		minnorm=obj.get('minNorm'),
		maxnorm=obj.get('maxNorm'),
		path=(pathprefix + obj['key']) if pathprefix else None,
	)

def ReadParamFromObj(obj, pathprefix=None):
	if 'key' not in obj:
		raise ParseException('Param is missing key')
	if 'type' not in obj:
		raise ParseException('Param is missing type')
	typestr = obj['type']
	ptype = ParseParamType(typestr) or ParamType.other
	partobjs = obj.get('parts')
	path = (pathprefix + obj['key']) if pathprefix else None
	return ParamSpec(
		obj['key'],
		ptype=ptype,
		path=path,
		label=obj.get('label'),
		othertype=obj.get('otherType') or obj.get('type'),
		style=obj.get('style'),
		group=obj.get('group'),
		tags=obj.get('tags'),
		help=obj.get('help'),
		offhelp=obj.get('offHelp'),
		buttontext=obj.get('buttonText'),
		buttonofftext=obj.get('buttonOffText'),
		defaultval=obj.get('default'),
		value=obj.get('value'),
		valueindex=obj.get('valueIndex'),
		minlimit=obj.get('minLimit'),
		maxlimit=obj.get('maxLimit'),
		minnorm=obj.get('minNorm'),
		maxnorm=obj.get('maxNorm'),
		options=OptionsFromObj(obj.get('options')),
		parts=[
			ReadParamPartFromObj(p, pathprefix=path)
			for p in partobjs
			] if partobjs else None,
		properties={key: val for key, val in obj.items() if key not in _KnownKeys}
	)

_KnownKeys = [
	'key',
	'path',
	'label',
	'type',
	'otherType',
	'minLimit',
	'maxLimit',
	'minNorm',
	'maxNorm',
	'default',
	'value',
	'valueIndex',
	'parts',
	'style',
	'group',
	'options',
	'help',
	'offHelp',
	'buttonText',
	'buttonOffText',
	'tags',
]

def ReadModuleFromObj(obj, pathprefix=None):
	if 'key' not in obj:
		raise ParseException('Module is missing key')
	paramobjs = obj.get('params')
	childobjs = obj.get('children')
	path = (pathprefix + obj['key']) if pathprefix else None
	childprefix = (path + '/') if path else None
	return ModuleSpec(
		obj['key'],
		path=path,
		moduletype=obj.get('moduleType'),
		label=obj.get('label'),
		group=obj.get('group'),
		tags=obj.get('tags'),
		params=[
			ReadParamFromObj(o, pathprefix=childprefix) for o in paramobjs
			] if paramobjs else None,
		children=[
			ReadModuleFromObj(o, pathprefix=childprefix) for o in childobjs
			] if childobjs else None,
	)

def ReadConnectionFromObj(obj):
	if 'type' not in obj:
		raise ParseException('Connection is missing type')
	return ConnectionInfo(
		conntype=obj['type'],
		host=obj.get('host'),
		port=obj.get('port'),
	)

def ReadAppFromObj(obj):
	if 'key' not in obj:
		raise ParseException('App is missing key')
	childobjs = obj.get('children')
	connobjs = obj.get('connections')
	childprefix = obj['key'] + '/'
	return AppSchema(
		obj['key'],
		label=obj.get('label'),
		tags=obj.get('tags'),
		description=obj.get('description'),
		children=[
			ReadModuleFromObj(o, pathprefix=childprefix) for o in childobjs
			] if childobjs else None,
		connections=[
			ReadConnectionFromObj(o) for o in connobjs
			] if connobjs else None,
	)
