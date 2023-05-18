#MenuTitle: Report ssXX Names of All Open Fonts
# -*- coding: utf-8 -*-
__doc__="""
Opens Macro Window with a list of all stylistic set names.
"""

Glyphs.clearLog() # clears log of Macro window
Glyphs.showMacroWindow()
print("Names for ssXX:")

# reversed, so that italics are sorted after uprights:
sortedFonts = reversed(sorted(Glyphs.fonts, key=lambda font: font.filepath.lastPathComponent()))
for font in sortedFonts:
	print()
	# heuristics for determining if it is an italic:
	italic = all(["italic" in i.name.lower() for i in font.instances if i.active])
	sortedFeatures = sorted(font.features, key=lambda feature: feature.name)
	for feature in sortedFeatures:
		if feature.name.startswith("ss"):
			print(f'{font.familyName} {"Italic" if italic else ""}, {feature.name}: {feature.featureNamesString().splitlines()[1].strip()[6:-2]}'.replace(" ,",","))

