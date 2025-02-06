from PySide6.QtCore import QThread, Signal
import time


class SerialReaderThread(QThread):
    """
    시리얼 포트에서 데이터를 읽어오는 별도 쓰레드.
    수신된 데이터를 data_received 시그널을 통해 전달합니다.
    """
    data_received = Signal(bytes)
    error_occurred = Signal(str)

    def __init__(self, serial_port, parent=None):
        super().__init__(parent)
        self.serial_port = serial_port
        self._running = True
        self._sync_enabled = False
        self._sync_interval = 1000
        self._last_sync_time = 0

    def run(self):
        while self._running:
            # 시리얼 데이터 읽기
            if self.serial_port and self.serial_port.is_open:
                try:
                    # 수신 데이터 처리
                    bytes_waiting = self.serial_port.in_waiting
                    if bytes_waiting:
                        data = self.serial_port.read(bytes_waiting)
                        self.data_received.emit(data)
                    
                    # Sync 패킷 전송 처리
                    if self._sync_enabled:
                        current_time = time.time() * 1000
                        if current_time - self._last_sync_time >= self._sync_interval:
                            self._last_sync_time = current_time
                            # SerialManager의 protocol 사용
                            serial_manager = self.parent()
                            if serial_manager and serial_manager.protocol:
                                serial_manager.protocol.send_sync_packet(0x0001, 0x0000)

                except Exception as e:
                    self.error_occurred.emit(f"SerialReaderThread 에러: {str(e)}")
            
            # CPU 사용률을 낮추기 위한 짧은 대기
            self.msleep(1)

    def stop(self):
        """쓰레드를 중지합니다."""
        self._running = False
        self.quit()
        self.wait()

    def set_sync_enabled(self, enabled: bool):
        """Sync 패킷 전송 활성화/비활성화"""
        self._sync_enabled = enabled
        if enabled:
            self._last_sync_time = 0  # 즉시 첫 전송이 이루어지도록 초기화

    def set_sync_interval(self, interval_ms: int):
        """Sync 패킷 전송 주기 설정"""
        self._sync_interval = interval_ms 