import threading
import logging
from PySide6.QtCore import QObject, Signal, Slot
from typing import Optional, Dict, Any, List
from src.api.sse_client import SSEEventClient

class SSEManager(QObject):
    """SSE 연결 관리자 클래스 (싱글톤) - 새로운 object_id 기반 API 지원"""
    
    # 시그널 정의 (새로운 API 구조에 맞게 업데이트)
    event_received = Signal(str, str, dict)  # object_id, event_type, data
    connection_error = Signal(str, str)      # object_id, error_message
    connection_established = Signal(str)     # object_id
    connection_closed = Signal(str)          # object_id
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'SSEManager':
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """초기화 - 싱글톤 패턴이므로 직접 호출하지 마세요."""
        if SSEManager._instance is not None:
            raise Exception("SSEManager는 싱글톤 클래스입니다. get_instance()를 사용하세요.")
        
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.sse_client = None
        self.config = {
            'base_url': 'https://robot-monitor-dev.systemiic.com',
            'headers': {}
        }
    
    def configure(self, url: str = None, base_url: str = None, store_id: str = None, 
                  headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None) -> None:
        """
        SSE 클라이언트 설정
        
        Args:
            url: 이전 버전 호환성을 위한 파라미터 (base_url로 변환됨)
            base_url: 새로운 API의 베이스 URL
            store_id: 사용되지 않음 (하위 호환성을 위해 유지)
            headers: HTTP 헤더
            params: 사용되지 않음 (하위 호환성을 위해 유지)
        """
        # 하위 호환성: url 파라미터를 base_url로 변환
        if url and not base_url:
            # 기존 URL에서 base_url 추출
            if '/v1/service/stores/event-sources' in url:
                base_url = url.split('/v1/service/stores/event-sources')[0]
            else:
                base_url = url
        
        if base_url:
            self.config['base_url'] = base_url
        
        if headers:
            self.config['headers'] = headers
        
        self.logger.info(f"SSE 매니저 설정 완료: Base URL={self.config['base_url']}")
        
        # 이전 API 사용 경고
        if store_id or params:
            self.logger.warning("store_id와 params는 새로운 API에서 사용되지 않습니다. object_id 기반 연결을 사용합니다.")
    
    def start(self, object_id: str = None, retry_timeout: int = 3000) -> None:
        """
        SSE 연결 시작
        
        Args:
            object_id: 특정 오브제 ID (None이면 모든 오브제 연결)
            retry_timeout: 재연결 시도 간격(밀리초)
        """
        # 기존 연결 정리
        if self.sse_client and self.sse_client.is_running():
            self.logger.info("기존 SSE 연결을 종료합니다.")
            self.sse_client.stop()
        
        # 새 클라이언트 생성
        self.sse_client = SSEEventClient(
            base_url=self.config['base_url'],
            headers=self.config['headers']
        )
        
        # 시그널 연결
        self.sse_client.event_received.connect(self._forward_event)
        self.sse_client.connection_error.connect(self._forward_error)
        self.sse_client.connection_established.connect(self._forward_established)
        self.sse_client.connection_closed.connect(self._forward_closed)
        
        # 클라이언트 시작
        self.sse_client.start(object_id, retry_timeout)
        self.logger.info("SSE 클라이언트가 시작되었습니다.")
    
    def stop(self, object_id: str = None) -> None:
        """
        SSE 연결 중지
        
        Args:
            object_id: 특정 오브제 ID (None이면 모든 연결 중지)
        """
        if self.sse_client:
            self.sse_client.stop(object_id)
            self.logger.info("SSE 연결이 중지되었습니다.")
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """
        이벤트 핸들러 등록
        
        Args:
            event_type: 이벤트 타입
            handler: 핸들러 함수 (object_id, data를 매개변수로 받음)
        """
        if self.sse_client:
            self.sse_client.register_handler(event_type, handler)
            self.logger.info(f"이벤트 핸들러 등록: {event_type}")
        else:
            self.logger.warning("SSE 클라이언트가 초기화되지 않았습니다. 핸들러를 등록할 수 없습니다.")
    
    def is_connected(self, object_id: str = None) -> bool:
        """
        현재 연결 상태 반환
        
        Args:
            object_id: 특정 오브제 ID (None이면 전체 연결 상태)
            
        Returns:
            bool: 연결 상태
        """
        return self.sse_client is not None and self.sse_client.is_running(object_id)
    
    def get_connected_objects(self) -> List[str]:
        """현재 연결된 오브제 ID 목록 반환"""
        if self.sse_client:
            return self.sse_client.get_connected_objects()
        return []
    
    def get_connection_status(self) -> Dict[str, bool]:
        """모든 오브제의 연결 상태 반환"""
        if self.sse_client:
            return self.sse_client.get_connection_status()
        return {}
    
    # 시그널 전달 메서드들 (새로운 API 구조에 맞게 업데이트)
    @Slot(str, str, dict)
    def _forward_event(self, object_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """이벤트 시그널 전달"""
        self.event_received.emit(object_id, event_type, data)
    
    @Slot(str, str)
    def _forward_error(self, object_id: str, error_message: str) -> None:
        """에러 시그널 전달"""
        self.connection_error.emit(object_id, error_message)
    
    @Slot(str)
    def _forward_established(self, object_id: str) -> None:
        """연결 성공 시그널 전달"""
        self.connection_established.emit(object_id)
    
    @Slot(str)
    def _forward_closed(self, object_id: str) -> None:
        """연결 종료 시그널 전달"""
        self.connection_closed.emit(object_id)
    
    # 하위 호환성을 위한 메서드들
    def start_legacy(self, retry_timeout: int = 3000) -> None:
        """이전 버전 호환성을 위한 시작 메서드"""
        self.logger.warning("start_legacy() 사용됨. start()를 사용하세요.")
        self.start(None, retry_timeout)
    
    def connect_legacy_signals(self, event_slot, error_slot, established_slot, closed_slot):
        """이전 버전 호환성을 위한 시그널 연결"""
        self.logger.warning("Legacy 시그널 연결이 사용됨. 새로운 시그널 구조를 사용하세요.")
        
        # 이전 시그널 구조에 맞게 변환
        def legacy_event_adapter(object_id: str, event_type: str, data: Dict[str, Any]):
            # 이전 구조: (event_type, data)
            event_slot(event_type, data)
        
        def legacy_error_adapter(object_id: str, error_message: str):
            # 이전 구조: (error_message)
            error_slot(error_message)
        
        def legacy_established_adapter(object_id: str):
            # 이전 구조: ()
            established_slot()
        
        def legacy_closed_adapter(object_id: str):
            # 이전 구조: ()
            closed_slot()
        
        self.event_received.connect(legacy_event_adapter)
        self.connection_error.connect(legacy_error_adapter)
        self.connection_established.connect(legacy_established_adapter)
        self.connection_closed.connect(legacy_closed_adapter) 