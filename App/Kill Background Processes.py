#MenuTitle: Kill Background Processes
# -*- coding: utf-8 -*-
__doc__="""
Terminates all makeotfGlyphs processes. If your fan keeps screaming after exporting a font, or after cancelling a font export, then run this script and see if it helps.
"""
import os
terminalCommand = 'killall makeotfGlyphs'
terminalCommandResult = os.system( terminalCommand )
print "%s: %s" % ( terminalCommand, terminalCommandResult )

