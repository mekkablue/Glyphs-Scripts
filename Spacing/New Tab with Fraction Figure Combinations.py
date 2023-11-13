#MenuTitle: New Tab with Fraction Figure Combinations
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Open Tab with fraction figure combos for spacing and kerning. Hold down COMMAND and SHIFT for all fonts.
"""

from AppKit import NSEvent, NSEventModifierFlagShift, NSEventModifierFlagCommand
keysPressed = NSEvent.modifierFlags()
shiftKeyPressed = keysPressed & NSEventModifierFlagShift == NSEventModifierFlagShift
commandKeyPressed = keysPressed & NSEventModifierFlagCommand == NSEventModifierFlagCommand

if commandKeyPressed and shiftKeyPressed:
	fonts = Glyphs.fonts
else:
	fonts = (Glyphs.font,)

for thisFont in fonts:
	paragraph = "/%s\n" % "/".join( [g.name for g in thisFont.glyphs if g.export and (g.name.startswith("percent") or g.name.startswith("perthousand"))] )

	z = "/zero.numr"
	figs = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

	for numr in figs:
		n = "/%s.numr" % numr
		line = z+n+z+n+n+z+z
		for dnom in figs:
			line += "/zero.numr/%s.numr/fraction/%s.dnom/zero.dnom  " % (numr,dnom)
		paragraph += line
		paragraph += "\n"
	
	paragraph += "\n"
	for glyph in thisFont.glyphs:
		slashedName = f"/{glyph.name}"
		if glyph.subCategory == "Fraction" and not slashedName in paragraph:
			paragraph += slashedName
	
	# opens new Edit tab:
	thisFont.newTab(paragraph.strip())

