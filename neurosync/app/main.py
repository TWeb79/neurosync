"""
Main Application Entry Point
Author: Inventions4All - github:TWeb79
Version: 0.1.0 (2026-05-24)
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl


def main():
    """Run the NeuroSync application."""
    app = QApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.load(QUrl("neurosync/ui/qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    return app.exec()


if __name__ == "__main__":
    main()