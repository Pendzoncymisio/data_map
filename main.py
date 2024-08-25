import sys
import argparse

from PyQt6.QtWidgets import QApplication

from main_window import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--group')
    args = parser.parse_args()


    app = QApplication(sys.argv)
    window = MainWindow()

    

    window.load_documentation_wrapper()

    if args.export:
        if not args.group:
            print("Warning: The --export flag was used without the --group flag. The scene was exported to a JPG but might be very big")
        window.export_scene_to_jpg('output.jpg', args.group)  # Export the scene to a JPG image

        sys.exit(0)

    window.show()
    sys.exit(app.exec())

