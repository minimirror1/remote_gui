# mainwindow.py

from PySide6.QtWidgets import QMainWindow, QApplication
from src.ui.mainwindow_ui import Ui_MainWindow  # Designer에서 uic로 생성된 UI 클래스


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # UI 클래스 인스턴스를 생성하고 현재 윈도우에 설정합니다.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 추가 UI 초기화 및 시그널-슬롯 연결 함수 호출
        self.init_ui()

    def init_ui(self):
        """
        UI 초기화 작업을 수행하는 함수입니다.
        예를 들어, 위젯 속성 설정, 시그널-슬롯 연결 등의 작업을 여기에 추가합니다.
        """
        # 예시: pushButton 클릭 시 on_pushButton_clicked 메서드 호출
        # self.ui.pushButton.clicked.connect(self.on_pushButton_clicked)
        pass

    def on_pushButton_clicked(self):
        """
        pushButton 클릭 이벤트 핸들러 예시입니다.
        """
        print("PushButton이 클릭되었습니다.")
