import pythonosc.udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
from tctrl.model import *
from tctrl.schema import *
from tctrl.util import FillToLength

class OscAccessor(Accessor):
	def __init__(self, address, port):
		super().__init__()
		self.client = pythonosc.udp_client.UDPClient(address, port)

	def SetParam(self, param, value):
		super().SetParam(param, value)
		message = self._BuildSetParamMessage(param, value)
		if message is not None:
			self.client.send(message)

	def _BuildSetParamMessage(self, param, value):
		message = OscMessageBuilder(address=param.path)
		for argval, argtype in self._BuildSetParamArgs(param, value):
			message.add_arg(argval, argtype)
		return message

	def _BuildSetParamArgs(
			self,
			param : ParamModel,
			value):
		if param.ptype == ParamType.bool:
			return [(value, None)]
		elif param.ptype == ParamType.string or param.ptype == ParamType.menu:
			return [(value, OscMessageBuilder.ARG_TYPE_STRING)]
		elif param.ptype == ParamType.int:
			return [(value, OscMessageBuilder.ARG_TYPE_INT)]
		elif param.ptype == ParamType.float:
			return [(value, OscMessageBuilder.ARG_TYPE_FLOAT)]
		elif param.ptype == ParamType.ivec:
			vals = FillToLength(value, param.length)
			return [(val, OscMessageBuilder.ARG_TYPE_INT) for val in vals]
		elif param.ptype == ParamType.fvec:
			vals = FillToLength(value, param.length)
			return [(val, OscMessageBuilder.ARG_TYPE_FLOAT) for val in vals]
		elif param.ptype == ParamType.trigger:
			return [(1, OscMessageBuilder.ARG_TYPE_INT)]
		return []

class RemoteNode:
	def __init__(self, key, path):
		self.key = key
		self.path = path

class ModuleRemote:
	def __init__(self, schema, sender):
		self.schema = schema
		self.sender = sender
		pass

class _ModulePars:
	def __init__(self, schema, sender):
		self._schema = schema
		self._sender = sender

	def __setattr__(self, key, value):
		pass

class AppRemote:
	def __init__(self, sender):
		self._schema = None
		self._sender = sender
