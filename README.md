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

## 錨點（已完成v2）

*「錨點移動器」用於批次處理錨點位置，在調整 x 高度之後會很有用。 輕而易舉：在組合標記上使用「重新定位」腳本，能讓你在斜體角度時也能維持一致。*

* **Anchor Mover / 錨點移動器：** 在一個操作視窗中批次移動多個字符中的錨點位置。 *需要 香草JS*
* **Batch Insert Anchors / 批次插入錨點：** 在一個操作視窗中批次在多個字符的相近位置批次插入錨點。 *需要 香草JS*
* **Find and Replace in Anchor Names / 尋找與取代錨點名稱：** 在一個操作視窗中搜尋並取代特定的錨點名稱（尋找範圍為選定字符的所有圖層）。 *需要 香草JS*
* **Fix Arabic Anchor Order in Ligatures / 修復連字中的阿拉伯文錨點順序：** 此腳本可以修正 *top_X* 和 *bottom_X* 錨點的順序，讓它們符合右至左書寫的排列方式。有些從其他格式轉換而來的檔案，可能會發生 *top_1* 在左邊，而 *top_2* 在右邊的情況，但實際上順序應該相反，否則會影響到後續的 mark2liga 步驟。這個腳本會針對所選擇的阿拉伯文連字進行處理，將所有錨點按照右至左的順序重新排列，同時不影響它們的座標位置。
* **Insert All Anchors in All Layers / 在所有圖層插入錨點：** 為該字符的所有圖層加入遺失的錨點（如果該錨點沒有出現在所有圖層中的話）。
* **Insert exit and entry Anchors to Selected Positional Glyphs / 在選定的位置字符上插入 exit/entry 錨點：** 此腳本會在所選擇的字符中添加連筆連接所需的入口和出口錨點。預設情況下，它會在座標點 (0, 0) 添加出口錨點，而入口錨點則會放置在 RSB (右側基線) 的節點上（如果有的話）。請根據自己的需求進行調整。
* **Mark Mover / 標號移動器：** 將結合用標號移到相對應的高度。例如大寫上標符號移到大寫高度，小寫上標符號移到 x 高度...等。你也可以另外設定左右間距的數值。 *需要 香草JS*
* **Move ogonek Anchors to Baseline Intersection / 將反尾形符錨點移動到基線交界處：** 將所有反尾形符錨點和結合用錨點移動到字符線框最右側和基線的交界處。
* **Move topright Anchors for Vertical Carons / 移動垂直抑揚符的右上角錨點：** 此腳本可以將所有的 topright 和 _topright 錨點移動到字型輪廓與 x-height 的最右交匯點。這對於建立帶有垂直抑揚符的捷克文/斯洛伐克文字母非常有用。
* **Move Vietnamese Marks to top_viet Anchor in Circumflex / 移動越南語標號到揚抑符中的 top_viet 錨點上：** 此腳本可以將所選擇的字符中每一層的 *acute*、*grave* 和 *hookabovecomb* 錨點移動到 *top_viet* 錨點上。這對於製作越南文雙重音符號非常有用。前提是在所有 *circumflexcomb* 的層中都有 *top_viet* 錨點。
* **New Tab with Glyphs Containing Anchor / 新分頁－所有包含錨點的字符：** 打開一個新分頁，該分頁包含所有已製作錨點的字符。
* **New Tab with top and bottom Anchors Not on Metric Lines / 新分頁－所有位在度量線上的頂部和底部錨點：** 將所有 *top* 和 *bottom* 錨點的垂直高度資訊顯示在巨集面板上，並且開啟一個新分頁，列出所有主板或支撐層中錨點位置不在度量線位置上的字符。
* **Prefix all exit/entry anchors with a hashtag / 在所有 exit/entry 錨點前加上井字號：** 此腳本會搜尋字型中所有的 exit/entry 錨點，並在它們的錨點名稱前加上 `#`，以停用 `curs` 特性的生成。
* **Realign Stacking Anchors / 重新對齊堆疊錨點：** 此腳本可以在堆疊結合重音符號中，將頂部和底部錨點準確地移動到相應的 _top 和 _bottom 錨點正上方或正下方，同時考慮斜體角度。這樣，堆疊多個非間隔重音符號時，它們將始終保持在一條線上。 *需要 香草JS*
* **Remove Anchors in Suffixed Glyphs / 刪除後綴字符中的錨點：** 此腳本可以從字符中移除所有包含使用者指定後綴的錨點。這對於在複製、縮放和編輯後的上標、下標、下方變體或序數變體中，清除剩餘的錨點非常有用。 *需要 香草JS*
* **Remove Anchors / 移除錨點：** 刪除選定字符（或整個字型）中具有指定名稱的錨點。 *需要 香草JS*
* **Remove Non-Standard Anchors from Selected Glyphs / 移除選定字符的異常錨點：** 此腳本可以從字符中移除所有不應存在的預設錨點，例如在 `J` 字母中的 `ogonek`。這可能存在潛在風險，因為它可能會刪除錯誤的錨點。因此，在使用此移除腳本之前，請先使用下面的報告腳本，以避免意外刪除錯誤的錨點。
* **Replicate Anchors / 複製錨點：** 在操作視窗中選擇一個來源字符，並在目前的字符上批次加入錨點。 *需要 香草JS*
* **Replicate Anchors in Suffixed Glyphs / 複製錨點到後綴字符：** 掃描選取的後綴字符，從它們的基本字符複製錨點過來。 例如將 *X* 的錨點貼到 *X.ss01*、*X.swsh* 和 *X.alt* 上。
* **Report Non-Standard Anchors to Macro window / 在巨集面板報告異常錨點資訊：** 掃描字型中的所有字符，將偵測到的異常錨點顯示在巨集面板中，命令行內容可被複製貼上到編輯畫面中。
* **Shine Through Anchors / 穿透錨點：** 此腳本可以在所選字符的所有圖層中，從組件中插入 ‘traversing’ 錨點。

## 應用程式（已完成v1）

*如果你正在寫程式，請為「方法報告器」添加快捷鍵，你將非常需要它。如果你想要一個與解析度無關的視窗內容的PDF螢幕截圖讓你可以在向量插圖應用程式中進行後製，「列印視窗」可以派上用場。*

* **Close All Tabs of All Open Fonts / 關閉所有字型檔的編輯分頁：** 關閉目前在應用程式中開啟字型檔的所有編輯分頁。
* **Copy Download URL for Current App Version / 複製目前應用程式版本的下載連結：** 將目前 Glyphs 應用程式版本的下載連結放入剪貼簿以便於貼上。
* **Decrease and Increase Line Height / 減少和增加行高：** 將「編輯畫面」的行高增加四分之一或減少五分之一。如果你需要在行高之間頻繁切換，推薦將它們設定到快捷鍵。
* **Method Reporter / 方法報告器：** 圖形使用者介面用於過濾 Glyphs 中可用的 Python 和 PyObjC 類的方法名稱。你可以使用多個空格分隔檢索詞（用於 AND 串接）和星號作為未知字元（可放在開頭、中間和結尾）。按兩下可將方法名稱放入剪貼簿，然後在巨集面板中打開説明。對寫程式的人很有用。 *需要 香草JS*
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

## 建構字符（已完成v2）

*推薦腳本：「引號管理器」，以及用於小型大寫數字、符號和 ​​Ldot 的「構建腳本」。其他腳本主要是為了讓你快速開始覆蓋某些 Unicode 範圍如果客戶有需求。*

* **Build APL Greek / 建立 APL 希臘字母：** 此腳本可以建立算式用的希臘字母。
* **Build careof and cadauna / 建立 careof 和 cadauna 符號：** B此腳本可以從你的 `c`、`o`、`u` 和 `fraction` 字母建立 `cadauna` 和 `careof` 字符。
* **Build Circled Glyphs / 建立圓圈符號：** 此腳本可以從 `_part.circle` 和您的字母和數字，建立圓圈數字和字母（U+24B6...24EA 和 U+2460...2473）。 *需要 香草JS*
* **Build Dotted Numbers / 建立帶點數字：** 此腳本可以從你的標準數字和句號建立帶有點的數字。
* **Build ellipsis from period components / 從句點組件建立刪節號：** 此腳本在句號字形中插入 exit 和 entry 錨點，並使用句號字形的自動對齊組件重新建構省略號。注意：此腳本會解構在其他字形中使用的句號組件（例如冒號）。
* **Build Extra Math Symbols / 建立額外的數學符號：** 此腳本可以建立 `lessoverequal`, `greateroverequal`, `bulletoperator`, `rightanglearc`, `righttriangle`, `sphericalangle`, `measuredangle`, `sunWithRays`, `positionIndicator`, `diameterSign`, `viewdataSquare`, `control` 等額外的數學符號。
* **Build Ldot and ldot / 建立 Ldot 和 ldot 字符：** 此腳本可以從現有的 `L` 和 `periodcentered.loclCAT`（`.case`/`.sc`）建立 `Ldot`、`ldot` 和 `ldot.sc`。假設你已經建立並正確設定好間距 `L`-`periodcentered.loclCAT`-`L` 等等。
* **Build Parenthesized Glyphs / 建立帶括號的字母和數字：** 建立帶括號的字母和數字： `one.paren`, `two.paren`, `three.paren`, `four.paren`, `five.paren`, `six.paren`, `seven.paren`, `eight.paren`, `nine.paren`, `one_zero.paren`, `one_one.paren`, `one_two.paren`, `one_three.paren`, `one_four.paren`, `one_five.paren`, `one_six.paren`, `one_seven.paren`, `one_eight.paren`, `one_nine.paren`, `two_zero.paren`, `a.paren`, `b.paren`, `c.paren`, `d.paren`, `e.paren`, `f.paren`, `g.paren`, `h.paren`, `i.paren`, `j.paren`, `k.paren`, `l.paren`, `m.paren`, `n.paren`, `o.paren`, `p.paren`, `q.paren`, `r.paren`, `s.paren`, `t.paren`, `u.paren`, `v.paren`, `w.paren`, `x.paren`, `y.paren`, `z.paren`。
* **Build Q from O and _tail.Q / 將 _tail.Q 和現有的 O 元件組合成 Q：** 請在將 Q 的尾巴轉換為組件（使用 將選取的路徑轉為組件 功能）並命名為 `_tail.Q` 後執行此腳本。
* **Build Rare Symbols / 建立罕見符號：** 建立白色和黑色的小型和大型圓形、三角形和正方形。 *需要 香草JS*
* **Build rtlm Alternates / 建立 rtlm 替代字符：** 為選定的字符建立水平鏡像組合，並更新 rtlm OpenType 功能。自動對齊組件，但也添加度量鍵，以防您進行拆解。
* **Build Small Figures / 建立小型數字：** 這個腳本會以一組預設的小型數字 (例如`.dnom`) 為基礎，並以組件複製的方式產生其他數字（例如`.numr`、`superior`/`.sups`、`inferior`/`.sinf`、`.subs`等等），同時也會考慮斜體角度。 *需要 香草JS*
* **Build small letter SM, TEL / 建立小寫字母SM和TEL：** 建立字符：`servicemark`（服務商標）和 `telephone`（電話符號）。
* **Build space glyphs / 建立空格字符：** 建立 `mediumspace-math`, `emquad`, `emspace`, `enquad`, `enspace`, `figurespace`, `fourperemspace`, `hairspace`, `narrownbspace`, `punctuationspace`, `sixperemspace`, `nbspace`, `thinspace`, `threeperemspace`, `zerowidthspace`等不同寬度的空格字符。
* **Build Symbols / 建立符號：** 這個腳本會幫你建立一些符號字符，例如沒有定義的符號字符 `.notdef`，它會以最粗的問號作為參考，還有一個代表估算值的字符 `estimated`。此外，還會建立 `bar` 和 `brokenbar` 字符，並且會遵循標準的垂線和斜體角度。 *需要 香草JS*
* **Fix Punctuation Dots and Heights / 修復標點符號和高度：** 此腳本會同步 ¡!¿? 的標點符號點位置（包括它們的小型大寫、一般大寫版本），並且在變體中移動 ¡¿ 的位置。假設 ¡¿ 是 !? 的組件。詳細報告會顯示在巨集面板中。
* **Quote Manager / 引號管理器：** 從單引號建立雙引號，並在單引號中插入 `#exit` 和 `#entry` 錨點以進行自動對齊。你需要已經有單引號。 *需要 香草JS*

## 彩色字型（已完成v1）

*這些腳本能幫助你在製作彩色字體的工作流程中解決遇到的問題。「合併腳本」主要用於為 CPAL/COLR 字型建立後備字符。這個方式產生的後備字符將會填滿編輯框，且不會在 Chrome 瀏覽器中發生裁切。*

* **Add All Missing Color Layers to Selected Glyphs / 加入所有遺失的顏色圖層到選定字符中：** 為所選字符在色盤參數定義的每個 (CPAL/COLR) 顏色添加圖層，該圖層從備用層複製並轉換為色盤圖層。該腳本只添加字符中仍然缺少的顏色。
* **Add sbix Images to Font / 加入sbix圖片到字型中：** 將獲取文件夾中的所有 PNG、GIF、JPG 文件，並在當前字型和主板中使用它們建立 iColor 圖層。文件名格式： `字符名稱 像素尺寸.副檔名` ，例： `Adieresis 128.png` 。
* **Convert Layerfont to CPAL+COLR Font / 將圖層字型轉換為CPAL+COLR字型：** 將圖層彩色字型轉換為在每個字符中具有 CPAL 和 COLR 層的單一主板字型。它將以第一個主板作為備用字體層。
* **Delete Non-Color Layers in Selected Glyphs / 刪除選定字符的非顏色圖層：** 刪除所有字符中不是 `色盤` 類型的所有子圖層（CPAL/COLR 層）。
* **Merge All Other Masters in Current Master / 將所有其他主板合併到當前主板：** 在所選字符中，將所有路徑從其他主板複製到目前主板層。
* **Merge Suffixed Glyphs into Color Layers / 合併關聯字符到顏色層中：** 將 `x.shadow` 、 `x.body` 和 `x.front` 合併到 `x` 的單獨 CPAL 顏色圖層中。 *需要 香草JS*
* **sbix Spacer / sbix字型空間調整器：** 大量設定 sbix 位置和字符寬度。 *需要 香草JS*

## 比較當前字型（已完成v2）

*這些腳本用於同步正體和它們的斜體。打開兩個字型檔，然後運行腳本。它們不會更改你的字型，但會在巨集面板中顯示詳細的報告。*

* **Compare Font Info > Font / 比較字型資訊 > 字型：** 對於前兩個字型檔，詳細比較字型資訊 > 字型，並在巨集面板中輸出報告。
* **Compare Font Info > Masters / 比較字型資訊 > 主板：** 對於前兩個字型檔，詳細比較字型資訊 > 主板，並在巨集面板中輸出報告。
* **Compare Font Info > Instances /  比較字型資訊 > 匯出：** 對於前兩個字型檔，詳細比較字型資訊 > 匯出，並在巨集面板中輸出報告。
* **Compare Font Info > Features / 比較字型資訊 > 特性：**  對於前兩個字型檔，詳細比較字型資訊 > 特性，並在巨集面板中輸出報告。
* **Compare Anchors / 比較錨點：** 比較前兩個字型檔之間的錨點結構和錨點高度。
* **Compare Composites / 比較複合字元：** 報告複合字符的不同結構，例如在一個字型中使用   `acutecomb` 構建的 `iacute`，而在另一個字型中使用 `acutecomb.narrow`。
* **Compare Glyph Heights / 比較字符高度：** 列出所有在字高方面與第二個字體差異超過給定閾值的字符。
* **Compare Glyph Info / 比較字符資訊：** 比較開啟的字型，並建立一個差異字符資訊列表，包括Unicode值和分類。 *需要 香草JS*
* **Compare Glyphsets / (翻譯名稱)：** 比較前兩個字型檔的字符集，並在巨集面板中輸出報告。
* **Compare Kerning Groups / 比較調距群組：** 比較前兩個字型檔之間的調距群組，輸出具有差異的群組字符名稱表格。
* **Compare Metrics / 比較度量：** 比較前兩個字型檔的字形寬度。
* **Compare Sidebearings / 比較字符邊界：** 比較前兩個字型檔的字符邊界。

## 組件（已完成v1）

*當你使用其他字母構建字母時「使用組件填充背景」非常有用，例如：ae 或 oe，該腳本將會把 e 放在每個母版的背景中，且使用者介面有一個選項可以將選定的點與背景中的 e 對齊。如果你正在使用角落組件製作多母版的襯線字體，「傳播角落組件到其他主板」將為你節省大量時間。*

* **Alignment Manager / 對齊管理器：** 啟用或停用所選字符中可見圖層上所有組件的自動就定位。與右鍵選單中的命令相同，但您可以一步完成多個字符。 *需要 香草JS*
* **Component Mover / 組件移動器：** 跨選定字符批量編輯（智慧）組件。更改位置、比例和智慧組件屬性。 *需要 香草JS*
* **Component Problem Finder / 組件問題搜尋器：** 搜尋組件和角落組件可能存在的問題：同時包含路徑和部件的組合字符；鎖定、嵌套、孤立、鏡像、平移、旋轉和縮放組件；具有異常組件順序或非正統組件結構的複合字符。也包含未連接和縮放過的角落組件。 *需要 香草JS*
* **Decompose Components in Background / 拆開背景中的組件：** 拆開所選字符的背景圖層。適用於當前主板或所有主板，或所有字型的所有主板。
* **Decompose Corner and Cap Components / 拆開角落和筆帽組件：** 拆開選定字符中的所有角落和筆帽組件。開啟巨集面板顯示報告。
* **Find and Replace Components / 置換組件：** 將所選字符中的組件重新連結到新的來源。 *需要 香草JS*
* **Find and Replace Cap and Corner Components / 置換角落和筆帽組件：** 將所選字符中的 `_cap.*` 和 `_corner.*` 組件重新連結到新的角落和筆帽組件。 *需要 香草JS*
* **Find and Replace Corner Components at Certain Angles / 依角度置換角落組件：** 以鈍角或銳角取代角落組件。 *需要 香草JS*
* **Move Paths to Component / 將路徑移動到組件：** 將路徑移動到單獨的字符中，並將它們作為錨定的自動就定位組件插入原本的字符中。非常適合將路徑和組件混雜的字符整理成純組件字符。 *需要 香草JS*
* **Populate Backgrounds with Components / 使用組件填充背景：** 添加組件到所選字符的所有背景中。 *需要 香草JS*
* **Propagate Corner Components to Other Masters / 傳播角落組件到其他主板：** 嘗試在同一字符的所有其他主板中重新建立當前主板圖層的角落組件。請確保你的外框是兼容的。
* **Remove Components / 刪除組件：** 從選定（或所有）的字符中刪除指定的組件。
* **Remove Detached Corners / 刪除分離的角落組件：** 從選定（或所有）的字符中移除分離的角落組件。
* **Stitcher / 打洞器：** 打洞器會以固定間隔在您的路徑上插入組件。用於將開放路徑變成虛線。使用稱為 `origin` 的錨點來確定拼接字母中的組件位置。考慮改用 [ Stitcher 外掛](glyphsapp3://showplugin/Stitcher)。 *需要 香草JS*
* **Sync Components Across Masters / 跨主板同步組件：** 獲取目前圖層的組件，並將所有其他主板重置為相同的組件結構。忽略路徑和錨點。按住 Option 鍵 *刪除* 所有路徑和錨點。

## 特性

*在製作手寫風格字體時，你可能經常需要「建構位置變體」的腳本。如果你發現自己經常開關 OT 功能，請用看看「啟動預設特性」和「浮動特性」腳本。並到 視窗 > 外掛程式管理員 看看 Set Palette 這個外掛。*

* **Activate Default Features / 啟動預設特性：** 在目前的編輯分頁中，啟用所有根據規範建議預設開啟的OT功能。
* **Build ccmp for Hebrew Presentation Forms / 建構希伯來表示形式的ccmp：** 為預組 uniFBxx 字符建構ccmp功能，例如，如果你有 pedagesh，則在你的ccmp中會得到 'sub pe dagesh by pedagesh'。
* **Build Italic Shift Feature / 建構斜體位移特性：** 建立並插入GPOS功能代碼，用於移動字符，例如，用於形式特性的括號和標點符號。 *需要 香草JS*
* **Build Positional Feature / 建構位置變體特性：** 尋找 .`init``.medi``.fina` 和 `.isol` 字符，並將位置取代代碼注入到你的calt特性（或其他你指定的特性）。如果再次運行，將 *更新* 類別和特性代碼。詳細資訊可參考此教程：https://glyphsapp.com/learn/features-part-4-positional-alternates *需要 香草JS*
* **Build rand Feature / 建構 rand 特性：** 從 .cvXX 或其他（編號的）後綴建構 rand（隨機）特性。 *需要 香草JS*
* **Feature Code Tweaks / 特性代碼微調：** 對OT特性代碼進行微調。在巨集面板中顯示報告。請小心使用：如果你不理解某個選項，請勿使用。 *需要 香草JS*
* **Find in Features / 在特性中搜尋：** 在OT特性、前綴和類別中搜尋表達式（字符、搜尋或類別名稱）。 *需要 香草JS*
* **Floating Features / 浮動特性：** 用於啟用和停用OT特性的浮動面板。與彈出菜單具有相同的功能。 *需要 香草JS*
* **Fraction Fever 2 / 分數瘋狂2：** 將Tal Leming 的 Fraction Fever 2 代碼插入字型中。詳細信息請參考此教程：https://glyphsapp.com/learn/fractions
* **New OT Class with Selected Glyphs / 使用所選字符建立新的OT類別：** 用於使用所選字符建立新的OT類別的圖形用戶界面。 *需要 香草JS*
* **New Tab with OT Class / 使用OT類別打開新分頁：** 用於在新分頁中打開所有OT類別中的字符（列在 *文件 > 字體資訊 > 特性 > 類別* 中）的圖形用戶界面。 *需要 香草JS*
* **Update Features without Reordering / 更新特性而不重新排序：** 瀏覽字型中現有的特性，並刷新每一個。既不添加特性，也不重新排序。
* * **Stylistic Sets > Synchronize ssXX glyphs / 文樣集 > 同步 ssXX 字形：** 建立缺失的 ssXX 字符，使你擁有同步的 ssXX 字符組。例如，如果你有 *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> 該腳本將建立 *b.ss02*。
* * **Stylistic Sets > Create ssXX from layer / 文樣集 > 從圖層建立 ssXX：** 使用當前圖層將其複製到新的 .ssXX 字符的主要圖層。
* * **Stylistic Sets > Create pseudorandom calt feature / 文樣集 > 建立虛擬隨機calt特性：** 基於字型中現有的ssXX字形數量，建立基於偽隨機的calt（上下文取代）特性。還包括在旋轉算法中的默認類別。
* * **Stylistic Sets > Set ssXX Names / 文樣集 > 設置 ssXX 名稱：** 使用‘Alternate’或其他選擇的文本，以及第一個取代的字符名稱，預先填充ssXX特性的名稱，例如‘Alternate a’。也可以選擇保留現有的命名。 *需要 香草JS*

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
* **New Tab with Uppercase-Lowercase Inconsistencies / 新分頁－大小寫不一致：** 打開一個新分頁，其中包含所有大小寫不一致的字符。在巨集面板中列出詳細報告。
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

*Most important: Set blueScale, Set Family Alignment Zones for PostScript hinting. If you are making big changes, The Transfer and Keep Only scripts can save you a lot of work. The New Tab scripts help find glyphs missing zones. Also consider Paths > Find Near Vertical Misses for that purpose.推薦腳本：「設定 blueScale」「為 PostScript 提示設置系列對齊區域」。如果你要進行大的更改，「Transfer」和「Keep Only」腳本可以為你節省大量工作。「新標籤」腳本有助於找到字形缺失區域。為此，還可以考慮路徑 > 搜尋近垂直未命中。* *:question:翻譯 專業領域暫時擱置*

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

* **Axis Location Setter / 軸位置設定器：** 批量為所有具有特定名稱字節的主板設定軸位置。例如，為所有Condensed主板設定一個軸位置。 *需要 香草JS*
* **Axis Mapper / 軸映射器：** Extracts, resets and inserts an ‘avar’ axis mapping for the Axis Mappings parameter. 提取、重置並插入Axis Mappings參數的'avar'軸映射。 *需要 香草JS*
* **Brace and Bracket Manager / 花括號和方括號管理器：** 在Glyphs 3及更高版本中搜尋並取代花括號或方括號圖層的坐標。 *需要 香草JS*
* **Composite Variabler / 合成變數：** 在使用它們的組件中，將組件的花括號和方括號圖層複製一份。使合成中的方括號圖層運作正常。 *需要 香草JS*
* **Copy Layer to Layer / 複製圖層到圖層：** 從一個主板圖層複製路徑（可選擇性地還包括組件、錨點和度量），然後黏貼到另一個主板圖層。 *需要 香草JS*
* **Dekink Masters / 消除扭結主板：** 去除所有兼容圖層中的節點扭結（如果它們不是水平或垂直的話很有用）。選擇一個或多個產生扭結的節點，運行此腳本將其他所有主圖層中的相應節點移動到相同的相對位置。因此，你在所有主圖層中實現相同的點比例，避免在角度變化時產生節點扭結。有一個 [描述它的影片](http://tinyurl.com/dekink-py)。這個三元組問題在 [這個教程中有描述](http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)。
* **Fill up Empty Masters / 填滿空白主板：** 複製一個主板的路徑到另一個，當目標主板為空白時。 *需要 香草JS*
* **Find and Replace in Layer Names / 在圖層名稱中搜尋並取代：** 取代所選字符的所有圖層名稱（除了主板圖層）中的文本。如果在許多字符中使用花括號技巧，這很有用。 *需要 香草JS*
* **Find Shapeshifting Glyphs / 搜尋形狀變化的字符：** 搜尋在插值時更改路徑數量的字符。打開新的分頁並在巨集面板中報告。 *需要 香草JS*
* **Insert Brace Layers for Component Rotation / 插入用於組件旋轉的花括號圖層：** 插入一些連續縮放和旋轉的組件的花括號圖層。對於帶有旋轉元素的OTVar插值很有用。 *需要 香草JS*
* **Insert Brace Layers for Movement along Background Path / 插入用於沿著背景路徑移動的花括號圖層：** Inserts a number of Brace Layers with copies of the first layer, shifted according to the first path in the background. Useful for OTVar interpolations with moving elements. 插入一些帶有第一圖層的複本的花括號圖層，根據背景中的第一路徑進行偏移。對於帶有移動元素的OTVar插值很有用。
* **Insert Instances / 插入實體：** 用於計算並插入字重實體的圖形用戶界面。該教程學中有詳細描述：https://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances *需要 香草JS*
* **Insert Layers / 插入圖層：** 批量在所選字符中插入花括號或方括號圖層。 *需要 香草JS*
* **Instance Cooker / 實體烹飪器：** 使用配方一次性插入多個實體。 *需要 香草JS*
* **Kink Finder / 扭結尋找：** 在輪廓或插值空間中搜尋扭結，並在巨集面板中報告它們，同時打開一個包含受影響字符的新分頁。有關紐結的訊息可參考此教學：https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible *需要 香草JS*
* **New Tab with Dangerous Glyphs for Interpolation / 打開包含插值風險字符的新分頁：** 打開一個包含字型中至少兩個兼容元素的所有字符的分頁。即，包含一個元素（路徑或元件）可能與錯誤元素進行插值的字符，例如等號。有關詳細訊息，請參閱此教學中的謹慎使用部分：<http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible>.
* **New Tab with Special Layers / 打開包含特殊圖層的新分頁：** 快速添加一個包含所有包含花括號和方括號圖層字符的新編輯分頁。
* **New Tab with Uneven Handle Distributions / 打開包含不均勻控制桿分佈的新分頁：** 搜尋控制柄分佈變化過大的字符（例如，從均衡到和諧的變化）。 *需要 香草JS*
* **OTVar Player / OTVar播放器：** 以沿著字重軸的循環方式播放目前字符的動畫。 *需要 香草JS*
* **Remove All Non-Master Layers / 刪除所有非主板圖層：** 刪除既不是主板圖層，也不是花括號圖層或方括號圖層的所有圖層。有助於清理備份圖層。
* **Report Instance Interpolations / 報告實體插值：** 在巨集面板中輸出每個實體的主板係數。告訴你在插值特定實體時涉及哪些主板和程度。
* **Reset Axis Mappings / 重置軸映射：** 為字型中目前存在的所有樣式值插入（或重置）默認的軸映射參數。忽略超出主板所定義設計空間範圍的樣式值。
* **Set Weight Axis Locations in Instances / 在實體中設置字重軸位置：** 將為所有實體設置字重軸位置參數，並將其與相應的usWeightClass同步。如果尚未設置寬度軸座標，則將其設置為usWidthClass的規範默認值。否則將保持不變。
* **Short Segment Finder / 短線段搜尋器：** 遍歷所有插值，搜尋短於用戶指定閾值長度的線段。 *需要 香草JS*
* **Travel Tracker / 旅行追蹤器：** 搜尋插值中點位移超過應有範圍的情況，即可以找到連接錯誤的星號和斜線。結果不完善，且通常會有很多誤報，但有時可以找到Shapeshifter腳本錯過的情況。 *需要 香草JS*
* **Variation Interpolator / 變體插值器：** 建立由用戶定義的字符變體數量，帶有用戶定義的後綴，其中包含圖層與其相應背景之間的插值。覆蓋相同名稱的字符。類似於Pablo Impallari的SimplePolator。例如，對於長度變體的天城體Matra很有用，請參見José Nicolás Silva Schwarzenberg的示範視頻：<https://www.youtube.com/watch?v=QDbaUlHifBc>。 *需要 香草JS*
* * **Other > Lines by Master / 每個主板一行字：** 透過每個主板呈現你的編輯文本內容，將在編輯視窗中為每個主板圖層添加一行文本。謹慎使用，將覆蓋第一個換行符後的所有內容。用於在系統偏好設定中添加快捷鍵。
* * **Other > New Tab with Masters of Selected Glyphs / 其他 > 打開包含所選字符主板圖層的新分頁：** 打開一個新的編輯分頁，其中包含所選字符的所有主板圖層。
* * **Other > Show Masters of Next/Previous Glyph / 其他 > 顯示上/下一個字符的主板圖層：** 允許你逐個字符地查看所有主板圖層。結合了顯示上/下一個字符功能（fn+左/右）和 *編輯 > 顯示所有主板* 功能。方便在系統偏好設定中設定快捷鍵。
* * **Other > Show Next/Previous Instance / 其他 > 顯示上/下一個實體：** 跳轉到目前編輯分頁預覽部分中的上/下一個實體。方便在系統偏好設定中設定快捷鍵。

## Kerning 調距

*推薦腳本：「自動緩衝器」、「KernCrasher」、「GapFinder」、「示例字符串製造器」。如果你有太多的 kerning，請考慮使用「異常清除器」。*

* **Adjust Kerning in Master / 調整主板調距：** GUI to add a value to all kerning pairs, multiply them by a value, round them by a value, or limit them to a value. 通過圖形用戶界面為所有調距字偶添加一個值，將它們乘以一個值，按一個值四捨五入，或將它們限制在一個值內。*:question:round的意思？* *需要 香草JS*
* **Auto Bumper / 自動調整器：** 指定最小距離、左邊和右邊的字符，自動調整器將為當前主圖層添加最小必要的調距。 *需要 香草JS*
* **BBox Bumper / 邊界框調整器：** 與自動調整器類似，但使用一組字符的邊界框，並將字距插入為GPOS特徵代碼，在 字型資訊 > 特性 > kern 中。如果要使用與字距群組不同的類進行群組字距調整，這很有用。 *需要 香草JS*
* **Convert RTL Kerning from Glyphs 2 to 3 / 將Glyphs 2中的RTL字距轉換為Glyphs 3格式：** 將Glyphs 2中的RTL調距轉換為Glyphs 3格式並切換調距類別。 （按住OPTION和SHIFT鍵可將Glyphs 3轉換回Glyphs 2。）在巨集面板中有詳細的報告。
* **Copy Kerning Exceptions to Double Accents / 將調距例外複製到雙重附加符號：** 將具有 `acircumflex`, `ecircumflex`, `ocircumflex`, `udieresis` 的調距例外複製到越南語和拼音的雙重附加符號中。
* **Exception Cleaner / 例外清理器：** 將每個例外與相同對的調距群組進行比較。如果差異在一個閾值以下，則刪除該調距例外。 *需要 香草JS*
* **Find and Replace in Kerning Groups / 在調距群組中搜尋與取代：** 用於在左右調距群組中搜索和取代文本的圖形用戶界面，例如將 'O' 取代為 'O.alt'。將搜尋欄位留空以進行附加。 *需要 香草JS*
* **GapFinder / 間隙搜尋器：** 在當前字型主板中打開一個新的分頁，其中包含具有大間隙的調距組合。 *需要 香草JS*
* **Import Kerning from .fea File / 從 .fea 文件導入調距：** 選擇一個包含 AFDKO 代碼中 kern 特徵的 .fea 文件，此腳本將嘗試將調距值導入到最前面的字型主板中（參見 *視窗 > 調距*）。
* **KernCrash Current Glyph / 調距衝突檢查（目前字符）：** 打開一個包含與目前字符在目前字型主板中發生衝突的調距組合的新分頁。
* **KernCrasher / 調距衝突檢查器：** 在當前字型主板中打開一個包含調距組合衝突的新分頁。 *需要 香草JS*
* **Kern Flattener / 調距平坦化工具：** 複製您的字型，將字距平坦化為僅字符對字符的調距，刪除所有調距群組並僅保留相關配對（具有內置列表），為每個實體添加一個 *匯出字距表* 參數（以及其他一些參數）。警告：僅在需要使您的調距與過時且不完善的軟體（如PowerPoint）相容時才這樣做。儘管如此，不能保證其有效性。
* **Kern String Mixer / 調距字串混合器：** 將兩組字符（也可能是標記）相互交叉，以獲得所有可能的字符組合。 *需要 香草JS*
* **New Tab with All Group Members / 包含所有群組成員的新分頁：** 選擇兩個字符，例如 'Ta'，運行該腳本，它將打開一個新分頁，其中包含 'T' 的右調距群組與 'a' 的左調距群組的所有組合。
* **New Tab with Glyphs of Same Kerning Groups / 包含相同調距群組的字符的新分頁：** 打開一個新分頁，其中包含當前字符左右調距群組的所有成員。
* **New Tab with Kerning Missing in Masters / 缺失調距的主板的新分頁：** 為每個主板打開新分頁，顯示在該主板中缺失但在其他主板中存在的調距。
* **New Tab with Large Kerning Pairs / 過大調距字偶的新分頁：** 列出所有超出給定閾值的正向和負向調距字偶。 *需要 香草JS*
* **New Tab with Overkerned Pairs / 過度調距字偶的新分頁：** 詢問閾值百分比，並打開一個新分頁，其中包含所有超出寬度閾值的負向調距字偶。例如：對於閾值為40%和寬度為160的逗號，腳本將報告任何逗號的負向調距字偶大於64（等於160的40%）。假設 r-逗號的調距為 -60，而 P-逗號的調距為 -70。在這種情況下，它將回報後者，但不是前者。 *需要 香草JS*
* **New Tab with Right Groups / 右調距群組的新分頁：** 建立一個新分頁，其中包含每個右調距群組的一個字符。用於檢查右調距群組的一致性。
* **New Tab with all Selected Glyph Combinations / 包含所有選定字符組合的新分頁：** 使用您選定的字符，打開一個包含所有可能字母組合的新分頁。同時輸出一個字符串，以便將其複製到巨集面板中，以防分頁打開失敗。
* **New Tab with Uneven Symmetric Kernings / 包含不均勻對稱調距的新分頁：** 查找對稱字母（如ATA AVA TOT WIW等）的調距字偶，並查看AT是否與TA相同之類的。
* **New Tabs with Punctuation Kern Strings / 包含標點符號調距字符串的新分頁：** 輸出帶有標點符號的調距字符串的多個分頁。
* **Remove all Kerning Exceptions / 刪除所有調距例外：** 刪除當前主板的所有調距，除了群組對群組的調距。請小心操作！
* **Remove Kerning Between Categories / 刪除類別間的調距：** 刪除字符、類別、子類別、文字之間的調距。 *需要 香草JS*
* **Remove Kerning Pairs for Selected Glyphs / 刪除所選字符的調距字偶：** 僅刪除當前主板中與所選字符相關的所有調距字偶。
* **Remove Orphaned Group Kerning / 刪除孤立的調距群組：** 刪除字型中所有指向不存在群組的調距群組。
* **Remove Small Kerning Pairs / (翻譯名稱)：** Removes all kerning pairs in the current font master with a value smaller than specified, or a value equal to zero. Be careful. *需要 香草JS*
* **Report Kerning Mistakes / (翻譯名稱)：** Tries to find unnecessary kernings and groupings. Reports in Macro window, for reviewing.
* **Sample String Maker / 示例字符串製造器：** Creates kern strings for user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored. *需要 香草JS*
* **Set Kerning Groups / (翻譯名稱)：** Sets left and right kerning groups for all selected glyphs. In the case of compounds, will use the groups of the base components, otherwise makes an informed guess based on a built-in dictionary.
* **Steal Kerning from InDesign / (翻譯名稱)：** Steals the kerning from text set in InDesign. Useful for extracting InDesign’s [Optical Kerning](https://web.archive.org/web/20160414170915/http://blog.extensis.com/adobe/about-adobe’s-optical-kerning.php) values.
* **Steal Kerning Groups from Font / (翻譯名稱)：** Steals left/right kerning groups for all selected glyphs from a 2nd font. *需要 香草JS*
* **Zero Kerner / (翻譯名稱)：** Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports. *需要 香草JS*

## 路徑（已完成v2）

*我使用「以錨點為中心旋轉」功能來處理星號符號。在輪廓檢查中非常重要：「路徑問題搜尋器」、「尋找近垂直缺失」和「節點綠藍管理器」。在 OTVar 製作中，「Rewire Fire」 變得越來越重要，因為它有助於減少形狀邊緣重疊輪廓線段（這會在反鋸齒中造成暗斑）。*

* **Align Selected Nodes with Background / 對齊選取節點與背景：** 將選取的節點與最近的背景節點對齊，除非它已經被先前移動的節點佔用。類似於使用 Cmd-Shift-A 將單個節點與背景對齊，但可針對多個節點。
* **Batch-Set Path Attributes / 批次設置路徑屬性：** 設定所選字符、主板、字型等中所有路徑的路徑屬性。 *需要 香草JS*
* **Copy Glyphs from Other Font into Backup Layers / 從其他字型複製字符到備份圖層：** 在目標字型中為所選字符建立備份圖層，並使用來源字型中相應的字符填充它們。如果您想要將一個字型的字符作為括號層添加到另一個字型中，這非常有用。 *需要 香草JS* -執行有問題？
* **Distribute Nodes / 均分節點：** 水平或垂直均分節點（取決於所選範圍的寬高比）。
* **Enlarge Short Segments / 放大單位線段：** 將線段長度小於一個單位的線段加倍。 -小於一單位？
* **Fill Up with Rectangles / 填滿矩形：** 遍歷所選字符，如果發現空白字符，則插入一個佔位符矩形。對於快速構建用於測試的虛擬字型非常有用。
* **Find Close Encounters of Orthogonal Line Segments / 找出靠近但未完全對齊的直角線段交會點：** 遍歷所有垂直和水平線段，並找到接近但未完全對齊的線段對。 *需要 香草JS*
* **Find Near Vertical Misses / 尋找近垂直缺失：** 找到靠近但不完全在垂直度量上的節點。 *需要 香草JS*
* **Green Blue Manager / 節點綠藍管理器：** 定義一個角度，節點在該角度之上被設置為藍色，在該角度之下被設置為綠色。 *需要 香草JS*
* **Grid Switcher / 格線單位切換器：** 通過點擊浮動按鈕在兩個用戶定義的格線單位之間切換。 *需要 香草JS*
* **Harmonise Curve to Line / 協調曲線與直線：** 將（選定的）曲線線段上的控制手柄重新排列，以便與後面的直線段之間的過渡是平滑的（匹配）。 -功能原理不明？
* **Interpolate two paths / 插值兩條路徑：** 選擇兩個路徑並運行此腳本，它將以50％的插值取代它們。（節點數量需一致）
* **New Tab with Small Paths / 開新分頁-小路徑：** 打開一個包含小於用戶定義閾值大小（平方單位）的路徑的新標籤頁。-小於用戶定義單位？
* **Path Problem Finder / 路徑問題搜尋器：** 在輪廓中搜尋各種潛在問題，並打開一個包含受影響圖層的新分頁。 *需要 香草JS*
* **Position Clicker / 位置點擊器：** Finds all combinations of positional shapes that do not click well. ‘Clicking’ means sharing two point coordinates when overlapping.搜尋那些在重疊時兩個形狀不能良好對齊的位置，並列出它們的組合。重疊的兩個形狀在同一個位置有共同的點坐標。-功能待測試 *需要 香草JS*
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
* **Delete Duplicate Components / 刪除重複組件：** 尋找重複的組件（相同名稱和位置）並只保留一個。這個情況經常在建立像素字型時發生。
* **Flashify Pixels / Flash化像素：** 創造小接口以避免路徑交錯產生的白色區域，這對於 Flash 字體渲染器來說尤其是一個問題，這也是此腳本名稱的由來。
* **Reset Rotated and Mirrored Components / 重置被旋轉和鏡像的組件：** 尋找被縮放、鏡像和旋轉的組件並將它們恢復為預設的比例和方向，但不更動其位置。用於修復被鏡像的像素。

## 小體大寫字母（已完成v1）

*當製作中的字體包含小體大寫字母時，可以執行「檢查小體大寫字母一致性」。不過請對它的報告持保留態度：它列出了許多誤報，而且也不是每個警告都這麼重要。*

* **Check Smallcap Consistency / 檢查小體大寫字母一致性：** 對您的小體大寫字母集執行一些測試並在巨集面板列出報告，尤其是調距群組和字符集。
* **Copy Kerning from Caps to Smallcaps / 將大寫字母的調距數值複製到小體大寫字母：** 將大寫字母的調距字偶複製到相應的小體大寫字母，如果它們包含在字型中。請注意：將覆蓋現有的小體大寫字母的調距字偶。

## 間距

*推薦腳本：「修復數學運算符間距」、「括號度量管理器」，如果你的字型中有箭頭可以試試「修復箭頭定位」。「新增分頁」腳本在建立數字時也很好用。*

* **Add Metrics Keys for Symmetric Glyphs / 為對稱字形添加度量鍵：** 如果在所有主要字符中RSB與LSB相同，將添加RSB =|。 *需要 香草JS*
* **Bracket Metrics Manager / 括號度量管理器：** 管理括號圖層（例如，美元和分）的側輻和寬度。 *需要 香草JS*
* **Center Glyphs / 居中字符：** 將所有選定的字符置於其寬度內居中，使LSB=RSB。
* **Change Metrics by Percentage / 按百分比更改度量值：** 通過百分比值更改所選字形的LSB/RSB。可使用「還原」按鈕還原更改。 *需要 香草JS*
* **Find and Replace in Metrics Keys / 在度量鍵中搜尋並取代：** 用於在左右度量鍵中搜索和取代文本的圖形用戶界面，例如將 '=X+15' 取代為 '=X'。將搜索字段留空以進行附加。
* **Fix Arrow Positioning / 修復箭頭定位：** 修復箭頭的位置和度量鍵，依賴於指定的默認箭頭。添加度量鍵並將箭頭垂直移動。不建立新字符，僅對現有字符有效。 *需要 香草JS*
* **Fix Math Operator Spacing / 修復數學運算符間距：** 同步+−×÷=≠±≈¬等符號的寬度並使其居中，可選擇還包括小於/大於符號以及上標符號/波浪號。 *需要 香草JS*
* **Freeze Placeholders / 凍結占位符：** 在當前的編輯分頁中，將更改當前字符的所有插入占位符，從而“凍結”這些占位符。
* **Metrics Key Manager / 度量鍵管理器：** 批次應用度量鍵到目前字型。 *需要 香草JS*
* **Monospace Checker / 等寬字體檢查器：** 檢查前景字型中的所有字符寬度是否實際上是等寬的。在巨集面板中報告，並打開一個包含受影響圖層的分頁。 *需要 香草JS*
* **New Tab with all Figure Combinations / 包含所有數字組合的新分頁：** 打開一個包含所有可能的數字組合的新分頁。同時輸出一個字串，以便將其複製到巨集面板中，以防分頁打開失敗。
* **New Tab with Fraction Figure Combinations / 包含分數數字組合的新分頁：** 打開一個編輯分頁，其中包含分數數字組合，以用於間距和字距的調整。
* **Remove Layer-Specific Metrics Keys / 刪除特定圖層的度量鍵：** 刪除所有所選字符的所有圖層中特定圖層（==）的左右度量鍵。同時簡化字符度量鍵（即將 "=H" 轉換為 "H"）。
* **Remove Metrics Keys / 刪除度量鍵：** 刪除所有所選字符中的左右度量鍵。影響所有主板和所有圖層。
* **Reset Alternate Glyph Widths / 重置替代字符寬度：** 將帶有後綴的字符寬度重置為其沒有後綴的對應字符的寬度。例如，`Adieresis.ss01` 將被重置為 `Adieresis` 的寬度。
* **Spacing Checker / 間距檢查器：** 搜尋具有異常間距的字符並將它們打開在一個新分頁中。 *需要 香草JS*
* **Steal Metrics / 擷取度量值：** 從第二個字型中將所有所選字符的側輻或寬度值擷取過來。可選擇性地轉換度量鍵，例如 '=x+20'。 *需要 香草JS*
* **Tabular Checker / 等寬數字檢查器：** 檢查等寬數字字符並確認它們是否等寬。報告例外情況。 *需要 香草JS*

## 測試（已完成v1）

*推薦「測試用 HTML 腳本」。如果你在 Adobe 或 Apple 應用程式中發現選取框異常的高或低，可以執行「最高和最低點字符報告」查詢找出導致狀況發生的字符。「拉丁字母支援語言報告」提供的資訊是參考性的建議，不是絕對要遵守的規範。*

* **Copy InDesign Test Text / 複製 InDesign 測試文字：** 將 InDesign 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Copy Word Test Text / 複製 Word 測試文字：** 將 Word 的測試文字複製到剪貼簿。 *:question:功能 無軟體測試*
* **Language Report / 拉丁字母支援語言報告：** 在巨集面板輸出讓你初步了解你的拉丁字符支持多少種語言以及哪些語言的資訊。基於 Underware's Latin-Plus 列表，並進行了修改。
* **Pangram Helper / 全字母句小幫手：** 幫助你編寫歐文的全字母句，你可以將其複製到剪貼簿或放入新分頁中。 *需要 香草JS* *:question:成果 其他字母句要自己添加？*
* **Report Highest and Lowest Glyphs / 最高和最低點字符報告：** 讀取所有母版的所有字符，在巨集面板輸出最高和最低點字符的資訊。
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
