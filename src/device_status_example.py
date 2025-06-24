"""
DeviceStatusManager 사용 예제
SSE 통신이나 다른 컴포넌트에서 장치 상태 데이터를 활용하는 방법을 보여줍니다.
"""

from src.device_status_manager import DeviceStatusManager
from PySide6.QtCore import QObject, QTimer, Slot
import json


class SSEDataProvider(QObject):
    """
    SSE 통신을 위한 데이터 제공자 예제
    DeviceStatusManager에서 최신 장치 상태를 가져와서 SSE 형태로 제공
    """
    
    def __init__(self):
        super().__init__()
        
        # DeviceStatusManager 인스턴스 가져오기
        self.device_status_manager = DeviceStatusManager.get_instance()
        
        # 시그널 연결
        self.device_status_manager.device_status_updated.connect(self.on_device_status_updated)
        self.device_status_manager.device_connected.connect(self.on_device_connected)
        self.device_status_manager.device_disconnected.connect(self.on_device_disconnected)
        
        # 주기적 상태 전송을 위한 타이머 (선택사항)
        self.periodic_timer = QTimer()
        self.periodic_timer.timeout.connect(self.send_periodic_status)
        
    def start_periodic_updates(self, interval_ms=5000):
        """주기적 상태 업데이트 시작 (5초마다)"""
        self.periodic_timer.start(interval_ms)
        print(f"주기적 상태 업데이트 시작 (간격: {interval_ms}ms)")
    
    def stop_periodic_updates(self):
        """주기적 상태 업데이트 중지"""
        self.periodic_timer.stop()
        print("주기적 상태 업데이트 중지")
    
    @Slot(str, dict)
    def on_device_status_updated(self, device_id: str, status_data: dict):
        """장치 상태 업데이트 시 SSE 데이터 전송"""
        sse_data = {
            'type': 'device_status_update',
            'device_id': device_id,
            'data': status_data,
            'timestamp': status_data.get('timestamp', '')
        }
        
        # 실제 SSE 전송 로직이 여기에 들어갑니다
        self.send_sse_data(sse_data)
        print(f"SSE 장치 상태 업데이트 전송: {device_id}")
    
    @Slot(str)
    def on_device_connected(self, device_id: str):
        """장치 연결 시 SSE 알림"""
        sse_data = {
            'type': 'device_connected',
            'device_id': device_id,
            'message': f'Device {device_id} connected'
        }
        
        self.send_sse_data(sse_data)
        print(f"SSE 장치 연결 알림: {device_id}")
    
    @Slot(str)
    def on_device_disconnected(self, device_id: str):
        """장치 연결 해제 시 SSE 알림"""
        sse_data = {
            'type': 'device_disconnected',
            'device_id': device_id,
            'message': f'Device {device_id} disconnected'
        }
        
        self.send_sse_data(sse_data)
        print(f"SSE 장치 연결 해제 알림: {device_id}")
    
    @Slot()
    def send_periodic_status(self):
        """주기적으로 전체 장치 상태 전송"""
        status_summary = self.device_status_manager.get_status_summary()
        
        sse_data = {
            'type': 'periodic_status',
            'data': status_summary
        }
        
        self.send_sse_data(sse_data)
        print(f"주기적 상태 전송: {status_summary['connected_devices']}/{status_summary['total_devices']} 장치")
    
    def send_sse_data(self, data):
        """실제 SSE 데이터 전송 (구현 필요)"""
        # 여기에 실제 SSE 전송 로직을 구현합니다
        # 예: WebSocket, HTTP SSE, 파일 출력 등
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        print(f"SSE 데이터 전송: {json_data}")
    
    def get_current_status_for_api(self):
        """API 요청용 현재 상태 반환"""
        return self.device_status_manager.get_sse_data()
    
    def get_device_list_for_api(self):
        """API용 장치 목록 반환"""
        all_devices = self.device_status_manager.get_all_devices_status()
        connected_devices = self.device_status_manager.get_connected_devices()
        
        device_list = []
        for device_id, status_data in all_devices.items():
            device_info = {
                'id': device_id,
                'connected': device_id in connected_devices,
                'last_update': self.device_status_manager.get_device_last_update_time(device_id),
                'status_summary': {
                    'main_power': status_data.get('main_power', {}).get('status', False),
                    'motion_status': status_data.get('motion', {}).get('status', 'UNKNOWN'),
                    'has_error': status_data.get('error', {}).get('flag', False)
                }
            }
            device_list.append(device_info)
        
        return device_list


class DeviceStatusMonitor:
    """
    DeviceStatusManager를 활용한 간단한 모니터링 예제
    """
    
    def __init__(self):
        self.device_status_manager = DeviceStatusManager.get_instance()
    
    def print_all_devices_status(self):
        """모든 장치의 현재 상태 출력"""
        print("\n=== 전체 장치 상태 ===")
        all_devices = self.device_status_manager.get_all_devices_status()
        connected_devices = self.device_status_manager.get_connected_devices()
        
        if not all_devices:
            print("등록된 장치가 없습니다.")
            return
        
        for device_id, status_data in all_devices.items():
            connected = "연결됨" if device_id in connected_devices else "연결 안됨"
            main_power = status_data.get('main_power', {}).get('status', False)
            motion_status = status_data.get('motion', {}).get('status', 'UNKNOWN')
            last_update = self.device_status_manager.get_device_last_update_time(device_id)
            
            print(f"장치 ID: {device_id}")
            print(f"  상태: {connected}")
            print(f"  메인 전원: {'ON' if main_power else 'OFF'}")
            print(f"  모션 상태: {motion_status}")
            print(f"  마지막 업데이트: {last_update.toString('hh:mm:ss') if last_update else 'N/A'}")
            print()
    
    def get_connected_devices_count(self):
        """연결된 장치 개수 반환"""
        return self.device_status_manager.get_connected_device_count()
    
    def is_device_healthy(self, device_id: str):
        """특정 장치의 건강 상태 확인"""
        status_data = self.device_status_manager.get_device_status(device_id)
        
        if not status_data:
            return False, "장치 데이터 없음"
        
        # 메인 전원이 켜져있고 에러가 없으면 건강한 상태
        main_power = status_data.get('main_power', {}).get('status', False)
        has_error = status_data.get('error', {}).get('flag', False)
        
        if not main_power:
            return False, "메인 전원 OFF"
        
        if has_error:
            error_code = status_data.get('error', {}).get('code', 'unknown')
            return False, f"에러 발생: {error_code}"
        
        return True, "정상"


# 사용 예제
if __name__ == "__main__":
    # SSE 데이터 제공자 생성
    sse_provider = SSEDataProvider()
    
    # 장치 상태 모니터 생성
    monitor = DeviceStatusMonitor()
    
    # 장치 상태 출력
    monitor.print_all_devices_status()
    
    # 연결된 장치 개수 확인
    connected_count = monitor.get_connected_devices_count()
    print(f"연결된 장치 개수: {connected_count}")
    
    # 특정 장치 건강 상태 확인
    is_healthy, message = monitor.is_device_healthy("1")
    print(f"장치 1 건강 상태: {is_healthy}, {message}") 