from PySide6.QtCore import QObject, Signal, QDateTime, Slot
from typing import Dict, Any, Optional, List
import threading


class DeviceStatusManager(QObject):
    """
    장치 상태 데이터를 전역으로 관리하는 싱글톤 클래스
    - 장치 ID별 최신 상태 데이터 저장
    - SSE 통신 및 다른 컴포넌트에서 활용 가능
    """
    
    # 시그널 정의
    device_status_updated = Signal(str, dict)  # device_id, status_data
    device_connected = Signal(str)  # device_id
    device_disconnected = Signal(str)  # device_id
    all_devices_status_updated = Signal(dict)  # {device_id: status_data}
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """초기화 - 한 번만 실행됨"""
        if self._initialized:
            return
            
        super().__init__()
        
        # 장치별 상태 데이터 저장소
        self._device_status: Dict[str, Dict[str, Any]] = {}
        
        # 장치별 마지막 업데이트 시간
        self._last_update_time: Dict[str, QDateTime] = {}
        
        # 연결된 장치 목록
        self._connected_devices: set = set()
        
        # 데이터 접근을 위한 락
        self._data_lock = threading.Lock()
        
        # 프로토콜 시그널 연결 관리
        self._protocol_connected = False
        self._current_protocol = None
        self._serial_manager = None
        
        # SerialManager 인스턴스 연결 (싱글톤이므로 직접 import 후 연결)
        self._connect_to_serial_manager()
        
        self._initialized = True
        print("DeviceStatusManager 초기화 완료")
    
    @classmethod
    def get_instance(cls) -> 'DeviceStatusManager':
        """싱글톤 인스턴스 반환"""
        return cls()
    
    def _connect_to_serial_manager(self):
        """SerialManager와 연결하여 프로토콜 시그널 모니터링"""
        try:
            # SerialCommands를 통해 SerialManager 인스턴스 가져오기
            from src.widgets.serial_commands import SerialCommands
            serial_commands = SerialCommands.get_instance()
            self._serial_manager = serial_commands.serial_manager
            
            # SerialManager의 연결 상태 변경 시그널 연결
            self._serial_manager.connection_changed.connect(self._on_serial_connection_changed)
            
            # 현재 연결 상태 확인하여 프로토콜 시그널 연결
            if self._serial_manager.is_port_connected():
                self._connect_protocol_signals()
                
            print("DeviceStatusManager: SerialManager 연결 완료")
            
        except Exception as e:
            print(f"DeviceStatusManager: SerialManager 연결 실패: {e}")
    
    @Slot(bool)
    def _on_serial_connection_changed(self, is_connected: bool):
        """시리얼 연결 상태 변경 시 호출"""
        print(f"DeviceStatusManager: 시리얼 연결 상태 변경 - {is_connected}")
        
        if is_connected:
            self._connect_protocol_signals()
        else:
            self._disconnect_protocol_signals()
            # 연결 해제 시 모든 장치를 연결 해제 상태로 변경
            self._mark_all_devices_disconnected()
    
    def _connect_protocol_signals(self):
        """프로토콜 시그널에 직접 연결"""
        if not self._serial_manager:
            return
            
        protocol = self._serial_manager.get_protocol()
        if protocol:
            # 현재 protocol이 다르다면 이전 연결 해제
            if self._current_protocol is not protocol:
                self._disconnect_protocol_signals()
            
            # 새로운 연결 설정
            if not self._protocol_connected:
                protocol.status_sync_changed.connect(self._on_status_sync_changed)
                self._protocol_connected = True
                self._current_protocol = protocol
                print("DeviceStatusManager: 프로토콜 시그널 연결 완료")
    
    def _disconnect_protocol_signals(self):
        """프로토콜 시그널 연결 해제"""
        if self._protocol_connected and self._current_protocol:
            try:
                self._current_protocol.status_sync_changed.disconnect(self._on_status_sync_changed)
                print("DeviceStatusManager: 프로토콜 시그널 연결 해제 완료")
            except Exception as e:
                print(f"DeviceStatusManager: 프로토콜 시그널 연결 해제 실패: {e}")
            finally:
                self._protocol_connected = False
                self._current_protocol = None
    
    @Slot(dict)
    def _on_status_sync_changed(self, status_data: dict):
        """프로토콜에서 직접 받은 상태 동기화 시그널 처리"""
        # 상태 데이터에서 장치 ID 추출
        device_id = status_data.get('device_id')
        
        print(f"DeviceStatusManager: 상태 데이터 수신 - device_id: {device_id}")
        
        if device_id is not None:
            # device_id 타입 통일 (문자열로 변환)
            try:
                device_id = str(device_id)
                status_data['device_id'] = device_id
            except (ValueError, TypeError):
                print(f"DeviceStatusManager: device_id 타입 변환 실패: {device_id}")
                return
        else:
            print("DeviceStatusManager: device_id가 없음 - 상태 데이터 무시")
            return
        
        # 장치 상태 업데이트
        self.update_device_status(device_id, status_data)
        print(f"DeviceStatusManager: 장치 ID {device_id} 상태 업데이트 완료 (전역)")
    
    def _mark_all_devices_disconnected(self):
        """모든 장치를 연결 해제 상태로 변경"""
        with self._data_lock:
            for device_id in list(self._connected_devices):
                self._connected_devices.remove(device_id)
                self.device_disconnected.emit(device_id)
        
        print("DeviceStatusManager: 모든 장치 연결 해제로 설정")
    
    def update_device_status(self, device_id: str, status_data: Dict[str, Any]) -> None:
        """
        장치 상태 데이터 업데이트
        
        Args:
            device_id: 장치 ID (문자열로 통일)
            status_data: 상태 데이터 딕셔너리
        """
        device_id = str(device_id)  # 문자열로 통일
        current_time = QDateTime.currentDateTime()
        
        with self._data_lock:
            # 이전 상태와 비교하여 변경된 경우만 처리
            old_status = self._device_status.get(device_id, {})
            
            # 상태 데이터 업데이트
            self._device_status[device_id] = status_data.copy()
            self._last_update_time[device_id] = current_time
            
            # 새로 연결된 장치인지 확인
            was_connected = device_id in self._connected_devices
            is_now_connected = self._is_device_connected(status_data)
            
            if is_now_connected:
                self._connected_devices.add(device_id)
                if not was_connected:
                    self.device_connected.emit(device_id)
            else:
                if device_id in self._connected_devices:
                    self._connected_devices.remove(device_id)
                if was_connected:
                    self.device_disconnected.emit(device_id)
        
        # 시그널 발생 (락 외부에서)
        self.device_status_updated.emit(device_id, status_data)
        
        # 전체 상태 업데이트 시그널 (필요시)
        self.all_devices_status_updated.emit(self.get_all_devices_status())
        
        print(f"장치 상태 업데이트: ID={device_id}, 연결={is_now_connected}")
    
    def _is_device_connected(self, status_data: Dict[str, Any]) -> bool:
        """
        상태 데이터를 기반으로 장치 연결 상태 판단
        
        Args:
            status_data: 상태 데이터
            
        Returns:
            bool: 연결 상태 (True=연결됨, False=연결 안됨)
        """
        # main_power 상태로 연결 여부 판단
        main_power = status_data.get('main_power', {})
        return main_power.get('status', False)
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 장치의 최신 상태 데이터 반환
        
        Args:
            device_id: 장치 ID
            
        Returns:
            Dict[str, Any]: 상태 데이터 또는 None
        """
        device_id = str(device_id)
        with self._data_lock:
            return self._device_status.get(device_id, None)
    
    def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """
        모든 장치의 최신 상태 데이터 반환
        
        Returns:
            Dict[str, Dict[str, Any]]: {device_id: status_data}
        """
        with self._data_lock:
            return self._device_status.copy()
    
    def get_connected_devices(self) -> List[str]:
        """
        현재 연결된 장치 ID 목록 반환
        
        Returns:
            List[str]: 연결된 장치 ID 목록
        """
        with self._data_lock:
            return list(self._connected_devices)
    
    def get_device_count(self) -> int:
        """
        등록된 장치 총 개수 반환
        
        Returns:
            int: 장치 개수
        """
        with self._data_lock:
            return len(self._device_status)
    
    def get_connected_device_count(self) -> int:
        """
        현재 연결된 장치 개수 반환
        
        Returns:
            int: 연결된 장치 개수
        """
        with self._data_lock:
            return len(self._connected_devices)
    
    def is_device_connected(self, device_id: str) -> bool:
        """
        특정 장치의 연결 상태 확인
        
        Args:
            device_id: 장치 ID
            
        Returns:
            bool: 연결 상태
        """
        device_id = str(device_id)
        with self._data_lock:
            return device_id in self._connected_devices
    
    def get_device_last_update_time(self, device_id: str) -> Optional[QDateTime]:
        """
        특정 장치의 마지막 업데이트 시간 반환
        
        Args:
            device_id: 장치 ID
            
        Returns:
            QDateTime: 마지막 업데이트 시간 또는 None
        """
        device_id = str(device_id)
        with self._data_lock:
            return self._last_update_time.get(device_id, None)
    
    def remove_device(self, device_id: str) -> bool:
        """
        장치 데이터 제거 (연결 해제 시 사용)
        
        Args:
            device_id: 장치 ID
            
        Returns:
            bool: 제거 성공 여부
        """
        device_id = str(device_id)
        
        with self._data_lock:
            removed = False
            
            if device_id in self._device_status:
                del self._device_status[device_id]
                removed = True
            
            if device_id in self._last_update_time:
                del self._last_update_time[device_id]
            
            if device_id in self._connected_devices:
                self._connected_devices.remove(device_id)
                self.device_disconnected.emit(device_id)
        
        if removed:
            print(f"장치 데이터 제거: ID={device_id}")
        
        return removed
    
    def clear_all_devices(self) -> None:
        """모든 장치 데이터 초기화"""
        with self._data_lock:
            disconnected_devices = list(self._connected_devices)
            
            self._device_status.clear()
            self._last_update_time.clear()
            self._connected_devices.clear()
        
        # 연결 해제 시그널 발생
        for device_id in disconnected_devices:
            self.device_disconnected.emit(device_id)
        
        print("모든 장치 데이터 초기화")
    
    def cleanup(self):
        """DeviceStatusManager 정리 (프로그램 종료 시 호출)"""
        self._disconnect_protocol_signals()
        
        # SerialManager 시그널 연결 해제
        if self._serial_manager:
            try:
                self._serial_manager.connection_changed.disconnect(self._on_serial_connection_changed)
            except Exception as e:
                print(f"DeviceStatusManager: SerialManager 시그널 연결 해제 실패: {e}")
        
        print("DeviceStatusManager 정리 완료")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        상태 요약 정보 반환 (SSE나 API에서 활용)
        
        Returns:
            Dict[str, Any]: 요약 정보
        """
        with self._data_lock:
            total_devices = len(self._device_status)
            connected_devices = len(self._connected_devices)
            
            # 각 장치별 간단한 상태 정보
            device_summary = {}
            for device_id, status_data in self._device_status.items():
                main_power = status_data.get('main_power', {}).get('status', False)
                motion_status = status_data.get('motion', {}).get('status', 'UNKNOWN')
                error_flag = status_data.get('error', {}).get('flag', False)
                
                device_summary[device_id] = {
                    'connected': main_power,
                    'motion_status': motion_status,
                    'has_error': error_flag,
                    'last_update': self._last_update_time.get(device_id, QDateTime()).toString("hh:mm:ss")
                }
        
        return {
            'total_devices': total_devices,
            'connected_devices': connected_devices,
            'devices': device_summary,
            'timestamp': QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        }
    
    def get_sse_data(self) -> Dict[str, Any]:
        """
        SSE 전송용 데이터 포맷 반환
        
        Returns:
            Dict[str, Any]: SSE 전송용 데이터
        """
        return {
            'type': 'device_status',
            'data': self.get_status_summary()
        } 