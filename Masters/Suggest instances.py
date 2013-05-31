#MenuTitle: Suggest instances
# -*- coding: utf-8 -*-
"""Outputs suggestions for instance weight values, based on the weight values of the masters in the current font."""

import GlyphsApp

def distribute( minWt, maxWt, numOfInst ):
	returnlist = [  ]
	for i in range( numOfInst ):
		gain = ( float(maxWt) / float(minWt) ) ** ( 1 / float(numOfInst) )
		instanceValue = float(minWt) * gain ** i
		returnlist.append( str(int(instanceValue)) )
	
	returnlist.append( str(int(maxWt)) )
	return (returnlist, gain)
			
weightvalues = [ m.weightValue for m in Glyphs.font.masters ]
minimumWeight = min( weightvalues )
maximumWeight = max( weightvalues )

Glyphs.clearLog()
Glyphs.showMacroWindow()
if minimumWeight != maximumWeight:
	print "Suggested Luc(as) distributions between %i and %i:" % ( minimumWeight, maximumWeight )
	print
	
	for i in range(2,10):
		(distributedValues, distributedGain) = distribute( minimumWeight, maximumWeight, i )
		print "%i instances: %s --> growth: %.1f%%" % ( i+1, "-".join( distributedValues ), distributedGain*100-100 )
	
	print
	print "Hint 1: growth of 41.4% = squareroot of 2."
	print "Hint 2: growth of 61.8% = Golden Mean."
	print "Hint 3: steady growth curves may not work well for light weights."
else:
	print "You need at least two masters with differing weight values."