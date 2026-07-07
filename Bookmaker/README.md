# Bookmaker

A small LaTeX-based layout editor for typesetting a book, as a native Mac app (SwiftUI). First iteration: text only, no images.

![](https://img.shields.io/badge/platform-macOS%2013%2B-blue)

## Requirements

- macOS 13 Ventura or later, Xcode 15 or later to build.
- A TeX distribution providing `pdflatex`: [MacTeX or BasicTeX](https://tug.org/mactex/). Bookmaker looks in `/Library/TeX/texbin`, Homebrew paths, and finally asks your login shell.

## Build & Run

Open `Bookmaker.xcodeproj` in Xcode and press ⌘R. The app is unsandboxed so it can launch `pdflatex`.

## How It Works

A **Bookmaker Book** document (`.bookmaker`, JSON) holds four things:

1. **Page settings** — paper size and the four book margins (top, bottom, inner, outer) in millimeters, with presets for A4, A5, B5, and US Trade 6″×9″.
2. **Spread template** — the LaTeX wrapper for the whole book: document class, `geometry` setup, running headers/footers for regular spreads.
3. **TOC template** — how the front matter and table of contents are produced.
4. **Body** — your chapters, as plain LaTeX (`\chapter`, `\section`, paragraphs).

On typeset, the templates and body are assembled into one `main.tex` via placeholders:

| Placeholder | Replaced with |
|---|---|
| `{{GEOMETRY}}` | `geometry` package options from the page settings |
| `{{TOC}}` | the TOC template |
| `{{BODY}}` | the body text |

`pdflatex` runs twice (so the TOC and page numbers settle) in a private temp folder, and the result appears in the preview.

## UI

- **Editor pane** with a picker to switch between Body, Spread Template, and TOC Template. Templates have a *Reset to Default* button.
- **Page setup bar** (toggleable) for paper size and margins. Change a margin, and the whole multipage document reflows.
- **PDF preview** in an optional split view (toolbar toggle), with *Single Pages* or *Spreads* display, keeping your reading position across reflows.
- **Typeset** button (⌘R) plus an *Auto Typeset* toggle that re-typesets ~1 second after you stop editing.
- Errors show a summary bar with the full LaTeX log one click away.

## Not Yet (Ideas for Later)

- Images and figures
- Multiple chapters as separate files
- Named template library, more page presets
- Export/print of the finished PDF (for now: typeset, then grab `main.pdf` from the temp folder, or print from Preview after opening the PDF)
