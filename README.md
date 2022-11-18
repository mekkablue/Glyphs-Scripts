# ABOUT

These are Python scripts intended for font production in the [Glyphs font editor](http://glyphsapp.com/).

# INSTALLATION

## Glyphs 3

1. **Install the modules:** In *Window > Plugin Manager,* click on the *Modules* tab, and make sure at least the [Python](glyphsapp3://showplugin/python) and [Vanilla](glyphsapp3://showplugin/vanilla) modules are installed. If they were not installed before, restart the app.
2. **Install the scripts:** Go to *Window > Plugin Manager* and click on the *Scripts* tab. Scroll down to [mekkablue scripts](glyphsapp3://showplugin/mekkablue%20scripts) and click on the *Install* button next to it.

Now the scripts are available in *Script > mekkablue.* If the mekkablue scripts do not show up in the *Script* menu, hold down the Option key and choose *Script > Reload Scripts* (Cmd-Opt-Shift-Y).


## Glyphs 2

### Video installation guide for Glyphs 2

There is a [tutorial video on how to install the mekkablue scripts](https://www.youtube.com/watch?v=Q6ly16Q0BmE) available on YouTube. While you are there, feel free to subscribe to the [mekkablue channel](https://www.youtube.com/channel/UCFPSSuEMZVQtrFpTzgFh9lA).

### General installation guide for Glyphs 2

The scripts need to be in the *Scripts* folder inside the app’s Application Support folder. Here is how:

1. Put the scripts folder (or an alias) into the *Scripts* folder which appears when you choose *Script > Open Scripts Folder* (Cmd-Shift-Y): `~/Library/Application Support/Glyphs/Scripts/`, or, better yet, use **git** for that. See below.
2. Then, hold down the Option (Alt) key, and choose *Script > Reload Scripts* (Cmd-Opt-Shift-Y). Now the scripts are visible in the *Script* menu
3. For some of the scripts, you will also need to install Tal Leming's *Vanilla:* Go to *Glyphs > Preferences > Addons > Modules* and click the *Install Modules* button. That’s it.

### git installation for Glyphs 2

I recommend to use git for getting the scripts, because it is easier for you to keep them up to date. Use this git command for cloning the repository into your *Scripts* folder:

```bash
git clone https://github.com/mekkablue/Glyphs-Scripts ~/Library/Application\ Support/Glyphs/Scripts/mekkablue/
```

If the terminal scares you, feel free to use one of the many readily available git clients, e.g. the free [Source Tree](https://www.sourcetreeapp.com) or [GitHub Desktop](https://desktop.github.com).

After you installed the mekkablue scripts, you can **update** this script repository (and all the others you have in your *Scripts* folder) by running *Scripts > mekkablue > App > Update git Repositories in Scripts Folder.*

# TROUBLESHOOTING

Please report problems and request features [as a GitHub issue](/issues). Make sure you have the latest version of the scripts and your app is up to date. And please, always **indicate both your Glyphs and macOS version.** Thank you.

# REQUIREMENTS

The scripts require a recent version of Glyphs 2.x running on macOS 10.9 or later. I can only test them and make them work in the latest version of the software. If a script is not working for you, please first update to the latest version of the script.

# ABOUT THE SCRIPTS

All the scripts show a **tooltip** when you hover the mouse pointer over their menu entry. In scripts with a GUI, most UI elements (checkboxes, text entry fields, etc.) have tooltips as well. This way you get the explanation you need right where it counts.

## 錨點

*「錨點移動器」用於批次處理錨點位置，在調整 x 高度之後會很有用。 輕而易舉：我總是在我的組合標記上使用「重新定位」腳本，因此就算在斜體角度也能維持一致。*

* **Anchor Mover / 錨點移動器：** GUI for batch-processing anchor positions in multiple glyphs. *需要 Vanilla JavaScript*
* **Batch Insert Anchors:** GUI for batch-inserting anchors of the same name at the same approximate position in multiple glyphs. *需要 Vanilla JavaScript*
* **Find and Replace in Anchor Names:** GUI for replacing text in the names of anchors in selected glyphs. Processes all layers. *需要 Vanilla JavaScript*
* **Fix Arabic Anchor Order in Ligatures:** Fixes the order of *top_X* and *bottom_X* anchors to RTL. In files converted from a different format, it sometimes happens that *top_1* is left of *top_2*, but it should be the other way around, otherwise your mark2liga will mess up. This script goes through your selected glyphs, and if they are Arabic ligatures, reorders all anchors to RTL order, at the same time not touching their coordinates.
* **Insert All Anchors in All Layers:** On each layer of a selected glyph, adds all missing anchors (but present in other layers of that glyph). Puts anchors at an averaged position.
* **Insert exit and entry Anchors to Selected Positional Glyphs:** Adds entry and exit anchors for cursive attachment in selected glyphs. By default, it places the exit at (0, 0) and the entry at a node at RSB if such a node exists. Please adjust for your own needs.
* **Mark Mover / 標記移動器：** Move marks to their respective heights, e.g. …comb.case to cap height, …comb to x-height, etc. Also allows you to set left and right metrics keys. *需要 Vanilla JavaScript*
* **Move ogonek Anchors to Baseline Intersection:** Moves all ogonek and _ogonek anchors to the rightmost intersection of the outline with the baseline.
* **Move topright Anchors for Vertical Carons:** Moves all topright and _topright anchors to the rightmost intersection of the outline with the x-height. Useful for building Czech/Slovak letters with vertical caron.
* **Move Vietnamese Marks to top_viet Anchor in Circumflex:** Moves *acute*, *grave* and *hookabovecomb* to the *top_viet* anchor in every layer of selected glyphs. Useful for Vietnamese double accents. Assumes that you have *top_viet* anchors in all layers of *circumflexcomb*.
* **New Tab with Glyphs Containing Anchor:** Opens a new tab with all glyphs containing a specific anchor.
* **New Tab with top and bottom Anchors Not on Metric Lines:** Report the y positions of all *top* and *bottom* anchors into the Macro Panel, and opens new tabs with all glyphs that have a stray anchor on any of the master, bracket or brace layers of any glyph in the font. Ignores the user selection, and analyses all glyphs, exporting and non-exporting. Useful to see if a top anchor is not exactly where it should be.
* **Prefix all exit/entry anchors with a hashtag:** Looks for all exit and entry anchors anywhere in the font, and disables `curs` feature generation by prefixing their anchor names with `#`.
* **Realign Stacking Anchors:** In stacking combining accents, moves top and bottom anchors exactly above or below the respective _top and _bottom anchors, respecting the italic angle. This way, stacking multiple nonspacing accents will always stay in line. *需要 Vanilla JavaScript*
* **Remove Anchors in Suffixed Glyphs:** Removes all anchors from glyphs with one of the user-specified suffix. Useful for removing left-over anchors in sups/subs/sinf/ordn variants of glyphs after copying, scaling and editing. *需要 Vanilla JavaScript*
* **Remove Anchors:** Deletes anchors with a specified name in selected glyphs (or the whole font). *需要 Vanilla JavaScript*
* **Remove Non-Standard Anchors from Selected Glyphs:** Removes all anchors from a glyph that should not be there by default, e.g., `ogonek` from `J`. Potentially dangerous, because it may delete false positives. So, first use the report script below.
* **Replicate Anchors:** Batch-add anchors to selected glyphs. Specify a source glyph to replicate the anchors from. *需要 Vanilla JavaScript*
* **Replicate Anchors in Suffixed Glyphs:** Goes through selected dot-suffixed glyphs and duplicates anchors from their respective base glyphs. E.g. will recreate anchors of *X* in *X.ss01*, *X.swsh* and *X.alt*.
* **Report Non-Standard Anchors to Macro window:** Goes through all glyphs in the font and reports in the Macro window if it finds non-default anchors. Lines are copy-pasteable in Edit view.
* **Shine Through Anchors:** In all layers of selected glyphs, inserts ‘traversing’ anchors from components.

## 應用程式

*如果您正在寫程式，請為「方法報告器」添加快捷鍵，您將非常需要它。如果你想要一個與解析度無關的視窗內容的PDF螢幕截圖讓你可以在向量插圖應用程式中進行後製，「列印視窗」可以派上用場。*

* **Close All Tabs of All Open Fonts / 關閉所有字型檔的編輯分頁：** 關閉目前在應用程式中開啟字型檔的所有編輯分頁。
* **Copy Download URL for Current App Version / 複製目前應用程式版本的下載連結：** 將目前 Glyphs 應用程式版本的下載連結放入剪貼簿以便於貼上。
* **Decrease and Increase Line Height / 減少和增加行高：** 將「編輯畫面」的行高增加四分之一或減少五分之一。如果您需要在行高之間頻繁切換，推薦將它們設定到快捷鍵。
* **Method Reporter / 方法報告器：** 圖形使用者介面用於過濾 Glyphs 中可用的 Python 和 PyObjC 類的方法名稱。您可以使用多個空格分隔檢索詞（用於 AND 串接）和星號作為未知字元（可放在開頭、中間和結尾）。按兩下可將方法名稱放入剪貼簿，然後在巨集視窗中打開説明。對寫程式的人很有用。 *需要 Vanilla JavaScript*
* **Navigate - Activate next and previous glyph / ：** 啟動下一個或上一個字符的編輯模式。
* **Parameter Reporter / 參數報告器：** 類似於方法報告器，但用於自定義參數。按兩下以複製剪貼簿中的參數，準備貼到字型資訊中。 *需要 Vanilla JavaScript*
* **Print Window / 列印視窗：** 列印當前視窗。用於保存視窗內容的向量 PDF，包括檢視器外掛的渲染（“顯示”選單的擴展）。 *:question:成果*
* **Resetter / 重置器：** 重置快速查看預覽、鍵盤快捷鍵和清除偏好設定、已儲存的應用程式狀態和自動儲存。 *需要 Vanilla JavaScript*
* **Set Export Paths to Adobe Fonts Folder / 將匯出路徑設置為 Adobe Fonts 資料夾：** 將 OpenType 字型和可變字型的匯出位置設定為 Adobe 字型資料夾。
* **Set Hidden App Preferences / 設定隱藏的應用程式偏好設定：** GUI for reading and setting ‘hidden’ app preferences, which are not listed in the GUI.一個用於讀取和設定「隱藏」的應用程式偏好設定的圖形使用者介面，這些偏好設定未在圖形使用者介面中列出。 *需要 Vanilla JavaScript* *:question:翻譯*
* **Set Label Colors / 設定標籤顏色：** 覆蓋預設應用程式標籤顏色。 *需要 Vanilla JavaScript*
* **Set Tool Shortcuts / 設定工具快捷鍵：** 為工具列中的工具設置鍵盤快捷鍵。 *需要 Vanilla JavaScript*
* **Toggle Horizontal-Vertical / 切換 橫排-直排：** 在當前分頁切換橫排（左起）-直排書寫方向。推薦在「系統偏好設定」中設定快捷鍵使用。
* **Toggle RTL-LTR / 切換 右起-左起：** 在當前分頁切換右起-左起書寫方向。推薦在「系統偏好設定」中設定快捷鍵使用。
* **Update git Repositories in Scripts Folder / 更新文本資料夾中的 git 儲存庫：** 對 Glyphs 腳本資料夾中的所有子資料夾執行「git pull」指令。如果腳本資料夾中有很多 git 儲存庫就很有用。 *:question:功能*

## 建構字符

*推薦腳本：「引用符管理器」，以及用於小型大寫數字、符號和 ​​Ldot 的「構建腳本」。其他腳本主要是為了讓您快速開始覆蓋某些 Unicode 範圍如果客戶有需求。*

* **Build APL Greek:** Create APL Greek glyphs.
* **Build careof and cadauna:** Builds `cadauna` and `careof` from your `c`, `o`, `u` and `fraction` glyphs.
* **Build Circled Glyphs:** Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from `_part.circle` and your letters and figures. *需要 Vanilla JavaScript*
* **Build Dotted Numbers:** Build dotted numbers from your default figures and the period.
* **Build ellipsis from period components:** Inserts exit and entry anchors in the period glyph and rebuilds ellipsis with auto-aligned components of period. Attention: decomposes all period components used in other glyphs (e.g., colon).
* **Build Extra Math Symbols:** Builds `lessoverequal`, `greateroverequal`, `bulletoperator`, `rightanglearc`, `righttriangle`, `sphericalangle`, `measuredangle`, `sunWithRays`, `positionIndicator`, `diameterSign`, `viewdataSquare`, `control`.
* **Build Ldot and ldot:** Builds `Ldot`, `ldot` and `ldot.sc` from existing `L` and `periodcentered.loclCAT` (`.case`/`.sc`). Assumes that you have already created and properly spaced `L`-`periodcentered.loclCAT`-`L`, etc.
* **Build Parenthesized Glyphs:** Creates parenthesized letters and numbers: `one.paren`, `two.paren`, `three.paren`, `four.paren`, `five.paren`, `six.paren`, `seven.paren`, `eight.paren`, `nine.paren`, `one_zero.paren`, `one_one.paren`, `one_two.paren`, `one_three.paren`, `one_four.paren`, `one_five.paren`, `one_six.paren`, `one_seven.paren`, `one_eight.paren`, `one_nine.paren`, `two_zero.paren`, `a.paren`, `b.paren`, `c.paren`, `d.paren`, `e.paren`, `f.paren`, `g.paren`, `h.paren`, `i.paren`, `j.paren`, `k.paren`, `l.paren`, `m.paren`, `n.paren`, `o.paren`, `p.paren`, `q.paren`, `r.paren`, `s.paren`, `t.paren`, `u.paren`, `v.paren`, `w.paren`, `x.paren`, `y.paren`, `z.paren`.
* **Build Q from O and _tail.Q:** Run this script *after* doing *Component from Selection* on the Q tail and naming it `_tail.Q`.
* **Build Rare Symbols:** Builds white and black, small and large, circles, triangles and squares. *需要 Vanilla JavaScript*
* **Build rtlm Alternates:** Creates horizontally mirrored composites for selected glyphs and updates the rtlm OpenType feature. Auto-aligns the components, but also adds metrics keys that kick in in case you decompose.
* **Build Small Figures:** Takes a default set of figures (e.g., `.dnom`), and derives the others (`.numr`, `superior`/`.sups`, `inferior`/`.sinf`, `.subs`) as component copies. Respects the italic angle. *Need Vanilla.*
* **Build small letter SM, TEL:** Creates the glyphs: `servicemark`, `telephone`.
* **Build space glyphs:** Creates `mediumspace-math`, `emquad`, `emspace`, `enquad`, `enspace`, `figurespace`, `fourperemspace`, `hairspace`, `narrownbspace`, `punctuationspace`, `sixperemspace`, `nbspace`, `thinspace`, `threeperemspace`, `zerowidthspace`.
* **Build Symbols:** Creates symbol glyphs such as `.notdef` (based on the boldest available `question` mark), an `estimated` glyph, as well as `bar` and `brokenbar` (for which it respects standard stems and italic angle). *需要 Vanilla JavaScript*
* **Fix Punctuation Dots and Heights:** Syncs punctuation dots between ¡!¿? (and their SC+CASE variants). Will use dot from exclam in all other glyphs, and shift ¡¿ in SC and CASE variants. Assumes that ¡¿ are components in !?. Detailed report in Macro Window..
* **Quote Manager / 引用符管理器：** Build double quotes from single quotes, and insert `#exit` and `#entry` anchors in the single quotes for auto-alignment. You need to have the single quotes already. *需要 Vanilla JavaScript*

## 彩色字型

*These scripts are for situations you will encounter in a Color Font workflow. The Merge script is mainly for creating a fallback glyph for CPAL/COLR fonts. This way the fallback has the full bbox, and no clipping will occur in Chrome.這些腳本能幫助您在製作彩色字體的工作流程中解決遇到的問題。「合併腳本」主要用於為 CPAL/COLR 字型創建後備字符。這樣後備具有完整的 bbox，並且不會在 Chrome 瀏覽器中發生裁切。*

* **Add All Missing Color Layers to Selected Glyphs:** Adds a duplicate of the fallback layer for each (CPAL/COLR) color defined in the Color Palettes parameter, for each selected glyph. Only adds colors that are still missing in the glyph.
* **Add sbix Images to Font:** Will get all PNG, GIF, JPG files in a folder and create iColor layers with them in the current font and master. File name convention: ‘glyphname pixelsize.suffix’, e.g., ‘Adieresis 128.png’.
* **Convert Layerfont to CPAL+COLR Font:** Turns a layered color font into a single-master font with a CPAL and COLR layers in each glyph. It will take the first master as default.
* **Delete Non-Color Layers in Selected Glyphs:** Deletes all sublayers in all glyphs that are not of type "Color X" (CPAL/COLR layers).
* **Merge All Other Masters in Current Master:** In selected glyphs, copies all paths from other masters onto the current master layer.
* **Merge Suffixed Glyphs into Color Layers:** Merges x.shadow, x.body and x.front into separate CPAL Color layers of x. *需要 Vanilla JavaScript*
* **sbix Spacer:** Batch-set sbix positions and glyph widths. *需要 Vanilla JavaScript*

## 比較當前字型

*These scripts are intended for syncing uprights with their italics. Open two fonts, and run the scripts. They do not change your fonts, but report in detail in the Macro window.這些腳本用於同步正斜體和斜體。打開兩種字體，然後運行腳本。它們不會更改您的字體，但會在宏窗口中詳細報告。*

* **Compare Font Info > Font:** Detailed report of Font Info > Masters for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Masters:** Detailed report of Font Info > Masters for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Instances:** Detailed report of Font Info > Instances for the two frontmost fonts and outputs a report in the Macro window.
* **Compare Font Info > Features:**  Compares the OT features set of the two frontmost fonts and outputs a report in the Macro window.
* **Compare Anchors:** Compares anchor structure and anchor heights between the two frontmost fonts.
* **Compare Composites:** Reports diverging component structures of composite glyphs, e.g., `iacute` built with `acutecomb` in one font, and `acutecomb.narrow` in the other.
* **Compare Glyph Heights:** Lists all glyphs that differ from the second font in height beyond a given threshold.
* **Compare Glyph Info:** Compares open fonts and builds a lits of differing glyph info, including Unicode values and categorisation. *需要 Vanilla JavaScript*
* **Compare Glyphsets:** Compares the glyph set of the two frontmost fonts and outputs a report in the Macro window.
* **Compare Kerning Groups:** Compares kerning groups between frontmost fonts, outputs a table of glyph names with unmatching groups.
* **Compare Metrics:** Compare widths of two frontmost fonts.
* **Compare Sidebearings:** Compare sidebearings of two frontmost fonts.

## 部件

*Populate Backgrounds with Components is very useful when you build letters based on other, e.g., ae or oe can take an e in the background. The script puts the e in the background of each master, and the UI has an option to align selected points with the e in the background. If you use corner components for serifs in a multiple-master font, the Propagate script will save you a lot of time.當您基於其他字母構建字母時，使用組件填充背景非常有用，例如，ae 或 oe 可以在背景中使用 e。該腳本將 e 放在每個母版的背景中，UI 有一個選項可以將選定的點與背景中的 e 對齊。如果您在多母版字體中為襯線使用角組件，傳播腳本將為您節省大量時間。*

* **Alignment Manager:** Enables or disables automatic alignment for all components on visible layers in selected glyphs. Does the same as the command in the context menu, but you can do it in one step for many glyphs. *需要 Vanilla JavaScript*
* **Component Problem Finder:** Find possible issues with components and corner components:  composable glyphs consisting of paths; locked, nested, orphaned, mirrored, shifted, rotated and scaled components; composite glyphs with an unusual component order or an unorthodox component structure. Also, disconnected and scaled corner components. *需要 Vanilla JavaScript*
* **Decompose Components in Background:** Decomposes background layers of selected glyphs. Works on the current master or all masters, or all masters of all fonts.
* **Decompose Corner and Cap Components:** Decomposes all corner and cap components in selected glyphs. Reports to Macro window.
* **Find and Replace Components:** Relinks components in selected glyphs to a new source glyph. *需要 Vanilla JavaScript*
* **Find and Replace Cap and Corner Components:** Relinks `_cap.*` and `_corner.*` components in selected glyphs to a different corner/cap component. *需要 Vanilla JavaScript*
* **Find and Replace Corner Components at Certain Angles:** Replace Corner Components at blunt or acute angles. *需要 Vanilla JavaScript*
* **Move Paths to Component:** Moves paths to a separate glyph and insert them as auto-aligned, anchored components in the source glyph. Perfect for making path-component mixtures into pure composites. *需要 Vanilla JavaScript*
* **Populate Backgrounds with Components:** Removes the specified component from all glyphs or all selected glyphs. *需要 Vanilla JavaScript*
* **Propagate Corner Components to Other Masters:** Tries to recreate the corner components of the current master layer in all other masters of the same glyph. Make sure your outlines are compatible.
* **Remove Components:** Removes the specified component from all (selected) glyphs.
* **Remove Detached Corners:** Removes detached corner component from all (selected) glyphs.
* **Stitcher:** In selected glyphs, the Stitcher inserts components on your paths at fixed intervals. Useful for turning open paths (monolines) into dotted lines. Use an anchor called 'origin' for determining the component position in stitched letters. Consider using the [Stitcher plug-in](glyphsapp3://showplugin/Stitcher) instead. *需要 Vanilla JavaScript*
* **Sync Components Across Masters:** Takes the current layer’s components, and resets all other masters to the same component structure. Ignores paths and anchors. Hold down Option key to *delete* all paths and anchors.

## 特性

*In script typefaces, you may often need the Build Positional calt script. If you find yourself turning OT features on and off a lot, take a look at the Activate Default Features and Floating Features scripts. And check out the Set Palette from Window > Plugin Manager.在腳本字體中，您可能經常需要 Build Positional calt 腳本。如果您發現自己經常打開和關閉 OT 功能，請查看激活默認功能和浮動功能腳本。並從 Window > Plugin Manager 查看 Set Palette。*

* **Activate Default Features:** In the current Edit tab, activates all OT features that are recommended to be on by default (according to the spec).
* **Build ccmp for Hebrew Presentation Forms:** Builds the ccmp feature for precomposed `uniFBxx` glyphs, e.g. if you have pedagesh, you get 'sub pe dagesh by pedagesh' in your ccmp.
* **Build Italic Shift Feature:** Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature. *需要 Vanilla JavaScript*
* **Build Positional Feature:** Looks for `.init`, `.medi`, `.fina`, and `.isol` glyphs, and injects positional substitution code into your `calt` feature (or any other feature you specify). If run again, will *update* class and feature code. See this tutorial for more info: https://glyphsapp.com/learn/features-part-4-positional-alternates *需要 Vanilla JavaScript*
* **Build rand Feature:** Build rand (random) feature from .cvXX or another (numbered) suffix. *需要 Vanilla JavaScript*
* **Feature Code Tweaks:** Adds tweaks to OT feature code. Reports in Macro window. Careful: if you do not understand an option, do not use it. *需要 Vanilla JavaScript*
* **Find in Features:** Finds expressions (glyph, lookup or class names) in OT Features, Prefixes and Classes. *需要 Vanilla JavaScript*
* **Floating Features:** Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. *需要 Vanilla JavaScript*
* **Fraction Fever 2:** Insert Tal Leming’s Fraction Fever 2 code into the font. Read more in this tutorial: https://glyphsapp.com/learn/fractions
* **New OT Class with Selected Glyphs:** GUI for creating a new OT class with the selected glyphs. *需要 Vanilla JavaScript*
* **New Tab with OT Class:** GUI for opening all glyphs in an OT class (listed in *File > Font Info > Features > Classes*) in a new tab. *需要 Vanilla JavaScript*
* **Update Features without Reordering:** Goes through the existing features in the font and refreshes each one of them. Does neither add nor reorder features.
* * **Stylistic Sets > Synchronize ssXX glyphs:** Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> the script creates *b.ss02*
* * **Stylistic Sets > Create ssXX from layer:** Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
* * **Stylistic Sets > Create pseudorandom calt feature:** Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Also includes the default class in the rotation algorithm.
* * **Stylistic Sets > Set ssXX Names:** Prefills names for ssXX features with ‘Alternate’ or another chosen text, plus the name of the first substituted glyph, e.g., ‘Alternate a’. Option to preserve existing namings.*需要 Vanilla JavaScript*

## 字型資訊

*Vertical Metrics is useful for finding and syncing the vertical metric parameters in Font Info > Font and Font Info > Masters. Clean Version String is very useful too. Font Info Batch Setter is a must for syncing Font Info settings across many fonts. Careful about Set WWS/Preferred Names scripts: The app usually takes care of naming automatically, so their use cases are very rare.Vertical Metrics 對於在 Font Info > Font and Font Info > Masters 中查找和同步垂直度量參數很有用。Clean Version String 也非常有用。Font Info Batch Setter 是跨多種字體同步字體信息設置的必備工具。注意 Set WWS/Preferred Names 腳本：該應用程序通常會自動處理命名，因此它們的用例非常少。*

* **Clean Version String:** Adds a clean versionString parameter, and disables ttfAutohint info in the version string. The exported font will have a version string consisting only of ‘Version X.XXX’.
* **Find and Replace in Font Info:** Finds and replaces names in *Font Info > Font* and *Font Info > Instances.* *需要 Vanilla JavaScript*
* **Find and Replace In Instance Parameters:** Finds and Replace in Custom Parameters of selected instances of the current font or project file.
* **Font Info Batch Setter:** Batch-apply settings in *Font Info > Font* to open fonts: designer, designer URL, manufacturer, manufacturer URL, copyright, version number, date and time. Useful for syncing Font Info settings across many fonts. *需要 Vanilla JavaScript*
* **Font Info Overview:** Lists some Font Info values for all opened fonts.
* **Prepare Font Info:** Prepare open fonts for a modern font production and git workflow by setting certain custom parameters. *需要 Vanilla JavaScript*
* **Remove Custom Parameters:** Removes all parameters of one kind from Font Info > Font, Masters, Instances. Useful if you have many masters or instances. *需要 Vanilla JavaScript*
* **Set Preferred Names (Name IDs 16 and 17)  for Width Variants:** Sets Preferred Names custom parameters (Name IDs 16 and 17) for all instances, so that width variants will appear in separate menus in Adobe apps.
* **Set Style Linking:** Attempts to set the Bold/Italic bits.
* **Set Subscript and Superscript Parameters:** Measures your superior and inferior figures and derives subscript/superscript X/Y offset/size parameters. *需要 Vanilla JavaScript*
* **Set WWS Names (Name IDs 21 and 22):** Sets WWS custom parameters (Name IDs 21 and 22) for all instances where necessary: Puts all info except RIBBI into the WWSFamilyName, and only keeps RIBBI for the WWSSubfamilyName.
* **Style Renamer:** Batch-add a name particle to your style names, or batch-remove it from them. Useful for switching all your styles from italic to roman naming and vice versa. *需要 Vanilla JavaScript*
* **Vertical Metrics Manager:** Calculate and insert values for OS/2 usWin and sTypo, hhea and fsSelection bit 7 (for preferring sTypo Metrics over usWin metrics). *需要 Vanilla JavaScript*

## 字形名稱、註釋和 Unicode

*Most scripts make managing glyph names and Unicodes a little easier. Garbage Collection is useful for cleaning up the mess of the reporter scripts, or other annotations before you hand the files over to a third party.大多數腳本使管理字形名稱和 Unicode 更容易一些。垃圾收集對於在將文件移交給第三方之前清理記者腳本或其他註釋的混亂很有用。*

* **Add PUA Unicode Values to Selected Glyphs:** Iterates through selected glyphs and incrementally applies custom Unicode values, starting at a user-specified value. *需要 Vanilla JavaScript*
* **Color Composites in Shade of Base Glyph:** Color composites in a lighter shade of the base glyph. E.g., if your A is has a red label color, then ÄÁÀĂ... will have a lighter shade of red.
* **Convert to Uppercase:** Turns lowercase names into uppercase names, e.g., `a` → `A`, `ccaron` → `Ccaron`, `aeacute` → `AEacute`, etc.
* **Convert to Lowercase:** Turns the names of selected glyphs lowercase.
* **Encoding Converter:** Converts old expert 8-bit encodings into Glyphs nice names, based on a importable/exportable text with renaming scheme. Default is an AXt converting scheme. *需要 Vanilla JavaScript*
* **Garbage Collection:** Removes markers in glyphs, such as node names, glyph names or annotations, as well as guides.
* **New Tab with Uppercase-Lowercase Inconsistencies:** Opens a new Edit tab containing all glyphs without consistent case folding. Writes a detailed report in Macro Window.
* **Production Namer:** Override default production names. Default are the usual subjects which create problems in legacy PDF workflows: mu, onesuperior, twosuperior, threesuperior. *需要 Vanilla JavaScript*
* **Rename Glyphs:** Takes a list of `oldglyphname=newglyphname` pairs and renames glyphs in the font accordingly, much like the *Rename Glyphs* custom parameter. *需要 Vanilla JavaScript*
* **Reorder Unicodes of Selected Glyphs:** Reorders Unicodes so that default Unicode comes first.
* **Switch Mirrored Characters:** In the current Edit View, switch mirrored BiDi characters, e.g. () → )(. Useful for switching parentheses and quotes after switching writing direction in a tab.

## 指南

*These scripts are mostly intended for cleaning up the plethora of guides I see when working on third-party fonts.這些腳本主要用於清理我在處理第三方字體時看到的過多指南。*

* **Guides through All Selected Nodes:** Lays guides through all selected nodes in current glyph. Tries to avoid duplicate guides.
* **Remove Global Guides in Current Master:** Deletes all global (red) guides in the current master.
* **Remove Local Guides in Selected Glyphs:** Deletes all local (blue) guides in selected glyphs.
* **Select All Global Guides:** Selects all global (red) guides in Edit view. Useful if you have many and need to batch-transform them.
* **Select All Local Guides:** Selects all local (blue) guides (in all selected glyphs).

## 字體微調

*Most important: Set blueScale, Set Family Alignment Zones for PostScript hinting. If you are making big changes, The Transfer and Keep Only scripts can save you a lot of work. The New Tab scripts help find glyphs missing zones. Also consider Paths > Find Near Vertical Misses for that purpose.最重要的是：設置 blueScale，為 PostScript 提示設置系列對齊區域。如果您要進行大的更改，Transfer 和 Keep Only 腳本可以為您節省大量工作。新標籤腳本有助於找到字形缺失區域。為此，還可以考慮路徑 > 查找近垂直未命中。*

* **Add Alignment Zones for Selected Glyphs:** Creates fitting zones for the selected glyphs in all masters. *需要 Vanilla JavaScript*
* **Add Hints for Selected Nodes:** Adds hints for the selected nodes. Tries to guess whether it should be H or V. If exactly one node inside a zone is selected, it will add a Ghost Hint. Useful for setting a shortcut in System Prefs.
* **Add TTF Autohint Control Instructions for Current Glyph:** Adds a touch line for a given up/down amount to the Control Instructions of the current instance. *需要 Vanilla JavaScript*
* **BlueFuzzer:** Extends all alignment zones by the specified value. Similar to what the blueFuzz value used to do, hence the name. *需要 Vanilla JavaScript*
* **Keep Only First Master Hints:** In selected glyphs, deletes all hints in all layers except for whatever is ordered as first master. Respects Bracket Layers. E.g., if your first master is 'Regular', then the script will delete hints in 'Bold', 'Bold [120]', but keep them in 'Regular' and 'Regular [100]'.
* **New Tab with Glyphs in Alignment Zones:** Opens a new tab and lists all glyphs that reach into alignment zones.
* **New Tabs with Glyphs Not Reaching Into Zones:** Opens a new tab with all glyphs that do NOT reach into any top or bottom alignment zone. Only counts glyphs that contain paths in the current master. Ignores empty glyphs and compounds. *需要 Vanilla JavaScript*
* **New Tab with Layers with TTDeltas:** Opens a new tab with all layers that have defined TTDeltas.
* **Remove PS Hints:** Deletes all stem and/or ghost hints throughout the current font, the selected master and/or the selected glyphs. *需要 Vanilla JavaScript*
* **Remove TT Hints:** Deletes a user-specified set of TT instructions throughout the current font, the selected master and/or the selected glyphs. *需要 Vanilla JavaScript*
* **Remove Zero Deltas in Selected Glyphs:** Goes through all layers of each selected glyph, and deletes all TT Delta Hints with an offset of zero. Detailed Report in Macro window.
* **Set blueScale:** Sets maximum blueScale value (determining max size for overshoot suppression) possible in Font Info > Font. Outputs other options in Macro window.
* **Set Family Alignment Zones:** Pick an instance and set its zones as Family Alignment Zones in *Font Info > Font > Custom Parameters.* *需要 Vanilla JavaScript*
* **Set TT Stem Hints to Auto:** Sets all TT stem hints to ‘auto’ in selected glyphs.
* **Set TT Stem Hints to No Stem:** Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.
* **Set TTF Autohint Options:** Set options for existing 'TTF Autohint Options' Custom Parameters. *需要 Vanilla JavaScript*
* **Transfer Hints to First Master:** Copies PS hints from the current layer to the first master layer, provided the paths are compatible. Reports errors to the Macro window.
* **TT Autoinstruct:** Automatically add Glyphs TT instructions to the selected glyphs in the selected master. (Should be the first master.) Attention: this is NOT Werner Lemberg's ttfAutohint, but the manual TT hints that the TT Instruction tool (I) would add through the context menu item of the same name. Useful for adding hints in many glyphs at once.

## 圖片

*Mainly intended for curing the headaches you may undergo when handling a lot of (background) images.主要用於解決處理大量（背景）圖像時可能遇到的頭痛問題。*

* **Add Same Image to Selected Glyphs:** Asks you for an image, and then inserts it into all currently selected glyphs as background image.
* **Adjust Image Alpha:** Slider for setting the alpha of all images in selected glyphs. *需要 Vanilla JavaScript*
* **Delete All Images in Font:** Deletes all placed images throughout the entire font.
* **Delete Images:** Deletes all images placed in the visible layers of selected glyphs.
* **Reset Image Transformation:** Resets all image transformations (x/y offset, scale, and distortion) back to default in the visible layers of selected glyphs.
* **Set New Path for Images:** Resets the path for placed images in selected glyphs. Useful if you have moved your images.
* **Toggle Image Lock:** Lock or unlock all images in all selected glyphs. *需要 Vanilla JavaScript*
* **Transform Images:** GUI for batch-transforming images (x/y offset and x/y scale) in the visible layers of selected glyphs. *需要 Vanilla JavaScript*

## 插值

*Most important: Insert Instances (for determining your instances and their style linking), Kink Finder and Find Shapeshifting Glyphs. I use Show Next/Previous Instance with the keyboard shortcut ctrl-up/down a lot.最重要的是：Insert Instances（用於確定您的實例及其樣式鏈接）、Kink Finder 和 Find Shapeshifting Glyphs。我經常使用 Show Next/Previous Instance 和鍵盤快捷鍵 ctrl-up/down。*

* **Axis Location Setter:** Batch-set axis locations for all instances with a certain name particle. E.g., set an axis location for all Condensed instances. *需要 Vanilla JavaScript*
* **Axis Mapper:** Extracts, resets and inserts an ‘avar’ axis mapping for the Axis Mappings parameter. *需要 Vanilla JavaScript*
* **Brace and Bracket Manager:** Find and replace brace or bracket layer coordinates in Glyphs 3 and later. *需要 Vanilla JavaScript*
* **Composite Variabler:** Reduplicates Brace and Bracket layers of components in the compounds in which they are used. Makes bracket layers work in composites. *需要 Vanilla JavaScript*
* **Copy Layer to Layer:** Copies paths (and optionally, also components, anchors and metrics) from one Master to another. *需要 Vanilla JavaScript*
* **Dekink Masters:** Dekinks your smooth point triplets in all compatible layers (useful if they are not horizontal or vertical). Select a point in one or more smooth point triplets, and run this script to move the corresponding nodes in all other masters to the same relative position. Thus you achieve the same point ratio in all masters and avoid interpolation kinks, when the angle of the triplet changes. There is a [video describing it.](http://tinyurl.com/dekink-py) The triplet problem is [described in this tutorial](http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible).
* **Fill up Empty Masters:** Copies paths from one Master to another. But only if target master is empty. *需要 Vanilla JavaScript*
* **Find and Replace in Layer Names:** Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. *需要 Vanilla JavaScript*
* **Find Shapeshifting Glyphs:** Finds glyphs that change the number of paths while interpolating. Opens a new tab and reports to Macro window. *需要 Vanilla JavaScript*
* **Insert Brace Layers for Component Rotation:** Inserts a number of Brace Layers with continuously scaled and rotated components. Useful for OTVar interpolations with rotating elements. *需要 Vanilla JavaScript*
* **Insert Brace Layers for Movement along Background Path:** Inserts a number of Brace Layers with copies of the first layer, shifted according to the first path in the background. Useful for OTVar interpolations with moving elements.
* **Insert Instances:** GUI for calculating and inserting weight instances. It is described in this tutorial: https://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances *需要 Vanilla JavaScript*
* **Insert Layers:** Batch-insert brace or bracket layers in selected glyphs. *需要 Vanilla JavaScript*
* **Instance Cooker:** Insert many instances at once with a recipe. *需要 Vanilla JavaScript*
* **Kink Finder:** Finds kinks in outlines or the interpolation space, reports them in the Macro window and opens a new tab with affected glyphs. Kinks are described in this tutorial: https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible *需要 Vanilla JavaScript*
* **New Tab with Dangerous Glyphs for Interpolation:** Opens a tab with all glyphs in the font that contain at least two compatible elements. I.e., glyphs where an element (a path or a component) could interpolate with the wrong element, like the equals sign. For a detailed description, see section *Be suspicious* in this tutorial: <http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible>.
* **New Tab with Special Layers:** Quickly adds a new edit tab with all glyphs containing brace and bracket layers.
* **New Tab with Uneven Handle Distributions:** Finds glyphs where handle distributions change too much (e.g., from balanced to harmonised). *需要 Vanilla JavaScript*
* **OTVar Player:** Animates the current glyph with a loop along the weight axis. *需要 Vanilla JavaScript*
* **Remove All Non-Master Layers:** Deletes all layers which are neither master layers, nor brace layers, nor bracket layers. Useful for getting rid of backup layers.
* **Report Instance Interpolations:** Outputs master coefficients for each instance in Macro Window. Tells you which masters are involved in interpolating a specific instance, and to which extent.
* **Reset Axis Mappings:** Inserts (or resets) a default Axis Mappings parameter for all style values currently present in the font. Ignores style values outside the designspace bounds defined by the masters.
* **Set Weight Axis Locations in Instances:** Will set weight axis location parameters for all instances, and sync them with their respective usWeightClass. Will set the width axis coordinates to the spec defaults for usWidthClass, if they have not been set yet. Otherwise will keep them as is.
* **Short Segment Finder:** Goes through all interpolations and finds segments shorter than a user-specified threshold length. *需要 Vanilla JavaScript*
* **Travel Tracker:** Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes. The results are incomplete, and usually have many false positives, but it sometimes finds cases that the Shapeshifter script misses. *需要 Vanilla JavaScript*
* **Variation Interpolator:** Creates a user-defined number of glyph variations with a user-defined suffix, containing interpolations between the layers and their respective backgrounds. Overwrites glyphs with same name. Similar to Pablo Impallari’s SimplePolator. Useful for e.g. length variants of Devanagari Matra, see José Nicolás Silva Schwarzenberg’s sample video: <https://www.youtube.com/watch?v=QDbaUlHifBc>. *需要 Vanilla JavaScript*
* * **Other > Lines by Master:** Reduplicates your edit text across masters, will add one line per master in Edit view. Careful, ignores everything after the first newline. Intended for adding a keyboard in System Preferences.
* * **Other > New Tab with Masters of Selected Glyphs:** Opens a new Edit tab containing all masters of selected glyphs.
* * **Other > Show Masters of Next/Previous Glyph:** Allows you to step through one glyph after another, but with all masters. Combines the show next/previous glyph function (fn+left/right) with the *Edit > Show All Masters* function. Handy for attaching a keyboard shortcut in System Preferences.
* * **Other > Show Next/Previous Instance:** Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut in System Preferences.

## Kerning

*Most important: Auto Bumper, KernCrasher, GapFinder, Sample String Maker. If you have too much kerning, consider Exception Cleaner.最重要的：Auto Bumper、KernCrasher、GapFinder、Sample String Maker。如果字距調整太多，請考慮 Exception Cleaner。*

* **Adjust Kerning in Master:** GUI to add a value to all kerning pairs, multiply them by a value, round them by a value, or limit them to a value. *需要 Vanilla JavaScript*
* **Auto Bumper:** Specify a minimum distance, left and right glyphs, and Auto Bumper will add the minimum necessary kerning for the current master. *需要 Vanilla JavaScript*
* **BBox Bumper:** Like Auto Bumper, but with the bounding box of a group of glyphs, and the kerning inserted as GPOS feature code in Font Info > Features > kern. Useful if you want to do group kerning with classes that are different from the kerning groups. 需要 Vanilla JavaScript
* **Convert RTL Kerning from Glyphs 2 to 3:** Convert RTL kerning from Glyphs 2 to Glyphs 3 format and switches the kerning classes. (Hold down OPTION and SHIFT to convert from Glyphs 3 back to Glyphs 2.) Detailed report in Macro Window.
* **Copy Kerning Exceptions to Double Accents:** Copies Kerning exceptions with abreve, `acircumflex`, `ecircumflex`, `ocircumflex`, `udieresis` into Vietnamese and Pinyin double accents.
* **Exception Cleaner:** Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception. *需要 Vanilla JavaScript*
* **Find and Replace in Kerning Groups:** GUI for searching and replacing text in the L and R Kerning Groups, e.g. replace 'O' by 'O.alt'. Leave the search field blank for appending. *需要 Vanilla JavaScript*
* **GapFinder:** Opens a new tab with kerning combos that have large gaps in the current fontmaster. *需要 Vanilla JavaScript*
* **Import Kerning from .fea File:** Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see *Window > Kerning*).
* **KernCrash Current Glyph:** Opens a new tab containing kerning combos with the current glyph that collide in the current fontmaster.
* **KernCrasher:** Opens a new tab with Kerning Combos that crash in the current fontmaster. *需要 Vanilla JavaScript*
* **Kern Flattener:** Duplicates your font, flattens kerning to glyph-to-glyph kerning only, deletes all group kerning and keeps only relevant pairs (it has a built-in list), adds a *Export kern Table* parameter (and some other parameters) to each instance. Warning: do this only for making your kerning compatible with outdated and broken software like PowerPoint. No guarantee it works, though.
* **Kern String Mixer:** Intersect two sets of glyphs (tokens are possible) with each other in order to get all possible glyph combinations. *需要 Vanilla JavaScript*
* **New Tab with All Group Members:** Select two glyphs, e.g. ‘Ta’, run the script, and it will open a new tab with all combinations of the right kerning group of T with the left kerning group of a.
* **New Tab with Glyphs of Same Kerning Groups:** Opens a new tab containing all members of the left and right kerning groups of the current glyph.
* **New Tab with Kerning Missing in Masters:** Opens New Tabs for each master showing kerning missing in this master but present in other masters.
* **New Tab with Large Kerning Pairs:** Lists all positive and negative kerning pairs beyond a given threshold. *需要 Vanilla JavaScript*
* **New Tab with Overkerned Pairs:** Asks a threshold percentage, and opens a new tab with all negative kern pairs going beyond the width threshold. Example: With a threshold of 40%, and a comma with width 160, the script will report any negative kern pair with comma larger than 64 (=40% of 160). Assume that r-comma is kerned -60, and P-comma is kerned -70. In this case, it would report the latter, but not the former. *需要 Vanilla JavaScript*
* **New Tab with Right Groups:** Creates a new tab with one glyph of each right group. Useful for checking the consistency of right kerning groups.
* **New Tab with all Selected Glyph Combinations:** Takes your selected glyphs and opens a new tab with all possible combinations of the letters. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Uneven Symmetric Kernings:** Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
* **New Tabs with Punctuation Kern Strings:** Outputs several tabs with kern strings with punctuation.
* **Remove all Kerning Exceptions:** Removes all kerning for the current master, except for group-to-group kerning. Be careful.
* **Remove Kerning Between Categories:** Removes kerning between glyphs, categories, subcategories, scripts. *Requires Vanilla.*
* **Remove Kerning Pairs for Selected Glyphs:** Deletes all kerning pairs with the selected glyphs, for the current master only.
* **Remove Orphaned Group Kerning:** Deletes all group kernings referring to groups that are not in the font.
* **Remove Small Kerning Pairs:** Removes all kerning pairs in the current font master with a value smaller than specified, or a value equal to zero. Be careful. *需要 Vanilla JavaScript*
* **Report Kerning Mistakes:** Tries to find unnecessary kernings and groupings. Reports in Macro window, for reviewing.
* **Sample String Maker:** Creates kern strings for user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored. *需要 Vanilla JavaScript*
* **Set Kerning Groups:** Sets left and right kerning groups for all selected glyphs. In the case of compounds, will use the groups of the base components, otherwise makes an informed guess based on a built-in dictionary.
* **Steal Kerning from InDesign:** Steals the kerning from text set in InDesign. Useful for extracting InDesign’s [Optical Kerning](https://web.archive.org/web/20160414170915/http://blog.extensis.com/adobe/about-adobe’s-optical-kerning.php) values.
* **Steal Kerning Groups from Font:** Steals left/right kerning groups for all selected glyphs from a 2nd font. *需要 Vanilla JavaScript*
* **Zero Kerner:** Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports. *需要 Vanilla JavaScript*

## 路徑

*I use Rotate Around Anchor for my asterisks. Important for outline checking: Path Problem Finder, Find Near Vertical Misses and the Green Blue Manager. Rewire Fire has become important in OTVar production, because it helps reduce duplicate outline segments at shape edges (which create dark spots in anti-aliasing).我為我的星號使用 Rotate Around Anchor。對於輪廓檢查很重要：Path Problem Finder、Find Near Vertical Misses 和 Green Blue Manager。Rewire Fire 在 OTVar 製作中變得很重要，因為它有助於減少形狀邊緣處的重複輪廓段（這會在抗鋸齒中產生暗點）。*

* **Align Selected Nodes with Background:** Align selected nodes with the nearest background node unless it is already taken by a previously moved node. Like Cmd-Shift-A for aligning a single node with the background, but for multiple nodes.
* **Batch-Set Path Attributes:** Set path attributes of all paths in selected glyphs, the master, the font, etc. *需要 Vanilla JavaScript*
* **Copy Glyphs from Other Font into Backup Layers:** Creates backup layers for selected glyphs in target font, and fills them with the respective glyphs from source font. Useful if you want to add glyphs from one font as bracket layers in another. *需要 Vanilla JavaScript*
* **Distribute Nodes:** Horizontally or vertically distributes nodes (depends on the width/height ratio of the selection bounding box).
* **Enlarge Single-Unit Segments:** Doubles the length of line segments shorter than one unit.
* **Fill Up with Rectangles:** Goes through your selected glyphs, and if it finds an empty one, inserts a placeholder rectangle. Useful for quickly building a dummy font for testing.
* **Find Close Encounters of Orthogonal Line Segments:** Goes through all vertical and horizontal line segments, and finds pairs that are close, but do not align completely. *需要 Vanilla JavaScript*
* **Find Near Vertical Misses:** Finds nodes that are close but not exactly on vertical metrics. *需要 Vanilla JavaScript*
* **Green Blue Manager:** Define an angle above which a node will be set to blue, below which it will be set to green. *需要 Vanilla JavaScript*
* **Grid Switcher:** Toggles grid between two user-definable gridstep values with the click of a floating button. *需要 Vanilla JavaScript*
* **Harmonise Curve to Line:** Will rearrange handles on (selected) curve segments with a following line segment, in such a way that the transition between the two segments is smooth (harmonized).
* **Interpolate two paths:** Select two paths and run this script, it will replace them with their interpolation at 50%.
* **New Tab with Small Paths:** Opens a new tab containing paths that are smaller than a user-definable threshold size in square units.
* **Path Problem Finder:** Finds all kinds of potential problems in outlines, and opens a new tab with affected layers. *需要 Vanilla JavaScript*
* **Position Clicker:** Finds all combinations of positional shapes that do not click well. ‘Clicking’ means sharing two point coordinates when overlapping. *需要 Vanilla JavaScript*
* **Realign BCPs:** Realigns all BCPs in all selected glyphs. Useful if handles got out of sync, e.g. after nudging or some other transformation, or after interpolation. Hold down Option to apply to all layers of the selected glyph(s).
* **Remove all Open Paths:** Deletes all *open* paths in the visible layers of all selected glyphs.
* **Remove Nodes and Try to Keep Shape:** Deletes selected on-curve nodes and tries to keep the shape as much as possible. Similar to what happens when you delete a single node, but for a selection of multiple nodes. Pro tip: Hold down the Shift key while running the script, and it will also balance the remaining handles as much as possible, which is exactly what happens when you delete a single node.
* **Remove Short Segments:** Deletes segments shorter than one unit.
* **Remove Stray Points:** Deletes stray points (single node paths) in selected glyphs. Careful: a stray point can be used as a quick hack to disable automatic alignment. Reports in detail to the Macro window.
* **Rewire Fire:** Finds, selects and marks duplicate coordinates. Two nodes on the same position typically can be rewired with Reconnect Nodes. *需要 Vanilla JavaScript*
* **Rotate Around Anchor:** GUI for rotating glyphs or selections of nodes and components around a 'rotate' anchor. Allows to step and repeat. *需要 Vanilla JavaScript*
* **Set Transform Origin:** Simple GUI for setting the Transform Origin of the Rotate tool numerically. Should also have an effect on the Scale tool. *需要 Vanilla JavaScript*
* **Straight Stem Cruncher:** Finds distances between points in all layers, and compares them (with a tolerance) to specified stem widths. Lists glyphs that have deviating stems in their drawings. *需要 Vanilla JavaScript*
* **Tunnify:** Looks for all path segments where at least one handle is selected. Then, evens out the handles of the segments, i.e., they will both have the same Fit Curve percentage. Can fix Adobe Illustrator's zero-handles (segments with one handle retracted into the nearest node). The idea for this script came from Eduardo Tunni (as colported by Pablo Impallari), hence the title of the script. I have never seen Eduardo's algorithm though, so my implementation might be a little different to his, especially the treatment of zero-handles.

## 點陣字型

*These scripts are useful for a pixelfont workflow, where you place a pixel component in a coarser grid. If you are doing pixel designs, take a look at the pixel-related plug-ins available in Window > Plugin Manager.這些腳本對於 pixelfont 工作流程很有用，您可以在其中將像素組件放置在較粗糙的網格中。如果您正在進行像素設計，請查看窗口 > 插件管理器中可用的像素相關插件。*

* **Align Anchors to Grid:** Snaps diacritic anchors onto the font grid.
* **Delete Components out of Bounds:** If a component is placed far outside the usual coordinates (happens when you cmd-arrow components with a high grid step), this script will delete them.
* **Delete Duplicate Components:** Looks for duplicate components (same name and position) and keeps only one. Happens frequently when buliding pixel fonts.
* **Flashify Pixels:** Creates small bridges in order to prevent self-intersection of paths so counters stay white. This is especially a problem for the Flash font renderer, hence the name of the script.
* **Reset Rotated and Mirrored Components:** Looks for scaled, mirrored and rotated components and turns them back into their default scale and orientation, but keeps their position. Useful for fixing mirrored pixels.

## 小體大寫字母

*When I have Smallcaps in my font, I always run Check Smallcap Consistency. Take its report with a grain of salt though: it lists a lot of false positives, and not every warning is equally important.當我的字體中有 Smallcaps 時，我總是運行 Check Smallcap Consistency。不過，對它的報告持保留態度：它列出了很多誤報，而且並非每個警告都同樣重要。*

* **Check Smallcap Consistency:** Performs a few tests on your SC set and reports into the Macro window, especially kerning groups and glyph set.
* **Copy Kerning from Caps to Smallcaps:** Looks for cap kerning pairs and reduplicates their kerning for corresponding .sc glyphs, if they are available in the font. Please be careful: Will overwrite existing SC kerning pairs.

## 間距

*Most important: Fix Math Operator Spacing, Bracket Metrics Manager and, if you have arrows, Fix Arrow Positioning. The New Tab scripts are useful when creating figures.最重要的是：修復數學運算符間距、括號度量管理器，如果有箭頭，修復箭頭定位。新建標籤腳本在創建圖形時很有用。*

* **Add Metrics Keys for Symmetric Glyphs:** Will add RSB =| if the RSB is the same as the LSB in all masters. *需要 Vanilla JavaScript*
* **Bracket Metrics Manager:** Manage the sidebearings and widths of bracket layers, e.g., dollar and cent. *需要 Vanilla JavaScript*
* **Center Glyphs:** Centers all selected glyphs inside their width, so that LSB=RSB.
* **Change Metrics by Percentage:** Change LSB/RSB of selected glyphs by a percentage value. Undo with the Revert button. *需要 Vanilla JavaScript*
* **Find and Replace in Metrics Keys:** GUI for searching and replacing text in the L and R metrics keys, e.g. replace '=X+15' by '=X'. Leave the search field blank for appending.
* **Fix Arrow Positioning:** Fixes the placement and metrics keys of arrows, dependent on a specified default arrow. Adds metric keys and moves arrows vertically. Does not create new glyphs, only works on existing ones. *需要 Vanilla JavaScript*
* **Fix Math Operator Spacing:** Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also lesser/greater symbols and asciicircum/asciitilde. *需要 Vanilla JavaScript*
* **Freeze Placeholders:** In the current Edit tab, will change all inserted placeholders for the current glyph, thus 'freeze' the placeholders.
* **Metrics Key Manager:** Batch apply metrics keys to the current font. *需要 Vanilla JavaScript*
* **Monospace Checker:** Checks if all glyph widths in the frontmost font are actually monospaced. Reports in Macro Window and opens a tab with affected layers. *需要 Vanilla JavaScript*
* **New Tab with all Figure Combinations:** Opens a new tab with all possible figure combos. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Fraction Figure Combinations:** Opens an Edit tab with fraction figure combos for spacing and kerning.
* **Remove Layer-Specific Metrics Keys:** Deletes left and right metrics keys specific to layers (==), in all layers of all selected glyphs. Also simplifies glyph metrics keys (i.e., turns "=H" into "H").
* **Remove Metrics Keys:** Deletes both left and right metrics keys in all selected glyphs. Affects all masters and all layers.
* **Reset Alternate Glyph Widths:** Resets the width of suffixed glyphs to the width of their unsuffixed counterparts. E.g., `Adieresis.ss01` will be reset to the width of `Adieresis`.
* **Spacing Checker:** Look for glyphs with unusual spacings and open them in a new tab. *需要 Vanilla JavaScript*
* **Steal Metrics:** Steals the sidebearing or width values for all selected glyphs from a 2nd font. Optionally also transfers metrics keys like '=x+20'. *需要 Vanilla JavaScript*
* **Tabular Checker:** Goes through tabular glyphs and checks if they are monospaced. Reports exceptions. *需要 Vanilla JavaScript*

## 測試

*推薦「測試用 HTML 腳本」。如果您在 Adobe 或 Apple 應用程式中發現選取框異常的高或低，可以執行「最高和最低點字符報告」查詢找出導致狀況發生的字符。「拉丁字母支援語言報告」提供的資訊是參考性的建議，不是絕對要遵守的規範。*

* **Copy InDesign Test Text / 複製 InDesign 測試文字：** 將 InDesign 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Copy Word Test Text / 複製 Word 測試文字：** 將 Word 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Language Report / 拉丁字母支援語言報告：** 在巨集視窗輸出讓您初步了解您的拉丁字符支持多少種語言以及哪些語言的資訊。基於 Underware's Latin-Plus 列表，並進行了修改。
* **Pangram Helper / 全字母句小幫手：** 幫助您編寫歐文的全字母句，您可以將其複製到剪貼簿或放入新分頁中。 *需要 Vanilla JavaScript* *:question:成果 其他字母句要自己添加？*
* **Report Highest and Lowest Glyphs / 最高和最低點字符報告：** 讀取所有母版的所有字符，在巨集視窗輸出最高和最低點字符的資訊。
* **Variable Font Test HTML / 可變字型測試 HTML：** 為目前已輸出到資料夾的可變字型在預設瀏覽器開啟一個測試用的 HTML。
* **Webfont Test HTML / 網頁字型測試 HTML：** 為目前已輸出到資料夾的網頁字型或當前的字符專案在預設瀏覽器開啟一個測試用的 HTML。

# License

Copyright 2011 The mekkablue Glyphs-Scripts Project Authors.

Some code samples by Georg Seifert (@schriftgestalt) and Tal Leming (@typesupply).

Some algorithm input by Christoph Schindler (@hop) and Maciej Ratajski (@maciejratajski).

Some code fixes from Rafał Buchner (@RafalBuchner).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the software provided here except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.
