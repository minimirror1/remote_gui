from PySide6.QtWidgets import QWidget
from src.ui.help_page_ui import Ui_HelpPage


class HelpPage(QWidget, Ui_HelpPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
