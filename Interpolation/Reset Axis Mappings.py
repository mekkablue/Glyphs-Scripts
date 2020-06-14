#MenuTitle: Reset Axis Mappings
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Inserts (or resets) a default Axis Mappings parameter for all style values currently present in the font. Ignores style values outside the designspace bounds defined by the masters.
"""

from Foundation import NSMutableDictionary
from axisMethods import *

if Glyphs.versionNumber < 3.0:
	Message(title="Glyphs Version Error", message="This script requires Glyphs 3.0 or later.", OKButton=None)
	return

mappings = NSMutableDictionary.alloc().init()
font = Glyphs.font
for axis in font.axes:
	axisTag = axis.axisTag
	minAxisPos, maxAxisPos = extremeMasterValuesNative( font, axisTag=axisTag )
	
	# add axis extremes:
	axisMapping = NSMutableDictionary.alloc().init()
	for masterExtreme in nativeMasterExtremes:
		axisMapping.addObject_forKey_( masterExtreme, masterExtreme )
	
	# add style positions
	for style in font.instances:
		styleValue = styleValueForAxisTag( style, axisTag )
		if minAxisPos < styleValue < maxAxisPos:
			axisMapping.addObject_forKey_( styleValue, styleValue )
	
	# add this axis mapping to mappings:
	mappings.addObject_forKey_( axisMapping, axisTag )
	
parameterName = "Axis Mappings"

# backup old parameter:
existingParameter = font.customParameterForKey_(parameterName)
if existingParameter:
	existingParameter.name = "OLD %s" % parameterName

# write new parameter:
font.customParameters[parameterName] = mappings
