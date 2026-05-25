"""
Main Application Entry Point
Author: Inventions4All - github:TWeb79
Version: 2.0.2 (2026-05-25)
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


def main():
    """Run the NeuroSync desktop application with embedded web UI."""
    app = QApplication(sys.argv)

    view = QWebEngineView()
    html_path = os.path.join(os.path.dirname(__file__), "..", "..", "neurosync_ui.html")
    view.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
    view.setWindowTitle("NeuroSync v2.0.2")
    view.resize(1200, 800)
    view.show()

    return app.exec()


if __name__ == "__main__":
    main()