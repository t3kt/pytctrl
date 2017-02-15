

def FillToLength(vals, length=None):
	length = length or 1
	if vals is None or len(vals) == 0:
		return [None] * length
	if not isinstance(vals, list):
		return [vals] * length
	if len(vals) >= length:
		return vals[:length]
	return [
		vals[i if i < len(vals) else -1]
		for i in range(length)
	]

def CleanDict(d):
	for k in list(d.keys()):
		if d[k] is None or d[k] == '':
			del d[k]
	return d

def MergeDicts(*parts):
	if parts is None:
		return {}
	d = {}
	for part in parts:
		if part:
			d.update(part)
	return d

def GetByKey(items, key):
	if not items:
		return None
	for item in items:
		if item.key == key:
			return item
