import threading
import logging
from PySide6.QtCore import QObject, Signal, Slot
from typing import Optional, Dict, Any, List
from src.api.sse_client import SSEEventClient

class SSEManager(QObject):
    """SSE 연결 관리자 클래스 (싱글톤)"""
    
    # 시그널 정의
    event_received = Signal(str, dict)  # 이벤트 타입, 데이터
    connection_error = Signal(str)      # 에러 메시지
    connection_established = Signal()   # 연결 성공 시
    connection_closed = Signal()        # 연결 종료 시
    
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
            'url': '',
            'store_id': '',
            'headers': {},
            'params': {}
        }
    
    def configure(self, url: str, store_id: str = None, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None) -> None:
        """SSE 클라이언트 설정"""
        self.config.update({
            'url': url,
            'store_id': store_id,
            'headers': headers or {},
            'params': params or {}
        })
        
        self.logger.info(f"SSE 매니저 설정 완료: URL={url}, Store ID={store_id}")
    
    def start(self, retry_timeout: int = 3000) -> None:
        """SSE 연결 시작"""
        # 기존 연결 정리
        if self.sse_client and self.sse_client.is_running():
            self.logger.info("기존 SSE 연결을 종료합니다.")
            self.sse_client.stop()
        
        # 설정 검증
        if not self.config['url']:
            self.logger.error("SSE URL이 설정되지 않았습니다.")
            self.connection_error.emit("SSE URL이 설정되지 않았습니다.")
            return
        
        # 새 클라이언트 생성
        self.sse_client = SSEEventClient(
            url=self.config['url'],
            store_id=self.config['store_id'],
            headers=self.config['headers'],
            params=self.config['params']
        )
        
        # 시그널 연결
        self.sse_client.event_received.connect(self._forward_event)
        self.sse_client.connection_error.connect(self._forward_error)
        self.sse_client.connection_established.connect(self._forward_established)
        self.sse_client.connection_closed.connect(self._forward_closed)
        
        # 클라이언트 시작
        self.sse_client.start(retry_timeout)
        self.logger.info("SSE 클라이언트가 시작되었습니다.")
    
    def stop(self) -> None:
        """SSE 연결 중지"""
        if self.sse_client:
            self.sse_client.stop()
            self.logger.info("SSE 연결이 중지되었습니다.")
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """이벤트 핸들러 등록"""
        if self.sse_client:
            self.sse_client.register_handler(event_type, handler)
            self.logger.info(f"이벤트 핸들러 등록: {event_type}")
        else:
            self.logger.warning("SSE 클라이언트가 초기화되지 않았습니다. 핸들러를 등록할 수 없습니다.")
    
    def is_connected(self) -> bool:
        """현재 연결 상태 반환"""
        return self.sse_client is not None and self.sse_client.is_running()
    
    @Slot(str, dict)
    def _forward_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """이벤트 시그널 전달"""
        self.event_received.emit(event_type, data)
    
    @Slot(str)
    def _forward_error(self, error_message: str) -> None:
        """에러 시그널 전달"""
        self.connection_error.emit(error_message)
    
    @Slot()
    def _forward_established(self) -> None:
        """연결 성공 시그널 전달"""
        self.connection_established.emit()
    
    @Slot()
    def _forward_closed(self) -> None:
        """연결 종료 시그널 전달"""
        self.connection_closed.emit() 