import sys
import qdarkstyle
import logging
from PySide6.QtWidgets import QApplication
from src.mainwindow import MainWindow

def setup_logging():
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """애플리케이션의 메인 진입점입니다."""
    try:

        # 로깅 설정
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("애플리케이션 시작")

        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)

        # 다크 스타일 시트 설정
        light_stylesheet = qdarkstyle.load_stylesheet(palette=qdarkstyle.LightPalette)
        app.setStyleSheet(light_stylesheet)
        

        # 메인 윈도우 생성 및 표시
        window = MainWindow()
        window.show()
        
        # 이벤트 루프 실행
        exit_code = app.exec()
        
        logger.info("애플리케이션 종료")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
