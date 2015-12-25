# ABOUT

These are Python scripts for use with the [Glyphs font editor](http://glyphsapp.com/).


# INSTALLATION

Put the scripts into the *Scripts* folder which appears when you choose *Open Scripts Folder* from the *Scripts* menu.

For some scripts, you will also need to install Tal Leming's *Vanilla*. Here's how. 

In **Glyphs 2.0 or later**, go to *Glyphs > Preferences > Addons > Scripts* and click the *Install Modules* button. You are done and can skip the rest of these installation instructions.

For **Glyphs 1.x**, open Terminal and copy and paste the following lines and hit return. You can copy all of them at once. Notes: the second line (`curl`) may take a while, the `sudo` line will prompt you for your password (type it and press Return, you will *not* see bullets):

    cd ~/Library/
    curl http://download.robofab.com/RoboFab_599_plusAllDependencies.zip > robofab.zip
    unzip -o robofab.zip -d Python_Installs
    rm robofab.zip
    cd Python_Installs/Vanilla/
    sudo python2.6 setup.py install
	

And you are done. The installation should be effective immediately, but in case it does not work right away, you may want to restart your Mac or log out and back in again.

While we're at it, we can also install Robofab, DialogKit, and FontTools. You do not need those for my scripts though:

    cd ../Robofab/
    sudo python2.6 setup.py install
    cd ../DialogKit/
    sudo python2.6 install.py
    cd ../FontTools/
    sudo python2.6 setup.py install

# TROUBLESHOOTING

Please report problems and request features as a GitHub issue. Make sure you have the latest version of the scripts and your app is up to date. And always, I mean *always*, indicate both your Glyphs.app and your OS X version. Thank you.

# ABOUT THE SCRIPTS

## Anchors
* **All Anchors in All Layers:** On each layer of a selected glyph, adds all missing anchors (but present in other layers of that glyph). Puts anchors at an averaged position.
* **Anchor Mover 1:** GUI for moving anchors vertically in multiple glyphs. Handy for getting all top anchors right after changing your cap height. *Needs Vanilla.*
* **Anchor Mover 2:** GUI for batch-processing anchor positions in multiple glyphs. *Needs Vanilla.*
* **Combining Accent Maker:** Goes through your selected (spacing) marks and adds a combining (non-spacing), component-based copy of it to your font, e.g., for *acute* and *dieresis.case*, it will add *acutecomb* and *dieresiscomb.case*.
* **Delete All Anchors:** Deletes all anchors in visible layers of selected glyphs.
* **Delete Entry and Exit Anchors:** Deletes all cursive attachment anchors (exit, entry and its variants) in visible layers of selected glyphs.
* **Find and Replace in Anchor Names:** GUI for replacing text in the names of anchors in selected glyphs. Processes all layers. *Needs Vanilla.*
* **Insert Anchors into Ligatures:** Copies base glyph anchors with number extensions into selected ligatures. E.g., if c has top and bottom, and e has top, bottom, and ogonek, the c_e ligature will get top_1, bottom_1, top_2, bottom_2, and ogonek_2. Horizontally adapts the anchor positioning to the width of the ligature. Ignores non-ligatures and glyph name extensions.
* **Move accents to custom anchors:** Moves accents to a custom anchor in the base glyph if available. E.g.: assuming glyph "A" has both "top" and "top_acute" anchors, if you run the script on "Aacute" and "Adieresis", it will move the acute on "top_acute", but leave the dieresis where it is.
* **Move acute, grave and hook to *top_viet*:** Moves *acute*, *grave* and *hookabovecomb* to the *top_viet* anchor in every layer of selected glyphs. Useful for Vietnamese double accents. Assumes that you have *top_viet* anchors in all layers of *circumflexcomb*.
* **New Tab with Anchor:** Opens a new tab with all glyphs containing a specific anchor.
* **Replicate Anchors:** Goes through selected dot-suffixed glyphs and duplicates anchors from their respective base glyphs. E.g. will recreate anchors of *X* in *X.ss01*, *X.swsh* and *X.alt*.
* **Report top anchors:** Report the y positions of all *top* anchors into the Macro Panel. Useful to see if a top anchor is not exactly where it should be.

## App
* **Kill background processes:** Terminates all makeotfGlyphs processes. If your fan keeps screaming after exporting a font, or after cancelling a font export, then run this script and see if it helps.
* **Print Window:** Print the frontmost window. Useful for saving a vector PDF of your window content.

## Arabic
* **Add Entry and Exit:** Adds entry and exit anchors for cursive attachment in selected glyphs. By default, it places the exit at (0, 0) and the entry at a node at RSB if such a node exists. Please adjust for your own needs.
* **Align All Arabic Double Marks in Current Master:** Substitute for automatic alignment in Arabic double marks. Goes through all Arabic compound mark ligatures in the current master, and aligns all the mark components according to their anchor positions (top, _top, and bottom, _bottom).
* **AXt Converter:** Converts the MacRoman glyph names (used in legacy AXt fonts) into nice names as employed by Glyphs. Attention: the script is still a work in progress. Suggestions are very welcome in the Wiki: https://github.com/mekkablue/Glyphs-Scripts/wiki/AXt-Converter
* **Fix Arabic Anchor Order in Ligatures:** Fixes the order of *top_X* and *bottom_X* anchors to RTL. In files converted from a different format, it sometimes happens that *top_1* is left of *top_2*, but it should be the other way around, otherwise your mark2liga will mess up. This script goes through your selected glyphs, and if they are Arabic ligatures, reorders all anchors to RTL order, at the same time not touching their coordinates.

## Components
* **Align All Components:** Fakes auto-alignment in glyphs that cannot be auto-aligned.
* **Align Accents Only:** Aligns accents without the need to use Automatic Alignment. Useful if you have an individually placed base glyph and want to update the accent positions.
* **Decompose Background:** Decomposes background layers of selected glyphs. Only works on the current master.
* **Delete All Components:** Deletes ALL components in selected glyphs. Be careful or use TimeMachine. You have been warned.
* **Diacritic Ligature Maker:** For selected ligatures with appropriate anchors (top_1, top_2, etc.), all possible diacritic variations are created. E.g., from A_h, the script can produce Adieresis_h, Aacute_h, A_hcircumflex, Adieresis_hcircumflex, etc. For preparing the anchors, try the *Anchors > Insert Anchors into Ligatures* script.
* **Enable** and **Disable Alignment:** Enables or disables automatic alignment for all components on visible layers in selected glyphs. Does the same as the command in the context menu, but you can do it in one step for many glyphs.
* **Modify Components:** In selected glyphs, replaces accents with their dot suffix variant where possible. *Needs Vanilla*
* **New Tab with Orphaned Components:** Opens a new tab in the current font window containing all glyphs (of the current master) that have components that point to non-existent glyphs, i.e., no base glyphs.
* **New Tab with Unaligned Compounds:** Opens a new tab containing all glyphs that have components that are not automatically aligned. Lists them for every master, so your font should contain all glyphs necessary for writing your font master names.
* **New Tab with Unusual Compounds:** Open a new tab containing all compound glyphs that have an unusual component order or an unorthodox component structure. Useful for finding wrong component orders.
* **Rebuild Components:** Moves outlines to background, then tries to rebuild the glyph with components in the foreground. Tries to position the accents as precisely as possible. Useful for rebuilding a decomposed font.
* **Remove Components:** Removes the specified component from all glyphs or all selected glyphs. *Needs Vanilla.*
* **Replace components:** Relinks components in selected glyphs to a new source glyph. *Needs Vanilla.*

## Effects Scripts
* **Wackelpudding** and **Beowulferize:** Select some or all glyphs in the Font tab, then run the script. It will create alternates of the selected glyphs and create a pseudorandom calt feature. Activate it by selecting Contextual Alternates in e.g. InDesign.
* **Baseline Wiggle:** Creates a pos feature that randomly displaces the glyphs while you type.
* **Stitcher:** In selected glyphs, the Stitcher inserts components on your paths at fixed intervals. Useful for turning open paths (monolines) into dotted lines. Use an anchor called 'origin' for determining the component position in stitched letters. *Needs Vanilla.*

## Features
* **Build ccmp for Hebrew Presentation Forms:** Builds or updates a Hebrew ccmp feature, where presentation forms (Unicode FBxx) are prebuilt like ligatures if present in the font.
* **Build positional calt feature:** Looks for .init, .medi, .fina, and .isol glyphs, and injects positional substitution code into your calt feature. If run again, will update its class and feature code. 
* **Floating Features:** Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. *Needs Vanilla.*
* **Glyph Names as Discretionary Ligatures:** Adds names of exporting glyphs without a Unicode value as ligatures into the dlig feature. Useful for proofing otherwise inaccessible glyphs.
* **Make OT Class from selected glyphs:** GUI for creating a new OT class with the selected glyphs. *Needs Vanilla.*
* **Refresh Features without Reordering:** Goes through the existing features in the font and refreshes each one of them. Does neither add nor reorder features.
* * **Stylistic Sets > Synchronize ssXX glyphs:** Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> the script creates *b.ss02*
* * **Stylistic Sets > Create ssXX from layer:** Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
* * **Stylistic Sets > Create pseudorandom calt feature:** Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Update: now includes the default class in the rotation algorithm.

## Glyph Names
* **Add PUA Unicode Values to Selected Glyphs:** Iterates through selected glyphs and incrementally applies custom Unicode values, starting at a user-specified value. *Needs Vanilla.*
* **Check Glyph Names:** Checks all available glyph names for illegal characters.
* **Copy Glyph Name List:** Copies a newline-separated list of glyph names. Useful for pasting into a *glyphOrder* custom parameter or a List filter.
* **Copy Unicode-Sorted Glyph Name List:** Copies a newline-separated list of glyph names, in the order of their respective Unicode values. Useful for pasting into a *glyphOrder* custom parameter or a List filter.
* **Lowercase:** Turns the names of selected glyphs lowercase.

## Guidelines
* **Add Center Guideline:** Adds vertical or horizontal guideline in the middle between two selected nodes.
* **Delete guidelines:** Deletes all local (blue) guidelines in selected glyphs.
* **Delete global guidelines:** Deletes all global (red) guidelines in the current master.

## Hinting
* **Add Hints for Selected Nodes:** Adds hints for the selected nodes. Tries to guess whether it should be H or V. If exactly one node inside a zone is selected, it will add a Ghost Hint. Useful for setting a shortcut in System Prefs.
* **BlueFuzzer:** Extends all alignment zones by the specified value. Similar to what the blueFuzz value used to do, hence the name. *Needs Vanilla.*
* **Delete Hints in Visible Layers:** Deletes hints in active layers of selected glyphs.
* **Delete All Hints in Font:** Deletes all hints throughout the active font. Be careful.
* **Delete All Vertical Hints in Font:** Deletes all vertical hints throughout the active font. Be careful.
* **Delete All Vertical Hints in Selected Glyphs:** Deletes all vertical hints in selected glyphs only.
* **Delete All Horizontal Hints in Font:** Deletes all horizontal hints throughout the active font. Be careful.
* **Keep First Master Hints Only:** In selected glyphs, deletes all hints in all layers except for whatever is ordered as first master. Respects Bracket Layers. E.g., if your first master is 'Regular', then the script will delete hints in 'Bold', 'Bold [120]', but keep them in 'Regular' and 'Regular [100]'.
* **New Tab with Glyphs Exceeding Zones:** Opens a new tab with all glyphs where the extremums do not lie within zones.
* **Set TT Stem Hints to Auto:** Sets all TT stem hints to ‘auto’ in selected glyphs.
* **Set TT Stem Hints to No Stem:** Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.

## Images
* **Add Same Image to Selected Glyphs:** Asks you for an image, and then inserts it into all currently selected glyphs as background image.
* **Delete Images:** Deletes all placed images in the visible layers of selected glyphs.
* **Reset Image Transformations:** Resets all image transformations (x/y offset, scale, and distortion) back to default in the visible layers of selected glyphs.
* **Set New Path for Images:** Resets the path for placed images in selected glyphs. Useful if you have moved your images.
* **Transform Images:** GUI for batch-transforming images (x/y offset and x/y scale) in the visible layers of selected glyphs. *Needs Vanilla.*

## Masters
* **Copy layer to layer:** Copies paths (and optionally, also components, anchors and metrics) from one Master to another. *Needs Vanilla.*
* **Dekink:** Dekinks your smooth transitions which are not horizontal or vertical. Select one or more angled smooth connections and run this script to move the corresponding nodes in all other masters to the same relative position. There is a video describing it: http://tinyurl.com/dekink-py
* **Delete all non-Master layers:** Deletes all layers which are neither master layers, nor brace layers, nor bracket layers. Useful for getting rid of backup layers.
* **Fill up empty layers:** Copies paths from one Master to another. But only if target master is empty. *Needs Vanilla.*
* **Find and Replace in Layer Names:** Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. *Needs Vanilla.*
* **Insert instances:** GUI for calculating and inserting weight instances. *Needs Vanilla.*
* **Merge All Other Masters in Current Master:** In selected glyphs, copies all paths from other masters onto the current master layer.
* **New Tab with Brace Layer Glyphs**: Opens a new Edit tab with all glyphs which contain the Brace Layer trick.
* **New Tab with Bracket Layer Glyphs:** Looks for all glyphs in the font that contain Bracket Trick Layers, and opens them in a new Edit tab.
* **New Tab with Dangerous Glyphs for Interpolation:** Opens a tab with all glyphs in the font that contain at least two compatible elements. I.e., glyphs where an element (a path or a component) could interpolate with the wrong element, like the equals sign. For a detailed description, see section *Be suspicious* in this tutorial: <http://www.glyphsapp.com/tutorials/multiple-masters-part-2-keeping-your-outlines-compatible>.
* **Show next/previous instance:** Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut in System Preferences.
* **Show masters of next/previous glyph:** Allows you to step through one glyph after another, but with all masters. Combines the show next/previous glyph function (fn+left/right) with the *Edit > Show All Masters* function. Handy for attaching a keyboard shortcut in System Preferences.
* **Sync Components Across Masters:** Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors.
* **Suggest instances:** Calculates distributions of weight values between your masters. Outputs into the macro window.
* **Variation Interpolator:** Creates a user-defined number of glyph variations with a user-defined suffix, containing interpolations between the layers and their respective backgrounds. Overwrites glyphs with same name. Similar to Pablo Impallari’s SimplePolator. Useful for e.g. length variants of Devanagari Matra, see José Nicolás Silva Schwarzenberg’s sample video: <https://www.youtube.com/watch?v=QDbaUlHifBc>. *Needs Vanilla.*

## Metrics
* **Adjust Kerning:** GUI to add a value to all kerning pairs, multiply all pairs by a value or round them by a value. *Needs Vanilla.*
* **Center glyphs:** centers all selected glyphs inside their width, so that LSB=RSB.
* **Change Metrics by Percentage:** Change LSB/RSB of selected glyphs by a percentage value. Undo with the Revert button. *Needs Vanilla.*
* **Compare Font Spacings:** Compares the overall widths, and widths weighted for English, of lowercase and uppercase A-Z for all currently opened fonts. Reports to the Macro window.
* **Copy Kerning from Caps to Small Caps:** Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.
* **Delete kerning pairs for selected glyphs:** deletes all kerning pairs with the selected glyphs, for the current master only.
* **Delete metrics keys:** deletes both left and right metrics keys in all selected glyphs. Affects all masters and all layers.
* **Delete Small Kerning Pairs:** Removes all kerning pairs in the current font master with a value smaller than specified, or a value equal to zero. Be careful. *Needs Vanilla.*
* **Export Kerning CSV:** exports a CSV containing all kerning pairs ('mastername;left;right;kerningvalue').
* **Export Metrics CSV:** exports a CSV containing all LSB, RSB and width values ('glyphname;mastername;LSB;RSB;width').
* **Extract kern strings 1st char:** asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 1st letter. *Needs Vanilla.*
* **Extract kern strings 2nd char:** asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 2nd letter. *Needs Vanilla.*
* **Find and Replace Kerning Groups:** GUI for searching and replacing text in the L and R Kerning Groups, e.g. replace 'O' by 'O.alt'. Leave the search field blank for appending.
* **Find and Replace Metrics Keys:** GUI for searching and replacing text in the L and R metrics keys, e.g. replace '=X+15' by '=X'. Leave the search field blank for appending.
* **New Tab with all Figure Combinations:** opens a new tab with all possible figure combos. Also outputs a string for copying into the macro window, in case the opening of the tab fails.
* **New Tab with all Selected Glyph Combinations:** takes your selected glyphs and opens a new tab with all possible combinations of the letters. Also outputs a string for copying into the macro window, in case the opening of the tab fails.
* **New Tab with All Group Members:** Select two glyphs, e.g. ‘Ta’, run the script, and it will open a new tab with all combinations of the right kerning group of T with the left kerning group of a.
* **New Tab with Fraction Figure Combinations:** Opens an Edit tab with fraction figure combos for spacing and kerning.
* **New Tab with Glyphs of Same Kerning Groups:** Opens an Edit tab containing all glyphs that share the same left or right kerning groups.
* **Remove All Kerning Exceptions:** Removes all kerning for the current master, except for group-to-group kerning. Be careful.
* **Reset alternate glyph width:** resets the width of suffixed glyphs to the width of their unsuffixed counterparts. E.g., *Adieresis.ss01* will be reset to the width of *Adieresis*.
* **Reset Compound Metrics to First Component:** Looks for the first component in a compound glyph, sets it back to x=0 and inherits its width. Useful for syncing numerators and denominators.
* **Steal kerning from InDesign:** steals the kerning from text set in InDesign. Useful for extracting InDesign’s Optical Kerning values.
* **Steal kerning groups:** steals left/right kerning groups for all selected glyphs from a 2nd font. *Needs Vanilla.*
* **Steal Sidebearings:** steals the sidebearing values for all selected glyphs from a 2nd font. Ignores metrics keys like '=x+20'. *Needs Vanilla.*

## Paths
* All **Move > Align** scripts look for a path in the currently active layer and align it to whatever the script title says. Useful if you need to do one of these alignment operations very often. Hint: you can set a keyboard shortcut in System Preferences.
* All **Move > Bump** scripts move the selection towards the next available metric to the left, right, top or bottom. The Bump Left/Right scripts also include the halfwidth of the glyph, the Bump Up/Down scripts include global guidelines as well. These are intended for setting a shortcut in System Preferences > Keyboard > Keyboard Shortcuts > Application Shortcuts (I recommend ctrl-opt-cmd-arrows).
* All **Distribute** scripts distribute all selected nodes horizontally or vertically, whatever is closer or what the script title says.
* All **Move > Move** scripts move the selected glyph(s) up/down by the specified distance, similar to what (shift-)ctrl-cmd-left/rightarrow does. As shortcut, I therefore recommend (shift-)ctrl-cmd-up/downarrow.
* **Close all open paths:** Closes all open paths in the visible layers of all selected glyphs.
* **Copy Glyphs from Other Font into Backup Layers:** Creates backup layers for selected glyphs in target font, and fills them with the respective glyphs from source font. Useful if you want to add glyphs from one font as bracket layers in another.
* **Delete all open paths:** Deletes all *open* paths in the visible layers of all selected glyphs.
* **Delete all paths:** Deletes *all paths* in the visible layers of all selected glyphs. Be careful.
* **Delete duplicate paths:** Deletes exact path duplicates (same paths on top of each other) in the visible layers of all selected glyphs.
* **Delete Nodes and Try to Keep Shape:** Deletes selected on-curve nodes and tries to keep the shape as much as possible. Similar to what happens when you delete a single node, but for a selection of multiple nodes.
* **Delete Stray Points:** Deletes stray points (single node paths) in selected glyphs. Careful: a stray point can be used as a quick hack to disable automatic alignment. Reports in detail to the macro window.
* **Fill up with rectangles:** Goes through your selected glyphs, and if it finds an empty one, inserts a placeholder rectangle. Useful for quickly building a dummy font for testing.
* **Grid Switcher:** Toggles grid between two user-definable gridstep values with the click of a floating button. *Needs Vanilla.*
* **Insert BCPs into straight segments:** Inserts off-curve points (BCPs) into straight line segments of all selected glyphs. Like option-clicking on all straight lines.
* **Insert Inflections:** Inserts nodes at path inflections in the visible layers of all selected glyphs.
* **New Tab with Zero Handles:** Opens a new tab with glyphs containing zero handles in the current font master.
* **Open all closed paths:** Opens all closed paths in the visible layers of all selected glyphs. Useful after importing open paths from FontLab Studio.
* **Realign Handles:** Realigns all BCPs on smooth connections. Only works in edit mode with the currently active layer. Useful if handles got out of sync, e.g. after nudging or some other transformation, or after interpolation.
* **Retract BCPs:** Deletes all off-curve points (BCPs). Handy if you want to make sure that your font only has straight lines. 
* **Rotate around anchor:** GUI for rotating glyphs or selections of nodes and components around a 'rotate' anchor. Allows to step and repeat. Requires Vanilla.
* **Set Transform Origin:** Simple GUI for setting the Transform Origin of the Rotate tool numerically. Should also have an effect on the Scale tool. Requires Vanilla.
* **Tunnify:** Looks for all path segments where at least one handle is selected. Then, evens out the handles of the segments, i.e., they will both have the same Fit Curve percentage. Can fix Adobe Illustrator's zero-handles (segments with one handle retracted into the nearest node). The idea for this script came from Eduardo Tunni (as colported by Pablo Impallari), hence the title of the script. I have never seen Eduardo's algorithm though, so my implementation might be a little different to his, especially the treatment of zero-handles.

## Pixelfonts
* **Align anchors to pixelgrid:** Moves diacritic anchors onto the grid. Assumes a grid step of 50.
* **Delete components out of bounds:** If a component is placed far outside the usual coordinates (happens when you cmd-arrow components with a high grid step), this script will delete them.
* **Delete duplicate components:** Looks for duplicate components (same name and position) and keeps only one.
* **Flashify Pixels:** Creates small bridges in order to prevent self-intersection of paths so counters stay white. This is especially a problem for the Flash font renderer, hence the name of the script.
* **Pixelate:** Replaces outlines with pixel components and optionally resets width to to pixel grid. *Needs Vanilla.*
* **Reset rotated and mirrored components:** Looks for scaled, mirrored and rotated components and turns them back into their default scale and orientation, but keeps their position. Useful for fixing mirrored pixels.

## Select
* **Select Same Color:** Select a glyph with a color, and the script will add all other glyphs with the same color to the selection, as long as they are currently displayed in the Font Tab. Does nothing if no glyph is selected.

## Smallcaps
* **Check Small Cap Consistency:** Performs a few tests on your SC set and reports into the Macro Window.
* **Copy kerning classes from smcp to c2sc:** If you already have c2sc and smcp glyphs, it will copy kerning group attributes from smcp to c2sc glyphs, e.g. *d.smcp* has *leftgroup=h.smcp* and *rightgroup=o.smcp*, then *leftgroup=h.smcp* and *rightgroup=o.smcp* will be copied to *D.c2sc*. 
* **Make c2sc from smcp:** Creates .c2sc copies of your .smcp glyphs, with the .smcp glyphs inserted as components in the .c2sc copies. For example, if you have *a.smcp*, the script will create *A.c2sc* and insert *a.smcp* as component. It will not do anything in case *A.c2sc* already exists.
* **Make smcp from c2sc:** Creates .smcp copies of your .c2sc glyphs, with the .c2sc glyphs inserted as components in the .smcp copies. For example, if you have *A.c2sc*, the script will create *a.smcp* and insert *A.c2sc* as component. It will not do anything in case *a.smcp* already exists.

## Test
* **Compare Font Family:** Compares a few Font Info entries between all currently opened fonts, and displays them in the Macro window if there are any differences.
* **Pangram Helper:** Helps you write a pangram, which you can copy into the clipboard, or put into a new tab. *Needs Vanilla.*
* **Preflight Font:** Checks for a few common mistakes, like bad glyph names, and reports them to the Macro Window.
* **Report Area in Square Units:** Calculates the area of each selected glyph, and outputs the result to the Macro Window in square units. Increase precision by changing the value for the PRECISION variable in line 9 (script will slow down).
* **Report Black to White Ratios:** Calculates the black area of all selected glyphs, and the black/white area ratio in relation to bounding box and several vertical metrics. Outputs a CSV spreadsheet.
* **Report highest glyphs:** Outputs list of selected glyphs, ordered by the highest point of the glyph bounding boxes.
* **Report lowest glyphs:** Outputs list of selected glyphs, ordered by the lowest point of the glyph bounding boxes.
* **Webfont Test HTML:** Creates a test HTML file in the folder where you last exported webfonts. *Requires Glyphs 2.*

# License

Copyright 2011-2015 Rainer Erich Scheichelbauer (@mekkablue).
Some code samples by Georg Seifert (@schriftgestalt) and Tal Leming (@typesupply).
Some algorithm input by Christoph Schindler (@hop) and Maciej Ratajski (@maciejratajski).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the software provided here except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.
