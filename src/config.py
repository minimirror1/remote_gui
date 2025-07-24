"""
애플리케이션 설정 관리 모듈
Clean Architecture 원칙에 따라 설정 저장/로드 기능을 제공합니다.
"""
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path
import logging


@dataclass
class BusinessHours:
    """영업시간 정보"""
    monday: str = "09:00-18:00"
    tuesday: str = "09:00-18:00"
    wednesday: str = "09:00-18:00"
    thursday: str = "09:00-18:00"
    friday: str = "09:00-18:00"
    saturday: str = "09:00-18:00"
    sunday: str = "휴무"


@dataclass
class BasicInfo:
    """기본 정보"""
    country: str = "대한민국"
    region: str = "서울특별시"
    store_name: str = "매장명"
    business_hours: BusinessHours = None
    
    def __post_init__(self):
        if self.business_hours is None:
            self.business_hours = BusinessHours()


@dataclass
class ProgramSettings:
    """프로그램 설정값"""
    schedule_function: bool = True
    sync_time_ms: float = 1000.0  # 밀리초 단위


@dataclass
class AppConfig:
    """애플리케이션 전체 설정"""
    config_version: str = "1.0.0"
    basic_info: BasicInfo = None
    program_settings: ProgramSettings = None
    enable_log_file: bool = True  # 기존 로그 파일 설정도 포함
    
    def __post_init__(self):
        if self.basic_info is None:
            self.basic_info = BasicInfo()
        if self.program_settings is None:
            self.program_settings = ProgramSettings()


class IConfigRepository(ABC):
    """설정 저장소 인터페이스 (Port)"""
    
    @abstractmethod
    def save(self, config: AppConfig) -> bool:
        """설정을 저장합니다."""
        pass
    
    @abstractmethod
    def load(self) -> Optional[AppConfig]:
        """설정을 로드합니다."""
        pass
    
    @abstractmethod
    def exists(self) -> bool:
        """설정 파일이 존재하는지 확인합니다."""
        pass


class JsonConfigRepository(IConfigRepository):
    """JSON 파일 기반 설정 저장소 구현체 (Adapter)"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Args:
            config_path: 설정 파일 경로. None이면 기본 경로 사용
        """
        if config_path is None:
            # 실행 파일과 같은 디렉토리에 저장
            if hasattr(os.sys, 'frozen') and os.sys.frozen:
                # PyInstaller로 빌드된 경우
                exe_dir = Path(os.sys.executable).parent
            else:
                # 개발 환경
                exe_dir = Path(__file__).parent.parent
            
            self.config_path = exe_dir / "config.json"
        else:
            self.config_path = config_path
            
        self.logger = logging.getLogger(__name__)
    
    def save(self, config: AppConfig) -> bool:
        """설정을 JSON 파일로 저장합니다."""
        try:
            # 설정 디렉토리가 없으면 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # dataclass를 dict로 변환 (중첩된 dataclass도 처리)
            config_dict = self._dataclass_to_dict(config)
            
            # JSON 파일로 저장 (들여쓰기 포함)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"설정이 저장되었습니다: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 저장 실패: {e}")
            return False
    
    def load(self) -> Optional[AppConfig]:
        """JSON 파일에서 설정을 로드합니다."""
        try:
            if not self.exists():
                self.logger.info("설정 파일이 없습니다. 기본 설정을 사용합니다.")
                return AppConfig()  # 기본 설정 반환
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # dict를 dataclass로 변환
            config = self._dict_to_dataclass(config_dict)
            
            self.logger.info(f"설정을 로드했습니다: {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"설정 로드 실패: {e}")
            return AppConfig()  # 실패 시 기본 설정 반환
    
    def exists(self) -> bool:
        """설정 파일 존재 여부 확인"""
        return self.config_path.exists()
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """dataclass를 중첩 구조 포함하여 dict로 변환"""
        if hasattr(obj, '__dataclass_fields__'):
            # dataclass인 경우
            result = {}
            for field_name, field_value in asdict(obj).items():
                result[field_name] = field_value
            return result
        else:
            return obj
    
    def _dict_to_dataclass(self, data: Dict[str, Any]) -> AppConfig:
        """dict를 AppConfig dataclass로 변환"""
        try:
            # BusinessHours 변환
            business_hours_data = data.get('basic_info', {}).get('business_hours', {})
            business_hours = BusinessHours(**business_hours_data) if business_hours_data else BusinessHours()
            
            # BasicInfo 변환
            basic_info_data = data.get('basic_info', {})
            basic_info = BasicInfo(
                country=basic_info_data.get('country', '대한민국'),
                region=basic_info_data.get('region', '서울특별시'),
                store_name=basic_info_data.get('store_name', '매장명'),
                business_hours=business_hours
            )
            
            # ProgramSettings 변환
            program_settings_data = data.get('program_settings', {})
            program_settings = ProgramSettings(
                schedule_function=program_settings_data.get('schedule_function', True),
                sync_time_ms=program_settings_data.get('sync_time_ms', 1000.0)
            )
            
            # AppConfig 변환
            return AppConfig(
                config_version=data.get('config_version', '1.0.0'),
                basic_info=basic_info,
                program_settings=program_settings,
                enable_log_file=data.get('enable_log_file', True)
            )
            
        except Exception as e:
            self.logger.error(f"설정 데이터 변환 실패: {e}")
            return AppConfig()  # 실패 시 기본 설정


class ConfigManager:
    """설정 관리자 클래스 (싱글톤)"""
    
    _instance = None
    _lock = threading.Lock() if 'threading' in globals() else None
    
    @classmethod
    def get_instance(cls, repository: Optional[IConfigRepository] = None) -> 'ConfigManager':
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            if cls._lock:
                with cls._lock:
                    if cls._instance is None:
                        cls._instance = cls(repository)
            else:
                cls._instance = cls(repository)
        return cls._instance
    
    def __init__(self, repository: Optional[IConfigRepository] = None):
        """
        Args:
            repository: 설정 저장소 구현체. None이면 JsonConfigRepository 사용
        """
        if ConfigManager._instance is not None:
            raise Exception("ConfigManager는 싱글톤 클래스입니다. get_instance()를 사용하세요.")
        
        self.repository = repository or JsonConfigRepository()
        self.current_config: Optional[AppConfig] = None
        self.logger = logging.getLogger(__name__)
        
        # 시작 시 설정 로드
        self.load_config()
    
    def load_config(self) -> AppConfig:
        """설정을 로드하고 현재 설정으로 설정합니다."""
        self.current_config = self.repository.load()
        return self.current_config
    
    def save_config(self, config: Optional[AppConfig] = None) -> bool:
        """설정을 저장합니다."""
        config_to_save = config or self.current_config
        if config_to_save is None:
            self.logger.warning("저장할 설정이 없습니다.")
            return False
        
        success = self.repository.save(config_to_save)
        if success:
            self.current_config = config_to_save
        return success
    
    def get_config(self) -> AppConfig:
        """현재 설정을 반환합니다."""
        if self.current_config is None:
            self.current_config = self.load_config()
        return self.current_config
    
    def update_basic_info(self, **kwargs) -> bool:
        """기본 정보를 업데이트합니다."""
        config = self.get_config()
        
        # 허용된 필드만 업데이트
        allowed_fields = ['country', 'region', 'store_name']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(config.basic_info, field, value)
        
        return self.save_config(config)
    
    def update_business_hours(self, **kwargs) -> bool:
        """영업시간을 업데이트합니다."""
        config = self.get_config()
        
        # 허용된 요일만 업데이트
        allowed_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day, hours in kwargs.items():
            if day in allowed_days:
                setattr(config.basic_info.business_hours, day, hours)
        
        return self.save_config(config)
    
    def update_program_settings(self, **kwargs) -> bool:
        """프로그램 설정을 업데이트합니다."""
        config = self.get_config()
        
        # 허용된 필드만 업데이트
        allowed_fields = ['schedule_function', 'sync_time_ms']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(config.program_settings, field, value)
        
        return self.save_config(config)
    
    def update_log_setting(self, enable_log_file: bool) -> bool:
        """로그 파일 설정을 업데이트합니다."""
        config = self.get_config()
        config.enable_log_file = enable_log_file
        return self.save_config(config)


# threading import (필요한 경우에만)
try:
    import threading
    ConfigManager._lock = threading.Lock()
except ImportError:
    pass 