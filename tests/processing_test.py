import unittest
from tctrl.schema import *
from tctrl.processing import ProcessAppSchema

stuff_list = OptionList(
	'stuff',
	label='Stuff',
	options=[
		ParamOption('abc', 'ABC'),
		ParamOption('def', 'DEF'),
		ParamOption('xyz', 'XYZ'),
	]
)

things_list = OptionList(
	'things',
	label='Things',
	options=[
		ParamOption('zzzabc', 'zzzABC'),
		ParamOption('zzzdef', 'zzzDEF'),
		ParamOption('zzzxyz', 'zzzXYZ'),
	]
)

class ProcessingTest(unittest.TestCase):

	def test_noop(self):
		inputschema = AppSchema(
			'test',
			optionlists=[
				stuff_list,
				things_list
			],
			children=[
				ModuleSpec(
					'foo1',
					label='Foo 1',
					params=[
						ParamSpec(
							'stuff1',
							label='Stuff 1',
							ptype=ParamType.menu,
							optionlist='stuff',
						),
						ParamSpec(
							'nonmenu',
							label='Non menu',
							ptype=ParamType.float,
						)
					]
				)
			],
		)
		expectedschema = AppSchema(
			'test',
			optionlists=[
				stuff_list,
				things_list
			],
			children=[
				ModuleSpec(
					'foo1',
					label='Foo 1',
					params=[
						ParamSpec(
							'stuff1',
							label='Stuff 1',
							ptype=ParamType.menu,
							optionlist='stuff',
						),
						ParamSpec(
							'nonmenu',
							label='Non menu',
							ptype=ParamType.float,
						)
					]
				)
			],
		)
		self.assertEqual(
			ProcessAppSchema(inputschema),
			expectedschema)

	def test_embedlists(self):
		inputschema = AppSchema(
			'test',
			optionlists=[
				stuff_list,
				things_list
			],
			children=[
				ModuleSpec(
					'foo1',
					label='Foo 1',
					params=[
						ParamSpec(
							'stuff1',
							label='Stuff 1',
							ptype=ParamType.menu,
							optionlist='stuff',
						),
						ParamSpec(
							'nonmenu',
							label='Non menu',
							ptype=ParamType.float,
						)
					]
				)
			],
		)

		expected = AppSchema(
			'test',
			children=[
				ModuleSpec(
					'foo1',
					label='Foo 1',
					params=[
						ParamSpec(
							'stuff1',
							label='Stuff 1',
							ptype=ParamType.menu,
							optionlist='stuff',
							options=[
								ParamOption('abc', 'ABC'),
								ParamOption('def', 'DEF'),
								ParamOption('xyz', 'XYZ'),
							],
						),
						ParamSpec(
							'nonmenu',
							label='Non menu',
							ptype=ParamType.float,
						)
					]
				)
			],
		)

		self.assertEqual(
			ProcessAppSchema(inputschema, embedlists=True),
			expected)

if __name__ == '__main__':
	unittest.main()
