from tctrl.schema import *
import copy

def WalkChildModules(node, action):
	if node.children:
		for child in node.children:
			action(child, parent=node)
			WalkChildModules(child, action)

def EmbedParamOptionLists(appschema:AppSchema, striplists=True, onmissinglist=None):
	appschema = copy.deepcopy(appschema)
	optionlistsbykey = {
		l.key: l for l in appschema.optionlists or []
	}
	if not optionlistsbykey:
		return appschema

	def _moduleAction(module:ModuleSpec, parent=None, **kwargs):
		if module.params:
			for param in module.params:
				if param.optionlist and not param.options:
					if param.optionlist not in optionlistsbykey:
						if onmissinglist:
							onmissinglist(param.optionlist, param=param)
						continue
					param.options = copy.deepcopy(optionlistsbykey[param.optionlist])

	WalkChildModules(appschema, _moduleAction)

	# TODO: implement...

	if striplists:
		appschema.optionlists = []
	return appschema
