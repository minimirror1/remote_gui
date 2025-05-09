from PySide6.QtCore import QObject, Signal, Slot
import requests
import json
import threading
from typing import Optional, Dict, Any, List

class ApiManager(QObject):
    """REST API 통신 관리자 클래스"""
    
    # 시그널 정의
    request_completed = Signal(dict)  # 요청 성공 시 응답 데이터
    request_error = Signal(str)       # 요청 실패 시 에러 메시지
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'ApiManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if ApiManager._instance is not None:
            raise Exception("ApiManager는 싱글톤 클래스입니다. get_instance()를 사용하세요.")
        
        super().__init__()
        self.base_url = ""
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 10  # 기본 타임아웃 10초
    
    def set_base_url(self, url: str) -> None:
        """기본 URL 설정"""
        self.base_url = url
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """기본 헤더 설정"""
        self.headers.update(headers)
    
    def set_timeout(self, timeout: int) -> None:
        """요청 타임아웃 설정"""
        self.timeout = timeout
    
    # GET 요청 메서드
    def get(self, endpoint: str, params: Dict = None) -> None:
        """GET 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.request_completed.emit(response.json())
        except Exception as e:
            self.request_error.emit(str(e))
    
    # POST 요청 메서드
    def post(self, endpoint: str, data: Dict) -> None:
        """POST 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.request_completed.emit(response.json())
        except Exception as e:
            self.request_error.emit(str(e))
    
    # PUT 요청 메서드
    def put(self, endpoint: str, data: Dict) -> None:
        """PUT 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.put(url, json=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.request_completed.emit(response.json())
        except Exception as e:
            self.request_error.emit(str(e))
    
    # DELETE 요청 메서드
    def delete(self, endpoint: str) -> None:
        """DELETE 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.request_completed.emit(response.json())
        except Exception as e:
            self.request_error.emit(str(e)) 