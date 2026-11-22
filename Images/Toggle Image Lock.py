# MenuTitle: Toggle Image Lock
__doc__ = """
Floating Window for toggling the locked status of selected glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class ToggleImageLock(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Toggle Image Lock",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		inset = 15
		self.w.lockButton = vanilla.Button("auto", "🔒 Lock", callback=self.ToggleImageLockMain)
		self.w.lockButton.setToolTip("Locks the images in the selected layers.")
		self.w.unlockButton = vanilla.Button("auto", "🔓 Unlock", callback=self.ToggleImageLockMain)
		self.w.unlockButton.setToolTip("Unlocks the images in the selected layers.")
		self.w.setDefaultButton(self.w.unlockButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[lockButton]-gap-[unlockButton]-inset-|",
				"V:|-inset-[lockButton]-inset-|",
				"V:|-inset-[unlockButton]-inset-|",
				{"view1": self.w.lockButton, "attribute1": "width", "view2": self.w.unlockButton, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 10},
		)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ToggleImageLockMain(self, sender):
		try:
			lockedStatus = sender != self.w.unlockButton

			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				return
			listOfSelectedLayers = thisFont.selectedLayers  # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers:  # loop through layers
				if thisLayer.backgroundImage:
					thisLayer.backgroundImage.locked = lockedStatus
					if thisLayer.parent:
						status = "Locked" if thisLayer.backgroundImage.locked else "Unlocked"
						print(f"{status} image in {thisLayer.parent.name}.")
			if thisFont.currentTab:
				thisFont.currentTab.redraw()
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Toggle Image Lock Error: {e}")


ToggleImageLock()
