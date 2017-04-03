from tctrl.schema import *
import copy

class ErrorHandler:
	def OnMissingList(self, param):
		pass

def WalkChildModules(node, action):
	if node.children:
		for child in node.children:
			action(child, parent=node)
			WalkChildModules(child, action)

def ProcessAppSchema(appschema,
										 embedlists=False,
										 striplists=None,
										 embedmoduletypes=False,
										 stripmoduletypes=None,
										 generateparamgroups=False,
										 generatechildgroups=False,
										 errorhandler=None):
	if striplists is None:
		striplists = embedlists
	if stripmoduletypes is None:
		stripmoduletypes = embedmoduletypes

	appschema = copy.deepcopy(appschema)

	if embedmoduletypes:
		_EmbedModuleTypes(appschema, errorhandler)

	if embedlists:
		_EmbedSchemaLists(appschema, errorhandler)

	if generateparamgroups:
		_GenerateParamGroups(appschema)

	if generatechildgroups:
		_GenerateChildGroups(appschema)

	if striplists:
		appschema.optionlists = []
	if stripmoduletypes:
		appschema.moduletypes = []

	return appschema


def _EmbedModuleTypes(appschema,
                      errorhandler):
	if not appschema.moduletypes:
		return
	moduletypesbykey = {t.key: t for t in appschema.moduletypes}
	def _moduleAction(module: ModuleSpec, **kwargs):
		if not module.path:
			raise Exception('OMG MODULE HAS NO PATH: ' + repr(module))
		if module.moduletype and module.moduletype in moduletypesbykey:
			modtype = moduletypesbykey[module.moduletype]
			if not module.params:
				module.params = []
				for masterparam in modtype.params:
					# if not masterparam.path:
					# 	raise Exception('OMG PARAM HAS NO PATH IN module ' + module.path + ' : ' + repr(masterparam))
					param = _CreateParamFromMaster(masterparam, module)
					module.params.append(param)
			if not module.paramgroups:
				module.paramgroups = copy.deepcopy(modtype.paramgroups)
	WalkChildModules(appschema, _moduleAction)

def _CreateParamFromMaster(masterparam, module):
	param = copy.deepcopy(masterparam)
	if masterparam.path:
		param.path = module.path + masterparam.path
	else:
		param.path = module.path + ':' + param.key
	if param.parts:
		for part in param.parts:
			part.path = param.path + param.key
	return param

def _EmbedSchemaLists(appschema,
                      errorhandler):
	if not appschema.optionlists:
		return
	optionlistsbykey = {l.key: l for l in appschema.optionlists}
	def _moduleAction(module: ModuleSpec, **kwargs):
		for param in module.params:
			if param.optionlist and not param.options:
				if param.optionlist not in optionlistsbykey:
					if errorhandler:
						errorhandler.OnMissingList(param)
					continue
				param.options = copy.deepcopy(optionlistsbykey[param.optionlist].options)
	WalkChildModules(appschema, _moduleAction)

def _GenerateParamGroups(appschema):
	def _moduleAction(module: ModuleSpec, **kwargs):
		if module.params:
			module.paramgroups = _GenerateGroups(module.params, module.paramgroups)
	WalkChildModules(appschema, _moduleAction)

def _GenerateChildGroups(appschema):
	def _moduleAction(module, **kwargs):
		if module.children:
			module.childgroups = _GenerateGroups(module.children, module.childgroups)
	_moduleAction(appschema)
	WalkChildModules(appschema, _moduleAction)

def _GenerateGroups(nodes, groups):
	groups = groups or []
	if not nodes:
		return groups
	knowngroups = {g.key for g in groups}
	for node in nodes:
		if node.group and node.group not in knowngroups:
			groups.append(GroupInfo(
				node.group,
				label=node.group))
			knowngroups.add(node.group)
	return groups
