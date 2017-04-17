import xml.etree.ElementTree as ET
from tctrl.schema import *
import sys
from bs4 import BeautifulSoup

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

class ResolumeSoupConverter:
	def __init__(self, compfilepath):
		self.soup = BeautifulSoup(open(compfilepath), 'xml')

	def ConvertToSchema(self):
		compname = self.soup.composition.generalInfo['name']
		key = compname.replace(' ', '')
		app = AppSchema(
			key=key,
			label=compname,
			tags=['resolume'],
		)
		app.children.append(self._BuildCompositionMaster(self.soup.composition))
		for layer in self.soup.composition.find_all('layer', recursive=False):
			app.children.append(self._BuildLayer(layer))
		return app

	def _BuildCompositionMaster(self, composition: BeautifulSoup):
		module = ModuleSpec(
			'composition',
			label='Composition Master',
			moduletype='composition',
			path='/composition'
		)
		return module

	def _BuildLayer(self, layer: BeautifulSoup):
		layerIndex = int(layer['layerIndex'])
		module = ModuleSpec(
			'layer%d' % layerIndex,
			label=layer.settings.find('name', recursive=False)['value'],
			path='/layer%d' % layerIndex,
			moduletype='layer',
		)
		effects = layer.effects
		if effects is not None:
			for i, effect in enumerate(effects.find_all('effect', recursive=False)):
				module.children.append(self._BuildEffect(effect, 'effect%d' % (i + 1), basepath=module.path + '/'))
		return module

	def _BuildEffect(self, effect: BeautifulSoup, key: str, basepath: str):
		module = ModuleSpec(
			key,
			path=basepath + key,
			label=effect['name'],
			moduletype=effect['fileName'],
		)
		return module


class ResolumeConverter:
	def __init__(self, compfilepath):
		self.root = ET.parse(compfilepath).getroot()

	def ConvertToSchema(self):
		compname = self.root.findtext('generalInfo/@name')
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
		path = 'composition'
		module = ModuleSpec(
			'master',
			label='Composition Master',
			moduletype='composition',
			path=path,
		)
		effects = compositionelem.findall('./videoEngine/effects/effect')
		for i, effect in enumerate(effects):
			module.children.append(self._ConvertEffect(effect, path, 'effect%d' % i))
		return module

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
		param = ParamSpec(
			key,
			label=paramelem.findtext('./nameGiven/@value'),
			ptype=ParamType.float,
			path=path,
			minnorm=float(paramelem.findtext('./values/@startValue', default='0')),
			maxnorm=float(paramelem.findtext('./values/@endValue', default='1')),
			defaultval=float(paramelem.findtext('./values/@defaultValue', default='0')),
			value=float(paramelem.findtext('./values/@curValue', default='0')),
		)
		return param

def main(args):
	compfilepath = args[1]
	converter = ResolumeSoupConverter(compfilepath)
	schema = converter.ConvertToSchema()
	schemajson = schema.ToJson(indent='  ')
	print(schemajson)

if __name__ == '__main__':
	main(sys.argv)
