import requests
import json
import logging
from typing import Callable, Dict, Optional, Any, List
import sseclient  # sseclient-py 패키지 임포트
import threading
from PySide6.QtCore import QObject, Signal


class SSEEventClient(QObject):
    """
    Server-Sent Events 클라이언트 클래스
    서버로부터 실시간 이벤트를 수신하고 처리합니다.
    새로운 API 구조에 맞게 object_id 기반 다중 연결을 지원합니다.
    """
    # 이벤트 시그널 정의
    event_received = Signal(str, str, dict)  # object_id, event_type, data
    connection_error = Signal(str, str)      # object_id, error_message
    connection_established = Signal(str)     # object_id
    connection_closed = Signal(str)          # object_id
    
    def __init__(self, base_url: str = "https://robot-monitor-dev.systemiic.com", headers: Optional[Dict[str, str]] = None, parent=None):
        """
        SSE 클라이언트 초기화
        
        Args:
            base_url: SSE 서버 베이스 URL
            headers: 요청에 사용할 HTTP 헤더 (선택사항)
            parent: Qt 부모 객체
        """
        super().__init__(parent)
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        
        # SSE 연결을 위한 Accept 헤더 설정
        if 'Accept' not in self.headers:
            self.headers['Accept'] = 'text/event-stream'
            
        self.event_handlers = {}
        self.logger = logging.getLogger(__name__)
        
        # 다중 오브제 연결 관리
        self.connections: Dict[str, Dict[str, Any]] = {}  # object_id -> connection_info
        self.stop_flags: Dict[str, threading.Event] = {}
        
        # DeviceStatusManager 연결
        self.device_manager = None
        self._setup_device_manager()
    
    def _setup_device_manager(self):
        """DeviceStatusManager 연결 설정"""
        try:
            from src.device_status_manager import DeviceStatusManager
            self.device_manager = DeviceStatusManager.get_instance()
            
            # DeviceStatusManager 시그널 연결 (실시간 장치 감지)
            self.device_manager.device_connected.connect(self._on_device_connected)
            self.device_manager.device_status_updated.connect(self._on_device_status_updated)
            
            self.logger.info("DeviceStatusManager 연결 완료")
        except Exception as e:
            self.logger.error(f"DeviceStatusManager 연결 실패: {e}")
            self.device_manager = None
    
    def _on_device_connected(self, device_id: str):
        """새로운 장치 연결 시 자동으로 SSE 연결 시작 (비활성화)"""
        # AutoDeviceSync에서 오브제 생성 후 올바른 object_id로 연결을 관리하므로
        # 여기서는 자동 연결을 시작하지 않음
        # 기존: 장치 ID로 직접 연결 → 404 오류 발생
        # 변경: AutoDeviceSync에서 오브제 ID로 연결 관리
        self.logger.info(f"새로운 장치 감지됨, SSE 연결 시작: {device_id}")
        self.logger.info(f"AutoDeviceSync에서 오브제 생성 후 연결 관리됨")
        
        # 자동 연결 비활성화
        # if device_id not in self.connections:
        #     self.start_object_connection(device_id)
    
    def _on_device_status_updated(self, device_id: str, status_data: dict):
        """장치 상태 업데이트 시 SSE 연결 확인 (AutoDeviceSync에서 관리)"""
        # AutoDeviceSync에서 오브제 생성 후 올바른 object_id로 연결을 관리하므로
        # 여기서는 자동 연결을 시작하지 않음
        # 기존: 장치 ID로 직접 연결 → 404 오류 발생
        # 변경: AutoDeviceSync에서 오브제 ID로 연결 관리
        pass
    
    def get_object_ids(self) -> List[str]:
        """
        DeviceStatusManager에서 관리 중인 모든 object_id 반환
        
        Returns:
            List[str]: object_id 목록
        """
        if not self.device_manager:
            self.logger.warning("DeviceStatusManager가 연결되지 않음")
            return []
        
        try:
            # 연결된 장치들의 ID를 object_id로 사용
            connected_devices = self.device_manager.get_connected_devices()
            all_devices = list(self.device_manager.get_all_devices_status().keys())
            
            # 연결된 장치를 우선으로 하되, 모든 장치 포함
            object_ids = list(set(connected_devices + all_devices))
            
            self.logger.info(f"관리 중인 object_ids: {object_ids}")
            return object_ids
            
        except Exception as e:
            self.logger.error(f"object_id 목록 가져오기 실패: {e}")
            return []
        
    def register_handler(self, event_type: str, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        특정 이벤트 타입에 대한 핸들러 등록
        
        Args:
            event_type: 처리할 이벤트 타입
            handler: 이벤트 데이터를 처리할 콜백 함수 (object_id, data)
        """
        self.event_handlers[event_type] = handler
        
    def start(self, object_id: str = None, retry_timeout: int = 3000) -> None:
        """
        SSE 연결 시작
        
        Args:
            object_id: 특정 오브제 ID (None이면 모든 오브제 연결)
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        if object_id:
            self.start_object_connection(object_id, retry_timeout)
        else:
            self.start_all_connections(retry_timeout)
    
    def start_all_connections(self, retry_timeout: int = 3000) -> None:
        """
        모든 오브제에 대한 SSE 연결 시작
        
        Args:
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        object_ids = self.get_object_ids()
        
        if not object_ids:
            self.logger.warning("연결할 오브제가 없습니다")
            return
        
        self.logger.info(f"다중 SSE 연결 시작: {len(object_ids)}개 오브제")
        
        for object_id in object_ids:
            self.start_object_connection(object_id, retry_timeout)
    
    def start_object_connection(self, object_id: str, retry_timeout: int = 3000) -> None:
        """
        특정 오브제에 대한 SSE 연결 시작
        
        Args:
            object_id: 오브제 ID
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        # 이미 연결된 경우 중단
        if object_id in self.connections:
            self.logger.warning(f"이미 연결된 오브제: {object_id}")
            return
        
        # 중단 플래그 초기화
        self.stop_flags[object_id] = threading.Event()
        
        # 연결 정보 저장
        thread = threading.Thread(
            target=self._run_sse_client,
            args=(object_id, retry_timeout),
            name=f"SSE-{object_id}",
            daemon=True
        )
        
        self.connections[object_id] = {
            'thread': thread,
            'client': None,
            'url': f"{self.base_url}/v1/service/objects/{object_id}/power"
        }
        
        thread.start()
        self.logger.info(f"SSE 연결 시작됨: {object_id}")
        
    def stop(self, object_id: str = None) -> None:
        """
        SSE 연결 중지
        
        Args:
            object_id: 특정 오브제 ID (None이면 모든 연결 중지)
        """
        if object_id:
            self.stop_object_connection(object_id)
        else:
            self.stop_all_connections()
    
    def stop_object_connection(self, object_id: str) -> None:
        """특정 오브제의 SSE 연결 중지"""
        if object_id in self.stop_flags:
            self.stop_flags[object_id].set()
            self.logger.info(f"SSE 연결 중단 신호 전송: {object_id}")
        
        if object_id in self.connections:
            connection = self.connections[object_id]
            
            # 클라이언트 종료
            if connection.get('client'):
                try:
                    connection['client'].close()
                except:
                    pass
            
            # 스레드 종료 대기
            thread = connection.get('thread')
            if thread and thread.is_alive():
                thread.join(timeout=2.0)
            
            # 연결 정보 제거
            del self.connections[object_id]
            self.connection_closed.emit(object_id)
            self.logger.info(f"SSE 연결 종료됨: {object_id}")
    
    def stop_all_connections(self) -> None:
        """모든 SSE 연결 중지"""
        self.logger.info("모든 SSE 연결 중단 중...")
        
        for object_id in list(self.connections.keys()):
            self.stop_object_connection(object_id)
        
        # 정리
        self.stop_flags.clear()
        self.logger.info("모든 SSE 연결이 중단되었습니다")
    
    def _run_sse_client(self, object_id: str, retry_timeout: int) -> None:
        """
        백그라운드 스레드에서 SSE 클라이언트 실행
        
        Args:
            object_id: 오브제 ID
            retry_timeout: 재연결 시도 간격(밀리초)
        """
        connection = self.connections.get(object_id)
        if not connection:
            return
        
        url = connection['url']
        
        while not self.stop_flags.get(object_id, threading.Event()).is_set():
            try:
                self.logger.info(f"SSE 서버 연결 중: {url}")
                response = requests.get(url, headers=self.headers, stream=True, timeout=30)
                response.raise_for_status()  # HTTP 오류 확인
                
                client = sseclient.SSEClient(response)
                connection['client'] = client
                
                self.connection_established.emit(object_id)
                self.logger.info(f"SSE 서버에 연결됨: {object_id}")
                
                for event in client.events():
                    if self.stop_flags.get(object_id, threading.Event()).is_set():
                        break
                    self._process_event(object_id, event)
                    
            except requests.RequestException as e:
                self.logger.error(f"SSE 연결 오류 ({object_id}): {str(e)}")
                self.connection_error.emit(object_id, str(e))
                
                # 재연결 시도 전 대기
                if not self.stop_flags.get(object_id, threading.Event()).is_set():
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도... ({object_id})")
                    self.stop_flags[object_id].wait(timeout=retry_timeout/1000)
                    
            except Exception as e:
                self.logger.error(f"SSE 처리 중 예상치 못한 오류 ({object_id}): {str(e)}")
                self.connection_error.emit(object_id, f"예상치 못한 오류: {str(e)}")
                
                # 재연결 시도 전 대기
                if not self.stop_flags.get(object_id, threading.Event()).is_set():
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도... ({object_id})")
                    self.stop_flags[object_id].wait(timeout=retry_timeout/1000)
    
    def _process_event(self, object_id: str, event):
        """
        수신된 SSE 이벤트 처리
        
        Args:
            object_id: 오브제 ID
            event: SSE 이벤트 객체
        """
        event_type = event.event or 'message'
        try:
            # 이벤트 데이터 파싱
            data = json.loads(event.data) if event.data else {}
            
            # 시그널 발생
            self.event_received.emit(object_id, event_type, data)
            
            # 등록된 핸들러 호출
            if event_type in self.event_handlers:
                self.logger.debug(f"이벤트 수신: {event_type} (Object: {object_id})")
                self.event_handlers[event_type](object_id, data)
            else:
                self.logger.debug(f"처리되지 않은 이벤트 타입: {event_type}, Object: {object_id}, 데이터: {data}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"JSON 파싱 오류 (Object {object_id}): {event.data}")
            # JSON이 아닌 경우 원본 데이터 전달
            if event_type in self.event_handlers:
                self.event_handlers[event_type](object_id, event.data)
    
    def is_running(self, object_id: str = None) -> bool:
        """
        현재 연결 상태 반환
        
        Args:
            object_id: 특정 오브제 ID (None이면 전체 연결 상태)
            
        Returns:
            bool: 연결 상태
        """
        if object_id:
            connection = self.connections.get(object_id)
            if connection:
                thread = connection.get('thread')
                return thread and thread.is_alive() and not self.stop_flags.get(object_id, threading.Event()).is_set()
            return False
        else:
            # 하나라도 연결되어 있으면 True
            for obj_id in self.connections:
                if self.is_running(obj_id):
                    return True
            return False
    
    def get_connected_objects(self) -> List[str]:
        """현재 연결된 오브제 ID 목록 반환"""
        connected = []
        for object_id in self.connections:
            if self.is_running(object_id):
                connected.append(object_id)
        return connected
    
    def get_connection_status(self) -> Dict[str, bool]:
        """모든 오브제의 연결 상태 반환"""
        status = {}
        for object_id in self.connections:
            status[object_id] = self.is_running(object_id)
        return status 