# MenuTitle: Create Pseudorandom calt Feature from ssXX Glyphs
__doc__ = """
Create pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font.
"""

from mekkablue import createOTFeature, createOTClass
from GlyphsApp import Glyphs


lineLength = 70
addDefault = True
featureName = "calt"
classNamePrefix = featureName


def ssXXsuffix(i):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	returnString = ""
	if i > 0 and i <= 20:
		returnString = ".ss%02i" % i
	return returnString


def highestStylisticSetInNameList(nameList):
	ssXX_exists = True
	i = 1
	while ssXX_exists:
		ssXX = ssXXsuffix(i)
		ssXXglyphs = [x for x in nameList if x.find(ssXX) != -1]
		if len(ssXXglyphs) == 0:
			i -= 1
			ssXX_exists = False
		else:
			i += 1
	return i


thisFont = Glyphs.font
if not thisFont:
	print("Please open a font first.")
else:
	allGlyphs = [x.name for x in list(thisFont.glyphs)]
	highestSetNumber = highestStylisticSetInNameList(allGlyphs)
	ssXX = ssXXsuffix(highestSetNumber)

	if not ssXX:
		print("No ssXX glyphs in the thisFont. Aborting.")
	else:
		ssXXglyphs = [x for x in allGlyphs if x.find(ssXX) > -1]

		# Build and add OT classes:
		defaultGlyphs = [x[:-5] for x in ssXXglyphs]
		for XX in range(highestSetNumber + 1):
			className = "%s%02i" % (classNamePrefix, XX)
			classGlyphs = [x + ssXXsuffix(XX) for x in defaultGlyphs] + ["space"]
			result = createOTClass(className=className, classGlyphNames=classGlyphs, targetFont=thisFont)
			print(result)

		# Build OT feature:
		featureText = ""
		if addDefault:
			zeroOrOne = 0
		else:
			zeroOrOne = 1

		suffixNumberRange = list(range(zeroOrOne, highestSetNumber + 1)) * (lineLength // highestSetNumber + 2)

		for j in range(highestSetNumber * (lineLength // highestSetNumber + 1), 0, -1):
			suffixNumber = suffixNumberRange[j]
			newLine = "sub @%s00' %s by @%s%02i;\n" % (classNamePrefix, "@%s00 " % classNamePrefix * j, classNamePrefix, suffixNumber)
			featureText += newLine

		# Add OT feature:
		result = createOTFeature(featureName=featureName, featureCode=featureText, targetFont=thisFont, codeSig="PSEUDORANDOM")
		print(result)
