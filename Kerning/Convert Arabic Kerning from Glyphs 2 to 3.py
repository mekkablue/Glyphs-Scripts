#MenuTitle: Convert Arabic Kerning from Glyphs 2 to 3
from __future__ import division, print_function, unicode_literals
__doc__="""
Convert RTL kerning from Glyphs2 to Glyphs3 format and switches the kerning classes
"""

from GlyphsApp import objcObject

# copy RTL kerning and swith class prefixes in kern dict
ExportClass = NSClassFromString("GSExportInstanceOperation")
exporter = ExportClass.new()
exporter.setFont_(Font)
key2Scripts = {}
exporter._makeKey2Scripts_splitGroups_GroupDict_error_(key2Scripts, None, {}, None)

for master in Font.masters:
	RTLMasterKerning = Font.kerningRTL[master.id]
	if RTLMasterKerning is None:
		RTLMasterKerning = {}
		Font.kerningRTL[master.id] = objcObject(RTLMasterKerning)
	masterKerning = Font.kerning[master.id]
	for firstKey in masterKerning.allKeys():
		firstKerning = masterKerning[firstKey]
		if firstKey.startswith("@"):
			firstName = firstKey
		else:
			firstName = Font.glyphForId_(firstKey).name
		if GSGlyphsInfo.isRTLScript_(key2Scripts[firstName]):
			newFirstKey = firstKey.replace("@MMK_L_", "@MMK_R_")
			newFirstKerning = {}
			RTLMasterKerning[newFirstKey] = newFirstKerning
			for secondKey in firstKerning.allKeys():
				newSecondKey = secondKey.replace("@MMK_R_", "@MMK_L_")
				kernValue = firstKerning[secondKey]
				newFirstKerning[newSecondKey] = kernValue
			del(masterKerning[firstKey])

# Switch kerning classes in glyphs
for g in Font.glyphs:
	if g.direction == RTL:
		rightClass = g.rightKerningGroup
		leftClass = g.leftKerningGroup
		g.rightKerningGroup = leftClass
		g.leftKerningGroup = rightClass
