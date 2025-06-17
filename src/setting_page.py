from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QMessageBox
from PySide6.QtCore import Slot, QTimer

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
       
        # 장치 스캔 변수 초기화
        self.scan_timer = None
        self.current_scan_id = 0
        self.max_scan_id = 0
        self.scanning = False
        self.found_devices = []  # 발견된 장치 목록
        self.device_buttons = []  # 장치 라디오 버튼 목록
        
        # 전체 모니터링 모드 관련 변수 초기화
        self.all_monitor_timer = None
        self.current_device_index = 0
        self.is_all_monitor_mode = False
        
        # 초기에 버튼 비활성화
        self.ScanStartButton.setEnabled(False)
        self.SelectDeviceButton.setEnabled(False)
        self.ScanIdStartspinBox.setEnabled(False)
        self.ScanIdEndSpinBox.setEnabled(False)
        self.sync_enable.setEnabled(False)
        self.AllMonitorModeButton.setEnabled(False)
               
        # 시그널 연결
        self.SerialRefreshButton.clicked.connect(self.refresh_ports)
        self.SerialConnectButton.clicked.connect(self.on_port_selected)
        self.serial_manager.connection_changed.connect(self._update_connection_status)
        self.serial_manager.error_occurred.connect(self._show_error)
        self.sync_enable.toggled.connect(self._on_sync_enable_changed)
        self.sync_ms_spinBox.valueChanged.connect(self._on_sync_interval_changed)
        self.ScanStartButton.clicked.connect(self.on_scan_start)
        self.SelectDeviceButton.clicked.connect(self.on_device_selected)
        self.AllMonitorModeButton.clicked.connect(self.on_all_monitor_selected)

        # 프로토콜 연결 상태 초기화
        self.protocol = self.serial_manager.get_protocol()
        if self.protocol:
            # 초기화 시 속성 설정
            if not hasattr(self.protocol, 'id_scan_received_connected'):
                self.protocol.id_scan_received_connected = False
            if not hasattr(self.protocol, 'sync_success_connected'):
                self.protocol.sync_success_connected = False
            if not hasattr(self.protocol, 'sync_failed_connected'):
                self.protocol.sync_failed_connected = False
                
            # ID 스캔 시그널 연결
            self.protocol.id_scan_received.connect(self.on_id_scan_received)
            self.protocol.id_scan_received_connected = True
        
        self.refresh_ports()

    def __del__(self):
        """소멸자: 사용한 자원 정리"""
        self.cleanup()
        
    def cleanup(self):
        """자원 정리 함수"""
        # 스캔 타이머 정리
        if hasattr(self, 'scan_timer') and self.scan_timer:
            self.scan_timer.stop()
            
        # 연결 해제
        if hasattr(self, 'protocol') and self.protocol:
            # 각종 시그널 연결 해제
            if hasattr(self.protocol, 'id_scan_received_connected') and self.protocol.id_scan_received_connected:
                try:
                    self.protocol.id_scan_received.disconnect(self.on_id_scan_received)
                    self.protocol.id_scan_received_connected = False
                except Exception as e:
                    print(f"id_scan_received 연결 해제 실패: {e}")
                    
            if hasattr(self.protocol, 'sync_success_connected') and self.protocol.sync_success_connected:
                try:
                    self.protocol.sync_success.disconnect(self.on_sync_success)
                    self.protocol.sync_success_connected = False
                except Exception as e:
                    print(f"sync_success 연결 해제 실패: {e}")
                    
            if hasattr(self.protocol, 'sync_failed_connected') and self.protocol.sync_failed_connected:
                try:
                    self.protocol.sync_failed.disconnect(self.on_sync_failed)
                    self.protocol.sync_failed_connected = False
                except Exception as e:
                    print(f"sync_failed 연결 해제 실패: {e}")
                    
        # SerialManager 연결 해제
        if hasattr(self, 'serial_manager') and self.serial_manager:
            try:
                self.serial_manager.connection_changed.disconnect(self._update_connection_status)
            except Exception as e:
                print(f"connection_changed 연결 해제 실패: {e}")
                
            try:
                self.serial_manager.error_occurred.disconnect(self._show_error)
            except Exception as e:
                print(f"error_occurred 연결 해제 실패: {e}")

        self.stop_all_monitor_mode()

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
            if self.serial_manager.connect_to_port(selected_port):
                # 연결 성공 시 동기화 시작
                self.protocol = self.serial_manager.get_protocol()
                if self.protocol:
                    self.on_port_connected()

    @Slot(bool)
    def _update_connection_status(self, is_connected: bool):
        """연결 상태에 따라 UI 업데이트"""
        self.SerialConnectButton.setText("해제" if is_connected else "연결")
        
        # sync_enable 버튼 활성화/비활성화 상태 업데이트
        self.sync_enable.setEnabled(is_connected)
        
        # 스캔 및 장치 선택 버튼 활성화/비활성화
        self.ScanStartButton.setEnabled(is_connected)
        self.SelectDeviceButton.setEnabled(is_connected)
        self.ScanIdStartspinBox.setEnabled(is_connected)
        self.ScanIdEndSpinBox.setEnabled(is_connected)
        self.AllMonitorModeButton.setEnabled(is_connected)
        
        print(f"sync_enable 버튼 활성화 상태: {is_connected}")
        
        # 연결 상태에 따라 sync 설정 업데이트
        if is_connected:
            reader_thread = self.serial_manager.get_reader_thread()
            if reader_thread:
                reader_thread.set_sync_enabled(self.sync_enable.isChecked())
                reader_thread.set_sync_interval(self.sync_ms_spinBox.value())
        else:
            self.sync_enable.setChecked(False)
            # 연결 해제 시 동기화 정리
            if hasattr(self, 'protocol') and self.protocol:
                self.protocol.cleanup_sync()
                
                # 연결 상태 확인 후 해제
                if hasattr(self.protocol, 'sync_success_connected') and self.protocol.sync_success_connected:
                    try:
                        self.protocol.sync_success.disconnect(self.on_sync_success)
                        self.protocol.sync_success_connected = False
                    except Exception as e:
                        print(f"sync_success 연결 해제 실패: {e}")
                    
                if hasattr(self.protocol, 'sync_failed_connected') and self.protocol.sync_failed_connected:
                    try:
                        self.protocol.sync_failed.disconnect(self.on_sync_failed)
                        self.protocol.sync_failed_connected = False
                    except Exception as e:
                        print(f"sync_failed 연결 해제 실패: {e}")
                
                if hasattr(self.protocol, 'id_scan_received_connected') and self.protocol.id_scan_received_connected:
                    try:
                        self.protocol.id_scan_received.disconnect(self.on_id_scan_received)
                        self.protocol.id_scan_received_connected = False
                    except Exception as e:
                        print(f"id_scan_received 연결 해제 실패: {e}")
            
            # 스캔 중이면 중지
            if self.scanning:
                self.stop_scan()
                
            # 장치 목록 초기화
            self.clear_device_list()
    
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
                
            # ID 스캔 응답 시그널 연결 설정
            protocol = self.serial_manager.get_protocol()
            if protocol:
                # 초기화 시 속성 설정 확인
                if not hasattr(protocol, 'id_scan_received_connected'):
                    protocol.id_scan_received_connected = False
                
                # 이미 연결되어 있다면 연결 해제
                if protocol.id_scan_received_connected:
                    try:
                        protocol.id_scan_received.disconnect(self.on_id_scan_received)
                        protocol.id_scan_received_connected = False
                    except Exception as e:
                        print(f"id_scan_received 연결 해제 실패: {e}")
                
                # 새로 연결
                protocol.id_scan_received.connect(self.on_id_scan_received)
                protocol.id_scan_received_connected = True
        
    def hideEvent(self, event):
        """페이지가 숨겨질 때 호출"""
        super().hideEvent(event)
        # 페이지가 숨겨질 때는 sync 상태를 유지합니다
        
    def closeEvent(self, event):
        """위젯이 닫힐 때 호출"""
        self.cleanup()
        super().closeEvent(event)

    def on_port_connected(self):
        """포트 연결 성공 후 호출되는 함수"""
        print("포트 연결 성공")
        
        # ID 스캔 응답 시그널 연결 - 시그널 중복 연결 방지를 위한 코드 수정
        self.protocol = self.serial_manager.get_protocol()
        if self.protocol:
            # 연결 전에 시그널이 이미 연결되어 있는지 확인
            if hasattr(self.protocol, 'id_scan_received_connected') and self.protocol.id_scan_received_connected:
                try:
                    self.protocol.id_scan_received.disconnect(self.on_id_scan_received)
                    self.protocol.id_scan_received_connected = False
                except Exception as e:
                    print(f"id_scan_received 연결 해제 실패: {e}")
            
            # 시그널 연결
            self.protocol.id_scan_received.connect(self.on_id_scan_received)
            self.protocol.id_scan_received_connected = True

    def on_sync_success(self):
        """동기화 성공 처리"""
        # 이전 연결 해제
        if hasattr(self, 'protocol') and self.protocol:
            if hasattr(self.protocol, 'sync_success_connected') and self.protocol.sync_success_connected:
                try:
                    self.protocol.sync_success.disconnect(self.on_sync_success)
                    self.protocol.sync_success_connected = False
                except Exception as e:
                    print(f"sync_success 연결 해제 실패: {e}")
                
            if hasattr(self.protocol, 'sync_failed_connected') and self.protocol.sync_failed_connected:
                try:
                    self.protocol.sync_failed.disconnect(self.on_sync_failed)
                    self.protocol.sync_failed_connected = False
                except Exception as e:
                    print(f"sync_failed 연결 해제 실패: {e}")
            
        # 성공 메시지 표시
        QMessageBox.information(
            self,
            "동기화 성공",
            "장치와의 동기화가 성공적으로 완료되었습니다.",
            QMessageBox.Ok
        )
        print("장치와 동기화 성공")

    def on_sync_failed(self):
        """동기화 실패 처리"""
        # 이전 연결 해제
        if hasattr(self, 'protocol') and self.protocol:
            if hasattr(self.protocol, 'sync_success_connected') and self.protocol.sync_success_connected:
                try:
                    self.protocol.sync_success.disconnect(self.on_sync_success)
                    self.protocol.sync_success_connected = False
                except Exception as e:
                    print(f"sync_success 연결 해제 실패: {e}")
                
            if hasattr(self.protocol, 'sync_failed_connected') and self.protocol.sync_failed_connected:
                try:
                    self.protocol.sync_failed.disconnect(self.on_sync_failed)
                    self.protocol.sync_failed_connected = False
                except Exception as e:
                    print(f"sync_failed 연결 해제 실패: {e}")
        
        QMessageBox.critical(
            self,
            "동기화 실패",
            "장치와의 동기화에 실패했습니다.\n장치 연결 상태를 확인해주세요.",
            QMessageBox.Ok
        )
        print("장치와 동기화 실패")

    @Slot()
    def on_scan_start(self):
        """ID 스캔 시작 버튼 클릭 처리"""
        if not self.serial_manager.is_port_connected():
            QMessageBox.warning(self, "경고", "시리얼 포트에 연결되어 있지 않습니다.")
            return
            
        if self.scanning:
            # 이미 스캔 중이면 중단
            self.stop_scan()
            self.ScanStartButton.setText("스캔 시작")
            return
            
        # 스캔 시작 설정
        self.current_scan_id = self.ScanIdStartspinBox.value()
        self.max_scan_id = self.ScanIdEndSpinBox.value()
        
        if self.current_scan_id > self.max_scan_id:
            QMessageBox.warning(self, "경고", "시작 ID는 종료 ID보다 작아야 합니다.")
            return
            
        # 스캔 관련 UI 초기화
        self.ScanProgressBar.setValue(0)
        self.found_devices.clear()
        self.clear_device_list()
        
        # 스캔 상태 업데이트
        self.scanning = True
        self.ScanStartButton.setText("스캔 중지")
        
        # 시그널 연결을 재설정
        protocol = self.serial_manager.get_protocol()
        if protocol:
            # 중복 연결 방지를 위한 코드
            if hasattr(protocol, 'id_scan_received_connected') and protocol.id_scan_received_connected:
                try:
                    protocol.id_scan_received.disconnect(self.on_id_scan_received)
                    protocol.id_scan_received_connected = False
                except Exception as e:
                    print(f"id_scan_received 연결 해제 실패: {e}")
                
            # 새로 연결
            protocol.id_scan_received.connect(self.on_id_scan_received)
            protocol.id_scan_received_connected = True
        
        # 타이머 설정 (100ms 간격으로 스캔)
        if self.scan_timer is None:
            self.scan_timer = QTimer()
            self.scan_timer.timeout.connect(self.scan_next_id)
            
        self.scan_timer.start(100)  # 100ms 간격으로 스캔
        self.scan_next_id()  # 첫 번째 ID 즉시 스캔 시작
            
    def scan_next_id(self):
        """다음 ID 스캔 처리"""
        if not self.scanning or self.current_scan_id > self.max_scan_id:
            self.stop_scan()
            return
            
        # 진행률 업데이트
        total_ids = self.max_scan_id - self.ScanIdStartspinBox.value() + 1
        current_progress = self.current_scan_id - self.ScanIdStartspinBox.value()
        progress_percent = int((current_progress / total_ids) * 100)
        self.ScanProgressBar.setValue(progress_percent)
        
        # ID 스캔 요청 전송
        protocol = self.serial_manager.get_protocol()
        if protocol:
            protocol.sendIdScan(self.current_scan_id)
            
        # 다음 ID로 이동
        self.current_scan_id += 1
        
    def stop_scan(self):
        """스캔 중지 처리"""
        if self.scan_timer:
            self.scan_timer.stop()
        self.scanning = False
        self.ScanStartButton.setText("스캔 시작")
        self.ScanProgressBar.setValue(100)  # 진행률 100%로 설정
        
    @Slot(int)
    def on_id_scan_received(self, device_id):
        """ID 스캔 응답 수신 처리"""
        print(f"ID 스캔 응답 수신: {device_id}")
        
        # 이미 찾은 장치인지 확인
        if device_id not in self.found_devices:
            self.found_devices.append(device_id)
            self.add_device_to_list(device_id)
    
    def clear_device_list(self):
        """장치 목록 초기화"""
        # 기존 버튼 삭제
        for btn in self.device_buttons:
            btn.deleteLater()
        self.device_buttons.clear()
        
        # 레이아웃 초기화
        layout = self.scrollAreaWidgetContents_2.layout()
        if layout is None:
            layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
            layout.setContentsMargins(0, 0, 0, 0)
            self.scrollAreaWidgetContents_2.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
    
    def add_device_to_list(self, device_id):
        """장치를 목록에 추가"""
        layout = self.scrollAreaWidgetContents_2.layout()
        if layout is None:
            layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
            layout.setContentsMargins(0, 0, 0, 0)
            self.scrollAreaWidgetContents_2.setLayout(layout)
            
        # 라디오 버튼 생성
        device_info = f"장치 ID: {device_id}"
        rb = QRadioButton(device_info)
        rb.setProperty("device_id", device_id)
        self.device_buttons.append(rb)
        layout.addWidget(rb)
        
    @Slot()
    def on_device_selected(self):
        """선택한 장치에 대한 처리"""
        if not self.serial_manager.is_port_connected():
            QMessageBox.warning(self, "경고", "시리얼 포트에 연결되어 있지 않습니다.")
            return
            
        # 선택된 장치 확인
        selected_device_id = None
        for rb in self.device_buttons:
            if rb.isChecked():
                selected_device_id = rb.property("device_id")
                break
                
        if selected_device_id is None:
            QMessageBox.warning(self, "경고", "장치를 선택해주세요.")
            return
            
        # 선택된 장치 ID를 시리얼 통신의 수신자 ID로 설정
        if self.serial_manager:
            # SerialManager의 set_target_device_id 메서드 호출
            self.serial_manager.set_target_device_id(selected_device_id)
            
        # 동기화 시작
        self.protocol = self.serial_manager.get_protocol()
        if self.protocol:
            # 초기화 시 속성 설정 확인
            if not hasattr(self.protocol, 'sync_success_connected'):
                self.protocol.sync_success_connected = False
            if not hasattr(self.protocol, 'sync_failed_connected'):
                self.protocol.sync_failed_connected = False
            
            # 이전 연결 해제
            if self.protocol.sync_success_connected:
                try:
                    self.protocol.sync_success.disconnect(self.on_sync_success)
                    self.protocol.sync_success_connected = False
                except Exception as e:
                    print(f"sync_success 연결 해제 실패: {e}")
                
            if self.protocol.sync_failed_connected:
                try:
                    self.protocol.sync_failed.disconnect(self.on_sync_failed)
                    self.protocol.sync_failed_connected = False
                except Exception as e:
                    print(f"sync_failed 연결 해제 실패: {e}")
            
            # 새로운 연결 설정
            self.protocol.sync_success.connect(self.on_sync_success)
            self.protocol.sync_success_connected = True
            
            self.protocol.sync_failed.connect(self.on_sync_failed)
            self.protocol.sync_failed_connected = True
            
            self.protocol.start_sync_session()
        
        QMessageBox.information(self, "장치 선택", f"장치 ID {selected_device_id}가 선택되었습니다.")
        print(f"장치 ID {selected_device_id} 선택됨")

    @Slot()
    def on_all_monitor_selected(self):
        """모든 모니터 선택 처리"""
        if not self.serial_manager.is_port_connected():
            QMessageBox.warning(self, "경고", "시리얼 포트에 연결되어 있지 않습니다.")
            return
            
        if not self.found_devices:
            QMessageBox.warning(self, "경고", "스캔된 장치가 없습니다. 먼저 장치를 스캔해주세요.")
            return
            
        if self.is_all_monitor_mode:
            # 전체 모니터링 모드 종료
            self.stop_all_monitor_mode()
            self.AllMonitorModeButton.setText("전체 모니터링 모드")
        else:
            # 전체 모니터링 모드 시작
            self.start_all_monitor_mode()
            self.AllMonitorModeButton.setText("모니터링 중지")
            
    def start_all_monitor_mode(self):
        """전체 모니터링 모드 시작"""
        self.is_all_monitor_mode = True
        self.current_device_index = 0
        
        # 현재 sync 주기의 2배로 타이머 설정
        sync_interval = self.sync_ms_spinBox.value() * 2
        
        if self.all_monitor_timer is None:
            self.all_monitor_timer = QTimer()
            self.all_monitor_timer.timeout.connect(self.cycle_next_device)
            
        self.all_monitor_timer.start(sync_interval)
        self.cycle_next_device()  # 첫 번째 장치 즉시 선택
        
    def stop_all_monitor_mode(self):
        """전체 모니터링 모드 종료"""
        self.is_all_monitor_mode = False
        if self.all_monitor_timer:
            self.all_monitor_timer.stop()
            
    def cycle_next_device(self):
        """다음 장치로 순환"""
        if not self.is_all_monitor_mode or not self.found_devices:
            return
            
        # 현재 장치 ID 설정
        device_id = self.found_devices[self.current_device_index]
        self.serial_manager.set_target_device_id(device_id)
        print(f"전체 모니터링 모드: 장치 ID {device_id} 선택됨")
        
        # 다음 장치 인덱스 계산
        self.current_device_index = (self.current_device_index + 1) % len(self.found_devices)