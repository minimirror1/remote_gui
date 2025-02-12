import enum
import struct
import time
from PySide6.QtCore import QObject, Signal


class FileTransferStage(enum.Enum):
    REQUEST_RECEIVE = 1    # 파일 수신 요청
    READY_TO_RECEIVE = 2   # 수신 준비 완료
    RECEIVING_DATA = 3     # 데이터 수신 중
    VERIFY_CHECKSUM = 4    # 체크섬 검증


class ComProtocol(QObject):
    # 시그널 정의
    data_sent = Signal(bytes)  # 데이터 전송 시그널 추가
    main_power_status_changed = Signal(bool)  # 전원 상태 변경 시그널 추가
    status_sync_changed = Signal(dict)  # 시간, 카운트, 전압/전류 정보를 딕셔너리로 전달
    sync_success = Signal()  # 동기화 성공 시그널
    sync_failed = Signal()   # 동기화 실패 시그널
    play_control_status_changed = Signal(int)  # 재생 상태 변경 시그널

    # 명령어 및 상수 정의
    # 네트워크 0x0000 ~ 0x00FF
    CMD_ACK_BIT = 0x8000
    CMD_PING = 0x0001
    CMD_PONG = CMD_PING | CMD_ACK_BIT  # PONG 응답용
    CMD_FILE_RECEIVE = 0x0002         # 파일 수신 요청
    CMD_FILE_RECEIVE_ACK = CMD_FILE_RECEIVE | CMD_ACK_BIT
    CMD_CONFIG = 0x0003
    # 상태 동기화
    CMD_STATUS_SYNC = 0x0010
    CMD_STATUS_SYNC_ACK = CMD_STATUS_SYNC | CMD_ACK_BIT
    # 새 세션 연결결    
    CMD_SESSION_SYNC = 0x0020
    CMD_SESSION_SYNC_ACK = CMD_SESSION_SYNC | CMD_ACK_BIT

    # 제어 0x0100 ~ 0x01FF
    CMD_MAIN_POWER_CONTROL = 0x0100
    CMD_MAIN_POWER_CONTROL_ACK = CMD_MAIN_POWER_CONTROL | CMD_ACK_BIT

    CMD_PLAY_CONTROL = 0x0110;
    CMD_PLAY_CONTROL_ACK = CMD_PLAY_CONTROL | CMD_ACK_BIT;



    MAX_RETRY_COUNT = 5
    MAX_FILENAME_LENGTH = 256
    MAX_FILE_SIZE = 1024 * 1024  # 1MB

    START_MARKER = 0x16
    START_SEQUENCE_LENGTH = 4
    CRC_LENGTH = 0x02
    PACKET_TIMEOUT_MS = 100

    CRC16_INIT = 0xFFFF
    CRC16_POLY = 0x1021  # CCITT 다항식

    # CRC16 XMODEM 테이블
    CRC16_TABLE = [
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
        0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
        0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
        0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
        0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
        0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
        0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
        0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
        0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
        0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
        0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
        0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
        0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
        0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
        0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
        0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
        0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
        0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
    ]

    class ReceiveState(enum.Enum):
        WAIT_START = 0
        READ_LENGTH = 1
        READ_RECEIVER_ID = 2
        READ_SENDER_ID = 3
        READ_CMD = 4
        READ_PAYLOAD = 5
        # VERIFY_CRC 단계 등 필요에 따라 추가

    class FileTransferContext:
        def __init__(self):
            self.filename = ""           # 최대 MAX_FILENAME_LENGTH 문자
            self.fileSize = 0
            self.bufferSize = 0
            self.currentIndex = 0
            self.retryCount = 0
            self.isTransferring = False
            self.isSender = False
            self.receivedSize = 0
            self.checksum = 0

    def __init__(self, serial, tick):
        """
        :param serial: 시리얼 입출력을 위한 인터페이스 (write, read 메소드 등 구현되어 있어야 함)
        :param tick: 타이머 혹은 시간 관련 인터페이스 (필요 시 구현)
        """
        super().__init__()  # QObject 초기화
        self.serial = serial
        self.tick = tick

        self.currentState = ComProtocol.ReceiveState.WAIT_START
        self.lastReceiveTime = 0
        self.expectedLength = 0
        self.receiverId = 0
        self.senderId = 0
        self.payloadIndex = 0
        self.startSequenceCount = 0

        self.receiveBuffer = bytearray()  # 수신된 데이터 저장용 버퍼

        self.receivedCRC = 0
        self.calculatedCRC = 0
        self.cmd = 0

        self.fileContext = ComProtocol.FileTransferContext()

        # 시퀀스 번호 관련 변수 추가
        self.currentSequenceNumber = 0
        self.expectedSequenceNumber = 0
        self.missingPacketCount = 0
        self.SEQUENCE_JUMP_THRESHOLD = 3

        # sync 관련 변수 추가
        self.sync_retry_count = 0
        self.sync_timer = None
        self.MAX_SYNC_RETRIES = 3
        self.SYNC_INTERVAL = 500  # ms
        self.waiting_for_sync = False

    def buildPacket(self, receiverId, senderId, cmd, data):
        packet = bytearray()

        # 시작 마커 추가
        for _ in range(ComProtocol.START_SEQUENCE_LENGTH):
            packet.append(ComProtocol.START_MARKER)

        # 총 길이 = header(8) + payload + CRC(2)
        length = 8 + len(data) + 2
        packet.extend(struct.pack('>H', length))
        
        # 헤더에 시퀀스 번호 추가
        packet.extend(struct.pack('>H', receiverId))
        packet.extend(struct.pack('>H', senderId))
        packet.extend(struct.pack('>H', cmd))
        packet.extend(struct.pack('>H', self.currentSequenceNumber))
        packet.extend(data)

        # CRC 계산 및 추가
        crc_start = ComProtocol.START_SEQUENCE_LENGTH + 2
        crc_data = packet[crc_start:crc_start + 8 + len(data)]
        crc = self.calculateCRC16(crc_data, len(crc_data))
        packet.extend(struct.pack('>H', crc))

        # 시퀀스 번호 증가
        self.currentSequenceNumber = (self.currentSequenceNumber + 1) & 0xFFFF

        return packet

    def sendData(self, receiverId, senderId, cmd, data):
        """
        데이터를 패킷으로 구성하여 시리얼 인터페이스로 전송한다.
        """
        packet = self.buildPacket(receiverId, senderId, cmd, data)
        result = self.serial.write(packet)

        #print(f"[TX] Sequence: {self.currentSequenceNumber-1}, CMD: 0x{cmd:04X}")  # 현재 전송된 패킷의 시퀀스 번호
        
        if result > 0:
            self.data_sent.emit(packet)
        return result

    def receiveData(self, data):
        """
        시리얼 인터페이스에서 읽어온 데이터를 내부 버퍼에 추가한다.
        :param data: bytes-like object
        """
        self.receiveBuffer.extend(data)

    def isDataAvailable(self):
        """
        수신 버퍼에 데이터가 있는지 여부 반환.
        """
        return len(self.receiveBuffer) > 0

    def processReceivedData(self):
        """
        내부 버퍼에 쌓인 데이터를 상태 머신에 따라 하나 이상의 패킷 단위로 처리한다.
        실제 구현에서는 부분적으로 수신된 패킷 처리 등 보다 정교한 로직이 필요함.
        """
        # 충분한 데이터가 있을 때까지 반복 처리
        while len(self.receiveBuffer) >= (ComProtocol.START_SEQUENCE_LENGTH + 2):
            # 시작 마커 확인
            expected_start = bytes([ComProtocol.START_MARKER]) * ComProtocol.START_SEQUENCE_LENGTH
            if self.receiveBuffer[:ComProtocol.START_SEQUENCE_LENGTH] != expected_start:
                # 시작 마커가 아닌 경우 한 바이트씩 제거하며 동기화
                self.receiveBuffer.pop(0)
                continue

            # 시작 마커 다음 2바이트에서 길이 필드를 확인
            if len(self.receiveBuffer) < ComProtocol.START_SEQUENCE_LENGTH + 2:
                break  # 아직 길이 정보가 완전히 수신되지 않음

            length_bytes = self.receiveBuffer[ComProtocol.START_SEQUENCE_LENGTH:
                                              ComProtocol.START_SEQUENCE_LENGTH + 2]
            packet_length = struct.unpack('>H', length_bytes)[0]
            total_packet_length = ComProtocol.START_SEQUENCE_LENGTH + packet_length

            print(f"packet_length: {packet_length}, total_packet_length: {total_packet_length}")

            if len(self.receiveBuffer) < total_packet_length + ComProtocol.CRC_LENGTH:
                break  # 전체 패킷 수신 전

            # 패킷 추출
            packet = self.receiveBuffer[:total_packet_length + ComProtocol.CRC_LENGTH]
            #del self.receiveBuffer[:total_packet_length + ComProtocol.CRC_LENGTH]  # CRC 길이를 포함하여 삭제
            # 250212 버그 수정 : 버퍼 완전 비우기
            del self.receiveBuffer[:]

            # 패킷 파싱
            offset = ComProtocol.START_SEQUENCE_LENGTH + 2
            receiverId = struct.unpack('>H', packet[offset:offset + 2])[0]
            offset += 2
            senderId = struct.unpack('>H', packet[offset:offset + 2])[0]
            offset += 2
            cmd = struct.unpack('>H', packet[offset:offset + 2])[0]
            offset += 2
            seq = struct.unpack('>H', packet[offset:offset + 2])[0]
            offset += 2
            
            #print(f"[RX] Received Sequence: {seq}, CMD: 0x{cmd:04X}")  # 수신된 패킷의 시퀀스 번호

            # payload 길이 계산
            payload_length = packet_length - 10
            payload = packet[offset:offset + payload_length]
            offset += payload_length

            if cmd == ComProtocol.CMD_SESSION_SYNC:
                if len(payload) >= 6:
                    authToken = struct.unpack('>H', payload[4:6])[0]
                    if authToken == 0xABCD:
                        # print(f"[SYNC] Resetting sequence number (current: {self.expectedSequenceNumber} -> 0)")
                        self.expectedSequenceNumber = 0
            else:
                diff = (seq - self.expectedSequenceNumber) & 0xFFFF
                if diff == 0:
                    # print(f"[SEQ] Sequence match: {seq}")
                    self.expectedSequenceNumber = (self.expectedSequenceNumber + 1) & 0xFFFF
                elif diff > 0 and diff <= self.SEQUENCE_JUMP_THRESHOLD:
                    # print(f"[SEQ] Missing {diff} packets")
                    self.missingPacketCount += diff
                    self.expectedSequenceNumber = (seq + 1) & 0xFFFF
                elif diff > 0:
                    # print(f"[SEQ] Large sequence jump: {diff} packets")
                    self.missingPacketCount += diff
                    self.expectedSequenceNumber = (seq + 1) & 0xFFFF
                else:
                    # print(f"[SEQ] Old sequence number received: {seq}")
                    continue

            # CRC 검증을 위한 데이터 준비
            crc_start = ComProtocol.START_SEQUENCE_LENGTH +2
            crc_end = offset  # CRC 필드 직전까지
            
            # 패킷 내용을 hex 형식으로 출력
            #print("수신된 패킷 (hex):", " ".join([f"{b:02x}" for b in packet]))
            if crc_end <= crc_start:
                # 유효하지 않은 패킷 길이
                continue
                
            crc_data = packet[crc_start:crc_end]

            #print("crc_data 패킷 (hex):", " ".join([f"{b:02x}" for b in crc_data]))
            
            try:
                received_crc = struct.unpack('>H', packet[offset:offset + 2])[0]
            except struct.error:
                continue

            # CRC 계산 및 검증
            calculated_crc = self.calculateCRC16(crc_data, len(crc_data))
            if calculated_crc != received_crc:
                continue

            # 명령 처리
            self.processCommand(senderId, receiverId, cmd, payload, payload_length)

    def sendPing(self, targetId):
        """
        대상에게 ping 요청을 보낸다.
        """
        self.sendData(targetId, 0, ComProtocol.CMD_PING, b'')

    # --- 사용자가 필요에 따라 재정의할 수 있는 핸들러들 ---
    def handlePing(self, senderId, payload):
        """
        ping 요청에 대한 기본 처리 (기본값: PONG 응답 전송).
        """
        print("ping 요청 수신")
        self.sendData(senderId, 0, ComProtocol.CMD_PONG, payload)


    def handleData(self, senderId, payload):
        """
        데이터 패킷 수신에 대한 처리 (필요시 재정의).
        """
        pass

    def handleConfig(self, senderId, payload):
        """
        설정 관련 패킷 수신에 대한 처리 (필요시 재정의).
        """
        pass
    
    def handleStatusSyncAck(self, senderId, payload):
        """상태 동기화 응답 처리"""
        if len(payload) < 15:  # 페이로드 길이 체크 (기존 11바이트 + 모션시간 4바이트)
            return

        try:
            # 시간 정보 파싱
            hours = payload[0]
            minutes = payload[1]
            seconds = payload[2]

            # 동작 회차 정보 파싱
            current_count = struct.unpack('>H', payload[3:5])[0]
            total_count = struct.unpack('>H', payload[5:7])[0]

            # 에너지 정보 파싱
            voltage = struct.unpack('>H', payload[7:9])[0]
            current = struct.unpack('>H', payload[9:11])[0]

            # 모션 시간 정보 파싱 추가
            motion_current = struct.unpack('>H', payload[11:13])[0]
            motion_end = struct.unpack('>H', payload[13:15])[0]

            # 데이터를 딕셔너리로 구성
            status_data = {
                'time': {
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds
                },
                'count': {
                    'current': current_count,
                    'total': total_count
                },
                'power': {
                    'voltage': voltage,
                    'current': current
                },
                'motion': {
                    'current': motion_current,
                    'end': motion_end
                }
            }

            # 시그널 발생
            self.status_sync_changed.emit(status_data)

        except Exception as e:
            print(f"Status sync data parsing error: {e}")

    def handleMainPowerControlAck(self, senderId, payload):
        """메인 전원 제어 응답 처리"""

        if len(payload) >= 1:
            power_status = bool(payload[0])
            self.main_power_status_changed.emit(power_status)    

    def handleUnknownCommand(self, cmd):
        """
        알 수 없는 명령을 수신한 경우의 처리 (필요시 재정의).
        """
        pass


    def handleFileReceive(self, senderId, payload):
        """
        파일 전송 요청 패킷에 대한 처리 (필요시 재정의).
        """
        pass

    def handlePlayControlAck(self, senderId, payload):
        """재생 제어 응답 처리"""
        if len(payload) >= 1:
            play_status = payload[0]
            self.play_control_status_changed.emit(play_status)

    # --------------------------------------------------

    def calculateCRC16(self, data, length):
        """
        테이블을 사용한 CRC16-XMODEM 계산
        :param data: bytes-like object
        :param length: 계산할 데이터 길이
        :return: 16비트 CRC 값 (정수)
        """
        crc = 0x0000  # XMODEM 초기값
        
        for i in range(length):
            crc = ((crc << 8) & 0xFFFF) ^ self.CRC16_TABLE[((crc >> 8) ^ data[i]) & 0xFF]
            #crc = ((crc >> 8) & 0xFFFF) ^ self.CRC16_TABLE[((crc & 0xFF) ^ data[i]) & 0xFF]
            
        return crc

    # cmd 분류류
    def processCommand(self, senderId, receiverId, cmd, payload, payloadLength):
        """
        수신한 패킷의 명령어(cmd)에 따라 적절한 핸들러로 전달한다.
        """
        if cmd == ComProtocol.CMD_PING:
            self.handlePing(senderId, payload)
        elif cmd == ComProtocol.CMD_FILE_RECEIVE:
            self.handleFileReceive(senderId, payload)
        elif cmd == ComProtocol.CMD_CONFIG:
            self.handleConfig(senderId, payload)
        elif cmd == ComProtocol.CMD_STATUS_SYNC_ACK:
            self.handleStatusSyncAck(senderId, payload)
        elif cmd == ComProtocol.CMD_MAIN_POWER_CONTROL_ACK:
            self.handleMainPowerControlAck(senderId, payload)
        elif cmd == ComProtocol.CMD_PLAY_CONTROL_ACK:
            self.handlePlayControlAck(senderId, payload)
        elif cmd == ComProtocol.CMD_SESSION_SYNC:
            if len(payload) >= 6:
                timestamp = struct.unpack('>I', payload[0:4])[0]
                authToken = struct.unpack('>H', payload[4:6])[0]
                if authToken == 0xABCD:
                    self.expectedSequenceNumber = 0
                    print("동기화 성공: 시퀀스 번호 초기화")
            else:
                print("잘못된 동기화 패킷")
        elif cmd == ComProtocol.CMD_SESSION_SYNC_ACK:
            if self.waiting_for_sync:
                self.sync_timer.stop()
                self.waiting_for_sync = False
                self.sync_success.emit()
                print("동기화 성공")
        else:
            self.handleUnknownCommand(cmd)



    def resetFileTransferContext(self):
        """
        파일 전송 관련 내부 상태를 초기화한다.
        """
        self.fileContext = ComProtocol.FileTransferContext()

    def processFileTransfer(self, stage: FileTransferStage, payload):
        """
        파일 전송 프로세스를 단계별로 처리한다.
        실제 파일 전송 로직은 필요에 따라 구현해야 한다.
        :param stage: FileTransferStage 열거형 값
        :param payload: 해당 단계의 payload (bytes-like object)
        """
        # 예시) 각 단계에 따라 다르게 처리
        if stage == FileTransferStage.REQUEST_RECEIVE:
            # 파일 수신 요청 처리
            pass
        elif stage == FileTransferStage.READY_TO_RECEIVE:
            # 수신 준비 완료 처리
            pass
        elif stage == FileTransferStage.RECEIVING_DATA:
            # 데이터 수신 중 처리
            pass
        elif stage == FileTransferStage.VERIFY_CHECKSUM:
            # 체크섬 검증 처리
            pass

    def sendFileAck(self, receiverId, stage: FileTransferStage, success, data=0):
        """
        파일 전송 관련 응답(ACK) 패킷 전송.
        :param receiverId: 응답을 받을 대상 ID
        :param stage: FileTransferStage 단계
        :param success: 성공 여부 (bool)
        :param data: 추가 데이터 (예: 전송한 데이터 크기 등)
        """
        payload = bytearray()
        # payload 구성: [stage (1바이트), success (1바이트), data (4바이트)]
        payload.append(stage.value)
        payload.append(1 if success else 0)
        payload.extend(struct.pack('>I', data))
        self.sendData(receiverId, 0, ComProtocol.CMD_FILE_RECEIVE_ACK, payload)

    def calculateFileChecksum(self, data):
        """
        파일 데이터에 대한 체크섬 계산 (여기서는 간단히 바이트 합산).
        실제 사용 환경에 맞게 다른 알고리즘(CRC 등)으로 변경 가능.
        :param data: bytes-like object
        :return: 16비트 체크섬 (정수)
        """
        return sum(data) & 0xFFFF

    def sendFileReceiveAck(self, receiverId, stage: FileTransferStage, success, data=0):
        """
        파일 수신 응답 전송 함수 (sendFileAck와 동일하게 동작).
        """
        self.sendFileAck(receiverId, stage, success, data)

    def send_session_sync_packet(self, receiverId: int, senderId: int) -> None:
        """
        세션 동기화를 위한 sync 패킷 전송
        """
        timestamp = int(time.time())
        payload = struct.pack('>I', timestamp) + struct.pack('>H', 0xABCD)
        self.sendData(receiverId, senderId, ComProtocol.CMD_SESSION_SYNC, payload)

    def send_sync_packet(self, receiverId: int, senderId: int) -> None:
        """
        동기화 패킷 전송 (페이로드 없음)
        Args:
            receiverId (int): 수신자 ID
            senderId (int): 송신자 ID
        """
        self.sendData(receiverId, senderId, ComProtocol.CMD_STATUS_SYNC, b'')

    def start_sync_session(self):
        """새 세션 동기화 시작"""
        self.sync_retry_count = 0
        self.waiting_for_sync = True
        
        # QTimer 설정
        if self.sync_timer is None:
            from PySide6.QtCore import QTimer
            self.sync_timer = QTimer()
            self.sync_timer.timeout.connect(self._try_sync)
        
        self.sync_timer.start(self.SYNC_INTERVAL)
        self._try_sync()  # 첫 번째 시도 즉시 실행

    def _try_sync(self):
        """동기화 패킷 전송 시도"""
        if self.sync_retry_count >= self.MAX_SYNC_RETRIES:
            self.sync_timer.stop()
            self.waiting_for_sync = False
            self.sync_failed.emit()
            return

        self.send_session_sync_packet(0, 0)  # receiverId와 senderId는 적절히 수정
        self.sync_retry_count += 1

    def cleanup_sync(self):
        """동기화 관련 자원 정리"""
        if self.sync_timer:
            self.sync_timer.stop()
        self.waiting_for_sync = False
        self.sync_retry_count = 0

"""
# ======================================================================
# 예제: 간단한 시리얼 인터페이스 모의 구현
class DummySerialInterface:
    def write(self, data: bytes):
        print("Sending bytes:", data.hex())


class DummyTick:
    def get_time(self):
        return time.time()


# ======================================================================
# 사용 예제
if __name__ == "__main__":
    serial_iface = DummySerialInterface()
    tick = DummyTick()
    protocol = ComProtocol(serial_iface, tick)

    # 예제: ping 전송
    protocol.sendPing(0x0002)

    # 예제: 수신 데이터(실제 환경에서는 시리얼 포트로부터 읽어온 데이터를 receiveData()로 전달)
    # 여기서는 임의의 패킷을 구성하여 프로토콜 처리 테스트
    # 패킷 구성은 sendData()의 구성과 동일하게 만들어야 함
"""
