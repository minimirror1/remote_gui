from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QMessageBox
from PySide6.QtCore import Slot

from src.ui.setting_page_ui import Ui_SettingPage
from src.serial_manager import SerialManager

# 기본 보우레이트 설정
SERIAL_BAUD_RATE = 115200


class SettingPage(QWidget, Ui_SettingPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        print("SettingPage 초기화")
        
        # 시리얼 포트 관련 변수 초기화
        self.port_buttons = []           # 동적으로 생성되는 라디오 버튼 목록
        
        # SerialManager 인스턴스 가져오기
        self.serial_manager = SerialManager.get_instance()
        
        # 시그널 연결
        self.SerialRefreshButton.clicked.connect(self.refresh_ports)
        self.SerialConnectButton.clicked.connect(self.on_port_selected)
        self.serial_manager.connection_changed.connect(self._update_connection_status)
        self.serial_manager.error_occurred.connect(self._show_error)
        
        self.refresh_ports()

    @Slot()
    def refresh_ports(self):
        """시리얼 포트 목록을 새로고침합니다."""
        print("포트 목록 새로고침 시작")
        
        # 기존 버튼 삭제
        for btn in self.port_buttons:
            btn.deleteLater()
        self.port_buttons.clear()
        
        # 레이아웃 초기화
        layout = self.scrollAreaWidgetContents.layout()
        if layout is None:
            layout = QVBoxLayout(self.scrollAreaWidgetContents)
            layout.setContentsMargins(0, 0, 0, 0)
            self.scrollAreaWidgetContents.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # 포트 목록 가져오기
        available_ports = self.serial_manager.get_available_ports()
        
        # 포트별 라디오 버튼 생성
        for port, description in available_ports:
            port_info = f"{port}"
            if description:
                port_info += f" - {description}"
            
            rb = QRadioButton(port_info)
            rb.setProperty("port_device", port)
            self.port_buttons.append(rb)
            layout.addWidget(rb)
        
        if not self.port_buttons:
            print("사용 가능한 시리얼 포트가 없습니다.")

    @Slot()
    def on_port_selected(self):
        """포트 연결/해제 버튼 클릭 처리"""
        if self.serial_manager.is_port_connected():
            self.serial_manager.disconnect_port()
            return
        
        # 선택된 포트 확인
        selected_port = None
        for rb in self.port_buttons:
            if rb.isChecked():
                selected_port = rb.property("port_device")
                break
        
        if selected_port:
            self.serial_manager.connect_to_port(selected_port)
    
    @Slot(bool)
    def _update_connection_status(self, is_connected: bool):
        """연결 상태에 따라 UI 업데이트"""
        self.SerialConnectButton.setText("해제" if is_connected else "연결")
    
    @Slot(str)
    def _show_error(self, error_message: str):
        """에러 메시지 표시"""
        QMessageBox.critical(self, "에러", error_message)