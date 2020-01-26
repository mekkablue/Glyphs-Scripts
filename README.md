# ABOUT

These are Python scripts for use with the [Glyphs font editor](http://glyphsapp.com/).

# INSTALLATION

1. Put the scripts folder (or an alias) into the *Scripts* folder which appears when you choose *Script > Open Scripts Folder* (Cmd-Shift-Y): `~/Library/Application Support/Glyphs/Scripts/`
2. Then, hold down the Option (Alt) key, and choose *Script > Reload Scripts* (Cmd-Opt-Shift-Y). Now the scripts are visible in the *Script* menu
3. For some of the scripts, you will also need to install Tal Leming's *Vanilla*: Go to *Glyphs > Preferences > Addons > Modules* and click the *Install Modules* button. That’s it.

### git

I recommend to use git for getting the scripts, and syncing them on a regular basis. Use this git command for cloning the repository into your Scripts folder:

```bash
git clone https://github.com/mekkablue/Glyphs-Scripts ~/Library/Application\ Support/Glyphs/Scripts/mekkablue/
```

And this one for updating it:

```bash
cd ~/Library/Application\ Support/Glyphs/Scripts/mekkablue/
git checkout
```

If the terminal scares you, feel free to use one of the many readily available git clients.

# TROUBLESHOOTING

Please report problems and request features [as a GitHub issue](/issues). Make sure you have the latest version of the scripts and your app is up to date. And please, always **indicate both your Glyphs and macOS version.** Thank you.

# REQUIREMENTS

The scripts require a recent version of Glyphs 2.x running on macOS 10.9 or later. I can only test them and make them work in the latest version of the software. If a script is not working for you, please first update to the latest version of the script.

# ABOUT THE SCRIPTS

> All the scripts show a tooltip when you hover the mouse pointer over their menu entry. In scripts with a GUI, most UI elements (checkboxes, text entry fields, etc.) have tooltips as well. This way you get the explanation you need right where it counts.

## Anchors

*Anchor Mover is for batch-processing anchor positions. Can be useful after adjusting the x-height. No-brainer: I always use the Reposition script on my combining marks, so stacking combining marks stays in the italic angle.*

* **Anchor Mover:** GUI for batch-processing anchor positions in multiple glyphs. *Needs Vanilla.*
* **Batch Insert Anchors:** GUI for batch-inserting anchors of the same name at the same approximate position in multiple glyphs. *Needs Vanilla.*
* **Find and Replace in Anchor Names:** GUI for replacing text in the names of anchors in selected glyphs. Processes all layers. *Needs Vanilla.*
* **Fix Arabic Anchor Order in Ligatures:** Fixes the order of *top_X* and *bottom_X* anchors to RTL. In files converted from a different format, it sometimes happens that *top_1* is left of *top_2*, but it should be the other way around, otherwise your mark2liga will mess up. This script goes through your selected glyphs, and if they are Arabic ligatures, reorders all anchors to RTL order, at the same time not touching their coordinates.
* **Insert All Anchors in All Layers:** On each layer of a selected glyph, adds all missing anchors (but present in other layers of that glyph). Puts anchors at an averaged position.
* **Insert exit and entry Anchors to Selected Positional Glyphs:** Adds entry and exit anchors for cursive attachment in selected glyphs. By default, it places the exit at (0, 0) and the entry at a node at RSB if such a node exists. Please adjust for your own needs.
* **Move ogonek Anchors to Baseline Intersection:** Moves all ogonek and _ogonek anchors to the rightmost intersection of the outline with the baseline.
* **Move topright Anchors for Vertical Carons:** Moves all topright and _topright anchors to the rightmost intersection of the outline with the x-height. Useful for building Czech/Slovak letters with vertical caron.
* **Move Vietnamese Marks to top_viet Anchor in Circumflex:** Moves *acute*, *grave* and *hookabovecomb* to the *top_viet* anchor in every layer of selected glyphs. Useful for Vietnamese double accents. Assumes that you have *top_viet* anchors in all layers of *circumflexcomb*.
* **New Tab with Glyphs Containing Anchor:** Opens a new tab with all glyphs containing a specific anchor.
* **New Tab with top and bottom Anchors Not on Metric Lines:** Report the y positions of all *top* and *bottom* anchors into the Macro Panel, and opens new tabs with all glyphs that have a stray anchor on any of the master, bracket or brace layers of any glyph in the font. Ignores the user selection, and analyses all glyphs, exporting and non-exporting. Useful to see if a top anchor is not exactly where it should be.
* **Prefix all exit/entry anchors with a hashtag:** Looks for all exit and entry anchors anywhere in the font, and disables `curs` feature generation by prefixing their anchor names with `#`.
* **Remove Anchors in Suffixed Glyphs:** Removes all anchors from glyphs with one of the user-specified suffix. Useful for removing left-over anchors in sups/subs/sinf/ordn variants of glyphs after copying, scaling and editing. *Needs Vanilla.*
* **Remove Anchors:** Deletes anchors with a specified name in selected glyphs (or the whole font). *Needs Vanilla.*
* **Remove Non-Standard Anchors from Selected Glyphs:** Removes all anchors from a glyph that should not be there by default, e.g., `ogonek` from `J`. Potentially dangerous, because it may delete false positives. So, first use the report script below.
* **Replicate Anchors in Suffixed Glyphs:** Goes through selected dot-suffixed glyphs and duplicates anchors from their respective base glyphs. E.g. will recreate anchors of *X* in *X.ss01*, *X.swsh* and *X.alt*.
* **Report Non-Standard Anchors to Macro window:** Goes through all glyphs in the font and reports in the Macro window if it finds non-default anchors. Lines are copy-pasteable in Edit view.
* **Reposition top and bottom Anchors in Combining Accents:** In stacking combining accents, moves top and bottom anchors exactly above or below the respective _top and _bottom anchors, respecting the italic angle. This way, stacking multiple nonspacing accents will always stay in line.

## App

*If you are coding, add a keyboard shortcut for Method Reporter, you will need this a lot. Print Window can come in handy if you want a resolution-independent PDF screenshot of your window content. Best for post-processing in a vector illustration app.*

* **Line Height Decrease** and **Line Height Increase:** Increases the Edit View line height by a quarter, or decreases it by a fifth. Useful for setting shortcuts if you need to switch between line heights a lot.
* **Method Reporter:** GUI for filtering through the method names of Python and PyObjC Classes available from within Glyphs. You can use multiple space-separated search terms (for an AND concatenation) and asterisk as jokers (at the beginning, in the middle and at the end). Double click to put the method name in your clipboard and open help in the Macro window. Useful for coders. *Needs Vanilla.*
* **Parameter Reporter:** Like Method Reporter, but for custom parameters. Double click to copy a prameter in the clipboard, ready for pasting in Font Info. *Needs Vanilla.*
* **Print Window:** Print the frontmost window. Useful for saving a vector PDF of your window content, including the renderings of reporter plug-ins (extensions for the *View* menu).
* **Set Export Paths to Adobe Fonts Folder:** Sets the OpenType font and Variable Font export paths to the Adobe Fonts Folder.
* **Set Hidden App Preferences:** GUI for reading and setting ‘hidden’ app preferences, which are not listed in the GUI. *Needs Vanilla.*
* **Set Tool Shortcuts:** Set keyboard shortcuts for the tools in the toolbar. *Needs Vanilla.*
* **Toggle RTL-LTR:** Toggle frontmost tab between LTR and RTL writing direction. Useful for setting a keyboard shortcut in System Preferences.
* **Update git Repositories in Scripts Folder:** Executes a 'git pull' command on all subfolders in the Glyphs Scripts folder. Useful if you have a lot of git repos in your Scripts folder.

## Build Glyphs

*Most important: Quote Manager, and the Build scripts for Small Figures, notdef, Ldot, estimated/bar/brokenbar. The other scripts are mainly intended to give you a quick head start for covering certain Unicode ranges if requested by the client.*

* **Build APL Greek:** Create APL Greek glyphs.
* **Build careof and cadauna:** Builds cadauna and careof from your c, u and fraction glyphs.
* **Build Circled Glyphs:** Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from _part.circle and your letters and figures.
* **Build Dotted Numbers:** Build dotted numbers from your default figures and the period.
* **Build estimated, bar, brokenbar:** Creates an estimated glyph and draws an estimated sign in it. Does the same for bar and brokenbar, for which it respects standard stems and italic angle. Does not overwrite existing glyphs.
* **Build Extra Math Symbols:** Builds lessoverequal, greateroverequal, bulletoperator, rightanglearc, righttriangle, sphericalangle, measuredangle, sunWithRays, positionIndicator, diameterSign, viewdataSquare, control.
* **Build Ldot and ldot:** Builds Ldot, ldot and ldot.sc from existing L and periodcentered.loclCAT(.case/.sc). Assumes that you have already created and properly spaced L-periodcentered.loclCAT-L, etc.
* **Build notdef:** Creates a .notdef from your boldest available question mark.
* **Build Parenthesized Glyphs:** Creates parenthesized letters and numbers: one.paren, two.paren, three.paren, four.paren, five.paren, six.paren, seven.paren, eight.paren, nine.paren, one_zero.paren, one_one.paren, one_two.paren, one_three.paren, one_four.paren, one_five.paren, one_six.paren, one_seven.paren, one_eight.paren, one_nine.paren, two_zero.paren, a.paren, b.paren, c.paren, d.paren, e.paren, f.paren, g.paren, h.paren, i.paren, j.paren, k.paren, l.paren, m.paren, n.paren, o.paren, p.paren, q.paren, r.paren, s.paren, t.paren, u.paren, v.paren, w.paren, x.paren, y.paren, z.paren.
* **Build Q from O and _tail.Q:** Run this script *after* doing *Component from Selection* on the Q tail and naming it `_tail.Q`.
* **Build Small Figures:** Takes a default set of figures (e.g., dnom), and derives the others (.numr, superior/.sups, inferiour/.sinf, .subs) as component copies. Respects the italic angle.
* **Build small letter SM, TEL:** Creates the glyphs: `servicemark`, `telephone`.
* **Build space glyphs:** Creates mediumspace-math, emquad, emspace, enquad, enspace, figurespace, fourperemspace, hairspace, narrownbspace, punctuationspace, sixperemspace, nbspace, thinspace, threeperemspace, zerowidthspace.
* **Quote Manager:** Build double quotes from single quotes, and insert #exit and #entry anchors in the single quotes for auto-alignment. You need to have the single quotes already. *Needs Vanilla.*

## Color Fonts

*These scripts are for situations you will encounter in a Color Font workflow. The Merge script is mainly for creating a fallback glyph for CPAL/COLR fonts. This way the fallback has the full bbox, and no clipping will occur in Chrome.*

* **Convert Layerfont to CPAL+COLR Font:** Turns a layered color font into a single-master font with a CPAL and COLR layers in each glyph. It will take the first master as default.
* **Delete Non-Color Layers in Selected Glyphs:** Deletes all sublayers in all glyphs that are not of type "Color X" (CPAL/COLR layers).
* **Merge All Other Masters in Current Master:** In selected glyphs, copies all paths from other masters onto the current master layer.

## Compare Frontmost Fonts

*These scripts are intended for syncing uprights with their italics. Open two fonts, and run the scipts. They do not change your fonts, but report in detail in the Macro window.*

* **Compare Font Info > Font:** Detailed report of Font Info > Masters for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Masters:** Detailed report of Font Info > Masters for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Instances:** Detailed report of Font Info > Instances for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Features:**  Compares the OT features set of the two frontmost fonts and outputs a report in the Macro window.
* **Compare Anchors:** Compares anchor structure and anchor heights between the two frontmost fonts.
* **Compare Compounds:** Reports diverging component structures of compound glyphs, e.g., iacute built with acutecomb in one font, and acutecomb.narrow in the other.
* **Compare Glyph Heights:** Lists all glyphs that differ from the second font in height beyond a given threshold.
* **Compare Glyphsets:** Compares the glyph set of the two frontmost fonts and outputs a report in the Macro window.
* **Compare Kerning Groups:** Compares kerning groups between frontmost fonts, outputs a table of glyph names with unmatching groups.
* **Compare Metrics:** Compare widths of two frontmost fonts.
* **Compare Sidebearings:** Compare sidebearings of two frontmost fonts.

## Components

*Populate Backgrounds with Components is very useful when you build letters based on other, e.g., ae or oe can take an e in the background. The script puts the e in the background of each master, and the UI has an option to align selected points with the e in the background. If you use corner components for serifs in a multiple-master font, the Propagate script will save you a lot of time.*

* **Alignment Manager:** Enables or disables automatic alignment for all components on visible layers in selected glyphs. Does the same as the command in the context menu, but you can do it in one step for many glyphs. *Needs Vanilla.*
* **Decompose Components in Background:** Decomposes background layers of selected glyphs. Only works on the current master.
* **Decompose Corner and Cap Components:** Decomposes all corner and cap components in selected glyphs. Reports to Macro window.
* **Find and Replace Components:** Relinks components in selected glyphs to a new source glyph. *Needs Vanilla.*
* **Find and Replace Cap and Corner Components:** Relinks `_cap.*` and `_corner.*` components in selected glyphs to a different corner/cap component. *Needs Vanilla.*
* **Find and Replace Corner Components at Certain Angles:** Replace Corner Components at blunt or acute angles. *Needs Vanilla.*
* **New Tab with Composable Glyphs that have no Components:** Opens a new Edit tab containing all glyphs that consist of paths, but could be composed according to Glyph Data.
* **New Tab with Orphaned Components:** Opens a new tab in the current font window containing all glyphs (of the current master) that have components that point to non-existent glyphs, i.e., no base glyphs.
* **New Tab with Transformed Components:** Opens a new tab containing all compound glyphs that have mirrored, or rotated, or scaled components.
* **New Tab with Transformed Corner Components:** Opens a new Edit tab containing all glyphs with scaled corner components.
* **New Tab with Unusual Compounds:** Open a new tab containing all compound glyphs that have an unusual component order or an unorthodox component structure. Useful for finding wrong component orders.
* **Populate Backgrounds with Components:** Removes the specified component from all glyphs or all selected glyphs. *Needs Vanilla.*
* **Propagate Corner Components to Other Masters:** Tries to recreate the corner components of the current master layer in all other masters of the same glyph. Make sure your outlines are compatible.
* **Remove Components:** Removes the specified component from all (selected) glyphs.
* **Stitcher:** In selected glyphs, the Stitcher inserts components on your paths at fixed intervals. Useful for turning open paths (monolines) into dotted lines. Use an anchor called 'origin' for determining the component position in stitched letters. *Needs Vanilla.*
* **Sync Components Across Masters:** Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors.

## Features

*In script typefaces, you may often need the Build Positional calt script. If you find yourself turning OT features on and off a lot, take a look at the Activate Default Features and Floating Features scripts. And check out the Set Palette from Window > Plugin Manager.*

* **Activate Default Features:** In the current Edit tab, activates all OT features that are recommended to be on by default (according to the spec).
* **Build Italic Shift Feature:** Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature. *Needs Vanilla.*
* **Build Positional calt Feature:** Looks for .init, .medi, .fina, and .isol glyphs, and injects positional substitution code into your calt feature. If run again, will update its class and feature code. See this tutorial for more info: https://glyphsapp.com/tutorials/features-part-4-positional-alternates
* **Feature Code Tweaks:** Adds tweaks to OT feature code. Reports in Macro window. Careful: if you do not understand an option, do not use it. *Needs Vanilla.*
* **Floating Features:** Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. *Needs Vanilla.*
* **Fraction Fever 2:** Insert Tal Leming’s Fraction Fever 2 code into the font. Read more in this tutorial: https://glyphsapp.com/tutorials/fractions
* **New OT Class with Selected Glyphs:** GUI for creating a new OT class with the selected glyphs. *Needs Vanilla.*
* **New Tab with OT Class:** GUI for opening all glyphs in an OT class (listed in *File > Font Info > Features > Classes*) in a new tab. *Needs Vanilla.*
* **Update Features without Reordering:** Goes through the existing features in the font and refreshes each one of them. Does neither add nor reorder features.
* * **Stylistic Sets > Synchronize ssXX glyphs:** Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> the script creates *b.ss02*
* * **Stylistic Sets > Create ssXX from layer:** Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
* * **Stylistic Sets > Create pseudorandom calt feature:** Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Also includes the default class in the rotation algorithm.
* * **Stylistic Sets > Set ssXX Names:** Prefills names for ssXX features with ‘Alternate’ or another chosen text, plus the name of the first substituted glyph, e.g., ‘Alternate a’. Option to preserve existing namings.*Needs Vanilla.*

## Font Info

*Vertical Metrics is useful for finding and syncing the vertical metric parameters in Font Info > Font and Font Info > Masters. Clean Version String is probably the most important one in this category. Careful about Set WWS/Preferred Names scripts: The app usually takes care of naming automtaically, so their use cases are very rare.*

* **Clean Version String:** Adds a clean versionString parameter, and disables ttfAutohint info in the version string. The exported font will have a version string consisting only of ‘Version X.XXX’.
* **Find and Replace In Instance Parameters:** Finds and Replace in Custom Parameters of selected instances of the current font or project file.
* **Font Info Overview:** Lists some Font Info values for all opened fonts.
* **Set Preferred Names (Name IDs 16 and 17)  for Width Variants:** Sets Preferred Names custom parameters (Name IDs 16 and 17) for all instances, so that width variants will appear in separate menus in Adobe apps. 
* **Set Style Linking:** Attempts to set the Bold/Italic bits.
* **Set Time of Font Date to High Noon:** In the *Creation Date* in *Font Info > Font,* sets the time (invisible in the UI) to 12:00:00 o’clock.
* **Set WWS Names (Name IDs 21 and 22):** Sets WWS custom parameters (Name IDs 21 and 22) for all instances where necessary: Puts all info except RIBBI into the WWSFamilyName, and only keeps RIBBI for the WWSSubfamilyName. 
* **Vertical Metrics Manager:** Calculate and insert values for OS/2 usWin and sTypo, hhea and fsSelection bit 7 (for preferring sTypo Metrics over usWin metrics). *Needs Vanilla.*

## Glyph Names, Notes and Unicode

*Most scripts make managing glyph names and Unicodes a little easier. Garbage Collection is useful for cleaning up the mess of the reporter scripts, or other annotations before you hand the files over to a third party.*

* **Add PUA Unicode Values to Selected Glyphs:** Iterates through selected glyphs and incrementally applies custom Unicode values, starting at a user-specified value. *Needs Vanilla.*
* **Convert to Capitalised:** Turns lowercase names into uppercase names, e.g., `a` → `A`, `ccaron` → `Ccaron`, `aeacute` → `AEacute`, etc.
* **Convert to Lowercase:** Turns the names of selected glyphs lowercase.
* **Garbage Collection:** Removes markers in glyphs, such as node names, glyph names or annotations, as well as guides.
* **New Tab with Uppercase-Lowercase Inconsistencies:** Opens a new Edit tab containing all glyphs without consistent case folding. Writes a detailed report in Macro Window.
* **Rename Glyphs:** Takes a list of `oldglyphname=newglyphname` pairs and renames glyphs in the font accordingly, much like the *Rename Glyphs* custom parameter. *Needs Vanilla.*
* **Reorder Unicodes of Selected Glyphs:** Reorders Unicodes so that default Unicode comes first. Glyphs 2.5+ only.

## Guides

*These scripts are mostly intended for cleaning up the plethora of guides I see when working on third-party fonts.*

* **Guides through All Selected Nodes:** Lays guides through all selected nodes in current glyph. Tries to avoid duplicate guides.
* **Remove Global Guides in Current Master:** Deletes all global (red) guides in the current master.
* **Remove Local Guides in Selected Glyphs:** Deletes all local (blue) guides in selected glyphs.
* **Select All Local Guides:** Selects all local (blue) guides (in all selected glyphs).

## Hinting

*Most important: Set blueScale, Set Family Alignment Zones for PostScript hinting. If you are making big changes, The Transfer and Keep Only scripts can save you a lot of work. The New Tab scripts help find glyphs missing zones. Also consider Paths > Find Near Vertical Misses for that purpose.*

* **Add Hints for Selected Nodes:** Adds hints for the selected nodes. Tries to guess whether it should be H or V. If exactly one node inside a zone is selected, it will add a Ghost Hint. Useful for setting a shortcut in System Prefs.
* **Add TTF Autohint Control Instructions for Current Glyph:** Adds a touch line for a given up/down amount to the Control Instructions of the current instance. *Needs Vanilla.*
* **BlueFuzzer:** Extends all alignment zones by the specified value. Similar to what the blueFuzz value used to do, hence the name. *Needs Vanilla.*
* **Keep Only First Master Hints:** In selected glyphs, deletes all hints in all layers except for whatever is ordered as first master. Respects Bracket Layers. E.g., if your first master is 'Regular', then the script will delete hints in 'Bold', 'Bold [120]', but keep them in 'Regular' and 'Regular [100]'.
* **New Tab with Glyphs in Alignment Zones:** Opens a new tab and lists all glyphs that reach into alignment zones.
* **New Tab with Glyphs Not Reaching Into Zones:** Opens a new tab with all glyphs that do NOT reach into any top or bottom alignment zone. Only counts glyphs that contain paths in the current master. Ignores empty glyphs and compounds.
* **Remove PS Hints:** Deletes all stem and/or ghost hints throughout the current font, the selected master and/or the selected glyphs. *Needs Vanilla.*
* **Remove Zero Deltas in Selected Glyphs:** Goes through all layers of each selected glyph, and deletes all TT Delta Hints with an offset of zero. Detailed Report in Macro window.
* **Set blueScale:** Sets maximum blueScale value (determining max size for overshoot suppression) possible in Font Info > Font. Outputs other options in Macro window.
* **Set Family Alignment Zones:** Pick an instance and set its zones as Family Alignment Zones in *Font Info > Font > Custom Parameters.* *Needs Vanilla.*
* **Set TT Stem Hints to Auto:** Sets all TT stem hints to ‘auto’ in selected glyphs.
* **Set TT Stem Hints to No Stem:** Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.
* **Set TTF Autohint Options:** Set options for existing 'TTF Autohint Options' Custom Parameters. *Needs Vanilla.*
* **Transfer Hints to First Master:** Copies PS hints from the current layer to the first master layer, provided the paths are compatible. Reports errors to the Macro window.
* **TT Autoinstruct:** Automatically add Glyphs TT instructions to the selected glyphs in the selected master. (Should be the first master.) Attention: this is NOT Werner Lemberg's ttfAutohint, but the manual TT hints that the TT Instruction tool (I) would add through the context menu item of the same name. Useful for adding hints in many glyphs at once.

## Images

*Mainly intended for curing the headaches you may undergo when handling a lot of (background) images.*

* **Add Same Image to Selected Glyphs:** Asks you for an image, and then inserts it into all currently selected glyphs as background image.
* **Adjust Image Alpha:** Slider for setting the alpha of all images in selected glyphs. *Needs Vanilla.*
* **Delete All Images in Font:** Deletes all placed images throughout the entire font.
* **Delete Images:** Deletes all images placed in the visible layers of selected glyphs.
* **Reset Image Transformation:** Resets all image transformations (x/y offset, scale, and distortion) back to default in the visible layers of selected glyphs.
* **Set New Path for Images:** Resets the path for placed images in selected glyphs. Useful if you have moved your images.
* **Toggle Image Lock:** Lock or unlock all images in all selected glyphs. *Needs Vanilla.*
* **Transform Images:** GUI for batch-transforming images (x/y offset and x/y scale) in the visible layers of selected glyphs. *Needs Vanilla.*

## Interpolation

*Most important: Insert Instances (for determining your instances and their style linking), Kink Finder and Find Shapeshifting Glyphs. I use Show Next/Previous Instance with the keyboard shortcut ctrl-up/down a lot.*

* **Compund Variabler:** Reduplicates Brace and Bracket layers of components in the compounds in which they are used. Makes brace and bracket layers work in the compounds. *Needs Vanilla.*
* **Copy Layer to Layer:** Copies paths (and optionally, also components, anchors and metrics) from one Master to another. *Needs Vanilla.*
* **Dekink Masters:** Dekinks your smooth point triplets in all compatible layers (useful if they are not horizontal or vertical). Select a point in one or more smooth point triplets, and run this script to move the corresponding nodes in all other masters to the same relative position. Thus you achieve the same point ratio in all masters and avoid interpolation kinks, when the angle of the triplet changes. There is a [video describing it.](http://tinyurl.com/dekink-py) The triplet problem is [described in this tutorial](http://www.glyphsapp.com/tutorials/multiple-masters-part-2-keeping-your-outlines-compatible).
* **Fill up Empty Masters:** Copies paths from one Master to another. But only if target master is empty. *Needs Vanilla.*
* **Find and Replace in Layer Names:** Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. *Needs Vanilla.*
* **Find Shapeshifting Glyphs:** Finds glyphs that change the number of paths while interpolating. Opens a new tab and reports to Macro window. *Needs Vanilla.*
* **Insert Brace Layers for Component Rotation:** Inserts a number of Brace Layers with continuously scaled and rotated components. Useful for OTVar interpolations with rotating elements. *Needs Vanilla.*
* **Insert Brace Layers for Movement along Background Path:** Inserts a number of Brace Layers with copies of the first layer, shifted according to the first path in the background. Useful for OTVar interpolations with moving elements.
* **Insert Instances:** GUI for calculating and inserting weight instances. It is described in this tutorial: https://www.glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances *Needs Vanilla.*
* **Kink Finder:** Finds kinks in outlines or the interpolation space, reports them in the Macro window and opens a new tab with affected glyphs. Kinks are described in this tutorial: https://glyphsapp.com/tutorials/multiple-masters-part-2-keeping-your-outlines-compatible *Needs Vanilla.*
* **New Tab with Dangerous Glyphs for Interpolation:** Opens a tab with all glyphs in the font that contain at least two compatible elements. I.e., glyphs where an element (a path or a component) could interpolate with the wrong element, like the equals sign. For a detailed description, see section *Be suspicious* in this tutorial: <http://www.glyphsapp.com/tutorials/multiple-masters-part-2-keeping-your-outlines-compatible>.
* **New Tab with Special Layers:** Quickly adds a new edit tab with all glyphs containing brace and bracket layers.
* **New Tab with Uneven Handle Distributions:** Finds glyphs where handle distributions change too much (e.g., from balanced to harmonised). *Needs Vanilla.*
* **OTVar Player:** Animates the current glyph with a loop along the weight axis. *Needs Vanilla.*
* **Remove All Non-Master Layers:** Deletes all layers which are neither master layers, nor brace layers, nor bracket layers. Useful for getting rid of backup layers.
* **Short Segment Finder:** Goes through all interpolations and finds segments shorter than a user-specified threshold length. *Needs Vanilla.*
* **Travel Tracker:** Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes. The results are incomplete, and usually have many false positives, but it sometimes finds cases that the Shapeshifter script misses. *Needs Vanilla.*
* **Variation Interpolator:** Creates a user-defined number of glyph variations with a user-defined suffix, containing interpolations between the layers and their respective backgrounds. Overwrites glyphs with same name. Similar to Pablo Impallari’s SimplePolator. Useful for e.g. length variants of Devanagari Matra, see José Nicolás Silva Schwarzenberg’s sample video: <https://www.youtube.com/watch?v=QDbaUlHifBc>. *Needs Vanilla.*
* * **Other > Lines by Master:** Reduplicates your edit text across masters, will add one line per master in Edit view. Careful, ignores everything after the first newline. Intended for adding a keyboard in System Preferences.
* * **Other > Show Masters of Next/Previous Glyph:** Allows you to step through one glyph after another, but with all masters. Combines the show next/previous glyph function (fn+left/right) with the *Edit > Show All Masters* function. Handy for attaching a keyboard shortcut in System Preferences.
* * **Other > Show Next/Previous Instance:** Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut in System Preferences.


## Kerning

*Most important: Auto Bumper, KernCrasher, GapFinder, Sample String Maker. If you have too much kerning, consider Exception Cleaner.*

* **Adjust Kerning in Master:** GUI to add a value to all kerning pairs, multiply all pairs by a value or round them by a value. *Needs Vanilla.*
* **Auto Bumper:** Specify a minimum distance, left and right glyphs, and Autokern will add the minimum necessary kerning for the current master. *Needs Vanilla.*
* **Copy Kerning Exceptions to Double Accents:** Copies Kerning exceptions with abreve, `acircumflex`, `ecircumflex`, `ocircumflex`, `udieresis` into Vietnamese and Pinyin double accents.
* **Exception Cleaner:** Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception. *Needs Vanilla.*
* **Find and Replace in Kerning Groups:** GUI for searching and replacing text in the L and R Kerning Groups, e.g. replace 'O' by 'O.alt'. Leave the search field blank for appending. *Needs Vanilla.*
* **GapFinder:** Opens a new tab with kerning combos that have large gaps in the current fontmaster. *Needs Vanilla.*
* **Import Kerning from .fea File:** Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see *Window > Kerning*).
* **KernCrash Current Glyph:** Opens a new tab containing kerning combos with the current glyph that collide in the current fontmaster.
* **KernCrasher:** Opens a new tab with Kerning Combos that crash in the current fontmaster. *Needs Vanilla.*
* **New Tab with All Group Members:** Select two glyphs, e.g. ‘Ta’, run the script, and it will open a new tab with all combinations of the right kerning group of T with the left kerning group of a.
* **New Tab with Glyphs of Same Kerning Groups:** Opens a new tab containing all members of the left and right kerning groups of the current glyph.
* **New Tab with Kerning Missing in Masters:** Opens New Tabs for each master showing kerning missing in this master but present in other masters.
* **New Tab with Large Kerning Pairs:** Lists all positive and negative kerning pairs beyond a given threshold. *Needs Vanilla.*
* **New Tab with Overkerned Pairs:** Asks a threshold percentage, and opens a new tab with all negative kern pairs going beyond the width threshold. Example: With a threshold of 40%, and a comma with width 160, the script will report any negative kern pair with comma larger than 64 (=40% of 160). Assume that r-comma is kerned -60, and P-comma is kerned -70. In this case, it would report the latter, but not the former. *Needs Vanilla.*
* **New Tab with Right Groups:** Creates a new tab with one glyph of each right group. Useful for checking the constency of right kerning groups.
* **New Tab with all Selected Glyph Combinations:** Takes your selected glyphs and opens a new tab with all possible combinations of the letters. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Uneven Symmetric Kernings:** Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
* **New Tabs with Punctuation Kern Strings:** Outputs several tabs with kern strings with punctuation.
* **Remove all Kerning Exceptions:** Removes all kerning for the current master, except for group-to-group kerning. Be careful.
* **Remove Kerning Between Categories:** Removes kerning between glyphs, categories, subcategories, scripts. *Requires Vanilla.*
* **Remove Kerning Pairs for Selected Glyphs:** Deletes all kerning pairs with the selected glyphs, for the current master only.
* **Remove Orphaned Group Kerning:** Deletes all group kernings referring to groups that are not in the font.
* **Remove Small Kerning Pairs:** Removes all kerning pairs in the current font master with a value smaller than specified, or a value equal to zero. Be careful. *Needs Vanilla.*
* **Report Kerning Mistakes:** Tries to find unnecessary kernings and groupings. Reports in Macro window, for reviewing.
* **Sample String Maker:** Creates kern strings for user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored. *Needs Vanilla.*
* **Set Kerning Groups:** Sets left and right kerning groups for all selected glyphs. In the case of compounds, will use the groups of the base components, otherwise makes an informed guess based on a built-in dictionary.
* **Steal Kerning from InDesign:** Steals the kerning from text set in InDesign. Useful for extracting InDesign’s Optical Kerning values.
* **Steal Kerning Groups from Font:** Steals left/right kerning groups for all selected glyphs from a 2nd font. *Needs Vanilla.*
* **Zero Kerner:** Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports. *Needs Vanilla.*

## Paths

*I use Rotate Around Anchor for my asterisks. Important for outline checking: Find Near Vertical Misses and the Green Blue Manager (in combination with Realign BCPs). Rewire Fire has become important in OTVar production, because it helps reduce duplicate outline segments at shape edges, which may yield darker anti-aliasing.*

* **Align Selected Nodes with Background:** Align selected nodes with the nearest background node unless it is already taken by a previously moved node. Like Cmd-Shift-A for aligning a single node with the background, but for multiple nodes.
* **Copy Glyphs from Other Font into Backup Layers:** Creates backup layers for selected glyphs in target font, and fills them with the respective glyphs from source font. Useful if you want to add glyphs from one font as bracket layers in another. *Needs Vanilla.*
* **Distribute Nodes:** Horizontally or vertically distributes nodes (depends on the width/height ratoi of the selection bounding box).
* **Enlarge Single-Unit Segments:** Doubles the length of line segments shorter than one unit.
* **Fill Up with Rectangles:** Goes through your selected glyphs, and if it finds an empty one, inserts a placeholder rectangle. Useful for quickly building a dummy font for testing.
* **Find Near Vertical Misses:** Finds nodes that are close but not exactly on vertical metrics. *Needs Vanilla.*
* **Green Blue Manager:** Define an angle above which a node will be set to blue, below which it will be set to green. *Needs Vanilla.*
* **Grid Switcher:** Toggles grid between two user-definable gridstep values with the click of a floating button. *Needs Vanilla.*
* **Harmonise Curve to Line:** Will rearrange handles on (selected) curve segments with a following line segment, in such a way that the transition between the two segments is smooth (harmonized).
* **New Tab with Offcurves as Start Points:** Opens a new tab with all glyphs that contain paths where the first point is an offcurve.
* **New Tab with Path Problems:** Opens a new tab with glyphs containing zero handles, bad outline orders or path directions. Only opens master layers in tabs. Full layer report (including non-master layers) in the Macro window log.
* **New Tab with Shallow Segments:** Opens a new tab with all layers that have small outline segments, i.e., not extending far enough horizontally or vertically.
* **New Tab with Short Segments:** Goes through all glyphs in the present font(s), and reports segments shorter than a user-specified distance to the Macro window, and opens a new tab with affected glyphs. Useful for finding alignment errors in exported OTFs. *Needs Vanilla.*
* **New Tab with Small Paths:** Opens a new tab containing paths that are smaller than a user-definable threshold size in square units.
* **Realign BCPs:** Realigns all BCPs in all selected glyphs. Useful if handles got out of sync, e.g. after nudging or some other transformation, or after interpolation. Hold down Option to apply to all layers of the selected glyph(s).
* **Remove all Open Paths:** Deletes all *open* paths in the visible layers of all selected glyphs.
* **Remove Nodes and Try to Keep Shape:** Deletes selected on-curve nodes and tries to keep the shape as much as possible. Similar to what happens when you delete a single node, but for a selection of multiple nodes. Pro tip: Hold down the Shift key while running the script, and it will also balance the remaining handles as much as possible, which is exactly what happens when you delete a single node.
* **Remove Short Segments:** Deletes segments shorter than one unit.
* **Remove Stray Points:** Deletes stray points (single node paths) in selected glyphs. Careful: a stray point can be used as a quick hack to disable automatic alignment. Reports in detail to the Macro window.
* **Rewire Fire:** Finds, selects and marks duplicate coordinates. Two nodes on the same position typically can be rewired with Reconnect Nodes. *Needs Vanilla.*
* **Rotate Around Anchor:** GUI for rotating glyphs or selections of nodes and components around a 'rotate' anchor. Allows to step and repeat. *Needs Vanilla.*
* **Set Transform Origin:** Simple GUI for setting the Transform Origin of the Rotate tool numerically. Should also have an effect on the Scale tool. *Needs Vanilla.*
* **Straight Stem Cruncher:** Finds distances between points in all layers, and compares them (with a tolerance) to specified stem widths. Lists glyphs that have deviating stems in their drawings. *Needs Vanilla.*
* **Tunnify:** Looks for all path segments where at least one handle is selected. Then, evens out the handles of the segments, i.e., they will both have the same Fit Curve percentage. Can fix Adobe Illustrator's zero-handles (segments with one handle retracted into the nearest node). The idea for this script came from Eduardo Tunni (as colported by Pablo Impallari), hence the title of the script. I have never seen Eduardo's algorithm though, so my implementation might be a little different to his, especially the treatment of zero-handles.

## Pixelfonts

*These scripts are useful for a pixelfont workflow, where you place a pixel component in a coarser grid.*

* **Align Anchors to Grid:** Snaps diacritic anchors onto the font grid.
* **Delete Components out of Bounds:** If a component is placed far outside the usual coordinates (happens when you cmd-arrow components with a high grid step), this script will delete them.
* **Delete Duplicate Components:** Looks for duplicate components (same name and position) and keeps only one. Happens frequently when buliding pixel fonts.
* **Flashify Pixels:** Creates small bridges in order to prevent self-intersection of paths so counters stay white. This is especially a problem for the Flash font renderer, hence the name of the script.
* **Reset Rotated and Mirrored Components:** Looks for scaled, mirrored and rotated components and turns them back into their default scale and orientation, but keeps their position. Useful for fixing mirrored pixels.

## Smallcaps

*When I have Smallcaps in my font, I always run Check Smallcap Consistency. Take its report with a grain of salt though: it lists a lot of false positives, and not every warning is equally important.*

* **Check Smallcap Consistency:** Performs a few tests on your SC set and reports into the Macro window, especially kerning groups and glyph set.
* **Copy Kerning from Caps to Smallcaps:** Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.

## Spacing

*Most important: Fix Math Operator Spacing, Bracket Metrics Manager and, if you have arrows, Fix Arrow Positioning. The New Tab scripts are useful when creating figures.*

* **Bracket Metrics Manager:** Manage the sidebearings and widths of bracket layers, e.g., dollar and cent. *Needs Vanilla.*
* **Center Glyphs:** Centers all selected glyphs inside their width, so that LSB=RSB.
* **Change Metrics by Percentage:** Change LSB/RSB of selected glyphs by a percentage value. Undo with the Revert button. *Needs Vanilla.*
* **Find and Replace in Metrics Keys:** GUI for searching and replacing text in the L and R metrics keys, e.g. replace '=X+15' by '=X'. Leave the search field blank for appending.
* **Fix Arrow Positioning:** Fixes the placement and metrics keys of arrows, dependent on a specified default arrow. Adds metric keys and moves arrows vertically. Does not create new glyphs, only works on existing ones. *Needs Vanilla.*
* **Fix Math Operator Spacing:** Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also lesser/greater symbols and asciicircum/asciitilde. *Needs Vanilla.* 
* **Freeze Placeholders:** In the current Edit tab, will change all inserted placeholders for the current glyph, thus 'freeze' the placeholders.
* **Metrics Key Manager:** Batch apply metrics keys to the current font. *Needs Vanilla.*
* **New Tab with all Figure Combinations:** Opens a new tab with all possible figure combos. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Fraction Figure Combinations:** Opens an Edit tab with fraction figure combos for spacing and kerning.
* **Remove Layer-Specific Metrics Keys:** Deletes left and right metrics keys specific to layers (==), in all layers of all selected glyphs. Also simplifies glyph metrics keys (i.e., turns "=H" into "H").
* **Remove Metrics Keys:** Deletes both left and right metrics keys in all selected glyphs. Affects all masters and all layers.
* **Reset Alternate Glyph Widths:** Resets the width of suffixed glyphs to the width of their unsuffixed counterparts. E.g., *Adieresis.ss01* will be reset to the width of *Adieresis.*
* **Spacing Checker:** Look for glyphs with unusual spacings and open them in a new tab. *Needs Vanilla.*
* **Steal Metrics:** Steals the sidebearing or width values for all selected glyphs from a 2nd font. Optionally also transfers metrics keys like '=x+20'. *Needs Vanilla.*
* **Tabular Checker:** Goes through tabular glyphs and checks if they are monospaced. Reports exceptions. *Needs Vanilla.*

## Test

*Most important: the Test HTML scripts. If you have unusually high or low text selection highlights in Adobe or Apple apps, run Report Highest and Lowest Glyphs to find the glyph causing it. Language Report is just for beefing up your specimen, and will not give you authoritative information.*

* **Copy InDesign Test Text:** Copies a test text for InDesign into the clipboard.
* **Copy Word Test Text:** Copies a test text for MS Word into the clipboard.
* **Language Report:** Tries to give you a preliminary idea about how many and which languages are supported with your Latin characters. Based on Underware’s Latin-Plus list, with modifications.
* **Pangram Helper:** Helps you write a pangram, which you can copy into the clipboard, or put into a new tab. *Needs Vanilla.*
* **Report Highest and Lowest Glyphs:** Reports glyphs with highest and lowest bounding boxes for all masters.
* **Variable Font Test HTML:** Create a Test HTML for the current font inside the current Variation Font Export folder.
* **Webfont Test HTML:** Creates a Test HTML for the current font inside the current Webfont Export folder, or for the current Glyphs Project in the project’s export path.


# License

Copyright 2011 The mekkablue Glyphs-Scripts Project Authors.

Some code samples by Georg Seifert (@schriftgestalt) and Tal Leming (@typesupply).

Some algorithm input by Christoph Schindler (@hop) and Maciej Ratajski (@maciejratajski).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the software provided here except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.
