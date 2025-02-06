from PySide6.QtWidgets import QWidget
from src.ui.home_page_ui import Ui_HomePage

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        
        # UI 설정
        self.ui = Ui_HomePage()
        self.ui.setupUi(self)
        
        # 초기 설정
        self.setup_ui()
        
    def setup_ui(self):
        """UI 컴포넌트들의 추가적인 설정"""
        # frame_2 설정 (왼쪽 프레임)
        self.ui.frame_2.setMinimumWidth(200)
        
        # frame_3 설정 (오른쪽 프레임)
        self.ui.frame_3.setMinimumWidth(200)
        
        # frame 설정 (하단 프레임)
        self.ui.frame.setMinimumHeight(150)
