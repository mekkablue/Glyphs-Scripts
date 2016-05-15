#MenuTitle: Fix Stuck Macro Window
# -*- coding: utf-8 -*-
__doc__="""
If you cannot resize your Macro window anymore, run this script.
"""

import os
terminalCommand = 'defaults delete com.GeorgSeifert.Glyphs2 "NSWindow Frame MacroPanel"'
os.system( terminalCommand )

