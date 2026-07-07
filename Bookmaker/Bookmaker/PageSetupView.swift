import SwiftUI

struct PageSetupView: View {
	@Binding var settings: PageSettings

	private static let presets: [(name: String, width: Double, height: Double)] = [
		("A4", 210, 297),
		("A5", 148, 210),
		("B5", 176, 250),
		("US Trade 6″×9″", 152.4, 228.6),
	]

	var body: some View {
		VStack(alignment: .leading, spacing: 6) {
			HStack(spacing: 12) {
				Picker("Page:", selection: presetBinding) {
					ForEach(Self.presets, id: \.name) { preset in
						Text(preset.name).tag(preset.name)
					}
					Text("Custom").tag("Custom")
				}
				.fixedSize()
				mmField("Width", $settings.paperWidth)
				mmField("Height", $settings.paperHeight)
			}
			HStack(spacing: 12) {
				Text("Margins:")
				mmField("Top", $settings.marginTop)
				mmField("Bottom", $settings.marginBottom)
				mmField("Inner", $settings.marginInner)
				mmField("Outer", $settings.marginOuter)
			}
		}
		.padding(10)
	}

	private var presetBinding: Binding<String> {
		Binding(
			get: {
				Self.presets.first { $0.width == settings.paperWidth && $0.height == settings.paperHeight }?.name ?? "Custom"
			},
			set: { name in
				if let preset = Self.presets.first(where: { $0.name == name }) {
					settings.paperWidth = preset.width
					settings.paperHeight = preset.height
				}
			}
		)
	}

	private func mmField(_ label: String, _ value: Binding<Double>) -> some View {
		HStack(spacing: 4) {
			Text(label)
				.font(.caption)
				.foregroundColor(.secondary)
			TextField("", value: value, format: .number)
				.textFieldStyle(.roundedBorder)
				.multilineTextAlignment(.trailing)
				.frame(width: 52)
			Text("mm")
				.font(.caption)
				.foregroundColor(.secondary)
		}
	}
}
