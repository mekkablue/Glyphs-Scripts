#MenuTitle: Suggest instances
# -*- coding: utf-8 -*-
"""Outputs suggestions for instance weight values, based on the weight values of the masters in the current font."""
from __future__ import division
import GlyphsApp

def distribute(min, max, n):
	return [ min * (max / min) ** ( i/(n-1) ) for i in range(n) ]
			
weightvalues = [ m.weightValue for m in Glyphs.font.masters ]
minimumWeight = min( weightvalues )
maximumWeight = max( weightvalues )

Glyphs.clearLog()
Glyphs.showMacroWindow()

if minimumWeight != maximumWeight:
	print "Suggested Luc(as) distributions between %i and %i:" % ( minimumWeight, maximumWeight )
	print
	
	for i in range( 3, 11 ):
		distributedValues = distribute( minimumWeight, maximumWeight, i )
		distributedGain   = distributedValues[1] / distributedValues[0]
		print "%i instances: %s --> growth: %.1f%%" % ( i, "-".join("{0:.0f}".format(weight) for weight in distributedValues ), distributedGain*100-100 )
	
	print
	print "Hint 1: growth of 41.4% = squareroot of 2."
	print "Hint 2: growth of 61.8% = Golden Mean."
	print "Hint 3: steady growth curves may not work well for light weights."
	
else:
	print "You need at least two masters with differing weight values."
	