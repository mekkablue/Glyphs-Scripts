#MenuTitle: Convert RTL Kerning from Glyphs 2 to 3
from __future__ import division, print_function, unicode_literals
__doc__="""
Convert RTL kerning from Glyphs 2 to Glyphs 3 format and switches the kerning classes. (Hold down OPTION and SHIFT to convert from Glyphs 3 back to Glyphs 2.) Detailed report in Macro Window.
"""

from GlyphsApp import objcObject, RTL
from AppKit import NSEvent
from Foundation import NSMutableDictionary
thisFont = Glyphs.font

# see which keys are pressed:
keysPressed = NSEvent.modifierFlags()
optionKey, shiftKey = 524288, 131072
optionKeyPressed = keysPressed & optionKey == optionKey
shiftKeyPressed = keysPressed & shiftKey == shiftKey
convertFrom3to2 = optionKeyPressed and shiftKeyPressed

ExportClass = NSClassFromString("GSExportInstanceOperation")
exporter = ExportClass.new()
exporter.setFont_(thisFont)
key2Scripts = {}
exporter._makeKey2Scripts_splitGroups_GroupDict_error_(key2Scripts, None, {}, None)

def nameForKey(thisKey):
	if thisKey.startswith("@"):
		return thisKey
	else:
		return thisFont.glyphForId_(thisKey).name

# brings macro window to front and clears its log:
Glyphs.clearLog()
print("1️⃣ Convert RTL kerning from Glyphs %i → %i:" % (
	3 if convertFrom3to2 else 2,
	2 if convertFrom3to2 else 3,
	))

def copyFrom3to2(masterKerning, RTLmasterKerning):
	for firstKey in RTLmasterKerning.allKeys():
		firstName = nameForKey(firstKey)
		if GSGlyphsInfo.isRTLScript_(key2Scripts[firstName]):
			newFirstKey = firstKey.replace("@MMK_R_", "@MMK_L_")
			newFirstKerning = {}
			firstKerning = RTLmasterKerning[firstKey]
			for secondKey in firstKerning.allKeys():
				newSecondKey = secondKey.replace("@MMK_L_", "@MMK_R_")
				kernValue = firstKerning[secondKey]
				thisFont.setKerningForPair(master.id, nameForKey(newFirstKey), nameForKey(newSecondKey), kernValue)
				print("  ✅ %s %s %i" % (
					nameForKey(newFirstKey).replace("MMK_L_",""),
					nameForKey(newSecondKey).replace("MMK_R_",""),
					kernValue,
				))
			del(RTLmasterKerning[firstKey])
		else:
			print("  ⚠️ Cannot convert RTL kerning with %s to G2; not an RTL %s." % (
				firstName.replace("MMK_L_",""),
				"group" if firstName.startswith("@") else "glyph", 
			))

def copyFrom2to3(masterKerning, RTLmasterKerning):
	for firstKey in masterKerning.allKeys():
		firstName = nameForKey(firstKey)
		if firstName not in key2Scripts:
			continue
		if GSGlyphsInfo.isRTLScript_(key2Scripts[firstName]):
			firstKerning = masterKerning[firstKey]
			newFirstKey = firstKey.replace("@MMK_L_", "@MMK_R_")
			newFirstKerning = {}
			RTLmasterKerning[newFirstKey] = newFirstKerning
			for secondKey in firstKerning.allKeys():
				newSecondKey = secondKey.replace("@MMK_R_", "@MMK_L_")
				kernValue = firstKerning[secondKey]
				newFirstKerning[newSecondKey] = kernValue
				print("  ✅ %s %s %i" % (
					nameForKey(newFirstKey).replace("MMK_R_",""),
					nameForKey(newSecondKey).replace("MMK_L_",""),
					kernValue,
				))
			del(masterKerning[firstKey])

# copy RTL kerning and swith class prefixes in kern dict
for master in thisFont.masters:
	print("\n🔠 Master: %s" % master.name)
	RTLMasterKerning = thisFont.kerningRTL.get(master.id, None)
	if RTLMasterKerning is None:
		RTLMasterKerning = NSMutableDictionary.new()
		thisFont.kerningRTL[master.id] = RTLMasterKerning
	
	masterKerning = thisFont.kerning.get(master.id, None)
	if not masterKerning:
		print("  No convertible kerning found in this master.")
		continue
	if convertFrom3to2:
		copyFrom3to2(masterKerning, RTLMasterKerning)
	else:
		copyFrom2to3(masterKerning, RTLMasterKerning)

# Switch kerning classes in glyphs
print("\n2️⃣ Switching kern classes of RTL glyphs:")
for g in thisFont.glyphs:
	if g.direction == RTL:
		rightClass = g.rightKerningGroup
		leftClass = g.leftKerningGroup
		g.rightKerningGroup = leftClass
		g.leftKerningGroup = rightClass
		print("  ↔️ %s   ◀️ %s  ▶️ %s" % (
			g.name,
			g.leftKerningGroup,
			g.rightKerningGroup,
		))
		
