from PySide6.QtCore import QThread, Signal
from threading import Lock  # threading에서 Lock import
import time
import serial
from serial.serialutil import SerialException


class SerialReaderThread(QThread):
    """
    시리얼 포트에서 데이터를 읽어오는 별도 쓰레드.
    수신된 데이터를 data_received 시그널을 통해 전달합니다.
    """
    data_received = Signal(bytes)
    error_occurred = Signal(str)
    connection_lost = Signal()

    def __init__(self, serial_port, parent=None):
        super().__init__(parent)
        self.serial_port = serial_port
        self._running = True
        self._sync_enabled = False
        self._sync_interval = 1000
        self._last_sync_time = 0
        self._error_reported = False
        self._sync_lock = Lock()

    def run(self):
        while self._running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    if not self._error_reported:
                        self.connection_lost.emit()
                        self._error_reported = True
                    break

                # 먼저 데이터 수신 처리
                try:
                    bytes_waiting = self.serial_port.in_waiting
                    if bytes_waiting:
                        data = self.serial_port.read(bytes_waiting)
                        self.data_received.emit(data)
                except serial.SerialTimeoutException:
                    # 타임아웃은 무시
                    pass
                except serial.SerialException as e:
                    # 실제 연결 문제는 상위로 전파
                    raise e
                except:
                    # 기타 예외는 무시
                    pass

                # Sync 패킷 전송 처리 - 실패시 무시
                if self._sync_enabled:
                    current_time = time.time() * 1000
                    if current_time - self._last_sync_time >= self._sync_interval:
                        try:
                            with self._sync_lock:
                                serial_manager = self.parent()
                                if serial_manager and serial_manager.protocol:
                                    serial_manager.protocol.send_sync_packet(0x0001, 0x0000)
                        except serial.SerialTimeoutException:
                            # 타임아웃은 무시
                            pass
                        except serial.SerialException as e:
                            # 실제 연결 문제인 경우만 상위로 전파
                            if "disconnected" in str(e).lower() or "access denied" in str(e).lower():
                                raise e
                        except:
                            # 기타 예외는 무시
                            pass
                        finally:
                            self._last_sync_time = current_time

            except serial.SerialException as e:
                # 실제 연결 끊김 상황만 처리
                if "disconnected" in str(e).lower() or "access denied" in str(e).lower():
                    if not self._error_reported:
                        self.error_occurred.emit("시리얼 포트 연결이 끊어졌습니다.")
                        self.connection_lost.emit()
                        self._error_reported = True
                    break
                else:
                    # 다른 시리얼 예외는 무시하고 계속 진행
                    continue
            except Exception as e:
                print(f"예상치 못한 예외 발생: {str(e)}")
                continue
            
            self.msleep(1)

        self._cleanup()

    def _cleanup(self):
        """리소스 정리"""
        self._running = False
        self._error_reported = False
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except:
                pass

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
            self._error_reported = False  # 에러 상태 초기화

    def set_sync_interval(self, interval_ms: int):
        """Sync 패킷 전송 주기 설정"""
        self._sync_interval = interval_ms 