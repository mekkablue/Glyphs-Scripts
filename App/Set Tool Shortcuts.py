# MenuTitle: Set Tool Shortcuts
__doc__ = """
Set Shortcuts for tools in toolbar.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from GlyphsApp import Glyphs
from mekkablue import mekkaObject

shortcuts = {
	"AnnotationTool": "a",
	"DrawTool": "p",
	"HandTool": "h",
	"MeasurementTool": "l",
	"OtherPathsTool": "e",
	"PenTool": "b",
	"PrimitivesTool": "f",
	"SelectTool": "v",
	"SelectAllLayersTool": "v",
	"TextTool": "t",
	"RotateTool": "r",
	"ScaleTool": "s",
	"TrueTypeTool": "i",
	"ZoomTool": "z",
}


def displayedShortcut(shortcut):
	"""Shortcuts are shown capitalized, except ß, because ß.upper() would be SS (and the SF font is buggy)."""
	return shortcut if shortcut == "ß" else shortcut.upper()


class SetToolShortcuts(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Set Tool Shortcuts",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		toolNames = sorted(shortcuts.keys())
		widestLabel = max(toolNames, key=len)
		self.fields = {}
		rules = []
		widthRules = []
		for toolName in toolNames:
			shortcut = Glyphs.defaults[f"{toolName}.Hotkey"]
			if not shortcut:
				shortcut = shortcuts[toolName]

			label = vanilla.TextBox("auto", toolName, sizeStyle="small")
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
			field = vanilla.EditText("auto", displayedShortcut(shortcut), sizeStyle="small", callback=self.changeShortcut)
			setattr(self.w, f"text_{toolName}", label)
			setattr(self.w, f"edit_{toolName}", field)
			self.fields[toolName] = field

			rules.append(f"H:|-inset-[text_{toolName}]-gap-[edit_{toolName}(>=40)]-inset-|")
			rules.append({"view1": label, "attribute1": "centerY", "view2": field, "attribute2": "centerY"})

		# all labels get the width of the widest one:
		for toolName in toolNames:
			if toolName != widestLabel:
				widthRules.append({"view1": getattr(self.w, f"text_{toolName}"), "attribute1": "width", "view2": getattr(self.w, f"text_{widestLabel}"), "attribute2": "width"})

		# one vertical chain, one field per row:
		chain = "-row-".join(f"[edit_{toolName}]" for toolName in toolNames)
		rules.append(f"V:|-inset-{chain}-inset-|")

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(rules + widthRules, metrics={"inset": inset, "gap": 8, "row": 6})

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def toolNameForField(self, field):
		for toolName, toolField in self.fields.items():
			if toolField is field:
				return toolName
		return None

	def changeShortcut(self, sender):
		try:
			toolName = self.toolNameForField(sender)
			if toolName is None:
				return
			newShortcut = sender.get()
			if newShortcut:
				# only the last typed character counts:
				newShortcut = newShortcut[-1].lower()
				sender.set(displayedShortcut(newShortcut))
				Glyphs.defaults[f"{toolName}.Hotkey"] = newShortcut
				print(f"New Shortcut for {toolName}: {newShortcut}")
				sender.selectAll()
			else:
				defaultShortcut = shortcuts[toolName]
				print(f"Resetting Shortcut for {toolName}: {defaultShortcut}")
				del Glyphs.defaults[f"{toolName}.Hotkey"]
				sender.set(displayedShortcut(defaultShortcut))

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set Tool Shortcuts Error: {e}")
			import traceback
			print(traceback.format_exc())


SetToolShortcuts()
