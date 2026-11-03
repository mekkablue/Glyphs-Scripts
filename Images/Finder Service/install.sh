#!/bin/bash
# Installs the "Trim Image to Content" Quick Action for the current user (macOS only).
set -e
cd "$(dirname "$0")"
mkdir -p "$HOME/Library/Services"
rm -rf "$HOME/Library/Services/Trim Image to Content.workflow"
cp -R "Trim Image to Content.workflow" "$HOME/Library/Services/"
/System/Library/CoreServices/pbs -update 2>/dev/null || true
echo "Installed. In Finder: right-click an image > Quick Actions > Trim Image to Content."
echo "Requires Pillow: pip3 install Pillow"
