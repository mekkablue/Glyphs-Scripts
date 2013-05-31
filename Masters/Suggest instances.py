#MenuTitle: Suggest instances
# -*- coding: utf-8 -*-
"""Outputs suggestions for instance weight values, based on the weight values of the masters in the current font."""

import GlyphsApp

def distribute( minWt, maxWt, numOfInst ):
	returnlist = [  ]
	for i in range( numOfInst ):
		instanceValue = float(minWt) * ( float(maxWt)/float(minWt) ) ** ( (i)/float(numOfInst) )
		returnlist.append( str(int(instanceValue)) )
	
	returnlist.append( str(int(maxWt)) )
	return returnlist
			
weightvalues = [ m.weightValue for m in Glyphs.font.masters ]
minimumWeight = min( weightvalues )
maximumWeight = max( weightvalues )

Glyphs.clearLog()
Glyphs.showMacroWindow()
if minimumWeight != maximumWeight:
	print "Suggested distributions between %i and %i:" % ( minimumWeight, maximumWeight )
	for i in range(3,10):
		print "%i instances: %s" % ( i, " - ".join( distribute( minimumWeight, maximumWeight, i ) ))
else:
	print "You need at least two masters with differing weight values."