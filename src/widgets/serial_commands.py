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
                receiverId=0x0001,  # 대상 장치 ID
                senderId=0x0000,    # 호스트 ID
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
                receiverId=0x0001,  # 대상 장치 ID
                senderId=0x0000,    # 호스트 ID
                cmd=ComProtocol.CMD_PLAY_CONTROL,
                data=data
            )
            
            return success
                
        except Exception:
            return False 