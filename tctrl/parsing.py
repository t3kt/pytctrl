# tctrl.parser

from tctrl.schema import ParamType, ParamOption, ParamPartSpec, ParamSpec, ModuleSpec, ConnectionInfo, AppSchema, ModuleTypeSpec, OptionList, GroupInfo

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


def OptionsFromObjList(obj):
	return [OptionFromObj(o) for o in obj] if obj else None

def ReadOptionListFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Option list is missing key')
	return OptionList(
		obj['key'],
		label=obj.get('label'),
		options=OptionsFromObjList(obj.get('options')),
	)

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
		options=OptionsFromObjList(obj.get('options')),
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
		paramgroups=_GroupsFromObjs(obj.get('paramGroups')),
		children=[
			ReadModuleFromObj(o, pathprefix=childprefix) for o in childobjs
			] if childobjs else None,
		childgroups=_GroupsFromObjs(obj.get('childGroups')),
	)

def ReadModuleTypeFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Module type is missing key')
	paramobjs = obj.get('params')
	return ModuleTypeSpec(
		obj['key'],
		label=obj.get('label'),
		params=[
			ReadParamFromObj(o, pathprefix=':') for o in paramobjs
			] if paramobjs else None,
		paramgroups=_GroupsFromObjs(obj.get('paramGroups')),
	)

def ReadConnectionFromObj(obj):
	if 'type' not in obj:
		raise ParseException('Connection is missing type')
	return ConnectionInfo(
		conntype=obj['type'],
		host=obj.get('host'),
		port=obj.get('port'),
	)

def ReadGroupInfoFromObj(obj):
	if 'key' not in obj:
		raise ParseException('Group info is missing type')
	return GroupInfo(
		obj['key'],
		label=obj.get('label'),
		tags=obj.get('tags'),
	)

def _GroupsFromObjs(objs):
	if not objs:
		return None
	return [ReadGroupInfoFromObj(o) for o in objs]

def ReadAppFromObj(obj):
	if 'key' not in obj:
		raise ParseException('App is missing key')
	childobjs = obj.get('children')
	connobjs = obj.get('connections')
	childprefix = obj['key'] + '/'
	modtypeobjs = obj.get('moduleTypes')
	optionlistobjs = obj.get('optionLists')
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
		moduletypes=[
			ReadModuleTypeFromObj(o) for o in modtypeobjs
		] if modtypeobjs else None,
		optionlists=[
			ReadOptionListFromObj(o) for o in optionlistobjs
		] if optionlistobjs else None,
	)
