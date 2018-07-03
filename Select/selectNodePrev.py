#MenuTitle: Select previous on-curve point
# -*- coding: utf-8 -*-
__doc__="""
From the currently selected point, go to the previous on-curve.
"""

import selectNodeNext

def main():
	currentLayer = Glyphs.font.selectedLayers[0] # active layers of selected glyphs
	selection = currentLayer.selection # node selection in edit mode
	currentPoint = getTheFirstPoint(selection)
	if currentPoint:
		prevOnCurveNode = prevOnCurve(currentPoint)
		currentLayer.selection = (prevOnCurveNode,)

if __name__ == "__main__":
	# execute only if run as a script
	main()

