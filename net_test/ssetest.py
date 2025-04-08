import requests
import json
import logging
from typing import Callable, Dict, Optional, Any
import sseclient  # sseclient-py 패키지 임포트


class SSEEventClient:
    """
    Server-Sent Events 클라이언트 클래스
    서버로부터 실시간 이벤트를 수신하고 처리합니다.
    """
    
    def __init__(self, url: str, store_id: str = None, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None):
        """
        SSE 클라이언트 초기화
        
        Args:
            url: SSE 서버 엔드포인트 URL
            store_id: 요청에 포함할 상점 ID
            headers: 요청에 사용할 HTTP 헤더 (선택사항)
            params: 추가적인 GET 파라미터 (선택사항)
        """
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
        
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        특정 이벤트 타입에 대한 핸들러 등록
        
        Args:
            event_type: 처리할 이벤트 타입
            handler: 이벤트 데이터를 처리할 콜백 함수
        """
        self.event_handlers[event_type] = handler
    
    def check_cache_status(self, base_url: str = None) -> Dict[str, Any]:
        """
        서버의 캐시 상태를 확인합니다.
        
        Args:
            base_url: 캐시 확인 API의 베이스 URL (기본값: SSE URL의 도메인)
            
        Returns:
            캐시 상태 정보가 포함된 딕셔너리
        """
        # 베이스 URL이 지정되지 않은 경우, SSE URL에서 도메인 추출
        if not base_url:
            from urllib.parse import urlparse
            parsed_url = urlparse(self.url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        cache_check_url = f"{base_url}/v1/cache-check"
        print(f"\n[캐시 확인] URL: {cache_check_url}")
        self.logger.info(f"캐시 상태 확인 중: {cache_check_url}")
        
        try:
            # Accept 헤더를 추가하여 요청
            headers = {'Accept': '*/*'}
            print(f"[캐시 확인] 요청 헤더: {headers}")
            response = requests.get(cache_check_url, headers=headers)
            response.raise_for_status()
            
            cache_status = response.json()
            print(f"[캐시 확인] 응답 상태 코드: {response.status_code}")
            self.logger.info(f"캐시 상태: {cache_status}")
            
            # 이 부분이 매우 중요합니다 - 결과를 명확하게 터미널에 출력
            print(f"\n===== 서버 캐시 상태 =====")
            print(json.dumps(cache_status, indent=2, ensure_ascii=False))
            print("========================\n")
            
            return cache_status
            
        except requests.RequestException as e:
            error_msg = f"캐시 상태 확인 오류: {str(e)}"
            print(f"[캐시 확인 오류] {error_msg}")
            self.logger.error(error_msg)
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            error_msg = f"캐시 상태 응답 파싱 오류: {str(e)}"
            print(f"[캐시 확인 오류] {error_msg}")
            self.logger.error(error_msg)
            return {"error": "응답 파싱 오류", "response": response.text}
        
    def start(self, retry_timeout: int = 3000) -> None:
        """
        SSE 연결 시작 및 이벤트 수신 처리
        
        Args:
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        try:
            self.logger.info(f"SSE 서버 {self.url}에 연결 중... (파라미터: {self.params})")
            response = requests.get(self.url, headers=self.headers, params=self.params, stream=True)
            response.raise_for_status()  # HTTP 오류 확인
            
            client = sseclient.SSEClient(response)
            
            for event in client.events():
                self._process_event(event)
                
        except requests.RequestException as e:
            self.logger.error(f"SSE 연결 오류: {str(e)}")
            self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도...")
            import time
            time.sleep(retry_timeout/1000)
            self.start(retry_timeout)  # 재연결 시도
    
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


# 사용 예제
if __name__ == "__main__":
    # 로깅 설정 (DEBUG로 변경)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n===== SSEEventClient 시작 =====")
    
    # SSE 클라이언트 인스턴스 생성
    sse_client = SSEEventClient(
        url="https://robot-monitor-dev.systemiic.com/v1/service/stores/event-sources?storeId=store123&pcId=pc1",
        headers={"Authorization": "Bearer your-token-here"},
    )
    
    # 캐시 상태 확인
    print("\n캐시 상태를 확인합니다...")
    cache_status = sse_client.check_cache_status()
    
    # 이벤트 핸들러 등록
    def handle_sse(data):
        print(f"SSE 이벤트 수신: {data}")
    
    def handle_message(data):
        print(f"기본 메시지 수신: {data}")
    
    # "sse" 이벤트 타입에 대한 핸들러 등록
    sse_client.register_handler("sse", handle_sse)
    
    # 기본 메시지 타입에 대한 핸들러도 등록 (fallback)
    sse_client.register_handler("message", handle_message)
    
    print("\nSSE 연결을 시작합니다...")
    # SSE 연결 시작
    sse_client.start()