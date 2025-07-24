import sys
import qdarkstyle
import logging
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from src.mainwindow import MainWindow
import _icons_rc
import os
from datetime import datetime

# ============================================================================
# 로그 파일 생성 설정 (하드코딩)
# ============================================================================
ENABLE_LOG_FILE = False  # True: 로그 파일 생성, False: 콘솔만 출력
# ============================================================================

class TeeOutput:
    """표준 출력을 콘솔과 파일에 동시에 출력하는 클래스"""
    def __init__(self, console_stream, file_stream):
        self.console_stream = console_stream
        self.file_stream = file_stream
    
    def write(self, text):
        # 콘솔에 출력
        self.console_stream.write(text)
        self.console_stream.flush()
        
        # 파일에 출력
        try:
            self.file_stream.write(text)
            self.file_stream.flush()
        except Exception:
            pass  # 파일 쓰기 실패 시 콘솔 출력은 계속 진행
    
    def flush(self):
        self.console_stream.flush()
        try:
            self.file_stream.flush()
        except Exception:
            pass

def setup_logging():
    """로깅 설정을 초기화합니다."""
    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 포맷터 생성
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 콘솔 핸들러 (항상 활성화)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 로그 파일 생성 여부 확인
    if not ENABLE_LOG_FILE:
        logger.info("로그 파일 생성이 비활성화되었습니다. 콘솔 출력만 사용됩니다.")
        return
    
    # 실행 파일의 경로 가져오기
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일인 경우
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 개발 환경에서 실행하는 경우
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 로그 파일 이름 생성 (날짜와 시간 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"remote_gui_log_{timestamp}.txt"
    log_filepath = os.path.join(exe_dir, log_filename)
    
    # 파일 핸들러 (ENABLE_LOG_FILE이 True일 때만 생성)
    try:
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 로그 파일 생성 확인 메시지
        logger.info(f"로그 파일이 생성되었습니다: {log_filepath}")
        
        # print() 문들도 파일에 저장되도록 표준 출력 리디렉션
        try:
            output_file = open(log_filepath.replace('.txt', '_console.txt'), 'w', encoding='utf-8')
            tee_output = TeeOutput(sys.stdout, output_file)
            sys.stdout = tee_output
            
            # 표준 에러도 같은 방식으로 처리
            error_file = open(log_filepath.replace('.txt', '_error.txt'), 'w', encoding='utf-8')
            tee_error = TeeOutput(sys.stderr, error_file)
            sys.stderr = tee_error
            
            print(f"콘솔 출력이 파일에 저장됩니다: {log_filepath.replace('.txt', '_console.txt')}")
            
        except Exception as e:
            logger.warning(f"표준 출력 리디렉션 설정 실패: {e}")
        
    except Exception as e:
        # 파일 핸들러 생성 실패 시에도 콘솔 출력은 계속 작동
        console_handler.setLevel(logging.WARNING)
        logger.warning(f"로그 파일 생성 실패: {e}")


def main():
    """애플리케이션의 메인 진입점입니다."""
    try:
        # 로깅 설정
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("애플리케이션 시작")

        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)
        
        # 저사양 CPU 최적화 설정 적용
        try:
            from performance_config import PerformanceConfig
            PerformanceConfig.apply_qt_optimizations(app)
        except ImportError:
            logger.warning("성능 최적화 설정을 불러올 수 없습니다. 기본 설정으로 실행합니다.")
        except Exception as e:
            logger.warning(f"성능 최적화 적용 중 오류: {e}")

        # 스플래시 스크린 설정 (리소스 경로 사용)
        splash_pix = QPixmap(u":/font_awesome_solid/icons/user/splash.png")
        
        # 화면 크기 얻기
        screen = app.primaryScreen().geometry()
        
        # 스플래시 이미지 크기를 화면 크기의 40%로 조정
        target_width = int(screen.width() * 0.4)
        scaled_splash = splash_pix.scaled(target_width, 
                                       target_width, 
                                       Qt.KeepAspectRatio, 
                                       Qt.SmoothTransformation)
        
        splash = QSplashScreen(scaled_splash, Qt.WindowStaysOnTopHint)
        
        # 스플래시 화면을 중앙으로 이동
        splash.move(
            screen.center().x() - splash.width() // 2,
            screen.center().y() - splash.height() // 2
        )
        
        splash.show()
        app.processEvents()

        # 다크 스타일 시트 설정
        light_stylesheet = qdarkstyle.load_stylesheet(palette=qdarkstyle.LightPalette)
        app.setStyleSheet(light_stylesheet)
        
        # 메인 윈도우 생성
        window = MainWindow()
        
        # 스플래시 스크린을 2초 동안 표시 후 메인 윈도우 표시
        QTimer.singleShot(2000, lambda: [window.show(), splash.finish(window)])
        
        # 이벤트 루프 실행
        exit_code = app.exec()
        
        # 애플리케이션 종료 시 DeviceStatusManager 정리
        try:
            from src.device_status_manager import DeviceStatusManager
            device_status_manager = DeviceStatusManager.get_instance()
            device_status_manager.cleanup()
        except Exception as e:
            logger.error(f"DeviceStatusManager 정리 중 오류: {e}")
        
        # 로그 파일 핸들러 정리 (ENABLE_LOG_FILE이 True일 때만)
        if ENABLE_LOG_FILE:
            try:
                # 표준 출력/에러 복원
                if hasattr(sys.stdout, 'file_stream'):
                    sys.stdout.file_stream.close()
                if hasattr(sys.stderr, 'file_stream'):
                    sys.stderr.file_stream.close()
                
                # 로깅 핸들러 정리
                for handler in logging.getLogger().handlers[:]:
                    if isinstance(handler, logging.FileHandler):
                        handler.close()
                        logging.getLogger().removeHandler(handler)
            except Exception as e:
                logger.warning(f"로그 파일 정리 중 오류: {e}")
        
        logger.info("애플리케이션 종료")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
