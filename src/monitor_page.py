from PySide6.QtWidgets import (QWidget, QMessageBox, QFrame, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QProgressBar)
from PySide6.QtCore import Slot, QTimer, Signal, QDateTime
from PySide6.QtGui import QFont, QPixmap

from src.ui.monitor_page_ui import Ui_Form
from src.serial_manager import SerialManager
from src.widgets.serial_commands import SerialCommands
import _icons_rc


class DeviceInfoWidget(QFrame):
    """개별 장치 정보를 표시하는 위젯"""
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        
        # 폰트 크기 설정
        self.name_font_size = 12  # 장치 이름 전용 폰트 크기
        self.default_font_size = 10  # 모든 다른 라벨의 폰트 크기
        
        # LED 이미지 로드
        self.led_on = QPixmap(u":/font_awesome_solid/icons/user/status_led_g.png")
        self.led_off = QPixmap(u":/font_awesome_solid/icons/user/status_led_r.png")
        
        self.setupUI()
        
    def setupUI(self):
        """장치 정보 위젯 UI 설정"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: white;
                margin: 2px;
                padding: 5px;
            }
            QFrame:hover {
                border-color: #007ACC;
                background-color: #f0f8ff;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 5, 8, 5)
        main_layout.setSpacing(8)
        
        # 왼쪽: 장치 기본 정보
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 장치 이름
        name_label = QLabel(f"Device: {self.device_info.get('name', 'Unknown')}")
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(self.name_font_size)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #333; margin-bottom: 2px;")
        
        # 장치 ID
        id_label = QLabel(f"ID: {self.device_info.get('id', 'N/A')}")
        id_label.setStyleSheet(f"color: #666; font-size: {self.default_font_size}px;")
        
        # 모션 상태
        self.motion_status_label = QLabel("Motion: STOP")
        self.motion_status_label.setStyleSheet(f"color: #666; font-size: {self.default_font_size}px;")
        
        # 전원 상태
        power_layout = QHBoxLayout()
        power_layout.setSpacing(3)
        self.power_indicator = QLabel()
        self.power_indicator.setFixedSize(50, 50)  # LED 크기를 12x12 픽셀로 고정
        self.power_indicator.setScaledContents(True)  # 이미지를 라벨 크기에 맞게 스케일링
        self.power_indicator.setPixmap(self.led_off)
        power_text = QLabel("Main Power")
        power_text.setStyleSheet(f"color: #666; font-size: {self.default_font_size}px;")
        power_layout.addWidget(self.power_indicator)
        power_layout.addWidget(power_text)
        power_layout.addStretch()
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(id_label)
        info_layout.addWidget(self.motion_status_label)
        info_layout.addLayout(power_layout)
        
        # 가운데: 상세 정보
        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(1)
        
        # 연속구동시간
        self.runtime_label = QLabel("Runtime: 00h00m00s")
        self.runtime_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        # 회차 정보
        self.round_label = QLabel("Round: 0/0")
        self.round_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        # 전력 정보
        self.energy_label = QLabel("Power: 0.0V / 0.0A / 0.0W")
        self.energy_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        # 에러 정보
        self.error_label = QLabel("Error: 정상")
        self.error_label.setStyleSheet(f"color: green; font-size: {self.default_font_size}px;")
        
        detail_layout.addWidget(self.runtime_label)
        detail_layout.addWidget(self.round_label)
        detail_layout.addWidget(self.energy_label)
        detail_layout.addWidget(self.error_label)
        detail_layout.addStretch()
        
        # 오른쪽: 모션 시간 정보
        motion_layout = QVBoxLayout()
        motion_layout.setSpacing(1)
        
        # 모션 시간 정보
        self.motion_time_label = QLabel("Time: 00:00:000 / 00:00:000")
        self.motion_time_label.setStyleSheet(f"color: #333; font-size: {self.default_font_size}px;")
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 1px;
            }
        """)
        
        # 마지막 업데이트 시간
        self.last_update_label = QLabel("Last Update: Never")
        self.last_update_label.setStyleSheet(f"color: #888; font-size: {self.default_font_size}px;")
        
        motion_layout.addWidget(self.motion_time_label)
        motion_layout.addWidget(self.progress_bar)
        motion_layout.addWidget(self.last_update_label)
        motion_layout.addStretch()
        
        main_layout.addLayout(info_layout, 3)
        main_layout.addLayout(detail_layout, 3)
        main_layout.addLayout(motion_layout, 2)
        
    def _format_time_ms(self, time_ms):
        """밀리초 값을 mm:ss:zzz 형식으로 변환"""
        minutes = time_ms // 60000
        seconds = (time_ms % 60000) // 1000
        ms = time_ms % 1000
        return f"{minutes:02d}:{seconds:02d}:{ms:03d}"
        
    def update_status(self, status_data):
        """장치 상태 업데이트 - home_page.py의 update_status_info와 동일한 데이터 구조 사용"""
        if not status_data:
            return
            
        # 메인 전원 상태 업데이트
        if 'main_power' in status_data:
            main_power_status = status_data['main_power']['status']
            self.power_indicator.setPixmap(self.led_on if main_power_status else self.led_off)
        
        # 모션 재생 상태 업데이트
        if 'motion' in status_data:
            motion_info = status_data['motion']
            motion_status = motion_info.get('status', 'UNKNOWN')
            self.motion_status_label.setText(f"Motion: {motion_status}")
            
            # 모션 시간 정보 업데이트
            current_time = motion_info.get('current', 0)  # ms 단위
            end_time = motion_info.get('end', 0)  # ms 단위
            
            self.motion_time_label.setText(f"Time: {self._format_time_ms(current_time)} / {self._format_time_ms(end_time)}")
            
            # 진행률 업데이트
            if end_time > 0:
                progress = (current_time / end_time) * 100
                self.progress_bar.setValue(int(progress))
            else:
                self.progress_bar.setValue(0)
        
        # 연속구동시간 업데이트
        if 'time' in status_data:
            time_info = status_data['time']
            runtime_text = f"Runtime: {time_info['hours']:02d}h{time_info['minutes']:02d}m{time_info['seconds']:02d}s"
            self.runtime_label.setText(runtime_text)
        
        # 회차 정보 업데이트
        if 'count' in status_data:
            count_info = status_data['count']
            round_text = f"Round: {count_info['current']}/{count_info['total']}"
            self.round_label.setText(round_text)
        
        # 전력 정보 업데이트
        if 'power' in status_data:
            power_info = status_data['power']
            voltage = power_info['voltage'] / 100.0  # 전압값이 100배로 전송된다고 가정
            current = power_info['current'] / 100.0  # 전류값이 100배로 전송된다고 가정
            power = voltage * current  # 전력 계산
            
            energy_text = f"Power: {voltage:.1f}V / {current:.1f}A / {power:.1f}W"
            self.energy_label.setText(energy_text)
        
        # 에러 정보 업데이트
        if 'error' in status_data:
            error_info = status_data['error']
            error_flag = error_info['flag']
            
            if error_flag:
                # 에러가 있는 경우
                can_id = error_info['can_id']
                can_sub_id = error_info['can_sub_id']
                error_code = error_info['code']
                self.error_label.setText(f"Error: {can_id}-{can_sub_id} ({error_code})")
                self.error_label.setStyleSheet(f"color: red; font-size: {self.default_font_size}px; font-weight: bold;")
            else:
                # 에러가 없는 경우
                self.error_label.setText("Error: 정상")
                self.error_label.setStyleSheet(f"color: green; font-size: {self.default_font_size}px;")
        
        # 마지막 업데이트 시간
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.last_update_label.setText(f"Last Update: {current_time}")


class MonitorPage(QWidget, Ui_Form):
    # 커스텀 시그널
    device_status_updated = Signal(str, dict)  # device_id, status_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        print("MonitorPage 초기화")
        
        # SerialCommands 인스턴스 가져오기 (home_page.py와 동일)
        self.serial_commands = SerialCommands.get_instance()
        self.serial_manager = self.serial_commands.serial_manager
        
        # 모니터링 관련 변수 초기화
        self.is_monitoring = False
        self.device_widgets = {}  # device_id -> DeviceInfoWidget 매핑
        self.monitored_devices = []  # 모니터링할 장치 목록
        
        # 상태 데이터 저장 (각 장치별)
        self.device_status_data = {}  # device_id -> status_data
        
        # 시그널 연결 상태 추적
        self._status_signals_connected = False
        self._current_protocol = None
        
        # 폴링 타이머 설정 (실제로는 프로토콜 시그널을 사용)
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.request_status_update)
        self.status_update_interval = 1000  # 1초마다 상태 요청
        
        # UI 초기 설정
        self._setup_initial_ui()
        
        # 시그널 연결
        self.refreshButton.clicked.connect(self.on_refresh_clicked)
        self.serial_manager.connection_changed.connect(self._update_connection_status)
        self.serial_manager.error_occurred.connect(self._show_error)
        
        # 연결 상태 초기화 및 프로토콜 시그널 연결
        if self.serial_manager.is_port_connected():
            self.connect_protocol_signals()
        self._update_connection_status(self.serial_manager.is_port_connected())

    def _setup_initial_ui(self):
        """초기 UI 설정"""
        self.refreshButton.setEnabled(False)
        self.update_device_count(0)
        
    def __del__(self):
        """소멸자: 사용한 자원 정리"""
        self.cleanup()
        
    def cleanup(self):
        """자원 정리 함수"""
        # 모니터링 중지
        if self.is_monitoring:
            self.stop_monitoring()
            
        # 타이머 정지
        if hasattr(self, 'status_update_timer') and self.status_update_timer:
            self.status_update_timer.stop()
            
        # 프로토콜 시그널 연결 해제
        self.disconnect_protocol_signals()
            
        # SerialManager 연결 해제
        if hasattr(self, 'serial_manager') and self.serial_manager:
            try:
                self.serial_manager.connection_changed.disconnect(self._update_connection_status)
                self.serial_manager.error_occurred.disconnect(self._show_error)
            except Exception as e:
                print(f"시그널 연결 해제 실패: {e}")
                
    def connect_protocol_signals(self):
        """프로토콜 시그널 연결 (home_page.py와 동일)"""
        protocol = self.serial_commands.serial_manager.get_protocol()
        if protocol:
            # 현재 protocol이 다르다면 이전 연결 해제
            if self._current_protocol is not protocol:
                self.disconnect_protocol_signals()
            
            # 새로운 연결 설정
            if not self._status_signals_connected:
                protocol.status_sync_changed.connect(self.on_status_sync_changed)
                self._status_signals_connected = True
                self._current_protocol = protocol
                print("MonitorPage: 프로토콜 시그널 연결됨")
                
    def disconnect_protocol_signals(self):
        """프로토콜 시그널 연결 해제"""
        if self._status_signals_connected and self._current_protocol:
            try:
                self._current_protocol.status_sync_changed.disconnect(self.on_status_sync_changed)
                print("MonitorPage: 프로토콜 시그널 연결 해제됨")
            except:
                pass
            self._status_signals_connected = False
            self._current_protocol = None

    def on_connection_changed(self, is_connected: bool):
        """시리얼 연결 상태가 변경될 때 호출 (home_page.py와 동일)"""
        if is_connected:
            self.connect_protocol_signals()
        else:
            self.disconnect_protocol_signals()
            
    @Slot()
    def on_refresh_clicked(self):
        """새로고침 버튼 클릭 처리"""
        if not self.serial_manager.is_port_connected():
            QMessageBox.warning(self, "경고", "시리얼 포트에 연결되어 있지 않습니다.")
            return
            
        # 장치가 없으면 기본 장치 생성 시도
        if not self.monitored_devices:
            self._create_default_device()
            
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
            
    @Slot(dict)
    def on_status_sync_changed(self, status_data: dict):
        """상태 동기화 시그널 처리 - 장치 ID별로 데이터 분리 처리"""
        # 상태 데이터에서 장치 ID 추출
        device_id = status_data.get('device_id')
        
        if device_id is not None:
            # ID가 있는 경우: 해당 장치의 상태 데이터로 업데이트
            self.device_status_data[device_id] = status_data
            
            # 해당 장치 위젯 업데이트
            if device_id in self.device_widgets:
                self.device_widgets[device_id].update_status(status_data)
            
            # 시그널 발생
            self.device_status_updated.emit(str(device_id), status_data)
            print(f"장치 ID {device_id} 상태 업데이트")
            
        else:
            # ID가 없는 경우: 기존 방식으로 첫 번째 장치에 적용 (하위 호환성)
            if self.monitored_devices:
                device = self.monitored_devices[0]
                fallback_device_id = device.get('id', device.get('port', 'unknown'))
                
                # status_data에 device_id 추가
                status_data['device_id'] = fallback_device_id
                self.device_status_data[fallback_device_id] = status_data
                
                # UI 업데이트
                if fallback_device_id in self.device_widgets:
                    self.device_widgets[fallback_device_id].update_status(status_data)
                    
                # 시그널 발생
                self.device_status_updated.emit(str(fallback_device_id), status_data)
                print(f"장치 ID 없음 - 기본 장치 {fallback_device_id}에 적용")

    def set_monitored_devices(self, devices):
        """모니터링할 장치 목록 설정 (setting_page에서 호출)"""
        self.monitored_devices = devices
        self.clear_device_widgets()
        
        # 각 장치에 대한 위젯 생성
        for device in devices:
            self.add_device_widget(device)
            
        self.update_device_count(len(devices))
        print(f"모니터링 장치 설정: {len(devices)}개")
        
    def set_scanned_devices(self, scanned_device_ids):
        """Setting 페이지에서 스캔된 장치 ID 목록을 받아서 모니터링 장치로 설정"""
        devices = []
        
        for device_id in scanned_device_ids:
            device_info = {
                'id': device_id,  # 스캔된 실제 장치 ID (숫자)
                'name': f"Robot Device {device_id}",
                'port': self.serial_manager.get_current_port() if self.serial_manager.is_port_connected() else 'N/A',
                'type': 'robot',
                'status': 'scanned'
            }
            devices.append(device_info)
            
        self.set_monitored_devices(devices)
        print(f"스캔된 장치 설정: {scanned_device_ids}")

    def add_device_widget(self, device_info):
        """장치 위젯을 동적으로 추가"""
        device_id = device_info.get('id', device_info.get('port', 'unknown'))
        
        # 기존 위젯이 있으면 제거
        if device_id in self.device_widgets:
            self.remove_device_widget(device_id)
            
        # 새 위젯 생성
        device_widget = DeviceInfoWidget(device_info)
        self.device_widgets[device_id] = device_widget
        
        # deviceLayout에 추가 (spacer 앞에 삽입)
        insert_index = self.deviceLayout.count() - 1
        self.deviceLayout.insertWidget(insert_index, device_widget)
        
        print(f"장치 위젯 추가: {device_id}")

    def remove_device_widget(self, device_id):
        """장치 위젯 제거"""
        if device_id in self.device_widgets:
            widget = self.device_widgets[device_id]
            self.deviceLayout.removeWidget(widget)
            widget.deleteLater()
            del self.device_widgets[device_id]
            print(f"장치 위젯 제거: {device_id}")

    def clear_device_widgets(self):
        """모든 장치 위젯 제거"""
        for device_id in list(self.device_widgets.keys()):
            self.remove_device_widget(device_id)
            
    def _create_default_device(self):
        """현재 연결된 시리얼 포트를 기반으로 기본 장치 생성"""
        if not self.serial_manager.is_port_connected():
            return
            
        # 현재 연결된 포트 정보 가져오기
        current_port = self.serial_manager.get_current_port()
        if current_port:
            # 포트 번호에서 숫자 추출 (예: COM3 -> 3)
            try:
                port_number = int(current_port.replace('COM', ''))
            except:
                port_number = 1  # 기본값
                
            device_info = {
                'id': port_number,  # 숫자 ID 사용
                'name': f"Robot Device",
                'port': current_port,
                'type': 'robot',
                'status': 'connected'
            }
            
            print(f"기본 장치 생성: {device_info}")
            self.set_monitored_devices([device_info])
        else:
            print("연결된 포트 정보를 찾을 수 없습니다.")

    def update_device_count(self, count):
        """연결된 장치 수 업데이트"""
        self.statusLabel.setText(f"Connected Devices: {count}")

    def start_monitoring(self):
        """모니터링 시작"""
        # 장치가 없으면 현재 연결된 시리얼 포트를 기반으로 생성
        if not self.monitored_devices:
            self._create_default_device()
            
        if not self.monitored_devices:
            QMessageBox.information(self, "정보", "모니터링할 장치가 없습니다.\n시리얼 포트가 연결되어 있는지 확인해주세요.")
            return
            
        print("장치 모니터링 시작")
        self.is_monitoring = True
        self.refreshButton.setText("모니터링 중지")
        
        # 상태 업데이트 타이머 시작 (실제로는 프로토콜 시그널을 주로 사용)
        self.status_update_timer.start(self.status_update_interval)
        
    def stop_monitoring(self):
        """모니터링 중지"""
        print("장치 모니터링 중지")
        self.is_monitoring = False
        self.refreshButton.setText("Refresh")
        
        # 상태 업데이트 타이머 중지
        self.status_update_timer.stop()

    @Slot()
    def request_status_update(self):
        """상태 업데이트 요청 (필요시)"""
        if not self.is_monitoring or not self.serial_manager.is_port_connected():
            return
            
        # 실제로는 프로토콜 시그널로 상태가 들어오므로, 여기서는 별도 요청하지 않음
        # 필요시 serial_commands를 통해 상태 조회 명령을 보낼 수 있음
        pass

    def get_device_status(self, device):
        """개별 장치의 상태를 확인 - 실제 저장된 상태 데이터 반환"""
        device_id = device.get('id', device.get('port', 'unknown'))
        
        # 저장된 상태 데이터가 있으면 반환
        if device_id in self.device_status_data:
            return self.device_status_data[device_id]
        
        # 없으면 기본값 반환 (연결되지 않은 상태) - 장치 ID 포함
        return {
            'device_id': device_id,
            'main_power': {'status': False},
            'motion': {'status': 'UNKNOWN', 'current': 0, 'end': 0},
            'time': {'hours': 0, 'minutes': 0, 'seconds': 0},
            'count': {'current': 0, 'total': 0},
            'power': {'voltage': 0, 'current': 0},
            'error': {'flag': False, 'can_id': 0, 'can_sub_id': 0, 'code': 0}
        }

    @Slot(bool)
    def _update_connection_status(self, is_connected: bool):
        """연결 상태에 따라 UI 업데이트"""
        self.refreshButton.setEnabled(is_connected)
        
        if not is_connected and self.is_monitoring:
            self.stop_monitoring()
        else:
            # 연결되면 프로토콜 시그널 연결
            self.on_connection_changed(is_connected)
            
        print(f"MonitorPage - 연결 상태: {is_connected}")
    
    @Slot(str)
    def _show_error(self, error_message: str):
        """에러 메시지 표시"""
        QMessageBox.critical(self, "에러", error_message)

    def showEvent(self, event):
        """페이지가 표시될 때 호출"""
        super().showEvent(event)
        # UI 상태 업데이트
        is_connected = self.serial_manager.is_port_connected()
        self.refreshButton.setEnabled(is_connected)
        
        # 메인 윈도우에서 스캔된 장치 가져오기 시도
        if is_connected and not self.monitored_devices:
            # 메인 윈도우를 통해 스캔된 장치 목록 가져오기
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'transfer_scanned_devices_to_monitor'):
                main_window = main_window.parent()
                
            if main_window and hasattr(main_window, 'transfer_scanned_devices_to_monitor'):
                # 스캔된 장치가 있으면 가져오고, 없으면 기본 장치 생성
                if not main_window.transfer_scanned_devices_to_monitor():
                    self._create_default_device()
            else:
                # 메인 윈도우를 찾을 수 없으면 기본 장치 생성
                self._create_default_device()
            
        # 장치가 있고 모니터링이 중지된 상태면 자동으로 모니터링 시작
        if is_connected and self.monitored_devices and not self.is_monitoring:
            print("자동으로 모니터링 시작")
            self.start_monitoring()
            
        print("MonitorPage 표시됨")
        
    def hideEvent(self, event):
        """페이지가 숨겨질 때 호출"""
        super().hideEvent(event)
        # 페이지가 숨겨질 때 모니터링 중지
        if self.is_monitoring:
            self.stop_monitoring()
        print("MonitorPage 숨겨짐")
        
    def closeEvent(self, event):
        """위젯이 닫힐 때 호출"""
        self.cleanup()
        super().closeEvent(event)

    # 외부에서 호출할 수 있는 공개 메서드들
    def refresh_devices(self):
        """장치 목록 새로고침"""
        if self.is_monitoring:
            # 현재 모니터링 중이면 재시작
            self.stop_monitoring()
            self.start_monitoring()
        else:
            # 장치 위젯들의 상태만 업데이트
            for device in self.monitored_devices:
                device_id = device.get('id', device.get('port', 'unknown'))
                if device_id in self.device_widgets:
                    status_data = self.get_device_status(device)
                    self.device_widgets[device_id].update_status(status_data)

    def get_monitoring_status(self):
        """현재 모니터링 상태 반환"""
        connected_count = 0
        for device in self.monitored_devices:
            status_data = self.get_device_status(device)
            if status_data.get('main_power', {}).get('status', False):
                connected_count += 1
                
        return {
            'is_monitoring': self.is_monitoring,
            'device_count': len(self.monitored_devices),
            'connected_devices': connected_count,
            'serial_connected': self.serial_manager.is_port_connected()
        }
