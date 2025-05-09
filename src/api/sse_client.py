import requests
import json
import logging
from typing import Callable, Dict, Optional, Any
import sseclient  # sseclient-py 패키지 임포트
import threading
from PySide6.QtCore import QObject, Signal


class SSEEventClient(QObject):
    """
    Server-Sent Events 클라이언트 클래스
    서버로부터 실시간 이벤트를 수신하고 처리합니다.
    """
    # 이벤트 시그널 정의
    event_received = Signal(str, dict)  # 이벤트 타입, 데이터
    connection_error = Signal(str)      # 에러 메시지
    connection_established = Signal()   # 연결 성공 시
    connection_closed = Signal()        # 연결 종료 시
    
    def __init__(self, url: str, store_id: str = None, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None, parent=None):
        """
        SSE 클라이언트 초기화
        
        Args:
            url: SSE 서버 엔드포인트 URL
            store_id: 요청에 포함할 상점 ID
            headers: 요청에 사용할 HTTP 헤더 (선택사항)
            params: 추가적인 GET 파라미터 (선택사항)
        """
        super().__init__(parent)
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        
        # storeId가 제공된 경우 GET 파라미터에 추가
        if store_id:
            self.params['storeId'] = store_id
            
        # SSE 연결을 위한 Accept 헤더 설정
        if 'Accept' not in self.headers:
            self.headers['Accept'] = 'text/event-stream'
        self.event_handlers = {}
        self.logger = logging.getLogger(__name__)
        
        # 스레드 관련 변수
        self._thread = None
        self._is_running = False
        self._client = None
        
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        특정 이벤트 타입에 대한 핸들러 등록
        
        Args:
            event_type: 처리할 이벤트 타입
            handler: 이벤트 데이터를 처리할 콜백 함수
        """
        self.event_handlers[event_type] = handler
        
    def start(self, retry_timeout: int = 3000) -> None:
        """
        SSE 연결 시작 - 백그라운드 스레드에서 실행
        
        Args:
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        if self._thread and self._thread.is_alive():
            self.logger.warning("SSE 클라이언트가 이미 실행 중입니다.")
            return
            
        self._is_running = True
        self._thread = threading.Thread(
            target=self._run_sse_client,
            args=(retry_timeout,),
            daemon=True  # 메인 스레드 종료 시 함께 종료
        )
        self._thread.start()
        
    def stop(self) -> None:
        """SSE 연결 중지"""
        self._is_running = False
        if self._client:
            try:
                self._client.close()
            except:
                pass
        
        # 스레드가 종료될 때까지 최대 5초 대기
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self.connection_closed.emit()
        self.logger.info("SSE 연결 종료됨")
    
    def _run_sse_client(self, retry_timeout: int) -> None:
        """
        백그라운드 스레드에서 SSE 클라이언트 실행
        
        Args:
            retry_timeout: 재연결 시도 간격(밀리초)
        """
        while self._is_running:
            try:
                self.logger.info(f"SSE 서버 {self.url}에 연결 중... (파라미터: {self.params})")
                response = requests.get(self.url, headers=self.headers, params=self.params, stream=True)
                response.raise_for_status()  # HTTP 오류 확인
                
                self._client = sseclient.SSEClient(response)
                self.connection_established.emit()
                self.logger.info("SSE 서버에 연결되었습니다.")
                
                for event in self._client.events():
                    if not self._is_running:
                        break
                    self._process_event(event)
                    
            except requests.RequestException as e:
                self.logger.error(f"SSE 연결 오류: {str(e)}")
                self.connection_error.emit(str(e))
                
                # 재연결 시도 전 대기
                if self._is_running:
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도...")
                    import time
                    time.sleep(retry_timeout/1000)
                    
            except Exception as e:
                self.logger.error(f"SSE 처리 중 예상치 못한 오류: {str(e)}")
                self.connection_error.emit(f"예상치 못한 오류: {str(e)}")
                
                # 재연결 시도 전 대기
                if self._is_running:
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도...")
                    import time
                    time.sleep(retry_timeout/1000)
    
    def _process_event(self, event):
        """
        수신된 SSE 이벤트 처리
        
        Args:
            event: SSE 이벤트 객체
        """
        event_type = event.event or 'message'
        try:
            # 이벤트 데이터 파싱
            data = json.loads(event.data) if event.data else {}
            
            # 시그널 발생
            self.event_received.emit(event_type, data)
            
            # 등록된 핸들러 호출
            if event_type in self.event_handlers:
                self.logger.debug(f"이벤트 수신: {event_type}")
                self.event_handlers[event_type](data)
            else:
                self.logger.debug(f"처리되지 않은 이벤트 타입: {event_type}, 데이터: {data}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"JSON 파싱 오류: {event.data}")
            # JSON이 아닌 경우 원본 데이터 전달
            if event_type in self.event_handlers:
                self.event_handlers[event_type](event.data)
    
    def is_running(self) -> bool:
        """현재 연결 상태 반환"""
        return self._is_running and self._thread and self._thread.is_alive() 