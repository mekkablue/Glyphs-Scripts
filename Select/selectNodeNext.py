#MenuTitle: Select following on-curve point
# -*- coding: utf-8 -*-
__doc__="""
From the currently selected point, go to the next on-curve.
"""

def getTheFirstPoint(selection):
	for thisItem in selection:
		if type(thisItem) == GSNode:
			return thisItem
	return None

def nextOnCurve(currPoint):
	nextPoint = currPoint.nextNode
	if nextPoint.type != "offcurve":
		return nextPoint
	else:
		return nextOnCurve(nextPoint)

def prevOnCurve(currPoint):
	prevPoint = currPoint.prevNode
	if prevPoint.type != "offcurve":
		return prevPoint
	else:
		return prevOnCurve(prevPoint)

def main():
	currentLayer = Glyphs.font.selectedLayers[0] # active layers of selected glyphs
	selection = currentLayer.selection # node selection in edit mode
	currentPoint = getTheFirstPoint(selection)
	if currentPoint:
		nextOnCurveNode = nextOnCurve(currentPoint)
		currentLayer.selection = (nextOnCurveNode,)

if __name__ == "__main__":
	# execute only if run as a script
	main()

