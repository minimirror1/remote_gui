import requests
import json
import logging
import threading
import time
from typing import Callable, Dict, Optional, Any, List
import sseclient

class RobotMonitorClient:
    """
    Robot Monitor API 클라이언트 클래스
    서버와 통신하여 이벤트 송수신 처리
    """
    
    # 서버 기본 URL
    BASE_URL = "https://robot-monitor-dev.systemiic.com"
    
    # API 엔드포인트
    ENDPOINTS = {
        "event_sources": "/v1/service/stores/event-sources",  # SSE 이벤트 소스 (GET)
        "send_event": "/v1/service/stores/send-event",        # 제어 이벤트 전송 (POST)
        "log_event": "/v1/service/stores/log",                # 로그 이벤트 전송 (POST)
        "store_list": "/v1/stores",                           # 매장 목록 조회 (GET)
        "pc_list": "/v1/service/pc/list",                     # PC 목록 조회 (GET)
    }
    
    # 이벤트 타입
    EVENT_TYPES = {
        "ON": "ON",          # 전원 켜기
        "OFF": "OFF",        # 전원 끄기
        "REBOOT": "REBOOT"   # 재부팅
    }
    
    def __init__(self, store_id: str, pc_id: str, token: str = None):
        """
        Robot Monitor 클라이언트 초기화
        
        Args:
            store_id: 매장 ID
            pc_id: PC ID
            token: 인증 토큰 (선택사항)
        """
        self.store_id = store_id
        self.pc_id = pc_id
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 토큰이 제공된 경우 인증 헤더 추가
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
            
        self.event_handlers = {}
        self.logger = logging.getLogger(__name__)
        
        # SSE 클라이언트 관련 변수
        self._sse_client = None
        self._sse_thread = None
        self._is_running = False
    
    def set_token(self, token: str) -> None:
        """인증 토큰 설정"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    # ===== REST API 메서드 =====
    
    def send_control_event(self, object_id: str, event: str) -> bool:
        """
        제어 이벤트 전송 (ON/OFF/REBOOT)
        
        Args:
            object_id: 제어 대상 객체 ID
            event: 이벤트 타입 (ON, OFF, REBOOT)
            
        Returns:
            성공 여부 (True/False)
        """
        # 이벤트 타입 검증
        if event not in self.EVENT_TYPES:
            self.logger.error(f"지원하지 않는 이벤트 타입: {event}")
            return False
        
        url = f"{self.BASE_URL}{self.ENDPOINTS['send_event']}"
        payload = {
            "storeId": self.store_id,
            "pcId": self.pc_id,
            "objectId": object_id,
            "event": event
        }
        
        try:
            self.logger.info(f"제어 이벤트 전송: {payload}")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"제어 이벤트 전송 성공: {object_id} / {event}")
            print(f"제어 이벤트 전송 성공: {object_id} / {event}")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"제어 이벤트 전송 실패: {str(e)}")
            print(f"제어 이벤트 전송 실패: {str(e)}")
            return False
    
    def send_log_event(self, object_id: str, object_status: str, 
                     operating_status: str = None, error: str = None, 
                     electric_current: str = None, config: Dict = None) -> bool:
        """
        로그 이벤트 전송
        
        Args:
            object_id: 객체 ID
            object_status: 객체 상태 (ON/OFF)
            operating_status: 작동 상태 (PLAY/STOP/REPEAT) (선택사항)
            error: 에러 메시지 (선택사항)
            electric_current: 전류 정보 (선택사항)
            config: 설정 정보 (선택사항)
            
        Returns:
            성공 여부 (True/False)
        """
        url = f"{self.BASE_URL}{self.ENDPOINTS['log_event']}"
        
        # 객체 상태 정보 구성
        object_info = {
            "objectId": object_id,
            "objectStatus": object_status
        }
        
        # 선택적 필드 추가
        if operating_status:
            object_info["operatingStatus"] = operating_status
        if error:
            object_info["error"] = error
        if electric_current:
            object_info["electricCurrent"] = electric_current
        if config:
            object_info["config"] = config
        
        payload = {
            "storeId": self.store_id,
            "pcId": self.pc_id,
            "objectInfo": object_info,
            "event": object_status  # 이벤트 타입은 객체 상태와 동일하게 설정
        }
        
        try:
            self.logger.info(f"로그 이벤트 전송: {payload}")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"로그 이벤트 전송 성공: {object_id} / {object_status}")
            print(f"로그 이벤트 전송 성공: {object_id} / {object_status}")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"로그 이벤트 전송 실패: {str(e)}")
            print(f"로그 이벤트 전송 실패: {str(e)}")
            return False
    
    def get_store_list(self) -> Optional[Dict]:
        """
        매장 목록 조회
        
        Returns:
            매장 목록 정보 (실패 시 None)
        """
        url = f"{self.BASE_URL}{self.ENDPOINTS['store_list']}"
        params = {"request": {"storeId": self.store_id}}
        
        try:
            self.logger.info(f"매장 목록 요청: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"매장 목록 조회 성공")
            print(f"매장 목록 조회 성공: {data}")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"매장 목록 조회 실패: {str(e)}")
            print(f"매장 목록 조회 실패: {str(e)}")
            return None
    
    def get_pc_list(self) -> Optional[Dict]:
        """
        PC 목록 조회
        
        Returns:
            PC 목록 정보 (실패 시 None)
        """
        url = f"{self.BASE_URL}{self.ENDPOINTS['pc_list']}"
        params = {"request": {"storeId": self.store_id}}
        
        try:
            self.logger.info(f"PC 목록 요청: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"PC 목록 조회 성공")
            print(f"PC 목록 조회 성공: {data}")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"PC 목록 조회 실패: {str(e)}")
            print(f"PC 목록 조회 실패: {str(e)}")
            return None
    
    # ===== SSE 이벤트 수신 메서드 =====
    
    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        특정 이벤트 타입에 대한 핸들러 등록
        
        Args:
            event_type: 처리할 이벤트 타입
            handler: 이벤트 데이터를 처리할 콜백 함수
        """
        self.event_handlers[event_type] = handler
        self.logger.info(f"이벤트 핸들러 등록: {event_type}")
    
    def start_event_listener(self) -> None:
        """
        이벤트 수신 리스너 시작 (비동기)
        별도 스레드에서 SSE 연결 및 이벤트 처리
        """
        if self._is_running:
            self.logger.warning("이벤트 리스너가 이미 실행 중입니다.")
            return
            
        self._is_running = True
        self._sse_thread = threading.Thread(
            target=self._run_sse_client,
            daemon=True  # 메인 스레드 종료 시 함께 종료
        )
        self._sse_thread.start()
        self.logger.info("이벤트 리스너가 시작되었습니다.")
        print("이벤트 리스너가 시작되었습니다.")
    
    def stop_event_listener(self) -> None:
        """이벤트 수신 리스너 중지"""
        self._is_running = False
        
        # SSE 클라이언트 종료 시도
        if self._sse_client:
            try:
                # sseclient 종료 로직 (response.close() 호출)
                self._sse_client._http_response.close()
            except:
                pass
        
        # 스레드가 종료될 때까지 최대 5초 대기
        if self._sse_thread and self._sse_thread.is_alive():
            self._sse_thread.join(timeout=5.0)
        
        self.logger.info("이벤트 리스너가 중지되었습니다.")
        print("이벤트 리스너가 중지되었습니다.")
    
    def _run_sse_client(self, retry_timeout: int = 3000) -> None:
        """
        백그라운드 스레드에서 SSE 클라이언트 실행
        
        Args:
            retry_timeout: 재연결 시도 간격(밀리초)
        """
        # Accept 헤더를 text/event-stream으로 설정 (SSE 연결 필수)
        sse_headers = self.headers.copy()
        sse_headers["Accept"] = "text/event-stream"
        
        while self._is_running:
            try:
                # SSE 연결 URL 구성
                url = f"{self.BASE_URL}{self.ENDPOINTS['event_sources']}"
                params = {
                    "storeId": self.store_id,
                    "pcId": self.pc_id
                }
                
                self.logger.info(f"SSE 서버 연결 시도: {url} (파라미터: {params})")
                print(f"SSE 서버 연결 시도: {url} (파라미터: {params})")
                
                # 스트리밍 모드로 GET 요청
                response = requests.get(url, headers=sse_headers, params=params, stream=True)
                response.raise_for_status()
                
                # SSE 클라이언트 생성 및 이벤트 수신
                self._sse_client = sseclient.SSEClient(response)
                self.logger.info("SSE 서버에 연결되었습니다.")
                print("SSE 서버에 연결되었습니다.")
                
                # 이벤트 수신 및 처리
                for event in self._sse_client.events():
                    if not self._is_running:
                        break
                    self._process_event(event)
                    
            except requests.RequestException as e:
                self.logger.error(f"SSE 연결 오류: {str(e)}")
                print(f"SSE 연결 오류: {str(e)}")
                
                # 재연결 시도 전 대기
                if self._is_running:
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도...")
                    print(f"{retry_timeout/1000}초 후 재연결 시도...")
                    time.sleep(retry_timeout/1000)
                    
            except Exception as e:
                self.logger.error(f"SSE 처리 중 예상치 못한 오류: {str(e)}")
                print(f"SSE 처리 중 예상치 못한 오류: {str(e)}")
                
                # 재연결 시도 전 대기
                if self._is_running:
                    self.logger.info(f"{retry_timeout/1000}초 후 재연결 시도...")
                    print(f"{retry_timeout/1000}초 후 재연결 시도...")
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
            
            # 이벤트 정보 로깅
            self.logger.info(f"이벤트 수신: {event_type} - {data}")
            print(f"이벤트 수신: {event_type} - {data}")
            
            # 등록된 핸들러 호출
            if event_type in self.event_handlers:
                self.logger.debug(f"이벤트 핸들러 호출: {event_type}")
                self.event_handlers[event_type](data)
            else:
                self.logger.debug(f"처리되지 않은 이벤트 타입: {event_type}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"JSON 파싱 오류: {event.data}")
            print(f"JSON 파싱 오류: {event.data}")
            
            # JSON이 아닌 경우 원본 데이터 전달
            if event_type in self.event_handlers:
                self.event_handlers[event_type](event.data)


# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 클라이언트 인스턴스 생성
    client = RobotMonitorClient(
        store_id="store123",
        pc_id="pc1",
        token="your-token-here"  # 실제 토큰으로 변경
    )
    
    # 이벤트 핸들러 등록
    def handle_control_event(data):
        print(f"제어 이벤트 수신: {data}")
        # 실제 구현에서는 여기서 로봇이나 디바이스 제어 기능 호출
        # 예: robot_controller.execute_command(data["command"])
    
    def handle_message(data):
        print(f"일반 메시지 수신: {data}")
        # 실제 구현에서는 UI 업데이트나 로깅 등의 작업 수행
        # 예: ui_manager.update_status(data)
    
    # 이벤트 핸들러 등록
    client.register_event_handler("control", handle_control_event)
    client.register_event_handler("message", handle_message)
    
    # 이벤트 리스너 시작
    client.start_event_listener()
    
    try:
        # 샘플 이벤트 전송
        client.send_control_event("robot1", "ON")
        
        # 프로그램 종료 방지 (실제 애플리케이션에서는 필요 없음)
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # 이벤트 리스너 중지
        client.stop_event_listener()
        print("프로그램이 종료되었습니다.") 