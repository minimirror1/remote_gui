from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton
from PySide6.QtCore import Slot
from serial.tools import list_ports
import serial

from src.ui.setting_page_ui import Ui_SettingPage

class SettingPage(QWidget, Ui_SettingPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        print("SettingPage 초기화")
        
        # 시리얼 포트 관련 변수 초기화
        self.serial_port = None          # 실제 연결된 시리얼 포트 객체
        self.port_buttons = []           # 동적으로 생성되는 라디오 버튼 목록
        self.selected_port = None        # 사용자가 선택한 포트 이름
        self.is_connected = False        # 연결 상태를 추적하는 변수 추가

        # 버튼 객체 확인을 위한 디버그 출력
        print("SerialRefreshButton 객체 존재 여부:", self.SerialRefreshButton is not None)
        
        # 포트 목록 새로고침 버튼 시그널 연결
        if self.SerialRefreshButton is not None:
            self.SerialRefreshButton.clicked.connect(self.refresh_ports)
            print("SerialRefreshButton 시그널 연결 완료")
        else:
            print("Error: SerialRefreshButton이 존재하지 않습니다")
        
        # 포트 선택(연결) 버튼 시그널 연결
        self.SerialConnectButton.clicked.connect(self.on_port_selected)

        self.refresh_ports()

    @Slot()
    def refresh_ports(self):
        """시리얼 포트 목록을 새로고침하고, 스크롤 영역에 라디오 버튼을 생성합니다."""
        print("포트 목록 새로고침 시작")

        # 기존에 생성된 라디오 버튼이 있다면 삭제합니다.
        for btn in self.port_buttons:
            btn.deleteLater()
        self.port_buttons.clear()
        
        # 스크롤 영역 레이아웃 설정
        layout = self.scrollAreaWidgetContents.layout()
        if layout is None:
            layout = QVBoxLayout(self.scrollAreaWidgetContents)
            layout.setContentsMargins(0, 0, 0, 0)
            self.scrollAreaWidgetContents.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # 사용 가능한 시리얼 포트 목록을 가져옵니다.
        ports = list(list_ports.comports())
        
        # COM 포트 번호를 기준으로 정렬
        def get_com_num(port):
            # COM 포트 이름에서 숫자 부분을 추출
            try:
                return int(''.join(filter(str.isdigit, port.device)))
            except ValueError:
                return float('inf')  # 숫자가 없는 경우 맨 뒤로 정렬
        
        ports.sort(key=get_com_num)
        print("검색된 포트:", [port.device for port in ports])

        # 각 포트에 대해 간단한 정보를 포함한 라디오 버튼을 생성합니다.
        for port in ports:
            # 포트 정보 구성 (포트 이름과 설명만 포함)
            port_info = f"{port.device}"
            if port.description:
                port_info += f" - {port.description}"
            
            rb = QRadioButton(port_info)
            rb.setProperty("port_device", port.device)  # 실제 포트 이름을 속성으로 저장
            self.port_buttons.append(rb)
            layout.addWidget(rb)
        
        if not self.port_buttons:
            print("사용 가능한 시리얼 포트가 없습니다.")

    @Slot()
    def on_port_selected(self):
        """선택된 시리얼 포트를 확인하고 연결/해제를 처리합니다."""
        print("포트 선택 버튼 클릭됨")
        
        # 이미 연결된 상태라면 연결 해제
        if self.is_connected:
            try:
                if self.serial_port:
                    self.serial_port.close()
                    print(f"포트 연결 해제 성공: {self.selected_port}")
                self.is_connected = False
                self.SerialConnectButton.setText("연결")
                self.selected_port = None
                self.serial_port = None
                return
            except Exception as e:
                print(f"포트 연결 해제 실패: {e}")
                return
        
        # 새로운 연결 시도
        selected_port = None
        for rb in self.port_buttons:
            if rb.isChecked():
                selected_port = rb.property("port_device")
                print(f"선택된 포트: {selected_port}")
                try:
                    self.serial_port = serial.Serial(selected_port, 9600, timeout=1)
                    print(f"포트 연결 성공: {selected_port}")
                    self.is_connected = True
                    self.selected_port = selected_port
                    self.SerialConnectButton.setText("해제")
                except serial.SerialException as e:
                    print(f"포트 연결 실패: {e}")
                break
