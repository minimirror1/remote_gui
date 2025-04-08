from PySide6.QtCore import QObject
from src.serial_manager import SerialManager
from src.widgets.serial_protocol import ComProtocol

class SerialCommands(QObject):
    """시리얼 통신 명령어 처리를 위한 클래스"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        super().__init__()
        self.serial_manager = SerialManager.get_instance()
        
    def send_main_power_control(self, power_state: bool) -> bool:
        """
        메인 전원 제어 명령 전송
        Args:
            power_state (bool): True=켜기, False=끄기
        Returns:
            bool: 전송 성공 여부
        """
        if not self.serial_manager.is_port_connected():
            return False
            
        try:
            data = bytes([1 if power_state else 0])
            
            success = self.serial_manager.send_packet(
                receiverId=self.serial_manager.get_target_device_id(),  # 설정된 대상 장치 ID 사용
                senderId=SerialManager.DEFAULT_HOST_ID,  # 호스트 ID
                cmd=ComProtocol.CMD_MAIN_POWER_CONTROL,
                data=data
            )
            
            return success
                
        except Exception:
            return False

    def send_play_control(self, play_state: int) -> bool:
        """
        재생 제어 명령 전송
        Args:
            play_state (int): 재생 상태 (PLAY_ONE=1, PLAY_REPEAT=2, PAUSE=3, STOP=4)
        Returns:
            bool: 전송 성공 여부
        """
        if not self.serial_manager.is_port_connected():
            return False
        
        try:
            data = bytes([play_state])
            
            success = self.serial_manager.send_packet(
                receiverId=self.serial_manager.get_target_device_id(),  # 설정된 대상 장치 ID 사용
                senderId=SerialManager.DEFAULT_HOST_ID,  # 호스트 ID
                cmd=ComProtocol.CMD_PLAY_CONTROL,
                data=data
            )
            
            return success
                
        except Exception:
            return False 
        
    def send_jog_move_cwccw(self, direction: str, speed: int, id_value: int = 0, subid_value: int = 0) -> bool:
        """
        조그 이동 명령 전송 (CW/CCW)
        Args:
            direction (str): 이동 방향 ("CW" 또는 "CCW")
            speed (int): 이동 속도
            id_value (int, optional): 장치 ID. 기본값은 0
            subid_value (int, optional): 서브 ID. 기본값은 0
        Returns:
            bool: 전송 성공 여부
        """
        if not self.serial_manager.is_port_connected():
            return False
            
        try:
            # 방향 값 설정 (0=CCW, 1=CW)
            direction_value = 1 if direction.upper() == "CW" else 0
            
            # 페이로드 구성
            # [id(1), subId(1), speed(4), direction(1)]
            data = bytearray()
            data.append(id_value)  # ID
            data.append(subid_value)  # SubID
            
            # speed 값을 4바이트로 변환하여 추가 (빅 엔디안)
            data.append((speed >> 24) & 0xFF)  # 최상위 바이트
            data.append((speed >> 16) & 0xFF)
            data.append((speed >> 8) & 0xFF)
            data.append(speed & 0xFF)  # 최하위 바이트
            
            # 방향 추가
            data.append(direction_value)
            
            # 명령어 코드 사용
            success = self.serial_manager.send_packet(
                receiverId=self.serial_manager.get_target_device_id(),  # 설정된 대상 장치 ID 사용
                senderId=SerialManager.DEFAULT_HOST_ID,  # 호스트 ID
                cmd=ComProtocol.CMD_JOG_MOVE_CWCCW,
                data=bytes(data)
            )
            
            return success
                
        except Exception:
            return False
