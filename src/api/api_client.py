from PySide6.QtCore import QThread, Signal, QObject
import requests
from typing import Dict, Any, Optional

class ApiRequestThread(QThread):
    """비동기 API 요청 처리 스레드"""
    
    # 시그널 정의
    request_success = Signal(dict)  # 요청 성공 시 응답 데이터
    request_error = Signal(str)     # 요청 실패 시 에러 메시지
    
    def __init__(self, method: str, url: str, headers: Dict = None, params: Dict = None, 
                 data: Dict = None, timeout: int = 10, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.method = method
        self.url = url
        self.headers = headers
        self.params = params
        self.data = data
        self.timeout = timeout
        self._running = True
    
    def run(self):
        """스레드 실행"""
        try:
            if self.method == 'GET':
                response = requests.get(
                    self.url, 
                    headers=self.headers, 
                    params=self.params, 
                    timeout=self.timeout
                )
            elif self.method == 'POST':
                response = requests.post(
                    self.url, 
                    headers=self.headers, 
                    json=self.data, 
                    timeout=self.timeout
                )
            elif self.method == 'PUT':
                response = requests.put(
                    self.url, 
                    headers=self.headers, 
                    json=self.data, 
                    timeout=self.timeout
                )
            elif self.method == 'DELETE':
                response = requests.delete(
                    self.url, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {self.method}")
            
            response.raise_for_status()
            self.request_success.emit(response.json())
            
        except Exception as e:
            self.request_error.emit(str(e))
    
    def stop(self):
        """스레드 중지"""
        self._running = False
        self.quit()
        
class ApiClient:
    """API 요청 클라이언트"""
    
    def __init__(self, base_url: str = "", default_headers: Dict = None, default_timeout: int = 10):
        self.base_url = base_url
        self.default_headers = default_headers or {"Content-Type": "application/json"}
        self.default_timeout = default_timeout
        self.active_threads = []
    
    def make_request(self, method: str, endpoint: str, headers: Dict = None, params: Dict = None, 
                     data: Dict = None, timeout: int = None, success_callback = None, error_callback = None) -> ApiRequestThread:
        """API 요청 생성 및 실행"""
        # 헤더 및 타임아웃 결합
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        
        # URL 구성
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        # 스레드 생성
        thread = ApiRequestThread(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            data=data,
            timeout=timeout or self.default_timeout
        )
        
        # 콜백 연결
        if success_callback:
            thread.request_success.connect(success_callback)
        if error_callback:
            thread.request_error.connect(error_callback)
        
        # 스레드 실행
        thread.start()
        
        # 활성 스레드 관리
        self.active_threads.append(thread)
        thread.finished.connect(lambda: self._remove_thread(thread))
        
        return thread
    
    def get(self, endpoint: str, params: Dict = None, headers: Dict = None, timeout: int = None, 
            success_callback = None, error_callback = None) -> ApiRequestThread:
        """GET 요청 수행"""
        return self.make_request('GET', endpoint, headers, params, None, timeout, success_callback, error_callback)
    
    def post(self, endpoint: str, data: Dict, headers: Dict = None, timeout: int = None,
             success_callback = None, error_callback = None) -> ApiRequestThread:
        """POST 요청 수행"""
        return self.make_request('POST', endpoint, headers, None, data, timeout, success_callback, error_callback)
    
    def put(self, endpoint: str, data: Dict, headers: Dict = None, timeout: int = None,
            success_callback = None, error_callback = None) -> ApiRequestThread:
        """PUT 요청 수행"""
        return self.make_request('PUT', endpoint, headers, None, data, timeout, success_callback, error_callback)
    
    def delete(self, endpoint: str, headers: Dict = None, timeout: int = None,
               success_callback = None, error_callback = None) -> ApiRequestThread:
        """DELETE 요청 수행"""
        return self.make_request('DELETE', endpoint, headers, None, None, timeout, success_callback, error_callback)
    
    def _remove_thread(self, thread: ApiRequestThread) -> None:
        """완료된 스레드 제거"""
        if thread in self.active_threads:
            self.active_threads.remove(thread)
    
    def cleanup(self) -> None:
        """모든 활성 스레드 정리"""
        for thread in self.active_threads[:]:  # 복사본으로 반복
            thread.stop()
            thread.wait()
            self.active_threads.remove(thread) 