import xml.etree.ElementTree as ET
from tctrl.schema import *

class ResolumeConverter:
	def __init__(self, root: ET.ElementTree):
		self.root = root

	def ConvertToSchema(self):
		compname = self.root.find('./composition/generalInfo').attrib['name']
		app = AppSchema(
			key=compname,
			label=compname,
			tags=['resolume'],
			children=[],
		)
		app.children.append(self._ConvertCompositionMaster(self.root.find('./composition')))
		for layer in self.root.findall('./composition/layer'):
			app.children.append(self._ConvertLayer(layer))
		# ...
		return app

	def _ConvertCompositionMaster(self, element: ET.Element):
		pass

	def _ConvertLayer(self, element: ET.Element):
		module = ModuleSpec(
			'',
			children=[],
		)
		effects = element.findall('./videoLayer/effects/effect')
		for effect in effects:
			module.children.append(self._ConvertEffect(effect))
		# ...
		return module

	def _ConvertEffect(self, element: ET.Element):
		module = ModuleSpec(
			'',
		)
		# ...
		return module

	def _ConvertParameter(self, element: ET.Element):
		pass
