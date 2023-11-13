#MenuTitle: Report missing glyphs for all open fonts
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
In Macro window, reports all glyphs that are missing in some of the currently open files, but present in other other fonts.
"""

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()


def reportName(font):
	if font.filepath:
		return font.filepath.lastPathComponent().stringByDeletingDotSuffix()
	else:
		return font.familyName
	
def findMissingItems(listOfLists):
	# Create a set to store the items present in each list
	# commonItems = listOfLists[0][:]
	allItems = listOfLists[0][:]
	
	# Iterate through the rest of the lists
	for subList in listOfLists[1:]:
		# commonItems = list([x for x in commonItems if x in subList])
		allItems.extend([x for x in subList if not x in allItems])
	
	# Iterate through each list and find missing items
	missingItems = {}
	for idx, subList in enumerate(listOfLists):
		for item in allItems:
			if item not in subList:
				if not item in missingItems.keys():
					missingItems[item] = []
				missingItems[item].append(idx)

	return missingItems

def groupKeysByValues(inputDict):
	groupedKeys = {}
	
	for key, value in inputDict.items():
		valueStr = ", ".join([str(v) for v in value])
		if valueStr not in groupedKeys.keys():
			groupedKeys[valueStr] = []
		groupedKeys[valueStr].append(key)
	
	return groupedKeys


glyphSets = []
fonts = Glyphs.fonts
for font in fonts:
	glyphSet = list([g.name for g in font.glyphs if g.export])
	glyphSets.append(glyphSet)

missingGlyphsByGlyphs = findMissingItems(glyphSets)
missingGlyphs = groupKeysByValues(missingGlyphsByGlyphs)

for indicesStr, glyphNames in missingGlyphs.items():
	
	indices = [int(i.strip()) for i in indicesStr.split(",")]

	print(f"{', '.join(glyphNames)} missing in:")
	fontNames = [reportName(fonts[i]) for i in indices]
	report = '\n   '.join(fontNames)
	print(f"   {report}\n")
	

