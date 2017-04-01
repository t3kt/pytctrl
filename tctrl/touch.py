import tctrl.schema as schema

class ModuleSchemaBuilder:
	def __init__(self,
	             comp,
	             appkey=None,
	             excludepages=None,
	             tags=None,
	             key=None,
	             label=None,
	             path=None,
	             moduletype=None,
	             group=None):
		self.comp = comp
		if not key:
			key = comp.name
		modspec = self.modspec = schema.ModuleSpec(key)
		if path:
			modspec.path = path
		else:
			modspec.path = (('/' + appkey + '/') if appkey else '') + comp.path
		modspec.label = label or key.replace('_', ' ')
		self.excludepages = excludepages or []
		# passing tags=[] means no tags but passing tags=None means auto-tags
		if tags is None:
			modspec.tags = list(comp.tags)
		else:
			modspec.tags = tags
		if moduletype:
			modspec.moduletype = moduletype
		else:
			master = comp.par.clone.eval()
			modspec.moduletype = master.path if master else None
		modspec.group = group


	def GetModuleParamTuplets(self, comp):
		tuplets = []
		for page in self.GetModuleParamPages(comp):
			tuplets += self._GetPageParamTuplets(comp, page=page)
		return tuplets

	def BuildModuleParamSchemas(self, comp):
		tuplets = self.GetModuleParamTuplets(comp)
		pass

	def GetModuleParamPages(self, comp):
		for page in comp.customPages:
			if page.name not in self.excludepages:
				yield page

	@staticmethod
	def _GetParamPage(comp, pagename):
		for page in comp.customPages:
			if page.name == pagename:
				return page

	def _GetPageParamTuplets(self, comp, page=None, pagename=None):
		if pagename and not page:
			page = self._GetParamPage(comp, pagename)
		if not page:
			return []
		return page.parTuplets

	def GetModuleParamGroups(self, comp, params):

		pass

	def BuildModuleSchema(self, comp):
		key = self.GetModuleKey(comp)
		path = self.GetModulePath(comp)
		params = self.BuildModuleParamSchemas(comp)

		module = schema.ModuleSpec(
			key=self.key,
			label=self.GetModuleLabel(comp),
			path=path,
			moduletype=self.GetModuleType(comp),
			group=self.GetModuleGroup(comp),
			tags=self.GetModuleTags(comp),
			params=params,
			paramgroups=self.GetModuleParamGroups(comp, params),
		)
		pass

	def GetParameterTags(self, comp, partuplet):
		return []

	def GetChildModules(self, comp):
		return []

	def GetChildModuleGroups(self, comp):
		return []


