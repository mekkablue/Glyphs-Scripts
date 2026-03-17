# MB LetterKerner

Optical kerning scripts for [Glyphs.app](https://glyphsapp.com/), by [mekkablue](https://github.com/mekkablue).

---

## Concept

**MB LetterKerner** borrows the optical measurement engine from
**[HT LetterSpacer](https://github.com/huertatipografica/HTLetterSpacer)**
by [Huerta Tipográfica](https://www.huertatipografica.com/) and repurposes
it for kerning.

HT LetterSpacer shoots horizontal rays inward from each side of a glyph,
accumulates depth-clamped, vertically-weighted distances (the *optical white
area*), and adjusts the glyph's sidebearings until that area matches a
target. MB LetterKerner applies the same measurement to the *corridor between
two glyphs* — the right white of the left glyph plus the left white of the
right glyph — and instead of moving any sidebearings, it calculates the kern
value that brings the combined optical area to the target.

> **Credits & kudos:** The optical measurement model — trapezoidal vertical
> weighting, per-side depth clamping, and the notion of an "area" target —
> is entirely the work of Huerta Tipográfica. This repository is an adaptation
> of their idea to the kerning domain. Please support their work at
> <https://www.huertatipografica.com/>.

---

## Files

| File | Purpose |
|---|---|
| `mbLetterKerner.py` | Library: core algorithm, importable from other scripts |
| `Kern Tab Contents.py` | Script: GUI for applying optical kerning to the current tab |

---

## Algorithm (`mbLetterKerner.py`)

### `kernLayerToLayer(leftLayer, rightLayer, parameters) → int`

The main function. Returns an integer kern value (negative = tighter,
positive = looser), or `None` if the measurement fails.

**Steps:**

1. Determine the vertical overlap of both glyph layers' bounding boxes.
2. Sample at every `step` units from `bottomY` to `topY`.
3. At each height *y*, read `RSB_left(y)` and `LSB_right(y)` via the
   Glyphs API (`rsbAtHeight_` / `lsbAtHeight_`). Skip heights where either
   glyph has no outline.
4. Clamp each measurement to `depth` so large open whites don't dominate.
5. Weight the clamped sum by `opticalWeight(y, xHeight, factor)` — a
   trapezoid function: full weight across the main body (baseline →
   x-height), linearly tapered in the descender and ascender zones.
6. Solve for `kern`:

```
currentArea = weightedGapSum × step
targetArea  = (weightedGapSum + kern × totalWeight) × step

kern = (targetArea / step − weightedGapSum) / totalWeight
```

### Parameters

| Key | Default | Description |
|---|---|---|
| `area` | `50000` | Target optical area in units². **Must be calibrated per font.** |
| `depth` | `200` | Max probe depth from each glyph side (units). |
| `factor` | `1.25` | Optical correction factor — scales all weights. Matches the HT LetterSpacer default. |
| `xHeight` | `500` | Master x-height; sets the boundary of the full-weight zone. Passed automatically by the script. |
| `step` | `5` | Vertical sampling interval (units). Smaller = more precise, slower. |

### Other public functions

| Function | Description |
|---|---|
| `opticalWeight(y, xHeight, factor)` | Optical weight at height *y* |
| `measureOpticalArea(layer, side, depth, xHeight, factor, step)` | Single-side area, mirrors HT LetterSpacer's per-side measurement |
| `kernKeyForGlyph(glyph, side, useGroups)` | Returns `@MMK_R_…` / `@MMK_L_…` group key or bare glyph name |

---

## Script: `Kern Tab Contents.py`

Opens a floating window. Fill the tab in Glyphs with glyph pairs and click
**Kern** to set kerning for every consecutive pair.

### Parameters in the UI

| Field | Description |
|---|---|
| **Target area** | The optical area to aim for (see calibration below). |
| **Depth** | Max probe depth per glyph side. 150–250 is typical. |
| **Factor** | Optical correction factor (1.25 = HT LetterSpacer default). |
| **Step** | Sampling interval in font units (5 = good balance). |
| **Round kern to** | Snap kern values to multiples of N (0 or 1 = no snap). |
| **Use kerning groups** | Store kerning against `@MMK` group keys (recommended). |
| **Skip pairs with existing kerning** | Leave already-kerned pairs alone. |

### Calibrating the target area

The `area` parameter is font-specific. To calibrate:

1. Open a tab with a "neutral" pair that should kern to **0** — typically
   the spacing reference pair for your script (e.g. `nn` for Latin
   lowercase, `HH` for uppercase, `ОО` for Cyrillic, etc.).
2. In the script UI, set **Target area** to something arbitrary (e.g. `50000`)
   and click **Kern**. Check the Macro Window — it will print the *current
   optical area* for that pair.
3. Copy that number and paste it as the **Target area**.
4. Re-run: the neutral pair should now kern to 0 (or very close).
   All other pairs in the tab will be kerned relative to that reference.

### Workflow tip

Maintain separate tabs for different pair categories:
- A tab of uppercase combos (H H, H A, H V, T A, …)
- A tab of lowercase combos (n n, n a, n v, f i, …)

Calibrate `area` for each category using its neutral pair, then run the
script per tab.

---

## Installation

Place the `MB LetterKerner` folder inside your Glyphs scripts folder
(`~/Library/Application Support/Glyphs 3/Scripts/` or the path shown
in *Glyphs → Preferences → Addons → Scripts*) and refresh the Script
menu (`Script → Refresh Script Menu`, or hold Option while opening the
menu).

Both files must stay in the same folder: `Kern Tab Contents.py` imports
`mbLetterKerner.py` from its own directory at runtime.

---

## License

Copyright 2024 Rainer Erich Scheichelbauer (mekkablue).
Licensed under the [Apache License, Version 2.0](LICENSE).

The optical measurement concept is adapted from
**HT LetterSpacer** © Huerta Tipográfica, also Apache 2.0.
