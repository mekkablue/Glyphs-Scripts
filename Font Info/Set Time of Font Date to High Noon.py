#MenuTitle: Set Time of Font Date to High Noon
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
In the Font Creation Date in Font Info, sets the time (invisible in the UI) to high noon.
"""

import datetime

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

# Report in macro window:
thisFont = Glyphs.font # frontmost font
print("Resetting font creation time for %s" % thisFont.familyName)
print(thisFont.filepath)

# Get current date:
currentDate = thisFont.date
newDate = datetime.datetime(
	currentDate.year,
	currentDate.month,
	currentDate.day,
	12, #d.hour,
	00, #d.minute,
	00, #d.second,
	00, #d.microsecond,
	currentDate.tzinfo,
	)

thisFont.date = newDate
print(u"✅ New Date:", newDate)
