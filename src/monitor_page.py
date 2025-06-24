from PySide6.QtWidgets import (QWidget, QMessageBox, QFrame, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QPushButton, QProgressBar)
from PySide6.QtCore import Slot, QTimer, Signal, QDateTime
from PySide6.QtGui import QFont, QPixmap

from src.ui.monitor_page_ui import Ui_Form
from src.serial_manager import SerialManager
from src.widgets.serial_commands import SerialCommands
from src.device_status_manager import DeviceStatusManager
import _icons_rc


class DeviceInfoWidget(QFrame):
    """개별 장치 정보를 표시하는 위젯"""
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        
        # 폰트 크기 설정
        self.name_font_size = 10  # 장치 이름 전용 폰트 크기
        self.default_font_size = 9  # 모든 다른 라벨의 폰트 크기
        
        # LED 이미지 로드
        self.led_on = QPixmap(u":/font_awesome_solid/icons/user/status_led_g.png")
        self.led_off = QPixmap(u":/font_awesome_solid/icons/user/status_led_r.png")
        
        self.setupUI()
        
    def setupUI(self):
        """장치 정보 위젯 UI 설정"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # 너비를 상위 요소의 절반 정도로 설정 (마진, 스페이싱 고려)
        # 상위 컨테이너 마진: 20px (좌우 각 10px)
        # 장치 간 스페이싱: 10px 
        # 따라서 실제 사용 가능한 너비의 절반에서 스페이싱/2를 뺀 값
        self.setMinimumWidth(350)  # 최소 너비 설정
        self.setMaximumWidth(450)  # 최대 너비 설정
        
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
        
        # 연속구동시간
        self.runtime_label = QLabel("Runtime: 00h00m00s")
        self.runtime_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        # 전력 정보
        self.energy_label = QLabel("Power: 0.0V / 0.0A / 0.0W")
        self.energy_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(id_label)
        info_layout.addLayout(power_layout)
        info_layout.addWidget(self.runtime_label)
        info_layout.addWidget(self.energy_label)
        
        # 가운데: 상세 정보
        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(1)
        
        # 모션 상태 (info_layout에서 이동)
        detail_layout.addWidget(self.motion_status_label)
        
        # 회차 정보
        self.round_label = QLabel("Round: 0/0")
        self.round_label.setStyleSheet(f"color: #555; font-size: {self.default_font_size}px;")
        
        # 에러 정보
        self.error_label = QLabel("Error: 정상")
        self.error_label.setStyleSheet(f"color: green; font-size: {self.default_font_size}px;")
        
        # 모션 시간 정보 (motion_layout에서 이동)
        self.motion_time_label = QLabel("Time: 00:00:000 / 00:00:000")
        self.motion_time_label.setStyleSheet(f"color: #333; font-size: {self.default_font_size}px;")
        
        # 진행률 바 (motion_layout에서 이동)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumHeight(10)
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
        
        # 마지막 업데이트 시간 (motion_layout에서 이동)
        self.last_update_label = QLabel("Last Update: Never")
        self.last_update_label.setStyleSheet(f"color: #888; font-size: {self.default_font_size}px;")
        
        detail_layout.addWidget(self.round_label)
        detail_layout.addWidget(self.error_label)
        detail_layout.addWidget(self.motion_time_label)
        detail_layout.addWidget(self.progress_bar)
        detail_layout.addWidget(self.last_update_label)
        detail_layout.addStretch()
        
        main_layout.addLayout(info_layout, 1)
        main_layout.addLayout(detail_layout, 2)
        
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
        
        # DeviceStatusManager 인스턴스 가져오기
        self.device_status_manager = DeviceStatusManager.get_instance()
        
        # 모니터링 관련 변수 초기화
        self.is_monitoring = False
        self.device_widgets = {}  # device_id -> DeviceInfoWidget 매핑
        self.monitored_devices = []  # 모니터링할 장치 목록
        self.device_rows = []  # 각 행의 HBoxLayout을 저장할 리스트
        self.current_row_widget_count = 0  # 현재 행의 위젯 개수
        
        # 상태 데이터 저장 (각 장치별) - 하위 호환성용
        self.device_status_data = {}  # device_id -> status_data
        
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
        
        # DeviceStatusManager 시그널 연결
        self.device_status_manager.device_status_updated.connect(self.on_device_status_updated)
        self.device_status_manager.device_connected.connect(self.on_device_connected)
        self.device_status_manager.device_disconnected.connect(self.on_device_disconnected)
        
        # GridLayout으로 2열 배치 설정
        self._setup_device_grid_layout()
        
        # 연결 상태 초기화 - DeviceStatusManager가 자동으로 프로토콜 시그널 처리
        self._update_connection_status(self.serial_manager.is_port_connected())
        
        print("MonitorPage: DeviceStatusManager를 통한 전역 상태 관리 활성화")

    def _setup_initial_ui(self):
        """초기 UI 설정"""
        self.refreshButton.setEnabled(False)
        self.update_device_count(0)
        
    def _setup_device_grid_layout(self):
        """장치 위젯을 2열로 배치하기 위한 준비 - 기존 VBoxLayout 유지"""
        # 기존 deviceLayout은 그대로 두고, 2열 배치를 위한 변수만 초기화
        self.device_rows = []  # 각 행의 HBoxLayout을 저장할 리스트
        self.current_row_widget_count = 0  # 현재 행의 위젯 개수
        print("2열 배치 준비 완료")
        
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
            
        # SerialManager 연결 해제
        if hasattr(self, 'serial_manager') and self.serial_manager:
            try:
                self.serial_manager.connection_changed.disconnect(self._update_connection_status)
                self.serial_manager.error_occurred.disconnect(self._show_error)
            except Exception as e:
                print(f"시그널 연결 해제 실패: {e}")
                
        # DeviceStatusManager 시그널 연결 해제
        if hasattr(self, 'device_status_manager') and self.device_status_manager:
            try:
                self.device_status_manager.device_status_updated.disconnect(self.on_device_status_updated)
                self.device_status_manager.device_connected.disconnect(self.on_device_connected)
                self.device_status_manager.device_disconnected.disconnect(self.on_device_disconnected)
            except Exception as e:
                print(f"DeviceStatusManager 시그널 연결 해제 실패: {e}")
                
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
            

    
    @Slot(str, dict)
    def on_device_status_updated(self, device_id: str, status_data: dict):
        """DeviceStatusManager에서 장치 상태 업데이트 알림을 받았을 때 처리"""
        # device_id를 int로 변환하여 기존 위젯과 매칭
        try:
            widget_key = int(device_id)
        except (ValueError, TypeError):
            widget_key = device_id
            
        # 해당 장치 위젯 업데이트
        if widget_key in self.device_widgets:
            self.device_widgets[widget_key].update_status(status_data)
            print(f"✓ 장치 ID {device_id} 위젯 업데이트 성공")
        else:
            print(f"✗ 장치 ID {device_id} 위젯을 찾을 수 없음")
            print(f"  등록된 위젯 키: {list(self.device_widgets.keys())}")
            
        # 기존 로컬 상태 데이터도 업데이트 (하위 호환성)
        self.device_status_data[widget_key] = status_data
        
        # 시그널 발생 (기존 호환성)
        self.device_status_updated.emit(device_id, status_data)
    
    @Slot(str)
    def on_device_connected(self, device_id: str):
        """장치 연결 시 호출"""
        print(f"장치 연결됨: {device_id}")
        # 필요시 UI 업데이트 로직 추가
        
    @Slot(str)
    def on_device_disconnected(self, device_id: str):
        """장치 연결 해제 시 호출"""
        print(f"장치 연결 해제됨: {device_id}")
        # 필요시 UI 업데이트 로직 추가

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
        
        print(f"스캔된 장치 ID 목록 수신: {scanned_device_ids} (타입: {[type(x) for x in scanned_device_ids]})")
        
        for device_id in scanned_device_ids:
            # device_id가 이미 int인지 확인하고, 아니면 변환
            try:
                device_id = int(device_id)
            except (ValueError, TypeError):
                print(f"device_id 타입 변환 실패 (set_scanned_devices): {device_id}")
                
            device_info = {
                'id': device_id,  # 스캔된 실제 장치 ID (숫자)
                'name': f"Robot Device {device_id}",
                'port': self.serial_manager.get_current_port() if self.serial_manager.is_port_connected() else 'N/A',
                'type': 'robot',
                'status': 'scanned'
            }
            devices.append(device_info)
            
        self.set_monitored_devices(devices)
        print(f"스캔된 장치 설정 완료: {[d['id'] for d in devices]}")

    def add_device_widget(self, device_info):
        """장치 위젯을 동적으로 추가 - HBoxLayout으로 2열 배치"""
        device_id = device_info.get('id', device_info.get('port', 'unknown'))
        
        # device_id를 int 타입으로 통일
        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            print(f"device_id 타입 변환 실패 (add_device_widget): {device_id}")
        
        print(f"장치 위젯 생성: device_id={device_id} (타입: {type(device_id)})")
        
        # 기존 위젯이 있으면 제거
        if device_id in self.device_widgets:
            self.remove_device_widget(device_id)
            
        # 새 위젯 생성
        device_widget = DeviceInfoWidget(device_info)
        self.device_widgets[device_id] = device_widget
        
        # 2열 배치를 위한 HBoxLayout 사용
        if self.current_row_widget_count == 0:
            # 새로운 행 생성
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(10)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # 첫 번째 위젯 추가
            row_layout.addWidget(device_widget)
            
            # 두 번째 자리 확보를 위한 스트레치 추가 (나중에 제거됨)
            row_layout.addStretch()
            
            # deviceLayout에 행 추가 (spacer 앞에)
            spacer_index = self.deviceLayout.count() - 1
            if spacer_index >= 0:
                self.deviceLayout.insertWidget(spacer_index, row_widget)
            else:
                self.deviceLayout.addWidget(row_widget)
            
            self.device_rows.append((row_widget, row_layout))
            self.current_row_widget_count = 1
            
        elif self.current_row_widget_count == 1:
            # 현재 행에 두 번째 위젯 추가
            if self.device_rows:
                row_widget, row_layout = self.device_rows[-1]
                
                # 기존 스트레치 제거
                if row_layout.count() > 1:
                    stretch_item = row_layout.takeAt(1)
                    if stretch_item:
                        del stretch_item
                
                # 두 번째 위젯 추가
                row_layout.addWidget(device_widget)
                self.current_row_widget_count = 2
        
        else:
            # 현재 행이 꽉 찬 경우, 새로운 행 시작
            self.current_row_widget_count = 0
            self.add_device_widget(device_info)  # 재귀 호출
            return
        
        print(f"장치 위젯 추가: {device_id} (행: {len(self.device_rows)}, 위치: {self.current_row_widget_count})")

    def remove_device_widget(self, device_id):
        """장치 위젯 제거 - 2열 배치에서 제거"""
        if device_id in self.device_widgets:
            widget = self.device_widgets[device_id]
            
            # 해당 위젯이 포함된 행 찾기
            for i, (row_widget, row_layout) in enumerate(self.device_rows):
                for j in range(row_layout.count()):
                    item = row_layout.itemAt(j)
                    if item and item.widget() == widget:
                        row_layout.removeWidget(widget)
                        widget.deleteLater()
                        del self.device_widgets[device_id]
                        
                        # 행이 비어있으면 행 전체 제거
                        widget_count_in_row = sum(1 for k in range(row_layout.count()) 
                                                if row_layout.itemAt(k) and row_layout.itemAt(k).widget())
                        
                        if widget_count_in_row == 0:
                            self.deviceLayout.removeWidget(row_widget)
                            row_widget.deleteLater()
                            self.device_rows.pop(i)
                            
                        # 카운트 업데이트
                        self.current_row_widget_count = max(0, self.current_row_widget_count - 1)
                        if self.current_row_widget_count == 0 and self.device_rows:
                            self.current_row_widget_count = 2  # 이전 행이 꽉 차있다고 가정
                            
                        print(f"장치 위젯 제거: {device_id}")
                        return
            
            print(f"장치 위젯 제거 실패 (찾을 수 없음): {device_id}")

    def clear_device_widgets(self):
        """모든 장치 위젯 제거"""
        # 모든 행 위젯 제거
        for row_widget, row_layout in self.device_rows:
            self.deviceLayout.removeWidget(row_widget)
            row_widget.deleteLater()
        
        # 장치 위젯 딕셔너리 초기화
        self.device_widgets.clear()
        
        # 행 관련 변수 초기화
        self.device_rows.clear()
        self.current_row_widget_count = 0
            
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
            
            print(f"기본 장치 생성: {device_info} (ID 타입: {type(port_number)})")
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
        """개별 장치의 상태를 확인 - DeviceStatusManager에서 최신 데이터 반환"""
        device_id = device.get('id', device.get('port', 'unknown'))
        
        # DeviceStatusManager에서 최신 상태 데이터 가져오기
        status_data = self.device_status_manager.get_device_status(str(device_id))
        
        if status_data:
            return status_data
        
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
            
        print(f"MonitorPage - 연결 상태: {is_connected} (DeviceStatusManager가 프로토콜 시그널 자동 관리)")
    
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
        """현재 모니터링 상태 반환 - DeviceStatusManager 활용"""
        # DeviceStatusManager에서 연결된 장치 개수 직접 가져오기
        connected_count = self.device_status_manager.get_connected_device_count()
        total_devices = self.device_status_manager.get_device_count()
        
        return {
            'is_monitoring': self.is_monitoring,
            'device_count': max(len(self.monitored_devices), total_devices),  # 더 큰 값 사용
            'connected_devices': connected_count,
            'serial_connected': self.serial_manager.is_port_connected(),
            'status_manager_devices': total_devices  # DeviceStatusManager의 장치 개수
        }
