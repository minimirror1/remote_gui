import requests
import json
import logging
from typing import Callable, Dict, Optional, Any, List
import sseclient  # sseclient-py 패키지 임포트
import threading
import time


class SSEEventClient:
    """
    Server-Sent Events 클라이언트 클래스
    서버로부터 실시간 이벤트를 수신하고 처리합니다.
    여러 오브제의 전원 상태 이벤트를 동시에 처리할 수 있습니다.
    """
    
    def __init__(self, base_url: str = "https://robot-monitor-dev.systemiic.com", headers: Optional[Dict[str, str]] = None):
        """
        SSE 클라이언트 초기화
        
        Args:
            base_url: SSE 서버 베이스 URL
            headers: 요청에 사용할 HTTP 헤더 (선택사항)
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        
        # SSE 연결을 위한 Accept 헤더 설정
        if 'Accept' not in self.headers:
            self.headers['Accept'] = 'text/event-stream'
            
        self.event_handlers = {}
        self.logger = logging.getLogger(__name__)
        
        # 다중 SSE 연결 관리
        self.sse_connections: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        
        # DeviceStatusManager 연결
        self.device_manager = None
        self._setup_device_manager()
        
    def _setup_device_manager(self):
        """DeviceStatusManager 연결 설정"""
        try:
            import sys
            import os
            # src 디렉토리를 Python 경로에 추가
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            src_dir = os.path.join(parent_dir, 'src')
            if src_dir not in sys.path:
                sys.path.append(src_dir)
            
            from device_status_manager import DeviceStatusManager
            self.device_manager = DeviceStatusManager.get_instance()
            self.logger.info("DeviceStatusManager 연결 완료")
            
        except Exception as e:
            self.logger.error(f"DeviceStatusManager 연결 실패: {e}")
            self.device_manager = None
    
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
    
    def check_cache_status(self) -> Dict[str, Any]:
        """
        서버의 캐시 상태를 확인합니다.
            
        Returns:
            캐시 상태 정보가 포함된 딕셔너리
        """
        cache_check_url = f"{self.base_url}/v1/cache-check"
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
            
            # 결과를 명확하게 터미널에 출력
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
    
    def start_single_object_sse(self, object_id: str, retry_timeout: int = 3000) -> None:
        """
        단일 오브제에 대한 SSE 연결 시작
        
        Args:
            object_id: 오브제 ID
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        sse_url = f"{self.base_url}/v1/service/objects/{object_id}/power"
        
        try:
            self.logger.info(f"SSE 서버 연결 중: {sse_url}")
            print(f"[SSE 연결] Object ID: {object_id}")
            
            response = requests.get(sse_url, headers=self.headers, stream=True)
            response.raise_for_status()  # HTTP 오류 확인
            
            client = sseclient.SSEClient(response)
            
            # 연결 중단 플래그 확인하면서 이벤트 수신
            for event in client.events():
                if self.stop_flags.get(object_id, threading.Event()).is_set():
                    self.logger.info(f"SSE 연결 중단 요청됨: {object_id}")
                    break
                    
                self._process_event(object_id, event)
                
        except requests.RequestException as e:
            self.logger.error(f"SSE 연결 오류 (Object {object_id}): {str(e)}")
            if not self.stop_flags.get(object_id, threading.Event()).is_set():
                self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도... (Object {object_id})")
                time.sleep(retry_timeout/1000)
                if not self.stop_flags.get(object_id, threading.Event()).is_set():
                    self.start_single_object_sse(object_id, retry_timeout)  # 재연결 시도
    
    def start_all_objects_sse(self, retry_timeout: int = 3000) -> None:
        """
        모든 오브제에 대한 SSE 연결 시작
        
        Args:
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        object_ids = self.get_object_ids()
        
        if not object_ids:
            self.logger.warning("연결할 오브제가 없습니다")
            print("연결할 오브제가 없습니다. DeviceStatusManager를 확인하세요.")
            return
        
        print(f"\n===== 다중 SSE 연결 시작 =====")
        print(f"연결할 오브제 수: {len(object_ids)}")
        print(f"오브제 ID 목록: {object_ids}")
        print("================================\n")
        
        for object_id in object_ids:
            self.start_object_sse(object_id, retry_timeout)
    
    def start_object_sse(self, object_id: str, retry_timeout: int = 3000) -> None:
        """
        특정 오브제에 대한 SSE 연결을 별도 스레드에서 시작
        
        Args:
            object_id: 오브제 ID
            retry_timeout: 연결 끊김 시 재연결 시도 간격(밀리초)
        """
        # 이미 연결된 경우 중단
        if object_id in self.sse_connections:
            self.logger.warning(f"이미 연결된 오브제: {object_id}")
            return
        
        # 중단 플래그 초기화
        self.stop_flags[object_id] = threading.Event()
        
        # SSE 연결을 별도 스레드에서 실행
        thread = threading.Thread(
            target=self.start_single_object_sse,
            args=(object_id, retry_timeout),
            name=f"SSE-{object_id}",
            daemon=True
        )
        
        self.sse_connections[object_id] = thread
        thread.start()
        
        self.logger.info(f"SSE 스레드 시작됨: {object_id}")
    
    def stop_object_sse(self, object_id: str) -> None:
        """
        특정 오브제의 SSE 연결 중단
        
        Args:
            object_id: 오브제 ID
        """
        if object_id in self.stop_flags:
            self.stop_flags[object_id].set()
            self.logger.info(f"SSE 연결 중단 신호 전송: {object_id}")
        
        if object_id in self.sse_connections:
            thread = self.sse_connections[object_id]
            thread.join(timeout=2.0)  # 2초 대기
            del self.sse_connections[object_id]
            self.logger.info(f"SSE 스레드 정리됨: {object_id}")
    
    def stop_all_sse(self) -> None:
        """모든 SSE 연결 중단"""
        print("\n===== 모든 SSE 연결 중단 =====")
        
        for object_id in list(self.sse_connections.keys()):
            self.stop_object_sse(object_id)
        
        # 정리
        self.sse_connections.clear()
        self.stop_flags.clear()
        
        print("모든 SSE 연결이 중단되었습니다.")
    
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


# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n===== 다중 오브제 SSEEventClient 시작 =====")
    
    # SSE 클라이언트 인스턴스 생성 (Bearer 토큰 제거)
    sse_client = SSEEventClient()
    
    # 캐시 상태 확인
    print("\n캐시 상태를 확인합니다...")
    cache_status = sse_client.check_cache_status()
    
    # 이벤트 핸들러 등록
    def handle_power_event(object_id: str, data: Dict[str, Any]) -> None:
        print(f"[전원 이벤트] Object {object_id}: {data}")
    
    def handle_message(object_id: str, data: Dict[str, Any]) -> None:
        print(f"[기본 메시지] Object {object_id}: {data}")
    
    # 이벤트 핸들러 등록
    sse_client.register_handler("power", handle_power_event)
    sse_client.register_handler("message", handle_message)
    
    print("\n모든 오브제에 대한 SSE 연결을 시작합니다...")
    
    try:
        # 모든 오브제에 대한 SSE 연결 시작
        sse_client.start_all_objects_sse()
        
        # 메인 스레드에서 대기 (사용자 입력 대기)
        input("연결 중... 종료하려면 Enter를 누르세요.")
        
    except KeyboardInterrupt:
        print("\n사용자 중단 요청")
    finally:
        # 모든 연결 정리
        sse_client.stop_all_sse()
        print("프로그램을 종료합니다.")