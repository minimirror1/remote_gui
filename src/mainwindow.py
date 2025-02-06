# mainwindow.py

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt  # Qt 플래그를 사용하기 위해 추가

from src.ui.mainwindow_ui import Ui_MainWindow  # Designer에서 uic로 생성된 UI 클래스
from src.home_page import HomePage  # HomePage UI 클래스 import 추가
from src.setting_page import SettingPage  # SettingPage UI 클래스 import 추가

import _icons_rc  # 수정된 import 경로
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import logging
from PySide6.QtCore import QThread
from src.serial_manager import SerialManager
from PySide6.QtCore import QTimer


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 프레임리스 윈도우 설정
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 윈도우 배경을 투명하게 설정
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # UI 클래스 인스턴스를 생성하고 현재 윈도우에 설정합니다.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # SerialManager 인스턴스 가져오기
        self.serial_manager = SerialManager.get_instance()
        self.serial_manager.set_main_window(self)  # MainWindow 참조 설정
        
        # 스레드 초기화
        self.serial_thread = SerialReaderThread()
        self.serial_thread.start()

        # 마우스 드래그를 위한 변수 초기화
        self._drag_pos = None

        # LED 타이머 초기화
        self.tx_timer = QTimer(self)
        self.rx_timer = QTimer(self)
        self.tx_timer.timeout.connect(self.turn_off_tx)
        self.rx_timer.timeout.connect(self.turn_off_rx)
        
        # LED 스타일시트
        self.LED_TX_ON_STYLE = """
            background-color: #ff0000;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        self.LED_RX_ON_STYLE = """
            background-color: #00ff00;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        self.LED_OFF_STYLE = """
            background-color: #808080;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        # 초기 LED 상태 설정
        self.init_ui()

    def init_ui(self):
        """
        UI 초기화 작업을 수행하는 함수입니다.
        예를 들어, 위젯 속성 설정, 시그널-슬롯 연결 등의 작업을 여기에 추가합니다.
        """
        # HomePage UI 초기화 - addWidget 방식으로 변경
        self.home_page = HomePage()
        self.ui.mainPage.addWidget(self.home_page)
        
        # SettingPage UI 초기화
        self.setting_page = SettingPage()
        self.ui.mainPage.addWidget(self.setting_page)

        # 창 제어 버튼 시그널 연결
        if hasattr(self.ui, 'closeBtn'):
            self.ui.closeBtn.clicked.connect(self.close)
        
        if hasattr(self.ui, 'minimizeBtn'):
            self.ui.minimizeBtn.clicked.connect(self.showMinimized)
        
        if hasattr(self.ui, 'restoreBtn'):
            self.ui.restoreBtn.clicked.connect(self.toggle_maximize_restore)
            
        # 페이지 전환 버튼 시그널 연결        
        self.ui.HomeButton.clicked.connect(lambda: self.change_page(0))  # HomePage
        self.ui.PlayButton.clicked.connect(lambda: self.change_page(0))  # PlayPage
        self.ui.jogButton.clicked.connect(lambda: self.change_page(0))   # JogPage
        self.ui.SettingButton.clicked.connect(lambda: self.change_page(1))  # SettingPage

        # 마우스 이벤트 추적을 위해 위젯들의 mouseTracking 활성화
        self.ui.centralwidget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.ui.headerContainer.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # LED 초기 스타일 설정
        self.ui.labelTx.setStyleSheet(self.LED_OFF_STYLE)
        self.ui.labelRx.setStyleSheet(self.LED_OFF_STYLE)

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

    def closeEvent(self, event):
        """프로그램 종료 시 정리 작업"""
        self.serial_manager.stop_serial_thread()
        super().closeEvent(event)

    def __del__(self):
        """소멸자"""
        try:
            if hasattr(self, 'serial_thread'):
                self.serial_thread.stop()
                self.serial_thread.wait()
        except Exception as e:
            self.logger.error(f"객체 삭제 중 에러 발생: {str(e)}")

    def indicate_tx(self):
        """TX LED를 켜고 타이머 시작"""
        self.ui.labelTx.setStyleSheet(self.LED_TX_ON_STYLE)
        self.tx_timer.start(100)  # 100ms 후 LED 끄기

    def indicate_rx(self):
        """RX LED를 켜고 타이머 시작"""
        self.ui.labelRx.setStyleSheet(self.LED_RX_ON_STYLE)
        self.rx_timer.start(100)  # 100ms 후 LED 끄기

    def turn_off_tx(self):
        """TX LED 끄기"""
        self.ui.labelTx.setStyleSheet(self.LED_OFF_STYLE)
        self.tx_timer.stop()

    def turn_off_rx(self):
        """RX LED 끄기"""
        self.ui.labelRx.setStyleSheet(self.LED_OFF_STYLE)
        self.rx_timer.stop()


class SerialReaderThread(QThread):
    def __init__(self):
        super().__init__()
        self._is_running = True
        
    def run(self):
        while self._is_running:
            # 시리얼 읽기 작업
            pass
            
    def stop(self):
        self._is_running = False
