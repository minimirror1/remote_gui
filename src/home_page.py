from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtGui import QPixmap
from src.ui.home_page_ui import Ui_HomePage
from src.widgets.serial_commands import SerialCommands
import _icons_rc   


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        
        # UI 설정
        self.ui = Ui_HomePage()
        self.ui.setupUi(self)
        
        # SerialCommands 인스턴스 가져오기
        self.serial_commands = SerialCommands.get_instance()
        
        # 상태 LED 이미지 로드             
        self.led_on = QPixmap(u":/font_awesome_solid/icons/user/status_led_g.png")
        self.led_off = QPixmap(u":/font_awesome_solid/icons/user/status_led_r.png")
        
        # 시그널 연결 상태 추적
        self._power_status_connected = False
        self._current_protocol = None
        
        # 초기 설정
        self.setup_ui()
        
        # 시리얼 연결 상태 변경 시그널 연결
        self.serial_commands.serial_manager.connection_changed.connect(self.on_connection_changed)
        
        # 현재 연결된 상태라면 시그널 연결
        if self.serial_commands.serial_manager.is_port_connected():
            self.connect_protocol_signals()
        
    def setup_ui(self):
        """UI 컴포넌트들의 추가적인 설정"""
        # frame_2 설정 (왼쪽 프레임)
        self.ui.frame_2.setMinimumWidth(200)
        
        # frame_3 설정 (오른쪽 프레임)
        self.ui.frame_3.setMinimumWidth(200)
        
        # frame 설정 (하단 프레임)
        self.ui.frame.setMinimumHeight(150)
        
        # 메인 전원 버튼 설정
        self.ui.MainPowerButton.setCheckable(True)
        self.ui.MainPowerButton.clicked.connect(self.on_main_power_clicked)
        
        # 초기 LED 상태 설정
        self.ui.MainPowerIndicator.setPixmap(self.led_off)
        
    def on_connection_changed(self, is_connected: bool):
        """시리얼 연결 상태가 변경될 때 호출"""
        if is_connected:
            self.connect_protocol_signals()
        else:
            self.disconnect_protocol_signals()
        
    def disconnect_protocol_signals(self):
        """프로토콜 시그널 연결 해제"""
        if self._power_status_connected and self._current_protocol:
            try:
                self._current_protocol.main_power_status_changed.disconnect(self.update_power_status)
            except:
                pass
            self._power_status_connected = False
            self._current_protocol = None
        
    def connect_protocol_signals(self):
        """프로토콜 시그널 연결"""
        protocol = self.serial_commands.serial_manager.get_protocol()
        if protocol:
            # 현재 protocol이 다르다면 이전 연결 해제
            if self._current_protocol is not protocol:
                self.disconnect_protocol_signals()
            
            # 새로운 연결 설정
            if not self._power_status_connected:
                protocol.main_power_status_changed.connect(self.update_power_status)
                self._power_status_connected = True
                self._current_protocol = protocol
        
    def on_main_power_clicked(self):
        """메인 전원 버튼 클릭 핸들러"""
        success = self.serial_commands.send_main_power_control(self.ui.MainPowerButton.isChecked())
        
        if not success:
            # 실패 시 에러 메시지 표시 및 버튼 상태 되돌리기
            if not self.serial_commands.serial_manager.is_port_connected():
                QMessageBox.warning(self, "경고", "시리얼 포트가 연결되지 않았습니다.")
            else:
                QMessageBox.critical(self, "오류", "메인 전원 제어 실패")
            self.ui.MainPowerButton.setChecked(not self.ui.MainPowerButton.isChecked())
    
    def update_power_status(self, is_on: bool):
        """전원 상태에 따라 LED 이미지 업데이트"""
        print(f"전원 상태 업데이트: {'켜짐' if is_on else '꺼짐'}")  # 디버깅용
        self.ui.MainPowerIndicator.setPixmap(self.led_on if is_on else self.led_off)
        # 버튼 상태도 동기화
        self.ui.MainPowerButton.setChecked(is_on)
