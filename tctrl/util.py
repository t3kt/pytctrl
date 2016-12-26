

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
