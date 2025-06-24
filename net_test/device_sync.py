import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# src 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

from device_status_manager import DeviceStatusManager


class DeviceServerSync:
    """
    DeviceStatusManager의 로컬 장치 데이터를 서버에 동기화하는 클래스
    """
    
    def __init__(self, base_url: str = "https://robot-monitor-dev.systemiic.com"):
        self.base_url = base_url.rstrip('/')
        self.device_manager = DeviceStatusManager.get_instance()
        
        # 기본 매장/PC 정보 (실제 환경에 맞게 수정 필요)
        self.default_store = {
            "store_name": "Test Store",
            "country_code": "KR",
            "address": "Seoul Test Location",
            "latitude": 37.5665,
            "longitude": 126.978,
            "timezone": "Asia/Seoul"
        }
        
        self.default_pc = {
            "pc_name": "Main PC",
            "sw_version": "1.0.0"
        }
        
        self.store_id = None
        self.pc_id = None
    
    def sync_all_devices(self) -> bool:
        """
        모든 로컬 장치를 서버에 동기화
        
        Returns:
            bool: 동기화 성공 여부
        """
        print("=== 로컬 장치 → 서버 동기화 시작 ===")
        
        # 1. 로컬 장치 데이터 확인
        local_devices = self.device_manager.get_all_devices_status()
        if not local_devices:
            print("동기화할 로컬 장치가 없습니다.")
            return False
        
        print(f"동기화할 장치 수: {len(local_devices)}")
        print(f"장치 ID 목록: {list(local_devices.keys())}")
        
        # 2. 매장 생성/확인
        if not self._ensure_store():
            print("매장 생성/확인 실패")
            return False
        
        # 3. PC 생성/확인
        if not self._ensure_pc():
            print("PC 생성/확인 실패")
            return False
        
        # 4. 각 장치를 오브제로 등록
        success_count = 0
        for device_id, status_data in local_devices.items():
            if self._create_object(device_id, status_data):
                success_count += 1
                print(f"✅ 장치 {device_id} 등록 성공")
            else:
                print(f"❌ 장치 {device_id} 등록 실패")
        
        print(f"\n=== 동기화 완료: {success_count}/{len(local_devices)} 성공 ===")
        return success_count > 0
    
    def _ensure_store(self) -> bool:
        """매장 생성 또는 기존 매장 확인"""
        try:
            # 기존 매장 목록 조회
            response = requests.get(
                f"{self.base_url}/v1/service/stores",
                params={"country_code": self.default_store["country_code"]}
            )
            
            if response.status_code == 200:
                stores = response.json().get("stores", [])
                if stores:
                    # 기존 매장 사용
                    self.store_id = stores[0]["id"]
                    print(f"기존 매장 사용: {self.store_id}")
                    return True
            
            # 새 매장 생성
            response = requests.post(
                f"{self.base_url}/v1/service/stores",
                json=self.default_store
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
            return False
        
        try:
            # 기존 PC 목록 조회
            response = requests.get(f"{self.base_url}/v1/service/stores/{self.store_id}")
            
            if response.status_code == 200:
                store_data = response.json()
                pcs = store_data.get("pcs", [])
                if pcs:
                    # 기존 PC 사용
                    self.pc_id = pcs[0]["pc_id"]
                    print(f"기존 PC 사용: {self.pc_id}")
                    return True
            
            # 새 PC 생성
            pc_data = {
                **self.default_pc,
                "store_id": self.store_id
            }
            
            response = requests.post(
                f"{self.base_url}/v1/service/stores/{self.store_id}/pcs",
                json=pc_data
            )
            
            if response.status_code == 200:
                self.pc_id = response.json().get("pc_id")
                print(f"새 PC 생성: {self.pc_id}")
                return True
                
        except Exception as e:
            print(f"PC 처리 오류: {e}")
        
        return False
    
    def _create_object(self, device_id: str, status_data: Dict[str, Any]) -> bool:
        """장치를 오브제로 서버에 등록"""
        if not self.store_id or not self.pc_id:
            return False
        
        try:
            # 장치 상태 데이터에서 오브제 정보 생성
            object_data = self._build_object_data(device_id, status_data)
            
            response = requests.post(
                f"{self.base_url}/v1/service/stores/{self.store_id}/pcs/{self.pc_id}/objects",
                json=object_data
            )
            
            if response.status_code == 200:
                object_id = response.json().get("object_id")
                print(f"  오브제 생성됨: {object_id}")
                return True
            else:
                print(f"  오브제 생성 실패: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  오브제 생성 오류: {e}")
        
        return False
    
    def _build_object_data(self, device_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """장치 상태 데이터로부터 오브제 데이터 구성"""
        # 기본 오브제 정보
        object_data = {
            "object_name": f"Device {device_id}",
            "operation_status": "STOP",  # 기본값
            "schedule_flag": False,
            "power_status": "OFF"  # 기본값
        }
        
        # 실제 상태 데이터에서 정보 추출
        if status_data:
            # 전원 상태
            main_power = status_data.get('main_power', {})
            if main_power.get('status'):
                object_data["power_status"] = "ON"
            
            # 동작 상태
            motion = status_data.get('motion', {})
            motion_status = motion.get('status', '').upper()
            if motion_status in ["PLAY", "STOP", "REPEAT"]:
                object_data["operation_status"] = motion_status
            
            # 전력 소비 정보 (있는 경우)
            power_consumption = status_data.get('power_consumption', {})
            if power_consumption:
                object_data["power_consumption"] = power_consumption
            
            # 에러 정보 (있는 경우)
            error_data = status_data.get('error', {})
            if error_data and error_data.get('flag'):
                object_data["error_data"] = [error_data]
        
        return object_data
    
    def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            response = requests.get(f"{self.base_url}/v1/health")
            print(f"서버 연결 테스트: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"서버 연결 실패: {e}")
            return False


if __name__ == "__main__":
    print("=== DeviceServerSync 시작 ===")
    
    sync = DeviceServerSync()
    
    # 서버 연결 테스트
    if not sync.test_server_connection():
        print("서버에 연결할 수 없습니다. 프로그램을 종료합니다.")
        exit(1)
    
    # 동기화 실행
    if sync.sync_all_devices():
        print("\n✅ 동기화가 완료되었습니다!")
        print("이제 SSE 연결을 테스트할 수 있습니다.")
    else:
        print("\n❌ 동기화에 실패했습니다.") 