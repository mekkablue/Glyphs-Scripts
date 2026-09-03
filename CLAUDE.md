# mekkablue Glyphs Scripts

Python scripts for the [Glyphs font editor](http://glyphsapp.com/). Scripts run inside Glyphs.app via its Python runtime (Python 3, PyObjC).

## Project Structure

- Each subfolder contains standalone `.py` scripts grouped by topic (~370 scripts total across 25+ categories).
- `__init__.py` — shared `mekkaObject` base class and utility functions (clipboard, wildcard matching, etc.).
- `geometry.py` — math/geometry helpers (transforms, italicization, intersections, etc.).
- `pyproject.toml` — black/flake8 config (line length: 120).
- `.style.yapf` — yapf formatting config (tabs, column limit 180).
- `.flake8` — flake8 ignore rules (W191, E501, E722, W503, E741, F841, E265, E225).

### Script Categories

| Folder | Topic |
|---|---|
| `Anchors/` | Anchor management & positioning (29 scripts) |
| `App/` | Application-level utilities, navigation (10 scripts) |
| `Build Glyphs/` | Font build utilities (3 scripts) |
| `Color Fonts/` | COLR/CBDT color font handling (4 scripts) |
| `Compare Frontmost Fonts/` | Multi-font comparison (4 scripts) |
| `Components/` | Component generation, alignment, flattening (13 scripts) |
| `Features/` | OpenType feature code generation (15 scripts) |
| `Font Info/` | Font metadata handling (8 scripts) |
| `Glyph Names, Notes and Unicode/` | Naming & Unicode assignment (12 scripts) |
| `Guides/` | Guide management (10 scripts) |
| `Hinting/` | TrueType hinting utilities (6 scripts) |
| `Images/` | Image/bitmap handling (7 scripts) |
| `Interpolation/` | Variable font, brace layers, axis manipulation (19 scripts) |
| `Kerning/` | Kerning analysis & manipulation (21 scripts) |
| `Paths/` | Path/contour operations (21 scripts) |
| `Pixelfonts/` | Bitmap font utilities (4 scripts) |
| `Post Production/` | Build finishing tasks (11 scripts) |
| `Smallcaps/` | Smallcaps generation (6 scripts) |
| `Spacing/` | Metric & spacing tools (10 scripts) |
| `Test/` | Testing & QA helpers (7 scripts) |

Some subfolders contain helper modules (not scripts), e.g., `Interpolation/axisMethods.py` for axis value lookups.

## Script File Header

Every script must begin in this exact order:

```python
# MenuTitle: My Script Name
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Short description of what the script does.
"""
```

`# MenuTitle:` **must be the very first line** of every script.

## Code Conventions

- **Tabs**, not spaces, for indentation (PyObjC convention — underscores have special meaning in PyObjC).
- **camelCase** for all variables and function names (not `under_score`).
- Descriptive names: `points` not `p`; `layers` not `layerList` or `listOfLayers`.
- Max line length: 120 (flake8/black), 180 (yapf).

## Import Order

```python
# Standard library
from itertools import product
from copy import copy

# Vanilla UI toolkit
import vanilla

# mekkablue shared module
from mekkablue import mekkaObject

# GlyphsApp core
from GlyphsApp import Glyphs, GSFont, GSLayer

# PyObjC frameworks
from AppKit import NSFont, NSAffineTransform
from Foundation import NSPoint
```

## Script Structures

### Simple scripts (no GUI)

```python
# MenuTitle: My Simple Script
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """Description."""

from GlyphsApp import Glyphs

font = Glyphs.font
if font:
	# do work directly at module level
	pass
```

### GUI scripts — subclass `mekkaObject`

```python
# MenuTitle: My GUI Script
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """Description."""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from mekkablue import mekkaObject


class MyScript(mekkaObject):
	prefDict = {
		"someOption": True,
		"someValue": 0,
	}

	def __init__(self):
		windowWidth = 330
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		# no minSize/maxSize: that keeps the window unresizable and the size limits out of
		# Auto Layout's way (see “Window layout” below)
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"My Script",
			autosaveName=self.domain("mainwindow"),  # persists window position
		)

		# UI elements:
		inset = 15

		self.w.myCheckbox = vanilla.CheckBox("auto", "Do the thing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.myCheckbox.setToolTip("Tooltip explaining what this does.")

		self.w.runButton = vanilla.Button("auto", "Run", callback=self.run)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[myCheckbox]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[myCheckbox]-inset-[runButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 8},
		)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# enable/disable dependent elements based on current pref values
		self.w.myCheckbox.enable(onOff=True)

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)

	def run(self, sender):
		# main action
		font = Glyphs.font
		if not font:
			return
		print("Report for My Script\n")
		# ... do work ...
		Glyphs.showNotification("My Script", "Done! Details in Macro Window.")


MyScript()
```

## `mekkaObject` API Reference

| Method | Description |
|---|---|
| `self.domain(prefName)` | Returns `"com.mekkablue.ClassName.prefName"` — the full Glyphs.defaults key |
| `self.pref(name)` | Reads preference; falls back to `prefDict` default |
| `self.prefBool(name)` | Reads preference as `bool` via NSUserDefaults |
| `self.prefInt(name)` | Reads preference as `int` via NSUserDefaults |
| `self.prefFloat(name)` | Reads preference as `float` via NSUserDefaults |
| `self.setPref(name, value)` | Writes value to `Glyphs.defaults` |
| `self.uiElement(name)` | Returns UI element for a given pref name (supports dot notation for nested elements) |
| `self.LoadPreferences()` | Populates all UI elements from prefs; calls `updateUI()` if defined |
| `self.SavePreferences(sender)` | Saves all UI element values to prefs; calls `updateUI()` if defined |
| `self.resizeWindowToMinimum()` | Clamps the window to `contentMinSize`/`contentMaxSize`, per axis. `LoadPreferences()` wraps `open()` so it runs once the autosaved frame is restored. A no-op for windows created without `minSize`/`maxSize`; for windows created **with** them it currently shrinks the window by the title bar height, because vanilla stores those as frame sizes while this compares content sizes |

Both `LoadPreferences()` and `SavePreferences()` automatically call `self.updateUI()` if that method exists — use `updateUI()` to cascade enable/disable state across dependent UI elements.

## Vanilla UI Elements

Common components and how to use them:

Pass `"auto"` instead of a `posSize` tuple and place them with rules (see below):

```python
self.w.label    = vanilla.TextBox("auto", "Label:", sizeStyle="small", selectable=True)
self.w.field    = vanilla.EditText("auto", "default", callback=self.SavePreferences, sizeStyle="small")
self.w.field.setToolTip("Tooltip for the field.")

self.w.check    = vanilla.CheckBox("auto", "Option", value=True, callback=self.SavePreferences, sizeStyle="small")
self.w.check.setToolTip("Tooltip for the checkbox.")

self.w.popup    = vanilla.PopUpButton("auto", ["A", "B"], callback=self.SavePreferences, sizeStyle="small")
self.w.combo    = vanilla.ComboBox("auto", ["A", "B"], callback=self.SavePreferences, sizeStyle="small")
self.w.combo.setToolTip("Tooltip.")
self.w.combo.getNSComboBox().setNumberOfVisibleItems_(20)
self.w.combo.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))

self.w.editor   = vanilla.TextEditor("auto", "", callback=self.SavePreferences)  # give it a height in the rules
self.w.editor.setToolTip("Multi-line field.")

self.w.divider  = vanilla.HorizontalLine("auto")  # needs an explicit height, e.g. [divider(1)]
self.w.bar      = vanilla.ProgressBar("auto")
self.w.status   = vanilla.TextBox("auto", "", sizeStyle="small")
```

### Tooltips

Use vanilla's `.setToolTip()` directly on the element — this is the preferred modern approach:

```python
self.w.myCheckbox.setToolTip("Explanation of what this does.")
self.w.myField.setToolTip("Explanation of what this does.")
```

**Exception — `vanilla.List`**: vanilla's `setToolTip()` sets the tooltip on the enclosing `NSScrollView`, not the inner `NSTableView`. For `List` widgets, use the direct PyObjC call:

```python
self.w.myList.getNSTableView().setToolTip_("Tooltip on the table view.")
```

### Window layout — use Auto Layout

Do **not** compute `posSize` frames by hand. Vanilla's frame-based layout inflates a control's
`posSize` by its `frameAdjustments` — for a push button `(-6, -8, 12, 12)`, hardcoded for the
classic Aqua bezel. On macOS 26 and later, buttons no longer draw that way, so hardcoded rows
overlap each other and sit too close to the window edge.

Create every control with `"auto"` and place them with Visual Format Language rules. Auto Layout
positions *alignment rects* and takes each control's intrinsic content size, so the layout fits
whatever the running macOS draws, and the insets and gaps are the distances actually seen:

```python
self.w.addAutoPosSizeRules(
	[
		"H:|-inset-[descriptionText]-inset-|",
		"H:|-inset-[label]-gap-[field]-inset-|",
		"H:|-inset-[optionA]-gap-[optionB]-(>=inset)-|",
		"H:|-(>=inset)-[uncheckAllButton(>=70)]-gap-[checkAllButton(>=70)]-gap-[runButton(>=70)]-inset-|",
		"V:|-gap-[descriptionText]-row-[field]-row-[optionA]-inset-[runButton]-inset-|",
		"V:[uncheckAllButton]-inset-|",
		"V:[checkAllButton]-inset-|",
		{"view1": self.w.label, "attribute1": "centerY", "view2": self.w.field, "attribute2": "centerY"},
	],
	metrics={"inset": 15, "gap": 8, "row": 8},
)
```

- View names in the rules are the `self.w.<name>` attribute names. Rules may also be dicts
  (`view1`/`attribute1`/`relation`/`view2`/`attribute2`), which is the only way to express
  `centerY` alignment or an equal width between two controls.
- `(>=70)` keeps short button titles from shrinking below the usual push-button width.
- Guard a right-aligned row with a leading `|-(>=inset)-`, otherwise the chain can run off the
  left edge when the window is narrow.
- Put a label on the same baseline as its field with a `centerY` rule, not a `+2` offset.
- `HorizontalLine` has no intrinsic height — give it one in the rule: `[divider(1)]`.
- Write one vertical chain per column; equal row heights keep the rows aligned.

**Columns.** Give the cells of a grid one shared width, measured against a single reference
control, so the columns line up without a hardcoded column offset:

```python
columnRules = [
	{"view1": cell, "attribute1": "width", "view2": gridCheckBoxes[0], "attribute2": "width"}
	for cell in gridCheckBoxes[1:]
]
```

**Hugging and compression.** A label next to a flexible control should hug its text, so the
field or popup takes the leftover width. Where two labels share a width, also make them resist
compression, otherwise the pair settles below the wider intrinsic width and wraps:

```python
nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
```

Keep labels on one line. A block that has to wrap needs a fixed height in the rules plus a
lowered horizontal compression resistance, so it takes the width it is given instead of
demanding one long line.

### Letting Auto Layout size the window

Pass **no** `minSize`/`maxSize`. Vanilla adds `NSResizableWindowMask` only when one of them is
given, and only then calls `setMinSize_`/`setMaxSize_` — which take *frame* sizes, while
`getPosSize()` and `resizeWindowToMinimum()` work in *content* sizes, so the title bar gets
counted twice and the window opens shorter than declared. Without them the window stays
fixed-size, `resizeWindowToMinimum()` becomes a no-op, and AppKit restores only the position
from the autosaved frame, not the size.

For the window to take its height from the content, two things must hold:

1. **No flexible gap in the vertical chain.** A `-(>=row)-` absorbs any surplus, so the layout
   has a minimum but no maximum and the window never shrinks.
2. **Every control hugs vertically** at `NSLayoutPriorityWindowSizeStayPut` (500) — the level at
   which a constraint starts outranking “keep the window size”. `TextBox`, `Button`, `EditText`,
   `PopUpButton` and `HorizontalLine` already default to 750, but `CheckBox` and `SquareButton`
   default to 250 and stretch:

```python
for view in self.w.getNSWindow().contentView().subviews():
	view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
```

`windowHeight` is then only a starting value — AppKit grows the window when the content needs
more and shrinks it when it needs less. Use `1`, not `0`: vanilla treats a zero height specially
and the window comes out full-screen tall. Widths are still taken from `windowWidth`; hugging
horizontally at the same level would shrink each window to its widest row and collapse the
labels that are meant to stretch across the full width.

### Frame-based layout (existing scripts)

Most scripts still place controls with `posSize` tuples and a running `linePos`:

```python
linePos, inset, lineHeight = 12, 15, 22
self.w.someElement = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Text", sizeStyle="small")
linePos += lineHeight
```

Negative coordinates are measured from the right/bottom edge (`-inset` = inset from right).
Read it, but prefer Auto Layout for new windows and when reworking an existing one.

## Shared Utility Functions (`__init__.py`)

| Function | Description |
|---|---|
| `getClipboard(verbose=False)` | Returns plain-text clipboard contents, or `None` |
| `setClipboard(text, verbose=False)` | Sets clipboard to text; returns `True` on success |
| `match(first, second)` | Wildcard matching supporting `*` and `?` |
| `camelCaseSplit(string)` | Splits a camelCase string into a list of words |
| `reportTimeInNaturalLanguage(seconds)` | Formats a duration as a readable string (e.g., `"2:34 minutes"`) |
| `newLineControlLayer()` | Returns a newline `GSControlLayer` for `tab.layers`; use instead of `GSControlLayer.newline()`, which raises a `TypeError` in some Glyphs versions |
| `newGlyphWithName(glyphName)` | Returns a new `GSGlyph` with that name; use instead of `GSGlyph(glyphName)`, which raises a `TypeError` in some Glyphs versions |
| `guidesOf(layerOrMaster)` | Returns the guides of a `GSLayer` or `GSFontMaster`; use instead of `.guideLines`, which is gone in Glyphs 4, or `.guides`, which does not exist in Glyphs 2 |
| `clearGuides(layerOrMaster)` | Deletes all guides of a `GSLayer` or `GSFontMaster`, Glyphs 2/3/4 compatible |
| `layerGroupsOf(glyph)` | Returns the interpolation-compatible layer ID groups of a `GSGlyph` as tuples; use instead of `layerGroups_masters_error_()`, which groups by instances — not the default in Glyphs 3/4 — and instead of `glyph.layerGroups()`, which does not exist in Glyphs 3.1 |
| `newAnchorWithName(anchorName, position=None)` | Returns a new `GSAnchor`; use instead of `GSAnchor(name, position)` (raises a `TypeError` in Glyphs 4) or `GSAnchor.alloc().initWithName_position_()` (missing in Glyphs 3) |
| `getLegibleFont(size=None)` | Returns a system legible font (Glyphs 2/3 compatible) |
| `UpdateButton(posSize, callback, title="")` | Creates a refresh button with an NSRefreshTemplate icon; `posSize` may be `"auto"` |

### `caseDict` (Glyphs 3 only)

`__init__.py` exports `caseDict`, a mapping from string names to Glyphs case constants. Available only when `Glyphs.versionNumber >= 3`:

```python
from mekkablue import caseDict
# Keys: "Lower", "lowercase", "Upper", "Uppercase", "SC", "Smallcaps", "Minor", "NoCase"
# Values: GSLowercase, GSUppercase, GSSmallcaps, GSMinor, GSNoCase
```

## Geometry Helpers (`geometry.py`)

| Function | Description |
|---|---|
| `transform(shiftX, shiftY, rotate, skew, scale)` | Returns an `NSAffineTransform` for layer transforms |
| `italicize(point, italicAngle, pivotalY)` | Returns the italicized position of an `NSPoint` |
| `angle(firstPoint, secondPoint)` | Angle in degrees between two points (`0°` = right) |
| `bezierWithPoints(A, B, C, D, t)` | Point on a Bézier curve at parameter `t` |
| `intersectionLineLinePoints(A, B, C, D, includeMidBcp)` | Line–line intersection; returns `NSPoint` or `None` |
| `offsetLayer(layer, offset, makeStroke, position, autoStroke)` | Applies offset filter (Glyphs 2/3 compatible) |
| `centerOfRect(rect)` | Center `NSPoint` of an `NSRect` |
| `normalizedCoordinate(x, y, layer, angle=0)` | Returns `(nx, ny)` in `0.0–1.0, 0.0–1.0` relative to the layer bbox; `angle` tilts the reference frame for italic/slanted glyphs |
| `normalizedMove(glyph, pathIndex, nodeIndex, layerID1, layerID2)` | Returns `(dnx, dny)` — normalized-space move of a node between two layers, italic-angle-corrected; `None` if layers missing/empty or index out of range |
| `divideAndTolerateZero(dividend, divisor)` | Safe division; returns `None` (not `0`) when divisor is zero |
| `bothPointsAreOnSameSideOfOrigin(pointA, pointB, pointOrigin)` | Returns `True` if both points are on the same side of origin |
| `pointIsBetweenOtherPoints(thisPoint, otherPointA, otherPointB)` | Returns `True` if point lies between the other two points |

> **Note:** Always import geometry helpers via `from mekkablue.geometry import ...`. Never use the bare `from geometry import ...` path.

Applying a transform to a layer:
```python
from mekkablue.geometry import transform
t = transform(shiftX=10, rotate=5, scale=1.1)
layer.applyTransform(t.transformStruct())
```

## Reporting / Logging

```python
Glyphs.clearLog()                         # optional: clear Macro Window
print("Report for My Script\n")           # always start with a title
print(f"\t✅ {glyphName}: done")          # use emojis + indentation
print(f"\t⚠️ {glyphName}: skipped")
print(f"\t❌ {glyphName}: error")
Glyphs.showNotification("My Script", "Brief summary. Details in Macro Window.")
```

- Use `print()` for the Macro Window log.
- Use emojis (`⚠️ ✅ ❌ ☑️ 💾 ↔️ 🔠`) and indentation for scannability.
- **Do not** open the Macro Window automatically unless reporting is the script's entire purpose.
- Notify the user via `Glyphs.showNotification()` for completion messages.

## Formatting Tools

```bash
# Format a single script
yapf --style .style.yapf -i path/to/script.py

# Lint (ignores tabs, bare except, long lines, etc. — see .flake8)
flake8

# Type check (adjust path to your Glyphs install)
export MYPYPATH="~/Code/Glyphs/Glyphs/Scripts/:$MYPYPATH"
mypy --ignore-missing-imports .
```

> **Note:** yapf has a known bug that can mis-indent closing parentheses/braces. Review after formatting.

## Key APIs

- `Glyphs` — app singleton: `Glyphs.font`, `Glyphs.fonts`, `Glyphs.defaults`, `Glyphs.clearLog()`, `Glyphs.showNotification()`, `Glyphs.registerDefault()`, `Glyphs.versionNumber`
- `GSFont`, `GSMaster`, `GSGlyph`, `GSLayer`, `GSPath`, `GSNode`, `GSAnchor`, `GSComponent` — core font model
- `vanilla` — UI toolkit for floating windows, dialogs, controls
- `AppKit`, `Foundation` — PyObjC frameworks (available at runtime inside Glyphs)

## Performance Guidelines

- Prefer tuples over lists where mutation is not needed.
- Use generator expressions: `(n for n in myList)` instead of `list(myList)`.
- Use the `timer` snippet for benchmarking hot paths:
  ```python
  from timeit import default_timer as timer
  start = timer()
  # ... hot code ...
  print(f"Elapsed: {timer() - start:.3f}s")
  ```
