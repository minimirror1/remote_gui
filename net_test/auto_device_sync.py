import requests
import json
import sys
import os
import time
import threading
from typing import Dict, Any, Set
from PySide6.QtCore import QObject, Slot, QTimer, QCoreApplication

# src 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

from device_status_manager import DeviceStatusManager


class AutoDeviceSync(QObject):
    """
    DeviceStatusManager의 장치 상태 변화를 모니터링하고
    새로운 장치가 추가되면 자동으로 서버에 등록하는 서비스
    """
    
    def __init__(self, base_url: str = "https://robot-monitor-dev.systemiic.com"):
        super().__init__()
        self.base_url = base_url.rstrip('/')
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
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.check_and_sync)
        
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
    
    def start_service(self, check_interval: int = 5000):
        """
        자동 동기화 서비스 시작
        
        Args:
            check_interval: 체크 간격 (밀리초)
        """
        if self.is_running:
            print("이미 서비스가 실행 중입니다.")
            return
        
        print("=== 자동 장치 동기화 서비스 시작 ===")
        
        # 서버 연결 테스트
        if not self._test_server_connection():
            print("⚠️ 서버 연결 실패. 오프라인 모드로 시작합니다.")
        else:
            # 서버 환경 설정 (매장/PC 생성)
            if not self._setup_server_environment():
                print("⚠️ 서버 환경 설정 실패. 제한된 기능으로 서비스를 시작합니다.")
        
        # 주기적 체크 시작 (서버 환경 설정 실패와 관계없이)
        self.sync_timer.start(check_interval)
        self.is_running = True
        
        print(f"✅ 서비스 시작됨 (체크 간격: {check_interval}ms)")
        print("DeviceStatusManager의 장치 변화를 모니터링합니다...")
        
        if not self.store_id or not self.pc_id:
            print("⚠️ 서버 등록 기능이 비활성화됨 (매장/PC 정보 없음)")
            print("   장치 감지는 계속 동작하며, 서버 환경이 준비되면 자동으로 등록됩니다.")
    
    def stop_service(self):
        """자동 동기화 서비스 중단"""
        if not self.is_running:
            return
        
        self.sync_timer.stop()
        self.is_running = False
        print("자동 장치 동기화 서비스가 중단되었습니다.")
    
    @Slot(str)
    def on_device_connected(self, device_id: str):
        """장치 연결 시 호출되는 슬롯"""
        print(f"[자동 동기화] 장치 연결됨: {device_id}")
        
        # 즉시 동기화 시도
        self._sync_device(device_id)
    
    @Slot(str)
    def on_device_disconnected(self, device_id: str):
        """장치 연결 해제 시 호출되는 슬롯"""
        print(f"[자동 동기화] 장치 연결 해제됨: {device_id}")
        
        # 등록 목록에서 제거 (재연결 시 다시 등록하도록)
        self.registered_devices.discard(device_id)
    
    @Slot(str, dict)
    def on_device_status_updated(self, device_id: str, status_data: Dict[str, Any]):
        """장치 상태 업데이트 시 호출되는 슬롯"""
        # 새로운 장치인 경우에만 등록
        if device_id not in self.registered_devices:
            print(f"[자동 동기화] 새로운 장치 감지: {device_id}")
            # 임시로 등록된 장치로 표시하여 무한 반복 방지
            self.registered_devices.add(device_id)
            self._sync_device(device_id)
    
    @Slot()
    def check_and_sync(self):
        """주기적으로 장치 상태를 확인하고 동기화"""
        try:
            current_devices = set(self.device_manager.get_all_devices_status().keys())
            
            # 새로운 장치가 있는지 확인
            new_devices = current_devices - self.registered_devices
            
            if new_devices:
                print(f"[자동 동기화] 새로운 장치 발견: {new_devices}")
                for device_id in new_devices:
                    self._sync_device(device_id)
            
        except Exception as e:
            print(f"주기적 체크 오류: {e}")
    
    def _sync_device(self, device_id: str):
        """단일 장치를 서버에 동기화"""        
        try:
            print(f"[동기화 시작] 장치 ID: {device_id}")
            
            # 서버 환경 확인 및 재설정
            if not self.store_id or not self.pc_id:
                print(f"  서버 환경 미설정: store_id={self.store_id}, pc_id={self.pc_id}")
                print("  서버 환경 재설정 시도...")
                
                if not self._setup_server_environment():
                    print(f"  ❌ 서버 환경 설정 실패 - 오프라인 모드로 동작")
                    print(f"  장치 {device_id}는 로컬에서만 관리됩니다.")
                    return
                else:
                    print(f"  ✅ 서버 환경 설정 성공: store_id={self.store_id}, pc_id={self.pc_id}")
            
            # 장치 상태 데이터 가져오기
            status_data = self.device_manager.get_device_status(device_id)
            if not status_data:
                print(f"  ⚠️ 장치 {device_id}의 상태 데이터가 없습니다.")
                return
            
            print(f"  📊 상태 데이터 확인: {len(status_data)} 항목")
            
            # 서버에 오브제로 등록
            if self._create_object_on_server(device_id, status_data):
                print(f"✅ 장치 {device_id} 서버 등록 완료")
            else:
                print(f"❌ 장치 {device_id} 서버 등록 실패")
                
        except Exception as e:
            print(f"❌ 장치 동기화 오류 ({device_id}): {e}")
            import traceback
            traceback.print_exc()
    
    def _test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            print(f"서버 연결 테스트 중: {self.base_url}/v1/health")
            response = requests.get(f"{self.base_url}/v1/health", timeout=5)
            print(f"서버 연결 테스트 결과: {response.status_code}")
            if response.status_code == 200:
                print("✅ 서버 연결 성공")
                return True
            else:
                print(f"❌ 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 오류: {e}")
            return False
    
    def _setup_server_environment(self) -> bool:
        """서버 환경 설정 (매장/PC 생성)"""
        try:
            # 매장 확인/생성
            if not self._ensure_store():
                return False
            
            # PC 확인/생성
            if not self._ensure_pc():
                return False
            
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
    
    def _create_object_on_server(self, device_id: str, status_data: Dict[str, Any]) -> bool:
        """장치를 오브제로 서버에 등록"""
        if not self.store_id or not self.pc_id:
            print(f"  오브제 생성 실패: store_id={self.store_id}, pc_id={self.pc_id}")
            return False
        
        try:
            # 장치 상태 데이터에서 오브제 정보 생성
            object_data = self._build_object_data(device_id, status_data)
            url = f"{self.base_url}/v1/service/stores/{self.store_id}/pcs/{self.pc_id}/objects"
            
            print(f"  오브제 생성 요청: {url}")
            print(f"  요청 데이터: {json.dumps(object_data, indent=2)}")
            
            response = requests.post(
                url,
                json=object_data,
                timeout=5
            )
            
            print(f"  응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                object_id = response_data.get("object_id")
                print(f"  ✅ 오브제 생성 성공: {object_id}")
                print(f"  응답 데이터: {response_data}")
                
                # 장치 ID → 오브제 ID 매핑 저장
                self.device_to_object_mapping[device_id] = object_id
                print(f"  📝 매핑 저장: 장치 {device_id} → 오브제 {object_id}")
                
                # SSE 클라이언트에 올바른 오브제 ID로 연결 시작
                self._start_sse_connection(device_id, object_id)
                
                return True
            else:
                print(f"  ❌ 오브제 생성 실패: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  오류 상세: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"  오류 텍스트: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 오브제 생성 예외: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
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
    
    def _start_sse_connection(self, device_id: str, object_id: str):
        """SSE 클라이언트에 올바른 오브제 ID로 연결 시작"""
        try:
            # SSE 매니저를 통해 클라이언트 참조 갱신
            if self.sse_manager and hasattr(self.sse_manager, 'client'):
                self.sse_client = self.sse_manager.client
            
            # SSE 클라이언트 참조가 없으면 설정 시도
            if not self.sse_client:
                self._setup_sse_client()
            
            # 여전히 참조가 없으면 지연된 연결 시도
            if not self.sse_client:
                print(f"  ⏰ SSE 클라이언트 참조 없음, 지연된 연결 시도")
                QTimer.singleShot(1000, lambda: self._retry_sse_connection(device_id, object_id))
                return
            
            # 기존 장치 ID 기반 연결이 있다면 중단
            if hasattr(self.sse_client, 'stop_object_connection'):
                self.sse_client.stop_object_connection(device_id)
            
            # 올바른 오브제 ID로 새 연결 시작
            if hasattr(self.sse_client, 'start_object_connection'):
                self.sse_client.start_object_connection(object_id)
                print(f"  🔗 SSE 연결 시작: 오브제 {object_id}")
            else:
                print(f"  ⚠️ SSE 클라이언트에 start_object_connection 메서드가 없습니다.")
                
        except Exception as e:
            print(f"  ❌ SSE 연결 시작 실패: {e}")
    
    def _retry_sse_connection(self, device_id: str, object_id: str):
        """지연된 SSE 연결 재시도"""
        print(f"  🔄 SSE 연결 재시도: 장치 {device_id} → 오브제 {object_id}")
        self._start_sse_connection(device_id, object_id)
    
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