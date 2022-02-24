from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow
from ui_form import Ui_MainWindow
from ytmusic_deleter import cli
from PyQt5.QtCore import pyqtSlot

import sys

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.removeLibraryButton.clicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        cli.remove_library()

if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow()
    window.show()
    sys.exit(appctxt.app.exec_())
