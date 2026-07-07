import Foundation

struct TypesetResult {
	var pdfData: Data?
	var log: String
	var errorMessage: String?
}

enum LaTeXEngine {
	static let engineCandidates = [
		"/Library/TeX/texbin/pdflatex",
		"/opt/homebrew/bin/pdflatex",
		"/usr/local/bin/pdflatex",
		"/usr/texbin/pdflatex",
	]

	static func findEngine() -> String? {
		for path in engineCandidates where FileManager.default.isExecutableFile(atPath: path) {
			return path
		}
		// last resort: the user's login shell may know a PATH that the app does not
		let process = Process()
		process.executableURL = URL(fileURLWithPath: "/bin/zsh")
		process.arguments = ["-l", "-c", "command -v pdflatex"]
		let pipe = Pipe()
		process.standardOutput = pipe
		process.standardError = Pipe()
		do {
			try process.run()
			let data = pipe.fileHandleForReading.readDataToEndOfFile()
			process.waitUntilExit()
			if process.terminationStatus == 0 {
				let path = String(decoding: data, as: UTF8.self).trimmingCharacters(in: .whitespacesAndNewlines)
				if !path.isEmpty {
					return path
				}
			}
		} catch {
			// fall through
		}
		return nil
	}

	static func typeset(source: String, in directory: URL) -> TypesetResult {
		guard let engine = findEngine() else {
			return TypesetResult(
				pdfData: nil,
				log: "",
				errorMessage: "No pdflatex found. Install MacTeX or BasicTeX from https://tug.org/mactex/"
			)
		}
		let pdfURL = directory.appendingPathComponent("main.pdf")
		do {
			try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
			try source.write(to: directory.appendingPathComponent("main.tex"), atomically: true, encoding: .utf8)

			var lastLog = ""
			// two passes so the table of contents and page references settle
			for _ in 0 ..< 2 {
				let (status, output) = runEngine(engine, in: directory)
				lastLog = output
				if status != 0 {
					return TypesetResult(
						pdfData: try? Data(contentsOf: pdfURL),
						log: output,
						errorMessage: firstErrorLine(in: output) ?? "pdflatex exited with status \(status)."
					)
				}
			}
			return TypesetResult(pdfData: try Data(contentsOf: pdfURL), log: lastLog, errorMessage: nil)
		} catch {
			return TypesetResult(pdfData: nil, log: "", errorMessage: error.localizedDescription)
		}
	}

	private static func runEngine(_ engine: String, in directory: URL) -> (Int32, String) {
		let process = Process()
		process.executableURL = URL(fileURLWithPath: engine)
		process.arguments = ["-interaction=nonstopmode", "-file-line-error", "main.tex"]
		process.currentDirectoryURL = directory
		let pipe = Pipe()
		process.standardOutput = pipe
		process.standardError = pipe
		do {
			try process.run()
		} catch {
			return (-1, "Could not launch \(engine): \(error.localizedDescription)")
		}
		let data = pipe.fileHandleForReading.readDataToEndOfFile()
		process.waitUntilExit()
		return (process.terminationStatus, String(decoding: data, as: UTF8.self))
	}

	private static func firstErrorLine(in log: String) -> String? {
		for line in log.split(separator: "\n") {
			if line.hasPrefix("!") || line.range(of: #"^[^:]+\.tex:\d+:"#, options: .regularExpression) != nil {
				return String(line)
			}
		}
		return nil
	}
}
