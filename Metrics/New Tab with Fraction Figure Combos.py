#MenuTitle: New Tab with Fraction Figure Combinations
# -*- coding: utf-8 -*-
__doc__="""
Open Tab with fraction figure combos for spacing and kerning.
"""

thisFont = Glyphs.font

paragraph = ""
z = "/zero.numr"
figs = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

for numr in figs:
	n = "/%s.numr" % numr
	line = z+n+z+n+n+z+z
	for dnom in figs:
		line += "/zero.numr/%s.numr/fraction/%s.dnom/zero.dnom  " % (numr,dnom)
	paragraph += line
	paragraph += "\n"

# in case last line fails, the text is in the macro window:
Glyphs.clearLog() # clears macro window log
print paragraph

# opens new Edit tab:
thisFont.newTab( paragraph )
	