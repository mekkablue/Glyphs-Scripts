#MenuTitle: Update git Repositories in Scripts Folder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Executes a 'git pull' command on all subfolders in the Glyphs Scripts folder.
"""

from os import system, chdir, path

scriptsFolderPath = "~/Library/Application Support/Glyphs/Scripts/"
chdir( path.expanduser(scriptsFolderPath) )
result = system('find . -mindepth 1 -maxdepth 1 -type d -print -exec git -C {} pull -f \; -exec echo \;')

# Output in Macro Window
Glyphs.clearLog()
print(result)

if result.splitlines()[-1].strip()!="0":
	Glyphs.showMacroWindow()
else:
	Glyphs.showNotification( 
		u"Completed git pull in Scripts folder",
		u"Detailed report in Macro Window.",
	)
