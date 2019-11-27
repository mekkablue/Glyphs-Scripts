#MenuTitle: Remove Hints in Selected Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Deletes all hints in active (visible) layers of selected glyphs.
"""

Font = Glyphs.font
selectedLayers = Font.selectedLayers
print("Deleting hints in active layer:")

def process( thisLayer ):
	for x in reversed( range( len( thisLayer.hints ))):
		del thisLayer.hints[x]
		
Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print("Processing", thisLayer.parent.name)
	process( thisLayer )

Font.enableUpdateInterface()
