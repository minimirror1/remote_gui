import serial
import time


def main():
    # 시리얼 포트 설정
    port = 'COM9'
    baud_rate = 115200
    
    try:
        # 시리얼 포트 연결
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"포트 {port}에 연결되었습니다.")
        
        # 송신할 데이터
        data = bytes([0x01, 0x02, 0x03])
        
        while True:
            # 데이터 송신
            ser.write(data)
            print(f"송신 데이터: {data.hex()}")
            
            # 약간의 대기 시간
            time.sleep(0.1)
            
            # 데이터 수신
            received_data = ser.read(len(data))
            if received_data:
                print(f"수신 데이터: {received_data.hex()}")
                if received_data == data:
                    print("루프백 테스트 성공!")
                else:
                    print("루프백 테스트 실패: 데이터가 일치하지 않습니다.")
            else:
                print("수신 데이터 없음")
            
            # 다음 송수신까지 대기
            time.sleep(0.9)
            
    except serial.SerialException as e:
        print(f"시리얼 포트 연결 오류: {e}")
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("시리얼 포트 연결이 해제되었습니다.")

if __name__ == "__main__":
    main()
