import argparse
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

import theme
from main_window import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--group")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # ── Apply global stylesheet ──
    app.setStyleSheet(theme.STYLESHEET)

    # ── Default application font ──
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    window = MainWindow()

    if args.export:
        if not args.group:
            print("Warning: --export used without --group. " "The scene may be very large.")
        window.load_documentation_wrapper(filter_group=args.group)
        window.export_scene_to_jpg("output.jpg", args.group)
        sys.exit(0)

    window.load_documentation_wrapper()
    window.show()
    sys.exit(app.exec())
