#MenuTitle: Update git Repositories in Scripts Folder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Executes a 'git pull' command on all subfolders in the Glyphs Scripts folder.
"""

from os import system, chdir, path

Glyphs.clearLog()
scriptsFolderPath = "~/Library/Application Support/Glyphs/Scripts/"
print("Executing 'git pull' for all subfolders in:\n%s" % scriptsFolderPath)

chdir( path.expanduser(scriptsFolderPath) )
exitStatus = system('find . -mindepth 1 -maxdepth 1 -type d -print -exec git -C {} pull -f \; -exec echo \;')

if exitStatus != 0:
	print("ERROR: Exit Status %i"%exitStatus)
	Glyphs.showMacroWindow()
else:
	print("Done.")
	Glyphs.showNotification( 
		u"Repo Update Successful",
		u"Completed git pull in Scripts folder.",
	)

