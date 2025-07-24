"""
설정 시스템 사용 예제
이 파일은 config.py에서 제공하는 설정 관리 기능의 사용법을 보여줍니다.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import ConfigManager, AppConfig, BasicInfo, BusinessHours, ProgramSettings
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def example_basic_usage():
    """기본 사용법 예제"""
    print("=== 기본 사용법 예제 ===")
    
    # 설정 관리자 인스턴스 가져오기
    config_manager = ConfigManager.get_instance()
    
    # 현재 설정 가져오기
    current_config = config_manager.get_config()
    
    print(f"매장명: {current_config.basic_info.store_name}")
    print(f"국가: {current_config.basic_info.country}")
    print(f"스케줄 기능: {current_config.program_settings.schedule_function}")
    print(f"동기화 시간: {current_config.program_settings.sync_time_ms}ms")
    print(f"로그 파일 생성: {current_config.enable_log_file}")
    print()

def example_update_basic_info():
    """기본 정보 업데이트 예제"""
    print("=== 기본 정보 업데이트 예제 ===")
    
    config_manager = ConfigManager.get_instance()
    
    # 기본 정보 업데이트
    success = config_manager.update_basic_info(
        store_name="강남점",
        region="강남구",
        country="대한민국"
    )
    
    if success:
        print("기본 정보가 업데이트되었습니다.")
        config = config_manager.get_config()
        print(f"새 매장명: {config.basic_info.store_name}")
        print(f"새 지역: {config.basic_info.region}")
    else:
        print("기본 정보 업데이트에 실패했습니다.")
    print()

def example_update_business_hours():
    """영업시간 업데이트 예제"""
    print("=== 영업시간 업데이트 예제 ===")
    
    config_manager = ConfigManager.get_instance()
    
    # 영업시간 업데이트
    success = config_manager.update_business_hours(
        monday="08:00-20:00",
        saturday="10:00-18:00",
        sunday="12:00-17:00"
    )
    
    if success:
        print("영업시간이 업데이트되었습니다.")
        config = config_manager.get_config()
        hours = config.basic_info.business_hours
        print(f"월요일: {hours.monday}")
        print(f"토요일: {hours.saturday}")
        print(f"일요일: {hours.sunday}")
    else:
        print("영업시간 업데이트에 실패했습니다.")
    print()

def example_update_program_settings():
    """프로그램 설정 업데이트 예제"""
    print("=== 프로그램 설정 업데이트 예제 ===")
    
    config_manager = ConfigManager.get_instance()
    
    # 프로그램 설정 업데이트
    success = config_manager.update_program_settings(
        schedule_function=False,
        sync_time_ms=2500.0
    )
    
    if success:
        print("프로그램 설정이 업데이트되었습니다.")
        config = config_manager.get_config()
        settings = config.program_settings
        print(f"스케줄 기능: {settings.schedule_function}")
        print(f"동기화 시간: {settings.sync_time_ms}ms")
    else:
        print("프로그램 설정 업데이트에 실패했습니다.")
    print()

def example_update_log_setting():
    """로그 설정 업데이트 예제"""
    print("=== 로그 설정 업데이트 예제 ===")
    
    config_manager = ConfigManager.get_instance()
    
    # 로그 파일 생성 비활성화
    success = config_manager.update_log_setting(enable_log_file=False)
    
    if success:
        print("로그 설정이 업데이트되었습니다.")
        config = config_manager.get_config()
        print(f"로그 파일 생성: {config.enable_log_file}")
    else:
        print("로그 설정 업데이트에 실패했습니다.")
    print()

def example_manual_config_creation():
    """수동으로 설정 생성하는 예제"""
    print("=== 수동 설정 생성 예제 ===")
    
    # 영업시간 설정
    business_hours = BusinessHours(
        monday="07:00-22:00",
        tuesday="07:00-22:00",
        wednesday="07:00-22:00",
        thursday="07:00-22:00",
        friday="07:00-22:00",
        saturday="08:00-20:00",
        sunday="10:00-18:00"
    )
    
    # 기본 정보 설정
    basic_info = BasicInfo(
        country="대한민국",
        region="부산광역시",
        store_name="부산 해운대점",
        business_hours=business_hours
    )
    
    # 프로그램 설정
    program_settings = ProgramSettings(
        schedule_function=True,
        sync_time_ms=800.0
    )
    
    # 전체 설정 구성
    custom_config = AppConfig(
        config_version="1.0.0",
        basic_info=basic_info,
        program_settings=program_settings,
        enable_log_file=True
    )
    
    # 설정 저장
    config_manager = ConfigManager.get_instance()
    success = config_manager.save_config(custom_config)
    
    if success:
        print("커스텀 설정이 저장되었습니다.")
        print(f"매장명: {custom_config.basic_info.store_name}")
        print(f"지역: {custom_config.basic_info.region}")
        print(f"월요일 영업시간: {custom_config.basic_info.business_hours.monday}")
    else:
        print("커스텀 설정 저장에 실패했습니다.")
    print()

def example_config_file_info():
    """설정 파일 정보 확인 예제"""
    print("=== 설정 파일 정보 확인 ===")
    
    config_manager = ConfigManager.get_instance()
    repository = config_manager.repository
    
    print(f"설정 파일 경로: {repository.config_path}")
    print(f"설정 파일 존재 여부: {repository.exists()}")
    
    if repository.exists():
        import os
        stat = os.stat(repository.config_path)
        print(f"파일 크기: {stat.st_size} bytes")
        print(f"마지막 수정 시간: {stat.st_mtime}")
    print()

def main():
    """메인 실행 함수"""
    print("설정 시스템 사용 예제를 실행합니다.\n")
    
    # 기본 사용법
    example_basic_usage()
    
    # 설정 파일 정보
    example_config_file_info()
    
    # 각종 업데이트 예제
    example_update_basic_info()
    example_update_business_hours()
    example_update_program_settings()
    example_update_log_setting()
    
    # 수동 설정 생성
    example_manual_config_creation()
    
    print("모든 예제가 완료되었습니다.")
    print("config.json 파일을 확인해보세요.")

if __name__ == "__main__":
    main() 