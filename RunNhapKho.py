from PyQt6.QtWidgets import QApplication, QMainWindow
from NhapKhoExt import NhapKho

import sys

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

w = QMainWindow()
f = NhapKho()
f.setupUi(w)
w.show()

sys.exit(app.exec())
