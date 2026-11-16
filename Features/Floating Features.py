# MenuTitle: Floating Features
__doc__ = """
Floating window for activating features in the frontmost Edit tab.
"""

import traceback
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class FeatureActivator(mekkaObject):

	def __init__(self):
		font = Glyphs.font
		if not font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		if not font.features:
			Message(title="No Features", message=f"There are no OpenType features in {font.familyName}. Add features in Font Info > Features and run the script again.", OKButton=None)
			return

		editTab = Glyphs.currentDocument.windowController().activeEditViewController()
		selectedFeatures = editTab.selectedFeatures() if editTab else ()

		windowWidth = 200
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		rules = []
		verticalChain = "V:|-inset"
		for i, feature in enumerate(font.features):
			featureTag = feature.name
			featureName = feature.fullName()
			checkBoxName = f"featureCheckBox_{i}"
			checkBox = vanilla.CheckBox("auto", featureName, sizeStyle="small", callback=self.toggleFeature, value=(featureTag in selectedFeatures))
			checkBox.getNSButton().setIdentifier_(featureTag)
			setattr(self.w, checkBoxName, checkBox)
			rules.append(f"H:|-inset-[{checkBoxName}]-(>=inset)-|")
			verticalChain += f"-[{checkBoxName}]-checkRow" if i < len(font.features) - 1 else f"-[{checkBoxName}]-inset-|"
		rules.append(verticalChain)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(rules, metrics={"inset": 8, "checkRow": 5})
		self.w.open()

	def toggleFeature(self, sender):
		try:
			editTab = Glyphs.currentDocument.windowController().activeEditViewController()
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
