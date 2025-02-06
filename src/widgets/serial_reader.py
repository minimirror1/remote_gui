from PySide6.QtCore import QThread, Signal


class SerialReaderThread(QThread):
    """
    시리얼 포트에서 데이터를 읽어오는 별도 쓰레드.
    수신된 데이터를 data_received 시그널을 통해 전달합니다.
    """
    data_received = Signal(bytes)

    def __init__(self, serial_port, parent=None):
        super().__init__(parent)
        self.serial_port = serial_port
        self._running = True

    def run(self):
        while self._running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    bytes_waiting = self.serial_port.in_waiting
                    if bytes_waiting:
                        data = self.serial_port.read(bytes_waiting)
                        self.data_received.emit(data)
                except Exception as e:
                    print("SerialReaderThread 에러:", e)
            # CPU 사용률을 낮추기 위해 짧은 시간 대기 (10ms)
            self.msleep(10)

    def stop(self):
        """쓰레드를 중지합니다."""
        self._running = False
        self.quit()
        self.wait() 