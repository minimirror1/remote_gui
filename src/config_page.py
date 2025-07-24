from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PySide6.QtCore import Slot
from src.ui.config_page_ui import Ui_ConfigPage
from src.config import ConfigManager, AppConfig, BasicInfo, BusinessHours, ProgramSettings
import json
import os


class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # UI 설정
        self.ui = Ui_ConfigPage()
        self.ui.setupUi(self)
        
        # ConfigManager 인스턴스 가져오기
        self.config_manager = ConfigManager.get_instance()
        
        # 초기 설정
        self.setup_ui()
        
        # 버튼 시그널 연결
        self.ui.loadButton.clicked.connect(self.on_load_clicked)
        self.ui.saveButton.clicked.connect(self.on_save_clicked)
        self.ui.resetButton.clicked.connect(self.on_reset_clicked)
        
        # 설정 변경 시그널 연결
        self.connect_change_signals()
        
        # 현재 설정 로드
        self.load_current_config()

    def setup_ui(self):
        """UI 컴포넌트들의 추가적인 설정"""
        # 설정 버전은 읽기 전용으로 유지
        self.ui.configVersionLineEdit.setReadOnly(True)
        
        # 동기화 시간 설정
        self.ui.syncTimeDoubleSpinBox.setSuffix(" ms")
        self.ui.syncTimeDoubleSpinBox.setDecimals(0)

    def connect_change_signals(self):
        """설정 변경 감지를 위한 시그널 연결"""
        # 기본 정보 필드
        self.ui.countryLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.regionLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.storeNameLineEdit.textChanged.connect(self.on_config_changed)
        
        # 영업 시간 필드
        self.ui.mondayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.tuesdayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.wednesdayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.thursdayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.fridayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.saturdayLineEdit.textChanged.connect(self.on_config_changed)
        self.ui.sundayLineEdit.textChanged.connect(self.on_config_changed)
        
        # 프로그램 설정
        self.ui.scheduleFunctionCheckBox.toggled.connect(self.on_config_changed)
        self.ui.syncTimeDoubleSpinBox.valueChanged.connect(self.on_config_changed)
        
        # 로그 설정
        self.ui.enableLogFileCheckBox.toggled.connect(self.on_config_changed)

    def load_current_config(self):
        """현재 설정을 UI에 로드"""
        try:
            config = self.config_manager.get_config()
            
            # 기본 정보 로드
            self.ui.countryLineEdit.setText(config.basic_info.country)
            self.ui.regionLineEdit.setText(config.basic_info.region)
            self.ui.storeNameLineEdit.setText(config.basic_info.store_name)
            
            # 영업 시간 로드
            business_hours = config.basic_info.business_hours
            self.ui.mondayLineEdit.setText(business_hours.monday)
            self.ui.tuesdayLineEdit.setText(business_hours.tuesday)
            self.ui.wednesdayLineEdit.setText(business_hours.wednesday)
            self.ui.thursdayLineEdit.setText(business_hours.thursday)
            self.ui.fridayLineEdit.setText(business_hours.friday)
            self.ui.saturdayLineEdit.setText(business_hours.saturday)
            self.ui.sundayLineEdit.setText(business_hours.sunday)
            
            # 프로그램 설정 로드
            self.ui.scheduleFunctionCheckBox.setChecked(config.program_settings.schedule_function)
            self.ui.syncTimeDoubleSpinBox.setValue(config.program_settings.sync_time_ms)
            
            # 로그 설정 로드
            self.ui.enableLogFileCheckBox.setChecked(config.enable_log_file)
            
            # 설정 버전 로드
            self.ui.configVersionLineEdit.setText(config.config_version)
            
        except Exception as e:
            print(f"설정 로드 중 오류: {e}")
            QMessageBox.warning(self, "경고", f"설정 로드 중 오류가 발생했습니다: {str(e)}")

    def save_current_config(self):
        """현재 UI 상태를 설정으로 저장"""
        try:
            # 현재 설정 가져오기
            config = self.config_manager.get_config()
            
            # 기본 정보 업데이트
            config.basic_info.country = self.ui.countryLineEdit.text()
            config.basic_info.region = self.ui.regionLineEdit.text()
            config.basic_info.store_name = self.ui.storeNameLineEdit.text()
            
            # 영업 시간 업데이트
            config.basic_info.business_hours.monday = self.ui.mondayLineEdit.text()
            config.basic_info.business_hours.tuesday = self.ui.tuesdayLineEdit.text()
            config.basic_info.business_hours.wednesday = self.ui.wednesdayLineEdit.text()
            config.basic_info.business_hours.thursday = self.ui.thursdayLineEdit.text()
            config.basic_info.business_hours.friday = self.ui.fridayLineEdit.text()
            config.basic_info.business_hours.saturday = self.ui.saturdayLineEdit.text()
            config.basic_info.business_hours.sunday = self.ui.sundayLineEdit.text()
            
            # 프로그램 설정 업데이트
            config.program_settings.schedule_function = self.ui.scheduleFunctionCheckBox.isChecked()
            config.program_settings.sync_time_ms = self.ui.syncTimeDoubleSpinBox.value()
            
            # 로그 설정 업데이트
            config.enable_log_file = self.ui.enableLogFileCheckBox.isChecked()
            
            # 설정 버전 업데이트
            config.config_version = self.ui.configVersionLineEdit.text()
            
            # 파일에 저장
            return self.config_manager.save_config(config)
        except Exception as e:
            print(f"설정 저장 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 중 오류가 발생했습니다: {str(e)}")
            return False

    @Slot()
    def on_load_clicked(self):
        """불러오기 버튼 클릭 처리"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "설정 파일 불러오기",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # UI에 로드된 설정 적용
                self.apply_config_to_ui(config_data)
                
                QMessageBox.information(self, "성공", "설정이 성공적으로 불러와졌습니다.")
                
            except Exception as e:
                QMessageBox.critical(self, "오류", f"설정 파일 불러오기 실패: {str(e)}")

    @Slot()
    def on_save_clicked(self):
        """저장 버튼 클릭 처리"""
        if self.save_current_config():
            QMessageBox.information(self, "성공", "설정이 성공적으로 저장되었습니다.")

    @Slot()
    def on_reset_clicked(self):
        """초기화 버튼 클릭 처리"""
        reply = QMessageBox.question(
            self,
            "설정 초기화",
            "설정을 기본값으로 초기화하시겠습니까?\n현재 변경사항은 모두 사라집니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        """설정을 기본값으로 초기화"""
        try:
            # 기본 설정 객체 생성
            default_config = AppConfig()
            
            # UI에 기본값 적용
            self.apply_config_to_ui(default_config)
            
            QMessageBox.information(self, "완료", "설정이 기본값으로 초기화되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"설정 초기화 중 오류: {str(e)}")

    def apply_config_to_ui(self, config_data):
        """설정 데이터를 UI에 적용"""
        try:
            # JSON 데이터를 AppConfig 객체로 변환
            if isinstance(config_data, dict):
                # dict 형태의 데이터를 AppConfig로 변환
                business_hours_data = config_data.get('basic_info', {}).get('business_hours', {})
                business_hours = BusinessHours(
                    monday=business_hours_data.get('monday', '09:00-18:00'),
                    tuesday=business_hours_data.get('tuesday', '09:00-18:00'),
                    wednesday=business_hours_data.get('wednesday', '09:00-18:00'),
                    thursday=business_hours_data.get('thursday', '09:00-18:00'),
                    friday=business_hours_data.get('friday', '09:00-18:00'),
                    saturday=business_hours_data.get('saturday', '10:00-16:00'),
                    sunday=business_hours_data.get('sunday', '휴무')
                )
                
                basic_info_data = config_data.get('basic_info', {})
                basic_info = BasicInfo(
                    country=basic_info_data.get('country', '대한민국'),
                    region=basic_info_data.get('region', '서울특별시'),
                    store_name=basic_info_data.get('store_name', '시스테믹 본점'),
                    business_hours=business_hours
                )
                
                program_settings_data = config_data.get('program_settings', {})
                program_settings = ProgramSettings(
                    schedule_function=program_settings_data.get('schedule_function', True),
                    sync_time_ms=program_settings_data.get('sync_time_ms', program_settings_data.get('sync_time', 1500.0))
                )
                
                config = AppConfig(
                    config_version=config_data.get('config_version', '1.0.0'),
                    basic_info=basic_info,
                    program_settings=program_settings,
                    enable_log_file=config_data.get('enable_log_file', config_data.get('log_settings', {}).get('enable_log_file', True))
                )
            else:
                # 이미 AppConfig 객체인 경우
                config = config_data
            
            # UI에 적용
            self.ui.countryLineEdit.setText(config.basic_info.country)
            self.ui.regionLineEdit.setText(config.basic_info.region)
            self.ui.storeNameLineEdit.setText(config.basic_info.store_name)
            
            # 영업 시간 적용
            self.ui.mondayLineEdit.setText(config.basic_info.business_hours.monday)
            self.ui.tuesdayLineEdit.setText(config.basic_info.business_hours.tuesday)
            self.ui.wednesdayLineEdit.setText(config.basic_info.business_hours.wednesday)
            self.ui.thursdayLineEdit.setText(config.basic_info.business_hours.thursday)
            self.ui.fridayLineEdit.setText(config.basic_info.business_hours.friday)
            self.ui.saturdayLineEdit.setText(config.basic_info.business_hours.saturday)
            self.ui.sundayLineEdit.setText(config.basic_info.business_hours.sunday)
            
            # 프로그램 설정 적용
            self.ui.scheduleFunctionCheckBox.setChecked(config.program_settings.schedule_function)
            self.ui.syncTimeDoubleSpinBox.setValue(config.program_settings.sync_time_ms)
            
            # 로그 설정 적용
            self.ui.enableLogFileCheckBox.setChecked(config.enable_log_file)
            
            # 설정 버전 적용
            self.ui.configVersionLineEdit.setText(config.config_version)
                
        except Exception as e:
            print(f"설정 UI 적용 중 오류: {e}")
            raise

    @Slot()
    def on_config_changed(self):
        """설정이 변경되었을 때 호출"""
        # 설정 변경 감지 시 필요한 작업 수행
        # 예: 저장되지 않은 변경사항 표시 등
        pass

    def showEvent(self, event):
        """페이지가 표시될 때 호출"""
        super().showEvent(event)
        # 페이지 표시 시 최신 설정 로드
        self.load_current_config()

    def closeEvent(self, event):
        """위젯이 닫힐 때 호출"""
        # 필요시 정리 작업 수행
        super().closeEvent(event)
