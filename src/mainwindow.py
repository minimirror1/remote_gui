# mainwindow.py

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt  # Qt 플래그를 사용하기 위해 추가
from src.ui.mainwindow_ui import Ui_MainWindow  # Designer에서 uic로 생성된 UI 클래스
import _icons_rc  # 수정된 import 경로
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 프레임리스 윈도우 설정
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 윈도우 배경을 투명하게 설정
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # UI 클래스 인스턴스를 생성하고 현재 윈도우에 설정합니다.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 둥근 모서리를 위한 스타일시트 설정
        # self.ui.centralwidget.setStyleSheet("""
        #     QWidget#centralwidget {
        #         background-color: #ffffff;  /* 원하는 배경색으로 변경 가능 */
        #         border-radius: 10px;  /* 모서리의 둥근 정도 조절 가능 */
        #     }
        # """)

        # 마우스 드래그를 위한 변수 초기화
        self._drag_pos = None

        # 추가 UI 초기화 및 시그널-슬롯 연결 함수 호출
        self.init_ui()

    def init_ui(self):
        """
        UI 초기화 작업을 수행하는 함수입니다.
        예를 들어, 위젯 속성 설정, 시그널-슬롯 연결 등의 작업을 여기에 추가합니다.
        """
        # 창 제어 버튼 시그널 연결
        if hasattr(self.ui, 'closeBtn'):
            self.ui.closeBtn.clicked.connect(self.close)
        
        if hasattr(self.ui, 'minimizeBtn'):
            self.ui.minimizeBtn.clicked.connect(self.showMinimized)
        
        if hasattr(self.ui, 'restoreBtn'):
            self.ui.restoreBtn.clicked.connect(self.toggle_maximize_restore)
            
        # 페이지 전환 버튼 시그널 연결
        self.ui.HomeButton.clicked.connect(lambda: self.change_page(2))  # HomePage
        self.ui.PlayButton.clicked.connect(lambda: self.change_page(1))  # PlayPage
        self.ui.jogButton.clicked.connect(lambda: self.change_page(0))   # JogPage

        # 마우스 이벤트 추적을 위해 위젯들의 mouseTracking 활성화
        self.ui.centralwidget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.ui.headerContainer.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            # 복원 상태일 때 아이콘 변경이 필요한 경우
            # self.ui.restoreBtn.setIcon(QIcon(":/icons/maximize.png"))
        else:
            self.showMaximized()
            # 최대화 상태일 때 아이콘 변경이 필요한 경우
            # self.ui.restoreBtn.setIcon(QIcon(":/icons/restore.png"))

    def change_page(self, index):
        """
        스택 위젯의 페이지를 전환하는 메서드
        :param index: 전환할 페이지의 인덱스
        """
        self.ui.mainPage.setCurrentIndex(index)

    def on_pushButton_clicked(self):
        """
        pushButton 클릭 이벤트 핸들러 예시입니다.
        """
        print("PushButton이 클릭되었습니다.")

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton:
            # 마우스 Y 좌표가 0-30 픽셀 범위 내에 있을 때만 드래그 허용
            if event.pos().y() <= 30:
                self._drag_pos = event.globalPos() - self.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트"""
        self._drag_pos = None
        event.accept()
