from tctrl.util import MergeDicts

_defaultTemplate = {
	"fileversion": 1,
	"appversion": {
		"major": 7,
		"minor": 3,
		"revision": 4,
		"architecture": "x64",
		"modernui": 1
	},
	"rect": [264.0, 283.0, 640.0, 480.0],
	"bglocked": 0,
	"openinpresentation": 0,
	"default_fontsize": 12.0,
	"default_fontface": 0,
	"default_fontname": "Arial",
	"gridonopen": 1,
	"gridsize": [15.0, 15.0],
	"gridsnaponopen": 1,
	"objectsnaponopen": 1,
	"statusbarvisible": 2,
	"toolbarvisible": 1,
	"lefttoolbarpinned": 0,
	"toptoolbarpinned": 0,
	"righttoolbarpinned": 0,
	"bottomtoolbarpinned": 0,
	"toolbars_unpinned_last_save": 0,
	"tallnewobj": 0,
	"boxanimatetime": 200,
	"enablehscroll": 1,
	"enablevscroll": 1,
	"devicewidth": 0.0,
	"description": "",
	"digest": "",
	"tags": "",
	"style": "",
	"subpatcher_template": "",
	"autosave": 0,
}


class MaxPatchBuilder:
	def __init__(
			self,
			appversion=None,
			rect=None,
			openinpresentation=True,
			template=None):
		self.appversion = appversion
		self.rect = rect
		self.openinpresentation = openinpresentation
		self.objectidgen = _IdGenerator('obj-')
		self.boxes = {}
		self.lines = []
		self.template = template if template is not None else _defaultTemplate

	def AddBox(self, **box):
		if not box.get('id'):
			box['id'] = self.objectidgen.Next()
		self.boxes[box['id']] = box
		return box

	def AddLine(self, srcid, srcindex, destid, destindex):
		self.lines.append({
			'destination': [destid, destindex],
			'source': [srcid, srcindex],
		})

	def Build(self):
		return MergeDicts(self.template, {
			'appversion': self.appversion,
			'rect': self.rect,
			'openinpresentation': self.openinpresentation,
			'boxes': [{'box': dict(box)} for box in self.boxes.values()],
			'lines': [{'patchline': dict(line) for line in self.lines}],
		})


class _IdGenerator:
	def __init__(self, prefix):
		self.prefix = prefix
		self.i = 0

	def Next(self):
		self.i += 1
		return '%s%d' % (self.prefix, self.i)

def JParameter(
		name,
		type,
		value=None,
		description=None,
		clipmode=None,
		dataspace=None, priority=None):
	pass
