import SwiftUI
import PDFKit

struct ContentView: View {
	@Binding var document: BookDocument
	@StateObject private var typesetter = TypesetController()
	@State private var editedSource: EditedSource = .bodyText
	@State private var previewMode: PreviewMode = .spreads
	@State private var showPreview = true
	@State private var showPageSetup = true
	@State private var autoTypeset = true
	@State private var showLog = false
	@State private var pendingTypeset: Task<Void, Never>?

	enum EditedSource: String, CaseIterable, Identifiable {
		case bodyText = "Body"
		case spreadTemplate = "Spread Template"
		case tocTemplate = "TOC Template"
		var id: String { rawValue }
	}

	enum PreviewMode: String, CaseIterable, Identifiable {
		case singlePages = "Single Pages"
		case spreads = "Spreads"
		var id: String { rawValue }
		var pdfDisplayMode: PDFDisplayMode {
			self == .spreads ? .twoUpContinuous : .singlePageContinuous
		}
	}

	var body: some View {
		HSplitView {
			editorPane
				.frame(minWidth: 350, maxWidth: .infinity, maxHeight: .infinity)
			if showPreview {
				previewPane
					.frame(minWidth: 320, maxWidth: .infinity, maxHeight: .infinity)
			}
		}
		.toolbar {
			ToolbarItemGroup {
				if typesetter.isTypesetting {
					ProgressView()
						.controlSize(.small)
				}
				Button {
					typeset()
				} label: {
					Label("Typeset", systemImage: "play.fill")
				}
				.help("Typeset the book with pdflatex (⌘R)")
				.keyboardShortcut("r", modifiers: .command)
				.disabled(typesetter.isTypesetting)
				Toggle(isOn: $autoTypeset) {
					Label("Auto Typeset", systemImage: "arrow.triangle.2.circlepath")
				}
				.help("Automatically typeset after every change")
				Toggle(isOn: $showPageSetup) {
					Label("Page Setup", systemImage: "ruler")
				}
				.help("Show page size and margins")
				Toggle(isOn: $showPreview) {
					Label("Preview", systemImage: "sidebar.right")
				}
				.help("Show the PDF preview in a split view")
			}
		}
		.onAppear {
			typeset()
		}
		.onChange(of: document) { _ in
			scheduleAutoTypeset()
		}
	}

	// MARK: - Editor

	private var editorPane: some View {
		VStack(spacing: 0) {
			HStack {
				Picker("", selection: $editedSource) {
					ForEach(EditedSource.allCases) { source in
						Text(source.rawValue).tag(source)
					}
				}
				.pickerStyle(.segmented)
				.labelsHidden()
				if editedSource != .bodyText {
					Button("Reset to Default") {
						resetCurrentTemplate()
					}
					.help("Replace this template with the built-in default")
				}
			}
			.padding(8)
			Divider()
			TextEditor(text: sourceBinding)
				.font(.system(size: 12, design: .monospaced))
				.autocorrectionDisabled()
			if showPageSetup {
				Divider()
				PageSetupView(settings: $document.settings)
			}
		}
	}

	private var sourceBinding: Binding<String> {
		switch editedSource {
		case .bodyText:
			return $document.bodyText
		case .spreadTemplate:
			return $document.spreadTemplate
		case .tocTemplate:
			return $document.tocTemplate
		}
	}

	private func resetCurrentTemplate() {
		switch editedSource {
		case .spreadTemplate:
			document.spreadTemplate = DefaultTemplates.spread
		case .tocTemplate:
			document.tocTemplate = DefaultTemplates.toc
		case .bodyText:
			break
		}
	}

	// MARK: - Preview

	private var previewPane: some View {
		VStack(spacing: 0) {
			HStack {
				Picker("", selection: $previewMode) {
					ForEach(PreviewMode.allCases) { mode in
						Text(mode.rawValue).tag(mode)
					}
				}
				.pickerStyle(.segmented)
				.labelsHidden()
				.frame(width: 200)
				Spacer()
				if let pdf = typesetter.pdfDocument {
					Text("\(pdf.pageCount) pages")
						.font(.caption)
						.foregroundColor(.secondary)
				}
			}
			.padding(8)
			Divider()
			if let pdf = typesetter.pdfDocument {
				PDFPreviewView(document: pdf, displayMode: previewMode.pdfDisplayMode)
			} else if typesetter.isTypesetting {
				Spacer()
				ProgressView("Typesetting…")
				Spacer()
			} else {
				Spacer()
				Text("Press Typeset (⌘R) to build the PDF preview.")
					.foregroundColor(.secondary)
				Spacer()
			}
			if let error = typesetter.lastError {
				Divider()
				errorBar(error)
			}
		}
	}

	private func errorBar(_ error: String) -> some View {
		VStack(alignment: .leading, spacing: 6) {
			HStack {
				Image(systemName: "exclamationmark.triangle.fill")
					.foregroundColor(.yellow)
				Text(error)
					.font(.caption)
					.lineLimit(2)
					.textSelection(.enabled)
				Spacer()
				if !typesetter.log.isEmpty {
					Button(showLog ? "Hide Log" : "Show Log") {
						showLog.toggle()
					}
					.controlSize(.small)
				}
			}
			if showLog {
				ScrollView {
					Text(typesetter.log)
						.font(.system(size: 10, design: .monospaced))
						.textSelection(.enabled)
						.frame(maxWidth: .infinity, alignment: .leading)
				}
				.frame(height: 160)
			}
		}
		.padding(8)
	}

	// MARK: - Typesetting

	private func typeset() {
		pendingTypeset?.cancel()
		typesetter.typeset(source: document.assembledLaTeX)
	}

	private func scheduleAutoTypeset() {
		guard autoTypeset else {
			return
		}
		pendingTypeset?.cancel()
		pendingTypeset = Task {
			try? await Task.sleep(nanoseconds: 1_200_000_000)
			if !Task.isCancelled {
				typeset()
			}
		}
	}
}
