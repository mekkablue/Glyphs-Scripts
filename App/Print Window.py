#MenuTitle: Print Window
"""Print the frontmost window."""



doc = Glyphs.currentDocument

if doc:
	print doc.windowController().window().print_( None )
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print "Cannot print window: No document open."
	