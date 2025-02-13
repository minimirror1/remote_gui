from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap
from src.ui.jog_page_ui import Ui_Form
from src.widgets.serial_commands import SerialCommands
import _icons_rc

class JogPage(QWidget):
    def __init__(self):
        super().__init__()
        
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
        self.ui.spinBox.setRange(0, 255)    # id
        self.ui.spinBox_2.setRange(0, 255)  # subid
        self.ui.spinBox_3.setRange(0, 255)  # value
        
        # 버튼 시그널 연결
        self.ui.cwButton.clicked.connect(self.on_ccw_clicked)    # CCW 버튼
        self.ui.ccwButton.clicked.connect(self.on_cw_clicked)   # CW 버튼
        
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
        id_value = self.ui.spinBox.value()
        subid_value = self.ui.spinBox_2.value()
        value = self.ui.spinBox_3.value()
        
        # CCW 명령 전송 (실제 구현은 SerialCommands에서 해당 메서드 추가 필요)
        self.serial_commands.send_jog_command(id_value, subid_value, value, direction="CCW")
    
    def on_cw_clicked(self):
        """CW 버튼 클릭 처리"""
        id_value = self.ui.spinBox.value()
        subid_value = self.ui.spinBox_2.value()
        value = self.ui.spinBox_3.value()
        
        # CW 명령 전송 (실제 구현은 SerialCommands에서 해당 메서드 추가 필요)
        self.serial_commands.send_jog_command(id_value, subid_value, value, direction="CW")
