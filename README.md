# ABOUT

These are Python scripts for use with the [Glyphs font editor](http://glyphsapp.com/).


# INSTALLATION

Put the scripts into the *Scripts* folder which appears when you choose *Open Scripts Folder* from the *Scripts* menu.

For some scripts, you will also need to install Tal Leming's *Vanilla*. Here's how. Open Terminal and copy and paste each of the following lines and hit return. Notes: the second line (*curl*...) may take a while, the sudo lines will prompt you for your password:

    cd ~/Library/
    curl http://download.robofab.com/RoboFab_599_plusAllDependencies.zip > robofab.zip
    unzip robofab.zip -d Python_Installs
    rm robofab.zip
    cd Python_Installs/Vanilla/
    sudo python setup.py install

While we're at it, we can also install Robofab, DialogKit, and FontTools. You don’t need those for my scripts though:

    cd ../Robofab/
    sudo python setup.py install
    cd ../DialogKit/
    sudo python install.py
    cd ../FontTools/
    sudo python setup.py install

And if you are running Glyphs on Lion (10.7) or later, you should add:

    cd /Library/Python/
    sudo rsync -aE 2.7/site-packages/* 2.6/site-packages/


# ABOUT THE SCRIPTS

## Anchors
* **Anchor Mover 1:** GUI for moving anchors vertically in multiple glyphs. Handy for getting all top anchors right after changing your cap height. *Needs Vanilla.*
* **Anchor Mover 2:** GUI for batch-processing anchor positions in multiple glyphs. *Needs Vanilla.*
* **Combining Accent Maker:** Goes through your selected (spacing) marks and adds a combining (non-spacing) copy of it to your font, e.g., for *acute* and *dieresis.case*, it will add *acutecomb* and *dieresiscomb.case*.
* **Move top anchors:** Moves top anchors in all selected glyphs to the new_y value hardcoded in the .py file.
* **Put accents on new anchors in all layers:** Moves *acute*, *grave* and *hookabovecomb* to the *top_viet* anchor. Useful for Vietnamese double accents. Assumes that you have top_viet anchors in all layers of *circumflex*.
* **Replicate Anchors:** Goes through selected dot-suffixed glyphs and duplicates anchors from their respective base glyphs. E.g. will recreate anchors of X in X.ss01, X.swsh and X.alt.
* **Report top anchors:** Report the y positions of all *top* anchors into the Macro Panel.

## Arabic
* **AXt Converter:** converts the MacRoman glyph names (used in legacy AXt fonts) into nice names as employed by Glyphs. Attention: the script is still a work in progress. Suggestions are very welcome in the Wiki: https://github.com/mekkablue/Glyphs-Scripts/wiki/AXt-Converter

## Components
* **Delete all components:** Deletes ALL components in selected glyphs. Be careful.
* **Disable alignment:** Disables automatic alignment for all components in selected glyphs.
* **New Edit tab with compound glyphs:** Opens a new edit tab with the currently selected glyphs plus all compound glyphs containing them as components.
* **Replace components:** Relinks components in selected glyphs to a new source glyph. *Needs Vanilla.*

## Effects Scripts
* **Wackelpudding** and **Beowulferize:** Select some or all glyphs in the Font tab, then run the script. It will create alternates of the selected glyphs and create a pseudorandom calt feature. Activate it by selecting Contextual Alternates in e.g. InDesign.
* **Baseline Wiggle:** Creates a pos feature that randomly displaces the glyphs while you type.
* **Glyph Shaker:** Randomly moves each node in selected layers of selected glyphs.
* **Insert BCPs into straight segments:** Inserts offcurve points (BCPs) into straight line segments of all selected glyphs. Like option-clicking on all straight lines.
* **Retract BCPs:** Deletes all offcurve points (BCPs). Handy for making sure, your font only consists of straight lines. 
* **Turn offcurve into oncurve:** Does exactly what the name suggests. Makes fonts look really weird.

## Glyph Names:
* **Check glyph names:** Checks all available glyph names for illegal characters.
* **Lowercase:** Turns the names of selected glyphs lowercase.

## Hinting
* **Delete Hints in Visible Layers:** Deletes hints in active layers of selected glyphs.
* **Delete All Hints in Font:** Deletes all hints throughout the active font. Be careful.
* **Keep First Master Hints Only:** In selected glyphs, deletes all hints in all layers except for whatever is ordered as first master. Respects Bracket Layers. E.g., if your first master is ‘Regular’, then the script will delete hints in ‘Bold’, ‘Bold [120]’, but keep them in ‘Regular’ and ‘Regular [100]’.

## Masters
* **Copy layer to layer:** Copies paths from one Master to another. *Needs Vanilla.*
* **Dekink masters:** Dekinks your smooth transitions which are not horizontal or vertical. Select one or more angled smooth connections and run this script to move the corresponding nodes in all other masters to the same relative position. There is a video describing it: http://tinyurl.com/dekinktutorial
* **Fill up empty layers:** Copies paths from one Master to another. But only if target master is empty. *Needs Vanilla.*
* **Find and Replace in Layer Names:** Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. *Needs Vanilla.*
* **Insert instances:** GUI for calculating and inserting weight instances. *Needs Vanilla.*
* **New Edit tab with Bracket Layer glyphs:** Looks for all glyphs in the font that contain Bracket Trick Layers, and opens them in a new Edit tab.
* **Show next/previous instance:** Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut to.
* **Suggest instances:** Calculates distributions of weight values between your masters. Outputs into the macro window.

## Metrics
* **Adjust Kerning:** GUI to add a value to all kerning pairs, multiply all pairs by a value or round them by a value. *Needs Vanilla.*
* **Center glyphs:** centers all selected glyphs inside their width, so that LSB=RSB.
* **Copy kerning groups:** steals left/right kerning groups for all selected glyphs from a 2nd font. *Needs Vanilla.*
* **Copy sidebearings:** steals the sidebearing values for all selected glyphs from a 2nd font. Ignores metrics keys like ‘=x+20’. *Needs Vanilla.*
* **Delete guidelines:** deletes all local guidelines in selected glyphs.
* **Delete kerning pairs for selected glyphs:** deletes all kerning pairs with the selected glyphs, for the current master only.
* **Export Kerning CSV:** exports a CSV containing all kerning pairs (‘mastername;left;right;kerningvalue’).
* **Export Metrics CSV:** exports a CSV containing all LSB, RSB and width values (‘glyphname;mastername;LSB;RSB;width’).
* **Extract kern strings 1st char:** asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 1st letter. *Needs Vanilla.*
* **Extract kern strings 2nd char:** asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 2nd letter. *Needs Vanilla.*
* **Find and Replace Metrics Keys:** GUI for searching and replacing text in the L and R metrics keys, e.g. replace ‘=X+15’ by ‘=X’, etc.
* **Make tab with letter combos:** takes your selected glyphs and opens a new tab with all possible combinations of the letters.
* **Reset alternate glyph width:** resets the width of suffixed glyphs to the width of their unsuffixed counterparts. E.g., *Adieresis.ss01* will be reset to the width of *Adieresis*.

## OpenType
* **Floating Features:** Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. *Needs Vanilla.*
* **Make OT Class from selected glyphs:** GUI for creating a new OT class with the selected glyphs. *Needs Vanilla.*

## Paths
* All **Align** scripts look for a path in the currently active layer and align it to whatever the script title says. Useful if you need to do one of these alignment operations very often. Hint: you can set a keyboard shortcut in System Preferences.
* All **Bump** scripts move the selection towards the next available metric to the left, right, top or bottom. The Bump Left/Right scripts also include the halfwidth of the glyph. These are intended for setting a shortcut in System Preferences > Keyboard > Keyboard Shortcuts > Application Shortcuts (I recommend ctrl-opt-cmd-arrows).
* All **Distribute** scripts distribute all selected nodes horizontally or vertically, whatever is closer or what the script title says.
* All **Move** scripts move the selected glyph(s) up/down by the specified distance, similar to what (shift-)ctrl-cmd-left/rightarrow does. As shortcut, I recommend (shift-)ctrl-cmd-up/downarrow.
* **Close all paths:** Closes all open paths in the visible layers of all selected glyphs.
* **Rotate around anchor:** GUI for rotating glyphs or selections of nodes and components around a 'rotate' anchor. Allows to step and repeat. Requires Vanilla.
* **Tunnify:** Looks for all path segments where at least one handle is selected. Then, evens out the handles of the segments, i.e., they will both have the same Fit Curve percentage. Can fix Adobe Illustrator's zero-handles (segments with one handle retracted into the nearest node).

## Pixelfonts
* **Align anchors to pixelgrid:** Moves diacritic anchors onto the grid. Assumes a grid step of 50.
* **Delete components out of bounds:** If a component is placed far outside the usual coordinates (happens when you cmd-arrow components with a high grid step), this script will delete them.
* **Delete duplicate components:** Looks for duplicate components (same name and position) and keeps only one.
* **Flashify Pixels:** Creates small bridges in order to prevent self-intersection of paths so counters stay white. This is especially a problem for the Flash font renderer, hence the name of the script.
* **Re-Compose Pixels:** Tries to rebuild accidentally decomposed pixelglyphs with *pixel* components.
* **Reset rotated and mirrored components:** Looks for scaled, mirrored and rotated components and turns them back into their default scale and orientation, but keeps their position. Useful for fixing mirrored pixels.

## Smallcaps
* **Copy kerning classes from smcp to c2sc:** If you already have c2sc and smcp glyphs, it will copy kerning group attributes from smcp to c2sc glyphs, e.g. d.smcp has leftgroup=h.smcp and rightgroup=o.smcp, then leftgroup=h.smcp and rightgroup=o.smcp will be copied to D.c2sc. 
* **Make c2sc from smcp:** Creates .c2sc copies of your .smcp glyphs, with the .smcp glyphs inserted as components in the .c2sc copies. For example, if you have a.smcp, the script will create A.c2sc and insert a.smcp as component. It will not do anything in case A.c2sc already exists.
* **Make smcp from c2sc:** Creates .smcp copies of your .c2sc glyphs, with the .c2sc glyphs inserted as components in the .smcp copies. For example, if you have A.c2sc, the script will create a.smcp and insert A.c2sc as component. It will not do anything in case a.smcp already exists.

## Stylistic Sets 
* **Synchronize ssXX glyphs:** Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> the script creates *b.ss02*
* **Create ssXX from layer:** Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
* **Create pseudorandom calt feature:** Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Update: now includes the default class in the rotation algorithm.

## Test
* **Preflight Font:** Checks for a few common mistakes, like bad glyph names, and reports them to the Macro Window.