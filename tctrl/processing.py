from tctrl.schema import *
import copy

def WalkChildModules(node, action):
	if node.children:
		for child in node.children:
			action(child, parent=node)
			WalkChildModules(child, action)

def ProcessAppSchema(appschema:AppSchema,
										 embedlists=False,
										 striplists=None,
										 embedmoduletypes=False,
										 stripmoduletypes=None,
										 errorhandler=None):
	if striplists is None:
		striplists = embedlists
	if stripmoduletypes is None:
		stripmoduletypes = embedmoduletypes

	appschema = copy.deepcopy(appschema)
	optionlistsbykey = {
		l.key: l for l in appschema.optionlists or []
		} if embedlists else {}

	moduletypesbykey = {
		t.key: t for t in appschema.moduletypes or []
	} if embedmoduletypes else None

	def _moduleAction(module:ModuleSpec, parent=None, **kwargs):
		if embedmoduletypes and module.moduletype and module.moduletype in moduletypesbykey:
			modtype = moduletypesbykey[module.moduletype]
			if not module.params:
				module.params = copy.deepcopy(modtype.params)
			if not module.paramgroups:
				module.paramgroups = copy.deepcopy(modtype.paramgroups)

		if embedlists and optionlistsbykey:
			for param in module.params:
				if param.optionlist and not param.options:
					if param.optionlist not in optionlistsbykey:
						if errorhandler:
							errorhandler.OnMissingList(param.optionlist, param=param)
						continue
					param.options = copy.deepcopy(optionlistsbykey[param.optionlist].options)

	WalkChildModules(appschema, _moduleAction)

	if striplists:
		appschema.optionlists = []
	if stripmoduletypes:
		appschema.moduletypes = []

	return appschema

class ErrorHandler:
	def OnMissingList(self, param):
		pass

