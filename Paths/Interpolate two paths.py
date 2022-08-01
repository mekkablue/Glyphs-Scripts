#MenuTitle: Interpolate two paths
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Select two paths and run this script, it will replace them with their interpolation at 50%.
"""

Font = Glyphs.font

if not Font:
	Message("You need to open a glyph in a font and select two paths for this script.", title='No font open', OKButton="Hachoo")
else:
	Layer = Font.selectedLayers[0]
	interpolatablePaths = []
	for path in Layer.paths:
		if path.selected:
			interpolatablePaths.append(path)

	if len(interpolatablePaths) == 2:
		path1, path2 = interpolatablePaths
		if len(path1.nodes) != len(path2.nodes):
			Message("The two paths you selected do not have the same number of points.", title='Incompatible Paths', OKButton="Duh")
		else:
			if distance(path1.nodes[0].position, path2.nodes[-1].position) < distance(path1.nodes[0].position, path2.nodes[0].position):
				path2.reverse()
			tempGlyph = GSGlyph()
			layerA, layerB = GSLayer(), GSLayer()
			layerA.shapes.append(path1.__copy__())
			layerB.shapes.append(path2.__copy__())
			tempGlyph.layers = [layerA, layerB]
			tempLayer = tempGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
											[layerA, layerB], 
											{
												layerA.layerId:0.5,
												layerB.layerId:0.5,
											}, 
											None, False, Font, None)
			if len(tempLayer.shapes) == 1:
				for i in range(len(Layer.shapes)-1,-1,-1):
					if Layer.shapes[i].selected and type(Layer.shapes[i])==GSPath:
						del Layer.shapes[i]
				Layer.shapes.append(tempLayer.paths[0].__copy__())
			else:
				Message("Could not interpolate the two paths.", title='No interpolation possible', OKButton="Darn")
	else:
		Message("You need to select exactly two paths to interpolate.", title='Wrong number of paths selected', OKButton="Oh well")