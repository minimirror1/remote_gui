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
        self.sync_enable.toggled.connect(self._on_sync_enable_changed)
        self.sync_ms_spinBox.valueChanged.connect(self._on_sync_interval_changed)

        
        
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
        
        # sync_enable 버튼 활성화/비활성화 상태 업데이트
        self.sync_enable.setEnabled(is_connected)
        print(f"sync_enable 버튼 활성화 상태: {is_connected}")
        
        # 연결 상태에 따라 sync 설정 업데이트
        if is_connected:
            reader_thread = self.serial_manager.get_reader_thread()
            if reader_thread:
                reader_thread.set_sync_enabled(self.sync_enable.isChecked())
                reader_thread.set_sync_interval(self.sync_ms_spinBox.value())
        else:
            self.sync_enable.setChecked(False)
    
    @Slot(str)
    def _show_error(self, error_message: str):
        """에러 메시지 표시"""
        QMessageBox.critical(self, "에러", error_message)

    def _on_sync_enable_changed(self, enabled: bool):
        """Sync 활성화 상태가 변경되었을 때 호출"""
        print(f"Sync 상태 변경: {enabled}")  # 디버깅용 출력 추가
        
        if enabled and not self.serial_manager.is_port_connected():
            print("포트가 연결되지 않아 sync를 활성화할 수 없습니다.")
            self.sync_enable.setChecked(False)
            return
            
        reader_thread = self.serial_manager.get_reader_thread()
        if reader_thread:
            print(f"Reader thread sync 설정: {enabled}")
            reader_thread.set_sync_enabled(enabled)
        else:
            print("Reader thread not available")
    
    def _on_sync_interval_changed(self, value: int):
        """Sync 주기가 변경되었을 때 호출"""
        reader_thread = self.serial_manager.get_reader_thread()
        if reader_thread:
            reader_thread.set_sync_interval(value)
    
    def _on_connection_changed(self, is_connected: bool):
        """시리얼 연결 상태가 변경되었을 때 호출"""
        if not is_connected:
            self.sync_enable.setChecked(False)
    
    def showEvent(self, event):
        """페이지가 표시될 때 호출"""
        super().showEvent(event)
        # UI 상태 업데이트
        is_connected = self.serial_manager.is_port_connected()
        self.sync_enable.setEnabled(is_connected)
        
        # 연결된 상태에서만 이전 sync 상태를 복원
        if is_connected:
            reader_thread = self.serial_manager.get_reader_thread()
            if reader_thread:
                # 임시로 _sync_enabled 속성을 직접 사용
                self.sync_enable.setChecked(reader_thread._sync_enabled)
        
    def hideEvent(self, event):
        """페이지가 숨겨질 때 호출"""
        super().hideEvent(event)
        # 페이지가 숨겨질 때는 sync 상태를 유지합니다