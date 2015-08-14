import json

obj = json.load(open("finalLED_s.json"))

yGroups = []

# def group_y(moire):
# 	for i in range(0, len(moire)):
# 		for j in range(len(moire), i):
# 			if get_y(moire[i]) != get_y(moire[j]):


def getKey(item):
	return item.point[0]

def gex_y(point):
	return point.point[1]

[list(g) for k, g in itertools.groupby(sorted(obj, get_y))]
