# MenuTitle: Filter Manager
__doc__ = """
Edit Filter custom parameters as plain text, one filter value string per line, including the optional exclude/include parts. ‘Paste’ reads the parameters plist from the clipboard (as copied from Custom Parameters in Font Info) into the text view (‘Paste & Add’ adds them at the bottom). ‘Copy Parameters’ turns the lines back into a parameters plist on the clipboard, ready to paste into Custom Parameters in Font Info. Disabled filters are prefixed with #.
"""

import re
import vanilla
from AppKit import NSMakeSize, NSDictionary, NSArray
from mekkablue import mekkaObject, getClipboard, setClipboard, getLegibleFont

parameterName = "Filter"
disabledPrefix = "#"
unlimited = 10000000.0


plistTokens = re.compile(r'"((?:\\.|[^"\\])*)"|([^\s=;{}(),"]+)|([={}();,])')
escapes = {"n": "\n", "t": "\t"}


def parseParameters(plistString):
	"""Returns a list of parameter dicts from a plist string, or None if it cannot be parsed."""
	try:
		parsed = plistString.propertyList()
	except:
		import traceback
		print(traceback.format_exc())
		return None

	if isinstance(parsed, (dict, NSDictionary)):
		# Glyphs 4 format, or a single parameter
		parsed = parsed.get("customParameters", [parsed])
	if not isinstance(parsed, (list, NSArray)):
		return None
	return parsed


def quoted(text):
	return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"')


class FilterManager(mekkaObject):
	prefDict = {
		"filters": "",
	}

	def __init__(self):
		windowWidth = 500
		windowHeight = 300
		self.w = vanilla.Window(
			(windowWidth, windowHeight),
			"Filter Manager",
			minSize=(250, 150),
			maxSize=(2000, 2000),
			autosaveName=self.domain("mainwindow"),  # persists window position and size
		)

		inset = 15

		self.w.filters = vanilla.TextEditor("auto", "", callback=self.SavePreferences, checksSpelling=False)
		self.w.filters.setToolTip("One filter per line, without the name ‘Filter’. Start a line with # to disable it.")
		scrollView = self.w.filters.getNSScrollView()
		scrollView.setHasVerticalScroller_(True)
		scrollView.setHasHorizontalScroller_(True)
		scrollView.setAutohidesScrollers_(True)
		textView = self.w.filters.getNSTextView()
		textView.setFont_(getLegibleFont())
		textView.setRichText_(False)
		textView.setAutomaticQuoteSubstitutionEnabled_(False)
		textView.setAutomaticDashSubstitutionEnabled_(False)
		textView.setAutomaticTextReplacementEnabled_(False)
		textView.setAutomaticSpellingCorrectionEnabled_(False)
		textView.setAutomaticLinkDetectionEnabled_(False)
		# no line wrapping, overflow is reached with the scroll bars:
		textView.setMinSize_(NSMakeSize(0.0, 0.0))
		textView.setMaxSize_(NSMakeSize(unlimited, unlimited))
		textView.setHorizontallyResizable_(True)
		textView.setVerticallyResizable_(True)
		textView.textContainer().setContainerSize_(NSMakeSize(unlimited, unlimited))
		textView.textContainer().setWidthTracksTextView_(False)

		self.w.pasteButton = vanilla.Button("auto", "Paste", callback=self.pasteParameters)
		self.w.pasteButton.setToolTip("Copy parameters in Font Info first. Replaces the text with one filter per line.")
		self.w.pasteAddButton = vanilla.Button("auto", "Paste & Add", callback=self.pasteAndAddParameters)
		self.w.pasteAddButton.setToolTip("Like Paste, but adds the filters at the bottom and keeps the existing lines.")
		self.w.copyButton = vanilla.Button("auto", "Copy Parameters", callback=self.copyParameters)
		self.w.copyButton.setToolTip("Puts the lines on the clipboard, ready to paste into Font Info.")
		self.w.setDefaultButton(self.w.copyButton)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[filters]-inset-|",
				"H:|-inset-[pasteButton(>=70)]-gap-[pasteAddButton(>=70)]-(>=inset)-[copyButton(>=120)]-inset-|",
				"V:|-inset-[filters]-inset-[pasteButton]-inset-|",
				"V:[pasteAddButton]-inset-|",
				"V:[copyButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def pasteParameters(self, sender=None):
		self.pasteFromClipboard(append=False)

	def pasteAndAddParameters(self, sender=None):
		self.pasteFromClipboard(append=True)

	def pasteFromClipboard(self, append=False):
		clipboard = getClipboard()
		parameters = parseParameters(clipboard) if clipboard else None
		if parameters is None:
			print("⚠️ Filter Manager: the clipboard does not contain parameters. Copy them from Custom Parameters in Font Info.")
			return

		lines = []
		for parameter in parameters:
			if not isinstance(parameter, (dict, NSDictionary)) or parameter.get("name") != parameterName:
				continue
			value = parameter.get("value")
			if not isinstance(value, str):
				continue
			line = value.replace("\n", " ")
			if str(parameter.get("disabled", 0)) not in ("0", "False", ""):
				line = f"{disabledPrefix} {line}"
			lines.append(line)

		existingText = self.w.filters.get().rstrip("\n")
		if append and existingText:
			lines.insert(0, existingText)
		self.w.filters.set("\n".join(lines))
		self.SavePreferences()

	def copyParameters(self, sender=None):
		entries = []
		for line in self.w.filters.get().splitlines():
			line = line.strip()
			disabled = line.startswith(disabledPrefix)
			if disabled:
				line = line[len(disabledPrefix):].strip()
			if not line:
				continue
			entry = "{\n"
			if disabled:
				entry += "disabled = 1;\n"
			entries.append(f"{entry}name = {parameterName};\nvalue = {quoted(line)};\n}},\n")

		if not entries:
			return
		plist = "{\n.formatVersion = 4;\ncustomParameters = (\n" + "".join(entries) + ");\n}"
		if not setClipboard(plist):
			print("⚠️ Filter Manager: could not write to the clipboard.")


FilterManager()
