# MenuTitle: Floating Features
__doc__ = """
Floating window for activating features in the frontmost Edit tab. Follows tab and window changes: the list of features and their activation state are refreshed whenever you switch tabs, windows or fonts.
"""

import traceback
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message, DOCUMENTACTIVATED, DOCUMENTDIDCLOSE, TABDIDOPEN, UPDATEINTERFACE
from AppKit import NSColor, NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSMakePoint


class FeatureActivator(mekkaObject):

	def __init__(self):
		font = Glyphs.font
		if not font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		if not font.features:
			Message(title="No Features", message=f"There are no OpenType features in {font.familyName}. Add features in Font Info > Features and run the script again.", OKButton=None)
			return

		self.w = None
		self.featureTags = None  # the features the window is built for, None until it is built
		self.checkBoxes = {}  # feature tag -> checkbox
		self.isRebuilding = False
		self.buildWindow(font)

		# follow window, tab and font changes. UPDATEINTERFACE fires often, so refresh() stays cheap:
		for callbackType in (DOCUMENTACTIVATED, DOCUMENTDIDCLOSE, TABDIDOPEN, UPDATEINTERFACE):
			Glyphs.addCallback(self.refresh, callbackType)

	def activeEditTab(self):
		document = Glyphs.currentDocument
		if document is None:
			return None
		return document.windowController().activeEditViewController()

	def buildWindow(self, font, topLeft=None):
		"""Creates the window for the features of this font, or a note if there is nothing to show."""
		tags = tuple(feature.name for feature in font.features) if font else ()
		self.featureTags = tags
		self.checkBoxes = {}

		windowWidth = 200
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		rules = []
		if tags:
			editTab = self.activeEditTab()
			selectedFeatures = editTab.selectedFeatures() if editTab else ()
			verticalChain = "V:|-inset"
			for i, feature in enumerate(font.features):
				featureTag = feature.name
				checkBoxName = f"featureCheckBox_{i}"
				checkBox = vanilla.CheckBox("auto", feature.fullName(), sizeStyle="small", callback=self.toggleFeature, value=(featureTag in selectedFeatures))
				checkBox.getNSButton().setIdentifier_(featureTag)
				checkBox.enable(editTab is not None)
				setattr(self.w, checkBoxName, checkBox)
				self.checkBoxes[featureTag] = checkBox
				rules.append(f"H:|-inset-[{checkBoxName}]-(>=inset)-|")
				verticalChain += f"-[{checkBoxName}]-checkRow" if i < len(font.features) - 1 else f"-[{checkBoxName}]-inset-|"
			rules.append(verticalChain)
		else:
			note = "No font open." if not font else "No features in this font."
			self.w.note = vanilla.TextBox("auto", note, sizeStyle="small")
			self.w.note.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
			rules.append("H:|-inset-[note]-(>=inset)-|")
			rules.append("V:|-inset-[note]-inset-|")

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(rules, metrics={"inset": 8, "checkRow": 5})
		self.w.bind("close", self.windowClose)
		self.w.open()
		if topLeft is not None:
			# a different number of features changes the height: keep the window anchored at its top left
			self.w.getNSWindow().setFrameTopLeftPoint_(topLeft)

	def windowClose(self, sender=None):
		if self.isRebuilding:
			return  # we are replacing the window, keep following
		Glyphs.removeCallback(self.refresh)

	def refresh(self, sender=None):
		"""
		Registered for window, tab and interface updates, which fire very frequently:
		only touches the window if the features differ (rebuilds it) or the activation state differs.
		"""
		if self.isRebuilding or self.w is None:
			return
		try:
			font = Glyphs.font
			tags = tuple(feature.name for feature in font.features) if font else ()
			if tags != self.featureTags:
				# other font or other features: build the window anew, at the same place
				self.isRebuilding = True
				try:
					frame = self.w.getNSWindow().frame()
					topLeft = NSMakePoint(frame.origin.x, frame.origin.y + frame.size.height)
					self.w.close()  # closes first, because two windows cannot share the autosave name
					self.buildWindow(font, topLeft)
				finally:
					self.isRebuilding = False
				return

			# same features: update the activation state
			editTab = self.activeEditTab()
			selectedFeatures = editTab.selectedFeatures() if editTab else ()
			for featureTag, checkBox in self.checkBoxes.items():
				isActive = featureTag in selectedFeatures
				if bool(checkBox.get()) != isActive:
					checkBox.set(isActive)
				if bool(checkBox.getNSButton().isEnabled()) != (editTab is not None):
					checkBox.enable(editTab is not None)
		except Exception as e:
			print(f"Floating Features refresh error: {e}")
			print(traceback.format_exc())

	def toggleFeature(self, sender):
		try:
			editTab = self.activeEditTab()
			if not editTab:
				Message(title="No Edit Tab Open", message="Features can only be toggled in an Edit tab. Open a tab and try again.", OKButton=None)
				return False
			featureTag = sender.getNSButton().identifier()
			featureActive = bool(sender.get())
			if featureActive:
				# add the feature:
				try:
					editTab.selectedFeatures().append(featureTag)
				except:
					editTab.selectedFeatures().addObject_(featureTag)
			else:
				# remove the feature:
				try:
					while True:
						editTab.selectedFeatures().remove(featureTag)
				except:
					pass

			editTab.graphicView().reflow()
			editTab.graphicView().layoutManager().updateActiveLayer()
			editTab._updateFeaturePopup()
			editTab.updatePreview()
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			return False

		return True


FeatureActivator()
