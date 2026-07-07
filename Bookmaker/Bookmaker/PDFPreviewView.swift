import SwiftUI
import PDFKit

struct PDFPreviewView: NSViewRepresentable {
	let document: PDFDocument?
	var displayMode: PDFDisplayMode = .twoUpContinuous

	func makeNSView(context: Context) -> PDFView {
		let view = PDFView()
		view.autoScales = true
		view.displayMode = displayMode
		view.displaysAsBook = displayMode == .twoUpContinuous
		view.document = document
		return view
	}

	func updateNSView(_ view: PDFView, context: Context) {
		view.displayMode = displayMode
		view.displaysAsBook = displayMode == .twoUpContinuous
		if view.document !== document {
			// keep the reading position across reflows
			var pageIndex = 0
			if let currentPage = view.currentPage, let oldDocument = view.document {
				pageIndex = oldDocument.index(for: currentPage)
			}
			view.document = document
			if let document = document, pageIndex > 0 {
				let boundedIndex = min(pageIndex, document.pageCount - 1)
				if boundedIndex > 0, let page = document.page(at: boundedIndex) {
					view.go(to: page)
				}
			}
		}
	}
}
