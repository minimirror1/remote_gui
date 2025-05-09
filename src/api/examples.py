"""
REST API 클라이언트 사용 예제
"""

from src.api.api_manager import ApiManager
from src.api.api_client import ApiClient
from src.api.models.response_model import ApiResponse
from src.api.sse_client import SSEEventClient
from src.api.sse_manager import SSEManager
from PySide6.QtCore import QObject, Signal, Slot


class ApiExamples(QObject):
    """API 사용 예제 클래스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 방법 1: ApiManager 싱글톤 인스턴스 사용
        self.api_manager = ApiManager.get_instance()
        self.api_manager.set_base_url("https://api.example.com")
        
        # 방법 2: ApiClient 인스턴스 직접 사용
        self.api_client = ApiClient(base_url="https://api.example.com")
    
    def example_using_manager(self):
        """ApiManager 사용 예제"""
        # ApiManager 사용 시, 시그널 연결이 필요합니다.
        self.api_manager.request_completed.connect(self.handle_response)
        self.api_manager.request_error.connect(self.handle_error)
        
        # GET 요청 보내기
        self.api_manager.get("/users", params={"page": 1, "limit": 10})
        
        # POST 요청 보내기
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secure_password"
        }
        self.api_manager.post("/users", data=user_data)
    
    def example_using_client(self):
        """ApiClient 사용 예제"""
        # 요청 보내기 (콜백 함수 직접 지정)
        self.api_client.get(
            "/users", 
            params={"page": 1, "limit": 10},
            success_callback=self.handle_response,
            error_callback=self.handle_error
        )
        
        # POST 요청 보내기
        user_data = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "password": "another_secure_password"
        }
        self.api_client.post(
            "/users", 
            data=user_data,
            success_callback=self.handle_response,
            error_callback=self.handle_error
        )
    
    def example_using_sse(self):
        """SSE 클라이언트 사용 예제"""
        # SSE 매니저 사용 (싱글톤)
        sse_manager = SSEManager.get_instance()
        
        # SSE 이벤트 처리 함수
        @Slot(str, dict)
        def handle_event(event_type, data):
            print(f"SSE 이벤트 수신: 타입={event_type}, 데이터={data}")
        
        # 연결 상태 변화 처리
        @Slot()
        def handle_connected():
            print("SSE 서버에 연결되었습니다.")
        
        @Slot(str)
        def handle_error(error_msg):
            print(f"SSE 연결 오류: {error_msg}")
        
        # 시그널 연결
        sse_manager.event_received.connect(handle_event)
        sse_manager.connection_established.connect(handle_connected)
        sse_manager.connection_error.connect(handle_error)
        
        # SSE 설정 및 시작
        sse_manager.configure(
            url="https://robot-monitor-dev.systemiic.com/v1/service/stores/event-sources",
            store_id="store123",
            params={"pcId": "pc1"},
            headers={"Authorization": "Bearer your-token-here"}
        )
        
        # 특정 이벤트 타입에 대한 핸들러 등록 (선택사항)
        sse_manager.register_handler("sse", lambda data: print(f"SSE 이벤트 처리: {data}"))
        sse_manager.register_handler("message", lambda data: print(f"메시지 이벤트 처리: {data}"))
        
        # SSE 연결 시작
        sse_manager.start()
        
        # 연결 종료 예시 (실제로는 호출하지 않음)
        # sse_manager.stop()
    
    @Slot(dict)
    def handle_response(self, data):
        """API 응답 처리"""
        # 응답 객체로 변환
        response = ApiResponse.from_dict(data)
        
        if response.success:
            print(f"요청 성공: {response.message}")
            print(f"응답 데이터: {response.data}")
        else:
            print(f"요청 실패: {response.message}")
    
    @Slot(str)
    def handle_error(self, error_msg):
        """API 에러 처리"""
        print(f"API 오류: {error_msg}")


def run_examples():
    """예제 실행 함수"""
    examples = ApiExamples()
    
    print("=== ApiManager 사용 예제 ===")
    examples.example_using_manager()
    
    print("\n=== ApiClient 사용 예제 ===")
    examples.example_using_client()
    
    print("\n=== SSE 클라이언트 사용 예제 ===")
    examples.example_using_sse()


if __name__ == "__main__":
    run_examples() 