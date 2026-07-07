import SwiftUI

@main
struct BookmakerApp: App {
	var body: some Scene {
		DocumentGroup(newDocument: BookDocument()) { file in
			ContentView(document: file.$document)
		}
		.defaultSize(width: 1150, height: 760)
	}
}
