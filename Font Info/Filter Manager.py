# MenuTitle: Filter Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Edit Filter custom parameters as plain text, one filter value string per line, including the optional exclude/include parts. ‘Paste Parameters’ reads the parameters plist from the clipboard (as copied from Custom Parameters in Font Info) into the text view. ‘Copy Parameters’ turns the lines back into a parameters plist on the clipboard, ready to paste into Custom Parameters in Font Info. Disabled filters are prefixed with //.
"""

import vanilla
from AppKit import NSFont, NSMakeSize
from Foundation import NSPropertyListSerialization, NSString, NSUTF8StringEncoding
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, getClipboard, setClipboard

parameterName = "Filter"
disabledPrefix = "//"
unlimited = 10000000.0


def parseParameters(plistString):
	"""Returns a list of parameter dicts from a plist string, or None if it cannot be parsed."""
	data = NSString.stringWithString_(plistString).dataUsingEncoding_(NSUTF8StringEncoding)
	parsed, _, error = NSPropertyListSerialization.propertyListWithData_options_format_error_(data, 0, None, None)
	if parsed is None:
		return None
	if hasattr(parsed, "objectForKey_"):
		# a single parameter was copied
		return [parsed]
	return list(parsed)


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
		self.w.filters.setToolTip("One filter value string per line, without the parameter name ‘Filter’, e.g.: Transformations;OffsetX:10;exclude:a,b. Prefix a line with // to disable it.")
		scrollView = self.w.filters.getNSScrollView()
		scrollView.setHasVerticalScroller_(True)
		scrollView.setHasHorizontalScroller_(True)
		scrollView.setAutohidesScrollers_(True)
		textView = self.w.filters.getNSTextView()
		textView.setFont_(NSFont.userFixedPitchFontOfSize_(11))
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

		self.w.pasteButton = vanilla.Button("auto", "Paste Parameters", callback=self.pasteParameters)
		self.w.pasteButton.setToolTip("Reads Filter parameters from the clipboard (copied from Custom Parameters in Font Info) and replaces the text with one filter per line.")
		self.w.copyButton = vanilla.Button("auto", "Copy Parameters", callback=self.copyParameters)
		self.w.copyButton.setToolTip("Puts the lines as Filter parameters on the clipboard, ready to paste into Custom Parameters in Font Info.")
		self.w.setDefaultButton(self.w.copyButton)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[filters]-inset-|",
				"H:|-inset-[pasteButton(>=120)]-gap-[copyButton(>=120)]-(>=inset)-|",
				"V:|-inset-[filters]-inset-[pasteButton]-inset-|",
				"V:[copyButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def pasteParameters(self, sender=None):
		clipboard = getClipboard()
		parameters = parseParameters(clipboard) if clipboard else None
		if parameters is None:
			print("⚠️ Filter Manager: the clipboard does not contain parameters. Copy them from Custom Parameters in Font Info.")
			Glyphs.showNotification("Filter Manager", "No parameters on the clipboard.")
			return

		lines = []
		skipped = 0
		for parameter in parameters:
			if not hasattr(parameter, "objectForKey_") or parameter.get("name") != parameterName:
				skipped += 1
				continue
			value = parameter.get("value")
			if not isinstance(value, str):
				skipped += 1
				continue
			line = value.replace("\n", " ")
			if str(parameter.get("disabled", 0)) not in ("0", "False", ""):
				line = f"{disabledPrefix} {line}"
			lines.append(line)

		self.w.filters.set("\n".join(lines))
		self.SavePreferences()
		message = f"Pasted {len(lines)} filter(s)."
		if skipped:
			message += f" Skipped {skipped} other parameter(s)."
		print(f"Filter Manager: {message}")
		Glyphs.showNotification("Filter Manager", message)

	def copyParameters(self, sender=None):
		entries = []
		for line in self.w.filters.get().splitlines():
			line = line.strip()
			disabled = line.startswith(disabledPrefix)
			if disabled:
				line = line[len(disabledPrefix):].strip()
			if not line:
				continue
			entry = f"{{\nname = {parameterName};\nvalue = {quoted(line)};\n"
			if disabled:
				entry += "disabled = 1;\n"
			entries.append(entry + "}")

		if not entries:
			Glyphs.showNotification("Filter Manager", "No filters to copy.")
			return
		plist = "(\n" + ",\n".join(entries) + "\n)"
		if setClipboard(plist):
			message = f"Copied {len(entries)} filter parameter(s)."
		else:
			message = "Could not write to the clipboard."
		print(f"Filter Manager: {message}")
		Glyphs.showNotification("Filter Manager", message)


FilterManager()
