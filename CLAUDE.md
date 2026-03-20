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
from mekkablue import mekkaObject


class MyScript(mekkaObject):
	prefDict = {
		"someOption": True,
		"someValue": 0,
	}

	def __init__(self):
		windowWidth = 330
		windowHeight = 240
		windowWidthResize = 0   # extra width the user can resize by
		windowHeightResize = 0  # extra height the user can resize by
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"My Script",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),  # persists window position/size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.myCheckbox = vanilla.CheckBox((inset, linePos, -inset, 20), "Do the thing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.myCheckbox.setToolTip("Tooltip explaining what this does.")
		linePos += lineHeight

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Run", callback=self.run, sizeStyle="small")
		self.w.setDefaultButton(self.w.runButton)

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
| `self.resizeWindowToMinimum()` | Resizes window to its minSize if the saved size is smaller (called automatically by `LoadPreferences()`) |

Both `LoadPreferences()` and `SavePreferences()` automatically call `self.updateUI()` if that method exists — use `updateUI()` to cascade enable/disable state across dependent UI elements.

## Vanilla UI Elements

Common components and how to use them:

```python
self.w.label    = vanilla.TextBox((inset, linePos + 2, 120, 14), "Label:", sizeStyle="small", selectable=True)
self.w.field    = vanilla.EditText((inset + 120, linePos, -inset, 19), "default", callback=self.SavePreferences, sizeStyle="small")
self.w.field.setToolTip("Tooltip for the field.")

self.w.check    = vanilla.CheckBox((inset, linePos, -inset, 20), "Option", value=True, callback=self.SavePreferences, sizeStyle="small")
self.w.check.setToolTip("Tooltip for the checkbox.")

self.w.popup    = vanilla.PopUpButton((inset, linePos, 120, 18), ["A", "B"], callback=self.SavePreferences, sizeStyle="small")
self.w.combo    = vanilla.ComboBox((inset, linePos, 120, 19), ["A", "B"], callback=self.SavePreferences, sizeStyle="small")
self.w.combo.setToolTip("Tooltip.")
self.w.combo.getNSComboBox().setNumberOfVisibleItems_(20)
self.w.combo.getNSComboBox().setFont_(NSFont.userFixedPitchFontOfSize_(11))

self.w.editor   = vanilla.TextEditor((inset, linePos, -inset, 80), "", callback=self.SavePreferences)
self.w.editor.setToolTip("Multi-line field.")

self.w.divider  = vanilla.HorizontalLine((inset, linePos, -inset, 1))
self.w.bar      = vanilla.ProgressBar((inset, linePos, -inset, 16))
self.w.status   = vanilla.TextBox((inset, -28 - inset, -inset - 80, 14), "", sizeStyle="small")
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

### Layout pattern

```python
linePos, inset, lineHeight = 12, 15, 22

# Place elements, then advance:
self.w.someElement = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Text", sizeStyle="small")
linePos += lineHeight
```

Negative coordinates are measured from the right/bottom edge (`-inset` = inset from right).

## Shared Utility Functions (`__init__.py`)

| Function | Description |
|---|---|
| `getClipboard(verbose=False)` | Returns plain-text clipboard contents, or `None` |
| `setClipboard(text, verbose=False)` | Sets clipboard to text; returns `True` on success |
| `match(first, second)` | Wildcard matching supporting `*` and `?` |
| `camelCaseSplit(string)` | Splits a camelCase string into a list of words |
| `reportTimeInNaturalLanguage(seconds)` | Formats a duration as a readable string (e.g., `"2:34 minutes"`) |
| `getLegibleFont(size=None)` | Returns a system legible font (Glyphs 2/3 compatible) |
| `UpdateButton(posSize, callback, title="")` | Creates a refresh button with an NSRefreshTemplate icon |
| `transform(shiftX, shiftY, rotate, skew, scale)` | Returns an `NSAffineTransform` (duplicate of `geometry.transform`; not imported directly by scripts) |

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
| `divideAndTolerateZero(dividend, divisor)` | Safe division; returns `None` (not `0`) when divisor is zero |
| `bothPointsAreOnSameSideOfOrigin(pointA, pointB, pointOrigin)` | Returns `True` if both points are on the same side of origin |
| `pointIsBetweenOtherPoints(thisPoint, otherPointA, otherPointB)` | Returns `True` if point lies between the other two points |

> **Note:** `transform()` exists in both `__init__.py` and `geometry.py`, but all scripts import it via `from mekkablue.geometry import transform`. Never use `from geometry import ...` (bare module path) — always use `from mekkablue.geometry import ...`.

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
