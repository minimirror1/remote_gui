from PySide6.QtCore import QObject, Signal, Slot
from serial.tools import list_ports
import serial
from typing import Optional, List, Tuple
from src.widgets.serial_protocol import ComProtocol
from src.widgets.serial_reader import SerialReaderThread
import threading
import re  # 파일 상단에 추가

class SerialManager(QObject):
    """시리얼 통신 관리자 클래스"""
    # 시그널 정의
    data_received = Signal(bytes)  # 데이터 수신 시
    connection_changed = Signal(bool)  # 연결 상태 변경 시
    error_occurred = Signal(str)  # 에러 발생 시
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'SerialManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if SerialManager._instance is not None:
            raise Exception("SerialManager는 싱글톤 클래스입니다. get_instance()를 사용하세요.")
        
        super().__init__()
        self.serial_port = None
        self.protocol = None
        self.reader_thread = None
        self.is_connected = False
        self._baud_rate = 115200
        
    def get_available_ports(self) -> List[Tuple[str, str]]:
        """사용 가능한 시리얼 포트 목록을 반환합니다."""
        def extract_port_number(port: str) -> int:
            """포트 이름에서 숫자를 추출합니다."""
            match = re.search(r'\d+', port)
            return int(match.group()) if match else float('inf')
        
        def clean_description(description: str) -> str:
            """포트 설명에서 (COMx) 패턴을 제거합니다."""
            return re.sub(r'\s*\(COM\d+\)', '', description).strip()
        
        ports = list(list_ports.comports())
        port_list = [(port.device, clean_description(port.description)) for port in ports]
        # COM 번호를 기준으로 정렬
        return sorted(port_list, key=lambda x: extract_port_number(x[0]))
    
    @Slot(str)
    def connect_to_port(self, port_name: str) -> bool:
        """지정된 포트에 연결을 시도합니다."""
        if self.is_connected:
            self.disconnect_port()
            
        try:
            self.serial_port = serial.Serial(port_name, self._baud_rate, timeout=1)
            self.protocol = ComProtocol(self.serial_port, None)
            self.start_serial_thread()
            self.is_connected = True
            self.connection_changed.emit(True)
            return True
        except Exception as e:
            self.error_occurred.emit(f"연결 실패: {str(e)}")
            return False
    
    def disconnect_port(self) -> None:
        """현재 연결된 포트를 해제합니다."""
        try:
            self.stop_serial_thread()
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = None
            self.protocol = None
            self.is_connected = False
            self.connection_changed.emit(False)
        except Exception as e:
            self.error_occurred.emit(f"연결 해제 실패: {str(e)}")
    
    def send_data(self, data: bytes) -> bool:
        """데이터를 전송합니다."""
        if not self.is_connected or not self.serial_port:
            self.error_occurred.emit("포트가 연결되지 않았습니다")
            return False
            
        try:
            self.serial_port.write(data)
            return True
        except Exception as e:
            self.error_occurred.emit(f"데이터 전송 실패: {str(e)}")
            return False
    
    def start_serial_thread(self) -> None:
        """시리얼 데이터 수신 스레드를 시작합니다."""
        if self.serial_port and self.serial_port.is_open:
            self.reader_thread = SerialReaderThread(self.serial_port)
            self.reader_thread.data_received.connect(self._handle_received_data)
            self.reader_thread.start()
    
    def stop_serial_thread(self) -> None:
        """시리얼 데이터 수신 스레드를 중지합니다."""
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread = None
    
    @Slot(bytes)
    def _handle_received_data(self, data: bytes) -> None:
        """수신된 데이터를 처리합니다."""
        if self.protocol:
            self.protocol.receiveData(data)
            self.protocol.processReceivedData()
        self.data_received.emit(data)
    
    def get_protocol(self) -> Optional[ComProtocol]:
        """현재 ComProtocol 인스턴스를 반환합니다."""
        return self.protocol
    
    def is_port_connected(self) -> bool:
        """현재 포트 연결 상태를 반환합니다."""
        return self.is_connected
    
    def get_current_port(self) -> Optional[str]:
        """현재 연결된 포트 이름을 반환합니다."""
        if self.serial_port and self.serial_port.is_open:
            return self.serial_port.port
        return None 