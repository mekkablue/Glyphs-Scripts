# MenuTitle: Parameter Reporter
__doc__ = """
Searches in Custom Parameter names of all registered parameters in the current app version.
"""

import vanilla
from AppKit import NSWindowStyleMaskResizable
from Foundation import NSSize
from GlyphsApp import Glyphs, GSGlyphsInfo
from mekkablue import setClipboard, mekkaObject


class ParameterReporter(mekkaObject):
	prefDict = {
		"filter": ""
	}
	if Glyphs.versionNumber >= 3:
		# GLYPHS 3:
		fontParameters = GSGlyphsInfo.customFontParameters()
		masterParameters = GSGlyphsInfo.customMasterParameters()
		instanceParameters = GSGlyphsInfo.customInstanceParameters()
	else:
		# GLYPHS 2
		appInfo = GSGlyphsInfo.sharedManager()
		fontParameters = appInfo.customFontParameters()
		masterParameters = appInfo.customMasterParameters()
		instanceParameters = appInfo.customInstanceParameters()

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 200
		windowWidthResize = 400  # user can resize width by this value
		windowHeightResize = 650  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Parameter Reporter",
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI ELEMENTS:
		inset = 8

		# Filter:
		self.w.filter = vanilla.EditText("auto", "", callback=self.ParameterReporterMain, sizeStyle="small")
		self.w.filter.setToolTip("Type one or more search terms here. Use * as wildcard.")

		# Listing of Parameters:
		self.w.parameterList = vanilla.List("auto", [], autohidesScrollers=False, drawVerticalLines=True, doubleClickCallback=self.copySelection, rowHeight=19)
		self.w.parameterList.getNSTableView().tableColumns()[0].setWidth_(501)
		self.w.parameterList.getNSTableView().setToolTip_("Double click an entry to copy the respective parameter into the clipboard.")

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[filter]-inset-|",
				"H:|[parameterList]|",
				"V:|-inset-[filter]-inset-[parameterList(>=100)]|",
			],
			metrics={"inset": inset},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in both directions. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.setContentMinSize_(NSSize(windowWidth, windowHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, windowHeight + windowHeightResize))

		self.ParameterReporterMain(None)

	def realmStringForParameter(self, parameterName):
		realms = []
		if parameterName in self.fontParameters:
			realms.append("F")
		if parameterName in self.masterParameters:
			realms.append("M")
		if parameterName in self.instanceParameters:
			realms.append("I")
		return f"({','.join(realms)})"

	def copySelection(self, sender):
		try:
			indexes = self.w.parameterList.getSelection()
			if not indexes:
				return

			clipboardPieces = []
			for index in indexes:
				parameterName = self.w.parameterList[index]
				parenthesisOffset = parameterName.rfind("(")  # strips the realms, e.g. ‘(F,M)’
				parameterName = parameterName[:parenthesisOffset].strip()
				clipboardPieces.append(f'{{"{parameterName}" = "";}}')

			# puts parameters in clipboard:
			clipboardString = f"({','.join(clipboardPieces)})"

			if not setClipboard(clipboardString):
				print("⚠️ Warning: could not set clipboard.")

			# Floating notification:
			Glyphs.showNotification(
				f"{len(indexes)} parameter{'' if len(indexes) == 1 else 's'} copied",
				"You can paste in Font Info.",
			)

		except Exception as e:
			Glyphs.showMacroWindow()
			print(f"Parameter Reporter Error:\nCould not copy to clipboard.\n{e}")

	def ParameterReporterMain(self, sender):
		try:
			filterStrings = self.w.filter.get().strip().split(" ")

			parameters = sorted(set(self.fontParameters + self.instanceParameters + self.masterParameters), key=lambda thisName: thisName.lower())
			for filterString in filterStrings:
				filterString = filterString.lower()
				if "*" not in filterString:
					parameters = [f for f in parameters if filterString in f.lower()]
				elif filterString.startswith("*"):
					parameters = [f for f in parameters if f.lower().endswith(filterString[1:])]
				elif filterString.endswith("*"):
					parameters = [f for f in parameters if f.lower().startswith(filterString[:-1])]
				else:
					asteriskPos = filterString.find("*")
					beginning = filterString[:asteriskPos]
					ending = filterString[asteriskPos + 1:]
					parameters = [f for f in parameters if f.lower().startswith(beginning) and f.lower().endswith(ending)]

			parameters = [f"{item} {self.realmStringForParameter(item)}" for item in parameters]
			self.w.parameterList.set(parameters)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Parameter Reporter Error: {e}")
			import traceback
			print(traceback.format_exc())


ParameterReporter()
