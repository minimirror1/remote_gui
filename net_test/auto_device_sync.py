import requests
import json
import sys
import os
import time
import threading
from typing import Dict, Any, Set
from PySide6.QtCore import QObject, Slot, QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication

# src 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

from device_status_manager import DeviceStatusManager


class AutoDeviceSync(QObject):
    """
    DeviceStatusManager와 연동하여 새로운 장치를 자동으로 서버에 동기화하는 서비스
    다중 장치 환경에서 안정성을 위해 순차 처리 방식을 사용합니다.
    """
    
    def __init__(self, base_url: str = "https://robot-monitor-dev.systemiic.com"):
        super().__init__()
        
        self.base_url = base_url
        self.device_manager = None
        self.sse_manager = None
        self.sse_client = None
        
        # 서버 환경 정보
        self.store_id = None
        self.pc_id = None
        
        # 등록된 장치 추적
        self.registered_devices: set = set()
        
        # 장치 ID → 오브제 ID 매핑
        self.device_to_object_mapping: Dict[str, str] = {}
        
        # 서비스 상태
        self.is_running = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_and_sync)
        
        # 다중 장치 환경 안정성을 위한 순차 처리 큐
        self.sync_queue = []  # 처리 대기 중인 장치 목록
        self.is_syncing = False  # 현재 동기화 진행 중 여부
        self.sync_timer = QTimer()  # 순차 처리용 타이머
        self.sync_timer.timeout.connect(self._process_sync_queue)
        self.sync_timer.setSingleShot(True)
        
        # 기본 매장/PC 정보 (필요시 수정)
        self.default_store = {
            "store_name": "Default Store",
            "country_code": "KR",
            "address": "Seoul, Korea"
        }
        
        print("🔍 [DEBUG] AutoDeviceSync 초기화 시작...")
        
        # DeviceStatusManager 연결
        self._setup_device_manager()
        
        print("AutoDeviceSync 초기화 완료")
        print("🔍 [DEBUG] AutoDeviceSync 생성 완료")
    
    def _setup_device_manager(self):
        """DeviceStatusManager 연결"""
        self.device_manager = DeviceStatusManager.get_instance()
        
        # 서버에 등록된 장치 추적
        self.registered_devices: Set[str] = set()
        
        # 장치 ID → 오브제 ID 동적 매핑
        self.device_to_object_mapping: Dict[str, str] = {}
        
        # 서버 정보 캐싱
        self.store_id = None
        self.pc_id = None
        
        # 기본 매장/PC 정보
        self.default_store = {
            "store_name": "Auto Sync Store",
            "country_code": "KR",
            "address": "Seoul Auto Location",
            "latitude": 37.5665,
            "longitude": 126.978,
            "timezone": "Asia/Seoul"
        }
        
        self.default_pc = {
            "pc_name": "Main PC",
            "sw_version": "1.0.0"
        }
        
        # 서비스 상태
        self.is_running = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_and_sync)
        
        # DeviceStatusManager 시그널 연결
        self._connect_signals()
        
        # SSE 클라이언트 참조 (매핑 정보 전달용)
        self.sse_client = None
        self.sse_manager = None
        
        print("AutoDeviceSync 초기화 완료")
    
    def _connect_signals(self):
        """DeviceStatusManager 시그널 연결"""
        try:
            # 장치 연결/해제 시그널 연결
            self.device_manager.device_connected.connect(self.on_device_connected)
            self.device_manager.device_disconnected.connect(self.on_device_disconnected)
            self.device_manager.device_status_updated.connect(self.on_device_status_updated)
            
            print("DeviceStatusManager 시그널 연결 완료")
        except Exception as e:
            print(f"시그널 연결 실패: {e}")
    
    def _setup_sse_client(self):
        """SSE 클라이언트 참조 설정"""
        try:
            # SSE 매니저를 통해 클라이언트 참조 가져오기
            from src.api.sse_manager import SSEManager
            sse_manager = SSEManager.get_instance()
            
            # 여러 방법으로 클라이언트 참조 시도
            client = None
            if hasattr(sse_manager, 'client') and sse_manager.client:
                client = sse_manager.client
            elif hasattr(sse_manager, '_client') and sse_manager._client:
                client = sse_manager._client
            
            if client:
                self.sse_client = client
                print("SSE 클라이언트 참조 설정 완료")
            else:
                print("SSE 클라이언트가 아직 초기화되지 않음")
                
        except Exception as e:
            print(f"SSE 클라이언트 참조 설정 실패: {e}")
    
    def set_sse_manager(self, sse_manager):
        """SSE 매니저 참조 설정"""
        self.sse_manager = sse_manager
        if hasattr(sse_manager, 'client') and sse_manager.client:
            self.sse_client = sse_manager.client
            print("SSE 매니저 및 클라이언트 참조 설정 완료")
        else:
            print("SSE 매니저 설정됨, 클라이언트는 나중에 설정 예정")
    
    def start(self, check_interval: int = 15000):
        """자동 동기화 서비스 시작 (간단한 인터페이스)"""
        return self.start_service(check_interval)
    
    def start_service(self, check_interval: int = 15000):
        """
        자동 동기화 서비스 시작 (저사양 CPU 최적화)
        
        Args:
            check_interval: 체크 간격 (밀리초) - 기본값 15초
        """
        if self.is_running:
            print("자동 장치 동기화 서비스가 이미 실행 중입니다.")
            return
        
        print(f"자동 장치 동기화 서비스를 시작합니다... (체크 간격: {check_interval/1000}초)")
        
        # 주기적 체크 시작 (서버 환경 설정과 독립적으로)
        self.check_timer.start(check_interval)
        self.is_running = True
        
        print("자동 장치 동기화 서비스가 시작되었습니다.")
        print("DeviceStatusManager의 장치 상태 변화를 모니터링합니다.")
    
    def stop(self):
        """자동 동기화 서비스 중지 (간단한 인터페이스)"""
        return self.stop_service()
    
    def stop_service(self):
        """자동 동기화 서비스 중지"""
        if not self.is_running:
            print("자동 장치 동기화 서비스가 실행되지 않고 있습니다.")
            return
        
        self.check_timer.stop()
        self.is_running = False
        print("자동 장치 동기화 서비스가 중단되었습니다.")
    
    @Slot(str)
    def on_device_connected(self, device_id: str):
        """장치 연결 시 자동 동기화 (지연 시작)"""
        device_id = str(device_id)
        print(f"[자동 동기화] 장치 연결됨: {device_id} (타입: {type(device_id)})")
        
        if device_id not in self.registered_devices:
            print(f"  💡 새로운 장치 연결 - 시리얼 폴링 안정화 대기 중...")
            print(f"  ⏳ 10초 후 동기화 시작 (시리얼 데이터 수집 완료 대기)")
            
            # 장치 연결 시에는 더 긴 지연 시간 적용 (10초)
            self.registered_devices.add(device_id)  # 중복 방지를 위해 미리 추가
            
            # 10초 후에 동기화 시작
            QTimer.singleShot(10000, lambda: self._delayed_sync_start(device_id))
        else:
            print(f"  ✅ 장치 {device_id}는 이미 등록됨")
    
    @Slot(str)
    def on_device_disconnected(self, device_id: str):
        """장치 연결 해제 시 호출되는 슬롯"""
        # 장치 ID 정규화 (int -> str 변환)
        device_id = str(device_id)
        print(f"[자동 동기화] 장치 연결 해제됨: {device_id}")
        
        # 등록 목록에서 제거 (재연결 시 다시 등록하도록)
        self.registered_devices.discard(device_id)
    
    @Slot(str, dict)
    def on_device_status_updated(self, device_id: str, status_data: Dict[str, Any]):
        """장치 상태 업데이트 시 자동 동기화 (순차 처리)"""
        # 장치 ID 정규화 (int -> str 변환)
        device_id = str(device_id)
        
        if device_id not in self.registered_devices:
            print(f"[자동 동기화] 새로운 장치 감지: {device_id} (타입: {type(device_id)})")
            print(f"  현재 등록된 장치: {self.registered_devices}")
            
            # 시리얼 폴링 완료를 위해 충분한 지연 시간 추가 (5초)
            print(f"  ⏳ 시리얼 폴링 완료 대기 중... (5초 후 동기화 시작)")
            
            # 다중 장치 환경에서 안정성을 위해 큐에 추가하여 순차 처리
            if device_id not in self.sync_queue:
                self.sync_queue.append(device_id)
                print(f"  장치 {device_id}를 동기화 큐에 추가 (큐 크기: {len(self.sync_queue)})")
                
                # 5초 후에 처리 시작 (시리얼 폴링 완료 대기)
                if not self.is_syncing:
                    print(f"  📅 동기화 예약: 5초 후 시작")
                    QTimer.singleShot(5000, self._process_sync_queue)  # 5초 지연
        else:
            # 이미 등록된 장치의 상태 업데이트는 로그 출력하지 않음 (너무 빈번함)
            # print(f"[자동 동기화] 장치 {device_id}는 이미 등록됨 (스킵)")
            pass
    
    def _process_sync_queue(self):
        """동기화 큐를 순차적으로 처리"""
        if self.is_syncing or not self.sync_queue:
            return
        
        # 다음 장치 가져오기
        device_id = self.sync_queue.pop(0)
        self.is_syncing = True
        
        print(f"🔄 [큐 처리] 장치 {device_id} 동기화 시작... (남은 큐: {len(self.sync_queue)})")
        
        # 별도 스레드에서 처리하되, 완료 후 다음 장치 처리
        import threading
        sync_thread = threading.Thread(
            target=self._sync_device_with_callback,
            args=(device_id,),
            daemon=True,
            name=f"DeviceSync-{device_id}"
        )
        sync_thread.start()
    
    def _sync_device_with_callback(self, device_id: str):
        """장치 동기화 후 다음 큐 처리를 위한 콜백"""
        try:
            # 임시로 등록된 장치로 표시하여 무한 반복 방지
            self.registered_devices.add(device_id)
            print(f"  등록된 장치 목록 업데이트: {self.registered_devices}")
            
            # 실제 동기화 수행
            self._sync_device(device_id)
            print(f"✅ [큐 처리] 장치 {device_id} 동기화 완료")
            
        except Exception as e:
            print(f"❌ [큐 처리] 장치 {device_id} 동기화 오류: {e}")
            # 오류 시 registered_devices에서 제거 (재시도 가능하도록)
            self.registered_devices.discard(device_id)
            import traceback
            traceback.print_exc()
        finally:
            # 동기화 완료 후 다음 장치 처리 (2초 지연으로 서버 부하 분산)
            self.is_syncing = False
            if self.sync_queue:
                print(f"⏳ 다음 장치 처리를 위해 2초 대기... (남은 큐: {len(self.sync_queue)})")
                self.sync_timer.start(2000)  # 2초 후 다음 장치 처리
            else:
                print("✅ 모든 장치 동기화 완료")
    
    def _sync_device_threaded(self, device_id: str):
        """별도 스레드에서 장치 동기화 수행 (더 이상 사용하지 않음 - 순차 처리로 대체)"""
        # 이 메서드는 하위 호환성을 위해 유지하되, 순차 처리로 리디렉션
        print(f"🔄 [리디렉션] 장치 {device_id}를 순차 처리 큐로 이동")
        if device_id not in self.sync_queue:
            self.sync_queue.append(device_id)
            if not self.is_syncing:
                self._process_sync_queue()
    
    @Slot()
    def check_and_sync(self):
        """주기적으로 장치 상태를 확인하고 동기화"""
        try:
            # 모든 장치 ID를 문자열로 정규화
            current_devices = set(str(device_id) for device_id in self.device_manager.get_all_devices_status().keys())
            
            # 새로운 장치가 있는지 확인
            new_devices = current_devices - self.registered_devices
            
            if new_devices:
                print(f"[자동 동기화] 새로운 장치 발견: {new_devices}")
                for device_id in new_devices:
                    self._sync_device(device_id)
            
        except Exception as e:
            print(f"주기적 체크 오류: {e}")
    
    def _sync_device(self, device_id: str):
        """장치를 서버에 동기화 (개별 장치 처리) - 완전 비동기"""
        try:
            print(f"🔄 [동기화] 장치 {device_id} 동기화 시작...")
            
            # 1. 서버 연결 테스트 (빠른 체크)
            print(f"  🔍 서버 연결 테스트...")
            if not self._test_server_connection():
                print("  ❌ 서버 연결 실패 - 오프라인 모드로 동작")
                return
            print(f"  ✅ 서버 연결 성공")
            
            # 2. 매장/PC 환경 설정 (필요시)
            if not self.store_id or not self.pc_id:
                print("  🏪 매장/PC 환경 설정...")
                self._setup_store_and_pc()
                if not self.store_id or not self.pc_id:
                    print("  ❌ 매장/PC 환경 설정 실패")
                    return
                print(f"  ✅ 환경 설정 완료: Store={self.store_id}, PC={self.pc_id}")
            
            # 3. 장치 상태 데이터 가져오기
            print(f"  🔍 장치 상태 데이터 조회...")
            
            try:
                print(f"  🔍 DeviceStatusManager에서 장치 {device_id} 데이터 요청...")
                device_data = self.device_manager.get_device_status(device_id)
                print(f"  📋 조회 결과: {type(device_data)} (None={device_data is None})")
                
                if not device_data or not self._is_valid_device_data(device_data):
                    print(f"  ❌ 장치 {device_id}의 유효한 상태 데이터가 없습니다")
                    print(f"  💡 Zigbee 통신 문제 또는 장치 MCU 비활성 상태")
                    print(f"  🚫 서버 등록 중단 (실제 장치 상태 없음)")
                    
                    # registered_devices에서 제거하여 나중에 재시도 가능하도록
                    self.registered_devices.discard(device_id)
                    return
                
                print(f"  ✅ 유효한 상태 데이터 확인 (키 개수: {len(device_data)})")
                    
            except Exception as data_error:
                print(f"  ❌ 상태 데이터 조회 중 예외: {data_error}")
                print(f"  🚫 서버 등록 중단 (데이터 조회 실패)")
                
                # registered_devices에서 제거하여 나중에 재시도 가능하도록
                self.registered_devices.discard(device_id)
                import traceback
                traceback.print_exc()
                return
            
            print(f"  ✅ 상태 데이터 검증 완료 - 오브제 생성 진행")
            
            # 4. 오브제 생성 (비동기 처리)
            print(f"  🔧 오브제 생성 시작...")
            
            # 복잡한 스레드 처리 대신 QTimer로 간단하게 처리
            def create_object_delayed():
                try:
                    print(f"  🔄 [지연실행] 오브제 생성 시작...")
                    object_id = self._create_object(device_id, device_data)
                    
                    if object_id:
                        # 매핑 저장
                        self.device_to_object_mapping[device_id] = object_id
                        print(f"  ✅ 매핑 저장: 장치 {device_id} → 오브제 {object_id}")
                        
                        # SSE 연결 시작 (추가 지연)
                        if self.sse_manager:
                            print(f"  🔗 SSE 연결 예약 (2초 후)...")
                            QTimer.singleShot(2000, lambda: self._start_sse_connection(object_id))
                        
                        print(f"✅ [동기화] 장치 {device_id} 동기화 완료 (오브제 ID: {object_id})")
                    else:
                        print(f"❌ [동기화] 장치 {device_id} 오브제 생성 실패")
                        
                except Exception as e:
                    print(f"❌ [지연실행] 오브제 생성 오류: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 오브제 생성을 메인 스레드에서 즉시 실행 (타이머 경고 방지)
            print(f"  🔧 오브제 생성 즉시 실행...")
            self._create_object_for_device(device_id)
            
        except Exception as e:
            print(f"❌ [동기화] 장치 {device_id} 동기화 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _start_sse_connection(self, object_id: str):
        """SSE 연결 시작 (지연 실행)"""
        try:
            print(f"  🔗 오브제 {object_id}에 대한 SSE 연결 시작...")
            self.sse_manager.start(object_id)  # start_connection -> start로 수정
            print(f"  ✅ SSE 연결 시작 완료")
        except Exception as e:
            print(f"  ❌ SSE 연결 시작 실패: {e}")
    
    def _test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            print(f"🔍 [DEBUG] 서버 연결 테스트 중: {self.base_url}/v1/health")
            print("🔍 [DEBUG] HTTP 요청 전송 중... (여기서 멈출 수 있음)")
            response = requests.get(f"{self.base_url}/v1/health", timeout=5)
            print(f"🔍 [DEBUG] 서버 응답 수신: {response.status_code}")
            if response.status_code == 200:
                print("🔍 [DEBUG] ✅ 서버 연결 성공")
                return True
            else:
                print(f"🔍 [DEBUG] ❌ 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"🔍 [DEBUG] ❌ 서버 연결 오류: {e}")
            return False
    
    def _setup_store_and_pc(self):
        """서버 환경 설정 (매장/PC 생성)"""
        try:
            # 매장 확인/생성
            if not self._ensure_store():
                return
            
            # PC 확인/생성
            if not self._ensure_pc():
                return
            
            print(f"서버 환경 설정 완료: Store={self.store_id}, PC={self.pc_id}")
            return True
            
        except Exception as e:
            print(f"서버 환경 설정 오류: {e}")
            return False
    
    def _ensure_store(self) -> bool:
        """매장 생성 또는 기존 매장 확인"""
        try:
            # 기존 매장 목록 조회
            response = requests.get(
                f"{self.base_url}/v1/service/stores",
                params={"country_code": self.default_store["country_code"]},
                timeout=5
            )
            
            if response.status_code == 200:
                stores = response.json().get("stores", [])
                if stores:
                    self.store_id = stores[0]["id"]
                    print(f"기존 매장 사용: {self.store_id}")
                    return True
            
            # 새 매장 생성
            response = requests.post(
                f"{self.base_url}/v1/service/stores",
                json=self.default_store,
                timeout=5
            )
            
            if response.status_code == 200:
                self.store_id = response.json().get("store_id")
                print(f"새 매장 생성: {self.store_id}")
                return True
                
        except Exception as e:
            print(f"매장 처리 오류: {e}")
        
        return False
    
    def _ensure_pc(self) -> bool:
        """PC 생성 또는 기존 PC 확인"""
        if not self.store_id:
            print("PC 확인 실패: store_id가 없습니다")
            return False
        
        try:
            # 방법 1: 전용 PC 목록 조회 API 시도
            pc_list_url = f"{self.base_url}/v1/service/stores/{self.store_id}/pcs"
            print(f"PC 목록 조회 (전용 API): {pc_list_url}")
            response = requests.get(pc_list_url, timeout=5)
            
            print(f"PC 목록 조회 응답: {response.status_code}")
            
            if response.status_code == 200:
                pc_data = response.json()
                print(f"PC 목록 데이터: {json.dumps(pc_data, indent=2)}")
                
                # PC 목록에서 첫 번째 PC 사용
                pcs = pc_data.get("pcs", []) if isinstance(pc_data, dict) else pc_data
                if pcs and len(pcs) > 0:
                    self.pc_id = pcs[0].get("pc_id") or pcs[0].get("id")
                    print(f"✅ 기존 PC 사용: {self.pc_id}")
                    return True
                else:
                    print("기존 PC가 없습니다. 새 PC를 생성합니다.")
            else:
                print(f"PC 목록 조회 실패: {response.status_code} - {response.text}")
                
                # 방법 2: 매장 상세 정보에서 PC 정보 확인
                store_url = f"{self.base_url}/v1/service/stores/{self.store_id}"
                print(f"매장 상세 조회: {store_url}")
                store_response = requests.get(store_url, timeout=5)
                
                if store_response.status_code == 200:
                    store_data = store_response.json()
                    pcs = store_data.get("pcs", [])
                    if pcs:
                        self.pc_id = pcs[0]["pc_id"]
                        print(f"✅ 매장 데이터에서 기존 PC 사용: {self.pc_id}")
                        return True
            
            # 새 PC 생성 (고유한 이름 생성)
            import time
            timestamp = int(time.time())
            unique_pc_name = f"PC_{timestamp}"
            
            pc_data = {
                "pc_name": unique_pc_name,
                "sw_version": "1.0.0",
                "store_id": self.store_id
            }
            
            create_url = f"{self.base_url}/v1/service/stores/{self.store_id}/pcs"
            print(f"PC 생성 요청: {create_url}")
            print(f"PC 생성 데이터: {json.dumps(pc_data, indent=2)}")
            
            response = requests.post(
                create_url,
                json=pc_data,
                timeout=5
            )
            
            print(f"PC 생성 응답: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                self.pc_id = response_data.get("pc_id") or response_data.get("id")
                print(f"✅ 새 PC 생성 성공: {self.pc_id}")
                print(f"PC 생성 응답 데이터: {response_data}")
                return True
            else:
                print(f"❌ PC 생성 실패: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"PC 생성 오류 상세: {json.dumps(error_data, indent=2)}")
                    
                    # PC_NAME_ALREADY_EXISTS 오류인 경우 더 고유한 이름으로 재시도
                    if error_data.get("errorCode") == "PC_NAME_ALREADY_EXISTS":
                        import uuid
                        unique_id = str(uuid.uuid4())[:8]
                        retry_pc_name = f"PC_{unique_id}_{timestamp}"
                        
                        retry_pc_data = {
                            "pc_name": retry_pc_name,
                            "sw_version": "1.0.0",
                            "store_id": self.store_id
                        }
                        
                        print(f"PC 이름 중복으로 재시도: {retry_pc_name}")
                        retry_response = requests.post(
                            create_url,
                            json=retry_pc_data,
                            timeout=5
                        )
                        
                        if retry_response.status_code in [200, 201]:
                            retry_data = retry_response.json()
                            self.pc_id = retry_data.get("pc_id") or retry_data.get("id")
                            print(f"✅ PC 재생성 성공: {self.pc_id}")
                            return True
                        else:
                            print(f"❌ PC 재생성도 실패: {retry_response.status_code}")
                            
                except:
                    print(f"PC 생성 오류 텍스트: {response.text}")
                
        except Exception as e:
            print(f"❌ PC 처리 예외: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def _create_object(self, device_id: str, status_data: Dict[str, Any]) -> str:
        """장치를 오브제로 서버에 등록 (안전한 처리)"""
        if not self.store_id or not self.pc_id:
            print(f"  ❌ 오브제 생성 실패: store_id={self.store_id}, pc_id={self.pc_id}")
            return None
        
        try:
            print(f"🔧 [오브제 생성] 장치 {device_id} 오브제 생성 시작...")
            
            # 1. 오브제 데이터 생성 (빠른 실패)
            try:
                print(f"  📊 오브제 데이터 생성 중...")
                object_data = self._build_object_data(device_id, status_data)
                if not object_data:
                    print(f"  ❌ 오브제 데이터 생성 실패")
                    return None
                print(f"  ✅ 오브제 데이터 생성 완료")
            except Exception as build_error:
                print(f"  ❌ 오브제 데이터 생성 중 오류: {build_error}")
                return None
            
            # 2. HTTP 요청 준비
            url = f"{self.base_url}/v1/service/stores/{self.store_id}/pcs/{self.pc_id}/objects"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            print(f"  📡 오브제 생성 요청: {url}")
            print(f"  📋 요청 데이터: {json.dumps(object_data, indent=2)}")
            
            # 3. HTTP 요청 전송 (타임아웃 단축)
            try:
                print(f"  ⏳ HTTP 요청 전송 시작... (타임아웃: 3초)")
                import time
                start_time = time.time()
                
                # 더 짧은 타임아웃으로 빠른 실패
                response = requests.post(
                    url,
                    json=object_data,
                    headers=headers,
                    timeout=3  # 3초로 더 단축
                )
                
                elapsed_time = time.time() - start_time
                print(f"  ✅ HTTP 응답 수신 완료 (소요시간: {elapsed_time:.2f}초)")
                
            except requests.exceptions.Timeout:
                print(f"  ⏰ HTTP 요청 타임아웃 (3초 초과) - 빠른 실패로 GUI 보호")
                return None
            except requests.exceptions.ConnectionError as conn_error:
                print(f"  🔌 HTTP 연결 오류: {conn_error}")
                return None
            except requests.exceptions.RequestException as req_error:
                print(f"  📡 HTTP 요청 오류: {req_error}")
                return None
            except Exception as e:
                print(f"  ❌ 예상치 못한 HTTP 오류: {e}")
                return None
            
            # 4. 응답 처리
            print(f"  📊 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    print(f"  📝 응답 JSON 파싱 중...")
                    response_data = response.json()
                    object_id = response_data.get("object_id")
                    
                    if not object_id:
                        print(f"  ❌ 응답에 object_id가 없습니다: {response_data}")
                        return None
                    
                    print(f"  ✅ 오브제 생성 성공: {object_id}")
                    print(f"  📋 응답 데이터: {response_data}")
                    
                    return object_id
                    
                except ValueError as json_error:
                    print(f"  ❌ 응답 JSON 파싱 오류: {json_error}")
                    print(f"  📄 응답 텍스트: {response.text[:200]}...")
                    return None
                except Exception as parse_error:
                    print(f"  ❌ 응답 처리 중 오류: {parse_error}")
                    return None
                    
            else:
                print(f"  ❌ 오브제 생성 실패: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  📋 오류 상세: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"  📄 오류 텍스트: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"  ❌ 오브제 생성 치명적 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_object_data(self, device_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """장치 상태 데이터로부터 오브제 데이터 구성 (올바른 API 스키마 사용)"""
        # 기본 오브제 데이터 (API 스키마에 맞게 구성)
        object_data = {
            "object_name": f"Robot{device_id}",
            "object_operation_time": {
                "start_time": "09:00",
                "end_time": "22:00"
            },
            "schedule_flag": True,
            "firmware_version": {
                "board_id": "1-1", 
                "board_type": "MAI",
                "version": "0.1.51"
            },
            "operation_status": "PLAY"
        }
        
        if status_data:
            # 동작 상태 매핑
            motion = status_data.get('motion', {})
            motion_status = motion.get('status', '').upper()
            if motion_status in ["PLAY", "STOP", "PAUSE"]:
                object_data["operation_status"] = motion_status
            elif motion_status == "REPEAT":
                object_data["operation_status"] = "PLAY"  # REPEAT를 PLAY로 매핑
            
            # 전원 상태에 따른 동작 상태 조정
            main_power = status_data.get('main_power', {})
            if not main_power.get('status'):
                object_data["operation_status"] = "STOP"  # 전원이 꺼져있으면 STOP
        
        return object_data
    
    def get_object_id(self, device_id: str) -> str:
        """장치 ID에 해당하는 오브제 ID 반환"""
        return self.device_to_object_mapping.get(device_id)
    
    def get_device_id(self, object_id: str) -> str:
        """오브제 ID에 해당하는 장치 ID 반환"""
        for device_id, obj_id in self.device_to_object_mapping.items():
            if obj_id == object_id:
                return device_id
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """서비스 상태 정보 반환"""
        return {
            "is_running": self.is_running,
            "store_id": self.store_id,
            "pc_id": self.pc_id,
            "registered_devices": list(self.registered_devices),
            "current_devices": list(self.device_manager.get_all_devices_status().keys()),
            "connected_devices": self.device_manager.get_connected_devices(),
            "device_to_object_mapping": dict(self.device_to_object_mapping)
        }

    def _delayed_sync_start(self, device_id: str):
        """지연된 동기화 시작 (장치 상태 데이터 검증 후)"""
        try:
            print(f"🚀 [지연 동기화] 장치 {device_id} 상태 검증 시작...")
            
            # 장치 상태 데이터 검증
            device_data = self.device_manager.get_device_status(device_id)
            
            if not device_data or not self._is_valid_device_data(device_data):
                print(f"  ❌ 장치 {device_id} 상태 데이터가 없거나 유효하지 않음")
                print(f"  📋 데이터 내용: {device_data}")
                print(f"  💡 Zigbee 통신 문제 또는 장치 MCU 비활성 상태로 추정")
                print(f"  🚫 서버 등록 건너뜀 (장치 번호만 검색된 상태)")
                
                # registered_devices에서 제거하여 나중에 재시도 가능하도록
                self.registered_devices.discard(device_id)
                return
            
            print(f"  ✅ 장치 {device_id} 상태 데이터 검증 성공")
            print(f"  📊 유효한 데이터 키: {list(device_data.keys())}")
            
            # 큐에 추가하여 순차 처리
            if device_id not in self.sync_queue:
                self.sync_queue.append(device_id)
                print(f"  🔄 장치 {device_id}를 동기화 큐에 추가")
                
                if not self.is_syncing:
                    self._process_sync_queue()
            else:
                print(f"  ⚠️ 장치 {device_id}는 이미 큐에 있음")
                
        except Exception as e:
            print(f"❌ [지연 동기화] 오류: {e}")
            # 오류 시 registered_devices에서 제거하여 재시도 가능하도록
            self.registered_devices.discard(device_id)
            import traceback
            traceback.print_exc()
    
    def _is_valid_device_data(self, device_data: Dict[str, Any]) -> bool:
        """장치 상태 데이터가 유효한지 검증"""
        if not device_data:
            return False
        
        # 기본 필수 필드 확인
        required_fields = ['device_id']
        for field in required_fields:
            if field not in device_data:
                print(f"    ❌ 필수 필드 누락: {field}")
                return False
        
        # 실제 장치 상태 데이터 확인 (motion, main_power 등)
        has_motion_data = 'motion' in device_data and device_data['motion']
        has_power_data = 'main_power' in device_data and device_data['main_power']
        has_status_data = has_motion_data or has_power_data
        
        if not has_status_data:
            print(f"    ❌ 실제 장치 상태 데이터 없음 (motion/main_power 데이터 부재)")
            print(f"    💡 장치 번호만 검색되고 Zigbee 통신 또는 장치 MCU 문제로 추정")
            return False
        
        print(f"    ✅ 유효한 장치 상태 데이터 확인됨")
        return True

    def _create_object_for_device(self, device_id: str):
        """장치에 대한 오브제 생성 (메인 스레드에서 실행)"""
        try:
            print(f"  🔧 오브제 생성 시작...")
            
            # 메인 스레드에서 즉시 실행하도록 변경
            self._perform_object_creation(device_id)
            
        except Exception as e:
            print(f"  ❌ 오브제 생성 중 오류: {e}")
            import traceback
            traceback.print_exc()

    def _perform_object_creation(self, device_id: str):
        """실제 오브제 생성 작업 수행"""
        try:
            # 장치 상태 데이터 조회
            status_data = self.device_manager.get_device_status(device_id)
            if not status_data:
                print(f"  ❌ 장치 {device_id} 상태 데이터를 찾을 수 없음")
                return
            
            # 오브제 생성 요청
            object_id = self._create_object(device_id, status_data)
            if object_id:
                # 매핑 저장
                self.device_to_object_mapping[device_id] = object_id
                print(f"  ✅ 매핑 저장: 장치 {device_id} → 오브제 {object_id}")
                
                # SSE 연결 시작
                if self.sse_manager:
                    self._start_sse_connection(object_id)
                    
        except Exception as e:
            print(f"  ❌ 오브제 생성 작업 중 오류: {e}")
            import traceback
            traceback.print_exc()


class AutoSyncService:
    """
    백그라운드에서 실행되는 자동 동기화 서비스
    """
    
    def __init__(self):
        self.app = None
        self.sync_service = None
        self.running = False
    
    def start(self):
        """서비스 시작"""
        if self.running:
            print("서비스가 이미 실행 중입니다.")
            return
        
        print("=== 자동 장치 동기화 서비스 시작 ===")
        
        # Qt 애플리케이션 생성 (시그널 처리를 위해 필요)
        self.app = QCoreApplication(sys.argv)
        
        # 자동 동기화 서비스 생성
        self.sync_service = AutoDeviceSync()
        
        # 서비스 시작
        self.sync_service.start_service()
        
        self.running = True
        
        print("서비스가 백그라운드에서 실행됩니다.")
        print("종료하려면 Ctrl+C를 누르세요.\n")
        
        try:
            # 이벤트 루프 실행
            self.app.exec()
        except KeyboardInterrupt:
            print("\n사용자 중단 요청")
        finally:
            self.stop()
    
    def stop(self):
        """서비스 중단"""
        if not self.running:
            return
        
        print("서비스를 중단합니다...")
        
        if self.sync_service:
            self.sync_service.stop_service()
        
        if self.app:
            self.app.quit()
        
        self.running = False
        print("서비스가 중단되었습니다.")


if __name__ == "__main__":
    # 서비스 실행
    service = AutoSyncService()
    service.start() 