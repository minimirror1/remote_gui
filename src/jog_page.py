from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap
from src.ui.jog_page_ui import Ui_Form
from src.widgets.serial_commands import SerialCommands
import _icons_rc
from PySide6.QtCore import Qt

class JogPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # 키보드 포커스 활성화
        self.setFocusPolicy(Qt.StrongFocus)
        
        # UI 설정
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # SerialCommands 인스턴스 가져오기
        self.serial_commands = SerialCommands.get_instance()
        
        # LED 이미지 로드
        self.sensor_led_main_on = QPixmap(u":/font_awesome_solid/icons/user/jog_sen_main_on.png")
        self.sensor_led_main_off = QPixmap(u":/font_awesome_solid/icons/user/jog_sen_main_off.png")
        self.sensor_led_sub_on = QPixmap(u":/font_awesome_solid/icons/user/jog_sen_sub_on.png")
        self.sensor_led_sub_off = QPixmap(u":/font_awesome_solid/icons/user/jog_sen_sub_off.png")
        #self.led_on = QPixmap(u":/font_awesome_solid/icons/user/status_led_g.png")
        #self.led_off = QPixmap(u":/font_awesome_solid/icons/user/status_led_r.png")
        
        # 현재 눌린 키 추적을 위한 변수
        self._pressed_key = None
        
        # 이전 동기화 상태 저장 변수
        self._previous_sync_state = True
        
        # 초기 설정
        self.setup_ui()
        
        # 시리얼 연결 상태 변경 시그널 연결
        self.serial_commands.serial_manager.connection_changed.connect(self.on_connection_changed)
        
    def setup_ui(self):
        """UI 컴포넌트들의 초기 설정"""
        # cw ccw 버튼
        self.ui.cwButton.setStyleSheet("""
            QPushButton {
                background: url(:/font_awesome_solid/icons/user/jog_cw_btn_off.png);
                background-repeat: no-repeat;
                background-position: center;                
            }

            QPushButton:pressed {
                background: url(:/font_awesome_solid/icons/user/jog_cw_btn_on.png);
                background-repeat: no-repeat;
                background-position: center;                
            }
        """)
        self.ui.ccwButton.setStyleSheet("""
            QPushButton {
                background: url(:/font_awesome_solid/icons/user/jog_ccw_btn_off.png);
                background-repeat: no-repeat;
                background-position: center;                
            }

            QPushButton:pressed {
                background: url(:/font_awesome_solid/icons/user/jog_ccw_btn_on.png);
                background-repeat: no-repeat;
                background-position: center;                
            }
        """)

        # LED 초기 상태 설정
        self.ui.sensor_main_led_ind.setPixmap(self.sensor_led_main_off)
        self.ui.sensor_sub_led_ind.setPixmap(self.sensor_led_sub_off)
        
        # SpinBox 범위 설정
        self.ui.idSpinBox.setRange(0, 255)    # id
        self.ui.subIdSpinBox.setRange(0, 255)  # subid
        self.ui.speedSpinBox.setRange(0, 255)  # speed
        
        # 버튼 시그널 연결
        self.ui.cwButton.clicked.connect(self.on_cw_clicked)    # CW 버튼
        self.ui.ccwButton.clicked.connect(self.on_ccw_clicked)   # CCW 버튼
        
    def on_connection_changed(self, is_connected: bool):
        """시리얼 연결 상태가 변경될 때 호출"""
        # 버튼 활성화/비활성화
        self.ui.cwButton.setEnabled(is_connected)
        self.ui.ccwButton.setEnabled(is_connected)
        
        # LED 상태 업데이트
        #self.ui.sensor_main_led_ind.setPixmap(self.led_on if is_connected else self.led_off)
        #self.ui.sensor_sub_led_ind.setPixmap(self.led_on if is_connected else self.led_off)
    
    def on_ccw_clicked(self):
        """CCW 버튼 클릭 처리"""
        id_value = self.ui.idSpinBox.value()
        subid_value = self.ui.subIdSpinBox.value()
        speed_value = self.ui.speedSpinBox.value()
        
        # CCW 명령 전송
        self.serial_commands.send_jog_move_cwccw(
            direction="CCW", 
            speed=speed_value,
            id_value=id_value,
            subid_value=subid_value
        )
    
    def on_cw_clicked(self):
        """CW 버튼 클릭 처리"""
        id_value = self.ui.idSpinBox.value()
        subid_value = self.ui.subIdSpinBox.value()
        speed_value = self.ui.speedSpinBox.value()
        
        # CW 명령 전송
        self.serial_commands.send_jog_move_cwccw(
            direction="CW", 
            speed=speed_value,
            id_value=id_value,
            subid_value=subid_value
        )

    def keyPressEvent(self, event):
        """키보드 키 누름 이벤트 처리"""
        # 이미 다른 키가 눌려있다면 무시
        if self._pressed_key is not None:
            event.accept()
            return
            
        if event.key() == Qt.Key_Left:
            self._pressed_key = Qt.Key_Left
            self.ui.ccwButton.setDown(True)
            self.on_ccw_clicked()
        elif event.key() == Qt.Key_Right:
            self._pressed_key = Qt.Key_Right
            self.ui.cwButton.setDown(True)
            self.on_cw_clicked()
        elif event.key() == Qt.Key_Up:
            current_value = self.ui.speedSpinBox.value()
            self.ui.speedSpinBox.setValue(min(current_value + 10, 255))
        elif event.key() == Qt.Key_Down:
            current_value = self.ui.speedSpinBox.value()
            self.ui.speedSpinBox.setValue(max(current_value - 10, 0))
        event.accept()

    def keyReleaseEvent(self, event):
        """키보드 키 뗌 이벤트 처리"""
        if event.key() == Qt.Key_Left and self._pressed_key == Qt.Key_Left:
            self.ui.ccwButton.setDown(False)
            self._pressed_key = None
        elif event.key() == Qt.Key_Right and self._pressed_key == Qt.Key_Right:
            self.ui.cwButton.setDown(False)
            self._pressed_key = None
        event.accept()
        
    def showEvent(self, event):
        """페이지가 표시될 때 호출됩니다."""
        super().showEvent(event)
        
        # 동기화 비활성화
        reader_thread = self.serial_commands.serial_manager.get_reader_thread()
        if reader_thread:
            # 이전 동기화 상태 저장
            self._previous_sync_state = reader_thread.is_sync_enabled()
            
            # 동기화 비활성화
            reader_thread.set_sync_enabled(False)
            print("조그 페이지 진입: 동기화 비활성화")
            
    def hideEvent(self, event):
        """페이지가 숨겨질 때 호출됩니다."""
        super().hideEvent(event)
        
        # 동기화 이전 상태로 복원
        reader_thread = self.serial_commands.serial_manager.get_reader_thread()
        if reader_thread:
            reader_thread.set_sync_enabled(self._previous_sync_state)
            if self._previous_sync_state:
                print("조그 페이지 종료: 동기화 활성화")
            else:
                print("조그 페이지 종료: 동기화 비활성화 유지")
