#MenuTitle: Print Window
"""Print the frontmost window."""
from __future__ import print_function
from AppKit import NSPasteboard, NSStringPboardType

doc = Glyphs.currentDocument
if doc:
	print(doc.windowController().window().contentView().print_( None ))
else:
	Message(
		title = "Print Window Error",
		message = "Cannot print window: No document open.",
		OKButton = None,
		)
	