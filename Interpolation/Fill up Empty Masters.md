# Tutorial: Fill Up Empty Masters

When you add a new master to a font, many glyphs may still have empty layers for that master (e.g. the 2nd or 3rd master is empty in some glyphs). Interpolation cannot work as long as those layers are empty, and you will get *incompatible masters* errors. The **Fill Up Empty Masters** script gives every empty master layer a temporary set of outlines copied from a master that *does* have shapes, so all masters become compatible and interpolate. You can then adjust the copied outlines master by master.

## The scenario

Imagine a font with three masters:

| Master | State in glyph `A` |
|---|---|
| Master 1 (Light) | has outlines ✅ |
| Master 2 (Regular) | **empty** ❌ |
| Master 3 (Bold) | **empty** ❌ |

Master 2 and Master 3 are empty for `A` (and perhaps many other glyphs). To make the glyph interpolatable, both empty layers need matching outlines. Rather than redrawing them by hand, we copy the shapes from Master 1 as a starting point.

## Step by step

1. In **Font View**, select the glyphs you want to fix. To catch everything, select all glyphs (**Edit → Select All**, or ⌘A).
2. Run **Script → mekkablue → Interpolation → Fill Up Empty Masters.**
3. In the **Use shapes from** pop-up, pick the master that already contains outlines you want to use as the source — e.g. *Master 1 (Light)*. Use the refresh button next to it if the master list is out of date.
4. Set the options (see below), then click **Fill Up.**

Only *empty* master (and special/brace) layers are filled. Layers that already contain shapes are left untouched — unless you explicitly enable overwriting.

## Options

- **If empty, use first master with shapes** — recommended. If your chosen source master happens to be empty for a particular glyph, the script falls back to the first master that *does* have outlines. This makes bulk runs across the whole font reliable.
- **Add missing default anchors** — adds the standard anchors (e.g. `top`, `bottom`) to the filled-up layers so anchor-based mark attachment stays compatible.
- **Also copy sidebearings** — copies the LSB/RSB from the source layer, so spacing stays roughly consistent until you space the new master.
- **Color-mark filled-up layers** — tags every layer the script touched with a label color of your choice. Very useful: it leaves you a visual to-do list of layers that still need real drawing.
- **Overwrite Existing Outlines ❗️** — off by default. When on, the script replaces outlines on *all* target master layers, not just the empty ones. Use with care — this discards existing drawings.

## After running

- The Macro Window prints a report of which glyphs were filled and from which master, e.g. `🔤 Filling up A from layer Light`, and a final count of layers filled.
- All masters are now compatible, so the glyphs interpolate and export.
- The copied outlines are only a placeholder. Go through the color-marked layers and correct the shapes for each master (weight, width, etc.). Remove the label colors as you finish each glyph to track progress.

## Tips

- Run it on a **selection** first to test your settings before doing the whole font.
- Turn on **Color-mark filled-up layers** on every real run — it is the fastest way to find which layers still need proper drawing.
- The script also fills **brace/intermediate layers** (special layers), not just plain masters.
