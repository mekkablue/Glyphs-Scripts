# 關於

這是在 [字型編輯軟體 Glyphs](http://glyphsapp.com/) 中製作字型時使用的 Python 腳本集。

# 安裝

## Glyphs 3

1. **安裝模組：** 在 *視窗 > 外掛程式管理員* 點擊 *模組* 分頁，確保安裝了最新版本的 [Python](glyphsapp3://showplugin/python) 和 [Vanilla](glyphsapp3://showplugin/vanilla) 模組。如果之前從未安裝過，請在完成安裝後重新啟動程式。
2. **安裝腳本：** 前往 *視窗 > 外掛程式管理員* 點擊上方的 *腳本* 分頁。往下捲動到 [mekkablue scripts](glyphsapp3://showplugin/mekkablue%20scripts) 後點擊 *安裝* 按鈕下載它。

現在該腳本集已被安裝在 *腳本 > mekkablue*。如果你沒有在 *腳本* 選單看到該腳本集，請按著 Option 鍵選擇 *腳本 > 重新載入腳本* (Cmd-Opt-Shift-Y)。


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

*「錨點移動器」用於批次處理錨點位置，在調整 x 高度之後會很有用。 輕而易舉：在組合標記上使用「重新定位」腳本，能讓你在斜體角度時也能維持一致。*

* **Anchor Mover / 錨點移動器：** 在一個操作視窗中批次移動多個字符中的錨點位置。 *需要 香草JS*
* **Batch Insert Anchors / 批次插入錨點：** 在一個操作視窗中批次在多個字符的相近位置批次插入錨點。 *需要 香草JS*
* **Find and Replace in Anchor Names / 尋找與取代錨點名稱：** 在一個操作視窗中搜尋並替換特定的錨點名稱（尋找範圍為選定字符的所有圖層）。 *需要 香草JS*
* **Fix Arabic Anchor Order in Ligatures / 修復連字中的阿拉伯文錨點順序：** Fixes the order of *top_X* and *bottom_X* anchors to RTL. In files converted from a different format, it sometimes happens that *top_1* is left of *top_2*, but it should be the other way around, otherwise your mark2liga will mess up. This script goes through your selected glyphs, and if they are Arabic ligatures, reorders all anchors to RTL order, at the same time not touching their coordinates.
* **Insert All Anchors in All Layers / 在所有圖層插入錨點：** 為該字符的所有圖層加入遺失的錨點（如果該錨點沒有出現在所有圖層中的話）。
* **Insert exit and entry Anchors to Selected Positional Glyphs / 在選定的位置字符上插入 exit/entry 錨點：** Adds entry and exit anchors for cursive attachment in selected glyphs. By default, it places the exit at (0, 0) and the entry at a node at RSB if such a node exists. Please adjust for your own needs.
* **Mark Mover / 標號移動器：** 將結合用標號移到相對應的高度。例如大寫上標符號移到大寫高度，小寫上標符號移到 x 高度...等。你也可以另外設定左右間距的數值。 *需要 香草JS*
* **Move ogonek Anchors to Baseline Intersection / 將反尾形符錨點移動到基線交界處：** 將所有反尾形符錨點和結合用錨點移動到字符線框最右側和基線的交界處。
* **Move topright Anchors for Vertical Carons / 移動垂直抑揚符的右上角錨點：** Moves all topright and _topright anchors to the rightmost intersection of the outline with the x-height. Useful for building Czech/Slovak letters with vertical caron.
* **Move Vietnamese Marks to top_viet Anchor in Circumflex / 移動越南語標號到揚抑符中的 top_viet 錨點上：** Moves *acute*, *grave* and *hookabovecomb* to the *top_viet* anchor in every layer of selected glyphs. Useful for Vietnamese double accents. Assumes that you have *top_viet* anchors in all layers of *circumflexcomb*.
* **New Tab with Glyphs Containing Anchor / 新分頁－所有包含錨點的字符：** 打開一個新分頁，該分頁包含所有已製作錨點的字符。
* **New Tab with top and bottom Anchors Not on Metric Lines / 新分頁－所有位在度量線上的頂部和底部錨點：** 將所有 *top* 和 *bottom* 錨點的垂直高度資訊顯示在巨集面板上，並且開啟一個新分頁，列出所有主板或支撐層中錨點位置不在度量線位置上的字符。
* **Prefix all exit/entry anchors with a hashtag / 在所有 exit/entry 錨點前加上主題標籤：** Looks for all exit and entry anchors anywhere in the font, and disables `curs` feature generation by prefixing their anchor names with `#`.
* **Realign Stacking Anchors / 重新對齊堆疊錨點：** In stacking combining accents, moves top and bottom anchors exactly above or below the respective _top and _bottom anchors, respecting the italic angle. This way, stacking multiple nonspacing accents will always stay in line. *需要 香草JS*
* **Remove Anchors in Suffixed Glyphs / 刪除後綴字符中的錨點：** Removes all anchors from glyphs with one of the user-specified suffix. Useful for removing left-over anchors in sups/subs/sinf/ordn variants of glyphs after copying, scaling and editing. *需要 香草JS*
* **Remove Anchors / 移除錨點：** 刪除選定字符（或整個字型）中具有指定名稱的錨點。 *需要 香草JS*
* **Remove Non-Standard Anchors from Selected Glyphs / 移除選定字符的異常錨點：** Removes all anchors from a glyph that should not be there by default, e.g., `ogonek` from `J`. Potentially dangerous, because it may delete false positives. So, first use the report script below.
* **Replicate Anchors / 複製錨點：** 在操作視窗中選擇一個來源字符，並在目前的字符上批次加入錨點。 *需要 香草JS*
* **Replicate Anchors in Suffixed Glyphs / 複製錨點到後綴字符：** 掃描選取的後綴字符，從它們的基本字符複製錨點過來。 例如將 *X* 的錨點貼到 *X.ss01*、*X.swsh* 和 *X.alt* 上。
* **Report Non-Standard Anchors to Macro window / 在巨集面板回報異常錨點資訊：** 掃描字型中的所有字符，將偵測到的異常錨點顯示在巨集面板中，命令行內容可被複製貼上到編輯畫面中。
* **Shine Through Anchors / (翻譯名稱)：** In all layers of selected glyphs, inserts ‘traversing’ anchors from components.

## 應用程式（已完成v1）

*如果你正在寫程式，請為「方法報告器」添加快捷鍵，你將非常需要它。如果你想要一個與解析度無關的視窗內容的PDF螢幕截圖讓你可以在向量插圖應用程式中進行後製，「列印視窗」可以派上用場。*

* **Close All Tabs of All Open Fonts / 關閉所有字型檔的編輯分頁：** 關閉目前在應用程式中開啟字型檔的所有編輯分頁。
* **Copy Download URL for Current App Version / 複製目前應用程式版本的下載連結：** 將目前 Glyphs 應用程式版本的下載連結放入剪貼簿以便於貼上。
* **Decrease and Increase Line Height / 減少和增加行高：** 將「編輯畫面」的行高增加四分之一或減少五分之一。如果你需要在行高之間頻繁切換，推薦將它們設定到快捷鍵。
* **Method Reporter / 方法報告器：** 圖形使用者介面用於過濾 Glyphs 中可用的 Python 和 PyObjC 類的方法名稱。你可以使用多個空格分隔檢索詞（用於 AND 串接）和星號作為未知字元（可放在開頭、中間和結尾）。按兩下可將方法名稱放入剪貼簿，然後在巨集視窗中打開説明。對寫程式的人很有用。 *需要 香草JS*
* **Navigate - Activate next and previous glyph / ：** 啟動下一個或上一個字符的編輯模式。
* **Parameter Reporter / 參數報告器：** 類似於方法報告器，但用於自定義參數。按兩下以複製剪貼簿中的參數，準備貼到字型資訊中。 *需要 香草JS*
* **Print Window / 列印視窗：** 列印當前視窗。用於保存視窗內容的向量 PDF，包括檢視器外掛的渲染（“顯示”選單的擴展）。 *:question:成果*
* **Resetter / 重置器：** 重置快速查看預覽、鍵盤快捷鍵和清除偏好設定、已儲存的應用程式狀態和自動儲存。 *需要 香草JS*
* **Set Export Paths to Adobe Fonts Folder / 將匯出路徑設置為 Adobe Fonts 資料夾：** 將 OpenType 字型和可變字型的匯出位置設定為 Adobe 字型資料夾。
* **Set Hidden App Preferences / 設定隱藏的應用程式偏好設定：** GUI for reading and setting ‘hidden’ app preferences, which are not listed in the GUI.一個用於讀取和設定「隱藏」的應用程式偏好設定的圖形使用者介面，這些偏好設定未在圖形使用者介面中列出。 *需要 香草JS* *:question:翻譯*
* **Set Label Colors / 設定標籤顏色：** 覆蓋預設應用程式標籤顏色。 *需要 香草JS*
* **Set Tool Shortcuts / 設定工具快捷鍵：** 為工具列中的工具設置鍵盤快捷鍵。 *需要 香草JS*
* **Toggle Horizontal-Vertical / 切換 橫排-直排：** 在當前分頁切換橫排（左起）-直排書寫方向。推薦在「系統偏好設定」中設定快捷鍵使用。
* **Toggle RTL-LTR / 切換 右起-左起：** 在當前分頁切換右起-左起書寫方向。推薦在「系統偏好設定」中設定快捷鍵使用。
* **Update git Repositories in Scripts Folder / 更新文本資料夾中的 git 儲存庫：** 對 Glyphs 腳本資料夾中的所有子資料夾執行「git pull」指令。如果腳本資料夾中有很多 git 儲存庫就很有用。 *:question:功能*

## 建構字符

*推薦腳本：「引用符管理器」，以及用於小型大寫數字、符號和 ​​Ldot 的「構建腳本」。其他腳本主要是為了讓你快速開始覆蓋某些 Unicode 範圍如果客戶有需求。*

* **Build APL Greek / (翻譯名稱)：** Create APL Greek glyphs.
* **Build careof and cadauna / (翻譯名稱)：** Builds `cadauna` and `careof` from your `c`, `o`, `u` and `fraction` glyphs.
* **Build Circled Glyphs / (翻譯名稱)：** Builds circled numbers and letters (U+24B6...24EA and U+2460...2473) from `_part.circle` and your letters and figures. *需要 香草JS*
* **Build Dotted Numbers / (翻譯名稱)：** Build dotted numbers from your default figures and the period.
* **Build ellipsis from period components / (翻譯名稱)：** Inserts exit and entry anchors in the period glyph and rebuilds ellipsis with auto-aligned components of period. Attention: decomposes all period components used in other glyphs (e.g., colon).
* **Build Extra Math Symbols / (翻譯名稱)：** Builds `lessoverequal`, `greateroverequal`, `bulletoperator`, `rightanglearc`, `righttriangle`, `sphericalangle`, `measuredangle`, `sunWithRays`, `positionIndicator`, `diameterSign`, `viewdataSquare`, `control`.
* **Build Ldot and ldot / (翻譯名稱)：** Builds `Ldot`, `ldot` and `ldot.sc` from existing `L` and `periodcentered.loclCAT` (`.case`/`.sc`). Assumes that you have already created and properly spaced `L`-`periodcentered.loclCAT`-`L`, etc.
* **Build Parenthesized Glyphs / (翻譯名稱)：** Creates parenthesized letters and numbers: `one.paren`, `two.paren`, `three.paren`, `four.paren`, `five.paren`, `six.paren`, `seven.paren`, `eight.paren`, `nine.paren`, `one_zero.paren`, `one_one.paren`, `one_two.paren`, `one_three.paren`, `one_four.paren`, `one_five.paren`, `one_six.paren`, `one_seven.paren`, `one_eight.paren`, `one_nine.paren`, `two_zero.paren`, `a.paren`, `b.paren`, `c.paren`, `d.paren`, `e.paren`, `f.paren`, `g.paren`, `h.paren`, `i.paren`, `j.paren`, `k.paren`, `l.paren`, `m.paren`, `n.paren`, `o.paren`, `p.paren`, `q.paren`, `r.paren`, `s.paren`, `t.paren`, `u.paren`, `v.paren`, `w.paren`, `x.paren`, `y.paren`, `z.paren`.
* **Build Q from O and _tail.Q / (翻譯名稱)：** Run this script *after* doing *Component from Selection* on the Q tail and naming it `_tail.Q`.
* **Build Rare Symbols / (翻譯名稱)：** Builds white and black, small and large, circles, triangles and squares. *需要 香草JS*
* **Build rtlm Alternates / (翻譯名稱)：** Creates horizontally mirrored composites for selected glyphs and updates the rtlm OpenType feature. Auto-aligns the components, but also adds metrics keys that kick in in case you decompose.
* **Build Small Figures / (翻譯名稱)：** Takes a default set of figures (e.g., `.dnom`), and derives the others (`.numr`, `superior`/`.sups`, `inferior`/`.sinf`, `.subs`) as component copies. Respects the italic angle. *Need Vanilla.*
* **Build small letter SM, TEL / (翻譯名稱)：** Creates the glyphs: `servicemark`, `telephone`.
* **Build space glyphs / (翻譯名稱)：** Creates `mediumspace-math`, `emquad`, `emspace`, `enquad`, `enspace`, `figurespace`, `fourperemspace`, `hairspace`, `narrownbspace`, `punctuationspace`, `sixperemspace`, `nbspace`, `thinspace`, `threeperemspace`, `zerowidthspace`.
* **Build Symbols / (翻譯名稱)：** Creates symbol glyphs such as `.notdef` (based on the boldest available `question` mark), an `estimated` glyph, as well as `bar` and `brokenbar` (for which it respects standard stems and italic angle). *需要 香草JS*
* **Fix Punctuation Dots and Heights / (翻譯名稱)：** Syncs punctuation dots between ¡!¿? (and their SC+CASE variants). Will use dot from exclam in all other glyphs, and shift ¡¿ in SC and CASE variants. Assumes that ¡¿ are components in !?. Detailed report in Macro Window..
* **Quote Manager / 引用符管理器：** Build double quotes from single quotes, and insert `#exit` and `#entry` anchors in the single quotes for auto-alignment. You need to have the single quotes already. *需要 香草JS*

## 彩色字型（已完成v1）

*這些腳本能幫助你在製作彩色字體的工作流程中解決遇到的問題。「合併腳本」主要用於為 CPAL/COLR 字型創建後備字符。這個方式產生的後備字符將會填滿編輯框，且不會在 Chrome 瀏覽器中發生裁切。*

* **Add All Missing Color Layers to Selected Glyphs / 加入所有遺失的顏色圖層到選定字符中：** 為所選字符在色盤參數定義的每個 (CPAL/COLR) 顏色添加圖層，該圖層從備用層複製並轉換為色盤圖層。該腳本只添加字符中仍然缺少的顏色。
* **Add sbix Images to Font / 加入sbix圖片到字型中：** 將獲取文件夾中的所有 PNG、GIF、JPG 文件，並在當前字型和主板中使用它們建立 iColor 圖層。文件名格式： `字符名稱 像素尺寸.副檔名` ，例： `Adieresis 128.png` 。
* **Convert Layerfont to CPAL+COLR Font / 將圖層字型轉換為CPAL+COLR字型：** 將圖層彩色字型轉換為在每個字符中具有 CPAL 和 COLR 層的單一主板字型。它將以第一個主板作為備用字體層。
* **Delete Non-Color Layers in Selected Glyphs / 刪除選定字符的非顏色圖層：** 刪除所有字符中不是 `色盤` 類型的所有子圖層（CPAL/COLR 層）。
* **Merge All Other Masters in Current Master / 將所有其他主板合併到當前主板：** 在所選字符中，將所有路徑從其他主板複製到目前主板層。
* **Merge Suffixed Glyphs into Color Layers / 合併關聯字符到顏色層中：** 將 `x.shadow` 、 `x.body` 和 `x.front` 合併到 `x` 的單獨 CPAL 顏色圖層中。 *需要 香草JS*
* **sbix Spacer / sbix字型空間調整器：** 大量設定 sbix 位置和字符寬度。 *需要 香草JS*

## 比較當前字型（已完成v2）

*這些腳本用於同步正體和它們的斜體。打開兩個字型檔，然後運行腳本。它們不會更改你的字型，但會在巨集視窗中顯示詳細的報告。*

* **Compare Font Info > Font / 比較字型資訊 > 字型：** 對於前兩個字型檔，詳細比較字型資訊 > 字型，並在巨集面板中輸出報告。
* **Compare Font Info > Masters / 比較字型資訊 > 主板：** 對於前兩個字型檔，詳細比較字型資訊 > 主板，並在巨集面板中輸出報告。
* **Compare Font Info > Instances /  比較字型資訊 > 匯出：** 對於前兩個字型檔，詳細比較字型資訊 > 匯出，並在巨集面板中輸出報告。
* **Compare Font Info > Features / 比較字型資訊 > 特性：**  對於前兩個字型檔，詳細比較字型資訊 > 特性，並在巨集面板中輸出報告。
* **Compare Anchors / 比較錨點：** 比較前兩個字型檔之間的錨點結構和錨點高度。
* **Compare Composites / 比較複合字元：** 報告複合字符的不同結構，例如在一個字型中使用   `acutecomb` 構建的 `iacute`，而在另一個字型中使用 `acutecomb.narrow`。
* **Compare Glyph Heights / 比較字符高度：** 列出所有在字高方面與第二個字體差異超過給定閾值的字符。
* **Compare Glyph Info / 比較字符資訊：** 比較開啟的字型，並建立一個差異字符資訊列表，包括Unicode值和分類。 *需要 香草JS*
* **Compare Glyphsets / (翻譯名稱)：** 比較前兩個字型檔的字符集，並在巨集視窗中輸出報告。
* **Compare Kerning Groups / 比較調距群組：** 比較前兩個字型檔之間的調距群組，輸出具有差異的群組字符名稱表格。
* **Compare Metrics / 比較度量：** 比較前兩個字型檔的字形寬度。
* **Compare Sidebearings / 比較字符邊界：** 比較前兩個字型檔的字符邊界。

## 組件（已完成v1）

*當你使用其他字母構建字母時「使用組件填充背景」非常有用，例如：ae 或 oe，該腳本將會把 e 放在每個母版的背景中，且使用者介面有一個選項可以將選定的點與背景中的 e 對齊。如果你正在使用角落組件製作多母版的襯線字體，「傳播角落組件到其他主板」將為你節省大量時間。*

* **Alignment Manager / 對齊管理器：** 啟用或停用所選字符中可見圖層上所有組件的自動就定位。與右鍵選單中的命令相同，但您可以一步完成多個字符。 *需要 香草JS*
* **Component Mover / 組件移動器：** 跨選定字符批量編輯（智慧）組件。更改位置、比例和智慧組件屬性。 *需要 香草JS*
* **Component Problem Finder / 組件問題查找器：** 查找組件和角落組件可能存在的問題：同時包含路徑和部件的組合字符；鎖定、嵌套、孤立、鏡像、平移、旋轉和縮放組件；具有異常組件順序或非正統組件結構的複合字符。也包含未連接和縮放過的角落組件。 *需要 香草JS*
* **Decompose Components in Background / 拆開背景中的組件：** 拆開所選字符的背景圖層。適用於當前主板或所有主板，或所有字型的所有主板。
* **Decompose Corner and Cap Components / 拆開角落和筆帽組件：** 拆開選定字符中的所有角落和筆帽組件。開啟巨集視窗顯示報告。
* **Find and Replace Components / 置換組件：** 將所選字符中的組件重新連結到新的來源。 *需要 香草JS*
* **Find and Replace Cap and Corner Components / 置換角落和筆帽組件：** 將所選字符中的 `_cap.*` 和 `_corner.*` 組件重新連結到新的角落和筆帽組件。 *需要 香草JS*
* **Find and Replace Corner Components at Certain Angles / 依角度置換角落組件：** 以鈍角或銳角替換角落組件。 *需要 香草JS*
* **Move Paths to Component / 將路徑移動到組件：** 將路徑移動到單獨的字符中，並將它們作為錨定的自動就定位組件插入原本的字符中。非常適合將路徑和組件混雜的字符整理成純組件字符。 *需要 香草JS*
* **Populate Backgrounds with Components / 使用組件填充背景：** 添加組件到所選字符的所有背景中。 *需要 香草JS*
* **Propagate Corner Components to Other Masters / 傳播角落組件到其他主板：** 嘗試在同一字符的所有其他主板中重新創建當前主板圖層的角落組件。請確保你的外框是兼容的。
* **Remove Components / 刪除組件：** 從選定（或所有）的字符中刪除指定的組件。
* **Remove Detached Corners / 刪除分離的角落組件：** 從選定（或所有）的字符中移除分離的角落組件。
* **Stitcher / 打洞器：** 打洞器會以固定間隔在您的路徑上插入組件。用於將開放路徑變成虛線。使用稱為 `origin` 的錨點來確定拼接字母中的組件位置。考慮改用 [ Stitcher 外掛](glyphsapp3://showplugin/Stitcher)。 *需要 香草JS*
* **Sync Components Across Masters / 跨主板同步組件：** 獲取目前圖層的組件，並將所有其他主板重置為相同的組件結構。忽略路徑和錨點。按住 Option 鍵 *刪除* 所有路徑和錨點。

## 特性

*在製作手寫風格字體時，你可能經常需要「建構位置變體」的腳本。如果你發現自己經常開關 OT 功能，請用看看「啟動預設特性」和「浮動特性」腳本。並到 視窗 > 外掛程式管理員 看看 Set Palette 這個外掛。*

* **Activate Default Features / 啟動預設特性：** In the current Edit tab, activates all OT features that are recommended to be on by default (according to the spec).
* **Build ccmp for Hebrew Presentation Forms / (翻譯名稱)：** Builds the ccmp feature for precomposed `uniFBxx` glyphs, e.g. if you have pedagesh, you get 'sub pe dagesh by pedagesh' in your ccmp.
* **Build Italic Shift Feature / (翻譯名稱)：** Creates and inserts GPOS feature code for shifting glyphs, e.g., parentheses and punctuation for the case feature. *需要 香草JS*
* **Build Positional Feature / 建構位置變體特性：** Looks for `.init`, `.medi`, `.fina`, and `.isol` glyphs, and injects positional substitution code into your `calt` feature (or any other feature you specify). If run again, will *update* class and feature code. See this tutorial for more info: https://glyphsapp.com/learn/features-part-4-positional-alternates *需要 香草JS*
* **Build rand Feature / (翻譯名稱)：** Build rand (random) feature from .cvXX or another (numbered) suffix. *需要 香草JS*
* **Feature Code Tweaks / (翻譯名稱)：** Adds tweaks to OT feature code. Reports in Macro window. Careful: if you do not understand an option, do not use it. *需要 香草JS*
* **Find in Features / (翻譯名稱)：** Finds expressions (glyph, lookup or class names) in OT Features, Prefixes and Classes. *需要 香草JS*
* **Floating Features / 浮動特性：** Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. *需要 香草JS*
* **Fraction Fever 2 / (翻譯名稱)：** Insert Tal Leming’s Fraction Fever 2 code into the font. Read more in this tutorial: https://glyphsapp.com/learn/fractions
* **New OT Class with Selected Glyphs / (翻譯名稱)：** GUI for creating a new OT class with the selected glyphs. *需要 香草JS*
* **New Tab with OT Class / (翻譯名稱)：** GUI for opening all glyphs in an OT class (listed in *File > Font Info > Features > Classes*) in a new tab. *需要 香草JS*
* **Update Features without Reordering / (翻譯名稱)：** Goes through the existing features in the font and refreshes each one of them. Does neither add nor reorder features.
* * **Stylistic Sets > Synchronize ssXX glyphs / (翻譯名稱)：** Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> the script creates *b.ss02*
* * **Stylistic Sets > Create ssXX from layer / (翻譯名稱)：** Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
* * **Stylistic Sets > Create pseudorandom calt feature / (翻譯名稱)：** Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Also includes the default class in the rotation algorithm.
* * **Stylistic Sets > Set ssXX Names / (翻譯名稱)：** Prefills names for ssXX features with ‘Alternate’ or another chosen text, plus the name of the first substituted glyph, e.g., ‘Alternate a’. Option to preserve existing namings.*需要 香草JS*

## 字型資訊（已完成v1）

*「垂直度量管理器」對於在 字型資訊 視窗的 字型 和 主板 分頁中尋找和同步垂直度量參數很好用。「清除版本字串」也非常好用。「字型資訊批量設定器」是在多個字型檔之間同步字型資訊設定的必備工具。留意「設定 WWS/Preferred 名稱」腳本：Glyphs 通常會自動處理命名，因此使用它們的機會非常少。*

* **Clean Version String / 清除版本字串：** 添加一個乾淨的 版本字串 參數，並禁用版本字串中的 ttfAutohint 訊息。導出的字型將具有僅包含“Version X.XXX”的版本字符串。 *:question:ttfAutohint功能*
* **Find and Replace in Font Info / 尋找與取代字型資訊：** 尋找與取代在 *字型資訊 > 字型* 和 *字型資訊 > 匯出* 中的名稱。（不包含本地化名稱和數值） *需要 香草JS*
* **Find and Replace In Instance Parameters / 尋找與取代匯出的參數：** 尋找和取代在目前字型或項目文件中選定樣式的自定義參數。
* **Font Info Batch Setter / 字型資訊批次設定器：** 批次設定已開啟字型的 *字型資訊 > 字型* 數值：包含設計師、設計師 URL、製造商、製造商 URL、版權、版本號、日期和時間。對於跨多種字型同步字型資訊設定很有用。 *需要 香草JS*
* **Font Info Overview / 字型資訊概覽：** 列出所有已開啟字型檔的部分字型資訊數值。 *:question:功能？*
* **Prepare Font Info / 準備字型資訊：** 通過設定部分自定義參數，為現代字型製作和 git 工作流程準備開放字體 *:question:開源？* 。 *需要 香草JS*
* **Remove Custom Parameters / 刪除自定義參數：** 從字型資訊 > 字型、主板、匯出中刪除其中一種類型的所有參數。如果您有許多主板或樣式就會很有用。 *需要 香草JS*
* **Set Preferred Names (Name IDs 16 and 17)  for Width Variants / 為寬度變體設定首選名稱：** 為所有樣式設定首選名稱的自定義參數（名稱 ID 16 和 17），以便使寬度變體顯示在 Adob​​e 應用程序的單獨清單中。
* **Set Style Linking / 設定樣式連結：** Attempts to set the Bold/Italic bits.嘗試設置粗體/斜體位。 *:question:不懂名詞bit*
* **Set Subscript and Superscript Parameters / 設定下標和上標參數：** 測量您的上標和下標圖形並導出下標/上標 X/Y 偏移/尺寸參數。 *需要 香草JS* *:question:沒用過*
* **Set WWS Names (Name IDs 21 and 22) / 設定 WWS 名稱（名稱 ID 21 和 22）：** 在必要時為所有樣式設定 WWS 自定義參數（名稱 ID 21 和 22）：將除 RIBBI 之外的所有訊息放入 WWSFamilyName，並且僅保留 WWSSubfamilyName 的 RIBBI。 *:question:名詞釋義？*
* **Style Renamer / 樣式改名器：** 將名稱詞綴批次加入到您的樣式名稱中，或將其從樣式名稱中批次刪除。用於將所有樣式從斜體轉換為羅馬體的名稱，反之亦然。 *需要 香草JS*
* **Vertical Metrics Manager / 垂直度量管理器：** Calculate and insert values for OS/2 usWin and sTypo, hhea and fsSelection bit 7 (for preferring sTypo Metrics over usWin metrics).計算並插入 OS/2 usWin 和 sTypo、hhea 和 fsSelection 位 7 的值（用於優先使用 sTypo 指標而不是 usWin 指標）。*:question:不懂名詞bit* *需要 香草JS*

## 字形名稱、註釋和 Unicode（已完成v1）

*大多數腳本使管理字符名稱和 Unicode 更簡單一點。「垃圾收集」對於在將文件移交給第三方之前清理回報器腳本或其他註釋的雜亂很有用。*

* **Add PUA Unicode Values to Selected Glyphs / 添加 PUA Unicode 值到選定的字符：** 將所選字符套用使用者自訂義的 Unicode 值。 *需要 香草JS*
* **Color Composites in Shade of Base Glyph / 添加關聯的字符顏色標籤：** 基於基本字符添加較淡的字符顏色標籤。例如：如果 A 的顏色標籤是紅色，則 ÄÁÀĂ... 等相關聯字符將添加較淡的淺紅色標籤。
* **Convert to Uppercase / 轉換為大寫：** 將小寫名稱轉換為大寫名稱，例如： `a` → `A`, `ccaron` → `Ccaron`, `aeacute` → `AEacute` ...等。
* **Convert to Lowercase / 轉換為小寫：** 將選定字符的名稱轉為小寫。
* **Encoding Converter / 編碼轉換器：** 基於具有重命名方案的可導入/可導出文本，將舊的專家 8 位編碼轉換為 Glyphs 漂亮的名稱。默認是 AXt 轉換方案。Converts old expert 8-bit encodings into Glyphs nice names, based on a importable/exportable text with renaming scheme. Default is an AXt converting scheme. *需要 香草JS*
* **Garbage Collection / 垃圾收集：** 刪除字符中的標記，例如節點名稱、字符名稱或註釋以及參考線。
* **New Tab with Uppercase-Lowercase Inconsistencies / 新分頁－大小寫不一致：** 打開一個新分頁，其中包含所有大小寫不一致的字符。在巨集視窗中列出詳細報告。
* **Production Namer / 生產名稱：** 覆蓋默認的生產名稱。默認是在遺留 PDF 工作流程中產生問題的常見主題：mu、onesuperior、twosuperior、threesuperior。Override default production names. Default are the usual subjects which create problems in legacy PDF workflows: mu, onesuperior, twosuperior, threesuperior. *需要 香草JS*
* **Rename Glyphs / 重命名字符：** 獲取 `oldglyphname=newglyphname` 清單並相應的重命名字型中的字符，類似於自訂義參數 *Rename Glyphs* 。 *需要 香草JS*
* **Reorder Unicodes of Selected Glyphs / 重新排序所選字符的 Unicode：** 重新排序 Unicode，使默認 Unicode 排在第一位。
* **Switch Mirrored Characters / 切換鏡像字元：** 在目前編輯畫面中，切換鏡像雙向字元，例如 () 到 )( 。用於在分頁中切換書寫方向後，切換括號和引號。

## 參考線（已完成v1）

*這些腳本主要用於清理在處理第三方字體時看到的過多參考線。*

* **Guides through All Selected Nodes / 生成通過所有已選節點的參考線：** 在目前字符中穿過所有已選擇節點放置參考線。盡量避免參考線重複。
* **Remove Global Guides in Current Master / 刪除目前主板的全域參考線：** 刪除目前主板中的所有全域（紅色）參考線。
* **Remove Local Guides in Selected Glyphs / 刪除已選擇字符的區域參考線：** 刪除選定字符中的所有區域（藍色）參考線。
* **Select All Global Guides / 全選全域參考線：** 在編輯區域中選擇所有全域（紅色）參考線。如果你有很多並且需要批次轉換它們會非常有用。
* **Select All Local Guides / 全選區域參考線：** 選擇所有區域（藍色）參考線（在所有已選擇的字符中）。

## 字體微調

*Most important: Set blueScale, Set Family Alignment Zones for PostScript hinting. If you are making big changes, The Transfer and Keep Only scripts can save you a lot of work. The New Tab scripts help find glyphs missing zones. Also consider Paths > Find Near Vertical Misses for that purpose.推薦腳本：「設定 blueScale」「為 PostScript 提示設置系列對齊區域」。如果你要進行大的更改，「Transfer」和「Keep Only」腳本可以為你節省大量工作。「新標籤」腳本有助於找到字形缺失區域。為此，還可以考慮路徑 > 查找近垂直未命中。* *:question:翻譯 專業領域暫時擱置*

* **Add Alignment Zones for Selected Glyphs / (翻譯名稱)：** Creates fitting zones for the selected glyphs in all masters. *需要 香草JS*
* **Add Hints for Selected Nodes / (翻譯名稱)：** Adds hints for the selected nodes. Tries to guess whether it should be H or V. If exactly one node inside a zone is selected, it will add a Ghost Hint. Useful for setting a shortcut in System Prefs.
* **Add TTF Autohint Control Instructions for Current Glyph / (翻譯名稱)：** Adds a touch line for a given up/down amount to the Control Instructions of the current instance. *需要 香草JS*
* **BlueFuzzer / (翻譯名稱)：** Extends all alignment zones by the specified value. Similar to what the blueFuzz value used to do, hence the name. *需要 香草JS*
* **Keep Only First Master Hints / (翻譯名稱)：** In selected glyphs, deletes all hints in all layers except for whatever is ordered as first master. Respects Bracket Layers. E.g., if your first master is 'Regular', then the script will delete hints in 'Bold', 'Bold [120]', but keep them in 'Regular' and 'Regular [100]'.
* **New Tab with Glyphs in Alignment Zones / (翻譯名稱)：** Opens a new tab and lists all glyphs that reach into alignment zones.
* **New Tabs with Glyphs Not Reaching Into Zones / (翻譯名稱)：** Opens a new tab with all glyphs that do NOT reach into any top or bottom alignment zone. Only counts glyphs that contain paths in the current master. Ignores empty glyphs and compounds. *需要 香草JS*
* **New Tab with Layers with TTDeltas / (翻譯名稱)：** Opens a new tab with all layers that have defined TTDeltas.
* **Remove PS Hints / (翻譯名稱)：** Deletes all stem and/or ghost hints throughout the current font, the selected master and/or the selected glyphs. *需要 香草JS*
* **Remove TT Hints / (翻譯名稱)：** Deletes a user-specified set of TT instructions throughout the current font, the selected master and/or the selected glyphs. *需要 香草JS*
* **Remove Zero Deltas in Selected Glyphs / (翻譯名稱)：** Goes through all layers of each selected glyph, and deletes all TT Delta Hints with an offset of zero. Detailed Report in Macro window.
* **Set blueScale / 設定 blueScale：** Sets maximum blueScale value (determining max size for overshoot suppression) possible in Font Info > Font. Outputs other options in Macro window.
* **Set Family Alignment Zones / (翻譯名稱)：** Pick an instance and set its zones as Family Alignment Zones in *Font Info > Font > Custom Parameters.* *需要 香草JS*
* **Set TT Stem Hints to Auto / (翻譯名稱)：** Sets all TT stem hints to ‘auto’ in selected glyphs.
* **Set TT Stem Hints to No Stem / (翻譯名稱)：** Sets all TT stem hints to ‘no stem’ in selected glyphs. In complex paths, it can improve rendering on Windows.
* **Set TTF Autohint Options / (翻譯名稱)：** Set options for existing 'TTF Autohint Options' Custom Parameters. *需要 香草JS*
* **Transfer Hints to First Master / (翻譯名稱)：** Copies PS hints from the current layer to the first master layer, provided the paths are compatible. Reports errors to the Macro window.
* **TT Autoinstruct / (翻譯名稱)：** Automatically add Glyphs TT instructions to the selected glyphs in the selected master. (Should be the first master.) Attention: this is NOT Werner Lemberg's ttfAutohint, but the manual TT hints that the TT Instruction tool (I) would add through the context menu item of the same name. Useful for adding hints in many glyphs at once.

## 圖片（已完成v1）

*主要用於解決處理大量（背景）圖像時可能遇到的頭痛問題。*

* **Add Same Image to Selected Glyphs / 將相同圖片添加到已選擇字符：** 要求您提供圖片，然後將其作為背景圖片插入到目前所有已選擇的字符中。
* **Adjust Image Alpha / 調整圖片透明度：** 以滑桿介面設定所選字符中的圖片透明度。 *需要 香草JS*
* **Delete All Images in Font / 刪除字型中的所有圖片：** 刪除整個字型中所有放置的圖片。

* **Delete Images / 刪除圖片：** 刪除放置在所選字符可見圖層中的所有圖片。
* **Reset Image Transformation / 重置圖片變形：** 將所有圖片變形參數（x/y 平移、縮放和變形）重置為所選字符中可見圖層的預設值。
* **Set New Path for Images / 為圖片設定新路徑：** Resets the path for placed images in selected glyphs. Useful if you have moved your images.重置所選字符中放置圖片的路徑。如果您移動了圖片，這很有用。 *:question:圖片有路徑？*
* **Toggle Image Lock / 切換圖片鎖定：** 以浮動視窗按鈕鎖定或解鎖所有選定字符中的圖片。 *需要 香草JS*
* **Transform Images / 變形圖片：** 用於在已選擇字符的可見圖層中，以浮動視窗界面批次變形圖片（x/y 平移和 x/y 縮放）。 *需要 香草JS*

## 插值

*推薦腳本：「插入實體」（用於確認你的實體及其樣式正確的對應）、「拗折尋找」 和 「尋找變形字符」。作者經常搭配快捷鍵使用「顯示上/下一個實體」這個腳本。*

* **Axis Location Setter / (翻譯名稱)：** Batch-set axis locations for all instances with a certain name particle. E.g., set an axis location for all Condensed instances. *需要 香草JS*
* **Axis Mapper / (翻譯名稱)：** Extracts, resets and inserts an ‘avar’ axis mapping for the Axis Mappings parameter. *需要 香草JS*
* **Brace and Bracket Manager / (翻譯名稱)：** Find and replace brace or bracket layer coordinates in Glyphs 3 and later. *需要 香草JS*
* **Composite Variabler / (翻譯名稱)：** Reduplicates Brace and Bracket layers of components in the compounds in which they are used. Makes bracket layers work in composites. *需要 香草JS*
* **Copy Layer to Layer / (翻譯名稱)：** Copies paths (and optionally, also components, anchors and metrics) from one Master to another. *需要 香草JS*
* **Dekink Masters / (翻譯名稱)：** Dekinks your smooth point triplets in all compatible layers (useful if they are not horizontal or vertical). Select a point in one or more smooth point triplets, and run this script to move the corresponding nodes in all other masters to the same relative position. Thus you achieve the same point ratio in all masters and avoid interpolation kinks, when the angle of the triplet changes. There is a [video describing it.](http://tinyurl.com/dekink-py) The triplet problem is [described in this tutorial](http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible).
* **Fill up Empty Masters / 填滿空白主板：** Copies paths from one Master to another. But only if target master is empty.複製一個主板的路徑到另一個，當目標主板為空白時。 *需要 香草JS*
* **Find and Replace in Layer Names / 尋找和取代圖層名稱：** Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. *需要 香草JS*
* **Find Shapeshifting Glyphs / 尋找變形字符：** Finds glyphs that change the number of paths while interpolating. Opens a new tab and reports to Macro window. *需要 香草JS*
* **Insert Brace Layers for Component Rotation / (翻譯名稱)：** Inserts a number of Brace Layers with continuously scaled and rotated components. Useful for OTVar interpolations with rotating elements. *需要 香草JS*
* **Insert Brace Layers for Movement along Background Path / (翻譯名稱)：** Inserts a number of Brace Layers with copies of the first layer, shifted according to the first path in the background. Useful for OTVar interpolations with moving elements.
* **Insert Instances / 插入實體：** GUI for calculating and inserting weight instances. It is described in this tutorial: https://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances *需要 香草JS*
* **Insert Layers / 插入圖層：** Batch-insert brace or bracket layers in selected glyphs. *需要 香草JS*
* **Instance Cooker / (翻譯名稱)：** Insert many instances at once with a recipe. *需要 香草JS*
* **Kink Finder / 拗折尋找：** Finds kinks in outlines or the interpolation space, reports them in the Macro window and opens a new tab with affected glyphs. Kinks are described in this tutorial: https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible *需要 香草JS*
* **New Tab with Dangerous Glyphs for Interpolation / (翻譯名稱)：** Opens a tab with all glyphs in the font that contain at least two compatible elements. I.e., glyphs where an element (a path or a component) could interpolate with the wrong element, like the equals sign. For a detailed description, see section *Be suspicious* in this tutorial: <http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible>.
* **New Tab with Special Layers / (翻譯名稱)：** Quickly adds a new edit tab with all glyphs containing brace and bracket layers.
* **New Tab with Uneven Handle Distributions / (翻譯名稱)：** Finds glyphs where handle distributions change too much (e.g., from balanced to harmonised). *需要 香草JS*
* **OTVar Player / (翻譯名稱)：** Animates the current glyph with a loop along the weight axis. *需要 香草JS*
* **Remove All Non-Master Layers / (翻譯名稱)：** Deletes all layers which are neither master layers, nor brace layers, nor bracket layers. Useful for getting rid of backup layers.
* **Report Instance Interpolations / (翻譯名稱)：** Outputs master coefficients for each instance in Macro Window. Tells you which masters are involved in interpolating a specific instance, and to which extent.
* **Reset Axis Mappings / (翻譯名稱)：** Inserts (or resets) a default Axis Mappings parameter for all style values currently present in the font. Ignores style values outside the designspace bounds defined by the masters.
* **Set Weight Axis Locations in Instances / (翻譯名稱)：** Will set weight axis location parameters for all instances, and sync them with their respective usWeightClass. Will set the width axis coordinates to the spec defaults for usWidthClass, if they have not been set yet. Otherwise will keep them as is.
* **Short Segment Finder / (翻譯名稱)：** Goes through all interpolations and finds segments shorter than a user-specified threshold length. *需要 香草JS*
* **Travel Tracker / (翻譯名稱)：** Finds interpolations in which points travel more than they should, i.e., can find wrongly hooked-up asterisks and slashes. The results are incomplete, and usually have many false positives, but it sometimes finds cases that the Shapeshifter script misses. *需要 香草JS*
* **Variation Interpolator / (翻譯名稱)：** Creates a user-defined number of glyph variations with a user-defined suffix, containing interpolations between the layers and their respective backgrounds. Overwrites glyphs with same name. Similar to Pablo Impallari’s SimplePolator. Useful for e.g. length variants of Devanagari Matra, see José Nicolás Silva Schwarzenberg’s sample video: <https://www.youtube.com/watch?v=QDbaUlHifBc>. *需要 香草JS*
* * **Other > Lines by Master / (翻譯名稱)：** Reduplicates your edit text across masters, will add one line per master in Edit view. Careful, ignores everything after the first newline. Intended for adding a keyboard in System Preferences.
* * **Other > New Tab with Masters of Selected Glyphs / (翻譯名稱)：** Opens a new Edit tab containing all masters of selected glyphs.
* * **Other > Show Masters of Next/Previous Glyph / (翻譯名稱)：** Allows you to step through one glyph after another, but with all masters. Combines the show next/previous glyph function (fn+left/right) with the *Edit > Show All Masters* function. Handy for attaching a keyboard shortcut in System Preferences.
* * **Other > Show Next/Previous Instance / 其他 > 顯示上/下一個實體：** Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut in System Preferences.

## Kerning 調距

*推薦腳本：「自動緩衝器」、「KernCrasher」、「GapFinder」、「示例字符串製造器」。如果你有太多的 kerning，請考慮使用「異常清除器」。*

* **Adjust Kerning in Master / (翻譯名稱)：** GUI to add a value to all kerning pairs, multiply them by a value, round them by a value, or limit them to a value. *需要 香草JS*
* **Auto Bumper / 自動緩衝器：** Specify a minimum distance, left and right glyphs, and Auto Bumper will add the minimum necessary kerning for the current master. *需要 香草JS*
* **BBox Bumper / 邊界框緩衝器：** Like Auto Bumper, but with the bounding box of a group of glyphs, and the kerning inserted as GPOS feature code in Font Info > Features > kern. Useful if you want to do group kerning with classes that are different from the kerning groups. 需要 香草JS
* **Convert RTL Kerning from Glyphs 2 to 3 / (翻譯名稱)：** Convert RTL kerning from Glyphs 2 to Glyphs 3 format and switches the kerning classes. (Hold down OPTION and SHIFT to convert from Glyphs 3 back to Glyphs 2.) Detailed report in Macro Window.
* **Copy Kerning Exceptions to Double Accents / (翻譯名稱)：** Copies Kerning exceptions with abreve, `acircumflex`, `ecircumflex`, `ocircumflex`, `udieresis` into Vietnamese and Pinyin double accents.
* **Exception Cleaner / (翻譯名稱)：** Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception. *需要 香草JS*
* **Find and Replace in Kerning Groups / (翻譯名稱)：** GUI for searching and replacing text in the L and R Kerning Groups, e.g. replace 'O' by 'O.alt'. Leave the search field blank for appending. *需要 香草JS*
* **GapFinder / (翻譯名稱)：** Opens a new tab with kerning combos that have large gaps in the current fontmaster. *需要 香草JS*
* **Import Kerning from .fea File / (翻譯名稱)：** Choose an .fea file containing a kern feature in AFDKO code, and this script will attempt to import the kerning values into the frontmost font master (see *Window > Kerning*).
* **KernCrash Current Glyph / (翻譯名稱)：** Opens a new tab containing kerning combos with the current glyph that collide in the current fontmaster.
* **KernCrasher / (翻譯名稱)：** Opens a new tab with Kerning Combos that crash in the current fontmaster. *需要 香草JS*
* **Kern Flattener / (翻譯名稱)：** Duplicates your font, flattens kerning to glyph-to-glyph kerning only, deletes all group kerning and keeps only relevant pairs (it has a built-in list), adds a *Export kern Table* parameter (and some other parameters) to each instance. Warning: do this only for making your kerning compatible with outdated and broken software like PowerPoint. No guarantee it works, though.
* **Kern String Mixer / (翻譯名稱)：** Intersect two sets of glyphs (tokens are possible) with each other in order to get all possible glyph combinations. *需要 香草JS*
* **New Tab with All Group Members / (翻譯名稱)：** Select two glyphs, e.g. ‘Ta’, run the script, and it will open a new tab with all combinations of the right kerning group of T with the left kerning group of a.
* **New Tab with Glyphs of Same Kerning Groups / (翻譯名稱)：** Opens a new tab containing all members of the left and right kerning groups of the current glyph.
* **New Tab with Kerning Missing in Masters / (翻譯名稱)：** Opens New Tabs for each master showing kerning missing in this master but present in other masters.
* **New Tab with Large Kerning Pairs / (翻譯名稱)：** Lists all positive and negative kerning pairs beyond a given threshold. *需要 香草JS*
* **New Tab with Overkerned Pairs / (翻譯名稱)：** Asks a threshold percentage, and opens a new tab with all negative kern pairs going beyond the width threshold. Example: With a threshold of 40%, and a comma with width 160, the script will report any negative kern pair with comma larger than 64 (=40% of 160). Assume that r-comma is kerned -60, and P-comma is kerned -70. In this case, it would report the latter, but not the former. *需要 香草JS*
* **New Tab with Right Groups / (翻譯名稱)：** Creates a new tab with one glyph of each right group. Useful for checking the consistency of right kerning groups.
* **New Tab with all Selected Glyph Combinations / (翻譯名稱)：** Takes your selected glyphs and opens a new tab with all possible combinations of the letters. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Uneven Symmetric Kernings / (翻譯名稱)：** Finds kern pairs for symmetric letters like ATA AVA TOT WIW etc. and sees if AT is the same as TA, etc.
* **New Tabs with Punctuation Kern Strings / (翻譯名稱)：** Outputs several tabs with kern strings with punctuation.
* **Remove all Kerning Exceptions / (翻譯名稱)：** Removes all kerning for the current master, except for group-to-group kerning. Be careful.
* **Remove Kerning Between Categories / (翻譯名稱)：** Removes kerning between glyphs, categories, subcategories, scripts. *Requires Vanilla.*
* **Remove Kerning Pairs for Selected Glyphs / (翻譯名稱)：** Deletes all kerning pairs with the selected glyphs, for the current master only.
* **Remove Orphaned Group Kerning / (翻譯名稱)：** Deletes all group kernings referring to groups that are not in the font.
* **Remove Small Kerning Pairs / (翻譯名稱)：** Removes all kerning pairs in the current font master with a value smaller than specified, or a value equal to zero. Be careful. *需要 香草JS*
* **Report Kerning Mistakes / (翻譯名稱)：** Tries to find unnecessary kernings and groupings. Reports in Macro window, for reviewing.
* **Sample String Maker / 示例字符串製造器：** Creates kern strings for user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored. *需要 香草JS*
* **Set Kerning Groups / (翻譯名稱)：** Sets left and right kerning groups for all selected glyphs. In the case of compounds, will use the groups of the base components, otherwise makes an informed guess based on a built-in dictionary.
* **Steal Kerning from InDesign / (翻譯名稱)：** Steals the kerning from text set in InDesign. Useful for extracting InDesign’s [Optical Kerning](https://web.archive.org/web/20160414170915/http://blog.extensis.com/adobe/about-adobe’s-optical-kerning.php) values.
* **Steal Kerning Groups from Font / (翻譯名稱)：** Steals left/right kerning groups for all selected glyphs from a 2nd font. *需要 香草JS*
* **Zero Kerner / (翻譯名稱)：** Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports. *需要 香草JS*

## 路徑（已完成v2）

*我使用「以錨點為中心旋轉」功能來處理星號符號。在輪廓檢查中非常重要：「路徑問題查找器」、「尋找近垂直缺失」和「節點綠藍管理器」。在 OTVar 製作中，「Rewire Fire」 變得越來越重要，因為它有助於減少形狀邊緣重疊輪廓線段（這會在反鋸齒中造成暗斑）。*

* **Align Selected Nodes with Background / 對齊選取節點與背景：** 將選取的節點與最近的背景節點對齊，除非它已經被先前移動的節點佔用。類似於使用 Cmd-Shift-A 將單個節點與背景對齊，但可針對多個節點。
* **Batch-Set Path Attributes / 批次設置路徑屬性：** 設定所選字符、主板、字型等中所有路徑的路徑屬性。 *需要 香草JS*
* **Copy Glyphs from Other Font into Backup Layers / 從其他字型複製字符到備份圖層：** 在目標字型中為所選字符創建備份圖層，並使用來源字型中相應的字符填充它們。如果您想要將一個字型的字符作為括號層添加到另一個字型中，這非常有用。 *需要 香草JS* -執行有問題？
* **Distribute Nodes / 均分節點：** 水平或垂直均分節點（取決於所選範圍的寬高比）。
* **Enlarge Short Segments / 放大單位線段：** 將線段長度小於一個單位的線段加倍。 -小於一單位？
* **Fill Up with Rectangles / 填滿矩形：** 遍歷所選字符，如果發現空白字符，則插入一個佔位符矩形。對於快速構建用於測試的虛擬字型非常有用。
* **Find Close Encounters of Orthogonal Line Segments / 找出靠近但未完全對齊的直角線段交會點：** 遍歷所有垂直和水平線段，並找到接近但未完全對齊的線段對。 *需要 香草JS*
* **Find Near Vertical Misses / 尋找近垂直缺失：** 找到靠近但不完全在垂直度量上的節點。 *需要 香草JS*
* **Green Blue Manager / 節點綠藍管理器：** 定義一個角度，節點在該角度之上被設置為藍色，在該角度之下被設置為綠色。 *需要 香草JS*
* **Grid Switcher / 格線單位切換器：** 通過點擊浮動按鈕在兩個用戶定義的格線單位之間切換。 *需要 香草JS*
* **Harmonise Curve to Line / 協調曲線與直線：** 將（選定的）曲線線段上的控制手柄重新排列，以便與後面的直線段之間的過渡是平滑的（匹配）。 -功能原理不明？
* **Interpolate two paths / 插值兩條路徑：** 選擇兩個路徑並運行此腳本，它將以50％的插值替換它們。（節點數量需一致）
* **New Tab with Small Paths / 開新分頁-小路徑：** 打開一個包含小於用戶定義閾值大小（平方單位）的路徑的新標籤頁。-小於用戶定義單位？
* **Path Problem Finder / 路徑問題查找器：** 在輪廓中查找各種潛在問題，並打開一個包含受影響圖層的新分頁。 *需要 香草JS*
* **Position Clicker / 位置點擊器：** Finds all combinations of positional shapes that do not click well. ‘Clicking’ means sharing two point coordinates when overlapping.查找那些在重疊時兩個形狀不能良好對齊的位置，並列出它們的組合。重疊的兩個形狀在同一個位置有共同的點坐標。-功能待測試 *需要 香草JS*
* **Realign BCPs / 重新對齊貝茲曲線控制點：** Realigns all BCPs in all selected glyphs. Useful if handles got out of sync, e.g. after nudging or some other transformation, or after interpolation. Hold down Option to apply to all layers of the selected glyph(s).重新對齊所選字符中的所有貝茲曲線控制點。 如果控制柄失去同步，例如在微調或其他轉換之後或在插值之後，此腳本非常有用。按住Option鍵以將其應用於所選字形的所有圖層。-功能待測試
* **Remove all Open Paths / 刪除所有開放路徑：** 刪除所有所選字符的可見圖層中的 開放 路徑。
* **Remove Nodes and Try to Keep Shape / 刪除節點並儘可能保持形狀：** 刪除所選擇的節點，並儘可能保持形狀。類似於刪除單個節點時發生的情況，但針對多個節點的選擇。專業提示：在運行腳本時按住Shift鍵，它也會盡可能平衡剩餘的控制柄，這正是刪除單個節點時發生的情況。
* **Remove Short Segments / 刪除短線段：** 刪除線段長度小於一個單位的線段。-功能待測試
* **Remove Stray Points / 移除零散的點：** 在所選字形中刪除零散的點（僅有一個節點的路徑）。注意：零散的點可以被用來快速禁用自動對齊。腳本將在巨集面板詳細報告。
* **Rewire Fire / 重整連線：** 尋找、選取並標記重複的座標。通常兩個在相同位置的節點可以使用重新連接節點功能進行重整。 *需要 香草JS*
* **Rotate Around Anchor / 環繞錨點旋轉：** 圖形使用者介面，用於繞「rotate」錨點旋轉選擇的字符或節點、組件。可以進行角度、方向和重複次數的設定。 *需要 香草JS*
* **Set Transform Origin / 設定變形原點：** 一個簡單的GUI，用於以數值方式設定旋轉工具的變形原點。也應該對縮放工具有影響。 *需要 香草JS*
* **Straight Stem Cruncher / 字幹壓縮器：** Finds distances between points in all layers, and compares them (with a tolerance) to specified stem widths. Lists glyphs that have deviating stems in their drawings. 可以檢查字型中是否有部分字符的字幹（如直的線條）偏離了指定的標準大小。它會列出這些有問題的字符，方便使用者進一步修正。 *需要 香草JS* -功能待測試
* **Tunnify：** 尋找至少有一個控制桿被選中的所有路徑段。接著，平均調整這些路徑段的控制桿，即兩個控制桿的擬合曲線百分比將相同。可以修復Adobe Illustrator的零控制桿問題（即將一個控制桿縮回到最近的節點中）。這個腳本的靈感來自Eduardo Tunni（由Pablo Impallari傳達），因此得名。但是我沒有看過Eduardo的算法，因此我的實現可能與他的有些不同，尤其是對於零控制桿的處理。

## 像素字型（已完成v1）

*這些腳本在像素字型的工作流程中都很有用，它們能幫助你在較粗的網格中放置像素組件。如果你正在進行像素設計，請看看 窗口 > 外掛程式管理員 中可用的像素相關外掛。*

* **Align Anchors to Grid / 對齊錨點與網格：** 將變音符號錨點對齊到字型網格上。
* **Delete Components out of Bounds / 刪除邊界外的組件：** 如果組件放置在遠離平常坐標的地方（通常發生在當您使用 cmd 加方向鍵在低網格密度中移動組件時），此腳本將刪除它們。
* **Delete Duplicate Components / 刪除重複組件：** 尋找重複的組件（相同名稱和位置）並只保留一個。這個情況經常在創建像素字型時發生。
* **Flashify Pixels / Flash化像素：** 創造小接口以避免路徑交錯產生的白色區域，這對於 Flash 字體渲染器來說尤其是一個問題，這也是此腳本名稱的由來。
* **Reset Rotated and Mirrored Components / 重置被旋轉和鏡像的組件：** 尋找被縮放、鏡像和旋轉的組件並將它們恢復為預設的比例和方向，但不更動其位置。用於修復被鏡像的像素。

## 小體大寫字母（已完成v1）

*當製作中的字體包含小體大寫字母時，可以執行「檢查小體大寫字母一致性」。不過請對它的報告持保留態度：它列出了許多誤報，而且也不是每個警告都這麼重要。*

* **Check Smallcap Consistency / 檢查小體大寫字母一致性：** 對您的小體大寫字母集執行一些測試並在巨集視窗列出報告，尤其是調距群組和字符集。
* **Copy Kerning from Caps to Smallcaps / 將大寫字母的調距數值複製到小體大寫字母：** 將大寫字母的調距字偶複製到相應的小體大寫字母，如果它們包含在字型中。請注意：將覆蓋現有的小體大寫字母的調距字偶。

## 間距

*推薦腳本：「修復數學運算符間距」、「括號度量管理器」，如果你的字型中有箭頭可以試試「修復箭頭定位」。「新增分頁」腳本在創建數字時也很好用。*

* **Add Metrics Keys for Symmetric Glyphs / (翻譯名稱)：** Will add RSB =| if the RSB is the same as the LSB in all masters. *需要 香草JS*
* **Bracket Metrics Manager / 括號度量管理器：** Manage the sidebearings and widths of bracket layers, e.g., dollar and cent. *需要 香草JS*
* **Center Glyphs / (翻譯名稱)：** Centers all selected glyphs inside their width, so that LSB=RSB.
* **Change Metrics by Percentage / (翻譯名稱)：** Change LSB/RSB of selected glyphs by a percentage value. Undo with the Revert button. *需要 香草JS*
* **Find and Replace in Metrics Keys / (翻譯名稱)：** GUI for searching and replacing text in the L and R metrics keys, e.g. replace '=X+15' by '=X'. Leave the search field blank for appending.
* **Fix Arrow Positioning / 修復箭頭定位：** Fixes the placement and metrics keys of arrows, dependent on a specified default arrow. Adds metric keys and moves arrows vertically. Does not create new glyphs, only works on existing ones. *需要 香草JS*
* **Fix Math Operator Spacing / 修復數學運算符間距：** Syncs widths and centers glyphs for +−×÷=≠±≈¬, optionally also lesser/greater symbols and asciicircum/asciitilde. *需要 香草JS*
* **Freeze Placeholders / (翻譯名稱)：** In the current Edit tab, will change all inserted placeholders for the current glyph, thus 'freeze' the placeholders.
* **Metrics Key Manager / (翻譯名稱)：** Batch apply metrics keys to the current font. *需要 香草JS*
* **Monospace Checker / (翻譯名稱)：** Checks if all glyph widths in the frontmost font are actually monospaced. Reports in Macro Window and opens a tab with affected layers. *需要 香草JS*
* **New Tab with all Figure Combinations / (翻譯名稱)：** Opens a new tab with all possible figure combos. Also outputs a string for copying into the Macro window, in case the opening of the tab fails.
* **New Tab with Fraction Figure Combinations / (翻譯名稱)：** Opens an Edit tab with fraction figure combos for spacing and kerning.
* **Remove Layer-Specific Metrics Keys / (翻譯名稱)：** Deletes left and right metrics keys specific to layers (==), in all layers of all selected glyphs. Also simplifies glyph metrics keys (i.e., turns "=H" into "H").
* **Remove Metrics Keys / (翻譯名稱)：** Deletes both left and right metrics keys in all selected glyphs. Affects all masters and all layers.
* **Reset Alternate Glyph Widths / (翻譯名稱)：** Resets the width of suffixed glyphs to the width of their unsuffixed counterparts. E.g., `Adieresis.ss01` will be reset to the width of `Adieresis`.
* **Spacing Checker / (翻譯名稱)：** Look for glyphs with unusual spacings and open them in a new tab. *需要 香草JS*
* **Steal Metrics / (翻譯名稱)：** Steals the sidebearing or width values for all selected glyphs from a 2nd font. Optionally also transfers metrics keys like '=x+20'. *需要 香草JS*
* **Tabular Checker / (翻譯名稱)：** Goes through tabular glyphs and checks if they are monospaced. Reports exceptions. *需要 香草JS*

## 測試（已完成v1）

*推薦「測試用 HTML 腳本」。如果你在 Adobe 或 Apple 應用程式中發現選取框異常的高或低，可以執行「最高和最低點字符報告」查詢找出導致狀況發生的字符。「拉丁字母支援語言報告」提供的資訊是參考性的建議，不是絕對要遵守的規範。*

* **Copy InDesign Test Text / 複製 InDesign 測試文字：** 將 InDesign 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Copy Word Test Text / 複製 Word 測試文字：** 將 Word 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Language Report / 拉丁字母支援語言報告：** 在巨集視窗輸出讓你初步了解你的拉丁字符支持多少種語言以及哪些語言的資訊。基於 Underware's Latin-Plus 列表，並進行了修改。
* **Pangram Helper / 全字母句小幫手：** 幫助你編寫歐文的全字母句，你可以將其複製到剪貼簿或放入新分頁中。 *需要 香草JS* *:question:成果 其他字母句要自己添加？*
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
