# MenuTitle: Print Window
__doc__ = """
Print the frontmost window.
"""

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
