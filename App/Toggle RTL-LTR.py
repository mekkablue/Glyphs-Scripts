from __future__ import print_function
#MenuTitle: Toggle RTL/LTR
# -*- coding: utf-8 -*-
__doc__="""
Toggle frontmost tab between LTR and RTL writing direction. Useful for setting a keyboard shortcut in System Preferences.
"""

if Glyphs.font:
    thisTab = Glyphs.font.currentTab
    if thisTab:
        if thisTab.writingDirection() == 0: # LTR
            newDirection = 1 # RTL
        else: # RTL or TTB
            newDirection = 0 # LTR
        thisTab.setWritingDirection_( newDirection )
    else:
        print("ERROR: No Edit tab open. Cannot switch writing direction.")
else:
    print("ERROR: No font open. Cannot switch writing direction.")