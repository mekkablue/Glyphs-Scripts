import Foundation
import PDFKit

@MainActor
final class TypesetController: ObservableObject {
	@Published var pdfDocument: PDFDocument?
	@Published var isTypesetting = false
	@Published var lastError: String?
	@Published var log = ""

	private let workDirectory: URL
	private var queuedSource: String?

	init() {
		workDirectory = FileManager.default.temporaryDirectory
			.appendingPathComponent("Bookmaker-\(UUID().uuidString)", isDirectory: true)
	}

	func typeset(source: String) {
		if isTypesetting {
			// remember the newest source and run it as soon as the current pass finishes
			queuedSource = source
			return
		}
		isTypesetting = true
		lastError = nil
		let directory = workDirectory
		Task.detached(priority: .userInitiated) {
			let result = LaTeXEngine.typeset(source: source, in: directory)
			await MainActor.run {
				self.finish(with: result)
			}
		}
	}

	private func finish(with result: TypesetResult) {
		isTypesetting = false
		log = result.log
		lastError = result.errorMessage
		if let data = result.pdfData, let pdf = PDFDocument(data: data) {
			pdfDocument = pdf
		}
		if let queued = queuedSource {
			queuedSource = nil
			typeset(source: queued)
		}
	}
}
