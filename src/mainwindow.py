# mainwindow.py

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt  # Qt 플래그를 사용하기 위해 추가

from src.ui.mainwindow_ui import Ui_MainWindow  # Designer에서 uic로 생성된 UI 클래스
from src.home_page import HomePage  # HomePage UI 클래스 import 추가
from src.monitor_page import MonitorPage  # MonitorPage UI 클래스 import 추가
from src.jog_page import JogPage  # JogPage UI 클래스 import 추가
from src.setting_page import SettingPage  # SettingPage UI 클래스 import 추가
from src.help_page import HelpPage  # HelpPage UI 클래스 import 추가

import _icons_rc  # 수정된 import 경로
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Slot
import logging
from PySide6.QtCore import QThread
from src.serial_manager import SerialManager
from PySide6.QtCore import QTimer
import json

# API 관련 임포트 추가
from src.api.api_manager import ApiManager
from src.api.sse_manager import SSEManager  # SSE 매니저 추가

# 자동 동기화 서비스 임포트
from net_test.auto_device_sync import AutoDeviceSync


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 프레임리스 윈도우 설정
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 윈도우 배경을 투명하게 설정
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # UI 클래스 인스턴스를 생성하고 현재 윈도우에 설정합니다.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # SerialManager 인스턴스 가져오기
        self.serial_manager = SerialManager.get_instance()
        self.serial_manager.set_main_window(self)  # MainWindow 참조 설정
        
        # API 매니저 인스턴스 가져오기
        self.api_manager = ApiManager.get_instance()
        
        # API 시그널 연결
        self.api_manager.request_completed.connect(self.handle_api_response)
        self.api_manager.request_error.connect(self.handle_api_error)
        
        # SSE 매니저 인스턴스 가져오기
        self.sse_manager = SSEManager.get_instance()
        
        # SSE 시그널 연결
        self.sse_manager.event_received.connect(self.handle_sse_event)
        self.sse_manager.connection_error.connect(self.handle_sse_error)
        self.sse_manager.connection_established.connect(self.handle_sse_connected)
        self.sse_manager.connection_closed.connect(self.handle_sse_disconnected)
        
        # 자동 장치 동기화 서비스 초기화
        print("🔍 [DEBUG] AutoDeviceSync 초기화 시작...")
        self.auto_device_sync = AutoDeviceSync()
        print("🔍 [DEBUG] AutoDeviceSync 생성 완료")
        
        # 자동 동기화 서비스에 SSE 매니저 참조 전달
        print("🔍 [DEBUG] SSE 매니저 참조 전달 중...")
        self.auto_device_sync.set_sse_manager(self.sse_manager)
        print("🔍 [DEBUG] SSE 매니저 참조 전달 완료")
        
        # 자동 장치 동기화 서비스 시작 (지연 실행으로 GUI 블로킹 방지)
        print("🔍 [DEBUG] 자동 동기화 서비스 지연 시작 예약 (5초 후)")
        QTimer.singleShot(5000, self._start_auto_device_sync)  # 5초 후 시작
        
        # 스레드 초기화
        self.serial_thread = SerialReaderThread()
        self.serial_thread.start()

        # 마우스 드래그를 위한 변수 초기화
        self._drag_pos = None

        # LED 타이머 초기화
        self.tx_timer = QTimer(self)
        self.rx_timer = QTimer(self)
        self.tx_timer.timeout.connect(self.turn_off_tx)
        self.rx_timer.timeout.connect(self.turn_off_rx)
        
        # LED 스타일시트
        self.LED_TX_ON_STYLE = """
            background-color: #ff0000;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        self.LED_RX_ON_STYLE = """
            background-color: #00ff00;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        self.LED_OFF_STYLE = """
            background-color: #808080;
            border: 2px solid black;
            border-radius: 5px;
            color: white;
            min-width: 12px;
            min-height: 12px;
            qproperty-alignment: AlignCenter;
        """
        
        # 초기 LED 상태 설정
        self.init_ui()
        
        # SSE 연결 설정 및 시작
        self.init_sse_connection()

    def init_ui(self):
        """
        UI 초기화 작업을 수행하는 함수입니다.
        예를 들어, 위젯 속성 설정, 시그널-슬롯 연결 등의 작업을 여기에 추가합니다.
        """
        # HomePage UI 초기화 - addWidget 방식으로 변경
        self.home_page = HomePage()
        self.ui.mainPage.addWidget(self.home_page)

        # MonitorPage UI 초기화
        self.monitor_page = MonitorPage()
        self.ui.mainPage.addWidget(self.monitor_page)

        # JogPage UI 초기화
        self.jog_page = JogPage()
        self.ui.mainPage.addWidget(self.jog_page)
        
        # SettingPage UI 초기화
        self.setting_page = SettingPage()
        self.ui.mainPage.addWidget(self.setting_page)
        
        # HelpPage UI 초기화
        self.help_page = HelpPage()
        self.ui.mainPage.addWidget(self.help_page)
        
        # 페이지 간 데이터 연결 설정
        self._connect_page_signals()
        
        # 창 제어 버튼 시그널 연결
        if hasattr(self.ui, 'closeBtn'):
            self.ui.closeBtn.clicked.connect(self.close)

        
        if hasattr(self.ui, 'minimizeBtn'):
            self.ui.minimizeBtn.clicked.connect(self.showMinimized)
        
        if hasattr(self.ui, 'restoreBtn'):
            self.ui.restoreBtn.clicked.connect(self.toggle_maximize_restore)
            
        # 페이지 전환 버튼 시그널 연결        
        self.ui.HomeButton.clicked.connect(lambda: self.change_page(0))  # HomePage
        self.ui.monitorButton.clicked.connect(lambda: self.change_page(1))  # MonitorPage
        self.ui.PlayButton.clicked.connect(lambda: self.change_page(0))  # PlayPage
        self.ui.jogButton.clicked.connect(lambda: self.change_page(2))   # JogPage
        self.ui.SettingButton.clicked.connect(lambda: self.change_page(3))  # SettingPage
        self.ui.HelpButton.clicked.connect(lambda: self.change_page(4))  # HelpPage

        # 마우스 이벤트 추적을 위해 위젯들의 mouseTracking 활성화
        self.ui.centralwidget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.ui.headerContainer.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # LED 초기 스타일 설정
        self.ui.labelTx.setStyleSheet(self.LED_OFF_STYLE)
        self.ui.labelRx.setStyleSheet(self.LED_OFF_STYLE)

    def _connect_page_signals(self):
        """페이지 간 시그널 연결"""
        # SettingPage에서 장치 스캔이 완료되었을 때 MonitorPage로 장치 목록 전달
        # 현재는 수동으로 전달하는 메서드 추가 (추후 시그널로 변경 가능)
        pass
        
    def transfer_scanned_devices_to_monitor(self):
        """Setting 페이지에서 스캔된 장치들을 Monitor 페이지로 전달"""
        if hasattr(self.setting_page, 'found_devices') and self.setting_page.found_devices:
            # 스캔된 장치 ID 목록을 Monitor 페이지로 전달
            scanned_ids = self.setting_page.found_devices.copy()
            self.monitor_page.set_scanned_devices(scanned_ids)
            print(f"스캔된 장치 {len(scanned_ids)}개를 Monitor 페이지로 전달: {scanned_ids}")
            return True
        else:
            print("스캔된 장치가 없습니다.")
            return False

    def init_sse_connection(self):
        """SSE 연결 초기화 및 시작"""
        print("🔍 [DEBUG] SSE 연결 초기화 시작...")
        
        # SSE 연결 설정 (새로운 API 구조)
        print("🔍 [DEBUG] SSE 매니저 설정 중...")
        self.sse_manager.configure(
            base_url="https://robot-monitor-dev.systemiic.com",
            headers={}  # Bearer 토큰이 필요하면 여기에 추가
        )
        print("🔍 [DEBUG] SSE 매니저 설정 완료")
        
        # 특정 이벤트 타입에 대한 핸들러 등록 (새로운 시그널 구조)
        print("🔍 [DEBUG] SSE 이벤트 핸들러 등록 중...")
        self.sse_manager.register_handler("power", self.handle_power_event_data)
        self.sse_manager.register_handler("message", self.handle_message_event_data)
        print("🔍 [DEBUG] SSE 이벤트 핸들러 등록 완료")
        
        # 새로운 시그널 연결 (object_id 포함)
        print("🔍 [DEBUG] SSE 시그널 연결 중...")
        self.sse_manager.event_received.connect(self.handle_sse_event)
        self.sse_manager.connection_error.connect(self.handle_sse_error)
        self.sse_manager.connection_established.connect(self.handle_sse_connected)
        self.sse_manager.connection_closed.connect(self.handle_sse_disconnected)
        print("🔍 [DEBUG] SSE 시그널 연결 완료")
        
        # SSE 연결 시작 (모든 오브제 연결)
        print("🔍 [DEBUG] SSE 연결 시작 중... (여기서 멈출 수 있음)")
        self.sse_manager.start()
        print("🔍 [DEBUG] ✅ SSE 연결 시작 완료")
        self.logger.info("SSE 연결이 시작되었습니다.")

    @Slot(str, dict)
    def handle_power_event_data(self, object_id, data):
        """전원 이벤트 데이터 처리"""
        self.logger.info(f"전원 이벤트 처리 (Object {object_id}): {data}")
        # 여기에 전원 이벤트 처리 로직 구현
    
    @Slot(str, dict)
    def handle_message_event_data(self, object_id, data):
        """메시지 이벤트 데이터 처리"""
        self.logger.info(f"메시지 이벤트 처리 (Object {object_id}): {data}")
        # 여기에 메시지 이벤트 처리 로직 구현

    @Slot(str, str, dict)
    def handle_sse_event(self, object_id, event_type, data):
        """SSE 이벤트 수신 처리"""
        self.logger.info(f"SSE 이벤트 수신: Object={object_id}, 타입={event_type}, 데이터={data}")
        
        # 이벤트 타입에 따른 처리 로직
        if event_type == 'power':
            # 전원 이벤트 처리
            self._handle_power_event(object_id, data)
        elif event_type == 'message':
            # 일반 메시지 처리
            self._handle_message(object_id, data)
        elif event_type == 'control':
            # 제어 명령 처리
            self._handle_control_command(object_id, data)
        else:
            self.logger.debug(f"처리되지 않은 이벤트 타입: {event_type} (Object: {object_id})")
    
    def _handle_power_event(self, object_id, data):
        """전원 이벤트 처리"""
        try:
            # 전원 상태 변경 이벤트 처리
            power_status = data.get('power_status')
            
            if power_status == 'ON':
                self.logger.info(f"전원 ON 이벤트 수신: Object ID={object_id}")
                # 실제 디바이스 전원 켜기 로직 구현
                # 예: self.device_controller.turn_on(object_id)
                
            elif power_status == 'OFF':
                self.logger.info(f"전원 OFF 이벤트 수신: Object ID={object_id}")
                # 실제 디바이스 전원 끄기 로직 구현
                # 예: self.device_controller.turn_off(object_id)
                
            else:
                self.logger.info(f"전원 상태 변경: {power_status}, Object ID={object_id}")
                
        except Exception as e:
            self.logger.error(f"전원 이벤트 처리 중 오류 발생: {str(e)}")
    
    def _handle_message(self, object_id, data):
        """일반 메시지 이벤트 처리"""
        self.logger.info(f"메시지 이벤트 처리 (Object {object_id}): {data}")
        # 메시지 처리 로직 구현
        # 예: self.ui.update_status_message(data.get('message'))
    
    def _handle_control_command(self, object_id, data):
        """제어 명령 이벤트 처리"""
        self.logger.info(f"제어 명령 처리 (Object {object_id}): {data}")
        # 제어 명령 처리 로직 구현
        # 예: self.robot_controller.execute_command(data)
    
    @Slot(str)
    def handle_sse_connected(self, object_id):
        """SSE 연결 성공 처리"""
        self.logger.info(f"SSE 서버에 연결되었습니다 (Object: {object_id})")
        # 연결 성공 시 추가 처리 로직
    
    @Slot(str, str)
    def handle_sse_error(self, object_id, error_msg):
        """SSE 연결 오류 처리"""
        self.logger.error(f"SSE 연결 오류 (Object: {object_id}): {error_msg}")
        # 오류 처리 로직 (재연결 시도, 사용자에게 알림 등)
    
    @Slot(str)
    def handle_sse_disconnected(self, object_id):
        """SSE 연결 종료 처리"""
        self.logger.info(f"SSE 연결이 종료되었습니다 (Object: {object_id})")
        # 연결 종료 처리 로직
    
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            # 복원 상태일 때 아이콘 변경이 필요한 경우
            # self.ui.restoreBtn.setIcon(QIcon(":/icons/maximize.png"))
        else:
            self.showMaximized()
            # 최대화 상태일 때 아이콘 변경이 필요한 경우
            # self.ui.restoreBtn.setIcon(QIcon(":/icons/restore.png"))

    def change_page(self, index):
        """
        스택 위젯의 페이지를 전환하는 메서드
        :param index: 전환할 페이지의 인덱스
        """
        self.ui.mainPage.setCurrentIndex(index)

    def on_pushButton_clicked(self):
        """
        pushButton 클릭 이벤트 핸들러 예시입니다.
        """
        print("PushButton이 클릭되었습니다.")

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton:
            # 마우스 Y 좌표가 0-30 픽셀 범위 내에 있을 때만 드래그 허용
            if event.pos().y() <= 30:
                self._drag_pos = event.globalPos() - self.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트"""
        self._drag_pos = None
        event.accept()

    def closeEvent(self, event):
        """애플리케이션 종료 시 리소스 정리"""
        try:
            print("애플리케이션 종료 중...")
            
            # 자동 동기화 서비스 중지 (가장 먼저)
            if hasattr(self, 'auto_device_sync'):
                print("자동 동기화 서비스 중지 중...")
                self.auto_device_sync.stop()
                
            # SSE 연결 중지
            if hasattr(self, 'sse_manager'):
                print("SSE 연결 중지 중...")
                self.sse_manager.stop()
                
            # 장치 상태 매니저 정리
            if hasattr(self, 'device_status_manager'):
                print("장치 상태 매니저 정리 중...")
                self.device_status_manager.cleanup()
                
            # 시리얼 매니저 정리
            if hasattr(self, 'serial_manager'):
                print("시리얼 매니저 정리 중...")
                self.serial_manager.cleanup()
                
            # 모든 스레드가 정리될 때까지 잠시 대기
            print("스레드 정리 대기 중...")
            import time
            time.sleep(0.5)  # 500ms 대기
                
            print("리소스 정리 완료")
            
        except Exception as e:
            print(f"종료 중 오류: {e}")
        finally:
            # 부모 클래스의 closeEvent 호출
            super().closeEvent(event)

    def __del__(self):
        """소멸자"""
        try:
            # SSE 연결 정리
            if hasattr(self, 'sse_manager'):
                self.sse_manager.stop()
                
            # 시리얼 연결 정리
            if hasattr(self, 'serial_thread'):
                self.serial_thread.stop()
                self.serial_thread.wait()
        except Exception as e:
            self.logger.error(f"객체 삭제 중 에러 발생: {str(e)}")

    def indicate_tx(self):
        """TX LED를 켜고 타이머 시작"""
        self.ui.labelTx.setStyleSheet(self.LED_TX_ON_STYLE)
        self.tx_timer.start(100)  # 100ms 후 LED 끄기

    def indicate_rx(self):
        """RX LED를 켜고 타이머 시작"""
        self.ui.labelRx.setStyleSheet(self.LED_RX_ON_STYLE)
        self.rx_timer.start(100)  # 100ms 후 LED 끄기

    def turn_off_tx(self):
        """TX LED 끄기"""
        self.ui.labelTx.setStyleSheet(self.LED_OFF_STYLE)
        self.tx_timer.stop()

    def turn_off_rx(self):
        """RX LED 끄기"""
        self.ui.labelRx.setStyleSheet(self.LED_OFF_STYLE)
        self.rx_timer.stop()

    def handle_api_response(self, data):
        """API 응답 처리"""
        self.logger.info(f"API 응답 데이터: {data}")
        # 응답 처리 로직 구현

    def handle_api_error(self, error_msg):
        """API 에러 처리"""
        self.logger.error(f"API 오류: {error_msg}")
        # 에러 처리 로직 구현

    def _start_auto_device_sync(self):
        """자동 장치 동기화 서비스 시작 (지연 실행)"""
        try:
            print("🔍 [DEBUG] 자동 동기화 서비스 시작...")
            
            # SSE 매니저 참조 전달 (동적 매핑을 위해 필요)
            self.auto_device_sync.set_sse_manager(self.sse_manager)
            
            # 다중 장치 환경에서 안정성을 위해 체크 간격을 20초로 증가
            self.auto_device_sync.start(check_interval=20000)  # 간단한 인터페이스 사용
            
            print("🔍 [DEBUG] 자동 동기화 서비스 시작 완료")
        except Exception as e:
            print(f"🔍 [DEBUG] ❌ 자동 동기화 서비스 시작 실패: {e}")
            import traceback
            traceback.print_exc()


class SerialReaderThread(QThread):
    def __init__(self):
        super().__init__()
        self._is_running = True
        
    def run(self):
        while self._is_running:
            # 시리얼 읽기 작업
            pass
            
    def stop(self):
        self._is_running = False
