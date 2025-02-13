import sys
import qdarkstyle
import logging
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from src.mainwindow import MainWindow
import _icons_rc
import os

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
        
        logger.info("애플리케이션 종료")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
