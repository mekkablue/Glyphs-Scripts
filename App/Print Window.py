# MenuTitle: Print Window
"""Print the frontmost window."""

from __future__ import print_function
from GlyphsApp import Glyphs, Message

doc = Glyphs.currentDocument
if doc:
	print(doc.windowController().window().contentView().print_(None))
else:
	Message(
		title="Print Window Error",
		message="Cannot print window: No document open.",
		OKButton=None,
	)
