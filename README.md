---
date: 2024-10-25
language: zh-Hant
translator: yintzuyuan
---
# 關於

這些是用於 [Glyphs 字型編輯器](http://glyphsapp.com/)（字型編輯軟體）中進行字型製作的 Python 腳本。

# 安裝方式

## Glyphs 3

1. **安裝模組：** 在「視窗 > 外掛程式管理員」中，點選「模組」分頁，確認至少已安裝 [Python](glyphsapp3://showplugin/python)（程式語言）和 [Vanilla](glyphsapp3://showplugin/vanilla)（介面框架）模組。如果這些模組之前未安裝，請重新啟動應用程式。
2. **安裝腳本：** 前往「視窗 > 外掛程式管理員」並點選「腳本」分頁。向下捲動至 [mekkablue scripts](glyphsapp3://showplugin/mekkablue%20scripts)（腳本集），點選旁邊的「安裝」按鈕。

現在這些腳本可在「腳本 > mekkablue」中使用。如果 mekkablue 腳本沒有出現在「腳本」選單中，請按住 Option 鍵並選擇「腳本 > 重新載入腳本」(Cmd-Opt-Shift-Y)。


## Glyphs 2

### Glyphs 2 的影片安裝指南

YouTube 上有一部[關於如何安裝 mekkablue 腳本的教學影片](https://www.youtube.com/watch?v=Q6ly16Q0BmE)。當您造訪時，歡迎訂閱 [mekkablue 頻道](https://www.youtube.com/channel/UCFPSSuEMZVQtrFpTzgFh9lA)。

### Glyphs 2 的一般安裝指南

腳本需要放在應用程式的 Application Support 資料夾中的「Scripts」資料夾內。以下是安裝步驟：

1. 將腳本資料夾（或其別名）放入選擇「腳本 > 打開腳本資料夾」(Cmd-Shift-Y) 時出現的「Scripts」資料夾中：`~/Library/Application Support/Glyphs/Scripts/`，或者更好的方式是使用 **git**。詳見下方說明。
2. 然後，按住 Option (Alt) 鍵，並選擇「腳本 > 重新載入腳本」(Cmd-Opt-Shift-Y)。現在腳本會顯示在「腳本」選單中。
3. 對於某些腳本，您還需要安裝 Tal Leming 的 *Vanilla：* 前往「Glyphs > 偏好設定 > 附加元件 > 模組」並點選「安裝模組」按鈕。這樣就完成了。

### Glyphs 2 的 git 安裝方式

我建議使用 git 來取得腳本，因為這樣更容易保持更新。使用以下 git 指令將儲存庫複製到您的「腳本」資料夾中：

```bash
git clone https://github.com/mekkablue/Glyphs-Scripts ~/Library/Application\ Support/Glyphs/Scripts/mekkablue/
```

如果您對終端機感到不安，可以使用許多現成的 git 用戶端，例如免費的 [Source Tree](https://www.sourcetreeapp.com)（版本控制工具）或 [GitHub Desktop](https://desktop.github.com)（版本控制工具）。

安裝 mekkablue 腳本後，您可以透過執行「腳本 > mekkablue > App > Update git Repositories in Scripts Folder」來**更新**這個腳本儲存庫（以及您腳本資料夾中的所有其他儲存庫）。

# 疑難排解

請在 [GitHub issue](/issues) 回報問題和功能要求。請確保您使用最新版本的腳本，且應用程式已更新至最新版本。此外，請務必**同時註明您的 Glyphs 和 macOS 版本**。感謝您的配合。

# 系統需求

這些腳本需要在 macOS 10.9 或更新版本上執行最新版本的 Glyphs 2.x。我只能在最新版本的軟體中測試並使用這些腳本。如果腳本無法運作，請先更新至最新版本的腳本。

# 關於這些腳本

所有腳本在滑鼠指標停留在其選單項目上時都會顯示**工具提示**。在具有圖形使用者介面的腳本中，大多數 UI 元素（核取方塊、文字輸入欄位等）也都有工具提示。這樣您就能在需要的地方獲得解釋說明。

## Anchors（錨點）

*Anchor Mover（錨點移動工具）用於批次處理錨點位置。在調整 x 字高後特別有用。簡單建議：我總是在組合標號上使用 Reposition 指令碼，這樣堆疊的組合標號就能保持在義大利體的傾斜角度。*

* **Add missing smart anchors（新增遺漏的智慧錨點）：** 在所有圖層中為選取的智慧字符的屬性新增所有錨點。略過 *Width*（寬度）和 *Height*（高度）錨點。
* **Add ZWRO origin Anchors（新增 ZWRO 原點錨點）：** 在指定文字的所有組合標號中插入 ZWRO 的原點錨點。
* **Anchor Mover（錨點移動工具）：** 用於在多個字符中批次處理錨點位置的圖形使用者介面。
* **Batch Insert Anchors（批次插入錨點）：** 用於在多個字符中批次插入相同名稱且位於相近位置的錨點的圖形使用者介面。
* **Find and Replace in Anchor Names（錨點名稱尋找與取代）：** 用於在選取字符的錨點名稱中取代文字的圖形使用者介面。處理所有圖層。
* **Fix Arabic Anchor Order in Ligatures（修正阿拉伯文合字中的錨點順序）：** 將 *top_X* 和 *bottom_X* 錨點的順序修正為從右到左。在從其他格式轉換的檔案中，有時會發生 *top_1* 在 *top_2* 左側的情況，但應該相反，否則您的 mark2liga 會出錯。這個指令碼會檢查您選取的字符，如果是阿拉伯文合字，就會將所有錨點重新排序為從右到左，同時保持其座標不變。
* **Insert All Anchors in All Layers（在所有圖層中插入所有錨點）：** 在選取字符的每個圖層中，新增所有遺漏的錨點（但在該字符的其他圖層中已存在）。將錨點放在平均位置。
* **Insert #exit and #entry anchors at sidebearings（在字距邊緣插入 #exit 和 #entry 錨點）：** 在選取字符的所有主板和特殊圖層中，在左側字距插入 #entry，在右側字距插入 #exit（從左到右）或相反（從右到左）。除非按住 Option-Shift，否則不會覆寫現有錨點。
* **Insert #exit and #entry on baseline at selected points（在選取點的基線上插入 #exit 和 #entry）：** 使用最外側選取點的 x 座標，在基線上新增具有相同 x 座標的 #exit 和 #entry 錨點。對於從組件建立合字很有用。
* **Insert exit and entry Anchors to Selected Positional Glyphs（在選取的位置字符中插入 exit 和 entry 錨點）：** 在選取字符中新增用於連寫連接的 entry 和 exit 錨點。預設會將 exit 放在 (0, 0)，如果右側字距存在控制點，則將 entry 放在該處。請根據需求調整。
* **Mark Mover（標號移動工具）：** 將標號移動到各自的高度，例如將 …comb.case 移至大寫字高，將 …comb 移至 x 字高等。也允許設定左右度量鍵。
* **Move ogonek Anchors to Baseline Intersection（將 ogonek 錨點移至基線交點）：** 將所有 ogonek 和 _ogonek 錨點移至外框與基線最右側的交點。
* **Move topright Anchors for Vertical Carons（移動垂直抑揚符號的右上錨點）：** 將所有 topright 和 _topright 錨點移至外框與 x 字高最右側的交點。對於建立捷克/斯洛伐克文字的垂直抑揚符號很有用。
* **Move Vietnamese Marks to top_viet Anchor in Circumflex（將越南文標號移至外加符號中的 top_viet 錨點）：** 在選取字符的每個圖層中，將 *acute*、*grave* 和 *hookabovecomb* 移至 *top_viet* 錨點。對於越南文雙重重音很有用。假設您在 *circumflexcomb* 的所有圖層中都有 *top_viet* 錨點。
* **New Tab with Glyphs Containing Anchor（含錨點字符分頁）：** 開啟新分頁，顯示所有包含特定錨點的字符。
* **New Tab with top and bottom Anchors Not on Metric Lines（頂底錨點偏離基準線分頁）：** 在巨集面板中回報所有 *top* 和 *bottom* 錨點的垂直位置，並開啟新分頁顯示在字型中任何字符的主板、中括號或大括號圖層中有偏離錨點的字符。忽略使用者的選取範圍，分析所有字符（包含匯出和未匯出的字符）。適用於檢查頂部錨點是否位於正確位置。
* **Prefix all exit/entry anchors with a hashtag（替出入錨點加上井字號）：** 尋找字型中所有的 exit/entry 錨點，並在錨點名稱前加上 `#` 以停用 `curs` 特性的生成。
* **Propagate Components and Mark Anchoring（複製組件和標號錨點）：** 將目前主板的組件和標號錨點設定，複製到所有其他（相容）主板。適用於複雜的阿拉伯文合字標號。
* **Realign Stacking Anchors（重新對齊堆疊錨點）：** 在堆疊組合重音中，將頂部和底部錨點精確移動到各自的 _top 和 _bottom 錨點正上方或下方，並顧及義大利體角度。如此一來，堆疊多個非間距重音符號時將保持一致。
* **Remove Anchors in Suffixed Glyphs（移除後綴字符錨點）：** 移除具有使用者指定後綴的字符中的所有錨點。在複製、縮放和編輯字符的 sups/subs/sinf/ordn 變體後，適用於移除殘留的錨點。
* **Remove Anchors（移除錨點）：** 在選取的字符（或整個字型）中刪除具有指定名稱的錨點。
* **Remove Non-Standard Anchors from Selected Glyphs（移除選取字符中的非標準錨點）：** 移除字符中預設不應存在的所有錨點，例如 `J` 中的 `ogonek`。可能具有風險，因為它可能刪除誤判項目。建議先使用下方的回報腳本。
* **Replicate Anchors（複製錨點）：** 批次將錨點新增至選取的字符。指定來源字符以複製其錨點。
* **Replicate Anchors in Suffixed Glyphs（複製後綴字符錨點）：** 檢查選取的點後綴字符，並從其各自的基本字符複製錨點。例如，將在 *X.ss01*、*X.swsh* 和 *X.alt* 中重新建立 *X* 的錨點。
* **Report Non-Standard Anchors to Macro window（回報非標準錨點至巨集視窗）：** 檢查字型中的所有字符，並在巨集視窗中回報發現的非預設錨點。可在編輯檢視中複製貼上這些行。
* **Shine Through Anchors（透視錨點）：** 在選取字符的所有圖層中，插入來自組件的「穿透」錨點。
* **Snap Anchors to Nearest Metric（對齊錨點至最近基準）：** 在指定閾值內，將指定的錨點移動到最近的基準（如 x 字高、上伸部等）。
* **Steal Anchors（擷取錨點）：** 批次將錨點從一個字型主板複製到另一個。
* **Top Mark Mover（頂部標號移動工具）：** 垂直移動選取的標號，使其 _top 錨點位於相應的垂直基準上。

## App（應用程式）

*如果您正在編寫程式碼，建議為 Method Reporter（方法回報器）設定快捷鍵，因為您會經常需要使用它。如果您想要取得視窗內容的解析度獨立的 PDF 螢幕截圖，Print Window（列印視窗）會很有用，特別適合在向量繪圖應用程式中進行後製。*

* **Close All Tabs of All Open Fonts（關閉所有開啟字型的所有分頁）：**關閉目前在應用程式中開啟的所有字型的所有編輯分頁。
* **Copy Download URL for Current App Version（複製目前應用程式版本的下載網址）：**將目前 Glyphs 應用程式版本的下載網址複製到剪貼簿中，方便貼上。
* **Decrease（減少）**和 **Increase Line Height（增加行高）：**將編輯檢視的行高增加四分之一或減少五分之一。如果您需要經常切換行高，設定快捷鍵會很有用。
* **Method Reporter（方法回報器）：**用於過濾 Glyphs 中可用的 Python 和 PyObjC 類別方法名稱的圖形使用者介面。您可以使用多個以空格分隔的搜尋詞（作為 AND 連接）以及星號作為萬用字元（可在開頭、中間和結尾使用）。連按兩下可將方法名稱複製到剪貼簿並在巨集視窗中開啟說明。對程式設計師很有用。
* **Parameter Reporter（參數回報器）：**類似 Method Reporter，但用於自訂參數。連按兩下可將參數複製到剪貼簿中，可直接貼到字型資訊中。
* **Print Window（列印視窗）：**列印最前方的視窗。適用於儲存視窗內容的向量 PDF，包含回報器外掛程式的渲染結果（*顯示* 選單的擴充功能）。
* **Resetter（重設工具）：**重設快速預覽、鍵盤快捷鍵，並清除應用程式偏好設定、已儲存的應用程式狀態和自動儲存。
* **Set Export Paths to Adobe Fonts Folder（設定匯出路徑至 Adobe 字型資料夾）：**將 OpenType 字型和可變字型的匯出路徑設定為 Adobe 字型資料夾。
* **Set Hidden App Preferences（設定隱藏的應用程式偏好設定）：**用於讀取和設定圖形使用者介面中未列出的「隱藏」應用程式偏好設定的介面。
* **Set Label Colors（設定標籤顏色）：**覆寫預設的應用程式標籤顏色。
* **Set Tool Shortcuts（設定工具快捷鍵）：**設定工具列中工具的鍵盤快捷鍵。
* **Toggle Horizontal-Vertical（切換水平-垂直）：**在 LTR（水平）和垂直書寫方向之間切換最前方的分頁。適合設定鍵盤快捷鍵。
* **Toggle Macro Window Separator（切換巨集視窗分隔線）：**在巨集視窗中切換分隔線位置，在 80% 和 20% 之間切換。
* **Toggle RTL-LTR（切換 RTL-LTR）：**在 LTR 和 RTL 書寫方向之間切換最前方的分頁。適合在系統偏好設定中設定鍵盤快捷鍵。
* **Toggle Script Windows（切換腳本視窗）：**顯示或隱藏所有腳本視窗。適合在應用程式設定中指派快捷鍵。
* **Update git Repositories in Scripts Folder（更新腳本資料夾中的 git 儲存庫）：**在 Glyphs 腳本資料夾的所有子資料夾中執行「git pull」指令。如果您的腳本資料夾中有許多 git 儲存庫，這會很有用。
* **Update Text Preview（更新文字預覽）：**強制更新「視窗 > 文字預覽」。當您在字型視窗以外進行變更（如在字型資訊中的 OpenType 特性）且預覽無法自動重新整理時很有用。
* **Navigate > Activate next/previous glyph（導覽 > 啟用下一個/上一個字符）：**在編輯檢視中啟用下一個/上一個字符進行編輯。

## Build Glyphs（建立字符）

*最重要的是：Quote Manager（引號管理器），以及用於建立 Small Figures（小型數字）、Symbols（符號）、Ldot（L 點）的建構指令。其他指令主要用於當客戶要求特定 Unicode 範圍時，能快速開始製作。*

* **Add Adobe Symbol Glyphs（新增 Adobe 符號字符）：** 當字型中缺少以下符號字符時，會新增 Adobe 的內插符號：*Omega、Delta、Ohm、increment（增量）、asciicircum（插入符號）、greaterequal（大於等於）、infinity（無限）、partialdiff（偏微分）、lessequal（小於等於）、notequal（不等於）、product（乘積）、approxequal（約等於）、plus（加號）、lozenge（菱形）、integral（積分）、summation（總和）、radical（根號）、daggerdbl（雙劍號）、perthousand（千分號）、logicalnot（邏輯非）、plusminus（正負號）、asciitilde（波浪號）、divide（除號）、minus（減號）、multiply（乘號）、dagger（劍號）、less（小於）、equal（等於）、greater（大於）、literSign（升號）、.notdef（未定義字符）。* 需要安裝 makeotf (AFDKO)。
* **Build APL Greek（建立 APL 希臘文）：** 建立 APL 希臘文字符。
* **Build careof and cadauna（建立 careof 與 cadauna）：** 使用 `c`、`o`、`u` 和 `fraction` 字符建立 `cadauna` 和 `careof`。
* **Build Circled Glyphs（建立圓圈字符）：** 使用 `_part.circle` 以及現有的字母和數字建立圓圈數字和字母（U+24B6...24EA 和 U+2460...2473）。
* **Build Dotted Numbers（建立點號數字）：** 使用預設數字和句點建立帶句點的編號字符（例如用於有序清單的 1.、2.、3. 等格式）。
* **Build ellipsis from period components（使用句點組件建立省略號）：** 在句點字符中插入出口和入口錨點，並使用自動對齊的句點組件重建省略號。注意：會分解所有用於其他字符中的句點組件（例如冒號）。
* **Build Extra Math Symbols（建立額外數學符號）：** 建立 `lessoverequal`（小於上等於）、`greateroverequal`（大於上等於）、`bulletoperator`（點運算符）、`rightanglearc`（直角弧）、`righttriangle`（直角三角形）、`sphericalangle`（球面角）、`measuredangle`（測量角）、`sunWithRays`（帶光芒太陽）、`positionIndicator`（位置指示器）、`diameterSign`（直徑符號）、`viewdataSquare`（檢視資料方塊）、`control`（控制）。
* **Build Ldot and ldot（建立 Ldot 和 ldot）：** 使用現有的 `L` 和 `periodcentered.loclCAT`（`.case`/`.sc`）建立 `Ldot`、`ldot` 和 `ldot.sc`。假設您已經建立並適當調整了 `L`-`periodcentered.loclCAT`-`L` 等的間距。
* **Build Parenthesized Glyphs（建立括號字符）：** 建立帶括號的字母和數字：`one.paren`、`two.paren`、`three.paren`、`four.paren`、`five.paren`、`six.paren`、`seven.paren`、`eight.paren`、`nine.paren`、`one_zero.paren`、`one_one.paren`、`one_two.paren`、`one_three.paren`、`one_four.paren`、`one_five.paren`、`one_six.paren`、`one_seven.paren`、`one_eight.paren`、`one_nine.paren`、`two_zero.paren`、`a.paren`、`b.paren`、`c.paren`、`d.paren`、`e.paren`、`f.paren`、`g.paren`、`h.paren`、`i.paren`、`j.paren`、`k.paren`、`l.paren`、`m.paren`、`n.paren`、`o.paren`、`p.paren`、`q.paren`、`r.paren`、`s.paren`、`t.paren`、`u.paren`、`v.paren`、`w.paren`、`x.paren`、`y.paren`、`z.paren`。
* **Build Q from O and _tail.Q（使用 O 和 _tail.Q 建立 Q）：** 在對 Q 尾部執行「將選取的路徑轉為組件」並將其命名為 `_tail.Q` *之後*執行此指令。
* **Build Rare Symbols（建立罕用符號）：** 建立白色和黑色、小型和大型的圓形、三角形和方形。
* **Build rtlm Alternates（建立 rtlm 替代字）：** 為選取的字符建立水平鏡像組件，並更新 rtlm OpenType 特性。自動對齊組件，並在您分解組件時加入度量鍵。
* **Build Small Figures（建立小型數字）：** 使用預設的數字集（例如 `.dnom`），並衍生其他變體（`.numr`、`superior`/`.sups`、`inferior`/`.sinf`、`.subs`）作為組件副本。會顧及義大利體角度。
* **Build small letter SM, TEL（建立小寫字母 SM、TEL）：** 建立以下字符：`servicemark`（服務標記）、`telephone`（電話）。
* **Build space glyphs（建立空格字符）：** 建立各種空格字符 `mediumspace-math`、`emquad`、`emspace`、`enquad`、`enspace`、`figurespace`、`fourperemspace`、`hairspace`、`narrownbspace`、`punctuationspace`、`sixperemspace`、`nbspace`、`thinspace`、`threeperemspace`、`zerowidthspace`。
* **Build Symbols（建立符號）：** 建立符號字符，如 `.notdef`（基於最粗的可用 `question` 標記）、`estimated`（估計）字符，以及 `bar`（直線）和 `brokenbar`（斷直線）（會顧及標準字幹和義大利體角度）。
* **Center punt volat（置中間隔圓點）：** 水平移動所有 `periodcentered.loclCAT` 字符，使其適合放置在兩個 L 之間。按住 ⌘ Cmd 和 ⇧ Shift 可處理所有開啟的字型。
* **Quote Manager（引號管理器）：** 使用單引號建立雙引號，並在單引號中插入 `#exit` 和 `#entry` 錨點以進行自動對齊。您需要已經有單引號。

## Color Fonts (彩色字型)

*這些腳本是用於處理彩色字型工作流程中會遇到的情況。Merge（合併）腳本主要用於為 CPAL/COLR 字型建立備用字符。這樣備用字符就能具有完整的邊界框，且不會在 Chrome 瀏覽器中發生裁切。*

* **Add All Missing Color Layers to Selected Glyphs（為選取的字符加入所有缺少的彩色圖層）：** 為每個選取的字符，依據 Color Palettes（色盤）參數中定義的每個 CPAL/COLR 顏色，加入備用圖層的副本。僅加入字符中尚未設定的顏色。
* **Add sbix Images to Font（為字型加入 sbix 圖片）：** 會取得資料夾中所有的 PNG、GIF、JPG 檔案，並在目前的字型和主板中以這些檔案建立 iColor 圖層。檔案命名規則：「字符名稱 像素大小.副檔名」，例如：「Adieresis 128.png」。
* **Convert Layerfont to CPAL+COLR Font（將圖層字型轉換為 CPAL+COLR 字型）：** 將圖層彩色字型轉換為單一主板字型，每個字符都具有 CPAL 和 COLR 圖層。它會採用第一個主板作為預設值。
* **Convert Master Colors to CPAL Palette（將主板顏色轉換為 CPAL 色盤）：** 會在字型主板中尋找 Master Color（主板顏色）參數，然後在「字型資訊 > 字型」中建立具有相同顏色的 Color Palettes（色盤）參數。若缺少主板顏色參數則預設為黑色。會將深色模式主板顏色加入為第二個色盤。
* **Cycle CPAL Colors for Selected Glyphs（循環選取字符的 CPAL 顏色）：** 會遞增每個 CPAL Color Palette 圖層的顏色索引，若超過可用顏色數量則設為 0。
* **Delete Non-Color Layers in Selected Glyphs（刪除選取字符中的非彩色圖層）：** 刪除所有字符中不屬於 "Color X"（CPAL/COLR 圖層）類型的子圖層。
* **Merge All Other Masters in Current Master（將所有其他主板合併至目前主板）：** 在選取的字符中，將其他主板的所有路徑複製到目前的主板圖層。
* **Merge CPAL Layers into Master Layer（將 CPAL 圖層合併至主板圖層）：** 取得所有 CPAL/COLR 圖層並將其圖形的副本放入主板圖層。
* **Merge Suffixed Glyphs into Color Layers（將帶後綴的字符合併為彩色圖層）：** 將 x.shadow、x.body 和 x.front 合併為 x 的個別 CPAL Color 圖層。
* **Randomly Distribute Shapes on Color Layers（在彩色圖層上隨機分配圖形）：** 取得備用主板圖層的圖形，並隨機將它們複製到可用的 CPAL/COLR 彩色圖層上。注意：除非按住 Cmd-Shift，否則會覆寫現有彩色圖層的內容。
* **Reverse CPAL Colors for Selected Glyphs（反轉選取字符的 CPAL 顏色）：** 將反轉每個 CPAL Color Palette 圖層的顏色索引。例如，對於三個顏色，會將索引 0,1,2 轉換為 2,1,0。
* **sbix Spacer（sbix 間距工具）：** 批次設定 sbix 位置和字符寬度。

## Compare Frontmost Fonts（比較最前方字型）

*這些腳本用於同步正體與其對應的義大利體。開啟兩個字型後執行腳本。腳本不會變更您的字型，而是在巨集視窗中提供詳細報告。*

* **Compare Font Info > Font（比較字型資訊 > 字型）：** 針對最前方的兩個字型，比較其「字型資訊 > 字型」的詳細資料，並在巨集視窗中輸出報告。
* **Compare Font Info > Masters（比較字型資訊 > 主板）：** 針對最前方的兩個字型，比較其「字型資訊 > 主板」的詳細資料，並在巨集視窗中輸出報告。
* **Compare Font Info > Instances（比較字型資訊 > 實體）：** 針對最前方的兩個字型，比較其「字型資訊 > 實體」的詳細資料，並在巨集視窗中輸出報告。
* **Compare Font Info > Features（比較字型資訊 > 特性）：** 比較最前方兩個字型的 OpenType 特性設定，並在巨集視窗中輸出報告。
* **Compare Anchors（比較錨點）：** 比較最前方兩個字型之間的錨點結構與高度。
* **Compare Composites（比較組合字符）：** 報告組合字符中不一致的組件結構，例如一個字型中的 `iacute` 使用 `acutecomb` 建構，而另一個字型則使用 `acutecomb.narrow`。
* **Compare Glyph Heights（比較字符高度）：** 列出所有與第二個字型在高度上差異超過指定閾值的字符。
* **Compare Glyph Info（比較字符資訊）：** 比較開啟的字型並建立字符資訊差異清單，包含 Unicode 值和分類。
* **Compare Glyphsets（比較字符集）：** 比較最前方兩個字型的字符集，並在巨集視窗中輸出報告。
* **Compare Kerning Groups（比較調距群組）：** 比較最前方字型之間的調距群組，輸出群組不符的字符名稱表格。
* **Compare Metrics（比較度量）：** 比較最前方兩個字型的寬度。
* **Compare Sidebearings（比較邊界）：** 比較最前方兩個字型的邊界。
* **Report Missing Glyphs for all Open Fonts（報告所有開啟字型的遺漏字符）：** 在巨集視窗中，報告目前開啟的檔案中遺漏，但存在於其他字型中的所有字符。

## Components（組件）

*當您想根據其他字母建立新字母時，Populate Backgrounds with Components（使用組件填充背景）非常實用，例如 ae 或 oe 可以在背景中放置 e。此腳本會在每個主板的背景中放入 e，並且使用者介面有一個選項可以將選取的控制點與背景中的 e 對齊。如果您在多主板字型中使用角落組件來製作襯線，Propagate（傳播）腳本可以為您節省大量時間。*

* **Alignment Manager（對齊管理器）：**啟用或停用所選字符中可見圖層上所有組件的自動就定位功能。與右鍵選單中的指令功能相同，但您可以一次為多個字符執行此操作。
* **Auto-align Composites with Incremental Metrics Keys（使用遞增度量鍵自動對齊組合字符）：**針對最前方的字型，自動對齊只有第一個組件停用自動就定位的組合字符。忽略 .tf、.tosf 和數學運算符。會開啟一個分頁顯示受影響的字符圖層。
* **Cap and Corner Manager（筆帽與角落管理器）：**在最前方字型的所有字符中批次編輯筆帽、角落、筆刷或線段組件的設定。
* **Component Mover（組件移動工具）：**在選取的字符中批次編輯（智慧）組件。變更位置、縮放比例和智慧屬性。
* **Component Problem Finder（組件問題偵測器）：**尋找組件和角落組件可能存在的問題：由路徑組成的可組合字符；鎖定、巢狀、孤立、鏡射、偏移、旋轉和縮放的組件；具有不尋常組件順序或非正統組件結構的組合字符。同時也會檢查斷開連接和縮放的角落組件。
* **Composite Consistencer（組合字符一致性檢查器）：**檢查最前方字型中所有字符的目前主板中的組合字符。如果帶點後綴的字符變體缺少組件，會在巨集視窗中報告。
* **Decompose Components in Background（分解背景中的組件）：**分解選取字符的背景圖層。可用於目前主板或所有主板，或所有字型的所有主板。
* **Decompose Corner and Cap Components（分解角落和筆帽組件）：**分解選取字符中的所有角落和筆帽組件。在巨集視窗中報告結果。
* **Find and Replace Components（尋找和取代組件）：**將選取字符中的組件重新連結到新的來源字符。
* **Find and Replace Cap and Corner Components（尋找和取代筆帽和角落組件）：**將選取字符中的 `_cap.*` 和 `_corner.*` 組件重新連結到不同的角落/筆帽組件。
* **Find and Replace Corner Components at Certain Angles（在特定角度尋找和取代角落組件）：**取代鈍角或銳角處的角落組件。
* **Move Paths to Component（將路徑移至組件）：**將路徑移至單獨的字符，並將其作為自動就定位的錨點組件插入來源字符中。非常適合將路徑與組件混合的字符轉換為純組合字符。
* **Populate Backgrounds with Components（使用組件填充背景）：**將指定的組件加入字符的所有背景中，並允許您將選取的前景控制點對齊到該組件。對於保持前景中已分解形狀與相似字符同步很有用。
* **Propagate Corner Components to Other Masters（將角落組件傳播到其他主板）：**嘗試在同一字符的所有其他主板中重新建立目前主板圖層的角落組件。請確保您的外框相容。
* **Remove Components（移除組件）：**從所有（選取的）字符中移除指定的組件。
* **Remove Detached Corners（移除分離的角落）：**從所有（選取的）字符中移除分離的角落組件。
* **Sync Components Across Masters（在主板間同步組件）：**取用目前圖層的組件，並將所有其他主板重設為相同的組件結構。忽略路徑和錨點。按住 Option 鍵可*刪除*所有路徑和錨點。

## Features（特性）

*在手寫字體中，您可能經常需要 Build Positional calt script（建立位置相關 calt 腳本）。如果您發現自己經常需要開關 OT 特性，建議查看 Activate Default Features（啟用預設特性）和 Floating Features（浮動特性）腳本。另外別忘了從「視窗 > 外掛程式管理員」查看 Set Palette（設定控制盤）。*

* **Activate Default Features（啟用預設特性）：** 在目前的編輯分頁中，啟用所有依照規格建議預設開啟的 OT 特性。
* **Baseline Wiggle（基線擺動）：** 為指定類別中的所有字符加入具有虛擬隨機 GPOS 基線位移的 OpenType 特性。
* **Build ccmp for Hebrew Presentation Forms（建立希伯來文顯示形式的 ccmp）：** 為預組合的 `uniFBxx` 字符建立 ccmp 特性，例如：若您有 pedagesh，就會在 ccmp 中得到 'sub pe dagesh by pedagesh'。
* **Build Italic Shift Feature（建立義大利體位移特性）：** 建立並插入用於位移字符的 GPOS 特性程式碼，如大小寫特性中的括號和標點符號。
* **Build Positional Feature（建立位置特性）：** 尋找 `.init`、`.medi`、`.fina` 和 `.isol` 字符，並將位置替換程式碼注入到您的 `calt` 特性（或您指定的任何其他特性）中。再次執行時，會*更新*類別和特性程式碼。更多資訊請參考[此教學](https://glyphsapp.com/learn/features-part-4-positional-alternates)。
* **Build rand Feature（建立隨機特性）：** 從 .cvXX 或其他（編號）後綴建立 rand（隨機）特性。
* **Feature Code Tweaks（特性程式碼調整）：** 對 OT 特性程式碼進行調整。在巨集視窗中報告。請注意：如果您不了解某個選項，請勿使用。
* **Find in Features（在特性中尋找）：** 在 OT 特性、前置和類別中尋找表達式（字符、查詢或類別名稱）。
* **Floating Features（浮動特性）：** 用於啟用和停用 OT 特性的浮動控制盤。功能與彈出式選單相同。
* **Fraction Fever 2（分數狂熱 2）：** 將 Tal Leming 的 Fraction Fever 2 程式碼插入字型中。在[此教學](https://glyphsapp.com/learn/fractions)中了解更多。
* **New OT Class with Selected Glyphs（以選取的字符建立新 OT 類別）：** 用於以選取的字符建立新 OT 類別的圖形使用者介面。
* **New Tab with OT Class（包含 OT 類別的新分頁）：** 用於在新分頁中開啟 OT 類別（列於「*檔案 > 字型資訊 > 特性 > 類別*」）中所有字符的圖形使用者介面。
* **Update Features without Reordering（更新特性但不重新排序）：** 檢視字型中現有的特性並重新整理每一個特性。不會新增或重新排序特性。
* * **Stylistic Sets > Synchronize ssXX glyphs（樣式集 > 同步 ssXX 字符）：** 建立缺少的 ssXX 字符，以使您擁有同步的 ssXX 字符群組。例如：若您有 *a.ss01 b.ss01 c.ss01 a.ss02 c.ss02* --> 此腳本會建立 *b.ss02*
* * **Stylistic Sets > Create ssXX from layer（樣式集 > 從圖層建立 ssXX）：** 取用目前的圖層並將其複製到新 .ssXX 字符的主要圖層。
* * **Stylistic Sets > Create pseudorandom calt feature（樣式集 > 建立虛擬隨機 calt 特性）：** 根據字型中現有的 ssXX 字符數量建立虛擬隨機 calt（上下文替換）特性。也在輪替演算法中包含預設類別。
* * **Stylistic Sets > Report ssXX Names（樣式集 > 報告 ssXX 名稱）：** 報告所有開啟字型中的所有 ssXX 特性名稱。
* * **Stylistic Sets > Set ssXX Names（樣式集 > 設定 ssXX 名稱）：** 使用「Alternate」或其他選擇的文字，加上第一個被替換字符的名稱（例如「Alternate a」）預填 ssXX 特性的名稱。可選擇保留現有名稱。

## Font Info（字型資訊）

*Vertical Metrics（垂直度量）對於在「字型資訊 > 字型」和「字型資訊 > 主板」中尋找和同步垂直度量參數很有用。Clean Version String（清理版本字串）也非常實用。Font Info Batch Setter（字型資訊批次設定器）對於在多個字型之間同步字型資訊設定是不可或缺的。使用 Set WWS/Preferred Names（設定 WWS／偏好名稱）腳本時要小心：應用程式通常會自動處理命名，所以很少需要使用這些腳本。*

* **Batch-Import Masters（批次匯入主板）：**使用匯入主板參數一次匯入多個主板。
* **Clean Version String（清理版本字串）：**新增乾淨的 versionString 參數，並在版本字串中停用 ttfAutohint 資訊。匯出的字型將只包含「Version X.XXX」格式的版本字串。
* **Find and Replace in Font Info（字型資訊搜尋與取代）：**在「字型資訊 > 字型」和「字型資訊 > 實體」中搜尋和取代名稱。
* **Find and Replace In Instance Parameters（實體參數搜尋與取代）：**在目前字型或專案檔案被選取實體的自訂參數中進行搜尋和取代。
* **Font Info Batch Setter（字型資訊批次設定器）：**批次套用「字型資訊 > 字型」內的設定到開啟的字型中：設計師、設計師網址、製造商、製造商網址、版權、版本號碼、日期和時間。適用於在多個字型之間同步字型資訊設定。
* **Font Info Overview（字型資訊總覽）：**列出所有開啟字型的部分字型資訊值。
* **OTVAR Maker（OTVAR 產生器）：**在「字型資訊 > 匯出」中建立可變字型設定。
* **Prepare Font Info（準備字型資訊）：**透過設定特定自訂參數，為現代字型製作和 git 工作流程準備開啟的字型。
* **PS Name Maker（PS 名稱產生器）：**為所有實體建立 postscriptFontName 項目（名稱 ID 6），並提供縮短名稱的選項。
* **Remove Custom Parameters（移除自訂參數）：**從「字型資訊 > 字型、主板、實體」中移除某一類型的所有參數。當您有許多主板或實體時很有用。
* **Set Preferred Names for Width Variants（設定寬度變體的偏好名稱）（名稱 ID 16 和 17）：**為所有實體設定偏好名稱自訂參數（名稱 ID 16 和 17），使寬度變體在 Adobe 應用程式中出現在獨立的選單中。
* **Set Style Linking（設定樣式連結）：**嘗試設定粗體／義大利體位元。
* **Set Subscript and Superscript Parameters（設定下標和上標參數）：**測量您的上標和下標數字，並推導出下標／上標的 X／Y 偏移／大小參數。
* **Set WWS Names（設定 WWS 名稱）（名稱 ID 21 和 22）：**在必要時為所有實體設定 WWS 自訂參數（名稱 ID 21 和 22）：將除 RIBBI 以外的所有資訊放入 WWSFamilyName，並只在 WWSSubfamilyName 中保留 RIBBI。
* **Style Renamer（樣式重命名器）：**批次在樣式名稱中添加名稱片段，或從中批次移除。適用於將所有樣式從義大利體命名切換到羅馬體命名，反之亦然。
* **Vertical Metrics Manager（垂直度量管理器）：**計算並插入 OS/2 usWin 和 sTypo、hhea 以及 fsSelection 位元 7 的值（用於優先使用 sTypo 度量而非 usWin 度量）。

## Glyph Names, Notes and Unicode（字符名稱、註記與 Unicode）

*大多數文字系統都能讓字符名稱和 Unicode 的管理變得較為容易。在將檔案交給第三方之前，Garbage Collection（垃圾清理）對清除回報腳本或其他註記的雜亂資料很有幫助。*

* **Add PUA Unicode Values to Selected Glyphs（替選取的字符加入私用區 Unicode 值）：**逐一處理選取的字符，並從使用者指定的值開始，依序套用自訂 Unicode 值。
* **Casefolding Report（大小寫配對回報）：**檢查大寫與小寫是否相符。開啟新的編輯分頁，顯示所有沒有一致大小寫配對的字符。在巨集視窗中寫入詳細回報。
* **Color Composites in Shade of Base Glyph（以基礎字符色調標示組合字符）：**以基礎字符較淺色調標示組合字符。例如，如果您的 A 標示為紅色，那麼 ÄÁÀĂ... 就會呈現較淺的紅色。
* **Convert to Uppercase（轉換為大寫）：**將小寫名稱轉換為大寫名稱，例如：`a` → `A`、`ccaron` → `Ccaron`、`aeacute` → `AEacute` 等。
* **Convert to Lowercase（轉換為小寫）：**將選取字符的名稱轉換為小寫。
* **Double Encode micro, Ohm and increment（micro、Ohm 和 increment 雙重編碼）：**替 micro、Ohm 和 increment 加入 mu、Omega 和 Delta 的 Unicode。
* **Encoding Converter（編碼轉換器）：**根據可匯入/匯出的重新命名方案文字，將舊式專家級 8 位元編碼轉換為 Glyphs 的標準名稱。預設為 AXt 轉換方案。
* **Garbage Collection（垃圾清理）：**移除字符中的標記，如控制點名稱、字符名稱或註記，以及參考線。
* **Glyph Order Manager（字符順序管理器）：**用於管理字符順序參數的使用者介面，也可跨多個檔案。
* **Production Namer（產品用命名器）：**覆寫預設的產品用名稱。預設為在傳統 PDF 工作流程中會造成問題的常見項目：mu、onesuperior、twosuperior、threesuperior。
* **Rename Glyphs（重新命名字符）：**採用 `oldglyphname=newglyphname` 的配對清單，據此重新命名字型中的字符，類似「重新命名字符」自訂參數。
* **Reorder Unicodes of Selected Glyphs（重新排序選取字符的 Unicode）：**重新排序 Unicode，使預設 Unicode 排在最前。
* **Reset Unicode Codepoints Based on GlyphData（根據字符資料重設 Unicode 碼位）：**對於選取的字符，其功能類似「字符 > 更新字符資訊」，但不會更改名稱，而是重設 Unicode。將處理內建的 GlyphData 和位於 ~/Library/Application Support/Glyphs 3/Info/ 的 GlyphData-XXX.xml。
* **Switch Mirrored Characters（切換鏡像字元）：**在目前的編輯面板中，切換雙向文字的鏡射字元，例如 () → )(。在分頁中切換書寫方向後，用於切換括號和引號很有用。

## Guides（參考線）

*這些腳本主要用於清理在處理第三方字型時看到的大量參考線。*

* **Guides through All Selected Nodes (貫穿所有選取控制點的參考線)：** 在目前字符中建立貫穿所有選取控制點的參考線。會嘗試避免重複的參考線。
* **Remove Global Guides in Current Master (移除目前主板中的全域參考線)：** 刪除目前主板中所有全域（紅色）參考線。
* **Remove Local Guides in Selected Glyphs (移除選取字符中的區域參考線)：** 刪除選取字符中所有區域（藍色）參考線。
* **Select All Global Guides (選取所有全域參考線)：** 在編輯面板中選取所有全域（紅色）參考線。當您有許多參考線需要批次變形時特別有用。
* **Select All Local Guides (選取所有區域參考線)：** 選取所有區域（藍色）參考線（在所有選取的字符中）。

## Hinting（字型調適）

*最重要：為 PostScript 調適設定 blueScale 值和字型家族對齊區域。如果您要進行大幅度修改，Transfer（傳輸）和 Keep Only（僅保留）腳本可以為您節省大量工作。New Tab（新增分頁）系列腳本可協助找出缺少對齊區域的字符。另外也可以考慮使用「Paths > Find Near Vertical Misses（路徑 > 尋找接近垂直未對齊處）」來達到此目的。*

* **Add Alignment Zones for Selected Glyphs（為選取的字符新增對齊區域）：** 在所有主板中為選取的字符建立適當的對齊區域。
* **Add Hints for Selected Nodes（為選取的控制點新增調適）：** 為選取的控制點新增調適。會自動判斷應該使用水平或垂直調適。如果在對齊區域內只選取一個控制點，會新增幽靈調適。適合在系統偏好設定中設定快捷鍵。
* **Add TTF Autohint Control Instructions for Current Glyph（為目前字符新增 TTF 自動調適控制指令）：** 為目前實體的控制指令新增指定上/下數值的邊線。
* **Auto Stems（自動字幹）：** 透過測量字型中特定圖形來為所有主板推導出一個水平和一個垂直字幹值。
* **BlueFuzzer（藍色模糊工具）：** 將所有對齊區域擴展指定的數值。類似於過去 blueFuzz 值的功能，因此得名。
* **Keep Only First Master Hints（僅保留第一主板調適）：** 在選取的字符中，刪除所有圖層中的調適，只保留排序為第一主板的調適。會保留括號圖層。例如，如果您的第一主板是「Regular」，腳本會刪除「Bold」、「Bold [120]」中的調適，但保留「Regular」和「Regular [100]」中的調適。
* **New Tab with Glyphs in Alignment Zones（以位於對齊區域中的字符開啟新分頁）：** 開啟新分頁並列出所有延伸至對齊區域的字符。
* **New Tab with Layers with TTDeltas（以具有 TTDeltas 的圖層開啟新分頁）：** 開啟包含所有已定義 TTDeltas 圖層的新分頁。
* **New Tabs with Glyphs Not Reaching Into Zones（以未延伸至對齊區域的字符開啟新分頁）：** 開啟包含所有未延伸至任何上方或下方對齊區域字符的新分頁。僅計算目前主板中包含路徑的字符。忽略空白字符和組合字符。
* **Remove PS Hints（移除 PS 調適）：** 刪除目前字型、選取的主板和/或選取字符中的所有字幹和/或幽靈調適。
* **Remove TT Hints（移除 TT 調適）：** 刪除目前字型、選取的主板和/或選取字符中使用者指定的 TT 指令集。
* **Remove Zero Deltas in Selected Glyphs（移除選取字符中的零位移值）：** 檢查每個選取字符的所有圖層，並刪除所有位移值為零的 TT 差值調適。詳細報告會顯示在巨集視窗中。
* **Set blueFuzz to zero for master instances（將主板實體的 blueFuzz 設為零）：** 為與主板相同的實體新增值為 0 的 blueFuzz 自訂參數。
* **Set blueScale（設定 blueScale）：** 在「字型資訊 > 字型」中設定可能的最大 blueScale 值（決定出框微調整抑制的最大尺寸）。在巨集視窗中輸出其他選項。
* **Set Family Alignment Zones（設定字型家族對齊區域）：** 選擇一個實體，並在「字型資訊 > 字型 > 自訂參數」中將其區域設為字型家族對齊區域。
* **Set TT Stem Hints to Auto（將 TT 字幹調適設為自動）：** 將選取字符中的所有 TT 字幹調適設為「自動」。
* **Set TT Stem Hints to No Stem（將 TT 字幹調適設為無字幹）：** 將選取字符中的所有 TT 字幹調適設為「無字幹」。在複雜路徑中，這可以改善 Windows 上的渲染效果。
* **Set TTF Autohint Options（設定 TTF 自動調適選項）：** 設定現有「TTF 自動調適選項」自訂參數的選項。
* **Transfer Hints to First Master（將調適傳輸至第一主板）：** 將 PS 調適從目前圖層複製到第一主板圖層，前提是路徑必須相容。錯誤會回報至巨集視窗。
* **TT Autoinstruct（TT 自動指令）：** 自動將 Glyphs TT 指令新增至選取主板（應為第一主板）中選取的字符。注意：這不是 Werner Lemberg 的 ttfAutohint，而是 TT 指令工具（I）透過相同名稱的右鍵選單項目所新增的手動 TT 調適。適用於一次為多個字符新增調適。

## Images（圖片）

*主要用於解決處理大量（背景）圖片時可能遇到的困擾。*

* **Add Same Image to Selected Glyphs（將相同圖片加入已選取的字符）：**要求您選擇一個圖片，然後將其作為背景圖片插入至所有目前選取的字符中。
* **Adjust Image Alpha（調整圖片透明度）：**用於設定已選取字符中所有圖片透明度的滑桿。
* **Delete All Images in Font（刪除字型中的所有圖片）：**刪除整個字型中所有置入的圖片。
* **Delete Images（刪除圖片）：**刪除已選取字符之可見圖層中所有置入的圖片。
* **Reset Image Transformation（重設圖片變形）：**將已選取字符之可見圖層中的所有圖片變形（X/Y 位移、縮放和扭曲）重設回預設值。
* **Set New Path for Images（設定圖片的新路徑）：**重設已選取字符中置入圖片的路徑。當您移動了圖片位置時很實用。
* **Toggle Image Lock（切換圖片鎖定）：**鎖定或解除鎖定所有已選取字符中的全部圖片。
* **Transform Images（變形圖片）：**用於批次變形已選取字符之可見圖層中的圖片（X/Y 位移和 X/Y 縮放）的圖形使用者介面。

## Interpolation（內插）

*最重要的是：Insert Instances（插入實體，用於決定實體及其樣式連結）、Kink Finder（折點尋找器）和 Find Shapeshifting Glyphs（形變字符尋找器）。我經常使用 Show Next/Previous Instance（顯示下一個/上一個實體）搭配 ctrl-上/下方向鍵的快捷鍵。*

* **Add Grade（新增等級）：** 根據您的 Weight（字重）和 Width（字寬）變化軸，新增 Grade（等級）軸和/或 Grade 主板。
* **Add Missing Brace Layers（新增遺漏的大括號圖層）：** 完成 OTVAR 匯出所需的矩形設定。
* **Axis Location Setter（變化軸位置設定器）：** 批次設定具有特定名稱片段的所有實體的軸位置。例如，設定所有 Condensed（壓縮）實體的變化軸位置。
* **Axis Mapper（變化軸映射器）：** 提取、重設並插入軸映射參數的 'avar' 變化軸映射。
* **Batch-Add Smart Axes（批次新增智慧型變化軸）：** 為選取的字符新增智慧型變化軸和額外的智慧型圖層。
* **Brace and Bracket Manager（大括號和方括號管理器）：** 在 Glyphs 3 及更新版本中尋找和替換大括號或方括號圖層座標。
* **Bracify（大括號化）：** 將字型主板轉換為特定字符的大括號圖層。又稱為 Sparsify（稀疏化）。
* **Composite Variabler（組合變數器）：** 在使用組件的複合字符中重新複製組件的大括號和方括號圖層。使方括號圖層在組合字符中生效。
* **Copy Layer to Layer（圖層間複製）：** 將路徑（也可以選擇性地包含組件、錨點和度量）從一個主板複製到另一個主板。
* **Dekink Masters（主板去折點）：** 在所有相容圖層中去除平滑節點三元組的折點（當它們不是水平或垂直時很有用）。在一個或多個平滑節點三元組中選擇一個節點，執行此腳本可將其他所有主板中對應的控制點移動到相同的相對位置。這樣可以在所有主板中達到相同的節點比例，避免當三元組角度改變時出現內插折點。這裡有一個[說明影片](http://tinyurl.com/dekink-py)。三元組問題在[這個教學中有詳細說明](http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)。
* **Enhance Compatibility（增強相容性）：** 取用每個選取字符的目前圖層，並將控制點類型、控制點連接、重新對齊控制桿傳播到相同字符的技術相容圖層中。用於修復顯示為相容但仍無法匯出之字符的相容性。
* **Fill up Empty Masters（填充空白主板）：** 將路徑從一個主板複製到另一個主板，但僅在目標主板為空時進行。
* **Find and Replace in Layer Names（圖層名稱尋找和替換）：** 替換選取字符中所有圖層名稱（主板圖層除外）中的文字。當您在多個字符中使用方括號技巧時很有用。
* **Find Shapeshifting Glyphs（尋找形變字符）：** 尋找在內插時改變路徑數量的字符。開啟新分頁並在巨集視窗中回報。
* **Insert Brace Layers for Component Rotation（插入組件旋轉大括號圖層）：** 插入多個具有連續縮放和旋轉組件的大括號圖層。對於具有旋轉元素的 OTVar 內插很有用。
* **Insert Brace Layers for Movement along Background Path（插入沿背景路徑移動的大括號圖層）：** 插入多個包含第一個圖層副本的大括號圖層，根據背景中的第一個路徑進行位移。對於具有移動元素的 OTVar 內插很有用。
* **Insert Instances（插入實體）：** 計算和插入字重實體的圖形使用者介面。在[此教學](https://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances)中有相關描述。
* **Insert Layers（插入圖層）：** 在選取的字符中批次插入大括號或方括號圖層。
* **Instance Cooker（實體產生器）：** 使用成份設定一次產生多個實體。
* **Kink Finder（折點尋找器）：** 在外框或內插空間中尋找折點，並在巨集視窗中回報，同時開啟新分頁顯示受影響的字符。關於折點的詳細說明請參考[此教學](https://glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)。
* **New Tab with Dangerous Glyphs for Interpolation（開啟具內插風險字符分頁）：** 開啟包含所有至少有兩個相容元素的字符分頁。也就是說，會顯示某個元素（路徑或組件）可能與錯誤元素進行內插的字符，例如等號。詳細說明請參考[此教學](http://www.glyphsapp.com/learn/multiple-masters-part-2-keeping-your-outlines-compatible)中的「Find shapeshifters」章節。
* **New Tab with Special Layers（特殊圖層分頁）：** 快速新增包含所有具有大括號和方括號圖層的字符編輯分頁。
* **New Tab with Uneven Handle Distributions（控制桿分布不均分頁）：** 尋找控制桿分布變化過大的字符（例如從平衡分布變為和諧分布）。
* **OTVar Player（OpenType 可變動畫播放器）：** 以迴圈方式沿著字重軸線製作目前字符的動畫。
* **Remove All Non-Master Layers（移除非主板圖層）：** 刪除所有非主板圖層、非大括號圖層、非方括號圖層。適用於清除備份圖層。
* **Report Instance Interpolations（實體內插報告）：** 在巨集視窗中輸出每個實體的主板係數。說明特定實體涉及哪些主板的內插，以及其影響程度。
* **Reset Axis Mappings（重設變化軸映射）：** 為字型中目前所有的樣式值插入（或重設）預設的變化軸映射參數。忽略主板定義的設計空間範圍以外的樣式值。
* **Set Weight Axis Locations in Instances（設定實體字重軸位置）：** 為所有實體設定字重軸位置參數，並與各自的 usWeightClass 同步。如果尚未設定寬度軸座標，將設定為符合 usWidthClass 規格的預設值。否則保持現有設定。
* **Short Segment Finder（短線段尋找器）：** 檢查所有內插並尋找短於使用者指定閾值的線段。
* **Travel Tracker（路徑追蹤器）：** 尋找控制點位移過度的內插，可用於找出錯誤連接的星號和斜線。結果可能不完整，且通常會有許多誤判，但有時能找出 Shapeshifter 腳本遺漏的情況。
* **Variation Interpolator（變體內插器）：** 建立使用者定義數量的字符變體，並加上使用者定義的後綴，包含圖層與其各自背景之間的內插。會覆寫同名字符。類似 Pablo Impallari 的 SimplePolator。適用於例如天城文 Matra 的長度變體，請參考 José Nicolás Silva Schwarzenberg 的[示範影片](https://www.youtube.com/watch?v=QDbaUlHifBc)。
* * **Other > Lines by Master（依主板分行）：** 將您的編輯文字複製到各個主板中，會在編輯面板中為每個主板新增一行。請注意，會忽略第一個換行符號之後的所有內容。適用於在系統偏好設定中新增鍵盤快捷鍵。
* * **Other > New Tab with Masters of Selected Glyphs（以所選字符的主板開新分頁）：** 開啟新的編輯分頁，顯示所選字符的所有主板。
* * **Other > Show Masters of Next/Previous Glyph（顯示下一個/上一個字符的主板）：** 讓您可以逐一瀏覽字符，但會顯示所有主板。結合了顯示下一個/上一個字符功能（fn+左/右方向鍵）與「*編輯 > 顯示所有主板*」功能。適合在系統偏好設定中設定鍵盤快捷鍵。
* * **Other > Show Next/Previous Instance（顯示下一個/上一個實體）：** 在目前編輯分頁的預覽區塊中跳至下一個/上一個實體。適合在系統偏好設定中設定鍵盤快捷鍵。

## Kerning（調距）

*最重要的工具：Auto Bumper（自動調距）、KernCrasher（調距碰撞檢查）、GapFinder（間距檢查）、Sample String Maker（範例字串產生器）。如果您的調距過多，可以考慮使用 Exception Cleaner（例外清理器）。*

* **Adjust Kerning in Master（主板調距調整）：**提供圖形介面，可對所有調距對新增數值、進行倍數運算、進行數值四捨五入，或限制在特定數值範圍內。
* **Auto Bumper（自動調距）：**指定最小間距、左右字符後，Auto Bumper 會在目前的主板中新增必要的最小調距。
* **BBox Bumper（邊界框調距）：**類似 Auto Bumper，但是使用一組字符的邊界框，並將調距以 GPOS 特性程式碼插入到「字型資訊 > 特性 > kern」。當您想要使用與調距群組不同的類別進行群組調距時很有用。需要 Vanilla。
* **Compare Kerning Between Masters（主板間調距比較）：**回報兩個主板之間調距結構的差異。
* **Compress Glyph（字符壓縮）：**僅壓縮指定字符的調距。
* **Convert RTL Kerning from Glyphs 2 to 3（從 Glyphs 2 轉換 RTL 調距到 Glyphs 3）：**將 Glyphs 2 的 RTL 調距轉換為 Glyphs 3 格式並切換調距類別。（按住 Option 和 Shift 可從 Glyphs 3 轉回 Glyphs 2。）詳細報告在巨集視窗中。
* **Copy Kerning Exceptions to Double Accents（複製調距例外到雙重重音）：**將包含 abreve、`acircumflex`、`ecircumflex`、`ocircumflex`、`udieresis` 的調距例外複製到越南語和拼音的雙重重音符號。
* **Exception Cleaner（例外清理器）：**比較每個例外與相同字偶可用的群組調距。如果差異低於閾值，則移除該調距例外。
* **Find and Replace in Kerning Groups（調距群組尋找與取代）：**提供圖形介面，用於在左右調距群組中搜尋和取代文字，例如將「O」取代為「O.alt」。留空搜尋欄位可用於附加。
* **GapFinder（間隙檢查）：**在目前的字型主板中開啟新分頁，顯示具有大間隙的調距組合。
* **Import Kerning from .fea File（從 .fea 檔案匯入調距）：**選擇包含 AFDKO 程式碼 kern 特性的 .fea 檔案，此指令碼將嘗試將調距值匯入最前方的字型主板（請參見「*視窗 > 調距*」）。
* **KernCrash Current Glyph（目前字符調距碰撞檢查）：**在目前的字型主板中開啟新分頁，顯示與目前字符發生碰撞的調距組合。
* **KernCrasher（調距碰撞檢查）：**在目前的字型主板中開啟新分頁，顯示發生碰撞的調距組合。
* **Kern Flattener（調距平面化）：**複製您的字型，將調距平面化為僅限字符對字符的調距，刪除所有群組調距並僅保留相關字偶（內建清單），為每個實體新增*匯出 kern 表格*參數（和其他一些參數）。警告：這只適用於使其與過時和損壞的軟體（如 PowerPoint）相容。不過，無法保證一定有效。
* **Kern String Mixer（調距字串混合器）：**將兩組字符（可使用代碼）相互交叉，以獲得所有可能的字符組合。
* **New Tab with All Group Members（使用群組成員開新分頁）：** 選取兩個字符，例如「Ta」，執行腳本後會開啟新分頁，顯示 T 的右側調距群組與 a 的左側調距群組的所有組合。
* **New Tab with Glyphs of Same Kerning Groups（相同調距群組字符開新分頁）：** 開啟新分頁，顯示目前字符的左右調距群組的所有成員。
* **New Tab with Kerning Missing in Masters（主板缺漏調距開新分頁）：** 為每個主板開啟新分頁，顯示在此主板中缺少但存在於其他主板中的調距。
* **New Tab with Overkerned Pairs（過度調距字偶開新分頁）：** 詢問閾值百分比，並開啟新分頁顯示所有超過寬度閾值的負值調距字偶。例如：閾值為 40%，逗號寬度為 160，腳本會回報任何大於 64（160 的 40%）的負值調距字偶。假設 r-逗號的調距值為 -60，P-逗號的調距值為 -70，在這種情況下，只會回報後者而非前者。
* **New Tab with Right Groups（右側群組開新分頁）：** 建立新分頁，每個右側群組顯示一個字符。適用於檢查右側調距群組的一致性。
* **New Tab with all Selected Glyph Combinations（已選字符組合開新分頁）：** 將您選取的字符建立所有可能的組合並開啟新分頁。同時輸出一個字串到巨集視窗，以備分頁開啟失敗時使用。
* **New Tab with Uneven Symmetric Kernings（不對稱調距開新分頁）：** 尋找對稱字母的調距字偶，如 ATA、AVA、TOT、WIW 等，並檢查 AT 是否與 TA 相同等。
* **New Tabs with Punctuation Kern Strings（標點符號調距字串開新分頁）：** 輸出多個包含標點符號調距字串的分頁。
* **Partial Compress（部分壓縮）：** 僅針對特定字符壓縮調距。
* **Remove Kerning Between Categories（移除類別間調距）：** 移除字符、類別、子類別、字符集之間的調距。
* **Remove Kerning Exceptions（移除調距例外）：** 移除目前主板的所有調距，但保留群組對群組的調距。請謹慎使用。
* **Remove Kerning Pairs for Selected Glyphs（移除已選字符的調距字偶）：** 僅刪除目前主板中已選字符的所有調距字偶。
* **Remove Orphaned Group Kerning（移除孤立群組調距）：** 刪除所有參照到字型中不存在群組的群組調距。
* **Remove Small Kerning Pairs（移除微小調距字偶）：** 移除目前字型主板中所有小於指定值或等於零的調距字偶。請謹慎使用。
* **Report Kerning Mistakes（回報調距錯誤）：** 嘗試找出不必要的調距和群組。在巨集視窗中回報供審查。
* **Sample String Maker（範例字串產生器）：** 為使用者定義的類別建立調距字串，並加入到範例字串中。僅限群組調距，忽略無群組的字符。
* **Sample Strings with Master Kerning（主板調距範例字串）：** 為目前的調距建立調距字串，並加入到範例字串中。
* **Set Kerning Groups（設定調距群組）：** 為所有選取的字符設定左右調距群組。對於組合字符，會使用基礎組件的群組，否則會根據內建字典做出合理推測。
* **Steal Kerning from InDesign（從 InDesign 取得調距）：** 從 InDesign 中設定的文字取得調距。適用於擷取 InDesign 的[光學調距](https://web.archive.org/web/20160414170915/http://blog.extensis.com/adobe/about-adobe%E2%80%99s-optical-kerning.php)值。
* **Steal Kerning Groups from Font（從字型取得調距群組）：** 從第二個字型中取得所有選取字符的左右調距群組。
* **Transfer RTL kerning（轉移 RTL 調距）：** 將從右至左書寫的調距從一個主板轉移到另一個主板。
* **Zero Kerner（零值調距器）：** 為在某個主板中缺少但存在於其他主板的字偶加入值為零的群組調距。有助於在 OTVar 匯出時保留可內插的調距。

## Paths（路徑）

*我使用 Rotate Around Anchor（繞錨點旋轉）來製作星號。對於外框檢查來說很重要的工具有：Path Problem Finder（路徑問題檢測器）、Find Near Vertical Misses（尋找接近垂直的未對齊點）和 Green Blue Manager（綠藍控制點管理器）。Rewire Fire（重新連接工具）在可變字型製作中變得很重要，因為它可以減少形狀邊緣的重複外框線段（這些重複線段會在反鋸齒時產生暗點）。*

* **Align Selected Nodes with Background（將選取的控制點對齊背景）：**將選取的控制點對齊最近的背景控制點，除非該背景控制點已被先前移動的控制點佔用。類似使用 Cmd-Shift-A 來對齊單一控制點與背景，但這個功能可以一次處理多個控制點。
* **Batch-Set Path Attributes（批次設定路徑屬性）：**設定選取字符、主板、字型等中所有路徑的屬性。
* **Copy Glyphs from Other Font into Backup Layers（將其他字型的字符複製到備份圖層）：**在目標字型中為選取的字符建立備份圖層，並用來源字型中對應的字符填充這些圖層。當您想要將一個字型的字符作為另一個字型的括號圖層時很有用。
* **Distribute Nodes（分配控制點）：**水平或垂直分配控制點（取決於選取範圍邊界框的寬高比）。
* **Enlarge Single-Unit Segments（放大單位線段）：**將短於一個單位的線段長度加倍。
* **Fill Up with Rectangles（以矩形填充）：**檢查您選取的字符，如果發現空白的字符，就插入一個佔位矩形。適用於快速建立測試用的暫代字型。
* **Find Close Encounters of Orthogonal Line Segments（尋找正交線段的接近處）：**檢查所有垂直和水平線段，找出接近但未完全對齊的線段對。
* **Find Near Vertical Misses（尋找接近垂直的未對齊控制點）：**找出接近但未完全位於垂直度量線上的控制點。
* **Green Blue Manager（綠藍控制點管理器）：**定義一個角度，高於此角度的控制點將設為藍色，低於此角度的控制點將設為綠色。
* **Grid Switcher（格線切換器）：**透過點選浮動按鈕，在兩個使用者可定義的格線間距值之間切換。
* **Harmonise Curve to Line（曲線與直線和諧化）：**將（選取的）曲線段與其後續直線段的控制點重新排列，使兩個線段之間平滑的轉換（和諧化）。
* **Interpolate two paths（內插兩個路徑）：**選取兩個路徑並執行此腳本，它會將這兩個路徑替換為它們在 50% 處的內插結果。
* **New Tab with Small Paths（開啟含小路徑的新分頁）：**開啟一個新分頁，顯示面積小於使用者可定義閾值（以平方單位計）的路徑。
* **Path Problem Finder（路徑問題偵測器）：**尋找外框中所有可能的問題，並在新分頁中顯示受影響的圖層。
* **Position Clicker（位置吻合檢查器）：**尋找所有位置形狀組合中不能良好吻合的部分。「吻合」指的是重疊時共用兩個節點座標。
* **Realign BCPs（重新對齊貝茲控制點）：**重新對齊所有選取字符中的所有貝茲控制點。當控制桿因推移或其他變形後失去同步，或是在內插後特別有用。按住 Option 鍵可套用到選取字符的所有圖層。
* **Remove all Open Paths（移除所有開放路徑）：**刪除所有選取字符可見圖層中的所有*開放*路徑。
* **Remove Short Segments（移除短線段）：**刪除短於一個單位的線段。
* **Rewire Fire（重複座標檢查）：**尋找、選取並標記重複的座標。位於相同位置的兩個控制點通常可以使用重新連接控制點功能進行重新連接。
* **Rotate Around Anchor（錨點旋轉）：**提供以「rotate」錨點為中心旋轉字符或選取的控制點和組件的圖形介面。允許逐步和重複操作。
* **Set Transform Origin（設定變形基準點）：**提供以數值方式設定旋轉工具變形基準點的簡易圖形介面。對縮放工具也會有效果。
* **Snap selected points to nearest metric in all masters（將選取節點對齊所有主板中最近的度量）：**選取節點並執行此腳本，可將節點對齊每個相容圖層中最近的度量，前提是與度量的距離不超過 2 個單位。在巨集視窗中顯示報告。
* **Straight Stem Cruncher（直線字幹檢查器）：**在所有圖層中尋找節點之間的距離，並與指定的字幹寬度進行比較（具有容許值）。列出繪製中具有偏差字幹的字符。
* **Tunnify（控制桿平均化）：**尋找至少有一個控制桿被選取的所有路徑段。然後，將這些線段的控制桿平均化，也就是讓它們具有相同的曲線符合百分比。可以修正 Adobe Illustrator 的零控制桿（一個控制桿縮回最近控制點的線段）。這個腳本的想法來自 Eduardo Tunni（由 Pablo Impallari 轉述），因此以此命名。不過我從未看過 Eduardo 的演算法，所以我的實作可能與他的有些許不同，特別是在處理零控制桿的部分。

## Pixelfonts（像素字型）

*這些腳本適用於像素字型的工作流程，讓您可以在較粗的網格中放置像素組件。如果您在進行像素設計，可以查看「視窗 > 外掛程式管理員」中提供的像素相關外掛程式。*

* **Align Anchors to Grid（將錨點對齊格線）：**將變音符號的錨點對齊至字型格線。
* **Delete Components out of Bounds（刪除超出邊界的組件）：**如果組件被放置在一般座標範圍之外（當您使用 cmd-方向鍵移動具有較大格線間距的組件時可能發生），這個腳本會將其刪除。
* **Delete Duplicate Components（刪除重複組件）：**尋找重複的組件（相同名稱和位置）並只保留一個。這種情況在製作像素字型時經常發生。
* **Flashify Pixels（Flash 像素最佳化）：**建立小型橋接以防止路徑自我相交，使字符內空白部分保持白色。這個問題在 Flash 字型渲染器中特別明顯，因此腳本以此命名。
* **Reset Rotated and Mirrored Components（重設旋轉和鏡射組件）：**尋找經過縮放、鏡像和旋轉的組件，將它們恢復為預設的縮放比例和方向，但保持其位置不變。這對修正鏡射像素很有用。

## Post Production（後製處理）

*如果您使用最新版本的 Glyphs，DSIG 和 GDEF 腳本已不再需要。對於義大利體的匯出，我建議修正 PS 名稱和 STAT 項目。Upgrade STAT 腳本是選用性的，它會新增目前軟體幾乎不支援的範圍，但可能對未來相容性有幫助。*

* **Add Empty DSIG (OTVAR)「新增空白 DSIG」：** 在匯出可變字型 (TTF) 後執行此腳本，它會新增一個空白的 DSIG 表格。這是通過 MyFonts 的 OTVAR TTF 上架程序所必需的。需要 FontTools 模組。在最新的 Glyphs 3.2+ 版本中，此腳本應該已不再需要。
* **Fix GDEF class definition of Legacy Marks (OTVAR)「修正傳統標記的 GDEF 類別定義」：** 修正最近匯出的 OTVAR 中，具有間距、非組合標記的 GDEF 定義，必要時會切換至類別 1（「基底字符」，單一字元，具間距字符）。需要 FontTools 模組。在最新的 Glyphs 3.2+ 版本中，此腳本應該已不再需要。
* **Fix Italic PS Names (OTVAR)「修正義大利體 PS 名稱」：** 修正目前字型最近匯出中，用於 fvar postScriptName 項目的名稱表格中重複的義大利體命名，例如將 `MyfontItalic-SemiboldItalic` 改為 `MyfontItalic-Semibold`。在匯出義大利體可變字型後立即執行此腳本。需要 FontTools 模組。
* **Fix Italic STAT Entries (OTVAR)「修正義大利體 STAT 項目」：** 針對每個軸向，將一般 STAT 項目重新命名為「Regular」（必要時也會修改名稱表格），並使其可省略（Flags=2）。通常只在義大利體 OTVAR 匯出時需要。需要 FontTools 模組。
* **Read and Write Axis Values (OTVAR)「讀取與寫入軸向數值」：** 在 OTVAR 匯出後執行一次，它會讀取目前 Glyphs 檔案最近匯出的 STAT.AxisValueArray，並在您的可變字型設定中新增「Axis Values」參數。當執行時若存在這些自訂參數，它會用來重寫目前 Glyphs 檔案最近匯出的 OTVAR 中的 STAT.AxisValueArray。自訂參數的數值語法：`axisTag; value=name, value=elidableName*, minValue:nominalValue:maxValue=name, value>linkedValue=name`
* **Upgrade STAT Axis Values from Discrete to Ranges (OTVAR)「將 STAT 軸向數值從離散升級為範圍」：** 將具有多個軸向數值的軸的格式 1（離散）STAT 項目轉換為格式 2（範圍）。請在匯出可變字型後立即執行此腳本。需要 FontTools 模組。

## Smallcaps（小型大寫字母）

*當我的字型中有小型大寫字母時，我總是會執行 Check Smallcap Consistency（檢查小型大寫字母一致性）。不過對其報告要抱持保留態度：它列出了許多誤判項目，且並非每個警告都同樣重要。*

* **Check Smallcap Consistency（檢查小型大寫字母一致性）：**對您的小型大寫字母集進行一系列測試，並在巨集視窗中提供報告，特別是針對調距群組和字符集的部分。
* **Copy Kerning from Caps to Smallcaps（從大寫複製調距至小型大寫字母）：**尋找大寫字母的調距字偶，並在字型中有對應的 .sc 字符時，複製其調距設定。請謹慎使用：這會覆寫現有的小型大寫字母調距字偶。

## Spacing（間距）

*最重要的是：Fix Math Operator Spacing（修正數學運算子間距）、Bracket Metrics Manager（括號度量管理器），如果有箭頭符號，則需要 Fix Arrow Positioning（修正箭頭位置）。建立數字時，New Tab（開新分頁）系列腳本很實用。*

* **Add Metrics Keys for Symmetric Glyphs（為對稱字符加入度量鍵）：** 當所有主板中的右側空白 (RSB) 與左側空白 (LSB) 相同時，會加入 RSB =|。
* **Adjust Sidebearings（調整邊界）：** 可進行邊界的乘除、加減、限制或四捨五入，並可區分正負值的邊界。
* **Bracket Metrics Manager（括號度量管理器）：** 管理括號圖層的邊界和寬度，例如美元符號和美分符號。
* **Center Glyphs（置中字符）：** 將所有選取的字符置中於其寬度內，使 LSB=RSB。
* **Change Metrics by Percentage（依百分比更改度量）：** 依百分比更改選取字符的左右邊界。可使用還原按鈕復原。
* **Find and Replace in Metrics Keys（在度量鍵中尋找和取代）：** 用於在左右度量鍵中搜尋與取代文字的圖形介面，例如將「=X+15」取代為「=X」。搜尋欄位留空則為附加模式。
* **Fix Arrow Positioning（修正箭頭位置）：** 根據指定的預設箭頭修正箭頭的位置和度量鍵。加入度量鍵並垂直移動箭頭。僅作用於現有字符，不會建立新字符。
* **Fix Math Operator Spacing（修正數學運算子間距）：** 同步寬度並置中 +−×÷=≠±≈¬ 等符號，可選擇是否包含大於/小於符號和抑揚符/波浪號。
* **Freeze Placeholders（凍結預留位置）：** 在目前的編輯分頁中，將所有插入的預留位置變更為目前字符，從而「凍結」預留位置。
* **Metrics Key Manager（度量鍵管理器）：** 批次套用度量鍵到目前的字型。
* **Monospace Checker（等寬檢查器）：** 檢查最前方字型中的所有字符寬度是否確實等寬。在巨集視窗中回報並開啟受影響圖層的分頁。
* **New Tab with all Figure Combinations（開啟含所有數字組合的新分頁）：** 開啟含所有可能數字組合的新分頁。同時輸出字串到巨集視窗，以備開啟分頁失敗時使用。
* **New Tab with Fraction Figure Combinations（開啟含分數數字組合的新分頁）：** 開啟含分數數字組合的編輯分頁，用於調整間距和調距。
* **Remove Layer-Specific Metrics Keys（移除圖層專用度量鍵）：** 刪除所有選取字符的所有圖層專用（==）左右度量鍵。同時簡化字符度量鍵（例如，將「=H」變更為「H」）。
* **Remove Metrics Keys（移除度量鍵）：** 刪除所有選取字符的左右度量鍵。影響所有主板和圖層。
* **Reset Alternate Glyph Widths（重設替代字符寬度）：** 將帶後綴的字符寬度重設為其無後綴對應字符的寬度。例如，將 `Adieresis.ss01` 重設為 `Adieresis` 的寬度。
* **Spacing Checker（間距檢查器）：** 尋找具有異常間距的字符並在新分頁中開啟。
* **Steal Metrics（擷取度量）：** 從第二個字型擷取所有選取字符的邊界或寬度值。可選擇是否也轉移如「=x+20」等度量鍵。
* **Tabular Checker（等寬檢查器）：** 檢查等寬字符是否等寬，並回報例外情況。
* **Tabular Figure Maker（等寬數字製作器）：** 使用現有的 .tf 數字並設定等寬間距，或從現有的預設數字建立它們。

## Test（測試）

*最重要的是 Test HTML（測試 HTML）腳本。如果你在 Adobe 或 Apple 應用程式中發現文字選取區域異常偏高或偏低，請執行 Report Highest and Lowest Glyphs（回報最高與最低字符）來找出造成問題的字符。Language Report（語言報告）僅供充實你的樣本使用，不會提供權威性的資訊。*

* **Copy InDesign Test Text（複製 InDesign 測試文字）：**將測試文字複製到剪貼簿中，供 InDesign 使用。
* **Copy Word Test Text（複製 Word 測試文字）：**將測試文字複製到剪貼簿中，供 MS Word 使用。
* **Language Report（語言報告）：**試圖根據你的拉丁字符提供初步的語言支援範圍評估。以 Underware 的 Latin-Plus 清單為基礎並加以修改。
* **Pangram Helper（全字母句協助工具）：**協助你撰寫全字母句，可複製到剪貼簿或放入新分頁中。
* **Report Highest and Lowest Glyphs（回報最高與最低字符）：**回報所有主板中具有最高和最低邊界框的字符。
* **Variable Font Test HTML（可變字型測試 HTML）：**在目前可變字型匯出資料夾中為目前的字型建立測試用 HTML。
* **Webfont Test HTML（網頁字型測試 HTML）：**在目前的網頁字型匯出資料夾內，或是目前 Glyphs 專案的匯出路徑中，建立一個測試用 HTML。

# 授權條款

Copyright 2011 The mekkablue Glyphs-Scripts (Glyphs 腳本) Project Authors (專案作者群)。

部分程式碼範例由 Georg Seifert (@schriftgestalt) 和 Tal Leming (@typesupply) 提供。

部分演算法構想由 Christoph Schindler (@hop) 和 Maciej Ratajski (@maciejratajski) 提供。

部分程式碼修正來自 Rafał Buchner (@RafalBuchner)。

本專案採用 Apache License, Version 2.0 (Apache 2.0 版授權條款) 授權。
除非遵守本授權條款，否則不得使用此處提供的軟體。
您可以在以下網址取得授權條款內容：

http://www.apache.org/licenses/LICENSE-2.0

如需更多詳細資訊，請參閱本儲存庫中隨附的授權條款檔案。
