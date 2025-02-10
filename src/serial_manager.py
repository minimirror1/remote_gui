from PySide6.QtCore import QObject, Signal, Slot
from serial.tools import list_ports
import serial
from typing import Optional, List, Tuple
from src.widgets.serial_protocol import ComProtocol
from src.widgets.serial_reader import SerialReaderThread
import threading
import re  # 파일 상단에 추가
from threading import Lock  # 파일 상단에 추가
import time  # 파일 상단에 추가

class SerialManager(QObject):
    """시리얼 통신 관리자 클래스"""
    # 시그널 정의
    data_received = Signal(bytes)  # 데이터 수신 시
    connection_changed = Signal(bool)  # 연결 상태 변경 시
    error_occurred = Signal(str)  # 에러 발생 시
    
    _instance = None
    _lock = threading.Lock()
    
    # 클래스 상수 정의
    DEFAULT_HOST_ID = 0x0000
    DEFAULT_DEVICE_ID = 0x0001
    
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
        self.main_window = None  # MainWindow 참조를 저장할 속성 추가
        self._error_dialog_shown = False  # 에러 다이얼로그 표시 상태 추적
        self._send_lock = Lock()  # 전송 뮤텍스 추가
        self._write_timeout = 1.0  # 쓰기 타임아웃을 1초로 증가
        self._max_retries = 3  # 최대 재시도 횟수
        self._retry_delay = 0.05  # 재시도 간격 (50ms)
        
    def set_main_window(self, window):
        """MainWindow 인스턴스 참조를 설정합니다."""
        self.main_window = window
    
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
    
    @Slot()
    def connect_to_port(self, port_name: str) -> bool:
        """지정된 포트에 연결"""
        if self.is_connected:
            self.disconnect_port()
            
        try:
            self.serial_port = serial.Serial(
                port_name, 
                self._baud_rate, 
                timeout=1,
                write_timeout=self._write_timeout  # 쓰기 타임아웃 설정
            )
            self.protocol = ComProtocol(self.serial_port, None)
            self.protocol.data_sent.connect(self._handle_data_sent)
            
            self.start_serial_thread()
            
            # 연결 끊김 시그널 연결
            if self.reader_thread:
                self.reader_thread.connection_lost.connect(self._handle_connection_lost)
            
            self.is_connected = True
            self._error_dialog_shown = False  # 에러 다이얼로그 상태 초기화
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
    
    def send_packet(self, receiverId: int, senderId: int, cmd: int, data: bytes) -> bool:
        """
        시리얼 포트로 패킷을 전송합니다.
        재시도 로직이 포함되어 있습니다.
        """
        if not self.is_port_connected() or not self.protocol:
            return False
        
        retries = 0
        while retries < self._max_retries:
            try:
                with self._send_lock:  # 뮤텍스로 보호된 전송
                    # SYNC 패킷이 아닌 경우 우선순위를 높임
                    if cmd != ComProtocol.CMD_STATUS_SYNC:
                        # 현재 write_timeout 저장
                        original_timeout = self.serial_port.write_timeout
                        try:
                            # 제어 패킷은 더 긴 타임아웃 사용
                            self.serial_port.write_timeout = self._write_timeout
                            self.protocol.sendData(receiverId, senderId, cmd, data)
                            return True
                        finally:
                            # 원래 타임아웃으로 복원
                            self.serial_port.write_timeout = original_timeout
                    else:
                        # SYNC 패킷은 기존 타임아웃 사용
                        self.protocol.sendData(receiverId, senderId, cmd, data)
                        return True
                    
            except serial.SerialTimeoutException:
                print(f"시리얼 쓰기 타임아웃 발생 (재시도 {retries + 1}/{self._max_retries})")
                retries += 1
                if retries < self._max_retries:
                    time.sleep(self._retry_delay)  # 재시도 전 대기
                continue
                
            except Exception as e:
                print(f"패킷 전송 실패: {str(e)}")
                return False
                
        return False  # 모든 재시도 실패
    
    def start_serial_thread(self) -> None:
        """시리얼 데이터 수신 스레드를 시작합니다."""
        if self.serial_port and self.serial_port.is_open:
            self.reader_thread = SerialReaderThread(self.serial_port, self)  # self를 parent로 전달
            self.reader_thread.data_received.connect(self._handle_received_data)
            self.reader_thread.error_occurred.connect(self.error_occurred.emit)  # 에러 시그널 연결
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
        # RX LED 표시
        if self.main_window:
            self.main_window.indicate_rx()
    
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

    @Slot(bytes)
    def _handle_data_sent(self, data: bytes) -> None:
        """ComProtocol에서 데이터가 전송되었을 때 호출되는 핸들러"""
        # TX LED 표시
        if self.main_window:
            self.main_window.indicate_tx() 

    def send_sync_packet(self, receiverId: int = None, senderId: int = None) -> bool:
        """
        상태 동기화를 위한 sync 패킷을 전송합니다.
        
        Args:
            receiverId (int, optional): 수신자 ID. 
                                      기본값은 DEFAULT_DEVICE_ID (0x0001)
            senderId (int, optional): 송신자 ID. 
                                    기본값은 DEFAULT_HOST_ID (0x0000)
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.is_port_connected() or not self.protocol:
            self.error_occurred.emit("포트가 연결되지 않았습니다")
            return False
            
        try:
            # 기본값 설정
            if receiverId is None:
                receiverId = self.DEFAULT_DEVICE_ID
            if senderId is None:
                senderId = self.DEFAULT_HOST_ID
                
            # ComProtocol의 sync 패킷 전송 메서드 호출
            self.protocol.send_sync_packet(receiverId, senderId)
            return True
            
        except Exception as e:
            error_msg = f"Sync 패킷 전송 실패: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False 

    def get_reader_thread(self) -> Optional['SerialReaderThread']:
        """현재 실행 중인 SerialReaderThread 인스턴스를 반환합니다."""
        # 단순히 reader_thread 반환 (연결 상태와 관계없이)
        return self.reader_thread

    def _handle_connection_lost(self):
        """연결 끊김 처리"""
        if not self._error_dialog_shown:
            self.error_occurred.emit("시리얼 포트 연결이 끊어졌습니다.")
            self._error_dialog_shown = False
            self.disconnect_port()

    def _handle_received_data(self, data: bytes) -> None:
        """수신된 데이터를 처리합니다."""
        if self.protocol:
            self.protocol.receiveData(data)
            self.protocol.processReceivedData()
        self.data_received.emit(data)
        # RX LED 표시
        if self.main_window:
            self.main_window.indicate_rx()
    
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

    @Slot(bytes)
    def _handle_data_sent(self, data: bytes) -> None:
        """ComProtocol에서 데이터가 전송되었을 때 호출되는 핸들러"""
        # TX LED 표시
        if self.main_window:
            self.main_window.indicate_tx() 

    def send_sync_packet(self, receiverId: int = None, senderId: int = None) -> bool:
        """
        상태 동기화를 위한 sync 패킷을 전송합니다.
        
        Args:
            receiverId (int, optional): 수신자 ID. 
                                      기본값은 DEFAULT_DEVICE_ID (0x0001)
            senderId (int, optional): 송신자 ID. 
                                    기본값은 DEFAULT_HOST_ID (0x0000)
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.is_port_connected() or not self.protocol:
            self.error_occurred.emit("포트가 연결되지 않았습니다")
            return False
            
        try:
            # 기본값 설정
            if receiverId is None:
                receiverId = self.DEFAULT_DEVICE_ID
            if senderId is None:
                senderId = self.DEFAULT_HOST_ID
                
            # ComProtocol의 sync 패킷 전송 메서드 호출
            self.protocol.send_sync_packet(receiverId, senderId)
            return True
            
        except Exception as e:
            error_msg = f"Sync 패킷 전송 실패: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False 

    def get_reader_thread(self) -> Optional['SerialReaderThread']:
        """현재 실행 중인 SerialReaderThread 인스턴스를 반환합니다."""
        # 단순히 reader_thread 반환 (연결 상태와 관계없이)
        return self.reader_thread

    @Slot()
    def connect_to_port(self, port_name: str) -> bool:
        """지정된 포트에 연결을 시도합니다."""
        if self.is_connected:
            self.disconnect_port()
            
        try:
            self.serial_port = serial.Serial(
                port_name, 
                self._baud_rate, 
                timeout=1,
                write_timeout=self._write_timeout  # 쓰기 타임아웃 설정
            )
            self.protocol = ComProtocol(self.serial_port, None)
            # 프로토콜의 data_sent 시그널 연결
            self.protocol.data_sent.connect(self._handle_data_sent)
            
            # 시리얼 스레드 시작 (protocol 설정 후)
            self.start_serial_thread()
            
            self.is_connected = True
            self.connection_changed.emit(True)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"연결 실패: {str(e)}")
            return False 