# MenuTitle: Convert RTL Kerning from Glyphs 2 to 3
from __future__ import division, print_function, unicode_literals
__doc__ = """
Convert RTL kerning from Glyphs 2 to Glyphs 3 format and switches the kerning classes. Detailed report in Macro Window.

Hold down OPTION and SHIFT to convert from Glyphs 3 back to Glyphs 2.
"""

from AppKit import NSEvent
from Foundation import NSMutableDictionary, NSClassFromString
from GlyphsApp import Glyphs, GSGlyphsInfo

Glyphs.clearLog()

try:
	from GlyphsApp import GSRTL as RTL
except:
	from GlyphsApp import RTL


def nameForKey(thisKey):
	if thisKey.startswith("@"):
		return thisKey
	else:
		return thisFont.glyphForId_(thisKey).name


def glyphNameIsRTL(glyphName, key2Scripts):
	# glyphName = flipMMK(glyphName)  # @MMK_L_flipMMK -->  @MMK_R_ --> glyphName = Glyphs.niceGlyphName(glyphNam
	flippedName = flipMMK(glyphName)
	if glyphName in key2Scripts.keys():
		if GSGlyphsInfo.isRTLScript_(key2Scripts[glyphName]):
			return True
	elif flippedName in key2Scripts.keys():
		if GSGlyphsInfo.isRTLScript_(key2Scripts[flippedName]):
			return True
	return False


def glyphInFontIsRTL(glyphName, thisFont, key2Scripts):
	glyph = thisFont.glyphs[glyphName]
	if glyph:
		if glyph.direction == RTL or GSGlyphsInfo.isRTLScript_(glyph.script):
			return True
	return glyphNameIsRTL(glyphName, key2Scripts)


def stripMMK(name):
	return name.replace("MMK_L_", "").replace("MMK_R_", "")


def flipMMK(name):
	left = "@MMK_L_"
	right = "@MMK_R_"
	if name.startswith(left):
		return name.replace(left, right)
	elif name.startswith(right):
		return name.replace(right, left)
	else:
		return name


def copyFrom3to2(thisFont, masterKerning, RTLmasterKerning, key2Scripts):
	countKernPairs = 0
	for firstKey in list(RTLmasterKerning.keys()):
		firstKerning = RTLmasterKerning[firstKey]
		newFirstKerning = {}

		firstName = nameForKey(firstKey)
		if glyphInFontIsRTL(firstName, thisFont, key2Scripts):
			newFirstKey = flipMMK(firstKey)  # @MMK_R_ --> @MMK_L_

		for secondKey in firstKerning.keys():
			secondName = nameForKey(secondKey)
			if glyphInFontIsRTL(secondName, thisFont, key2Scripts):
				newSecondKey = flipMMK(secondKey)  # @MMK_L_ --> @MMK_R_

			kernValue = firstKerning[secondKey]
			thisFont.setKerningForPair(master.id, stripMMK(firstName), stripMMK(secondName), kernValue)
			print("  ✅ %s %s %i" % (
				stripMMK(firstName),
				stripMMK(secondName),
				kernValue,
			))
			countKernPairs += 1

	RTLmasterKerning = {}  # delete RTL kerning
	return countKernPairs


def copyFrom2to3(masterKerning, RTLmasterKerning, key2Scripts):
	countKernPairs = 0
	toBeDeleted = []
	for firstKey in masterKerning.keys():
		firstKeyIsRTL = False

		# check if first key is RTL
		firstName = nameForKey(firstKey)
		if glyphNameIsRTL(firstName, key2Scripts):
			firstKeyIsRTL = True

		firstKerning = masterKerning[firstKey]
		newFirstKey = flipMMK(firstKey)  # @MMK_L_ --> @MMK_R_
		newFirstKerning = {}

		for secondKey in firstKerning.keys():
			secondKeyIsRTL = False
			# check if second key is RTL
			if not firstKeyIsRTL:
				secondName = nameForKey(secondKey)
				if glyphNameIsRTL(secondName, key2Scripts):
					secondKeyIsRTL = True

			# if either is RTL, convert to RTL kerning:
			if firstKeyIsRTL or secondKeyIsRTL:
				if newFirstKey not in RTLmasterKerning.keys():
					RTLmasterKerning[newFirstKey] = newFirstKerning
				newSecondKey = flipMMK(secondKey)  # @MMK_R_ --> @MMK_L_
				kernValue = firstKerning[secondKey]
				RTLmasterKerning[newFirstKey][newSecondKey] = kernValue
				print("  ✅ %s %s %i" % (
					stripMMK(nameForKey(newFirstKey)),  # remove MMK_R_
					stripMMK(nameForKey(newSecondKey)),  # remove MMK_L_
					kernValue,
				))
				countKernPairs += 1
				delPair = (firstKey, secondKey)

				if secondKeyIsRTL:
					if delPair not in toBeDeleted:
						toBeDeleted.append(delPair)

		if firstKeyIsRTL:
			delPair = (firstKey, None)
			toBeDeleted.append(delPair)

	# delete converted LTR pairs:
	for delPair in toBeDeleted:
		firstKey, secondKey = delPair
		if firstKey in masterKerning.keys():
			if secondKey is None:
				del (masterKerning[firstKey])
			elif secondKey in masterKerning[firstKey].keys():
				del (masterKerning[firstKey][secondKey])

	return countKernPairs


def mapGlyphsToScripts(thisFont):
	glyph2script = {}
	ExportClass = NSClassFromString("GSExportInstanceOperation")
	exporter = ExportClass.new()
	exporter.setFont_(thisFont)
	if Glyphs.versionNumber < 3.1:
		exporter._makeKey2Scripts_splitGroups_GroupDict_error_(glyph2script, None, {}, None)
	else:
		exporter._makeCachesKey2Scripts_splitGroups_groupDict_glyphsID2Glyph_name2Glyph_error_(glyph2script, None, {}, None, None, None)
	return glyph2script


try:
	# see which keys are pressed:
	keysPressed = NSEvent.modifierFlags()
	optionKey, shiftKey = 524288, 131072
	optionKeyPressed = keysPressed & optionKey == optionKey
	shiftKeyPressed = keysPressed & shiftKey == shiftKey
	userWantsToConvertFrom3to2 = optionKeyPressed and shiftKeyPressed

	# map glyphs to scripts for the current font:
	thisFont = Glyphs.font
	glyph2scriptMapping = mapGlyphsToScripts(thisFont)

	# prepare Macro Window logging:
	Glyphs.clearLog()
	conversionDirection = "%i → %i:" % (
		3 if userWantsToConvertFrom3to2 else 2,
		2 if userWantsToConvertFrom3to2 else 3,
	)

	# copy RTL kerning and swith class prefixes in kern dict
	print("1️⃣ Convert RTL kerning from Glyphs %s" % conversionDirection)
	countKernPairs = 0
	for master in thisFont.masters:
		print("\n  🔠 Master: %s" % master.name)
		RTLMasterKerning = thisFont.kerningRTL.get(master.id, None)
		if RTLMasterKerning is None:
			RTLMasterKerning = NSMutableDictionary.new()
			thisFont.kerningRTL[master.id] = RTLMasterKerning

		masterKerning = thisFont.kerning.get(master.id, None)
		if userWantsToConvertFrom3to2:
			countKernPairs = copyFrom3to2(thisFont, masterKerning, RTLMasterKerning, glyph2scriptMapping)
		else:
			if not masterKerning:
				print("  No kerning found in this master.")
				continue
			countKernPairs = copyFrom2to3(masterKerning, RTLMasterKerning, glyph2scriptMapping)
			if thisFont.formatVersion != 3:
				thisFont.formatVersion = 3
				print("✅ Font Info > Other > File Format: switched to 3")

	# Switch kerning groups in glyphs:
	print("\n2️⃣ Flipping kerning groups for RTL glyphs:")
	countFlippedGroups = 0
	for g in thisFont.glyphs:
		if g.direction == RTL and (g.rightKerningGroup or g.leftKerningGroup) and g.rightKerningGroup != g.leftKerningGroup:
			countFlippedGroups += 1
			rightGroup = g.rightKerningGroup
			leftGroup = g.leftKerningGroup
			g.rightKerningGroup = leftGroup
			g.leftKerningGroup = rightGroup
			print("  ↔️ %s   ◀️ %s  ▶️ %s" % (
				g.name,
				g.leftKerningGroup,
				g.rightKerningGroup,
			))

	print("\n✅ Done.")
	# Floating notification:
	Glyphs.showNotification(
		"RTL kerning %s for %s" % (conversionDirection, thisFont.familyName),
		"Converted %i pair%s, flipped groups in %i glyph%s. Details in Macro Window." % (
			countKernPairs,
			"" if countKernPairs == 1 else "s",
			countFlippedGroups,
			"" if countFlippedGroups == 1 else "s",
		),
	)


except Exception as e:
	Glyphs.showMacroWindow()
	import traceback
	print(traceback.format_exc())
