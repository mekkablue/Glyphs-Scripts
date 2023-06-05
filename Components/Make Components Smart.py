#MenuTitle: Make Components Smart in All Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Turn the selected components into smart components, based on the axes defined in the font.
"""

# clears macro window log:
Glyphs.clearLog()

font = Glyphs.font
fontAxisValues = [m.axes[i] for m in font.masters]
selectedLayers = font.selectedLayers
if len(selectedLayers) > 1:
	batchProcess = True
else:
	batchProcess = False

processedGlyphs = []
for selectedLayer in selectedLayers:
	selectedGlyph = selectedLayer.parent
	print(f"Processing {selectedGlyph.name}...")
	for compIndex, component in enumerate(selectedLayer.components):
		if component.selected or batchProcess:
			originalGlyph = font.glyphs[component.name]

			# Check if component is already smart
			if not originalGlyph.smartComponentAxes:
				for i in range(len(font.axes)):
					newAxis = GSSmartComponentAxis()
					newAxis.name = font.axes[i].name
					# newAxis.axisTag = font.axes[i].axisTag
					newAxis.bottomValue = min(fontAxisValues)
					newAxis.topValue = max(fontAxisValues)
					originalGlyph.smartComponentAxes.append(newAxis)
					for layer in originalGlyph.layers:
						if layer.isMasterLayer:
							if font.masters[layer.associatedMasterId].axes[i] == newAxis.bottomValue:
								layer.smartComponentPoleMapping[originalGlyph.smartComponentAxes[newAxis.name].id] = 1
							if font.masters[layer.associatedMasterId].axes[i] == newAxis.topValue:
								layer.smartComponentPoleMapping[originalGlyph.smartComponentAxes[newAxis.name].id] = 2
								
			# Reset axis values, so they can be accessed:
			for layer in selectedGlyph.layers:
				if layer.isMasterLayer:
					for i in range(len(font.axes)):
						component = layer.components[compIndex]
						interpolationValue = layer.associatedFontMaster().axes[i]
						component.smartComponentValues[originalGlyph.smartComponentAxes[i].id] = interpolationValue
			
			# Renew selection in order to show smart glyph controls
			if not batchProcess:
				for b in range(2):
					component.selected = bool(b)
		
			processedGlyphs.append(originalGlyph.name)

if processedGlyphs:
	print(f'{", ".join(processedGlyphs)} are now smart glyphs.')
else:
	print("No glyphs changed.")