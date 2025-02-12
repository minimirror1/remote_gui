from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtGui import QPixmap
from src.ui.home_page_ui import Ui_HomePage
from src.widgets.serial_commands import SerialCommands
import _icons_rc   
from PySide6.QtCore import QTimer, QDateTime


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
        
        # 전원 버튼 관련 변수 추가
        self._power_cooldown_timer = QTimer(self)
        self._power_cooldown_timer.setInterval(1000)  # 1초 간격
        self._power_cooldown_timer.timeout.connect(self._update_power_cooldown)
        self._power_cooldown_count = 0
        self._power_button_enabled = True
        
        # 재생 제어 관련 변수 추가
        self._play_control_timer = QTimer(self)
        self._play_control_timer.setInterval(3000)  # 3초 타임아웃
        self._play_control_timer.timeout.connect(self._handle_play_control_timeout)
        self._waiting_play_control_ack = False
        
        # 모션 시간 UI 업데이트를 위한 타이머 추가
        self._motion_update_timer = QTimer(self)
        self._motion_update_timer.setInterval(50)  # 50ms 간격으로 업데이트
        self._motion_update_timer.timeout.connect(self._update_motion_time_display)
        self._motion_update_timer.start()
        
        # 모션 시간 관련 변수 (모두 ms 단위)
        self._last_current_time = 0
        self._last_end_time = 0
        self._last_update_time = 0
        self._display_current_time = 0
        
        # 초기 설정
        self.setup_ui()
        
        # 시리얼 연결 상태 변경 시그널 연결
        self.serial_commands.serial_manager.connection_changed.connect(self.on_connection_changed)
        
        # 현재 연결된 상태라면 시그널 연결
        if self.serial_commands.serial_manager.is_port_connected():
            self.connect_protocol_signals()
        
        # 버튼 시그널 연결
        self.ui.playButton.clicked.connect(self.on_play_clicked)
        self.ui.pauseButton.clicked.connect(self.on_pause_clicked)
        self.ui.stopButton.clicked.connect(self.on_stop_clicked)
        
        # 프로토콜 시그널 연결
        if self.serial_commands.serial_manager.get_protocol():
            self.serial_commands.serial_manager.get_protocol().play_control_status_changed.connect(
                self.on_play_control_status_changed)
        
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
                self._current_protocol.status_sync_changed.disconnect(self.update_status_info)
                self._current_protocol.play_control_status_changed.disconnect(self.on_play_control_status_changed)
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
                protocol.status_sync_changed.connect(self.update_status_info)
                protocol.play_control_status_changed.connect(self.on_play_control_status_changed)
                self._power_status_connected = True
                self._current_protocol = protocol
        
    def on_main_power_clicked(self):
        """메인 전원 버튼 클릭 핸들러"""
        if not self._power_button_enabled:
            return  # 쿨다운 중이면 동작하지 않음
        
        success = self.serial_commands.send_main_power_control(self.ui.MainPowerButton.isChecked())
        
        if not success:
            # 실패 시 에러 메시지 표시 및 버튼 상태 되돌리기
            if not self.serial_commands.serial_manager.is_port_connected():
                QMessageBox.warning(self, "경고", "시리얼 포트가 연결되지 않았습니다.")
            else:
                QMessageBox.critical(self, "오류", "메인 전원 제어 실패")
            self.ui.MainPowerButton.setChecked(not self.ui.MainPowerButton.isChecked())
        else:
            # 성공 시 쿨다운 시작
            self._power_button_enabled = False
            self._power_cooldown_count = 3  # 3초 카운트다운
            self.ui.MainPowerButton.setEnabled(False)  # 버튼 비활성화
            self.ui.mainPowerCountDownLabel.setText(f"대기시간: {self._power_cooldown_count}초")
            self._power_cooldown_timer.start()
    
    def _update_power_cooldown(self):
        """전원 버튼 쿨다운 타이머 업데이트"""
        self._power_cooldown_count -= 1
        
        if self._power_cooldown_count <= 0:
            # 쿨다운 종료
            self._power_cooldown_timer.stop()
            self._power_button_enabled = True
            self.ui.MainPowerButton.setEnabled(True)
            self.ui.mainPowerCountDownLabel.setText("")
        else:
            # 카운트다운 표시 업데이트
            self.ui.mainPowerCountDownLabel.setText(f"대기시간: {self._power_cooldown_count}초")

    def update_power_status(self, is_on: bool):
        """전원 상태에 따라 LED 이미지 업데이트"""
        print(f"전원 상태 업데이트: {'켜짐' if is_on else '꺼짐'}")
        self.ui.MainPowerIndicator.setPixmap(self.led_on if is_on else self.led_off)
        # 버튼 상태 동기화 (쿨다운 중이 아닐 때만)
        if self._power_button_enabled:
            self.ui.MainPowerButton.setChecked(is_on)

    def _format_time_ms(self, time_ms):
        """밀리초 값을 mm:ss:zzz 형식으로 변환"""
        minutes = time_ms // 60000
        seconds = (time_ms % 60000) // 1000
        ms = time_ms % 1000
        return f"{minutes:02d}:{seconds:02d}:{ms:03d}"

    def _update_motion_time_display(self):
        """모션 시간 표시 업데이트"""
        if self._last_end_time > 0:
            # 경과 시간 계산 (ms 단위)
            elapsed = QDateTime.currentMSecsSinceEpoch() - self._last_update_time
            
            # 예상 현재 시간 계산 (ms 단위)
            self._display_current_time = min(self._last_current_time + elapsed, self._last_end_time)
            
            # UI 업데이트
            self.ui.motionCurrentTimeLabel.setText(self._format_time_ms(self._display_current_time))
            self.ui.motionEndTimeLabel.setText(self._format_time_ms(self._last_end_time))
            
            # 진행률 업데이트
            progress = (self._display_current_time / self._last_end_time) * 100
            self.ui.motionTimeHorizontalSlider.setValue(int(progress))

    def update_status_info(self, status_data: dict):
        """상태 정보 업데이트"""
        # 연속구동시간 업데이트 (00h00m00s 형식)
        time_info = status_data['time']
        runtime_text = f"{time_info['hours']:02d}h{time_info['minutes']:02d}m{time_info['seconds']:02d}s"
        self.ui.runTimeLabel.setText(runtime_text)
        
        # 회차 정보 업데이트 (0/0 형식)
        count_info = status_data['count']
        round_text = f"{count_info['current']}/{count_info['total']}"
        self.ui.roundLabel.setText(round_text)
        
        # 에너지 정보 업데이트 (000V / 000A / 000W 형식)
        power_info = status_data['power']
        voltage = power_info['voltage'] / 100.0  # 전압값이 100배로 전송된다고 가정
        current = power_info['current'] / 100.0  # 전류값이 100배로 전송된다고 가정
        power = voltage * current  # 전력 계산
        
        energy_text = f"{voltage:.1f}V / {current:.1f}A / {power:.1f}W"
        self.ui.energyLabel.setText(energy_text)
        
        # 모션 시간 정보 업데이트 (이미 ms 단위로 수신)
        motion_info = status_data.get('motion', {})
        current_time = motion_info.get('current', 0)  # ms 단위
        end_time = motion_info.get('end', 0)  # ms 단위
        
        # 새로운 시간 값 저장
        self._last_current_time = current_time
        self._last_end_time = end_time
        self._last_update_time = QDateTime.currentMSecsSinceEpoch()
        self._display_current_time = current_time
        
        # 레이블 즉시 업데이트
        self.ui.motionCurrentTimeLabel.setText(self._format_time_ms(current_time))
        self.ui.motionEndTimeLabel.setText(self._format_time_ms(end_time))
        
        # 슬라이더 업데이트
        if end_time > 0:
            progress = (current_time / end_time) * 100
            self.ui.motionTimeHorizontalSlider.setValue(int(progress))
        else:
            self.ui.motionTimeHorizontalSlider.setValue(0)

    def on_play_clicked(self):
        """재생 버튼 클릭 처리"""
        if self._waiting_play_control_ack:
            return
            
        play_state = 2 if self.ui.repeatButton.isChecked() else 1  # PLAY_REPEAT or PLAY_ONE
        success = self.serial_commands.send_play_control(play_state)
        
        if success:
            self._waiting_play_control_ack = True
            self._play_control_timer.start()
        else:
            if not self.serial_commands.serial_manager.is_port_connected():
                QMessageBox.warning(self, "경고", "시리얼 포트가 연결되지 않았습니다.")
            else:
                QMessageBox.critical(self, "오류", "재생 제어 명령 전송 실패")
    
    def on_pause_clicked(self):
        """일시정지 버튼 클릭 처리"""
        if self._waiting_play_control_ack:
            return
            
        success = self.serial_commands.send_play_control(3)  # PAUSE
        
        if success:
            self._waiting_play_control_ack = True
            self._play_control_timer.start()
        else:
            if not self.serial_commands.serial_manager.is_port_connected():
                QMessageBox.warning(self, "경고", "시리얼 포트가 연결되지 않았습니다.")
            else:
                QMessageBox.critical(self, "오류", "일시정지 명령 전송 실패")
    
    def on_stop_clicked(self):
        """정지 버튼 클릭 처리"""
        if self._waiting_play_control_ack:
            return
            
        success = self.serial_commands.send_play_control(4)  # STOP
        
        if success:
            self._waiting_play_control_ack = True
            self._play_control_timer.start()
        else:
            if not self.serial_commands.serial_manager.is_port_connected():
                QMessageBox.warning(self, "경고", "시리얼 포트가 연결되지 않았습니다.")
            else:
                QMessageBox.critical(self, "오류", "정지 명령 전송 실패")
    
    def on_play_control_status_changed(self, status: int):
        """재생 제어 상태 변경 처리"""
        self._play_control_timer.stop()
        self._waiting_play_control_ack = False
        
        # 상태에 따른 UI 업데이트
        self.ui.playButton.setEnabled(status != 1 and status != 2)  # 재생 중이 아닐 때만 활성화
        self.ui.pauseButton.setEnabled(status == 1 or status == 2)  # 재생 중일 때만 활성화
        self.ui.stopButton.setEnabled(status != 4)  # 정지 상태가 아닐 때만 활성화
        self.ui.repeatButton.setEnabled(True)
    
    def _handle_play_control_timeout(self):
        """재생 제어 응답 타임아웃 처리"""
        self._play_control_timer.stop()
        self._waiting_play_control_ack = False
        QMessageBox.warning(self, "경고", "재생 제어 응답 없음")
