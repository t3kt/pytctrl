import xml.etree.ElementTree as ET
from tctrl.schema import *
import sys

#
# Example osc mappings
# /layer1/video/opacity/values
# /layer1/video/effect1/bypassed
# /composition/link1/values: float 0-1
# /layer1/video/effect1/opacity/values (Float 0.0 - 1.0)
# /layer1/video/effect1/mixer (Int 0 to 47)
# /layer1/video/scale/values (Float 0.0 - 1.0) range (0.0 - 1000.0)
# /activelayer/video/rotatex/values (Float 0.0 - 1.0) range (-180.0 - 180.0)
# /composition/video/effect5/opacity/values (Float 0.0 - 1.0)
# /composition/video/effect5/param1/values (Float 0.0 - 1.0)
# /composition/video/effect5/param2/values (Float 0.0 - 1.0)
#

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

	def _ConvertCompositionMaster(self, compositionelem: ET.Element):
		pass

	def _ConvertLayer(self, layerelem: ET.Element):
		layernum = int(layerelem.attrib['layerIndex'])
		layerkey = 'layer%d' % layernum
		layerpath = '/layer%d' % layernum
		module = ModuleSpec(
			layerkey,
			label=layerkey,
			path=layerpath,
			moduletype='layer',
			children=[],
			params=[],
		)
		module.params.append(
			self._BypassedParam(
				layerelem.find('./settings/bypassed'),
				modulepath=layerpath))
		module.params.append(
			ParamSpec(
				'solo',
				label='Solo',
				ptype=ParamType.bool,
				path='%s/solo' % layerpath,
				defaultval=False,
				value=layerelem.find('./settings/solo').attrib('value') != '0'
			))
		effects = layerelem.findall('./videoLayer/effects/effect')
		for i, effect in enumerate(effects):
			module.children.append(
				self._ConvertEffect(
					effect,
					path='%s/effect%d' % (layerpath, (i + 1)),
					key='effect%d' % (i + 1),
				))
		# ...
		return module

	def _BypassedParam(self, bypassedelem: ET.Element, modulepath: str):
		return ParamSpec(
			'bypass',
			label='Bypass',
			path='%s/bypassed/values' % modulepath,
			defaultval=False,
			value=bypassedelem.attrib['value'] != '0',
		)

	def _OpacityParam(self, paramelem: ET.Element, modulepath: str):
		# TODO: stuff...?
		return ParamSpec(
			'opacity',
			label='Opacity',
			path='%s/opacity/values' % modulepath,
			defaultval=1
		)

	def _ConvertEffect(self, effectelem: ET.Element, path : str, key : str):
		module = ModuleSpec(
			key,
			path=path,
			label=effectelem.attrib['name'],
			# moduletype ?
			params=[
				self._BypassedParam(effectelem.find('./bypassed'), modulepath=path),
			],
		)
		for paramelem in effectelem.findall('./parameter'):
			paramkey = paramelem.find('./name').attrib['value']
			if paramkey == 'Opacity':
				module.params.append(self._OpacityParam(paramelem, modulepath=path))
			else:
				module.params.append(
					self._ConvertParameter(
						paramelem,
						path=path + '/' + paramkey,
						key=paramkey))
		# ...
		return module

	def _ConvertParameter(self, paramelem: ET.Element, path: str, key: str):
		pass

def main(args):
	compfilepath = args[1]
	root = ET.parse(compfilepath)
	converter = ResolumeConverter(root)
	schema = converter.ConvertToSchema()
	schemajson = schema.ToJson(indent='  ')
	print(schemajson)

if __name__ == '__main__':
	main(sys.argv)
