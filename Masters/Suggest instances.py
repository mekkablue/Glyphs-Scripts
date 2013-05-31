#MenuTitle: Suggest instances
# -*- coding: utf-8 -*-
"""Outputs suggestions for instance weight values, based on the weight values of the masters in the current font."""
from __future__ import division
import GlyphsApp

rangemin = 3
rangemax = 11

def distribute_lucas(min, max, n):
    q = max / min
    return [min * q**(i/(n-1)) for i in range(n)]
 
def distribute_equal(min, max, n):
    d = (max - min) / (n-1)
    return [min + i*d for i in range(n)]
 
def distribute_pablo(min, max, n):
    es = distribute_equal(min, max, n)
    ls = distribute_lucas(min, max, n)
    return [l*(1-i/(n-1)) + e*(i/(n-1)) for (i, e, l) in zip(range(n), es, ls)]

weightvalues = [ m.weightValue for m in Glyphs.font.masters ]
minimumWeight = min( weightvalues )
maximumWeight = max( weightvalues )

Glyphs.clearLog()
Glyphs.showMacroWindow()

if minimumWeight != maximumWeight:
	print "Luc(as) de Groot distributions between %i and %i:" % ( minimumWeight, maximumWeight )
	print
	
	for i in range( rangemin, rangemax ):
		distributedValues = distribute_lucas( minimumWeight, maximumWeight, i )
		distributedGain   = distributedValues[1] / distributedValues[0]
		print "%i instances: %s --> growth: %.1f%%" % ( i, "-".join("{0:.0f}".format(weight) for weight in distributedValues ), distributedGain*100-100 )
	
	print
	print "This is a steady percentage gain across weights, a:b = b:c = c:d, etc."
	print "Hint 1: growth of 41.4% = squareroot of 2."
	print "Hint 2: growth of 61.8% = Golden Mean."
	print "Hint 3: steady growth curves may not work well for light weights."
	print
	print "Pablo Impallari distribution between %i and %i:" % ( minimumWeight, maximumWeight )
	print
	
	for i in range( rangemin, rangemax ):
		distributedValues = distribute_pablo( minimumWeight, maximumWeight, i )
		print "%i instances: %s" % ( i, "-".join("{0:.0f}".format(weight) for weight in distributedValues ))
	
	print
	print "This is the Luc(as) algorithm steadily converging towards a linear growth."
	
	
else:
	print "You need at least two masters with differing weight values."
	